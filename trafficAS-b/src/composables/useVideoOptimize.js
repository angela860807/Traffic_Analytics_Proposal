import { onMounted, onUnmounted, watch } from 'vue'

/**
 * 비디오 자동 최적화 컴포저블
 *
 * 1. Page Visibility — 브라우저 탭 비활성화 시 모든 비디오 일시정지
 * 2. IntersectionObserver — 뷰포트 밖 비디오 자동 정지
 * 3. active prop watch — 컴포넌트 비활성(v-show=false) 시 일시정지
 *
 * 사용:
 *   useVideoOptimize({ active: () => activeTab.value === 'monitoring' })
 *   // 또는 props.active를 reactive하게 전달
 *
 * @param {Object} opts
 * @param {() => boolean} [opts.active]  컴포넌트 활성 상태 (false면 비디오 정지)
 * @param {string} [opts.selector='video']  대상 비디오 셀렉터
 */
export function useVideoOptimize(opts = {}) {
  const { active, selector = 'video' } = opts
  let io = null

  const videos = () => document.querySelectorAll(selector)
  const pauseAll = () => videos().forEach(v => v.pause())
  const resumeVisible = () => videos().forEach(v => {
    const r = v.getBoundingClientRect()
    if (r.top < innerHeight && r.bottom > 0) v.play().catch(() => {})
  })

  const onVisibility = () => {
    if (document.hidden) pauseAll()
    else if (!active || active()) resumeVisible()
  }

  onMounted(() => {
    setTimeout(() => {
      io = new IntersectionObserver(es => es.forEach(e => {
        if (e.isIntersecting && (!active || active())) e.target.play().catch(() => {})
        else e.target.pause()
      }), { threshold: 0.1 })
      videos().forEach(v => io.observe(v))
    }, 300)
    document.addEventListener('visibilitychange', onVisibility)
  })

  if (active) {
    watch(active, v => v ? resumeVisible() : pauseAll())
  }

  onUnmounted(() => {
    io?.disconnect()
    document.removeEventListener('visibilitychange', onVisibility)
    pauseAll()
  })
}
