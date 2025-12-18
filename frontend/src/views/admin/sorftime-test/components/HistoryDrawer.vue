<template>
  <el-drawer
    :model-value="visible"
    title="请求历史"
    direction="rtl"
    size="500px"
    @update:model-value="$emit('update:visible', $event)"
  >
    <div class="history-drawer">
      <div class="history-header">
        <el-button 
          size="small" 
          type="danger" 
          :icon="Delete" 
          @click="$emit('clear-all')"
          v-if="history.length"
        >
          清空历史
        </el-button>
      </div>
      
      <el-empty v-if="!history.length" description="暂无历史记录" />
      
      <el-timeline v-else>
        <el-timeline-item
          v-for="item in history"
          :key="item.id"
          :timestamp="formatTime(item.timestamp)"
          placement="top"
        >
          <el-card shadow="hover">
            <div class="history-item">
              <div class="history-item-header">
                <el-tag :type="item.success ? 'success' : 'danger'" size="small">
                  {{ item.success ? '成功' : '失败' }}
                </el-tag>
                <el-tag type="info" size="small">{{ item.endpoint }}</el-tag>
                <span class="history-time">{{ item.responseTime }}ms</span>
              </div>
              <div class="history-item-params">
                <div v-if="item.params.asins" class="param-line">
                  <strong>ASIN:</strong> {{ item.params.asins }}
                </div>
                <div v-if="item.params.keyword" class="param-line">
                  <strong>Keyword:</strong> {{ item.params.keyword }}
                </div>
                <div v-if="item.params.nodeId" class="param-line">
                  <strong>NodeId:</strong> {{ item.params.nodeId }}
                </div>
              </div>
              <div class="history-item-actions">
                <el-button size="small" type="primary" @click="$emit('load-item', item)">
                  加载配置
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  :icon="Delete" 
                  @click="$emit('delete-item', item.id)" 
                />
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { Delete } from '@element-plus/icons-vue'

/**
 * 历史记录抽屉
 * 
 * 显示请求历史记录,支持加载和删除
 */

interface HistoryItem {
  id: string
  endpoint: string
  params: Record<string, any>
  success: boolean
  responseTime: number
  timestamp: number
}

interface Props {
  visible: boolean
  history: HistoryItem[]
}

defineProps<Props>()

defineEmits<{
  'update:visible': [value: boolean]
  'load-item': [item: HistoryItem]
  'delete-item': [id: string]
  'clear-all': []
}>()

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped lang="scss">
.history-drawer {
  padding: 0 20px;
}

.history-header {
  margin-bottom: 20px;
  text-align: right;
}

.history-item {
  &-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }
  
  &-params {
    margin-bottom: 12px;
    font-size: 14px;
    color: #606266;
    
    .param-line {
      margin-bottom: 4px;
      
      strong {
        color: #303133;
      }
    }
  }
  
  &-actions {
    display: flex;
    gap: 8px;
  }
}

.history-time {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
}
</style>
