<template>
  <el-dialog 
    :model-value="visible" 
    @update:model-value="$emit('update:visible', $event)"
    title="导入数据" 
    width="500px"
  >
    <el-form label-position="top" class="upload-form">
      <el-form-item label="选择文件">
        <el-upload
          class="upload-area"
          drag
          action="#"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          accept=".csv,.xlsx"
          v-model:file-list="fileList"
        >
          <div class="upload-content">
            <div class="upload-icon-wrapper">
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
            </div>
            <div class="upload-text">
              <h4>点击或拖拽文件到此处</h4>
              <p>支持 .csv 或 .xlsx 文件，最大 50MB</p>
            </div>
          </div>
        </el-upload>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="$emit('update:visible', false)">取消</el-button>
        <el-button 
          type="primary" 
          :loading="submitting" 
          @click="submit"
          :disabled="fileList.length === 0"
        >
          开始导入
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, type UploadUserFile, type UploadFile } from 'element-plus'
import { http } from '@/utils/http'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits(['update:visible', 'success'])

const submitting = ref(false)
const fileList = ref<UploadUserFile[]>([])
const strategy = ref('append')

const handleFileChange = (uploadFile: UploadFile) => {
  const maxSize = 50 * 1024 * 1024
  if (uploadFile.size && uploadFile.size > maxSize) {
    ElMessage.error('文件大小超过 50MB 限制,请压缩后重试')
    fileList.value = []
    return
  }
  const fileName = uploadFile.name || ''
  const validExtensions = ['.csv', '.xlsx', '.xls']
  const hasValidExtension = validExtensions.some(ext => fileName.toLowerCase().endsWith(ext))
  if (!hasValidExtension) {
    ElMessage.error('文件格式不正确,仅支持 CSV 和 XLSX 格式')
    fileList.value = []
    return
  }
  fileList.value = [uploadFile]
}

const handleFileRemove = () => {
  fileList.value = []
}

const submit = async () => {
  if (fileList.value.length === 0) return
  const file = fileList.value[0]?.raw
  if (!file) return
  
  const form = new FormData()
  form.append('file', file)
  form.append('importStrategy', strategy.value)
  
  submitting.value = true
  try {
    await http.post('/imports', form)
    ElMessage.success('导入任务已提交，正在处理...')
    fileList.value = []
    emit('update:visible', false)
    emit('success')
  } catch (err) {
    console.error('Import failed:', err)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.upload-area {
  :deep(.el-upload) {
    width: 100%;
  }
  
  :deep(.el-upload-dragger) {
    width: 100%;
    height: 200px;
    border: 2px dashed var(--el-border-color);
    border-radius: 12px;
    background: var(--el-fill-color-blank);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      border-color: var(--el-color-primary);
      background: rgba(var(--el-color-primary-rgb), 0.05);
      
      .upload-icon {
        transform: scale(1.1);
        color: var(--el-color-primary);
      }
    }
  }
}

.upload-content {
  text-align: center;
}

.upload-icon-wrapper {
  margin-bottom: 16px;
}

.upload-icon {
  font-size: 48px;
  color: var(--el-text-color-placeholder);
  transition: all 0.3s ease;
}

.upload-text {
  h4 {
    margin: 0 0 8px;
    font-size: 16px;
    color: var(--el-text-color-primary);
  }
  
  p {
    margin: 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}
</style>
