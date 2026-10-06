"""
Interactive SQLite Shell for DineDesk
Enables full interactive SQL query execution with multi-line queries,
dot-commands (.tables, .schema, .exit), and tabular results formatting.
"""

import os
import sys
import sqlite3

DEFAULT_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "dinedesk.db"))

def print_table(cur, cols, rows):
    if not rows:
        print("(0 rows returned)")
        return

    col_widths = [len(c) for c in cols]
    for row in rows:
        for idx, val in enumerate(row):
            str_val = str(val) if val is not None else "NULL"
            col_widths[idx] = max(col_widths[idx], len(str_val))

    header = " | ".join(cols[i].ljust(col_widths[i]) for i in range(len(cols)))
    divider = "-+-".join("-" * col_widths[i] for i in range(len(cols)))
    print(header)
    print(divider)
    for row in rows:
        row_str = " | ".join((str(val) if val is not None else "NULL").ljust(col_widths[i]) for i, val in enumerate(row))
        print(row_str)
    print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''})\n")

def run_sql(conn, sql):
    cur = conn.cursor()
    try:
        cur.execute(sql)
        if cur.description:
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            print_table(cur, cols, rows)
        else:
            conn.commit()
            print(f"Statement executed successfully. (Rows affected: {cur.rowcount})\n")
    except Exception as e:
        print(f"Error: {e}\n")

def interactive_shell(db_path):
    print("=" * 60)
    print(" DineDesk SQLite Interactive Terminal")
    print(f" Database: {db_path}")
    print(" Enter SQL queries ending with a semicolon (;)")
    print(" Special commands: .tables | .schema [tbl] | .quit | .help")
    print("=" * 60 + "\n")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    buffer = []
    while True:
        try:
            prompt = "sqlite> " if not buffer else "   ...> "
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting DineDesk SQLite Console.")
            break

        stripped = line.strip()
        if not buffer and stripped.startswith("."):
            cmd_parts = stripped.split()
            cmd = cmd_parts[0].lower()
            if cmd in [".exit", ".quit", ".q"]:
                print("Goodbye.")
                break
            elif cmd == ".tables":
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
                tables = [r[0] for r in cur.fetchall()]
                print("  " + "  ".join(tables) + "\n")
            elif cmd == ".schema":
                if len(cmd_parts) > 1:
                    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (cmd_parts[1],))
                else:
                    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                for r in cur.fetchall():
                    if r[0]:
                        print(r[0] + ";\n")
            elif cmd == ".help":
                print("Commands:")
                print("  .tables        List all tables in database")
                print("  .schema [name] Show SQL schema definition")
                print("  .quit / .exit  Exit terminal")
                print("  SELECT ... ;   Execute any SQL query\n")
            else:
                print(f"Unknown command: {cmd}. Type .help for available commands.\n")
            continue

        if not stripped and not buffer:
            continue

        buffer.append(line)
        if stripped.endswith(";"):
            full_sql = "\n".join(buffer)
            buffer = []
            run_sql(conn, full_sql)

    conn.close()

def main():
    db_path = DEFAULT_DB
    args = sys.argv[1:]

    # If first arg is a file ending in .db, use it
    if args and (args[0].endswith(".db") or os.path.exists(args[0])):
        db_path = os.path.abspath(args[0])
        args = args[1:]

    if not os.path.exists(db_path):
        # Check relative to backend
        alt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", db_path))
        if os.path.exists(alt_path):
            db_path = alt_path

    if args:
        # Run one-off query
        query = " ".join(args)
        conn = sqlite3.connect(db_path)
        run_sql(conn, query)
        conn.close()
    else:
        interactive_shell(db_path)

if __name__ == "__main__":
    main()
