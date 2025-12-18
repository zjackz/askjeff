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
            <el-icon class="magic-icon"><MagicStick /></el-icon>
            <div class="icon-glow"></div>
          </div>
          <div class="mcp-title-group">
            <h2>一键抓取</h2>
            <p>粘贴 Amazon 链接或 ASIN，AI 自动识别 Top 100 数据。</p>
          </div>
        </div>

        <div class="mcp-form">
          <div class="form-group">
            <div class="label-row">
              <label>输入内容</label>
              <div class="quick-examples">
                <span class="example-link" @click="useExample(examples[0]?.value || '')">ASIN 示例</span>
                <span class="divider"></span>
                <span class="example-link" @click="useExample(examples[1]?.value || '')">链接示例</span>
              </div>
            </div>
            <div class="input-container">
              <el-input
                v-model="mcpForm.input"
                type="textarea"
                :rows="4"
                resize="none"
                class="premium-textarea"
                placeholder="在此粘贴链接或 ASIN..."
                @input="handleInputPreview"
              />
              <div class="input-decoration">
                <el-icon><Link /></el-icon>
              </div>
            </div>
          </div>

          <div class="options-grid">
            <div class="option-card">
              <div class="option-info">
                <span class="option-label">抓取数量</span>
                <el-tooltip content="限制获取详情的产品数量" placement="top">
                  <el-icon class="info-icon"><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-input-number v-model="mcpForm.limit" :min="1" :max="500" size="small" controls-position="right" class="premium-number" />
            </div>
            <div class="option-card" :class="{ active: mcpForm.test_mode }">
              <div class="option-info">
                <span class="option-label">测试模式 (Mock)</span>
                <el-tooltip content="开启后将使用模拟数据，无需 API Key" placement="top">
                  <el-icon class="info-icon"><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-switch v-model="mcpForm.test_mode" size="small" @change="handleInputPreview(mcpForm.input)" />
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
            <span v-if="!mcpSubmitting">开始抓取</span>
            <span v-else>正在抓取数据...</span>
          </el-button>
        </div>
      </div>

      <!-- 右侧：展示区 -->
      <div class="mcp-right-panel">
        <div class="panel-mesh-bg"></div>
        <div class="panel-glow-1"></div>
        <div class="panel-glow-2"></div>

        <div class="panel-header">
          <div class="header-title">
            <el-icon><DataAnalysis /></el-icon>
            <span>实时预览 & 状态</span>
          </div>
          <div v-if="previewLoading" class="loading-badge">
            <el-icon class="is-loading"><Loading /></el-icon>
            AI 识别中
          </div>
        </div>

        <div class="panel-content">
          <!-- 1. 初始空状态 -->
          <div v-if="!previewData && !importProgress.visible && !previewLoading" class="empty-state">
            <div class="empty-illustration">
              <div class="pulse-ring"></div>
              <div class="icon-box">
                <el-icon><Document /></el-icon>
              </div>
            </div>
            <p class="main-text">等待输入...</p>
            <p class="sub-text">在左侧输入内容以开始预览</p>
          </div>

          <!-- 2. 加载状态 -->
          <div v-if="previewLoading" class="preview-skeleton-container">
            <div class="skeleton-card">
              <el-skeleton animated>
                <template #template>
                  <div class="flex gap-4">
                    <el-skeleton-item variant="image" class="skeleton-img" />
                    <div class="flex-1 space-y-3">
                      <el-skeleton-item variant="text" style="width: 30%" />
                      <el-skeleton-item variant="h3" style="width: 90%" />
                      <el-skeleton-item variant="text" style="width: 50%" />
                    </div>
                  </div>
                </template>
              </el-skeleton>
            </div>
          </div>

          <!-- 3. 预览卡片 (只要有数据且不在加载中就显示) -->
          <div v-if="previewData && !previewLoading" class="preview-card-wrapper animate-slide-up" :class="{ 'in-progress': importProgress.visible }">
            <div class="preview-card glass-card" :class="{ 'is-invalid': !previewData.valid }">
              <div class="card-glow"></div>
              <div v-if="previewData.valid" class="valid-content">
                <div class="product-image-box">
                   <el-image v-if="previewData.image" :src="previewData.image" fit="contain">
                     <template #error><el-icon><Picture /></el-icon></template>
                   </el-image>
                   <el-icon v-else><Picture /></el-icon>
                </div>
                <div class="product-details">
                  <div class="details-header">
                    <span class="type-badge" :class="previewData.type">
                      {{ previewData.type === 'asin' ? 'ASIN' : 'CATEGORY' }}
                    </span>
                    <span class="id-code">{{ previewData.value }}</span>
                  </div>
                  <h4 class="product-title">{{ previewData.title || '暂无标题' }}</h4>
                  <div v-if="previewData.category_id" class="category-tag">
                    <el-icon><Menu /></el-icon>
                    <span>类目 ID: <b>{{ previewData.category_id }}</b></span>
                  </div>
                </div>
              </div>
              
              <div v-else class="error-content">
                <div class="error-visual">
                  <div class="error-icon-box">
                    <el-icon><Warning /></el-icon>
                  </div>
                </div>
                <div class="error-info">
                  <h4 class="error-title">{{ isApiKeyError ? 'API 未配置' : '识别失败' }}</h4>
                  <p class="error-message">{{ previewData.error }}</p>
                  <div v-if="isApiKeyError" class="mock-action">
                    <el-button type="primary" link @click="enableMockMode">
                      开启测试模式 (Mock) 预览
                      <el-icon class="ml-1"><MagicStick /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 进度展示 -->
          <div v-if="importProgress.visible" class="progress-container animate-fade-in">
            <div class="progress-glass-card">
              <div class="progress-visual">
                <el-progress 
                  type="circle" 
                  :percentage="importProgress.percentage" 
                  :status="getProgressStatus(importProgress.status)"
                  :width="110"
                  :stroke-width="7"
                  class="premium-progress"
                >
                  <template #default="{ percentage }">
                    <div class="progress-inner">
                      <span class="percent-val">{{ percentage }}%</span>
                      <span class="percent-label">处理中</span>
                    </div>
                  </template>
                </el-progress>
              </div>
              
              <div class="progress-text-content">
                <h4 class="status-msg">{{ importProgress.message }}</h4>
                <p class="status-detail">{{ importProgress.detail }}</p>
                
                <div class="modern-steps">
                  <div class="m-step" :class="{ active: importProgress.percentage >= 10, done: importProgress.percentage > 30 }">
                    <div class="m-step-dot"></div>
                    <span>提交任务</span>
                  </div>
                  <div class="m-step" :class="{ active: importProgress.percentage > 30, done: importProgress.percentage > 80 }">
                    <div class="m-step-dot"></div>
                    <span>AI 识别解析</span>
                  </div>
                  <div class="m-step" :class="{ active: importProgress.percentage > 80, done: importProgress.status === 'succeeded' }">
                    <div class="m-step-dot"></div>
                    <span>数据入库</span>
                  </div>
                </div>
              </div>
              
              <div v-if="importProgress.status === 'failed'" class="progress-actions">
                <el-button type="danger" plain round @click="importProgress.visible = false">返回修改</el-button>
              </div>
              <div v-if="importProgress.status === 'succeeded'" class="progress-actions">
                <el-button type="primary" round class="success-finish-btn" @click="$emit('update:visible', false)">
                  完成并查看结果
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- SVG 渐变定义 -->
    <svg width="0" height="0" style="position: absolute;">
      <defs>
        <linearGradient id="progress-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#3b82f6" />
          <stop offset="100%" stop-color="#8b5cf6" />
        </linearGradient>
      </defs>
    </svg>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { MagicStick, Link, InfoFilled, DataAnalysis, Loading, Document, Picture, Menu, Warning, CircleCheckFilled, CircleCheck } from '@element-plus/icons-vue'
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

