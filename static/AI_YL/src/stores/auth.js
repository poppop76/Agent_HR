import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

// 检查JWT是否过期
function isTokenExpired(token) {
  if (!token) return true
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return true
    const payload = JSON.parse(atob(parts[1]))
    if (payload.exp) {
      const now = Math.floor(Date.now() / 1000)
      return payload.exp < now
    }
    return false
  } catch (e) {
    return true
  }
}

export const useAuthStore = defineStore('auth', () => {
  const savedToken = localStorage.getItem('token') || ''
  const savedUserInfo = localStorage.getItem('userInfo')
  
  // 如果token过期，清除本地存储
  if (savedToken && isTokenExpired(savedToken)) {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }
  
  const token = ref(localStorage.getItem('token') || '')
  const userInfoStr = localStorage.getItem('userInfo')
  const userInfo = ref(userInfoStr && userInfoStr !== 'undefined' ? JSON.parse(userInfoStr) : {})

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value.role === 'admin')
  const userName = computed(() => userInfo.value.name || '')
  const userRole = computed(() => userInfo.value.role || '')

  // 调用后端真实登录接口
  async function login(loginData) {
    const res = await authApi.login(loginData)
    token.value = res.data.token
    userInfo.value = res.data.user
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('userInfo', JSON.stringify(res.data.user))
    return res
  }

  function logout() {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    userName,
    userRole,
    login,
    logout
  }
})
