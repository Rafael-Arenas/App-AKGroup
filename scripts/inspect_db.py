
import sqlite3
import os

def inspect_db():
    db_path = 'app_akgroup.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- Tables ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(tables)

    for table in ['plants', 'orders', 'quotes', 'invoices_sii', 'invoices_export']:
        if table in tables:
            print(f"\n--- Columns in {table} ---")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"{col[1]} ({col[2]})")
        else:
            print(f"\n--- Table {table} does not exist ---")
    
    print("\n--- Alembic Version ---")
    try:
        cursor.execute("SELECT * FROM alembic_version")
        print(cursor.fetchall())
    except sqlite3.OperationalError:
        print("alembic_version table not found")

    conn.close()

if __name__ == "__main__":
    inspect_db()
