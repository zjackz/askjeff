<template>
  <div class="admin-container">
    <el-card class="admin-card">
      <template #header>
        <div class="card-header">
          <span>数据管理</span>
        </div>
      </template>
      
      <div class="action-section">
        <div class="warning-box">
          <el-icon class="warning-icon"><Warning /></el-icon>
          <div class="warning-content">
            <h3>危险操作区域</h3>
            <p>以下操作不可逆，请谨慎执行。主要用于测试环境的数据重置。</p>
          </div>
        </div>
        
        <div class="action-item">
          <div class="action-info">
            <h4>清空所有数据</h4>
            <p>删除所有产品、提取任务、导入批次和日志数据。保留用户账号。</p>
          </div>
          
          <el-popconfirm
            title="确定要清空所有数据吗？此操作不可恢复！"
            confirm-button-text="确定删除"
            cancel-button-text="取消"
            confirm-button-type="danger"
            @confirm="handleDeleteAllData"
          >
            <template #reference>
              <el-button type="danger" :loading="loading">
                <el-icon><Delete /></el-icon>
                一键清空
              </el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Delete, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { http } from '@/utils/http'

const loading = ref(false)

const handleDeleteAllData = async () => {
  loading.value = true
  try {
    await http.delete('/admin/data')
    ElMessage.success('所有数据已清空')
  } catch (error) {
    console.error('Failed to delete data', error)
    // Error is handled by global interceptor usually, but we can add specific handling
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.admin-container {
  max-width: 800px;
  margin: 0 auto;
}

.admin-card {
  border-radius: var(--radius-lg);
}

.card-header {
  font-size: 1.1rem;
  font-weight: 600;
}

.warning-box {
  background-color: var(--warning-light);
  border: 1px solid var(--warning-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
  
  .warning-icon {
    font-size: 24px;
    color: var(--warning-color);
    flex-shrink: 0;
  }
  
  .warning-content {
    h3 {
      margin: 0 0 4px 0;
      color: var(--warning-dark);
      font-size: 1rem;
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 0.9rem;
    }
  }
}

.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  
  .action-info {
    h4 {
      margin: 0 0 4px 0;
      font-size: 1rem;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 0.9rem;
    }
  }
}
</style>
