<template>
  <div class="extraction-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <el-button circle :icon="ArrowLeft" @click="$router.back()" />
          <div>
            <h1 class="text-2xl font-bold text-gray-800">
              AI 特征提取 
              <span v-if="batch?.id" class="text-gray-400 text-lg font-normal ml-2">#{{ batch.id }}</span>
            </h1>
            <p class="text-sm text-gray-500 mt-1" v-if="batch">
              {{ batch.filename }} · {{ batch.total_rows }} 条记录
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="main-content" v-loading="loading">
      <!-- 第一部分：数据预览和配置 -->
      <div class="section-card mb-6">
        <div class="section-header">
          <h2 class="section-title">数据预览与配置</h2>
          <p class="section-subtitle">查看原始数据并配置 AI 提取字段</p>
        </div>

        <el-row :gutter="24">
          <!-- 左侧：数据预览 -->
          <el-col :span="16">
            <el-card shadow="never" class="preview-card">
              <template #header>
                <div class="flex justify-between items-center">
                  <span class="font-semibold text-gray-700">数据预览</span>
                  <el-tag size="small" type="info">全部数据</el-tag>
                </div>
              </template>
              
              <el-table :data="previewRecords" style="width: 100%" border stripe size="small">
                <el-table-column 
                  v-for="col in previewColumns" 
                  :key="col" 
                  :prop="col" 
                  :label="col"
                  min-width="120" 
                  show-overflow-tooltip
                />
              </el-table>
            </el-card>

            <!-- 现有字段 -->
            <el-card shadow="never" class="mt-4">
              <template #header>
                <span class="font-semibold text-gray-700">现有字段</span>
              </template>
              <div class="flex flex-wrap gap-2">
                <el-tag 
                  v-for="col in previewColumns" 
                  :key="col" 
                  effect="plain"
                  size="large"
                  class="field-tag"
                >
                  {{ col }}
                </el-tag>
              </div>
            </el-card>
          </el-col>

          <!-- 右侧：提取配置 -->
          <el-col :span="8">
            <el-card shadow="never" class="config-card">
              <template #header>
                <div class="flex items-center gap-2">
                  <el-icon class="text-primary" :size="20"><MagicStick /></el-icon>
                  <span class="font-semibold text-gray-700">提取配置</span>
                </div>
              </template>

              <el-form label-position="top">
                <el-form-item label="目标字段">
                  <div class="text-xs text-gray-500 mb-2">
                    输入您想要 AI 从原始数据中分析并提取的新字段
                  </div>
                  <el-select
                    v-model="targetFields"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    :reserve-keyword="false"
                    placeholder="输入新字段名称并回车添加 (如: 材质, 适用人群)"
                    no-data-text="输入字段名称并回车添加"
                    class="w-full custom-tag-input"
                    size="large"
                  />
                </el-form-item>

                <div class="info-box">
                  <div class="flex items-start gap-2">
                    <el-icon class="text-blue-500 mt-0.5"><InfoFilled /></el-icon>
                    <div class="text-xs text-gray-600 leading-5">
                      <div>• AI 将分析所有原始列的内容</div>
                      <div>• 提取结果将自动添加到新列中</div>
                      <div>• 建议使用清晰的字段名称</div>
                    </div>
                  </div>
                </div>

                <el-button 
                  type="primary" 
                  size="large" 
                  class="w-full mt-4" 
                  :loading="extracting"
                  @click="submitExtraction"
                  :disabled="targetFields.length === 0"
                >
                  <el-icon class="mr-2"><MagicStick /></el-icon>
                  开始 AI 提取
                </el-button>
              </el-form>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 第二部分：提取历史 -->
      <div class="section-card">
        <div class="section-header">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="section-title">提取历史（查看所有提取记录及其详细结果）</h2>
            </div>
            <!-- <div class="flex items-center gap-3">
              <el-badge :value="runs.length" type="primary" v-if="runs.length > 0" />
              <el-button :icon="Refresh" circle size="small" @click="fetchRuns" />
            </div> -->
          </div>
        </div>

        <el-card shadow="never">
          <el-table 
            :data="runs" 
            style="width: 100%" 
            border 
            stripe
            row-key="id"
            @expand-change="handleExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="expanded-content">
                  <el-table 
                    :data="runResultsCache[row.id] || []" 
                    border 
                    size="small"
                    :loading="loadingRunResults[row.id]"
                    max-height="400"
                  >
                    <el-table-column label="ASIN" prop="asin" width="120" fixed />
                    <el-table-column label="标题" prop="title" min-width="200" show-overflow-tooltip />
                    <el-table-column 
                      v-for="field in (row.target_fields || [])" 
                      :key="field" 
                      :label="field"
                      min-width="150"
                      show-overflow-tooltip
                    >
                      <template #default="{ row: record }">
                        <span class="text-sm">{{ record.ai_features?.[field] || '-' }}</span>
                      </template>
                    </el-table-column>

                    <el-table-column label="提取依据" width="120" fixed="right">
                      <template #default="{ row: record }">
                        <el-button 
                          link 
                          type="primary" 
                          size="small" 
                          @click="viewDetails(record)"
                        >
                          查看
                        </el-button>
                      </template>
                    </el-table-column>

                    <template #empty>
                      <div class="text-gray-400 text-sm py-8">
                        暂无提取记录
                      </div>
                    </template>
                  </el-table>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="编号" width="80" prop="id">
              <template #default="{ row }">
                <span class="font-mono text-gray-500">#{{ row.id }}</span>
              </template>
            </el-table-column>

            <el-table-column label="时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            
            <el-table-column label="提取字段" min-width="200">
              <template #default="{ row }">
                <div class="flex flex-wrap gap-1">
                  <el-tag 
                    v-for="field in (row.target_fields || [])" 
                    :key="field" 
                    size="small" 
                    type="info" 
                    effect="plain"
                  >
                    {{ field }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getAiStatusType(row.status)">
                  {{ getAiStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="统计" width="250">
              <template #default="{ row }">
                <div v-if="row.stats" class="text-xs space-y-1">
                  <div class="flex gap-2">
                    <span>总计: {{ row.stats.total }}</span>
                    <span class="text-success">成功: {{ row.stats.success }}</span>
                    <span class="text-danger" v-if="row.stats.failed > 0">失败: {{ row.stats.failed }}</span>
                  </div>
                  <div class="flex gap-2 text-gray-500">
                    <span>Token: {{ row.stats.total_tokens?.toLocaleString() || '-' }}</span>
                    <span class="text-orange-600 font-bold" v-if="row.stats.total_cost">
                      ${{ row.stats.total_cost.toFixed(4) }}
                    </span>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="exportRun(row)">
                  导出
                </el-button>
              </template>
            </el-table-column>

            <template #empty>
              <div class="text-gray-400 text-sm py-8">
                暂无提取记录
              </div>
            </template>
          </el-table>
        </el-card>
      </div>

      <!-- 详情弹窗 -->
      <el-dialog
        v-model="detailsVisible"
        title="提取详情"
        width="900px"
        destroy-on-close
      >
        <div class="extraction-details" v-if="currentRecord">
          <!-- 顶部操作栏 -->
          <div class="flex justify-between items-center mb-6 pb-4 border-b">
            <div>
              <div class="text-sm text-gray-500">ASIN</div>
              <div class="font-mono font-bold text-lg">{{ currentRecord.asin }}</div>
            </div>
            <el-button 
              type="primary" 
              :icon="MagicStick"
              :loading="reExtracting"
              @click="reExtractRecord"
            >
              重新提取
            </el-button>
          </div>

          <!-- 产品标题 -->
          <div class="mb-6">
            <div class="text-sm text-gray-500 mb-1">产品标题</div>
            <div class="text-base">{{ currentRecord.title }}</div>
          </div>

          <el-tabs v-model="activeTab" type="border-card">
            <!-- Tab 1: 提取依据 -->
            <el-tab-pane label="提取依据 (Prompt)" name="prompt">
              <div class="prompt-container">
                <div class="flex justify-between items-center mb-3">
                  <span class="text-sm text-gray-600">此 Prompt 将发送给 DeepSeek API</span>
                  <el-button size="small" @click="copyPrompt">
                    <el-icon><DocumentCopy /></el-icon>
                    复制
                  </el-button>
                </div>
                <div class="code-block">
{{ constructPrompt(currentRecord) }}
                </div>
              </div>
            </el-tab-pane>

            <!-- Tab 2: 原始数据 -->
            <el-tab-pane label="原始数据 (JSON)" name="raw">
              <div class="code-block">
{{ JSON.stringify(currentRecord.raw_payload || currentRecord.normalized_payload, null, 2) }}
              </div>
            </el-tab-pane>

            <!-- Tab 3: 提取结果 -->
            <el-tab-pane label="提取结果" name="result">
              <div v-if="reExtractionResult" class="mb-4">
                <el-alert 
                  type="success" 
                  :closable="false"
                  show-icon
                >
                  <template #title>
                    <span class="font-semibold">重新提取完成</span>
                  </template>
                  最新提取结果如下（未保存到数据库）
                </el-alert>
              </div>
              <div class="result-block">
{{ JSON.stringify(reExtractionResult || currentRecord.ai_features, null, 2) }}
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, MagicStick, Refresh, InfoFilled, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { http } from '@/utils/http'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const batchId = route.params.batchId as string

interface Batch {
  id: number
  filename: string
  total_rows?: number
  ai_status?: string
  ai_summary?: {
    total: number
    success: number
    failed: number
  }
  [key: string]: unknown
}

interface RecordData {
  id: string
  normalized_payload?: Record<string, unknown>
  raw_payload?: Record<string, unknown>
  ai_status?: string
  ai_features?: Record<string, any>
  asin?: string
  title?: string
  [key: string]: unknown
}

const loading = ref(false)
const extracting = ref(false)
const batch = ref<Batch | null>(null)
const previewRecords = ref<RecordData[]>([])
const targetFields = ref<string[]>([])



// 结果列表相关
const resultRecords = ref<RecordData[]>([])
const resultPage = ref(1)
const resultPageSize = ref(20)
const resultTotal = ref(0)
const loadingResults = ref(false)
let pollTimer: number | null = null

// 运行记录
interface ExtractionRun {
  id: number
  batch_id: number
  status: string
  target_fields: string[]
  created_at: string
  stats?: {
    total: number
    success: number
    failed: number
    total_tokens?: number
    total_cost?: number
  }
}
const runs = ref<ExtractionRun[]>([])
const selectedRun = ref<ExtractionRun | null>(null)
const runResultsCache = ref<Record<number, RecordData[]>>({}) // 缓存每个 run 的结果
const loadingRunResults = ref<Record<number, boolean>>({}) // 每个 run 的加载状态



// 详情弹窗
const detailsVisible = ref(false)
const currentRecord = ref<RecordData | null>(null)
const activeTab = ref('prompt')
const reExtracting = ref(false)
const reExtractionResult = ref<any>(null)


// 计算预览列（从第一条记录的 payload 中获取 key）
const previewColumns = computed(() => {
  if (previewRecords.value.length === 0) return []
  // 优先使用 normalized_payload，否则使用 raw_payload
  const firstRecord = previewRecords.value[0]
  if (!firstRecord) return []
  // 排除 id 字段
  return Object.keys(firstRecord).filter(key => key !== 'id')
})

const fetchBatchDetails = async () => {
  loading.value = true
  try {
    // 获取批次详情
    const { data: batchData } = await http.get(`/imports/${batchId}`)
    if (batchData && batchData.batch) {
      batch.value = batchData.batch
    }

    // 获取预览记录
    const { data: recordsData } = await http.get(`/imports/${batchId}/records`, {
      params: { limit: 10000 }
    })
    
    if (Array.isArray(recordsData)) {
      // 处理记录数据，展平 payload
      previewRecords.value = recordsData.map((record: RecordData) => {
        const payload = record.raw_payload || record.normalized_payload || {}
        return {
          id: record.id,
          ...payload
        }
      })
    }
  } catch (err) {
    console.error('Failed to load batch details:', err)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const fetchResults = async () => {
  loadingResults.value = true
  try {
    const { data } = await http.get(`/imports/${batchId}/records`, {
      params: { 
        limit: resultPageSize.value,
        offset: (resultPage.value - 1) * resultPageSize.value
      }
    })
    
    if (Array.isArray(data)) {
      resultRecords.value = data
      // 如果是第一页，尝试更新总数（虽然 API 没返回总数，但可以用 batch.total_rows 近似）
      if (batch.value?.total_rows) {
        resultTotal.value = batch.value.total_rows
      }
    }
  } catch (err) {
    console.error('Failed to load results:', err)
  } finally {
    loadingResults.value = false
  }
}

const fetchRuns = async () => {
  try {
    const { data } = await http.get(`/imports/${batchId}/runs`)
    if (data && Array.isArray(data.items)) {
      runs.value = data.items
      // 如果没有选中的 run，默认选中最新的一个
      if (!selectedRun.value && runs.value.length > 0) {
        const firstRun = runs.value[0]
        if (firstRun) {
          selectedRun.value = firstRun
        }
      }
    }
  } catch (err) {
    console.error('Failed to load runs:', err)
  }
}

const viewRunDetails = (run: ExtractionRun) => {
  selectedRun.value = run
  fetchResults()
}

const handleExpandChange = (row: ExtractionRun, expandedRows: ExtractionRun[]) => {
  // 如果行被展开且还没有加载数据，则自动加载
  const isExpanded = expandedRows.some(r => r.id === row.id)
  if (isExpanded && !runResultsCache.value[row.id]) {
    loadRunResults(row.id)
  }
}

const loadRunResults = async (runId: number) => {
  loadingRunResults.value[runId] = true
  try {
    const run = runs.value.find(r => r.id === runId)
    if (!run) return
    
    // 获取该批次的所有记录（API 限制最大 100）
    const { data } = await http.get(`/imports/${run.batch_id}/records`, {
      params: { limit: 10000 }
    })
    
    if (Array.isArray(data)) {
      runResultsCache.value[runId] = data
    }
  } catch (err) {
    console.error('Failed to load run results:', err)
    ElMessage.error('加载提取结果失败')
  } finally {
    loadingRunResults.value[runId] = false
  }
}

const exportRun = async (run: ExtractionRun) => {
  // 跳转到导出页面，传递参数
  router.push({
    path: '/export',
    query: {
      type: 'extraction',
      batchId: run.batch_id.toString(),
      runId: run.id.toString(),
      fields: run.target_fields.join(',')
    }
  })
}


const formatDate = (dateStr: string) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

// 计算已提取的字段（从结果中动态获取，或者使用 targetFields）
const extractedFields = computed(() => {
  // 如果选中了某个 run，只展示该 run 的目标字段
  if (selectedRun.value?.target_fields?.length) {
    return selectedRun.value.target_fields
  }

  // 优先使用用户输入的目标字段
  if (targetFields.value.length > 0) return targetFields.value
  
  // 否则尝试从结果中获取
  const fields = new Set<string>()
  resultRecords.value.forEach(row => {
    if (row.ai_features) {
      Object.keys(row.ai_features).forEach(k => {
        if (k !== '_usage') fields.add(k)
      })
    }
  })
  return Array.from(fields)
})

const getAiStatusType = (status?: string) => {
  switch (status) {
    case 'completed':
    case 'success': return 'success'
    case 'processing': return 'primary'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getAiStatusText = (status?: string) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'success': return '成功'
    case 'processing': return '进行中'
    case 'failed': return '失败'
    case 'none': return '未开始'
    default: return status || '未知'
  }
}

const startPolling = () => {
  if (pollTimer) return
  pollTimer = window.setInterval(async () => {
    // 刷新 runs
    await fetchRuns()
    
    // 检查是否有正在进行的 run
    const processingRun = runs.value.find(r => r.status === 'processing')
    
    if (processingRun) {
      // 如果有正在进行的，刷新结果列表（虽然结果可能还没出来，但为了实时性）
      fetchResults()
    } else {
      // 如果没有正在进行的，停止轮询
      stopPolling()
      fetchResults()
    }
  }, 3000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const estimateCost = () => {
  if (!batch.value?.total_rows || previewRecords.value.length === 0) return null

  // 1. 计算单行输入 Token (JSON 字符串长度 / 3)
  const sampleRow = previewRecords.value[0]
  // 排除 id
  const rowData = { ...sampleRow }
  delete rowData.id
  const inputChars = JSON.stringify(rowData).length
  const inputTokensPerRow = Math.ceil(inputChars / 3) + 100 // +100 System Prompt

  // 2. 计算单行输出 Token (目标字段数 * 20 字符 / 3)
  const outputTokensPerRow = Math.ceil((targetFields.value.length * 20) / 3)

  // 3. 总 Token
  const totalRows = batch.value.total_rows
  const totalInputTokens = inputTokensPerRow * totalRows
  const totalOutputTokens = outputTokensPerRow * totalRows
  const totalTokens = totalInputTokens + totalOutputTokens

  // 4. 预估费用 (DeepSeek V3: Input $0.14/1M, Output $0.28/1M)
  // 汇率假设 1 USD = 7.2 CNY
  const pricePerMillionInput = 0.14
  const pricePerMillionOutput = 0.28
  
  const costUSD = (totalInputTokens / 1_000_000 * pricePerMillionInput) + 
                  (totalOutputTokens / 1_000_000 * pricePerMillionOutput)
  
  return {
    tokens: totalTokens,
    cost: costUSD
  }
}

const submitExtraction = async () => {
  if (!batchId || targetFields.value.length === 0) return

  // 检查是否超过 50 条记录
  if (batch.value?.total_rows && batch.value.total_rows > 50) {
    try {
      await ElMessageBox.confirm(
        `当前批次包含 ${batch.value.total_rows} 条记录，超过 50 条。AI 提取将消耗较多 Token，是否继续？`,
        '高消耗预警',
        {
          confirmButtonText: '确认继续',
          cancelButtonText: '取消',
          type: 'warning',
          icon: InfoFilled
        }
      )
    } catch {
      return
    }
  }

  const estimate = estimateCost()
  if (estimate) {
    try {
      await ElMessageBox.confirm(
        `预计消耗 Token: ${estimate.tokens.toLocaleString()} \n预计费用: $${estimate.cost.toFixed(4)}`,
        '确认开始提取?',
        {
          confirmButtonText: '开始提取',
          cancelButtonText: '取消',
          type: 'info'
        }
      )
    } catch {
      return
    }
  }

  extracting.value = true
  try {
    await http.post(`/imports/${batchId}/extract`, {
      target_fields: targetFields.value
    })
    ElMessage.success('AI 提取任务已启动')
    // 开始轮询
    startPolling()
  } catch (err) {
    console.error('Extraction failed:', err)
    ElMessage.error('AI 提取启动失败')
  } finally {
    extracting.value = false
  }
}

const copyPrompt = async () => {
  if (!currentRecord.value) return
  const prompt = constructPrompt(currentRecord.value)
  try {
    await navigator.clipboard.writeText(prompt)
    ElMessage.success('Prompt 已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

const reExtractRecord = async () => {
  if (!currentRecord.value) return
  
  reExtracting.value = true
  reExtractionResult.value = null
  
  try {
    // 构建 prompt
    const prompt = constructPrompt(currentRecord.value)
    
    // 调用后端 API 进行提取（这里需要一个单条记录提取的 API）
    // 暂时使用模拟调用
    const { data } = await http.post('/extraction/single', {
      prompt: prompt,
      record_id: currentRecord.value.id
    })
    
    reExtractionResult.value = data
    activeTab.value = 'result'
    ElMessage.success('重新提取完成')
  } catch (err: any) {
    console.error('Re-extraction failed:', err)
    ElMessage.error(err.response?.data?.detail || '重新提取失败')
  } finally {
    reExtracting.value = false
  }
}

const viewDetails = (row: RecordData) => {
  currentRecord.value = row
  detailsVisible.value = true
}

const constructPrompt = (record: RecordData) => {
  // 优先使用 selectedRun 的 target_fields，其次使用 targetFields
  const fieldsToUse = selectedRun.value?.target_fields || targetFields.value
  const fields = fieldsToUse.length > 0 ? fieldsToUse.join(', ') : '所有相关特征'
  const payload = record.raw_payload || record.normalized_payload || {}
  return `请分析以下产品数据，并提取以下字段：${fields}。
  
产品数据：
${JSON.stringify(payload, null, 2)}

请以 JSON 格式返回提取结果。`
}

onMounted(() => {
  if (batchId) {
    fetchBatchDetails()
    fetchRuns()
    startPolling()
  } else {
    ElMessage.error('缺少批次 ID')
    router.push('/import')
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
.extraction-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  padding: 32px;
}

.page-header {
  max-width: 1400px;
  margin: 0 auto 32px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
}

.section-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.section-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.section-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.preview-card,
.config-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  
  :deep(.el-card__header) {
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
  }
}

.info-box {
  background: #f3f4f6;
  border-left: 3px solid #9ca3af;
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.field-tag {
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 6px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  color: #374151;
  transition: all 0.2s;
  
  &:hover {
    background: #e5e7eb;
    transform: translateY(-1px);
  }
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
  
  th {
    background: #f9fafb !important;
    color: #374151;
    font-weight: 600;
  }
  
  .el-table__expand-icon {
    color: #3b82f6;
  }
}

.expanded-content {
  padding: 16px;
  background: #fafafa;
}

:deep(.el-badge__content) {
  font-weight: 600;
}

.extraction-details {
  .code-block {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.6;
    white-space: pre-wrap;
    max-height: 400px;
    overflow-y: auto;
    color: #374151;
  }

  .result-block {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border: 1px solid #10b981;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.6;
    white-space: pre-wrap;
    max-height: 400px;
    overflow-y: auto;
    color: #065f46;
  }

  .prompt-container {
    padding: 8px 0;
  }
}

.text-primary {
  color: var(--primary-color);
}

.extraction-config-card {
  position: sticky;
  top: 20px;
}

.field-tag {
  margin-bottom: 4px;
}

/* 隐藏下拉箭头，使其看起来像纯文本输入框 */
.custom-tag-input :deep(.el-select__suffix) {
  display: none;
}
</style>
