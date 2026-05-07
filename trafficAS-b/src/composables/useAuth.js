import { ref, computed } from 'vue'

const _user = ref(JSON.parse(localStorage.getItem('tas_user') || 'null'))
const _showModal = ref(false)
const _modalMode = ref('login')

const ADMIN_EMAIL = 'admin@trafficAS.com'
const ADMIN_PW    = 'admin1234'

// 관리자 계정 항상 최신 상태로 동기화
;(() => {
  const stored = JSON.parse(localStorage.getItem('tas_users') || '[]')
  const idx = stored.findIndex(u => u.email === ADMIN_EMAIL)
  const admin = { name: '관리자', email: ADMIN_EMAIL, phone: '', password: ADMIN_PW }
  if (idx === -1) stored.push(admin)
  else stored[idx] = admin
  localStorage.setItem('tas_users', JSON.stringify(stored))
})()

export function useAuth() {
  const isLoggedIn  = computed(() => !!_user.value)
  const currentUser = computed(() => _user.value)
  const isAdmin     = computed(() => _user.value?.email === ADMIN_EMAIL)
  const showModal   = _showModal
  const modalMode   = _modalMode

  const openLogin  = () => { _modalMode.value = 'login';  _showModal.value = true }
  const openSignup = () => { _modalMode.value = 'signup'; _showModal.value = true }
  const closeModal = () => { _showModal.value = false }

  const signup = (name, email, phone, password) => {
    const stored = JSON.parse(localStorage.getItem('tas_users') || '[]')
    if (stored.find(u => u.email === email)) throw new Error('이미 사용 중인 이메일입니다.')
    stored.push({ name, email, phone, password })
    localStorage.setItem('tas_users', JSON.stringify(stored))
    const user = { name, email, phone }
    localStorage.setItem('tas_user', JSON.stringify(user))
    _user.value = user
  }

  const login = (email, password) => {
    const stored = JSON.parse(localStorage.getItem('tas_users') || '[]')
    const found  = stored.find(u => u.email === email && u.password === password)
    if (!found) throw new Error('이메일 또는 비밀번호가 올바르지 않습니다.')
    const user = { name: found.name, email: found.email }
    localStorage.setItem('tas_user', JSON.stringify(user))
    _user.value = user
  }

  const logout = () => {
    localStorage.removeItem('tas_user')
    _user.value = null
  }

  return { isLoggedIn, isAdmin, currentUser, showModal, modalMode, openLogin, openSignup, closeModal, signup, login, logout }
}
