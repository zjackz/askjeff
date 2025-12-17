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
    <el-dialog v-model="mcpDialogVisible" title="一键抓取亚马逊数据" width="900px" destroy-on-close>
      <div class="flex gap-6" style="height: 600px;">
        <!-- 左侧：操作区 -->
        <div class="flex-1 flex flex-col">
          <div class="bg-blue-50 text-blue-600 p-3 rounded-lg mb-4 text-sm flex items-start leading-relaxed">
            <el-icon class="mt-0.5 mr-2 text-base"><InfoFilled /></el-icon>
            <span>只需粘贴 <strong>亚马逊链接</strong> 或 <strong>ASIN</strong>，系统将自动识别并为您抓取 Top 100 数据。</span>
          </div>

          <el-form :model="mcpForm" label-position="top" size="default" class="flex-1 flex flex-col">
            <el-form-item label="粘贴内容" class="!mb-4">
              <el-input 
                v-model="mcpForm.input" 
                type="textarea" 
                :rows="4"
                placeholder="例如：https://www.amazon.com/dp/B08N5WRWNW 或 B08N5WRWNW"
                resize="none"
                @input="handleInputPreview"
              />
            </el-form-item>
            
            <div class="grid grid-cols-2 gap-4 mb-4">
              <el-form-item label="抓取数量 (Top N)" class="!mb-0">
                 <div class="flex flex-col w-full">
                   <el-input-number v-model="mcpForm.limit" :min="1" :max="500" :step="1" controls-position="right" class="!w-full" />
                   <span class="text-xs text-gray-400 mt-1.5 leading-none">限制获取详情的产品数，节省额度</span>
                 </div>
              </el-form-item>
              
              <el-form-item label="高级选项" class="!mb-0">
                 <div class="flex items-center h-[32px]">
                   <el-checkbox v-model="mcpForm.test_mode" border class="!mr-0 !w-full">
                     <span class="text-gray-600 text-sm">仅试抓取 (Mock 数据)</span>
                   </el-checkbox>
                 </div>
                 <span class="text-xs text-gray-400 mt-1.5 leading-none block">不消耗 API 额度，用于测试流程</span>
              </el-form-item>
            </div>
            
            <!-- 说明文字 -->
            <div class="flex-1 bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <el-icon><InfoFilled /></el-icon>
                功能说明
              </h4>
              <div class="text-sm text-gray-600 space-y-2">
                <div class="flex items-start gap-2">
                  <span class="text-blue-500">•</span>
                  <span>支持粘贴亚马逊商品链接或 ASIN 码</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-blue-500">•</span>
                  <span>自动识别类目并抓取 Best Sellers</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-blue-500">•</span>
                  <span>批量获取产品详情（标题、价格、评分等）</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-blue-500">•</span>
                  <span>自动生成 Excel 文件供下载</span>
                </div>
              </div>
            </div>
          </el-form>
        </div>
        
        <!-- 右侧：状态区 -->
        <div class="w-80 bg-gray-50 rounded-xl p-4 flex flex-col border border-gray-200 overflow-hidden">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-gray-700 flex items-center gap-2">
              <el-icon><DataAnalysis /></el-icon>
              实时状态
            </h3>
          </div>
          
          <div class="flex-1 overflow-y-auto space-y-4">
            <!-- 智能预览 -->
            <div>
              <div class="text-xs font-medium text-gray-500 mb-2">智能识别</div>
              <transition name="el-fade-in">
                <div v-if="previewLoading" class="p-4 bg-white rounded-lg border border-gray-200 flex flex-col items-center justify-center text-gray-400 gap-2">
                  <el-icon class="is-loading text-xl"><Loading /></el-icon>
                  <span class="text-xs">识别中...</span>
                </div>
                
                <div v-else-if="previewData && previewData.valid" class="p-3 bg-white rounded-lg border border-gray-200 shadow-sm">
                  <!-- Image -->
                  <div class="flex items-center gap-3 mb-3">
                    <div class="rounded bg-gray-50 border border-gray-100 flex-shrink-0 overflow-hidden flex items-center justify-center" style="width: 60px; height: 60px;">
                       <el-image 
                         v-if="previewData.image" 
                         :src="previewData.image" 
                         class="w-full h-full"
                         fit="contain"
                       >
                         <template #error>
                           <el-icon class="text-gray-300"><Picture /></el-icon>
                         </template>
                       </el-image>
                       <el-icon v-else class="text-gray-300 text-xl"><Picture /></el-icon>
                    </div>
                    
                    <div class="flex-1 min-w-0">
                      <el-tag size="small" effect="dark" :type="previewData.type === 'asin' ? 'warning' : 'primary'" class="mb-1">
                        {{ previewData.type === 'asin' ? 'ASIN' : 'CATEGORY' }}
                      </el-tag>
                      <div class="text-xs font-mono text-gray-600 truncate">{{ previewData.value }}</div>
                    </div>
                  </div>
                  
                  <!-- Title -->
                  <div class="text-xs font-medium text-gray-800 mb-2 line-clamp-2" :title="previewData.title">
                    {{ previewData.title || '暂无标题' }}
                  </div>
                  
                  <!-- Meta -->
                  <div v-if="previewData.category_id" class="text-xs text-gray-500 flex items-center gap-1">
                    <el-icon><Menu /></el-icon>
                    <span>类目: <span class="font-medium">{{ previewData.category_id }}</span></span>
                  </div>
                </div>
                
                <div v-else-if="previewData && !previewData.valid" class="p-3 bg-red-50 rounded-lg border border-red-100 flex items-center gap-2 text-red-600">
                   <el-icon class="text-base"><Warning /></el-icon>
                   <div class="text-xs">{{ previewData.error || '无法识别' }}</div>
                </div>
                
                <div v-else class="p-4 bg-white rounded-lg border border-gray-200 border-dashed flex flex-col items-center justify-center text-gray-400">
                  <el-icon class="text-2xl mb-2"><Document /></el-icon>
                  <span class="text-xs">等待输入...</span>
                </div>
              </transition>
            </div>
            
            <!-- 进度显示 -->
            <div v-if="importProgress.visible">
              <div class="text-xs font-medium text-gray-500 mb-2">抓取进度</div>
              <div class="bg-white rounded-lg p-3 border border-gray-200">
                <div class="flex items-center gap-2 mb-3">
                  <el-icon 
                    v-if="importProgress.status === 'processing'" 
                    class="is-loading text-blue-500 text-xl"
                  >
                    <Loading />
                  </el-icon>
                  <el-icon 
                    v-else-if="importProgress.status === 'succeeded'" 
                    class="text-green-500 text-xl"
                  >
                    <CircleCheckFilled />
                  </el-icon>
                  <el-icon 
                    v-else-if="importProgress.status === 'failed'" 
                    class="text-red-500 text-xl"
                  >
                    <Warning />
                  </el-icon>
                  
                  <div class="flex-1 min-w-0">
                    <div class="font-medium text-gray-800 text-xs">{{ importProgress.message }}</div>
                    <div v-if="importProgress.detail" class="text-xs text-gray-500 mt-0.5 truncate">
                      {{ importProgress.detail }}
                    </div>
                  </div>
                </div>
                
                <el-progress 
                  v-if="importProgress.status === 'processing'" 
                  :percentage="importProgress.percentage" 
                  :status="importProgress.percentage === 100 ? 'success' : undefined"
                  :stroke-width="6"
                  striped
                  striped-flow
                />
              </div>
            </div>
            
            <!-- 提示信息 -->
            <div class="text-xs text-gray-500 space-y-2 bg-white rounded-lg p-3 border border-gray-200">
              <div class="flex items-start gap-2">
                <el-icon class="text-blue-500 mt-0.5 flex-shrink-0"><InfoFilled /></el-icon>
                <span>抓取过程中请勿关闭窗口</span>
              </div>
              <div class="flex items-start gap-2">
                <el-icon class="text-green-500 mt-0.5 flex-shrink-0"><CircleCheckFilled /></el-icon>
                <span>完成后将自动跳转到列表</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCancelImport" :disabled="importProgress.status === 'processing'">
            {{ importProgress.status === 'processing' ? '进行中...' : '取消' }}
          </el-button>
          <el-button 
            type="primary" 
            :loading="mcpSubmitting" 
            @click="handleMcpSubmit" 
            class="px-8" 
            round
            :disabled="importProgress.status === 'processing'"
          >
            {{ importProgress.status === 'processing' ? '抓取中...' : '开始抓取' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, Document, Refresh, User, MagicStick, Plus, Loading, Warning, InfoFilled, CircleCheckFilled, Picture, Menu, DataAnalysis } from '@element-plus/icons-vue'
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
</style>
