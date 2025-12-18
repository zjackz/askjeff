# 前端编码规范

> Vue 3 + TypeScript 项目的编码标准和最佳实践

**最后更新**: 2025-12-18

---

## 组件规范

### 组件大小限制

- **单个 .vue 文件**: ≤ 300 行
- **单个函数/方法**: ≤ 50 行
- **script setup 块**: ≤ 200 行

**超过限制时必须拆分!**

---

### 组件拆分原则

#### 何时拆分?

1. **文件 >300 行** - 立即拆分
2. **重复逻辑 >3 次** - 提取 composable
3. **独立功能模块** - 拆分为子组件
4. **复杂表单/表格** - 拆分为独立组件

#### 如何拆分?

```
大组件 (>300 行)
├── components/
│   ├── ComponentHeader.vue
│   ├── ComponentForm.vue
│   ├── ComponentTable.vue
│   └── ComponentDialog.vue
├── composables/
│   ├── useComponentData.ts
│   └── useComponentActions.ts
└── types/
    └── component.ts
```

---

### 组件命名

- **PascalCase**: 组件文件名和组件名
- **kebab-case**: 模板中使用

```vue
<!-- ✅ 正确 -->
<script setup lang="ts">
import UserProfile from '@/components/UserProfile.vue'
</script>

<template>
  <user-profile />
</template>

<!-- ❌ 错误 -->
<template>
  <UserProfile />  <!-- 应该用 kebab-case -->
</template>
```

---

## Composables 规范

### 命名约定

- 以 `use` 开头
- 描述功能,不是数据

```typescript
// ✅ 正确
useUserData()
useProductList()
usePagination()

// ❌ 错误
userData()
products()
pagination()
```

---

### Composable 结构

```typescript
// composables/useProductList.ts
import { ref, computed } from 'vue'
import type { Product } from '@/types'

export function useProductList() {
  // 1. 状态
  const products = ref<Product[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)
  
  // 2. 计算属性
  const totalCount = computed(() => products.value.length)
  
  // 3. 方法
  async function fetchProducts() {
    loading.value = true
    try {
      const data = await api.getProducts()
      products.value = data
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }
  
  // 4. 返回
  return {
    products,
    loading,
    error,
    totalCount,
    fetchProducts
  }
}
```

---

### 通用 Composables

项目应该有以下通用 composables:

```typescript
// composables/useLoading.ts
export function useLoading()

// composables/usePagination.ts
export function usePagination()

// composables/useTable.ts
export function useTable()

// composables/useForm.ts
export function useForm()

// composables/useDialog.ts
export function useDialog()
```

---

## TypeScript 规范

### 类型定义

```typescript
// ✅ 正确 - 定义接口
interface Product {
  id: number
  asin: string
  title: string
  price: number
}

// ✅ 正确 - 使用类型
const product = ref<Product>()
const products = ref<Product[]>([])

// ❌ 错误 - 使用 any
const product = ref<any>()
```

---

### API 响应类型

```typescript
// types/api.ts
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

// 使用
async function getProducts(): Promise<ApiResponse<Product[]>> {
  // ...
}
```

---

## 状态管理规范

### Pinia Store 结构

```typescript
// stores/product.ts
import { defineStore } from 'pinia'

export const useProductStore = defineStore('product', () => {
  // 1. State
  const products = ref<Product[]>([])
  const loading = ref(false)
  
  // 2. Getters
  const activeProducts = computed(() => 
    products.value.filter(p => p.status === 'active')
  )
  
  // 3. Actions
  async function fetchProducts() {
    loading.value = true
    try {
      products.value = await api.getProducts()
    } finally {
      loading.value = false
    }
  }
  
  return {
    products,
    loading,
    activeProducts,
    fetchProducts
  }
})
```

---

## API 调用规范

### 统一的 API 客户端

```typescript
// api/client.ts
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000
})

// 请求拦截器
client.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
client.interceptors.response.use(
  response => response.data,
  error => {
    // 统一错误处理
    ElMessage.error(error.message)
    return Promise.reject(error)
  }
)
```

---

### API 模块化

```typescript
// api/product.ts
import { client } from './client'
import type { Product, ApiResponse } from '@/types'

export const productApi = {
  list: (params: ListParams) => 
    client.get<ApiResponse<Product[]>>('/products', { params }),
  
  get: (id: number) => 
    client.get<ApiResponse<Product>>(`/products/${id}`),
  
  create: (data: ProductCreate) => 
    client.post<ApiResponse<Product>>('/products', data),
  
  update: (id: number, data: ProductUpdate) => 
    client.put<ApiResponse<Product>>(`/products/${id}`, data),
  
  delete: (id: number) => 
    client.delete<ApiResponse<void>>(`/products/${id}`)
}
```

