#!/usr/bin/env python3
"""
查询最近的 API 调用日志
"""
import sys
import os
sys.path.insert(0, '/app')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/askjeff')

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from app.models.log import SystemLog
import json

# 创建数据库连接
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/askjeff')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def main():
    db = SessionLocal()
    try:
        # 查询最近的 external_api 日志
        logs = db.query(SystemLog).filter(
            SystemLog.category == "external_api"
        ).order_by(desc(SystemLog.timestamp)).limit(10).all()
        
        print(f"\n=== 最近 {len(logs)} 条 API 调用日志 ===\n")
        
        for i, log in enumerate(logs, 1):
            print(f"[{i}] {log.timestamp} - {log.level.upper()}")
            print(f"    消息: {log.message}")
            
            if log.context:
                ctx = log.context
                print(f"    平台: {ctx.get('platform', 'N/A')}")
                print(f"    URL: {ctx.get('url', 'N/A')}")
                print(f"    状态: {ctx.get('status_code', 'N/A')}")
                print(f"    耗时: {ctx.get('duration_ms', 'N/A')}ms")
                
                if ctx.get('response'):
                    resp = ctx['response']
                    print(f"    响应: Code={resp.get('code')}, Message={resp.get('message', '')[:50]}")
                    if resp.get('requestLeft') is not None:
                        print(f"    Quota: 消耗={resp.get('requestConsumed')}, 剩余={resp.get('requestLeft')}")
                
                if ctx.get('error'):
                    print(f"    错误: {ctx['error']}")
            
            print()
            
    finally:
        db.close()

if __name__ == "__main__":
    main()
