<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { amazonAdsApi, type Campaign, type CampaignQueryParams } from '@/api/amazon-ads'
import { Search, Refresh, Filter, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  storeId?: string
}>()

// State
const loading = ref(false)
const campaigns = ref<Campaign[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// Filters
const filters = ref({
  state: '',
  campaign_type: '',
  search: ''
})

// Metrics Summary
const summary = computed(() => {
  const s = {
    spend: 0,
    sales: 0,
    orders: 0,
    clicks: 0,
    impressions: 0
  }
  campaigns.value.forEach(c => {
    s.spend += c.spend
    s.sales += c.sales
    s.orders += c.orders
    s.clicks += c.clicks
    s.impressions += c.impressions
  })
  return {
    ...s,
    acos: s.sales > 0 ? (s.spend / s.sales * 100) : 0,
    roas: s.spend > 0 ? (s.sales / s.spend) : 0,
    ctr: s.impressions > 0 ? (s.clicks / s.impressions * 100) : 0,
    cpc: s.clicks > 0 ? (s.spend / s.clicks) : 0,
    cvr: s.clicks > 0 ? (s.orders / s.clicks * 100) : 0
  }
})

// Fetch Data
const fetchCampaigns = async () => {
  if (!props.storeId) return
  
  loading.value = true
  try {
    const params: CampaignQueryParams = {
      store_id: props.storeId,
      page: currentPage.value,
      limit: pageSize.value,
      sort_by: 'spend',
      sort_order: 'desc'
    }
    
    if (filters.value.state) params.state = filters.value.state
    if (filters.value.campaign_type) params.campaign_type = filters.value.campaign_type
    
    const res = await amazonAdsApi.getCampaigns(params)
    campaigns.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('Failed to fetch campaigns:', error)
    ElMessage.error('获取广告活动失败')
  } finally {
    loading.value = false
  }
}

// Watchers
watch(() => props.storeId, () => {
  if (props.storeId) fetchCampaigns()
})

watch([currentPage, pageSize], () => {
  fetchCampaigns()
})

onMounted(() => {
  if (props.storeId) fetchCampaigns()
})

// Formatters
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
}

const formatPercent = (value: number) => {
  return `${value.toFixed(2)}%`
}

const formatNumber = (value: number) => {
  return new Intl.NumberFormat('en-US').format(value)
}

const getStateColor = (state: string) => {
  switch (state.toLowerCase()) {
    case 'enabled': return 'success'
    case 'paused': return 'warning'
    case 'archived': return 'info'
    default: return 'info'
  }
}
</script>

