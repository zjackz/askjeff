<template>
  <el-switch
    v-model="isDark"
    class="theme-toggle"
    :active-action-icon="Moon"
    :inactive-action-icon="Sunny"
    inline-prompt
    @change="toggleTheme"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Moon, Sunny } from '@element-plus/icons-vue'

const isDark = ref(false)

// 初始化主题
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark'
  applyTheme(isDark.value)
})

// 切换主题
const toggleTheme = (value: boolean) => {
  applyTheme(value)
  localStorage.setItem('theme', value ? 'dark' : 'light')
}

// 应用主题
const applyTheme = (dark: boolean) => {
  if (dark) {
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
}
</script>

<style scoped>
.theme-toggle {
  --el-switch-on-color: var(--primary-color);
  --el-switch-off-color: var(--text-tertiary);
}
</style>
