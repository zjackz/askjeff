<template>
  <el-dialog 
    :model-value="visible" 
    @update:model-value="$emit('update:visible', $event)"
    title="" 
    width="900px" 
    destroy-on-close 
    class="premium-dialog-wide"
    :show-close="true"
    align-center
  >
    <div class="mcp-layout">
      <!-- 左侧：操作区 -->
      <div class="mcp-left-panel">
        <div class="mcp-header">
          <div class="mcp-icon-wrapper">
            <el-icon><MagicStick /></el-icon>
          </div>
          <div class="mcp-title-group">
            <h2>一键抓取</h2>
            <p>只需粘贴 Amazon 商品链接或 ASIN，AI 将自动识别并提取 Top 100 数据。</p>
          </div>
        </div>

        <div class="mcp-form">
          <div class="form-group">
            <label>输入内容</label>
            <div class="input-wrapper">
              <el-input
                v-model="mcpForm.input"
                type="textarea"
                :rows="6"
                resize="none"
                class="premium-textarea"
                placeholder="在此粘贴链接或 ASIN..."
                @input="handleInputPreview"
              />
              <el-icon class="input-icon"><Link /></el-icon>
            </div>
          </div>

          <div class="options-box">
            <div class="option-item">
              <div class="label-with-icon">
                <span>抓取数量</span>
                <el-tooltip content="限制获取详情的产品数量" placement="top">
                  <el-icon><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-input-number v-model="mcpForm.limit" :min="1" :max="500" size="small" controls-position="right" />
            </div>
            <div class="option-item">
              <span>测试模式 (Mock)</span>
              <el-switch v-model="mcpForm.test_mode" size="small" />
            </div>
          </div>
        </div>

        <div class="mcp-footer">
          <el-button 
            type="primary" 
            class="start-btn"
            :loading="mcpSubmitting"
            @click="handleMcpSubmit"
            :disabled="!mcpForm.input || (previewData && !previewData.valid)"
          >
            {{ mcpSubmitting ? '正在抓取...' : '开始抓取' }}
          </el-button>
        </div>
      </div>

      <!-- 右侧：展示区 -->
      <div class="mcp-right-panel">
        <div class="panel-bg"></div>

        <div class="panel-header">
          <h3>
            <el-icon><DataAnalysis /></el-icon>
            实时预览 & 状态
          </h3>
          <el-tag v-if="previewLoading" size="small" type="warning" effect="light">
            <el-icon class="is-loading"><Loading /></el-icon>
            AI 识别中...
          </el-tag>
        </div>

        <div class="panel-content">
          <div v-if="!previewData && !importProgress.visible" class="empty-state">
            <div class="empty-icon">
              <el-icon><Document /></el-icon>
            </div>
            <p class="main-text">等待输入...</p>
            <p class="sub-text">在左侧输入内容以开始预览</p>
          </div>

          <div v-else-if="previewData && !importProgress.visible" class="preview-card">
            <div class="status-bar" :class="{ valid: previewData.valid }"></div>
            <div class="card-body">
              <div v-if="previewData.valid" class="valid-content">
                <div class="product-image">
                   <el-image v-if="previewData.image" :src="previewData.image" fit="contain">
                     <template #error><el-icon><Picture /></el-icon></template>
                   </el-image>
                   <el-icon v-else><Picture /></el-icon>
                </div>
                <div class="product-info">
                  <div class="tags-row">
                    <el-tag size="small" effect="dark" :type="previewData.type === 'asin' ? 'warning' : 'primary'">
                      {{ previewData.type === 'asin' ? 'ASIN' : 'CATEGORY' }}
                    </el-tag>
                    <span class="id-text">{{ previewData.value }}</span>
                  </div>
                  <div class="product-title" :title="previewData.title">
                    {{ previewData.title || '暂无标题' }}
                  </div>
                  <div v-if="previewData.category_id" class="category-info">
                    <el-icon><Menu /></el-icon>
                    <span>类目 ID: <b>{{ previewData.category_id }}</b></span>
                  </div>
                </div>
              </div>
              
              <div v-else class="error-content">
                <div class="error-icon"><el-icon><Warning /></el-icon></div>
                <div>
                  <div class="error-title">无法识别内容</div>
                  <div class="error-desc">{{ previewData.error || '请输入有效的 Amazon 链接或 ASIN' }}</div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="importProgress.visible" class="progress-state">
            <div class="progress-card">
              <el-progress 
                type="dashboard" 
                :percentage="importProgress.percentage" 
                :status="getProgressStatus(importProgress.status)"
                :width="100"
                :stroke-width="8"
              >
                <template #default="{ percentage }">
                  <div class="progress-label">
                    <span class="percentage">{{ percentage }}%</span>
                    <span class="text">Progress</span>
                  </div>
                </template>
              </el-progress>
              
              <h4>{{ importProgress.message }}</h4>
              <p>{{ importProgress.detail }}</p>
              
              <div v-if="importProgress.status === 'failed'" class="action-row">
                <el-button size="small" @click="importProgress.visible = false">返回修改</el-button>
              </div>
              <div v-if="importProgress.status === 'succeeded'" class="action-row">
                <el-button type="success" size="small" plain @click="$emit('update:visible', false)">完成并查看</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { MagicStick, Link, InfoFilled, DataAnalysis, Loading, Document, Picture, Menu, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useDebounceFn } from '@vueuse/core'
