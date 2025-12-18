<template>
  <el-card class="table-card">
    <div class="table-header">
      <h2>上传产品列表</h2>
      <div class="table-actions">
        <el-button link type="primary" @click="$emit('reload')">刷新</el-button>
        <el-button 
          type="primary" 
          :loading="exportLoading" 
          @click="$emit('export')"
        >
          导出当前筛选
        </el-button>
        <el-popover placement="bottom-end" :width="200" trigger="click">
          <template #reference>
            <el-button>列设置</el-button>
          </template>
          <div class="column-settings">
            <el-checkbox v-for="(label, key) in columnLabels" :key="key" v-model="columnVisibility[key]" :label="label" />
            <div v-if="dynamicColumns.length > 0" class="dynamic-columns-section">
              <div class="section-title">动态字段</div>
              <el-checkbox 
                v-for="col in dynamicColumns" 
                :key="col"
                v-model="columnVisibility[col]" 
                :label="col" 
              />
            </div>
          </div>
        </el-popover>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="products"
      style="width: 100%"
      @sort-change="onSortChange"
      @row-click="$emit('row-click', $event)"
    >
      <el-table-column v-if="columnVisibility.asin" prop="asin" label="ASIN" sortable="custom" width="140" />
      <el-table-column v-if="columnVisibility.title" prop="title" label="标题" min-width="240" show-overflow-tooltip />
      
      <el-table-column v-if="columnVisibility.title_cn" prop="title_cn" label="中文标题" min-width="240">
        <template #default="{ row }">
          <el-popover effect="dark" trigger="hover" placement="top" :width="400" append-to-body>
            <template #default>
              <div class="popover-content">{{ row.title_cn || '—' }}</div>
            </template>
            <template #reference>
              <div class="line-clamp-2">{{ row.title_cn || '—' }}</div>
            </template>
          </el-popover>
        </template>
      </el-table-column>

      <el-table-column v-if="columnVisibility.bullets" prop="bullets" label="五点描述" min-width="240">
        <template #default="{ row }">
          <el-popover effect="dark" trigger="hover" placement="top" :width="400" append-to-body>
            <template #default>
              <div class="popover-content">{{ row.bullets || row.raw_payload?.['Bullet Points'] || row.raw_payload?.bullets || row.raw_payload?.bullet_points || row.raw_payload?.Description || row.raw_payload?.description || '—' }}</div>
            </template>
            <template #reference>
              <div class="line-clamp-2">{{ row.bullets || row.raw_payload?.['Bullet Points'] || row.raw_payload?.bullets || row.raw_payload?.bullet_points || row.raw_payload?.Description || row.raw_payload?.description || '—' }}</div>
            </template>
          </el-popover>
        </template>
      </el-table-column>

      <el-table-column v-if="columnVisibility.bullets_cn" prop="bullets_cn" label="中文五点" min-width="240">
        <template #default="{ row }">
          <el-popover effect="dark" trigger="hover" placement="top" :width="400" append-to-body>
            <template #default>
              <div class="popover-content">{{ row.bullets_cn || '—' }}</div>
            </template>
            <template #reference>
              <div class="line-clamp-2">{{ row.bullets_cn || '—' }}</div>
            </template>
          </el-popover>
        </template>
      </el-table-column>

      <el-table-column v-if="columnVisibility.brand" prop="brand" label="品牌" width="120" show-overflow-tooltip />
      <el-table-column v-if="columnVisibility.category" prop="category" label="类目" width="120" show-overflow-tooltip />
      
      <el-table-column v-if="columnVisibility.batch_id" label="批次编号" sortable="custom" prop="batch_id" width="120">
        <template #default="{ row }">
          <span class="font-mono">#{{ row.batch_id }}</span>
        </template>
      </el-table-column>

      <el-table-column v-if="columnVisibility.validation_status" prop="validation_status" label="状态" width="100">
        <template #default="{ row }">
          {{ formatStatus(row.validation_status) }}
        </template>
      </el-table-column>

      <el-table-column v-if="columnVisibility.ingested_at" prop="ingested_at" label="更新时间" sortable="custom" width="170">
        <template #default="{ row }">
          {{ formatTime(row.ingested_at) }}
        </template>
      </el-table-column>

      <el-table-column v-if="columnVisibility.price" label="价格" width="140">
        <template #default="{ row }">
          <span>{{ row.currency }} {{ row.price }}</span>
        </template>
      </el-table-column>

      <el-table-column v-if="columnVisibility.rating" prop="rating" label="评分" width="100" />
      <el-table-column v-if="columnVisibility.reviews" prop="reviews" label="评论数" width="100" />
      <el-table-column v-if="columnVisibility.sales_rank" prop="sales_rank" label="排名" width="120" />
      
      <!-- 动态列 -->
      <template v-for="col in dynamicColumns" :key="col">
        <el-table-column v-if="columnVisibility[col]" :label="col" min-width="150">
          <template #default="{ row }">
            <el-popover effect="dark" trigger="hover" placement="top" :width="400" append-to-body>
              <template #default>
                <div class="popover-content">{{ row.raw_payload?.[col] ?? '—' }}</div>
              </template>
              <template #reference>
                <div class="line-clamp-2">{{ row.raw_payload?.[col] ?? '—' }}</div>
              </template>
            </el-popover>
          </template>
        </el-table-column>
      </template>

      <template #empty>
        <el-empty description="暂无数据" />
      </template>
    </el-table>

    <div class="pagination">
      <el-pagination
        background
        layout="prev, pager, next, sizes, total"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        :current-page="currentPage"
        :total="total"
        @size-change="$emit('update:pageSize', $event)"
        @current-change="$emit('update:currentPage', $event)"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, computed, watch } from 'vue'
