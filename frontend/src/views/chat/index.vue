<template>
  <div class="insight-page">
    <el-card class="filter-card">
      <el-form :inline="true" label-width="86px" class="filter-form">
        <el-form-item label="批次 ID">
          <el-input v-model="filters.batchId" placeholder="输入批次 ID" clearable />
        </el-form-item>
        <el-form-item label="ASIN/标题">
          <el-input v-model="filters.asin" placeholder="输入 ASIN 或关键词" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="全部" value="" />
            <el-option label="有效" value="valid" />
            <el-option label="警告" value="warning" />
            <el-option label="错误" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item label="更新时间">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DDTHH:mm:ss"
            :clearable="true"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="applyFilters">查询</el-button>
          <el-button @click="resetFilters">清除筛选</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <div class="table-header">
        <h2>上传产品列表</h2>
        <div class="table-actions">
          <el-button link type="primary" @click="reload">刷新</el-button>
          <el-button 
            type="primary" 
            :loading="exportLoading" 
            @click="exportCurrentFilters"
          >
            导出当前筛选
          </el-button>
        </div>
      </div>

      <el-alert
        v-if="errorMessage"
        type="error"
        :closable="false"
        class="mb-12"
        title="列表加载失败"
        :description="errorMessage"
        show-icon
      />

      <el-table
        v-loading="loading"
        :data="products"
        style="width: 100%"
        @sort-change="onSortChange"
        @row-click="openDetail"
      >
        <el-table-column prop="asin" label="ASIN" sortable="custom" width="140" />
        <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip />
        <el-table-column prop="batch_id" label="批次 ID" sortable="custom" width="160" />
        <el-table-column prop="validation_status" label="状态" width="120" :formatter="formatStatusCell" />
        <el-table-column
          prop="ingested_at"
          label="最近更新时间"
          sortable="custom"
          width="180"
          :formatter="formatTimeCell"
        />
        <el-table-column
          prop="price"
          label="价格"
          width="120"
        />
        <el-table-column
          prop="rating"
          label="评分"
          width="120"
        />
        <el-table-column
          prop="sales_rank"
          label="排名"
          width="120"
        />
        <template #empty>
          <el-empty description="暂无数据" />
        </template>
      </el-table>

      <div class="pagination">
        <el-pagination
          background
          layout="prev, pager, next, sizes, total"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="filters.pageSize"
          :current-page="filters.page"
          :total="total"
          @size-change="onPageSizeChange"
          @current-change="onPageChange"
        />
      </div>
    </el-card>

    <el-drawer
      v-model="detailVisible"
      title="产品详情"
      size="40%"
      append-to-body
      :destroy-on-close="false"
    >
      <div v-if="selectedProduct" class="detail-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="ASIN">{{ selectedProduct.asin }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ selectedProduct.title }}</el-descriptions-item>
          <el-descriptions-item label="批次 ID">{{ selectedProduct.batch_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            {{ formatStatus(selectedProduct.validation_status) }}
          </el-descriptions-item>
          <el-descriptions-item label="最近更新时间">
            {{ formatTime(selectedProduct.ingested_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="价格">{{ selectedProduct.price ?? '—' }}</el-descriptions-item>
          <el-descriptions-item label="评分">{{ selectedProduct.rating ?? '—' }}</el-descriptions-item>
          <el-descriptions-item label="排名">{{ selectedProduct.sales_rank ?? '—' }}</el-descriptions-item>
          <el-descriptions-item label="校验信息">
            {{ selectedProduct.validation_messages ? JSON.stringify(selectedProduct.validation_messages) : '—' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>

    <div class="chat-fab">
      <el-button type="primary" circle size="large" @click="openChat">
        <el-icon><ChatDotRound /></el-icon>
      </el-button>
    </div>

    <el-drawer
      v-model="chatVisible"
      title="智能数据洞察"
      size="500px"
      :modal="false"
      :lock-scroll="false"
      class="chat-drawer"
    >
      <div class="chat-container">
        <div class="chat-history" ref="chatHistoryRef">
          <div v-if="messages.length === 0" class="chat-empty">
            <p>👋 你好！我是你的数据助手。</p>
            <p>你可以问我关于当前数据的任何问题，例如：</p>
            <ul>
              <li>"销量前 10 的产品有哪些？"</li>
              <li>"最近一次导入的批次 ID 是多少？"</li>
              <li>"分析一下价格分布情况"</li>
            </ul>
          </div>
          
          <div 
            v-for="(msg, index) in messages" 
            :key="index" 
            class="chat-message"
            :class="msg.role"
          >
            <div class="message-avatar">
              <el-avatar :size="32" :icon="msg.role === 'user' ? UserFilled : Service" :class="msg.role" />
            </div>
            <div class="message-content">
              <div class="message-bubble">
                {{ msg.content }}
              </div>
            </div>
          </div>
          
          <div v-if="chatLoading" class="chat-message assistant">
             <div class="message-avatar">
              <el-avatar :size="32" :icon="Service" class="assistant" />
            </div>
            <div class="message-content">
              <div class="message-bubble typing">
                <span>.</span><span>.</span><span>.</span>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <el-input
            v-model="question"
            type="textarea"
            :rows="3"
            placeholder="输入问题，按 Enter 发送..."
            @keydown.enter.prevent="handleEnter"
            :disabled="chatLoading"
          />
          <div class="chat-actions">
            <el-button type="primary" :loading="chatLoading" @click="sendQuestion" :disabled="!question.trim()">
              发送
            </el-button>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, watch, nextTick } from 'vue'
import { isAxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { ChatDotRound, UserFilled, Service } from '@element-plus/icons-vue'
import { http, API_BASE } from '@/utils/http'
import type { ProductItem, ProductQueryParams, ChatResponse } from './types'

const FILTER_STORAGE_KEY = 'insight_filters'

// 从 sessionStorage 加载筛选条件
const loadFiltersFromStorage = () => {
  try {
    const stored = sessionStorage.getItem(FILTER_STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      return {
        batchId: parsed.batchId || '',
        asin: parsed.asin || '',
        status: parsed.status || '',
        dateRange: parsed.dateRange || [],
        sortBy: parsed.sortBy || '',
        sortOrder: parsed.sortOrder || '' as 'asc' | 'desc' | '',
        page: 1, // 总是从第一页开始
        pageSize: parsed.pageSize || 20
      }
    }
  } catch (e) {
    console.warn('Failed to load filters from storage:', e)
  }
  return null
}

// 保存筛选条件到 sessionStorage
const saveFiltersToStorage = (filters: typeof filters) => {
  try {
    sessionStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify({
      batchId: filters.batchId,
      asin: filters.asin,
      status: filters.status,
      dateRange: filters.dateRange,
      sortBy: filters.sortBy,
      sortOrder: filters.sortOrder,
      pageSize: filters.pageSize
    }))
  } catch (e) {
    console.warn('Failed to save filters to storage:', e)
  }
}

const savedFilters = loadFiltersFromStorage()
const filters = reactive(savedFilters || {
  batchId: '',
  asin: '',
  status: '',
  dateRange: [] as string[],
  sortBy: '',
  sortOrder: '' as 'asc' | 'desc' | '',
  page: 1,
  pageSize: 20
})

// 监听筛选条件变化并保存
watch(filters, (newFilters) => {
  saveFiltersToStorage(newFilters)
}, { deep: true })

const products = ref<ProductItem[]>([])
const total = ref(0)
const loading = ref(false)
const errorMessage = ref('')
const detailVisible = ref(false)
const selectedProduct = ref<ProductItem | null>(null)

const chatVisible = ref(false)
const question = ref('')
const chatLoading = ref(false)
const chatHistoryRef = ref<HTMLElement | null>(null)

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}
const messages = ref<ChatMessage[]>([])

const exportLoading = ref(false)


const trackEvent = (event: string, payload?: Record<string, unknown>) => {
  // 轻量埋点：后续可替换成统一埋点 SDK
  console.info(`[埋点] ${event}`, payload || {})
}

const buildQueryParams = (): ProductQueryParams => {
  const params: ProductQueryParams = {
    batchId: filters.batchId || undefined,
    asin: filters.asin || undefined,
    status: filters.status || undefined,
    page: filters.page,
    pageSize: filters.pageSize,
    sortBy: filters.sortBy || undefined,
    sortOrder: (filters.sortOrder as 'asc' | 'desc') || undefined
  }
  if (filters.dateRange?.length === 2) {
    params.updated_from = filters.dateRange[0]
    params.updated_to = filters.dateRange[1]
  }
  return params
}

type RawProduct = Record<string, unknown>

const normalizeProduct = (raw: RawProduct): ProductItem => ({
  id: String(raw.id ?? ''),
  asin: String(raw.asin ?? ''),
  title: String(raw.title ?? ''),
  batch_id: String(raw.batchId ?? raw.batch_id ?? ''),
  ingested_at: String(raw.ingestedAt ?? raw.ingested_at ?? ''),
  validation_status: String(raw.validationStatus ?? raw.validation_status ?? ''),
  validation_messages: (raw.validationMessages as Record<string, unknown> | null) ??
    (raw.validation_messages as Record<string, unknown> | null) ??
    null,
  price: typeof raw.price === 'number' ? raw.price : null,
  rating: typeof raw.rating === 'number' ? raw.rating : null,
  sales_rank:
    typeof raw.salesRank === 'number'
      ? raw.salesRank
      : typeof raw.sales_rank === 'number'
        ? raw.sales_rank
        : null
})

const extractErrorMessage = (err: unknown): string | null => {
  if (isAxiosError(err)) {
    const detail = err.response?.data?.detail
    if (detail) return String(detail)
    return err.message || null
  }
  if (err instanceof Error) return err.message
  return null
}

const fetchProducts = async (resetPage = false) => {
  if (resetPage) {
    filters.page = 1
  }
  loading.value = true
  errorMessage.value = ''
  try {
    const params = buildQueryParams()
    const { data } = await http.get(`${API_BASE}/products`, {
      params: {
        batchId: params.batchId,
        asin: params.asin,
        status: params.status,
        page: params.page,
        pageSize: params.pageSize,
        sortBy: params.sortBy,
        sortOrder: params.sortOrder,
        updated_from: params.updated_from,
        updated_to: params.updated_to
      }
    })
    const items = (data?.items ?? []).map((item: RawProduct) => normalizeProduct(item))
    products.value = items
    total.value = data?.total || 0
    trackEvent('products_fetch_success', { total: total.value })
  } catch (err: unknown) {
    const detail = extractErrorMessage(err)
    errorMessage.value = detail
      ? String(detail)
      : '获取产品列表失败，请重试或联系维护人员'
    trackEvent('products_fetch_failed', { error: errorMessage.value })
    console.error(err)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  trackEvent('filter_apply', { ...filters })
  fetchProducts(true)
}

const resetFilters = () => {
  filters.batchId = ''
  filters.asin = ''
  filters.status = ''
  filters.dateRange = []
  filters.sortBy = ''
  filters.sortOrder = ''
  filters.page = 1
  filters.pageSize = 20
  trackEvent('filter_reset')
  fetchProducts(true)
}

const onSortChange = ({ prop, order }: { prop: string; order: 'ascending' | 'descending' | null }) => {
  filters.sortBy = prop
  filters.sortOrder = order === 'ascending' ? 'asc' : order === 'descending' ? 'desc' : ''
  fetchProducts()
}

const onPageChange = (page: number) => {
  filters.page = page
  fetchProducts()
}

const onPageSizeChange = (size: number) => {
  filters.pageSize = size
  filters.page = 1
  fetchProducts()
}

const openDetail = (row: ProductItem) => {
  selectedProduct.value = row
  detailVisible.value = true
  trackEvent('detail_open', { asin: row.asin })
}

const formatTime = (value?: string) => {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

const formatTimeCell = (_: unknown, __: unknown, cell: unknown) =>
  formatTime(typeof cell === 'string' ? cell : '')
const formatStatus = (status?: string) => {
  const map: Record<string, string> = {
    valid: '有效',
    warning: '警告',
    error: '错误'
  }
  return map[status || ''] || status || ''
}
const formatStatusCell = (_: unknown, __: unknown, cell: unknown) =>
  formatStatus(typeof cell === 'string' ? cell : '')

const openChat = () => {
  chatVisible.value = true
  trackEvent('chat_open')
  scrollToBottom()
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatHistoryRef.value) {
    chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
  }
}

const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    sendQuestion()
  }
}

const sendQuestion = async () => {
  const content = question.value.trim()
  if (!content) return
  
  messages.value.push({ role: 'user', content })
  question.value = ''
  chatLoading.value = true
  scrollToBottom()

  try {
    const { data } = await http.post<ChatResponse>(`${API_BASE}/chat/query`, {
      question: content
    })
    messages.value.push({ role: 'assistant', content: data.answer })
    trackEvent('chat_success')
  } catch (err) {
    // 全局错误处理已接管
  } finally {
    chatLoading.value = false
    scrollToBottom()
  }
}

const exportCurrentFilters = async () => {
  if (exportLoading.value) return
  
  exportLoading.value = true
  trackEvent('export_start', { filters: { ...filters }, total: total.value })
  
  try {
    const params = buildQueryParams()
    // 构造导出请求
    const payload = {
      exportType: 'clean-products',
      selectedFields: ['asin', 'title', 'price', 'batch_id', 'validation_status'],
      filters: {
        batch_id: params.batchId, // 注意后端字段名差异
        asin: params.asin,
        validation_status: params.status, // 注意后端字段名差异
        updated_from: params.updated_from,
        updated_to: params.updated_to
      },
      fileFormat: 'csv'
    }

    const { data } = await http.post(`${API_BASE}/exports`, payload)
    
    if (data.status === 'succeeded' && data.fileUrl) {
      // 触发下载
      const downloadUrl = `${API_BASE}${data.fileUrl}`
      const link = document.createElement('a')
      link.href = downloadUrl
      link.setAttribute('download', `export-${data.id}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      ElMessage.success('导出成功，正在下载...')
      trackEvent('export_success', { jobId: data.id })
    } else {
      ElMessage.warning(`导出任务状态: ${data.status}，请稍后查看`)
    }
  } catch (err: unknown) {
    const detail = extractErrorMessage(err)
    const errorMsg = (detail && String(detail)) || '导出失败，请稍后重试'
    ElMessage.error(errorMsg)
    trackEvent('export_failed', { error: errorMsg })
    console.error(err)
  } finally {
    exportLoading.value = false
  }
}

const reload = () => fetchProducts()

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.insight-page {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.filter-card {
  margin-bottom: 4px;
}
.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 24px;
  align-items: flex-end;
}
.table-card {
  position: relative;
}
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.table-actions {
  display: flex;
  gap: 8px;
}
.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
.detail-content {
  padding: 8px 0;
}
.mb-12 {
  margin-bottom: 12px;
}
.chat-fab {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 20;
}
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
}
.chat-empty {
  text-align: center;
  color: #909399;
  margin-top: 40px;
}
.chat-empty ul {
  text-align: left;
  display: inline-block;
  margin-top: 10px;
}
.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.chat-message.user {
  flex-direction: row-reverse;
}
.message-avatar .el-avatar {
  background-color: #409eff;
}
.message-avatar .el-avatar.user {
  background-color: #67c23a;
}
.message-content {
  max-width: 80%;
}
.message-bubble {
  padding: 10px 14px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  line-height: 1.5;
  white-space: pre-wrap;
}
.chat-message.user .message-bubble {
  background-color: #95d475;
  color: #303133;
}
.typing span {
  display: inline-block;
  animation: dot-blink 1.4s infinite both;
  margin: 0 2px;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-blink {
  0% { opacity: 0.2; }
  20% { opacity: 1; }
  100% { opacity: 0.2; }
}

.chat-input-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.chat-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
