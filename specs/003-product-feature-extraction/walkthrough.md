# 003 LLM 产品特征提取 - 验证报告

## 1. 功能概述

本功能允许用户上传 Excel/CSV 文件，利用 DeepSeek LLM 自动提取产品特征字段（如电池容量、材质等），并支持导出结果。

## 2. 变更内容

### 后端 (FastAPI)

- **Models**: 新增 `ExtractionTask` 和 `ExtractionItem` 表。
- **Services**:
  - `DeepseekClient`: 新增 `extract_features` 方法，调用 DeepSeek API 进行 JSON 提取。
  - `ExtractionService`: 处理文件解析、任务创建、异步执行和结果导出。
- **API**: 新增 `/api/extraction` 路由模块，提供上传、启动、查询、导出接口。

### 前端 (Vue 3)

- **API Client**: `src/api/extraction.ts`
- **View**: `src/views/extraction/index.vue`
  - 文件上传 (Drag & Drop)
  - 动态字段配置 (Tags Input)
  - 任务状态轮询与进度展示
  - 结果导出
- **Router**: 注册 `/extraction` 路由。
- **Menu**: 在侧边栏添加入口。

## 3. 验证步骤

### 3.1 自动化测试 (Docker)

已编写集成测试 `backend/tests/api/test_extraction.py`，并在 Docker 环境中验证通过。

测试覆盖率：
- ✅ 文件上传与解析
- ✅ 任务创建与状态流转
- ✅ DeepSeek API Mock 调用
- ✅ 结果导出 Excel 格式校验

运行命令：

```bash
docker exec askjeff-dev-backend-1 poetry run pytest tests/api/test_extraction.py
```

### 3.2 手动验证 (部署环境)

建议在部署环境进行以下手动验证：

1. **上传文件**:
    - 上传一个包含产品描述的 Excel 文件。
    - 确认页面显示文件名和自动识别的列名。

2. **配置字段**:
    - 输入 "电池容量", "材质" 等字段。
    - 点击 "开始提取"。

3. **任务执行**:
    - 观察状态变为 `PROCESSING`。
    - 等待完成后变为 `COMPLETED`。

4. **结果导出**:
    - 点击 "下载结果 Excel"。
    - 打开下载的文件，确认新增了 "电池容量", "材质" 列，且内容已由 AI 填充。

## 4. 关键代码片段

### DeepSeek 提取逻辑

```python
prompt = (
    "你是一个电商产品专家。请根据以下产品信息，提取指定的特征字段。\n\n"
    f"产品信息: {text}\n"
    f"需要提取的字段: {', '.join(fields)}\n\n"
    "请以 JSON 格式返回结果..."
)
```

### 异步任务处理

```python
@router.post("/{task_id}/start")
async def start_extraction(..., background_tasks: BackgroundTasks):
    service.update_task_fields(task_id, target_fields)
    background_tasks.add_task(run_extraction_background, task_id)
```

## 5. 已知限制

- 目前仅支持 DeepSeek 模型。
- 异步任务使用 FastAPI `BackgroundTasks`，重启服务会导致任务丢失（MVP 阶段可接受）。
- 依赖外部 DeepSeek API，需确保网络连通性。
