#!/usr/bin/make -f
# 统一开发命令（容器优先）
# 使用方法：在仓库根目录执行 make <目标>
# 环境切换：COMPOSE_ENV=test|dev，默认 dev

COMPOSE_ENV ?= dev
PROJECT ?= askjeff-$(COMPOSE_ENV)
COMPOSE_FILE := infra/docker/compose.$(COMPOSE_ENV).yml
# 说明：Compose 默认只会读取“项目目录”的 .env；本仓库的 Compose 文件在 infra/docker/ 下
# 为避免环境变量（如 DEEPSEEK_API_KEY）丢失，统一显式指定根目录 .env
# 兼容不同 Docker 安装方式：优先使用 docker compose，其次 docker-compose
COMPOSE_BIN := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")
ENV_FILE := $(if $(wildcard .env),--env-file .env,)
COMPOSE := $(COMPOSE_BIN) $(ENV_FILE) -p $(PROJECT) -f $(COMPOSE_FILE)

.PHONY: up down restart logs ps backend-logs frontend-logs db-logs rebuild shell-backend shell-frontend test-backend test-frontend test-frontend-e2e test-frontend-all speckit-check help tag release tag-and-push

up:
	$(COMPOSE) up -d --build
	@echo "\n=================================================="
	@echo "🚀 ASKJeff 服务正在启动..."
	@echo "--------------------------------------------------"
	@echo "前端访问地址: http://localhost:5174"
	@echo "后端接口地址: http://localhost:8001/api/v1"
	@echo "健康检查地址: http://localhost:8001/api/health"
	@echo "--------------------------------------------------"
	@echo "提示: 可运行 'make logs' 或 'make ps' 查看状态"
	@echo "==================================================\n"

down:
	$(COMPOSE) down -v

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f --tail=100

ps:
	$(COMPOSE) ps

backend-logs:
	$(COMPOSE) logs backend -f --tail=100

frontend-logs:
	$(COMPOSE) logs frontend -f --tail=100

db-logs:
	$(COMPOSE) logs db -f --tail=100

rebuild:
	$(COMPOSE) build --no-cache

# 进入容器交互式 Shell（便于临时调试）
shell-backend:
	$(COMPOSE) exec backend bash || true

shell-frontend:
	$(COMPOSE) exec frontend bash || true

# 运行后端静态检查与单测（容器内执行）
test-backend:
	$(COMPOSE) exec backend bash -c "poetry run ruff check app tests && poetry run pytest -q"

# 前端 Lint（容器内执行）
lint-frontend:
	$(COMPOSE) exec frontend pnpm lint

# 前端单测（Vitest，容器内）
test-frontend:
	$(COMPOSE) exec frontend bash -lc "cd /app && pnpm test"

# 前端 E2E（Playwright，容器内；依赖 backend 已启动）
test-frontend-e2e:
	$(COMPOSE) exec frontend bash -lc "cd /app && BASE_URL=http://localhost:5174 pnpm exec playwright test --reporter=html"

# 综合前端测试（先跑 Vitest 再跑 Playwright）
test-frontend-all:
	$(COMPOSE) exec frontend bash -lc "cd /app && pnpm test && BASE_URL=http://localhost:5174 pnpm exec playwright test --reporter=html"

# speckit 轻量校验
speckit-check:
	bash scripts/check_speckit.sh

# ========== 发布相关 ==========
# 生成标签：make tag VERSION=0.1.0 MSG="容器优先改造"
tag:
	@if [ -z "$(VERSION)" ]; then echo "[错误] 需要指定 VERSION，例如: make tag VERSION=0.1.0"; exit 1; fi
	@git tag v$(VERSION) -m "${MSG:-Release v$(VERSION)}"
	@echo "已创建标签 v$(VERSION)，可执行: make release VERSION=$(VERSION)"

# 推送标签到远端并触发 GitHub Release
release:
	@if [ -z "$(VERSION)" ]; then echo "[错误] 需要指定 VERSION，例如: make release VERSION=0.1.0"; exit 1; fi
	@git push origin v$(VERSION)
	@echo "已推送标签 v$(VERSION)。稍后在 GitHub Releases 自动生成发布说明。"

# 一步完成：打标签 + 推送
tag-and-push:
	@if [ -z "$(VERSION)" ]; then echo "[错误] 需要指定 VERSION，例如: make tag-and-push VERSION=0.1.0"; exit 1; fi
	@$(MAKE) tag VERSION=$(VERSION) MSG='$(MSG)'
	@$(MAKE) release VERSION=$(VERSION)

# 基于变更自动生成 CHANGELOG，并建议用于 Release 说明
changelog:
	@if [ -z "$(VERSION)" ]; then echo "[错误] 需要指定 VERSION，例如: make changelog VERSION=0.1.0"; exit 1; fi
	@python3 scripts/generate_changelog.py --version $(VERSION)
	@echo "CHANGELOG.md 已生成/更新。"

# 一步完成：升级版本（patch|minor|major）、生成 changelog、打标并推送
# 用法：make release-complete BUMP=patch  或  make release-complete VERSION=0.2.0
release-complete:
	@if [ -z "$(VERSION)" ] && [ -z "$(BUMP)" ]; then echo "[错误] 需要指定 VERSION 或 BUMP=[patch|minor|major]"; exit 1; fi
	@if [ -n "$(BUMP)" ]; then python3 scripts/bump_version.py --type $(BUMP) --commit --tag; fi
	@if [ -n "$(VERSION)" ]; then python3 scripts/bump_version.py --set $(VERSION) --commit --tag; fi
	@python3 - <<'PY'
	import re,sys
	from pathlib import Path
	v = Path('VERSION').read_text().strip()
	if not re.match(r'^\d+\.\d+\.\d+$', v):
	    print('VERSION 文件格式不正确'); sys.exit(1)
	print(v)
	PY
	@V=$$(cat VERSION); python3 scripts/generate_changelog.py --version $$V
	@git add CHANGELOG.md && git commit -m "docs(changelog): update for v$$(cat VERSION)" || true
	@git push origin HEAD
	@$(MAKE) release VERSION=$$(cat VERSION)

# 简易帮助
help:
	@echo "常用命令："
	@echo "  make up                # 启动全部容器（默认 test 环境，可 COMPOSE_ENV=dev）"
	@echo "  make down              # 停止并清理容器与卷（当前环境）"
	@echo "  make ps                # 查看服务状态"
	@echo "  make backend-logs      # 查看后端日志"
	@echo "  make frontend-logs     # 查看前端日志"
	@echo "  make test-backend      # 后端 ruff + pytest"
	@echo "  make lint-frontend     # 前端 ESLint"
	@echo "  make rebuild           # 重新构建镜像"
	@echo "  make tag VERSION=0.1.0 MSG=...        # 创建发布标签"
	@echo "  make release VERSION=0.1.0            # 推送标签触发 Release"
	@echo "  make tag-and-push VERSION=0.1.0 MSG=...  # 一步完成"
