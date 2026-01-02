<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { http } from '@/utils/http'
import { ElMessage } from 'element-plus'
import { 
  MagicStick, 
  CircleCheck,
  ArrowRight
} from '@element-plus/icons-vue'
import WastedSpendBlocker from './components/WastedSpendBlocker.vue'
import HighAcosWarning from './components/HighAcosWarning.vue'

const props = defineProps<{
  storeId: string | undefined
}>()

const loading = ref(false)
const actions = ref<any[]>([])

const fetchActions = async () => {
  if (!props.storeId) return
  loading.value = true
  try {
    // 暂时从 matrix 接口获取数据并生成建议
    const response = await http.get('ads-analysis/matrix', {
      params: { store_id: props.storeId }
    })
    
    // 模拟 AI 生成建议逻辑
    actions.value = response.data
      .filter((item: any) => item.status !== 'POTENTIAL / DEFENSE')
      .map((item: any) => {
        let priority = 'P2'
        let type = 'optimization'
        let suggestion = ''
        
        if (item.status === 'CRITICAL / CLEARANCE') {
          priority = 'P0'
          type = 'emergency'
          suggestion = '库存积压严重且广告亏损。建议立即降低售价 15% 并提高广告预算以加速清仓。'
        } else if (item.status === 'STAR / GROWTH') {
          priority = 'P1'
          type = 'growth'
          suggestion = '表现优异且库存充足。建议提高核心关键词竞价，抢占 Top of Search 流量。'
        } else if (item.status === 'DROP / KILL') {
          priority = 'P2'
          type = 'cleanup'
          suggestion = '销量低且无库存优势。建议大幅削减广告预算，考虑自然淘汰。'
        }
        
        return {
          id: item.sku,
          sku: item.sku,
          asin: item.asin,
          priority,
          type,
          suggestion,
          metrics: {
            tacos: item.tacos,
            margin: item.margin,
            stock_weeks: item.stock_weeks
          }
        }
      })
      .sort((a: any, b: any) => a.priority.localeCompare(b.priority))
  } catch (error) {
    console.error('Failed to fetch actions:', error)
    ElMessage.error('获取建议失败')
  } finally {
    loading.value = false
  }
}

watch(() => props.storeId, fetchActions)
onMounted(fetchActions)

const handleApply = (action: any) => {
  ElMessage.success(`已应用策略: ${action.sku}`)
}
</script>

<template>
  <div class="actions-view">
    <div class="actions-header">
      <div class="h-left">
        <h2 class="h-title">智能决策中心</h2>
        <p class="h-subtitle">AI 根据当前库存与广告表现生成的优化建议</p>
      </div>
      <div class="h-right">
        <span class="action-count">{{ actions.length }} 条待处理建议</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><MagicStick /></el-icon>
      <p>AI 正在扫描全店 SKU...</p>
    </div>

    <div v-else class="actions-content">
      <!-- 诊断卡片区域 -->
      <div class="diagnosis-grid">
        <WastedSpendBlocker :store-id="storeId" />
        <HighAcosWarning :store-id="storeId" />
      </div>

      <!-- 建议列表 -->
      <div class="actions-list">
        <div v-for="action in actions" :key="action.id" class="action-card" :class="action.type">
          <div class="card-side-indicator"></div>
          
          <div class="card-main">
            <div class="card-top">
              <div class="sku-info">
                <span class="priority-tag">{{ action.priority }}</span>
                <span class="sku-name">{{ action.sku }}</span>
                <span class="asin-name">{{ action.asin }}</span>
              </div>
              <div class="type-tag">{{ action.type }}</div>
            </div>

            <div class="card-body">
              <div class="suggestion-box">
                <el-icon class="magic-icon"><MagicStick /></el-icon>
                <p class="suggestion-text">{{ action.suggestion }}</p>
              </div>
              
              <div class="metrics-row">
                <div class="m-item">
                  <span class="l">TACOS</span>
                  <span class="v">{{ action.metrics.tacos }}%</span>
                </div>
                <div class="m-item">
                  <span class="l">Margin</span>
                  <span class="v" :class="action.metrics.margin > 0 ? 'pos' : 'neg'">{{ action.metrics.margin }}%</span>
                </div>
                <div class="m-item">
                  <span class="l">Stock</span>
                  <span class="v">{{ action.metrics.stock_weeks }}w</span>
                </div>
              </div>
            </div>

            <div class="card-footer">
              <button class="apply-btn" @click="handleApply(action)">
                <el-icon><CircleCheck /></el-icon>
                立即执行
              </button>
              <button class="detail-btn">
                查看详情
                <el-icon><ArrowRight /></el-icon>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.actions-view {
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.actions-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.h-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.h-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
}

.action-count {
  font-size: 13px;
  color: var(--primary-color);
  font-weight: 600;
  background: rgba(102, 126, 234, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
}

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  gap: 16px;
}

.diagnosis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.actions-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.action-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  display: flex;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
    border-color: var(--primary-light);
  }
}

.card-side-indicator {
  width: 6px;
  background: var(--primary-color);
}

.action-card.emergency .card-side-indicator { background: var(--danger-color); }
.action-card.growth .card-side-indicator { background: var(--success-color); }
.action-card.cleanup .card-side-indicator { background: var(--text-tertiary); }

.card-main {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sku-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.priority-tag {
  font-size: 10px;
  font-weight: 700;
  background: var(--text-primary);
  color: var(--bg-primary);
  padding: 2px 6px;
  border-radius: 4px;
}

.sku-name {
  font-weight: 700;
  font-size: 15px;
  color: var(--text-primary);
}

.asin-name {
  font-size: 12px;
  color: var(--text-secondary);
}

.type-tag {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-tertiary);
}

.suggestion-box {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 12px;
  display: flex;
  gap: 12px;
  border: 1px solid var(--border-light);
}

.magic-icon {
  color: var(--primary-color);
  font-size: 18px;
  flex-shrink: 0;
}

.suggestion-text {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-primary);
  margin: 0;
}

.metrics-row {
  display: flex;
  gap: 24px;
}

.m-item {
  display: flex;
  flex-direction: column;
}

.m-item .l { font-size: 10px; color: var(--text-tertiary); text-transform: uppercase; }
.m-item .v { font-size: 14px; font-weight: 700; color: var(--text-primary); }
.m-item .v.pos { color: var(--success-color); }
.m-item .v.neg { color: var(--danger-color); }

.card-footer {
  display: flex;
  gap: 12px;
  margin-top: auto;
}

.apply-btn {
  flex: 1;
  background: var(--primary-color);
  border: none;
  color: #fff;
  padding: 10px;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;

  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
  }
}

.detail-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 10px 16px;
  border-radius: var(--radius-md);
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border-color: var(--primary-light);
  }
}
</style>
