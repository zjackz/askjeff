<template>
  <div class="table-container hover-card">
    <el-table 
      :data="batches" 
      height="100%" 
      v-loading="loading" 
      class="custom-table"
      border
    >
      <el-table-column label="批次 ID" width="80">
        <template #default="{ row }">
          <span class="font-mono text-gray-500">#{{ row.id }}</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <el-icon class="text-gray-400"><Document /></el-icon>
              <a 
                class="font-medium truncate hover:text-primary cursor-pointer no-underline text-gray-700" 
                :title="row.filename"
                @click.prevent="downloadFile(row)"
              >
                {{ row.filename }}
              </a>
            </div>
            <div class="flex items-center gap-2 pl-6">
              <span class="text-xs text-gray-400" v-if="row.sheetName">
                Sheet: {{ row.sheetName }}
              </span>
              <el-tag v-if="row.importMetadata" size="small" type="warning" effect="plain" class="scale-90 origin-left">
                {{ row.importMetadata.input_type || 'API' }}: {{ row.importMetadata.input_value }}
              </el-tag>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="createdBy" label="导入人" width="100" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="flex items-center gap-1 text-gray-600">
            <el-icon><User /></el-icon>
            <span class="text-xs">{{ row.createdBy || '管理员' }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="createdAt" label="导入时间" width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="text-xs text-gray-500">{{ formatDate(row.createdAt) }}</span>
        </template>
      </el-table-column>

      <el-table-column label="导入进度" width="220">
        <template #default="{ row }">
          <div class="flex flex-col gap-1">
            <div class="flex justify-between text-xs mb-1">
              <span :class="getStatusColor(row.status)">{{ getStatusLabel(row.status) }}</span>
              <span class="text-gray-400">{{ row.successRows }}/{{ row.totalRows }}</span>
            </div>
            <el-progress 
              :percentage="calculateProgress(row)" 
              :status="getProgressStatus(row.status)"
              :stroke-width="6"
              :show-text="false"
            />
            <div class="flex justify-between text-xs text-gray-400 mt-1" v-if="row.failedRows > 0">
              <span>失败: {{ row.failedRows }}</span>
              <el-button 
                link 
                type="danger" 
                size="small" 
                class="!p-0 !h-auto text-xs"
                @click="downloadFailures(row)"
              >
                下载失败记录
              </el-button>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="AI 分析" width="140">
        <template #default="{ row }">
          <div v-if="row.aiStatus === 'processing'" class="flex items-center gap-2 text-primary">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span class="text-xs">分析中...</span>
          </div>
          <div v-else-if="row.aiStatus === 'completed'" class="flex flex-col gap-1">
            <el-tag type="success" size="small" effect="plain">分析完成</el-tag>
            <span class="text-xs text-gray-400" v-if="row.aiSummary">
              {{ row.aiSummary.success || 0 }} 条特征
            </span>
          </div>
          <div v-else-if="row.aiStatus === 'failed'" class="text-danger text-xs flex items-center gap-1">
            <el-icon><Warning /></el-icon>
            分析失败
          </div>
          <div v-else class="text-gray-400 text-xs">-</div>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <div class="flex gap-2 items-center justify-center">
            <el-button 
              type="primary" 
              @click="navigateToChat(row)"
            >
              查看详情
            </el-button>
            <el-button 
              type="warning" 
              plain
              @click="openExtractionDialog(row)"
            >
              <el-icon class="mr-1"><MagicStick /></el-icon>
              AI 提取
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { Document, User, Loading, Warning, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { API_BASE } from '@/utils/http'
import { useRouter } from 'vue-router'
import type { BatchRow } from '../types'

defineProps<{
  batches: BatchRow[]
  loading: boolean
}>()

const router = useRouter()

const formatDate = (val?: string) => {
  if (!val) return '-'
  const date = new Date(val)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getStatusColor = (status: string) => {
  const map: Record<string, string> = {
    completed: 'text-success',
    succeeded: 'text-success',
    failed: 'text-danger',
    processing: 'text-primary',
    pending: 'text-gray-400'
  }
  return map[status.toLowerCase()] || 'text-gray-400'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    completed: '已完成',
    succeeded: '已完成',
    failed: '失败',
    processing: '处理中',
    pending: '等待中'
  }
  return map[status.toLowerCase()] || status
}

const getProgressStatus = (status: string) => {
  if (status === 'failed') return 'exception'
  if (status === 'completed' || status === 'succeeded') return 'success'
  return ''
}

const calculateProgress = (row: BatchRow) => {
  if (row.status === 'completed' || row.status === 'succeeded') return 100
  if (row.status === 'pending') return 0
  const total = row.totalRows || 0
  if (total === 0) {
    const processed = (row.successRows || 0) + (row.failedRows || 0)
    return processed > 0 ? 50 : 0
  }
  const processed = (row.successRows || 0) + (row.failedRows || 0)
  return Math.min(Math.round((processed / total) * 100), 100)
}

const downloadFailures = (row: BatchRow) => {
  if (row.failureSummary?.failed_rows_path) {
    const baseUrl = API_BASE.startsWith('http') ? API_BASE : window.location.origin + API_BASE
    const downloadUrl = `${baseUrl}/exports/download?path=${encodeURIComponent(row.failureSummary.failed_rows_path)}`
    window.open(downloadUrl, '_blank')
  } else {
    ElMessage.warning('暂无失败记录文件')
  }
}

const downloadFile = (row: BatchRow) => {
  if (!row.filePath) {
    ElMessage.warning('文件路径不存在')
    return
  }
  const baseUrl = API_BASE.startsWith('http') ? API_BASE : window.location.origin + API_BASE
  const downloadUrl = `${baseUrl}/exports/download?path=${encodeURIComponent(row.filePath)}`
  window.open(downloadUrl, '_blank')
}

const navigateToChat = (row: BatchRow) => {
  router.push({
    path: '/product',
    query: { batchId: row.id }
  })
}

const openExtractionDialog = (row: BatchRow) => {
  router.push(`/extraction/${row.id}`)
}
</script>

<style scoped lang="scss">
.table-container {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  padding: 0;
  border: none;
}

.hover-card {
  transition: all 0.3s ease;
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
}

.custom-table {
  :deep(th) {
    background: #f9fafb;
    font-weight: 600;
    color: var(--text-primary);
    height: 56px;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  :deep(td) {
    padding: 16px 0;
    height: 72px;
  }

  :deep(.el-table__inner-wrapper::before) {
    display: none;
  }
}

.text-success { color: var(--success-color); }
.text-danger { color: var(--danger-color); }
.text-primary { color: var(--primary-color); }
</style>
