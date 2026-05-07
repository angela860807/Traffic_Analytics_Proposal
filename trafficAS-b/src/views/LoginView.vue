<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <div class="wrap">
      <!-- 왼쪽 브랜딩 패널 -->
      <div class="left">
        <div class="left-inner">
          <RouterLink to="/" class="logo">
            <span class="ls"></span>Traffic<em>AS</em>
          </RouterLink>
          <div class="brand-copy">
            <div class="ey">AI-POWERED TRAFFIC SYSTEM</div>
            <h1>차량이 움직이는<br />모든 순간을<br /><em>포착합니다.</em></h1>
            <p>YOLO 기반 실시간 차량 감지와<br />번호판 OCR로 교통 흐름을 분석합니다.</p>
          </div>
          <ul class="feats">
            <li v-for="f in feats" :key="f"><span class="fdot"></span>{{ f }}</li>
          </ul>
          <div class="left-foot">© 2025 네바퀴 1조 · 스마트 모빌리티 DX Academy</div>
        </div>
        <div class="left-grid"></div>
        <div class="left-glow"></div>
      </div>

      <!-- 오른쪽 폼 패널 -->
      <div class="right">
        <div class="form-wrap">
          <div class="form-ey">AUTHENTICATION</div>
          <h2>로그인</h2>
          <p class="form-sub">TrafficAS 계정으로 로그인하세요.</p>

          <form @submit.prevent="handleLogin" class="form" novalidate>
            <div class="field" :class="{ focused: focus === 'email', filled: email }">
              <label>이메일</label>
              <div class="input-wrap">
                <span class="iico">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                </span>
                <input
                  v-model="email"
                  type="email"
                  placeholder="example@email.com"
                  autocomplete="email"
                  @focus="focus = 'email'"
                  @blur="focus = ''"
                />
              </div>
            </div>

            <div class="field" :class="{ focused: focus === 'pw', filled: password }">
              <label>비밀번호</label>
              <div class="input-wrap">
                <span class="iico">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <rect x="3" y="11" width="18" height="11" rx="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </span>
                <input
                  v-model="password"
                  :type="showPw ? 'text' : 'password'"
                  placeholder="비밀번호 입력"
                  autocomplete="current-password"
                  @focus="focus = 'pw'"
                  @blur="focus = ''"
                />
                <button type="button" class="eye" @click="showPw = !showPw">
                  <svg
                    v-if="showPw"
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                    <path
                      d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"
                    />
                    <path
                      d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"
                    />
                    <line x1="2" y1="2" x2="22" y2="22" />
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
              </div>
            </div>

            <Transition name="err">
              <p v-if="error" class="err">{{ error }}</p>
            </Transition>

            <button type="submit" class="submit" :class="{ loading }">
              <span v-if="!loading">로그인 <span class="arr">→</span></span>
              <span v-else class="spin">⟳</span>
            </button>
          </form>

          <div class="divider"><span>또는</span></div>

          <p class="switch">
            계정이 없으신가요? <RouterLink to="/signup">회원가입하기</RouterLink>
          </p>
          <p class="back"><RouterLink to="/">← 메인 페이지로</RouterLink></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { useTheme } from "@/composables/useTheme";
import { useAuth } from "@/composables/useAuth";

const { isDark } = useTheme();
const { login, isAdmin } = useAuth();
const router = useRouter();

const email = ref("");
const password = ref("");
const error = ref("");
const focus = ref("");
const showPw = ref(false);
const loading = ref(false);

