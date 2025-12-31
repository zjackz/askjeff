<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MatrixView from './MatrixView.vue'
import OverviewView from './OverviewView.vue'
import ActionsView from './ActionsView.vue'
import SyncStatus from './components/SyncStatus.vue'
import StoreSelector from './components/StoreSelector.vue'
import { Shop, Calendar } from '@element-plus/icons-vue'

interface Store {
  id: string
  store_name: string
  marketplace_name: string
}

const currentStore = ref<Store | null>(null)
const activeTab = ref('overview')

import { ElMessage } from 'element-plus'

const handleStoreSelected = (store: Store) => {
  currentStore.value = store
}
</script>

<template>
  <div class="ads-analysis-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="title">广告决策中台</h1>
        <p class="subtitle">Ads Decision Middle Platform</p>
      </div>
      <div class="header-right">
        <StoreSelector @store-selected="handleStoreSelected" />
        <div class="date-picker-wrapper">
          <el-icon class="calendar-icon"><Calendar /></el-icon>
          <el-date-picker
            type="daterange"
            range-separator="-"
            start-placeholder="开始"
            end-placeholder="结束"
            size="default"
            class="custom-date-picker"
          />
        </div>
      </div>
    </div>

    <!-- Tabs Navigation -->
    <div class="tabs-nav">
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'overview' }"
        @click="activeTab = 'overview'"
      >
        全店概览
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'matrix' }"
        @click="activeTab = 'matrix'"
      >
        表现矩阵
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'actions' }"
        @click="activeTab = 'actions'"
      >
        智能决策
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'sync' }"
        @click="activeTab = 'sync'"
      >
        数据同步
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="tab-content">
      <OverviewView v-if="activeTab === 'overview'" :store-id="currentStore?.id" />
      <MatrixView v-if="activeTab === 'matrix'" :store-id="currentStore?.id" />
      <ActionsView v-if="activeTab === 'actions'" :store-id="currentStore?.id" />
      <SyncStatus v-if="activeTab === 'sync'" :store-id="currentStore?.id" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.ads-analysis-container {
  height: calc(100vh - 64px); // 减去顶部导航高度
  display: flex;
  flex-direction: column;
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  overflow: hidden;
  font-family: var(--font-family-base);
}

.page-header {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  z-index: 10;
}

.title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.subtitle {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.header-right {
  display: flex;
  gap: 16px;
  align-items: center;
}

.date-picker-wrapper {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 0 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;

  &:hover {
    border-color: var(--primary-color);
  }
}

.calendar-icon {
  color: var(--primary-color);
}

.tabs-nav {
  display: flex;
  padding: 0 24px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.tab-item {
  padding: 16px 24px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
  position: relative;

  &:hover {
    color: var(--primary-color);
  }

  &.active {
    color: var(--primary-color);
    
    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 24px;
      right: 24px;
      height: 3px;
      background: var(--primary-color);
      border-radius: 3px 3px 0 0;
      box-shadow: 0 -2px 10px rgba(102, 126, 234, 0.3);
    }
  }
}

.tab-content {
  flex: 1;
  min-height: 0;
  padding: 24px;
  overflow-y: auto;
  background: var(--bg-secondary);
}

:deep(.custom-date-picker) {
  border: none !important;
  background: transparent !important;
  
  .el-range-input {
    background: transparent !important;
    color: var(--text-primary) !important;
  }
  
  .el-range-separator {
    color: var(--text-secondary) !important;
  }
}
</style>
