<template>
  <el-card class="filter-card">
    <el-form :inline="true" label-width="86px" class="filter-form">
      <el-form-item label="批次 ID">
        <el-select v-model="filters.batchId" placeholder="选择批次" clearable style="width: 200px">
          <el-option 
            v-for="batch in batches" 
            :key="batch.id" 
            :label="formatBatchLabel(batch)" 
            :value="batch.id" 
          />
        </el-select>
      </el-form-item>
      <el-form-item label="ASIN/标题">
        <el-input v-model="filters.asin" placeholder="输入 ASIN 或关键词" clearable style="width: 240px" />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="有效" value="valid" />
          <el-option label="警告" value="warning" />
          <el-option label="错误" value="error" />
        </el-select>
      </el-form-item>
      <el-form-item label="更新时间">
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DDTHH:mm:ss"
          :clearable="true"
          style="width: 340px"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="$emit('search')">查询</el-button>
        <el-button @click="$emit('reset')">清除筛选</el-button>
        <el-button 
          type="warning" 
          plain 
          :icon="MagicStick"
          :disabled="!filters.batchId"
          @click="$emit('extract')"
        >
          AI 提取
        </el-button>
        <el-button link @click="showAdvanced = !showAdvanced">
          {{ showAdvanced ? '收起高级筛选' : '展开高级筛选' }}
        </el-button>
      </el-form-item>

      <div v-if="showAdvanced" class="w-full flex flex-wrap gap-6 mt-4 border-t pt-4">
        <el-form-item label="价格区间">
          <el-input-number v-model="filters.minPrice" :min="0" placeholder="Min" style="width: 100px" />
          <span class="mx-2">-</span>
          <el-input-number v-model="filters.maxPrice" :min="0" placeholder="Max" style="width: 100px" />
        </el-form-item>
        <el-form-item label="评分区间">
          <el-input-number v-model="filters.minRating" :min="0" :max="5" :step="0.1" placeholder="Min" style="width: 100px" />
          <span class="mx-2">-</span>
          <el-input-number v-model="filters.maxRating" :min="0" :max="5" :step="0.1" placeholder="Max" style="width: 100px" />
        </el-form-item>
        <el-form-item label="评论数">
          <el-input-number v-model="filters.minReviews" :min="0" placeholder="Min" style="width: 100px" />
          <span class="mx-2">-</span>
          <el-input-number v-model="filters.maxReviews" :min="0" placeholder="Max" style="width: 100px" />
        </el-form-item>
        <el-form-item label="排名区间">
          <el-input-number v-model="filters.minRank" :min="0" placeholder="Min" style="width: 100px" />
          <span class="mx-2">-</span>
          <el-input-number v-model="filters.maxRank" :min="0" placeholder="Max" style="width: 100px" />
        </el-form-item>
        <el-form-item label="类目">
          <el-input v-model="filters.category" placeholder="输入类目关键词" clearable />
        </el-form-item>
      </div>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { MagicStick } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

defineProps<{
  filters: any
  batches: any[]
}>()

defineEmits(['search', 'reset', 'extract'])

const showAdvanced = ref(false)

const formatBatchLabel = (batch: any) => {
  const time = dayjs(batch.createdAt).format('YYYYMMDD HH:mm:ss')
  return `${batch.id} - ${time}`
}
</script>

<style scoped lang="scss">
.filter-card {
  margin-bottom: 20px;
}
.w-full { width: 100%; }
.flex { display: flex; }
.flex-wrap { flex-wrap: wrap; }
.gap-6 { gap: 24px; }
.mt-4 { margin-top: 16px; }
.border-t { border-top: 1px solid var(--el-border-color-lighter); }
.pt-4 { padding-top: 16px; }
.mx-2 { margin-left: 8px; margin-right: 8px; }
</style>
