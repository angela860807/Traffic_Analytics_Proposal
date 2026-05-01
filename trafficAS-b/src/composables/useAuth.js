import { ref, computed } from 'vue'

const _user = ref(JSON.parse(localStorage.getItem('tas_user') || 'null'))
const _showModal = ref(false)
const _modalMode = ref('login')

export function useAuth() {
  const isLoggedIn  = computed(() => !!_user.value)
  const currentUser = computed(() => _user.value)
  const showModal   = _showModal
  const modalMode   = _modalMode

  const openLogin  = () => { _modalMode.value = 'login';  _showModal.value = true }
  const openSignup = () => { _modalMode.value = 'signup'; _showModal.value = true }
  const closeModal = () => { _showModal.value = false }

  const signup = (name, email, password) => {
    const stored = JSON.parse(localStorage.getItem('tas_users') || '[]')
    if (stored.find(u => u.email === email)) throw new Error('이미 사용 중인 이메일입니다.')
    stored.push({ name, email, password })
    localStorage.setItem('tas_users', JSON.stringify(stored))
    const user = { name, email }
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

  return { isLoggedIn, currentUser, showModal, modalMode, openLogin, openSignup, closeModal, signup, login, logout }
}
