#!/bin/bash
# 快速查看最近的 API 调用日志
# 使用方法: ./quick_check_api_logs.sh [minutes]

MINUTES=${1:-60}

echo "========================================"
echo "📊 最近 ${MINUTES} 分钟的 API 调用日志"
echo "========================================"
echo ""

docker exec askjeff-dev-db-1 psql -U postgres -d askjeff -c "
SELECT 
    to_char(timestamp, 'HH24:MI:SS') as time,
    level,
    message,
    context->>'platform' as platform,
    context->>'status_code' as status,
    context->>'duration_ms' as duration_ms,
    context->'response'->>'code' as api_code,
    context->'response'->>'requestLeft' as quota_left
FROM system_logs
WHERE category = 'external_api'
  AND timestamp >= NOW() - INTERVAL '${MINUTES} minutes'
ORDER BY timestamp DESC
LIMIT 20;
"

echo ""
echo "========================================"
echo "📈 统计信息"
echo "========================================"

docker exec askjeff-dev-db-1 psql -U postgres -d askjeff -c "
SELECT 
    level,
    COUNT(*) as count,
    ROUND(AVG((context->>'duration_ms')::numeric), 0) as avg_duration_ms
FROM system_logs
WHERE category = 'external_api'
  AND timestamp >= NOW() - INTERVAL '${MINUTES} minutes'
GROUP BY level;
"
