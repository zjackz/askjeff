# API 契约检查清单： Sorftime 数据智能控制台

**目的**：轻量自检 API 契约相关需求的完备性、清晰度与一致性，确保导入/问答/导出/审计接口在规格层面可复核。  
**创建时间**： 2025-11-17  
**关联文档**： `specs/001-sorftime-data-console/spec.md`、`specs/001-sorftime-data-console/plan.md`、`specs/001-sorftime-data-console/tasks.md`  

> 由 `/speckit.checklist` 生成，条目需指明引用的宪章原则（如 P1/P2）。涉及语言的检查请引用 **P6 中文交付**。

## 契约范围与资源建模

- [ ] CHK001 是否罗列全部 API 资源/端点（导入批次、产品/失败行查询、问答、导出、审计日志），并与用户故事/FR 对齐？[Completeness, Spec §FR-001~007/FR-010, P1]
- [ ] CHK002 资源标识与路径（如 `batchId`/`exportId`/`querySessionId`）是否与数据实体定义一致且无术语漂移？[Consistency, Spec §Key Entities, P3]
- [ ] CHK003 是否声明请求/响应 schema 版本或兼容策略，符合“合约先行”要求？[Traceability, Plan §P3 合约先行, P3]

## 请求输入与校验

- [ ] CHK004 Sorftime 导入接口的输入字段、必填校验、导入策略选项及失败行处理规则是否写清？[Completeness, Spec §FR-001/FR-002, P1]
- [ ] CHK005 问答接口是否限定输入长度/安全过滤，并定义 Deepseek 不可用时的返回结构与字段？[Clarity, Spec §FR-005/FR-006, P2]
- [ ] CHK006 导出接口是否定义字段选择、过滤条件、文件格式及超限（>50k 行）行为的需求？[Coverage, Spec §FR-007 & Edge Cases, P4]

## 输出、错误与审计

- [ ] CHK007 是否为各端点定义统一错误响应结构与典型错误枚举（含可追踪码/重试提示）？[Consistency, Gap if missing, P4]
- [ ] CHK008 是否明确需写入审计日志的字段（操作者、时间、条件、外部调用状态等）并在接口文档中标注？[Clarity, Spec §FR-010, P5]

## 性能与限流（轻量）

- [ ] CHK009 导入/问答/导出是否在契约中标注性能或吞吐目标及分页/流式策略（如导出分段），并与 SC-001~003 一致？[Measurability, Spec §SC-001~003 & Edge Cases, P4]

## 安全与权限（轻量）

- [ ] CHK010 API 的认证/权限要求是否与后台角色路由设定一致，并在契约中说明？[Consistency, Spec Assumptions & §FR-009, P2]

## 备注

- 完成项标记 `[x]`，可在行内追加说明或链接。
