<template>
  <div class="extraction-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <el-button circle :icon="ArrowLeft" class="back-btn" @click="$router.back()" />
          <div class="header-title-area">
            <h1 class="page-title">
              <span class="gradient-text">AI 特征提取</span>
              <span v-if="batch?.id" class="batch-id">#{{ batch.id }}</span>
            </h1>
            <p class="page-subtitle" v-if="batch">
              {{ batch.filename }} · {{ batch.total_rows }} 条记录
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="main-content" v-loading="loading">
      
      <!-- 顶部：场景化模板引导 -->
      <div class="step-section">
        <div class="step-header">
          <el-icon class="step-icon"><MagicStick /></el-icon>
          <h2 class="step-title">第一步：选择分析场景</h2>
        </div>
        <div class="scenario-grid">
          <div 
            v-for="template in scenarioTemplates" 
            :key="template.name"
            class="scenario-card"
            @click="applyTemplate(template)"
          >
            <div class="card-check-icon">
              <el-icon><CircleCheckFilled /></el-icon>
            </div>
            <div class="card-header">
              <div class="icon-wrapper">
                <el-icon :size="20"><component :is="template.icon || 'DataAnalysis'" /></el-icon>
              </div>
              <h3 class="card-title">{{ template.name }}</h3>
            </div>
            <p class="card-desc">{{ template.desc }}</p>
            <div class="card-tags">
              <span v-for="field in template.fields.slice(0, 3)" :key="field" class="mini-tag">
                {{ field }}
              </span>
              <span v-if="template.fields.length > 3" class="mini-tag-more">+{{ template.fields.length - 3 }}</span>
            </div>
          </div>
        </div>
      </div>

      <el-row :gutter="32">
        <!-- 左侧：配置区域 -->
        <el-col :span="10">
          <div class="config-panel-wrapper">
            <div class="step-header">
              <el-icon class="step-icon blue"><EditPen /></el-icon>
              <h2 class="step-title">第二步：配置提取规则</h2>
            </div>
            
            <div class="config-panel">
              <el-form label-position="top">
                <el-form-item>
                  <template #label>
                    <div class="form-label">
                      <span class="label-text">目标字段</span>
                      <span class="label-sub">AI 将提取这些信息</span>
                    </div>
                  </template>
                  <el-select
                    v-model="targetFields"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    :reserve-keyword="false"
                    placeholder="输入字段名并回车 (如: 材质, 适用人群)"
                    class="w-full custom-tag-input"
                    size="large"
                  />
                  
                  <!-- 智能推荐标签 -->
                  <div class="quick-tags-area">
                    <div class="tags-label">常用推荐：</div>
                    <div class="tags-list">
                      <div
                        v-for="tag in quickTags"
                        :key="tag"
                        class="quick-tag"
                        @click="addTag(tag)"
                      >
                        + {{ tag }}
                      </div>
                    </div>
                  </div>
                </el-form-item>

                <el-form-item class="mt-large">
                  <template #label>
                    <div class="form-label">
                      <span class="label-text">额外指令 (Prompt)</span>
                      <span class="label-sub">可选</span>
                    </div>
                  </template>
                  <el-input
                    v-model="customInstructions"
                    type="textarea"
                    :rows="4"
                    placeholder="例如：请忽略包装材质，只提取产品本身的材质。价格请统一保留两位小数..."
                    class="custom-textarea"
                  />
                </el-form-item>

                <!-- 预估费用提示 -->
                <div class="info-alert">
                  <div class="alert-content">
                    <el-icon class="alert-icon"><InfoFilled /></el-icon>
                    <div class="alert-text">
                      <div class="alert-title">AI 提取说明</div>
                      <div>• 系统将分析所有原始列的内容进行智能提取</div>
                      <div>• 提取结果将自动添加到新列中</div>
                      <div>• 建议先使用<span class="highlight">试运行</span>查看效果</div>
                    </div>
                  </div>
                </div>

                <div class="action-buttons">
                  <el-button 
                    type="warning" 
                    size="large" 
                    class="action-btn test-btn"
                    :loading="extracting && isTestRun"
                    @click="submitExtraction(true)"
                    :disabled="targetFields.length === 0 || extracting"
                  >
                    <el-icon class="mr-2"><VideoPlay /></el-icon>
                    试运行 (3条)
                  </el-button>
                  
                  <el-button 
                    type="primary" 
                    size="large" 
                    class="action-btn run-btn" 
                    :loading="extracting && !isTestRun"
                    @click="submitExtraction(false)"
                    :disabled="targetFields.length === 0 || extracting"
                  >
                    <el-icon class="mr-2"><MagicStick /></el-icon>
                    全部提取
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-col>

        <!-- 右侧：数据预览 -->
        <el-col :span="14">
          <div class="section-header-row">
            <div class="header-left">
              <el-icon class="header-icon"><DataBoard /></el-icon>
              <h2 class="section-title">数据预览</h2>
            </div>
            <el-tag size="small" type="info" effect="plain" class="count-tag">
              共 {{ previewRecords.length }} 条预览
            </el-tag>
          </div>

          <div class="preview-table-card">
            <el-table 
              :data="previewRecords" 
              style="width: 100%" 
              :header-cell-style="{ background: '#f9fafb', color: '#4b5563', fontWeight: '600' }"
              size="default"
            >
              <el-table-column label="ASIN" prop="asin" width="120" fixed>
                <template #default="{ row }">
                  <span class="asin-text">{{ row.asin }}</span>
                </template>
              </el-table-column>
              <el-table-column label="标题" prop="title" min-width="240" show-overflow-tooltip>
                <template #default="{ row }">
                  <span class="title-text">{{ row.title }}</span>
                </template>
              </el-table-column>
              <el-table-column 
                v-for="col in previewColumns.slice(0, 3)" 
                :key="col" 
                :prop="col" 
                :label="col"
                min-width="140" 
                show-overflow-tooltip
              />
              <el-table-column label="..." width="60" align="center">
                <template #default>
                  <span class="dots">...</span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 提取历史 -->
          <div class="history-section">
            <div class="section-header-row">
              <div class="header-left">
                <el-icon class="header-icon"><List /></el-icon>
                <h2 class="section-title">提取历史</h2>
              </div>
            </div>

            <div class="history-list">
              <div v-if="runs.length === 0" class="empty-history">
                <el-empty description="暂无提取记录" :image-size="100" />
              </div>

              <div 
                v-for="run in runs" 
                :key="run.id"
                class="history-card"
              >
                <div class="history-header">
                  <div class="history-meta">
                    <span class="run-id">#{{ run.id }}</span>
                    <el-tag :type="getAiStatusType(run.status)" size="small" effect="dark" class="status-tag">
                      {{ getAiStatusText(run.status) }}
                    </el-tag>
                    <span class="run-time">{{ formatDate(run.created_at) }}</span>
                  </div>
                  <div class="history-actions">
                    <el-button link type="primary" size="small" @click="viewRunDetails(run)">查看详情</el-button>
                    <el-divider direction="vertical" />
                    <el-button link type="primary" size="small" @click="exportRun(run)">导出结果</el-button>
                  </div>
                </div>
                
                <div class="history-body">
                  <div class="fields-row">
                    <span class="label">提取字段:</span>
                    <div class="tags-wrapper">
                      <el-tag 
                        v-for="field in (run.target_fields || [])" 
                        :key="field" 
                        size="small" 
                        type="info" 
                        effect="plain"
                        class="field-tag"
                      >
                        {{ field }}
                      </el-tag>
                    </div>
                  </div>
                  
                  <div v-if="run.stats" class="stats-row">
                    <span>总计: <span class="val">{{ run.stats.total }}</span></span>
                    <span>成功: <span class="val success">{{ run.stats.success }}</span></span>
                    <span v-if="run.stats.failed > 0">失败: <span class="val danger">{{ run.stats.failed }}</span></span>
                    <span v-if="run.stats.total_cost" class="cost-info">
                      费用: <span class="val cost">${{ run.stats.total_cost.toFixed(4) }}</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 详情弹窗 -->
      <el-dialog
        v-model="detailsVisible"
        title="提取详情"
        width="900px"
        destroy-on-close
        class="custom-dialog"
      >
        <div class="extraction-details" v-if="currentRecord">
          <!-- 顶部操作栏 -->
          <div class="details-header">
            <div>
              <div class="label">ASIN</div>
              <div class="value-lg">{{ currentRecord.asin }}</div>
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
          <div class="details-title-row">
            <div class="label">产品标题</div>
            <div class="value">{{ currentRecord.title }}</div>
          </div>

          <el-tabs v-model="activeTab" type="border-card" class="custom-tabs">
            <!-- Tab 1: 提取依据 -->
            <el-tab-pane label="提取依据 (Prompt)" name="prompt">
              <div class="prompt-container">
                <div class="prompt-header">
                  <span class="hint">此 Prompt 将发送给 DeepSeek API</span>
                  <el-button size="small" @click="copyPrompt">
                    <el-icon><DocumentCopy /></el-icon>
                    复制
                  </el-button>
                </div>
                <div class="code-block dark">
{{ constructPrompt(currentRecord) }}
                </div>
              </div>
            </el-tab-pane>

            <!-- Tab 2: 原始数据 -->
            <el-tab-pane label="原始数据 (JSON)" name="raw">
              <div class="code-block light">
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
              <div class="code-block success">
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
import { 
  ArrowLeft, MagicStick, Refresh, InfoFilled, DocumentCopy, VideoPlay, ArrowRight,
  CircleCheckFilled, EditPen, DataBoard, List, DataAnalysis, User, ShoppingBag
} from '@element-plus/icons-vue'
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
  // 排除 id, asin, title 字段（因为已经单独展示了）
  return Object.keys(firstRecord).filter(key => !['id', 'asin', 'title'].includes(key))
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

