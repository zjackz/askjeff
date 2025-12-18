<template>
  <div class="insight-page">
    <FilterForm
      :filters="filters"
      :batches="batches"
      @search="fetchProducts(true)"
      @reset="resetFilters"
      @extract="navigateToExtraction"
    />

    <el-alert
      v-if="errorMessage"
      type="error"
      :closable="false"
      class="error-alert"
      title="列表加载失败"
      :description="errorMessage"
      show-icon
    />

    <ProductTable
      :products="products"
      :loading="loading"
      :total="total"
      v-model:current-page="filters.page"
      v-model:page-size="filters.pageSize"
      :export-loading="exportLoading"
      @reload="fetchProducts"
      @export="exportCurrentFilters"
      @sort-change="handleSortChange"
      @row-click="openDetail"
    />

    <ProductDetail
      v-model:visible="detailVisible"
      :product="selectedProduct"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import FilterForm from './components/FilterForm.vue'
import ProductTable from './components/ProductTable.vue'
import ProductDetail from './components/ProductDetail.vue'
import { useProductList } from './composables/useProductList'
import type { ProductItem } from './types'

const router = useRouter()
const {
  filters,
  products,
  total,
  loading,
  errorMessage,
  batches,
  exportLoading,
  fetchBatches,
  fetchProducts,
  exportCurrentFilters
} = useProductList()

const detailVisible = ref(false)
const selectedProduct = ref<ProductItem | null>(null)

const resetFilters = () => {
  Object.assign(filters, {
    batchId: '',
    asin: '',
    status: '',
    dateRange: [],
    minPrice: undefined,
    maxPrice: undefined,
    minRating: undefined,
    maxRating: undefined,
    minReviews: undefined,
    maxReviews: undefined,
    minRank: undefined,
    maxRank: undefined,
    category: '',
    sortBy: '',
    sortOrder: '',
    page: 1,
    pageSize: 20
  })
  fetchProducts(true)
}

const handleSortChange = ({ prop, order }: { prop: string, order: 'asc' | 'desc' | '' }) => {
  filters.sortBy = prop
  filters.sortOrder = order
  fetchProducts()
}

const openDetail = (row: ProductItem) => {
  selectedProduct.value = row
  detailVisible.value = true
}

const navigateToExtraction = () => {
  if (filters.batchId) {
    router.push(`/extraction/${filters.batchId}`)
  }
}

// Watch pagination changes
watch(() => [filters.page, filters.pageSize], () => {
  fetchProducts()
})

onMounted(() => {
  fetchBatches()
  fetchProducts()
})
</script>

<style scoped lang="scss">
.insight-page {
  padding: 24px;
  background: var(--el-bg-color-page);
  min-height: 100%;
}
.error-alert {
  margin-bottom: 20px;
}
</style>
