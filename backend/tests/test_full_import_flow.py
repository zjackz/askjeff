
import pytest
import os
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from app.services.api_import_service import api_import_service
from app.services.extraction_service import ExtractionService
from app.models.import_batch import ImportBatch, ProductRecord
from app.models.extraction_run import ExtractionRun
from app.services.sorftime.models import SorftimeResponse

@pytest.mark.asyncio
async def test_full_import_to_extraction_flow(db: Session):
    """
    完整流程测试：从 API 导入 -> 数据标准化 -> 数据库保存 -> Excel 生成 -> AI 特征提取
    """
    # 1. 准备极其详尽的 Mock 数据
    asin = "B0FN44NCTQ"
    category_id = "123456"
    
    raw_api_data = {
        "Asin": asin,
        "Title": "Test Product Premium",
        "SalesPrice": 3999, # 测试 SalesPrice 映射
        "Ratings": 4.5,     # 测试 Ratings 映射
        "RatingsCount": 100,
        "Category": ["Electronics", "Kitchen", "Toasters"], # 测试类目列表提取
        "Rank": 123,
        "Brand": "Test Brand",
        "Photo": ["https://example.com/image.jpg"],
        "StoreName": "Test Store",
        "IsFBA": True,
        "ListingSalesVolumeOfMonthTrend": [100, 200, 300, 450], # 测试趋势提取
        "ListingSalesOfMonthTrend": [1000, 2000, 3000, 450000], # 测试趋势提取
        "OnlineDate": "2023-01-01",
        "VariationASINCount": 5,
        "SellerCount": 3,
        "Size": ["10x10x10"],
        "Weight": 500,
        "Description": "This is a long description that should not be lost.",
    }
    
    # 模拟 Sorftime API 响应
    mock_cat_response = MagicMock(spec=SorftimeResponse)
    mock_cat_response.code = 0
    mock_cat_response.data = {"products": [{"asin": asin, "title": "Test Product"}]}
    
    mock_prod_response = MagicMock(spec=SorftimeResponse)
    mock_prod_response.code = 0
    mock_prod_response.data = {"products": [raw_api_data]}

    # 2. 执行导入流程
    with patch("app.services.api_import_service.SorftimeClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.category_request.return_value = mock_cat_response
        mock_client.product_request.return_value = mock_prod_response
        MockClient.return_value = mock_client
        
        batch_id = await api_import_service.import_from_input(
            db=db,
            input_value=category_id,
            input_type="category_id",
            test_mode=False,
            limit=1
        )

    # 3. 【核心验证】数据库数据完整性
    product = db.query(ProductRecord).filter(ProductRecord.batch_id == batch_id).first()
    
    # A. 验证原始数据 (raw_payload) 是否 100% 保留
    assert product.raw_payload == raw_api_data, "原始数据丢失或被篡改"
    
    # B. 验证标准化数据 (normalized_payload)
    from decimal import Decimal
    assert product.price == Decimal('39.99')
    assert product.normalized_payload["asin"] == asin
    assert product.normalized_payload["store_name"] == "Test Store"
    assert product.category == "Toasters" # 验证取最细分类目
    
    # C. 验证扩展字段 (extended_data)
    assert product.extended_data["sales_volume"] == 450 # 验证从趋势列表提取最新值
    assert product.extended_data["revenue"] == 450000   # 验证从趋势列表提取最新值
    assert product.extended_data["variation_count"] == 5
    assert product.extended_data["seller_count"] == 3
    assert product.extended_data["description"] == "This is a long description that should not be lost."

    # 4. 【核心验证】Excel 导出数据完整性
    batch = db.query(ImportBatch).get(batch_id)
    excel_path = Path(os.getenv("STORAGE_DIR", "storage")) / batch.storage_path
    
    import pandas as pd
    df = pd.read_excel(excel_path)
    
    row = df.iloc[0]
    assert row["ASIN"] == asin
    assert row["Price"] == 39.99
    assert row["Category"] == "Toasters"
    assert row["Sales"] == 450
    assert row["Revenue"] == 450000
    assert row["Variations"] == 5
    assert row["Sellers"] == 3

    # 5. 【核心验证】AI 提取后的数据共存性
    mock_ai_extracted = {"material": "Steel"}
    mock_deepseek = AsyncMock()
    mock_deepseek.extract_features_async.return_value = (mock_ai_extracted, {"prompt_tokens": 10})
    
    extraction_service = ExtractionService(db=db, client=mock_deepseek)
    await extraction_service.extract_batch_features(batch_id=batch_id, target_fields=["material"])
    
    db.refresh(product)
    # 验证 AI 结果已添加，且原始数据依然完好
    assert product.ai_features["material"] == "Steel"
    assert product.raw_payload == raw_api_data, "AI 提取过程导致原始数据丢失"
    assert product.price == Decimal('39.99'), "AI 提取过程导致标准化数据丢失"

    print(f"\n[VERIFIED] Data integrity check passed. No data loss detected in the entire flow.")
    
    if excel_path.exists():
        excel_path.unlink()
    
    # 清理测试文件
    if excel_path.exists():
        excel_path.unlink()
