import { http, API_BASE } from '@/utils/http'

export interface ExtractionTask {
    id: string
    filename: string
    status: string
    target_fields: string[]
    columns: string[]
    created_at: string
    updated_at: string
}

export const extractionApi = {
    upload(file: File) {
        const formData = new FormData()
        formData.append('file', file)
        return http.post<ExtractionTask>(`${API_BASE}/extraction/upload`, formData)
    },

    start(taskId: string, targetFields: string[]) {
        return http.post(`${API_BASE}/extraction/${taskId}/start`, {
            target_fields: targetFields
        })
    },

    getTask(taskId: string) {
        return http.get<ExtractionTask>(`${API_BASE}/extraction/${taskId}`)
    },

    getExportUrl(taskId: string) {
        return `${API_BASE}/extraction/${taskId}/export`
    }
}
