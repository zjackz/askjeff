# 发布说明模板

> 按需填写，建议复制本模板到 GitHub Release 的描述中。

## 版本信息
- 版本号：vX.Y.Z
- 发布日期：YYYY-MM-DD
- 目标分支：001-sorftime-data-console

## 变更摘要
- 🧩 新功能
  - 
- 🐛 修复
  - 
- ⚙️ 基础设施 / CI
  - 
- 🧪 测试
  - 
- 📚 文档
  - 

## 升级指南
- 无破坏性变更/或说明需要注意的配置/数据迁移。
- 首次按“容器优先”方式启动：`make up`。

## 验证清单
- 后端健康检查：`curl http://localhost:8000/health` 应返回 200。
- 前端入口：访问 `http://localhost:5173` 可正常显示仪表盘。
- 核心功能：
  - 导入 CSV（/import）→ 列表显示批次。
  - 聊天问答（/chat）→ 返回回答与引用批次。
  - 数据导出（/export）→ 创建导出任务并可下载。

## 回滚步骤
- `make down` 停止服务。
- Git 回退至上一个稳定标签（例如 vX.Y.(Z-1)）：
  - `git checkout 001-sorftime-data-console && git pull`
  - `git checkout vX.Y.(Z-1)`（或 `git reset --hard vX.Y.(Z-1)`）
  - `make up`

## 兼容性与影响范围
- 数据库：无变更/或列出 Alembic 迁移编号影响的表。
- API 契约：兼容/或列出变更接口。
- 前端：浏览器兼容性不变（Chrome/Edge 最新版）。

## 已知问题
- 如有，列出并给出 workaround。

