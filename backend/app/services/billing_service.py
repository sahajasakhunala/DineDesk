import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.billing import Bill, BillItem, Discount, DiscountApplication, Payment
from app.models.dining import DiningSession
from app.models.orders import CustomerOrder
from app.models.users import UserAccount, Role

TAX_RATE = Decimal("0.05")  # 5% GST

def round_money(val: Any) -> Decimal:
    if val is None:
        return Decimal("0.00")
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def get_bill_by_id(db: Session, bill_id: uuid.UUID) -> Bill:
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    return bill

def get_bill_by_session_id(db: Session, session_id: uuid.UUID) -> Optional[Bill]:
    return db.query(Bill).filter(Bill.session_id == session_id).first()

def generate_bill_for_session(db: Session, session_id: uuid.UUID) -> Bill:
    # 1. Verify dining session exists
    session = db.query(DiningSession).filter(DiningSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dining session not found")

    # 2. Check for duplicate bill
    existing_bill = db.query(Bill).filter(Bill.session_id == session_id).first()
    if existing_bill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Bill already generated for session {session_id} with bill ID {existing_bill.id}"
        )

    # 3. Retrieve all non-cancelled orders for session
    orders = db.query(CustomerOrder).filter(
        CustomerOrder.session_id == session_id,
        CustomerOrder.status != "CANCELLED"
    ).all()

    if not orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate bill: No active or served orders found for this session"
        )

    # Collect order items
    order_items = []
    for order in orders:
        for oi in order.items:
            order_items.append(oi)

    if not order_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate bill: Orders contain no items"
        )

    # 4. Atomic transaction: create Bill and BillItems
    try:
        subtotal = Decimal("0.00")

        # Initial bill record
        bill = Bill(
            session_id=session_id,
            subtotal=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("0.00"),
            status="UNPAID"
        )
        db.add(bill)
        db.flush()  # populate bill.id

        for oi in order_items:
            item_name = "Menu Item"
            from app.models.menu import MenuItem
            m_item = db.query(MenuItem).filter(MenuItem.id == oi.item_id).first()
            if m_item:
                item_name = m_item.name

            unit_price = Decimal(str(oi.unit_price))
            qty = oi.quantity
            line_subtotal = round_money(unit_price * qty)
            subtotal += line_subtotal

            bill_item = BillItem(
                bill_id=bill.id,
                order_item_id=oi.id,
                item_name_snapshot=item_name,
                quantity=qty,
                unit_price=unit_price
            )
            db.add(bill_item)

        tax_amount = round_money(subtotal * TAX_RATE)
        total_amount = round_money(subtotal + tax_amount)

        bill.subtotal = subtotal
        bill.tax_amount = tax_amount
        bill.total_amount = total_amount

        db.commit()
        db.refresh(bill)
        return bill
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error generating bill: {str(e)}")
    except Exception as e:
        db.rollback()
        raise e

def apply_discount(
    db: Session,
    bill_id: uuid.UUID,
    discount_id: uuid.UUID,
    authorized_by_user_id: uuid.UUID,
    reason: Optional[str] = None
) -> Bill:
    bill = get_bill_by_id(db, bill_id)

    # 1. Verify bill is still open
    if bill.status in ["PAID", "VOIDED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot apply discount: Bill is already {bill.status}"
        )

    # 2. Check authorizing user
    authorizer = db.query(UserAccount).filter(UserAccount.id == authorized_by_user_id).first()
    if not authorizer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Authorizing user not found")
    
    role_name = authorizer.role.name.upper() if authorizer.role else ""
    if role_name not in ["ADMIN", "MANAGER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with role '{role_name}' is not authorized to apply discounts. Requires ADMIN or MANAGER."
        )

    # 3. Check discount rule
    discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not discount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discount not found")
    if not discount.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discount is inactive")

    # Prevent duplicate application of the same discount on this bill
    existing_app = db.query(DiscountApplication).filter(
        DiscountApplication.bill_id == bill.id,
        DiscountApplication.discount_id == discount.id
    ).first()
    if existing_app:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discount has already been applied to this bill")

    # 4. Calculate discount deduction
    bill_subtotal = Decimal(str(bill.subtotal))
    discount_val = Decimal(str(discount.value))
    max_cap = Decimal(str(discount.max_discount_amount)) if discount.max_discount_amount else None

    if discount.discount_type == "PERCENTAGE":
        calc_amount = round_money(bill_subtotal * (discount_val / Decimal("100.00")))
        if max_cap is not None:
            calc_amount = min(calc_amount, max_cap)
        discount_app = DiscountApplication(
            bill_id=bill.id,
            discount_id=discount.id,
            authorized_by_user_id=authorizer.id,
            discount_amount=None,
            discount_percentage=discount_val,
            reason=reason or f"Authorized by {authorizer.first_name}"
        )
        actual_deduction = calc_amount
    else:  # FIXED
        actual_deduction = min(bill_subtotal, discount_val)
        if max_cap is not None:
            actual_deduction = min(actual_deduction, max_cap)
        discount_app = DiscountApplication(
            bill_id=bill.id,
            discount_id=discount.id,
            authorized_by_user_id=authorizer.id,
            discount_amount=actual_deduction,
            discount_percentage=None,
            reason=reason or f"Authorized by {authorizer.first_name}"
        )

    try:
        db.add(discount_app)
        db.flush()

        # Recalculate total bill: Subtotal - All Discounts + Tax
        all_apps = db.query(DiscountApplication).filter(DiscountApplication.bill_id == bill.id).all()
        total_discount = Decimal("0.00")
        for da in all_apps:
            if da.discount_amount is not None:
                total_discount += Decimal(str(da.discount_amount))
            elif da.discount_percentage is not None:
                d_rule = da.discount_rule
                pct_amt = round_money(bill_subtotal * (Decimal(str(da.discount_percentage)) / Decimal("100.00")))
                if d_rule and d_rule.max_discount_amount:
                    pct_amt = min(pct_amt, Decimal(str(d_rule.max_discount_amount)))
                total_discount += pct_amt

        # Cap total discount at subtotal
        total_discount = min(bill_subtotal, total_discount)

        net_taxable = max(Decimal("0.00"), bill_subtotal - total_discount)
        new_tax = round_money(net_taxable * TAX_RATE)
        new_total = round_money(net_taxable + new_tax)

        bill.tax_amount = new_tax
        bill.total_amount = new_total

        db.commit()
        db.refresh(bill)
        return bill
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error applying discount: {str(e)}")
    except Exception as e:
        db.rollback()
        raise e