import type { ProductItem } from '../types'

const props = defineProps<{
  products: ProductItem[]
  loading: boolean
  total: number
  currentPage: number
  pageSize: number
  exportLoading: boolean
}>()

const emit = defineEmits(['reload', 'export', 'sort-change', 'row-click', 'update:currentPage', 'update:pageSize'])

const COLUMN_SETTINGS_KEY = 'insight_column_settings'

const columnLabels = {
  asin: 'ASIN',
  title: '标题',
  brand: '品牌',
  category: '类目',
  batch_id: '批次编号',
  validation_status: '状态',
  ingested_at: '更新时间',
  price: '价格',
  rating: '评分',
  reviews: '评论数',
  sales_rank: '排名',
  title_cn: '中文标题',
  bullets: '五点描述',
  bullets_cn: '中文五点'
}

const columnVisibility = reactive({
  asin: true,
  title: true,
  title_cn: true,
  bullets: true,
  bullets_cn: true,
  brand: true,
  category: true,
  batch_id: true,
  validation_status: true,
  ingested_at: true,
  price: true,
  rating: true,
  reviews: true,
  sales_rank: true
}) as Record<string, boolean>

const dynamicColumns = computed(() => {
  const keys = new Set<string>()
  props.products.forEach(p => {
    if (p.raw_payload) {
      Object.keys(p.raw_payload).forEach(k => {
        const lowerK = k.toLowerCase()
        if (['asin', 'title', 'price', 'currency', 'sales_rank', 'reviews', 'rating', 'category', 'title_cn', 'bullets_cn', 'bullets', 'bullet_points', 'bullet points', 'titlecn', 'bulletscn'].includes(lowerK)) {
           return
        }
        keys.add(k)
      })
    }
  })
  return Array.from(keys).sort()
})

watch(dynamicColumns, (newCols) => {
  newCols.forEach(col => {
    if (columnVisibility[col] === undefined) {
      columnVisibility[col] = true
    }
  })
})

const loadColumnSettings = () => {
  try {
    const stored = localStorage.getItem(COLUMN_SETTINGS_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      Object.assign(columnVisibility, parsed)
    }
  } catch (e) {
    console.warn('Failed to load column settings:', e)
  }
}

watch(columnVisibility, (newSettings) => {
  localStorage.setItem(COLUMN_SETTINGS_KEY, JSON.stringify(newSettings))
}, { deep: true })

loadColumnSettings()

const onSortChange = ({ prop, order }: { prop: string; order: 'ascending' | 'descending' | null }) => {
  emit('sort-change', { 
    prop, 
    order: order === 'ascending' ? 'asc' : order === 'descending' ? 'desc' : '' 
  })
}

const formatTime = (value?: string) => {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

const formatStatus = (status?: string) => {
  const map: Record<string, string> = {
    valid: '有效',
    warning: '警告',
    error: '错误'
  }
  return map[status || ''] || status || ''
}
</script>

<style scoped lang="scss">
.table-card {
  margin-top: 20px;
}
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  h2 { margin: 0; font-size: 18px; }
}
.table-actions {
  display: flex;
  gap: 12px;
}
.column-settings {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
}
.dynamic-columns-section {
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: 8px;
  padding-top: 8px;
  .section-title {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 8px;
  }
}
.popover-content {
  word-break: break-all;
  white-space: pre-wrap;
}
.line-clamp-2 {
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  cursor: pointer;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
