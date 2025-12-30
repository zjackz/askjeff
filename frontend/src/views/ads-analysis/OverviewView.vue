<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { http } from '@/utils/http'
import { ElMessage } from 'element-plus'
import { 
  TrendCharts, 
  Money, 
  ShoppingCart, 
  PieChart,
  CircleCheck,
  Warning,
  InfoFilled
} from '@element-plus/icons-vue'

const props = defineProps<{
  storeId: string | undefined
}>()

const loading = ref(false)
const data = ref<any>(null)

const fetchData = async () => {
  if (!props.storeId) return
  loading.value = true
  try {
    const response = await http.get('ads-analysis/overview', {
      params: { store_id: props.storeId }
    })
    data.value = response.data
  } catch (error) {
    console.error('Failed to fetch overview:', error)
    ElMessage.error('获取概览数据失败')
  } finally {
    loading.value = false
  }
}

watch(() => props.storeId, fetchData)
onMounted(fetchData)

const getScoreColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}
</script>

<template>
  <div class="overview-view">
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><TrendCharts /></el-icon>
      <p>正在聚合全店数据...</p>
    </div>

    <div v-else-if="data" class="overview-content">
      <!-- Top KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card health">
          <div class="kpi-header">
            <span class="kpi-label">健康度评分</span>
            <el-icon><InfoFilled /></el-icon>
          </div>
          <div class="score-display" :style="{ color: getScoreColor(data.health_score) }">
            <span class="score-value">{{ data.health_score }}</span>
            <span class="score-max">/ 100</span>
          </div>
          <div class="score-bar-bg">
            <div class="score-bar" :style="{ width: data.health_score + '%', backgroundColor: getScoreColor(data.health_score) }"></div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">总销售额</span>
            <el-icon><Money /></el-icon>
          </div>
          <div class="kpi-value">${{ data.total_sales.toLocaleString() }}</div>
          <div class="kpi-footer">
            <span class="trend up">↑ 12.5%</span>
            <span class="period">vs 环比</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">总广告支出</span>
            <el-icon><ShoppingCart /></el-icon>
          </div>
          <div class="kpi-value">${{ data.total_spend.toLocaleString() }}</div>
          <div class="kpi-footer">
            <span class="trend down">↓ 3.2%</span>
            <span class="period">vs 环比</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">全店 TACOS</span>
            <el-icon><PieChart /></el-icon>
          </div>
          <div class="kpi-value">{{ data.tacos }}%</div>
          <div class="kpi-footer">
            <span class="status-tag" :class="data.tacos < 15 ? 'success' : 'warning'">
              {{ data.tacos < 15 ? '健康' : '偏高' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Main Sections -->
      <div class="sections-grid">
        <!-- Quadrant Distribution -->
        <div class="glass-section distribution-card">
          <h3 class="section-title">产品表现分布</h3>
          <div class="dist-grid">
            <div class="dist-item q2">
              <span class="d-label">明星增长 (Q2)</span>
              <span class="d-value">{{ data.quadrant_distribution.Q2 }}</span>
              <span class="d-desc">高库存 / 低 TACOS</span>
            </div>
            <div class="dist-item q3">
              <span class="d-label">潜力防御 (Q3)</span>
              <span class="d-value">{{ data.quadrant_distribution.Q3 }}</span>
              <span class="d-desc">低库存 / 低 TACOS</span>
            </div>
            <div class="dist-item q1">
              <span class="d-label">积压清仓 (Q1)</span>
              <span class="d-value">{{ data.quadrant_distribution.Q1 }}</span>
              <span class="d-desc">高库存 / 高 TACOS</span>
            </div>
            <div class="dist-item q4">
              <span class="d-label">淘汰清理 (Q4)</span>
              <span class="d-value">{{ data.quadrant_distribution.Q4 }}</span>
              <span class="d-desc">低库存 / 高 TACOS</span>
            </div>
          </div>
        </div>

        <!-- Top Movers -->
        <div class="glass-section movers-card">
          <h3 class="section-title">核心 SKU 表现</h3>
          <div class="movers-list">
            <div v-for="sku in data.top_movers" :key="sku.sku" class="mover-item">
              <div class="m-info">
                <span class="m-sku">{{ sku.sku }}</span>
                <span class="m-status">{{ sku.status }}</span>
              </div>
              <div class="m-metrics">
                <div class="m-metric">
                  <span class="l">Sales</span>
                  <span class="v">${{ sku.sales.toLocaleString() }}</span>
                </div>
                <div class="m-metric">
                  <span class="l">Margin</span>
                  <span class="v" :class="sku.margin > 0 ? 'pos' : 'neg'">{{ sku.margin }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.overview-view {
  height: 100%;
  overflow-y: auto;
}

.loading-state {
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  gap: 16px;
}

.is-loading {
  font-size: 48px;
  color: var(--primary-color);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
    border-color: var(--primary-light);
  }
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-secondary);
  font-size: 14px;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.kpi-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.trend.up { color: var(--success-color); }
.trend.down { color: var(--danger-color); }
.period { color: var(--text-tertiary); }

.status-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  
  &.success { 
    background: rgba(16, 185, 129, 0.1); 
    color: var(--success-color); 
  }
  &.warning { 
    background: rgba(245, 158, 11, 0.1); 
    color: var(--warning-color); 
  }
}

/* Health Score Card */
.score-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.score-value {
  font-size: 40px;
  font-weight: 800;
}
.score-max {
  font-size: 14px;
  color: var(--text-tertiary);
}
.score-bar-bg {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}
.score-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease-out;
}

/* Sections Grid */
.sections-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
}

.glass-section {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text-primary);
}

/* Distribution Grid */
.dist-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.dist-item {
  padding: 20px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid var(--border-light);
  transition: all 0.3s;

  &:hover {
    border-color: var(--primary-light);
    background: var(--bg-secondary);
  }

  &.q2 { background: rgba(16, 185, 129, 0.02); border-color: rgba(16, 185, 129, 0.1); }
  &.q3 { background: rgba(59, 130, 246, 0.02); border-color: rgba(59, 130, 246, 0.1); }
  &.q1 { background: rgba(239, 68, 68, 0.02); border-color: rgba(239, 68, 68, 0.1); }
  &.q4 { background: rgba(107, 114, 128, 0.02); border-color: rgba(107, 114, 128, 0.1); }
}

.d-label { font-size: 12px; color: var(--text-secondary); font-weight: 600; }
.d-value { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.d-desc { font-size: 11px; color: var(--text-tertiary); }

/* Movers List */
.movers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mover-item {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: var(--radius-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid var(--border-light);
  transition: all 0.3s;

  &:hover {
    border-color: var(--primary-light);
    background: var(--bg-primary);
  }
}

.m-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.m-sku { font-weight: 600; font-size: 14px; color: var(--text-primary); }
.m-status { font-size: 11px; color: var(--text-secondary); }

.m-metrics {
  display: flex;
  gap: 20px;
  text-align: right;
}

.m-metric {
  display: flex;
  flex-direction: column;
}

.m-metric .l { font-size: 10px; color: var(--text-tertiary); text-transform: uppercase; }
.m-metric .v { font-size: 13px; font-weight: 700; color: var(--text-primary); }
.m-metric .v.pos { color: var(--success-color); }
.m-metric .v.neg { color: var(--danger-color); }
</style>
