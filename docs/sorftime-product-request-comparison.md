# Sorftime ProductRequest API 测试结果对比

## 测试目的

对比 Sorftime ProductRequest API 在传入单个 ASIN 和多个 ASIN（逗号分隔）时的返回数据结构差异。

## 测试 ASIN

- **单个 ASIN**: `B0G3NCGSHC`
- **多个 ASIN**: `B0G3NCGSHC,B0G4VWXFTZ`

## 测试方法

```bash
# 测试 1: 单个 ASIN
curl -X POST "http://localhost:8001/api/v1/sorftime/test/product" \
  -H "Content-Type: application/json" \
  -d '{"ASIN": "B0G3NCGSHC", "domain": 1}'

# 测试 2: 多个 ASIN
curl -X POST "http://localhost:8001/api/v1/sorftime/test/product" \
  -H "Content-Type: application/json" \
  -d '{"ASIN": "B0G3NCGSHC,B0G4VWXFTZ", "domain": 1}'
```

## 测试结果

### 响应结构对比

| 字段 | 单个 ASIN | 多个 ASIN | 说明 |
|------|----------|----------|------|
| `Code` | 0 | 0 | 成功状态码 |
| `Message` | null | null | 无错误消息 |
| `RequestLeft` | 数字 | 数字 | 剩余 Quota |
| `RequestConsumed` | 1 | 2 | 消耗 Quota（每个 ASIN 消耗 1） |
| `Data` 类型 | **dict** | **dict** | ⚠️ 都是字典类型 |

### Data 字段结构

根据 Sorftime API 文档和实际测试：

#### 单个 ASIN 返回

```json
{
  "Code": 0,
  "Message": null,
  "RequestLeft": 3790,
  "RequestConsumed": 1,
  "Data": {
    "Asin": "B0G3NCGSHC",
    "Title": "...",
    "Photo": [...],
    "Price": 1999,
    "Ratings": 4.5,
    "RatingsCount": 1234,
    "BsrCategory": [...],
    "Brand": "...",
    // ... 其他产品字段
  }
}
```

**特点**：
- `Data` 是一个 **字典对象**
- 直接包含单个产品的所有字段
- 字段名首字母大写（如 `Asin`, `Title`, `Photo`）

#### 多个 ASIN 返回

```json
{
  "Code": 0,
  "Message": null,
  "RequestLeft": 3788,
  "RequestConsumed": 2,
  "Data": {
    "B0G3NCGSHC": {
      "Asin": "B0G3NCGSHC",
      "Title": "...",
      "Photo": [...],
      // ... 产品字段
    },
    "B0G4VWXFTZ": {
      "Asin": "B0G4VWXFTZ",
      "Title": "...",
      "Photo": [...],
      // ... 产品字段
    }
  }
}
```

**特点**：
- `Data` 是一个 **字典对象**
- 以 ASIN 为 key，产品数据为 value
- 每个产品数据结构与单个 ASIN 相同

## 关键发现

### 1. 数据结构差异

| 场景 | Data 类型 | 数据访问方式 |
|------|----------|------------|
| **单个 ASIN** | `dict` | `data["Asin"]`, `data["Title"]` |
| **多个 ASIN** | `dict` | `data["B0G3NCGSHC"]["Asin"]`, `data["B0G4VWXFTZ"]["Title"]` |

### 2. Quota 消耗

- 单个 ASIN：消耗 1 个 Quota
- 多个 ASIN：消耗 N 个 Quota（N = ASIN 数量）

### 3. 字段命名规范

所有字段名都是 **首字母大写**：
- `Asin` (不是 `asin`)
- `Title` (不是 `title`)
- `Photo` (不是 `photo`)
- `Price` (不是 `price`)
- `Ratings` (不是 `ratings`)
- `RatingsCount` (不是 `ratingsCount`)
- `BsrCategory` (不是 `bsrCategory`)

## 对代码的影响

### 当前问题

在 `APIImportService._normalize_product_data()` 中：

```python
def _normalize_product_data(self, data: dict) -> dict:
    # 当前代码假设字段名是小写的
    return {
        "asin": data.get("Asin") or data.get("asin"),  # ✅ 正确
        "title": data.get("Title") or data.get("title"),  # ✅ 正确
        "image": image,
        "price": data.get("Price") or data.get("price"),  # ✅ 正确
        "ratings": data.get("Ratings") or data.get("ratings"),  # ✅ 正确
        "ratingsCount": data.get("RatingsCount") or data.get("ratingsCount"),  # ✅ 正确
        # ...
    }
```

### 处理多个 ASIN 的逻辑

在 `_fetch_details_batch()` 中需要处理两种情况：

```python
async def _fetch_details_batch(self, asins: list[str], domain: int) -> list[dict]:
    # 调用 API
    response = await client.product_request(
        asin=",".join(asins),  # 逗号分隔
        trend=0,
        domain=domain
    )
    
    # 解析返回数据
    data = response.data
    products = []
    
    if isinstance(data, dict):
        # 判断是单个产品还是多个产品
        if "Asin" in data:
            # 单个产品：直接是产品数据
            products = [data]
        else:
            # 多个产品：以 ASIN 为 key
            products = list(data.values())
    
    return [self._normalize_product_data(p) for p in products]
```

## 建议

### 1. 统一数据提取逻辑

创建辅助函数处理 ProductRequest 的返回：

```python
def _extract_products_from_response(self, data: Any) -> list[dict]:
    """
    从 ProductRequest 响应中提取产品列表
    
    处理两种情况：
    1. 单个 ASIN：Data 直接是产品对象
    2. 多个 ASIN：Data 是 {ASIN: 产品对象} 的字典
    """
    if not isinstance(data, dict):
        return []
    
    # 检查是否是单个产品（包含 Asin 字段）
    if "Asin" in data or "asin" in data:
        return [data]
    
    # 多个产品：提取所有值
    return list(data.values())
```

### 2. 优化批量查询

- 使用逗号分隔的 ASIN 字符串可以减少 API 调用次数
- 但每个 ASIN 仍然消耗 1 个 Quota
- 建议每次批量查询 10-20 个 ASIN

### 3. 错误处理

- 如果某个 ASIN 无效，整个请求可能失败
- 需要添加重试逻辑
- 考虑分批处理，避免单个失败影响整批

## 完整的测试数据

测试数据已保存到：
- 单个 ASIN: `/tmp/single_asin.json`
- 多个 ASIN: `/tmp/multiple_asins.json`

可以使用以下命令查看：

```bash
cat /tmp/single_asin.json | jq '.'
cat /tmp/multiple_asins.json | jq '.'
```

## 总结

1. ✅ **单个和多个 ASIN 都返回 dict 类型**
2. ✅ **字段名都是首字母大写**
3. ⚠️ **单个 ASIN 直接返回产品对象，多个 ASIN 返回 {ASIN: 产品} 字典**
4. ⚠️ **需要在代码中区分这两种情况**
5. ✅ **当前的 `_normalize_product_data` 已经支持大小写兼容**
6. ⚠️ **需要优化 `_fetch_details_batch` 的数据提取逻辑**
