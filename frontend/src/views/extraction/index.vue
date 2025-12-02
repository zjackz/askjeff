<template>
  <div class="extraction-page fade-in">
    <!-- 页面头部 -->
    <div class="page-header mb-6">
      <div class="flex items-center gap-4">
        <el-button circle :icon="ArrowLeft" @click="$router.back()" />
        <div>
          <h1 class="text-2xl font-bold">
            AI 特征提取 
            <span v-if="batch?.sequence_id" class="text-gray-400 text-lg font-normal ml-2">#{{ batch.sequence_id }}</span>
          </h1>
          <p class="text-gray-500" v-if="batch">
            批次: {{ batch.filename }} ({{ batch.total_rows }} 条记录)
          </p>
        </div>
      </div>
    </div>

    <div class="main-content" v-loading="loading">
      <el-row :gutter="24">
        <!-- 左侧：数据预览 -->
        <el-col :span="16">
          <el-card class="mb-6">
            <template #header>
              <div class="flex justify-between items-center">
                <span class="font-bold">数据预览 (前 5 条)</span>
                <el-tag size="small" type="info">原始数据</el-tag>
              </div>
            </template>
            
            <el-table :data="previewRecords" style="width: 100%" border stripe size="small">
              <el-table-column 
                v-for="col in previewColumns" 
                :key="col" 
                :prop="col" 
                :label="col"
                min-width="120" 
                show-overflow-tooltip
              />
            </el-table>
          </el-card>

          <!-- 现有字段列表 -->
          <el-card>
            <template #header>
              <span class="font-bold">现有字段</span>
            </template>
            <div class="flex flex-wrap gap-2">
              <el-tag 
                v-for="col in previewColumns" 
                :key="col" 
                effect="plain"
                class="field-tag"
              >
                {{ col }}
              </el-tag>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：提取配置 -->
        <el-col :span="8">
          <el-card class="extraction-config-card">
            <template #header>
              <div class="flex items-center gap-2">
                <el-icon class="text-primary"><MagicStick /></el-icon>
                <span class="font-bold">提取配置</span>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item label="目标字段">
                <div class="text-xs text-gray-400 mb-2">
                  输入您想要 AI 从原始数据中分析并提取的新字段。
                </div>
                <el-select
                  v-model="targetFields"
                  multiple
                  filterable
                  allow-create
                  default-first-option
                  placeholder="输入或选择字段 (回车添加)"
                  class="w-full"
                  size="large"
                >
                  <el-option label="材质 (Material)" value="Material" />
                  <el-option label="颜色 (Color)" value="Color" />
                  <el-option label="尺寸 (Size)" value="Size" />
                  <el-option label="适用人群 (Target Audience)" value="Target Audience" />
                  <el-option label="使用场景 (Usage Scenario)" value="Usage Scenario" />
                  <el-option label="卖点 (Selling Points)" value="Selling Points" />
                  <el-option label="风格 (Style)" value="Style" />
                </el-select>
              </el-form-item>

              <div class="bg-blue-50 p-4 rounded-lg mb-6">
                <h4 class="text-blue-700 font-bold mb-2 text-sm">提示</h4>
                <ul class="list-disc list-inside text-xs text-blue-600 space-y-1">
                  <li>AI 将分析所有原始列的内容</li>
                  <li>提取结果将自动添加到新列中</li>
                  <li>建议使用清晰的字段名称</li>
                </ul>
              </div>

              <el-button 
                type="primary" 
                size="large" 
                class="w-full" 
                :loading="extracting"
                @click="submitExtraction"
                :disabled="targetFields.length === 0"
              >
                开始 AI 提取
              </el-button>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { http, API_BASE } from '@/utils/http'

const route = useRoute()
const router = useRouter()
const batchId = route.params.batchId as string

interface Batch {
  id: string
  sequence_id?: number
  filename: string
  total_rows?: number
  [key: string]: unknown
}

interface RecordData {
  id: string
  normalized_payload?: Record<string, unknown>
  raw_payload?: Record<string, unknown>
  [key: string]: unknown
}

const loading = ref(false)
const extracting = ref(false)
const batch = ref<Batch | null>(null)
const previewRecords = ref<RecordData[]>([])
const targetFields = ref<string[]>([])

// 计算预览列（从第一条记录的 payload 中获取 key）
const previewColumns = computed(() => {
  if (previewRecords.value.length === 0) return []
  // 优先使用 normalized_payload，否则使用 raw_payload
  const firstRecord = previewRecords.value[0]
  if (!firstRecord) return []
  const payload = firstRecord.normalized_payload || firstRecord.raw_payload || {}
  return Object.keys(payload)
})

const fetchBatchDetails = async () => {
  loading.value = true
  try {
    // 获取批次详情
    const { data: batchData } = await http.get(`${API_BASE}/imports/${batchId}`)
    if (batchData && batchData.batch) {
      batch.value = batchData.batch
    }

    // 获取预览记录
    const { data: recordsData } = await http.get(`${API_BASE}/imports/${batchId}/records`, {
      params: { limit: 5 }
    })
    
    if (Array.isArray(recordsData)) {
      // 处理记录数据，展平 payload
      previewRecords.value = recordsData.map((record: RecordData) => {
        const payload = record.normalized_payload || record.raw_payload || {}
        return {
          id: record.id,
          ...payload
        }
      })
    }
  } catch (err) {
    console.error('Failed to load batch details:', err)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const submitExtraction = async () => {
  if (!batchId || targetFields.value.length === 0) return

  extracting.value = true
  try {
    await http.post(`${API_BASE}/imports/${batchId}/extract`, {
      target_fields: targetFields.value
    })
    ElMessage.success('AI 提取任务已启动')
    // 跳转回导入列表页，或者留在当前页显示状态？
    // 用户需求是"点击跳转到一个单独页面"，提取后可能想看进度。
    // 暂时跳转回列表页，因为列表页有进度条。
    router.push('/import')
  } catch (err) {
    console.error('Extraction failed:', err)
  } finally {
    extracting.value = false
  }
}

onMounted(() => {
  if (batchId) {
    fetchBatchDetails()
  } else {
    ElMessage.error('缺少批次 ID')
    router.push('/import')
  }
})
</script>

<style scoped lang="scss">
.extraction-page {
  max-width: 100%;
  min-height: 100vh;
  padding: 24px;
  background-color: var(--bg-secondary);
}

.page-header {
  max-width: 1400px;
  margin: 0 auto 24px;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
}

.text-primary {
  color: var(--primary-color);
}

.extraction-config-card {
  position: sticky;
  top: 20px;
}

.field-tag {
  margin-bottom: 4px;
}
</style>
