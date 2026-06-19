// 30초 polling + 탭 비활성 시 중단 + 폴링 실패 시 stale 표시
// 백엔드 §6: polling 실패 시 기존 데이터를 지우지 않고 stale 상태로 표시한다.

import { ref, onMounted, onBeforeUnmount } from 'vue'

export function usePolling(fetcher, { intervalMs = 30000, immediate = true } = {}) {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const stale = ref(false)
  const lastUpdatedAt = ref(null)

  let timer = null
  let inFlight = false
  let stopped = false

  async function run() {
    if (inFlight || stopped) return
    inFlight = true
    if (!data.value) loading.value = true
    try {
      const result = await fetcher()
      if (stopped) return
      data.value = result
      error.value = null
      stale.value = false
      lastUpdatedAt.value = new Date()
    } catch (err) {
      if (stopped) return
      error.value = err?.normalized || { code: 'NETWORK_ERROR', message: err?.message || '요청 실패' }
      // 기존 data는 유지 — stale 표시만
      if (data.value) stale.value = true
    } finally {
      inFlight = false
      loading.value = false
    }
  }

  function schedule() {
    clear()
    if (document.visibilityState !== 'visible') return
    timer = setInterval(run, intervalMs)
  }

  function clear() {
    if (timer) clearInterval(timer)
    timer = null
  }

  function onVisibility() {
    if (document.visibilityState === 'visible') {
      run()       // 복귀 시 즉시 1회
      schedule()
    } else {
      clear()
    }
  }

  onMounted(() => {
    document.addEventListener('visibilitychange', onVisibility)
    if (immediate) run()
    schedule()
  })

  onBeforeUnmount(() => {
    stopped = true
    document.removeEventListener('visibilitychange', onVisibility)
    clear()
  })

  return {
    data, loading, error, stale, lastUpdatedAt,
    refresh: run,
    stop: () => { stopped = true; clear() },
  }
}
