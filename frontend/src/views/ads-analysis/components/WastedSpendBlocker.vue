<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { amazonAdsApi, type WastedSpendResponse } from '@/api/amazon-ads'
import { Money, Warning } from '@element-plus/icons-vue'

const props = defineProps<{
  storeId?: string
}>()

const loading = ref(false)
const data = ref<WastedSpendResponse | null>(null)

const fetchData = async () => {
  if (!props.storeId) return
  loading.value = true
  try {
    const res = await amazonAdsApi.getWastedSpend(props.storeId)
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
  <div class="wasted-spend-card" v-if="loading || (data && data.campaign_count > 0)">
    <div v-if="loading" class="loading-placeholder">
      <el-skeleton :rows="3" animated />
    </div>
    
    <template v-else>
      <div class="card-header">
        <div class="icon-wrapper">
          <el-icon><Money /></el-icon>
        </div>
        <div class="header-content">
          <h3>无效花费拦截</h3>
          <p>发现 {{ data?.campaign_count }} 个广告活动在过去 7 天无转化</p>
        </div>
        <div class="total-wasted">
          <span class="label">浪费金额</span>
          <span class="amount">{{ formatCurrency(data?.total_wasted_spend || 0) }}</span>
        </div>
      </div>

      <div class="campaign-list">
        <div v-for="camp in data?.campaigns" :key="camp.id" class="campaign-item">
          <div class="camp-info">
            <span class="camp-name">{{ camp.name }}</span>
            <span class="camp-clicks">{{ camp.clicks }} Clicks</span>
          </div>
          <div class="camp-spend">
            {{ formatCurrency(camp.spend) }}
          </div>
        </div>
      </div>
      
      <div class="card-footer">
        <el-button type="danger" plain size="small">一键暂停所有</el-button>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.wasted-spend-card {
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
    background: rgba(245, 108, 108, 0.1);
    color: var(--danger-color);
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
  
  .total-wasted {
    text-align: right;
    .label { display: block; font-size: 10px; color: var(--text-secondary); }
    .amount { font-size: 20px; font-weight: bold; color: var(--danger-color); }
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
    
    .camp-name { font-size: 13px; color: var(--text-primary); font-weight: 500; }
    .camp-clicks { font-size: 11px; color: var(--text-secondary); }
  }
  
  .camp-spend {
    font-size: 13px;
    color: var(--danger-color);
    font-weight: 600;
  }
}

.card-footer {
  margin-top: 16px;
  text-align: right;
}
</style>
