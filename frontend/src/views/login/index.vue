<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <img src="/logo.png" alt="Logo" class="login-logo" />
        <h2 class="login-title">AskJeff 控制台</h2>
        <p class="login-subtitle">专业的亚马逊产品数据分析系统</p>
      </div>
      
      <el-card class="login-card" shadow="hover">
        <el-form 
          ref="formRef"
          :model="formData"
          :rules="rules"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input 
              v-model="formData.username" 
              placeholder="请输入账号" 
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="formData.password" 
              type="password" 
              placeholder="请输入密码" 
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-button 
            type="primary" 
            class="login-button" 
            size="large" 
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
          
          <div class="login-tips">
            默认账号: admin / admin666
          </div>
        </el-form>
      </el-card>
      
      <div class="login-footer">
        &copy; {{ new Date().getFullYear() }} AskJeff. All Rights Reserved.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const success = await userStore.login(formData.username, formData.password)
        if (success) {
          ElMessage.success('登录成功')
          router.push('/dashboard')
        } else {
          ElMessage.error('账号或密码错误')
        }
      } catch (error) {
        ElMessage.error('登录失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  }
}

.login-content {
  width: 100%;
  max-width: 420px;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  
  .login-logo {
    height: 64px;
    margin-bottom: 16px;
  }
  
  .login-title {
    font-size: 28px;
    color: #303133;
    margin: 0 0 8px;
    font-weight: 600;
  }
  
  .login-subtitle {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.login-card {
  border-radius: 12px;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  
  :deep(.el-card__body) {
    padding: 40px 30px;
  }
}

.login-form {
  .el-input {
    --el-input-height: 48px;
    
    :deep(.el-input__wrapper) {
      box-shadow: 0 0 0 1px #dcdfe6 inset;
      
      &:hover, &.is-focus {
        box-shadow: 0 0 0 1px var(--primary-color) inset;
      }
    }
  }
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
}

.login-tips {
  margin-top: 16px;
  text-align: center;
  font-size: 12px;
  color: #909399;
}

.login-footer {
  margin-top: 40px;
  text-align: center;
  font-size: 12px;
  color: #909399;
}
</style>
