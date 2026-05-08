# 🔧 TrafficAS — 트러블슈팅 가이드

개발 및 운영 중 발생한 주요 문제와 해결 방법을 정리한 문서입니다.

---

## 목차

1. [대시보드 접근 불가 (로그인 후에도 이동 안됨)](#1-대시보드-접근-불가)
2. [관리자 계정 로그인 실패](#2-관리자-계정-로그인-실패)
3. [알림이 누적되지 않는 문제](#3-알림이-누적되지-않는-문제)
4. [WebSocket 연결 실패](#4-websocket-연결-실패)
5. [Canvas 차트가 표시되지 않음](#5-canvas-차트가-표시되지-않음)
6. [탭 전환 시 하단 공백 발생](#6-탭-전환-시-하단-공백-발생)
7. [다크모드에서 UI 요소가 안 보이는 문제](#7-다크모드에서-ui-요소가-안-보이는-문제)
8. [AI 채팅 영어/한자 혼재 응답](#8-ai-채팅-영어한자-혼재-응답)
9. [라이트모드 숫자(01, 02) 안 보이는 문제](#9-라이트모드-숫자-안-보이는-문제)
10. [빌드 오류 — provide is not defined](#10-빌드-오류--provide-is-not-defined)

---

## 1. 대시보드 접근 불가

### 증상
로그인 후 `/dashboard`로 직접 이동해도 메인 페이지로 튕겨나옴.

### 원인
Vue Router 네비게이션 가드에서 비관리자 계정 접근을 차단.  
일반 사용자 계정으로 로그인한 경우 대시보드 접근 불가.

### 해결 방법
관리자 계정으로 로그인해야 합니다.

```
이메일 : admin@trafficAS.com
비밀번호 : admin1234
```

### 관련 코드
`src/router/index.js`

```js
router.beforeEach((to) => {
  if (to.path === '/dashboard') {
    const { isLoggedIn, isAdmin } = useAuth()
    if (!isLoggedIn.value) return '/login'
    if (!isAdmin.value)    return '/'
  }
})
```

---

## 2. 관리자 계정 로그인 실패

### 증상
`admin@trafficAS.com` / `admin1234` 로 로그인 시 "계정 정보가 맞지 않습니다" 오류 발생.

### 원인
`useAuth.js`의 관리자 계정 초기화 IIFE가 기존 데이터를 덮어쓰지 않고 조건부로만 추가하여, localStorage에 잘못된 패스워드로 저장된 관리자 데이터가 남아있으면 갱신되지 않음.

### 해결 방법
`src/composables/useAuth.js`에서 `findIndex`로 기존 항목을 찾아 **항상 덮어쓰도록** 수정:

```js
;(() => {
  const stored = JSON.parse(localStorage.getItem('tas_users') || '[]')
  const idx = stored.findIndex(u => u.email === ADMIN_EMAIL)
  const admin = { name: '관리자', email: ADMIN_EMAIL, phone: '', password: ADMIN_PW }
  if (idx === -1) stored.push(admin)
  else stored[idx] = admin          // 항상 최신 비밀번호로 덮어쓰기
  localStorage.setItem('tas_users', JSON.stringify(stored))
})()
```

### 즉시 해결
브라우저 개발자 도구 → Application → LocalStorage → `tas_users` 키 삭제 후 새로고침.

---

## 3. 알림이 누적되지 않는 문제

### 증상
도로 혼잡이 감지되어 팝업 알림은 뜨지만, 알림 탭에 내역이 쌓이지 않음.

### 원인
`watch`가 `pushNotif()` (팝업 큐)만 호출하고, `alerts` 배열에 실제로 push하지 않음.  
또한 같은 구간에서 중복 알림 방지 로직이 없어 dismiss 후에도 재등록이 안됨.

### 해결 방법
`src/views/DashboardView.vue` watch 수정:

```js
watch(() => segments.map(s => s.spd), () => {
  segments.forEach(seg => {
    if (seg.spd < thresholds.congSpeed) {
      const exists = alerts.find(a => a.title === `${seg.name} 혼잡 감지`)
      if (!exists) {
        const n = new Date()
        const t = `${String(n.getHours()).padStart(2,'0')}:${String(n.getMinutes()).padStart(2,'0')}`
        alerts.unshift({
          id: Date.now() + Math.random(), lv: 'H',
          title: `${seg.name} 혼잡 감지`,
          desc: `평균 속도 ${Math.round(seg.spd)}km/h — 임계값(${thresholds.congSpeed}km/h) 초과`,
          time: t
        })
        pushNotif('H', `${seg.name} 혼잡 감지`, `평균 속도 ${Math.round(seg.spd)}km/h`)
      }
    }
    // 속도 회복 시 알림 자동 제거
    if (seg.spd >= thresholds.slowSpeed) {
      const i = alerts.findIndex(a => a.title === `${seg.name} 혼잡 감지`)
      if (i >= 0) alerts.splice(i, 1)
    }
  })
}, { deep: true })
```

---

## 4. WebSocket 연결 실패

### 증상
탭바 우측에 "WS 대기 중" 표시 지속. 실시간 데이터 수신 안됨.

### 원인
백엔드 WebSocket 서버(`ws://localhost:8000/ws`)가 실행되지 않은 상태.

### 해결 방법

**A. 백엔드 서버 실행 확인**
```bash
# 서버가 8000 포트에서 동작 중인지 확인
netstat -an | findstr 8000
```

**B. 프론트엔드만 사용하는 경우 (목업 데이터)**  
WebSocket 없이도 `dataTimer` (4초 간격)로 자동 시뮬레이션 데이터가 갱신됩니다.  
실시간 연결 없이도 대시보드 기능은 정상 동작합니다.

**C. 자동 재연결**  
연결 실패 시 10초마다 자동 재시도 로직이 내장되어 있습니다.

```js
ws.onclose = () => { wsRetry = setTimeout(connectWS, 10000) }
```

---

## 5. Canvas 차트가 표시되지 않음

### 증상
통계 분석 탭의 시간대별 통행량 차트가 비어있거나 렌더링 안됨.

### 원인 A — 타이밍 문제
컴포넌트 마운트 직후 canvas 요소의 `offsetWidth`가 0으로 반환되어 크기 계산 실패.

### 해결 방법
`onMounted`에서 `nextTick` + `setTimeout` 지연 처리:

```js
onMounted(async () => {
  await nextTick()
  setTimeout(drawChart, 300)  // 레이아웃 계산 완료 후 실행
})
```

### 원인 B — 탭 비활성 상태
`v-show`로 숨겨진 탭의 canvas는 offsetWidth가 0.  
해당 탭을 클릭하면 자동으로 `chartData` watch가 재실행되어 다시 그려집니다.

---

## 6. 탭 전환 시 하단 공백 발생

### 증상
카메라 현황, 번호판 인식 등 탭 전환 시 콘텐츠 아래 빈 공간이 남음.

### 원인
탭 컴포넌트 루트 요소에 `flex: 1; min-height: 0` 패턴이 없어 부모의 flex 높이를 채우지 못함.

### 해결 방법
각 탭 컴포넌트의 레이아웃 최상위 클래스에 적용:

```css
.tab-layout {
  display: flex;       /* 또는 grid */
  flex: 1;
  min-height: 0;       /* 이 속성이 핵심 — flex 자식의 overflow 허용 */
  padding-bottom: 12px;
}
```

> `min-height: 0` 없이는 flex 컨테이너가 자식 콘텐츠 크기만큼 무한 확장되어 스크롤 발생.

---

## 7. 다크모드에서 UI 요소가 안 보이는 문제

### 증상 A — 알림 팝업 내용이 안 보임
다크 배경과 동일한 어두운 색상으로 텍스트가 보이지 않음.

### 해결 방법
알림 팝업을 흰색 배경으로 고정:

```css
.notif {
  background: #fff;
  box-shadow: 0 8px 32px rgba(0,0,0,.22);
}
.notif-title { color: #0c1a30; }
.notif-desc  { color: #4a5568; }
```

### 증상 B — CSS 변수 상속 문제
컴포넌트 내부에서 `var(--t)`, `var(--bg2)` 등이 올바른 값으로 계산되지 않음.

### 해결 방법
`.theme-navy` 클래스가 `DashboardView.vue` 루트에 올바르게 적용되어 있는지 확인:

```html
<div class="theme-navy" :class="{ light: !isDark }">
```

---

## 8. AI 채팅 영어/한자 혼재 응답

### 증상
Groq API 응답에 영어 단어나 한자가 섞여서 출력됨.

### 원인
시스템 프롬프트에 한국어 강제 지시가 약하거나, temperature가 높아 창의적 언어 혼용 발생.

### 해결 방법
`src/components/ChatTab.vue` 시스템 프롬프트 강화 + temperature 낮춤:

```js
const SYSTEM_PROMPT = `[절대 규칙] 반드시 한국어로만 답변하세요. 
영어, 중국어, 일본어 등 어떤 외국어도 섞지 마세요.
...`

// API 호출 시
temperature: 0.3  // 기존 0.7 → 0.3
```

---

## 9. 라이트모드 숫자 안 보이는 문제

### 증상
라이트모드 전환 시 IntroView의 `01`, `02` 배경 숫자, UsageView의 `step-big-n` 숫자가 흰 배경에 묻혀 안 보임.

### 원인
숫자 요소의 색상이 다크모드 기준으로만 설정되어 라이트모드에서 배경색과 동일해짐.

### 해결 방법
라이트모드 전용 스타일 추가:

```css
/* IntroView.vue */
.arch-step { opacity: .12; }
.theme-navy.light .arch-step { opacity: .35; color: var(--a); }

/* UsageView.vue */
.step-big-n { opacity: 0.15; }
.theme-navy.light .step-big-n { opacity: 0.4; }
```

---

## 10. 빌드 오류 — provide is not defined

### 증상
```
ReferenceError: provide is not defined
```
또는 대시보드 접속 시 흰 화면(White Screen)만 표시됨.

### 원인
`provide('timeStr', timeStr)` 호출이 `timeStr = ref('')` 선언보다 **앞에** 위치하여 undefined 값을 provide함.

### 잘못된 코드
```js
const { isDark } = useTheme()
provide('timeStr', timeStr)  // ❌ timeStr이 아직 undefined

const timeStr = ref('')      // 여기서 선언됨
```

### 해결 방법
`provide` 호출을 `ref` 선언 **뒤로** 이동:

```js
const { isDark } = useTheme()

const timeStr = ref('')
provide('timeStr', timeStr)  // ✅ 선언 후 호출
```

---

## 공통 디버깅 팁

### LocalStorage 초기화
계정/테마 관련 이상 동작 시 브라우저 개발자 도구에서 초기화:
```
F12 → Application → Local Storage → localhost → 전체 삭제 → 새로고침
```

### Vue 개발자 도구
Chrome 확장 프로그램 **Vue DevTools** 설치 후 컴포넌트 props / reactive 상태 확인 가능.

### 빌드 에러 확인
```bash
npm run build
# 에러 메시지에서 파일명:줄번호 확인 후 수정
```

### 개발 서버 재시작
```bash
# Ctrl+C 로 종료 후
npm run dev
```

---
