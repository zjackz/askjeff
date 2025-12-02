from app.db import SessionLocal
from sqlalchemy import text

def inspect_schema():
    with SessionLocal() as db:
        # Check product_records columns
        print("Checking product_records columns:")
        result = db.execute(text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'product_records'"))
        for row in result:
            print(f"  {row[0]}: {row[1]} (Nullable: {row[2]})")

        # Check extraction_tasks columns
        print("\nChecking extraction_tasks columns:")
        result = db.execute(text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'extraction_tasks'"))
        for row in result:
            print(f"  {row[0]}: {row[1]} (Nullable: {row[2]})")

        # Check extraction_items columns
        print("\nChecking extraction_items columns:")
        result = db.execute(text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'extraction_items'"))
        for row in result:
            print(f"  {row[0]}: {row[1]} (Nullable: {row[2]})")

if __name__ == "__main__":
    inspect_schema()
