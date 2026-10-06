"""
DineDesk SQLite Database Query Tool
Run this script to inspect all database tables, floor seating tables, reservations, and sessions:
    python backend/view_tables.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "dinedesk.db")

def print_separator(title=""):
    print("\n" + "=" * 80)
    if title:
        print(f" {title.upper()}")
        print("=" * 80)

def run_query(cur, title, query, params=()):
    print_separator(title)
    print(f"SQL Query:\n  {query.strip()}\n")
    cur.execute(query, params)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description] if cur.description else []
    
    if not rows:
        print("  (0 rows returned)")
        return
    
    # Calculate column widths
    col_widths = [len(c) for c in cols]
    for row in rows:
        for idx, val in enumerate(row):
            str_val = str(val) if val is not None else "NULL"
            col_widths[idx] = max(col_widths[idx], len(str_val))
    
    # Print Header
    header = " | ".join(cols[i].ljust(col_widths[i]) for i in range(len(cols)))
    divider = "-+-".join("-" * col_widths[i] for i in range(len(cols)))
    print("  " + header)
    print("  " + divider)
    
    # Print Rows
    for row in rows:
        row_str = " | ".join((str(val) if val is not None else "NULL").ljust(col_widths[i]) for i, val in enumerate(row))
        print("  " + row_str)
    
    print(f"\n  Total Records: {len(rows)}")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Show all SQLite Schema Tables
    run_query(
        cur,
        "1. All SQLite Database Tables (Schema Overview)",
        """
        SELECT 
            name AS table_name,
            type AS object_type
        FROM sqlite_master 
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name ASC;
        """
    )

    # 2. Show Restaurant Dining Tables (Floor Plan)
    run_query(
        cur,
        "2. Restaurant Dining Tables (table_entity & dining_area)",
        """
        SELECT 
            t.table_number,
            COALESCE(a.name, 'Main Floor') AS area_name,
            t.capacity AS max_guests,
            CASE WHEN t.is_active = 1 THEN 'ACTIVE' ELSE 'INACTIVE' END AS table_status
        FROM table_entity t
        LEFT JOIN dining_area a ON t.area_id = a.id
        ORDER BY t.table_number ASC;
        """
    )

    # 3. Show Reservations Ledger with Booked Table Details
    run_query(
        cur,
        "3. Live Table Reservations Ledger (Booked Table, Area & Slot)",
        """
        SELECT 
            SUBSTR(r.id, 1, 8) AS res_ref,
            c.first_name || ' ' || c.last_name AS customer_name,
            c.phone AS contact_phone,
            t.table_number,
            COALESCE(a.name, 'Main Floor') AS area_name,
            t.capacity AS table_capacity,
            r.guest_count AS booked_guests,
            r.start_time,
            r.end_time,
            r.status
        FROM reservation r
        JOIN customer c ON r.customer_id = c.id
        JOIN table_entity t ON r.table_id = t.id
        LEFT JOIN dining_area a ON t.area_id = a.id
        ORDER BY r.start_time ASC;
        """
    )

    # 4. Show Active & Past Dining Sessions
    run_query(
        cur,
        "4. Dining Sessions on Floor (dining_session)",
        """
        SELECT 
            SUBSTR(s.id, 1, 8) AS session_id,
            t.table_number,
            COALESCE(c.first_name || ' ' || c.last_name, 'Walk-in Guest') AS customer,
            s.guest_count,
            s.status,
            s.start_time,
            s.end_time
        FROM dining_session s
        JOIN table_entity t ON s.table_id = t.id
        LEFT JOIN customer c ON s.customer_id = c.id
        ORDER BY s.start_time DESC;
        """
    )

    # 5. Show Registered Customers
    run_query(
        cur,
        "5. Registered Customers (customer)",
        """
        SELECT 
            SUBSTR(id, 1, 8) AS customer_id,
            first_name || ' ' || last_name AS full_name,
            phone,
            COALESCE(email, 'None') AS email
        FROM customer
        ORDER BY created_at DESC
        LIMIT 10;
        """
    )

    # 6. Show Billing & Cashier Settlements
    run_query(
        cur,
        "6. Invoices & Billing Settlements (bill & payment)",
        """
        SELECT 
            SUBSTR(b.id, 1, 8) AS bill_ref,
            b.total_amount AS total_inr,
            b.status AS bill_status,
            p.payment_method,
            p.amount AS paid_amount,
            p.status AS payment_status
        FROM bill b
        LEFT JOIN payment p ON p.bill_id = b.id
        ORDER BY b.created_at DESC;
        """
    )

    # 7. Show Kitchen Display Tickets & Order Items
    run_query(
        cur,
        "7. Kitchen Display Tickets & Placed Orders (kitchen_ticket & order_item)",
        """
        SELECT 
            SUBSTR(kt.id, 1, 8) AS ticket_ref,
            t.table_number,
            kt.status AS ticket_status,
            m.name AS item_name,
            oi.quantity AS qty,
            kti.status AS item_status,
            COALESCE(oi.special_requests, 'None') AS chef_notes
        FROM kitchen_ticket kt
        JOIN customer_order co ON kt.order_id = co.id
        JOIN dining_session s ON co.session_id = s.id
        JOIN table_entity t ON s.table_id = t.id
        JOIN kitchen_ticket_item kti ON kt.id = kti.ticket_id
        JOIN order_item oi ON kti.order_item_id = oi.id
        JOIN menu_item m ON oi.item_id = m.id
        ORDER BY kt.created_at DESC, t.table_number ASC;
        """
    )

    conn.close()
    print_separator("Query Inspection Completed Successfully")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        custom_query = " ".join(sys.argv[1:])
        if not os.path.exists(DB_PATH):
            print(f"Database not found at: {DB_PATH}")
            sys.exit(1)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        run_query(cur, "Custom SQL Query", custom_query)
        conn.close()
    else:
        main()
