import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException
from app.models.billing import Discount
from app.models.dining import DiningSession
from app.models.orders import CustomerOrder, OrderItem
from app.models.users import Role, UserAccount
from app.services.billing_service import (
    generate_bill_for_session,
    apply_discount,
    process_payment,
    get_bill_summary
)

def test_generate_bill_and_gst_calculation(db, test_session, test_order, test_menu_item):
    # Add order item to test order
    oi = OrderItem(
        order_id=test_order.id,
        item_id=test_menu_item.id,
        quantity=2,
        unit_price=Decimal("100.00")
    )
    db.add(oi)
    db.commit()

    bill = generate_bill_for_session(db, test_session.id)
    assert bill is not None
    assert Decimal(str(bill.subtotal)) == Decimal("200.00")
    assert Decimal(str(bill.tax_amount)) == Decimal("10.00") # 5% GST
    assert Decimal(str(bill.total_amount)) == Decimal("210.00")
    assert bill.status == "UNPAID"
    assert len(bill.items) == 1
    assert bill.items[0].item_name_snapshot == test_menu_item.name

    # Duplicate bill generation should fail
    with pytest.raises(HTTPException) as exc_info:
        generate_bill_for_session(db, test_session.id)
    assert exc_info.value.status_code == 409

def test_apply_discount_authorization(db, test_session, test_order, test_menu_item, test_branch):
    oi = OrderItem(order_id=test_order.id, item_id=test_menu_item.id, quantity=1, unit_price=Decimal("200.00"))
    db.add(oi)
    db.commit()

    bill = generate_bill_for_session(db, test_session.id)

    # Get or create a waiter role (not allowed to authorize discounts)
    waiter_role = db.query(Role).filter(Role.name == "WAITER").first()
    if not waiter_role:
        waiter_role = Role(name="WAITER")
        db.add(waiter_role)
        db.commit()
    waiter = UserAccount(
        role_id=waiter_role.id,
        branch_id=test_branch.id,
        first_name="Sam",
        last_name="Waiter",
        email=f"waiter_{uuid.uuid4()}@test.com",
        password_hash="hash"
    )
    db.add(waiter)
    db.commit()

    discount = Discount(name=f"Promo_{uuid.uuid4()}", discount_type="PERCENTAGE", value=10.00)
    db.add(discount)
    db.commit()

    # Waiter tries to apply discount -> 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        apply_discount(db, bill.id, discount.id, waiter.id)
    assert exc_info.value.status_code == 403

    # Manager applies discount -> succeeds
    manager_role = db.query(Role).filter(Role.name == "MANAGER").first()
    manager = UserAccount(
        role_id=manager_role.id,
        branch_id=test_branch.id,
        first_name="Boss",
        last_name="Manager",
        email=f"mgr_{uuid.uuid4()}@test.com",
        password_hash="hash"
    )
    db.add(manager)
    db.commit()

    updated_bill = apply_discount(db, bill.id, discount.id, manager.id)
    # Subtotal: 200, 10% discount = 20. Net taxable: 180. Tax (5%): 9. Total: 189
    assert Decimal(str(updated_bill.total_amount)) == Decimal("189.00")
    assert Decimal(str(updated_bill.tax_amount)) == Decimal("9.00")

def test_payment_settlement_and_session_completion(db, test_session, test_order, test_menu_item):
    oi = OrderItem(order_id=test_order.id, item_id=test_menu_item.id, quantity=1, unit_price=Decimal("100.00"))
    db.add(oi)
    db.commit()

    bill = generate_bill_for_session(db, test_session.id)
    # Total: 100 + 5 = 105.00
    assert Decimal(str(bill.total_amount)) == Decimal("105.00")

    # Partial payment of 50
    p1 = process_payment(db, bill.id, Decimal("50.00"), "CASH")
    assert p1.status == "COMPLETED"
    assert bill.status == "PARTIAL"
    assert test_session.status == "ACTIVE"

    # Excessive payment of 60 when balance is 55 should fail
    with pytest.raises(HTTPException) as exc_info:
        process_payment(db, bill.id, Decimal("60.00"), "CARD")
    assert exc_info.value.status_code == 400

    # Final payment of 55
    p2 = process_payment(db, bill.id, Decimal("55.00"), "ONLINE")
    assert p2.status == "COMPLETED"
    assert bill.status == "PAID"
    assert test_session.status == "COMPLETED"
    assert test_session.end_time is not None

    # Paying a paid bill should fail
    with pytest.raises(HTTPException) as exc_info:
        process_payment(db, bill.id, Decimal("10.00"), "CASH")
    assert exc_info.value.status_code == 400