---

## UI 规范

### Loading 状态

**所有 API 调用必须有 loading 状态!**

```vue
<template>
  <el-button :loading="loading" @click="handleSubmit">
    提交
  </el-button>
  
  <el-table :data="products" v-loading="loading">
    <!-- ... -->
  </el-table>
</template>

<script setup lang="ts">
const loading = ref(false)

async function handleSubmit() {
  loading.value = true
  try {
    await api.submit()
  } finally {
    loading.value = false
  }
}
</script>
```

---

### 错误处理

**所有错误必须有用户友好的中文提示!**

```typescript
// ✅ 正确
try {
  await api.submit()
  ElMessage.success('提交成功')
} catch (error) {
  ElMessage.error('提交失败,请重试')
  console.error('Submit failed:', error)
}

// ❌ 错误
try {
  await api.submit()
} catch (error) {
  console.error(error)  // 用户看不到错误
}
```

---

### 表格规范

```vue
<template>
  <el-table
    :data="products"
    v-loading="loading"
    border
    stripe
  >
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="title" label="标题" min-width="200" />
    <!-- ... -->
  </el-table>
  
  <!-- 分页 -->
  <el-pagination
    v-model:current-page="page"
    v-model:page-size="pageSize"
    :total="total"
    :page-sizes="[20, 50, 100, 200]"
    layout="total, sizes, prev, pager, next, jumper"
    @size-change="handleSizeChange"
    @current-change="handlePageChange"
  />
</template>
```

---

### 表单规范

```vue
<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="120px"
  >
    <el-form-item label="产品名称" prop="title">
      <el-input v-model="form.title" />
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="handleSubmit">
        提交
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
const formRef = ref()
const form = reactive({
  title: ''
})

const rules = {
  title: [
    { required: true, message: '请输入产品名称', trigger: 'blur' }
  ]
}

async function handleSubmit() {
  await formRef.value.validate()
  // 提交逻辑
}
</script>
```

---

## 性能优化

### 懒加载

```typescript
// router/index.ts
const routes = [
  {
    path: '/products',
    component: () => import('@/views/products/index.vue')  // 懒加载
  }
]
```

---

### 计算属性缓存

```typescript
// ✅ 正确 - 使用 computed
const filteredProducts = computed(() => 
  products.value.filter(p => p.status === 'active')
)

// ❌ 错误 - 每次都重新计算
function getFilteredProducts() {
  return products.value.filter(p => p.status === 'active')
}
```

---

### 避免不必要的响应式

```typescript
// ✅ 正确 - 常量不需要响应式
const PAGE_SIZES = [20, 50, 100, 200]

// ❌ 错误 - 浪费性能
const pageSizes = ref([20, 50, 100, 200])
```

---

## 代码质量

### 禁止使用 console

```typescript
// ❌ 错误 - 生产环境会暴露信息
console.log('User data:', userData)
console.error('API failed:', error)

// ✅ 正确 - 使用日志服务
import { logger } from '@/utils/logger'
logger.debug('User data:', userData)
logger.error('API failed:', error)
```

---

### 移除 TODO 注释

```typescript
// ❌ 错误 - TODO 应该创建 Issue
// TODO: 实现分页功能

// ✅ 正确 - 创建 GitHub Issue #123
// See: #123 - 实现分页功能
```

---

## 自检清单

### 提交前必查

**组件**:
- [ ] 文件 ≤ 300 行
- [ ] 单一职责
- [ ] 有 TypeScript 类型
- [ ] 有中文注释

**API 调用**:
- [ ] 有 loading 状态
- [ ] 有错误处理
- [ ] 错误提示是中文
- [ ] 有超时配置

**UI 交互**:
- [ ] 表格有分页 [20, 50, 100, 200]
- [ ] 表单有校验
- [ ] 危险操作有确认
- [ ] 响应式布局正常

**代码质量**:
- [ ] 无 console 调用
- [ ] 无 TODO 注释
- [ ] 无 any 类型
- [ ] 通过 ESLint

---

## 参考资料

- [Vue 3 官方文档](https://cn.vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Pinia 文档](https://pinia.vuejs.org/)
