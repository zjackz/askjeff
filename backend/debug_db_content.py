from app.db.session import SessionLocal
from app.models.import_batch import ProductRecord
from sqlalchemy import select

db = SessionLocal()
try:
    stmt = select(ProductRecord).where(ProductRecord.batch_id == 1).limit(5)
    records = db.execute(stmt).scalars().all()
    print(f"Found {len(records)} records for batch 1")
    for r in records:
        print(f"ID: {r.id}, ASIN: '{r.asin}', Title: '{r.title}', Price: {r.price}")
        print(f"Raw Payload keys: {list(r.raw_payload.keys()) if r.raw_payload else 'None'}")
        print(f"AI Features: {r.ai_features}")
        print("-" * 50)
finally:
    db.close()
