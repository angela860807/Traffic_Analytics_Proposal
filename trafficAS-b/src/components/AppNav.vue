<template>
  <div class="appnav-line"></div>
  <nav class="appnav">
    <div class="ni">
      <RouterLink to="/" class="logo">
        <img src="/TAS.png" alt="TAS" class="logo-img" />
      </RouterLink>
      <div class="links">
        <RouterLink to="/sub/intro">시스템 소개</RouterLink>
        <RouterLink to="/sub/support">공지사항</RouterLink>
      </div>
      <div class="right">
        <template v-if="isLoggedIn">
          <span class="uname">{{ currentUser?.name || currentUser?.email?.split('@')[0] }}님 좋은하루되세요</span>
          <div v-if="isAdmin" class="admin-menu" ref="menuRef">
            <button class="btn-admin" @click.stop="open = !open">
              관제 시스템 <i class="bi bi-chevron-down"></i>
            </button>
            <div v-if="open" class="admin-pop">
              <RouterLink to="/admin/super"     class="ap-i" @click="open = false"><i class="bi bi-shield-shaded"></i><div><strong>경영전략본부</strong><span>전사 통합 · KPI · 보고</span></div></RouterLink>
              <div class="ap-sep"></div>
              <RouterLink to="/admin/control"   class="ap-i" @click="open = false"><i class="bi bi-bullseye"></i><div><strong>교통정보센터</strong><span>실시간 관제 · 이벤트</span></div></RouterLink>
              <RouterLink to="/admin/review"    class="ap-i" @click="open = false"><i class="bi bi-check2-square"></i><div><strong>단속관리팀</strong><span>위반 검토 · 판정</span></div></RouterLink>
              <RouterLink to="/admin/analytics" class="ap-i" @click="open = false"><i class="bi bi-bar-chart"></i><div><strong>교통분석팀</strong><span>구간 · 시간대 분석</span></div></RouterLink>
              <RouterLink to="/admin/ops"       class="ap-i" @click="open = false"><i class="bi bi-hdd-rack"></i><div><strong>시설운영팀</strong><span>카메라 · 서버 · 네트워크</span></div></RouterLink>
            </div>
          </div>
          <button class="btn-out" @click="logout">로그아웃</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="btn-login">로그인</RouterLink>
          <RouterLink to="/signup" class="btn-signup">회원가입</RouterLink>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink } from "vue-router";
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useAuth } from "@/composables/useAuth";

const { isLoggedIn, isAdmin, currentUser, logout } = useAuth();
const open = ref(false);
const menuRef = ref(null);
const onDocClick = (e) => {
  if (!open.value) return;
  if (menuRef.value && !menuRef.value.contains(e.target)) open.value = false;
};
onMounted(() => document.addEventListener("click", onDocClick));
onBeforeUnmount(() => document.removeEventListener("click", onDocClick));
</script>

<style scoped>
.ni {
  max-width: 1440px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 44px;
}
.logo {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 19px;
  font-weight: 800;
  letter-spacing: -0.4px;
  color: var(--t);
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}
.logo-img {
  height: 56px;
  width: auto;
  display: block;
  margin-right: 32px;
  white-space: nowrap;
  text-decoration: none;
}
.logo em {
  color: var(--a);
  font-style: normal;
}
.ls {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--a);
  box-shadow: 0 0 8px var(--a);
  flex-shrink: 0;
  animation: livePulse 2s ease-in-out infinite;
}
.links {
  display: flex;
  height: 66px;
  align-items: stretch;
  flex: 1;
}
.links a {
  display: flex;
  align-items: center;
  padding: 0 16px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.01em;
  color: var(--t);
  transition: color 0.2s;
  white-space: nowrap;
}
.links a:hover {
  color: var(--a);
}
.links a.router-link-active {
  color: var(--a);
}
.right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}
.uname {
  font-size: 14px;
  font-weight: 600;
  color: var(--t);
  letter-spacing: 0.01em;
  white-space: nowrap;
}
.btn-login {
  display: inline-flex;
  align-items: center;
  padding: 8px 18px;
  background: none;
  border: 1px solid var(--b);
  border-radius: 6px;
  color: var(--t);
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  white-space: nowrap;
  text-decoration: none;
}
.btn-login:hover {
  border-color: var(--ba);
  color: var(--t);
}
.btn-signup {
  display: inline-flex;
  align-items: center;
  padding: 8px 18px;
  background: var(--a);
  border: none;
  border-radius: 6px;
  color: var(--bg);
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 13.5px;
  font-weight: 700;
  transition: opacity 0.2s, transform 0.15s;
  white-space: nowrap;
  text-decoration: none;
}
.btn-signup:hover {
  opacity: 0.87;
  transform: translateY(-1px);
}
.btn-dash {
  display: inline-flex;
  align-items: center;
  padding: 8px 18px;
  background: var(--a);
  border: none;
  border-radius: 6px;
  color: var(--bg);
  font-size: 13.5px;
  font-weight: 700;
  transition: opacity 0.2s, transform 0.15s;
  white-space: nowrap;
  text-decoration: none;
}
.btn-dash:hover { opacity: 0.87; transform: translateY(-1px); }
.btn-out {
  padding: 8px 18px;
  background: none;
  border: 1px solid var(--b);
  border-radius: 6px;
  color: var(--t);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-out:hover {
  border-color: #f87171;
  color: #f87171;
}
.admin-menu { position: relative; }
.btn-admin {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px;
  background: var(--a); color: var(--bg);
  border: 0; border-radius: 6px;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 14px; font-weight: 700;
  cursor: pointer; white-space: nowrap;
  transition: opacity 0.18s;
}
.btn-admin:hover { opacity: 0.9; }
.btn-admin i { font-size: 11px; }
.admin-pop {
  position: absolute; top: calc(100% + 8px); right: 0;
  min-width: 290px;
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 10px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.2);
  padding: 6px;
  z-index: 250;
}
.theme-navy.light .admin-pop { background: #fff; box-shadow: 0 18px 50px rgba(15, 40, 90, 0.15); }
.ap-i {
  display: flex; align-items: center; gap: 14px;
  padding: 12px 14px;
  border-radius: 6px;
  color: var(--t); text-decoration: none;
  transition: background 0.15s;
}
.ap-i:hover { background: rgba(96, 165, 250, 0.08); }
.theme-navy.light .ap-i:hover { background: rgba(37, 99, 235, 0.06); }
.ap-i > i {
  width: 32px; height: 32px; border-radius: 8px;
  background: rgba(96, 165, 250, 0.12);
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--a); font-size: 16px; flex-shrink: 0;
}
.theme-navy.light .ap-i > i { background: rgba(37, 99, 235, 0.1); }
.ap-i > div { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.ap-i strong { font-size: 15px; font-weight: 700; }
.ap-i span { font-size: 12.5px; opacity: 0.78; }
.theme-navy.light .ap-i span { color: rgba(12,31,64,.78); opacity: 1; }
.theme-navy.light .ap-i strong { color: #0c1f40; }
.ap-sep { height: 1px; background: var(--b); margin: 4px 8px; }

@media (max-width: 768px) {
  .ni { padding: 0 16px; }
  .links a { padding: 0 10px; font-size: 12.5px; }
}
</style>
