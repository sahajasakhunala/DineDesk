import sqlite3
import sys
import os

def get_db_path():
    # Detect if run from DineDesk root or backend folder
    if os.path.exists("backend/dinedesk.db"):
        return "backend/dinedesk.db"
    elif os.path.exists("dinedesk.db"):
        return "dinedesk.db"
    elif os.path.exists("../backend/dinedesk.db"):
        return "../backend/dinedesk.db"
    return "backend/dinedesk.db"

import re

def clean_sql_input(text: str) -> str:
    # Strip common prompt prefixes if user copied them from terminal
    cleaned = re.sub(r'(dinedesk_sql\s*>\s*|\.{3}\s*>\s*)', ' ', text)
    return " ".join(cleaned.split()).strip()

def execute_query(query: str):
    query = clean_sql_input(query)
    if not query:
        return
    
    db_path = get_db_path()
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(query)
        
        upper_q = query.upper()
        if upper_q.startswith("SELECT") or upper_q.startswith("PRAGMA") or upper_q.startswith("EXPLAIN") or upper_q.startswith("WITH"):
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description] if cur.description else []
            
            if not rows:
                print("\n[Result]: Query returned 0 rows.\n")
                con.close()
                return
            
            # Calculate column widths
            col_widths = []
            for i, h in enumerate(headers):
                max_len = len(str(h))
                for row in rows:
                    val_str = str(row[i]) if row[i] is not None else "NULL"
                    if len(val_str) > max_len:
                        max_len = min(len(val_str), 35) # Cap width at 35 chars
                col_widths.append(max(max_len, 8))
            
            # Print table
            header_row = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
            separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
            
            print("\n" + header_row)
            print(separator)
            for row in rows:
                formatted_vals = []
                for i, val in enumerate(row):
                    val_str = str(val) if val is not None else "NULL"
                    if len(val_str) > col_widths[i]:
                        val_str = val_str[:col_widths[i]-3] + "..."
                    formatted_vals.append(f"{val_str:<{col_widths[i]}}")
                print(" | ".join(formatted_vals))
            print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''})\n")
        else:
            con.commit()
            print(f"\n[Success]: Query executed. Rows affected: {cur.rowcount}\n")
        
        con.close()
    except Exception as e:
        print(f"\n[Error]: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        execute_query(q)
    else:
        print("=" * 65)
        print("⚜️ DineDesk Interactive SQL Shell (Multi-line supported)")
        print("   • End queries with a semicolon ';' and press Enter")
        print("   • Type 'exit' or 'quit' to close")
        print("=" * 65)
        
        buffer = []
        while True:
            try:
                prompt = "dinedesk_sql> " if not buffer else "          ...> "
                line = input(prompt).strip()
                
                if not line and not buffer:
                    continue
                
                if line.lower() in ("exit", "quit", "q") and not buffer:
                    print("Goodbye.")
                    break
                
                buffer.append(line)
                
                # Check if statement ends with semicolon
                joined = " ".join(buffer).strip()
                if joined.endswith(";"):
                    execute_query(joined)
                    buffer = []
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye.")
                break
