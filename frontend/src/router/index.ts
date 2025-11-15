import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

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
        path: '/export',
        component: () => import('../views/export/index.vue'),
        meta: { title: '数据导出' }
      }
    ]
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
