import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const data = error.response?.data
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      ElMessage.error('登录已过期，请重新登录')
    } else if (status === 403) {
      ElMessage.error('您没有执行该操作的权限')
    } else {
      const msg = data?.detail || (typeof data === 'object' ? Object.values(data).flat().join('；') : null)
      ElMessage.error(msg || '请求失败，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default request
