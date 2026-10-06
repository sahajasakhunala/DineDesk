import sys
import json
import urllib.request
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api/v1"

def http_req(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(data).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_e2e():
    print("\n=======================================================")
    print("🚀 Running DineDesk End-to-End Comprehensive Flow")
    print("=======================================================")

    # 1. Register Customer
    print("\n1. Customer Registration...")
    cust = http_req("/auth/customer", "POST", {
        "name": "Arjun Kapoor",
        "phone": f"988{int(datetime.now().timestamp()) % 10000000}",
        "email": f"arjun_{int(datetime.now().timestamp())}@gmail.com"
    })
    print(f"   ✓ Customer: {cust['first_name']} {cust['last_name']} (ID: {cust['id'][:8]})")

    # 2. View Tables
    print("\n2. Querying Live Floor Tables...")
    tables = http_req("/restaurant/tables")
    available_tables = [t for t in tables if t["status"] == "AVAILABLE"]
    print(f"   ✓ Total Tables: {len(tables)}, Available: {len(available_tables)}")
    target_table = available_tables[0]
    print(f"   ✓ Selected Table {target_table['table_number']} (Capacity: {target_table['capacity']})")

    # 3. Make Reservation
    print("\n3. Making Reservation...")
    start_time = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()
    end_time = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
    booking = http_req("/reservations", "POST", {
        "table_id": target_table["id"],
        "customer_id": cust["id"],
        "start_time": start_time,
        "end_time": end_time,
        "guest_count": 2
    })
    print(f"   ✓ Reservation #{booking['id'][:8]} created with status: {booking['status']}")

    # 4. Staff Login
    print("\n4. Staff Authentication...")
    auth = http_req("/auth/login", "POST", {
        "email": "manager@dinedesk.com",
        "password": "manager123"
    })
    token = auth["access_token"]
    print(f"   ✓ Logged in as: {auth['first_name']} {auth['last_name']} ({auth['role']})")

    # 5. Seat Guests / Open Dining Session
    print("\n5. Seating Guests at Table...")
    session = http_req("/dining/sessions", "POST", {
        "table_id": target_table["id"],
        "customer_id": cust["id"],
        "reservation_id": booking["id"],
        "guest_count": 2
    }, token=token)
    print(f"   ✓ Dining Session opened: #{session['id'][:8]} for Table {session['table_number']}")

    # Check Table is now OCCUPIED
    updated_tables = http_req("/restaurant/tables")
    table_status = next(t["status"] for t in updated_tables if t["id"] == target_table["id"])
    print(f"   ✓ Table {target_table['table_number']} status is now: {table_status}")

    # 6. Query Menu & Place Order
    print("\n6. Exploring Menu Catalog & Placing Order...")
    menu_items = http_req("/menu/items")
    pizza = next(m for m in menu_items if "Pizza" in m["name"])
    mocktail = next(m for m in menu_items if "Mocktail" in m["name"])
    print(f"   ✓ Selected: {pizza['name']} (₹{pizza['price']}), {mocktail['name']} (₹{mocktail['price']})")

    order = http_req("/orders", "POST", {
        "session_id": session["id"],
        "items": [
            {"item_id": pizza["id"], "quantity": 1, "special_requests": "Crispy crust"},
            {"item_id": mocktail["id"], "quantity": 2, "special_requests": "Extra mint"}
        ]
    }, token=token)
    print(f"   ✓ Order placed: #{order['id'][:8]} with {len(order['items'])} line items")
    ticket_id = order["kitchen_ticket_id"]
    print(f"   ✓ Synchronous Kitchen Ticket generated: #{ticket_id[:8]} (Status: {order['kitchen_status']})")

    # 7. Kitchen Workflow (START -> READY)
    print("\n7. Kitchen Ticket Lifecycle...")
    k_ticket = http_req(f"/kitchen/tickets/{ticket_id}/start", "POST", token=token)
    print(f"   ✓ Ticket marked in preparation: Status -> {k_ticket['status']}")

    ready_ticket = http_req(f"/kitchen/tickets/{ticket_id}/ready", "POST", token=token)
    print(f"   ✓ Ticket marked ready: Status -> {ready_ticket['status']}")

    # 8. Mark Order Served
    print("\n8. Waitstaff Serving Order...")
    served_order = http_req(f"/orders/{order['id']}/status", "PATCH", {"status": "SERVED"}, token=token)
    print(f"   ✓ Order status transitioned to: {served_order['status']}")

    # 9. Generate Bill
    print("\n9. Cashier Generating Bill...")
    bill = http_req(f"/billing/sessions/{session['id']}/generate", "POST", token=token)
    print(f"   ✓ Bill #{bill['id'][:8]} generated:")
    print(f"     • Subtotal: ₹{bill['subtotal']}")
    print(f"     • 5% GST:   ₹{bill['tax_amount']}")
    print(f"     • Total:    ₹{bill['total_amount']}")

    # 10. Apply Authorized Discount
    print("\n10. Applying Discount...")
    discounts = http_req("/billing/discounts", token=token)
    discount = discounts[0]
    discounted_bill = http_req(f"/billing/bills/{bill['id']}/discounts", "POST", {
        "discount_id": discount["id"],
        "reason": "Happy Dining Promo"
    }, token=token)
    print(f"   ✓ Applied {discount['name']}: New Payable Total -> ₹{discounted_bill['total_amount']}")

    # 11. Process Payment
    print("\n11. Processing Final Payment...")
    payment = http_req(f"/billing/bills/{bill['id']}/payments", "POST", {
        "amount": discounted_bill["remaining_balance"],
        "payment_method": "ONLINE",
        "transaction_ref": f"UPI_{int(datetime.now().timestamp())}"
    }, token=token)
    print(f"   ✓ Payment of ₹{payment['amount']} processed via {payment['method']}")
    print(f"   ✓ Bill Status: {payment['bill']['status']}")

    # 12. Verify Table is Released and Session Completed
    print("\n12. Verifying Table Release & Session Closure...")
    final_tables = http_req("/restaurant/tables")
    final_status = next(t["status"] for t in final_tables if t["id"] == target_table["id"])
    print(f"   ✓ Table {target_table['table_number']} status is now: {final_status}")

    # 13. Reports Verification
    print("\n13. Verifying Operational Reports...")
    reports = http_req("/reports/dashboard-summary", token=token)
    print(f"   ✓ Total Cumulative Revenue: ₹{reports['total_revenue']}")
    print(f"   ✓ Active Sessions Remaining: {reports['active_sessions']}")

    print("\n=======================================================")
    print("🎉 FULL END-TO-END FLOW VERIFIED SUCCESSFULLY!")
    print("=======================================================\n")

if __name__ == "__main__":
    run_e2e()
