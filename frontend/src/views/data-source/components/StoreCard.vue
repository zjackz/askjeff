<template>
  <el-card class="store-card" :class="{ 'disabled': !store.is_active }">
    <template #header>
      <div class="card-header">
        <div class="store-info">
          <el-icon class="store-icon"><ShoppingBag /></el-icon>
          <div>
            <div class="store-name">{{ store.store_name }}</div>
            <div class="store-status">
              <el-tag :type="store.is_active ? 'success' : 'info'" size="small">
                {{ store.is_active ? '启用' : '禁用' }}
              </el-tag>
              <el-badge
                v-if="store.latest_sync"
                :value="getSyncStatus(store.latest_sync.status)"
                :type="getSyncBadgeType(store.latest_sync.status)"
                is-dot
              >
                <span class="sync-status-text">{{ getSyncStatusText(store.latest_sync.status) }}</span>
              </el-badge>
            </div>
          </div>
        </div>
        <el-dropdown trigger="click" @command="handleCommand">
          <el-button type="primary" link>
            <el-icon><More /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="sync">
                <el-icon><Refresh /></el-icon>
                立即同步
              </el-dropdown-item>
              <el-dropdown-item command="verify" :disabled="!store.has_credentials">
                <el-icon><CircleCheck /></el-icon>
                验证凭证
              </el-dropdown-item>
              <el-dropdown-item command="toggle">
                <el-icon><Operation /></el-icon>
                {{ store.is_active ? '禁用' : '启用' }}
              </el-dropdown-item>
              <el-dropdown-item command="edit">
                <el-icon><Edit /></el-icon>
                编辑
              </el-dropdown-item>
              <el-dropdown-item command="delete" divided>
                <el-icon><Delete /></el-icon>
                删除
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </template>

    <div class="card-content">
      <div class="info-row">
        <span class="label">市场:</span>
        <span class="value">{{ getMarketFlag(store.marketplace_id) }} {{ store.marketplace_name }}</span>
      </div>
      <div class="info-row">
        <span class="label">卖家 ID:</span>
        <span class="value">{{ store.seller_id }}</span>
      </div>
      <div class="info-row">
        <span class="label">最后同步:</span>
        <span class="value">{{ formatTime(store.last_sync_at) }}</span>
      </div>
      <div class="info-row">
        <span class="label">凭证状态:</span>
        <span class="value">
          <el-tag v-if="store.has_credentials" type="success" size="small">已配置</el-tag>
          <el-tag v-else type="warning" size="small">未配置</el-tag>
        </span>
      </div>
    </div>

    <template #footer>
      <div class="card-footer">
        <el-button
          :type="store.is_active ? 'success' : 'primary'"
          :icon="Refresh"
          @click="emit('sync', store)"
        >
          立即同步
        </el-button>
        <el-button :icon="Edit" @click="emit('edit', store)">
          编辑
        </el-button>
        <el-button
          :icon="store.is_active ? VideoPause : VideoPlay"
          @click="emit('toggle', store)"
        >
          {{ store.is_active ? '禁用' : '启用' }}
        </el-button>
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  ShoppingBag,
  More,
  Refresh,
  CircleCheck,
  Operation,
  Edit,
  Delete,
  VideoPause,
  VideoPlay
} from '@element-plus/icons-vue'
import type { AmazonStore } from '@/api/stores'
import { dayjs } from 'element-plus/es/components/time-picker/shared/helper.mjs'

interface Props {
  store: AmazonStore
}

const props = defineProps<Props>()

const emit = defineEmits<{
  edit: [store: AmazonStore]
  delete: [store: AmazonStore]
  toggle: [store: AmazonStore]
  sync: [store: AmazonStore]
  verify: [store: AmazonStore]
}>()

const handleCommand = (command: string) => {
  switch (command) {
    case 'sync':
      emit('sync', props.store)
      break
    case 'verify':
      emit('verify', props.store)
      break
    case 'toggle':
      emit('toggle', props.store)
      break
    case 'edit':
      emit('edit', props.store)
      break
    case 'delete':
      emit('delete', props.store)
      break
  }
}

const formatTime = (time?: string) => {
  if (!time) return '从未同步'
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const getMarketFlag = (marketplaceId: string) => {
  const flags: Record<string, string> = {
    'ATVPDKIKX0DER': '🇺🇸',
    'A1PA6795UKMFR9': '🇩🇪',
    'A1VC38T7YXB528': '🇯🇵',
    'A13UK1VYFJ83R7': '🇬🇧',
    'A2NODRKZP66I6WI': '🇮🇹',
    'A1F83G8C2OOF0N7': '🇪🇸',
    'A2Q3Y263D00KWC': '🇫🇷',
    'A1AM78C64UM0SV': '🇨🇦',
    'A1RKKUPIH0ZJDM': '🇦🇺'
  }
  return flags[marketplaceId] || '🌐'
}

const getSyncStatus = (status: string) => {
  const statusMap: Record<string, number> = {
    'never': 0,
    'running': 1,
    'success': 0,
    'failed': 1
  }
  return statusMap[status] || 0
}

const getSyncBadgeType = (status: string) => {
  const typeMap: Record<string, any> = {
    'never': 'info',
    'running': 'warning',
    'success': 'success',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

const getSyncStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    'never': '从未同步',
    'running': '同步中...',
    'success': '成功',
    'failed': '失败'
  }
  return textMap[status] || '未知'
}
</script>

<style scoped lang="scss">
.store-card {
  transition: all 0.3s ease;

  &:hover {
    box-shadow: var(--shadow-md);
  }

  &.disabled {
    opacity: 0.7;
  }

  :deep(.el-card__header) {
    padding: var(--spacing-md);
  }

  :deep(.el-card__body) {
    padding: var(--spacing-md);
  }

  :deep(.el-card__footer) {
    padding: var(--spacing-md);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-md);

  .store-info {
    display: flex;
    gap: var(--spacing-md);
    flex: 1;
  }

  .store-icon {
    font-size: 32px;
    color: var(--primary-color);
  }

  .store-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .store-status {
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
  }

  .sync-status-text {
    font-size: 0.85rem;
    color: var(--text-secondary);
  }
}

.card-content {
  .info-row {
    display: flex;
    justify-content: space-between;
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid var(--border-light);

    &:last-child {
      border-bottom: none;
    }

    .label {
      font-size: 0.9rem;
      color: var(--text-secondary);
    }

    .value {
      font-size: 0.9rem;
      color: var(--text-primary);
      font-weight: 500;
    }
  }
}

.card-footer {
  display: flex;
  gap: var(--spacing-sm);
}
</style>
