<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '240px'" class="layout-aside">
      <div class="logo-wrapper">
        <img src="/logo.png" alt="AskJeff Logo" class="logo-image" v-if="!isCollapse" />
        <img src="/logo-small.png" alt="Logo" class="logo-image-small" v-else />
      </div>
      
      <el-menu 
        :default-active="activePath" 
        router 
        class="sidebar-menu"
        :unique-opened="true"
        :collapse="isCollapse"
        :collapse-transition="false"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>数据总览</template>
        </el-menu-item>
        
        <el-menu-item index="/import">
          <el-icon><Upload /></el-icon>
          <template #title>文件导入</template>
        </el-menu-item>
        
        <el-menu-item index="/product">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>数据洞察</template>
        </el-menu-item>


        
        <el-menu-item index="/export">
          <el-icon><Download /></el-icon>
          <template #title>数据导出</template>
        </el-menu-item>
        
        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <template #title>日志中心</template>
        </el-menu-item>
      </el-menu>
      
      <!-- 侧边栏底部 -->
      <div class="sidebar-footer" v-if="!isCollapse">
        <div class="version-info">
          <el-icon><InfoFilled /></el-icon>
          <span>v0.1.0</span>
        </div>
      </div>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="layout-header">
        <div class="header-left">
          <div class="collapse-btn" @click="toggleCollapse">
            <el-icon :size="20">
              <component :is="isCollapse ? 'Expand' : 'Fold'" />
            </el-icon>
          </div>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentPageName">{{ currentPageName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <ThemeToggle />
          <el-dropdown trigger="click">
            <div class="user-avatar">
              <el-icon :size="20"><User /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <el-icon><Setting /></el-icon>
                  <span>设置</span>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主内容 -->
      <el-main class="layout-main">
        <transition name="fade-slide" mode="out-in">
          <router-view />
        </transition>
      </el-main>
    </el-container>
    <ChatBot />
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed, ref } from 'vue'
import { 
  Odometer, Upload, ChatDotRound, Download, 
  Document, InfoFilled, User, Setting, 
  SwitchButton
} from '@element-plus/icons-vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { ElMessage } from 'element-plus'

import { useUserStore } from '@/stores/user'
import ChatBot from '@/components/ChatBot.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const activePath = computed(() => route.path)
const isCollapse = ref(false)

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const pageNames: Record<string, string> = {
  '/dashboard': '数据总览',
  '/import': '文件导入',
  '/product': '数据洞察',
  '/extraction': 'AI 提取',
  '/export': '数据导出',
  '/logs': '日志中心'
}

const currentPageName = computed(() => pageNames[route.path] || '')

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped lang="scss">
.layout-container {
  min-height: 100vh;
}

// ==========================================
// 侧边栏
// ==========================================

.layout-aside {
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
  position: relative;
  overflow: hidden;
  transition: width 0.3s ease-in-out;
  
  // 装饰性背景
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
    pointer-events: none;
  }
}

.logo-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 64px;
  position: relative;
  z-index: 1;
}

.logo-image {
  height: 40px;
  width: auto;
  object-fit: contain;
}

.logo-image-small {
  height: 32px;
  width: auto;
  object-fit: contain;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0 var(--spacing-xs);
  position: relative;
  z-index: 1;
  
  :deep(.el-menu-item) {
    height: 48px;
    line-height: 48px;
    margin-bottom: var(--spacing-sm);
    border-radius: var(--radius-md);
    color: rgba(255, 255, 255, 0.9); // 提高亮度
    transition: all var(--transition-base) var(--ease-out);
    display: flex;
    align-items: center;
    
    &:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
    }
    
    &.is-active {
      background: var(--primary-gradient);
      color: #fff;
      box-shadow: var(--shadow-primary);
    }
    
    .el-icon {
      font-size: 18px;
      margin-right: var(--spacing-sm);
      text-align: center;
      vertical-align: middle;
      width: 24px;
      flex-shrink: 0;
    }
  }

  // 折叠状态下的特定样式
  &.el-menu--collapse {
    :deep(.el-menu-item) {
      padding: 0 !important;
      justify-content: center;
      margin-bottom: 8px;
      
      .el-icon {
        margin-right: 0;
      }
    }
  }
}

.sidebar-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
}

.version-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: rgba(255, 255, 255, 0.5);
  font-size: var(--font-size-sm);
  
  .el-icon {
    font-size: 16px;
  }
}

// ==========================================
// 顶部导航栏
// ==========================================

.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-primary);
  box-shadow: var(--shadow-sm);
  padding: 0 var(--spacing-xl);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;

  .collapse-btn {
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--radius-md);
    background: var(--bg-secondary);
    color: var(--text-primary);
    transition: all 0.3s;
    border: 1px solid var(--border-light);

    &:hover {
      color: var(--primary-color);
      background: var(--primary-light);
      border-color: var(--primary-color);
    }
  }

  :deep(.el-breadcrumb) {
    font-size: var(--font-size-base);
    
    .el-breadcrumb__item {
      .el-breadcrumb__inner {
        color: var(--text-secondary);
        font-weight: var(--font-weight-medium);
        
        &:hover {
          color: var(--primary-color);
        }
      }
      
      &:last-child .el-breadcrumb__inner {
        color: var(--text-primary);
      }
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  transition: all var(--transition-base) var(--ease-out);
  box-shadow: var(--shadow-sm);
  
  &:hover {
    transform: scale(1.05);
    box-shadow: var(--shadow-primary);
  }
}

// ==========================================
// 主内容区
// ==========================================

.layout-main {
  background: var(--bg-secondary);
  padding: var(--spacing-xl);
  min-height: calc(100vh - 60px);
}

// ==========================================
// 页面过渡动画
// ==========================================

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all var(--transition-base) var(--ease-out);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>

