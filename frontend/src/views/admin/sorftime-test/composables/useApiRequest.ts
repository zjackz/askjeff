import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * API 请求 Composable
 * 处理 Sorftime API 的请求和响应
 */
export function useApiRequest() {
    const loading = ref(false)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = ref<any>(null)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const error = ref<any>(null)
    const responseStatus = ref<{ code: number, text: string, time: number } | null>(null)

    // 创建 API 实例
    const getBaseUrl = () => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const url = (import.meta as any).env.VITE_API_BASE_URL || '/api/v1'
        if (url.endsWith('/api/v1')) return url
        return url.replace(/\/$/, '') + '/api/v1'
    }

    const api = axios.create({
        baseURL: getBaseUrl()
    })

    api.interceptors.request.use(config => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    })

    /**
     * 业务状态码解析
     */
    const businessStatus = computed(() => {
        if (!response.value) return null

        const code = response.value.Code ?? response.value.code
        const msg = response.value.Message ?? response.value.message

        // Sorftime 错误码映射
        const errorMap: Record<number, string> = {
            0: 'Success',
            9: 'Access Restricted',
            10: 'Parameter Error',
            400: 'Unauthorized IP',
            401: 'Interface Not Open',
            402: 'No Permission',
            500: 'Monthly Limit Reached',
            501: 'Minute Limit Reached',
            694: 'Insufficient Request Quota (余额不足)'
        }

        const desc = errorMap[code] || msg || 'Unknown Status'

        return {
            code,
            text: desc,
            isError: code !== 0
        }
    })

    /**
     * 发送 API 请求
     */
    const sendRequest = async (endpoint: string, payload: any) => {
        loading.value = true
        response.value = null
        error.value = null
        responseStatus.value = null
        const startTime = Date.now()

        try {
            const res = await api.post(`/sorftime/test/${endpoint}`, payload)

            response.value = res.data
            responseStatus.value = {
                code: res.status,
                text: res.statusText,
                time: Date.now() - startTime
            }

            return {
                success: true,
                startTime,
                statusCode: res.status
            }
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error(err)
            error.value = err.response?.data || err.message
            responseStatus.value = {
                code: err.response?.status || 0,
                text: err.response?.statusText || 'Error',
                time: Date.now() - startTime
            }

            return {
                success: false,
                startTime,
                statusCode: err.response?.status || 0
            }
        } finally {
            loading.value = false
        }
    }

    /**
     * 复制响应到剪贴板
     */
    const copyResponse = () => {
        if (response.value) {
            navigator.clipboard.writeText(JSON.stringify(response.value, null, 2))
            ElMessage.success('Response copied to clipboard')
        }
    }

    return {
        loading,
        response,
        error,
        responseStatus,
        businessStatus,
        sendRequest,
        copyResponse
    }
}
