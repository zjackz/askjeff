# 任务分解：Sorftime API 对接 (006)

- [x] **Step 1: API 文档解析** <!-- id: 0 -->
  - [x] 获取 PDF 文本内容
  - [x] 整理并生成 `docs/sorftime_api_docs.md`
  - [x] 确认所有可用接口和参数

- [ ] **Step 2: 数据模型定义** <!-- id: 1 -->
  - [ ] 创建 `backend/app/services/sorftime/models.py`
  - [ ] 定义请求参数模型 (Category, Product, Keyword)
  - [ ] 定义响应数据模型

- [ ] **Step 3: 客户端开发** <!-- id: 2 -->
  - [ ] 创建 `backend/app/services/sorftime/client.py`
  - [ ] 实现基础连接和鉴权逻辑
  - [ ] 实现各业务接口方法

- [ ] **Step 4: 后台测试功能开发** <!-- id: 4 -->
  - [ ] 创建 API 路由 `backend/app/api/v1/endpoints/sorftime_test.py`
  - [ ] 实现 `POST /api/v1/sorftime/test/product` 接口
  - [ ] 实现 `POST /api/v1/sorftime/test/category` 接口
  - [ ] 注册路由到主应用

- [ ] **Step 5: MCP 集成与测试** <!-- id: 3 -->
  - [ ] 注册 MCP 工具
  - [ ] 编写测试用例
  - [ ] 验证端到端流程
