"""
DineDesk Schema & Data Demonstration Runner
Executes table creation (DDL), sample data insertion (DML), and displays results.
"""

import sqlite3
import os

DB_NAME = "demo_dinedesk.db"

def main():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    print("=" * 80)
    print("STEP 1: CREATING DATABASE TABLES (DDL)")
    print("=" * 80)

    ddl_queries = [
        """
        CREATE TABLE dining_area (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            is_active BOOLEAN DEFAULT 1
        );
        """,
        """
        CREATE TABLE table_entity (
            id VARCHAR(36) PRIMARY KEY,
            area_id VARCHAR(36) REFERENCES dining_area(id) ON DELETE SET NULL,
            table_number VARCHAR(10) NOT NULL UNIQUE,
            capacity INTEGER NOT NULL CHECK (capacity > 0),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE customer (
            id VARCHAR(36) PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            phone VARCHAR(20) NOT NULL UNIQUE,
            email VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE reservation (
            id VARCHAR(36) PRIMARY KEY,
            table_id VARCHAR(36) NOT NULL REFERENCES table_entity(id) ON DELETE CASCADE,
            customer_id VARCHAR(36) NOT NULL REFERENCES customer(id) ON DELETE CASCADE,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            guest_count INTEGER NOT NULL CHECK (guest_count > 0),
            status VARCHAR(20) DEFAULT 'CONFIRMED',
            special_notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]

    for q in ddl_queries:
        cur.execute(q)
    conn.commit()
    print("Tables created successfully: dining_area, table_entity, customer, reservation\n")

    print("=" * 80)
    print("STEP 2: INSERTING DATA (DML)")
    print("=" * 80)

    cur.execute("""
    INSERT INTO dining_area (id, name, description) VALUES
    ('AREA-01', 'Romantic Terrace (Rooftop)', 'Sunset ambiance with panoramic city skyline views'),
    ('AREA-02', 'Main Dining Hall', 'Opulent crystal chandeliers and live classical lounge acoustics'),
    ('AREA-03', 'Family & Kids Lounge', 'Spacious plush seating with interactive dessert stations'),
    ('AREA-04', 'Chef''s Private Dining', 'Exclusive private suite featuring sommelier pairings');
    """)

    cur.execute("""
    INSERT INTO table_entity (id, area_id, table_number, capacity) VALUES
    ('TBL-R01', 'AREA-01', 'R01', 2),
    ('TBL-R02', 'AREA-01', 'R02', 2),
    ('TBL-R03', 'AREA-01', 'R03', 4),
    ('TBL-T01', 'AREA-02', 'T01', 4),
    ('TBL-T02', 'AREA-02', 'T02', 4),
    ('TBL-F01', 'AREA-03', 'F01', 6),
    ('TBL-P01', 'AREA-04', 'P01', 8);
    """)

    cur.execute("""
    INSERT INTO customer (id, first_name, last_name, phone, email) VALUES
    ('CUST-01', 'Sakhunala', 'Sahaja', '9154507776', 'sahaja@example.com'),
    ('CUST-02', 'Marcus', 'Vance', '9822334455', 'marcus@example.com');
    """)

    cur.execute("""
    INSERT INTO reservation (id, table_id, customer_id, start_time, end_time, guest_count, status, special_notes) VALUES
    ('RES-101', 'TBL-R03', 'CUST-01', '2026-10-06 19:30:00', '2026-10-06 21:30:00', 4, 'CONFIRMED', 'Window view requested');
    """)

    conn.commit()
    print("Sample records inserted successfully.\n")

    print("=" * 80)
    print("STEP 3: QUERY OUTPUT (SELECT)")
    print("=" * 80)

    def print_query(title, query):
        print(f"\n--- {title} ---")
        cur.execute(query)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        col_widths = [len(c) for c in cols]
        for row in rows:
            for idx, val in enumerate(row):
                col_widths[idx] = max(col_widths[idx], len(str(val) if val is not None else "NULL"))
        header = " | ".join(cols[i].ljust(col_widths[i]) for i in range(len(cols)))
        divider = "-+-".join("-" * col_widths[i] for i in range(len(cols)))
        print(header)
        print(divider)
        for row in rows:
            print(" | ".join((str(v) if v is not None else "NULL").ljust(col_widths[i]) for i, v in enumerate(row)))
        print(f"({len(rows)} rows)")

    print_query("1. Luxury Dining Areas", "SELECT id, name, description FROM dining_area;")
    print_query("2. Seating Tables with Area Names", """
        SELECT t.table_number, a.name AS area, t.capacity AS seats, t.is_active
        FROM table_entity t
        JOIN dining_area a ON t.area_id = a.id;
    """)
    print_query("3. Active Customer Reservations", """
        SELECT r.id AS res_id, c.first_name || ' ' || c.last_name AS customer, t.table_number, r.guest_count, r.start_time, r.status
        FROM reservation r
        JOIN customer c ON r.customer_id = c.id
        JOIN table_entity t ON r.table_id = t.id;
    """)

    conn.close()

if __name__ == "__main__":
    main()
