#!/bin/bash
# 完整系统测试脚本 - 使用两个样本文件
# 测试文件: 吸尘器-sample.xlsx 和 奶瓶消毒剂-sample.xlsx

set -e

API_BASE="http://localhost:8001"
SAMPLE_DIR="/home/dministrator/code/askjeff/samples"
FILE1="${SAMPLE_DIR}/吸尘器-sample.xlsx"
FILE2="${SAMPLE_DIR}/20251112_25131713011_产品列表-奶瓶消毒剂.xlsx"

echo "========================================="
echo "完整系统测试 - 双样本文件"
echo "========================================="
echo ""
echo "测试文件:"
echo "1. 吸尘器-sample.xlsx"
echo "2. 20251112_25131713011_产品列表-奶瓶消毒剂.xlsx"
echo ""

# 检查文件是否存在
if [ ! -f "$FILE1" ]; then
    echo "❌ 错误: 找不到文件 $FILE1"
    exit 1
fi

if [ ! -f "$FILE2" ]; then
    echo "❌ 错误: 找不到文件 $FILE2"
    exit 1
fi

echo "✅ 测试文件检查通过"
echo ""

# ==================== 测试 1: 吸尘器样本 ====================
echo "========================================="
echo "测试 1: 吸尘器产品特征提取"
echo "========================================="
echo ""

echo "步骤 1.1: 上传吸尘器样本文件..."
UPLOAD1=$(curl -s -X POST \
  "${API_BASE}/api/extraction/upload" \
  -F "file=@${FILE1}")

TASK1_ID=$(echo "$UPLOAD1" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ 任务 1 ID: $TASK1_ID"
echo ""

echo "步骤 1.2: 配置提取字段..."
FIELDS1='["产品类型", "吸力", "电池类型", "工作时间", "噪音等级", "重量"]'
START1=$(curl -s -X POST \
  "${API_BASE}/api/extraction/${TASK1_ID}/start" \
  -H "Content-Type: application/json" \
  -d "{\"target_fields\": $FIELDS1}")

echo "✅ 提取任务已启动"
echo "目标字段: 产品类型, 吸力, 电池类型, 工作时间, 噪音等级, 重量"
echo ""

# ==================== 测试 2: 奶瓶消毒剂样本 ====================
echo "========================================="
echo "测试 2: 奶瓶消毒剂产品特征提取"
echo "========================================="
echo ""

echo "步骤 2.1: 上传奶瓶消毒剂样本文件..."
UPLOAD2=$(curl -s -X POST \
  "${API_BASE}/api/extraction/upload" \
  -F "file=@${FILE2}")

TASK2_ID=$(echo "$UPLOAD2" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ 任务 2 ID: $TASK2_ID"
echo ""

echo "步骤 2.2: 配置提取字段..."
FIELDS2='["产品类型", "容量", "材质", "适用年龄", "消毒方式", "品牌"]'
START2=$(curl -s -X POST \
  "${API_BASE}/api/extraction/${TASK2_ID}/start" \
  -H "Content-Type: application/json" \
  -d "{\"target_fields\": $FIELDS2}")

echo "✅ 提取任务已启动"
echo "目标字段: 产品类型, 容量, 材质, 适用年龄, 消毒方式, 品牌"
echo ""

# ==================== 监控任务进度 ====================
echo "========================================="
echo "监控任务执行进度"
echo "========================================="
echo ""

monitor_task() {
    local TASK_ID=$1
    local TASK_NAME=$2
    
    echo "监控任务: $TASK_NAME (ID: $TASK_ID)"
    
    for i in {1..60}; do
        sleep 3
        STATUS_RESPONSE=$(curl -s "${API_BASE}/api/extraction/${TASK_ID}")
        STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "UNKNOWN")
        
        echo "  [$i/60] 状态: $STATUS"
        
        if [ "$STATUS" = "COMPLETED" ] || [ "$STATUS" = "SUCCESS" ]; then
            echo "  ✅ 任务完成!"
            return 0
        elif [ "$STATUS" = "FAILED" ]; then
            echo "  ❌ 任务失败!"
            return 1
        fi
    done
    
    echo "  ⚠️ 任务超时"
    return 2
}

echo "开始监控两个任务..."
echo ""

# 并行监控(简化版,实际是串行)
monitor_task "$TASK1_ID" "吸尘器"
RESULT1=$?
echo ""

monitor_task "$TASK2_ID" "奶瓶消毒剂"
RESULT2=$?
echo ""

# ==================== 验证结果 ====================
echo "========================================="
echo "验证提取结果"
echo "========================================="
echo ""

verify_results() {
    local TASK_ID=$1
    local TASK_NAME=$2
    
    echo "验证任务: $TASK_NAME"
    echo "----------------------------------------"
    
    RESULT=$(curl -s "${API_BASE}/api/extraction/${TASK_ID}")
    
    # 提取统计信息
    FILENAME=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('filename', 'N/A'))")
    STATUS=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'N/A'))")
    FIELDS=$(echo "$RESULT" | python3 -c "import sys, json; print(', '.join(json.load(sys.stdin).get('target_fields', [])))")
    
    echo "  文件名: $FILENAME"
    echo "  状态: $STATUS"
    echo "  提取字段: $FIELDS"
    echo ""
}

