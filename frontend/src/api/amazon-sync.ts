import { http } from '@/utils/http'

export interface SyncTask {
    id: string
    store_id: string
    sync_type: 'inventory' | 'business' | 'advertising'
    status: 'pending' | 'running' | 'success' | 'failed'
    start_time: string
    end_time?: string
    records_synced: number
    records_failed: number
    error_message?: string
    created_at: string
}

export interface SyncResponse {
    message: string
    task_id: string
    store_id?: string
    task_ids?: {
        inventory: string
        business: string
        advertising: string
    }
}

export const amazonSyncApi = {
    // 触发库存同步
    syncInventory: (storeId: string, days: number = 30, useMock: boolean = true) => {
        return http.post<SyncResponse>(`/amazon/stores/${storeId}/sync/inventory`, null, {
            params: { days, use_mock: useMock }
        })
    },

    // 触发业务报告同步
    syncBusiness: (storeId: string, days: number = 30, useMock: boolean = true) => {
        return http.post<SyncResponse>(`/amazon/stores/${storeId}/sync/business`, null, {
            params: { days, use_mock: useMock }
        })
    },

    // 触发广告数据同步
    syncAds: (storeId: string, days: number = 30, useMock: boolean = true) => {
        return http.post<SyncResponse>(`/amazon/stores/${storeId}/sync/ads`, null, {
            params: { days, use_mock: useMock }
        })
    },

    // 触发所有同步
    syncAll: (days: number = 30, useMock: boolean = true) => {
        return http.post<SyncResponse>('/amazon/sync/all', null, {
            params: { days, use_mock: useMock }
        })
    },

    // 获取同步任务历史
    getSyncTasks: (params?: {
        store_id?: string
        sync_type?: string
        status?: string
        limit?: number
        skip?: number
    }) => {
        return http.get<SyncTask[]>('/amazon/sync-tasks', { params })
    }
}
