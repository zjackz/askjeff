<template>
  <div class="extraction-page">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>LLM 产品特征提取</h2>
        </div>
      </template>

      <!-- Step 1: Upload -->
      <div v-if="!currentTask" class="upload-section">
        <el-upload
          class="upload-demo"
          drag
          action="#"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          accept=".csv,.xlsx"
          v-model:file-list="fileList"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .xlsx, .csv 文件。上传后将自动识别列名。
            </div>
          </template>
        </el-upload>
        <div class="actions" style="margin-top: 20px; text-align: center;">
          <el-button type="primary" @click="uploadFile" :loading="uploading" :disabled="!fileList.length">
            下一步：配置字段
          </el-button>
        </div>
      </div>

      <!-- Step 2: Configure & Monitor -->
      <div v-else class="task-section">
        <el-descriptions title="任务信息" :column="2" border>
          <el-descriptions-item label="文件名">{{ currentTask.filename }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTask.status)">{{ currentTask.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="原始列">
            <el-tag v-for="col in currentTask.columns.slice(0, 5)" :key="col" size="small" style="margin-right: 5px">{{ col }}</el-tag>
            <span v-if="currentTask.columns.length > 5">...</span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="field-config" style="margin-top: 24px" v-if="currentTask.status === 'PENDING'">
          <h3>需要提取的特征字段</h3>
          <p class="text-gray">输入你想从产品信息中提取的字段，例如："电池容量", "材质", "适用年龄"</p>
          
          <div class="tags-input">
            <el-tag
              v-for="tag in dynamicTags"
              :key="tag"
              class="mx-1"
              closable
              :disable-transitions="false"
              @close="handleClose(tag)"
              size="large"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="inputVisible"
              ref="InputRef"
              v-model="inputValue"
              class="ml-1 w-20"
              size="small"
              @keyup.enter="handleInputConfirm"
              @blur="handleInputConfirm"
            />
            <el-button v-else class="button-new-tag ml-1" size="small" @click="showInput">
              + 添加字段
            </el-button>
          </div>

          <div class="actions" style="margin-top: 24px">
            <el-button type="primary" @click="startExtraction" :loading="starting" :disabled="dynamicTags.length === 0">
              开始提取
            </el-button>
            <el-button @click="reset">取消</el-button>
          </div>
        </div>

        <div class="progress-section" style="margin-top: 24px" v-else>
          <el-alert
            v-if="currentTask.status === 'PROCESSING'"
            title="正在提取中，请稍候..."
            type="info"
            :closable="false"
            show-icon
          />
          <el-alert
            v-if="currentTask.status === 'COMPLETED'"
            title="提取完成！"
            type="success"
            :closable="false"
            show-icon
          />
          
          <div class="result-actions" style="margin-top: 24px" v-if="currentTask.status === 'COMPLETED'">
            <el-button type="success" @click="downloadResult">下载结果 Excel</el-button>
            <el-button @click="reset">处理新文件</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onUnmounted } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElInput, type UploadUserFile } from 'element-plus'
import { extractionApi, type ExtractionTask } from '@/api/extraction'
import { useIntervalFn } from '@vueuse/core'

const fileList = ref<UploadUserFile[]>([])
const uploading = ref(false)
const starting = ref(false)
const currentTask = ref<ExtractionTask | null>(null)

// Tags Input
const inputValue = ref('')
const dynamicTags = ref<string[]>([])
const inputVisible = ref(false)
const InputRef = ref<InstanceType<typeof ElInput>>()

// Polling
const { pause, resume, isActive } = useIntervalFn(async () => {
  if (!currentTask.value) return
  if (currentTask.value.status === 'COMPLETED' || currentTask.value.status === 'FAILED') {
    pause()
    return
  }
  try {
    const { data } = await extractionApi.getTask(currentTask.value.id)
    currentTask.value = data
  } catch (e) {
    console.error(e)
  }
}, 3000, { immediate: false })

const handleFileChange = (file: UploadUserFile) => {
  fileList.value = [file]
}

const uploadFile = async () => {
  if (!fileList.value.length) return
  uploading.value = true
  try {
    const { data } = await extractionApi.upload(fileList.value[0].raw!)
    currentTask.value = data
    dynamicTags.value = [] // Reset tags
    ElMessage.success('文件上传成功，请配置提取字段')
  } catch (e: any) {
    ElMessage.error(e.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

const handleClose = (tag: string) => {
  dynamicTags.value.splice(dynamicTags.value.indexOf(tag), 1)
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    InputRef.value!.input!.focus()
  })
}

const handleInputConfirm = () => {
  if (inputValue.value) {
    if (!dynamicTags.value.includes(inputValue.value)) {
      dynamicTags.value.push(inputValue.value)
    }
  }
  inputVisible.value = false
  inputValue.value = ''
}

const startExtraction = async () => {
  if (!currentTask.value) return
  starting.value = true
  try {
    await extractionApi.start(currentTask.value.id, dynamicTags.value)
    currentTask.value.status = 'PROCESSING'
    currentTask.value.target_fields = dynamicTags.value
    resume() // Start polling
    ElMessage.success('任务已启动')
  } catch (e: any) {
    ElMessage.error(e.message || '启动失败')
  } finally {
    starting.value = false
  }
}

const downloadResult = () => {
  if (!currentTask.value) return
  const url = extractionApi.getExportUrl(currentTask.value.id)
  window.open(url, '_blank')
}

const reset = () => {
  currentTask.value = null
  fileList.value = []
  pause()
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    COMPLETED: 'success',
    FAILED: 'danger',
    PROCESSING: 'primary',
    PENDING: 'info'
  }
  return map[status] || 'info'
}

onUnmounted(() => {
  pause()
})
</script>

<style scoped>
.extraction-page {
  max-width: 1000px;
  margin: 0 auto;
}

.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-height: 40px;
}

.text-gray {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}

.ml-1 {
  margin-left: 8px;
}
</style>
