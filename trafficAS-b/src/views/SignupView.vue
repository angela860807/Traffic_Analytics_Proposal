<template>
  <div class="theme-navy" :class="{light:!isDark}">
    <div class="wrap">

      <!-- 왼쪽 브랜딩 패널 -->
      <div class="left">
        <div class="left-inner">
          <RouterLink to="/" class="logo">
            <span class="ls"></span>Traffic<em>AS</em>
          </RouterLink>
          <div class="brand-copy">
            <div class="ey">JOIN TRAFFICIAS</div>
            <h1>교통 데이터의<br>새로운 기준을<br><em>경험하세요.</em></h1>
            <p>회원가입 후 실시간 차량 감지 대시보드와<br>AI 분석 리포트를 이용할 수 있습니다.</p>
          </div>
          <div class="steps">
            <div class="step" v-for="(s,i) in steps" :key="i">
              <div class="snum">0{{ i+1 }}</div>
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
            <div class="prog-step" :class="{on: step>=1, done: step>1}">
              <span>1</span><small>기본 정보</small>
            </div>
            <div class="prog-line" :class="{on: step>1}"></div>
            <div class="prog-step" :class="{on: step>=2}">
              <span>2</span><small>보안 설정</small>
            </div>
          </div>

          <form @submit.prevent="handleSubmit" class="form" novalidate>

            <!-- Step 1 -->
            <template v-if="step===1">
              <div class="field" :class="{focused: focus==='name', filled: name}">
                <label>이름</label>
                <div class="input-wrap">
                  <span class="iico">👤</span>
                  <input
                    v-model="name" type="text" placeholder="이름을 입력하세요"
                    autocomplete="name"
                    @focus="focus='name'" @blur="focus=''"
                  />
                </div>
              </div>

              <div class="field" :class="{focused: focus==='email', filled: email}">
                <label>이메일</label>
                <div class="input-wrap">
                  <span class="iico">✉</span>
                  <input
                    v-model="email" type="email" placeholder="example@email.com"
                    autocomplete="email"
                    @focus="focus='email'" @blur="focus=''"
                  />
                </div>
              </div>

              <Transition name="err">
                <p v-if="error" class="err">⚠ {{ error }}</p>
              </Transition>

              <button type="button" class="submit" @click="nextStep">
                다음 단계 <span class="arr">→</span>
              </button>
            </template>

            <!-- Step 2 -->
            <template v-else>
              <div class="back-step" @click="step=1">← 이전으로</div>

              <div class="user-preview">
                <div class="up-av">{{ name.charAt(0) }}</div>
                <div>
                  <div class="up-name">{{ name }}</div>
                  <div class="up-email">{{ email }}</div>
                </div>
              </div>

              <div class="field" :class="{focused: focus==='pw', filled: password}">
                <label>비밀번호 <span class="req">6자 이상</span></label>
                <div class="input-wrap">
                  <span class="iico">🔒</span>
                  <input
                    v-model="password" :type="showPw ? 'text' : 'password'"
                    placeholder="6자 이상 입력"
                    autocomplete="new-password"
                    @focus="focus='pw'" @blur="focus=''"
                  />
                  <button type="button" class="eye" @click="showPw=!showPw">
                    {{ showPw ? '🙈' : '👁' }}
                  </button>
                </div>
                <div class="pw-bar" v-if="password">
                  <div class="pw-fill" :style="{width: pwStrength+'%'}" :class="pwClass"></div>
                </div>
                <span class="pw-hint" v-if="password" :class="pwClass">{{ pwLabel }}</span>
              </div>

              <div class="field" :class="{focused: focus==='confirm', filled: confirm}">
                <label>비밀번호 확인</label>
                <div class="input-wrap" :class="{match: confirm && confirm===password, mismatch: confirm && confirm!==password}">
                  <span class="iico">🔑</span>
                  <input
                    v-model="confirm" :type="showPw ? 'text' : 'password'"
                    placeholder="비밀번호 재입력"
                    autocomplete="new-password"
                    @focus="focus='confirm'" @blur="focus=''"
                  />
                  <span v-if="confirm" class="match-ico">{{ confirm===password ? '✓' : '✗' }}</span>
                </div>
              </div>

              <Transition name="err">
                <p v-if="error" class="err">⚠ {{ error }}</p>
              </Transition>

              <button type="submit" class="submit" :class="{loading}">
                <span v-if="!loading">회원가입 완료 <span class="arr">→</span></span>
                <span v-else class="spin">⟳</span>
              </button>
            </template>
          </form>

          <div class="divider"><span>또는</span></div>
          <p class="switch">이미 계정이 있으신가요? <RouterLink to="/login">로그인하기</RouterLink></p>
          <p class="back"><RouterLink to="/">← 메인 페이지로</RouterLink></p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import { useAuth } from '@/composables/useAuth'

