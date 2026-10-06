import uuid
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.dining import ReservationCreate, ReservationResponse, ReservationUpdate
from app.services.reservation_service import (
    get_reservations,
    get_reservation_by_id,
    create_reservation,
    update_reservation,
    update_reservation_status,
    delete_reservation
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])

class StatusUpdateRequest(BaseModel):
    status: str

def serialize_reservation(r) -> Dict[str, Any]:
    return {
        "id": r.id,
        "table_id": r.table_id,
        "table_number": r.table.table_number if r.table else None,
        "customer_id": r.customer_id,
        "customer_name": f"{r.customer.first_name} {r.customer.last_name}".strip() if r.customer else None,
        "customer_phone": r.customer.phone if r.customer else None,
        "customer_email": r.customer.email if r.customer else None,
        "start_time": r.start_time.isoformat() if r.start_time else None,
        "end_time": r.end_time.isoformat() if r.end_time else None,
        "guest_count": r.guest_count,
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None
    }

@router.get("")
def list_reservations(
    filter_date: Optional[date] = Query(None, description="Filter reservations by date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status (PENDING, CONFIRMED, CANCELLED, NO_SHOW, COMPLETED)"),
    table_id: Optional[uuid.UUID] = Query(None, description="Filter by table ID"),
    db: Session = Depends(get_db)
):
    results = get_reservations(db, filter_date=filter_date, filter_status=status, filter_table_id=table_id)
    return [serialize_reservation(r) for r in results]

@router.post("", response_model=ReservationResponse)
def make_reservation(res_in: ReservationCreate, db: Session = Depends(get_db)):
    return create_reservation(db, res_in)

@router.get("/{id}")
def get_reservation(id: uuid.UUID = Path(...), db: Session = Depends(get_db)):
    r = get_reservation_by_id(db, id)
    return serialize_reservation(r)

@router.patch("/{id}/status")
def patch_reservation_status(
    id: uuid.UUID = Path(...),
    payload: StatusUpdateRequest = Body(...),
    db: Session = Depends(get_db)
):
    r = update_reservation_status(db, id, payload.status)
    return serialize_reservation(r)

@router.delete("/{id}")
def delete_reservation_record(
    id: uuid.UUID = Path(...),
    db: Session = Depends(get_db)
):
    delete_reservation(db, id)
    return {"status": "DELETED", "id": str(id), "message": "Reservation record permanently deleted from database."}
