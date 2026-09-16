import pytest
from sqlalchemy.exc import IntegrityError
from app.models.billing import Discount, DiscountApplication, Bill



def test_invalid_discount_percentage(db):
    discount = Discount(
        name="Invalid 150% off",
        discount_type='PERCENTAGE',
        value=150.00 # Invalid, max 100
    )
    db.add(discount)
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "chk_discount_value" in str(exc_info.value)

def test_discount_app_both_amount_and_percentage(db, test_bill, test_user):
    discount = Discount(name="Test Discount", discount_type="FIXED", value=10)
    db.add(discount)
    db.commit()

    da = DiscountApplication(
        bill_id=test_bill.id,
        discount_id=discount.id,
        authorized_by_user_id=test_user.id,
        discount_amount=10.00,
        discount_percentage=10.00 # Both provided -> Error
    )
    db.add(da)
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "chk_da_exclusive" in str(exc_info.value)
