<template>
  <div class="top-line"></div>
  <nav>
    <div class="ni">
      <RouterLink to="/" class="logo">
        <span class="ls"></span>
        Traffic<em>AS</em>
      </RouterLink>
      <div class="links">
        <RouterLink to="/sub#usage">사용법</RouterLink>
        <RouterLink to="/sub#intro">시스템 소개</RouterLink>
        <RouterLink to="/sub#support">고객 지원</RouterLink>
      </div>
      <div class="right">
        <span class="nbadge">네바퀴 1조</span>
        <button class="chat-btn" @click="$emit('goChat')">
          <span class="cdot"></span>채팅
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink } from 'vue-router'
defineEmits(['goChat'])
</script>

<style scoped>
.top-line{position:fixed;top:0;left:0;right:0;height:2px;z-index:201;
  background:linear-gradient(90deg,transparent,var(--a) 30%,var(--a) 70%,transparent);opacity:.55}
nav{position:fixed;top:2px;left:0;right:0;z-index:200;height:60px;
  background:var(--nav);backdrop-filter:blur(22px);border-bottom:1px solid var(--b)}
.ni{max-width:1440px;margin:0 auto;height:100%;display:flex;align-items:center;padding:0 44px}
.logo{font-family:'Syne',sans-serif;font-size:17px;font-weight:800;letter-spacing:-.4px;
  color:var(--t);display:flex;align-items:center;gap:9px;margin-right:32px;white-space:nowrap}
.logo em{color:var(--a);font-style:normal}
.ls{width:7px;height:7px;border-radius:50%;background:var(--a);
  box-shadow:0 0 8px var(--a);flex-shrink:0;animation:livePulse 2s ease-in-out infinite}
.links{display:flex;height:60px;align-items:stretch;flex:1}
.links a{display:flex;align-items:center;padding:0 14px;font-size:12px;letter-spacing:.04em;
  color:var(--t3);border-bottom:2px solid transparent;transition:color .2s,border-color .2s;white-space:nowrap}
.links a:hover{color:var(--t);border-bottom-color:var(--a)}
.links a.router-link-exact-active{color:var(--a);border-bottom-color:var(--a)}
.right{margin-left:auto;display:flex;align-items:center;gap:10px}
.nbadge{font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.12em;
  color:var(--t3);padding:4px 10px;border:1px solid var(--b);border-radius:100px}
.chat-btn{display:flex;align-items:center;gap:7px;padding:8px 18px;
  background:var(--a);color:var(--bg);font-family:'Syne',sans-serif;
  font-size:12px;font-weight:700;letter-spacing:.04em;border-radius:6px;
  cursor:pointer;border:none;transition:opacity .2s,transform .15s}
.chat-btn:hover{opacity:.87;transform:translateY(-1px)}
.cdot{width:5px;height:5px;border-radius:50%;background:var(--bg);animation:livePulse 1.5s ease-in-out infinite}
@media(max-width:768px){.ni{padding:0 16px}.links a{padding:0 9px;font-size:11px}}
</style>
