<template>
  <div class="import-page">
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
                <!-- <el-tag size="small" type="info" effect="plain" class="scale-90 origin-left">
                  {{ getStrategyLabel(row.importStrategy) }}
                </el-tag> -->
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

    <!-- Sorftime API 导入对话框 -->
    <el-dialog 
      v-model="mcpDialogVisible" 
      title="" 
      width="900px" 
      destroy-on-close 
      class="premium-dialog-wide"
      :show-close="true"
      align-center
    >
      <div class="mcp-layout">
        <!-- 左侧：操作区 -->
        <div class="mcp-left-panel">
          <!-- 标题 -->
          <div class="mcp-header">
            <div class="mcp-icon-wrapper">
              <el-icon><MagicStick /></el-icon>
            </div>
            <div class="mcp-title-group">
              <h2>一键抓取</h2>
              <p>只需粘贴 Amazon 商品链接或 ASIN，AI 将自动识别并提取 Top 100 数据。</p>
            </div>
          </div>

          <!-- 表单 -->
          <div class="mcp-form">
            <div class="form-group">
              <label>输入内容</label>
              <div class="input-wrapper">
                <el-input
                  v-model="mcpForm.input"
                  type="textarea"
                  :rows="6"
                  resize="none"
                  class="premium-textarea"
                  placeholder="在此粘贴链接或 ASIN..."
                  @input="handleInputPreview"
                />
                <el-icon class="input-icon"><Link /></el-icon>
              </div>
            </div>

            <div class="options-box">
              <div class="option-item">
                <div class="label-with-icon">
                  <span>抓取数量</span>
                  <el-tooltip content="限制获取详情的产品数量" placement="top">
                    <el-icon><InfoFilled /></el-icon>
                  </el-tooltip>
                </div>
                <el-input-number v-model="mcpForm.limit" :min="1" :max="500" size="small" controls-position="right" />
              </div>
              <div class="option-item">
                <span>测试模式 (Mock)</span>
                <el-switch v-model="mcpForm.test_mode" size="small" />
              </div>
            </div>
          </div>

          <!-- 底部按钮 -->
          <div class="mcp-footer">
            <el-button 
              type="primary" 
              class="start-btn"
              :loading="mcpSubmitting"
              @click="handleMcpSubmit"
              :disabled="!mcpForm.input || (previewData && !previewData.valid)"
            >
              {{ mcpSubmitting ? '正在抓取...' : '开始抓取' }}
            </el-button>
          </div>
        </div>

        <!-- 右侧：展示区 -->
        <div class="mcp-right-panel">
          <div class="panel-bg"></div>

          <div class="panel-header">
            <h3>
              <el-icon><DataAnalysis /></el-icon>
              实时预览 & 状态
            </h3>
            <el-tag v-if="previewLoading" size="small" type="warning" effect="light">
              <el-icon class="is-loading"><Loading /></el-icon>
              AI 识别中...
            </el-tag>
          </div>

          <div class="panel-content">
            <!-- 空状态 -->
            <div v-if="!previewData && !importProgress.visible" class="empty-state">
              <div class="empty-icon">
                <el-icon><Document /></el-icon>
              </div>
              <p class="main-text">等待输入...</p>
              <p class="sub-text">在左侧输入内容以开始预览</p>
            </div>

            <!-- 预览卡片 -->
            <div v-else-if="previewData && !importProgress.visible" class="preview-card">
              <div class="status-bar" :class="{ valid: previewData.valid }"></div>
              <div class="card-body">
                <div v-if="previewData.valid" class="valid-content">
                  <div class="product-image">
                     <el-image v-if="previewData.image" :src="previewData.image" fit="contain">
                       <template #error><el-icon><Picture /></el-icon></template>
                     </el-image>
                     <el-icon v-else><Picture /></el-icon>
                  </div>
                  <div class="product-info">
                    <div class="tags-row">
                      <el-tag size="small" effect="dark" :type="previewData.type === 'asin' ? 'warning' : 'primary'">
                        {{ previewData.type === 'asin' ? 'ASIN' : 'CATEGORY' }}
                      </el-tag>
                      <span class="id-text">{{ previewData.value }}</span>
                    </div>
                    <div class="product-title" :title="previewData.title">
                      {{ previewData.title || '暂无标题' }}
                    </div>
                    <div v-if="previewData.category_id" class="category-info">
                      <el-icon><Menu /></el-icon>
                      <span>类目 ID: <b>{{ previewData.category_id }}</b></span>
                    </div>
                  </div>
                </div>
                
                <div v-else class="error-content">
                  <div class="error-icon"><el-icon><Warning /></el-icon></div>
                  <div>
                    <div class="error-title">无法识别内容</div>
                    <div class="error-desc">{{ previewData.error || '请输入有效的 Amazon 链接或 ASIN' }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 进度状态 -->
            <div v-if="importProgress.visible" class="progress-state">
              <div class="progress-card">
                <el-progress 
                  type="dashboard" 
                  :percentage="importProgress.percentage" 
                  :status="getProgressStatus(importProgress.status)"
                  :width="100"
                  :stroke-width="8"
                >
                  <template #default="{ percentage }">
                    <div class="progress-label">
                      <span class="percentage">{{ percentage }}%</span>
                      <span class="text">Progress</span>
                    </div>
                  </template>
                </el-progress>
                
                <h4>{{ importProgress.message }}</h4>
                <p>{{ importProgress.detail }}</p>
                
                <div v-if="importProgress.status === 'failed'" class="action-row">
                  <el-button size="small" @click="importProgress.visible = false">返回修改</el-button>
                </div>
                <div v-if="importProgress.status === 'succeeded'" class="action-row">
                  <el-button type="success" size="small" plain @click="mcpDialogVisible = false">完成并查看</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, Document, Refresh, User, MagicStick, Plus, Loading, Warning, InfoFilled, CircleCheckFilled, Picture, Menu, DataAnalysis, Link } from '@element-plus/icons-vue'
