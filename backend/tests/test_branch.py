import pytest
from sqlalchemy.exc import IntegrityError
from app.models.restaurant import Branch, TableEntity

def test_valid_branch(db):
    branch = Branch(name="New Branch", address="456 New St", phone="555-0202")
    db.add(branch)
    db.commit()
    assert branch.id is not None

def test_duplicate_table_number_within_area(db, test_area):
    table1 = TableEntity(area_id=test_area.id, table_number="T10", capacity=4)
    db.add(table1)
    db.commit()

    table2 = TableEntity(area_id=test_area.id, table_number="T10", capacity=2)
    db.add(table2)
    
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "uq_table_entity_area_number" in str(exc_info.value)

def test_table_capacity_zero_or_less(db, test_area):
    table = TableEntity(area_id=test_area.id, table_number="T2", capacity=0)
    db.add(table)
    
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "chk_table_entity_capacity" in str(exc_info.value)
