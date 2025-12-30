<!--
通用表单组件

使用示例:
<BaseForm
  :model="formData"
  :rules="rules"
  :items="formItems"
  @submit="handleSubmit"
/>
-->
<template>
  <el-form
    ref="formRef"
    :model="model"
    :rules="rules"
    :label-width="labelWidth"
    :label-position="labelPosition"
    :inline="inline"
    :size="size"
  >
    <el-form-item
      v-for="item in items"
      :key="item.prop"
      :label="item.label"
      :prop="item.prop"
      :required="item.required"
    >
      <!-- 输入框 -->
      <el-input
        v-if="item.type === 'input'"
        v-model="model[item.prop]"
        :placeholder="item.placeholder"
        :disabled="item.disabled"
        :clearable="item.clearable !== false"
      />

      <!-- 文本域 -->
      <el-input
        v-else-if="item.type === 'textarea'"
        v-model="model[item.prop]"
        type="textarea"
        :placeholder="item.placeholder"
        :disabled="item.disabled"
        :rows="item.rows || 3"
      />

      <!-- 选择器 -->
      <el-select
        v-else-if="item.type === 'select'"
        v-model="model[item.prop]"
        :placeholder="item.placeholder"
        :disabled="item.disabled"
        :clearable="item.clearable !== false"
        style="width: 100%"
      >
        <el-option
          v-for="option in item.options"
          :key="option.value"
          :label="option.label"
          :value="option.value"
        />
      </el-select>

      <!-- 日期选择器 -->
      <el-date-picker
        v-else-if="item.type === 'date'"
        v-model="model[item.prop]"
        :type="item.dateType || 'date'"
        :placeholder="item.placeholder"
        :disabled="item.disabled"
        style="width: 100%"
      />

      <!-- 数字输入框 -->
      <el-input-number
        v-else-if="item.type === 'number'"
        v-model="model[item.prop]"
        :min="item.min"
        :max="item.max"
        :step="item.step"
        :disabled="item.disabled"
        style="width: 100%"
      />

      <!-- 开关 -->
      <el-switch
        v-else-if="item.type === 'switch'"
        v-model="model[item.prop]"
        :disabled="item.disabled"
      />

      <!-- 自定义插槽 -->
      <slot v-else :name="item.prop" :item="item"></slot>
    </el-form-item>

    <!-- 按钮 -->
    <el-form-item v-if="showButtons">
      <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
        {{ submitText }}
      </el-button>
      <el-button @click="handleReset">{{ resetText }}</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

interface FormItem {
  prop: string
  label: string
  type: 'input' | 'textarea' | 'select' | 'date' | 'number' | 'switch' | 'custom'
  placeholder?: string
  required?: boolean
  disabled?: boolean
  clearable?: boolean
  rows?: number
  options?: { label: string; value: any }[]
  dateType?: 'date' | 'datetime' | 'daterange'
  min?: number
  max?: number
  step?: number
}

interface Props {
  model: Record<string, any>
  rules?: FormRules
  items: FormItem[]
  labelWidth?: string | number
  labelPosition?: 'left' | 'right' | 'top'
  inline?: boolean
  size?: 'large' | 'default' | 'small'
  showButtons?: boolean
  submitText?: string
  resetText?: string
  submitLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  labelWidth: '100px',
  labelPosition: 'right',
  inline: false,
  size: 'default',
  showButtons: true,
  submitText: '提交',
  resetText: '重置',
  submitLoading: false
})

const emit = defineEmits<{
  (e: 'submit', values: Record<string, any>): void
  (e: 'reset'): void
}>()

const formRef = ref<FormInstance>()

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      emit('submit', props.model)
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  emit('reset')
}

// 暴露方法供父组件调用
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  clearValidate: () => formRef.value?.clearValidate()
})
</script>

<style scoped>
/* 自定义样式 (如需) */
</style>
