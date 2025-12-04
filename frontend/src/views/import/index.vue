<template>
  <div class="import-page">
    <div class="page-header">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-bold my-0">导入批次</h2>
        <div class="flex gap-2">
          <el-button :icon="Refresh" circle @click="fetchBatches" :loading="loading" />
          <el-button type="primary" :icon="Plus" @click="importDialogVisible = true">
            新建导入
          </el-button>
        </div>
      </div>
    </div>

    <div class="table-container">
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
                <span class="font-medium truncate" :title="row.filename">{{ row.filename }}</span>
              </div>
              <div class="flex items-center gap-2 pl-6">
                <el-tag size="small" type="info" effect="plain" class="scale-90 origin-left">
                  {{ getStrategyLabel(row.importStrategy) }}
                </el-tag>
                <span class="text-xs text-gray-400" v-if="row.sheetName">
                  Sheet: {{ row.sheetName }}
                </span>
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
            <div v-else-if="row.ai_status === 'failed'" class="text-danger text-xs flex items-center gap-1">
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
    <el-dialog v-model="importDialogVisible" title="导入数据" width="500px">
      <el-form label-position="top" class="upload-form">
        <el-form-item label="导入策略">
          <el-select v-model="strategy" class="w-full" size="large">
            <el-option label="仅追加 (Append)" value="append">
              <div class="flex items-center justify-between">
                <span>仅追加</span>
                <el-tag size="small" type="info">Append</el-tag>
              </div>
            </el-option>
            <el-option label="覆盖批次 (Overwrite)" value="overwrite">
              <div class="flex items-center justify-between">
                <span>覆盖批次</span>
                <el-tag size="small" type="warning">Overwrite</el-tag>
              </div>
            </el-option>
            <el-option label="仅更新 (Update Only)" value="update_only">
              <div class="flex items-center justify-between">
                <span>仅更新</span>
                <el-tag size="small" type="success">Update</el-tag>
              </div>
            </el-option>
          </el-select>
          <div class="form-tip">选择数据导入的处理方式</div>
        </el-form-item>
        
        <el-form-item label="选择文件">
          <el-upload
            class="upload-area"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".csv,.xlsx"
            v-model:file-list="fileList"
          >
            <div class="upload-content">
              <div class="upload-icon-wrapper">
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
              </div>
              <div class="upload-text">
                <h4>点击或拖拽文件到此处</h4>
                <p>支持 .csv 或 .xlsx 文件，最大 50MB</p>
              </div>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            :loading="submitting" 
            @click="submit"
            :disabled="fileList.length === 0"
          >
            开始导入
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, Document, Refresh, User, MagicStick, Plus, Loading, Warning } from '@element-plus/icons-vue'
import { ElMessage, type UploadUserFile, type UploadFile } from 'element-plus'
import { useIntervalFn } from '@vueuse/core'
import { http, API_BASE } from '@/utils/http'

const router = useRouter()
const strategy = ref('append')
const submitting = ref(false)
const loading = ref(false)
const fileList = ref<UploadUserFile[]>([])

const importDialogVisible = ref(false)


// Pagination
const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)

interface BatchRow {
  id: number
  filename: string
  sheetName?: string
  importStrategy?: string
  status: string
  aiStatus?: string
  aiSummary?: { total: number, success: number, failed: number }
  successRows?: number
  failedRows?: number
  totalRows?: number
  createdAt?: string
  createdBy?: string
  startedAt?: string
  finishedAt?: string
  duration?: string // 前端计算
  failureSummary?: { failed_rows_path: string, total_failed: number }
}

const batches = ref<BatchRow[]>([])

// 自动轮询：每 5 秒刷新一次列表
const { pause, resume, isActive: isPolling } = useIntervalFn(() => {
  fetchBatches(true)
}, 5000)

const handleFileChange = (uploadFile: UploadFile) => {
  // 文件大小验证 (50MB = 50 * 1024 * 1024 bytes)
  const maxSize = 50 * 1024 * 1024
  if (uploadFile.size && uploadFile.size > maxSize) {
    ElMessage.error('文件大小超过 50MB 限制,请压缩后重试')
    fileList.value = []
    return
  }
  
  // 文件格式验证
  const fileName = uploadFile.name || ''
  const validExtensions = ['.csv', '.xlsx', '.xls']
  const hasValidExtension = validExtensions.some(ext => fileName.toLowerCase().endsWith(ext))
  
  if (!hasValidExtension) {
    ElMessage.error('文件格式不正确,仅支持 CSV 和 XLSX 格式')
    fileList.value = []
    return
  }
  
  fileList.value = [uploadFile] // 限制单文件
}

const handleFileRemove = () => {
  fileList.value = []
}

