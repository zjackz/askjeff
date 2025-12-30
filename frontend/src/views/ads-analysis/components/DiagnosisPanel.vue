<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { http } from '@/utils/http'
import { ElMessage } from 'element-plus'
import { 
  DataAnalysis, 
  TrendCharts, 
  MagicStick, 
  CircleCheck,
  Close,
  Warning
} from '@element-plus/icons-vue'

const props = defineProps<{
  selectedSku: any | null
  storeId: string | undefined
}>()

const emit = defineEmits(['apply-strategy', 'close'])

const loading = ref(false)
const diagnosisResult = ref<string>('')

const statusInfo = computed(() => {
  if (!props.selectedSku) return { type: 'info', text: 'N/A', color: '#909399' }
  const { stock_weeks, tacos } = props.selectedSku
  if (stock_weeks > 24 && tacos > 20) return { type: 'danger', text: 'CRITICAL / CLEARANCE', color: '#ef4444' }
  if (stock_weeks > 24 && tacos <= 20) return { type: 'success', text: 'STAR / GROWTH', color: '#10b981' }
  if (stock_weeks <= 24 && tacos <= 20) return { type: 'primary', text: 'POTENTIAL / DEFENSE', color: '#3b82f6' }
  return { type: 'warning', text: 'DROP / KILL', color: '#f59e0b' }
})

const fetchDiagnosis = async () => {
  if (!props.selectedSku || !props.storeId) return
  
  loading.value = true
  diagnosisResult.value = ''
  try {
    const response = await http.get(`ads-analysis/${props.selectedSku.sku}/diagnosis`, {
      params: { store_id: props.storeId }
    })
    diagnosisResult.value = response.data.diagnosis
  } catch (error) {
    console.error('Failed to fetch AI diagnosis:', error)
    ElMessage.error('获取 AI 诊断失败')
  } finally {
    loading.value = false
  }
}

watch(() => props.selectedSku?.sku, (newSku) => {
  if (newSku) {
    fetchDiagnosis()
  } else {
    diagnosisResult.value = ''
  }
})
</script>

<template>
  <div class="premium-diagnosis-panel">
    <!-- Empty State -->
    <div v-if="!selectedSku" class="empty-state">
      <div class="glass-circle">
        <el-icon class="floating-icon"><DataAnalysis /></el-icon>
      </div>
      <p class="empty-title">等待数据选择</p>
      <p class="empty-desc">请在左侧矩阵中点击任意 SKU<br>获取深度 AI 诊断报告</p>
    </div>

    <!-- Active State -->
    <div v-else class="active-content">
      <!-- Header Section -->
      <div class="panel-header">
        <div class="title-group">
          <el-icon class="header-icon"><TrendCharts /></el-icon>
          <div class="text-content">
            <h2 class="sku-id">{{ selectedSku.sku }}</h2>
            <span class="asin-label">ASIN: {{ selectedSku.asin }}</span>
          </div>
        </div>
        <button class="close-btn" @click="emit('close')">
          <el-icon><Close /></el-icon>
        </button>
      </div>

      <!-- Status Badge -->
      <div class="status-section">
        <div class="status-badge" :style="{ '--badge-color': statusInfo.color }">
          <span class="pulse-dot"></span>
          {{ statusInfo.text }}
        </div>
      </div>

      <!-- Metrics Grid -->
      <div class="metrics-grid">
        <div class="metric-card">
          <span class="m-label">库存周转</span>
          <div class="m-value">
            {{ selectedSku.stock_weeks.toFixed(1) }}<span class="m-unit">周</span>
          </div>
          <div class="m-progress-bg">
            <div class="m-progress-bar" :style="{ width: Math.min(selectedSku.stock_weeks * 2, 100) + '%' }"></div>
          </div>
        </div>
        <div class="metric-card">
          <span class="m-label">TACOS</span>
          <div class="m-value" :class="{ 'text-danger': selectedSku.tacos > 20, 'text-success': selectedSku.tacos <= 20 }">
            {{ selectedSku.tacos.toFixed(1) }}<span class="m-unit">%</span>
          </div>
          <div class="m-progress-bg">
            <div class="m-progress-bar" :style="{ width: Math.min(selectedSku.tacos * 2, 100) + '%', backgroundColor: selectedSku.tacos > 20 ? '#f56c6c' : '#67c23a' }"></div>
          </div>
        </div>
        <div class="metric-card">
          <span class="m-label">ACOS</span>
          <div class="m-value">
            {{ selectedSku.acos.toFixed(1) }}<span class="m-unit">%</span>
          </div>
          <div class="m-progress-bg">
            <div class="m-progress-bar" :style="{ width: Math.min(selectedSku.acos, 100) + '%', backgroundColor: '#e6a23c' }"></div>
          </div>
        </div>
        <div class="metric-card">
          <span class="m-label">净利润率</span>
          <div class="m-value" :class="{ 'text-danger': selectedSku.margin < 0, 'text-success': selectedSku.margin > 15 }">
            {{ selectedSku.margin.toFixed(1) }}<span class="m-unit">%</span>
          </div>
          <div class="m-progress-bg">
            <div class="m-progress-bar" :style="{ width: Math.max(0, Math.min(selectedSku.margin * 2, 100)) + '%', backgroundColor: selectedSku.margin > 0 ? '#67c23a' : '#f56c6c' }"></div>
          </div>
        </div>
      </div>

      <!-- Funnel Analysis -->
      <div class="funnel-section">
        <h3 class="section-title">流量漏斗诊断</h3>
        <div class="funnel-container">
          <div class="funnel-item">
            <div class="funnel-label">
              <span>点击率 (CTR)</span>
              <span class="f-value">{{ selectedSku.ctr.toFixed(2) }}%</span>
            </div>
            <div class="funnel-bar-wrapper">
              <div class="funnel-bar ctr" :style="{ width: Math.min(selectedSku.ctr * 50, 100) + '%' }"></div>
              <span class="benchmark">基准: 0.5%</span>
            </div>
          </div>
          <div class="funnel-item">
            <div class="funnel-label">
              <span>转化率 (CVR)</span>
              <span class="f-value">{{ selectedSku.cvr.toFixed(2) }}%</span>
            </div>
            <div class="funnel-bar-wrapper">
              <div class="funnel-bar cvr" :style="{ width: Math.min(selectedSku.cvr * 5, 100) + '%' }"></div>
              <span class="benchmark">基准: 10%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Insight Card -->
      <div class="ai-insight-card" :style="{ borderColor: statusInfo.color + '44' }" v-loading="loading">
        <div class="ai-header">
          <el-icon class="ai-icon"><MagicStick /></el-icon>
          <span>AI 策略洞察</span>
        </div>
        <div class="ai-body">
          <p class="ai-text" v-if="diagnosisResult">{{ diagnosisResult }}</p>
          <p class="ai-text" v-else-if="!loading">正在生成 AI 深度诊断建议...</p>
          <div class="ai-tags">
            <span v-if="selectedSku.ctr < 0.4" class="ai-tag warning">流量吸引力不足</span>
            <span v-if="selectedSku.cvr < 8" class="ai-tag warning">页面转化待优化</span>
            <span v-if="selectedSku.margin < 5" class="ai-tag danger">利润空间极低</span>
            <span v-if="selectedSku.stock_weeks > 30" class="ai-tag info">库存周转缓慢</span>
          </div>
        </div>
      </div>

      <!-- Action Footer -->
      <div class="action-footer">
        <button class="primary-action-btn" @click="emit('apply-strategy', selectedSku)">
          <el-icon><CircleCheck /></el-icon>
          一键采纳建议
        </button>
        <button class="secondary-action-btn" @click="emit('close')">
          暂不处理
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.premium-diagnosis-panel {
  height: 100%;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
  color: var(--text-primary);
  font-family: var(--font-family-base);
}

