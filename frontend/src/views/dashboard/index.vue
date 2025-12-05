<template>
  <div class="dashboard fade-in">
    <!-- 欢迎区域 -->
    <div class="welcome-section mb-6">
      <h1 class="text-2xl font-bold mb-2">欢迎回来, 管理员 👋</h1>
      <p class="text-gray-500">这里是您的数据概览中心</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="mb-6">
      <el-col :span="8">
        <div class="stat-card primary-card slide-in" style="--delay: 0.1s">
          <div class="stat-icon">
            <el-icon><Upload /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">导入批次</div>
            <div class="stat-number">
              <count-to :start-val="0" :end-val="stats.batches" :duration="2000" />
            </div>
          </div>
          <div class="stat-bg-icon">
            <el-icon><Upload /></el-icon>
          </div>
        </div>
      </el-col>
      
      <el-col :span="8">
        <div class="stat-card success-card slide-in" style="--delay: 0.2s">
          <div class="stat-icon">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">产品数据</div>
            <div class="stat-number">
              <count-to :start-val="0" :end-val="stats.products" :duration="2000" />
            </div>
          </div>
          <div class="stat-bg-icon">
            <el-icon><Box /></el-icon>
          </div>
        </div>
      </el-col>
      
      <el-col :span="8">
        <div class="stat-card warning-card slide-in" style="--delay: 0.3s">
          <div class="stat-icon">
            <el-icon><MagicStick /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">特征提取</div>
            <div class="stat-number">
              <count-to :start-val="0" :end-val="stats.extractions" :duration="2000" />
            </div>
          </div>
          <div class="stat-bg-icon">
            <el-icon><MagicStick /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快速入口 -->
    <div class="section-title mb-4 slide-in" style="--delay: 0.4s">
      <h3>快速入口</h3>
    </div>
    
    <el-row :gutter="20" class="mb-6 slide-in" style="--delay: 0.5s">
      <el-col :span="8">
        <div class="quick-action-card" @click="$router.push('/import')">
          <div class="action-icon bg-blue-100 text-blue-600">
            <el-icon><Upload /></el-icon>
          </div>
          <div class="action-info">
            <h4>导入数据</h4>
            <p>上传产品数据文件</p>
          </div>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </el-col>
      
      <el-col :span="8">
        <div class="quick-action-card" @click="$router.push('/product')">
          <div class="action-icon bg-green-100 text-green-600">
            <el-icon><Search /></el-icon>
          </div>
          <div class="action-info">
            <h4>查询产品</h4>
            <p>AI 产品数据查询</p>
          </div>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </el-col>
      
      <el-col :span="8">
        <div class="quick-action-card" @click="$router.push('/export')">
          <div class="action-icon bg-purple-100 text-purple-600">
            <el-icon><Download /></el-icon>
          </div>
          <div class="action-info">
            <h4>导出数据</h4>
            <p>批量导出结果</p>
          </div>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </el-col>
    </el-row>
    
    <!-- 系统状态 -->
    <el-card class="system-status slide-in" style="--delay: 0.6s">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-bold">系统状态</span>
          <el-tag :type="systemHealthType" effect="dark" round>
            {{ systemHealthText }}
          </el-tag>
        </div>
      </template>
      
      <el-row :gutter="20" v-loading="loadingSystemStats">
        <!-- CPU使用率 -->
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon cpu-icon">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">CPU使用率</div>
              <div class="metric-value">{{ systemStats.cpu.percent }}%</div>
              <el-progress 
                :percentage="systemStats.cpu.percent" 
                :color="getProgressColor(systemStats.cpu.percent)"
                :show-text="false"
              />
              <div class="metric-detail">{{ systemStats.cpu.count }} 核心</div>
            </div>
          </div>
        </el-col>
        
        <!-- 内存使用率 -->
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon memory-icon">
              <el-icon><Memo /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">内存使用率</div>
              <div class="metric-value">{{ systemStats.memory.percent }}%</div>
              <el-progress 
                :percentage="systemStats.memory.percent"
                :color="getProgressColor(systemStats.memory.percent)"
                :show-text="false"
              />
              <div class="metric-detail">
                {{ formatBytes(systemStats.memory.used) }} / 
                {{ formatBytes(systemStats.memory.total) }}
              </div>
            </div>
          </div>
        </el-col>
        
        <!-- 磁盘使用率 -->
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon disk-icon">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">磁盘使用率</div>
              <div class="metric-value">{{ systemStats.disk.percent }}%</div>
              <el-progress 
                :percentage="systemStats.disk.percent"
                :color="getProgressColor(systemStats.disk.percent)"
                :show-text="false"
              />
              <div class="metric-detail">
                {{ formatBytes(systemStats.disk.used) }} / 
                {{ formatBytes(systemStats.disk.total) }}
              </div>
            </div>
          </div>
        </el-col>
        
        <!-- 系统运行时间 -->
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon uptime-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">运行时间</div>
              <div class="metric-value uptime-value">{{ formatUptime(systemStats.uptime.seconds) }}</div>
              <div class="metric-detail">
                启动于 {{ formatBootTime(systemStats.uptime.boot_time) }}
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { Upload, Box, MagicStick, Search, Download, ArrowRight, Cpu, Memo, FolderOpened, Clock } from '@element-plus/icons-vue'
import { http } from '@/utils/http'
// 简单的数字滚动组件逻辑，实际项目中可以使用 vue-count-to
import { TransitionPresets, useTransition } from '@vueuse/core'

