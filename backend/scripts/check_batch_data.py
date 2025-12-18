import sys
import os
# sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine, text
from app.config import settings

print(f"DB URL: {settings.database_url}")

try:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        print("Connected.")
        result = conn.execute(text("SELECT count(*) FROM product_records WHERE batch_id = 2"))
        count = result.scalar()
        print(f"Count for batch_id=2: {count}")
        
        if count == 0:
            print("Checking if batch 2 exists...")
            result = conn.execute(text("SELECT id, filename, status FROM import_batches WHERE id = 2"))
            batch = result.fetchone()
            if batch:
                print(f"Batch 2 found: {batch}")
            else:
                print("Batch 2 NOT found.")
                
            print("Listing all batches:")
            result = conn.execute(text("SELECT id, filename, status, total_rows FROM import_batches"))
            for row in result:
                print(row)
except Exception as e:
    print(f"Error: {e}")
