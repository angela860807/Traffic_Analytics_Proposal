<template>
  <div class="appnav-line"></div>
  <nav class="appnav">
    <div class="ni">
      <RouterLink to="/" class="logo">
        <span class="ls"></span>
        Traffic<em>AS</em>
      </RouterLink>
      <div class="links">
        <RouterLink to="/sub/usage">사용법</RouterLink>
        <RouterLink to="/sub/intro">시스템 소개</RouterLink>
        <RouterLink to="/sub/support">고객 지원</RouterLink>
      </div>
      <div class="right">
        <template v-if="isLoggedIn">
          <span class="uname">{{ currentUser?.name || currentUser?.email?.split('@')[0] }}님 좋은하루되세요</span>
          <RouterLink v-if="isAdmin" to="/dashboard" class="btn-dash">대시보드</RouterLink>
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
import { useAuth } from "@/composables/useAuth";

const { isLoggedIn, isAdmin, currentUser, logout } = useAuth();
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
  font-size: 14px;
  letter-spacing: 0.02em;
  color: var(--t3);
  transition: color 0.2s;
  white-space: nowrap;
}
.links a:hover {
  color: var(--t);
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
  font-size: 13.5px;
  color: var(--t2);
  letter-spacing: 0.02em;
  white-space: nowrap;
}
.btn-login {
  display: inline-flex;
  align-items: center;
  padding: 8px 18px;
  background: none;
  border: 1px solid var(--b);
  border-radius: 6px;
  color: var(--t2);
  font-size: 13.5px;
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
  color: var(--t3);
  font-size: 13.5px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-out:hover {
  border-color: #f87171;
  color: #f87171;
}
@media (max-width: 768px) {
  .ni {
    padding: 0 16px;
  }
  .links a {
    padding: 0 10px;
    font-size: 12.5px;
  }
}
</style>
