from app.db import SessionLocal
from app.models.import_batch import ImportBatch

with SessionLocal() as db:
    batch = db.get(ImportBatch, 6)
    if batch:
        print('批次 6 详情:')
        print(f'  status: {batch.status}')
        print(f'  source_type: {batch.source_type}')
        print(f'  total_rows: {batch.total_rows}')
        print(f'  success_rows: {batch.success_rows}')
        print(f'  import_metadata: {batch.import_metadata}')
