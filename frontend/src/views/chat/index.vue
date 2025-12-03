<template>
  <div class="insight-page">
    <el-card class="filter-card">
      <el-form :inline="true" label-width="86px" class="filter-form">
        <el-form-item label="批次 ID">
          <el-select v-model="filters.batchId" placeholder="选择批次" clearable>
            <el-option 
              v-for="batch in batches" 
              :key="batch.id" 
              :label="formatBatchLabel(batch)" 
              :value="batch.id" 
            />
          </el-select>
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
          <el-button link @click="showAdvanced = !showAdvanced">
            {{ showAdvanced ? '收起高级筛选' : '展开高级筛选' }}
          </el-button>
        </el-form-item>

        <div v-if="showAdvanced" class="w-full flex flex-wrap gap-6 mt-4 border-t pt-4">
          <el-form-item label="价格区间">
            <el-input-number v-model="filters.minPrice" :min="0" placeholder="Min" style="width: 100px" />
            <span class="mx-2">-</span>
            <el-input-number v-model="filters.maxPrice" :min="0" placeholder="Max" style="width: 100px" />
          </el-form-item>
          <el-form-item label="评分区间">
            <el-input-number v-model="filters.minRating" :min="0" :max="5" :step="0.1" placeholder="Min" style="width: 100px" />
            <span class="mx-2">-</span>
            <el-input-number v-model="filters.maxRating" :min="0" :max="5" :step="0.1" placeholder="Max" style="width: 100px" />
          </el-form-item>
          <el-form-item label="评论数">
            <el-input-number v-model="filters.minReviews" :min="0" placeholder="Min" style="width: 100px" />
            <span class="mx-2">-</span>
            <el-input-number v-model="filters.maxReviews" :min="0" placeholder="Max" style="width: 100px" />
          </el-form-item>
          <el-form-item label="排名区间">
            <el-input-number v-model="filters.minRank" :min="0" placeholder="Min" style="width: 100px" />
            <span class="mx-2">-</span>
            <el-input-number v-model="filters.maxRank" :min="0" placeholder="Max" style="width: 100px" />
          </el-form-item>
          <el-form-item label="类目">
            <el-input v-model="filters.category" placeholder="输入类目关键词" clearable />
          </el-form-item>
        </div>
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
          <el-popover placement="bottom-end" :width="200" trigger="click">
            <template #reference>
              <el-button>列设置</el-button>
            </template>
            <div class="flex flex-col gap-2">
              <el-checkbox v-model="columnVisibility.asin" :label="columnLabels.asin" />
              <el-checkbox v-model="columnVisibility.title" :label="columnLabels.title" />
              <el-checkbox v-model="columnVisibility.brand" :label="columnLabels.brand" />
              <el-checkbox v-model="columnVisibility.category" :label="columnLabels.category" />
              <el-checkbox v-model="columnVisibility.batch_id" :label="columnLabels.batch_id" />
              <el-checkbox v-model="columnVisibility.validation_status" :label="columnLabels.validation_status" />
              <el-checkbox v-model="columnVisibility.ingested_at" :label="columnLabels.ingested_at" />
              <el-checkbox v-model="columnVisibility.price" :label="columnLabels.price" />
              <el-checkbox v-model="columnVisibility.rating" :label="columnLabels.rating" />
              <el-checkbox v-model="columnVisibility.reviews" :label="columnLabels.reviews" />
              <el-checkbox v-model="columnVisibility.sales_rank" :label="columnLabels.sales_rank" />
            </div>
          </el-popover>
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
        <el-table-column v-if="columnVisibility.asin" prop="asin" label="ASIN" sortable="custom" width="140" />
        <el-table-column v-if="columnVisibility.title" prop="title" label="标题" min-width="240" show-overflow-tooltip />
        <el-table-column v-if="columnVisibility.brand" prop="brand" label="品牌" width="120" show-overflow-tooltip />
        <el-table-column v-if="columnVisibility.category" prop="category" label="类目" width="120" show-overflow-tooltip />
        <el-table-column v-if="columnVisibility.batch_id" label="批次编号" sortable="custom" prop="batch_id" width="120">
          <template #default="{ row }">
            <span class="font-mono">#{{ row.batch_id }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="columnVisibility.validation_status" prop="validation_status" label="状态" width="100" :formatter="formatStatusCell" />
        <el-table-column
          v-if="columnVisibility.ingested_at"
          prop="ingested_at"
          label="更新时间"
          sortable="custom"
          width="170"
          :formatter="formatTimeCell"
        />
        <el-table-column v-if="columnVisibility.price" label="价格" width="140">
          <template #default="{ row }">
            <span>{{ row.currency }} {{ row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="columnVisibility.rating" prop="rating" label="评分" width="100" />
        <el-table-column v-if="columnVisibility.reviews" prop="reviews" label="评论数" width="100" />
        <el-table-column v-if="columnVisibility.sales_rank" prop="sales_rank" label="排名" width="120" />
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

        <div v-if="selectedProduct.raw_payload" class="mt-6">
          <h3 class="text-lg font-bold mb-4">原始数据</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item 
              v-for="(value, key) in selectedProduct.raw_payload" 
              :key="key" 
              :label="key"
            >
              {{ value }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { isAxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { http, API_BASE } from '@/utils/http'
import type { ProductItem, ProductQueryParams } from './types'

import dayjs from 'dayjs'

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
        minPrice: parsed.minPrice,
        maxPrice: parsed.maxPrice,
        minRating: parsed.minRating,
        maxRating: parsed.maxRating,
        minReviews: parsed.minReviews,
        maxReviews: parsed.maxReviews,
        minRank: parsed.minRank,
        maxRank: parsed.maxRank,
        category: parsed.category || '',
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
      minPrice: filters.minPrice,
      maxPrice: filters.maxPrice,
      minRating: filters.minRating,
      maxRating: filters.maxRating,
      minReviews: filters.minReviews,
      maxReviews: filters.maxReviews,
      minRank: filters.minRank,
      maxRank: filters.maxRank,
      category: filters.category,
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
  batchId: '' as string | number,
  asin: '',
  status: '',
  dateRange: [] as string[],
  minPrice: undefined as number | undefined,
  maxPrice: undefined as number | undefined,
  minRating: undefined as number | undefined,
  maxRating: undefined as number | undefined,
  minReviews: undefined as number | undefined,
  maxReviews: undefined as number | undefined,
  minRank: undefined as number | undefined,
  maxRank: undefined as number | undefined,
  category: '',
  sortBy: '',
  sortOrder: '' as 'asc' | 'desc' | '',
  page: 1,
  pageSize: 20
})

// 监听筛选条件变化并保存
watch(filters, (newFilters) => {
  saveFiltersToStorage(newFilters)
}, { deep: true })

const batches = ref<any[]>([])

const fetchBatches = async () => {
  try {
    const { data } = await http.get(`${API_BASE}/imports`, {
      params: { pageSize: 100 }
    })
    batches.value = data.items || []
  } catch (err) {
    console.error('Fetch batches failed:', err)
  }
}

const formatBatchLabel = (batch: any) => {
  const time = dayjs(batch.created_at).format('YYYYMMDD HH:mm:ss')
  return `${batch.id} - ${time}`
}


const showAdvanced = ref(false)
const products = ref<ProductItem[]>([])
const total = ref(0)
const loading = ref(false)
const errorMessage = ref('')
const detailVisible = ref(false)
const selectedProduct = ref<ProductItem | null>(null)
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
    sortOrder: (filters.sortOrder as 'asc' | 'desc') || undefined,
    minPrice: filters.minPrice,
    maxPrice: filters.maxPrice,
    minRating: filters.minRating,
    maxRating: filters.maxRating,
    minReviews: filters.minReviews,
    maxReviews: filters.maxReviews,
    minRank: filters.minRank,
    maxRank: filters.maxRank,
    category: filters.category || undefined
  }
  if (filters.dateRange?.length === 2) {
    params.updated_from = filters.dateRange[0]
    params.updated_to = filters.dateRange[1]
  }
  return params
}