// ... (其他变量定义)

const customInstructions = ref('')
const isTestRun = ref(false)

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

// 场景化模板数据
const scenarioTemplates = [
  {
    name: '材质与工艺分析',
    desc: '提取产品的具体材质成分，区分主体和配件',
    fields: ['主体材质', '表面工艺', '核心组件材质'],
    instructions: '请提取产品的具体材质成分，区分主体和配件。如果未明确说明，请根据上下文推断最可能的材质。',
    icon: 'DataAnalysis'
  },
  {
    name: '适用人群与场景',
    desc: '分析产品描述中的适用对象和使用场景',
    fields: ['目标人群', '适用年龄', '使用场景', '节日属性'],
    instructions: '分析产品描述中的适用对象，如果是通用人群请标记为"All"。提取具体的节日或送礼场景。',
    icon: 'User'
  },
  {
    name: '痛点与卖点挖掘',
    desc: '提取产品解决的具体问题和差异化功能',
    fields: ['核心卖点', '解决的痛点', '特殊功能'],
    instructions: '提取产品声称解决的具体问题（痛点）和其主打的差异化功能。',
    icon: 'ShoppingBag'
  }
]

// 智能推荐标签
const quickTags = [
  '材质', '颜色', '尺寸', '重量', '产地',
  '风格', '适用季节', '保修期', '包装清单',
  '适用人群', '核心卖点'
]

