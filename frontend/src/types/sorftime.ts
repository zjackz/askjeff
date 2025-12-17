/**
 * Sorftime API TypeScript Type Definitions
 * 
 * This file contains type definitions for all Sorftime API responses.
 * It provides type safety and autocomplete support for frontend development.
 */

// ==================== Common Types ====================

export interface SorftimeResponse<T = any> {
    requestLeft?: number
    requestConsumed?: number
    requestCount?: number
    code: number
    message?: string
    data?: T
}

export interface SorftimeError {
    code: number
    message: string
    details?: any
}

// ==================== Domain Codes ====================

export enum DomainCode {
    US = 1,
    GB = 2,
    DE = 3,
    FR = 4,
    IN = 5,
    CA = 6,
    JP = 7,
    ES = 8,
    IT = 9,
    MX = 10,
    AE = 11,
    AU = 12,
    BR = 13,
    SA = 14
}

export const DOMAIN_NAMES: Record<DomainCode, string> = {
    [DomainCode.US]: '美国',
    [DomainCode.GB]: '英国',
    [DomainCode.DE]: '德国',
    [DomainCode.FR]: '法国',
    [DomainCode.IN]: '印度',
    [DomainCode.CA]: '加拿大',
    [DomainCode.JP]: '日本',
    [DomainCode.ES]: '西班牙',
    [DomainCode.IT]: '意大利',
    [DomainCode.MX]: '墨西哥',
    [DomainCode.AE]: '阿联酋',
    [DomainCode.AU]: '澳洲',
    [DomainCode.BR]: '巴西',
    [DomainCode.SA]: '沙特'
}

// ==================== Product Data Types ====================

export interface ProductSummary {
    title?: string
    photo?: string[]
    EBCPhoto?: string[]
    StoreName?: string
    listingSalesVolumeOfDaily?: number
    listingSalesOfDaily?: number
    listingSalesVolumeOfMonth?: number
    listingSalesOfMonth?: number
    asin?: string
    parentAsin?: string
    price?: number
    listPrice?: number
    coupon?: number
    salesPrice?: number
    DealType?: string
    brand?: string
    buyboxSeller?: string
    buyboxSellerId?: string
    buyboxSellerAddress?: string
    isFBA?: boolean
    fbaFee?: number
    fbaDetetail?: string[]
    shipCost?: number
    platformFee?: number
    profit?: number
    profitRate?: number
    onlineDate?: string
    onlineDays?: number
    ratingsCount?: number
    category?: string[]
    bsrCategory?: string[][]
    rank?: number
    ratings?: number
    variationASINCount?: number
    sellerCount?: number
    hasVideo?: boolean
    APlus?: boolean
    hasBrandStore?: boolean
    size?: string[]
    weight?: number
    refreshAsin?: string
    ExtraSavings?: Array<{
        Asin: string
        Text: string
    }>
}

export interface ProductDetail extends ProductSummary {
    Description?: string
    ProductBadge?: string[]
    updateDate?: string
    listingSalesVolumeOfDailyTrend?: number[]
    listingSalesOfDailyTrend?: number[]
    listingSalesVolumeOfMonthTrend?: number[]
    listingSalesOfMonthTrend?: number[]
    RankTrend?: string[]
    BsrRankTrend?: Array<{
        date: string
        category: string
        rank: number
    }>
    DealTrend?: any[]
    OffSale?: number
    VariationASIN?: string[]
    Attribute?: string
    PriceTrend?: number[]
    ListPriceTrend?: number[]
    ProductType?: string
    ShipsFrom?: string
    OneStartRatings?: number
    TwoStartRatings?: number
    ThreeStartRatings?: number
    FourStartRatings?: number
    FiveStartRatings?: number
    Feature?: string[]
    ProductInfo?: string[]
    Property?: string[]
    BrandPromotion?: string
}

// ==================== Category Data Types ====================

export interface CategoryNode {
    id: number
    ParentId: number
    nodeid: string
    Name: string
    CNName: string
    URL: string
}

export interface CategoryProduct {
    products: ProductSummary[]
}

export interface CategoryTrend {
    nodeId: string
    trendData: Array<{
        date: string
        value: number
    }>
}

// ==================== Keyword Data Types ====================

export interface KeywordSummary {
    keyword: string
    searchVolume?: number
    searchVolumeChange?: number
    products?: number
    avgPrice?: number
    avgRating?: number
    avgReviews?: number
}

export interface KeywordDetail extends KeywordSummary {
    relatedKeywords?: string[]
    topProducts?: ProductSummary[]
    trend?: Array<{
        date: string
        searchVolume: number
    }>
}