type RawProduct = Record<string, unknown>

const normalizeProduct = (raw: RawProduct): ProductItem => {
  const attributes = (raw.attributes as Record<string, unknown>) || {}
  const rawPayload = (raw.rawPayload as Record<string, unknown>) || (raw.raw_payload as Record<string, unknown>) || {}
  
  // 尝试从 attributes 或 rawPayload 中获取 brand
  const brand = (attributes.brand as string) || (rawPayload.Brand as string) || (rawPayload.brand as string) || (rawPayload['品牌'] as string) || null

  return {
    id: String(raw.id ?? ''),
    asin: String(raw.asin ?? ''),
    title: String(raw.title ?? ''),
    batch_id: Number(raw.batchId ?? raw.batch_id ?? 0),
    ingested_at: String(raw.ingestedAt ?? raw.ingested_at ?? ''),
    validation_status: String(raw.validationStatus ?? raw.validation_status ?? ''),
    validation_messages: (raw.validationMessages as Record<string, unknown> | null) ??
      (raw.validation_messages as Record<string, unknown> | null) ??
      null,
    price: typeof raw.price === 'number' ? raw.price : null,
    currency: String(raw.currency ?? ''),
    rating: typeof raw.rating === 'number' ? raw.rating : null,
    reviews: typeof raw.reviews === 'number' ? raw.reviews : null,
    sales_rank:
      typeof raw.salesRank === 'number'
        ? raw.salesRank
        : typeof raw.sales_rank === 'number'
          ? raw.sales_rank
          : null,
    category: String(raw.category ?? ''),
    brand: brand,
    raw_payload: rawPayload
  }
}

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
        updated_to: params.updated_to,
        minPrice: params.minPrice,
        maxPrice: params.maxPrice,
        minRating: params.minRating,
        maxRating: params.maxRating,
        minReviews: params.minReviews,
        maxReviews: params.maxReviews,
        minRank: params.minRank,
        maxRank: params.maxRank,
        category: params.category
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
  filters.minPrice = undefined
  filters.maxPrice = undefined
  filters.minRating = undefined
  filters.maxRating = undefined
  filters.minReviews = undefined
  filters.maxReviews = undefined
  filters.minRank = undefined
  filters.maxRank = undefined
  filters.category = ''
  filters.sortBy = ''
  filters.sortOrder = ''
  filters.page = 1
  filters.pageSize = 20
  trackEvent('filter_reset')
  fetchProducts(true)
}

