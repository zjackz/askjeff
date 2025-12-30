# Bug 修复记录

## Bug: 提交一次生成多条任务

### 问题描述
用户点击"开始抓取"按钮一次,后端会创建2-3个导入批次。

### 根本原因 (已找到!)

**后台任务在处理 ASIN 时重复创建批次**

流程:
1. API 路由创建批次 A (category_id="pending")
2. 启动后台线程,传入 batch_id=A
3. 后台线程获取真实 category_id
4. ❌ **BUG**: 后台线程又创建了新批次 B!

代码问题 (`api_import_service.py` 第 81-95 行):

```python
if batch_id:
    batch = get_batch(batch_id)  # 应该更新这个批次
    batch.status = "running"
else:
    batch = create_batch()  # ❌ 但这里又创建了新批次!
    batch_id = batch.id
```

**为什么会执行 else 分支?**
- 因为在获取 category_id 后,代码逻辑错误地进入了创建新批次的分支

### 解决方案

#### 方案 1: 前端防重复提交 ✅
在函数开始时立即检查并设置标志:

```vue
const handleMcpSubmit = async () => {
  // 立即检查
  if (mcpSubmitting.value) {
    return
  }
  
  // 立即设置标志
  mcpSubmitting.value = true
  
  // 执行提交
  // ...
}
```

**效果**: 可以防止快速双击,但无法防止后台任务重复创建

#### 方案 2: 后端请求去重 ✅
使用请求指纹在5秒内去重:

```python
# 生成请求指纹
request_key = f"{input}:{input_type}:{domain}:{test_mode}:{limit}"
request_hash = hashlib.md5(request_key.encode()).hexdigest()

# 5秒内相同请求返回已有批次
if request_hash in recent_requests:
    if current_time - recent['time'] < 5:
        return existing_batch_id
```

**效果**: 可以防止前端重复请求,但无法防止后台任务重复创建

#### 方案 3: 修复后台任务逻辑 ✅ (核心修复!)
当传入 batch_id 时,更新现有批次而不是创建新批次:

```python
if batch_id:
    # 使用已有批次,更新状态和 metadata
    batch = ImportRepository.get_batch(db, batch_id)
    
    # 更新 metadata (特别是 category_id)
    if batch.import_metadata:
        batch.import_metadata["category_id"] = parsed.get("category_id")
    
    batch.status = "running"
    db.commit()
    # ✅ 不再创建新批次!
else:
    # 只有在没有 batch_id 时才创建
    batch = self._create_batch(...)
```

**优势**:
- ✅ 彻底解决 ASIN 导入时的重复批次问题
- ✅ 正确更新 category_id 到现有批次
- ✅ 保持批次 ID 一致性

### 修改文件
- ✅ `frontend/src/views/import/components/SorftimeImportDialog.vue` - 前端防重复
- ✅ `backend/app/api/routes/imports.py` - 后端请求去重
- ✅ `backend/app/services/api_import_service.py` - 修复后台任务逻辑 (核心)

### 测试验证
- [x] 快速双击按钮,只创建一个批次
- [x] 5秒内重复提交相同参数,返回相同批次 ID
- [x] 不同参数正常创建新批次
- [x] 后端日志显示"Duplicate request detected"

### 优先级
🔴 高 - 会导致重复任务和资源浪费

### 状态
✅ 已修复 (双重保护)

---

**修复时间**: 2025-12-18 17:50  
**修复人**: AI Assistant
