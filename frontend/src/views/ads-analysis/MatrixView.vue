<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AdsMatrixChart from './components/AdsMatrixChart.vue'
import DiagnosisPanel from './components/DiagnosisPanel.vue'
import { http } from '@/utils/http'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps<{
  storeId: string | undefined
}>()

const selectedSku = ref(null)
const matrixData = ref([])
const loading = ref(false)

const fetchMatrixData = async () => {
  if (!props.storeId) return
  
  loading.value = true
  try {
    const response = await http.get('ads-analysis/matrix', {
      params: { store_id: props.storeId }
    })
    matrixData.value = response.data
  } catch (error) {
    console.error('Failed to fetch matrix data:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

watch(() => props.storeId, () => {
  selectedSku.value = null
  fetchMatrixData()
})

onMounted(fetchMatrixData)

const handleSkuSelect = (skuData: any) => {
  selectedSku.value = skuData
}

const handleApplyStrategy = (skuData: any) => {
  ElMessage.success(`已为 ${skuData.sku} 应用优化策略！`)
}

const handleClosePanel = () => {
  selectedSku.value = null
}
</script>

<template>
  <div class="matrix-view">
    <main class="dashboard-layout">
      <!-- Left: Visualization -->
      <section class="visualization-section">
        <div class="glass-card chart-card">
          <div class="card-header">
            <div class="header-title-group">
              <span class="card-label">表现矩阵</span>
              <h3 class="card-title">Inventory vs TACOS</h3>
            </div>
            <div class="matrix-legend">
              <div class="legend-item"><span class="dot q1"></span> 积压清仓</div>
              <div class="legend-item"><span class="dot q2"></span> 明星增长</div>
              <div class="legend-item"><span class="dot q3"></span> 潜力防御</div>
              <div class="legend-item"><span class="dot q4"></span> 淘汰清理</div>
            </div>
          </div>
          
          <div class="chart-container">
            <div v-if="loading" class="loading-overlay">
              <el-icon class="is-loading"><Loading /></el-icon>
              <p>正在分析数据...</p>
            </div>
            <AdsMatrixChart v-else :data="matrixData" @select-sku="handleSkuSelect" />
          </div>
        </div>
      </section>

      <!-- Right: Intelligence Panel -->
      <aside class="intelligence-section">
        <div class="glass-card panel-card">
          <DiagnosisPanel 
            :selected-sku="selectedSku"
            :store-id="props.storeId"
            @apply-strategy="handleApplyStrategy"
            @close="handleClosePanel"
          />
        </div>
      </aside>
    </main>
  </div>
</template>

<style scoped lang="scss">
.matrix-view {
  height: 100%;
  overflow: hidden;
}

.dashboard-layout {
  height: 100%;
  display: flex;
  gap: 24px;
  min-height: 0;
}

.visualization-section {
  flex: 1;
  min-width: 0;
}

.intelligence-section {
  width: 420px;
  flex-shrink: 0;
}

.glass-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--primary-light);
  }
}

.card-header {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid var(--border-light);
}

.card-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--primary-color);
  font-weight: 700;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  margin: 4px 0 0 0;
  color: var(--text-primary);
}

.matrix-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.q1 { background: var(--danger-color); }
.q2 { background: var(--success-color); }
.q3 { background: var(--info-color); }
.q4 { background: var(--text-tertiary); }

.chart-container {
  flex: 1;
  position: relative;
  padding: 12px;
  background: var(--bg-primary);
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  z-index: 10;
  gap: 16px;
  color: var(--text-secondary);
}

.is-loading {
  font-size: 40px;
  color: var(--primary-color);
}
</style>