const reload = () => fetchProducts()

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

const route = useRoute()

const COLUMN_SETTINGS_KEY = 'insight_column_settings'

const columnLabels = {
  asin: 'ASIN',
  title: '标题',
  brand: '品牌',
  category: '类目',
  batch_id: '批次编号',
  validation_status: '状态',
  ingested_at: '更新时间',
  price: '价格',
  rating: '评分',
  reviews: '评论数',
  sales_rank: '排名'
}

const columnVisibility = reactive({
  asin: true,
  title: true,
  brand: true,
  category: true,
  batch_id: true,
  validation_status: true,
  ingested_at: true,
  price: true,
  rating: true,
  reviews: true,
  sales_rank: true
})

// 加载列设置
const loadColumnSettings = () => {
  try {
    const stored = localStorage.getItem(COLUMN_SETTINGS_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      Object.assign(columnVisibility, parsed)
    }
  } catch (e) {
    console.warn('Failed to load column settings:', e)
  }
}

// 监听并保存列设置
watch(columnVisibility, (newSettings) => {
  localStorage.setItem(COLUMN_SETTINGS_KEY, JSON.stringify(newSettings))
}, { deep: true })

onMounted(() => {
  loadColumnSettings()
  fetchBatches()
  if (route.query.batchId) {
    filters.batchId = Number(route.query.batchId)
  }
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
</style>
