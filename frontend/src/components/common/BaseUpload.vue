<!--
通用上传组件

使用示例:
<BaseUpload
  :action="uploadUrl"
  :file-list="fileList"
  @success="handleSuccess"
/>
-->
<template>
  <el-upload
    :action="action"
    :headers="headers"
    :data="data"
    :name="name"
    :multiple="multiple"
    :accept="accept"
    :limit="limit"
    :file-list="fileList"
    :list-type="listType"
    :auto-upload="autoUpload"
    :disabled="disabled"
    :drag="drag"
    :before-upload="handleBeforeUpload"
    :on-success="handleSuccess"
    :on-error="handleError"
    :on-progress="handleProgress"
    :on-change="handleChange"
    :on-remove="handleRemove"
    :on-exceed="handleExceed"
  >
    <template v-if="drag">
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处,或<em>点击上传</em>
      </div>
      <template v-if="tip" #tip>
        <div class="el-upload__tip">{{ tip }}</div>
      </template>
    </template>
    <template v-else>
      <el-button :type="buttonType" :disabled="disabled">
        <el-icon><upload /></el-icon>
        {{ buttonText }}
      </el-button>
      <template v-if="tip" #tip>
        <div class="el-upload__tip">{{ tip }}</div>
      </template>
    </template>
  </el-upload>
</template>

<script setup lang="ts">
import { Upload, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadProps, UploadUserFile } from 'element-plus'

interface Props {
  action: string
  headers?: Record<string, string>
  data?: Record<string, any>
  name?: string
  multiple?: boolean
  accept?: string
  limit?: number
  fileList?: UploadUserFile[]
  listType?: 'text' | 'picture' | 'picture-card'
  autoUpload?: boolean
  disabled?: boolean
  drag?: boolean
  buttonText?: string
  buttonType?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  tip?: string
  maxSize?: number // MB
}

const props = withDefaults(defineProps<Props>(), {
  name: 'file',
  multiple: false,
  limit: 1,
  listType: 'text',
  autoUpload: true,
  disabled: false,
  drag: false,
  buttonText: '点击上传',
  buttonType: 'primary',
  maxSize: 10
})

const emit = defineEmits<{
  (e: 'success', response: any, file: any, fileList: any[]): void
  (e: 'error', error: any, file: any, fileList: any[]): void
  (e: 'progress', event: any, file: any, fileList: any[]): void
  (e: 'change', file: any, fileList: any[]): void
  (e: 'remove', file: any, fileList: any[]): void
  (e: 'exceed', files: any[], fileList: any[]): void
}>()

const handleBeforeUpload: UploadProps['beforeUpload'] = (file) => {
  // 文件大小检查
  if (props.maxSize && file.size / 1024 / 1024 > props.maxSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB`)
    return false
  }
  return true
}

const handleSuccess: UploadProps['onSuccess'] = (response, file, fileList) => {
  emit('success', response, file, fileList)
}

const handleError: UploadProps['onError'] = (error, file, fileList) => {
  emit('error', error, file, fileList)
}

const handleProgress: UploadProps['onProgress'] = (event, file, fileList) => {
  emit('progress', event, file, fileList)
}

const handleChange: UploadProps['onChange'] = (file, fileList) => {
  emit('change', file, fileList)
}

const handleRemove: UploadProps['onRemove'] = (file, fileList) => {
  emit('remove', file, fileList)
}

const handleExceed: UploadProps['onExceed'] = (files, fileList) => {
  emit('exceed', files, fileList)
  ElMessage.warning(`最多只能上传 ${props.limit} 个文件`)
}
</script>

<style scoped>
.el-icon--upload {
  font-size: 67px;
  color: #C0C4CC;
  margin: 40px 0 16px;
  line-height: 50px;
}

.el-upload__text {
  color: #606266;
  font-size: 14px;
  text-align: center;
}

.el-upload__text em {
  color: #409EFF;
  font-style: normal;
}

.el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 7px;
}
</style>
