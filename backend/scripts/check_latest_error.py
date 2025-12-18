from app.db import SessionLocal
from app.models import ExportJob
from sqlalchemy import select

with SessionLocal() as db:
    stmt = select(ExportJob).where(ExportJob.export_type == 'extraction_results').order_by(ExportJob.started_at.desc()).limit(1)
    job = db.execute(stmt).scalars().first()
    if job:
        print(f"Job ID: {job.id}")
        print(f"Status: {job.status}")
        print(f"Error: {job.error_message}")
        print(f"Filters: {job.filters}")
        print(f"Created At: {job.started_at}")
    else:
        print("No extraction export job found")
