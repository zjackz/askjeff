# 统一开发命令（容器优先）
# 使用方法：在仓库根目录执行 make <目标>

COMPOSE := docker compose -f infra/docker/compose.yml

.PHONY: up down restart logs ps backend-logs frontend-logs db-logs rebuild shell-backend shell-frontend test-backend lint-frontend

up:
	$(COMPOSE) up -d --build

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
	$(COMPOSE) exec backend poetry run ruff check && poetry run pytest -q

# 前端 Lint（容器内执行）
lint-frontend:
	$(COMPOSE) exec frontend pnpm lint