def process_payment(
    db: Session,
    bill_id: uuid.UUID,
    amount: Decimal,
    payment_method: str,
    transaction_ref: Optional[str] = None
) -> Payment:
    bill = get_bill_by_id(db, bill_id)

    # 1. Verify bill is open
    if bill.status in ["PAID", "VOIDED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot process payment: Bill is already {bill.status}"
        )

    # 2. Validate amount
    amt = round_money(Decimal(str(amount)))
    if amt <= Decimal("0.00"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount must be greater than zero")

    # 3. Validate payment method
    valid_methods = {"CASH", "CARD", "ONLINE", "WALLET"}
    method_clean = payment_method.upper()
    if method_clean not in valid_methods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment method '{payment_method}'. Allowed: {valid_methods}"
        )

    # 4. Check outstanding balance
    completed_payments = db.query(Payment).filter(
        Payment.bill_id == bill.id,
        Payment.status == "COMPLETED"
    ).all()
    total_paid = sum((Decimal(str(p.amount)) for p in completed_payments), Decimal("0.00"))
    bill_total = Decimal(str(bill.total_amount))
    remaining_balance = round_money(bill_total - total_paid)

    if amt > remaining_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ₹{amt} exceeds outstanding balance of ₹{remaining_balance}"
        )

    # 5. Create Payment record and update Bill & Session atomically
    try:
        payment = Payment(
            bill_id=bill.id,
            amount=amt,
            payment_method=method_clean,
            status="COMPLETED",
            transaction_ref=transaction_ref
        )
        db.add(payment)
        db.flush()

        new_total_paid = round_money(total_paid + amt)
        if new_total_paid >= bill_total:
            bill.status = "PAID"

            # Complete dining session and release table
            session = db.query(DiningSession).filter(DiningSession.id == bill.session_id).first()
            if session and session.status == "ACTIVE":
                session.status = "COMPLETED"
                session.end_time = datetime.now(timezone.utc)
        else:
            bill.status = "PARTIAL"

        db.commit()
        db.refresh(payment)
        db.refresh(bill)
        return payment
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error processing payment: {str(e)}")
    except Exception as e:
        db.rollback()
        raise e

def get_bill_summary(db: Session, bill_id: uuid.UUID) -> Dict[str, Any]:
    bill = get_bill_by_id(db, bill_id)
    payments = db.query(Payment).filter(Payment.bill_id == bill.id, Payment.status == "COMPLETED").all()
    total_paid = sum((Decimal(str(p.amount)) for p in payments), Decimal("0.00"))
    balance = max(Decimal("0.00"), Decimal(str(bill.total_amount)) - total_paid)

    return {
        "id": bill.id,
        "session_id": bill.session_id,
        "subtotal": Decimal(str(bill.subtotal)),
        "tax_amount": Decimal(str(bill.tax_amount)),
        "total_amount": Decimal(str(bill.total_amount)),
        "total_paid": round_money(total_paid),
        "remaining_balance": round_money(balance),
        "status": bill.status,
        "items": [
            {
                "id": it.id,
                "name": it.item_name_snapshot,
                "quantity": it.quantity,
                "unit_price": Decimal(str(it.unit_price)),
                "total_price": Decimal(str(it.total_price))
            } for it in bill.items
        ],
        "discounts": [
            {
                "id": da.id,
                "discount_id": da.discount_id,
                "name": da.discount_rule.name if da.discount_rule else "Discount",
                "amount": Decimal(str(da.discount_amount)) if da.discount_amount else None,
                "percentage": Decimal(str(da.discount_percentage)) if da.discount_percentage else None,
                "reason": da.reason
            } for da in bill.discounts
        ],
        "payments": [
            {
                "id": p.id,
                "amount": Decimal(str(p.amount)),
                "method": p.payment_method,
                "status": p.status,
                "created_at": p.created_at
            } for p in bill.payments
        ],
        "created_at": bill.created_at,
        "updated_at": bill.updated_at
    }
