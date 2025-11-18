import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const http: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 10000
})

const ingestPath = '/logs/ingest'

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
    await reportClientError(error)
    return Promise.reject(error)
  }
)

export { http, API_BASE }
export type { AxiosRequestConfig, AxiosResponse }
