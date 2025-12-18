export interface BatchRow {
    id: number
    filename: string
    filePath?: string
    sheetName?: string
    importStrategy?: string
    status: string
    aiStatus?: string
    aiSummary?: { total: number; success: number; failed: number }
    successRows?: number
    failedRows?: number
    totalRows?: number
    createdAt?: string
    createdBy?: string
    startedAt?: string
    finishedAt?: string
    duration?: string
    failureSummary?: { failed_rows_path: string; total_failed: number }
    importMetadata?: { input_value: string; input_type: string; test_mode: boolean }
}

export interface ImportProgress {
    visible: boolean
    status: 'idle' | 'running' | 'succeeded' | 'failed'
    message: string
    detail: string
    percentage: number
    batchId: number | null
}

export interface McpForm {
    input: string
    test_mode: boolean
    limit: number
}

export interface PreviewData {
    valid: boolean
    type?: 'asin' | 'category_id' | 'url'
    value?: string
    title?: string
    image?: string
    category_id?: string
    error?: string
    price?: number
    currency?: string
    rating?: number
    reviews?: number
    sales_rank?: number
    brand?: string
    bullets?: string
}
