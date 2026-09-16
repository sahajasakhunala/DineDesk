import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError, DataError
from app.models.dining import Reservation
from sqlalchemy import text

def test_reservation_end_before_start(db, test_table, test_customer):
    now = datetime.now()
    res = Reservation(
        table_id=test_table.id,
        customer_id=test_customer.id,
        start_time=now,
        end_time=now - timedelta(hours=1), # End <= Start
        guest_count=2,
        status='PENDING'
    )
    db.add(res)
    
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "chk_reservation_time" in str(exc_info.value)

def test_reservation_guest_count_zero(db, test_table, test_customer):
    now = datetime.now()
    res = Reservation(
        table_id=test_table.id,
        customer_id=test_customer.id,
        start_time=now,
        end_time=now + timedelta(hours=1),
        guest_count=0, # Invalid
        status='PENDING'
    )
    db.add(res)
    
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "chk_reservation_guests" in str(exc_info.value)

def test_reservation_overlapping_active(db, test_table, test_customer):
    # Reservation A: 10:00 to 12:00
    base_time = datetime(2026, 1, 1, 10, 0, 0)
    res_a = Reservation(
        table_id=test_table.id,
        customer_id=test_customer.id,
        start_time=base_time,
        end_time=base_time + timedelta(hours=2),
        guest_count=2,
        status='CONFIRMED'
    )
    db.add(res_a)
    db.commit()

    # Reservation B: 11:00 to 13:00 (Overlaps A)
    res_b = Reservation(
        table_id=test_table.id,
        customer_id=test_customer.id,
        start_time=base_time + timedelta(hours=1),
        end_time=base_time + timedelta(hours=3),
        guest_count=2,
        status='PENDING'
    )
    db.add(res_b)

    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "excl_reservation_overlap" in str(exc_info.value)

def test_cancelled_overlapping_reservation(db, test_table, test_customer):
    # Reservation A: 10:00 to 12:00 (CANCELLED)
    base_time = datetime(2026, 1, 1, 10, 0, 0)
    res_a = Reservation(
        table_id=test_table.id,
        customer_id=test_customer.id,
        start_time=base_time,
        end_time=base_time + timedelta(hours=2),
        guest_count=2,
        status='CANCELLED' # Should not trigger overlap exclusion
    )
    db.add(res_a)
    db.commit()

    # Reservation B: 11:00 to 13:00 (Overlaps A, but A is cancelled)
    res_b = Reservation(
        table_id=test_table.id,
        customer_id=test_customer.id,
        start_time=base_time + timedelta(hours=1),
        end_time=base_time + timedelta(hours=3),
        guest_count=2,
        status='CONFIRMED'
    )
    db.add(res_b)
    db.commit() # Should succeed
    assert res_b.id is not None
