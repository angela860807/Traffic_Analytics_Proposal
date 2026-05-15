import { ref } from 'vue'
/* 라이트 모드 고정 — 다크 모드 제거 */
const isDark = ref(false)
export function useTheme() {
  const toggle = () => { /* noop — 라이트 모드 고정 */ }
  return { isDark, toggle }
}
