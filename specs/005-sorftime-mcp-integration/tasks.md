# 任务分解 - 需求 005

## 阶段 1: 调研与验证 (Spike)
- [ ] **Task 1.1**: 编写 Python 脚本测试 Sorftime MCP 接口。
  - 验证 Account-SK 是否有效。
  - 测试不同输入 (ASIN, URL) 的响应格式。
  - 确认 Top 100 数据的字段结构。
  - 输出：`scripts/test_mcp.py` 和接口响应样例。

## 阶段 2: 后端开发
- [ ] **Task 2.1**: 创建 `McpService` 类。
  - 实现基础配置 (API Key, Base URL)。
  - 实现 `fetch_data(input)` 方法。
- [ ] **Task 2.2**: 实现数据转换逻辑。
  - 将 MCP JSON 响应转换为 Pandas DataFrame。
  - 映射字段到 `Product` 模型 (e.g., `title`, `price`, `reviews`, etc.)。
- [ ] **Task 2.3**: 集成 `ImportService`。
  - 调用 `ImportService.process_dataframe` 或类似方法将数据存入 DB。
- [ ] **Task 2.4**: 创建 API 端点 `POST /api/v1/mcp/fetch`。
  - 接收前端请求。
  - 触发 Service 逻辑。
  - 返回结果。

## 阶段 3: 前端开发
- [ ] **Task 3.1**: 更新 API 客户端。
  - 添加 `mcp.ts` 或在 `import.ts` 中添加 fetch 方法。
- [ ] **Task 3.2**: 创建/更新 UI 组件。
  - 在"数据导入"页面或首页添加 "MCP 智能抓取" 卡片/模态框。
  - 输入框 + 提交按钮。
  - 加载状态显示。

## 阶段 4: 测试与交付
- [ ] **Task 4.1**: 编写后端单元测试 (`tests/services/test_mcp_service.py`)。
- [ ] **Task 4.2**: 手动集成测试 (End-to-End)。
- [ ] **Task 4.3**: 更新文档 (User Guide)。
