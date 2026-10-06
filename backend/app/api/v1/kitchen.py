import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.kitchen import KitchenTicket
from app.services.kitchen_service import (
    get_kitchen_tickets,
    get_kitchen_ticket_by_id,
    start_kitchen_ticket,
    mark_kitchen_ticket_ready,
    update_kitchen_ticket_item_status
)

router = APIRouter(prefix="/kitchen", tags=["Kitchen Display System"])

class ItemStatusUpdateRequest(BaseModel):
    status: str

def serialize_ticket(t: KitchenTicket) -> Dict[str, Any]:
    order = t.order
    table_num = order.session.table.table_number if order and order.session and order.session.table else "N/A"
    return {
        "id": t.id,
        "order_id": t.order_id,
        "table_number": table_num,
        "status": t.status,
        "prep_start_time": t.prep_start_time.isoformat() if t.prep_start_time else None,
        "ready_time": t.ready_time.isoformat() if t.ready_time else None,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "items": [
            {
                "id": it.id,
                "order_item_id": it.order_item_id,
                "name": it.ticket.order.items[0].item.name if False else "Item",
                "quantity": 1,
                "status": it.status
            }
        ]
    }

def serialize_detailed_ticket(t: KitchenTicket, db: Session) -> Dict[str, Any]:
    order = t.order
    table_num = order.session.table.table_number if order and order.session and order.session.table else "N/A"
    
    items = []
    # Self-healing fallback: If ticket has no items registered, recover them from the associated order
    if (not t.items or len(t.items) == 0) and order and order.items:
        from app.models.kitchen import KitchenTicketItem
        from app.models.menu import MenuItem
        default_status = "COMPLETED" if t.status == "READY" else ("PREPARING" if t.status == "IN_PROGRESS" else "PENDING")
        for oi in order.items:
            kti = KitchenTicketItem(
                ticket_id=t.id,
                order_item_id=oi.id,
                status=default_status
            )
            db.add(kti)
            try:
                db.flush()
            except Exception:
                pass
            mi = db.query(MenuItem).filter(MenuItem.id == oi.item_id).first()
            items.append({
                "id": str(kti.id) if kti.id else str(uuid.uuid4()),
                "order_item_id": str(oi.id),
                "name": mi.name if mi else "Menu Item",
                "quantity": oi.quantity,
                "special_requests": oi.special_requests,
                "status": default_status
            })
        try:
            db.commit()
            db.refresh(t)
        except Exception:
            db.rollback()
    else:
        for it in t.items:
            from app.models.orders import OrderItem
            oi = db.query(OrderItem).filter(OrderItem.id == it.order_item_id).first()
            item_name = "Menu Item"
            qty = 1
            spec_req = None
            if oi:
                qty = oi.quantity
                spec_req = oi.special_requests
                from app.models.menu import MenuItem
                mi = db.query(MenuItem).filter(MenuItem.id == oi.item_id).first()
                if mi:
                    item_name = mi.name

            items.append({
                "id": str(it.id),
                "order_item_id": str(it.order_item_id),
                "name": item_name,
                "quantity": qty,
                "special_requests": spec_req,
                "status": it.status
            })

    return {
        "id": t.id,
        "order_id": t.order_id,
        "table_number": table_num,
        "status": t.status,
        "prep_start_time": t.prep_start_time.isoformat() if t.prep_start_time else None,
        "ready_time": t.ready_time.isoformat() if t.ready_time else None,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "items": items
    }

@router.get("/tickets")
def list_tickets(
    status: Optional[str] = Query(None, description="Filter tickets by status (PENDING, IN_PROGRESS, READY)"),
    db: Session = Depends(get_db)
):
    tickets = get_kitchen_tickets(db, status_filter=status)
    return [serialize_detailed_ticket(t, db) for t in tickets]

@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    ticket = get_kitchen_ticket_by_id(db, ticket_id)
    return serialize_detailed_ticket(ticket, db)

@router.post("/tickets/{ticket_id}/start")
def start_ticket(ticket_id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    ticket = start_kitchen_ticket(db, ticket_id)
    return serialize_detailed_ticket(ticket, db)

@router.post("/tickets/{ticket_id}/ready")
def complete_ticket(ticket_id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    ticket = mark_kitchen_ticket_ready(db, ticket_id)
    return serialize_detailed_ticket(ticket, db)

@router.patch("/tickets/{ticket_id}/items/{item_id}")
def update_item_status(
    ticket_id: uuid.UUID = Path(...),
    item_id: uuid.UUID = Path(...),
    payload: ItemStatusUpdateRequest = Body(...),
    db: Session = Depends(get_db)
):
    item = update_kitchen_ticket_item_status(db, ticket_id, item_id, payload.status)
    ticket = get_kitchen_ticket_by_id(db, ticket_id)
    return serialize_detailed_ticket(ticket, db)
