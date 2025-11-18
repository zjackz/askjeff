<template>
  <div class="logs-page">
    <el-card class="filters">
      <div class="filter-row">
        <el-select v-model="level" placeholder="级别" clearable style="width: 140px">
          <el-option label="全部" value="" />
          <el-option label="Info" value="info" />
          <el-option label="Warning" value="warning" />
          <el-option label="Error" value="error" />
        </el-select>
        <el-input v-model="category" placeholder="分类（如 api_request）" style="width: 220px" />
        <el-input v-model="keyword" placeholder="关键字" style="width: 240px" />
        <el-button type="primary" :loading="loading" @click="fetchLogs">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" :loading="analyzing" @click="analyzeLogs">AI 分析</el-button>
      </div>
    </el-card>

    <el-card>
      <el-table :data="logs" height="420" :loading="loading" border>
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="level" label="级别" width="90" />
        <el-table-column prop="category" label="分类" width="140" />
        <el-table-column prop="message" label="摘要" min-width="200" />
        <el-table-column label="上下文">
          <template #default="{ row }">
            <pre class="ctx">{{ formatContext(row.context) }}</pre>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          @current-change="onPageChange"
        />
      </div>
    </el-card>

    <el-card v-if="analysis.summary">
      <h3>AI 诊断</h3>
      <p>{{ analysis.summary }}</p>
      <div v-if="analysis.probableCauses.length">
        <h4>可能原因</h4>
        <ul>
          <li v-for="cause in analysis.probableCauses" :key="cause">{{ cause }}</li>
        </ul>
      </div>
      <div v-if="analysis.suggestions.length">
        <h4>建议</h4>
        <ul>
          <li v-for="s in analysis.suggestions" :key="s">{{ s }}</li>
        </ul>
      </div>
    </el-card>
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

const logs = ref<LogRow[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const level = ref('')
const category = ref('')
const keyword = ref('')
const loading = ref(false)
const analyzing = ref(false)
const analysis = ref<AnalysisResult>({ summary: '', probableCauses: [], suggestions: [], usedAi: false })

const fetchLogs = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('http://localhost:8000/logs', {
      params: {
        level: level.value || undefined,
        category: category.value || undefined,
        keyword: keyword.value || undefined,
        page: page.value,
        pageSize
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
    const { data } = await axios.post('http://localhost:8000/logs/analyze', {
      logIds: ids
    })
    analysis.value = data
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
    return JSON.stringify(ctx, null, 2)
  } catch (e) {
    return String(ctx)
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.logs-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pager {
  margin-top: 12px;
  text-align: right;
}

.ctx {
  white-space: pre-wrap;
  font-size: 12px;
  margin: 0;
}
</style>
