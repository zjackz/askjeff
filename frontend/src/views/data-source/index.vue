<template>
  <div class="data-source-container">
    <el-card class="header-card">
      <div class="header-content">
        <h2>数据源管理</h2>
        <div class="actions">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索店铺..."
            :prefix-icon="Search"
            clearable
            style="width: 200px"
          />
          <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px">
            <el-option label="全部" :value="null" />
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加数据源
          </el-button>
        </div>
      </div>
    </el-card>

    <div class="stores-grid">
      <StoreCard
        v-for="store in filteredStores"
        :key="store.id"
        :store="store"
        @edit="handleEdit"
        @delete="handleDelete"
        @toggle="handleToggle"
        @sync="handleSync"
        @verify="handleVerify"
      />
    </div>

    <el-empty v-if="filteredStores.length === 0 && !loading" description="暂无数据源" />

    <!-- 添加/编辑对话框 -->
    <StoreForm
      v-model:visible="formDialogVisible"
      :store="currentStore"
      :mode="formMode"
      @submit="handleSubmit"
    />

    <!-- 同步进度对话框 -->
    <SyncProgress
      v-model:visible="syncDialogVisible"
      :store="currentStore"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { storesApi, type AmazonStore, type StoreCreate, type StoreUpdate } from '@/api/stores'
import StoreCard from './components/StoreCard.vue'
import StoreForm from './components/StoreForm.vue'
import SyncProgress from './components/SyncProgress.vue'

const loading = ref(false)
const stores = ref<AmazonStore[]>([])
const searchKeyword = ref('')
const filterStatus = ref<boolean | null>(null)
const formDialogVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const currentStore = ref<AmazonStore | null>(null)
const syncDialogVisible = ref(false)

// 计算过滤后的店铺列表
const filteredStores = computed(() => {
  return stores.value.filter(store => {
    // 搜索过滤
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      return store.store_name.toLowerCase().includes(keyword) ||
             store.marketplace_name.toLowerCase().includes(keyword) ||
             store.seller_id.toLowerCase().includes(keyword)
    }

    // 状态过滤
    if (filterStatus.value !== null) {
      return store.is_active === filterStatus.value
    }

    return true
  })
})

// 获取店铺列表
const fetchStores = async () => {
  loading.value = true
  try {
    const response = await storesApi.list({ page_size: 100 })
    stores.value = response.items
  } catch (error) {
    console.error('Failed to fetch stores', error)
    ElMessage.error('获取店铺列表失败')
  } finally {
    loading.value = false
  }
}

// 添加店铺
const handleAdd = () => {
  formMode.value = 'create'
  currentStore.value = null
  formDialogVisible.value = true
}

// 编辑店铺
const handleEdit = (store: AmazonStore) => {
  formMode.value = 'edit'
  currentStore.value = store
  formDialogVisible.value = true
}

// 删除店铺
const handleDelete = async (store: AmazonStore) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除店铺 "${store.store_name}" 吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await storesApi.delete(store.id)
    ElMessage.success('删除成功')
    await fetchStores()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete store', error)
      ElMessage.error('删除失败')
    }
  }
}

// 切换启用状态
const handleToggle = async (store: AmazonStore) => {
  try {
    await storesApi.update(store.id, { is_active: !store.is_active })
    ElMessage.success(store.is_active ? '已禁用' : '已启用')
    await fetchStores()
  } catch (error) {
    console.error('Failed to toggle store', error)
    ElMessage.error('操作失败')
  }
}

// 触发同步
const handleSync = (store: AmazonStore) => {
  currentStore.value = store
  syncDialogVisible.value = true
}

// 验证凭证
const handleVerify = async (store: AmazonStore) => {
  try {
    ElMessage.info('正在验证凭证...')
    const result = await storesApi.verify(store.id)
    if (result.valid) {
      ElMessage.success('凭证验证成功')
    } else {
      ElMessage.warning(result.message)
    }
  } catch (error) {
    console.error('Failed to verify credentials', error)
    ElMessage.error('凭证验证失败')
  }
}

// 提交表单
const handleSubmit = async (data: StoreCreate | StoreUpdate) => {
  try {
    if (formMode.value === 'create') {
      await storesApi.create(data as StoreCreate)
      ElMessage.success('创建成功')
    } else {
      await storesApi.update(currentStore.value!.id, data as StoreUpdate)
      ElMessage.success('更新成功')
    }
    formDialogVisible.value = false
    await fetchStores()
  } catch (error: any) {
    console.error('Failed to submit form', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

onMounted(() => {
  fetchStores()
})
</script>

<style scoped lang="scss">
.data-source-container {
  padding: var(--spacing-lg);
}

.header-card {
  margin-bottom: var(--spacing-lg);

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
    }

    .actions {
      display: flex;
      gap: var(--spacing-md);
    }
  }
}

.stores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}
</style>