import { ElMessage, type UploadUserFile, type UploadFile } from 'element-plus'
import { useIntervalFn, useDebounceFn } from '@vueuse/core'
import { http, API_BASE } from '@/utils/http'

const router = useRouter()
const strategy = ref('append')
const submitting = ref(false)
const loading = ref(false)
const fileList = ref<UploadUserFile[]>([])

const importDialogVisible = ref(false)
const mcpDialogVisible = ref(false)
const mcpSubmitting = ref(false)
const mcpForm = ref({
  input: '',
  test_mode: false,
  limit: 5
})

const previewData = ref<any>(null)
const previewLoading = ref(false)

// 进度状态
const importProgress = ref({
  visible: false,
  status: 'idle' as 'idle' | 'processing' | 'succeeded' | 'failed',
  message: '',
  detail: '',
  percentage: 0,
  batchId: null as number | null
})

const handleInputPreview = useDebounceFn(async (val: string) => {
  if (!val.trim()) {
    previewData.value = null
    return
  }
  
  // 简单的本地预判，避免无效请求
  if (val.length < 5) return

  previewLoading.value = true
  try {
    const { data } = await http.post('/imports/preview-api', {
      input: val,
      test_mode: mcpForm.value.test_mode
    })
    previewData.value = data
  } catch (err) {
    console.error(err)
    // 不显示错误，以免打断用户输入
    previewData.value = null
  } finally {
    previewLoading.value = false
  }
}, 800)

const getTypeName = (type: string) => {
  const map: Record<string, string> = {
    'asin': '商品 (ASIN)',
    'category_id': '类目 (ID)',
    'url': '链接'
  }
  return map[type] || type
}

const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)

