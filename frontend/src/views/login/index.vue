<template>
  <div class="login-container">
    <!-- Dynamic Background Particles -->
    <div class="particles">
      <div class="particle" v-for="n in 6" :key="n"></div>
    </div>

    <div class="login-content fade-in-up">
      <div class="brand-section">
        <img src="/logo.png" alt="AskJeff Logo" class="brand-logo floating" />
        <p class="brand-slogan">Intelligent Data Analytics Platform</p>
      </div>
      
      <el-card class="login-card glass-effect" shadow="hover">
        <template #header>
          <div class="card-header">
            <h2>Welcome Back</h2>
            <p class="sub-text">Please sign in to continue</p>
          </div>
        </template>
        
        <el-form 
          ref="formRef"
          :model="form" 
          :rules="rules"
          label-position="top"
          @submit.prevent="handleLogin"
          size="large"
        >
          <el-form-item label="Username" prop="username">
            <el-input 
              v-model="form.username" 
              placeholder="Enter your username" 
              :prefix-icon="User"
              class="custom-input"
            />
          </el-form-item>
          
          <el-form-item label="Password" prop="password">
            <el-input 
              v-model="form.password" 
              type="password" 
              placeholder="Enter your password" 
              show-password 
              :prefix-icon="Lock"
              @keyup.enter="handleLogin"
              class="custom-input"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              native-type="submit" 
              :loading="loading" 
              class="submit-btn" 
              auto-insert-space
            >
              Sign In
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <div class="login-footer">
      <p>深圳拓芽 @2025</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { http } from '@/utils/http'
import type { FormInstance, FormRules } from 'element-plus'

import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  username: 'admin',
  password: 'password'
})

const rules = reactive<FormRules>({
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
})

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('username', form.username)
        formData.append('password', form.password)

        const response = await http.post('/login/access-token', formData)
        
        const { access_token } = response.data
        localStorage.setItem('token', access_token)
        userStore.token = access_token
        
        // Fetch user info to get role
        await userStore.getUserInfo()
        
        ElMessage.success('Welcome back!')
        router.push('/')
      } catch (error: any) {
        console.error(error)
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
  width: 100%;
  position: relative;
  background-color: #1e2944;
  overflow-x: hidden; /* Prevent horizontal scroll */
  overflow-y: auto;   /* Allow vertical scroll */
}

// Particles Animation Container - Fixed position
.particles {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
  animation: float-particle 20s infinite linear;
  
  &:nth-child(1) { width: 80px; height: 80px; left: 10%; top: 10%; animation-duration: 25s; }
  &:nth-child(2) { width: 120px; height: 120px; left: 80%; top: 20%; animation-duration: 30s; }
  &:nth-child(3) { width: 60px; height: 60px; left: 30%; top: 60%; animation-duration: 20s; }
  &:nth-child(4) { width: 100px; height: 100px; left: 70%; top: 80%; animation-duration: 35s; }
  &:nth-child(5) { width: 40px; height: 40px; left: 50%; top: 40%; animation-duration: 15s; }
  &:nth-child(6) { width: 150px; height: 150px; left: 20%; top: 90%; animation-duration: 40s; }
}

@keyframes float-particle {
  0% { transform: translateY(0) rotate(0deg); }
  100% { transform: translateY(-100vh) rotate(360deg); }
}

.login-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh; /* Ensure full height for centering */
  padding: 40px 20px 60px; /* Add bottom padding for footer space */
  box-sizing: border-box;
}

.fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.brand-section {
  text-align: center;
  margin-bottom: 2rem;
  
  .brand-logo {
    height: 80px;
    width: auto;
    margin-bottom: 0.5rem;
    filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
    transition: height 0.3s ease;
  }
  
  .floating {
    animation: float 6s ease-in-out infinite;
  }
  
  .brand-slogan {
    font-size: 1rem;
    color: #e5e7eb;
    margin-top: 0;
    opacity: 0.9;
    letter-spacing: 0.5px;
    transition: font-size 0.3s ease;
  }
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  }
  
  :deep(.el-card__header) {
    border-bottom: 1px solid rgba(0,0,0,0.05);
    padding: 24px;
    background: transparent;
  }
  
  :deep(.el-card__body) {
    padding: 32px 24px;
  }
}

.card-header {
  text-align: center;
  
  h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #1f2937;
    font-weight: 700;
  }
  
  .sub-text {
    margin: 8px 0 0;
    color: #6b7280;
    font-size: 0.9rem;
  }
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 8px;
  margin-top: 12px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border: none;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  }
  
  &:active {
    transform: translateY(0);
  }
}

:deep(.el-input__wrapper) {
  padding: 8px 12px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e5e7eb inset;
  background: #f9fafb;
  transition: all 0.3s ease;
  
  &:hover {
    background: #fff;
  }
  
  &.is-focus {
    box-shadow: 0 0 0 2px #2563eb inset;
    background: #fff;
  }
}

.login-footer {
  position: absolute;
  bottom: 20px;
  left: 0;
  width: 100%;
  text-align: center;
  z-index: 2;
  pointer-events: none; /* Allow clicking through if overlapping */
  
  p {
    color: rgba(255, 255, 255, 0.4);
    font-size: 0.85rem;
    margin: 0;
    letter-spacing: 1px;
  }
}

// Media Queries for Small Screens
@media (max-height: 700px) {
  .brand-section {
    margin-bottom: 1.5rem;
    
    .brand-logo {
      height: 60px;
    }
    
    .brand-slogan {
      font-size: 0.9rem;
    }
  }
  
  .login-card {
    :deep(.el-card__header) {
      padding: 16px 20px;
    }
    
    :deep(.el-card__body) {
      padding: 20px;
    }
  }
  
  .card-header {
    h2 { font-size: 1.25rem; }
    .sub-text { margin-top: 4px; font-size: 0.85rem; }
  }
  
  .login-footer {
    bottom: 10px;
    p { font-size: 0.75rem; }
  }
}

@media (max-width: 480px) {
  .login-content {
    padding: 20px;
  }
  
  .login-card {
    max-width: 100%;
  }
}
</style>
