<template>
  <div class="extraction-page fade-in">
    <!-- Header -->
    <div class="page-header mb-6 flex justify-between items-center">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <el-button circle :icon="Back" @click="router.back()" />
          <h1 class="text-2xl font-bold">AI 特征提取</h1>
        </div>
        <p class="text-gray-500 ml-12">配置提取字段并预览数据</p>
      </div>
      <div class="flex items-center gap-4">
        <div class="text-right" v-if="batch">
          <div class="text-sm text-gray-500">当前批次</div>
          <div class="font-medium">{{ batch.filename }}</div>
        </div>
        <el-tag :type="getStatusType(batch?.ai_status || 'none')" size="large" effect="dark">
          {{ getStatusLabel(batch?.ai_status || 'none') }}
        </el-tag>
      </div>
    </div>

    <div class="grid-layout">
      <!-- Left: Data Preview -->
      <div class="preview-section slide-in" style="--delay: 0.1s">
        <el-card class="glass-card h-full">
          <template #header>
            <div class="flex items-center gap-2">
              <el-icon class="text-primary"><View /></el-icon>
              <span class="font-bold">数据预览 (前5条)</span>
            </div>
          </template>
          
          <div class="preview-list" v-loading="loadingRecords">
            <div v-for="record in records" :key="record.id" class="preview-item">
              <div class="item-header">
                <span class="font-medium truncate">{{ record.title }}</span>
                <el-tag size="small" type="info">{{ record.asin }}</el-tag>
              </div>
              <div class="item-content">
                <div class="raw-data">
                  <div class="label">原始数据:</div>
                  <pre class="json-content">{{ JSON.stringify(record.raw_payload, null, 2) }}</pre>
                </div>
                <div class="ai-data" v-if="record.ai_features">
                  <div class="label text-success">AI 提取结果:</div>
                  <pre class="json-content success">{{ JSON.stringify(record.ai_features, null, 2) }}</pre>
                </div>
              </div>
            </div>
            <el-empty v-if="!loadingRecords && records.length === 0" description="暂无数据" />
          </div>
        </el-card>
      </div>

      <!-- Right: Configuration -->
      <div class="config-section slide-in" style="--delay: 0.2s">
        <el-card class="glass-card mb-4">
          <template #header>
            <div class="flex items-center gap-2">
              <el-icon class="text-warning"><Setting /></el-icon>
              <span class="font-bold">提取配置</span>
            </div>
          </template>
          
          <div class="config-form">
            <div class="mb-4">
              <div class="text-sm font-medium mb-2">目标字段</div>
              <div class="text-xs text-gray-500 mb-2">输入您希望提取的字段名称，按回车添加</div>
              <el-select
                v-model="targetFields"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="例如：电池容量、材质、适用人群"
                class="w-full"
                size="large"
              />
            </div>
            
            <el-button 
              type="primary" 
              size="large" 
              class="w-full" 
              :loading="extracting"
              @click="handleExtract"
              :disabled="targetFields.length === 0"
            >
              <el-icon class="mr-2"><VideoPlay /></el-icon>
              开始提取
            </el-button>
          </div>
        </el-card>

        <!-- Progress -->
        <el-card class="glass-card" v-if="batch?.ai_status && batch.ai_status !== 'none'">
          <template #header>
            <div class="flex items-center gap-2">
              <el-icon class="text-info"><DataLine /></el-icon>
              <span class="font-bold">任务进度</span>
            </div>
          </template>
          
          <div class="progress-info">
            <div class="flex justify-between mb-2 text-sm">
              <span>处理进度</span>
              <span>{{ batch.ai_summary?.success || 0 }} / {{ batch.ai_summary?.total || 0 }}</span>
            </div>
            <el-progress 
              :percentage="calculateProgress(batch)" 
              :status="batch.ai_status === 'failed' ? 'exception' : (batch.ai_status === 'completed' ? 'success' : '')"
              :stroke-width="8"
            />
            
            <div class="mt-4 grid grid-cols-2 gap-4">
              <div class="stat-item bg-success-light">
                <div class="label">成功</div>
                <div class="value text-success">{{ batch.ai_summary?.success || 0 }}</div>
              </div>
              <div class="stat-item bg-danger-light">
                <div class="label">失败</div>
                <div class="value text-danger">{{ batch.ai_summary?.failed || 0 }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back, View, Setting, VideoPlay, DataLine } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useIntervalFn } from '@vueuse/core'
