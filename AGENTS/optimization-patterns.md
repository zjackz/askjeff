# 常见优化模式

> 代码优化和重构的最佳实践,提高代码质量和性能。

**最后更新**: 2025-12-18

---

## 🚀 性能优化模式

### 模式 1: 数据库查询优化

#### 问题: N+1 查询

❌ **低效代码**:

```python
# 每次循环都查询数据库
products = db.query(Product).all()
for product in products:
    category = db.query(Category).filter_by(id=product.category_id).first()
    print(f"{product.name} - {category.name}")
```

✅ **优化后**:

```python
from sqlalchemy.orm import joinedload

# 一次性加载关联数据
products = db.query(Product).options(
    joinedload(Product.category)
).all()

for product in products:
    print(f"{product.name} - {product.category.name}")
```

**效果**: 查询次数从 N+1 减少到 1

---

### 模式 2: 批量操作优化

#### 问题: 逐条插入数据

❌ **低效代码**:

```python
for item in items:
    db.add(Product(**item))
    db.commit()  # 每次都提交
```

✅ **优化后**:

```python
# 批量插入
db.bulk_insert_mappings(Product, items)
db.commit()  # 一次提交
```

**效果**: 性能提升 10-100 倍

---

### 模式 3: 缓存优化

#### 问题: 重复计算或查询

❌ **低效代码**:

```python
async def get_product_stats(product_id: int):
    # 每次都重新计算
    product = db.query(Product).filter_by(id=product_id).first()
    stats = calculate_complex_stats(product)
    return stats
```

✅ **优化后**:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def calculate_complex_stats(product_id: int):
    product = db.query(Product).filter_by(id=product_id).first()
    return calculate_stats(product)

async def get_product_stats(product_id: int):
    return calculate_complex_stats(product_id)
```

**效果**: 避免重复计算

---

## 🔒 安全优化模式

### 模式 4: 参数化查询

#### 问题: SQL 注入风险

❌ **危险代码**:

```python
# 字符串拼接,有 SQL 注入风险
query = f"SELECT * FROM products WHERE name = '{user_input}'"
db.execute(query)
```

✅ **安全代码**:

```python
# 参数化查询
query = "SELECT * FROM products WHERE name = :name"
db.execute(query, {"name": user_input})

# 或使用 ORM
db.query(Product).filter(Product.name == user_input).all()
```

---

### 模式 5: 敏感数据脱敏

#### 问题: 日志泄露敏感信息

❌ **危险代码**:

```python
logger.info(f"API调用: key={api_key}, response={response}")
```

✅ **安全代码**:

```python
def mask_sensitive(text: str, show_chars: int = 4) -> str:
    if len(text) <= show_chars:
        return "***"
    return text[:show_chars] + "***"

logger.info(f"API调用: key={mask_sensitive(api_key)}, response={response}")
```

---

## 📦 代码组织模式

### 模式 6: 服务层拆分

#### 问题: 路由中包含业务逻辑

❌ **混乱代码**:

```python
@router.post("/products")
async def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    # 业务逻辑直接写在路由中
    product = Product(**data.dict())
    db.add(product)
    db.commit()
    
    # 发送通知
    send_notification(product)
    
    # 更新缓存
    cache.set(f"product:{product.id}", product)
    
    return product
```

✅ **清晰代码**:

```python
# routes/products.py
@router.post("/products")
async def create_product(
    data: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    return await service.create_product(data)

# services/product_service.py
class ProductService:
    async def create_product(self, data: ProductCreate) -> Product:
        product = Product(**data.dict())
        self.db.add(product)
        self.db.commit()
        
        await self._send_notification(product)
        await self._update_cache(product)
        
        return product
```

**优点**: 职责清晰,易于测试

---

### 模式 7: 配置管理

#### 问题: 硬编码配置

❌ **硬编码**:

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 散落在代码中
ALLOWED_EXTENSIONS = ['.csv', '.xlsx']
```

✅ **集中管理**:

```python
# config.py
class Settings(BaseSettings):
    max_file_size: int = 10 * 1024 * 1024
    allowed_extensions: List[str] = ['.csv', '.xlsx']
    
    class Config:
        env_file = ".env"

settings = Settings()

# 使用
if file_size > settings.max_file_size:
    raise ValueError("文件过大")
```

---

## 🧪 测试优化模式

### 模式 8: Fixture 复用

#### 问题: 重复的测试数据准备

❌ **重复代码**:

```python
def test_create_product():
    user = User(username="test", email="test@example.com")
    db.add(user)
    db.commit()
    # 测试逻辑...

def test_update_product():
    user = User(username="test", email="test@example.com")
    db.add(user)
    db.commit()
    # 测试逻辑...
```

✅ **使用 Fixture**:

```python
@pytest.fixture
def test_user(db):
    user = User(username="test", email="test@example.com")
    db.add(user)
    db.commit()
    return user

def test_create_product(test_user):
    # 直接使用 test_user
    pass

def test_update_product(test_user):
    # 直接使用 test_user
    pass
```

---

## 🔄 重构模式

### 模式 9: 提取函数

#### 问题: 函数过长

❌ **过长函数**:

```python
def process_order(order_id: int):
    # 50 行代码...
    # 验证订单
    # 计算价格
    # 更新库存
    # 发送通知
    # 记录日志
    pass
```

✅ **拆分函数**:

```python
def process_order(order_id: int):
    order = _validate_order(order_id)
    total = _calculate_total(order)
    _update_inventory(order)
    _send_notification(order)
    _log_order(order)
    return order

def _validate_order(order_id: int) -> Order:
    # 验证逻辑
    pass

def _calculate_total(order: Order) -> Decimal:
    # 计算逻辑
    pass
```

**原则**: 每个函数只做一件事

---

### 模式 10: 使用类型注解

#### 问题: 缺少类型信息

❌ **无类型**:

```python
def get_user(user_id):
    return db.query(User).filter_by(id=user_id).first()
```

✅ **有类型**:

```python
def get_user(user_id: int) -> User | None:
    return db.query(User).filter_by(id=user_id).first()
```

**优点**: IDE 提示更好,减少错误

---

## 📊 优化优先级

### P0 - 立即优化
- SQL 注入风险
- 敏感数据泄露
- 严重性能问题(N+1 查询)

### P1 - 本周优化
- 缺少超时配置
- 缺少分页限制
- 代码重复严重

### P2 - 可延后
- 函数过长
- 缺少类型注解
- 注释不足

---

## 🔗 参考资料

- [编码规范](coding-guidelines.md) - 编码标准
- [常见陷阱](common-pitfalls.md) - 避免错误
- [代码审查模板](code-review-template.md) - 审查流程
