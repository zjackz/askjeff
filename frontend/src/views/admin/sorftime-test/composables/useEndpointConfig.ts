import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { API_EXAMPLES } from '../../sorftime-examples'
import type { EndpointType } from './useRequestHistory'

export interface ApiDoc {
    title: string
    description: string
    note?: string
    cost: string
}

/**
 * API 端点配置 Composable
 * 包含所有 API 文档和示例数据
 */
export function useEndpointConfig(activeEndpoint: any, form: any) {
    // API 文档配置
    const apiDocs: Record<EndpointType, ApiDoc> = {
        'product': {
            title: 'ProductRequest',
            description: '产品（Listing）详情查询。',
            note: '当ASIN不存在或链接变狗时不会返回数据（这种场景下我们为了确保产品状态，会实时抓一次产品详情），request仍然会消耗。',
            cost: '按ASIN数量扣费'
        },
        'category': {
            title: 'CategoryRequest',
            description: '类目Best Sellers查询。查询类目Best Seller Top100产品。',
            cost: '5 request'
        },
        'category-tree': {
            title: 'CategoryTree',
            description: '返回Best Seller类目树结构。',
            note: '这个接口返回数据很大（约为10mb+）建议设置较长请求超时时间。',
            cost: '5 request'
        },
        'category-trend': {
            title: 'CategoryTrend',
            description: '类目趋势数据查询。',
            cost: '5 request'
        },
        'category-products': {
            title: 'CategoryProducts',
            description: '类目全部热销产品。查询类目下全部热销产品，对于长尾类目可返回1000+产品。',
            cost: '5 request'
        },
        'product-query': {
            title: 'ProductQuery',
            description: '多维度产品搜索。',
            cost: '5 request'
        },
        'keyword-query': {
            title: 'KeywordQuery',
            description: '关键词搜索。',
            cost: '5 request'
        },
        'keyword-detail': {
            title: 'KeywordRequest',
            description: '关键词详情查询。',
            cost: '5 request'
        },
        'keyword-search-results': {
            title: 'KeywordSearchResults',
            description: '关键词近15日搜索结果产品。仅支持ABA热搜词。',
            cost: '5 request'
        },
        'asin-sales-volume': {
            title: 'AsinSalesVolume',
            description: '产品官方公布子体销量。查询产品官方公布的子体销量历史数据。',
            cost: '1 request'
        },
        'product-variation-history': {
            title: 'ProductVariationHistory',
            description: '产品子体变化历史数据查询。',
            cost: '1 request'
        },
        'product-trend': {
            title: 'ProductTrend',
            description: '产品趋势数据查询（文档标注：未开发/设计中）。',
            cost: '1 request'
        },
        'product-realtime': {
            title: 'ProductRealtimeRequest',
            description: '产品实时数据查询。如果产品设定时间内未更新过，则实时抓取。',
            cost: '1 积分 (JP: 2积分)'
        },
        'product-realtime-status': {
            title: 'ProductRealtimeRequestStatusQuery',
            description: '产品实时数据查询状态查询。',
            cost: '0 request'
        },
        'reviews-collection': {
            title: 'ProductReviewsCollection',
            description: '实时采集产品评论。仅采集，不返回内容。',
            cost: '按页数扣积分 (1积分/页)'
        },
        'reviews-collection-status': {
            title: 'ProductReviewsCollectionStatusQuery',
            description: '评论实时查询任务状态查询。',
            cost: '0 request'
        },
        'reviews-query': {
            title: 'ProductReviewsQuery',
            description: '查询我们已经收录的产品评论。',
            cost: '5 request'
        },
        'similar-product-realtime': {
            title: 'SimilarProductRealtimeRequest',
            description: '图搜相似产品。通过产品图片实时搜索亚马逊平台上相似产品。',
            cost: '5 积分 (JP: 6积分)'
        },
        'similar-product-status': {
            title: 'SimilarProductRealtimeRequestStatusQuery',
            description: '图搜相似产品任务状态查询。',
            cost: '0 request'
        },
        'similar-product-result': {
            title: 'SimilarProductRealtimeRequestCollection',
            description: '图搜相似产品结果查询。',
            cost: '0 request'
        },
        'keyword-search-result-trend': { title: 'KeywordSearchResultTrend', description: '关键词搜索结果产品趋势', cost: '5 request' },
        'category-request-keyword': { title: 'CategoryRequestKeyword', description: '类目反查关键词', cost: '5 request' },
        'asin-request-keyword': { title: 'ASINRequestKeyword', description: 'ASIN反查关键词', cost: '5 request' },
        'keyword-product-ranking': { title: 'KeywordProductRanking', description: '关键词搜索结果产品排名', cost: '2 request' },
        'asin-keyword-ranking': { title: 'ASINKeywordRanking', description: 'ASIN在关键词下排名趋势', cost: '2 request' },
        'keyword-subscription': { title: 'KeywordSubscription', description: '关键词监控任务注册', cost: '0 request' },
        'keyword-tasks': { title: 'KeywordTasks', description: '关键词监控任务查询', cost: '0 request' },
        'keyword-task-update': { title: 'KeywordTaskUpdate', description: '修改关键词监控任务', cost: '0 request' },
        'keyword-batch-schedule-list': { title: 'KeywordBatchScheduleList', description: '查询关键词监控任务执行批次', cost: '0 request' },
        'keyword-batch-schedule-detail': { title: 'KeywordBatchScheduleDetail', description: '提取关键词监控产品列表详细数据', cost: '0 request' },
        'best-seller-list-subscription': { title: 'BestSellerListSubscription', description: '榜单监控任务注册', cost: '0 request' },
        'best-seller-list-task': { title: 'BestSellerListTask', description: '榜单监控任务查询', cost: '0 request' },
        'best-seller-list-delete': { title: 'BestSellerListDelete', description: '榜单监控任务删除', cost: '0 request' },
        'best-seller-list-data-collect': { title: 'BestSellerListDataCollect', description: '榜单监控数据提取', cost: '0 request' },
        'product-seller-subscription': { title: 'ProductSellerSubscription', description: '跟卖&库存监控', cost: '0 request' },
        'product-seller-tasks': { title: 'ProductSellerTasks', description: '跟卖&库存监控任务查询', cost: '0 request' },
        'product-seller-task-update': { title: 'ProductSellerTaskUpdate', description: '修改跟卖&库存监控任务', cost: '0 request' },
        'product-seller-task-schedule-list': { title: 'ProductSellerTaskScheduleList', description: '查询跟卖&库存监控任务执行批次', cost: '0 request' },
        'product-seller-task-schedule-detail': { title: 'ProductSellerTaskScheduleDetail', description: '提取跟卖&库存监控执行结果详细数据', cost: '0 request' },
        'asin-subscription': { title: 'ASINSubscription', description: 'ASIN更新订阅', cost: '0 request' },
        'asin-subscription-query': { title: 'ASINSubscriptionQuery', description: 'ASIN订阅查询', cost: '0 request' },
        'asin-subscription-collection': { title: 'ASINSubscriptionCollection', description: 'ASIN订阅结果数据查询', cost: '0 request' },
        'coin-query': { title: 'CoinQuery', description: '本月剩余积分查询', cost: '1 request' },
        'coin-stream': { title: 'CoinStream', description: '积分使用明细查询', cost: '1 request' },
        'request-stream': { title: 'RequestStream', description: '月度Request使用明细查询', cost: '1 request' }
    }

    // 当前文档
    const currentDoc = computed(() => apiDocs[activeEndpoint.value as EndpointType])

    /**
     * 加载示例数据
     */
    const loadExample = () => {
        const example = API_EXAMPLES[activeEndpoint.value as keyof typeof API_EXAMPLES]
        if (example) {
            Object.assign(form, example)
            ElMessage.success(`已加载 ${currentDoc.value.title} 的示例数据`)
        } else {
            ElMessage.warning('该 API 暂无示例数据')
        }
    }

    /**
     * 计算请求 payload
     */
    const getRequestPayload = () => {
        const base = { domain: form.domain }

        switch (activeEndpoint.value) {
            case 'product':
                return {
                    ...base,
                    ASIN: form.asins.split(/[\n,]/).map((s: string) => s.trim()).filter((s: string) => s).join(','),
                    Trend: 1
                }
            case 'category':
                return { ...base, nodeId: form.nodeId }
            case 'category-tree':
                return { ...base }
            case 'category-trend':
                return { ...base, nodeId: form.nodeId, trendIndex: form.trendIndex }
            case 'category-products':
                return { ...base, nodeId: form.nodeId, page: form.page }
            case 'product-query':
                return {
                    ...base,
                    query: 1,
                    queryType: form.queryType,
                    pattern: form.pattern,
                    page: form.page
                }
            case 'keyword-query':
                return { ...base, pattern: { keyword: form.keyword }, pageIndex: form.page }
            case 'keyword-detail':
                return { ...base, keyword: form.keyword }
            case 'keyword-search-results':
                return { ...base, keyword: form.keyword, pageIndex: form.page }
            case 'asin-sales-volume':
                return { ...base, asin: form.asins.trim(), queryDate: form.queryStart, queryEndDate: form.queryEnd, page: form.page }
            case 'product-variation-history':
                return { ...base, asin: form.asins.trim() }
            case 'product-trend':
                return {
                    ...base,
                    asin: form.asins.trim(),
                    dateRange: form.queryStart && form.queryEnd ? `${form.queryStart},${form.queryEnd}` : '',
                    trendType: form.trendIndex
                }
            case 'product-realtime':
                return { ...base, asin: form.asins.trim(), update: form.update }
            case 'product-realtime-status':
                return { ...base, queryDate: form.queryStart }
            case 'reviews-collection':
                return {
                    ...base,
                    asin: form.asins.trim(),
                    mode: form.mode,
                    star: form.star,
                    onlyPurchase: form.onlyPurchase,
                    page: form.page
                }
            case 'reviews-collection-status':
                return { ...base, asin: form.asins.trim(), update: form.update }
            case 'reviews-query':
                return {
                    ...base,
                    asin: form.asins.trim(),
                    querystartdt: form.queryStart,
                    star: form.star,
                    onlyPurchase: form.onlyPurchase,
                    pageIndex: form.page
                }
            case 'similar-product-realtime':
                return { ...base, image: form.image }
            case 'similar-product-status':
                return { ...base, Update: form.update }
            case 'similar-product-result':
                return { ...base, taskId: form.taskId }
            case 'keyword-search-result-trend':
                return { ...base, keyword: form.keyword, pageIndex: form.page }
            case 'category-request-keyword':
                return { ...base, nodeId: form.nodeId, pageIndex: form.page }
            case 'asin-request-keyword':
                return { ...base, asin: form.asins.trim(), pageIndex: form.page }
            case 'keyword-product-ranking':
                return { ...base, keyword: form.keyword, pageIndex: form.page }
            case 'asin-keyword-ranking':
                return { ...base, keyword: form.keyword, asin: form.asins.trim(), queryStart: form.queryStart, queryEnd: form.queryEnd, page: form.page }
            case 'keyword-subscription':
            case 'best-seller-list-subscription':
            case 'product-seller-subscription':
            case 'asin-subscription':
                return { ...base, content: form.asins }
            case 'keyword-tasks':
            case 'best-seller-list-task':
            case 'product-seller-tasks':
            case 'asin-subscription-query':
                return { ...base, pageIndex: form.page }
            case 'keyword-task-update':
            case 'product-seller-task-update':
                return { ...base, taskId: form.taskId, update: form.update }
            case 'keyword-batch-schedule-list':
            case 'product-seller-task-schedule-list':
                return { ...base, taskId: form.taskId }
            case 'keyword-batch-schedule-detail':
            case 'product-seller-task-schedule-detail':
                return { ...base, scheduleId: form.taskId }
            case 'best-seller-list-delete':
                return { ...base, taskId: form.taskId }
            case 'best-seller-list-data-collect':
                return { ...base, taskId: form.taskId, queryDate: form.queryStart }
            case 'asin-subscription-collection':
                return { ...base, asins: form.asins }
            case 'coin-query':
                return { ...base }
            case 'coin-stream':
            case 'request-stream':
                return { ...base, platform: 0, pageIndex: form.page }
            default:
                return {}
        }
    }

    return {
        apiDocs,
        currentDoc,
        loadExample,
        getRequestPayload
    }
}
