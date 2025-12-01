# 任务分解：Chatbot 数据库交互 (004)

- [ ] **Phase 1: 基础架构改造**
  - [ ] 修改 `DeepseekClient`，支持自定义 System Prompt 和 JSON 响应解析。
  - [ ] 在 `ChatService` 中建立工具注册机制 (Tool Registry)。

- [ ] **Phase 2: 工具实现**
  - [ ] 实现 `query_products` 工具：封装 `ProductService.list_products`。
  - [ ] 实现 `get_batch_status` 工具：封装 `ImportService.get_batch`。
  - [ ] 实现 `analyze_logs` 工具：封装 `LogService.list_logs`。

- [ ] **Phase 3: 逻辑串联**
  - [ ] 改造 `ChatService.ask`，实现“识别-执行-生成”的完整流程。
  - [ ] 编写 Prompt，教会 DeepSeek 何时调用工具。

- [ ] **Phase 4: 测试与优化**
  - [ ] 单元测试：测试工具函数的正确性。
  - [ ] 集成测试：模拟用户提问，验证完整流程。
  - [ ] Prompt 调优：提高意图识别的准确率。