const isApiKeyError = computed(() => {
  return previewData.value?.error?.includes('SORFTIME_API_KEY')
})

const enableMockMode = () => {
  mcpForm.value.test_mode = true
  handleInputPreview(mcpForm.value.input)
}

const examples = [
  { label: 'ASIN 示例', value: 'B0C1S6Z7Y2' },
  { label: '链接示例', value: 'https://www.amazon.com/dp/B0C1S6Z7Y2' }
]

const useExample = (val: string) => {
  mcpForm.value.input = val
  handleInputPreview(val)
}

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
    const batchId = data?.batch_id
    
    if (!batchId) {
      throw new Error('后端未返回有效的批次 ID')
    }
    
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
      // 后端返回的是 { batch: {...}, failed_rows: [...] }
      const batch = data.batch
      
      if (batch.status === 'processing') {
        const progress = Math.min(10 + (attempts * 1.5), 90)
        importProgress.value.percentage = Math.round(progress)
        importProgress.value.message = '正在抓取数据...'
        if (batch.importMetadata) {
          importProgress.value.detail = `输入: ${batch.importMetadata.inputValue || ''}`
        }
        setTimeout(poll, 3000)
      } else if (batch.status === 'succeeded') {
        importProgress.value.status = 'succeeded'
        importProgress.value.percentage = 100
        importProgress.value.message = `抓取成功！获取数据 ${batch.successRows || 0} 条`
        importProgress.value.detail = `总计: ${batch.totalRows || 0} 条 | 成功: ${batch.successRows || 0} 条`
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
        importProgress.value.detail = batch.failureSummary?.error || '未知错误'
        mcpSubmitting.value = false
      } else {
        // pending 或其他状态
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
  :deep(.el-dialog) {
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  }
  :deep(.el-dialog__header) { display: none; }
  :deep(.el-dialog__body) { padding: 0; }
}

