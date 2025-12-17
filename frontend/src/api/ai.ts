import { http } from '@/utils/http'

export interface ProductSelectionRequest {
    category_id: string
    domain: number
    use_cache?: boolean
}

export interface ProductSelectionResponse {
    category_id: string
    category_name: string
    domain: number
    market_score: number
    analysis: string
    statistics: {
        avg_price: number
        avg_rating: number
        avg_reviews: number
        competition_level: string
    }
    timestamp: string
}

export interface KeywordOptimizationRequest {
    asin: string
    domain: number
    include_bullet_points?: boolean
    use_cache?: boolean
}

export interface KeywordOptimizationResponse {
    asin: string
    domain: number
    original_title: string
    optimized_title: string
    optimization_report: string
    timestamp: string
}

export const aiApi = {
    analyzeProductSelection: (data: ProductSelectionRequest) => {
        return http.post<any>('/ai/product-selection', data)
    },
    optimizeKeywords: (data: KeywordOptimizationRequest) => {
        return http.post<any>('/ai/keyword-optimization', data)
    }
}
