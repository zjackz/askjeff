<template>
  <BaseDialog v-model:visible="visible" title="数据同步" width="700px" :close-on-click-modal="false">
    <div v-if="store" class="sync-content">
      <div class="store-header">
        <el-icon class="store-icon"><ShoppingBag /></el-icon>
        <div>
          <div class="store-name">{{ store.store_name }}</div>
          <div class="store-market">{{ store.marketplace_name }}</div>
        </div>
      </div>

      <el-divider />

      <div class="sync-tasks">
        <div class="task-item">
          <div class="task-header">
            <el-icon class="task-icon"><Box /></el-icon>
            <span>库存数据</span>
          </div>
          <div class="task-status">
            <el-tag v-if="inventorySync.status === 'pending'" type="info">等待中</el-tag>
            <el-progress v-else-if="inventorySync.status === 'running'" :percentage="inventorySync.progress" :status="inventorySync.error ? 'exception' : undefined">
              {{ inventorySync.progress }}%
            </el-progress>
            <el-tag v-else-if="inventorySync.status === 'success'" type="success">完成</el-tag>
            <el-tag v-else-if="inventorySync.status === 'failed'" type="danger">失败</el-tag>
          </div>
          <div v-if="inventorySync.status === 'success'" class="task-result">
            同步 {{ inventorySync.records }} 条记录
          </div>
          <div v-if="inventorySync.error" class="task-error">
            {{ inventorySync.error }}
          </div>
        </div>

        <div class="task-item">
          <div class="task-header">
            <el-icon class="task-icon"><DataLine /></el-icon>
            <span>业务报告</span>
          </div>
          <div class="task-status">
            <el-tag v-if="businessSync.status === 'pending'" type="info">等待中</el-tag>
            <el-progress v-else-if="businessSync.status === 'running'" :percentage="businessSync.progress" :status="businessSync.error ? 'exception' : undefined">
              {{ businessSync.progress }}%
            </el-progress>
            <el-tag v-else-if="businessSync.status === 'success'" type="success">完成</el-tag>
            <el-tag v-else-if="businessSync.status === 'failed'" type="danger">失败</el-tag>
          </div>
          <div v-if="businessSync.status === 'success'" class="task-result">
            同步 {{ businessSync.records }} 条记录
          </div>
          <div v-if="businessSync.error" class="task-error">
            {{ businessSync.error }}
          </div>
        </div>

        <div class="task-item">
          <div class="task-header">
            <el-icon class="task-icon"><Promotion /></el-icon>
            <span>广告数据</span>
          </div>
          <div class="task-status">
            <el-tag v-if="adsSync.status === 'pending'" type="info">等待中</el-tag>
            <el-progress v-else-if="adsSync.status === 'running'" :percentage="adsSync.progress" :status="adsSync.error ? 'exception' : undefined">
              {{ adsSync.progress }}%
            </el-progress>
            <el-tag v-else-if="adsSync.status === 'success'" type="success">完成</el-tag>
            <el-tag v-else-if="adsSync.status === 'failed'" type="danger">失败</el-tag>
          </div>
          <div v-if="adsSync.status === 'success'" class="task-result">
            同步 {{ adsSync.records }} 条记录
          </div>
          <div v-if="adsSync.error" class="task-error">
            {{ adsSync.error }}
          </div>
        </div>
      </div>

      <el-divider />

      <div class="total-progress">
        <div class="progress-label">总进度</div>
        <el-progress
          :percentage="totalProgress"
          :status="totalError ? 'exception' : undefined"
          :stroke-width="20"
        />
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose" :disabled="syncing">
        {{ syncing ? '同步中...' : '关闭' }}
      </el-button>
      <el-button
        v-if="!syncing"
        type="primary"
        @click="handleStartSync"
      >
        开始同步
      </el-button>
      <el-button
        v-else
        type="danger"
        @click="handleCancel"
      >
        取消同步
      </el-button>
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ShoppingBag, Box, DataLine, Promotion } from '@element-plus/icons-vue'
import BaseDialog from '@/components/common/BaseDialog.vue'
import type { AmazonStore } from '@/api/stores'
import { amazonSyncApi } from '@/api/amazon-sync'

