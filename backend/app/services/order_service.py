import uuid
from decimal import Decimal
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.orders import CustomerOrder, OrderItem, OrderStatusHistory
from app.models.dining import DiningSession
from app.models.menu import MenuItem
from app.models.kitchen import KitchenTicket, KitchenTicketItem
from app.models.users import UserAccount

ALLOWED_TRANSITIONS = {
    "PLACED": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["PREPARING", "CANCELLED"],
    "PREPARING": ["READY", "SERVED", "CANCELLED"],
    "READY": ["SERVED", "CANCELLED"],
    "SERVED": [],
    "CANCELLED": []
}

def create_order(
    db: Session,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    items_data: List[Dict[str, Any]]
) -> CustomerOrder:
    # 1. Validate active dining session
    session = db.query(DiningSession).filter(DiningSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dining session not found")
    if session.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot place order for a completed or inactive dining session"
        )

    # 2. Validate user (waiter / staff)
    user = db.query(UserAccount).filter(UserAccount.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff user not found")

    # 3. Validate items list
    if not items_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must contain at least one item")

    # Pre-validate all items before creating database records
    validated_items = []
    for it in items_data:
        item_id = it.get("item_id")
        qty = it.get("quantity", 0)
        special_req = it.get("special_requests")

        if qty <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than zero")

        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not menu_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Menu item '{item_id}' not found")
        if not menu_item.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Menu item '{menu_item.name}' is currently inactive")

        validated_items.append({
            "menu_item": menu_item,
            "quantity": qty,
            "unit_price": Decimal(str(menu_item.current_price)),
            "special_requests": special_req
        })

    # 4. Atomic transaction
    try:
        order = CustomerOrder(
            session_id=session_id,
            user_id=user_id,
            status="PLACED"
        )
        db.add(order)
        db.flush() # Populate order.id

        # Order status history
        history = OrderStatusHistory(order_id=order.id, status="PLACED")
        db.add(history)

        # Kitchen ticket
        ticket = KitchenTicket(order_id=order.id, status="PENDING")
        db.add(ticket)
        db.flush() # Populate ticket.id

        for v in validated_items:
            order_item = OrderItem(
                order_id=order.id,
                item_id=v["menu_item"].id,
                quantity=v["quantity"],
                unit_price=v["unit_price"],
                special_requests=v["special_requests"]
            )
            db.add(order_item)
            db.flush()

            ticket_item = KitchenTicketItem(
                ticket_id=ticket.id,
                order_item_id=order_item.id,
                status="PENDING"
            )
            db.add(ticket_item)

        db.commit()
        db.refresh(order)
        return order
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error creating order: {str(e)}")
    except Exception as e:
        db.rollback()
        raise e

def get_order_by_id(db: Session, order_id: uuid.UUID) -> CustomerOrder:
    order = db.query(CustomerOrder).filter(CustomerOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

def get_orders_by_session(db: Session, session_id: uuid.UUID) -> List[CustomerOrder]:
    return db.query(CustomerOrder).filter(CustomerOrder.session_id == session_id).order_by(CustomerOrder.created_at.asc()).all()

def update_order_status(db: Session, order_id: uuid.UUID, new_status: str) -> CustomerOrder:
    order = get_order_by_id(db, order_id)
    status_clean = new_status.upper()

    current_status = order.status
    if status_clean == current_status:
        return order

    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if status_clean not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status}' to '{status_clean}'. Allowed: {allowed}"
        )

    try:
        order.status = status_clean
        history = OrderStatusHistory(order_id=order.id, status=status_clean)
        db.add(history)

        # Synchronize kitchen ticket status if applicable
        if order.kitchen_ticket:
            if status_clean == "CANCELLED":
                order.kitchen_ticket.status = "READY" # or keep as is
            elif status_clean == "PREPARING" and order.kitchen_ticket.status == "PENDING":
                order.kitchen_ticket.status = "IN_PROGRESS"
            elif status_clean == "READY":
                order.kitchen_ticket.status = "READY"

        db.commit()
        db.refresh(order)
        return order
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error updating order status: {str(e)}")
