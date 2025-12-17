<template>
  <div class="export-page p-6 fade-up">
    <div class="page-header mb-6">
      <h1 class="text-2xl font-bold text-gray-800">数据导出</h1>
    </div>

    <div class="main-content">
      <!-- Top Section: Configuration & Preview Combined -->
      <div class="section-card mb-24 hover-card">
        <el-row>
          <!-- Left: Configuration (25%) -->
          <el-col :span="6" class="config-col">
            <div class="section-header">
              <h2 class="section-title">导出配置</h2>
            </div>
            
            <el-form label-position="top" :model="form" class="compact-form">
              <!-- 1. Batch Selection (Always First) -->
              <el-form-item label="选择批次 (Batch)">
                <el-select 
                  v-model="form.filters.batch_id" 
                  placeholder="请先选择批次" 
                  class="w-full" 
                  filterable
                  @change="handleBatchChange"
                >
                  <el-option 
                    v-for="batch in batches" 
                    :key="batch.id" 
                    :label="formatBatchLabel(batch)" 
                    :value="batch.id" 
                  />
                </el-select>
              </el-form-item>

              <!-- 2. Export Type -->
              <el-form-item label="导出类型">
                <el-select v-model="form.exportType" @change="handleTypeChange" class="w-full">
                  <el-option label="标准化产品 (Clean Products)" value="clean_products" />
                  <el-option label="AI 提取结果 (Extraction Results)" value="extraction_results" />
                  <el-option label="失败行 (Failed Rows)" value="failed_rows" />
                </el-select>
              </el-form-item>

              <!-- 3. Dynamic Filters -->
              <template v-if="form.exportType === 'extraction_results'">
                 <el-form-item label="提取运行记录 (Run ID)">
                   <el-select 
                     v-model="form.filters.run_id" 
                     placeholder="选择提取运行记录" 
                     class="w-full"
                     :disabled="!form.filters.batch_id"
                     no-data-text="该批次无提取记录"
                     @change="handleRunChange"
                   >
                     <el-option
                       v-for="run in runs"
                       :key="run.id"
                       :label="formatRunLabel(run)"
                       :value="run.id"
                     />
                   </el-select>
                   <div class="text-xs text-gray-400 mt-1" v-if="!form.filters.batch_id">
                     请先选择批次以加载运行记录
                   </div>
                 </el-form-item>
              </template>

              <!-- 4. Field Selection -->
              <el-form-item label="选择字段">
                 <el-select 
                   v-model="form.selectedFields" 
                   multiple 
                   filterable 
                   allow-create 
                   default-first-option
                   placeholder="选择要导出的字段"
                   class="w-full"
                   @change="fetchPreview"
                 >
                   <el-option 
                     v-for="field in availableFields" 
                     :key="field" 
                     :label="field" 
                     :value="field" 
                   />
                 </el-select>
                 <div class="text-xs text-gray-400 mt-1" v-if="form.exportType === 'extraction_results'">
                   留空则导出所有字段 (原始数据 + AI 提取结果)
                 </div>
              </el-form-item>

              <el-button type="primary" class="w-full mt-4" :loading="submitting" @click="submit" :disabled="!canSubmit">
                创建导出任务
              </el-button>
            </el-form>
          </el-col>

          <!-- Right: Preview (75%) -->
          <el-col :span="18" class="preview-col">
            <div class="h-full flex flex-col">
              <div class="section-header">
                  <div class="flex justify-between items-center">
                  <h2 class="section-title">数据预览 (全部数据)</h2>
                </div>
              </div>
              
              <el-table :data="previewData" border stripe v-loading="loadingPreview" height="100%" class="flex-1">
                 <el-table-column 
                   v-for="col in previewColumns" 
                   :key="col" 
                   :prop="col" 
                   :label="col" 
                   min-width="120" 
                   show-overflow-tooltip 
                 />
                 <template #empty>
                   <div class="text-center py-8 text-gray-400">
                     {{ previewMessage }}
                   </div>
                 </template>
              </el-table>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Bottom Section: History -->
      <div class="section-card hover-card">
        <div class="section-header">
          <div class="flex justify-between items-center">
            <h2 class="section-title">导出历史</h2>
            <el-button :icon="Refresh" circle @click="fetchJobs" />
          </div>
        </div>
        <el-table :data="jobs" stripe>
          <el-table-column prop="id" label="ID" width="100" align="center">
            <template #default="{ row }">
              <el-tooltip :content="row.id" placement="top">
                <span class="font-mono text-xs cursor-help">{{ row.id.substring(0, 8) }}...</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="exportType" label="类型" width="150">
            <template #default="{ row }">
              {{ formatExportType(row.exportType) }}
            </template>
          </el-table-column>
          
          <!-- 新增来源列 -->
          <el-table-column label="来源 (Batch / Run)" min-width="200">
            <template #default="{ row }">
              <div class="text-sm">
                <div v-if="row.filters?.batch_id">
                  <span class="text-gray-500">Batch:</span> 
                  <span class="font-mono ml-1">{{ row.filters.batch_id }}</span>
                </div>
                <div v-if="row.filters?.run_id">
                  <span class="text-gray-500">Run:</span> 
                  <span class="font-mono ml-1">{{ row.filters.run_id }}</span>
                </div>
                <div v-if="!row.filters?.batch_id && !row.filters?.run_id" class="text-gray-400">
                  -
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small" effect="plain">
                {{ formatStatus(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="startedAt" label="创建时间" width="180">
             <template #default="{ row }">
               <span class="text-gray-500 text-sm">{{ formatDate(row.startedAt) }}</span>
             </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <el-button 
                v-if="row.fileUrl" 
                link 
                type="primary" 
                :loading="downloadingId === row.id"
                @click="handleDownload(row)"
              >
                下载
              </el-button>
              <el-tooltip 
                v-else-if="row.status === 'failed'" 
                :content="row.errorMessage || '未知错误'" 
                placement="top"
              >
                <span class="text-red-500 text-xs cursor-help">失败原因</span>
              </el-tooltip>
              <span v-else class="text-gray-300">--</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { isAxiosError } from 'axios'
import { http } from '@/utils/http'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const route = useRoute()

const form = reactive({
  exportType: 'clean_products',
  filters: { 
    batch_id: '' as string | number,
    run_id: '' as string | number
  },
  selectedFields: [] as string[]
})

// 状态
const submitting = ref(false)
const jobs = ref<any[]>([])
const previewData = ref<any[]>([])
const loadingPreview = ref(false)
const previewMessage = ref('请选择批次以加载数据')
const showDebug = ref(false) // 开发调试用
const batches = ref<any[]>([]) // 批次列表
const runs = ref<any[]>([]) // 提取运行列表

// 预定义字段
const standardFields = ['asin', 'title', 'price', 'brand', 'reviews', 'rating']
const availableFields = computed(() => {
  let fields = [...standardFields]
  if (form.exportType === 'extraction_results' && form.filters.run_id) {
    const run = runs.value.find(r => r.id === form.filters.run_id)
    if (run && run.target_fields) {
      fields = [...fields, ...run.target_fields]
    }
  }
  return Array.from(new Set(fields))
})

const canPreview = computed(() => {
  if (form.exportType === 'extraction_results') {
    return !!form.filters.batch_id // 需要 batch_id 来获取预览数据
  }
  return !!form.filters.batch_id
})

const previewColumns = computed(() => {
  if (previewData.value.length > 0) {
    return Object.keys(previewData.value[0])
  }
  return []
})

// 获取批次列表
const fetchBatches = async () => {
  try {
    const { data } = await http.get('/imports', {
      params: { pageSize: 100 } // 获取最近 100 个批次
    })
    batches.value = data.items || []
  } catch (err) {
    console.error('Fetch batches failed:', err)
  }
}


// 格式化批次显示
const formatBatchLabel = (batch: any) => {
  const time = dayjs(batch.created_at).format('YYYY-MM-DD HH:mm')
  return `[${batch.id}] ${batch.filename} (${time})`
}

const formatRunLabel = (run: any) => {
  const time = dayjs(run.created_at).format('MM-DD HH:mm')
  return `Run #${run.id} - ${run.status} (${time})`
}

// 初始化
onMounted(async () => {
  await fetchBatches()
  fetchJobs() // Always load export history
  
  // 从 URL 参数初始化
  const { type, batchId, runId, fields } = route.query
  
  if (type === 'extraction') {
    form.exportType = 'extraction_results'
    if (runId) form.filters.run_id = Number(runId)
    if (batchId) form.filters.batch_id = Number(batchId) // 转换为数字以匹配 select
    if (fields) {
      form.selectedFields = (fields as string).split(',')
    }
    
    
    // 自动刷新预览
    if (batchId) {
      // 1. 获取运行记录
      await fetchRuns(Number(batchId))
      
      // 2. 恢复 run_id
      if (runId) {
        form.filters.run_id = Number(runId)
      }
      
      // 3. 恢复字段 (需要在 run_id 设置后)
      if (fields) {
        const fieldList = (fields as string).split(',').filter(Boolean)
        if (fieldList.length > 0) {
          form.selectedFields = fieldList
        }
      }
      
      // 4. 刷新预览
      fetchPreview()
    }
  } else if (batchId) {
    form.filters.batch_id = Number(batchId)
    handleBatchChange()
  }
})

const handleRunChange = () => {
  // 手动切换 run 时，重置字段为默认
  form.selectedFields = []
  updateSelectedFields()
  fetchPreview()
}

const updateSelectedFields = () => {
  if (form.exportType !== 'extraction_results' || !form.filters.run_id) return
  const run = runs.value.find(r => r.id === form.filters.run_id)
  if (run && run.target_fields) {
     form.selectedFields = Array.from(new Set([...standardFields, ...run.target_fields]))
  } else {
     form.selectedFields = [...standardFields]
  }
}



const handleTypeChange = () => {
  form.selectedFields = []
  // 如果已经选了 batch，尝试重新获取 runs (如果切换到 extraction)
  if (form.exportType === 'extraction_results' && form.filters.batch_id) {
    fetchRuns(form.filters.batch_id)
  }
  fetchPreview()
}

const handleBatchChange = async () => {
  const batchId = form.filters.batch_id
  if (!batchId) return

  // 1. 刷新预览
  fetchPreview()
  
  // 2. 如果是提取模式，获取运行记录
  if (form.exportType === 'extraction_results') {
    form.filters.run_id = '' // 重置 run_id
    await fetchRuns(batchId)
  }
}

const fetchRuns = async (batchId: number | string) => {
  try {
    const { data } = await http.get(`/imports/${batchId}/runs`)
    runs.value = data.items || []
    // 如果只有一个 run，自动选中
    if (runs.value.length === 1) {
      form.filters.run_id = runs.value[0].id
    }
    // 刷新选中字段 (如果 run_id 已存在或刚被选中)
    if (form.filters.run_id) {
      updateSelectedFields()
    }
  } catch (err) {
    console.error('Fetch runs failed:', err)
    ElMessage.error('获取提取记录失败')
  }
}

const canSubmit = computed(() => {
  if (!form.filters.batch_id) return false
  if (form.exportType === 'extraction_results') {
    if (!form.filters.run_id) return false
    // 允许字段为空 (表示导出所有)
    return true
  }
  return true
})

const fetchPreview = async () => {
  if (!form.filters.batch_id) {
    ElMessage.warning('需要批次 ID 才能预览')
    return
  }

  loadingPreview.value = true
  previewData.value = []
  
  try {
    // 获取所有记录 (不限制数量)
    const { data } = await http.get(`/imports/${form.filters.batch_id}/records`, {
      params: { limit: 10000 } // 设置一个较大的限制值以获取所有数据
    })
    
    if (Array.isArray(data)) {
      // 根据导出类型处理预览数据
      previewData.value = data.map(record => {
        const row: any = {}
        
        if (form.exportType === 'extraction_results') {
          // AI 提取结果模式: 原始数据 + AI 字段
          
          // 1. 基础数据: 优先使用 raw_payload (原始数据), 如果没有则使用标准字段
          if (record.raw_payload) {
            Object.assign(row, record.raw_payload)
          } else {
            standardFields.forEach(field => {
              row[field] = record[field] ?? '-'
            })
          }
          
          // 2. AI 字段: 追加或覆盖
          if (record.ai_features) {
            // 如果用户选择了特定字段
            if (form.selectedFields.length > 0) {
              // 过滤: 只保留用户选择的字段 (注意: 这里逻辑稍微复杂, 因为用户可能选了原始字段也可能选了AI字段)
              // 但为了预览简单, 我们展示所有 AI 字段, 或者只展示用户选的?
              // 用户需求是: 原始数据 + 增加字段. 
              // 如果用户选了字段, 导出时只会导出选中的. 预览也应该只显示选中的?
              // 但为了让用户看到效果, 我们还是展示 原始 + AI, 高亮 AI?
              // 暂且逻辑: 总是展示 原始 + AI. 如果用户选了字段, 可以在列上做过滤?
              // 不, 预览应该反映最终导出结果.
              
              // 重新思考: 预览应该显示最终会导出的列.
              // 如果 selectedFields 为空, 导出 = 原始 + 所有 AI.
              // 如果 selectedFields 有值, 导出 = 原始 + 选中的 AI (后端逻辑是: 原始总是保留, AI 只保留选中的).
              // 让我们匹配后端逻辑:
              
              const aiFields = Object.keys(record.ai_features)
              aiFields.forEach(field => {
                 if (form.selectedFields.length === 0 || form.selectedFields.includes(field)) {
                   row[field] = record.ai_features[field]
                 }
              })
            } else {
              // 没选字段, 显示所有 AI 字段
              Object.assign(row, record.ai_features)
            }
          }
        } else {
          // 标准产品导出模式 - 显示所有标准字段
          standardFields.forEach(field => {
            row[field] = record[field] ?? '-'
          })
        }
        return row
      })
      
      if (previewData.value.length === 0) {
        previewMessage.value = '该批次没有数据'
      }
    }
  } catch (err) {
    console.error('Preview failed:', err)
    previewMessage.value = '加载预览失败'
  } finally {
    loadingPreview.value = false
  }
}

const submit = async () => {
  submitting.value = true
  try {
    const filters: any = {}
    if (form.exportType === 'extraction_results') {
      if (!form.filters.run_id) throw new Error('请输入提取运行 ID')
      filters.run_id = form.filters.run_id
    } else {
      if (form.filters.batch_id) filters.batch_id = form.filters.batch_id
    }

    await http.post('/exports', {
      exportType: form.exportType,
      filters: filters,
      selectedFields: form.selectedFields,
      fileFormat: 'xlsx'
    })
    
    ElMessage.success('导出任务已创建')
    fetchJobs()
  } catch (err: any) {
    const msg = isAxiosError(err) ? err.response?.data?.detail : err.message
    ElMessage.error(msg || '创建导出任务失败')
  } finally {
    submitting.value = false
  }
}

const fetchJobs = async () => {
  try {
    const { data } = await http.get('/exports')
    jobs.value = data || []
  } catch (err) {
    console.error('Fetch jobs failed:', err)
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    succeeded: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const formatStatus = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    processing: '处理中',
    succeeded: '成功',
    failed: '失败'
  }
  return map[status] || status
}

const formatExportType = (type: string) => {
  const map: Record<string, string> = {
    clean_products: '标准化产品',
    extraction_results: 'AI 提取结果',
    failed_rows: '失败行'
  }
  return map[type] || type
}

const downloadingId = ref<number | null>(null)

const handleDownload = async (row: any) => {
  if (!row.fileUrl) return
  
  downloadingId.value = row.id
  try {
    const response = await http.get(row.fileUrl, {
      responseType: 'blob'
    })
    
    // Create blob link to download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // Extract filename from header or generate one
    const contentDisposition = response.headers['content-disposition']
    let filename = `export-${row.id}.${row.fileFormat || 'xlsx'}`
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
      if (filenameMatch && filenameMatch.length === 2)
        filename = filenameMatch[1]
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    
    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Download failed:', err)
    ElMessage.error('下载失败，请稍后重试')
  } finally {
    downloadingId.value = null
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}
</script>

<style scoped lang="scss">
.export-page {
  background-color: var(--bg-secondary);
  min-height: 100vh;
  animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.main-content {
  margin: 0 auto;
}

.section-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.section-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border-light);
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
  --el-table-border-color: var(--border-light);
  
  th {
    background: #f9fafb !important;
    color: var(--text-primary);
    font-weight: 600;
    height: 56px;
  }

  td {
    height: 64px;
  }

  .el-table__inner-wrapper::before {
    display: none;
  }
}

.compact-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.config-col {
  border-right: 1px solid var(--border-light);
  padding-right: 24px;
}

.preview-col {
  padding-left: 24px;
}

.mb-24 {
  margin-bottom: 24px;
}
</style>
