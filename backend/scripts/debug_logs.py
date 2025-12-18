import asyncio
import sys
from app.services.log_service import LogService
from app.db.session import SessionLocal
from app.models.log import SystemLog

async def main():
    db = SessionLocal()
    try:
        # 查询最近的 external_api 日志
        logs = db.query(SystemLog).filter(
            SystemLog.category == "external_api"
        ).order_by(SystemLog.timestamp.desc()).limit(5).all()
        
        print(f"Found {len(logs)} logs:")
        for log in logs:
            print(f"--- Log ID: {log.id} ---")
            print(f"Message: {log.message}")
            print(f"Context: {log.context}")
            print("-" * 30)
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