const { isDark } = useTheme()
const { signup } = useAuth()
const router     = useRouter()

const step     = ref(1)
const name     = ref('')
const email    = ref('')
const password = ref('')
const confirm  = ref('')
const error    = ref('')
const focus    = ref('')
const showPw   = ref(false)
const loading  = ref(false)

const pwStrength = computed(() => {
  const p = password.value
  if (!p) return 0
  let s = 0
  if (p.length >= 6)  s += 25
  if (p.length >= 10) s += 25
  if (/[A-Z]/.test(p) || /[0-9]/.test(p)) s += 25
  if (/[^a-zA-Z0-9]/.test(p)) s += 25
  return s
})
const pwClass = computed(() => {
  if (pwStrength.value <= 25) return 'weak'
  if (pwStrength.value <= 50) return 'fair'
  if (pwStrength.value <= 75) return 'good'
  return 'strong'
})
const pwLabel = computed(() => ({weak:'취약',fair:'보통',good:'양호',strong:'강함'}[pwClass.value]))

const nextStep = () => {
  error.value = ''
  if (!name.value.trim()) { error.value = '이름을 입력하세요.'; return }
  if (!email.value.trim()) { error.value = '이메일을 입력하세요.'; return }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) { error.value = '올바른 이메일 형식을 입력하세요.'; return }
  step.value = 2
}

