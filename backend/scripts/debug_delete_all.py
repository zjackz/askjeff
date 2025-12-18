import sys
import os
sys.path.append(os.getcwd())

from app.db import SessionLocal
from app.models.import_batch import ImportBatch, ProductRecord
from app.models.extraction import ExtractionTask, ExtractionItem
from app.models.extraction_run import ExtractionRun
from app.models.export_job import ExportJob
from app.models.system_log import SystemLog
from sqlalchemy import text

db = SessionLocal()
try:
    print("Attempting to delete all data...")
    
    # 1. Logs
    print("Deleting SystemLog...")
    db.query(SystemLog).delete()
    
    # 2. Extraction Items
    print("Deleting ExtractionItem...")
    db.query(ExtractionItem).delete()
    
    # 3. Extraction Tasks
    print("Deleting ExtractionTask...")
    db.query(ExtractionTask).delete()
    
    # 3.5 Extraction Runs
    print("Deleting ExtractionRun...")
    db.query(ExtractionRun).delete()
    
    # 4. Products
    print("Deleting ProductRecord...")
    db.query(ProductRecord).delete()
    
    # 5. Import Batches
    print("Deleting ImportBatch...")
    db.query(ImportBatch).delete()
    
    # 6. Export Jobs
    print("Deleting ExportJob...")
    db.query(ExportJob).delete()
    
    db.commit()
    print("Deletion successful!")
except Exception as e:
    db.rollback()
    print(f"Deletion failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
