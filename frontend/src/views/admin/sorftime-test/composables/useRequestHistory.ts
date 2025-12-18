import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

export type EndpointType =
    | 'product'
    | 'category'
    | 'category-tree'
    | 'category-trend'
    | 'category-products'
    | 'product-query'
    | 'keyword-query'
    | 'keyword-detail'
    | 'keyword-search-results'
    | 'asin-sales-volume'
    | 'product-variation-history'
    | 'product-trend'
    | 'product-realtime'
    | 'product-realtime-status'
    | 'reviews-collection'
    | 'reviews-collection-status'
    | 'reviews-query'
    | 'similar-product-realtime'
    | 'similar-product-status'
    | 'similar-product-result'
    | 'keyword-search-result-trend'
    | 'category-request-keyword'
    | 'asin-request-keyword'
    | 'keyword-product-ranking'
    | 'asin-keyword-ranking'
    | 'keyword-subscription'
    | 'keyword-tasks'
    | 'keyword-task-update'
    | 'keyword-batch-schedule-list'
    | 'keyword-batch-schedule-detail'
    | 'best-seller-list-subscription'
    | 'best-seller-list-task'
    | 'best-seller-list-delete'
    | 'best-seller-list-data-collect'
    | 'product-seller-subscription'
    | 'product-seller-tasks'
    | 'product-seller-task-update'
    | 'product-seller-task-schedule-list'
    | 'product-seller-task-schedule-detail'
    | 'asin-subscription'
    | 'asin-subscription-query'
    | 'asin-subscription-collection'
    | 'coin-query'
    | 'coin-stream'
    | 'request-stream'

export interface RequestHistoryItem {
    id: string
    timestamp: number
    endpoint: EndpointType
    params: Record<string, any>
    success: boolean
    responseTime: number
    statusCode: number
}

/**
 * 请求历史管理 Composable
 */
export function useRequestHistory() {
    const requestHistory = ref<RequestHistoryItem[]>([])

    const sessionStats = reactive({
        total: 0,
        success: 0,
        failed: 0,
        totalTime: 0,
        estimatedCost: 0
    })

    // 计算统计数据
    const successRate = computed(() => {
        if (sessionStats.total === 0) return 0
        return Math.round((sessionStats.success / sessionStats.total) * 100)
    })

    const avgResponseTime = computed(() => {
        if (sessionStats.total === 0) return 0
        return Math.round(sessionStats.totalTime / sessionStats.total)
    })

    /**
     * 保存请求到历史记录
     */
    const saveToHistory = (
        endpoint: EndpointType,
        params: Record<string, any>,
        startTime: number,
        success: boolean,
        statusCode: number,
        cost: number
    ) => {
        const historyItem: RequestHistoryItem = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            timestamp: Date.now(),
            endpoint,
            params: { ...params },
            success,
            responseTime: Date.now() - startTime,
            statusCode
        }

        requestHistory.value.unshift(historyItem)
        if (requestHistory.value.length > 20) {
            requestHistory.value = requestHistory.value.slice(0, 20)
        }

        // 保存到 localStorage
        try {
            localStorage.setItem('sorftime_history', JSON.stringify(requestHistory.value))
        } catch (e) {
            console.warn('Failed to save history to localStorage:', e)
        }

        // 更新会话统计
        sessionStats.total++
        if (success) {
            sessionStats.success++
        } else {
            sessionStats.failed++
        }
        sessionStats.totalTime += historyItem.responseTime
        sessionStats.estimatedCost += cost
    }

    /**
     * 从 localStorage 加载历史记录
     */
    const loadHistory = () => {
        try {
            const saved = localStorage.getItem('sorftime_history')
            if (saved) {
                requestHistory.value = JSON.parse(saved)
            }
        } catch (e) {
            console.warn('Failed to load history from localStorage:', e)
        }
    }

    /**
     * 删除单条历史记录
     */
    const deleteHistoryItem = (id: string) => {
        const index = requestHistory.value.findIndex(item => item.id === id)
        if (index !== -1) {
            requestHistory.value.splice(index, 1)
            localStorage.setItem('sorftime_history', JSON.stringify(requestHistory.value))
            ElMessage.success('已删除')
        }
    }

    /**
     * 清空所有历史记录
     */
    const clearHistory = () => {
        requestHistory.value = []
        localStorage.removeItem('sorftime_history')
        ElMessage.success('历史记录已清空')
    }

    /**
     * 格式化时间显示
     */
    const formatTime = (timestamp: number) => {
        const date = new Date(timestamp)
        const now = new Date()
        const diff = now.getTime() - date.getTime()

        if (diff < 60000) return '刚刚'
        if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`

        return date.toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    return {
        requestHistory,
        sessionStats,
        successRate,
        avgResponseTime,
        saveToHistory,
        loadHistory,
        deleteHistoryItem,
        clearHistory,
        formatTime
    }
}
