import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.models.dining import DiningSession

def test_active_dining_session_overlap(db, test_table):
    base_time = datetime(2026, 1, 1, 18, 0, 0)
    
    session1 = DiningSession(
        table_id=test_table.id,
        start_time=base_time,
        end_time=None,
        guest_count=2,
        status='ACTIVE'
    )
    db.add(session1)
    db.commit()
    
    session2 = DiningSession(
        table_id=test_table.id,
        start_time=base_time + timedelta(hours=1),
        end_time=None,
        guest_count=2,
        status='ACTIVE'
    )
    db.add(session2)
    
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "excl_session_overlap" in str(exc_info.value)
