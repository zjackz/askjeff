# Tasks: 数据洞察页面产品列表化改版

**输入**：`/specs/002-insight-product-list/` 内的 plan/spec/research/data-model/contracts  
**前置**：plan.md、spec.md 已完成  
**语言合规**：代码、注释、提交记录、任务描述、交付文档均需中文呈现，英文术语需附中文注解。

> 任务按用户故事分组，确保每个故事可独立交付。跨故事依赖仅在必要时声明。

## 阶段 1：基础环境

- [ ] T001 检查并启动 dev Compose 依赖（infra/docker/compose.yml），确保后端 8001、前端 5174 运行
- [ ] T002 [P] 校验前端依赖与 lint 可用（frontend/），复用 quickstart 中的 pnpm lint 命令
- [ ] T003 容器化执行校验：所有 lint/测试通过 Docker Compose 运行，记录命令（infra/docker/compose.yml）

## 阶段 2：通用基础能力

- [X] T010 对齐产品列表/详情/聊天接口契约与后端实现（backend/app/api/routes/products.py，backend/app/api/routes/chat.py），必要时补充查询参数校验与错误码
- [X] T011 [P] 为产品与查询条件定义前端类型与接口封装（frontend/src/views/chat/types.ts），并在 index.vue 引用
- [X] T012 建立产品列表与聊天的可观测性事件埋点方案（frontend/src/views/chat/index.vue），约定事件名/字段并与后端日志字段对齐

## 阶段 3：User Story 1 (P1) 🎯

- **目标**：在数据洞察页面展示上传产品列表，支持批次/ASIN/状态等组合筛选、排序、分页，并可查看行详情与空/错态。
- **独立验证**：使用多批次测试数据，执行组合筛选与排序，查看详情弹窗；触发空态与错误态检查文案与重置操作。

### Tests / Evidence

- [X] T101 [P][US1] 编写或更新页面自测脚本/手动验收清单，覆盖筛选、分页、排序、详情、空/错态（frontend/src/views/chat/index.vue）

### Implementation

- [X] T102 [US1] 重构数据洞察页面主区域为产品表格，增设筛选表单与分页/排序控制（frontend/src/views/chat/index.vue）
- [X] T103 [P][US1] 接入产品列表 API 与参数映射（批次 ID、ASIN 关键词、状态、时间范围、排序），支持列宽自适应与核心列展示（frontend/src/views/chat/index.vue）
- [X] T104 [US1] 实现行详情弹窗/抽屉，展示产品核心字段、所属批次、失败原因，返回后保持筛选与滚动位置（frontend/src/views/chat/index.vue）
- [X] T105 [P][US1] 实现加载中/空态/错误态与“重置筛选/重试”入口（frontend/src/views/chat/index.vue）
- [ ] T106A [US1] 实现筛选条件会话保持与刷新重置（前端状态/存储），含单测/自测清单

### Observability / Docs

- [X] T106 [US1] 为筛选、排序、分页、详情打开/关闭、空/错态记录前端事件并校验日志格式（frontend/src/views/chat/index.vue）

## 阶段 4：User Story 2 (P2) 🎯

- **目标**：在页面右下角提供悬浮 chat 入口，点击弹出对话框进行问答，失败时提示并可重试，不遮挡列表操作。
- **独立验证**：列表可用时点击悬浮入口打开 chat，发送问题获取回复；模拟上游失败查看错误提示与重试；关闭后列表状态保持。

### Tests / Evidence

- [X] T201 [P][US2] 补充手动验收要点，覆盖 chat 悬浮入口可见性、打开/关闭、发送/失败提示（frontend/src/views/chat/index.vue）

### Implementation

- [X] T202 [US2] 添加右下角悬浮 chat 入口与弹窗组件，保证滚动时固定且不遮挡列表（frontend/src/views/chat/index.vue）
- [X] T203 [P][US2] 接入 chat API（POST /api/chat/messages）并处理发送中、成功、失败提示与重试（frontend/src/views/chat/index.vue）

### Observability / Docs

- [X] T204 [US2] 埋点 chat 打开/关闭/发送/失败事件并校验错误提示文案为中文（frontend/src/views/chat/index.vue）

## 阶段 5：User Story 3 (P2)

- **目标**：导出当前筛选条件与当前页结果，支持失败重试。
- **独立验证**：设置组合筛选后导出，校验导出文件/JSON 含筛选条件与分页范围；失败时提示并可重试。

### Tests / Evidence

- [ ] T107 [US3] 验收导出：组合筛选后导出，校验导出文件/JSON 含筛选条件与页码范围，失败提示可重试（frontend/src/views/chat/index.vue）

### Implementation

- [ ] T108 [P][US3] 实现“导出当前筛选”前端触发与后端接口对接（含队列/排队提示），前端路径 `frontend/src/views/chat/index.vue`

## 阶段 6：收尾与跨故事事项

- [ ] T901 更新 quickstart 验收步骤与截图/说明（specs/002-insight-product-list/quickstart.md，必要时前端 README）
- [ ] T902 校验语言合规与可观测性覆盖，补充缺失的中文文案与日志字段说明（frontend/src/views/chat/index.vue，相关埋点方案）
- [ ] T903 运行前后端 lint/pytest 并记录结果，准备发布回归（frontend/，backend/）
- [ ] T301 列表性能验证：筛选+排序 80% ≤3s、首屏 ≤5s，输出报告（scripts/perf/product-list.md）
- [ ] T302 Chat 性能/可见性验证：入口 1s 内可见，发送 90% ≤10s，含失败提示用例
- [ ] T303 任务成功率与满意度调研：同页完成筛选+详情+chat 成功率≥90%，满意度≥80%，收集问卷/样本≥10

## 执行顺序提示

- 用户故事依赖：US1（列表筛选与详情） → US2（悬浮 chat 交互）。US2 依赖列表页面布局完成以避免遮挡。
- 并行示例：T011 类型封装可与 T010 契约确认并行；US1 中 API 接入（T103）与状态处理（T105）可并行；US2 中界面（T202）与发送逻辑（T203）可并行。
- Implementation strategy：先完成 Setup/基础契约与类型，优先交付 US1 作为 MVP（列表+筛选+详情+空/错态），再增量交付 US2 的悬浮 chat，最后统一补 observability 与合规检查。
