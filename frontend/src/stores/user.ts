import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
    const token = ref(localStorage.getItem('token') || '')

    const login = async (username: string, password: string): Promise<boolean> => {
        // 模拟登录验证
        if (username === 'admin' && password === 'admin666') {
            const mockToken = 'mock-token-' + Date.now()
            token.value = mockToken
            localStorage.setItem('token', mockToken)
            return true
        }
        return false
    }

    const logout = () => {
        token.value = ''
        localStorage.removeItem('token')
        // 这里的 router 可能在 setup 外无法直接使用，通常在组件内调用 logout 后手动跳转
        // 或者直接使用 window.location.reload() 简单粗暴
    }

    return {
        token,
        login,
        logout
    }
})
