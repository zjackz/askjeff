import { http } from '@/utils/http'

export interface AmazonStore {
    id: string
    user_id: number
    store_name: string
    marketplace_id: string  // ATVPDKIKX0DER, A1PA6795UKMFR9
    marketplace_name: string  // United States, Germany
    seller_id: string
    sp_api_refresh_token?: string
    advertising_api_refresh_token?: string
    is_active: boolean
    last_sync_at?: string
    created_at: string
    updated_at: string

    // 扩展字段
    has_credentials?: boolean
    latest_sync?: {
        status: string
        sync_type?: string
        created_at?: string
    }
}

export interface StoreCreate {
    store_name: string
    marketplace_id: string
    marketplace_name: string
    seller_id: string
    sp_api_refresh_token?: string
    advertising_api_refresh_token?: string
    is_active?: boolean
}

export interface StoreUpdate {
    store_name?: string
    sp_api_refresh_token?: string
    advertising_api_refresh_token?: string
    is_active?: boolean
}

export interface StoreListResponse {
    total: number
    page: number
    page_size: number
    items: AmazonStore[]
}

export interface VerifyCredentialsResponse {
    valid: boolean
    message: string
    task_id?: string
}

export const storesApi = {
    // 获取店铺列表
    list: (params?: {
        page?: number
        page_size?: number
        is_active?: boolean
        marketplace_id?: string
    }) => {
        return http.get<StoreListResponse>('/stores', { params })
    },

    // 获取店铺详情
    get: (id: string) => {
        return http.get<AmazonStore>(`/stores/${id}`)
    },

    // 创建店铺
    create: (data: StoreCreate) => {
        return http.post<{ message: string; id: string }>('/stores', data)
    },

    // 更新店铺
    update: (id: string, data: StoreUpdate) => {
        return http.put<{ message: string; id: string }>(`/stores/${id}`, data)
    },

    // 删除店铺
    delete: (id: string) => {
        return http.delete<{ message: string }>(`/stores/${id}`)
    },

    // 验证凭证
    verify: (id: string) => {
        return http.post<VerifyCredentialsResponse>(`/stores/${id}/verify`)
    },

    // 获取同步历史
    syncHistory: (id: string, params?: {
        page?: number
        page_size?: number
        status?: string
    }) => {
        return http.get<any>(`/stores/${id}/sync-history`, { params })
    }
}
