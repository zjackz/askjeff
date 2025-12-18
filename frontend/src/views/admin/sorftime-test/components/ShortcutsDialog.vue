<template>
  <el-dialog
    :model-value="visible"
    title="键盘快捷键"
    width="500px"
    @update:model-value="$emit('update:visible', $event)"
  >
    <el-table :data="shortcuts" :show-header="false">
      <el-table-column prop="key" width="200">
        <template #default="{ row }">
          <el-tag>{{ row.key }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" />
    </el-table>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * 快捷键帮助对话框
 * 
 * 显示所有可用的键盘快捷键
 */

interface Props {
  visible: boolean
}

defineProps<Props>()

defineEmits<{
  'update:visible': [value: boolean]
}>()

// 快捷键列表
const shortcuts = [
  { key: 'Ctrl/Cmd + Enter', description: '发送请求' },
  { key: 'Ctrl/Cmd + K', description: '清空表单' },
  { key: 'Ctrl/Cmd + H', description: '打开/关闭历史记录' },
  { key: 'Ctrl/Cmd + L', description: '加载示例数据' },
  { key: 'Ctrl/Cmd + /', description: '显示快捷键帮助' }
]
</script>

<style scoped lang="scss">
// 组件特定样式(如需要)
</style>
