# Sorftime 数据智能控制台

本项目用于演示如何在最小依赖下实现 Sorftime 表格导入、自然语言问答与数据导出。核心技术栈：FastAPI + PostgreSQL + SQLAlchemy（后端）以及 Vue 3 + Vite + Vue Element Admin（前端）。所有代码、文档与界面均需使用中文。

## 快速启动（Docker Compose）

```bash
git clone <repo>
cd <repo>
docker compose -f infra/docker/compose.yml up -d
```

- `backend/`：FastAPI 服务，默认监听 `8000`
- `frontend/`：Vite + Vue Element Admin，默认监听 `5173`
- `db`：PostgreSQL 15，默认账号/密码 `sorftime`

访问：
- `http://localhost:8000/docs` 查看 API 文档
- `http://localhost:5173` 进入运营后台

## systemd + Docker Compose 部署

1. 在服务器 `/opt/sorftime` 目录拉取代码并配置 `.env`。
2. 创建 systemd 服务：

```ini
# /etc/systemd/system/sorftime.service
[Unit]
Description=Sorftime Console
After=docker.service

[Service]
WorkingDirectory=/opt/sorftime
ExecStart=/usr/bin/docker compose -f infra/docker/compose.yml up -d
ExecStop=/usr/bin/docker compose -f infra/docker/compose.yml down
Restart=always

[Install]
WantedBy=multi-user.target
```

3. 重新加载并启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sorftime.service
```

## 指标与日志

- `scripts/report_metrics.py --days 7` 输出导入/问答/导出指标。
- `scripts/check_cn.py` 检查仓库中文合规。
- `backend/storage/imports/` 与 `backend/storage/exports/` 存放上传/导出文件。

更多细节请参考 `specs/001-sorftime-data-console/quickstart.md`。
