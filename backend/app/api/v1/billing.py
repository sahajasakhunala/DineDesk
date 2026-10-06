import uuid
from decimal import Decimal
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Path, Body, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.billing import Discount
from app.models.users import UserAccount
from app.services.auth_service import get_current_user, get_optional_current_user
from app.services.billing_service import (
    generate_bill_for_session,
    get_bill_by_id,
    get_bill_by_session_id,
    apply_discount,
    process_payment,
    get_bill_summary
)

router = APIRouter(prefix="/billing", tags=["Billing & Payments"])

class ApplyDiscountRequest(BaseModel):
    discount_id: uuid.UUID
    authorized_by_user_id: Optional[uuid.UUID] = None
    reason: Optional[str] = None

class ProcessPaymentRequest(BaseModel):
    amount: Decimal
    payment_method: str
    transaction_ref: Optional[str] = None

@router.get("/discounts")
def list_discounts(db: Session = Depends(get_db)):
    discounts = db.query(Discount).filter(Discount.is_active == True).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "discount_type": d.discount_type,
            "value": float(d.value),
            "max_discount_amount": float(d.max_discount_amount) if d.max_discount_amount else None
        }
        for d in discounts
    ]

@router.post("/sessions/{session_id}/generate")
def create_session_bill(session_id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    bill = generate_bill_for_session(db, session_id)
    return get_bill_summary(db, bill.id)

@router.get("/bills/{bill_id}")
def get_bill(bill_id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    return get_bill_summary(db, bill_id)

@router.get("/sessions/{session_id}/bill")
def get_session_bill(session_id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    bill = get_bill_by_session_id(db, session_id)
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No bill found for this session")
    return get_bill_summary(db, bill.id)

@router.post("/bills/{bill_id}/discounts")
def apply_bill_discount(
    bill_id: uuid.UUID = Path(...),
    payload: ApplyDiscountRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: Optional[UserAccount] = Depends(get_optional_current_user)
):
    authorizer_id = payload.authorized_by_user_id or (current_user.id if current_user else None)
    if not authorizer_id:
        # Check if an admin or manager user exists
        from app.models.users import Role
        mgr = db.query(UserAccount).join(Role).filter(Role.name.in_(["MANAGER", "ADMIN"])).first()
        if mgr:
            authorizer_id = mgr.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount requires an authorized staff (MANAGER or ADMIN) user ID."
            )

    bill = apply_discount(db, bill_id, payload.discount_id, authorizer_id, payload.reason)
    return get_bill_summary(db, bill.id)

@router.post("/bills/{bill_id}/payments")
def record_payment(
    bill_id: uuid.UUID = Path(...),
    payload: ProcessPaymentRequest = Body(...),
    db: Session = Depends(get_db)
):
    payment = process_payment(db, bill_id, payload.amount, payload.payment_method, payload.transaction_ref)
    return {
        "payment_id": payment.id,
        "amount": float(payment.amount),
        "method": payment.payment_method,
        "status": payment.status,
        "bill": get_bill_summary(db, bill_id)
    }
