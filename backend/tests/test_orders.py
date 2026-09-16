import pytest
from sqlalchemy.exc import IntegrityError
from app.models.orders import CustomerOrder, OrderItem
from app.models.dining import DiningSession
from datetime import datetime



def test_order_quantity_zero(db, test_order, test_menu_item):
    item = OrderItem(
        order_id=test_order.id,
        item_id=test_menu_item.id,
        quantity=0, # Invalid
        unit_price=test_menu_item.current_price
    )
    db.add(item)
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "chk_order_item_qty" in str(exc_info.value)

def test_negative_order_price(db, test_order, test_menu_item):
    item = OrderItem(
        order_id=test_order.id,
        item_id=test_menu_item.id,
        quantity=1,
        unit_price=-5.00 # Invalid
    )
    db.add(item)
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "chk_order_item_price" in str(exc_info.value)
