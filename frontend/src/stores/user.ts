import { defineStore } from 'pinia'
import { ref } from 'vue'
import { http } from '@/utils/http'

export const useUserStore = defineStore('user', () => {
    const token = ref(localStorage.getItem('token') || '')
    const role = ref(localStorage.getItem('role') || '')
    const username = ref('')

    const getUserInfo = async () => {
        try {
            const { data } = await http.get('/users/me')
            role.value = data.role
            username.value = data.username
            // Persist role for basic route guards (optional, but good for UX)
            localStorage.setItem('role', data.role)
            return data
        } catch (error) {
            console.error('Failed to get user info', error)
            throw error
        }
    }

    const logout = () => {
        token.value = ''
        role.value = ''
        username.value = ''
        localStorage.removeItem('token')
        localStorage.removeItem('role')
    }

    return {
        token,
        role,
        username,
        getUserInfo,
        logout
    }
})
