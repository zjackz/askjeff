<!-- 
通用按钮组件

使用示例:
<BaseButton type="primary" @click="handleClick">点击</BaseButton>
<BaseButton type="success" :loading="loading">提交</BaseButton>
<BaseButton type="danger" :disabled="true">删除</BaseButton>
-->
<template>
  <el-button
    :type="type"
    :size="size"
    :loading="loading"
    :disabled="disabled"
    :icon="icon"
    :plain="plain"
    :round="round"
    :circle="circle"
    @click="handleClick"
  >
    <slot></slot>
  </el-button>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface Props {
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'text'
  size?: 'large' | 'default' | 'small'
  loading?: boolean
  disabled?: boolean
  icon?: string
  plain?: boolean
  round?: boolean
  circle?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  size: 'default',
  loading: false,
  disabled: false,
  plain: false,
  round: false,
  circle: false
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const handleClick = (event: MouseEvent) => {
  if (!props.loading && !props.disabled) {
    emit('click', event)
  }
}
</script>

<style scoped>
/* 自定义样式 (如需) */
</style>
