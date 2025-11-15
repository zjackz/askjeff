<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="layout-aside">
      <h2 class="logo">Sorftime 控制台</h2>
      <el-menu :default-active="activePath" router>
        <el-menu-item index="/dashboard">数据总览</el-menu-item>
        <el-menu-item index="/import">文件导入</el-menu-item>
        <el-menu-item index="/chat">数据洞察</el-menu-item>
        <el-menu-item index="/export">数据导出</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <span>运营后台</span>
        <el-button type="primary" link @click="goHome">回到仪表盘</el-button>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()
const activePath = computed(() => route.path)

const goHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.layout-aside {
  background: #001529;
  color: #fff;
}

.logo {
  text-align: center;
  padding: 16px 0;
  margin: 0;
}

.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.layout-main {
  background: #f5f5f5;
  padding: 16px;
}
</style>
