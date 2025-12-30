<!--
通用表格组件

使用示例:
<BaseTable
  :data="tableData"
  :columns="columns"
  :loading="loading"
  @row-click="handleRowClick"
/>
-->
<template>
  <el-table
    :data="data"
    :loading="loading"
    :stripe="stripe"
    :border="border"
    :height="height"
    :max-height="maxHeight"
    @row-click="handleRowClick"
    @selection-change="handleSelectionChange"
  >
    <!-- 多选列 -->
    <el-table-column
      v-if="showSelection"
      type="selection"
      width="55"
    />

    <!-- 序号列 -->
    <el-table-column
      v-if="showIndex"
      type="index"
      label="序号"
      width="60"
    />

    <!-- 数据列 -->
    <el-table-column
      v-for="column in columns"
      :key="column.prop"
      :prop="column.prop"
      :label="column.label"
      :width="column.width"
      :min-width="column.minWidth"
      :fixed="column.fixed"
      :sortable="column.sortable"
      :formatter="column.formatter"
    >
      <template v-if="column.slot" #default="scope">
        <slot :name="column.slot" :row="scope.row" :column="column" :$index="scope.$index"></slot>
      </template>
    </el-table-column>

    <!-- 操作列 -->
    <el-table-column
      v-if="showActions"
      label="操作"
      :width="actionsWidth"
      fixed="right"
    >
      <template #default="scope">
        <slot name="actions" :row="scope.row" :$index="scope.$index"></slot>
      </template>
    </el-table-column>
  </el-table>

  <!-- 分页 -->
  <el-pagination
    v-if="showPagination"
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :total="total"
    :page-sizes="pageSizes"
    :layout="paginationLayout"
    :background="true"
    class="pagination"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Column {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  fixed?: 'left' | 'right'
  sortable?: boolean
  formatter?: (row: any, column: any, cellValue: any, index: number) => string
  slot?: string
}

interface Props {
  data: any[]
  columns: Column[]
  loading?: boolean
  stripe?: boolean
  border?: boolean
  height?: number | string
  maxHeight?: number | string
  showSelection?: boolean
  showIndex?: boolean
  showActions?: boolean
  actionsWidth?: number
  showPagination?: boolean
  total?: number
  page?: number
  pageSize?: number
  pageSizes?: number[]
  paginationLayout?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  stripe: true,
  border: false,
  showSelection: false,
  showIndex: false,
  showActions: false,
  actionsWidth: 150,
  showPagination: true,
  total: 0,
  page: 1,
  pageSize: 50,
  pageSizes: () => [20, 50, 100, 200],
  paginationLayout: 'total, sizes, prev, pager, next, jumper'
})

const emit = defineEmits<{
  (e: 'row-click', row: any): void
  (e: 'selection-change', selection: any[]): void
  (e: 'page-change', page: number): void
  (e: 'size-change', size: number): void
}>()

const currentPage = ref(props.page)
const pageSize = ref(props.pageSize)

watch(() => props.page, (val) => {
  currentPage.value = val
})

watch(() => props.pageSize, (val) => {
  pageSize.value = val
})

const handleRowClick = (row: any) => {
  emit('row-click', row)
}

const handleSelectionChange = (selection: any[]) => {
  emit('selection-change', selection)
}

const handleCurrentChange = (page: number) => {
  emit('page-change', page)
}

const handleSizeChange = (size: number) => {
  emit('size-change', size)
}
</script>

<style scoped>
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
