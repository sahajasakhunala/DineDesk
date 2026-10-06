import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.dining import DiningSession, Reservation
from app.models.restaurant import TableEntity, DiningArea
from app.models.users import Customer
from app.schemas.dining import DiningSessionCreate, DiningSessionUpdate

def compute_table_status(
    db: Session,
    table: TableEntity,
    check_start: Optional[datetime] = None,
    check_end: Optional[datetime] = None
) -> Dict[str, Any]:
    # 1. Check if table is actively occupied by a seated dining session (e.g. walk-in or seated guest)
    active_session = db.query(DiningSession).filter(
        DiningSession.table_id == table.id,
        DiningSession.status == "ACTIVE"
    ).first()

    if active_session:
        cust_name = f"{active_session.customer.first_name} {active_session.customer.last_name}".strip() if active_session.customer else "Walk-in Guest"
        return {
            "status": "OCCUPIED",
            "active_session_id": str(active_session.id),
            "guest_count": active_session.guest_count,
            "reserved_for": cust_name,
            "session_start": active_session.start_time.isoformat() if active_session.start_time else None,
            "reserved_window": "Walk-In Dining"
        }

    # 2. If specific reservation window is provided:
    if check_start and check_end:
        if check_start.tzinfo is not None:
            check_start = check_start.replace(tzinfo=None)
        if check_end.tzinfo is not None:
            check_end = check_end.replace(tzinfo=None)

        overlapping = db.query(Reservation).filter(
            Reservation.table_id == table.id,
            Reservation.status.in_(["PENDING", "CONFIRMED"]),
            Reservation.start_time < check_end,
            Reservation.end_time > check_start
        ).first()

        if overlapping:
            res_cust = f"{overlapping.customer.first_name} {overlapping.customer.last_name}".strip() if overlapping.customer else "Reserved Guest"
            start_str = overlapping.start_time.strftime('%I:%M %p') if overlapping.start_time else ""
            end_str = overlapping.end_time.strftime('%I:%M %p') if overlapping.end_time else ""
            return {
                "status": "RESERVED",
                "reservation_id": str(overlapping.id),
                "reserved_for": res_cust,
                "res_start": overlapping.start_time.isoformat() if overlapping.start_time else None,
                "res_end": overlapping.end_time.isoformat() if overlapping.end_time else None,
                "reserved_window": f"{start_str} – {end_str}" if start_str and end_str else "Booked Slot"
            }
        return {
            "status": "AVAILABLE"
        }

    # Default real-time table status
    active_session = db.query(DiningSession).filter(
        DiningSession.table_id == table.id,
        DiningSession.status == "ACTIVE"
    ).first()

    if active_session:
        return {
            "status": "OCCUPIED",
            "active_session_id": str(active_session.id),
            "guest_count": active_session.guest_count,
            "session_start": active_session.start_time.isoformat() if active_session.start_time else None
        }

    now = datetime.now(timezone.utc)
    two_hours_later = now + timedelta(hours=2)
    upcoming_reservation = db.query(Reservation).filter(
        Reservation.table_id == table.id,
        Reservation.status.in_(["PENDING", "CONFIRMED"]),
        Reservation.start_time <= two_hours_later,
        Reservation.end_time >= now
    ).first()

    if upcoming_reservation:
        return {
            "status": "RESERVED",
            "reservation_id": str(upcoming_reservation.id),
            "reserved_for": upcoming_reservation.customer.first_name + " " + upcoming_reservation.customer.last_name if upcoming_reservation.customer else "Guest",
            "res_time": upcoming_reservation.start_time.isoformat()
        }

    return {
        "status": "AVAILABLE"
    }

def get_tables_with_status(
    db: Session,
    area_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = None,
    check_start: Optional[datetime] = None,
    check_end: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    query = db.query(TableEntity)
    if area_id:
        query = query.filter(TableEntity.area_id == area_id)
    tables = query.order_by(TableEntity.table_number.asc()).all()

    result = []
    for table in tables:
        stat_info = compute_table_status(db, table, check_start=check_start, check_end=check_end)
        table_status = stat_info["status"]
        if status_filter and table_status != status_filter.upper():
            continue
        result.append({
            "id": table.id,
            "area_id": table.area_id,
            "area_name": table.area.name if table.area else None,
            "table_number": table.table_number,
            "capacity": table.capacity,
            "is_active": table.is_active,
            "status": table_status,
            "status_details": stat_info,
            "created_at": table.created_at,
            "updated_at": table.updated_at
        })
    return result

def get_sessions(
    db: Session,
    status_filter: Optional[str] = None,
    table_id: Optional[uuid.UUID] = None
) -> List[DiningSession]:
    query = db.query(DiningSession)
    if status_filter:
        query = query.filter(DiningSession.status == status_filter.upper())
    if table_id:
        query = query.filter(DiningSession.table_id == table_id)
    return query.order_by(DiningSession.start_time.desc()).all()

def get_session_by_id(db: Session, session_id: uuid.UUID) -> DiningSession:
    session = db.query(DiningSession).filter(DiningSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dining session not found")
    return session

def create_dining_session(db: Session, session_in: DiningSessionCreate) -> DiningSession:
    # 1. Validate table
    table = db.query(TableEntity).filter(TableEntity.id == session_in.table_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    if not table.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table is inactive")

    # 2. Prevent seating already occupied table
    existing_active = db.query(DiningSession).filter(
        DiningSession.table_id == session_in.table_id,
        DiningSession.status == "ACTIVE"
    ).first()
    if existing_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Table {table.table_number} is already occupied by an active dining session"
        )

    # 3. Validate capacity
    if session_in.guest_count <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Guest count must be greater than zero")
    if session_in.guest_count > table.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Guest count ({session_in.guest_count}) exceeds table capacity ({table.capacity})"
        )

    # 4. Handle reservation link if provided
    customer_id = session_in.customer_id
    if session_in.reservation_id:
        res = db.query(Reservation).filter(Reservation.id == session_in.reservation_id).first()
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Linked reservation not found")
        if res.table_id != session_in.table_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservation table does not match the requested table"
            )
        # Update reservation status to COMPLETED as customer is seated
        res.status = "COMPLETED"
        if not customer_id:
            customer_id = res.customer_id

    # 5. Create atomic session
    new_session = DiningSession(
        table_id=session_in.table_id,
        reservation_id=session_in.reservation_id,
        customer_id=customer_id,
        guest_count=session_in.guest_count,
        status="ACTIVE",
        start_time=datetime.now(timezone.utc)
    )

    try:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database constraint violation: {str(e)}")

def complete_dining_session(db: Session, session_id: uuid.UUID) -> DiningSession:
    session = get_session_by_id(db, session_id)
    if session.status == "COMPLETED":
        return session

    session.status = "COMPLETED"
    session.end_time = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(session)
        return session
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error ending session: {str(e)}")
