<template>
  <div class="import-page">
    <!-- 页面头部 -->
    <div class="page-header hover-card">
      <div class="flex justify-between items-center">
        <div class="header-title">
          <h2 class="text-lg font-bold my-0">导入批次</h2>
          <span class="text-gray-400 text-sm ml-2">管理和监控数据导入任务</span>
        </div>
        <div class="flex gap-3">
          <el-button :icon="Refresh" circle @click="fetchBatches" :loading="loading" class="action-btn" />
          <el-button type="primary" :icon="Plus" @click="importDialogVisible = true" class="action-btn shadow-btn">
            新建导入
          </el-button>
          <el-button type="primary" plain :icon="MagicStick" @click="mcpDialogVisible = true" class="action-btn">
            Sorftime API 导入
          </el-button>
        </div>
      </div>
    </div>

    <!-- 批次列表表格 -->
    <BatchTable 
      :batches="batches" 
      :loading="loading" 
    />

    <!-- 分页 -->
    <div class="pager-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 导入文件对话框 -->
    <ImportDialog 
      v-model:visible="importDialogVisible"
      @success="fetchBatches"
    />

    <!-- Sorftime API 导入对话框 -->
    <SorftimeImportDialog 
      v-model:visible="mcpDialogVisible"
      @success="fetchBatches"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Refresh, Plus, MagicStick } from '@element-plus/icons-vue'
import { useImportList } from './composables/useImportList'
import BatchTable from './components/BatchTable.vue'
import ImportDialog from './components/ImportDialog.vue'
import SorftimeImportDialog from './components/SorftimeImportDialog.vue'

const {
  loading,
  batches,
  currentPage,
  pageSize,
  total,
  fetchBatches,
  handleCurrentChange,
  handleSizeChange
} = useImportList()

const importDialogVisible = ref(false)
const mcpDialogVisible = ref(false)
</script>

<style scoped lang="scss">
.import-page {
  height: calc(100vh - 84px);
  display: flex;
  flex-direction: column;
  padding: 24px;
  box-sizing: border-box;
  background-color: var(--bg-secondary);
  animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  background: #fff;
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
  flex-shrink: 0;
  border: 1px solid rgba(0,0,0,0.02);
}

.header-title {
  display: flex;
  align-items: baseline;
}

.hover-card {
  transition: all 0.3s ease;
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
}

.action-btn {
  transition: all 0.2s;
  &:hover {
    transform: translateY(-1px);
  }
}

.shadow-btn {
  box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.3);
  &:hover {
    box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.4);
  }
}

.pager-container {
  background: #fff;
  padding: 8px 16px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}
</style>
