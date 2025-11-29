# 技术实施计划 - 003 LLM 产品特征提取

## 1. 技术架构

### 后端 (FastAPI)
- **API 设计**: 新增 `/api/extraction` 路由模块
- **数据处理**: 使用 `pandas` 处理 Excel/CSV 读取与导出
- **LLM 集成**: 封装 `DeepSeekService`，使用 `httpx` 调用 DeepSeek API
- **任务管理**:
  - 使用数据库表 `extraction_tasks` 和 `extraction_items` 记录状态
  - 使用 FastAPI `BackgroundTasks` 处理异步抽取任务 (MVP阶段，无需引入 Celery/Redis)
- **数据库**: PostgreSQL

### 前端 (Vue 3 + Element Plus)
- **新页面**: `src/views/extraction/index.vue`
- **交互流程**:
  1. 文件上传 (复用或新建 Upload 组件)
  2. 字段选择 (动态添加 Tag/Input)
  3. 任务监控 (轮询状态 + 进度条)
  4. 结果预览与导出

## 2. 数据模型

### `extraction_tasks`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| filename | String | 原文件名 |
| status | Enum | PENDING, PROCESSING, COMPLETED, FAILED |
| target_fields | JSON | 用户需要抽取的字段列表 |
| created_at | DateTime | 创建时间 |

### `extraction_items`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| task_id | UUID | 外键 |
| original_data | JSON | 原始行数据 |
| extracted_data | JSON | 抽取结果 |
| status | Enum | PENDING, SUCCESS, FAILED |
| error_message | String | 错误信息 |

## 3. API 接口定义

- `POST /api/extraction/upload`: 上传文件，返回预览数据和列名
- `POST /api/extraction/start`: 提交抽取任务 (参数: file_id, target_fields) -> 返回 task_id
- `GET /api/extraction/tasks/{task_id}`: 获取任务进度和统计
- `GET /api/extraction/tasks/{task_id}/export`: 导出 Excel

## 4. 核心逻辑 (DeepSeek Prompt)

```text
你是一个电商产品专家。请根据以下产品信息，提取指定的特征字段。

产品信息: {row_json_data}
需要提取的字段: {target_fields}

请以 JSON 格式返回结果，key 为字段名，value 为提取出的内容。如果无法提取，value 请留空。
```

## 5. 验证计划

### 自动化测试
- 单元测试: `DeepSeekService` Mock 测试
- 集成测试: 上传 -> 启动 -> 模拟完成 -> 导出 流程

### 手动验证
- 上传真实 Excel 文件
- 验证 DeepSeek 返回结果的准确性
- 验证导出文件的格式
