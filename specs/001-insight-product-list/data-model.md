# Data Model: 数据洞察页面产品列表化改版

## 实体与字段

### 产品记录（ProductItem）
- `id`：唯一标识。
- `asin`：ASIN 编号。
- `title`：产品标题。
- `batch_id`：所属导入批次 ID（关联 ImportBatch）。
- `status`：清洗/校验状态（如 success/failed/pending）。
- `last_updated_at`：最近更新时间。
- `metrics`：核心指标摘要（价格、销量、评分等，结构按现有后端字段复用）。
- `failure_reason`：失败或校验提示（可为空）。

### 查询条件（QueryFilter）
- `batch_id`（可选）：批次 ID。
- `asin_keyword`（可选）：ASIN 或标题关键词。
- `status`（可选）：状态过滤。
- `updated_from` / `updated_to`（可选）：更新时间范围。
- `page` / `page_size`：分页信息。
- `sort_by` / `sort_order`：排序字段及方向。

### 聊天会话（ChatSession）
- `session_id`：会话标识（可由前端生成 UUID）。
- `question`：用户问题。
- `answer`：系统回复。
- `status`：success/failed/pending。
- `created_at` / `completed_at`：时间戳。
- `error_message`：失败原因（可空）。

## 关系
- ProductItem 多对一 ImportBatch（已存在）。
- QueryFilter 为前端查询参数，不入库。
- ChatSession 与 ProductItem 无直接关联，但可在问答内容中引用筛选结果。
