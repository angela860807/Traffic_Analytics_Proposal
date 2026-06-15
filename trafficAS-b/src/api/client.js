import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 5000,
})

function genRequestId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  // 폴백 — UUIDv4 흉내 (보안 목적 아님)
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('tas_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  // 백엔드 API 계약 §2-1: 모든 요청에 X-Request-Id
  if (!config.headers['X-Request-Id']) {
    config.headers['X-Request-Id'] = genRequestId()
  }
  return config
})

// 에러 응답을 일관된 형태로 정규화
// 백엔드 §2-3 shape: { timestamp, status, code, message, requestId, fieldErrors }
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const res = error.response
    const data = res?.data || {}
    const normalized = {
      status: res?.status ?? 0,
      code: data.code || (res?.status === 401 ? 'UNAUTHORIZED'
        : res?.status === 403 ? 'FORBIDDEN'
        : res?.status === 404 ? 'RESOURCE_NOT_FOUND'
        : res?.status === 409 ? 'CONFLICT'
        : 'NETWORK_ERROR'),
      message: data.message || error.message || '요청 처리 중 오류가 발생했습니다.',
      requestId: data.requestId || res?.headers?.['x-request-id'] || '',
      fieldErrors: Array.isArray(data.fieldErrors) ? data.fieldErrors : [],
      timestamp: data.timestamp || new Date().toISOString(),
      raw: error,
    }
    error.normalized = normalized
    return Promise.reject(error)
  },
)

export async function apiGet(path, config) {
  const response = await apiClient.get(path, config)
  return response.data
}

export async function apiPatch(path, data, config) {
  const response = await apiClient.patch(path, data, config)
  return response.data
}

export async function apiPost(path, data, config) {
  const response = await apiClient.post(path, data, config)
  return response.data
}

// fieldErrors를 { 필드명: 메시지 } 맵으로 변환
export function fieldErrorMap(normalized) {
  const map = {}
  for (const fe of normalized?.fieldErrors || []) {
    if (fe?.field) map[fe.field] = fe.reason || ''
  }
  return map
}
