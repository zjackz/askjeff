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
          <div class="menu-content">
            <span class="menu-title">数据总览</span>
            <span class="menu-desc">核心指标监控</span>
          </div>
        </el-menu-item>
        
        <!-- 智能运营 -->
        <el-sub-menu index="/ai">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>智能运营</span>
          </template>
          <el-menu-item index="/ai/product-selection">
            <el-icon><DataAnalysis /></el-icon>
            <div class="menu-content">
              <span class="menu-title">智能选品</span>
              <span class="menu-desc">AI 辅助市场分析</span>
            </div>
          </el-menu-item>
          <el-menu-item index="/ai/keyword-optimization">
            <el-icon><Key /></el-icon>
            <div class="menu-content">
              <span class="menu-title">关键词优化</span>
              <span class="menu-desc">Listing 排名提升</span>
            </div>
          </el-menu-item>
          <el-menu-item index="/product">
            <el-icon><ChatDotRound /></el-icon>
            <div class="menu-content">
              <span class="menu-title">产品透视</span>
              <span class="menu-desc">深度数据洞察</span>
            </div>
          </el-menu-item>
        </el-sub-menu>

        <!-- 广告管理 -->
        <el-sub-menu index="/ads">
          <template #title>
            <el-icon><DataLine /></el-icon>
            <span>广告管理</span>
          </template>
          <el-menu-item index="/ads-analysis">
            <el-icon><TrendCharts /></el-icon>
            <div class="menu-content">
              <span class="menu-title">广告诊断</span>
              <span class="menu-desc">库存联动分析</span>
            </div>
          </el-menu-item>
        </el-sub-menu>

        <!-- 数据中心 -->
        <el-sub-menu index="/data">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>数据中心</span>
          </template>
          <el-menu-item index="/import">
            <el-icon><Upload /></el-icon>
            <div class="menu-content">
              <span class="menu-title">数据导入</span>
              <span class="menu-desc">批量数据上传</span>
            </div>
          </el-menu-item>
          <el-menu-item index="/export">
            <el-icon><Download /></el-icon>
            <div class="menu-content">
              <span class="menu-title">数据导出</span>
              <span class="menu-desc">报表下载中心</span>
            </div>
          </el-menu-item>
        </el-sub-menu>

        <!-- 系统管理 -->
        <el-sub-menu index="/system" v-if="userStore.role === 'admin'">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/admin">
            <el-icon><Delete /></el-icon>
            <div class="menu-content">
              <span class="menu-title">数据清理</span>
              <span class="menu-desc">系统数据维护</span>
            </div>
          </el-menu-item>
          <el-menu-item index="/logs">
            <el-icon><Monitor /></el-icon>
            <div class="menu-content">
              <span class="menu-title">日志监控</span>
              <span class="menu-desc">系统运行状态</span>
            </div>
          </el-menu-item>
          <el-menu-item index="/admin/sorftime-test">
            <el-icon><Connection /></el-icon>
            <div class="menu-content">
              <span class="menu-title">API 测试</span>
              <span class="menu-desc">接口调试工具</span>
            </div>
          </el-menu-item>
        </el-sub-menu>
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
              <component :is="isCollapse ? Expand : Fold" />
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
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
        
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
  SwitchButton, Delete, Expand, Fold, Connection,
  Cpu, DataAnalysis, Key, Monitor, DataLine
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
  '/import': '数据导入',
  '/product': '产品透视',
  '/ai/product-selection': '智能选品',
  '/ai/keyword-optimization': '关键词优化',
  '/ads-analysis': '广告诊断',
  '/extraction': 'AI 提取',
  '/export': '数据导出',
  '/logs': '日志监控',
  '/admin': '数据清理',
  '/admin/sorftime-test': 'API 测试'
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


