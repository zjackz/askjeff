# 前端组件库

通用组件库,提供常用的业务组件,提高开发效率。

## 📦 组件列表

### 基础组件

#### 1. BaseButton - 按钮组件

```vue
<BaseButton type="primary" @click="handleClick">点击</BaseButton>
<BaseButton type="success" :loading="loading">提交</BaseButton>
<BaseButton type="danger" :disabled="true">删除</BaseButton>
```

**Props**:

- `type`: 按钮类型 (primary | success | warning | danger | info | text)
- `size`: 尺寸 (large | default | small)
- `loading`: 加载状态
- `disabled`: 禁用状态
- `icon`: 图标
- `plain`: 朴素按钮
- `round`: 圆角按钮
- `circle`: 圆形按钮

---

#### 2. BaseTable - 表格组件

```vue
<BaseTable
  :data="tableData"
  :columns="columns"
  :loading="loading"
  :total="total"
  @page-change="handlePageChange"
  @row-click="handleRowClick"
>
  <template #actions="{ row }">
    <el-button size="small" @click="handleEdit(row)">编辑</el-button>
    <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
  </template>
</BaseTable>
```

**Props**:

- `data`: 表格数据
- `columns`: 列配置
- `loading`: 加载状态
- `stripe`: 斑马纹
- `border`: 边框
- `showSelection`: 显示多选列
- `showIndex`: 显示序号列
- `showActions`: 显示操作列
- `showPagination`: 显示分页
- `total`: 总数
- `page`: 当前页
- `pageSize`: 每页数量

**Events**:

- `row-click`: 行点击
- `selection-change`: 选择变化
- `page-change`: 页码变化
- `size-change`: 每页数量变化

---

#### 3. BaseDialog - 对话框组件

```vue
<BaseDialog
  v-model="visible"
  title="编辑"
  @confirm="handleConfirm"
  @cancel="handleCancel"
>
  <p>对话框内容</p>
</BaseDialog>
```

**Props**:

- `modelValue`: 显示状态
- `title`: 标题
- `width`: 宽度
- `fullscreen`: 全屏
- `showFooter`: 显示底部按钮
- `confirmText`: 确认按钮文本
- `cancelText`: 取消按钮文本
- `confirmLoading`: 确认按钮加载状态

**Events**:

- `confirm`: 确认
- `cancel`: 取消
- `open`: 打开
- `close`: 关闭

---

#### 4. BaseForm - 表单组件

```vue
<BaseForm
  :model="formData"
  :rules="rules"
  :items="formItems"
  @submit="handleSubmit"
  @reset="handleReset"
/>
```

**Props**:

- `model`: 表单数据
- `rules`: 验证规则
- `items`: 表单项配置
- `labelWidth`: 标签宽度
- `labelPosition`: 标签位置
- `showButtons`: 显示按钮
- `submitText`: 提交按钮文本
- `submitLoading`: 提交按钮加载状态

**FormItem 配置**:

```typescript
{
  prop: 'name',
  label: '名称',
  type: 'input',
  placeholder: '请输入名称',
  required: true
}
```

**支持的类型**:

- `input`: 输入框
- `textarea`: 文本域
- `select`: 选择器
- `date`: 日期选择器
- `number`: 数字输入框
- `switch`: 开关
- `custom`: 自定义 (使用插槽)

---

## 🎯 使用示例

### 完整示例: 用户管理页面

```vue
<template>
  <div class="user-management">
    <!-- 搜索表单 -->
    <BaseForm
      :model="searchForm"
      :items="searchItems"
      :inline="true"
      :show-buttons="false"
    >
      <template #actions>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="success" @click="handleAdd">新增</el-button>
      </template>
    </BaseForm>

    <!-- 数据表格 -->
    <BaseTable
      :data="tableData"
      :columns="columns"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      @page-change="handlePageChange"
      @size-change="handleSizeChange"
    >
      <template #status="{ row }">
        <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
          {{ row.status === 'active' ? '激活' : '禁用' }}
        </el-tag>
      </template>

      <template #actions="{ row }">
        <el-button size="small" @click="handleEdit(row)">编辑</el-button>
        <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
      </template>
    </BaseTable>

    <!-- 编辑对话框 -->
    <BaseDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :confirm-loading="submitLoading"
      @confirm="handleSubmit"
    >
      <BaseForm
        ref="formRef"
        :model="formData"
        :rules="rules"
        :items="formItems"
        :show-buttons="false"
      />
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import BaseForm from '@/components/common/BaseForm.vue'
import BaseTable from '@/components/common/BaseTable.vue'
import BaseDialog from '@/components/common/BaseDialog.vue'

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: ''
})

const searchItems = [
  { prop: 'keyword', label: '关键词', type: 'input', placeholder: '请输入关键词' },
  { prop: 'status', label: '状态', type: 'select', options: [
    { label: '全部', value: '' },
    { label: '激活', value: 'active' },
    { label: '禁用', value: 'inactive' }
  ]}
]

// 表格
const tableData = ref([])
const columns = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'name', label: '姓名', minWidth: 120 },
  { prop: 'email', label: '邮箱', minWidth: 180 },
  { prop: 'status', label: '状态', width: 100, slot: 'status' }
]

const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增用户')
const submitLoading = ref(false)

const formData = reactive({
  name: '',
  email: '',
  status: 'active'
})

const formItems = [
  { prop: 'name', label: '姓名', type: 'input', required: true },
  { prop: 'email', label: '邮箱', type: 'input', required: true },
  { prop: 'status', label: '状态', type: 'select', options: [
    { label: '激活', value: 'active' },
    { label: '禁用', value: 'inactive' }
  ]}
]

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }
  ]
}

// 方法
const handleSearch = () => {
  page.value = 1
  fetchData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  handleSearch()
}

const handleAdd = () => {
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogTitle.value = '编辑用户'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = (row: any) => {
  // 删除逻辑
}

const handleSubmit = async () => {
  // 提交逻辑
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  fetchData()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  fetchData()
}

const fetchData = () => {
  // 获取数据
}
</script>
```

---

## 📝 开发规范

### 1. 组件命名

- 基础组件: `Base` 前缀 (BaseButton, BaseTable)
- 业务组件: 功能名称 (UserCard, ProductList)
- 布局组件: `Layout` 前缀 (LayoutHeader, LayoutSidebar)

### 2. Props 定义

- 使用 TypeScript 接口定义
- 提供默认值
- 添加注释说明

### 3. Events 定义

- 使用 `defineEmits` 定义
- 事件名使用 kebab-case
- 提供类型定义

### 4. 插槽使用

- 提供默认插槽和具名插槽
- 使用作用域插槽传递数据
- 添加使用示例

---

## 🔄 组件更新日志

### v1.0.0 (2025-12-30)

- ✅ BaseButton - 按钮组件
- ✅ BaseTable - 表格组件
- ✅ BaseDialog - 对话框组件
- ✅ BaseForm - 表单组件

### 计划中

- [ ] BaseCard - 卡片组件
- [ ] BaseUpload - 上传组件
- [ ] BaseSearch - 搜索组件
- [ ] BaseTabs - 标签页组件
- [ ] BaseTree - 树形组件

---

## 📖 参考资料

- [Element Plus 文档](https://element-plus.org/)
- [Vue 3 文档](https://vuejs.org/)
- [TypeScript 文档](https://www.typescriptlang.org/)
