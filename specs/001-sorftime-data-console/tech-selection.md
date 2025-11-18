# 技术选型建议 - Sorftime 数据智能控制台

> 目标：在保证交付速度与团队现有能力的前提下，提供可验证、可扩展的前后端栈选择，并说明取舍理由与替代方案。

## 前端

- **UI 组件 / 布局**：Vue 3 + Vite + Vue Element Admin（Element Plus）。理由：现有模板与组件库可直接复用，中文文档成熟，表格/表单/菜单/权限路由能力现成；对比 React/Ant Design，可减少样式与权限路由的二次开发。
- **状态管理**：Pinia。理由：轻量、类型友好，支持模块化与持久化插件，适配 Vue 3 Composition API。
- **路由与权限**：Vue Router + 自定义路由守卫（基于角色）。理由：与 Vue Element Admin 预置的动态路由/菜单结构兼容，可通过后端返回的角色声明生成菜单。
- **表格/图表**：Element Plus Table（大数据量场景开启虚拟滚动）+ ECharts。理由：Element Table 支持筛选、排序、列显示控制；ECharts 满足趋势/对比图需求，社区示例丰富。
- **HTTP 客户端**：Axios。理由：成熟的请求/响应拦截器生态，便于统一处理鉴权与错误提示。
- **样式与主题**：基于 Element Plus 主题变量实现亮/暗或品牌主题，配置存放 `frontend/src/styles/theme/`，提供示例切换组件。

## 后端

- **框架**：FastAPI + Pydantic v2。理由：类型安全、自动文档生成，易于定义合约与校验导入数据。
- **ORM 与数据库**: SQLAlchemy 2.0 + Alembic, PostgreSQL 15。理由：满足批次/产品/日志结构化与事务要求，支持 JSON/索引优化；Alembic 便于迁移。
- **任务执行**：FastAPI BackgroundTasks。理由：满足导入/导出的短任务，无需独立 worker，配合 streaming 提供进度。
- **外部服务**：Deepseek 官方 SDK + HTTPX。理由：降低自定义协议工作量；HTTPX 用于回退或自定义超时重试。
- **存储目录**：本地挂载 `backend/storage/{imports,exports}/`。理由：Compose 卷便于导入/导出文件持久化与排障。

## 测试与验证

- **API/单测**：Pytest + HTTPX（Mock Deepseek）。理由：快速覆盖导入/导出/问答 API。
- **前端**：Vitest/组件快照 + Playwright（官方容器镜像）。理由：覆盖上传/问答/导出主要交互与降级路径。
- **性能**：k6（导入/导出吞吐）；Deepseek P90/P95 延迟使用 stub 模拟与降级验证；报告存放 `scripts/perf/*.md`。

## 部署与运维

- **运行模式**：开发/测试/生产统一使用 Docker Compose；生产由 systemd 管理 Compose stack，单机或轻量容器主机即可。理由：降低环境漂移，符合宪章“容器优先”要求。
- **日志与审计**：Python logging（JSON 格式）+ PostgreSQL `audit_logs`；前端展示日志中心页面，支持基础筛选与 AI 辅助诊断。
- **监控指针**：导入/导出成功率与耗时、Deepseek 错误率、批次失败率/超时告警。

## 替代方案与取舍

- **前端 React/AntD**：若客户强制要求 React，可改用 Ant Design Pro + Zustand/Redux Toolkit；成本：重建权限路由/菜单守卫与主题，改写现有页面与测试。
- **任务队列**：若导入/导出耗时显著上升，可引入 Celery/RQ + Redis，但当前需求由 BackgroundTasks 满足，避免新依赖。
- **对象存储**：若本地卷空间或多机部署成为瓶颈，可迁移导入/导出文件至 S3 兼容存储并在数据库记录 URL。

## 结论

沿用 Vue Element Admin + FastAPI/PostgreSQL 的组合，在团队已有资产基础上最小化定制开发和学习成本；满足当前导入/问答/导出的性能与可观测性需求，并保留 React/AntD 与队列/对象存储的升级通道。