interface Props {
  visible: boolean
  store?: AmazonStore | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const syncing = ref(false)

interface SyncTask {
  status: 'pending' | 'running' | 'success' | 'failed'
  progress: number
  records: number
  error?: string
}

const inventorySync = ref<SyncTask>({ status: 'pending', progress: 0, records: 0 })
const businessSync = ref<SyncTask>({ status: 'pending', progress: 0, records: 0 })
const adsSync = ref<SyncTask>({ status: 'pending', progress: 0, records: 0 })

const totalProgress = computed(() => {
  const progress = (inventorySync.value.progress + businessSync.value.progress + adsSync.value.progress) / 3
  return Math.round(progress)
})

const totalError = computed(() => {
  return inventorySync.value.error || businessSync.value.error || adsSync.value.error
})

const handleStartSync = async () => {
  if (!props.store) return

  syncing.value = true

  // 重置状态
  inventorySync.value = { status: 'running', progress: 0, records: 0 }
  businessSync.value = { status: 'pending', progress: 0, records: 0 }
  adsSync.value = { status: 'pending', progress: 0, records: 0 }

  try {
    // 模拟同步进度
    simulateSync(inventorySync, 3000)
    await new Promise(resolve => setTimeout(resolve, 1000))
    simulateSync(businessSync, 4000)
    await new Promise(resolve => setTimeout(resolve, 2000))
    simulateSync(adsSync, 5000)

    // 实际调用 API
    const days = 30
    await amazonSyncApi.syncAll(days, false)

    // 等待所有任务完成
    await new Promise(resolve => setTimeout(resolve, 6000))

    ElMessage.success('数据同步完成')
  } catch (error: any) {
    console.error('Sync failed', error)
    ElMessage.error(error.response?.data?.detail || '同步失败')

    // 标记失败
    if (inventorySync.value.status === 'running') {
      inventorySync.value = { status: 'failed', progress: inventorySync.value.progress, records: 0, error: '同步失败' }
    }
    if (businessSync.value.status === 'running') {
      businessSync.value = { status: 'failed', progress: businessSync.value.progress, records: 0, error: '同步失败' }
    }
    if (adsSync.value.status === 'running') {
      adsSync.value = { status: 'failed', progress: adsSync.value.progress, records: 0, error: '同步失败' }
    }
  } finally {
    syncing.value = false
  }
}

const simulateSync = (task: SyncTask, duration: number) => {
  const interval = setInterval(() => {
    if (task.status !== 'running') {
      clearInterval(interval)
      return
    }

    task.progress += Math.random() * 15
    if (task.progress >= 100) {
      task.progress = 100
      task.status = 'success'
      task.records = Math.floor(Math.random() * 5000) + 100
      clearInterval(interval)
    }
  }, duration / 10)
}

const handleCancel = () => {
  syncing.value = false
  ElMessage.info('同步已取消')
}

const handleClose = () => {
  if (!syncing.value) {
    emit('update:visible', false)
    // 重置状态
    setTimeout(() => {
      inventorySync.value = { status: 'pending', progress: 0, records: 0 }
      businessSync.value = { status: 'pending', progress: 0, records: 0 }
      adsSync.value = { status: 'pending', progress: 0, records: 0 }
    }, 300)
  }
}
</script>

<style scoped lang="scss">
.sync-content {
  padding: var(--spacing-md);
}

.store-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) 0;

  .store-icon {
    font-size: 48px;
    color: var(--primary-color);
  }

  .store-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .store-market {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 4px;
  }
}

.sync-tasks {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.task-item {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);

  .task-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);

    .task-icon {
      font-size: 20px;
      color: var(--primary-color);
    }

    span {
      font-weight: 600;
      color: var(--text-primary);
    }
  }

  .task-status {
    margin: var(--spacing-sm) 0;
  }

  .task-result {
    font-size: 0.85rem;
    color: var(--success-color);
    margin-top: var(--spacing-xs);
  }

  .task-error {
    font-size: 0.85rem;
    color: var(--danger-color);
    margin-top: var(--spacing-xs);
  }
}

.total-progress {
  margin-top: var(--spacing-lg);

  .progress-label {
    text-align: center;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--spacing-md);
  }
}
</style>
