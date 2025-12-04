# 部署指南

本指南介绍如何将 ASKJeff 系统部署到生产环境。

## 部署架构

```text
┌─────────────┐
│   Nginx     │ ← 反向代理 + SSL
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼────┐
│前端  │  │后端   │
│5174 │  │8001  │
└─────┘  └──┬───┘
            │
         ┌──▼──────┐
         │PostgreSQL│
         │  5432   │
         └─────────┘
```

## 方式一：Docker Compose 部署（推荐）

### 1. 准备服务器

**最低配置**:
- CPU: 2 核
- 内存: 4GB
- 磁盘: 20GB
- 系统: Ubuntu 20.04+ / CentOS 7+

**安装 Docker**:

```bash
# Ubuntu
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 克隆项目

```bash
cd /opt
sudo git clone <repository-url> askjeff
cd askjeff
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
POSTGRES_USER=sorftime
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=sorftime

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# JWT 密钥（生成随机字符串）
SECRET_KEY=$(openssl rand -hex 32)

# 环境
ENVIRONMENT=production

# 文件上传限制（MB）
MAX_FILE_SIZE_MB=100

# 日志级别
LOG_LEVEL=INFO
```

### 4. 使用生产配置启动

创建 `infra/docker/compose.prod.yml`：

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../../backend
      dockerfile: ../infra/docker/Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      DEEPSEEK_BASE_URL: ${DEEPSEEK_BASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: ${ENVIRONMENT}
      LOG_LEVEL: ${LOG_LEVEL}
    volumes:
      - ./storage:/app/storage
    depends_on:
      db:
        condition: service_healthy
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ../../frontend
      dockerfile: ../infra/docker/Dockerfile.frontend.prod
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: always

volumes:
  postgres-data:
```

启动服务：

```bash
docker-compose -f infra/docker/compose.prod.yml up -d
```

### 5. 配置 Nginx

创建 `infra/docker/nginx.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8001;
    }

    upstream frontend {
        server frontend:5174;
    }

    # HTTP 重定向到 HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # 前端
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 后端 API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 文件上传大小限制
            client_max_body_size 100M;
        }

        # API 文档
        location /docs {
            proxy_pass http://backend;
        }

        # 健康检查
        location /health {
            proxy_pass http://backend;
        }
    }
}
```

### 6. 配置 SSL 证书

使用 Let's Encrypt：

```bash
# 安装 certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem infra/docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem infra/docker/ssl/key.pem
```

### 7. 配置 systemd 服务

创建 `/etc/systemd/system/askjeff.service`：

```ini
[Unit]
Description=ASKJeff Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/askjeff
ExecStart=/usr/local/bin/docker-compose -f infra/docker/compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f infra/docker/compose.prod.yml down
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable askjeff
sudo systemctl start askjeff
```

## 方式二：手动部署

### 后端部署

```bash
cd backend

# 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install --no-dev

# 运行数据库迁移
poetry run alembic upgrade head

# 启动服务（使用 gunicorn）
poetry run gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --access-logfile - \
  --error-logfile -
```

### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 使用 nginx 或其他 Web 服务器托管 dist 目录
```

## 数据库管理

### 备份数据库

```bash
# 自动备份脚本
docker-compose -f infra/docker/compose.prod.yml exec db \
  pg_dump -U sorftime sorftime > backup_$(date +%Y%m%d_%H%M%S).sql

# 设置定时备份（crontab）
0 2 * * * cd /opt/askjeff && ./scripts/backup_db.sh
```

### 恢复数据库

```bash
# 停止服务
docker-compose -f infra/docker/compose.prod.yml stop backend

# 恢复数据
docker-compose -f infra/docker/compose.prod.yml exec -T db \
  psql -U sorftime sorftime < backup.sql

# 重启服务
docker-compose -f infra/docker/compose.prod.yml start backend
```

## 监控和日志

### 查看日志

```bash
# 所有服务日志
docker-compose -f infra/docker/compose.prod.yml logs -f

# 特定服务日志
docker-compose -f infra/docker/compose.prod.yml logs -f backend
docker-compose -f infra/docker/compose.prod.yml logs -f frontend
docker-compose -f infra/docker/compose.prod.yml logs -f db
```

### 配置日志轮转

创建 `/etc/logrotate.d/askjeff`：

```
/opt/askjeff/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker-compose -f /opt/askjeff/infra/docker/compose.prod.yml restart backend
    endscript
}
```

### 健康检查

```bash
# 检查服务状态
curl https://your-domain.com/health

# 预期响应
{
  "status": "healthy",
  "checks": {
    "database": "healthy",
    "storage": "healthy",
    "deepseek_config": "configured"
  }
}
```

## 性能优化

### 1. 数据库优化

编辑 PostgreSQL 配置：

```bash
# 进入数据库容器
docker-compose -f infra/docker/compose.prod.yml exec db bash

# 编辑配置
vi /var/lib/postgresql/data/postgresql.conf
```

推荐配置（4GB 内存服务器）：

```ini
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### 2. 后端优化

增加 worker 数量：

```bash
# 修改 gunicorn 配置
--workers $(( 2 * $(nproc) + 1 ))
```

### 3. 前端优化

- 启用 Gzip 压缩
- 配置 CDN
- 启用浏览器缓存

## 安全加固

### 1. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. 限制 API 访问

在 Nginx 配置中添加速率限制：

```nginx
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        location /api {
            limit_req zone=api burst=20 nodelay;
            # ...
        }
    }
}
```

### 3. 定期更新

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 更新 Docker 镜像
cd /opt/askjeff
docker-compose -f infra/docker/compose.prod.yml pull
docker-compose -f infra/docker/compose.prod.yml up -d
```

## 故障排除

### 服务无法启动

```bash
# 检查容器状态
docker-compose -f infra/docker/compose.prod.yml ps

# 查看错误日志
docker-compose -f infra/docker/compose.prod.yml logs backend

# 检查端口占用
sudo netstat -tlnp | grep :8001
```

### 数据库连接失败

```bash
# 检查数据库容器
docker-compose -f infra/docker/compose.prod.yml exec db psql -U sorftime -c "SELECT 1"

# 检查环境变量
docker-compose -f infra/docker/compose.prod.yml exec backend env | grep DATABASE
```

### 磁盘空间不足

```bash
# 清理 Docker 资源
docker system prune -a

# 清理旧日志
find /opt/askjeff/logs -name "*.log" -mtime +30 -delete
```

## 升级指南

```bash
cd /opt/askjeff

# 1. 备份数据库
./scripts/backup_db.sh

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建镜像
docker-compose -f infra/docker/compose.prod.yml build

# 4. 运行数据库迁移
docker-compose -f infra/docker/compose.prod.yml exec backend \
  poetry run alembic upgrade head

# 5. 重启服务
docker-compose -f infra/docker/compose.prod.yml up -d
```

## 监控方案（可选）

### 使用 Prometheus + Grafana

参考 `infra/monitoring/docker-compose.yml` 配置监控栈。

### 使用云服务监控

- AWS CloudWatch
- Azure Monitor
- Google Cloud Monitoring

## 更多资源

- [快速开始指南](./quickstart.md)
- [API 文档](./api-examples.md)
- [故障排除](./troubleshooting.md)
