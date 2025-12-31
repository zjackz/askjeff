<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { amazonAdsApi, type HighAcosResponse } from '@/api/amazon-ads'
import { Warning } from '@element-plus/icons-vue'

const props = defineProps<{
  storeId?: string
}>()

const loading = ref(false)
const data = ref<HighAcosResponse | null>(null)

const fetchData = async () => {
  if (!props.storeId) return
  loading.value = true
  try {
    const res = await amazonAdsApi.getHighAcos(props.storeId)
    data.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

watch(() => props.storeId, fetchData)
onMounted(fetchData)

const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}
</script>

<template>
  <div class="high-acos-card" v-if="loading || (data && data.campaign_count > 0)">
    <div v-if="loading" class="loading-placeholder">
      <el-skeleton :rows="3" animated />
    </div>

    <template v-else>
      <div class="card-header">
        <div class="icon-wrapper">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="header-content">
          <h3>高 ACOS 预警</h3>
          <p>发现 {{ data?.campaign_count }} 个广告活动 ACOS 超过 30%</p>
        </div>
      </div>

      <div class="campaign-list">
        <div v-for="camp in data?.campaigns" :key="camp.id" class="campaign-item">
          <div class="camp-info">
            <span class="camp-name">{{ camp.name }}</span>
            <div class="camp-metrics">
              <span>Spend: {{ formatCurrency(camp.spend) }}</span>
              <span>Sales: {{ formatCurrency(camp.sales) }}</span>
            </div>
          </div>
          <div class="camp-acos">
            <span class="acos-val">{{ camp.acos.toFixed(1) }}%</span>
            <span class="acos-label">ACOS</span>
          </div>
        </div>
      </div>
      
      <div class="card-footer">
        <el-button type="warning" plain size="small">一键降低竞价</el-button>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.high-acos-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  
  .icon-wrapper {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    background: rgba(230, 162, 60, 0.1);
    color: var(--warning-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
  }
  
  .header-content {
    flex: 1;
    h3 { margin: 0 0 4px 0; font-size: 16px; color: var(--text-primary); }
    p { margin: 0; font-size: 12px; color: var(--text-secondary); }
  }
}

.campaign-list {
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  max-height: 200px;
  overflow-y: auto;
}

.campaign-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-light);
  
  &:last-child { border-bottom: none; }
  
  .camp-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
    
    .camp-name { font-size: 13px; color: var(--text-primary); font-weight: 500; }
    .camp-metrics { 
      font-size: 11px; 
      color: var(--text-secondary); 
      display: flex;
      gap: 8px;
    }
  }
  
  .camp-acos {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    
    .acos-val { font-size: 14px; color: var(--warning-color); font-weight: 700; }
    .acos-label { font-size: 10px; color: var(--text-tertiary); }
  }
}

.card-footer {
  margin-top: 16px;
  text-align: right;
}
</style>