const stats = ref({
  batches: 0,
  products: 0,
  extractions: 0
})

const activities = ref<any[]>([])

// 系统状态数据
const systemStats = ref({
  cpu: { percent: 0, count: 0 },
  memory: { total: 0, used: 0, percent: 0 },
  disk: { total: 0, used: 0, percent: 0 },
  uptime: { seconds: 0, boot_time: '' }
})
const loadingSystemStats = ref(false)

// 使用 vueuse 的 useTransition 实现数字滚动
const CountTo = {
  props: ['startVal', 'endVal', 'duration'],
  setup(props: { startVal: number, endVal: number, duration: number }) {
    const source = ref(props.startVal)
    const output = useTransition(source, {
      duration: props.duration,
      transition: TransitionPresets.easeOutExpo,
    })
    
    // 监听 endVal 变化
    onMounted(() => {
      source.value = props.endVal
    })
    
    // 监听 props 变化 (如果 endVal 是响应式的)
    import('vue').then(({ watch }) => {
      watch(() => props.endVal, (val) => {
        source.value = val
      })
    })

    return () => Math.round(output.value).toLocaleString()
  }
}

const loadStats = async () => {
  try {
    // 获取批次统计
    const { data: batchData } = await http.get('/imports')
    stats.value.batches = batchData.total || 0

    // 获取产品统计
    const { data: productData } = await http.get('/products', {
      params: { page: 1, pageSize: 1 }
    })
    stats.value.products = productData.total || 0
    
  } catch (err) {
    console.error('加载统计数据失败:', err)
  }
}

// 加载系统状态
const loadSystemStats = async () => {
  loadingSystemStats.value = true
  try {
    const { data } = await http.get('/dashboard/system-stats')
    systemStats.value = data
  } catch (err) {
    console.error('加载系统状态失败:', err)
  } finally {
    loadingSystemStats.value = false
  }
}

// 工具函数
const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatUptime = (seconds: number) => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) return `${days}天 ${hours}小时`
  if (hours > 0) return `${hours}小时 ${minutes}分钟`
  return `${minutes}分钟`
}

