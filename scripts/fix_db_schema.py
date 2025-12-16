
import sqlite3
import os

DB_PATH = 'app_akgroup.db'

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Fixing database schema...")

    # Check if plants has data
    try:
        cursor.execute("SELECT count(*) FROM plants")
        count = cursor.fetchone()[0]
        print(f"Plants table has {count} rows.")
    except sqlite3.OperationalError:
        print("Plants table does not exist (unexpected).")

    # 1. Orders: Ensure plant_id exists
    try:
        # Check if plant_id exists
        cursor.execute("SELECT plant_id FROM orders LIMIT 1")
        print("orders.plant_id exists")
    except sqlite3.OperationalError:
        # If not, try to rename branch_id
        try:
            cursor.execute("ALTER TABLE orders RENAME COLUMN branch_id TO plant_id")
            print("Renamed orders.branch_id to plant_id")
        except sqlite3.OperationalError as e:
             print(f"Could not rename orders.branch_id: {e}")

    # 2. Quotes: Ensure plant_id exists
    try:
        # Check if plant_id exists
        cursor.execute("SELECT plant_id FROM quotes LIMIT 1")
        print("quotes.plant_id exists")
    except sqlite3.OperationalError:
         try:
            cursor.execute("ALTER TABLE quotes RENAME COLUMN branch_id TO plant_id")
            print("Renamed quotes.branch_id to plant_id")
         except sqlite3.OperationalError as e:
            print(f"Could not rename quotes.branch_id: {e}")

    # 3. Quotes: Add unit and company_rut_id if missing
    try:
        cursor.execute("ALTER TABLE quotes ADD COLUMN unit VARCHAR(20)")
        print("Added quotes.unit")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE quotes ADD COLUMN company_rut_id INTEGER")
        print("Added quotes.company_rut_id")
    except sqlite3.OperationalError:
        pass

    # 4. Invoices SII: Ensure plant_id exists
    try:
        cursor.execute("SELECT plant_id FROM invoices_sii LIMIT 1")
        print("invoices_sii.plant_id exists")
    except sqlite3.OperationalError:
        try:
            cursor.execute("ALTER TABLE invoices_sii RENAME COLUMN branch_id TO plant_id")
            print("Renamed invoices_sii.branch_id to plant_id")
        except sqlite3.OperationalError as e:
            print(f"Could not rename invoices_sii.branch_id: {e}")

    # 5. Invoices Export: Handle branch_id and plant_id
    # Copy data from branch_id to plant_id if needed, then drop branch_id
    try:
        cursor.execute("UPDATE invoices_export SET plant_id = branch_id WHERE plant_id IS NULL AND branch_id IS NOT NULL")
        conn.commit()
        cursor.execute("ALTER TABLE invoices_export DROP COLUMN branch_id")
        print("Dropped invoices_export.branch_id")
    except sqlite3.OperationalError as e:
        print(f"Skipping invoices_export adjustment: {e}")

    # 6. Update alembic version
    try:
        cursor.execute("DELETE FROM alembic_version")
        cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('a2587c89b2ce')")
        print("Updated alembic version to a2587c89b2ce")
    except sqlite3.OperationalError as e:
        print(f"Error updating alembic version: {e}")

    conn.commit()
    conn.close()
    print("Schema fix completed.")

if __name__ == "__main__":
    fix_schema()