const applyTemplate = (template: typeof scenarioTemplates[0]) => {
  // 合并字段，去重
  const newFields = new Set([...targetFields.value, ...template.fields])
  targetFields.value = Array.from(newFields)
  
  // 覆盖或追加指令？这里选择覆盖，或者如果已有内容则询问用户？
  // 简单起见，直接覆盖，但如果已有内容，追加换行
  if (customInstructions.value) {
    customInstructions.value += `\n${template.instructions}`
  } else {
    customInstructions.value = template.instructions
  }
  
  ElMessage.success(`已应用模板：${template.name}`)
}

const addTag = (tag: string) => {
  if (!targetFields.value.includes(tag)) {
    targetFields.value.push(tag)
  }
}

const submitExtraction = async (testRun = false) => {
  if (!batchId || targetFields.value.length === 0) return

  isTestRun.value = testRun

  // 检查是否超过 50 条记录 (仅在非测试模式下)
  if (!testRun && batch.value?.total_rows && batch.value.total_rows > 50) {
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
  if (!testRun && estimate) {
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
      target_fields: targetFields.value,
      custom_instructions: customInstructions.value,
      test_mode: testRun
    })
    ElMessage.success(testRun ? '试运行任务已启动' : 'AI 提取任务已启动')
    // 开始轮询
    startPolling()
  } catch (err) {
    console.error('Extraction failed:', err)
    ElMessage.error('AI 提取启动失败')
  } finally {
    extracting.value = false
    isTestRun.value = false
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
/* 全局变量 */
$primary-color: #2563eb;
$primary-gradient: linear-gradient(135deg, #2563eb 0%, #9333ea 100%);
$hover-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.1), 0 8px 10px -6px rgba(37, 99, 235, 0.1);
$card-border-radius: 16px;

.extraction-page {
  min-height: 100vh;
  background-color: #f8fafc; /* 更冷淡的高级灰 */
  padding-bottom: 64px;
}

.page-header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  padding: 20px 32px;
  margin-bottom: 40px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);

  .header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .back-btn {
    border-color: #e2e8f0;
    color: #64748b;
    transition: all 0.2s;
    &:hover {
      background-color: #fff;
      border-color: $primary-color;
      color: $primary-color;
      transform: translateX(-2px);
    }
  }

  .header-title-area {
    .page-title {
      font-size: 22px;
      font-weight: 800;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 0;
      letter-spacing: -0.02em;

      .gradient-text {
        background: $primary-gradient;
        -webkit-background-clip: text;
        color: transparent;
      }

      .batch-id {
        padding: 2px 10px;
        background: #f1f5f9;
        color: #64748b;
        font-size: 13px;
        border-radius: 6px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
      }
    }

    .page-subtitle {
      font-size: 13px;
      color: #64748b;
      margin: 4px 0 0 0;
      font-weight: 500;
    }
  }
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px;
}

