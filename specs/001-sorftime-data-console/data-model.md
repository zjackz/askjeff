# Data Model - Sorftime 数据智能控制台

> 实体均以 SQLAlchemy Declarative Base 建模，数据库使用 PostgreSQL 15，命名采用 snake_case。

## import_batches

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID (PK) | 导入批次唯一标识 |
| filename | Text | 上传的原始文件名 |
| storage_path | Text | 本地存储目录下的文件路径 |
| import_strategy | Enum('overwrite','append','update_only') | 导入策略（覆盖/追加/仅更新已存在记录） |
| status | Enum('pending','running','succeeded','failed') | 导入状态 |
| total_rows | Integer | 文件总行数 |
| success_rows | Integer | 成功写入的行数 |
| failed_rows | Integer | 失败的行数 |
| started_at | timestamptz | 导入开始时间 |
| finished_at | timestamptz | 导入完成时间 |
| sheet_name | Text | 实际解析的 sheet 名称 |
| created_by | UUID | 发起导入的用户 |
| failure_summary | JSONB | 汇总列覆盖率（已映射/未映射列）、警告计数、失败行文件路径、错误类型计数 |
| columns_seen | JSONB | 本次导入实际出现的列列表 |
| archived | Boolean default False | 是否被归档以隐藏在默认列表 |

关系：`ImportBatch` 1 - N `ProductRecord`。删除采用软删除。

## product_records

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID (PK) | 商品记录唯一标识 |
| batch_id | UUID (FK import_batches.id) | 关联的导入批次 ID |
| asin | Text | 亚马逊 ASIN 编号 |
| title | Text | 商品标题 |
| category | Text | 商品类目 |
| price | Numeric(12,2) | 商品价格 |
| currency | Char(3) | 货币代码 |
| sales_rank | Integer | 销量排名 |
| reviews | Integer | 评论条数 |
| rating | Numeric(3,2) | 平均评分 |
| raw_payload | JSONB | 原始入库 JSON 数据 |
| normalized_payload | JSONB | 清洗后的标准化 JSON 数据 |
| validation_status | Enum('valid','warning','error') | 校验结果 |
| validation_messages | JSONB | 校验明细及提示 |
| ingested_at | timestamptz | 记录入库时间 |

索引：`UNIQUE(asin,batch_id)`；`GIN(normalized_payload)`。

## query_sessions

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 问答会话唯一标识 |
| question | Text | 用户的自然语言问题 |
| intent | Text | 识别出的业务意图 |
| sql_template | Text | 生成的 SQL 模板 |
| answer | Text | 返回给用户的答案 |
| references | JSONB | 答案引用的数据片段或来源 |
| deepseek_trace | JSONB | Deepseek 调用链及调试信息 |
| status | Enum('succeeded','failed') | 会话处理状态 |
| error_message | Text | 失败时的错误信息 |
| asked_by | UUID | 提问用户 ID |
| asked_at | timestamptz | 提问时间 |

用于记录自然语言问答上下文及 Deepseek 调用日志。

## export_jobs

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 导出任务唯一标识 |
| export_type | Enum('clean_products','failed_rows') | 导出类型（清洗数据/失败行） |
| filters | JSONB | 导出筛选条件 |
| selected_fields | Text[] | 选中的导出字段 |
| file_format | Enum('csv','xlsx') | 导出文件格式 |
| status | Enum('pending','running','succeeded','failed') | 导出状态 |
| file_path | Text | 本地 `storage/exports/` 路径 |
| started_at | timestamptz | 导出开始时间 |
| finished_at | timestamptz | 导出完成时间 |
| triggered_by | UUID | 触发导出的用户 |
| error_message | Text | 失败时的错误信息 |

## audit_logs

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 审计日志唯一标识 |
| actor_id | UUID | 操作用户 ID |
| action | Text (`import.create`, `chat.ask`, `export.download` 等) | 操作类型 |
| entity_id | UUID | 被操作实体 ID |
| payload | JSONB | 操作上下文和请求参数 |
| created_at | timestamptz | 记录时间 |

所有实体通过 SQLAlchemy relationship 暴露，Pydantic Schema 直接生成 API DTO。
