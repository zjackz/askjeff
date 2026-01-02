<template>
  <div class="sync-status-container">
    <!-- 顶部状态概览 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <!-- 左侧：系统健康状态 -->
      <div class="md:col-span-2 bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 flex items-center justify-between relative overflow-hidden">
        <div class="z-10">
          <div class="flex items-center gap-2 mb-2">
            <el-icon :size="20" :class="systemHealth.color"><component :is="systemHealth.icon" /></el-icon>
            <h3 class="text-lg font-bold text-gray-800 dark:text-gray-100">{{ systemHealth.title }}</h3>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ systemHealth.desc }}
          </p>
          <div class="mt-4 flex items-center gap-4 text-xs text-gray-400">
            <span class="flex items-center gap-1">
              <el-icon><Clock /></el-icon> 上次同步: {{ lastSyncTime ? formatTime(lastSyncTime) : '从未同步' }}
            </span>
            <span class="flex items-center gap-1">
              <el-icon><Timer /></el-icon> 下次自动同步: 预计明日 02:00
            </span>
          </div>
        </div>
        <!-- 装饰背景 -->
        <div class="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-gray-50 to-transparent dark:from-gray-700/30 pointer-events-none"></div>
        
        <!-- 操作按钮 -->
        <div class="z-10 flex flex-col gap-2">
          <el-button 
            type="primary" 
            size="large" 
            :loading="isSyncing"
            @click="handleSyncAll"
            class="!px-6 !rounded-lg shadow-md hover:shadow-lg transition-all"
          >
            {{ isSyncing ? '正在同步数据...' : '立即同步所有' }}
          </el-button>
          <div v-if="isSyncing" class="w-full mt-2">
             <el-progress :percentage="syncProgress" :status="syncProgress === 100 ? 'success' : ''" :stroke-width="4" :show-text="false" class="!m-0"/>
             <p class="text-xs text-center text-blue-500 mt-1 animate-pulse">正在获取最新数据...</p>
          </div>
        </div>
      </div>

      <!-- 右侧：关键指标 -->
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col justify-center">
        <div class="text-center">
          <div class="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-1">{{ todaySyncedCount }}</div>
          <div class="text-xs text-gray-500 uppercase tracking-wider">今日同步记录数</div>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 flex justify-around">
          <div class="text-center">
            <div class="text-lg font-semibold text-green-500">{{ successRate }}%</div>
            <div class="text-[10px] text-gray-400">成功率</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-semibold text-blue-500">{{ avgDuration }}s</div>
            <div class="text-[10px] text-gray-400">平均耗时</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细状态卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div v-for="type in syncTypes" :key="type.key" 
        class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700 transition-all hover:shadow-md"
        :class="{'border-l-4 border-l-blue-500': latestTasks[type.key]?.status === 'running', 'border-l-4 border-l-green-500': latestTasks[type.key]?.status === 'success', 'border-l-4 border-l-red-500': latestTasks[type.key]?.status === 'failed'}"
      >
        <div class="flex justify-between items-start mb-3">
          <div class="flex items-center gap-2">
            <div class="p-2 rounded-lg" :class="type.bgClass">
              <el-icon :class="type.textClass" :size="18"><component :is="type.icon" /></el-icon>
            </div>
            <div>
              <h4 class="font-semibold text-gray-800 dark:text-gray-200">{{ type.label }}</h4>
              <p class="text-xs text-gray-500">{{ type.desc }}</p>
            </div>
          </div>
          <el-tag :type="getStatusType(latestTasks[type.key]?.status)" size="small" effect="light" round>
            {{ getStatusLabel(latestTasks[type.key]?.status) }}
          </el-tag>
        </div>
        
        <div class="space-y-2">
          <div class="flex justify-between text-xs">
            <span class="text-gray-500">状态</span>
            <span class="font-medium" :class="getStatusColor(latestTasks[type.key]?.status)">
              <span v-if="latestTasks[type.key]?.status === 'running'" class="flex items-center gap-1">
                <el-icon class="is-loading"><Loading /></el-icon> 进行中
              </span>
              <span v-else>{{ latestTasks[type.key]?.error_message ? '异常' : '正常' }}</span>
            </span>
          </div>
          <div class="flex justify-between text-xs">
            <span class="text-gray-500">更新于</span>
            <span class="text-gray-700 dark:text-gray-300">
              {{ latestTasks[type.key] ? formatTimeSimple(latestTasks[type.key].created_at) : '-' }}
            </span>
          </div>
          <div class="flex justify-between text-xs">
            <span class="text-gray-500">记录数</span>
            <span class="font-mono text-gray-700 dark:text-gray-300">{{ latestTasks[type.key]?.records_synced || 0 }}</span>
          </div>
        </div>
        
        <!-- 失败原因提示 -->
        <div v-if="latestTasks[type.key]?.status === 'failed'" class="mt-3 p-2 bg-red-50 dark:bg-red-900/20 rounded text-xs text-red-600 dark:text-red-400 truncate" :title="latestTasks[type.key]?.error_message">
          <el-icon class="mr-1 top-0.5 relative"><Warning /></el-icon>
          {{ latestTasks[type.key]?.error_message }}
        </div>
      </div>
    </div>

    <!-- 历史记录 -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div class="p-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
        <h4 class="font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
          <el-icon><List /></el-icon> 同步日志
        </h4>
        <el-button link type="primary" @click="fetchTasks" :icon="Refresh">刷新</el-button>
      </div>
      
      <el-table :data="tasks" style="width: 100%" :header-cell-style="{ background: 'var(--el-fill-color-light)' }">
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="sync_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="getTypeTagEffect(row.sync_type)">{{ getTypeLabel(row.sync_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <div class="flex items-center gap-1">
              <el-icon :class="getStatusColor(row.status)"><component :is="getStatusIcon(row.status)" /></el-icon>
              <span>{{ getStatusLabel(row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="records_synced" label="同步记录" width="100" align="right" />
        <el-table-column label="耗时" width="100" align="right">
          <template #default="{ row }">
            {{ calculateDuration(row.start_time, row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="error_message" label="备注" show-overflow-tooltip />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { amazonSyncApi, type SyncTask } from '@/api/amazon-sync'
import { ElMessage } from 'element-plus'
import { 
  Check, Close, Loading, Timer, Refresh, Clock, Warning, List,
  Box, DataLine, Goods
} from '@element-plus/icons-vue'

const props = defineProps<{
  storeId?: string
}>()

const tasks = ref<SyncTask[]>([])
const isSyncing = ref(false)
const syncProgress = ref(0)

const syncTypes = [
  { key: 'inventory', label: '库存数据', desc: 'FBA 库存快照', icon: Box, bgClass: 'bg-orange-100 dark:bg-orange-900/30', textClass: 'text-orange-600' },
  { key: 'business', label: '业务报告', desc: '销售与流量', icon: DataLine, bgClass: 'bg-blue-100 dark:bg-blue-900/30', textClass: 'text-blue-600' },
  { key: 'advertising', label: '广告数据', desc: 'SP/SB/SD 广告', icon: Goods, bgClass: 'bg-purple-100 dark:bg-purple-900/30', textClass: 'text-purple-600' }
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

// 系统健康状态计算
const systemHealth = computed(() => {
  const allSuccess = syncTypes.every(type => latestTasks.value[type.key]?.status === 'success')
  const hasRunning = syncTypes.some(type => latestTasks.value[type.key]?.status === 'running')
  const hasFailed = syncTypes.some(type => latestTasks.value[type.key]?.status === 'failed')

  if (hasRunning) return { title: '正在同步', desc: '系统正在获取最新数据，请稍候...', icon: Loading, color: 'text-blue-500' }
  if (hasFailed) return { title: '同步异常', desc: '部分数据同步失败，请检查日志或重试。', icon: Warning, color: 'text-red-500' }
  if (allSuccess) return { title: '系统健康', desc: '所有数据均为最新状态。', icon: Check, color: 'text-green-500' }
  
  return { title: '准备就绪', desc: '系统等待同步指令。', icon: Clock, color: 'text-gray-500' }
})

// 统计指标
const todaySyncedCount = computed(() => {
  const today = new Date().toDateString()
  return tasks.value
    .filter(t => new Date(t.created_at).toDateString() === today && t.status === 'success')
    .reduce((acc, curr) => acc + curr.records_synced, 0)
})

const successRate = computed(() => {
  if (tasks.value.length === 0) return 0
  const successCount = tasks.value.filter(t => t.status === 'success').length
  return Math.round((successCount / tasks.value.length) * 100)
})

const avgDuration = computed(() => {
  const completedTasks = tasks.value.filter(t => t.end_time && t.start_time)
  if (completedTasks.length === 0) return 0
  const totalDuration = completedTasks.reduce((acc, t) => {
    return acc + (new Date(t.end_time!).getTime() - new Date(t.start_time).getTime())
  }, 0)
  return (totalDuration / completedTasks.length / 1000).toFixed(1)
})

// 格式化工具
const formatTime = (isoString: string) => new Date(isoString).toLocaleString()
const formatTimeSimple = (isoString: string) => {
  const date = new Date(isoString)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const calculateDuration = (start: string, end?: string) => {
  if (!end) return '-'
  const duration = new Date(end).getTime() - new Date(start).getTime()
  return `${(duration / 1000).toFixed(1)}s`
}

// 状态样式映射
const getStatusLabel = (status?: string) => {
  const map: Record<string, string> = { pending: '等待中', running: '进行中', success: '成功', failed: '失败' }
  return status ? map[status] || status : '未开始'
}

const getStatusType = (status?: string) => {
  const map: Record<string, string> = { pending: 'info', running: 'primary', success: 'success', failed: 'danger' }
  return status ? map[status] as any : 'info'
}

const getStatusColor = (status?: string) => {
  const map: Record<string, string> = { pending: 'text-gray-500', running: 'text-blue-500', success: 'text-green-500', failed: 'text-red-500' }
  return status ? map[status] : 'text-gray-400'
}

const getStatusIcon = (status?: string) => {
  const map: Record<string, any> = { pending: Clock, running: Loading, success: Check, failed: Close }
  return status ? map[status] : Clock
}

const getTypeLabel = (type: string) => {
  const found = syncTypes.find(t => t.key === type)
  return found ? found.label : type
}

const getTypeTagEffect = (type: string) => {
  const map: Record<string, string> = { inventory: 'warning', business: 'primary', advertising: 'success' }
  return map[type] as any || ''
}

// API 调用
const fetchTasks = async () => {
  try {
    const params: any = { limit: 20 }
    if (props.storeId) {
      params.store_id = props.storeId
    }
    const res = await amazonSyncApi.getSyncTasks(params)
    tasks.value = res.data
  } catch (error) {
    console.error('Failed to fetch sync tasks:', error)
  }
}

const handleSyncAll = async () => {
  if (isSyncing.value) return
  
  isSyncing.value = true
  syncProgress.value = 0
  
  try {
    await amazonSyncApi.syncAll(30, true)
    ElMessage.success('同步任务已开始')
    
    // 模拟进度条动画
    const progressInterval = setInterval(() => {
      if (syncProgress.value < 90) {
        syncProgress.value += Math.random() * 10
      }
    }, 500)
    
    // 轮询更新状态
    let checks = 0
    const interval = setInterval(async () => {
      await fetchTasks()
      checks++
      
      const allDone = syncTypes.every(type => {
        const task = latestTasks.value[type.key]
        return task && task.status !== 'running' && task.status !== 'pending'
      })
      
      if (allDone || checks > 20) {
        clearInterval(interval)
        clearInterval(progressInterval)
        isSyncing.value = false
        syncProgress.value = 100
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
/* 覆盖 Element Plus 默认样式以适应 Tailwind */
:deep(.el-card__body) {
  padding: 0;
}
</style>
