import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.dining import DiningSessionCreate, DiningSessionResponse
from app.services.dining_service import (
    get_sessions,
    get_session_by_id,
    create_dining_session,
    complete_dining_session
)

router = APIRouter(prefix="/dining", tags=["Dining Sessions"])

def serialize_session(s) -> Dict[str, Any]:
    return {
        "id": s.id,
        "table_id": s.table_id,
        "table_number": s.table.table_number if s.table else None,
        "reservation_id": s.reservation_id,
        "customer_id": s.customer_id,
        "customer_name": f"{s.customer.first_name} {s.customer.last_name}".strip() if s.customer else "Walk-in Guest",
        "guest_count": s.guest_count,
        "status": s.status,
        "start_time": s.start_time.isoformat() if s.start_time else None,
        "end_time": s.end_time.isoformat() if s.end_time else None,
        "orders_count": len(s.orders) if s.orders else 0,
        "has_bill": s.bill is not None,
        "bill_id": s.bill.id if s.bill else None,
        "bill_status": s.bill.status if s.bill else None
    }

@router.get("/sessions")
def list_sessions(
    status: Optional[str] = Query(None, description="Filter sessions by status (ACTIVE, COMPLETED)"),
    table_id: Optional[uuid.UUID] = Query(None, description="Filter sessions by table ID"),
    db: Session = Depends(get_db)
):
    sessions = get_sessions(db, status_filter=status, table_id=table_id)
    return [serialize_session(s) for s in sessions]

@router.get("/sessions/{id}")
def get_session(id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    session = get_session_by_id(db, id)
    return serialize_session(session)

@router.post("/sessions")
def seat_guests(session_in: DiningSessionCreate, db: Session = Depends(get_db)):
    session = create_dining_session(db, session_in)
    return serialize_session(session)

@router.post("/sessions/{id}/complete")
def end_session(id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    session = complete_dining_session(db, id)
    return serialize_session(session)
