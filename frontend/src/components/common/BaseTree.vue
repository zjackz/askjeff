<!--
通用树形组件

使用示例:
<BaseTree
  :data="treeData"
  :props="treeProps"
  @node-click="handleNodeClick"
/>
-->
<template>
  <el-tree
    ref="treeRef"
    :data="data"
    :props="props"
    :node-key="nodeKey"
    :default-expand-all="defaultExpandAll"
    :expand-on-click-node="expandOnClickNode"
    :check-on-click-node="checkOnClickNode"
    :show-checkbox="showCheckbox"
    :check-strictly="checkStrictly"
    :default-checked-keys="defaultCheckedKeys"
    :default-expanded-keys="defaultExpandedKeys"
    :filter-node-method="filterNodeMethod"
    :highlight-current="highlightCurrent"
    @node-click="handleNodeClick"
    @node-contextmenu="handleNodeContextmenu"
    @check-change="handleCheckChange"
    @check="handleCheck"
    @current-change="handleCurrentChange"
    @node-expand="handleNodeExpand"
    @node-collapse="handleNodeCollapse"
  >
    <!-- 自定义节点 -->
    <template v-if="$slots.default" #default="{ node, data }">
      <slot :node="node" :data="data"></slot>
    </template>
  </el-tree>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, defineExpose } from 'vue'
import type { ElTree } from 'element-plus'

interface TreeProps {
  label?: string
  children?: string
  disabled?: string
  isLeaf?: string
}

interface Props {
  data: any[]
  props?: TreeProps
  nodeKey?: string
  defaultExpandAll?: boolean
  expandOnClickNode?: boolean
  checkOnClickNode?: boolean
  showCheckbox?: boolean
  checkStrictly?: boolean
  defaultCheckedKeys?: any[]
  defaultExpandedKeys?: any[]
  filterNodeMethod?: (value: string, data: any, node: any) => boolean
  highlightCurrent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  props: () => ({
    label: 'label',
    children: 'children',
    disabled: 'disabled'
  }),
  nodeKey: 'id',
  defaultExpandAll: false,
  expandOnClickNode: true,
  checkOnClickNode: false,
  showCheckbox: false,
  checkStrictly: false,
  highlightCurrent: false
})

const emit = defineEmits<{
  (e: 'node-click', data: any, node: any, instance: any): void
  (e: 'node-contextmenu', event: Event, data: any, node: any, instance: any): void
  (e: 'check-change', data: any, checked: boolean, indeterminate: boolean): void
  (e: 'check', data: any, checkedInfo: any): void
  (e: 'current-change', data: any, node: any): void
  (e: 'node-expand', data: any, node: any, instance: any): void
  (e: 'node-collapse', data: any, node: any, instance: any): void
}>()

const treeRef = ref<InstanceType<typeof ElTree>>()

const handleNodeClick = (data: any, node: any, instance: any) => {
  emit('node-click', data, node, instance)
}

const handleNodeContextmenu = (event: Event, data: any, node: any, instance: any) => {
  emit('node-contextmenu', event, data, node, instance)
}

const handleCheckChange = (data: any, checked: boolean, indeterminate: boolean) => {
  emit('check-change', data, checked, indeterminate)
}

const handleCheck = (data: any, checkedInfo: any) => {
  emit('check', data, checkedInfo)
}

const handleCurrentChange = (data: any, node: any) => {
  emit('current-change', data, node)
}

const handleNodeExpand = (data: any, node: any, instance: any) => {
  emit('node-expand', data, node, instance)
}

const handleNodeCollapse = (data: any, node: any, instance: any) => {
  emit('node-collapse', data, node, instance)
}

// 暴露方法
defineExpose({
  filter: (value: string) => treeRef.value?.filter(value),
  getCheckedKeys: () => treeRef.value?.getCheckedKeys(),
  getCheckedNodes: () => treeRef.value?.getCheckedNodes(),
  setCheckedKeys: (keys: any[]) => treeRef.value?.setCheckedKeys(keys),
  setCheckedNodes: (nodes: any[]) => treeRef.value?.setCheckedNodes(nodes),
  getCurrentKey: () => treeRef.value?.getCurrentKey(),
  getCurrentNode: () => treeRef.value?.getCurrentNode(),
  setCurrentKey: (key: any) => treeRef.value?.setCurrentKey(key),
  setCurrentNode: (node: any) => treeRef.value?.setCurrentNode(node)
})
</script>

<style scoped>
/* 自定义样式 (如需) */
</style>
