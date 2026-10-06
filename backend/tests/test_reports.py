import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_database_views_exist_and_queryable(db):
    # Test all 6 reporting views created in database/reports.sql
    views = [
        "view_available_tables",
        "view_daily_revenue",
        "view_item_sales",
        "view_waiter_performance",
        "view_kitchen_delays",
        "view_discount_usage"
    ]
    for view_name in views:
        result = db.execute(text(f"SELECT * FROM {view_name} LIMIT 5"))
        # Should execute without throwing error
        assert result is not None

def test_dashboard_summary_endpoint(client):
    res = client.get("/api/v1/reports/dashboard-summary")
    assert res.status_code == 200
    data = res.json()
    assert "tables" in data
    assert "available" in data["tables"]
    assert "occupied" in data["tables"]
    assert "active_sessions" in data
    assert "today_revenue" in data

def test_daily_revenue_report_endpoint(client):
    res = client.get("/api/v1/reports/daily-revenue")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_item_sales_report_endpoint(client):
    res = client.get("/api/v1/reports/item-sales")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_table_turnover_report_endpoint(client):
    res = client.get("/api/v1/reports/table-turnover")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_payment_methods_report_endpoint(client):
    res = client.get("/api/v1/reports/payment-methods")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
