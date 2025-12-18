<template>
  <el-drawer
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="产品详情"
    size="40%"
    append-to-body
    :destroy-on-close="false"
  >
    <div v-if="product" class="detail-content">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ASIN">{{ product.asin }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ product.title }}</el-descriptions-item>
        <el-descriptions-item label="中文标题">{{ product.title_cn || '—' }}</el-descriptions-item>
        <el-descriptions-item label="中文五点">
          <div class="whitespace-pre-wrap">{{ product.bullets_cn || '—' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="批次 ID">{{ product.batch_id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          {{ formatStatus(product.validation_status) }}
        </el-descriptions-item>
        <el-descriptions-item label="最近更新时间">
          {{ formatTime(product.ingested_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="价格">{{ product.price ?? '—' }}</el-descriptions-item>
        <el-descriptions-item label="评分">{{ product.rating ?? '—' }}</el-descriptions-item>
        <el-descriptions-item label="排名">{{ product.sales_rank ?? '—' }}</el-descriptions-item>
        <el-descriptions-item label="校验信息">
          {{ product.validation_messages ? JSON.stringify(product.validation_messages) : '—' }}
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="product.raw_payload" class="raw-payload-section">
        <h3 class="section-title">原始数据</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item 
            v-for="(value, key) in product.raw_payload" 
            :key="key" 
            :label="key"
          >
            {{ value }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import type { ProductItem } from '../types'

defineProps<{
  visible: boolean
  product: ProductItem | null
}>()

defineEmits(['update:visible'])

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
.detail-content {
  padding: 20px;
}
.raw-payload-section {
  margin-top: 24px;
  .section-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 16px;
  }
}
.whitespace-pre-wrap {
  white-space: pre-wrap;
}
</style>
