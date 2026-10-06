import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Path, Body, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.orders import CustomerOrder
from app.models.dining import DiningSession
from app.models.users import UserAccount
from app.services.auth_service import get_optional_current_user
from app.services.order_service import (
    create_order,
    get_order_by_id,
    get_orders_by_session,
    update_order_status
)

router = APIRouter(prefix="/orders", tags=["Food Orders"])

class OrderItemInput(BaseModel):
    item_id: uuid.UUID
    quantity: int
    special_requests: Optional[str] = None

class CreateOrderRequest(BaseModel):
    session_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    items: List[OrderItemInput]

class StatusUpdateRequest(BaseModel):
    status: str

def serialize_order(o: CustomerOrder) -> Dict[str, Any]:
    return {
        "id": o.id,
        "session_id": o.session_id,
        "table_number": o.session.table.table_number if o.session and o.session.table else None,
        "user_id": o.user_id,
        "staff_name": f"{o.user.first_name} {o.user.last_name}" if o.user else "Staff",
        "status": o.status,
        "items": [
            {
                "id": oi.id,
                "item_id": oi.item_id,
                "name": oi.item.name if hasattr(oi, "item") and oi.item else "Menu Item",
                "quantity": oi.quantity,
                "unit_price": float(oi.unit_price),
                "total_price": float(oi.unit_price * oi.quantity),
                "special_requests": oi.special_requests
            }
            for oi in o.items
        ],
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "updated_at": o.updated_at.isoformat() if o.updated_at else None,
        "kitchen_ticket_id": o.kitchen_ticket.id if o.kitchen_ticket else None,
        "kitchen_status": o.kitchen_ticket.status if o.kitchen_ticket else None
    }

@router.post("")
def place_order(
    req: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: Optional[UserAccount] = Depends(get_optional_current_user)
):
    target_user_id = req.user_id or (current_user.id if current_user else None)
    
    # If placed from customer web UI without staff user, find branch staff
    if not target_user_id:
        session = db.query(DiningSession).filter(DiningSession.id == req.session_id).first()
        if session and session.table and session.table.area:
            branch_id = session.table.area.branch_id
            staff = db.query(UserAccount).filter(UserAccount.branch_id == branch_id).first()
            if staff:
                target_user_id = staff.id
        if not target_user_id:
            # Fallback to any user account
            first_user = db.query(UserAccount).first()
            if first_user:
                target_user_id = first_user.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No staff user available to assign order to. Please ensure staff accounts exist."
                )

    items_data = [
        {
            "item_id": it.item_id,
            "quantity": it.quantity,
            "special_requests": it.special_requests
        }
        for it in req.items
    ]

    order = create_order(db, req.session_id, target_user_id, items_data)
    return serialize_order(order)

@router.get("/session/{session_id}")
def list_session_orders(session_id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    orders = get_orders_by_session(db, session_id)
    return [serialize_order(o) for o in orders]

@router.get("/{order_id}")
def get_order(order_id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    order = get_order_by_id(db, order_id)
    return serialize_order(order)

@router.patch("/{order_id}/status")
def change_order_status(
    order_id: uuid.UUID = Path(...),
    payload: StatusUpdateRequest = Body(...),
    db: Session = Depends(get_db)
):
    order = update_order_status(db, order_id, payload.status)
    return serialize_order(order)