import { http } from '@/utils/http'
import type { McpForm, ImportProgress, PreviewData } from '../types'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits(['update:visible', 'success'])

const mcpSubmitting = ref(false)
const mcpForm = ref<McpForm>({
  input: '',
  test_mode: false,
  limit: 5
})

const previewData = ref<PreviewData | null>(null)
const previewLoading = ref(false)

const importProgress = ref<ImportProgress>({
  visible: false,
  status: 'idle',
  message: '',
  detail: '',
  percentage: 0,
  batchId: null
})

const handleInputPreview = useDebounceFn(async (val: string) => {
  if (!val.trim()) {
    previewData.value = null
    return
  }
  if (val.length < 5) return

  previewLoading.value = true
  try {
    const { data } = await http.post('/imports/preview-api', {
      input: val,
      test_mode: mcpForm.value.test_mode
    })
    previewData.value = data
  } catch (err) {
    console.error(err)
    previewData.value = null
  } finally {
    previewLoading.value = false
  }
}, 800)

const handleMcpSubmit = async () => {
  if (!mcpForm.value.input) {
    ElMessage.warning('请输入内容')
    return
  }
  
  importProgress.value = {
    visible: true,
    status: 'processing',
    message: '正在提交任务...',
    detail: '',
    percentage: 0,
    batchId: null
  }
  
  mcpSubmitting.value = true
  try {
    const payload = {
      ...mcpForm.value,
      input_type: 'auto' 
    }
    
    const { data } = await http.post('/imports/from-api', payload)
    const batchId = data.batch_id
    
    importProgress.value.batchId = batchId
    importProgress.value.message = '任务已提交，正在抓取数据...'
    importProgress.value.percentage = 10
    
    pollImportStatus(batchId)
    
  } catch (err: any) {
    console.error('API import failed:', err)
    importProgress.value.status = 'failed'
    importProgress.value.message = '提交失败'
    importProgress.value.detail = err.response?.data?.detail || '未知错误'
    mcpSubmitting.value = false
  }
}

const pollImportStatus = async (batchId: number) => {
  const maxAttempts = 60
  let attempts = 0
  
  const poll = async () => {
    if (attempts >= maxAttempts) {
      importProgress.value.status = 'failed'
      importProgress.value.message = '抓取超时'
      importProgress.value.detail = '请检查日志或重试'
      mcpSubmitting.value = false
      return
    }
    
    attempts++
    
    try {
      const { data } = await http.get(`/imports/${batchId}`)
      const batch = data
      
      if (batch.status === 'processing') {
        const progress = Math.min(10 + (attempts * 1.5), 90)
        importProgress.value.percentage = Math.round(progress)
        importProgress.value.message = '正在抓取数据...'
        if (batch.import_metadata) {
          importProgress.value.detail = `输入: ${batch.import_metadata.input_value || ''}`
        }
        setTimeout(poll, 3000)
      } else if (batch.status === 'succeeded') {
        importProgress.value.status = 'succeeded'
        importProgress.value.percentage = 100
        importProgress.value.message = `抓取成功！获取数据 ${batch.success_rows || 0} 条`
        importProgress.value.detail = `总计: ${batch.total_rows || 0} 条 | 成功: ${batch.success_rows || 0} 条`
        mcpSubmitting.value = false
        ElMessage.success('数据抓取完成')
        setTimeout(() => {
          emit('update:visible', false)
          importProgress.value.visible = false
          emit('success')
        }, 3000)
      } else if (batch.status === 'failed') {
        importProgress.value.status = 'failed'
        importProgress.value.message = '抓取失败'
        importProgress.value.detail = batch.failure_summary?.error || '未知错误'
        mcpSubmitting.value = false
      } else {
        importProgress.value.percentage = 5
        setTimeout(poll, 3000)
      }
    } catch (err) {
      console.error('Poll status failed:', err)
      setTimeout(poll, 3000)
    }
  }
  poll()
}

const getProgressStatus = (status: string) => {
  if (status === 'failed') return 'exception'
  if (status === 'succeeded') return 'success'
  return ''
}
</script>

<style scoped lang="scss">
.premium-dialog-wide {
  :deep(.el-dialog__header) { display: none; }
  :deep(.el-dialog__body) { padding: 0; }
}

.mcp-layout {
  display: flex;
  height: 520px;
  background: #fff;
}

