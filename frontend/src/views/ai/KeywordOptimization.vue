<template>
  <div class="ai-page">
    <div class="page-header">
      <h2 class="text-xl font-bold flex items-center gap-2">
        <el-icon class="text-primary"><Key /></el-icon>
        AI 关键词优化引擎
      </h2>
      <p class="text-gray-500 text-sm mt-1">智能分析关键词数据，为您生成高转化的 Listing 标题和描述。</p>
    </div>

    <div class="content-container">
      <!-- 左侧：输入表单 -->
      <div class="input-section">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>优化配置</span>
            </div>
          </template>
          <el-form :model="form" label-position="top">
            <el-form-item label="产品 ASIN">
              <el-input v-model="form.asin" placeholder="例如: B08N5WRWNW" maxlength="10" show-word-limit />
              <div class="form-tip">请输入 10 位 ASIN</div>
            </el-form-item>
            <el-form-item label="站点">
              <el-select v-model="form.domain" placeholder="选择站点">
                <el-option label="美国 (US)" :value="1" />
                <el-option label="英国 (UK)" :value="2" />
                <el-option label="德国 (DE)" :value="3" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.include_bullet_points">同时优化五点描述</el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.use_cache">使用缓存 (推荐)</el-checkbox>
            </el-form-item>
            <el-button type="primary" class="w-full" @click="handleOptimize" :loading="loading">
              开始优化
            </el-button>
          </el-form>
        </el-card>

        <!-- 历史记录或提示 -->
        <el-card shadow="hover" class="mt-4">
          <div class="text-sm text-gray-500">
            <h4 class="font-bold mb-2">💡 提示</h4>
            <ul class="list-disc pl-4 space-y-1">
              <li>优化过程可能需要 15-20 秒。</li>
              <li>AI 将基于竞品关键词和长尾词生成建议。</li>
              <li>生成结果仅供参考，请遵守 Amazon 规范。</li>
            </ul>
          </div>
        </el-card>
      </div>

      <!-- 右侧：分析结果 -->
      <div class="result-section">
        <el-empty v-if="!result && !loading" description="请输入 ASIN 开始优化" />
        
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="10" animated />
          <p class="text-center mt-4 text-gray-500">AI 正在挖掘关键词并优化 Listing...</p>
        </div>

        <div v-if="result" class="analysis-result">
          <!-- 标题对比 -->
          <el-card shadow="never" class="mb-4">
            <template #header>
              <div class="font-bold">标题优化对比</div>
            </template>
            <div class="comparison-grid">
              <div class="original">
                <div class="label">当前标题</div>
                <div class="content">{{ result.original_title || '(无)' }}</div>
              </div>
              <div class="optimized">
                <div class="label text-primary">AI 优化标题</div>
                <div class="content font-bold">{{ result.optimized_title }}</div>
                <el-button type="primary" link size="small" class="mt-2" @click="copyText(result.optimized_title)">
                  复制标题
                </el-button>
              </div>
            </div>
          </el-card>

          <!-- 详细报告 -->
          <el-card shadow="never" class="report-card">
            <div class="markdown-body" v-html="renderedReport"></div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Key } from '@element-plus/icons-vue'
import { aiApi, type KeywordOptimizationResponse } from '@/api/ai'
import { ElMessage } from 'element-plus'
import { useClipboard } from '@vueuse/core'
import { renderMarkdown } from '@/utils/markdown'

// const md = new MarkdownIt()
const { copy } = useClipboard()
const loading = ref(false)
const form = ref({
  asin: '',
  domain: 1,
  include_bullet_points: true,
  use_cache: true
})
const result = ref<KeywordOptimizationResponse | null>(null)

const renderedReport = computed(() => {
  if (!result.value?.optimization_report) return ''
  return renderMarkdown(result.value.optimization_report)
})

const handleOptimize = async () => {
  if (!form.value.asin || form.value.asin.length !== 10) {
    ElMessage.warning('请输入有效的 10 位 ASIN')
    return
  }
  
  loading.value = true
  result.value = null
  
  try {
    const { data } = await aiApi.optimizeKeywords(form.value)
    result.value = data
    ElMessage.success('优化完成')
  } catch (err: any) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const copyText = (text: string) => {
  copy(text)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped lang="scss">
.ai-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  background: #fff;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
}

.content-container {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
}

.input-section {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-section {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
  overflow-y: auto;
}

.comparison-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  
  .label {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }
  
  .content {
    font-size: 14px;
    line-height: 1.5;
    color: var(--text-primary);
    background: var(--bg-secondary);
    padding: 12px;
    border-radius: 6px;
    min-height: 80px;
  }
}

.report-card {
  border: none;
  
  :deep(.markdown-body) {
    h1, h2, h3 { margin-top: 1.5em; margin-bottom: 0.5em; font-weight: bold; color: var(--text-primary); }
    h2 { font-size: 1.5em; border-bottom: 1px solid var(--border-light); padding-bottom: 0.3em; }
    h3 { font-size: 1.25em; }
    p { margin-bottom: 1em; line-height: 1.6; color: var(--text-secondary); }
    ul, ol { padding-left: 1.5em; margin-bottom: 1em; }
    li { margin-bottom: 0.5em; }
    strong { color: var(--primary-color); }
  }
}

.form-tip {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
}
</style>
