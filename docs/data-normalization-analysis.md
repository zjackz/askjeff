# 数据结构统一性分析和改进方案

## 当前状况分析

### 1. ProductRecord 模型（数据库表结构）

```python
class ProductRecord(Base):
    # 核心字段（两种导入都使用）
    asin: str                    # ASIN 码
    title: str                   # 产品标题
    category: str | None         # 类目
    price: Decimal | None        # 价格
    currency: str | None         # 货币
    sales_rank: int | None       # 销售排名
    reviews: int | None          # 评论数
    rating: Decimal | None       # 评分
    
    # 扩展字段（JSON 存储）
    raw_payload: dict | None          # 原始数据
    normalized_payload: dict | None   # 标准化数据
    validation_status: str            # 验证状态
    validation_messages: dict | None  # 验证消息
```

### 2. 文件导入 vs API 导入对比

| 字段 | 文件导入 (ImportService) | API 导入 (APIImportService) | 问题 |
|------|------------------------|---------------------------|------|
| **asin** | ✅ 从 Excel 列映射 | ✅ 从 API `asin` 字段 | ✅ 一致 |
| **title** | ✅ 从 Excel 列映射 | ✅ 从 API `title` 字段 | ✅ 一致 |
| **category** | ✅ 从 Excel 列映射 | ✅ 从 API `category` 字段 | ✅ 一致 |
| **price** | ✅ 通过 `_to_decimal()` 转换 | ⚠️ 直接使用 API 值 | ⚠️ 类型不一致 |
| **currency** | ✅ 通过 `_normalize_currency()` 标准化 | ⚠️ 硬编码 "USD" | ⚠️ 缺少灵活性 |
| **sales_rank** | ✅ 通过 `_to_int()` 转换 | ⚠️ 直接使用 API 值 | ⚠️ 类型不一致 |
| **reviews** | ✅ 通过 `_to_int()` 转换 | ⚠️ 直接使用 API 值（`ratingsCount`） | ⚠️ 类型不一致 |
| **rating** | ✅ 通过 `_to_decimal(scale=2)` 转换 | ⚠️ 直接使用 API 值（`ratings`） | ⚠️ 类型不一致 |
| **raw_payload** | ✅ 原始 Excel 行数据 | ✅ 原始 API 响应 | ✅ 一致 |
| **normalized_payload** | ✅ 标准化后的数据 | ⚠️ 包含额外字段（brand, image, etc） | ⚠️ 结构不一致 |
| **validation_status** | ✅ 根据验证规则设置 | ⚠️ 硬编码 "valid" | ❌ 缺少验证 |
| **validation_messages** | ✅ 记录验证错误 | ❌ 未使用 | ❌ 缺少验证 |

### 3. 主要问题

#### 问题 1：数据类型转换不一致
- **文件导入**：使用 `_to_decimal()`, `_to_int()` 等辅助函数确保类型正确
- **API 导入**：直接使用 API 返回值，可能导致类型不匹配

**风险**：
- 数据库插入失败（类型错误）
- 查询和过滤不准确
- 数据导出格式不一致

#### 问题 2：字段验证缺失
- **文件导入**：有完整的验证逻辑（ASIN 格式、必填字段等）
- **API 导入**：直接信任 API 数据，无验证

**风险**：
- 脏数据进入数据库
- 无法追踪数据质量问题
- 后续处理可能失败

#### 问题 3：normalized_payload 结构不一致
- **文件导入**：只包含核心字段
- **API 导入**：包含大量额外字段（brand, image, launch_date, etc）

**风险**：
- 数据查询和处理逻辑需要分别处理
- 导出时字段不统一
- 难以维护

#### 问题 4：货币处理不灵活
- **文件导入**：支持多种货币，有标准化逻辑
- **API 导入**：硬编码 "USD"

**风险**：
- 无法支持其他站点（UK, JP, DE 等）
- 价格比较不准确

## 改进方案

### 方案 1：创建统一的数据标准化层

创建一个 `ProductDataNormalizer` 类，统一处理两种来源的数据：

```python
class ProductDataNormalizer:
    """统一的产品数据标准化器"""
    
    @staticmethod
    def normalize_product(
        raw_data: dict,
        source: str = "file"  # "file" or "api"
    ) -> dict:
        """
        将原始数据标准化为统一格式
        
        Returns:
            {
                "asin": str,
                "title": str,
                "category": str | None,
                "price": Decimal | None,
                "currency": str | None,
                "sales_rank": int | None,
                "reviews": int | None,
                "rating": Decimal | None,
                "extra_fields": dict  # 额外字段统一放这里
            }
        """
        pass
    
    @staticmethod
    def validate_product(data: dict) -> tuple[str, dict | None]:
        """
        验证产品数据
        
        Returns:
            (validation_status, validation_messages)
        """
        pass
    
    @staticmethod
    def _to_decimal(value: Any, scale: int = 2) -> Decimal | None:
        """统一的 Decimal 转换"""
        pass
    
    @staticmethod
    def _to_int(value: Any) -> int | None:
        """统一的 int 转换"""
        pass
```