/* Empty State Styles */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.glass-circle {
  width: 80px;
  height: 80px;
  background: var(--bg-secondary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}

.floating-icon {
  font-size: 32px;
  color: var(--primary-color);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.empty-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Active State Styles */
.active-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.title-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

.header-icon {
  font-size: 24px;
  color: var(--primary-color);
  background: rgba(102, 126, 234, 0.1);
  padding: 8px;
  border-radius: 10px;
}

.sku-id {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.asin-label {
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
}

.close-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
}

.status-section {
  margin-bottom: 24px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--badge-color);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--badge-color);
  text-transform: uppercase;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  box-shadow: 0 0 8px currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.7; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.7; }
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 32px;
}

.metric-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  padding: 16px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
}

.m-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.m-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.m-unit {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-left: 4px;
}

.m-progress-bg {
  height: 4px;
  background: var(--border-light);
  border-radius: 2px;
  overflow: hidden;
}

.m-progress-bar {
  height: 100%;
  background: var(--primary-color);
  border-radius: 2px;
  transition: width 1s ease-out;
}

.text-danger { color: var(--danger-color); }
.text-success { color: var(--success-color); }

/* Funnel Section */
.funnel-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.funnel-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.funnel-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.funnel-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-primary);
}

.f-value {
  font-weight: 700;
  color: var(--primary-color);
}

.funnel-bar-wrapper {
  position: relative;
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
}

.funnel-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease-out;
}

.funnel-bar.ctr { background: var(--primary-gradient); }
.funnel-bar.cvr { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }

.benchmark {
  position: absolute;
  right: 0;
  top: -18px;
  font-size: 10px;
  color: var(--text-tertiary);
}

.ai-insight-card {
  background: var(--bg-secondary);
  border: 1px solid var(--primary-light);
  border-radius: var(--radius-lg);
  padding: 20px;
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 12px;
}

.ai-icon {
  font-size: 18px;
}

.ai-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.ai-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ai-tag {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
  
  &.warning { background: rgba(245, 158, 11, 0.1); color: var(--warning-color); border: 1px solid rgba(245, 158, 11, 0.2); }
  &.danger { background: rgba(239, 68, 68, 0.1); color: var(--danger-color); border: 1px solid rgba(239, 68, 68, 0.2); }
  &.info { background: rgba(59, 130, 246, 0.1); color: var(--info-color); border: 1px solid rgba(59, 130, 246, 0.2); }
}

.action-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.primary-action-btn {
  background: var(--primary-gradient);
  border: none;
  color: #fff;
  padding: 16px;
  border-radius: var(--radius-lg);
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: var(--shadow-primary);

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
}

.secondary-action-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 14px;
  border-radius: var(--radius-lg);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border-color: var(--primary-light);
  }
}
</style>
