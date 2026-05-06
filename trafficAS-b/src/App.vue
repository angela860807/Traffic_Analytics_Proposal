<template>
  <RouterView />
  <AuthModal />

  <!-- 관리자 대시보드 버튼 -->
  <Transition name="dash-btn">
    <RouterLink
      v-if="isAdmin"
      to="/dashboard"
      class="dash-fab"
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="1.8"
        stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="7" height="7"/>
        <rect x="14" y="3" width="7" height="7"/>
        <rect x="14" y="14" width="7" height="7"/>
        <rect x="3" y="14" width="7" height="7"/>
      </svg>
      <span>대시보드</span>
    </RouterLink>
  </Transition>
</template>

<script setup>
import { RouterView, RouterLink } from 'vue-router'
import AuthModal                  from '@/components/AuthModal.vue'
import { useAuth }                from '@/composables/useAuth'

const { isAdmin } = useAuth()
</script>

<style>
.dash-fab {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px 10px 14px;
  background: rgba(6, 10, 22, 0.92);
  border: 1px solid rgba(62, 201, 214, 0.40);
  color: rgba(62, 201, 214, 0.85);
  text-decoration: none;
  font-size: 12px;
  font-family: 'IBM Plex Mono', monospace;
  letter-spacing: 0.08em;
  border-radius: 4px;
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
  transition: border-color 0.2s, color 0.2s, box-shadow 0.2s, transform 0.15s;
  white-space: nowrap;
  cursor: pointer;
}
.dash-fab svg {
  flex-shrink: 0;
  opacity: 0.75;
  transition: opacity 0.2s;
}
.dash-fab:hover {
  border-color: rgba(62, 201, 214, 0.75);
  color: #3ec9d6;
  box-shadow: 0 4px 28px rgba(0, 0, 0, 0.45), 0 0 16px rgba(62, 201, 214, 0.18);
  transform: translateY(-2px);
}
.dash-fab:hover svg { opacity: 1; }

/* 등장 애니메이션 */
.dash-btn-enter-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.dash-btn-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.dash-btn-enter-from   { opacity: 0; transform: translateY(12px); }
.dash-btn-leave-to     { opacity: 0; transform: translateY(8px); }
</style>