<template>
  <div class="campaign-manager">
    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="summary-card">
        <div class="label">Total Spend</div>
        <div class="value">{{ formatCurrency(summary.spend) }}</div>
        <div class="trend down">Target: $5,000</div>
      </div>
      <div class="summary-card">
        <div class="label">Total Sales</div>
        <div class="value">{{ formatCurrency(summary.sales) }}</div>
        <div class="trend up">ROAS: {{ summary.roas.toFixed(2) }}</div>
      </div>
      <div class="summary-card">
        <div class="label">ACOS</div>
        <div class="value" :class="{ 'text-red': summary.acos > 30, 'text-green': summary.acos <= 30 }">
          {{ formatPercent(summary.acos) }}
        </div>
        <div class="trend">Target: 30%</div>
      </div>
      <div class="summary-card">
        <div class="label">Orders</div>
        <div class="value">{{ formatNumber(summary.orders) }}</div>
        <div class="trend">CVR: {{ formatPercent(summary.cvr) }}</div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="left">
        <el-input
          v-model="filters.search"
          placeholder="搜索广告活动..."
          class="search-input"
          :prefix-icon="Search"
        />
        <el-select v-model="filters.state" placeholder="状态" clearable class="filter-select" @change="fetchCampaigns">
          <el-option label="开启 (Enabled)" value="enabled" />
          <el-option label="暂停 (Paused)" value="paused" />
          <el-option label="归档 (Archived)" value="archived" />
        </el-select>
        <el-select v-model="filters.campaign_type" placeholder="类型" clearable class="filter-select" @change="fetchCampaigns">
          <el-option label="Sponsored Products" value="sponsoredProducts" />
          <el-option label="Sponsored Brands" value="sponsoredBrands" />
        </el-select>
      </div>
      <div class="right">
        <el-button :icon="Refresh" circle @click="fetchCampaigns" />
        <el-button :icon="Download" circle />
        <el-button type="primary">新建广告活动</el-button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-container">
      <el-table 
        :data="campaigns" 
        style="width: 100%" 
        v-loading="loading"
        size="small"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
      >
        <el-table-column prop="state" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStateColor(row.state)" size="small" effect="dark" class="state-tag">
              {{ row.state === 'enabled' ? 'ON' : 'OFF' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="广告活动名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="campaign-name">{{ row.name }}</div>
            <div class="campaign-meta">
              <span class="type-badge">{{ row.campaign_type === 'sponsoredProducts' ? 'SP' : 'SB' }}</span>
              <span class="targeting-badge">{{ row.targeting_type }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="daily_budget" label="预算" width="100" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.daily_budget) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="impressions" label="曝光" width="100" align="right" sortable>
          <template #default="{ row }">
            {{ formatNumber(row.impressions) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="clicks" label="点击" width="90" align="right" sortable>
          <template #default="{ row }">
            {{ formatNumber(row.clicks) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="ctr" label="CTR" width="90" align="right" sortable>
          <template #default="{ row }">
            {{ formatPercent(row.ctr) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="spend" label="花费" width="110" align="right" sortable>
          <template #default="{ row }">
            <span class="font-medium">{{ formatCurrency(row.spend) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="cpc" label="CPC" width="90" align="right" sortable>
          <template #default="{ row }">
            {{ formatCurrency(row.cpc) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="sales" label="销售额" width="110" align="right" sortable>
          <template #default="{ row }">
            <span class="font-medium">{{ formatCurrency(row.sales) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="acos" label="ACOS" width="100" align="right" sortable>
          <template #default="{ row }">
            <span :class="{ 'text-red': row.acos > 30, 'text-green': row.acos <= 30 && row.acos > 0 }">
              {{ formatPercent(row.acos) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="roas" label="ROAS" width="90" align="right" sortable>
          <template #default="{ row }">
            {{ row.roas.toFixed(2) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="orders" label="订单" width="90" align="right" sortable />
        
        <el-table-column prop="cvr" label="转化率" width="90" align="right" sortable>
          <template #default="{ row }">
            {{ formatPercent(row.cvr) }}
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.campaign-manager {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.summary-card {
  background: var(--bg-primary);
  border-radius: 8px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  
  .label {
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }
  
  .value {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
  }
  
  .trend {
    font-size: 12px;
    color: var(--text-secondary);
    
    &.up { color: var(--success-color); }
    &.down { color: var(--danger-color); }
  }
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-primary);
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  
  .left {
    display: flex;
    gap: 12px;
    align-items: center;
    
    .search-input {
      width: 240px;
    }
    
    .filter-select {
      width: 140px;
    }
  }
  
  .right {
    display: flex;
    gap: 8px;
  }
}

.table-container {
  flex: 1;
  background: var(--bg-primary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  
  :deep(.el-table) {
    flex: 1;
    
    th {
      font-weight: 600;
    }
  }
}

.campaign-name {
  font-weight: 500;
  color: var(--primary-color);
  cursor: pointer;
  margin-bottom: 4px;
  
  &:hover {
    text-decoration: underline;
  }
}

.campaign-meta {
  display: flex;
  gap: 6px;
  
  span {
    font-size: 10px;
    padding: 1px 4px;
    border-radius: 2px;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
  }
}

.state-tag {
  width: 36px;
  justify-content: center;
}

.text-red { color: #f56c6c; }
.text-green { color: #67c23a; }
.font-medium { font-weight: 500; }

.pagination-wrapper {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
}
</style>
