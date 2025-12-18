"""
验证批次数据序列化
"""
from app.db import SessionLocal
from app.models.import_batch import ImportBatch
from app.schemas.imports import ImportBatchOut
from sqlalchemy import select

with SessionLocal() as db:
    print("=" * 60)
    print("验证批次数据序列化")
    print("=" * 60)
    
    # 获取最新的批次
    stmt = select(ImportBatch).where(ImportBatch.source_type == 'api').order_by(ImportBatch.id.desc()).limit(1)
    batch = db.execute(stmt).scalars().first()
    
    if not batch:
        print("\n未找到 API 导入的批次，创建测试批次...")
        batch = ImportBatch(
            filename="test_batch.xlsx",
            storage_path="test/path.xlsx",
            import_strategy="append",
            source_type="api",
            status="succeeded",
            total_rows=100,
            success_rows=95,
            failed_rows=5
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        print(f"✓ 创建测试批次 ID: {batch.id}")
    
    print(f"\n1. 数据库字段 (snake_case):")
    print(f"   - batch.total_rows = {batch.total_rows}")
    print(f"   - batch.success_rows = {batch.success_rows}")
    print(f"   - batch.failed_rows = {batch.failed_rows}")
    print(f"   - batch.status = {batch.status}")
    
    # 序列化
    batch_out = ImportBatchOut.model_validate(batch)
    
    # 使用 by_alias=True 来获取驼峰命名
    batch_dict = batch_out.model_dump(by_alias=True)
    
    print(f"\n2. 序列化后 (camelCase, by_alias=True):")
    print(f"   - totalRows = {batch_dict.get('totalRows')}")
    print(f"   - successRows = {batch_dict.get('successRows')}")
    print(f"   - failedRows = {batch_dict.get('failedRows')}")
    print(f"   - status = {batch_dict.get('status')}")
    
    # 验证
    print(f"\n3. 验证:")
    checks = [
        ('totalRows' in batch_dict, "✓ totalRows 字段存在"),
        ('successRows' in batch_dict, "✓ successRows 字段存在"),
        ('failedRows' in batch_dict, "✓ failedRows 字段存在"),
        (batch_dict['totalRows'] == batch.total_rows, f"✓ totalRows 值正确 ({batch_dict['totalRows']} == {batch.total_rows})"),
        (batch_dict['successRows'] == batch.success_rows, f"✓ successRows 值正确 ({batch_dict['successRows']} == {batch.success_rows})"),
    ]
    
    all_passed = True
    for check, msg in checks:
        if check:
            print(f"   {msg}")
        else:
            print(f"   ✗ {msg}")
            all_passed = False
    
    if all_passed:
        print(f"\n✓ 所有检查通过！")
    else:
        print(f"\n✗ 部分检查失败")
    
    # 测试 JSON 序列化（模拟 FastAPI 响应）
    import json
    json_str = batch_out.model_dump_json(by_alias=True)
    json_data = json.loads(json_str)
    
    print(f"\n4. JSON 序列化测试 (模拟 API 响应):")
    print(f"   - totalRows in JSON: {'totalRows' in json_data}")
    print(f"   - JSON totalRows value: {json_data.get('totalRows')}")
