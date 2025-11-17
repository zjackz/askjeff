# 发布流程（容器优先）

本文档说明如何为仓库创建版本发布，并确保质量稳定。

## 版本规范
- 使用语义化版本：`vX.Y.Z`
  - X：重大不兼容变更
  - Y：向后兼容功能增加
  - Z：向后兼容修复/优化

## 预检清单
在本地或 CI 需通过以下检查：
- 后端：`make test-backend`（ruff + pytest 全通过）
- 前端：`make lint-frontend`（ESLint 通过）
- 中文占位检查：`python3 scripts/check_cn.py` 通过
- 容器冒烟：`make up` 后访问 `http://localhost:8000/health` 与 `http://localhost:5173`

## 打标签与发布
1) 选择版本号，例如 `v0.1.0`
2) 在仓库根目录执行：
```bash
make tag-and-push VERSION=0.1.0 MSG="简要说明，例如：容器优先改造与稳定化"
```
3) 推送标签后，GitHub Actions 会自动创建 Release，并生成发布说明（可在 Releases 页面补充细节）。

> 发布说明模板见：`docs/release/RELEASE_TEMPLATE.md`

## 回滚策略
- 若发布出现问题，可按下列方式回滚：
```bash
git checkout 001-sorftime-data-console
git pull
git reset --hard v0.0.9   # 上一个稳定版本
make up
```

## 常见问题
- CI 没有触发：确认推送的是 `v*.*.*` 的标签格式。
- 容器起不来：执行 `make backend-logs` / `make frontend-logs` 查看日志排查；常见为网络拉包慢/端口占用。
- 仅保留一个分支：本仓库采用“单主干”模式，发版靠标签，无需再维护多分支。