const handleLogin = async () => {
  error.value = "";
  if (!email.value || !password.value) {
    error.value = "이메일과 비밀번호를 입력하세요.";
    return;
  }
  loading.value = true;
  await new Promise((r) => setTimeout(r, 600));
  try {
    login(email.value, password.value);
    router.push(isAdmin.value ? '/dashboard' : '/');
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

const feats = [
  "실시간 차량 감지 및 분류",
  "OCR 번호판 자동 인식 96% 정확도",
  "50ms 이내 실시간 대시보드 반영",
  "구역별 유입·유출 통계 대시보드",
];
</script>

<style scoped>
.wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
}

/* ── 왼쪽 패널 ── */
.left {
  position: relative;
  overflow: hidden;
  background: linear-gradient(145deg, #020b18 0%, #051628 60%, #020b18 100%);
  display: flex;
  align-items: stretch;
}
.left-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image: linear-gradient(rgba(96, 165, 250, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(96, 165, 250, 0.04) 1px, transparent 1px);
  background-size: 52px 52px;
}
.left-glow {
  position: absolute;
  top: 30%;
  left: -10%;
  width: 60%;
  aspect-ratio: 1;
  background: radial-gradient(circle, rgba(96, 165, 250, 0.12) 0%, transparent 70%);
  pointer-events: none;
}
.left-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  padding: 48px 56px;
  width: 100%;
}
.logo {
  font-family: "Syne", sans-serif;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.4px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  margin-bottom: auto;
}
.logo em {
  color: #60a5fa;
  font-style: normal;
}
.ls {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #60a5fa;
  box-shadow: 0 0 10px #60a5fa;
  animation: livePulse 2s ease-in-out infinite;
}
.brand-copy {
  margin: auto 0;
}
.ey {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.22em;
  color: #60a5fa;
  opacity: 0.7;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ey::before {
  content: "";
  width: 18px;
  height: 1px;
  background: #60a5fa;
  opacity: 0.5;
}
h1 {
  font-family: "Syne", sans-serif;
  font-size: clamp(30px, 3.2vw, 52px);
  font-weight: 800;
  line-height: 0.96;
  letter-spacing: -2.5px;
  color: #fff;
  margin-bottom: 20px;
}
h1 em {
  color: #60a5fa;
  font-style: normal;
}
.brand-copy p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  line-height: 1.85;
  font-weight: 300;
}
.feats {
  list-style: none;
  padding: 0;
  margin: 40px 0 0;
  display: flex;
  flex-direction: column;
  gap: 11px;
}
.feats li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}
.fdot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #60a5fa;
  opacity: 0.6;
  flex-shrink: 0;
}
.left-foot {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  color: rgba(255, 255, 255, 0.2);
  letter-spacing: 0.08em;
  margin-top: 48px;
}

/* ── 오른쪽 패널 ── */
.right {
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
}
.form-wrap {
  width: 100%;
  max-width: 380px;
}
.form-ey {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.22em;
  color: var(--a);
  opacity: 0.65;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.form-ey::before {
  content: "";
  width: 14px;
  height: 1px;
  background: var(--a);
  opacity: 0.5;
}
h2 {
  font-family: "Syne", sans-serif;
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -1.2px;
  color: var(--t);
  margin-bottom: 6px;
}
.form-sub {
  font-size: 13px;
  color: var(--t2);
  font-weight: 300;
  margin-bottom: 36px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--t2);
  text-transform: uppercase;
}
.input-wrap {
  display: flex;
  align-items: center;
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.field.focused .input-wrap {
  border-color: var(--a);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}
.iico {
  padding: 0 12px;
  display: flex;
  align-items: center;
  color: var(--t3);
  flex-shrink: 0;
}
input {
  flex: 1;
  padding: 12px 0;
  background: none;
  border: none;
  font-size: 13px;
  color: var(--t);
  outline: none;
}
input::placeholder {
  color: var(--t3);
}
.eye {
  padding: 0 12px;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: var(--t3);
  transition: color 0.2s;
}
.eye:hover {
  color: var(--t);
}

.err-enter-active,
.err-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.err-enter-from,
.err-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
.err {
  font-size: 12px;
  color: #f87171;
  margin: 0;
  padding: 8px 12px;
  background: rgba(248, 113, 113, 0.08);
  border: 1px solid rgba(248, 113, 113, 0.2);
  border-radius: 6px;
}

.submit {
  width: 100%;
  padding: 13px;
  margin-top: 6px;
  background: var(--a);
  color: var(--bg);
  border: none;
  border-radius: 8px;
  font-family: "Syne", sans-serif;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.submit:hover:not(.loading) {
  opacity: 0.88;
  transform: translateY(-1px);
}
.submit.loading {
  opacity: 0.7;
  cursor: not-allowed;
}
.arr {
  transition: transform 0.2s;
}
.submit:hover .arr {
  transform: translateX(3px);
}
.spin {
  display: inline-block;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 24px 0;
  color: var(--t3);
  font-size: 11px;
}
.divider::before,
.divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--b);
}

.switch {
  font-size: 13px;
  color: var(--t2);
  text-align: center;
  margin: 0 0 12px;
}
.switch a {
  color: var(--a);
  font-weight: 600;
  text-decoration: none;
}
.switch a:hover {
  text-decoration: underline;
}
.back {
  font-size: 12px;
  color: var(--t3);
  text-align: center;
  margin: 0;
}
.back a {
  color: var(--t3);
  text-decoration: none;
  transition: color 0.2s;
}
.back a:hover {
  color: var(--t);
}

@media (max-width: 768px) {
  .wrap {
    grid-template-columns: 1fr;
  }
  .left {
    display: none;
  }
  .right {
    padding: 40px 24px;
  }
}
</style>
