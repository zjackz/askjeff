<template>
  <div class="logs-page">
    <div class="page-header">
      <div class="filter-row">
        <h2 class="text-lg font-bold mr-4 my-0">日志中心</h2>
        <el-select v-model="level" placeholder="级别" clearable style="width: 100px" size="small">
          <el-option label="全部" value="" />
          <el-option label="Info" value="info" />
          <el-option label="Warning" value="warning" />
          <el-option label="Error" value="error" />
        </el-select>
        <el-input v-model="category" placeholder="分类" style="width: 140px" size="small" />
        <el-input v-model="keyword" placeholder="关键字" style="width: 180px" size="small" />
        <el-button type="primary" :loading="loading" @click="fetchLogs" size="small">查询</el-button>
        <el-button @click="resetFilters" size="small">重置</el-button>
        <div class="flex-grow"></div>
        <el-button type="success" :loading="analyzing" @click="analyzeLogs" size="small" plain>AI 分析</el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table 
        :data="logs" 
        height="100%" 
        :loading="loading" 
        border 
        size="small"
        class="logs-table"
      >
        <el-table-column prop="timestamp" label="时间" width="160" show-overflow-tooltip />
        <el-table-column prop="level" label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small" effect="plain">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" show-overflow-tooltip />
        <el-table-column prop="message" label="摘要" min-width="300" show-overflow-tooltip />
        <el-table-column label="上下文" min-width="200">
          <template #default="{ row }">
            <span class="ctx-text" :title="formatContext(row.context)">{{ formatContext(row.context) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pager-container">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="onPageChange"
        size="small"
      />
    </div>

    <el-drawer v-model="showAnalysis" title="AI 诊断报告" size="40%">
      <div v-if="analysis.summary" class="analysis-content">
        <h3>诊断摘要</h3>
        <p>{{ analysis.summary }}</p>
        <div v-if="analysis.probableCauses.length" class="mt-4">
          <h4>可能原因</h4>
          <ul>
            <li v-for="cause in analysis.probableCauses" :key="cause">{{ cause }}</li>
          </ul>
        </div>
        <div v-if="analysis.suggestions.length" class="mt-4">
          <h4>建议</h4>
          <ul>
            <li v-for="s in analysis.suggestions" :key="s">{{ s }}</li>
          </ul>
        </div>
      </div>
      <el-empty v-else description="暂无分析结果" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface LogRow {
  id: string
  timestamp: string
  level: string
  category: string
  message: string
  context?: Record<string, unknown>
}

interface AnalysisResult {
  summary: string
  probableCauses: string[]
  suggestions: string[]
  usedAi: boolean
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const logs = ref<LogRow[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50) // 默认 50 条
const level = ref('')
const category = ref('')
const keyword = ref('')
const loading = ref(false)
const analyzing = ref(false)
const showAnalysis = ref(false)
const analysis = ref<AnalysisResult>({ summary: '', probableCauses: [], suggestions: [], usedAi: false })

const fetchLogs = async () => {
  loading.value = true
  try {
    const { data } = await axios.get(`${API_BASE}/logs`, {
      params: {
        level: level.value || undefined,
        category: category.value || undefined,
        keyword: keyword.value || undefined,
        page: page.value,
        pageSize: pageSize.value
      }
    })
    logs.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    console.error('获取日志失败', err)
  } finally {
    loading.value = false
  }
}

const analyzeLogs = async () => {
  analyzing.value = true
  try {
    const ids = logs.value.map((item) => item.id)
    const { data } = await axios.post(`${API_BASE}/logs/analyze`, {
      logIds: ids
    })
    analysis.value = data
    showAnalysis.value = true
  } catch (err) {
    console.error('AI 分析失败', err)
  } finally {
    analyzing.value = false
  }
}

const onPageChange = (newPage: number) => {
  page.value = newPage
  fetchLogs()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchLogs()
}

const resetFilters = () => {
  level.value = ''
  category.value = ''
  keyword.value = ''
  page.value = 1
  fetchLogs()
}

const formatContext = (ctx?: Record<string, unknown>) => {
  if (!ctx) return '-'
  try {
    return JSON.stringify(ctx)
  } catch (e) {
    return String(ctx)
  }
}

const getLevelType = (level: string) => {
  const map: Record<string, string> = {
    info: 'info',
    warning: 'warning',
    error: 'danger',
    debug: 'info'
  }
  return map[level.toLowerCase()] || 'info'
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped lang="scss">
.logs-page {
  height: calc(100vh - 84px); // 减去顶部导航高度
  display: flex;
  flex-direction: column;
  padding: 16px;
  box-sizing: border-box;
  background-color: var(--bg-secondary);
}

.page-header {
  background: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 12px;
  flex-shrink: 0;
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.table-container {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  overflow: hidden; // 确保表格滚动条在容器内
  padding: 1px; // 防止边框重叠
}

.pager-container {
  background: #fff;
  padding: 8px 16px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.ctx-text {
  font-family: monospace;
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.analysis-content {
  h3 { margin-top: 0; }
  ul { padding-left: 20px; }
}
</style>
