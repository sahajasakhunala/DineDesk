import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.models.restaurant import Branch, DiningArea, TableEntity
from app.models.menu import MenuCategory, MenuItem
from app.models.users import Role, UserAccount, Customer
from app.models.dining import DiningSession

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_api_customer_registration(client):
    res = client.post("/api/v1/auth/customer", json={
        "name": "Test Customer",
        "phone": "9999900001",
        "email": "testcust@example.com"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Customer"
    assert data["phone"] == "9999900001"

def test_api_restaurant_tables_and_occupancy(client, test_table):
    res = client.get("/api/v1/restaurant/tables")
    assert res.status_code == 200
    tables = res.json()
    assert len(tables) >= 1
    found = next((t for t in tables if t["table_number"] == test_table.table_number), None)
    assert found is not None
    assert found["status"] == "AVAILABLE"

def test_api_reservation_lifecycle(client, test_table, test_customer):
    now = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = now.isoformat()
    end_time = (now + timedelta(hours=2)).isoformat()

    # Create reservation
    res = client.post("/api/v1/reservations", json={
        "table_id": str(test_table.id),
        "customer_id": str(test_customer.id),
        "start_time": start_time,
        "end_time": end_time,
        "guest_count": 2
    })
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["status"] == "PENDING"
    res_id = res_data["id"]

    # Overlapping reservation on same table should conflict (409)
    overlap_res = client.post("/api/v1/reservations", json={
        "table_id": str(test_table.id),
        "customer_id": str(test_customer.id),
        "start_time": (now + timedelta(minutes=30)).isoformat(),
        "end_time": (now + timedelta(hours=3)).isoformat(),
        "guest_count": 2
    })
    assert overlap_res.status_code == 409

    # Update status to CONFIRMED
    patch_res = client.patch(f"/api/v1/reservations/{res_id}/status", json={"status": "CONFIRMED"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "CONFIRMED"

def test_api_ordering_and_kitchen_sync(client, test_session, test_user, test_menu_item):
    # Place order
    res = client.post("/api/v1/orders", json={
        "session_id": str(test_session.id),
        "user_id": str(test_user.id),
        "items": [
            {
                "item_id": str(test_menu_item.id),
                "quantity": 2,
                "special_requests": "Extra spicy"
            }
        ]
    })
    assert res.status_code == 200
    order_data = res.json()
    assert order_data["status"] == "PLACED"
    ticket_id = order_data["kitchen_ticket_id"]
    assert ticket_id is not None

    # Check kitchen ticket display
    k_res = client.get("/api/v1/kitchen/tickets")
    assert k_res.status_code == 200
    tickets = k_res.json()
    target_ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    assert target_ticket is not None
    assert target_ticket["status"] == "PENDING"

    # Start kitchen preparation
    start_res = client.post(f"/api/v1/kitchen/tickets/{ticket_id}/start")
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "IN_PROGRESS"

    # Mark ticket ready
    ready_res = client.post(f"/api/v1/kitchen/tickets/{ticket_id}/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "READY"

def test_api_billing_and_payment_flow(client, test_session, test_user, test_menu_item):
    # Place an order in the session first
    client.post("/api/v1/orders", json={
        "session_id": str(test_session.id),
        "user_id": str(test_user.id),
        "items": [
            {
                "item_id": str(test_menu_item.id),
                "quantity": 2
            }
        ]
    })

    # Generate bill
    res = client.post(f"/api/v1/billing/sessions/{test_session.id}/generate")
    assert res.status_code == 200
    bill = res.json()
    # 2 * 25.00 = 50.00 subtotal, 2.50 tax (5%), total 52.50
    assert bill["subtotal"] == 50.0
    assert bill["tax_amount"] == 2.5
    assert bill["total_amount"] == 52.5
    assert bill["status"] == "UNPAID"

    # Process payment
    pay_res = client.post(f"/api/v1/billing/bills/{bill['id']}/payments", json={
        "amount": 52.50,
        "payment_method": "ONLINE",
        "transaction_ref": f"TX_{datetime.now().timestamp()}"
    })
    assert pay_res.status_code == 200
    pay_data = pay_res.json()
    assert pay_data["bill"]["status"] == "PAID"
    assert pay_data["bill"]["remaining_balance"] == 0.0

def test_api_dashboard_reports(client, test_table):
    res = client.get("/api/v1/reports/dashboard-summary")
    assert res.status_code == 200
    data = res.json()
    assert "tables" in data
    assert "active_sessions" in data
    assert "total_revenue" in data
