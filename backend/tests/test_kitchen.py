import pytest
from sqlalchemy.exc import IntegrityError
from app.models.kitchen import KitchenTicket, KitchenTicketItem
from app.models.orders import OrderItem

def test_duplicate_kitchen_ticket_item(db, test_order, test_menu_item):
    order_item = OrderItem(
        order_id=test_order.id,
        item_id=test_menu_item.id,
        quantity=1,
        unit_price=10.00
    )
    db.add(order_item)
    db.commit()

    ticket = KitchenTicket(order_id=test_order.id, status='PENDING')
    db.add(ticket)
    db.commit()

    kti1 = KitchenTicketItem(ticket_id=ticket.id, order_item_id=order_item.id, status='PENDING')
    db.add(kti1)
    db.commit()

    kti2 = KitchenTicketItem(ticket_id=ticket.id, order_item_id=order_item.id, status='PENDING')
    db.add(kti2)
    with pytest.raises(IntegrityError) as exc_info:
        db.commit()
    assert "uq_kitchen_ticket_item" in str(exc_info.value)
