import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: () => import('../views/login/index.vue')
  },
  {
    path: '/',
    component: () => import('../layouts/BasicLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: '/dashboard',
        component: () => import('../views/dashboard/index.vue'),
        meta: { title: '数据概览' }
      },
      {
        path: '/import',
        component: () => import('../views/import/index.vue'),
        meta: { title: '文件导入' }
      },
      {
        path: '/product',
        component: () => import('../views/product-list/index.vue'),
        meta: { title: '产品查询' }
      },
      {
        path: '/export',
        component: () => import('../views/export/index.vue'),
        meta: { title: '数据导出' }
      },
      {
        path: '/logs',
        component: () => import('../views/logs/index.vue'),
        meta: { title: '日志中心' }
      },
      {
        path: '/ai/product-selection',
        component: () => import('../views/ai/ProductSelection.vue'),
        meta: { title: 'AI 选品助手' }
      },
      {
        path: '/ai/keyword-optimization',
        component: () => import('../views/ai/KeywordOptimization.vue'),
        meta: { title: 'AI 关键词优化' }
      },
      {
        path: '/ads-analysis',
        component: () => import('../views/ads-analysis/index.vue'),
        meta: { title: '广告诊断' }
      },
      {
        path: '/data-source',
        component: () => import('../views/data-source/index.vue'),
        meta: { title: '数据源管理' }
      },

      {
        path: '/admin',
        component: () => import('../views/admin/index.vue'),
        meta: { title: '数据管理', roles: ['admin'] }
      },
      {
        path: '/admin/sorftime-test',
        component: () => import('../views/admin/sorftime-test/index.vue'),
        meta: { title: 'Sorftime API 测试', roles: ['admin'] }
      },
      {
        path: '/style-guide',
        component: () => import('../views/StyleGuide.vue'),
        meta: { title: '组件样式指南' }
      }
    ]
  },
  {
    path: '/extraction/:batchId',
    component: () => import('../views/extraction/index.vue'),
    meta: { title: 'AI 特征提取' }
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    // Role based guard
    if (to.meta.roles && Array.isArray(to.meta.roles)) {
      if (!to.meta.roles.includes(role || '')) {
        next('/') // Redirect to home if no permission
        return
      }
    }
    next()
  }
})
