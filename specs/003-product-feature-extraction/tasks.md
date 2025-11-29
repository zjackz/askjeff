# 任务分解 - 003 LLM 产品特征提取

## Phase 1: 后端基础与数据模型

- [ ] 定义 SQLAlchemy 模型 `ExtractionTask` 和 `ExtractionItem` <!-- id: 0 -->
- [ ] 创建 Alembic 迁移脚本并应用 <!-- id: 1 -->
- [ ] 定义 Pydantic Schema (`TaskCreate`, `TaskResponse`, `ItemResponse`) <!-- id: 2 -->

## Phase 2: 核心服务实现

- [ ] 实现 `DeepSeekService` <!-- id: 3 -->
  - [ ] 封装 `extract_features(text, fields)` 方法
  - [ ] 处理 API 错误和重试
- [ ] 实现 `ExtractionService` <!-- id: 4 -->
  - [ ] `create_task`: 解析 Excel，创建 DB 记录
  - [ ] `process_task`: 后台任务，遍历 items 调用 DeepSeek
  - [ ] `export_task`: 生成 Excel

## Phase 3: API 接口开发

- [ ] 实现 `POST /api/extraction/upload` <!-- id: 5 -->
- [ ] 实现 `POST /api/extraction/start` <!-- id: 6 -->
- [ ] 实现 `GET /api/extraction/tasks/{task_id}` <!-- id: 7 -->
- [x] 实现 `GET /api/extraction/tasks/{task_id}/export` <!-- id: 8 -->
- [x] 编写后端测试 (Pytest) <!-- id: 9 -->

## Phase 4: 前端开发

- [x] 创建路由和页面 `src/views/extraction/index.vue` <!-- id: 10 -->
- [x] 实现文件上传组件 (支持 Excel/CSV) <!-- id: 11 -->
- [x] 实现字段配置区域 (Dynamic Tags) <!-- id: 12 -->
- [x] 实现任务进度展示 (Progress Bar, Status Badge) <!-- id: 13 -->
- [x] 实现导出按钮 <!-- id: 14 -->

## Phase 5: 验证与优化

- [ ] 联调测试：完整流程跑通 <!-- id: 15 -->
- [ ] 验证 DeepSeek 提取效果 <!-- id: 16 -->
- [ ] 优化 Prompt 以提高准确率 <!-- id: 17 -->
