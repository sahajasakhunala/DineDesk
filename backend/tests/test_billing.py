import pytest
from sqlalchemy.exc import IntegrityError
from app.models.billing import Bill, BillItem
from app.models.orders import OrderItem

def test_bill_total_negative(db, test_session):
    bill = Bill(
        session_id=test_session.id,
        subtotal=100.0,
        tax_amount=10.0,
        total_amount=-5.0, # Invalid
        status='UNPAID'
    )
    db.add(bill)
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "chk_bill_total" in str(exc_info.value)

def test_bill_item_total_price_calculated(db, test_session, test_order, test_menu_item):
    # Setup order item
    order_item = OrderItem(order_id=test_order.id, item_id=test_menu_item.id, quantity=2, unit_price=10.00)
    db.add(order_item)
    db.commit()
    
    # Setup bill
    bill = Bill(session_id=test_session.id, subtotal=20, tax_amount=2, total_amount=22, status='UNPAID')
    db.add(bill)
    db.commit()

    # Create bill item without total_price
    bill_item = BillItem(
        bill_id=bill.id,
        order_item_id=order_item.id,
        item_name_snapshot="Steak",
        quantity=3,
        unit_price=15.00
    )
    db.add(bill_item)
    db.commit()
    db.refresh(bill_item)
    
    assert float(bill_item.total_price) == 45.00
