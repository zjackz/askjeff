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
        meta: { title: '数据洞察' }
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
      }
    ]
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
