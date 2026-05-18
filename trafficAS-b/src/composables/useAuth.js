import { ref, computed } from 'vue'
import router from '@/router/index.js'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/* 인증 상태 변경 후 홈으로 안전하게 이동 (라우터 미초기화 시 무시) */
function goHome() {
  try { router.push('/') } catch {}
}

const _user = ref(JSON.parse(localStorage.getItem('tas_user') || 'null'))
const _showModal = ref(false)
const _modalMode = ref('login')

function parseJwtPayload(token) {
  if (!token) return {}

  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((char) => `%${(`00${char.charCodeAt(0).toString(16)}`).slice(-2)}`)
        .join('')
    )
    return JSON.parse(json)
  } catch {
    return {}
  }
}

async function readApiBody(res) {
  const text = await res.text()
  if (!text) return {}

  try {
    return JSON.parse(text)
  } catch {
    return { message: text }
  }
}

export function useAuth() {
  const isLoggedIn = computed(() => !!_user.value)
  const currentUser = computed(() => _user.value)
  const isAdmin = computed(() => _user.value?.role === 'ADMIN')
  const showModal = _showModal
  const modalMode = _modalMode

  const openLogin = () => { _modalMode.value = 'login'; _showModal.value = true }
  const openSignup = () => { _modalMode.value = 'signup'; _showModal.value = true }
  const closeModal = () => { _showModal.value = false }

  const signup = async (name, email, phone, password) => {
    const res = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone, password }),
    })
    const body = await readApiBody(res)

    if (!res.ok || body.success === false) {
      throw new Error(body.message || '회원가입에 실패했습니다.')
    }

    const user = body.data
    localStorage.setItem('tas_user', JSON.stringify(user))
    _user.value = user
    closeModal()
    goHome()
    return user
  }

  // ── 프론트 임시 계정 (백엔드 미연동 시 시연용) ──
  const LOCAL_ACCOUNTS = [
    { email: 'admin@local',   password: 'admin',  name: '임시 관리자', role: 'ADMIN' },
    { email: 'user@local',    password: 'user',   name: '임시 사용자', role: 'USER'  },
  ]

  const login = async (email, password) => {
    // 1) 프론트 임시 계정 우선 체크 (백엔드 없이 즉시 통과)
    const local = LOCAL_ACCOUNTS.find(a => a.email === email && a.password === password)
    if (local) {
      const user = { email: local.email, role: local.role, name: local.name }
      localStorage.setItem('tas_access_token', 'local-' + Date.now())
      localStorage.setItem('tas_user', JSON.stringify(user))
      _user.value = user
      closeModal()
      goHome()
      return user
    }

    // 2) 백엔드 정상 로그인
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const body = await readApiBody(res)

    if (!res.ok || body.success === false) {
      throw new Error(body.message || '이메일 또는 비밀번호가 올바르지 않습니다.')
    }

    const token = body.data?.accessToken
    const payload = parseJwtPayload(token)
    const role = payload.auth === 'ROLE_ADMIN' ? 'ADMIN' : 'USER'
    const user = { email: payload.sub || email, role }

    localStorage.setItem('tas_access_token', token)
    localStorage.setItem('tas_refresh_token', body.data?.refreshToken || '')
    localStorage.setItem('tas_user', JSON.stringify(user))
    _user.value = user
    closeModal()
    goHome()
    return user
  }

  const logout = () => {
    localStorage.removeItem('tas_access_token')
    localStorage.removeItem('tas_refresh_token')
    localStorage.removeItem('tas_user')
    _user.value = null
    goHome()
  }

  return { isLoggedIn, isAdmin, currentUser, showModal, modalMode, openLogin, openSignup, closeModal, signup, login, logout }
}
