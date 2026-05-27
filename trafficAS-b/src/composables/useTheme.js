import { ref } from 'vue'
const isDark = ref(false)
export function useTheme() {
  const toggle = () => {}
  return { isDark, toggle }
}