interface BatchRow {
  id: number
  filename: string
  filePath?: string
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
  duration?: string
  failureSummary?: { failed_rows_path: string, total_failed: number }
  importMetadata?: { input_value: string, input_type: string, test_mode: boolean }
}

const batches = ref<BatchRow[]>([])

const { pause, resume, isActive: isPolling } = useIntervalFn(() => {
  fetchBatches(true)
}, 5000)

const handleFileChange = (uploadFile: UploadFile) => {
  const maxSize = 50 * 1024 * 1024
  if (uploadFile.size && uploadFile.size > maxSize) {
    ElMessage.error('文件大小超过 50MB 限制,请压缩后重试')
    fileList.value = []
    return
  }
  const fileName = uploadFile.name || ''
  const validExtensions = ['.csv', '.xlsx', '.xls']
  const hasValidExtension = validExtensions.some(ext => fileName.toLowerCase().endsWith(ext))
  if (!hasValidExtension) {
    ElMessage.error('文件格式不正确,仅支持 CSV 和 XLSX 格式')
    fileList.value = []
    return
  }
  fileList.value = [uploadFile]
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
    fileList.value = []
    importDialogVisible.value = false
    currentPage.value = 1
    await fetchBatches()
    resume()
  } catch (err) {
  } finally {
    submitting.value = false
  }
}



const handleMcpSubmit = async () => {
  if (!mcpForm.value.input) {
    ElMessage.warning('请输入内容')
    return
  }
  
  // 重置进度
  importProgress.value = {
    visible: true,
    status: 'processing',
    message: '正在提交任务...',
    detail: '',
    percentage: 0,
    batchId: null
  }
  
  mcpSubmitting.value = true
  try {
    const payload = {
      ...mcpForm.value,
      input_type: 'auto' 
    }
    
    const { data } = await http.post('/imports/from-api', payload)
    const batchId = data.batch_id
    
    importProgress.value.batchId = batchId
    importProgress.value.message = '任务已提交，正在抓取数据...'
    importProgress.value.percentage = 10
    
    // 开始轮询状态
    pollImportStatus(batchId)
    
  } catch (err: any) {
    console.error('API import failed:', err)
    importProgress.value.status = 'failed'
    importProgress.value.message = '提交失败'
    importProgress.value.detail = err.response?.data?.detail || '未知错误'
    mcpSubmitting.value = false
  }
}

// 轮询导入状态
const pollImportStatus = async (batchId: number) => {
  const maxAttempts = 60 // 最多轮询60次 (5分钟)
  let attempts = 0
  
  const poll = async () => {
    if (attempts >= maxAttempts) {
      importProgress.value.status = 'failed'
      importProgress.value.message = '抓取超时'
      importProgress.value.detail = '请检查日志或重试'
      mcpSubmitting.value = false
      return
    }
    
    attempts++
    
    try {
      const { data } = await http.get(`/imports/${batchId}`)
      const batch = data
      
      // 更新进度
      if (batch.status === 'processing') {
        const progress = Math.min(10 + (attempts * 1.5), 90)
        importProgress.value.percentage = Math.round(progress)
        importProgress.value.message = '正在抓取数据...'
        
        // 根据 metadata 显示详细信息
        if (batch.import_metadata) {
          const meta = batch.import_metadata
          importProgress.value.detail = `输入: ${meta.input_value || ''}`
        }
        
        // 继续轮询
        setTimeout(poll, 3000)
        
      } else if (batch.status === 'succeeded') {
        importProgress.value.status = 'succeeded'
        importProgress.value.percentage = 100
        importProgress.value.message = `抓取成功！获取数据 ${batch.success_rows || 0} 条`
        importProgress.value.detail = `总计: ${batch.total_rows || 0} 条 | 成功: ${batch.success_rows || 0} 条`
        
        mcpSubmitting.value = false
        ElMessage.success('数据抓取完成')
        
        // 3秒后关闭对话框并刷新列表
        setTimeout(() => {
          mcpDialogVisible.value = false
          importProgress.value.visible = false
          fetchBatches()
        }, 3000)
        
      } else if (batch.status === 'failed') {
        importProgress.value.status = 'failed'
        importProgress.value.message = '抓取失败'
        importProgress.value.detail = batch.failure_summary?.error || '未知错误'
        mcpSubmitting.value = false
        
      } else {
        // pending 状态，继续轮询
        importProgress.value.percentage = 5
        setTimeout(poll, 3000)
      }
      
    } catch (err) {
      console.error('Poll status failed:', err)
      // 继续轮询，可能是临时网络问题
      setTimeout(poll, 3000)
    }
  }
  
  // 开始轮询
  poll()
}

