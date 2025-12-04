# 开发环境迁移指南

本指南帮助您将 ASKJeff 项目从一台电脑迁移到另一台电脑继续开发。

## 📋 迁移前准备

### 在旧电脑上

#### 1. 提交并推送所有代码

```bash
cd /path/to/askjeff

# 查看未提交的更改
git status

# 提交所有更改
git add .
git commit -m "feat: 迁移前保存工作进度"

# 推送到远程仓库
git push origin main
```

#### 2. 导出环境配置（可选）

如果您有自定义的环境变量配置:

```bash
# 备份 .env 文件（注意：不要提交到 Git）
cp backend/.env ~/askjeff-env-backup.txt

# 或者记录关键配置
echo "DEEPSEEK_API_KEY=$(grep DEEPSEEK_API_KEY backend/.env | cut -d '=' -f2)" > ~/askjeff-config.txt
```

#### 3. 导出数据库（如果需要）

```bash
# 导出数据库
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml exec db \
  pg_dump -U sorftime sorftime > ~/askjeff-db-backup.sql

# 或使用 make 命令（如果有配置）
make db-backup
```

## 🖥️ 在新电脑上设置

### 步骤 1: 安装必要软件

#### macOS

```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Docker Desktop
brew install --cask docker

# 安装 Git
brew install git

# 启动 Docker Desktop
open -a Docker
```

#### Ubuntu/Debian

```bash
# 更新包列表
sudo apt update

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt install docker-compose-plugin

# 安装 Git
sudo apt install git

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

#### Windows

1. 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. 下载并安装 [Git for Windows](https://git-scm.com/download/win)
3. 重启电脑

### 步骤 2: 克隆项目

```bash
# 克隆项目（替换为您的仓库地址）
git clone <your-repository-url> askjeff
cd askjeff

# 切换到您的工作分支（如果有）
git checkout main  # 或其他分支
```

### 步骤 3: 配置环境变量

```bash
# 创建后端环境配置文件
cd backend
cp .env.example .env

# 编辑 .env 文件，填入必要的配置
# 如果您从旧电脑备份了配置，可以直接复制
```

**必需配置项**:

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 数据库配置（使用 Docker 默认配置即可）
DATABASE_URL=postgresql+psycopg://sorftime:sorftime@db:5432/sorftime

# 其他可选配置
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 步骤 4: 启动开发环境

```bash
# 返回项目根目录
cd ..

# 启动所有服务（数据库、后端、前端）
make up

# 或使用 docker compose 命令
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml up -d

# 查看服务状态
docker ps
```

等待所有容器启动完成（约 30-60 秒）。

### 步骤 5: 恢复数据库（如果需要）

如果您从旧电脑导出了数据库:

```bash
# 将备份文件复制到项目目录
cp ~/askjeff-db-backup.sql .

# 恢复数据库
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml exec -T db \
  psql -U sorftime sorftime < askjeff-db-backup.sql

# 或使用 make 命令
make db-restore FILE=askjeff-db-backup.sql
```

如果不需要恢复数据，数据库会自动初始化并创建默认用户。

### 步骤 6: 验证环境

#### 检查服务状态

```bash
# 查看所有容器
docker ps

# 应该看到 3 个运行中的容器:
# - askjeff-dev-frontend-1
# - askjeff-dev-backend-1
# - askjeff-dev-db-1
```

#### 检查后端健康

```bash
# 检查后端健康状态
curl http://localhost:8001/health

# 应该返回: {"status":"healthy",...}
```

#### 访问前端

在浏览器中打开: <http://localhost:5174>

使用默认账号登录:
- 用户名: `admin`
- 密码: `admin666`

#### 查看日志

```bash
# 查看后端日志
make backend-logs

# 查看前端日志
make frontend-logs

# 查看所有日志
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml logs -f
```

## 🔧 常见问题排查

### Q1: 端口被占用

**错误信息**: `Bind for 0.0.0.0:5174 failed: port is already allocated`

**解决方案**:

```bash
# 检查端口占用
# macOS/Linux
lsof -i :5174
lsof -i :8001
lsof -i :5433

# Windows (PowerShell)
netstat -ano | findstr :5174

# 停止占用端口的进程，或修改 compose.dev.yml 中的端口映射
```

### Q2: Docker 容器启动失败

**解决方案**:

```bash
# 查看详细日志
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml logs

# 重新构建并启动
make down
make up

# 或强制重建
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml up -d --build --force-recreate
```

### Q3: 数据库连接失败

**解决方案**:

```bash
# 检查数据库容器状态
docker ps | grep db

# 进入数据库容器测试连接
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml exec db \
  psql -U sorftime -c "SELECT 1"

# 如果失败，重启数据库容器
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml restart db
```

### Q4: 前端无法连接后端

**解决方案**:

```bash
# 检查后端是否正常运行
curl http://localhost:8001/health

# 检查前端环境变量配置
cat frontend/.env

# 应该包含:
# VITE_API_BASE_URL=http://localhost:8001
```

### Q5: 权限问题（Linux）

**错误信息**: `permission denied while trying to connect to the Docker daemon socket`

**解决方案**:

```bash
# 将用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker

# 验证
docker ps
```

## 📝 开发工作流

### 日常开发

```bash
# 启动服务
make up

# 开发过程中...
# - 后端代码修改会自动热重载
# - 前端代码修改会自动刷新浏览器

# 查看日志
make backend-logs  # 后端日志
make frontend-logs # 前端日志

# 停止服务
make down
```

### 提交代码

```bash
# 查看更改
git status

# 提交更改
git add .
git commit -m "feat: 描述您的更改"

# 推送到远程
git push origin main
```

### 数据库迁移

```bash
# 如果有新的数据库迁移文件
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml exec backend \
  poetry run alembic upgrade head
```

## 🎯 快速参考

### 常用命令

| 命令 | 说明 |
|------|------|
| `make up` | 启动所有服务 |
| `make down` | 停止所有服务 |
| `make restart` | 重启所有服务 |
| `make ps` | 查看服务状态 |
| `make backend-logs` | 查看后端日志 |
| `make frontend-logs` | 查看前端日志 |
| `make test-backend` | 运行后端测试 |

### 服务地址

| 服务 | 地址 |
|------|------|
| 前端界面 | <http://localhost:5174> |
| 后端 API | <http://localhost:8001> |
| API 文档 | <http://localhost:8001/docs> |
| 健康检查 | <http://localhost:8001/health> |
| 数据库 | localhost:5433 |

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin666 |
| 运营人员 | shangu | shangu666 |

## 📚 更多资源

- [快速开始指南](./quickstart.md) - 基础使用教程
- [开发指南](./development.md) - 详细开发文档
- [部署指南](./deployment.md) - 生产环境部署
- [需求文档](../specs/README.md) - 功能需求详情

## 💡 提示

1. **定期提交代码**: 养成频繁提交的习惯，避免丢失工作进度
2. **使用 .gitignore**: 确保敏感信息（如 `.env` 文件）不会被提交
3. **备份数据库**: 如果有重要的测试数据，定期备份数据库
4. **保持同步**: 在新电脑上定期 `git pull` 获取最新代码
5. **环境一致性**: 使用 Docker 确保开发环境在不同电脑上保持一致

## ⚠️ 注意事项

- **不要提交 `.env` 文件**: 该文件包含敏感信息，已在 `.gitignore` 中
- **不要提交 `node_modules/`**: 依赖包会自动安装
- **不要提交数据库文件**: 使用导出/导入方式迁移数据
- **检查 Docker 版本**: 确保 Docker 和 Docker Compose 版本兼容