.mcp-layout {
  display: flex;
  width: 100%;
  height: 560px;
  background: #fff;
}

// --- 左侧面板 ---
.mcp-left-panel {
  width: 380px;
  padding: 40px;
  border-right: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  background: #fff;
  position: relative;
}

.mcp-header {
  margin-bottom: 36px;
  display: flex;
  align-items: flex-start;
  gap: 16px;

  .mcp-icon-wrapper {
    position: relative;
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 24px;
    flex-shrink: 0;
    box-shadow: 0 8px 16px -4px rgba(37, 99, 235, 0.3);

    .icon-glow {
      position: absolute;
      inset: -4px;
      background: inherit;
      filter: blur(8px);
      opacity: 0.4;
      z-index: -1;
    }
  }

  .mcp-title-group {
    h2 { font-size: 20px; font-weight: 800; color: #0f172a; margin: 0 0 6px 0; letter-spacing: -0.02em; }
    p { font-size: 13px; color: #64748b; margin: 0; line-height: 1.6; }
  }
}

.mcp-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 28px;

  .label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    
    label { font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }
    
    .quick-examples {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      
      .example-link {
        color: #3b82f6;
        cursor: pointer;
        opacity: 0.7;
        transition: opacity 0.2s;
        &:hover { opacity: 1; text-decoration: underline; }
      }
      .divider { width: 1px; height: 10px; background: #e2e8f0; }
    }
  }

  .input-container {
    position: relative;
    .input-decoration {
      position: absolute;
      bottom: 12px;
      right: 12px;
      color: #94a3b8;
      font-size: 18px;
      pointer-events: none;
      opacity: 0.5;
    }
  }

  .options-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;

    .option-card {
      background: #f8fafc;
      border: 1px solid #f1f5f9;
      border-radius: 16px;
      padding: 14px;
      transition: all 0.3s ease;
      
      &.active {
        background: #eff6ff;
        border-color: #bfdbfe;
      }

      .option-info {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 10px;
        .option-label { font-size: 12px; font-weight: 600; color: #64748b; }
        .info-icon { font-size: 14px; color: #94a3b8; cursor: help; }
      }
      
      .premium-number {
        width: 100%;
        :deep(.el-input__inner) { text-align: left; font-weight: 600; }
      }
    }
  }
}

.premium-textarea {
  :deep(.el-textarea__inner) {
    padding: 16px;
    border-radius: 16px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    font-size: 14px;
    line-height: 1.6;
    color: #1e293b;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:focus {
      background: #fff;
      border-color: #3b82f6;
      box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
    }
  }
}

.mcp-footer {
  margin-top: 32px;
  .start-btn {
    width: 100%;
    height: 54px;
    font-size: 16px;
    font-weight: 700;
    border-radius: 16px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    border: none;
    box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.4);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    
    &:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 15px 30px -5px rgba(37, 99, 235, 0.5);
    }
    
    &:active:not(:disabled) { transform: translateY(0); }
    
    &:disabled {
      background: #e2e8f0;
      box-shadow: none;
      color: #94a3b8;
    }
  }
}

// --- 右侧面板 ---
.mcp-right-panel {
  flex: 1;
  padding: 24px; // 减小面板内边距
  background: #f1f5f9;
  position: relative;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow-y: auto;
  overflow-x: hidden;

  // 隐藏滚动条但保留滚动功能 (Premium Look)
  &::-webkit-scrollbar {
    display: none;
  }
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.panel-mesh-bg {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
  background-size: 24px 24px;
  opacity: 0.2;
}

.panel-glow-1 {
  position: absolute;
  top: -10%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
  filter: blur(40px);
}

.panel-glow-2 {
  position: absolute;
  bottom: -10%;
  left: -10%;
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(147, 51, 234, 0.1) 0%, transparent 70%);
  filter: blur(40px);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  position: relative;
  z-index: 2;

  .header-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 15px;
    font-weight: 700;
    color: #334155;
    .el-icon { font-size: 18px; color: #3b82f6; }
  }

  .loading-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 20px;
    color: #2563eb;
    font-size: 12px;
    font-weight: 600;
  }
}