.mcp-left-panel {
  width: 360px;
  padding: 32px;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  background: #fff;
  z-index: 10;
  position: relative;
}

.mcp-right-panel {
  flex: 1;
  padding: 32px;
  background: #f8fafc;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.mcp-header {
  margin-bottom: 32px;
  .mcp-icon-wrapper {
    width: 40px;
    height: 40px;
    background: #eff6ff;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #2563eb;
    font-size: 20px;
    margin-bottom: 12px;
    display: inline-flex;
    margin-right: 12px;
    vertical-align: middle;
  }
  .mcp-title-group {
    display: inline-block;
    vertical-align: middle;
    h2 { font-size: 18px; font-weight: 700; color: #1f2937; margin: 0 0 4px 0; }
    p { font-size: 13px; color: #6b7280; margin: 0; line-height: 1.5; }
  }
}

.mcp-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  .form-group {
    label { font-size: 12px; font-weight: 700; color: #374151; margin-bottom: 8px; display: block; text-transform: uppercase; letter-spacing: 0.05em; }
    .input-wrapper {
      position: relative;
      .input-icon { position: absolute; bottom: 8px; right: 8px; color: #d1d5db; pointer-events: none; }
    }
  }
  .options-box {
    background: #f9fafb;
    border: 1px solid #f3f4f6;
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    .option-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 14px;
      color: #4b5563;
      .label-with-icon {
        display: flex;
        align-items: center;
        gap: 6px;
        .el-icon { color: #9ca3af; cursor: help; }
      }
    }
  }
}

.premium-textarea {
  :deep(.el-textarea__inner) {
    padding: 12px 16px;
    border-radius: 12px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    background-color: #f9fafb;
    border-color: #e5e7eb;
    font-size: 14px;
    line-height: 1.6;
    &:focus {
      background-color: #fff;
      box-shadow: 0 0 0 1px var(--el-color-primary), 0 4px 12px rgba(var(--el-color-primary-rgb), 0.1);
      border-color: var(--el-color-primary);
    }
  }
}

.mcp-footer {
  margin-top: auto;
  padding-top: 24px;
  .start-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2);
    &:hover { box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3); }
  }
}

.panel-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(219, 234, 254, 0.4) 0%, rgba(243, 232, 255, 0.4) 100%);
  border-radius: 50%;
  filter: blur(60px);
  transform: translate(30%, -30%);
  pointer-events: none;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
  h3 { font-size: 14px; font-weight: 700; color: #374151; margin: 0; display: flex; align-items: center; gap: 8px; }
}

.panel-content {
  flex: 1;
  position: relative;
  z-index: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  .empty-icon {
    width: 80px;
    height: 80px;
    background: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    border: 1px solid #f3f4f6;
    font-size: 32px;
    color: #e5e7eb;
  }
  .main-text { font-size: 14px; font-weight: 500; color: #6b7280; margin: 0 0 4px 0; }
  .sub-text { font-size: 12px; margin: 0; }
}

.preview-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  .status-bar {
    height: 6px;
    width: 100%;
    background: #ef4444;
    &.valid { background: #10b981; }
  }
  .card-body { padding: 20px; }
  .valid-content {
    display: flex;
    gap: 20px;
    .product-image {
      width: 80px;
      height: 80px;
      background: #f9fafb;
      border-radius: 8px;
      border: 1px solid #f3f4f6;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      .el-image { width: 100%; height: 100%; }
      .el-icon { font-size: 24px; color: #d1d5db; }
    }
    .product-info {
      flex: 1;
      min-width: 0;
      .tags-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        .id-text { font-family: monospace; font-size: 12px; color: #6b7280; background: #f3f4f6; padding: 2px 6px; border-radius: 4px; }
      }
      .product-title {
        font-size: 14px;
        font-weight: 700;
        color: #1f2937;
        line-height: 1.4;
        margin-bottom: 8px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      .category-info { font-size: 12px; color: #6b7280; display: flex; align-items: center; gap: 6px; b { color: #374151; } }
    }
  }
  .error-content {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #dc2626;
    .error-icon {
      width: 40px;
      height: 40px;
      background: #fef2f2;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }
    .error-title { font-size: 14px; font-weight: 700; margin-bottom: 2px; }
    .error-desc { font-size: 12px; opacity: 0.8; }
  }
}

.progress-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  .progress-card {
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
    text-align: center;
    width: 100%;
    max-width: 280px;
    .progress-label {
      display: flex;
      flex-direction: column;
      align-items: center;
      .percentage { font-size: 20px; font-weight: 700; color: #374151; }
      .text { font-size: 10px; text-transform: uppercase; color: #9ca3af; }
    }
    h4 { font-size: 16px; font-weight: 700; color: #1f2937; margin: 16px 0 4px 0; }
    p { font-size: 12px; color: #6b7280; margin: 0 0 16px 0; }
  }
}
</style>
