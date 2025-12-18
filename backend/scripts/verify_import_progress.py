"""
测试 API 导入进度更新功能
"""
import asyncio
from app.db import SessionLocal
from app.services.api_import_service import api_import_service

async def test_import_progress():
    """测试导入进度更新"""
    print("=" * 60)
    print("测试 API 导入进度更新")
    print("=" * 60)
    
    with SessionLocal() as db:
        # 使用测试模式，类目 ID 示例
        input_value = "172282"  # Electronics 类目
        
        print(f"\n1. 开始导入测试 (Category ID: {input_value})")
        print("-" * 60)
        
        try:
            batch_id = await api_import_service.import_from_input(
                db=db,
                input_value=input_value,
                input_type="category_id",
                domain=1,
                test_mode=True,  # 使用测试模式
                limit=10,  # 只抓取 10 条
            )
            
            print(f"\n✓ 导入完成！批次 ID: {batch_id}")
            
            # 获取批次详情
            from app.models.import_batch import ImportBatch
            batch = db.get(ImportBatch, batch_id)
            
            if batch:
                print(f"\n2. 批次详情:")
                print(f"   - 状态: {batch.status}")
                print(f"   - 总行数: {batch.total_rows}")
                print(f"   - 成功行数: {batch.success_rows}")
                print(f"   - 失败行数: {batch.failed_rows}")
                print(f"   - 文件路径: {batch.storage_path}")
                
                # 测试序列化
                from app.schemas.imports import ImportBatchOut
                batch_out = ImportBatchOut.model_validate(batch)
                batch_dict = batch_out.model_dump(by_alias=True)
                
                print(f"\n3. 序列化后的字段 (前端接收的格式):")
                print(f"   - totalRows: {batch_dict.get('totalRows')}")
                print(f"   - successRows: {batch_dict.get('successRows')}")
                print(f"   - failedRows: {batch_dict.get('failedRows')}")
                print(f"   - status: {batch_dict.get('status')}")
                
                # 验证字段存在
                assert 'totalRows' in batch_dict, "缺少 totalRows 字段"
                assert 'successRows' in batch_dict, "缺少 successRows 字段"
                assert batch_dict['totalRows'] == 10, f"totalRows 应该是 10，实际是 {batch_dict['totalRows']}"
                assert batch_dict['successRows'] == 10, f"successRows 应该是 10，实际是 {batch_dict['successRows']}"
                
                print(f"\n✓ 所有断言通过！")
            else:
                print(f"\n✗ 找不到批次 {batch_id}")
                
        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_import_progress())