### 方案 2：重构 API 导入服务

修改 `APIImportService._save_to_database()` 使用统一的标准化器：

```python
def _save_to_database(self, batch_id: int, products: list[dict]):
    """保存到数据库（使用统一标准化）"""
    from app.services.product_normalizer import ProductDataNormalizer
    
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
        
        # 3. 创建记录
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
            raw_payload=product,  # 保留原始 API 响应
            normalized_payload=normalized,  # 统一格式的标准化数据
            validation_status=validation_status,
            validation_messages=validation_messages,
        )
        records.append(record)
    
    # 批量插入
    self.db.bulk_save_objects(records)
    self.db.commit()
```

### 方案 3：扩展 ProductRecord 模型

为了更好地支持 API 导入的额外数据，建议：

```python
class ProductRecord(Base):
    # ... 现有字段 ...
    
    # 新增：扩展数据字段（统一存储额外信息）
    extended_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # 包含：brand, image, launch_date, revenue, sales, fees, lqs, variations, sellers, weight 等
    
    # 新增：数据来源标识
    data_source: Mapped[str] = mapped_column(String(20), default="file")  # file, api
```

### 方案 4：标准化 normalized_payload 结构

定义统一的 `normalized_payload` 结构：

```python
{
    # 核心字段（必须）
    "asin": str,
    "title": str,
    "category": str | None,
    "price": Decimal | None,
    "currency": str | None,
    "sales_rank": int | None,
    "reviews": int | None,
    "rating": Decimal | None,
    
    # 扩展字段（可选，统一命名）
    "brand": str | None,
    "image_url": str | None,  # 统一命名
    "product_url": str | None,
    "launch_date": str | None,
    "revenue": Decimal | None,
    "sales_volume": int | None,  # 统一命名
    "fba_fee": Decimal | None,  # 统一命名
    "lqs": int | None,
    "variation_count": int | None,  # 统一命名
    "seller_count": int | None,  # 统一命名
    "weight": Decimal | None,
}
```

## 实施步骤

### Step 1: 创建 ProductDataNormalizer（优先级：高）

```bash
# 创建文件
touch backend/app/services/product_normalizer.py

# 实现统一的标准化和验证逻辑
```

### Step 2: 重构 APIImportService（优先级：高）

- 使用 `ProductDataNormalizer` 处理数据
- 添加完整的验证逻辑
- 确保类型转换正确

### Step 3: 数据库迁移（优先级：中）

```bash
# 添加新字段
alembic revision --autogenerate -m "add extended_data and data_source to product_record"
alembic upgrade head
```

### Step 4: 重构 ImportService（优先级：中）

- 使用 `ProductDataNormalizer` 替代现有的辅助函数
- 确保两种导入方式使用相同的逻辑

### Step 5: 单元测试（优先级：高）

```python
# tests/services/test_product_normalizer.py
def test_normalize_api_data():
    """测试 API 数据标准化"""
    pass

def test_normalize_file_data():
    """测试文件数据标准化"""
    pass

def test_validation():
    """测试数据验证"""
    pass
```

## 预期收益

1. **数据一致性**：两种导入方式产生相同结构的数据
2. **类型安全**：统一的类型转换，避免数据库错误
3. **数据质量**：完整的验证逻辑，确保数据可靠
4. **可维护性**：单一职责，逻辑集中，易于维护
5. **可扩展性**：支持未来新的数据源（如其他 API、爬虫等）

## 风险和注意事项

1. **向后兼容**：需要确保现有数据不受影响
2. **性能影响**：标准化和验证会增加处理时间，需要优化
3. **测试覆盖**：必须有充分的单元测试和集成测试
4. **数据迁移**：现有数据可能需要重新标准化

## 总结

当前两种导入方式在数据处理上存在显著差异，主要体现在：
- **类型转换**：文件导入有严格的类型转换，API 导入缺失
- **数据验证**：文件导入有完整验证，API 导入缺失
- **数据结构**：normalized_payload 结构不一致

建议通过创建统一的 `ProductDataNormalizer` 来解决这些问题，确保数据的一致性、可靠性和可维护性。
