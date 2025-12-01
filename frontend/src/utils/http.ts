import axios, { AxiosError } from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api'

// 扩展 AxiosRequestConfig 类型以支持自定义配置
declare module 'axios' {
  export interface AxiosRequestConfig {
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
  401: '登录已过期，请重新登录',
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
    // 上报失败时静默处理，避免阻塞用户操作
  }
}

http.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    // 1. 上报错误日志
    await reportClientError(error)

    // 2. 全局错误提示 (除非显式跳过)
    if (!error.config?.skipGlobalErrorHandler) {
      let message = '网络请求失败'

      if (error.response) {
        // 优先使用后端返回的 detail
        const data = error.response.data as { detail?: string | Record<string, unknown> }
        if (data?.detail) {
          message = typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail)
        } else {
          // 回退到状态码映射
          message = HTTP_STATUS_MAP[error.response.status] || `请求失败 (${error.response.status})`
        }
      } else if (error.message.includes('timeout')) {
        message = '请求超时，请检查网络'
      } else if (!window.navigator.onLine) {
        message = '网络连接已断开'
      }

      ElMessage.error({
        message,
        duration: 5000,
        showClose: true
      })
    }

    return Promise.reject(error)
  }
)

export { http, API_BASE }
export type { AxiosRequestConfig, AxiosResponse }