import { http, API_BASE } from '@/utils/http'
import { extractionApi } from '@/api/extraction'

const route = useRoute()
const router = useRouter()
const batchId = route.params.batchId as string

const batch = ref<any>(null)
const records = ref<any[]>([])
const loadingRecords = ref(false)
const targetFields = ref<string[]>([])
const extracting = ref(false)

// Polling for status updates
const { pause, resume, isActive: isPolling } = useIntervalFn(() => {
  fetchBatchInfo(true)
  fetchRecords(true)
}, 3000)

const fetchBatchInfo = async (silent = false) => {
  try {
    const { data } = await http.get(`${API_BASE}/imports/${batchId}`)
    batch.value = data.batch
    
    // Stop polling if completed or failed
    if (['completed', 'failed'].includes(batch.value.ai_status)) {
      // pause() // Optional: keep polling to see updates if re-triggered
    }
  } catch (err) {
    console.error(err)
  }
}

const fetchRecords = async (silent = false) => {
  if (!silent) loadingRecords.value = true
  try {
    const { data } = await http.get(`${API_BASE}/imports/${batchId}/records`, {
      params: { limit: 5 }
    })
    records.value = data
  } catch (err) {
    console.error(err)
  } finally {
    if (!silent) loadingRecords.value = false
  }
}

const handleExtract = async () => {
  if (targetFields.value.length === 0) return
  
  extracting.value = true
  try {
    await extractionApi.extractBatch(batchId, targetFields.value)
    ElMessage.success('AI 提取任务已启动')
    // Force refresh
    await fetchBatchInfo()
    resume()
  } catch (err) {
    // handled by interceptor
  } finally {
    extracting.value = false
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    completed: 'success',
    failed: 'danger',
    processing: 'primary',
    pending: 'info',
    none: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    completed: '已完成',
    failed: '失败',
    processing: '进行中',
    pending: '等待中',
    none: '未开始'
  }
  return map[status] || '未知'
}

const calculateProgress = (batch: any) => {
  if (!batch || !batch.ai_summary || batch.ai_summary.total === 0) return 0
  const { total, success, failed } = batch.ai_summary
  return Math.min(Math.round(((success + failed) / total) * 100), 100)
}

onMounted(() => {
  if (batchId) {
    fetchBatchInfo()
    fetchRecords()
  }
})
</script>

<style scoped lang="scss">
.extraction-page {
  max-width: 1400px;
  margin: 0 auto;
}

.grid-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  align-items: start;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-item {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
  background: var(--bg-secondary);
  
  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .item-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
}

.json-content {
  font-family: monospace;
  font-size: 12px;
  background: rgba(0,0,0,0.03);
  padding: 8px;
  border-radius: 4px;
  margin: 4px 0 0;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 150px;
  overflow-y: auto;
  
  &.success {
    background: rgba(16, 185, 129, 0.05);
    border: 1px solid rgba(16, 185, 129, 0.2);
  }
}

.label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-item {
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  
  .value {
    font-size: 20px;
    font-weight: bold;
    margin-top: 4px;
  }
  
  &.bg-success-light { background: rgba(16, 185, 129, 0.1); }
  &.bg-danger-light { background: rgba(239, 68, 68, 0.1); }
}

.slide-in {
  animation: slideInUp 0.5s ease-out backwards;
  animation-delay: var(--delay, 0s);
}
</style>
