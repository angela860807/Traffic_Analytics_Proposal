<template>
  <RouterView />
  <AuthModal />
</template>

<script setup>
import { RouterView } from 'vue-router'
import { onMounted, onBeforeUnmount } from 'vue'
import AuthModal from '@/components/AuthModal.vue'

/* ── 빔프로젝터 시연 모드 (Ctrl + Shift + D) ── */
const DEMO_KEY = 'tas_demo_mode'

function applyDemoMode(on) {
  document.body.classList.toggle('demo-mode', on)
  try { localStorage.setItem(DEMO_KEY, on ? '1' : '0') } catch {}
}

function toggleDemoMode() {
  const now = document.body.classList.contains('demo-mode')
  applyDemoMode(!now)
  /* 토스트로 상태 표시 */
  const toast = document.createElement('div')
  toast.textContent = `🎯 시연 모드 ${!now ? 'ON (115% 확대)' : 'OFF'}`
  toast.style.cssText = `
    position: fixed; top: 80px; left: 50%; transform: translateX(-50%);
    background: rgba(37,99,235,0.95); color: #fff;
    padding: 12px 22px; border-radius: 100px;
    font-family: "Pretendard Variable", sans-serif;
    font-size: 14px; font-weight: 700; letter-spacing: -0.2px;
    z-index: 99999; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    pointer-events: none; transition: opacity 0.3s;
  `
  document.body.appendChild(toast)
  setTimeout(() => { toast.style.opacity = '0' }, 1400)
  setTimeout(() => toast.remove(), 1800)
}

function onKey(e) {
  /* Ctrl + Shift + D — 시연 모드 토글 */
  if (e.ctrlKey && e.shiftKey && (e.key === 'D' || e.key === 'd')) {
    e.preventDefault()
    toggleDemoMode()
  }
}

onMounted(() => {
  /* 새로고침해도 마지막 상태 복원 */
  try {
    if (localStorage.getItem(DEMO_KEY) === '1') {
      document.body.classList.add('demo-mode')
    }
  } catch {}
  window.addEventListener('keydown', onKey)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
})
</script>