.step-section {
  margin-bottom: 48px;

  .step-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    padding-left: 16px;
    border-left: 4px solid $primary-color;

    .step-icon {
      color: $primary-color;
      font-size: 22px;
      background: #eff6ff;
      padding: 6px;
      border-radius: 8px;
    }

    .step-title {
      font-size: 18px;
      font-weight: 700;
      color: #1e293b;
      margin: 0;
    }
  }
}

.scenario-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;

  @media (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.scenario-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: $card-border-radius;
  padding: 24px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;

  /* 默认状态下的微弱渐变 */
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);

  &:hover {
    border-color: #a78bfa;
    box-shadow: $hover-shadow;
    transform: translateY(-4px);

    .card-check-icon {
      opacity: 1;
      transform: scale(1);
    }

    .icon-wrapper {
      background: $primary-gradient;
      color: white;
      transform: scale(1.1) rotate(-5deg);
    }

    .card-title {
      color: #7c3aed;
    }
  }

  .card-check-icon {
    position: absolute;
    top: 16px;
    right: 16px;
    color: #8b5cf6;
    font-size: 24px;
    opacity: 0;
    transform: scale(0.8);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;

    .icon-wrapper {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background-color: #f3e8ff;
      color: #9333ea;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .card-title {
      font-size: 16px;
      font-weight: 700;
      color: #1e293b;
      margin: 0;
      transition: color 0.3s;
    }
  }

  .card-desc {
    font-size: 14px;
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 20px;
    height: 44px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .mini-tag {
      font-size: 12px;
      padding: 4px 10px;
      background-color: white;
      color: #475569;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      font-weight: 500;
    }

    .mini-tag-more {
      font-size: 12px;
      padding: 4px 8px;
      color: #94a3b8;
      background-color: #f8fafc;
      border-radius: 6px;
    }
  }
}

