<template>
  <div class="ai-page">
    <div class="page-header">
      <h2 class="text-xl font-bold flex items-center gap-2">
        <el-icon class="text-primary"><DataAnalysis /></el-icon>
        AI 智能选品助手
      </h2>
      <p class="text-gray-500 text-sm mt-1">基于 Sorftime 大数据和 DeepSeek AI，为您深度分析市场机会。</p>
    </div>

    <div class="content-container">
      <!-- 左侧：输入表单 -->
      <div class="input-section">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>分析配置</span>
            </div>
          </template>
          <el-form :model="form" label-position="top">
            <el-form-item label="类目 ID (Node ID)">
              <el-input v-model="form.category_id" placeholder="例如: 172282 (Electronics)" />
              <div class="form-tip">请输入 Amazon 类目 Node ID</div>
            </el-form-item>
            <el-form-item label="站点">
              <el-select v-model="form.domain" placeholder="选择站点">
                <el-option label="美国 (US)" :value="1" />
                <el-option label="英国 (UK)" :value="2" />
                <el-option label="德国 (DE)" :value="3" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.use_cache">使用缓存 (推荐)</el-checkbox>
            </el-form-item>
            <el-button type="primary" class="w-full" @click="handleAnalyze" :loading="loading">
              开始分析
            </el-button>
          </el-form>
        </el-card>

        <!-- 历史记录或提示 -->
        <el-card shadow="hover" class="mt-4">
          <div class="text-sm text-gray-500">
            <h4 class="font-bold mb-2">💡 提示</h4>
            <ul class="list-disc pl-4 space-y-1">
              <li>分析过程可能需要 20-30 秒，请耐心等待。</li>
              <li>建议优先分析二级或三级细分类目。</li>
              <li>评分仅供参考，请结合实际情况决策。</li>
            </ul>
          </div>
        </el-card>
      </div>

      <!-- 右侧：分析结果 -->
      <div class="result-section">
        <el-empty v-if="!result && !loading" description="请输入类目 ID 开始分析" />
        
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="10" animated />
          <p class="text-center mt-4 text-gray-500">AI 正在深入分析市场数据...</p>
        </div>

        <div v-if="result" class="analysis-result">
          <!-- 核心指标卡片 -->
          <div class="metrics-grid">
            <div class="metric-card score-card">
              <div class="label">市场机会评分</div>
              <div class="value" :class="getScoreColor(result.market_score)">{{ result.market_score }}</div>
              <div class="sub">/ 10</div>
            </div>
            <div class="metric-card">
              <div class="label">平均价格</div>
              <div class="value">${{ result.statistics.avg_price }}</div>
            </div>
            <div class="metric-card">
              <div class="label">平均评分</div>
              <div class="value">{{ result.statistics.avg_rating }}</div>
            </div>
            <div class="metric-card">
              <div class="label">竞争强度</div>
              <div class="value">{{ result.statistics.competition_level }}</div>
            </div>
          </div>

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
import { DataAnalysis } from '@element-plus/icons-vue'
import { aiApi, type ProductSelectionResponse } from '@/api/ai'
import { ElMessage } from 'element-plus'
import { renderMarkdown } from '@/utils/markdown'

// const md = new MarkdownIt()
const loading = ref(false)
const form = ref({
  category_id: '',
  domain: 1,
  use_cache: true
})
const result = ref<ProductSelectionResponse | null>(null)

const renderedReport = computed(() => {
  if (!result.value?.analysis) return ''
  return renderMarkdown(result.value.analysis)
})

const handleAnalyze = async () => {
  if (!form.value.category_id) {
    ElMessage.warning('请输入类目 ID')
    return
  }
  
  loading.value = true
  result.value = null
  
  try {
    const { data } = await aiApi.analyzeProductSelection(form.value)
    result.value = data
    ElMessage.success('分析完成')
  } catch (err: any) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const getScoreColor = (score: number) => {
  if (score >= 8) return 'text-green-500'
  if (score >= 6) return 'text-blue-500'
  return 'text-orange-500'
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
  min-height: 0; // Important for scrolling
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

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  
  .label {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }
  
  .value {
    font-size: 24px;
    font-weight: bold;
    color: var(--text-primary);
  }
  
  &.score-card {
    background: rgba(16, 185, 129, 0.1);
    .value {
      display: inline-block;
    }
    .sub {
      display: inline-block;
      font-size: 14px;
      color: var(--text-secondary);
      margin-left: 4px;
    }
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

.text-green-500 { color: var(--success-color); }
.text-blue-500 { color: var(--primary-color); }
.text-orange-500 { color: var(--warning-color); }
</style>
