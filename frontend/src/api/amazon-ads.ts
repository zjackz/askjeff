import { http } from '@/utils/http'

export interface Campaign {
    id: string
    campaign_id: string
    name: string
    state: string
    campaign_type: string
    targeting_type: string
    daily_budget: number
    start_date: string
    end_date: string | null

    // Metrics
    impressions: number
    clicks: number
    spend: number
    sales: number
    orders: number
    units: number
    ctr: number
    cpc: number
    acos: number
    roas: number
    cvr: number
}

export interface CampaignListResponse {
    total: number
    items: Campaign[]
    page: number
    limit: number
}

export interface CampaignQueryParams {
    store_id?: string
    state?: string
    campaign_type?: string
    start_date?: string
    end_date?: string
    page?: number
    limit?: number
    sort_by?: string
    sort_order?: 'asc' | 'desc'
}

export interface WastedSpendCampaign {
    id: string
    name: string
    spend: number
    clicks: number
    orders: number
}

export interface WastedSpendResponse {
    total_wasted_spend: number
    campaign_count: number
    campaigns: WastedSpendCampaign[]
}

export interface HighAcosCampaign {
    id: string
    name: string
    spend: number
    sales: number
    acos: number
    target_acos: number
}

export interface HighAcosResponse {
    campaign_count: number
    campaigns: HighAcosCampaign[]
}

export const amazonAdsApi = {
    getCampaigns: (params: CampaignQueryParams) => {
        return http.get<CampaignListResponse>('/amazon/campaigns', { params })
    },
    getWastedSpend: (storeId: string, days: number = 7, threshold: number = 50) => {
        return http.get<WastedSpendResponse>('/ads-analysis/diagnosis/wasted-spend', {
            params: { store_id: storeId, days, threshold }
        })
    },
    getHighAcos: (storeId: string, days: number = 7, acosThreshold: number = 30, minSpend: number = 50) => {
        return http.get<HighAcosResponse>('/ads-analysis/diagnosis/high-acos', {
            params: { store_id: storeId, days, acos_threshold: acosThreshold, min_spend: minSpend }
        })
    }
}