.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0 var(--spacing-xs);
  position: relative;
  z-index: 1;
  
  :deep(.el-menu-item) {
    height: 72px; // 增加高度以容纳双行文本
    line-height: normal; // 重置行高
    margin-bottom: var(--spacing-sm);
    border-radius: var(--radius-md);
    color: rgba(255, 255, 255, 0.7);
    transition: all var(--transition-base) var(--ease-out);
    display: flex;
    align-items: center;
    padding: 0 16px !important; // 调整内边距
    
    &:hover {
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
      
      .menu-desc {
        color: rgba(255, 255, 255, 0.9);
      }
    }
    
    &.is-active {
      background: var(--primary-gradient);
      color: #fff;
      box-shadow: var(--shadow-primary);
      
      .menu-desc {
        color: rgba(255, 255, 255, 0.9);
      }
    }
    
    .el-icon {
      font-size: 20px;
      margin-right: 12px;
      text-align: center;
      vertical-align: middle;
      width: 24px;
      flex-shrink: 0;
    }
  }

  :deep(.el-sub-menu__title) {
    height: 56px; // 分组标题稍矮一些
    line-height: 56px;
    margin-bottom: var(--spacing-sm);
    border-radius: var(--radius-md);
    color: rgba(255, 255, 255, 0.9);
    transition: all var(--transition-base) var(--ease-out);
    
    &:hover {
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
    }

    .el-icon {
      font-size: 18px;
      margin-right: 12px;
      text-align: center;
      vertical-align: middle;
      width: 24px;
      color: inherit;
    }
  }

  :deep(.el-menu--inline) {
    background: rgba(0, 0, 0, 0.2) !important; // 深色背景，形成凹陷感
    padding: 4px 0;
    
    .el-menu-item {
      height: 50px !important; // 显著降低二级菜单高度
      padding-left: 48px !important; // 增加缩进
      margin-bottom: 4px; // 减小间距
      background: transparent; // 确保透明，显示父容器背景
      
      &:hover {
        background: rgba(255, 255, 255, 0.05);
      }
      
      &.is-active {
        background: var(--primary-gradient);
      }

      .el-icon {
        font-size: 14px !important; // 进一步缩小图标
        width: 14px !important;
        margin-right: 10px !important;
        opacity: 0.6; // 降低图标透明度
      }
      
      .menu-content {
        .menu-title {
          font-size: 13px; // 缩小标题字体
          font-weight: 500; // 降低字重
        }
        
        .menu-desc {
          font-size: 11px; // 缩小描述字体
          opacity: 0.6;
          margin-top: 0; // 紧凑布局
        }
      }
    }
  }
  
  // 折叠状态下的特定样式
  &.el-menu--collapse {
    width: 64px;
    
    // 隐藏文字内容
    .menu-content,
    .el-sub-menu__title span {
      display: none;
    }
    
    :deep(.el-menu-item) {
      height: 48px; // 折叠时高度适中
      padding: 0 !important;
      justify-content: center;
      margin: 8px auto; // 上下间距，水平居中
      width: 48px; // 固定宽度
      border-radius: 8px; // 圆角
      
      .el-icon {
        margin-right: 0;
        font-size: 20px;
      }
      
      // 折叠状态下的激活样式
      &.is-active {
        background: var(--primary-gradient);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); // 更柔和的阴影
        
        .el-icon {
          color: #fff;
        }
      }
    }
    
    :deep(.el-sub-menu__title) {
      padding: 0 !important;
      justify-content: center;
      margin: 8px auto;
      width: 48px;
      height: 48px;
      border-radius: 8px;
      
      .el-icon {
        margin-right: 0;
      }
    }
  }
}

.logo-wrapper {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center; // 始终居中
  padding: 0 16px;
  background: transparent; // 透明背景，透出侧边栏渐变
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden; // 防止溢出
  
  .logo-image {
    height: 32px;
    width: auto;
    max-width: 100%;
  }
  
  .logo-image-small {
    height: 32px;
    width: 32px;
    object-fit: contain;
  }
}

.menu-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  line-height: 1.4;
  
  .menu-title {
    font-size: 14px;
    font-weight: 600;
  }
  
  .menu-desc {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
    margin-top: 2px;
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
  display: flex;
  flex-direction: column;
}

.layout-footer {
  margin-top: auto;
  padding-top: var(--spacing-lg);
  text-align: center;
  
  p {
    color: var(--text-tertiary);
    font-size: 0.85rem;
    margin: 0;
  }
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

