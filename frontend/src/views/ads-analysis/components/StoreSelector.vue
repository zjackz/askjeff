<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { http } from '@/utils/http'
import { Shop } from '@element-plus/icons-vue'

interface Store {
  id: string
  store_name: string
  marketplace_id: string
  marketplace_name: string
  seller_id: string
  is_active: boolean
  last_sync_at: string | null
  created_at: string
}

const emit = defineEmits(['store-selected'])

const stores = ref<Store[]>([])
const selectedStoreId = ref<string>('')
const loading = ref(false)

const fetchStores = async () => {
  loading.value = true
  try {
    const response = await http.get('ads-analysis/stores')
    stores.value = response.data
    
    // 自动选择第一个店铺
    if (stores.value.length > 0 && !selectedStoreId.value) {
      const firstStore = stores.value[0]
      if (firstStore) {
        selectedStoreId.value = firstStore.id
        emit('store-selected', firstStore)
      }
    }
  } catch (error) {
    console.error('Failed to fetch stores:', error)
    ElMessage.error('获取店铺列表失败')
  } finally {
    loading.value = false
  }
}

const handleStoreChange = (storeId: string) => {
  const store = stores.value.find(s => s.id === storeId)
  if (store) {
    emit('store-selected', store)
  }
}

onMounted(() => {
  fetchStores()
})

defineExpose({
  selectedStoreId,
  stores
})
</script>

<template>
  <div class="premium-store-selector">
    <el-select
      v-model="selectedStoreId"
      placeholder="选择分析店铺"
      :loading="loading"
      @change="handleStoreChange"
      size="default"
      class="custom-select"
      popper-class="premium-select-popper"
    >
      <template #prefix>
        <el-icon><Shop /></el-icon>
      </template>
      <el-option
        v-for="store in stores"
        :key="store.id"
        :label="store.store_name"
        :value="store.id"
      >
        <div class="store-option-content">
          <div class="store-main">
            <span class="store-name">{{ store.store_name }}</span>
            <span v-if="!store.is_active" class="status-tag inactive">未激活</span>
          </div>
          <div class="store-sub">
            <span class="marketplace-label">{{ store.marketplace_name }}</span>
            <span class="seller-id">{{ store.seller_id }}</span>
          </div>
        </div>
      </el-option>
    </el-select>
  </div>
</template>

<style scoped lang="scss">
.premium-store-selector {
  display: inline-block;
}

:deep(.custom-select .el-input__wrapper) {
  background: var(--bg-secondary) !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
  border-radius: 12px;
  padding: 8px 16px;
  transition: all 0.3s ease;
}

:deep(.custom-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--primary-light) inset !important;
  background: var(--bg-tertiary) !important;
}

:deep(.custom-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--primary-color) inset !important;
  background: var(--bg-primary) !important;
}

:deep(.custom-select .el-input__inner) {
  color: var(--text-primary) !important;
  font-weight: 600;
}

:deep(.custom-select .el-input__prefix-inner) {
  color: var(--primary-color);
}

.store-option-content {
  display: flex;
  flex-direction: column;
  padding: 4px 0;
  line-height: 1.4;
}

.store-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.store-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.store-sub {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.status-tag {
  font-size: 10px;
  padding: 0 6px;
  border-radius: 4px;
}

.status-tag.inactive {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

.marketplace-label {
  background: var(--bg-secondary);
  padding: 0 4px;
  border-radius: 2px;
  color: var(--text-tertiary);
}
</style>

<style lang="scss">
.premium-select-popper {
  background: var(--bg-primary) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 16px !important;
  box-shadow: var(--shadow-lg) !important;
}

.premium-select-popper .el-select-dropdown__item {
  height: auto !important;
  padding: 8px 16px !important;
  color: var(--text-secondary) !important;
}

.premium-select-popper .el-select-dropdown__item.selected {
  color: var(--primary-color) !important;
  background: rgba(102, 126, 234, 0.1) !important;
}

.premium-select-popper .el-select-dropdown__item.hover {
  background: var(--bg-secondary) !important;
}
</style>
