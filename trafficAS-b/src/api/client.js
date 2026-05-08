const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export async function apiGet(path) {
  const token = localStorage.getItem('tas_access_token')

  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })

  if (!res.ok) throw new Error(`API error: ${res.status}`)

  return res.json()
}
