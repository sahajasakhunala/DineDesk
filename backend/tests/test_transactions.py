import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models.restaurant import TableEntity
from app.models.dining import DiningSession, Reservation
from app.models.orders import CustomerOrder, OrderItem
from app.models.kitchen import KitchenTicket
from app.models.billing import Bill, Payment
from app.services.order_service import create_order
from app.services.reservation_service import create_reservation
from app.schemas.dining import ReservationCreate
from app.services.billing_service import process_payment, generate_bill_for_session

def test_atomic_order_and_kitchen_ticket_creation(db, test_session, test_user, test_menu_item):
    initial_orders = db.query(CustomerOrder).count()
    initial_tickets = db.query(KitchenTicket).count()

    order = create_order(
        db=db,
        session_id=test_session.id,
        user_id=test_user.id,
        items_data=[
            {
                "item_id": test_menu_item.id,
                "quantity": 3,
                "special_requests": "Mild spices"
            }
        ]
    )
    assert order.id is not None
    assert db.query(CustomerOrder).count() == initial_orders + 1
    assert db.query(KitchenTicket).count() == initial_tickets + 1
    assert order.kitchen_ticket is not None
    assert order.kitchen_ticket.status == "PENDING"
    assert len(order.kitchen_ticket.items) == 1

def test_order_creation_rollback_on_invalid_item(db, test_session, test_user, test_menu_item):
    initial_orders = db.query(CustomerOrder).count()
    initial_tickets = db.query(KitchenTicket).count()

    fake_item_id = uuid.uuid4()
    with pytest.raises(HTTPException) as exc_info:
        create_order(
            db=db,
            session_id=test_session.id,
            user_id=test_user.id,
            items_data=[
                {"item_id": test_menu_item.id, "quantity": 1},
                {"item_id": fake_item_id, "quantity": 2} # Invalid
            ]
        )
    assert exc_info.value.status_code == 404
    # Ensure atomic rollback: no order or ticket was persisted
    assert db.query(CustomerOrder).count() == initial_orders
    assert db.query(KitchenTicket).count() == initial_tickets

def test_atomic_payment_rollback_on_excess(db, test_session, test_order, test_menu_item):
    oi = OrderItem(order_id=test_order.id, item_id=test_menu_item.id, quantity=1, unit_price=Decimal("100.00"))
    db.add(oi)
    db.commit()

    bill = generate_bill_for_session(db, test_session.id)
    # Total is 105.00
    initial_payments = db.query(Payment).count()

    with pytest.raises(HTTPException) as exc_info:
        process_payment(db, bill.id, Decimal("200.00"), "CASH")
    assert exc_info.value.status_code == 400
    assert "exceeds" in str(exc_info.value.detail)
    assert db.query(Payment).count() == initial_payments

def test_reservation_overlap_transactional_rejection(db, test_table, test_customer):
    now = datetime.now(timezone.utc) + timedelta(days=2)
    start = now
    end = now + timedelta(hours=2)

    # First reservation succeeds
    r1 = create_reservation(
        db,
        ReservationCreate(
            table_id=test_table.id,
            customer_id=test_customer.id,
            start_time=start,
            end_time=end,
            guest_count=2
        )
    )
    assert r1.status == "PENDING"

    # Conflicting reservation overlaps window
    with pytest.raises(HTTPException) as exc_info:
        create_reservation(
            db,
            ReservationCreate(
                table_id=test_table.id,
                customer_id=test_customer.id,
                start_time=start + timedelta(minutes=30),
                end_time=end + timedelta(hours=1),
                guest_count=2
            )
        )
    assert exc_info.value.status_code == 409
