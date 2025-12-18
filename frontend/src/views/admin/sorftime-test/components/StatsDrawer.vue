<template>
  <el-drawer
    :model-value="visible"
    title="请求统计"
    direction="rtl"
    size="400px"
    @update:model-value="$emit('update:visible', $event)"
  >
    <div class="stats-drawer">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic title="总请求数" :value="stats.total" />
        </el-col>
        <el-col :span="12">
          <el-statistic title="成功率" :value="successRate" suffix="%" />
        </el-col>
      </el-row>
      
      <el-divider />
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic title="成功" :value="stats.success">
            <template #suffix>
              <el-icon color="#67C23A"><SuccessFilled /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="12">
          <el-statistic title="失败" :value="stats.failed">
            <template #suffix>
              <el-icon color="#F56C6C"><CircleCloseFilled /></el-icon>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic title="平均响应" :value="avgResponseTime" suffix="ms" />
        </el-col>
        <el-col :span="12">
          <el-statistic title="预估消耗" :value="stats.estimatedCost" suffix=" requests" />
        </el-col>
      </el-row>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { SuccessFilled, CircleCloseFilled } from '@element-plus/icons-vue'

/**
 * 请求统计抽屉
 * 
 * 显示当前会话的请求统计信息
 */

interface Stats {
  total: number
  success: number
  failed: number
  totalTime: number
  estimatedCost: number
}

interface Props {
  visible: boolean
  stats: Stats
}

const props = defineProps<Props>()

defineEmits<{
  'update:visible': [value: boolean]
}>()

// 计算成功率
const successRate = computed(() => {
  if (props.stats.total === 0) return 0
  return Math.round((props.stats.success / props.stats.total) * 100)
})

// 计算平均响应时间
const avgResponseTime = computed(() => {
  if (props.stats.total === 0) return 0
  return Math.round(props.stats.totalTime / props.stats.total)
})
</script>

<style scoped lang="scss">
.stats-drawer {
  padding: 0 20px;
}
</style>
