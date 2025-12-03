<template>
  <el-config-provider :size="size" :locale="locale">
    <div class="app-wrapper">
      <router-view />
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const size = 'default'
const locale = zhCn
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
}
</style>
