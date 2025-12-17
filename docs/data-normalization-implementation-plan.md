# 数据标准化统一方案 - 实施计划

## 目标

**将尽可能多的数据存到数据库和 XLSX 中，确保系统的一致性**

### 核心原则

1. ✅ **数据完整性**: 保存所有可用数据，不丢失任何信息
2. ✅ **结构一致性**: 文件导入和 API 导入使用相同的数据结构
3. ✅ **类型安全**: 统一的类型转换和验证
4. ✅ **可扩展性**: 支持未来添加新字段

## 实施步骤

### Step 1: 数据库模型扩展 ✅

**文件**: `backend/app/models/import_batch.py`

**新增字段**:

```python
class ProductRecord(Base):
    # ... 现有字段 ...
    
    # 新增：扩展数据字段
    extended_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # 存储: brand, image_url, launch_date, revenue, sales_volume, fba_fee, 
    #       lqs, variation_count, seller_count, weight, dimensions, etc.
    
    # 新增：数据来源标识
    data_source: Mapped[str] = mapped_column(String(20), default='file')
    # 值: "file" 或 "api"
```

**状态**: ✅ 已完成

### Step 2: 数据库迁移 🔄

**文件**: `backend/migrations/versions/add_extended_fields.py`

**命令**:

```bash
# 在 Docker 容器中执行
docker exec askjeff-dev-backend-1 bash -c "cd /app && python -m alembic upgrade head"
```

**状态**: ⏳ 待执行

### Step 3: 创建统一标准化器 ✅

**文件**: `backend/app/services/product_normalizer.py`

**功能**:
- ✅ 统一的字段映射（支持多种字段名）
- ✅ 统一的类型转换（Decimal, int, str）
- ✅ 统一的数据验证
- ✅ 自动提取扩展字段
- ✅ 保留原始数据

**核心方法**:

```python
ProductDataNormalizer.normalize_product(raw_data, source="file"|"api")
ProductDataNormalizer.validate_product(data)
```

**状态**: ✅ 已完成

### Step 4: 重构 API 导入服务 🔄

**文件**: `backend/app/services/api_import_service.py`

**修改内容**:

```python
from app.services.product_normalizer import ProductDataNormalizer

class APIImportService:
    async def _save_to_database(self, batch_id: int, products: list[dict]):
        """保存到数据库（使用统一标准化）"""
        records = []
        
        for product in products:
            # 1. 标准化数据
            normalized = ProductDataNormalizer.normalize_product(
                raw_data=product,
                source="api"
            )
            
            # 2. 验证数据
            validation_status, validation_messages = ProductDataNormalizer.validate_product(
                normalized
            )
            
            # 3. 创建 normalized_payload
            normalized_payload = ProductDataNormalizer.create_normalized_payload(normalized)
            
            # 4. 创建记录
            record = ProductRecord(
                batch_id=batch_id,
                asin=normalized["asin"],
                title=normalized["title"],
                category=normalized["category"],
                price=normalized["price"],
                currency=normalized["currency"],
                sales_rank=normalized["sales_rank"],
                reviews=normalized["reviews"],
                rating=normalized["rating"],
                raw_payload=normalized["raw_payload"],
                normalized_payload=normalized_payload,
                extended_data=normalized["extended_data"],  # 新增
                data_source=normalized["data_source"],      # 新增
                validation_status=validation_status,
                validation_messages=validation_messages,
            )
            records.append(record)
        
        self.db.bulk_save_objects(records)
        self.db.commit()
```

**状态**: ⏳ 待实施

### Step 5: 重构文件导入服务 🔄

**文件**: `backend/app/services/import_service.py`

**修改内容**:

```python
from app.services.product_normalizer import ProductDataNormalizer

class ImportService:
    def _process_rows(self, ...):
        """处理行数据（使用统一标准化）"""
        records = []
        
        for idx, row in enumerate(rows, start=2):
            row_dict = dict(zip(headers, row))
            
            # 1. 标准化数据
            normalized = ProductDataNormalizer.normalize_product(
                raw_data=row_dict,
                source="file"
            )
            
            # 2. 验证数据
            validation_status, validation_messages = ProductDataNormalizer.validate_product(
                normalized
            )
            
            # 3. 创建 normalized_payload
            normalized_payload = ProductDataNormalizer.create_normalized_payload(normalized)
            
            # 4. 创建记录
            record = ProductRecord(
                batch_id=batch_id,
                asin=normalized["asin"],
                title=normalized["title"],
                category=normalized["category"],
                price=normalized["price"],
                currency=normalized["currency"],
                sales_rank=normalized["sales_rank"],
                reviews=normalized["reviews"],
                rating=normalized["rating"],
                raw_payload=normalized["raw_payload"],
                normalized_payload=normalized_payload,
                extended_data=normalized["extended_data"],  # 新增
                data_source=normalized["data_source"],      # 新增
                validation_status=validation_status,
                validation_messages=validation_messages,
            )
            records.append(record)
        
        return records
```

