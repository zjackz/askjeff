# Implementation Plan: 数据洞察页面产品列表化改版

**Branch**: `002-insight-product-list` | **Date**: 2025-11-18 | **Spec**: specs/002-insight-product-list/spec.md  
**Input**: `/specs/002-insight-product-list/spec.md`

## 摘要

- 目标：将数据洞察页面主区域改为上传产品列表，提供完整筛选/排序/分页与行详情，同时保留右下角悬浮 chat 弹窗交互，并支持导出当前筛选条件。
- 方案：前端在现有 Vue 3 + Element Plus 页面中重构主容器与过滤器，复用后端产品查询接口与 chat 交互，新增筛选导出与状态保持能力、契约文档与观测埋点，无需改动数据模型和导入流程。

## 技术背景

- **语言/版本**：前端 Vue 3 + TypeScript；后端 Python 3.12 + FastAPI；通用工具 Vite、Pinia、Vue Router、Element Plus。
- **核心依赖**：后端使用 Pydantic v2、SQLAlchemy 2.0、Alembic、HTTPX；前端使用 Vue Element Admin 体系和 ECharts（本特性侧重表格/弹窗）。
- **存储/消息**：PostgreSQL 15 存储产品/批次；本需求不新增消息通道，复用现有存储。
- **测试策略**：前端 `pnpm --prefix frontend lint`，后端 `poetry run ruff check && pytest`，上述命令均在 Docker Compose 容器内执行；交互验收按 quickstart 步骤手测。
- **部署/目标平台**：开发与生产均由 Docker Compose 管理，dev 端口 5174/8001；遵循“容器优先与环境一致性”。
- **性能&约束**：列表查询 80% 在 3 秒内返回、首屏筛选≤5 秒；chat 回复或错误提示 90% 在 10 秒内；页面加载后 chat 入口 1 秒内可见；满意度≥80%。

## 宪章核对（必须全部满足）

1. **P1 用户意图**：交付产品列表化的数据洞察界面与悬浮 chat 弹窗，实现筛选、详情、问答三种主要操作在同页完成。  
2. **P2 独立价值**：用户故事覆盖 P1 列表筛选、P2 悬浮 chat、P2 导出筛选条件；现规格有 3 个清晰故事，可独立验收与回滚。  
3. **P3 合约先行**：定义/确认产品列表查询、详情、筛选导出与 chat 交互契约（见 contracts/products.md），若后端路径不符需先对齐。  
4. **P4 可验证证据**：成功指标 SC-001~SC-004；测试通过 lint+pytest，手动按 quickstart 验证筛选、详情、chat、错误/空态。  
5. **P5 可观测性**：列表筛选/分页/排序/详情与 chat 打开/发送/失败均需埋点耗时与成功率，日志/指标责任人：运营产品负责人。  
6. **P6 中文交付**：前端文案、注释、提交信息、文档均使用中文，保留术语需附中文说明。  
7. **P7 容器一致**：全部开发/测试在 Compose dev 环境执行；前端/后端命令在容器中运行，禁止跳过 env 配置。

## 项目结构

### 文档

```text
specs/002-insight-product-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── products.md
└── tasks.md   # 由 /speckit.tasks 生成
```

### 代码骨架

```text
frontend/
├── src/...
backend/
├── app/...
tests/
├── ...（后端 pytest，前端已有 lint）
```

**结构决策**：沿用现有前后端分离仓库结构，仅改动前端数据洞察页面与可能的后端查询/聊天接口契约，无需新增服务。

## 复杂度追踪（仅在违反宪章时填写）

| 违反项 | 必要性说明 | 放弃更简单方案的原因 |
|--------|------------|----------------------|
| 无 | - | - |
