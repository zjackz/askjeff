<template>
  <div class="sidebar-content">
    <!-- API Info Section -->
    <div class="sidebar-section info-section" v-if="currentDoc">
      <div class="doc-header">
        <span class="doc-title">{{ currentDoc.title }}</span>
        <el-tag size="small" type="info" effect="plain">{{ currentDoc.cost }}</el-tag>
      </div>
      <p class="doc-desc">{{ currentDoc.description }}</p>
      <div class="doc-note" v-if="currentDoc.note">
        <el-icon><Warning /></el-icon>
        <span>{{ currentDoc.note }}</span>
      </div>
    </div>

    <!-- Parameters Section -->
    <div class="sidebar-section params-section">
      <h4 class="section-header">Request Parameters</h4>
      
      <!-- Common Domain Selector -->
      <div class="param-group">
        <label>Domain (站点)</label>
        <el-select :model-value="form.domain" @update:model-value="updateForm('domain', $event)" style="width: 100%">
          <el-option label="US (美国)" :value="1" />
          <el-option label="GB (英国)" :value="2" />
          <el-option label="DE (德国)" :value="3" />
          <el-option label="JP (日本)" :value="7" />
          <el-option label="FR (法国)" :value="4" />
          <el-option label="IN (印度)" :value="5" />
          <el-option label="CA (加拿大)" :value="6" />
          <el-option label="ES (西班牙)" :value="8" />
          <el-option label="IT (意大利)" :value="9" />
          <el-option label="MX (墨西哥)" :value="10" />
          <el-option label="AU (澳洲)" :value="12" />
        </el-select>
      </div>

      <!-- Dynamic Parameters Based on Endpoint -->
      <component 
        :is="'div'" 
        v-for="param in endpointParams" 
        :key="param.key"
        class="param-group"
      >
        <label>{{ param.label }}</label>
        
        <!-- Text Input -->
        <el-input 
          v-if="param.type === 'text'"
          :model-value="form[param.key]"
          @update:model-value="updateForm(param.key, $event)"
          :placeholder="param.placeholder"
        />
        
        <!-- Textarea -->
        <el-input 
          v-else-if="param.type === 'textarea'"
          :model-value="form[param.key]"
          @update:model-value="updateForm(param.key, $event)"
          type="textarea"
          :rows="param.rows || 4"
          :placeholder="param.placeholder"
          resize="none"
        />
        
        <!-- Number Input -->
        <el-input-number 
          v-else-if="param.type === 'number'"
          :model-value="form[param.key]"
          @update:model-value="updateForm(param.key, $event)"
          :min="param.min || 0"
          :max="param.max"
          controls-position="right"
          style="width: 100%"
        />
        
        <!-- Select -->
        <el-select 
          v-else-if="param.type === 'select'"
          :model-value="form[param.key]"
          @update:model-value="updateForm(param.key, $event)"
          style="width: 100%"
        >
          <el-option 
            v-for="opt in param.options" 
            :key="opt.value" 
            :label="opt.label" 
            :value="opt.value" 
          />
        </el-select>
        
        <!-- Switch -->
        <el-switch 
          v-else-if="param.type === 'switch'"
          :model-value="form[param.key]"
          @update:model-value="updateForm(param.key, $event)"
          :active-value="1"
          :inactive-value="0"
        />
        
        <div v-if="param.tip" class="param-tip">{{ param.tip }}</div>
      </component>

      <!-- Empty State for No Params -->
      <div v-if="endpointParams.length === 0" class="empty-param">
        <el-alert title="无需额外参数" type="info" :closable="false" show-icon />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Warning } from '@element-plus/icons-vue'
import type { ApiDoc } from '../composables/useEndpointConfig'

interface Props {
  activeEndpoint: string
  form: Record<string, any>
  currentDoc: ApiDoc | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:form': [form: Record<string, any>]
}>()

const updateForm = (key: string, value: any) => {
  emit('update:form', { ...props.form, [key]: value })
}

