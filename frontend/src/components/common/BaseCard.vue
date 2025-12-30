<!--
通用卡片组件

使用示例:
<BaseCard title="标题" :shadow="'hover'">
  <p>卡片内容</p>
</BaseCard>
-->
<template>
  <el-card
    :shadow="shadow"
    :body-style="bodyStyle"
    :header="header"
  >
    <!-- 自定义头部 -->
    <template v-if="title || $slots.header" #header>
      <slot name="header">
        <div class="card-header">
          <span class="card-title">{{ title }}</span>
          <slot name="extra"></slot>
        </div>
      </slot>
    </template>

    <!-- 内容 -->
    <slot></slot>

    <!-- 底部 -->
    <template v-if="$slots.footer" #footer>
      <slot name="footer"></slot>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'

interface Props {
  title?: string
  shadow?: 'always' | 'hover' | 'never'
  bodyStyle?: Record<string, string>
  header?: string
}

withDefaults(defineProps<Props>(), {
  shadow: 'hover'
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}
</style>
