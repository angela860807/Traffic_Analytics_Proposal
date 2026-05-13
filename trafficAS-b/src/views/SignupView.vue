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
            <div class="ey">JOIN TRAFFICIAS</div>
            <h1>교통 데이터의<br />새로운 기준을<br /><em>경험하세요.</em></h1>
            <p>
              회원가입 후 실시간 차량 감지 대시보드와<br />AI 분석 리포트를 이용할 수
              있습니다.
            </p>
          </div>
          <div class="steps">
            <div class="step" v-for="(s, i) in steps" :key="i">
              <div class="snum">0{{ i + 1 }}</div>
              <div>
                <div class="st">{{ s.t }}</div>
                <div class="sd">{{ s.d }}</div>
              </div>
            </div>
          </div>
          <div class="left-foot">© 2025 네바퀴 1조 · 스마트 모빌리티 DX Academy</div>
        </div>
        <div class="left-grid"></div>
        <div class="left-glow"></div>
      </div>

      <!-- 오른쪽 폼 패널 -->
      <div class="right">
        <div class="form-wrap">
          <div class="form-ey">CREATE ACCOUNT</div>
          <h2>회원가입</h2>
          <p class="form-sub">TrafficAS 계정을 만들어보세요.</p>

          <!-- 진행 단계 표시 -->
          <div class="progress">
            <div class="prog-step" :class="{ on: step >= 1, done: step > 1 }">
              <span>
                <svg
                  v-if="step > 1"
                  xmlns="http://www.w3.org/2000/svg"
                  width="11"
                  height="11"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <template v-else>1</template>
              </span>
              <small>기본 정보</small>
            </div>
            <div class="prog-line" :class="{ on: step > 1 }"></div>
            <div class="prog-step" :class="{ on: step >= 2 }">
              <span>2</span><small>보안 설정</small>
            </div>
          </div>

          <form @submit.prevent="handleSubmit" class="form" novalidate>
            <!-- Step 1 -->
            <template v-if="step === 1">
              <!-- 이름 -->
              <div class="field" :class="{ focused: focus === 'name', filled: name }">
                <label>이름</label>
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
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                  </span>
                  <input
                    v-model="name"
                    type="text"
                    placeholder="이름을 입력하세요"
                    autocomplete="name"
                    @focus="focus = 'name'"
                    @blur="focus = ''"
                  />
                </div>
              </div>

              <!-- 연락처 -->
              <div class="field" :class="{ focused: focus === 'phone', filled: phone }">
                <label>연락처</label>
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
                      <path
                        d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.58 3.38 2 2 0 0 1 3.56 1.18h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 8.91a16 16 0 0 0 6 6l.81-.81a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21.73 16.92z"
                      />
                    </svg>
                  </span>
                  <input
                    v-model="phone"
                    type="tel"
                    placeholder="010-0000-0000"
                    autocomplete="tel"
                    @input="phone = formatPhone($event.target.value)"
                    @focus="focus = 'phone'"
                    @blur="focus = ''"
                  />
                </div>
              </div>

              <!-- 이메일 + 중복확인 -->
              <div class="field" :class="{ focused: focus === 'email', filled: email }">
                <label>
                  이메일
                  <span class="req">아이디로 사용됩니다</span>
                </label>
                <div class="email-row">
                  <div
                    class="input-wrap"
                    :class="{
                      'check-ok': emailCheck === 'ok',
                      'check-fail': emailCheck === 'taken',
                    }"
                  >
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
                      @input="emailCheck = null"
                      @focus="focus = 'email'"
                      @blur="focus = ''"
                    />
                    <span class="email-ico" v-if="emailCheck">
                      <svg
                        v-if="emailCheck === 'ok'"
                        xmlns="http://www.w3.org/2000/svg"
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      <svg
                        v-else
                        xmlns="http://www.w3.org/2000/svg"
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </span>
                  </div>
                  <button
                    type="button"
                    class="check-btn"
                    @click="checkDuplicate"
                    :disabled="!email.trim() || emailChecking"
                  >
                    <svg
                      v-if="emailChecking"
                      class="spin-sm"
                      xmlns="http://www.w3.org/2000/svg"
                      width="11"
                      height="11"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                    </svg>
                    <span v-else>중복 확인</span>
                  </button>
                </div>
                <p class="check-msg ok" v-if="emailCheck === 'ok'">
                  사용 가능한 이메일입니다.
                </p>
                <p class="check-msg taken" v-if="emailCheck === 'taken'">
                  이미 사용 중인 이메일입니다.
                </p>
              </div>

              <Transition name="err">
                <p v-if="error" class="err">{{ error }}</p>
              </Transition>

              <button type="button" class="submit" @click="nextStep">
                다음 단계 <span class="arr">→</span>
              </button>
            </template>

            <!-- Step 2 -->
            <template v-else>
              <div class="back-step" @click="step = 1">← 이전으로</div>

              <div class="user-preview">
                <div class="up-av">{{ name.charAt(0) }}</div>
                <div class="up-info">
                  <div class="up-name">{{ name }}</div>
                  <div class="up-sub">{{ email }}</div>
                  <div class="up-sub">{{ phone }}</div>
                </div>
              </div>

              <!-- 비밀번호 -->
              <div class="field" :class="{ focused: focus === 'pw', filled: password }">
                <label>비밀번호 <span class="req">4자 이상</span></label>
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
                    placeholder="4자 이상 입력"
                    autocomplete="new-password"
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
                <div class="pw-bar" v-if="password">
                  <div
                    class="pw-fill"
                    :style="{ width: pwStrength + '%' }"
                    :class="pwClass"
                  ></div>
                </div>
                <span class="pw-hint" v-if="password" :class="pwClass">{{
                  pwLabel
                }}</span>
              </div>

              <!-- 비밀번호 확인 -->
              <div
                class="field"
                :class="{ focused: focus === 'confirm', filled: confirm }"
              >
                <label>비밀번호 확인</label>
                <div
                  class="input-wrap"
                  :class="{
                    match: confirm && confirm === password,
                    mismatch: confirm && confirm !== password,
                  }"
                >
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
                      <circle cx="7.5" cy="15.5" r="5.5" />
                      <path d="m21 2-9.6 9.6" />
                      <path d="m15.5 7.5 3 3L22 7l-3-3" />
                    </svg>
                  </span>
                  <input
                    v-model="confirm"
                    :type="showPw ? 'text' : 'password'"
                    placeholder="비밀번호 재입력"
                    autocomplete="new-password"
                    @focus="focus = 'confirm'"
                    @blur="focus = ''"
                  />
                  <span v-if="confirm" class="match-ico">
                    <svg
                      v-if="confirm === password"
                      xmlns="http://www.w3.org/2000/svg"
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="3"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                    <svg
                      v-else
                      xmlns="http://www.w3.org/2000/svg"
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="3"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </span>
                </div>
              </div>

              <Transition name="err">
                <p v-if="error" class="err">{{ error }}</p>
              </Transition>

              <button type="submit" class="submit" :class="{ loading }">
                <span v-if="!loading">회원가입 완료 <span class="arr">→</span></span>
                <span v-else class="spin">⟳</span>
              </button>
            </template>
          </form>

          <div class="divider"><span>또는</span></div>
          <p class="switch">
            이미 계정이 있으신가요? <RouterLink to="/login">로그인하기</RouterLink>
          </p>
          <p class="back"><RouterLink to="/">← 메인 페이지로</RouterLink></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { useTheme } from "@/composables/useTheme";