.config-panel-wrapper {
  position: sticky;
  top: 120px;
}

.config-panel {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: $card-border-radius;
  padding: 32px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
}

.form-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 8px;

  .label-text {
    font-size: 14px;
    font-weight: 600;
    color: #334155;
  }

  .label-sub {
    font-size: 12px;
    color: #94a3b8;
  }
}

.quick-tags-area {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e2e8f0;

  .tags-label {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 10px;
    font-weight: 500;
  }

  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .quick-tag {
    font-size: 12px;
    padding: 6px 12px;
    border-radius: 8px;
    background-color: #f8fafc;
    color: #64748b;
    border: 1px solid #e2e8f0;
    cursor: pointer;
    transition: all 0.2s;
    user-select: none;
    font-weight: 500;

    &:hover {
      background-color: #eff6ff;
      color: $primary-color;
      border-color: #bfdbfe;
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    }
  }
}

.mt-large {
  margin-top: 32px;
}

.info-alert {
  background: linear-gradient(to right, #eff6ff, #f5f3ff);
  border: 1px solid #dbeafe;
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;

  .alert-content {
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }

  .alert-icon {
    color: $primary-color;
    margin-top: 2px;
    font-size: 18px;
  }

  .alert-text {
    font-size: 13px;
    color: #475569;
    line-height: 1.6;

    .alert-title {
      font-weight: 700;
      color: #1e40af;
      margin-bottom: 4px;
    }

    .highlight {
      font-weight: 700;
      color: #ea580c;
      background: #ffedd5;
      padding: 0 4px;
      border-radius: 4px;
    }
  }
}

.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 32px;

  .action-btn {
    flex: 1;
    border-radius: 10px;
    font-weight: 600;
    height: 48px;
    font-size: 15px;
    letter-spacing: 0.01em;
  }

  .test-btn {
    background: white;
    border: 1px solid #e2e8f0;
    color: #d97706;
    &:hover {
      background: #fffbeb;
      border-color: #fcd34d;
    }
  }

  .run-btn {
    background: $primary-gradient;
    border: none;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    transition: all 0.2s;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .header-icon {
    color: #64748b;
    font-size: 20px;
  }

  .section-title {
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
    margin: 0;
  }

  .count-tag {
    background-color: white;
    border-color: #e2e8f0;
    color: #64748b;
  }
}

.preview-table-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: $card-border-radius;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);

  .asin-text {
    font-family: 'JetBrains Mono', monospace;
    color: #475569;
    font-weight: 600;
    background: #f8fafc;
    padding: 2px 6px;
    border-radius: 4px;
  }

  .title-text {
    color: #334155;
    font-weight: 500;
  }

  .dots {
    color: #cbd5e1;
    letter-spacing: 2px;
  }
}

