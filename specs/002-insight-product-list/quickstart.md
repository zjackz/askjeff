# Quickstart: 数据洞察页面产品列表化改版

1. **启动依赖（dev 环境，必须用 Compose）**  

   ```bash
   docker compose -f infra/docker/compose.yml up -d
   ```

   确认后端端口 8001、前端 5174。

2. **后端检查**（容器内运行）  

   ```bash
   docker compose -f infra/docker/compose.yml run --rm backend poetry run ruff check
   docker compose -f infra/docker/compose.yml run --rm backend pytest
   ```

3. **前端检查**（容器内运行）  

   ```bash
   docker compose -f infra/docker/compose.yml run --rm frontend pnpm lint
   ```

4. **手动验证流程（自测清单）**  
   - US1 列表与筛选：  
     - 执行组合筛选（批次 ID + 状态 valid/warning/error + ASIN 关键词），确认列表刷新、分页、排序可用。  
     - **筛选条件持久化**：设置筛选条件后刷新页面，确认筛选条件被保留（页码重置为第一页）。
     - 列表为空时出现空态文案，点击"清除筛选"可恢复并清除 localStorage 中的筛选条件。  
     - 点击任一行打开详情抽屉，字段包含 ASIN/标题/批次/状态/时间/价格/评分/排名/校验信息，关闭后筛选与滚动位置保持。  
     - 模拟接口错误（断网或关后端），显示错误提示及重试。  
   - US2 悬浮 chat：  
     - 右下角悬浮按钮始终可见，点击后弹窗不遮挡列表，关闭后恢复列表状态。  
     - 发送问题后显示回复；模拟上游失败或网络错误，展示中文错误提示与重试。  
   - US3 导出筛选：  
     - 设置组合筛选，点击"导出当前筛选"按钮，确认导出任务已创建并显示任务 ID。  
     - 导出请求包含当前筛选条件（批次 ID、ASIN、状态、时间范围）、排序和分页信息。
     - 模拟导出失败，界面展示错误提示，不影响继续筛选。

5. **日志/指标检查**  
   - 确认列表查询、筛选、分页、详情、chat 发送/失败、导出筛选等关键埋点与日志写入可观测平台。  
   - 性能抽检：筛选+排序 80% ≤3s、首屏 ≤5s；chat 入口 1s 内可见、发送 90% ≤10s。  
   - 满意度/任务成功率：收集 ≥10 名用户体验“筛选→详情→chat→导出”闭环，成功率≥90%、满意度≥80%，记录问卷结果。
