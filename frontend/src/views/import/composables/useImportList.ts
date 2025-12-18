import { ref, onMounted } from 'vue'
import { http } from '@/utils/http'
import { useIntervalFn } from '@vueuse/core'
import type { BatchRow } from '../types'

export function useImportList() {
    const loading = ref(false)
    const batches = ref<BatchRow[]>([])
    const currentPage = ref(1)
    const pageSize = ref(50)
    const total = ref(0)

    const calculateDuration = (start?: string, end?: string) => {
        if (!start || !end) return null
        const diff = new Date(end).getTime() - new Date(start).getTime()
        if (diff < 1000) return '< 1s'
        return `${(diff / 1000).toFixed(1)}s`
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

            if (hasActiveTasks && !isPolling.value) {
                resume()
            } else if (!hasActiveTasks && isPolling.value) {
                // Optional: pause if no active tasks
                // pause()
            }
        } catch (err) {
            console.error('Fetch batches failed:', err)
            pause()
        } finally {
            if (!silent) loading.value = false
        }
    }

    const { pause, resume, isActive: isPolling } = useIntervalFn(() => {
        fetchBatches(true)
    }, 5000)

    const handleCurrentChange = (val: number) => {
        currentPage.value = val
        fetchBatches()
    }

    const handleSizeChange = (val: number) => {
        pageSize.value = val
        fetchBatches()
    }

    onMounted(() => {
        fetchBatches()
    })

    return {
        loading,
        batches,
        currentPage,
        pageSize,
        total,
        fetchBatches,
        handleCurrentChange,
        handleSizeChange,
        isPolling,
        pause,
        resume
    }
}
