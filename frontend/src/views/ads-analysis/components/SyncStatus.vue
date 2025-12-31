<template>
  <div class="sync-status-container">
    <!-- 状态概览卡片 -->
    <div class="status-card bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-100 dark:border-gray-700 mb-4">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">数据同步状态</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
            上次同步: {{ lastSyncTime ? formatTime(lastSyncTime) : '从未同步' }}
          </p>
        </div>
        <div class="flex gap-2">
          <button
            @click="handleSyncAll"
            :disabled="isSyncing"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isSyncing" class="animate-spin">↻</span>
            {{ isSyncing ? '同步中...' : '立即同步所有' }}
          </button>
          <button
            @click="fetchTasks"
            class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            title="刷新状态"
          >
            ↻
          </button>
        </div>
      </div>

      <!-- 同步进度/状态指示器 -->
      <div class="mt-4 grid grid-cols-3 gap-4">
        <div v-for="type in syncTypes" :key="type.key" class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-md border border-gray-100 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ type.label }}</span>
            <span :class="getStatusClass(latestTasks[type.key]?.status)" class="text-xs px-2 py-0.5 rounded-full">
              {{ getStatusLabel(latestTasks[type.key]?.status) }}
            </span>
          </div>
          <div class="text-xs text-gray-500 dark:text-gray-400">
            <div v-if="latestTasks[type.key]">
              <span v-if="latestTasks[type.key].status === 'success'">
                已同步 {{ latestTasks[type.key].records_synced }} 条记录
              </span>
              <span v-else-if="latestTasks[type.key].status === 'failed'" class="text-red-500 truncate block" :title="latestTasks[type.key].error_message">
                失败: {{ latestTasks[type.key].error_message }}
              </span>
              <span v-else>等待中...</span>
            </div>
            <div v-else>无记录</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史记录折叠面板 -->
    <div class="history-section bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
      <div 
        @click="isHistoryExpanded = !isHistoryExpanded"
        class="p-4 flex justify-between items-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
      >
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-200">同步历史记录</h4>
        <span class="text-gray-400 text-sm">{{ isHistoryExpanded ? '收起' : '展开' }}</span>
      </div>
      
      <div v-if="isHistoryExpanded" class="p-4 border-t border-gray-100 dark:border-gray-700 overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="text-xs text-gray-500 uppercase bg-gray-50 dark:bg-gray-700/50 dark:text-gray-400">
            <tr>
              <th class="px-4 py-2">时间</th>
              <th class="px-4 py-2">类型</th>
              <th class="px-4 py-2">状态</th>
              <th class="px-4 py-2">记录数</th>
              <th class="px-4 py-2">耗时</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in tasks" :key="task.id" class="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <td class="px-4 py-2">{{ formatTime(task.created_at) }}</td>
              <td class="px-4 py-2">{{ getTypeLabel(task.sync_type) }}</td>
              <td class="px-4 py-2">
                <span :class="getStatusClass(task.status)" class="text-xs px-2 py-0.5 rounded-full">
                  {{ getStatusLabel(task.status) }}
                </span>
              </td>
              <td class="px-4 py-2">{{ task.records_synced }}</td>
              <td class="px-4 py-2">{{ calculateDuration(task.start_time, task.end_time) }}</td>
            </tr>
            <tr v-if="tasks.length === 0">
              <td colspan="5" class="px-4 py-4 text-center text-gray-500">暂无同步记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { amazonSyncApi, type SyncTask } from '@/api/amazon-sync'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  storeId?: string
}>()

const tasks = ref<SyncTask[]>([])
const isSyncing = ref(false)
const isHistoryExpanded = ref(false)

const syncTypes = [
  { key: 'inventory', label: '库存数据' },
  { key: 'business', label: '业务报告' },
  { key: 'advertising', label: '广告数据' }
]

// 计算各类别的最新任务状态
const latestTasks = computed(() => {
  const result: Record<string, SyncTask> = {}
  syncTypes.forEach(type => {
    const task = tasks.value.find(t => t.sync_type === type.key)
    if (task) {
      result[type.key] = task
    }
  })
  return result
})

const lastSyncTime = computed(() => {
  if (tasks.value.length > 0) {
    return tasks.value[0].created_at
  }
  return null
})

// 格式化时间
const formatTime = (isoString: string) => {
  return new Date(isoString).toLocaleString()
}

// 计算耗时
const calculateDuration = (start: string, end?: string) => {
  if (!end) return '-'
  const duration = new Date(end).getTime() - new Date(start).getTime()
  return `${(duration / 1000).toFixed(1)}s`
}

const getStatusLabel = (status?: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    running: '进行中',
    success: '成功',
    failed: '失败'
  }
  return status ? map[status] || status : '未开始'
}

const getStatusClass = (status?: string) => {
  const map: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-gray-200',
    running: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }
  return status ? map[status] || '' : 'bg-gray-100 text-gray-500'
}

const getTypeLabel = (type: string) => {
  const found = syncTypes.find(t => t.key === type)
  return found ? found.label : type
}

// 获取任务列表
const fetchTasks = async () => {
  try {
    const params: any = { limit: 20 }
    if (props.storeId) {
      params.store_id = props.storeId
    }
    const res = await amazonSyncApi.getSyncTasks(params)
    tasks.value = res
  } catch (error) {
    console.error('Failed to fetch sync tasks:', error)
  }
}

// 触发全量同步
const handleSyncAll = async () => {
  if (isSyncing.value) return
  
  isSyncing.value = true
  try {
    // 使用 Mock 数据进行演示
    await amazonSyncApi.syncAll(30, true)
    ElMessage.success('同步任务已开始')
    
    // 轮询更新状态
    let checks = 0
    const interval = setInterval(async () => {
      await fetchTasks()
      checks++
      
      // 检查是否所有最新任务都完成了
      const allDone = syncTypes.every(type => {
        const task = latestTasks.value[type.key]
        return task && task.status !== 'running' && task.status !== 'pending'
      })
      
      if (allDone || checks > 20) { // 最多轮询 20 次 (40秒)
        clearInterval(interval)
        isSyncing.value = false
        if (allDone) {
             ElMessage.success('同步完成')
        }
      }
    }, 2000)
    
  } catch (error) {
    console.error('Sync failed:', error)
    ElMessage.error('同步启动失败')
    isSyncing.value = false
  }
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.animate-spin {
  display: inline-block;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