export interface KeywordSearchResult {
    keyword: string
    products: ProductSummary[]
    totalCount: number
    page: number
    pageSize: number
}

// ==================== Review Data Types ====================

export interface ProductReview {
    reviewId: string
    asin: string
    rating: number
    title: string
    content: string
    author: string
    date: string
    verified: boolean
    helpful: number
}

// ==================== Monitoring/Task Data Types ====================

export interface MonitoringTask {
    taskId: number
    type: string
    status: 'active' | 'paused' | 'deleted'
    createdAt: string
    lastRun?: string
    nextRun?: string
}

export interface TaskSchedule {
    scheduleId: string
    taskId: number
    executionTime: string
    status: 'pending' | 'running' | 'completed' | 'failed'
}

// ==================== Account/Billing Data Types ====================

export interface CoinBalance {
    totalCoins: number
    usedCoins: number
    remainingCoins: number
    expiryDate?: string
}

export interface CoinUsage {
    date: string
    taskType: number
    coinsConsumed: number
    remainingCoins: number
}

export interface RequestUsage {
    monthlyQuota: number
    usedRequests: number
    remainingRequests: number
    packages?: Array<{
        name: string
        quota: number
        used: number
        expiryDate: string
    }>
}

// ==================== API Request Payloads ====================

export interface ProductRequestPayload {
    ASIN: string
    Trend?: number
    QueryTrendStartDt?: string
    QueryTrendEndDt?: string
    gzip?: number
}

export interface CategoryRequestPayload {
    nodeId: string
    queryStart?: string
    queryDate?: string
}

export interface KeywordQueryPayload {
    pattern: {
        keyword?: string
        [key: string]: any
    }
    pageIndex?: number
    pageSize?: number
}

export interface ProductQueryPayload {
    query: number
    queryType: number
    pattern: string | Record<string, any>
    page?: number
}

// ==================== API Response Types ====================

export type ProductResponse = SorftimeResponse<ProductDetail | ProductDetail[]>
export type CategoryResponse = SorftimeResponse<CategoryProduct>
export type CategoryTreeResponse = SorftimeResponse<CategoryNode[]>
export type KeywordResponse = SorftimeResponse<KeywordDetail>
export type KeywordSearchResponse = SorftimeResponse<KeywordSearchResult>
export type ReviewsResponse = SorftimeResponse<ProductReview[]>
export type CoinQueryResponse = SorftimeResponse<CoinBalance>
export type CoinStreamResponse = SorftimeResponse<CoinUsage[]>
export type RequestStreamResponse = SorftimeResponse<RequestUsage>

// ==================== Utility Types ====================

export interface TrendDataPoint {
    date: string
    value: number
}

export interface ChartData {
    labels: string[]
    datasets: Array<{
        label: string
        data: number[]
        borderColor?: string
        backgroundColor?: string
    }>
}

// ==================== API Endpoint Types ====================

export type EndpointType =
    | 'product'
    | 'category'
    | 'category-tree'
    | 'category-trend'
    | 'category-products'
    | 'product-query'
    | 'keyword-query'
    | 'keyword-request'
    | 'keyword-search-results'
    | 'asin-sales-volume'
    | 'product-variation-history'
    | 'product-trend'
    | 'product-realtime'
    | 'product-realtime-status'
    | 'reviews-collection'
    | 'reviews-collection-status'
    | 'reviews-query'
    | 'similar-product-realtime'
    | 'similar-product-status'
    | 'similar-product-result'
    | 'keyword-search-result-trend'
    | 'category-request-keyword'
    | 'asin-request-keyword'
    | 'keyword-product-ranking'
    | 'asin-keyword-ranking'
    | 'keyword-subscription'
    | 'keyword-tasks'
    | 'keyword-task-update'
    | 'keyword-batch-schedule-list'
    | 'keyword-batch-schedule-detail'
    | 'best-seller-list-subscription'
    | 'best-seller-list-task'
    | 'best-seller-list-delete'
    | 'best-seller-list-data-collect'
    | 'product-seller-subscription'
    | 'product-seller-tasks'
    | 'product-seller-task-update'
    | 'product-seller-task-schedule-list'
    | 'product-seller-task-schedule-detail'
    | 'asin-subscription'
    | 'asin-subscription-query'
    | 'asin-subscription-collection'
    | 'coin-query'
    | 'coin-stream'
    | 'request-stream'

export interface ApiDocumentation {
    title: string
    description: string
    note?: string
    cost: string
}