**状态**: ⏳ 待实施

### Step 6: 更新导出服务 🔄

**文件**: `backend/app/services/export_service.py`

**修改内容**:

导出时包含 `extended_data` 中的所有字段：

```python
def _build_export_data(self, records: list[ProductRecord]) -> list[dict]:
    """构建导出数据（包含扩展字段）"""
    export_data = []
    
    for record in records:
        row = {
            # 核心字段
            "ASIN": record.asin,
            "标题": record.title,
            "类目": record.category,
            "价格": record.price,
            "货币": record.currency,
            "销售排名": record.sales_rank,
            "评论数": record.reviews,
            "评分": record.rating,
            
            # 扩展字段（从 extended_data 提取）
            "品牌": record.extended_data.get("brand") if record.extended_data else None,
            "图片URL": record.extended_data.get("image_url") if record.extended_data else None,
            "产品URL": record.extended_data.get("product_url") if record.extended_data else None,
            "上市日期": record.extended_data.get("launch_date") if record.extended_data else None,
            "月收入": record.extended_data.get("revenue") if record.extended_data else None,
            "月销量": record.extended_data.get("sales_volume") if record.extended_data else None,
            "FBA费用": record.extended_data.get("fba_fee") if record.extended_data else None,
            "LQS": record.extended_data.get("lqs") if record.extended_data else None,
            "变体数": record.extended_data.get("variation_count") if record.extended_data else None,
            "卖家数": record.extended_data.get("seller_count") if record.extended_data else None,
            "重量": record.extended_data.get("weight") if record.extended_data else None,
            
            # 元数据
            "数据来源": record.data_source,
            "导入时间": record.ingested_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        export_data.append(row)
    
    return export_data
```

**状态**: ⏳ 待实施

### Step 7: 单元测试 🔄

**文件**: `backend/tests/services/test_product_normalizer.py`

**测试用例**:

```python
def test_normalize_api_data():
    """测试 API 数据标准化"""
    raw_data = {
        "Asin": "B0G3NCGSHC",
        "Title": "Test Product",
        "Price": 1999,
        "Ratings": 4.5,
        "RatingsCount": 1234,
        "Brand": "Test Brand",
        "Photo": ["https://example.com/image.jpg"],
    }
    
    result = ProductDataNormalizer.normalize_product(raw_data, source="api")
    
    assert result["asin"] == "B0G3NCGSHC"
    assert result["title"] == "Test Product"
    assert result["price"] == Decimal("19.99")  # 假设 API 返回分
    assert result["rating"] == Decimal("4.5")
    assert result["reviews"] == 1234
    assert result["extended_data"]["brand"] == "Test Brand"
    assert result["extended_data"]["image_url"] == "https://example.com/image.jpg"
    assert result["data_source"] == "api"

def test_normalize_file_data():
    """测试文件数据标准化"""
    raw_data = {
        "asin": "B0G3NCGSHC",
        "product_name": "Test Product",
        "price": "$19.99",
        "star_rating": "4.5",
        "review_count": "1,234",
    }
    
    result = ProductDataNormalizer.normalize_product(raw_data, source="file")
    
    assert result["asin"] == "B0G3NCGSHC"
    assert result["title"] == "Test Product"
    assert result["price"] == Decimal("19.99")
    assert result["rating"] == Decimal("4.5")
    assert result["reviews"] == 1234
    assert result["data_source"] == "file"

def test_validation():
    """测试数据验证"""
    # 有效数据
    valid_data = {"asin": "B0G3NCGSHC", "title": "Test"}
    status, messages = ProductDataNormalizer.validate_product(valid_data)
    assert status == "valid"
    assert messages is None
    
    # 无效 ASIN
    invalid_data = {"asin": "INVALID", "title": "Test"}
    status, messages = ProductDataNormalizer.validate_product(invalid_data)
    assert status == "warning"
    assert "asin" in messages
```