import { useAuth } from "@/composables/useAuth";

const { isDark } = useTheme();
const { signup } = useAuth();
const router = useRouter();

const step = ref(1);
const name = ref("");
const phone = ref("");
const email = ref("");
const emailCheck = ref(null); // null | 'ok' | 'taken'
const emailChecking = ref(false);
const password = ref("");
const confirm = ref("");
const error = ref("");
const focus = ref("");
const showPw = ref(false);
const loading = ref(false);

function formatPhone(val) {
  const d = val.replace(/\D/g, "").slice(0, 11);
  if (d.length <= 3) return d;
  if (d.length <= 7) return `${d.slice(0, 3)}-${d.slice(3)}`;
  return `${d.slice(0, 3)}-${d.slice(3, 7)}-${d.slice(7)}`;
}

function checkDuplicate() {
  const val = email.value.trim();
  if (!val || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
    error.value = "올바른 이메일 형식을 입력하세요.";
    return;
  }
  emailChecking.value = true;
  setTimeout(() => {
    const stored = JSON.parse(localStorage.getItem("tas_users") || "[]");
    emailCheck.value = stored.find((u) => u.email === val) ? "taken" : "ok";
    emailChecking.value = false;
  }, 400);
}

const pwStrength = computed(() => {
  const p = password.value;
  if (!p) return 0;
  let s = 0;
  if (p.length >= 4) s += 25;
  if (p.length >= 10) s += 25;
  if (/[A-Z]/.test(p) || /[0-9]/.test(p)) s += 25;
  if (/[^a-zA-Z0-9]/.test(p)) s += 25;
  return s;
});
const pwClass = computed(() => {
  if (pwStrength.value <= 25) return "weak";
  if (pwStrength.value <= 50) return "fair";
  if (pwStrength.value <= 75) return "good";
  return "strong";
});
const pwLabel = computed(
  () => ({ weak: "취약", fair: "보통", good: "양호", strong: "강함" }[pwClass.value])
);

