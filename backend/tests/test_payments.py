import pytest
from sqlalchemy.exc import IntegrityError
from app.models.billing import Payment

def test_payment_amount_zero_or_less(db, test_bill):
    payment = Payment(
        bill_id=test_bill.id,
        amount=0, # Invalid
        payment_method='CASH',
        status='COMPLETED'
    )
    db.add(payment)
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "chk_payment_amount" in str(exc_info.value)

def test_duplicate_transaction_reference(db, test_bill):
    payment1 = Payment(
        bill_id=test_bill.id,
        amount=50.0,
        payment_method='CARD',
        status='COMPLETED',
        transaction_ref="TXN-12345"
    )
    db.add(payment1)
    db.commit()

    payment2 = Payment(
        bill_id=test_bill.id,
        amount=60.0,
        payment_method='CARD',
        status='COMPLETED',
        transaction_ref="TXN-12345" # Duplicate
    )
    db.add(payment2)
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    # Check for either the unique constraint name or unique constraint violation in general
    assert "uq_" in str(exc_info.value) or "unique constraint" in str(exc_info.value).lower() or "payment_transaction_ref_key" in str(exc_info.value)
