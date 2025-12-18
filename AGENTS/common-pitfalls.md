# 常见陷阱与解决方案

> 本文档记录 askjeff 项目开发中遇到的典型问题和最佳实践,帮助 AI 和开发者避免重复踩坑。

**最后更新**: 2025-12-18

---

## 🔥 高频问题 TOP 10

### 1. Pydantic 字段名大小写不匹配

**问题**: API 返回 `requestLeft`,但 Pydantic 模型定义为 `RequestLeft`,导致字段解析为 None

❌ **错误示例**:

```python
class SortimeResponse(BaseModel):
    RequestLeft: int  # 字段名不匹配
```

✅ **正确做法**:

```python
class SortimeResponse(BaseModel):
    request_left: int = Field(alias="requestLeft")
    
    model_config = ConfigDict(
        populate_by_name=True  # 允许使用 alias 或字段名
    )
```

**诊断方法**: 查看日志中的 `raw_response`,对比模型定义

---

### 2. Docker 环境变量未生效

**问题**: 修改 `.env` 文件后,容器内的环境变量没有更新

❌ **错误做法**:

```bash
# 修改 .env 后直接访问
vim .env
# 期望立即生效 ❌
```

✅ **正确做法**:

```bash
# 修改 .env 后重启容器
vim .env
docker compose -f infra/docker/compose.yml down
docker compose -f infra/docker/compose.yml up -d
```

**原因**: Docker Compose 只在容器启动时读取环境变量

---

### 3. 数据库迁移冲突

**问题**: 多人同时生成迁移文件,导致版本冲突

❌ **错误流程**:

```bash
# 直接生成迁移
alembic revision --autogenerate -m "add field"
```

✅ **正确流程**:

```bash
# 1. 先拉取最新代码
git pull

# 2. 检查是否有新的迁移
docker exec askjeff-dev-backend-1 alembic history

# 3. 应用所有迁移
docker exec askjeff-dev-backend-1 alembic upgrade head

# 4. 再生成新迁移
docker exec askjeff-dev-backend-1 alembic revision --autogenerate -m "add field"
```

**预防**: 在 tasks.md 中协调数据库变更

---

### 4. 外部 API 调用无超时

**问题**: 外部 API 响应慢或挂起,导致请求永久阻塞

❌ **错误示例**:

```python
response = httpx.get(url)  # 无超时设置
```

✅ **正确做法**:

```python
response = httpx.get(
    url,
    timeout=30.0,  # 默认 30 秒
    # 或更细粒度控制
    timeout=httpx.Timeout(
        connect=5.0,   # 连接超时
        read=30.0,     # 读取超时
        write=10.0,    # 写入超时
        pool=5.0       # 连接池超时
    )
)
```

**最佳实践**: 所有外部 API 调用都应设置超时

---

### 5. 前端 API 调用无 Loading 状态

**问题**: 用户点击按钮后无反馈,不知道是否在处理

❌ **错误示例**:

```typescript
const handleSubmit = async () => {
  await api.submitData(formData)
  ElMessage.success('提交成功')
}
```

✅ **正确做法**:

```typescript
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  try {
    await api.submitData(formData)
    ElMessage.success('提交成功')
  } catch (error) {
    ElMessage.error('提交失败,请重试')
  } finally {
    loading.value = false
  }
}
```

**UI 绑定**:

```vue
<el-button :loading="loading" @click="handleSubmit">提交</el-button>
```

---

### 6. 敏感数据未脱敏记录

**问题**: 日志中记录了完整的密码、Token 等敏感信息

❌ **错误示例**:

```python
logger.info(f"User login: {username}, password: {password}")
```

✅ **正确做法**:

```python
logger.info(f"User login: {username}, password: ***")

# 或使用工具函数
def mask_sensitive(text: str, show_chars: int = 4) -> str:
    if len(text) <= show_chars:
        return "***"
    return text[:show_chars] + "***"

logger.info(f"API Key: {mask_sensitive(api_key)}")
```

**规则**: 密码、Token、API Key 一律脱敏

---

### 7. 分页查询无上限

