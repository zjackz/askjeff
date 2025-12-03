import axios, { AxiosError } from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api'

// 扩展 AxiosRequestConfig 类型以支持自定义配置
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    __retryCount?: number
    skipGlobalErrorHandler?: boolean
  }
}

const http: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 10000
})

const ingestPath = '/logs/ingest'

// HTTP 状态码中文映射
const HTTP_STATUS_MAP: Record<number, string> = {
  400: '请求参数错误',
  401: '登录已过期,请重新登录',
  403: '没有权限执行此操作',
  404: '请求的资源不存在',
  405: '请求方法不允许',
  408: '请求超时',
  413: '请求体过大',
  422: '参数验证失败',
  500: '服务器内部错误',
  502: '网关错误',
  503: '服务不可用',
  504: '网关超时'
}

async function reportClientError(error: AxiosError) {
  try {
    // 避免递归上报
    if (error.config?.url && error.config.url.includes(ingestPath)) return
    await axios.post(
      `${API_BASE}${ingestPath}`,
      {
        level: 'error',
        category: 'frontend',
        message: error.message,
        context: {
          url: error.config?.url,
          method: error.config?.method,
          status: error.response?.status,
          data: error.config?.data,
          response: error.response?.data,
          code: error.code
        }
      },
      { timeout: 5000 }
    )
  } catch {
    // 上报失败时静默处理,避免阻塞用户操作
  }
}

http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

http.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    // 1. 上报错误日志
    await reportClientError(error)

    // 2. 网络错误或超时,自动重试
    if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
      const config = error.config

      if (config) {
        // 如果还没有重试次数记录,初始化为 0
        config.__retryCount = config.__retryCount || 0

        // 最多重试 3 次
        if (config.__retryCount < 3) {
          config.__retryCount += 1
          console.log(`网络错误,正在重试 (${config.__retryCount}/3)...`)

          // 延迟后重试
          await new Promise(resolve => setTimeout(resolve, 1000 * config.__retryCount))
          return http(config)
        }
      }
    }

    // 3. 全局错误提示 (除非显式跳过)
    if (error.config?.skipGlobalErrorHandler) {
      return Promise.reject(error)
    }

    // 处理错误响应
    const status = error.response?.status
    const responseData = error.response?.data as any

    // 新的错误响应格式: { error: { code, message, details } }
    if (responseData?.error) {
      const { code, message, details } = responseData.error

      // 根据错误码显示用户友好的提示
      const userMessage = getUserFriendlyMessage(code, message, details)
      ElMessage.error(userMessage)

      // 记录详细错误信息到控制台
      console.error('API Error:', { code, message, details, status })
    }
    // 兼容旧的错误格式
    else if (responseData?.detail) {
      const detail = typeof responseData.detail === 'string'
        ? responseData.detail
        : JSON.stringify(responseData.detail)
      ElMessage.error(detail)
    }
    // HTTP 状态码错误
    else if (status) {
      ElMessage.error(HTTP_STATUS_MAP[status] || `请求失败 (${status})`)
    }
    // 网络错误
    else if (error.message.includes('timeout')) {
      ElMessage.error('请求超时,请检查网络')
    } else if (!window.navigator.onLine) {
      ElMessage.error('网络连接已断开')
    } else {
      ElMessage.error('网络连接失败,请检查网络后重试')
    }

    return Promise.reject(error)
  }
)

/**
 * 将技术错误码转换为用户友好的消息
 */
function getUserFriendlyMessage(code: string, message: string, details?: any): string {
  // 错误码到用户消息的映射
  const errorMessages: Record<string, string> = {
    // 验证错误
    'VALIDATION_ERROR': '输入信息有误,请检查后重试',
    'INVALID_FILE_FORMAT': '文件格式不正确,仅支持 CSV 和 XLSX 格式',
    'FILE_TOO_LARGE': '文件太大,请上传小于 50MB 的文件',
    'MISSING_REQUIRED_COLUMNS': '文件缺少必需的列',
    'INVALID_DATA_TYPE': '数据格式不正确',

    // 业务错误
    'DUPLICATE_DATA': '数据已存在',
    'BATCH_NOT_FOUND': '批次不存在',
    'RUN_NOT_FOUND': '提取记录不存在',
    'EXPORT_JOB_NOT_FOUND': '导出任务不存在',

    // 系统错误
    'DATABASE_ERROR': '数据库操作失败,请稍后重试',
    'STORAGE_ERROR': '文件存储失败,请稍后重试',
    'EXTERNAL_API_ERROR': 'AI 服务暂时不可用,请稍后重试',
    'INTERNAL_SERVER_ERROR': '系统繁忙,请稍后重试',
  }

  // 优先使用映射的用户友好消息
  if (errorMessages[code]) {
    return errorMessages[code]
  }

  // 如果后端已经提供了用户友好的消息,直接使用
  if (message && !message.includes('Error') && !message.includes('Exception')) {
    return message
  }

  // 默认消息
  return '操作失败,请稍后重试'
}

export { http, API_BASE }
export type { AxiosRequestConfig, AxiosResponse }
