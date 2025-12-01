<template>
  <div class="import-page fade-in">
    <!-- 页面标题 -->
    <!-- 页面标题 -->
    <div class="page-header mb-6 flex justify-between items-center" style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 class="text-2xl font-bold">文件导入</h1>
        <p class="text-gray-500">上传并处理您的产品数据文件</p>
      </div>
      <el-button type="primary" size="large" @click="importDialogVisible = true">
        <el-icon class="mr-2"><Upload /></el-icon>
        导入数据
      </el-button>
    </div>

    <div class="main-content">
      <!-- 批次列表 -->
      <el-card class="glass-card">
        <template #header>
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <div class="icon-box bg-success-light">
                <el-icon><List /></el-icon>
              </div>
              <span class="font-bold text-lg">最近批次</span>
              <span v-if="isPolling" class="polling-status ml-2">
                <span class="pulse-dot"></span>
                实时更新中
              </span>
            </div>
            <div class="flex gap-2">
              <el-button :icon="Refresh" circle @click="fetchBatches" :loading="loading" />
            </div>
          </div>
        </template>

        <el-table :data="batches" style="width: 100%" v-loading="loading" class="custom-table">
          <el-table-column prop="filename" label="文件名" min-width="200">
            <template #default="{ row }">
              <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2">
                  <el-icon class="text-gray-400"><Document /></el-icon>
                  <span class="font-medium truncate" :title="row.filename">{{ row.filename }}</span>
                </div>
                <div class="flex items-center gap-2 pl-6">
                  <el-tag size="small" type="info" effect="plain" class="scale-90 origin-left">
                    {{ getStrategyLabel(row.import_strategy) }}
                  </el-tag>
                  <span class="text-xs text-gray-400" v-if="row.sheet_name">
                    Sheet: {{ row.sheet_name }}
                  </span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="created_by" label="导入人" width="100">
            <template #default="{ row }">
              <div class="flex items-center gap-1 text-gray-600">
                <el-icon><User /></el-icon>
                <span>{{ row.created_by || '系统' }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="导入状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" effect="light" round size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 新增：AI 状态列 -->
          <el-table-column label="AI 提取" width="140">
            <template #default="{ row }">
              <div v-if="!row.ai_status || row.ai_status === 'none'" class="text-gray-400 text-xs">
                -
              </div>
              <div v-else class="flex flex-col gap-1">
                <el-tag :type="getStatusType(row.ai_status)" effect="plain" round size="small">
                  {{ row.ai_status }}
                </el-tag>
                <div v-if="row.ai_summary" class="text-xs text-gray-500 scale-90 origin-left">
                  {{ row.ai_summary.success }}/{{ row.ai_summary.total }}
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="导入进度" width="180">
            <template #default="{ row }">
              <div class="flex flex-col gap-1">
                <div class="flex justify-between text-xs text-gray-500">
                  <span class="font-medium">
                    <span class="text-success">{{ row.success_rows || 0 }}</span>
                    <span class="mx-1">/</span>
                    <span>{{ row.total_rows || 0 }}</span>
                  </span>
                  <span class="text-danger" v-if="(row.failed_rows || 0) > 0">{{ row.failed_rows }} 失败</span>
                </div>
                <el-progress 
                  :percentage="calculateProgress(row)" 
                  :status="(row.failed_rows || 0) > 0 ? 'exception' : (row.status === 'completed' ? 'success' : '')"
                  :show-text="false"
                  :stroke-width="4"
                />
                <div class="text-xs text-gray-400 text-right" v-if="row.duration">
                  耗时: {{ row.duration }}
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="created_at" label="时间" width="160">
            <template #default="{ row }">
              <div class="flex flex-col text-xs text-gray-500">
                <span>{{ formatTime(row.created_at).split(' ')[0] }}</span>
                <span class="text-gray-400">{{ formatTime(row.created_at).split(' ')[1] }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <div class="flex flex-col gap-2">
                <el-button 
                  link 
                  type="primary" 
                  size="small" 
                  @click="viewBatchDetail(row)"
                >
                  查看详情
                </el-button>
                <el-button 
                  link 
                  type="warning" 
                  size="small" 
                  @click="navigateToExtraction(row)"
                >
                  <el-icon class="mr-1"><MagicStick /></el-icon>
                  AI 提取
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="mt-4 flex justify-end">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
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
import { Upload, UploadFilled, VideoPlay, List, Document, Refresh, User, MagicStick } from '@element-plus/icons-vue'
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
const pageSize = ref(20)
const total = ref(0)

interface BatchRow {
  id: string
  filename: string
  sheet_name?: string
  import_strategy?: string
  status: string
  ai_status?: string
  ai_summary?: { total: number, success: number, failed: number }
  success_rows?: number
  failed_rows?: number
  total_rows?: number
  created_at?: string
  created_by?: string
  started_at?: string
  finished_at?: string
  duration?: string // 前端计算
}

const batches = ref<BatchRow[]>([])

// 自动轮询：每 5 秒刷新一次列表
const { pause, resume, isActive: isPolling } = useIntervalFn(() => {
  fetchBatches(true)
}, 5000)

const handleFileChange = (uploadFile: UploadFile) => {
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
    await http.post(`${API_BASE}/imports`, form)
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
    const { data } = await http.get(`${API_BASE}/imports`, {
      params: {
        page: currentPage.value,
        pageSize: pageSize.value
      }
    })
    batches.value = (data.items || []).map((item: any) => ({
      ...item,
      duration: calculateDuration(item.started_at, item.finished_at)
    }))
    total.value = data.total || 0
    
    const hasActiveTasks = batches.value.some(b => 
      (b.status && ['pending', 'processing'].includes(b.status.toLowerCase())) ||
      (b.ai_status && ['pending', 'processing'].includes(b.ai_status.toLowerCase()))
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

const handlePageChange = (val: number) => {
  currentPage.value = val
  fetchBatches()
}


const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    completed: 'success',
    succeeded: 'success',
    failed: 'danger',
    processing: 'primary',
    pending: 'info'
  }
  return map[status.toLowerCase()] || 'info'
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
  
  const total = row.total_rows || 0
  if (total === 0) {
    // 如果总行数为 0 但有成功或失败记录，说明可能是后端未正确更新 total_rows，或者正在处理中
    const processed = (row.success_rows || 0) + (row.failed_rows || 0)
    return processed > 0 ? 50 : 0 // 临时显示 50%
  }
  
  const processed = (row.success_rows || 0) + (row.failed_rows || 0)
  return Math.min(Math.round((processed / total) * 100), 100)
}

const formatTime = (val?: string) => {
  if (!val) return '-'
  const date = new Date(val)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const viewBatchDetail = (row: BatchRow) => {
  router.push({
    path: '/chat',
    query: { batchId: row.id }
  })
}

const navigateToExtraction = (row: BatchRow) => {
  router.push(`/extraction/${row.id}`)
}

onMounted(() => {
  fetchBatches()
})
</script>

<style scoped lang="scss">
.import-page {
  max-width: 1400px;
  margin: 0 auto;
}

.glass-card {
  padding: 0; // Ensure header goes edge-to-edge
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
