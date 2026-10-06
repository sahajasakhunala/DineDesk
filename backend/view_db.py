import sqlite3

con = sqlite3.connect('backend/dinedesk.db')
cur = con.cursor()

# 1. Database Schema Tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
db_tables = [r[0] for r in cur.fetchall()]

print("=" * 65)
print(f"DATABASE TABLES IN dinedesk.db (Total: {len(db_tables)})")
print("=" * 65)
for t in db_tables:
    cur.execute(f'SELECT count(*) FROM "{t}"')
    cnt = cur.fetchone()[0]
    print(f"  • {t:<28} | {cnt:>4} rows")

# 2. Restaurant Dining Tables
print("\n" + "=" * 65)
print("RESTAURANT SEATING TABLES (Floor Plan)")
print("=" * 65)
cur.execute('''
    SELECT t.table_number, COALESCE(a.name, 'Unassigned'), t.capacity, t.is_active 
    FROM table_entity t
    LEFT JOIN dining_area a ON t.area_id = a.id
    ORDER BY t.table_number;
''')
tables = cur.fetchall()
for r in tables:
    status_str = "Active" if r[3] else "Inactive"
    print(f"  • Table {r[0]:<6} | Area: {r[1]:<24} | Max {r[2]:>2} Guests | Status: {status_str}")

print("=" * 65)
con.close()
