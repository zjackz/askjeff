<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useResizeObserver } from '@vueuse/core'

const props = defineProps<{
  data: Array<{
    sku: string
    asin: string
    stock_weeks: number
    tacos: number
    status: string
    sales: number
  }>
}>()

const emit = defineEmits(['select-sku'])

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  updateChart()
  
  chartInstance.on('click', (params: any) => {
    if (params.componentType === 'series') {
      emit('select-sku', params.data)
    }
  })
}

const updateChart = () => {
  if (!chartInstance) return

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      padding: 0,
      borderWidth: 0,
      backgroundColor: 'transparent',
      formatter: (params: any) => {
        const data = params.data
        return `
          <div style="
            background: #fff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            color: #1f2937;
            min-width: 180px;
          ">
            <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; border-bottom: 1px solid #f3f4f6; padding-bottom: 8px;">${data.sku}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px; gap: 20px;">
              <span style="color: #6b7280;">库存周转:</span>
              <span style="font-weight: 600;">${data.stock_weeks.toFixed(1)} 周</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px; gap: 20px;">
              <span style="color: #6b7280;">TACOS:</span>
              <span style="font-weight: 600; color: ${data.tacos > 20 ? '#ef4444' : '#10b981'}">${data.tacos.toFixed(1)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px; gap: 20px;">
              <span style="color: #6b7280;">ACOS:</span>
              <span style="font-weight: 600;">${data.acos.toFixed(1)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px; gap: 20px;">
              <span style="color: #6b7280;">净利润率:</span>
              <span style="font-weight: 600; color: ${data.margin > 0 ? '#10b981' : '#ef4444'}">${data.margin.toFixed(1)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; gap: 20px;">
              <span style="color: #6b7280;">CTR / CVR:</span>
              <span style="font-weight: 600;">${data.ctr.toFixed(2)}% / ${data.cvr.toFixed(1)}%</span>
            </div>
            <div style="font-size: 11px; color: #667eea; text-align: center; margin-top: 8px; font-weight: 600;">✨ 点击查看 AI 深度诊断</div>
          </div>
        `
      }
    },
    grid: {
      left: '8%',
      right: '10%',
      bottom: '12%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      name: '库存周转 (周)',
      nameLocation: 'middle',
      nameGap: 40,
      type: 'value',
      splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } },
      axisLabel: { color: '#9ca3af', fontSize: 11 },
      axisLine: { lineStyle: { color: '#e5e7eb' } }
    },
    yAxis: {
      name: 'TACOS (%)',
      nameLocation: 'middle',
      nameGap: 50,
      type: 'value',
      splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } },
      axisLabel: { color: '#9ca3af', fontSize: 11 },
      axisLine: { lineStyle: { color: '#e5e7eb' } }
    },
    series: [
      {
        type: 'scatter',
        symbolSize: (data: any) => {
          const size = Math.sqrt(data[3] || 100) / 2 + 10
          return Math.min(Math.max(size, 12), 45)
        },
        data: props.data.map(item => ({
          value: [item.stock_weeks, item.tacos, item.status, item.sales],
          ...item,
          itemStyle: {
            color: getColor(item.stock_weeks, item.tacos),
            opacity: 0.8,
            shadowBlur: 10,
            shadowColor: getColor(item.stock_weeks, item.tacos) + '44',
            borderColor: '#fff',
            borderWidth: 2
          },
          emphasis: {
            itemStyle: {
              opacity: 1,
              shadowBlur: 20,
              borderColor: '#fff',
              borderWidth: 3
            }
          }
        })),
        markArea: {
          silent: true,
          data: [
            // Q1: Critical (High Stock, High TACOS)
            [{ xAxis: 24, yAxis: 20, itemStyle: { color: 'rgba(239, 68, 68, 0.02)' } }, { xAxis: 100, yAxis: 100 }],
            // Q2: Star (High Stock, Low TACOS)
            [{ xAxis: 24, yAxis: 0, itemStyle: { color: 'rgba(16, 185, 129, 0.02)' } }, { xAxis: 100, yAxis: 20 }],
            // Q3: Potential (Low Stock, Low TACOS)
            [{ xAxis: 0, yAxis: 0, itemStyle: { color: 'rgba(59, 130, 246, 0.02)' } }, { xAxis: 24, yAxis: 20 }],
            // Q4: Drop (Low Stock, High TACOS)
            [{ xAxis: 0, yAxis: 20, itemStyle: { color: 'rgba(156, 163, 175, 0.02)' } }, { xAxis: 24, yAxis: 100 }]
          ]
        },
        markLine: {
          silent: true,
          lineStyle: { color: '#e5e7eb', type: 'solid', width: 1 },
          symbol: 'none',
          data: [
            { xAxis: 24, label: { show: true, position: 'end', formatter: '24周', color: '#9ca3af' } },
            { yAxis: 20, label: { show: true, position: 'end', formatter: '20%', color: '#9ca3af' } }
          ]
        }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const getColor = (stock: number, tacos: number) => {
  if (stock > 24 && tacos > 20) return '#ef4444' // Critical
  if (stock > 24 && tacos <= 20) return '#10b981' // Star
  if (stock <= 24 && tacos <= 20) return '#3b82f6' // Potential
  return '#9ca3af' // Drop
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  setTimeout(initChart, 300)
})

useResizeObserver(chartRef, () => {
  chartInstance?.resize()
})

onUnmounted(() => {
  chartInstance?.dispose()
})
</script>

<template>
  <div class="chart-container">
    <div ref="chartRef" class="chart-instance"></div>
  </div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
  position: relative;
}

.chart-instance {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}
</style>