.history-section {
  margin-top: 48px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-history {
  padding: 64px;
  background: white;
  border: 2px dashed #e2e8f0;
  border-radius: $card-border-radius;
  text-align: center;
}

.history-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: $card-border-radius;
  overflow: hidden;
  transition: all 0.2s;

  &:hover {
    border-color: #cbd5e1;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  }

  .history-header {
    padding: 16px 24px;
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .history-meta {
    display: flex;
    align-items: center;
    gap: 16px;

    .run-id {
      font-family: 'JetBrains Mono', monospace;
      color: #94a3b8;
      font-size: 14px;
      font-weight: 600;
    }

    .status-tag {
      border-radius: 6px;
      padding: 0 10px;
    }

    .run-time {
      font-size: 13px;
      color: #64748b;
    }
  }

  .history-body {
    padding: 20px 24px;
  }

  .fields-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;

    .label {
      font-size: 13px;
      color: #64748b;
      margin-top: 6px;
      font-weight: 500;
    }

    .tags-wrapper {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .field-tag {
      background: white;
      border-color: #e2e8f0;
      color: #475569;
      padding: 4px 10px;
      height: auto;
    }
  }

  .stats-row {
    display: flex;
    gap: 32px;
    font-size: 13px;
    color: #64748b;
    background-color: #f8fafc;
    padding: 10px 16px;
    border-radius: 8px;
    display: inline-flex;
    border: 1px solid #f1f5f9;

    .val {
      font-weight: 700;
      color: #0f172a;
      font-family: 'JetBrains Mono', monospace;
      
      &.success { color: #059669; }
      &.danger { color: #dc2626; }
      &.cost { color: #ea580c; }
    }

    .cost-info {
      padding-left: 32px;
      border-left: 1px solid #e2e8f0;
    }
  }
}

/* 详情弹窗样式 */
:deep(.custom-dialog) {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  
  .el-dialog__header {
    margin: 0;
    padding: 24px 32px;
    border-bottom: 1px solid #f1f5f9;
    background: #fff;
  }
  
  .el-dialog__body {
    padding: 32px;
    background: #f8fafc;
  }
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;

  .label {
    font-size: 13px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
  }

  .value-lg {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 20px;
    color: #0f172a;
  }
}

.details-title-row {
  margin-bottom: 32px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;

  .label {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 8px;
    font-weight: 500;
  }

  .value {
    font-size: 16px;
    font-weight: 500;
    color: #1e293b;
    line-height: 1.5;
  }
}

:deep(.custom-tabs) {
  border: none;
  box-shadow: none;
  background: transparent;
  
  .el-tabs__header {
    background: transparent;
    border-bottom: none;
    margin-bottom: 16px;

    .el-tabs__nav {
      border: none;
      background: #e2e8f0;
      border-radius: 8px;
      padding: 4px;
    }

    .el-tabs__item {
      border: none;
      border-radius: 6px;
      margin: 0;
      height: 36px;
      line-height: 36px;
      color: #64748b;
      transition: all 0.2s;

      &.is-active {
        background: white;
        color: $primary-color;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      }
    }
  }
  
  .el-tabs__content {
    padding: 0;
  }
}

.prompt-container {
  .prompt-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    .hint {
      font-size: 13px;
      color: #64748b;
    }
  }
}

.code-block {
  padding: 20px;
  border-radius: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid;

  &.dark {
    background-color: #1e293b;
    color: #e2e8f0;
    border-color: #334155;
  }

  &.light {
    background-color: white;
    color: #334155;
    border-color: #e2e8f0;
  }

  &.success {
    background-color: #f0fdf4;
    color: #15803d;
    border-color: #bbf7d0;
  }
}

/* 覆盖 Element Plus 样式 */
.custom-tag-input :deep(.el-select__wrapper) {
  box-shadow: none !important;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px 12px;
  min-height: 42px;
  transition: all 0.2s;
  
  &:hover {
    background-color: white;
    border-color: #cbd5e1;
  }
  
  &.is-focused {
    background-color: white;
    border-color: $primary-color;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
  }
}

.custom-textarea :deep(.el-textarea__inner) {
  box-shadow: none !important;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  transition: all 0.2s;
  font-size: 14px;
  
  &:hover {
    background-color: white;
    border-color: #cbd5e1;
  }
  
  &:focus {
    background-color: white;
    border-color: $primary-color;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
  }
}

.custom-tag-input :deep(.el-select__suffix) {
  display: none;
}

/* 表格样式优化 */
:deep(.el-table) {
  --el-table-border-color: #f1f5f9;
  --el-table-header-bg-color: #f8fafc;
  --el-table-row-hover-bg-color: #f8fafc;
  
  th.el-table__cell {
    background-color: #f8fafc !important;
    color: #475569;
    font-weight: 600;
    height: 48px;
    border-bottom: 1px solid #e2e8f0 !important;
  }
  
  td.el-table__cell {
    padding: 12px 0;
    border-bottom: 1px solid #f1f5f9 !important;
  }
  
  /* 去除垂直边框 */
  .el-table__inner-wrapper::before {
    display: none;
  }
}
</style>
