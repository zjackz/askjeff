#!/bin/bash
# 启动 Jeff Data Core 服务

echo "🚀 启动 Jeff Data Core (JDC) 服务..."
echo ""

# 检查 Docker 环境
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查环境变量
echo "📋 检查环境变量..."
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  警告: DATABASE_URL 未设置，使用默认值"
    DATABASE_URL="postgresql://jdc_user:jdc_pass@jdc-postgres:5432/jdc_db"
fi

if [ -z "$REDIS_URL" ]; then
    echo "⚠️  警告: REDIS_URL 未设置，使用默认值"
    REDIS_URL="redis://localhost:6379/0"
fi

# 停止旧容器
echo "🛑 停止旧容器..."
docker-compose -f docker-compose.jdc.yml down -v

# 启动服务
echo "🚀 启动 JDC 服务..."
docker-compose -f docker-compose.jdc.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 健康检查
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "🏥 健康检查 ($attempt/$max_attempts)..."

    # 检查 API
    if curl -sf http://localhost:8000/health; then
        echo "✅ JDC API 服务启动成功！"
        break
    fi

    if [ $attempt -eq $max_attempts ]; then
        echo "❌ 服务启动超时！"
        exit 1
    fi

    sleep 2
done

# 显示服务信息
echo ""
echo "📊 服务信息："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 JDC API:      http://localhost:8000"
echo "📊 Grafana:      http://localhost:3000"
echo "📈 PostgreSQL:    localhost:5432"
echo "🔄 Redis:       localhost:6379"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 文档："
echo "   API 文档: http://localhost:8000/docs"
echo "   Grafana:   http://localhost:3000"
echo ""
echo "🔧 常用命令："
echo "   查看日志: docker-compose -f docker-compose.jdc.yml logs -f jdc-api"
echo "   重启服务: docker-compose -f docker-compose.jdc.yml restart"
echo "   停止服务: docker-compose -f docker-compose.jdc.yml down"
echo ""
echo "✨ Jeff Data Core 已启动！"
