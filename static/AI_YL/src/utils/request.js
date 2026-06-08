import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: '/hr/api/v1',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const aiAxios = axios.create({
  baseURL: '/hr/api/v1',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

aiAxios.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

const handleResponse = (response) => {
  return response.data
}

const handleError = (error) => {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        const authStore = useAuthStore()
        authStore.logout()
        window.location.href = '/login'
        break
      case 403:
        ElMessage.error('没有权限访问')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 500:
        ElMessage.error('服务器错误')
        break
      default:
        ElMessage.error(error.response.data.message || error.response.data.msg || '请求失败')
    }
  } else if (error.code === 'ECONNABORTED') {
    ElMessage.error('请求超时，请稍后重试')
  } else {
    ElMessage.error('网络连接失败')
  }
  return Promise.reject(error)
}

api.interceptors.response.use(handleResponse, handleError)
aiAxios.interceptors.response.use(handleResponse, handleError)

export { api, aiAxios }
export default api
