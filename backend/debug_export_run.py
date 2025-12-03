import sys
import os
sys.path.append(os.getcwd())

from app.db import SessionLocal
from app.services.export_service import export_service
from app.models.extraction_run import ExtractionRun
from sqlalchemy import select

db = SessionLocal()
try:
    # Find a run
    stmt = select(ExtractionRun).limit(1)
    run = db.execute(stmt).scalars().first()
    if not run:
        print("No runs found")
        sys.exit(1)
        
    print(f"Testing export for Run {run.id} (Batch {run.batch_id})")
    
    # Simulate export
    filters = {"run_id": run.id}
    # Standard fields + one AI field if possible
    fields = ["asin", "title", "price", "带自动烘干功能"] 
    
    # Call _fetch_extraction_rows directly to see logs
    rows = export_service._fetch_extraction_rows(db, filters)
    print(f"Fetched {len(rows)} rows")
    if rows:
        print("First row sample:", rows[0])

finally:
    db.close()