const handleSubmit = async () => {
  error.value = ''
  if (password.value.length < 6) { error.value = '비밀번호는 6자 이상이어야 합니다.'; return }
  if (password.value !== confirm.value) { error.value = '비밀번호가 일치하지 않습니다.'; return }
  loading.value = true
  await new Promise(r => setTimeout(r, 700))
  try {
    signup(name.value, email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const steps = [
  { t: '계정 생성',   d: '이름과 이메일로 간단하게 가입하세요.' },
  { t: '대시보드 접근', d: '실시간 차량 데이터를 모니터링하세요.' },
  { t: 'AI 리포트',   d: '시간대별 교통 분석 리포트를 확인하세요.' },
]
</script>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1fr; min-height: 100vh; }

/* ── 왼쪽 패널 ── */
.left {
  position: relative; overflow: hidden;
  background: linear-gradient(145deg, #020b18 0%, #051628 60%, #020b18 100%);
  display: flex; align-items: stretch;
}
.left-grid {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(96,165,250,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(96,165,250,.04) 1px, transparent 1px);
  background-size: 52px 52px;
}
.left-glow {
  position: absolute; bottom: 20%; right: -5%; width: 55%; aspect-ratio: 1;
  background: radial-gradient(circle, rgba(96,165,250,.1) 0%, transparent 70%);
  pointer-events: none;
}
.left-inner {
  position: relative; z-index: 1;
  display: flex; flex-direction: column;
  padding: 48px 56px; width: 100%;
}
.logo {
  font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 800;
  letter-spacing: -.4px; color: #fff;
  display: flex; align-items: center; gap: 10px; text-decoration: none;
  margin-bottom: auto;
}
.logo em { color: #60a5fa; font-style: normal; }
.ls {
  width: 8px; height: 8px; border-radius: 50%; background: #60a5fa;
  box-shadow: 0 0 10px #60a5fa; animation: livePulse 2s ease-in-out infinite;
}
.brand-copy { margin: auto 0; }
.ey {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  letter-spacing: .22em; color: #60a5fa; opacity: .7;
  margin-bottom: 20px; display: flex; align-items: center; gap: 8px;
}
.ey::before { content: ''; width: 18px; height: 1px; background: #60a5fa; opacity: .5; }
h1 {
  font-family: 'Syne', sans-serif;
  font-size: clamp(30px, 3.2vw, 50px); font-weight: 800;
  line-height: .96; letter-spacing: -2.5px; color: #fff; margin-bottom: 20px;
}
h1 em { color: #60a5fa; font-style: normal; }
.brand-copy p { font-size: 13px; color: rgba(255,255,255,.45); line-height: 1.85; font-weight: 300; }

.steps { margin-top: 40px; display: flex; flex-direction: column; gap: 0; }
.step { display: flex; gap: 14px; padding: 16px 0; border-bottom: 1px solid rgba(255,255,255,.06); }
.step:last-child { border-bottom: none; }
.snum { font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; letter-spacing: -1px; color: rgba(96,165,250,.12); line-height: 1; flex-shrink: 0; width: 38px; }
.st { font-size: 13px; font-weight: 600; color: rgba(255,255,255,.65); margin-bottom: 3px; }
.sd { font-size: 11px; color: rgba(255,255,255,.3); line-height: 1.6; font-weight: 300; }

.left-foot {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  color: rgba(255,255,255,.2); letter-spacing: .08em; margin-top: 40px;
}

/* ── 오른쪽 패널 ── */
.right {
  background: var(--bg);
  display: flex; align-items: center; justify-content: center;
  padding: 60px 40px; overflow-y: auto;
}
.form-wrap { width: 100%; max-width: 400px; }
.form-ey {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  letter-spacing: .22em; color: var(--a); opacity: .65;
  margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}
.form-ey::before { content: ''; width: 14px; height: 1px; background: var(--a); opacity: .5; }
h2 {
  font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 800;
  letter-spacing: -1.2px; color: var(--t); margin-bottom: 6px;
}
.form-sub { font-size: 13px; color: var(--t2); font-weight: 300; margin-bottom: 28px; }

/* 진행 단계 */
.progress { display: flex; align-items: center; gap: 0; margin-bottom: 28px; }
.prog-step {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  opacity: .35; transition: opacity .3s;
}
.prog-step.on { opacity: 1; }
.prog-step span {
  width: 28px; height: 28px; border-radius: 50%;
  border: 2px solid var(--b); background: var(--bg2);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: var(--t2);
  transition: all .3s;
}
.prog-step.on span { border-color: var(--a); color: var(--a); background: rgba(96,165,250,.08); }
.prog-step.done span { background: var(--a); color: var(--bg); border-color: var(--a); }
.prog-step small { font-size: 9px; color: var(--t3); letter-spacing: .05em; white-space: nowrap; }
.prog-line { flex: 1; height: 1px; background: var(--b); margin: 0 8px 14px; transition: background .3s; }
.prog-line.on { background: var(--a); }

.back-step {
  font-size: 12px; color: var(--t3); cursor: pointer;
  display: inline-flex; align-items: center; gap: 4px;
  transition: color .2s; margin-bottom: 16px;
}
.back-step:hover { color: var(--t); }

.user-preview {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; background: var(--bg2);
  border: 1px solid var(--b); border-radius: 8px; margin-bottom: 20px;
}
.up-av {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--a); color: var(--bg);
  font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 800;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.up-name { font-size: 13px; font-weight: 600; color: var(--t); }
.up-email { font-size: 11px; color: var(--t3); margin-top: 2px; }

.form { display: flex; flex-direction: column; gap: 16px; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field label {
  font-size: 11px; font-weight: 600; letter-spacing: .06em;
  color: var(--t2); text-transform: uppercase;
  display: flex; align-items: center; gap: 6px;
}
.req { font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: var(--t3); text-transform: none; letter-spacing: .04em; }

.input-wrap {
  display: flex; align-items: center;
  background: var(--bg2); border: 1px solid var(--b);
  border-radius: 8px; overflow: hidden;
  transition: border-color .2s, box-shadow .2s;
}
.field.focused .input-wrap {
  border-color: var(--a);
  box-shadow: 0 0 0 3px rgba(96,165,250,.1);
}
.input-wrap.match { border-color: #34d399; box-shadow: 0 0 0 3px rgba(52,211,153,.08); }
.input-wrap.mismatch { border-color: #f87171; box-shadow: 0 0 0 3px rgba(248,113,113,.08); }
.iico { padding: 0 12px; font-size: 14px; opacity: .4; flex-shrink: 0; }
input {
  flex: 1; padding: 12px 0; background: none; border: none;
  font-size: 13px; color: var(--t); outline: none;
}
input::placeholder { color: var(--t3); }
.eye {
  padding: 0 12px; background: none; border: none;
  cursor: pointer; font-size: 14px; opacity: .4; transition: opacity .2s;
}
.eye:hover { opacity: .8; }
.match-ico { padding: 0 12px; font-size: 13px; font-weight: 700; }
.input-wrap.match .match-ico { color: #34d399; }
.input-wrap.mismatch .match-ico { color: #f87171; }

/* 비밀번호 강도 */
.pw-bar { height: 3px; background: var(--b); border-radius: 2px; overflow: hidden; margin-top: 4px; }
.pw-fill { height: 100%; border-radius: 2px; transition: width .3s, background .3s; }
.pw-fill.weak   { background: #f87171; }
.pw-fill.fair   { background: #fbbf24; }
.pw-fill.good   { background: #34d399; }
.pw-fill.strong { background: var(--a); }
.pw-hint { font-size: 10px; }
.pw-hint.weak   { color: #f87171; }
.pw-hint.fair   { color: #fbbf24; }
.pw-hint.good   { color: #34d399; }
.pw-hint.strong { color: var(--a); }

.err-enter-active, .err-leave-active { transition: opacity .2s, transform .2s; }
.err-enter-from, .err-leave-to { opacity: 0; transform: translateY(-4px); }
.err { font-size: 12px; color: #f87171; margin: 0; padding: 8px 12px; background: rgba(248,113,113,.08); border: 1px solid rgba(248,113,113,.2); border-radius: 6px; }

.submit {
  width: 100%; padding: 13px; margin-top: 6px;
  background: var(--a); color: var(--bg);
  border: none; border-radius: 8px;
  font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700;
  cursor: pointer; transition: opacity .2s, transform .15s;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}
.submit:hover:not(.loading) { opacity: .88; transform: translateY(-1px); }
.submit.loading { opacity: .7; cursor: not-allowed; }
.arr { transition: transform .2s; }
.submit:hover .arr { transform: translateX(3px); }
.spin { display: inline-block; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.divider {
  display: flex; align-items: center; gap: 12px;
  margin: 24px 0; color: var(--t3); font-size: 11px;
}
.divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: var(--b); }

.switch { font-size: 13px; color: var(--t2); text-align: center; margin: 0 0 12px; }
.switch a { color: var(--a); font-weight: 600; text-decoration: none; }
.switch a:hover { text-decoration: underline; }
.back { font-size: 12px; color: var(--t3); text-align: center; margin: 0; }
.back a { color: var(--t3); text-decoration: none; transition: color .2s; }
.back a:hover { color: var(--t); }

@media (max-width: 768px) {
  .wrap { grid-template-columns: 1fr; }
  .left { display: none; }
  .right { padding: 40px 24px; }
}
</style>
