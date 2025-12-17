```html
<template>
  <div class="logs-page fade-up">
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="px-6 pt-2">
        <el-tab-pane label="系统日志" name="system" />
        <el-tab-pane label="API 调用" name="api" />
      </el-tabs>
      
      <div class="p-6 pt-4 bg-gray-50/50 border-t border-gray-100">
        <!-- 筛选工具栏 -->
        <div class="flex items-center gap-3 mb-4">
          <el-select v-model="level" placeholder="级别" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="Info" value="info" />
            <el-option label="Warn" value="warning" />
            <el-option label="Error" value="error" />
          </el-select>
          
          <el-input 
            v-if="activeTab === 'system'" 
            v-model="category" 
            placeholder="分类" 
            style="width: 140px" 
            clearable
          />
          
          <el-input 
            v-model="keyword" 
            placeholder="搜索关键字..." 
            style="width: 240px" 
            clearable
            @keyup.enter="fetchLogs"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-button type="primary" :loading="loading" @click="fetchLogs">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </div>

        <!-- 表格区域 -->
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <el-table 
            :data="logs" 
            style="width: 100%"
            :header-cell-style="{ background: '#f9fafb', color: '#374151' }"
            v-loading="loading"
          >
            <el-table-column prop="timestamp" label="时间" width="180" show-overflow-tooltip />
            
            <el-table-column prop="level" label="级别" width="90">
              <template #default="{ row }">
                <el-tag :type="getLevelType(row.level)" size="small" effect="plain">{{ row.level }}</el-tag>
              </template>
            </el-table-column>

            <!-- 系统日志特有列 -->
            <template v-if="activeTab === 'system'">
              <el-table-column prop="category" label="分类" width="140" show-overflow-tooltip />
              <el-table-column prop="message" label="消息内容" min-width="300" show-overflow-tooltip />
            </template>

            <!-- API 日志特有列 -->
            <template v-if="activeTab === 'api'">
              <el-table-column label="平台" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.context?.platform === 'Sorftime' ? 'warning' : (row.context?.platform === 'DeepSeek' ? 'success' : 'info')" effect="plain" size="small">
                    {{ row.context?.platform || 'N/A' }}
                  </el-tag>
                </template>
              </el-table-column>

              <el-table-column prop="message" label="请求 (Method & Path)" min-width="250" show-overflow-tooltip>
                <template #default="{ row }">
                  <div class="flex flex-col">
                    <span class="font-mono font-bold text-primary">{{ row.message }}</span>
                    <span class="text-xs text-gray-400 truncate font-mono">{{ row.context?.url || row.context?.path }}</span>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column label="状态 / 耗时" width="140">
                <template #default="{ row }">
                  <div class="flex items-center gap-2">
                    <el-tag v-if="row.context?.status_code || row.context?.status" :type="getHttpStatusType(row.context?.status_code || row.context?.status)" effect="dark" size="small" class="font-mono">
                      {{ row.context?.status_code || row.context?.status }}
                    </el-tag>
                    <span v-if="row.context?.duration_ms" class="text-xs text-gray-500 font-mono">
                      {{ row.context.duration_ms }}ms
                    </span>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="Quota / 响应" width="180" show-overflow-tooltip>
                 <template #default="{ row }">
                    <div v-if="row.context?.response?.requestConsumed !== undefined" class="text-xs font-mono">
                        <span class="text-gray-500">消耗:</span> <span class="text-red-500 font-bold">{{ row.context.response.requestConsumed }}</span>
                        <span class="text-gray-500 ml-2">剩余:</span> {{ row.context.response.requestLeft }}
                    </div>
                    <div v-else class="text-xs text-gray-400">-</div>
                 </template>
              </el-table-column>
            </template>

            <!-- 详情列 (共享) -->
            <el-table-column label="详情 / 上下文" width="100" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="showLogDetail(row)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 分页 -->
        <div class="mt-4 flex justify-end">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            layout="total, sizes, prev, pager, next"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="onPageChange"
            background
          />
        </div>
      </div>
    </div>

    <!-- 日志详情弹窗 -->
    <el-dialog v-model="detailVisible" title="日志详情" width="600px" destroy-on-close>
      <div class="log-detail">
        <div class="detail-item">
          <span class="label">时间:</span>
          <span>{{ currentLog?.timestamp }}</span>
        </div>
        <div class="detail-item">
          <span class="label">级别:</span>
          <el-tag :type="getLevelType(currentLog?.level || '')" size="small">{{ currentLog?.level }}</el-tag>
        </div>
        <div class="detail-item">
          <span class="label">分类:</span>
          <span>{{ currentLog?.category }}</span>
        </div>
        <div class="detail-item">
          <span class="label">消息:</span>
          <span>{{ currentLog?.message }}</span>
        </div>
        <div class="detail-section">
          <div class="label mb-2">上下文数据:</div>
          <div class="json-box">
            <pre>{{ formatJson(currentLog?.context) }}</pre>
          </div>
        </div>
      </div>
    </el-dialog>

    <div class="pager-container">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="onPageChange"
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
import { http } from '@/utils/http'
import { Search, Refresh, MagicStick, Timer } from '@element-plus/icons-vue'

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

const API_BASE = (import.meta as any).env.VITE_API_BASE_URL || 'http://localhost:8000'
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
const activeTab = ref('system')

const handleTabClick = (tab: any) => {
  page.value = 1
  level.value = ''
  keyword.value = ''
  if (tab.props.name === 'api') {
    category.value = 'external_api'
  } else {
    category.value = ''
  }
  fetchLogs()
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const { data } = await http.get('/logs', {
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
    const { data } = await http.post('/logs/analyze', {
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
  keyword.value = ''
  if (activeTab.value === 'api') {
    category.value = 'external_api'
  } else {
    category.value = ''
  }
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

const detailVisible = ref(false)
const currentLog = ref<LogRow | null>(null)

const showLogDetail = (row: LogRow) => {
  currentLog.value = row
  detailVisible.value = true
}

const formatJson = (data: any) => {
  if (!data) return '{}'
  try {
    return JSON.stringify(data, null, 2)
  } catch (e) {
    return String(data)
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

const getHttpStatusType = (status: number) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 300 && status < 400) return 'warning'
  if (status >= 400) return 'danger'
  return 'info'
}

const formatQuery = (query: any) => {
  try {
    return new URLSearchParams(query).toString()
  } catch (e) {
    return ''
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped lang="scss">
.logs-page {
  height: calc(100vh - 84px);
  display: flex;
  flex-direction: column;
  padding: 24px;
  box-sizing: border-box;
  background-color: var(--bg-secondary);
  animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  background: #fff;
  padding: 20px;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.filter-row {
  display: flex;
  align-items: center;
}

.table-container {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  padding: 0;
  transition: all 0.3s ease;
}

.pager-container {
  background: #fff;
  padding: 12px 24px;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.custom-table {
  --el-table-border-color: var(--border-light);
  
  :deep(th) {
    background: #f9fafb !important;
    color: var(--text-primary);
    font-weight: 600;
    height: 56px;
  }

  :deep(td) {
    height: 64px;
  }

  :deep(.el-table__inner-wrapper::before) {
    display: none;
  }
}

.ctx-text {
  font-family: var(--font-family-mono);
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.analysis-content {
  h3 { margin-top: 0; }
  ul { padding-left: 20px; }
}

.log-detail {
  .detail-item {
    margin-bottom: 12px;
    display: flex;
    align-items: flex-start;
    
    .label {
      font-weight: 600;
      width: 60px;
      flex-shrink: 0;
      color: var(--text-secondary);
    }
  }
  
  .detail-section {
    margin-top: 20px;
    
    .label {
      font-weight: 600;
      color: var(--text-secondary);
    }
    
    .json-box {
      background: #f8fafc;
      padding: 12px;
      border-radius: 8px;
      border: 1px solid var(--border-light);
      max-height: 400px;
      overflow: auto;
      
      pre {
        margin: 0;
        font-family: var(--font-family-mono);
        font-size: 12px;
        white-space: pre-wrap;
        word-break: break-all;
        color: var(--text-primary);
      }
    }
  }
}
</style>
