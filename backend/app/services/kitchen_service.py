import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.kitchen import KitchenTicket, KitchenTicketItem
from app.models.orders import CustomerOrder, OrderStatusHistory

def get_kitchen_tickets(
    db: Session,
    status_filter: Optional[str] = None
) -> List[KitchenTicket]:
    query = db.query(KitchenTicket)
    if status_filter:
        query = query.filter(KitchenTicket.status == status_filter.upper())
    return query.order_by(KitchenTicket.created_at.asc()).all()

def get_kitchen_ticket_by_id(db: Session, ticket_id: uuid.UUID) -> KitchenTicket:
    ticket = db.query(KitchenTicket).filter(KitchenTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitchen ticket not found")
    return ticket

def start_kitchen_ticket(db: Session, ticket_id: uuid.UUID) -> KitchenTicket:
    ticket = get_kitchen_ticket_by_id(db, ticket_id)
    if ticket.status == "READY":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket is already marked READY")

    ticket.status = "IN_PROGRESS"
    if not ticket.prep_start_time:
        ticket.prep_start_time = datetime.now(timezone.utc)

    # Update items
    for it in ticket.items:
        if it.status == "PENDING":
            it.status = "PREPARING"

    # Synchronize order
    if ticket.order and ticket.order.status in ["PLACED", "CONFIRMED"]:
        ticket.order.status = "PREPARING"
        db.add(OrderStatusHistory(order_id=ticket.order.id, status="PREPARING"))

    try:
        db.commit()
        db.refresh(ticket)
        return ticket
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error starting ticket: {str(e)}")

def mark_kitchen_ticket_ready(db: Session, ticket_id: uuid.UUID) -> KitchenTicket:
    ticket = get_kitchen_ticket_by_id(db, ticket_id)

    # Mark all uncompleted items as COMPLETED
    for it in ticket.items:
        if it.status in ["PENDING", "PREPARING"]:
            it.status = "COMPLETED"

    ticket.status = "READY"
    ticket.ready_time = datetime.now(timezone.utc)

    if ticket.order and ticket.order.status != "READY":
        ticket.order.status = "READY"
        db.add(OrderStatusHistory(order_id=ticket.order.id, status="READY"))

    try:
        db.commit()
        db.refresh(ticket)
        return ticket
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error completing ticket: {str(e)}")

def update_kitchen_ticket_item_status(
    db: Session,
    ticket_id: uuid.UUID,
    item_id: uuid.UUID,
    new_status: str
) -> KitchenTicketItem:
    ticket = get_kitchen_ticket_by_id(db, ticket_id)
    status_clean = new_status.upper()

    allowed = {"PENDING", "PREPARING", "COMPLETED", "CANCELLED"}
    if status_clean not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid kitchen item status '{new_status}'. Allowed: {allowed}"
        )

    # Find item
    target_item = None
    for it in ticket.items:
        if it.id == item_id or it.order_item_id == item_id:
            target_item = it
            break

    if not target_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitchen ticket item not found")

    target_item.status = status_clean

    # If any item started preparing, set ticket to IN_PROGRESS
    if status_clean == "PREPARING" and ticket.status == "PENDING":
        ticket.status = "IN_PROGRESS"
        if not ticket.prep_start_time:
            ticket.prep_start_time = datetime.now(timezone.utc)
        if ticket.order and ticket.order.status in ["PLACED", "CONFIRMED"]:
            ticket.order.status = "PREPARING"
            db.add(OrderStatusHistory(order_id=ticket.order.id, status="PREPARING"))

    # Check if all items are completed or cancelled
    all_done = all(it.status in ["COMPLETED", "CANCELLED"] for it in ticket.items)
    if all_done and len(ticket.items) > 0:
        ticket.status = "READY"
        ticket.ready_time = datetime.now(timezone.utc)
        if ticket.order and ticket.order.status != "READY":
            ticket.order.status = "READY"
            db.add(OrderStatusHistory(order_id=ticket.order.id, status="READY"))

    try:
        db.commit()
        db.refresh(target_item)
        return target_item
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")
