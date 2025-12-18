"""
模拟前端请求，查看实际 API 响应
"""
from app.db import SessionLocal
from app.models.import_batch import ImportBatch
from app.schemas.imports import ImportDetailResponse, ImportBatchOut
from sqlalchemy import select

with SessionLocal() as db:
    print("=" * 60)
    print("模拟 GET /api/imports/{id} 响应")
    print("=" * 60)
    
    # 获取批次 ID 6 (用户报错的批次)
    batch_id = 6
    batch = db.get(ImportBatch, batch_id)
    
    if not batch:
        print(f"\n✗ 批次 {batch_id} 不存在")
    else:
        print(f"\n找到批次 {batch_id}")
        print(f"   - status: {batch.status}")
        print(f"   - total_rows: {batch.total_rows}")
        print(f"   - success_rows: {batch.success_rows}")
        
        # 模拟 API 响应
        response = ImportDetailResponse(
            batch=ImportBatchOut.model_validate(batch),
            failed_rows=[]
        )
        
        # 序列化为 JSON (by_alias=True)
        response_dict = response.model_dump(by_alias=True)
        
        print(f"\nAPI 响应 (response.model_dump(by_alias=True)):")
        print(f"   - batch.status: {response_dict['batch']['status']}")
        print(f"   - batch.totalRows: {response_dict['batch'].get('totalRows', 'NOT FOUND')}")
        print(f"   - batch.successRows: {response_dict['batch'].get('successRows', 'NOT FOUND')}")
        print(f"   - batch.total_rows: {response_dict['batch'].get('total_rows', 'NOT FOUND')}")
        
        # 检查字段
        if 'totalRows' in response_dict['batch']:
            print(f"\n✓ totalRows 字段存在于响应中")
        else:
            print(f"\n✗ totalRows 字段不存在！")
            print(f"   可用字段: {list(response_dict['batch'].keys())}")