const formatBootTime = (bootTime: string) => {
  if (!bootTime) return '-'
  return new Date(bootTime).toLocaleString('zh-CN', { 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const getProgressColor = (percent: number) => {
  if (percent < 60) return '#67c23a'
  if (percent < 80) return '#e6a23c'
  return '#f56c6c'
}

// 计算属性
const systemHealthType = computed(() => {
  const maxPercent = Math.max(
    systemStats.value.cpu.percent,
    systemStats.value.memory.percent,
    systemStats.value.disk.percent
  )
  if (maxPercent < 60) return 'success'
  if (maxPercent < 80) return 'warning'
  return 'danger'
})

const systemHealthText = computed(() => {
  const type = systemHealthType.value
  if (type === 'success') return '运行正常'
  if (type === 'warning') return '负载较高'
  return '负载过高'
})

const formatTime = (val: string) => {
  if (!val) return ''
  return new Date(val).toLocaleString()
}

const getActivityType = (action: string) => {
  if (action.includes('failed') || action.includes('error')) return 'danger'
  if (action.includes('success') || action.includes('completed')) return 'success'
  return 'primary'
}

const getActivityColor = (action: string) => {
  if (action.includes('failed') || action.includes('error')) return '#f56c6c'
  if (action.includes('success') || action.includes('completed')) return '#67c23a'
  return '#409eff'
}

const getActivityLabel = (action: string) => {
  const map: Record<string, string> = {
    'import_batch_created': '创建导入批次',
    'import_batch_completed': '导入批次完成',
    'import_batch_failed': '导入批次失败',
    'export_job_created': '创建导出任务',
    'extraction_task_created': '创建 AI 提取任务',
    'extraction_task_completed': 'AI 提取任务完成',
    'extraction_task_failed': 'AI 提取任务失败',
    'user_login': '用户登录'
  }
  return map[action] || action
}

// 自动刷新
let refreshTimer: number | null = null

onMounted(() => {
  loadStats()
  loadSystemStats()
  // 每30秒刷新一次系统状态
  refreshTimer = window.setInterval(loadSystemStats, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style scoped lang="scss">
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.mb-6 { margin-bottom: 24px; }
.mb-4 { margin-bottom: 16px; }
.mb-2 { margin-bottom: 8px; }
.text-2xl { font-size: 1.5rem; }
.font-bold { font-weight: 700; }
.text-gray-500 { color: var(--text-secondary); }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }

// 统计卡片
.stat-card {
  position: relative;
  padding: 24px;
  border-radius: var(--radius-lg);
  color: #fff;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-lg);
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-xl);
    
    .stat-bg-icon {
      transform: scale(1.2) rotate(15deg);
      opacity: 0.2;
    }
  }
}

.primary-card { background: var(--primary-gradient); }
.success-card { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.warning-card { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  backdrop-filter: blur(10px);
}

.stat-info {
  z-index: 1;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-bg-icon {
  position: absolute;
  right: -10px;
  bottom: -10px;
  font-size: 120px;
  opacity: 0.1;
  transform: rotate(0deg);
  transition: all 0.5s ease;
}

// 快速入口卡片
.quick-action-card {
  background: var(--bg-primary);
  height: 100%;
  padding: 20px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
    border-color: var(--primary-light);
    
    .arrow-icon {
      transform: translateX(4px);
      color: var(--primary-color);
    }
  }
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.bg-blue-100 { background: #dbeafe; }
.text-blue-600 { color: #2563eb; }
.bg-green-100 { background: #d1fae5; }
.text-green-600 { color: #059669; }
.bg-orange-100 { background: #ffedd5; }
.text-orange-600 { color: #ea580c; }
.bg-purple-100 { background: #f3e8ff; }
.text-purple-600 { color: #9333ea; }

.action-info {
  flex: 1;
  
  h4 {
    margin: 0 0 4px;
    font-size: 16px;
    color: var(--text-primary);
  }
  
  p {
    margin: 0;
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.arrow-icon {
  color: var(--text-tertiary);
  transition: all 0.3s ease;
}

// 系统状态指标卡片
.system-status {
  .metric-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: var(--bg-primary);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-light);
    transition: all 0.3s ease;
    
    &:hover {
      border-color: var(--primary-light);
      box-shadow: var(--shadow-sm);
    }
  }
  
  .metric-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    flex-shrink: 0;
    
    &.cpu-icon {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
    }
    
    &.memory-icon {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      color: #fff;
    }
    
    &.disk-icon {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      color: #fff;
    }
    
    &.uptime-icon {
      background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      color: #fff;
    }
  }
  
  .metric-info {
    flex: 1;
    min-width: 0;
  }
  
  .metric-label {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 6px;
  }
  
  .metric-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
    line-height: 1;
    
    &.uptime-value {
      font-size: 20px;
    }
  }
  
  .metric-detail {
    font-size: 12px;
    color: var(--text-tertiary);
    margin-top: 6px;
  }
  
  :deep(.el-progress) {
    .el-progress-bar__outer {
      background-color: var(--border-light);
    }
  }
}

// 动画延迟
.slide-in {
  animation: slideInRight 0.5s ease-out backwards;
  animation-delay: var(--delay, 0s);
}
</style>
