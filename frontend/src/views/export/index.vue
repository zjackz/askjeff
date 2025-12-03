<template>
  <div class="export-page p-6">
    <div class="page-header mb-6">
      <h1 class="text-2xl font-bold text-gray-800">数据导出</h1>
    </div>

    <el-row :gutter="24">
      <!-- Left: Configuration -->
      <el-col :span="8">
        <el-card shadow="never" class="mb-6">
          <template #header>
            <span class="font-bold">导出配置</span>
          </template>
          
          <el-form label-position="top" :model="form">
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
        </el-card>
      </el-col>

      <!-- Right: Preview & History -->
      <el-col :span="16">
        <!-- Preview -->
        <el-card shadow="never" class="mb-6">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">数据预览 (前 10 条)</span>
              <el-button link type="primary" @click="fetchPreview" :disabled="!canPreview">刷新预览</el-button>
            </div>
          </template>
          
          <el-table :data="previewData" border stripe v-loading="loadingPreview" height="300" size="small">
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
        </el-card>

        <!-- Export History -->
        <el-card shadow="never">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">导出历史</span>
              <el-button :icon="Refresh" circle size="small" @click="fetchJobs" />
            </div>
          </template>
          <el-table :data="jobs" stripe size="small">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="exportType" label="类型" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="startedAt" label="创建时间" width="160">
               <template #default="{ row }">
                 {{ formatDate(row.startedAt) }}
               </template>
            </el-table-column>
            <el-table-column label="操作" min-width="100">
              <template #default="{ row }">
                <el-link type="primary" v-if="row.fileUrl" :href="API_BASE + row.fileUrl" target="_blank">下载</el-link>
                <span v-else-if="row.status === 'failed'" class="text-red-500 text-xs truncate" :title="row.errorMessage">
                  {{ row.errorMessage || '失败' }}
                </span>
                <span v-else>--</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { isAxiosError } from 'axios'
import { http, API_BASE } from '@/utils/http'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const route = useRoute()

const form = reactive({
  exportType: 'clean_products',
  filters: { 
    batch_id: '' as string | number,
    run_id: ''
  },
  selectedFields: [] as string[]
})

// 状态
const submitting = ref(false)
const jobs = ref<any[]>([])
const previewData = ref<any[]>([])
const loadingPreview = ref(false)
const previewMessage = ref('请选择批次以预览数据')
const showDebug = ref(false) // 开发调试用
const batches = ref<any[]>([]) // 批次列表
const runs = ref<any[]>([]) // 提取运行列表

// 预定义字段
const standardFields = ['asin', 'title', 'price', 'brand', 'reviews', 'rating']
const availableFields = computed(() => {
  if (form.exportType === 'extraction_results') {
    // 对于提取结果，允许用户输入任意字段，这里提供一些建议
    return [...standardFields, ...form.selectedFields]
  }
  return standardFields
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
    const { data } = await http.get(`${API_BASE}/imports`, {
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
  return `[${batch.id}] ${batch.original_filename} (${time})`
}

const formatRunLabel = (run: any) => {
  const time = dayjs(run.created_at).format('MM-DD HH:mm')
  return `Run #${run.id} - ${run.status} (${time})`
}

// 初始化
onMounted(async () => {
  await fetchBatches()
  
  // 从 URL 参数初始化
  const { type, batchId, runId, fields } = route.query
  
  if (type === 'extraction') {
    form.exportType = 'extraction_results'
    if (runId) form.filters.run_id = runId as string
    if (batchId) form.filters.batch_id = Number(batchId) // 转换为数字以匹配 select
    if (fields) {
      form.selectedFields = (fields as string).split(',')
    }
    
    
    // 自动刷新预览
    if (batchId) {
      handleBatchChange() // 触发相关逻辑
    }
  } else if (batchId) {
    form.filters.batch_id = Number(batchId)
    handleBatchChange()
  }

  fetchJobs()
})

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
    const { data } = await http.get(`${API_BASE}/imports/${batchId}/runs`)
    runs.value = data.items || []
    // 如果只有一个 run，自动选中
    if (runs.value.length === 1) {
      form.filters.run_id = runs.value[0].id
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
    // 获取原始记录
    const { data } = await http.get(`${API_BASE}/imports/${form.filters.batch_id}/records`, {
      params: { limit: 10 }
    })
    
    if (Array.isArray(data)) {
      // 根据导出类型处理预览数据
      previewData.value = data.map(record => {
        const row: any = {}
        
        // 始终显示基础信息方便核对
        row.asin = record.asin
        row.title = record.title
        
        if (form.exportType === 'extraction_results') {
          // 提取 AI 字段
          form.selectedFields.forEach(field => {
            row[field] = record.ai_features?.[field] || '-'
          })
        } else {
          // 标准字段
          standardFields.forEach(field => {
            if (field !== 'asin' && field !== 'title') {
              row[field] = record[field]
            }
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

    await http.post(`${API_BASE}/exports`, {
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
    const { data } = await http.get(`${API_BASE}/exports`)
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

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}
</script>

<style scoped>
.export-page {
  background-color: #f3f4f6;
  min-height: 100vh;
}
</style>
