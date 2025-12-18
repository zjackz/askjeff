import { reactive, ref, watch, onMounted } from 'vue'
import { isAxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { http, API_BASE } from '@/utils/http'
import type { ProductItem, ProductQueryParams, ProductFilters } from '../types'
import dayjs from 'dayjs'

const FILTER_STORAGE_KEY = 'insight_filters'

export function useProductList() {
    // 从 sessionStorage 加载筛选条件
    const loadFiltersFromStorage = (): ProductFilters | null => {
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
                    page: 1,
                    pageSize: parsed.pageSize || 20
                }
            }
        } catch (e) {
            console.warn('Failed to load filters from storage:', e)
        }
        return null
    }

    const savedFilters = loadFiltersFromStorage()
    const filters = reactive<ProductFilters>(savedFilters || {
        batchId: '',
        asin: '',
        status: '',
        dateRange: [],
        minPrice: undefined,
        maxPrice: undefined,
        minRating: undefined,
        maxRating: undefined,
        minReviews: undefined,
        maxReviews: undefined,
        minRank: undefined,
        maxRank: undefined,
        category: '',
        sortBy: '',
        sortOrder: '',
        page: 1,
        pageSize: 20
    })

    // 保存筛选条件到 sessionStorage
    const saveFiltersToStorage = (filters: ProductFilters) => {
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

    watch(filters, (newFilters) => {
        saveFiltersToStorage(newFilters)
    }, { deep: true })

    const products = ref<ProductItem[]>([])
    const total = ref(0)
    const loading = ref(false)
    const errorMessage = ref('')
    const batches = ref<any[]>([])
    const exportLoading = ref(false)

    const fetchBatches = async () => {
        try {
            const { data } = await http.get('/imports', {
                params: { pageSize: 100 }
            })
            batches.value = data.items || []
        } catch (err) {
            console.error('Fetch batches failed:', err)
        }
    }

    const buildQueryParams = (): ProductQueryParams => {
        const params: ProductQueryParams = {
            batchId: filters.batchId ? String(filters.batchId) : undefined,
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

    const normalizeProduct = (raw: any): ProductItem => {
        const attributes = (raw.attributes as Record<string, unknown>) || {}
        const rawPayload = (raw.rawPayload as Record<string, unknown>) || (raw.raw_payload as Record<string, unknown>) || {}
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
            raw_payload: rawPayload,
            title_cn: (rawPayload.title_cn as string) || null,
            bullets_cn: (rawPayload.bullets_cn as string) || null
        }
    }

    const fetchProducts = async (resetPage = false) => {
        if (resetPage) {
            filters.page = 1
        }
        loading.value = true
        errorMessage.value = ''
        try {
            const params = buildQueryParams()
            const { data } = await http.get('/products', { params })
            products.value = (data?.items ?? []).map(normalizeProduct)
            total.value = data?.total || 0
        } catch (err: unknown) {
            if (isAxiosError(err)) {
                errorMessage.value = err.response?.data?.detail || err.message
            } else {
                errorMessage.value = '获取产品列表失败'
            }
            console.error(err)
        } finally {
            loading.value = false
        }
    }

    const exportCurrentFilters = async () => {
        if (exportLoading.value) return
        exportLoading.value = true
        try {
            const params = buildQueryParams()
            const payload = {
                exportType: 'clean-products',
                selectedFields: ['asin', 'title', 'price', 'batch_id', 'validation_status'],
                filters: {
                    batch_id: params.batchId,
                    asin: params.asin,
                    validation_status: params.status,
                    updated_from: params.updated_from,
                    updated_to: params.updated_to
                },
                fileFormat: 'csv'
            }
            const { data } = await http.post('/exports', payload)
            if (data.status === 'succeeded' && data.fileUrl) {
                const downloadUrl = `${API_BASE}/api${data.fileUrl}`
                const link = document.createElement('a')
                link.href = downloadUrl
                link.setAttribute('download', `export-${data.id}.csv`)
                document.body.appendChild(link)
                link.click()
                document.body.removeChild(link)
                ElMessage.success('导出成功，正在下载...')
            } else {
                ElMessage.warning(`导出任务状态: ${data.status}，请稍后查看`)
            }
        } catch (err: unknown) {
            ElMessage.error('导出失败')
            console.error(err)
        } finally {
            exportLoading.value = false
        }
    }

    return {
        filters,
        products,
        total,
        loading,
        errorMessage,
        batches,
        exportLoading,
        fetchBatches,
        fetchProducts,
        exportCurrentFilters
    }
}
