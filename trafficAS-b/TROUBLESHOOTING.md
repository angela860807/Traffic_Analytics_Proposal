# 🔧 TrafficAS — 트러블슈팅 가이드

개발 및 운영 중 발생한 주요 문제와 해결 방법을 정리한 문서입니다.

---

## 목차

1. [대시보드 접근 불가 (로그인 후에도 이동 안됨)](#1-대시보드-접근-불가)
2. [관리자 계정 로그인 실패](#2-관리자-계정-로그인-실패)
3. [알림이 누적되지 않는 문제](#3-알림이-누적되지-않는-문제)
4. [WebSocket 연결 실패](#4-websocket-연결-실패)
<<<<<<< HEAD
5. [ECharts 차트가 표시되지 않음](#5-echarts-차트가-표시되지-않음)
6. [편집 모드 ON 시 버튼이 안 눌리는 문제](#6-편집-모드-on-시-버튼이-안-눌리는-문제)
7. [vuedraggable "Item slot must have only one child" 오류](#7-vuedraggable-item-slot-오류)
8. [Leaflet 히트맵 전체 보기 시 검은 화면](#8-leaflet-히트맵-전체-보기-시-검은-화면)
9. [지도 줌 인 시 검은 화면으로 바뀌는 문제](#9-지도-줌-인-시-검은-화면)
10. [Leaflet 미니맵/히트맵 컨테이너 크기 0 문제](#10-leaflet-미니맵히트맵-컨테이너-크기-0-문제)
11. [영상 6개 동시 재생 시 랙 발생](#11-영상-6개-동시-재생-시-랙-발생)
12. [vuedraggable 드래그된 카드 안 차트가 사라지는 문제](#12-드래그-후-차트가-사라지는-문제)
13. [혼잡지점 드롭다운이 지도 뒤로 가려지는 문제](#13-드롭다운이-지도-뒤로-가려지는-문제)
=======
5. [Canvas 차트가 표시되지 않음](#5-canvas-차트가-표시되지-않음)
6. [탭 전환 시 하단 공백 발생](#6-탭-전환-시-하단-공백-발생)
7. [다크모드에서 UI 요소가 안 보이는 문제](#7-다크모드에서-ui-요소가-안-보이는-문제)
8. [AI 채팅 영어/한자 혼재 응답](#8-ai-채팅-영어한자-혼재-응답)
9. [라이트모드 숫자(01, 02) 안 보이는 문제](#9-라이트모드-숫자-안-보이는-문제)
10. [빌드 오류 — provide is not defined](#10-빌드-오류--provide-is-not-defined)
>>>>>>> 4ed7521ea2bd2ece0ed05b50f754e12e445a9afe

---

## 1. 대시보드 접근 불가

### 증상
로그인 후 `/dashboard`로 직접 이동해도 메인 페이지로 튕겨나옴.

### 원인
<<<<<<< HEAD
Vue Router 네비게이션 가드에서 비관리자 계정 접근을 차단.
=======
Vue Router 네비게이션 가드에서 비관리자 계정 접근을 차단.  
>>>>>>> 4ed7521ea2bd2ece0ed05b50f754e12e445a9afe
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
<<<<<<< HEAD
`watch`가 팝업 큐만 호출하고 `alerts` 배열에 실제로 push하지 않음.
또한 같은 구간에서 중복 알림 방지 로직이 없어 dismiss 후에도 재등록이 안됨.

### 해결 방법
중복 체크 후 unshift + 속도 회복 시 자동 제거 로직 추가 (`v-show`로 표시하는 알림 탭의 `alerts` 배열 직접 조작).
=======
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
>>>>>>> 4ed7521ea2bd2ece0ed05b50f754e12e445a9afe

---

## 4. WebSocket 연결 실패

### 증상
탭바 우측에 "WS 대기 중" 표시 지속. 실시간 데이터 수신 안됨.

### 원인
백엔드 WebSocket 서버(`ws://localhost:8000/ws`)가 실행되지 않은 상태.

### 해결 방법

**A. 백엔드 서버 실행 확인**
```bash
<<<<<<< HEAD
netstat -an | findstr 8000
```

**B. 프론트엔드만 사용하는 경우 (목업 데이터)**
WebSocket 없이도 `dataTimer` (3초 간격)로 자동 시뮬레이션 데이터가 갱신됩니다.

**C. 자동 재연결**
연결 실패 시 10초마다 자동 재시도 로직이 내장되어 있습니다.

---

## 5. ECharts 차트가 표시되지 않음

### 증상
혼잡도/도넛/스파크라인 차트가 비어있거나 렌더링 안됨.

### 원인 A — 의존성 미설치
`echarts` 패키지가 `package.json`에 없는데 import 됨.

### 해결 방법
```bash
npm install echarts
```

### 원인 B — 타이밍 문제
컴포넌트 마운트 직후 차트 컨테이너의 `offsetWidth`가 0으로 반환되어 크기 계산 실패.

### 해결 방법
`onMounted`에서 `nextTick` + 강제 `resizeAll()` 두 번 호출:
=======
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
>>>>>>> 4ed7521ea2bd2ece0ed05b50f754e12e445a9afe

```js
onMounted(async () => {
  await nextTick()
<<<<<<< HEAD
  initChart('cong', congEl.value, congOpt())
  setTimeout(resizeAll, 80)
  setTimeout(resizeAll, 300)
})
```

### 원인 C — 탭 비활성 상태 (StatsTab)
`v-show`로 숨겨진 탭의 차트는 컨테이너 크기 0.
`:active` prop을 watch해서 활성화 시점에 lazy init 적용.

---

## 6. 편집 모드 ON 시 버튼이 안 눌리는 문제

### 증상
편집 모드를 켜면 KPI / 카드 내부의 버튼 (혼잡 지점 / 전체 보기 / 슬라이드 점 등) 클릭이 안 됨.

### 원인
vuedraggable이 카드 영역의 모든 mousedown을 **드래그 시작**으로 가로채서 click 이벤트가 발생하지 않음.

### 해결 방법
SortableJS의 `filter` 옵션으로 특정 요소를 드래그에서 제외:

```vue
<draggable
  v-model="r3Order"
  :disabled="!editMode"
  filter="button, input, select, label, .v2-cam-cell, .v2-hotspot-wrap, .v2-heat-tools, .v2-aq-tools, .v2-aq-progress, .v2-log-more, .leaflet-container"
  :prevent-on-filter="false"
  ...
>
```

- **`button/input/select/label`** — 일반 폼 요소
- **`.v2-cam-cell`** — 카메라 클릭으로 모달 오픈
- **`.v2-hotspot-wrap`** — 혼잡 지점 드롭다운
- **`.v2-heat-tools / .v2-aq-tools`** — 카드 헤더 도구 모음
- **`.v2-aq-progress`** — 슬라이드 진행 점 (수동 클릭)
- **`.leaflet-container`** — 지도 줌/팬 유지

> 모든 draggable에 동일하게 적용해야 함 (4개: 사이드바 / KPI / Row2 / Row3).

---

## 7. vuedraggable Item slot 오류

### 증상
```
Error: Item slot must have only one child
    at computeNodes (vuedraggable.js)
```
페이지 전체가 깨지면서 버튼 클릭 등 동작이 멈춤.

### 원인
`<template #item="{ element }">` 슬롯 내부에 **HTML 주석**(`<!-- ... -->`)이 있으면 자식 노드 수가 2개 이상으로 인식됨. vuedraggable은 정확히 **1개의 root element**를 요구함.

### 해결 방법
`#item` 슬롯 내부 주석 제거 (v-if/v-else-if 분기 사이 주석이 흔한 함정):

```vue
<!-- ❌ 잘못된 예 -->
<template #item="{ element }">
  <!-- 날씨 패널 -->
  <div v-if="element.key === 'weather'">...</div>
  <!-- 카메라 그룹 -->
  <div v-else-if="element.key === 'cameras'">...</div>
</template>

<!-- ✅ 올바른 예 -->
<template #item="{ element }">
  <div v-if="element.key === 'weather'">...</div>
  <div v-else-if="element.key === 'cameras'">...</div>
</template>
```

> 다른 위치의 주석은 OK. 오직 `#item` 슬롯의 직접 자식 사이에 주석이 있을 때만 발생.

---

## 8. Leaflet 히트맵 전체 보기 시 검은 화면

### 증상
"전체 보기" 버튼 클릭 후 화면이 검정색으로 표시됨. 종료해도 검은 화면이 한참 남음.

### 원인
브라우저 `requestFullscreen()` API 사용 시:
- fullscreen 전환은 비동기 (~300-500ms)
- Leaflet 내부 panel들이 **fullscreen 전 크기 기준 픽셀 좌표**로 transform 되어 있음
- 컨테이너 크기 변경 후에도 transform 좌표 그대로 → 콘텐츠가 화면 밖으로 밀려남
- `invalidateSize()` 호출 시점이 빠르면 효과 없음

### 해결 방법
**Browser Fullscreen API 사용 중지 → CSS 기반 토글로 전환**

```js
const heatExpanded = ref(false)
function openHeatFullscreen() {
  heatExpanded.value = !heatExpanded.value
  nextTick().then(() => {
    if (!kakaoHeat) return
    const c = kakaoHeat.getCenter()
    const z = kakaoHeat.getZoom()
    kakaoHeat.invalidateSize(true)
    kakaoHeat.setView(c, z, { animate: false })
  })
}
```

```css
.v2-heat-card.v2-heat-expanded {
  position: fixed !important;
  inset: 0 !important;
  width: 100vw !important; height: 100vh !important;
  z-index: 99999 !important;
}
```

### 이유
CSS 토글은 동기적으로 즉시 크기 변경됨. `invalidateSize(true)` + `setView`(center, zoom)로 panel을 재정렬하면 검정 화면 없이 즉시 확대됩니다. ESC 키와 다시 클릭으로 닫기 가능.

---

## 9. 지도 줌 인 시 검은 화면

### 증상
줌 인을 계속 누르면 지도 타일이 사라지고 검정색만 보임.

### 원인
타일 서버는 특정 줌 레벨까지만 이미지를 제공함:
- CartoDB Dark Matter: 19까지
- VWorld: 18까지
- 그 이상 줌 인하면 타일이 없어서 빈 영역 = 검정

### 해결 방법
Leaflet `maxZoom` + `maxNativeZoom` 옵션으로 한계 설정:

```js
kakaoHeat = L.map(heatmapEl.value, {
  minZoom: 10,         // 너무 축소 방지
  maxZoom: 20,         // 줌 인 한계
  ...
})
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
  maxZoom: 20,
  maxNativeZoom: 19,   // 타일 실제 한계 — 그 이상은 마지막 타일 확대
}).addTo(kakaoHeat)
```

`maxNativeZoom` 을 넘어가도 마지막 가능한 타일을 확대해서 보여주므로 검정 화면 없음.

---

## 10. Leaflet 미니맵/히트맵 컨테이너 크기 0 문제

### 증상
지도가 안 보이거나 회색 영역만 표시됨.

### 원인 A — `v-show` 로 숨긴 상태에서 init
컨테이너 div가 `display: none` (size 0)인 상태에서 Leaflet 초기화하면 0×0 캔버스로 그려짐.

### 해결 방법
컨테이너는 항상 DOM에 렌더링하고, SVG 폴백을 v-if로 토글:

```vue
<!-- ❌ -->
<div ref="heatmapEl" v-show="heatReady"></div>

<!-- ✅ -->
<div ref="heatmapEl"></div>
<svg v-if="!heatReady" class="fallback">...</svg>
```

### 원인 B — vuedraggable 슬롯 내부 ref 바인딩 지연
`<draggable><template #item>` 안에 차트/맵 ref가 있으면 부모의 `onMounted` 시점에 ref가 아직 null임.

### 해결 방법
`waitForRef` 헬퍼로 ref 바인딩 대기:

```js
async function waitForRef(refObj, maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    if (refObj.value) return true
    await new Promise(r => setTimeout(r, 30))
  }
  return false
}

onMounted(async () => {
  await nextTick()
  await nextTick()
  await Promise.all([
    waitForRef(congEl),
    waitForRef(heatmapEl),
    ...
  ])
  initChart(...)
  initHeatMap()
})
```

---

## 11. 영상 6개 동시 재생 시 랙 발생

### 증상
실시간 카메라 6분할 영상이 끊김. 다른 인터랙션도 느려짐.

### 원인
- 브라우저 하드웨어 디코더 슬롯 제한 (보통 4~6개)
- 큰 파일(50MB+)이 섞이면 일부가 소프트웨어 디코드로 떨어짐
- 1080p 영상 6개 동시 디코드는 CPU 부담 큼

### 해결 방법

**A. video 태그 옵션 최적화**
```vue
<video
  :src="f.src"
  autoplay muted loop playsinline
  preload="metadata"
  disablepictureinpicture
  disableremoteplayback
  @loadedmetadata="onCamLoaded"
></video>
```

```js
function onCamLoaded(e) {
  try { e.target.playbackRate = 0.85 } catch {}  // 디코더 부하 15% 감소
}
```

**B. video를 absolute 포지셔닝**
비디오 메타데이터 로드 시 인트린식 사이즈가 셀에 영향 주는 것 방지:
```css
.v2-cam-video {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
}
```

**C. 영상 파일 크기 축소 (근본 해결)**
- 60MB+ 영상은 ffmpeg으로 480p~720p 트랜스코드:
```bash
ffmpeg -i road5.mp4 -vf scale=-2:480 -b:v 800k -an road5_small.mp4
```

---

## 12. 드래그 후 차트가 사라지는 문제

### 증상
편집 모드에서 카드 위치를 드래그 변경하면 차트(혼잡도/스파크/도넛 등)가 사라짐.

### 원인
vuedraggable의 v-model 변경 시 카드 DOM이 재마운트되어 차트 컨테이너 ref가 새로 바인딩됨. ECharts 인스턴스는 이전 DOM에 attached된 상태로 유효하지 않게 됨.

### 해결 방법
ref 변경을 watch해서 자동 재초기화:

```js
watch([congEl, sparkEl, heatmapEl], async () => {
  await nextTick()
  setTimeout(() => {
    if (congEl.value && !charts.cong) initChart('cong', congEl.value, congOpt())
    if (sparkEl.value && !charts.spark) initChart('spark', sparkEl.value, sparkOpt())
    if (heatmapEl.value && !kakaoHeat) initHeatMap()
    resizeAll()
  }, 80)
})
```

---

## 13. 드롭다운이 지도 뒤로 가려지는 문제

### 증상
HeatMap 카드의 "혼잡 지점" 드롭다운 클릭 시 메뉴가 Leaflet 지도 뒤로 가려져 안 보임.

### 원인
Leaflet 컨테이너 내부 panel들이 자체 z-index를 갖고 있어 드롭다운보다 위에 표시됨.

### 해결 방법
드롭다운 z-index를 매우 높게 + Leaflet 내부 z-index를 명시적으로 낮춤:

```css
.v2-hotspot-wrap { position: relative; z-index: 1000; }
.v2-hotspot-menu { z-index: 9999; }
.v2-heat-card .v2-card-h { position: relative; z-index: 500; }
.v2-heat-map { z-index: 1; }
.v2-heat-map .leaflet-pane,
.v2-heat-map .leaflet-top,
.v2-heat-map .leaflet-bottom { z-index: 100; }
```

→ 드롭다운 9999 ≫ 카드 헤더 500 ≫ Leaflet 내부 100 ≫ 컨테이너 1
=======
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
>>>>>>> 4ed7521ea2bd2ece0ed05b50f754e12e445a9afe

---

## 공통 디버깅 팁

### LocalStorage 초기화
<<<<<<< HEAD
계정/테마/대시보드 카드 순서 이상 동작 시:
=======
계정/테마 관련 이상 동작 시 브라우저 개발자 도구에서 초기화:
>>>>>>> 4ed7521ea2bd2ece0ed05b50f754e12e445a9afe
```
F12 → Application → Local Storage → localhost → 전체 삭제 → 새로고침
```

<<<<<<< HEAD
대시보드 카드 순서만 초기화하려면 다음 키만 삭제:
- `kpiOrder`
- `r2RightOrder`
- `r3Order`
- `sideOrder`

=======
>>>>>>> 4ed7521ea2bd2ece0ed05b50f754e12e445a9afe
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

<<<<<<< HEAD
### 콘솔 경고 확인
지도 로드 실패 시 콘솔에 다음 메시지 출력:
- `[Leaflet HeatMap] 로드 실패: ...`

타일 서버 차단 등이 원인일 수 있음.

=======
>>>>>>> 4ed7521ea2bd2ece0ed05b50f754e12e445a9afe
---