// 根据端点动态生成参数配置
const endpointParams = computed(() => {
  const params: any[] = []
  
  switch (props.activeEndpoint) {
    case 'product':
      params.push({
        key: 'asins',
        label: 'ASINs (逗号分隔)',
        type: 'textarea',
        rows: 6,
        placeholder: 'B0C135XWWH, B081P4LF73',
        tip: '支持多ASIN查询，按实际数量扣费。'
      })
      break
      
    case 'category':
    case 'category-products':
      params.push({
        key: 'nodeId',
        label: 'Node ID',
        type: 'text',
        placeholder: 'e.g. 172282',
        tip: '查询类目 Top100 产品。'
      })
      if (props.activeEndpoint === 'category-products') {
        params.push({ key: 'page', label: 'Page', type: 'number', min: 1 })
      }
      break
      
    case 'category-trend':
      params.push(
        { key: 'nodeId', label: 'Node ID', type: 'text', placeholder: 'e.g. 172282' },
        { key: 'trendIndex', label: 'Trend Index', type: 'number', min: 0 }
      )
      break
      
    case 'product-query':
      params.push(
        {
          key: 'queryType',
          label: 'Query Type',
          type: 'select',
          options: [
            { label: 'New Release', value: 1 },
            { label: 'Movers & Shakers', value: 2 },
            { label: 'Most Wished For', value: 3 },
            { label: 'Gift Ideas', value: 4 }
          ]
        },
        { key: 'pattern', label: 'Pattern (Optional)', type: 'text', placeholder: 'Filter pattern...' },
        { key: 'page', label: 'Page', type: 'number', min: 1 }
      )
      break
      
    case 'keyword-query':
    case 'keyword-search-results':
      params.push(
        { key: 'keyword', label: 'Keyword', type: 'text', placeholder: 'e.g. iphone case' },
        { key: 'page', label: 'Page', type: 'number', min: 1 }
      )
      break
      
    case 'keyword-detail':
      params.push({ key: 'keyword', label: 'Keyword', type: 'text', placeholder: 'e.g. iphone case' })
      break
      
    case 'asin-sales-volume':
      params.push(
        { key: 'asins', label: 'ASIN', type: 'text', placeholder: 'Single ASIN' },
        { key: 'queryStart', label: 'Start Date (Optional)', type: 'text', placeholder: 'yyyy-MM-dd' },
        { key: 'queryEnd', label: 'End Date (Optional)', type: 'text', placeholder: 'yyyy-MM-dd' }
      )
      break
      
    case 'product-variation-history':
      params.push({ key: 'asins', label: 'ASIN', type: 'text', placeholder: 'Single ASIN' })
      break
      
    case 'product-trend':
      params.push(
        { key: 'asins', label: 'ASIN', type: 'text', placeholder: 'Single ASIN' },
        { key: 'queryStart', label: 'Start Date', type: 'text', placeholder: 'yyyy-MM-dd' },
        { key: 'queryEnd', label: 'End Date', type: 'text', placeholder: 'yyyy-MM-dd' },
        { key: 'trendIndex', label: 'Trend Type', type: 'number', min: 0 }
      )
      break
      
    case 'product-realtime':
      params.push(
        { key: 'asins', label: 'ASIN', type: 'text', placeholder: 'Single ASIN' },
        { key: 'update', label: 'Update Threshold (Hours)', type: 'number', min: 1, max: 120 }
      )
      break
      
    case 'product-realtime-status':
      params.push({ key: 'queryStart', label: 'Query Date', type: 'text', placeholder: 'yyyy-MM-dd' })
      break
      
    case 'reviews-collection':
      params.push(
        { key: 'asins', label: 'ASIN', type: 'text', placeholder: 'Single ASIN' },
        {
          key: 'mode',
          label: 'Mode',
          type: 'select',
          options: [
            { label: 'Top Reviews', value: 0 },
            { label: 'Most Recent', value: 1 }
          ]
        },
        { key: 'star', label: 'Star Filter (e.g. 1,5)', type: 'text', placeholder: 'Optional' },
        { key: 'onlyPurchase', label: 'Only Purchase', type: 'switch' },
        { key: 'page', label: 'Pages (Cost 1pt/page)', type: 'number', min: 1, max: 10 }
      )
      break
      
    case 'reviews-collection-status':
      params.push(
        { key: 'asins', label: 'ASIN', type: 'text', placeholder: 'Single ASIN' },
        { key: 'update', label: 'Update (Hours)', type: 'number', min: 1, max: 240 }
      )
      break
      
    case 'reviews-query':
      params.push(
        { key: 'asins', label: 'ASIN', type: 'text', placeholder: 'Single ASIN' },
        { key: 'queryStart', label: 'Start Date', type: 'text', placeholder: 'yyyy-MM-dd' },
        { key: 'star', label: 'Star Filter', type: 'text', placeholder: 'e.g. 5' },
        { key: 'onlyPurchase', label: 'Only Purchase', type: 'switch' },
        { key: 'page', label: 'Page', type: 'number', min: 1 }
      )
      break
      
    case 'similar-product-realtime':
      params.push({ key: 'image', label: 'Image (Base64)', type: 'textarea', rows: 4, placeholder: 'Base64 string...' })
      break
      
    case 'similar-product-status':
      params.push({ key: 'update', label: 'Update (Hours)', type: 'number', min: 1, max: 240 })
      break
      
    case 'similar-product-result':
      params.push({ key: 'taskId', label: 'Task ID', type: 'text', placeholder: 'Task ID from realtime request' })
      break
      
    // Keyword/Page endpoints
    case 'keyword-search-result-trend':
    case 'keyword-product-ranking':
      params.push(
        { key: 'keyword', label: 'Keyword', type: 'text', placeholder: 'e.g. iphone case' },
        { key: 'page', label: 'Page', type: 'number', min: 1 }
      )
      break
      
    case 'category-request-keyword':
      params.push(
        { key: 'nodeId', label: 'Node ID', type: 'text', placeholder: 'e.g. 172282' },
        { key: 'page', label: 'Page', type: 'number', min: 1 }
      )
      break
      
    case 'asin-request-keyword':
      params.push(
        { key: 'asins', label: 'ASIN', type: 'text', placeholder: 'Single ASIN' },
        { key: 'page', label: 'Page', type: 'number', min: 1 }
      )
      break
      
    case 'asin-keyword-ranking':
      params.push(
        { key: 'keyword', label: 'Keyword', type: 'text', placeholder: 'e.g. iphone case' },
        { key: 'asins', label: 'ASIN', type: 'text', placeholder: 'Single ASIN' },
        { key: 'queryStart', label: 'Start Date', type: 'text', placeholder: 'yyyy-MM-dd' },
        { key: 'queryEnd', label: 'End Date', type: 'text', placeholder: 'yyyy-MM-dd' },
        { key: 'page', label: 'Page', type: 'number', min: 1 }
      )
      break
      
    // Subscription endpoints
    case 'keyword-subscription':
    case 'best-seller-list-subscription':
    case 'product-seller-subscription':
    case 'asin-subscription':
      params.push({
        key: 'asins',
        label: 'Content / ASINs',
        type: 'textarea',
        rows: 6,
        placeholder: 'Format varies by API. Check docs.',
        tip: 'Use this field for the complex subscription payload (e.g. "+,ASIN,1|...").'
      })
      break
      
    // Task query endpoints (page only)
    case 'keyword-tasks':
    case 'best-seller-list-task':
    case 'product-seller-tasks':
    case 'asin-subscription-query':
      params.push({ key: 'page', label: 'Page', type: 'number', min: 1 })
      break
      
    // Task update endpoints
    case 'keyword-task-update':
    case 'product-seller-task-update':
      params.push(
        { key: 'taskId', label: 'Task ID', type: 'text', placeholder: 'Task ID' },
        { key: 'update', label: 'Update Action', type: 'number', placeholder: '0:Modify, 1:Pause, 2:Start, 9:Delete' }
      )
      break
      
    // Task/Schedule ID endpoints
    case 'keyword-batch-schedule-list':
    case 'product-seller-task-schedule-list':
    case 'best-seller-list-delete':
    case 'keyword-batch-schedule-detail':
    case 'product-seller-task-schedule-detail':
      params.push({ key: 'taskId', label: 'Task / Schedule ID', type: 'text', placeholder: 'Task ID or Schedule ID' })
      break
      
    case 'best-seller-list-data-collect':
      params.push(
        { key: 'taskId', label: 'Task ID', type: 'text', placeholder: 'Task ID' },
        { key: 'queryStart', label: 'Query Date', type: 'text', placeholder: 'yyyy-MM-dd' }
      )
      break
      
    case 'asin-subscription-collection':
      params.push({ key: 'asins', label: 'ASINs', type: 'textarea', rows: 4, placeholder: 'ASINs to collect...' })
      break
      
    case 'coin-stream':
    case 'request-stream':
      params.push({ key: 'page', label: 'Page', type: 'number', min: 1 })
      break
  }
  
  return params
})
</script>

<style scoped lang="scss">
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.sidebar-section {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.info-section {
  .doc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    
    .doc-title {
      font-weight: 600;
      font-size: 14px;
      color: var(--el-text-color-primary);
    }
  }
  
  .doc-desc {
    margin: 0 0 8px 0;
    font-size: 13px;
    color: var(--el-text-color-regular);
    line-height: 1.5;
  }
  
  .doc-note {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    padding: 8px 12px;
    background: var(--el-color-warning-light-9);
    border-left: 3px solid var(--el-color-warning);
    border-radius: 4px;
    font-size: 12px;
    color: var(--el-color-warning-dark-2);
    
    .el-icon {
      flex-shrink: 0;
      margin-top: 2px;
    }
  }
}

.params-section {
  .section-header {
    margin: 0 0 16px 0;
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
}

.param-group {
  margin-bottom: 16px;
  
  label {
    display: block;
    margin-bottom: 6px;
    font-size: 13px;
    font-weight: 500;
    color: var(--el-text-color-regular);
  }
  
  .param-tip {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    font-style: italic;
  }
}

.empty-param {
  padding: 16px 0;
}
</style>
