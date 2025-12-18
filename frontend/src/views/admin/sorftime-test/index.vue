<template>
  <div class="postman-container">
    <div class="main-content">
      <!-- Left Pane: Request Configuration -->
      <div class="pane request-pane">
        <EndpointSelector
          v-model="activeEndpoint"
          :loading="loading"
          :history-count="requestHistory.length"
          @load-example="loadExample"
          @show-history="historyDrawerVisible = true"
          @show-shortcuts="shortcutsDialogVisible = true"
          @show-stats="statsDrawerVisible = true"
          @send-request="handleSend"
        />
        
        <RequestForm
          :active-endpoint="activeEndpoint"
          :form="form"
          :current-doc="currentDoc"
          @update:form="Object.assign(form, $event)"
        />
      </div>
      
      <!-- Right Pane: Response -->
      <div class="pane response-pane">
        <ResponseViewer
          :response="response"
          :loading="loading"
          :error="error"
          :response-status="responseStatus"
          :business-status="businessStatus"
          :active-endpoint="activeEndpoint"
          v-model:view-mode="responseViewMode"
          :json-options="jsonViewOptions"
          :available-keys="availableKeys"
          :highlighted-json="highlightJson(filteredResponse)"
          @update:json-options="handleJsonOptionsUpdate"
          @copy-response="copyResponse"
        />
      </div>
    </div>
    
    <!-- Drawers & Dialogs -->
    <HistoryDrawer
      v-model:visible="historyDrawerVisible"
      :history="requestHistory"
      @load-item="loadHistoryItem"
      @delete-item="deleteHistoryItem"
      @clear-all="clearHistory"
    />
    
    <StatsDrawer 
      v-model:visible="statsDrawerVisible"
      :stats="sessionStats"
      :success-rate="successRate"
      :avg-response-time="avgResponseTime"
    />
    
    <ShortcutsDialog v-model:visible="shortcutsDialogVisible" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import EndpointSelector from './components/EndpointSelector.vue'
import RequestForm from './components/RequestForm.vue'
import ResponseViewer from './components/ResponseViewer.vue'
import HistoryDrawer from './components/HistoryDrawer.vue'
import StatsDrawer from './components/StatsDrawer.vue'
import ShortcutsDialog from './components/ShortcutsDialog.vue'

import { useEndpointConfig } from './composables/useEndpointConfig'
import { useApiRequest } from './composables/useApiRequest'
import { useRequestHistory } from './composables/useRequestHistory'
import { useJsonHighlight } from './composables/useJsonHighlight'

// 状态
const activeEndpoint = ref('product')
const responseViewMode = ref('json')
const historyDrawerVisible = ref(false)
const shortcutsDialogVisible = ref(false)
const statsDrawerVisible = ref(false)

// 表单数据
const form = reactive({
  domain: 1,
  asins: 'B0C135XWWH',
  nodeId: '',
  trendIndex: 0,
  queryType: 1,
  pattern: '',
  page: 1,
  keyword: '',
  queryStart: '',
  queryEnd: '',
  update: 24,
  mode: 0,
  star: '',
  onlyPurchase: 0,
  taskId: '',
  image: ''
})

// 使用 composables
const { currentDoc, loadExample: loadExampleFn, getRequestPayload } = useEndpointConfig(activeEndpoint, form)
const { loading, response, error, responseStatus, businessStatus, sendRequest, copyResponse } = useApiRequest()
const { 
  requestHistory, 
  sessionStats, 
  successRate, 
  avgResponseTime,
  saveToHistory, 
  loadHistory, 
  deleteHistoryItem, 
  clearHistory,
  formatTime
} = useRequestHistory()
const { jsonViewOptions, availableKeys, filteredResponse, highlightJson } = useJsonHighlight(response)

// 加载示例
const loadExample = () => {
  loadExampleFn()
}

// 发送请求
const handleSend = async () => {
  const payload = getRequestPayload()
  const result = await sendRequest(activeEndpoint.value, payload)
  
  // 保存历史记录
  const cost = parseInt(currentDoc.value?.cost.match(/\d+/)?.[0] || '0')
  saveToHistory(
    activeEndpoint.value as any,
    form,
    result.startTime,
    result.success,
    result.statusCode,
    cost
  )
  
  // 切换视图模式
  if (activeEndpoint.value === 'product' && response.value?.data) {
    responseViewMode.value = 'visual'
  } else {
    responseViewMode.value = 'json'
  }
}

// 加载历史记录项
const loadHistoryItem = (item: any) => {
  activeEndpoint.value = item.endpoint
  Object.assign(form, item.params)
  historyDrawerVisible.value = false
  ElMessage.success('已加载历史请求配置')
}

// 更新 JSON 选项
const handleJsonOptionsUpdate = ({ key, value }: { key: string, value: any }) => {
  (jsonViewOptions as any)[key] = value
}

// 键盘快捷键
const handleKeyboard = (e: KeyboardEvent) => {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
  const modifier = isMac ? e.metaKey : e.ctrlKey
  
  if (!modifier) return
  
  switch(e.key.toLowerCase()) {
    case 'enter':
      e.preventDefault()
      if (!loading.value) handleSend()
      break
    case 'k':
      e.preventDefault()
      Object.assign(form, {
        asins: '',
        nodeId: '',
        keyword: '',
        pattern: '',
        queryStart: '',
        queryEnd: ''
      })
      ElMessage.info('表单已清空')
      break
    case 'h':
      e.preventDefault()
      historyDrawerVisible.value = !historyDrawerVisible.value
      break
    case 'l':
      e.preventDefault()
      loadExample()
      break
    case '/':
      e.preventDefault()
      shortcutsDialogVisible.value = true
      break
  }
}

// 生命周期
onMounted(() => {
  loadHistory()
  document.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyboard)
})
</script>

<style scoped lang="scss">
.postman-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 450px 1fr;
  gap: 0;
  overflow: hidden;
}

.pane {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--el-bg-color);
  
  &.request-pane {
    border-right: 1px solid var(--el-border-color-lighter);
  }
}
</style>