**状态**: ⏳ 待实施

## 数据字段映射表

### 核心字段（存入数据库列）

| 标准字段 | 文件导入可能的名称 | API 导入可能的名称 | 类型 |
|---------|-----------------|-----------------|------|
| asin | asin, ASIN | Asin, asin | String |
| title | title, product_name, ProductName | Title, title | String |
| category | category, category_name | Category, category | String |
| price | price, Price | Price, price | Decimal |
| currency | currency, Currency | Currency, currency | String(3) |
| sales_rank | sales_rank, salesRank, bsr, Rank | Rank, rank, salesRank | Integer |
| reviews | reviews, review_count, ratingsCount | RatingsCount, ratingsCount | Integer |
| rating | rating, star_rating, ratings | Ratings, ratings | Decimal(3,2) |

### 扩展字段（存入 extended_data JSON）

| 标准字段 | 可能的原始字段名 | 说明 |
|---------|----------------|------|
| brand | brand, Brand | 品牌 |
| image_url | image, Image, photo, Photo | 主图 URL |
| product_url | product_url, url, link | 产品链接 |
| launch_date | launch_date, launchDate, LaunchDate | 上市日期 |
| revenue | revenue, Revenue | 月收入 |
| sales_volume | sales, Sales, sales_volume | 月销量 |
| fba_fee | fbaFee, FbaFee, fba_fee, fees | FBA 费用 |
| lqs | lqs, Lqs, LQS | LQS 评分 |
| variation_count | variations, Variations | 变体数量 |
| seller_count | sellers, Sellers | 卖家数量 |
| weight | weight, Weight | 重量 |
| dimensions | dimensions, Dimensions | 尺寸 |
| bsr_category | BsrCategory, bsrCategory | BSR 类目信息 |
| parent_asin | parentAsin, ParentAsin | 父 ASIN |
| is_amazon | isAmazon, IsAmazon | 是否亚马逊自营 |
| availability | availability, Availability, in_stock | 库存状态 |

## 预期效果

### 数据完整性

- ✅ **核心字段**: 100% 保存到数据库列
- ✅ **扩展字段**: 100% 保存到 `extended_data` JSON
- ✅ **原始数据**: 100% 保存到 `raw_payload` JSON
- ✅ **无数据丢失**: 所有字段都被保留

### 数据一致性

- ✅ **文件导入和 API 导入使用相同的标准化器**
- ✅ **相同的类型转换逻辑**
- ✅ **相同的验证规则**
- ✅ **相同的数据结构**

### 导出完整性

- ✅ **XLSX 导出包含所有核心字段**
- ✅ **XLSX 导出包含所有扩展字段**
- ✅ **可选择导出哪些字段**
- ✅ **支持自定义列名**

## 执行顺序

1. ✅ **Step 1**: 更新数据库模型（已完成）
2. ⏳ **Step 2**: 执行数据库迁移
3. ✅ **Step 3**: 创建标准化器（已完成）
4. ⏳ **Step 4**: 重构 API 导入服务
5. ⏳ **Step 5**: 重构文件导入服务
6. ⏳ **Step 6**: 更新导出服务
7. ⏳ **Step 7**: 编写单元测试
8. ⏳ **Step 8**: 集成测试和验证

## 下一步行动

### 立即执行

1. **执行数据库迁移**:

   ```bash
   docker exec askjeff-dev-backend-1 bash -c "cd /app && python -m alembic upgrade head"
   ```

2. **重构 API 导入服务**:
   - 修改 `_save_to_database()` 方法
   - 使用 `ProductDataNormalizer`

3. **重构文件导入服务**:
   - 修改 `_process_rows()` 方法
   - 使用 `ProductDataNormalizer`

### 测试验证

1. **单元测试**: 确保标准化器正确工作
2. **集成测试**: 测试完整的导入流程
3. **数据验证**: 对比导入前后的数据

## 总结

通过实施这个统一方案，我们将实现：

1. ✅ **数据完整性**: 保存所有可用数据
2. ✅ **系统一致性**: 文件和 API 导入使用相同逻辑
3. ✅ **类型安全**: 统一的类型转换
4. ✅ **可扩展性**: 轻松添加新字段
5. ✅ **可维护性**: 集中管理数据处理逻辑

**核心优势**: 一次标准化，处处使用！
