# Data Model - Sorftime 数据智能控制台

> 实体均以 SQLAlchemy Declarative Base 建模，数据库使用 PostgreSQL 15，命名采用 snake_case。

## import_batches

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID (PK) |
| filename | Text |
| storage_path | Text | 本地存储目录下的文件路径 |
| import_strategy | Enum('overwrite','append','update_only') |
| status | Enum('pending','running','succeeded','failed') |
| total_rows | Integer |
| success_rows | Integer |
| failed_rows | Integer |
| started_at | timestamptz |
| finished_at | timestamptz |
| created_by | UUID |
| failure_summary | JSONB |
| archived | Boolean default False |

关系：`ImportBatch` 1 - N `ProductRecord`。删除采用软删除。

## product_records

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID (PK) |
| batch_id | UUID (FK import_batches.id) |
| asin | Text |
| title | Text |
| category | Text |
| price | Numeric(12,2) |
| currency | Char(3) |
| sales_rank | Integer |
| reviews | Integer |
| rating | Numeric(3,2) |
| raw_payload | JSONB |
| normalized_payload | JSONB |
| validation_status | Enum('valid','warning','error') |
| validation_messages | JSONB |
| ingested_at | timestamptz |

索引：`UNIQUE(asin,batch_id)`；`GIN(normalized_payload)`。

## query_sessions

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID |
| question | Text |
| intent | Text |
| sql_template | Text |
| answer | Text |
| references | JSONB |
| deepseek_trace | JSONB |
| status | Enum('succeeded','failed') |
| error_message | Text |
| asked_by | UUID |
| asked_at | timestamptz |

用于记录自然语言问答上下文及 Deepseek 调用日志。

## export_jobs

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID |
| export_type | Enum('clean_products','failed_rows') |
| filters | JSONB |
| selected_fields | Text[] |
| file_format | Enum('csv','xlsx') |
| status | Enum('pending','running','succeeded','failed') |
| file_path | Text | 本地 `storage/exports/` 路径 |
| started_at | timestamptz |
| finished_at | timestamptz |
| triggered_by | UUID |
| error_message | Text |

## audit_logs

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID |
| actor_id | UUID |
| action | Text (`import.create`, `chat.ask`, `export.download` 等) |
| entity_id | UUID |
| payload | JSONB |
| created_at | timestamptz |

所有实体通过 SQLAlchemy relationship 暴露，Pydantic Schema 直接生成 API DTO。