.panel-content {
  flex: 1;
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 12px; // 进一步减小间距
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;

  .empty-illustration {
    position: relative;
    margin-bottom: 24px;
    
    .pulse-ring {
      position: absolute;
      inset: -20px;
      border: 2px solid rgba(59, 130, 246, 0.1);
      border-radius: 50%;
      animation: pulse 2s infinite;
    }

    .icon-box {
      width: 80px;
      height: 80px;
      background: #fff;
      border-radius: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      color: #cbd5e1;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
    }
  }

  .main-text { font-size: 16px; font-weight: 600; color: #475569; margin: 0 0 6px 0; }
  .sub-text { font-size: 13px; color: #94a3b8; margin: 0; }
}

.preview-card-wrapper {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  
  &.in-progress {
    transform: scale(0.95);
    opacity: 0.9;
    
    .glass-card {
      background: rgba(255, 255, 255, 0.6);
    }
    
    .product-image-box {
      width: 60px;
      height: 60px;
    }
    
    .product-title {
      font-size: 14px;
      -webkit-line-clamp: 1;
    }
  }
}

.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  
  .card-glow {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  }

  &.is-invalid {
    .card-glow { background: #ef4444; }
  }
}

.valid-content {
  padding: 24px;
  display: flex;
  gap: 24px;

  .product-image-box {
    width: 100px;
    height: 100px;
    background: #fff;
    border-radius: 16px;
    padding: 8px;
    border: 1px solid #f1f5f9;
    display: flex;
    align-items: center;
    justify-content: center;
    .el-image { width: 100%; height: 100%; }
    .el-icon { font-size: 32px; color: #e2e8f0; }
  }

  .product-details {
    flex: 1;
    min-width: 0;
    
    .details-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
      
      .type-badge {
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.05em;
        &.asin { background: #fef3c7; color: #d97706; }
        &.category_id { background: #dcfce7; color: #16a34a; }
      }
      .id-code { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #64748b; }
    }

    .product-title {
      font-size: 16px;
      font-weight: 700;
      color: #1e293b;
      line-height: 1.5;
      margin: 0 0 12px 0;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .category-tag {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: #64748b;
      background: #f8fafc;
      padding: 6px 12px;
      border-radius: 10px;
      width: fit-content;
      b { color: #0f172a; }
    }
  }
}

.error-content {
  padding: 32px;
  display: flex;
  align-items: flex-start;
  gap: 20px;

  .error-visual {
    .error-icon-box {
      width: 56px;
      height: 56px;
      background: #fef2f2;
      border-radius: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      color: #ef4444;
      box-shadow: 0 8px 16px -4px rgba(239, 68, 68, 0.2);
    }
  }

  .error-info {
    flex: 1;
    .error-title { font-size: 18px; font-weight: 800; color: #991b1b; margin: 0 0 6px 0; }
    .error-message { font-size: 14px; color: #b91c1c; line-height: 1.6; margin: 0 0 16px 0; opacity: 0.8; }
    .mock-action {
      .el-button { font-weight: 700; padding: 0; }
    }
  }
}

.progress-container {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-bottom: 10px; // 留一点底部呼吸空间
}

.progress-glass-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 32px;
  padding: 24px; // 减小内边距
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 100%;
  max-width: 360px;
  margin: 0 auto;

  .progress-visual {
    margin-bottom: 16px; // 减小间距
    .premium-progress {
      :deep(.el-progress-circle__track) { stroke: #f1f5f9; }
      :deep(.el-progress-circle__path) { stroke: url(#progress-grad); }
    }
    .progress-inner {
      display: flex;
      flex-direction: column;
      .percent-val { font-size: 24px; font-weight: 800; color: #0f172a; letter-spacing: -0.02em; }
      .percent-label { font-size: 9px; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
    }
  }

  .status-msg { font-size: 15px; font-weight: 800; color: #1e293b; margin: 0 0 4px 0; }
  .status-detail { font-size: 11px; color: #64748b; margin: 0 0 20px 0; }

  .modern-steps {
    display: flex;
    justify-content: center;
    gap: 16px; // 减小间距
    margin-bottom: 20px;
    width: 100%;
    
    .m-step {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      flex: 1;
      min-width: 0;
      
      .m-step-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #e2e8f0;
        transition: all 0.4s ease;
      }
      
      span { 
        font-size: 10px; // 略微缩小
        font-weight: 700; 
        color: #94a3b8;
        line-height: 1.2;
        margin-top: 4px;
        // 允许在极窄情况下换行，防止撑开宽度
        display: block;
        max-width: 60px;
        text-align: center;
      }
      
      &.active {
        .m-step-dot { background: #3b82f6; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2); }
        span { color: #3b82f6; }
      }
      
      &.done {
        .m-step-dot { background: #10b981; }
        span { color: #10b981; }
      }
    }
  }

  .success-finish-btn {
    width: 100%;
    height: 50px;
    font-size: 15px;
    font-weight: 700;
    box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.3);
  }
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.2; }
  100% { transform: scale(1); opacity: 0.5; }
}

.animate-slide-up {
  animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>