verify_results "$TASK1_ID" "吸尘器"
verify_results "$TASK2_ID" "奶瓶消毒剂"

# ==================== 导出结果 ====================
echo "========================================="
echo "导出提取结果"
echo "========================================="
echo ""

export_task() {
    local TASK_ID=$1
    local TASK_NAME=$2
    
    OUTPUT_FILE="/tmp/extraction_${TASK_NAME}_${TASK_ID}.xlsx"
    
    echo "导出任务: $TASK_NAME"
    curl -s "${API_BASE}/api/extraction/${TASK_ID}/export" -o "$OUTPUT_FILE"
    
    if [ -f "$OUTPUT_FILE" ]; then
        FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
        echo "  ✅ 导出成功: $OUTPUT_FILE (大小: $FILE_SIZE)"
    else
        echo "  ❌ 导出失败"
    fi
    echo ""
}

export_task "$TASK1_ID" "吸尘器"
export_task "$TASK2_ID" "奶瓶消毒剂"

# ==================== 系统状态检查 ====================
echo "========================================="
echo "系统状态检查"
echo "========================================="
echo ""

echo "检查任务列表..."
TASK_LIST=$(curl -s "${API_BASE}/api/extraction/list?limit=10")
TASK_COUNT=$(echo "$TASK_LIST" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "  ✅ 任务列表: $TASK_COUNT 个任务"
echo ""

echo "检查 Dashboard 数据..."
EXTRACTIONS=$(curl -s "${API_BASE}/api/extraction/list?limit=1" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "  ✅ 提取任务统计: $EXTRACTIONS 个"
echo ""

# ==================== 数据库验证 ====================
echo "========================================="
echo "数据库数据验证"
echo "========================================="
echo ""

echo "查询任务 1 数据..."
docker exec askjeff-dev-db-1 psql -U sorftime -d sorftime_dev -c \
  "SELECT id, filename, status, array_length(target_fields, 1) as field_count 
   FROM extraction_tasks 
   WHERE id = '$TASK1_ID';" 2>/dev/null || echo "  ⚠️ 无法连接数据库"
echo ""

echo "查询任务 2 数据..."
docker exec askjeff-dev-db-1 psql -U sorftime -d sorftime_dev -c \
  "SELECT id, filename, status, array_length(target_fields, 1) as field_count 
   FROM extraction_tasks 
   WHERE id = '$TASK2_ID';" 2>/dev/null || echo "  ⚠️ 无法连接数据库"
echo ""

# ==================== 测试总结 ====================
echo "========================================="
echo "测试总结"
echo "========================================="
echo ""

echo "任务执行结果:"
echo "  任务 1 (吸尘器): $([ $RESULT1 -eq 0 ] && echo '✅ 成功' || echo '❌ 失败')"
echo "  任务 2 (奶瓶消毒剂): $([ $RESULT2 -eq 0 ] && echo '✅ 成功' || echo '❌ 失败')"
echo ""

echo "任务 ID:"
echo "  吸尘器: $TASK1_ID"
echo "  奶瓶消毒剂: $TASK2_ID"
echo ""

echo "导出文件:"
echo "  /tmp/extraction_吸尘器_${TASK1_ID}.xlsx"
echo "  /tmp/extraction_奶瓶消毒剂_${TASK2_ID}.xlsx"
echo ""

echo "数据已保留在数据库中,可通过以下方式查看:"
echo "  - 访问 http://localhost:5174/extraction"
echo "  - 查看任务列表和历史记录"
echo ""

echo "========================================="
echo "测试完成!"
echo "========================================="
