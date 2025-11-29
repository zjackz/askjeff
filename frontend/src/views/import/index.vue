<template>
  <div class="import-page">
    <el-card class="import-form">
      <template #header>
        <div class="card-header">
          <h2>文件导入</h2>
        </div>
      </template>
      
      <el-form label-width="100px">
        <el-form-item label="导入策略">
          <el-select v-model="strategy" style="width: 200px">
            <el-option label="仅追加 (Append)" value="append" />
            <el-option label="覆盖批次 (Overwrite)" value="overwrite" />
            <el-option label="仅更新 (Update Only)" value="update_only" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Sorftime 文件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".csv,.xlsx"
            v-model:file-list="fileList"
            style="width: 100%"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .csv 或 .xlsx 文件，单个文件不超过 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="submitting" 
            @click="submit"
            :disabled="fileList.length === 0"
          >
            开始导入
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="import-table">
      <template #header>
        <div class="card-header">
          <h3>最近批次</h3>
          <div class="header-actions">
            <span v-if="isPolling" class="polling-status">
              <el-icon class="is-loading"><loading /></el-icon> 实时更新中
            </span>
            <el-button :icon="Refresh" circle @click="fetchBatches" />
          </div>
        </div>
      </template>
      
      <el-table :data="batches" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="批次 ID" width="180" />
        <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="success_rows" label="成功行" width="100" align="right" />
        <el-table-column prop="failed_rows" label="失败行" width="100" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.failed_rows > 0 }">{{ row.failed_rows }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { UploadFilled, Refresh } from '@element-plus/icons-vue'
import { ElMessage, type UploadUserFile, type UploadFile } from 'element-plus'
import { useIntervalFn } from '@vueuse/core'
import { http, API_BASE } from '@/utils/http'

const strategy = ref('append')
const submitting = ref(false)
const loading = ref(false)
const fileList = ref<UploadUserFile[]>([])

interface BatchRow {
  id: string
  filename: string
  status: string
  success_rows?: number
  failed_rows?: number
  created_at?: string
}

const batches = ref<BatchRow[]>([])

// 自动轮询：每 5 秒刷新一次列表
const { pause, resume, isActive: isPolling } = useIntervalFn(() => {
  fetchBatches(true)
}, 5000)

const handleFileChange = (uploadFile: UploadFile) => {
  fileList.value = [uploadFile] // 限制单文件
}

const handleFileRemove = () => {
  fileList.value = []
}

const submit = async () => {
  if (fileList.value.length === 0) return
  
  const file = fileList.value[0].raw
  if (!file) return

  const form = new FormData()
  form.append('file', file)
  form.append('importStrategy', strategy.value)
  
  submitting.value = true
  try {
    await http.post(`${API_BASE}/imports`, form)
    ElMessage.success('导入任务已提交，正在处理...')
    fileList.value = [] // 清空选择
    await fetchBatches()
    resume() // 确保开启轮询
  } catch (err) {
    // 全局错误处理已接管，此处无需处理
  } finally {
    submitting.value = false
  }
}

const fetchBatches = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const { data } = await http.get(`${API_BASE}/imports`)
    batches.value = data.items || []
    
    // 如果所有任务都已完成（没有 pending/processing），可以暂停轮询节省资源
    const hasActiveTasks = batches.value.some(b => 
      ['pending', 'processing'].includes(b.status.toLowerCase())
    )
    if (!hasActiveTasks && isPolling.value) {
      // 可选：任务都完成了就暂停轮询，或者保持常开
      // pause() 
    } else if (hasActiveTasks && !isPolling.value) {
      resume()
    }
  } catch (err) {
    pause() // 出错暂停轮询
  } finally {
    if (!silent) loading.value = false
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    completed: 'success',
    failed: 'danger',
    processing: 'primary',
    pending: 'info'
  }
  return map[status.toLowerCase()] || 'info'
}

const formatTime = (val?: string) => {
  if (!val) return '-'
  return new Date(val).toLocaleString()
}

onMounted(() => {
  fetchBatches()
})
</script>

<style scoped>
.import-page {
  display: grid;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2, .card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.polling-status {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>
