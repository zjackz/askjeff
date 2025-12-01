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
      <el-col :span="6">
        <div class="quick-action-card" @click="$router.push('/import')">
          <div class="action-icon bg-blue-100 text-blue-600">
            <el-icon><Upload /></el-icon>
          </div>
          <div class="action-info">
            <h4>导入数据</h4>
            <p>上传新的产品数据文件</p>
          </div>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="quick-action-card" @click="$router.push('/chat')">
          <div class="action-icon bg-green-100 text-green-600">
            <el-icon><Search /></el-icon>
          </div>
          <div class="action-info">
            <h4>查询产品</h4>
            <p>AI 辅助产品数据查询</p>
          </div>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="quick-action-card" @click="$router.push('/extraction')">
          <div class="action-icon bg-orange-100 text-orange-600">
            <el-icon><MagicStick /></el-icon>
          </div>
          <div class="action-info">
            <h4>特征提取</h4>
            <p>智能提取产品特征</p>
          </div>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="quick-action-card" @click="$router.push('/export')">
          <div class="action-icon bg-purple-100 text-purple-600">
            <el-icon><Download /></el-icon>
          </div>
          <div class="action-info">
            <h4>导出数据</h4>
            <p>批量导出处理结果</p>
          </div>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </el-col>
    </el-row>
    
    <!-- 最近活动 (示例) -->
    <el-card class="recent-activity slide-in" style="--delay: 0.6s">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-bold">系统状态</span>
          <el-tag type="success" effect="dark" round>运行正常</el-tag>
        </div>
      </template>
      <el-empty description="暂无最近活动记录" :image-size="100" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Upload, Box, MagicStick, Search, Download, ArrowRight } from '@element-plus/icons-vue'
import { http, API_BASE } from '@/utils/http'
// 简单的数字滚动组件逻辑，实际项目中可以使用 vue-count-to
import { TransitionPresets, useTransition } from '@vueuse/core'

const stats = ref({
  batches: 0,
  products: 0,
  extractions: 0
})

// 使用 vueuse 的 useTransition 实现数字滚动
const CountTo = {
  props: ['startVal', 'endVal', 'duration'],
  setup(props: any) {
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
    const { data: batchData } = await http.get(`${API_BASE}/imports`)
    stats.value.batches = batchData.total || 0

    // 获取产品统计
    const { data: productData } = await http.get(`${API_BASE}/products`, {
      params: { page: 1, pageSize: 1 }
    })
    stats.value.products = productData.total || 0

    // 获取提取任务统计
    const { data: extractionData } = await http.get(`${API_BASE}/extraction/list`, {
      params: { limit: 1, offset: 0 }
    })
    stats.value.extractions = extractionData.length || 0
  } catch (err) {
    console.error('加载统计数据失败:', err)
  }
}

onMounted(() => {
  loadStats()
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

// 动画延迟
.slide-in {
  animation: slideInRight 0.5s ease-out backwards;
  animation-delay: var(--delay, 0s);
}
</style>