const submit = async () => {
  if (fileList.value.length === 0) return
  
  const file = fileList.value[0]?.raw
  if (!file) return

  const form = new FormData()
  form.append('file', file)
  form.append('importStrategy', strategy.value)
  
  submitting.value = true
  try {
    await http.post('/imports', form)
    ElMessage.success('导入任务已提交，正在处理...')
    fileList.value = [] // 清空选择
    importDialogVisible.value = false // 关闭弹窗
    currentPage.value = 1 // 重置到第一页
    await fetchBatches()
    resume() // 确保开启轮询
  } catch (err) {
    // 全局错误处理已接管
  } finally {
    submitting.value = false
  }
}

const fetchBatches = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const { data } = await http.get('/imports', {
      params: {
        page: currentPage.value,
        pageSize: pageSize.value
      }
    })
    batches.value = (data.items || []).map((item: BatchRow) => ({
      ...item,
      duration: calculateDuration(item.startedAt, item.finishedAt)
    }))
    total.value = data.total || 0
    
    const hasActiveTasks = batches.value.some(b => 
      (b.status && ['pending', 'processing'].includes(b.status.toLowerCase())) ||
      (b.aiStatus && ['pending', 'processing'].includes(b.aiStatus.toLowerCase()))
    )
    if (!hasActiveTasks && isPolling.value) {
      // pause() 
    } else if (hasActiveTasks && !isPolling.value) {
      resume()
    }
  } catch (err) {
    pause()
  } finally {
    if (!silent) loading.value = false
  }
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchBatches()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchBatches()
}




const getStrategyLabel = (strategy?: string) => {
  const map: Record<string, string> = {
    append: '追加',
    overwrite: '覆盖',
    update_only: '仅更新'
  }
  return map[strategy?.toLowerCase() || ''] || '未知'
}

const calculateDuration = (start?: string, end?: string) => {
  if (!start || !end) return null
  const diff = new Date(end).getTime() - new Date(start).getTime()
  if (diff < 1000) return '< 1s'
  return `${(diff / 1000).toFixed(1)}s`
}

const calculateProgress = (row: BatchRow) => {
  if (row.status === 'completed' || row.status === 'succeeded') return 100
  if (row.status === 'pending') return 0
  
  const total = row.totalRows || 0
  if (total === 0) {
    // 如果总行数为 0 但有成功或失败记录，说明可能是后端未正确更新 totalRows，或者正在处理中
    const processed = (row.successRows || 0) + (row.failedRows || 0)
    return processed > 0 ? 50 : 0 // 临时显示 50%
  }
  
  const processed = (row.successRows || 0) + (row.failedRows || 0)
  return Math.min(Math.round((processed / total) * 100), 100)
}

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

const downloadFailures = (row: BatchRow) => {
  if (row.failureSummary?.failed_rows_path) {
    window.open(`${API_BASE}/api/exports/download?path=${row.failureSummary.failed_rows_path}`, '_blank')
  } else {
    ElMessage.warning('暂无失败记录文件')
  }
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

onMounted(() => {
  fetchBatches()
})
</script>

<style scoped lang="scss">
.import-page {
  height: calc(100vh - 84px);
  display: flex;
  flex-direction: column;
  padding: 16px;
  box-sizing: border-box;
  background-color: var(--bg-secondary);
}

.page-header {
  background: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 12px;
  flex-shrink: 0;
}

.table-container {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  padding: 1px;
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

.text-primary {
  color: var(--primary-color);
}

.text-danger {
  color: var(--danger-color);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px; // Add padding back to header content if needed, or rely on el-card header padding
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.bg-primary-light { background: rgba(102, 126, 234, 0.1); color: var(--primary-color); }
  &.bg-success-light { background: rgba(16, 185, 129, 0.1); color: var(--success-color); }
}

.upload-area {
  :deep(.el-upload) {
    width: 100%;
  }
  
  :deep(.el-upload-dragger) {
    width: 100%;
    height: 200px;
    border: 2px dashed var(--border-color);
    border-radius: var(--radius-lg);
    background: var(--bg-secondary);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      border-color: var(--primary-color);
      background: rgba(102, 126, 234, 0.05);
      
      .upload-icon {
        transform: scale(1.1);
        color: var(--primary-color);
      }
    }
  }
}

.upload-content {
  text-align: center;
}

.upload-icon-wrapper {
  margin-bottom: 16px;
}

.upload-icon {
  font-size: 48px;
  color: var(--text-tertiary);
  transition: all 0.3s ease;
}

.upload-text {
  h4 {
    margin: 0 0 8px;
    font-size: 16px;
    color: var(--text-primary);
  }
  
  p {
    margin: 0;
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.form-tip {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.submit-btn {
  width: 100%;
  margin-top: 24px;
  height: 48px;
  font-size: 16px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-primary);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
}

.polling-status {
  font-size: 12px;
  color: var(--success-color);
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(16, 185, 129, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.custom-table {
  :deep(th) {
    background: transparent;
    font-weight: 600;
    color: var(--text-secondary);
  }
  
  :deep(td) {
    padding: 16px 0;
  }
}

.text-success { color: var(--success-color); }
.text-danger { color: var(--danger-color); }

// 动画
.slide-in {
  animation: slideInRight 0.5s ease-out backwards;
  animation-delay: var(--delay, 0s);
}
</style>
