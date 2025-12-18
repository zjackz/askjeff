<!-- 错误边界组件 -->
<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <el-icon class="error-icon" :size="64"><WarningFilled /></el-icon>
      <h2>页面加载失败</h2>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <el-button type="primary" @click="handleReload">刷新页面</el-button>
        <el-button @click="handleGoHome">返回首页</el-button>
      </div>
      <el-collapse v-if="showDetails" class="error-details">
        <el-collapse-item title="错误详情" name="1">
          <pre>{{ errorDetails }}</pre>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import { WarningFilled } from '@element-plus/icons-vue'
import { logger } from '@/utils/logger'

const router = useRouter()
const hasError = ref(false)
const errorMessage = ref('')
const errorDetails = ref('')
const showDetails = ref((import.meta as any).env.DEV) // 仅在开发环境显示详情

onErrorCaptured((err: Error) => {
  hasError.value = true
  errorMessage.value = '抱歉,页面遇到了一些问题'
  errorDetails.value = `${err.message}\n\n${err.stack}`
  
  // 记录错误
  logger.error('ErrorBoundary caught error', err)
  
  // 阻止错误继续传播
  return false
})

const handleReload = () => {
  window.location.reload()
}

const handleGoHome = () => {
  hasError.value = false
  router.push('/')
}
</script>

<style scoped lang="scss">
.error-boundary {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  padding: 24px;
}

.error-content {
  max-width: 600px;
  text-align: center;
  background: #fff;
  padding: 48px;
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
}

.error-icon {
  color: var(--danger-color);
  margin-bottom: 24px;
}

h2 {
  margin: 0 0 12px;
  color: var(--text-primary);
  font-size: 24px;
}

.error-message {
  color: var(--text-secondary);
  margin: 0 0 32px;
  font-size: 16px;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 24px;
}

.error-details {
  margin-top: 24px;
  text-align: left;
  
  pre {
    background: var(--bg-secondary);
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 12px;
    color: var(--text-secondary);
  }
}
</style>
