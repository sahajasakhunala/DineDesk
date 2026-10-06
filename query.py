import sqlite3
import os

# Connect to database
db_path = os.path.join(os.path.dirname(__file__), "backend", "dinedesk.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

query = """
SELECT 
    SUBSTR(r.id, 1, 8) AS res_ref,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.phone AS contact_phone,
    t.table_number,
    COALESCE(a.name, 'Main Dining Hall') AS area_name,
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

cur.execute(query)
rows = cur.fetchall()
cols = [desc[0] for desc in cur.description]

if not rows:
    print("No reservation records found.")
else:
    col_widths = [len(c) for c in cols]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val) if val is not None else "NULL"))

    header = " | ".join(cols[i].ljust(col_widths[i]) for i in range(len(cols)))
    divider = "-+-".join("-" * col_widths[i] for i in range(len(cols)))
    
    print("\n" + "=" * len(header))
    print(" DINEDESK LIVE RESERVATIONS TABLE")
    print("=" * len(header))
    print(header)
    print(divider)
    for row in rows:
        row_str = " | ".join((str(val) if val is not None else "NULL").ljust(col_widths[i]) for i, val in enumerate(row))
        print(row_str)
    print("=" * len(header))
    print(f"Total Rows: {len(rows)}\n")

conn.close()
