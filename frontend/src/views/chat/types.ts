// 产品列表与聊天交互所需的前端类型定义
export interface ProductItem {
  id: string
  asin: string
  title: string
  batch_id: string
  ingested_at: string
  validation_status: string
  validation_messages?: Record<string, unknown> | null
  price?: number | null
  rating?: number | null
  sales_rank?: number | null
}

export interface ProductListResponse {
  items: ProductItem[]
  total: number
}

export interface ProductQueryParams {
  batchId?: string
  asin?: string
  status?: string
  updated_from?: string
  updated_to?: string
  page: number
  pageSize: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface ChatRequest {
  question: string
  sessionId?: string
}

export interface ChatResponse {
  answer: string
  references?: Array<Record<string, unknown>> | null
  sessionId: string
}
