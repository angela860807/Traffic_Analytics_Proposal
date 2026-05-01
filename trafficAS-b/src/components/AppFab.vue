<template>
  <div class="fab-wrap">
    <button class="fab" @click="goChat" title="채팅">💬</button>
    <button class="fab" @click="toggle" :title="isDark?'라이트 모드':'다크 모드'">
      {{ isDark ? '☀️' : '🌙' }}
    </button>
    <button class="fab" @click="top" title="맨 위로">↑</button>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
const { isDark, toggle } = useTheme()
const router = useRouter()
const top    = () => window.scrollTo({ top:0, behavior:'smooth' })
const goChat = () => router.push('/sub/support?tab=chat')
</script>
<style scoped>
.fab-wrap{position:fixed;bottom:28px;right:28px;z-index:300;display:flex;flex-direction:column;gap:9px}
.fab{width:46px;height:46px;border-radius:50%;background:var(--nav);backdrop-filter:blur(16px);
  border:1px solid var(--b);display:flex;align-items:center;justify-content:center;
  cursor:pointer;font-size:17px;color:var(--t2);transition:all .2s}
.fab:hover{border-color:var(--ba);transform:scale(1.08);box-shadow:0 4px 20px var(--glow)}
</style>
