<template>
  <div class="response-pane">
    <div class="pane-header response-header">
      <div class="tabs-wrapper">
        <span class="tab-label">Response Body</span>
      </div>
      <div class="status-bar" v-if="responseStatus">
        <!-- HTTP Status -->
        <el-tag :type="responseStatus.code === 200 ? 'success' : 'danger'" size="small" effect="plain">
          HTTP {{ responseStatus.code }}
        </el-tag>
        
        <!-- Business Status -->
        <el-tag 
          v-if="businessStatus" 
          :type="businessStatus.isError ? 'danger' : 'success'" 
          size="small"
          effect="dark"
        >
          API {{ businessStatus.code }}: {{ businessStatus.text }}
        </el-tag>

        <el-tag type="info" size="small">{{ responseStatus.time }}ms</el-tag>
        <el-button size="small" link @click="$emit('copy-response')">Copy</el-button>
      </div>
    </div>

    <div class="pane-content relative">
      <!-- Empty State -->
      <div v-if="!response && !loading && !error" class="empty-state">
        <el-empty description="Select an endpoint, configure parameters, and click Send." />
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
      </div>

      <!-- Error -->
      <div v-if="error" class="error-message">
        <el-alert 
          title="Network/Server Error" 
          type="error" 
          :description="JSON.stringify(error, null, 2)" 
          show-icon 
          :closable="false" 
        />
      </div>

      <!-- Response Content -->
      <div v-if="response">
        <!-- Business Error Alert -->
        <div v-if="businessStatus && businessStatus.isError" class="mb-4">
          <el-alert
            :title="`API Error: ${businessStatus.text}`"
            type="error"
            show-icon
            :closable="false"
          >
            <p>Code: {{ businessStatus.code }}</p>
            <p>Message: {{ response.Message || response.message }}</p>
          </el-alert>
        </div>

        <!-- Response View Tabs -->
        <el-tabs :model-value="viewMode" @update:model-value="$emit('update:viewMode', $event)" class="mb-4">
          <!-- Visual View (Only for product endpoint) -->
          <el-tab-pane 
            v-if="activeEndpoint === 'product'" 
            label="Visual View" 
            name="visual"
          >
            <div class="visual-placeholder">
              <el-alert 
                title="Visual View" 
                type="info" 
                :closable="false"
              >
                <p>产品可视化视图已简化。请使用 JSON View 查看完整数据。</p>
                <p v-if="response.data">找到 {{ Array.isArray(response.data) ? response.data.length : 1 }} 个产品</p>
              </el-alert>
            </div>
          </el-tab-pane>
          
          <!-- JSON View -->
          <el-tab-pane label="JSON View" name="json">
            <div class="json-toolbar">
              <el-select 
                :model-value="jsonOptions.selectedKeys" 
                @update:model-value="updateJsonOptions('selectedKeys', $event)"
                multiple 
                collapse-tags 
                collapse-tags-tooltip
                placeholder="Filter fields..." 
                style="width: 300px"
                clearable
              >
                <el-option v-for="key in availableKeys" :key="key" :label="key" :value="key" />
              </el-select>
              <div class="toolbar-actions">
                <el-checkbox 
                  :model-value="jsonOptions.wrap" 
                  @update:model-value="updateJsonOptions('wrap', $event)"
                  label="Wrap Lines" 
                  border 
                  size="small" 
                />
                <el-checkbox 
                  :model-value="jsonOptions.compact" 
                  @update:model-value="updateJsonOptions('compact', $event)"
                  label="Compact" 
                  border 
                  size="small" 
                />
              </div>
            </div>
            <div 
              class="code-viewer-container response-viewer" 
              :class="{ 'is-compact': jsonOptions.compact, 'is-wrap': jsonOptions.wrap }"
            >
              <pre class="code-viewer" v-html="highlightedJson"></pre>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  response: any
  loading: boolean
  error: any
  responseStatus: { code: number, text: string, time: number } | null
  businessStatus: { code: number, text: string, isError: boolean } | null
  activeEndpoint: string
  viewMode: string
  jsonOptions: {
    compact: boolean
    wrap: boolean
    selectedKeys: string[]
  }
  availableKeys: string[]
  highlightedJson: string
}

defineProps<Props>()

const emit = defineEmits<{
  'update:viewMode': [value: string]
  'update:jsonOptions': [options: any]
  'copy-response': []
}>()

const updateJsonOptions = (key: string, value: any) => {
  emit('update:jsonOptions', { key, value })
}
</script>

<style scoped lang="scss">
.response-pane {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--el-bg-color);
}

.pane-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
}

.response-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  
  .tabs-wrapper {
    .tab-label {
      font-weight: 600;
      font-size: 14px;
      color: var(--el-text-color-primary);
    }
  }
  
  .status-bar {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.pane-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  
  &.relative {
    position: relative;
  }
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.loading-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--el-border-color-lighter);
    border-top-color: var(--el-color-primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  margin-bottom: 16px;
}

.mb-4 {
  margin-bottom: 16px;
}

.visual-placeholder {
  padding: 24px;
}

.json-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  
  .toolbar-actions {
    display: flex;
    gap: 8px;
  }
}

.code-viewer-container {
  background: #1e1e1e;
  border-radius: 4px;
  overflow: auto;
  max-height: 600px;
  
  &.is-wrap {
    .code-viewer {
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  }
  
  &.is-compact {
    .code-viewer {
      font-size: 11px;
      line-height: 1.3;
    }
  }
}

.code-viewer {
  margin: 0;
  padding: 16px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #d4d4d4;
  
  :deep(.key) { color: #9cdcfe; }
  :deep(.string) { color: #ce9178; }
  :deep(.number) { color: #b5cea8; }
  :deep(.boolean) { color: #569cd6; }
  :deep(.null) { color: #569cd6; }
}
</style>
