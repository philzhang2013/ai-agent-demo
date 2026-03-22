import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/api/types'
import { authAPI } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)

  // 初始化：从 localStorage 恢复
  function init() {
    const savedToken = authAPI.getToken()
    const savedUser = authAPI.getUser()

    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = savedUser
    }
  }

  // 注册
  async function register(username: string, password: string) {
    isLoading.value = true
    try {
      const response = await authAPI.register({ username, password })
      user.value = response.user
      token.value = response.token
      authAPI.saveAuth(response)
      return response
    } finally {
      isLoading.value = false
    }
  }

  // 登录
  async function login(username: string, password: string) {
    isLoading.value = true
    try {
      const response = await authAPI.login({ username, password })
      user.value = response.user
      token.value = response.token
      authAPI.saveAuth(response)
      return response
    } finally {
      isLoading.value = false
    }
  }

  // 退出登录
  function logout() {
    user.value = null
    token.value = null
    authAPI.logout()
  }

  // 检查是否已登录
  function isAuthenticated(): boolean {
    return !!token.value
  }

  return {
    user,
    token,
    isLoading,
    init,
    register,
    login,
    logout,
    isAuthenticated
  }
})