const nextStep = () => {
  error.value = "";
  if (!name.value.trim()) {
    error.value = "이름을 입력하세요.";
    return;
  }
  if (!phone.value.trim() || phone.value.replace(/\D/g, "").length < 10) {
    error.value = "올바른 연락처를 입력하세요.";
    return;
  }
  if (!email.value.trim()) {
    error.value = "이메일을 입력하세요.";
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    error.value = "올바른 이메일 형식을 입력하세요.";
    return;
  }
  if (emailCheck.value !== "ok") {
    error.value = "이메일 중복 확인을 해주세요.";
    return;
  }
  step.value = 2;
};

const handleSubmit = async () => {
  error.value = "";
  if (password.value.length < 4) {
    error.value = "비밀번호는 4자 이상이어야 합니다.";
    return;
  }
  if (password.value !== confirm.value) {
    error.value = "비밀번호가 일치하지 않습니다.";
    return;
  }
  loading.value = true;
  await new Promise((r) => setTimeout(r, 700));
  try {
    await signup(name.value, email.value, phone.value, password.value);
    router.push("/");
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

const steps = [
  { t: "계정 생성", d: "이름과 이메일로 간단하게 가입하세요." },
  { t: "대시보드 접근", d: "실시간 차량 데이터를 모니터링하세요." },
  { t: "AI 리포트", d: "시간대별 교통 분석 리포트를 확인하세요." },
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
  bottom: 20%;
  right: -5%;
  width: 55%;
  aspect-ratio: 1;
  background: radial-gradient(circle, rgba(96, 165, 250, 0.1) 0%, transparent 70%);
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
  font-family: "Pretendard Variable", Pretendard, sans-serif;
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
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
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
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: clamp(30px, 3.2vw, 50px);
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
  font-size: 15px;
  color: rgba(255, 255, 255, 0.45);
  line-height: 1.85;
  font-weight: 300;
}
.steps {
  margin-top: 40px;
  display: flex;
  flex-direction: column;
  gap: 0;
}
.step {
  display: flex;
  gap: 14px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.step:last-child {
  border-bottom: none;
}
.snum {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -1px;
  color: rgba(96, 165, 250, 0.12);
  line-height: 1;
  flex-shrink: 0;
  width: 38px;
}
.st {
  font-size: 14.5px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.65);
  margin-bottom: 3px;
}
.sd {
  font-size: 12.5px;
  color: rgba(255, 255, 255, 0.3);
  line-height: 1.6;
  font-weight: 300;
}
.left-foot {
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  color: rgba(255, 255, 255, 0.2);
  letter-spacing: 0.08em;
  margin-top: 40px;
}

/* ── 오른쪽 패널 ── */
.right {
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  overflow-y: auto;
}
.form-wrap {
  width: 100%;
  max-width: 400px;
}
.form-ey {
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
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
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -1.2px;
  color: var(--t);
  margin-bottom: 6px;
}
.form-sub {
  font-size: 14.5px;
  color: var(--t2);
  font-weight: 300;
  margin-bottom: 28px;
}

/* 진행 단계 */
.progress {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 28px;
}
.prog-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  opacity: 0.35;
  transition: opacity 0.3s;
}
.prog-step.on {
  opacity: 1;
}
.prog-step span {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--b);
  background: var(--bg2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--t2);
  transition: all 0.3s;
}
.prog-step.on span {
  border-color: var(--a);
  color: var(--a);
  background: rgba(96, 165, 250, 0.08);
}
.prog-step.done span {
  background: var(--a);
  color: var(--bg);
  border-color: var(--a);
}
.prog-step small {
  font-size: 9px;
  color: var(--t3);
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.prog-line {
  flex: 1;
  height: 1px;
  background: var(--b);
  margin: 0 8px 14px;
  transition: background 0.3s;
}
.prog-line.on {
  background: var(--a);
}

.back-step {
  font-size: 12px;
  color: var(--t3);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: color 0.2s;
  margin-bottom: 16px;
}
.back-step:hover {
  color: var(--t);
}

.user-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 8px;
  margin-bottom: 20px;
}
.up-av {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--a);
  color: var(--bg);
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 14px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.up-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.up-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--t);
}
.up-sub {
  font-size: 11px;
  color: var(--t3);
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
  font-size: 12.5px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--t2);
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 6px;
}
.req {
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  color: var(--t3);
  text-transform: none;
  letter-spacing: 0.04em;
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
.input-wrap.match {
  border-color: #34d399;
  box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.08);
}
.input-wrap.mismatch {
  border-color: #f87171;
  box-shadow: 0 0 0 3px rgba(248, 113, 113, 0.08);
}
.input-wrap.check-ok {
  border-color: #34d399;
}
.input-wrap.check-fail {
  border-color: #f87171;
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
  font-size: 14.5px;
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
.match-ico {
  padding: 0 12px;
  display: flex;
  align-items: center;
}
.input-wrap.match .match-ico {
  color: #34d399;
}
.input-wrap.mismatch .match-ico {
  color: #f87171;
}

/* 이메일 중복 확인 */
.email-row {
  display: flex;
  gap: 8px;
  align-items: stretch;
}
.email-row .input-wrap {
  flex: 1;
}
.email-ico {
  padding: 0 12px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.input-wrap.check-ok .email-ico {
  color: #34d399;
}
.input-wrap.check-fail .email-ico {
  color: #f87171;
}
.check-btn {
  padding: 0 14px;
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 8px;
  font-family: "JetBrains Mono", monospace;
  font-size: 10px;
  color: var(--t2);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}
.check-btn:hover:not(:disabled) {
  border-color: var(--ba);
  color: var(--a);
}
.check-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.spin-sm {
  animation: spin 0.9s linear infinite;
}
.check-msg {
  font-size: 11px;
  margin: 0;
}
.check-msg.ok {
  color: #34d399;
}
.check-msg.taken {
  color: #f87171;
}

/* 비밀번호 강도 */
.pw-bar {
  height: 3px;
  background: var(--b);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 4px;
}
.pw-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s, background 0.3s;
}
.pw-fill.weak {
  background: #f87171;
}
.pw-fill.fair {
  background: #fbbf24;
}
.pw-fill.good {
  background: #34d399;
}
.pw-fill.strong {
  background: var(--a);
}
.pw-hint {
  font-size: 10px;
}
.pw-hint.weak {
  color: #f87171;
}
.pw-hint.fair {
  color: #fbbf24;
}
.pw-hint.good {
  color: #34d399;
}
.pw-hint.strong {
  color: var(--a);
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
  font-family: "Pretendard Variable", Pretendard, sans-serif;
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
