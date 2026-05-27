import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 5000,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('tas_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function apiGet(path, config) {
  const response = await apiClient.get(path, config)
  return response.data
}

export async function apiPatch(path, data, config) {
  const response = await apiClient.patch(path, data, config)
  return response.data
}