// 取消导入
const handleCancelImport = () => {
  if (importProgress.value.status === 'processing') {
    return // 进行中不允许取消
  }
  mcpDialogVisible.value = false
  importProgress.value.visible = false
  mcpForm.value.input = ''
  previewData.value = null
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
    const processed = (row.successRows || 0) + (row.failedRows || 0)
    return processed > 0 ? 50 : 0
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

onMounted(() => {
  fetchBatches()
})
</script>
<style scoped lang="scss">
.import-page {
  height: calc(100vh - 84px);
  display: flex;
  flex-direction: column;
  padding: 24px; // Increase padding
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
  border-radius: 16px; // Larger radius
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px; // Increase margin
  flex-shrink: 0;
  border: 1px solid rgba(0,0,0,0.02);
}

.header-title {
  display: flex;
  align-items: baseline;
}

.table-container {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  padding: 0;
  border: none; // Remove border to avoid double border with el-table
}

// Hover card effect
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
    height: 72px; // Taller rows
  }

  :deep(.el-table__row) {
    transition: background-color 0.2s;
  }

  // Remove outer borders
  :deep(.el-table__inner-wrapper::before) {
    display: none;
  }
}

.text-success { color: var(--success-color); }
.text-danger { color: var(--danger-color); }

// 动画
.slide-in {
  animation: slideInRight 0.5s ease-out backwards;
  animation-delay: var(--delay, 0s);
}

// Premium Dialog Styles (Wide)
.premium-dialog-wide {
  :deep(.el-dialog__header) {
    display: none;
  }
  :deep(.el-dialog__body) {
    padding: 0;
  }
}

.premium-textarea {
  :deep(.el-textarea__inner) {
    padding: 12px 16px;
    border-radius: 12px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    background-color: #f9fafb;
    border-color: #e5e7eb;
    font-size: 14px;
    line-height: 1.6;
    
    &:focus {
      background-color: #fff;
      box-shadow: 0 0 0 1px var(--el-color-primary), 0 4px 12px rgba(var(--el-color-primary-rgb), 0.1);
      border-color: var(--el-color-primary);
    }
  }
}

// MCP Dialog Layout
.mcp-layout {
  display: flex;
  height: 520px;
  background: #fff;
}

.mcp-left-panel {
  width: 360px;
  padding: 32px;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  background: #fff;
  z-index: 10;
  position: relative;
}

.mcp-right-panel {
  flex: 1;
  padding: 32px;
  background: #f8fafc;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

// Left Panel Styles
.mcp-header {
  margin-bottom: 32px;
  
  .mcp-icon-wrapper {
    width: 40px;
    height: 40px;
    background: #eff6ff;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #2563eb;
    font-size: 20px;
    margin-bottom: 12px;
    display: inline-flex;
    margin-right: 12px;
    vertical-align: middle;
  }
  
  .mcp-title-group {
    display: inline-block;
    vertical-align: middle;
    
    h2 {
      font-size: 18px;
      font-weight: 700;
      color: #1f2937;
      margin: 0 0 4px 0;
    }
    
    p {
      font-size: 13px;
      color: #6b7280;
      margin: 0;
      line-height: 1.5;
    }
  }
}

.mcp-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  
  .form-group {
    label {
      font-size: 12px;
      font-weight: 700;
      color: #374151;
      margin-bottom: 8px;
      display: block;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    
    .input-wrapper {
      position: relative;
      
      .input-icon {
        position: absolute;
        bottom: 8px;
        right: 8px;
        color: #d1d5db;
        pointer-events: none;
      }
    }
  }
  
  .options-box {
    background: #f9fafb;
    border: 1px solid #f3f4f6;
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    
    .option-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 14px;
      color: #4b5563;
      
      .label-with-icon {
        display: flex;
        align-items: center;
        gap: 6px;
        
        .el-icon {
          color: #9ca3af;
          cursor: help;
        }
      }
    }
  }
}

