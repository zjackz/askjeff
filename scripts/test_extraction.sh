#!/bin/bash
# LLM 特征提取系统完整测试脚本
# 使用 samples/吸尘器-sample.xlsx 进行端到端测试

set -e

API_BASE="http://localhost:8001"
TEST_FILE="/home/dministrator/code/askjeff/samples/吸尘器-sample.xlsx"

echo "========================================="
echo "LLM 特征提取系统测试"
echo "========================================="
echo ""

# 步骤 1: 上传文件
echo "步骤 1: 上传测试文件..."
UPLOAD_RESPONSE=$(curl -s -X POST \
  "${API_BASE}/api/extraction/upload" \
  -F "file=@${TEST_FILE}")

echo "上传响应:"
echo "$UPLOAD_RESPONSE" | python3 -m json.tool

TASK_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo ""
echo "任务 ID: $TASK_ID"
echo ""

# 步骤 2: 查看任务详情和识别的字段
echo "步骤 2: 查看任务详情..."
TASK_RESPONSE=$(curl -s "${API_BASE}/api/extraction/${TASK_ID}")
echo "$TASK_RESPONSE" | python3 -m json.tool
echo ""

# 提取字段列表
COLUMNS=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; print(', '.join(json.load(sys.stdin).get('columns', [])))")
echo "识别的字段: $COLUMNS"
echo ""

# 步骤 3: 启动特征提取
echo "步骤 3: 启动特征提取任务..."
echo "目标提取字段: 产品类型, 吸力, 电池类型, 工作时间, 噪音等级"

START_RESPONSE=$(curl -s -X POST \
  "${API_BASE}/api/extraction/${TASK_ID}/start" \
  -H "Content-Type: application/json" \
  -d '{
    "target_fields": ["产品类型", "吸力", "电池类型", "工作时间", "噪音等级"]
  }')

echo "$START_RESPONSE" | python3 -m json.tool
echo ""

# 步骤 4: 监控任务状态
echo "步骤 4: 监控任务执行状态..."
for i in {1..30}; do
  sleep 2
  STATUS_RESPONSE=$(curl -s "${API_BASE}/api/extraction/${TASK_ID}")
  STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
  
  TOTAL=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('items', [])))")
  SUCCESS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; items = json.load(sys.stdin).get('items', []); print(sum(1 for item in items if item.get('status') == 'SUCCESS'))")
  FAILED=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; items = json.load(sys.stdin).get('items', []); print(sum(1 for item in items if item.get('status') == 'FAILED'))")
  PROCESSING=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; items = json.load(sys.stdin).get('items', []); print(sum(1 for item in items if item.get('status') == 'PROCESSING'))")
  
  echo "[$i/30] 任务状态: $STATUS | 总数: $TOTAL | 成功: $SUCCESS | 失败: $FAILED | 处理中: $PROCESSING"
  
  if [ "$STATUS" = "SUCCESS" ] || [ "$STATUS" = "FAILED" ]; then
    echo ""
    echo "任务完成! 最终状态: $STATUS"
    break
  fi
done
echo ""

# 步骤 5: 查看提取结果
echo "步骤 5: 查看提取结果..."
FINAL_RESPONSE=$(curl -s "${API_BASE}/api/extraction/${TASK_ID}")
echo "$FINAL_RESPONSE" | python3 -m json.tool | head -100
echo ""

# 显示前3条提取结果示例
echo "提取结果示例 (前3条):"
echo "$FINAL_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
items = data.get('items', [])[:3]
for idx, item in enumerate(items, 1):
    print(f'\n--- 产品 {idx} ---')
    print(f'状态: {item.get(\"status\")}')
    if item.get('extracted_data'):
        print('提取的特征:')
        for k, v in item.get('extracted_data', {}).items():
            print(f'  {k}: {v}')
"
echo ""

# 步骤 6: 导出结果
echo "步骤 6: 导出结果到文件..."
OUTPUT_FILE="/tmp/extraction_result_${TASK_ID}.xlsx"
curl -s "${API_BASE}/api/extraction/${TASK_ID}/export" -o "$OUTPUT_FILE"

if [ -f "$OUTPUT_FILE" ]; then
  FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
  echo "导出成功! 文件: $OUTPUT_FILE (大小: $FILE_SIZE)"
else
  echo "导出失败!"
fi
echo ""

echo "========================================="
echo "测试完成!"
echo "========================================="
echo ""
echo "任务 ID: $TASK_ID"
echo "导出文件: $OUTPUT_FILE"
echo ""
echo "数据已保留在数据库中,可通过以下命令查看:"
echo "  docker exec askjeff-dev-backend-1 psql -U sorftime -d sorftime_dev -c 'SELECT * FROM extraction_tasks;'"
