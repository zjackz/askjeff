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
        path: '/chat',
        component: () => import('../views/chat/index.vue'),
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
        path: '/extraction/:batchId',
        component: () => import('../views/extraction/index.vue'),
        meta: { title: '特征提取' }
      }
    ]
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})