.mcp-footer {
  margin-top: auto;
  padding-top: 24px;
  
  .start-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2);
    
    &:hover {
      box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
    }
  }
}

// Right Panel Styles
.panel-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(219, 234, 254, 0.4) 0%, rgba(243, 232, 255, 0.4) 100%);
  border-radius: 50%;
  filter: blur(60px);
  transform: translate(30%, -30%);
  pointer-events: none;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
  
  h3 {
    font-size: 14px;
    font-weight: 700;
    color: #374151;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.panel-content {
  flex: 1;
  position: relative;
  z-index: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  
  .empty-icon {
    width: 80px;
    height: 80px;
    background: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    border: 1px solid #f3f4f6;
    font-size: 32px;
    color: #e5e7eb;
  }
  
  .main-text {
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    margin: 0 0 4px 0;
  }
  
  .sub-text {
    font-size: 12px;
    margin: 0;
  }
}

.preview-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  
  .status-bar {
    height: 6px;
    width: 100%;
    background: #ef4444; // default red
    
    &.valid {
      background: #10b981; // green
    }
  }
  
  .card-body {
    padding: 20px;
  }
  
  .valid-content {
    display: flex;
    gap: 20px;
    
    .product-image {
      width: 80px;
      height: 80px;
      background: #f9fafb;
      border-radius: 8px;
      border: 1px solid #f3f4f6;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      
      .el-image {
        width: 100%;
        height: 100%;
      }
      
      .el-icon {
        font-size: 24px;
        color: #d1d5db;
      }
    }
    
    .product-info {
      flex: 1;
      min-width: 0;
      
      .tags-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        
        .id-text {
          font-family: monospace;
          font-size: 12px;
          color: #6b7280;
          background: #f3f4f6;
          padding: 2px 6px;
          border-radius: 4px;
        }
      }
      
      .product-title {
        font-size: 14px;
        font-weight: 700;
        color: #1f2937;
        line-height: 1.4;
        margin-bottom: 8px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      
      .category-info {
        font-size: 12px;
        color: #6b7280;
        display: flex;
        align-items: center;
        gap: 6px;
        
        b {
          color: #374151;
        }
      }
    }
  }
  
  .error-content {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #dc2626;
    
    .error-icon {
      width: 40px;
      height: 40px;
      background: #fef2f2;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }
    
    .error-title {
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 2px;
    }
    
    .error-desc {
      font-size: 12px;
      opacity: 0.8;
    }
  }
}

.progress-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .progress-card {
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
    text-align: center;
    width: 100%;
    max-width: 280px;
    
    .progress-label {
      display: flex;
      flex-direction: column;
      align-items: center;
      
      .percentage {
        font-size: 20px;
        font-weight: 700;
        color: #374151;
      }
      
      .text {
        font-size: 10px;
        text-transform: uppercase;
        color: #9ca3af;
      }
    }
    
    h4 {
      font-size: 16px;
      font-weight: 700;
      color: #1f2937;
      margin: 16px 0 4px 0;
    }
    
    p {
      font-size: 12px;
      color: #6b7280;
      margin: 0 0 16px 0;
    }
  }
}

// 动画增强
.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
