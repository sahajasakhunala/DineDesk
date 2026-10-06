import uuid
from datetime import datetime, date, time
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
from app.models.dining import Reservation
from app.models.restaurant import TableEntity
from app.models.users import Customer
from app.schemas.dining import ReservationCreate, ReservationUpdate

def get_reservations(
    db: Session,
    filter_date: Optional[date] = None,
    filter_status: Optional[str] = None,
    filter_table_id: Optional[uuid.UUID] = None
) -> List[Reservation]:
    query = db.query(Reservation)
    if filter_date:
        start_of_day = datetime.combine(filter_date, time.min)
        end_of_day = datetime.combine(filter_date, time.max)
        query = query.filter(Reservation.start_time >= start_of_day, Reservation.start_time <= end_of_day)
    if filter_status:
        query = query.filter(Reservation.status == filter_status.upper())
    if filter_table_id:
        query = query.filter(Reservation.table_id == filter_table_id)
    return query.order_by(Reservation.start_time.asc()).all()

def get_reservation_by_id(db: Session, reservation_id: uuid.UUID) -> Reservation:
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return res

def check_reservation_overlap(
    db: Session,
    table_id: uuid.UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_id: Optional[uuid.UUID] = None
) -> bool:
    query = db.query(Reservation).filter(
        Reservation.table_id == table_id,
        Reservation.status.in_(["PENDING", "CONFIRMED"]),
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    )
    if exclude_id:
        query = query.filter(Reservation.id != exclude_id)
    return query.first() is not None

def create_reservation(db: Session, res_in: ReservationCreate) -> Reservation:
    # 1. Validate table
    table = db.query(TableEntity).filter(TableEntity.id == res_in.table_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    if not table.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table is inactive")

    # 2. Validate customer
    customer = db.query(Customer).filter(Customer.id == res_in.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # 3. Validate guest count
    if res_in.guest_count <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Guest count must be greater than zero")
    if res_in.guest_count > table.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Guest count ({res_in.guest_count}) exceeds table capacity ({table.capacity})"
        )

    # 4. Validate time
    if res_in.end_time <= res_in.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End time must be after start time")

    # Advance booking requirement: must be booked at least 3 days in advance
    now_date = datetime.utcnow().date()
    res_start_date = res_in.start_time.date()
    if (res_start_date - now_date).days < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservations must be booked at least 3 days in advance."
        )

    # 5. Overlap check
    if check_reservation_overlap(db, res_in.table_id, res_in.start_time, res_in.end_time):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Table is already reserved for this time window"
        )

    reservation = Reservation(
        table_id=res_in.table_id,
        customer_id=res_in.customer_id,
        start_time=res_in.start_time,
        end_time=res_in.end_time,
        guest_count=res_in.guest_count,
        status="PENDING"
    )
    try:
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database constraint violation: {str(e)}")

def update_reservation(db: Session, reservation_id: uuid.UUID, res_in: ReservationUpdate) -> Reservation:
    reservation = get_reservation_by_id(db, reservation_id)

    target_table_id = res_in.table_id if res_in.table_id is not None else reservation.table_id
    target_start = res_in.start_time if res_in.start_time is not None else reservation.start_time
    target_end = res_in.end_time if res_in.end_time is not None else reservation.end_time
    target_guests = res_in.guest_count if res_in.guest_count is not None else reservation.guest_count

    table = db.query(TableEntity).filter(TableEntity.id == target_table_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if target_guests <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Guest count must be greater than zero")
    if target_guests > table.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Guest count ({target_guests}) exceeds table capacity ({table.capacity})"
        )

    if target_end <= target_start:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End time must be after start time")

    new_status = res_in.status.upper() if res_in.status else reservation.status
    allowed_statuses = {"PENDING", "CONFIRMED", "CANCELLED", "NO_SHOW", "COMPLETED"}
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of {allowed_statuses}"
        )

    if new_status in {"PENDING", "CONFIRMED"}:
        if check_reservation_overlap(db, target_table_id, target_start, target_end, exclude_id=reservation.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Table is already reserved for this time window"
            )

    reservation.table_id = target_table_id
    reservation.start_time = target_start
    reservation.end_time = target_end
    reservation.guest_count = target_guests
    reservation.status = new_status

    try:
        db.commit()
        db.refresh(reservation)
        return reservation
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database constraint violation: {str(e)}")

def update_reservation_status(db: Session, reservation_id: uuid.UUID, new_status: str) -> Reservation:
    status_clean = new_status.upper()
    allowed_statuses = {"PENDING", "CONFIRMED", "CANCELLED", "NO_SHOW", "COMPLETED"}
    if status_clean not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{new_status}'. Allowed: {allowed_statuses}"
        )
    reservation = get_reservation_by_id(db, reservation_id)
    reservation.status = status_clean
    try:
        db.commit()
        db.refresh(reservation)
        return reservation
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database constraint violation: {str(e)}")

def delete_reservation(db: Session, reservation_id: uuid.UUID) -> bool:
    reservation = get_reservation_by_id(db, reservation_id)
    from app.models.dining import DiningSession
    db.query(DiningSession).filter(DiningSession.reservation_id == reservation.id).update({"reservation_id": None})
    db.delete(reservation)
    db.commit()
    return True