**问题**: 用户请求 `page_size=999999`,导致数据库压力过大

❌ **错误示例**:

```python
@router.get("/products")
def list_products(page_size: int = 50):
    return db.query(Product).limit(page_size).all()
```

✅ **正确做法**:

```python
@router.get("/products")
def list_products(page_size: int = Query(50, ge=1, le=200)):
    # Pydantic 自动校验 1 <= page_size <= 200
    return db.query(Product).limit(page_size).all()
```

**统一规范**: 所有分页接口 `page_size` 最大值为 200

---

### 8. N+1 查询问题

**问题**: 循环中查询关联数据,导致大量数据库请求

❌ **错误示例**:

```python
products = db.query(Product).all()
for product in products:
    # 每次循环都查询数据库 ❌
    category = db.query(Category).filter_by(id=product.category_id).first()
```

✅ **正确做法**:

```python
from sqlalchemy.orm import joinedload

products = db.query(Product).options(
    joinedload(Product.category)  # 一次性加载关联数据
).all()

for product in products:
    category = product.category  # 无额外查询
```

**诊断**: 开启 SQL 日志,检查查询次数

---

### 9. 错误提示不友好

**问题**: 直接抛出英文技术错误,用户无法理解

❌ **错误示例**:

```python
raise ValueError("Invalid input")
```

前端显示: "ValueError: Invalid input"

✅ **正确做法**:

```python
# 后端
raise HTTPException(
    status_code=400,
    detail="输入的 ASIN 格式不正确,请检查后重试"
)

# 前端
catch (error) {
  const message = error.response?.data?.detail || '操作失败,请稍后重试'
  ElMessage.error(message)
}
```

**原则**: 错误提示必须中文且可执行

---

### 10. 文件上传无校验

**问题**: 用户上传超大文件或恶意文件类型

❌ **错误示例**:

```python
@router.post("/upload")
async def upload_file(file: UploadFile):
    content = await file.read()
    # 直接保存,无校验 ❌
```

✅ **正确做法**:

```python
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload_file(file: UploadFile):
    # 1. 检查文件扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"不支持的文件类型,仅支持: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # 2. 检查文件大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"文件过大,最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB")
    
    # 3. 保存文件
    ...
```

---

## 🛠️ 调试技巧

### 快速定位问题

1. **后端 API 报错** → 先查日志,再看代码

   ```bash
   docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c \
   "SELECT * FROM system_logs WHERE level='error' ORDER BY timestamp DESC LIMIT 5;"
   ```

2. **前端白屏** → 打开浏览器控制台,查看 Console 和 Network
   
3. **数据库查询慢** → 使用 EXPLAIN 分析

   ```sql
   EXPLAIN ANALYZE SELECT * FROM products WHERE category_id = 1;
   ```

4. **Docker 容器无法启动** → 查看容器日志

   ```bash
   docker logs askjeff-dev-backend-1
   ```

---

## 📋 最佳实践速查

### 后端

| 场景 | 最佳实践 |
|------|---------|
| API 超时 | 默认 30s,最大 60s |
| 分页上限 | 最大 200 条/页 |
| 文件上传 | 最大 10MB,校验扩展名 |
| 密码存储 | 使用 bcrypt,加盐哈希 |
| 日志级别 | info(业务) / error(异常) / warning(警告) |

### 前端

| 场景 | 最佳实践 |
|------|---------|
| Loading 状态 | 所有异步操作必须有 |
| 错误提示 | 中文 + 可执行建议 |
| 表单校验 | 实时校验 + 首错聚焦 |
| 时间格式 | YYYY-MM-DD HH:mm:ss |
| 分页配置 | [20, 50, 100, 200],默认 50 |

---

## 🔄 持续更新

遇到新问题时,请按以下格式添加:

```markdown
### X. 问题标题

**问题**: 简短描述问题现象

❌ **错误示例**:
\`\`\`
错误代码
\`\`\`

✅ **正确做法**:
\`\`\`
正确代码
\`\`\`

**原因/诊断**: 说明为什么会出现这个问题
```

**维护者**: 开发团队共同维护
