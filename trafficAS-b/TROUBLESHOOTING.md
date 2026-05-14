# 🔧 TrafficAS — 트러블슈팅 가이드

개발 및 운영 중 발생한 주요 문제와 해결 방법을 정리한 문서입니다.

---

## 목차

1. [대시보드 접근 불가 (로그인 후에도 이동 안됨)](#1-대시보드-접근-불가)
2. [관리자 계정 로그인 실패](#2-관리자-계정-로그인-실패)
3. [ECharts 차트가 표시되지 않음](#5-echarts-차트가-표시되지-않음)
4. [Leaflet 히트맵 전체 보기 시 검은 화면](#4-leaflet-히트맵-전체-보기-시-검은-화면)
5. [지도 줌 인 시 검은 화면으로 바뀌는 문제](#5-지도-줌-인-시-검은-화면)
6. [Leaflet 미니맵/히트맵 컨테이너 크기 0 문제](#6-leaflet-미니맵히트맵-컨테이너-크기-0-문제)
7. [영상 6개 동시 재생 시 랙 발생](#7-영상-6개-동시-재생-시-랙-발생)
8. [혼잡지점 드롭다운이 지도 뒤로 가려지는 문제](#8-드롭다운이-지도-뒤로-가려지는-문제)
9. [Overpass 도로가 지도와 어긋나는 문제](#9-overpass-도로가-지도와-어긋나는-문제)
10. [검색 결과가 실시간으로 흔들려서 검토 불가](#10-검색-결과-실시간-흔들림)
11. [더미 번호판이 차량 사진과 위치가 안 맞는 문제](#11-더미-번호판-위치-오버레이)
12. [날짜가 과거(2024-05-28)로 박혀있는 문제](#12-날짜-하드코딩)
13. [index.html 폰트가 적용 안 되는 문제](#13-indexhtml-폰트-누락)
14. [FastAPI 연동이 안 되는 것 같은 문제](#14-fastapi-연동-미실행)
15. [메인 페이지 첫 진입이 너무 느린 문제](#15-메인-페이지-첫-진입-속도)
16. [대시보드 탭이 다 마운트되어 메모리 많이 쓰는 문제](#16-대시보드-탭-사전-마운트)
17. [UTC 응답이 자정 근처 날짜 어긋남](#17-utc-응답-날짜-어긋남)
18. [프로덕션에서 가짜 차량 사진이 보이는 문제](#18-프로덕션-가짜-차량-사진)
19. [백엔드 응답에 이미지 URL이 없을 때 ＜img＞ 깨짐](#19-이미지-없을-때-img-깨짐)

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
이메일 : admin@email.com
비밀번호 : 1234
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
`admin@email.com` / `1234` 로 로그인 시 "계정 정보가 맞지 않습니다" 오류 발생.

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

## 3. ECharts 차트가 표시되지 않음

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

```js
onMounted(async () => {
  await nextTick()
  initChart('cong', congEl.value, congOpt())
  setTimeout(resizeAll, 80)
  setTimeout(resizeAll, 300)
})
```

### 원인 C — 탭 비활성 상태 (StatsTab)
`v-show`로 숨겨진 탭의 차트는 컨테이너 크기 0.
`:active` prop을 watch해서 활성화 시점에 lazy init 적용.

---

## 4. Leaflet 히트맵 전체 보기 시 검은 화면

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
    if (!heatMap) return
    const c = heatMap.getCenter()
    const z = heatMap.getZoom()
    heatMap.invalidateSize(true)
    heatMap.setView(c, z, { animate: false })
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

## 5. 지도 줌 인 시 검은 화면

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
heatMap = L.map(heatmapEl.value, {
  minZoom: 10,         // 너무 축소 방지
  maxZoom: 20,         // 줌 인 한계
  ...
})
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
  maxZoom: 20,
  maxNativeZoom: 19,   // 타일 실제 한계 — 그 이상은 마지막 타일 확대
}).addTo(heatMap)
```

`maxNativeZoom`을 넘어가도 마지막 가능한 타일을 확대해서 보여주므로 검정 화면 없음.

---

## 6. Leaflet 미니맵/히트맵 컨테이너 크기 0 문제

### 증상
지도가 안 보이거나 회색 영역만 표시됨.

### 원인 — `v-show` 로 숨긴 상태에서 init
컨테이너 div가 `display: none` (size 0)인 상태에서 Leaflet 초기화하면 0×0 캔버스로 그려짐.

### 해결 방법
컨테이너는 항상 DOM에 렌더링하고, 로딩 표시를 v-if로 토글:

```vue
<!-- ❌ -->
<div ref="heatmapEl" v-show="heatReady"></div>

<!-- ✅ -->
<div ref="heatmapEl"></div>
<div v-if="!heatReady" class="v2-heat-loading">지도 로딩 중…</div>
```

### 추가 — ref 바인딩 지연
부모의 `onMounted` 시점에 자식 컴포넌트의 ref가 아직 null인 경우:

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
  await Promise.all([waitForRef(congEl), waitForRef(heatmapEl)])
  initChart(...)
  initHeatMap()
})
```

---

## 7. 영상 6개 동시 재생 시 랙 발생

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

## 8. 드롭다운이 지도 뒤로 가려지는 문제

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

---

## 9. Overpass 도로가 지도와 어긋나는 문제

### 증상
히트맵 도로 폴리라인이 실제 지도의 도로 위에 정렬되지 않고 엉뚱한 위치에 그어짐. "지도 따로, 혼잡선 따로" 보임.

### 원인
- 과거: Overpass API 호출 실패 시 하드코딩된 `roadSegments`(지하철역 좌표 근사값)로 폴백
- 지하철역 좌표는 도로의 실제 geometry가 아니라 *역 위치*이므로 도로와 어긋남
- Overpass 호출 실패율이 높아 폴백이 자주 노출

### 해결 방법
**A. 다중 미러 + 24시간 캐시로 Overpass 성공률 끌어올리기**

```js
const OVERPASS_MIRRORS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://overpass.private.coffee/api/interpreter',
  'https://lz4.overpass-api.de/api/interpreter',
]
const OVERPASS_CACHE_KEY = 'osm-roads-v1-gangnam'
const OVERPASS_CACHE_TTL = 24 * 60 * 60 * 1000

async function loadOSMRoads() {
  // 1) 캐시 확인
  const cached = JSON.parse(localStorage.getItem(OVERPASS_CACHE_KEY) || 'null')
  if (cached && Date.now() - cached.ts < OVERPASS_CACHE_TTL) return cached.data
  // 2) 미러 순차 시도
  for (const url of OVERPASS_MIRRORS) {
    try { /* fetch with 12s timeout */ }
    catch (e) { console.warn(`[OSM] ${url} 실패`) }
  }
  return null
}
```

**B. 어긋난 하드코딩 폴백 제거**

모두 실패해도 부정확한 선을 그리지 않고 안내 배너 + 재시도 버튼 표시:

```vue
<div v-if="osmFailed" class="v2-heat-notice">
  <i class="bi bi-exclamation-triangle-fill"></i>
  OSM 도로 데이터 로드 실패 — 지도 타일만 표시 중
  <button @click="retryOSMRoads">다시 시도</button>
</div>
```

→ 캐시 적중 시 새로고침해도 즉시 정확한 도로 표시, 실패 시에도 어긋난 선 없이 깔끔.

---

## 10. 검색 결과 실시간 흔들림

### 증상
검색 탭에서 결과를 클릭/검토하는 중에 백그라운드 3초 갱신이 일어나 행 순서가 밀려 올라가버림.

### 원인
검색 탭은 `useDashboardData`의 공유 `plates` ref를 그대로 사용하는데, 메인 대시보드의 dataT 인터벌이 plates를 매 3초마다 갱신하면서 검색 결과도 함께 변동.

### 해결 방법
**결과 고정 토글 + 대기 카운터**

```vue
<button @click="togglePause">
  <i :class="paused ? 'bi bi-unlock-fill' : 'bi bi-lock-fill'"></i>
  {{ paused ? '실시간 복귀' : '결과 고정' }}
</button>
```

```js
const paused = ref(false)
const frozenPlates = ref([])
const pendingCount = ref(0)

function togglePause() {
  if (!paused.value) {
    frozenPlates.value = [...plates.value]   // 스냅샷
    paused.value = true
  } else {
    paused.value = false
    pendingCount.value = 0
  }
}

watch(() => plates.value.map(p => p.id).join(','), () => {
  if (paused.value) {
    const added = ... // 새로 들어온 plate 수 계산
    pendingCount.value += added
  }
})

const source = computed(() => paused.value ? frozenPlates.value : plates.value)
```

→ 고정 모드 중 LIVE 배지가 회색 "고정됨 · N건 스냅샷"으로 변경, 신규 결과는 `+N건 대기 ↻` 칩으로 누적 표시. 칩 클릭 시 즉시 실시간 복귀.

---

## 11. 더미 번호판 위치 오버레이

### 증상
차량 이미지(`car1.jpg`) 위 흰색 번호판 박스가 사진 정중앙에 떠 있어서 차량의 실제 번호판과 겹치지 않음. "OCR이 진짜로 인식한 것처럼" 보이지 않음.

### 원인
기존 `.v2-plate-vis`는 `display: grid; place-items: center` 컨테이너 안에 중앙 정렬되어 있어, 차량 사진의 실제 번호판 위치(절반 정도 아래쪽)와 무관하게 그려짐.

### 해결 방법
**A. 컨테이너에 이미지 비율 잠그기**

```css
.v2-ocr-photo {
  position: relative;
  overflow: hidden;
  aspect-ratio: 1500 / 1033;   /* car1.jpg 실제 해상도 */
  container-type: inline-size; /* cqw 폰트 스케일링 활성화 */
}
```

**B. 번호판 박스를 절대 위치로 이동 (이미지 좌표 %)**

```css
.v2-plate-vis {
  position: absolute;
  left: 44%;       /* 사진 속 번호판 좌측 */
  top: 52%;        /* 사진 속 번호판 상단 */
  width: 26.5%;
  height: 9%;
  background: #fff;
  border: 1px solid rgba(0,0,0,.35);
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

**C. 폰트를 컨테이너 너비에 비례 스케일링**

```css
.v2-plate-num {
  font-size: 4.5cqw;   /* container query width */
  font-weight: 800;
}
```

→ 메인 OCR 카드(작은 사이즈)나 검색 탭 모달(큰 사이즈) 어디서든 번호판 박스 안에 텍스트가 딱 맞게 자동 조절됨.

### 참고
다른 차량 이미지를 사용하려면:
1. `aspect-ratio` 값을 이미지 실제 해상도로 교체
2. `left/top/width/height` % 값을 새 이미지의 번호판 좌표로 조정

---

## 12. 날짜 하드코딩

### 증상
대시보드의 카메라 lastSeen, 이벤트 로그, OCR 시각, 설정 페이지의 "최종 업데이트" 등이 모두 `2024-05-28`로 고정되어 시연 시 어색함.

### 원인
초기 데모 데이터 작성 시점의 날짜가 그대로 박혀 있고, 여러 파일에 분산되어 일괄 갱신이 어려웠음.

### 해결 방법
**`todayStr` 동적 계산으로 일원화**

```js
// src/composables/useDashboardData.js
const _d = new Date()
const _p = n => String(n).padStart(2, '0')
const todayStr = `${_d.getFullYear()}-${_p(_d.getMonth() + 1)}-${_p(_d.getDate())}`
```

이후 모든 곳에서 `todayStr` 참조:

```js
// plates (초기 5건 + dataT 인터벌 생성)
{ id: 1, ..., date: todayStr, time: '14:32:18', ... }

// 카메라 lastSeen
{ name: '테헤란로 교차로', lastSeen: `${todayStr} 14:32:21`, ... }

// EventsTab 이벤트 시각
{ id: 1, time: `${todayStr} 14:32:18`, ... }

// SettingsTab
<span class="mono">{{ todayStr }}</span>
```

→ 페이지 새로고침할 때마다 오늘 날짜로 자동 갱신, 검색 탭 `[오늘]` 프리셋도 정상 매칭.

---

## 13. index.html 폰트 누락

### 증상
MainView의 헤딩(`h1`, `h2`)과 라벨(`.ey`, `.ey-tag`)이 디자인 시안과 다르게 시스템 기본 폰트로 표시됨. favicon도 404.

### 원인
**A. favicon 경로 오류**
```html
<!-- ❌ Vite는 public/ 폴더를 root에 매핑 -->
<link rel="icon" href="./public/favicon.ico">
```
런타임에 `/public/favicon.ico`로 해석되는데 그 경로는 존재하지 않음 → 404.

**B. 폰트 누락**
MainView가 `Syne`(헤딩)와 `IBM Plex Mono`(라벨)를 광범위하게 사용하는데 `index.html`에 로드 안 됨 → 시스템 monospace/sans-serif로 폴백.

### 해결 방법

```html
<!-- ✅ Vite 매핑 기준 root 경로 -->
<link rel="icon" href="/favicon.ico">

<!-- ✅ MainView가 사용하는 모든 폰트 로드 -->
<link
  href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=IBM+Plex+Mono:wght@300;400;500;600&family=Syne:wght@500;700;800&display=swap"
  rel="stylesheet"
/>

<!-- 추가: SEO/PWA 기본 메타 -->
<meta name="description" content="YOLO 기반 실시간 차량 감지와 번호판 OCR로 교통 흐름을 분석하는 관제 대시보드">
<meta name="theme-color" content="#020b18">
```

---

## 14. FastAPI 연동 미실행

### 증상
백엔드를 띄웠는데 대시보드가 여전히 랜덤 데모 데이터로 동작. 네트워크 탭에 API 호출이 안 잡힘.

### 원인
`.env`의 `VITE_FASTAPI_BASE_URL`이 비어있으면 fetch 함수가 첫 줄에서 즉시 종료:

```js
const FASTAPI_BASE = import.meta.env.VITE_FASTAPI_BASE_URL;
async function fetchRoadCongestion() {
  if (!FASTAPI_BASE) return null;   // ← URL 비어있으면 여기서 끝
  ...
}
```

→ null 리턴 → 모든 인터벌이 데모 폴백 코드로 빠짐.

### 해결 방법

**A. `.env` 파일에 백엔드 주소 명시**
```env
VITE_FASTAPI_BASE_URL=http://localhost:8000
```

**B. Vite 개발 서버 재시작 (필수)**
환경 변수는 빌드 타임에 임베드되므로 `.env` 수정 후 반드시 dev 서버 재시작.

```bash
# Ctrl+C 로 종료 후
npm run dev
```

**C. 백엔드 응답 형식 확인**
프론트가 가정하는 형식:
- `GET /api/v1/road-congestion` → `[{ name: '테헤란로 (강남역→역삼역)', c: 0.85 }, ...]`
- `GET /api/v1/plates/recent?limit=20` → `[{ id, plateNumber, cameraName, detectedAt, confidenceScore, plateCropImageUrl, ... }]`

필드명이 다르면 `RoadDashboardView.vue`의 `normalizePlate()`에서 매핑 조정:

```js
function normalizePlate(p) {
  return {
    id:    p.id ?? p.detectionLogId,
    num:   p.plateNumber ?? p.num ?? '미인식',
    cam:   p.cameraName ?? p.cameraCode ?? p.cam ?? '-',
    date:  p.date ?? (p.detectedAt ? p.detectedAt.slice(0, 10) : todayStr),
    time:  p.time ?? (p.detectedAt ? p.detectedAt.slice(11, 19) : ''),
    conf:  p.conf ?? Math.round((p.confidenceScore ?? 0) * 100),
    dir:   p.dir ?? 'in',
    ...
  }
}
```

**D. 디버깅: 콘솔에서 직접 확인**
```js
fetch(`${import.meta.env.VITE_FASTAPI_BASE_URL}/api/v1/plates/recent?limit=5`)
  .then(r => r.json())
  .then(console.log)
```

---

## 15. 메인 페이지 첫 진입 속도

### 증상
일반 사용자가 메인 페이지(`/`)만 방문하는데도 다운로드해야 하는 JS가 수백 KB. 사용자 동시 접속 시 첫 화면 표시(LCP)가 느려짐.

### 원인
라우터에서 모든 view를 **eager import**로 한 번에 번들링:

```js
// ❌ 이러면 메인 페이지 진입자도 RoadDashboardView + ECharts + Leaflet 다 받음
import RoadDashboardView from '@/views/RoadDashboardView.vue'
import StatsTab from '@/components/dashboard/StatsTab.vue'
```

Vite는 한 청크에 다 묶어서 빌드 → 최초 진입 시 전체 다운로드.

### 해결 방법
**라우트별 lazy loading**:

```js
// src/router/index.js
const MainView          = () => import('@/views/MainView.vue')
const RoadDashboardView = () => import('@/views/RoadDashboardView.vue')
```

Vite가 자동으로 view별 청크 분리. 메인 페이지 진입자는 `MainView.js`만 받고, `/dashboard` 클릭 시점에 추가 청크 다운로드.

**효과 (gzip 기준)**:
- 메인 페이지 첫 진입: 약 480KB → **약 51KB** (90% 감소)
- 대시보드는 진입 시점에 비로소 다운로드

### 검증
```bash
npm run build
# dist/assets/ 에 view별 청크가 분리되어 생성됨
# index-*.js (공통) / MainView-*.js / RoadDashboardView-*.js ...
```

---

## 16. 대시보드 탭 사전 마운트

### 증상
대시보드 진입 시 모든 탭(모니터링/이벤트/검색/통계/설정)의 컴포넌트가 마운트되어 메모리·타이머·차트 인스턴스를 동시 점유. 저사양 PC에서 초기 렌더 느림.

### 원인
`v-show`로 탭을 숨기면 컴포넌트는 마운트된 상태로 DOM만 hidden. ECharts 차트도 초기화되고, 자체 타이머도 동작.

```vue
<!-- ❌ 마운트는 즉시, 가려져만 있음 -->
<StatsTab v-show="activeTab === 'stats'" />
```

### 해결 방법
**`defineAsyncComponent` + "처음 방문한 탭만 마운트" 패턴**:

```js
// src/views/RoadDashboardView.vue
import { defineAsyncComponent } from "vue";

const StatsTab = defineAsyncComponent(() => import("@/components/dashboard/StatsTab.vue"));

const activeTab = ref("overview");
const visitedTabs = ref(new Set(["overview"]));
watch(activeTab, (v) => { visitedTabs.value.add(v); });
```

```vue
<!-- ✅ visitedTabs에 추가된 후에만 마운트, 이후엔 v-show로 visibility 토글 -->
<StatsTab v-if="visitedTabs.has('stats')" :active="activeTab === 'stats'" />
<EventsTab v-if="visitedTabs.has('events')" v-show="activeTab === 'events'" />
```

### 효과
- overview 탭만 본 사용자: 다른 4개 탭 컴포넌트는 다운로드/마운트 안 됨 (메모리 0)
- 한 번 방문한 탭은 마운트 유지 → 상태(검색 필터 등) 보존
- 대시보드 진입 직후 메모리 사용량 절반 이하

---

## 17. UTC 응답 날짜 어긋남

### 증상
백엔드가 보낸 `detectedAt: "2026-05-12T20:30:00Z"`(UTC) 데이터가 한국 시각으론 `2026-05-13 05:30:00`인데, 프론트엔 `2026-05-12 20:30:00`으로 표시. 검색 탭 "오늘" 필터에도 어제 데이터가 잡힘.

### 원인
기존 `normalizePlate()`가 단순 문자열 슬라이스:
```js
date: p.detectedAt.slice(0, 10),  // ← UTC 그대로 자름
time: p.detectedAt.slice(11, 19), // ← 한국 시각 변환 안 됨
```

### 해결 방법
**`new Date()` + `toLocaleDateString('sv-SE')` 조합** — 'sv-SE' 로케일은 ISO 형식(`yyyy-MM-dd`)을 반환하므로 비교 가능:

```js
function normalizePlate(p) {
  let d = '', t = ''
  if (p.detectedAt) {
    const dt = new Date(p.detectedAt)
    if (!isNaN(dt)) {
      d = dt.toLocaleDateString('sv-SE')             // yyyy-MM-dd (로컬 기준)
      t = dt.toLocaleTimeString('en-GB', { hour12: false })  // HH:mm:ss
    }
  }
  return {
    date: p.date ?? d ?? todayStr,
    time: p.time ?? t,
    ...
  }
}
```

### 권장 백엔드 규칙
- 항상 UTC ISO 8601로 송신 (`...Z` 또는 `+00:00`)
- 프론트가 사용자 로컬 시각으로 변환
- 그래야 다중 지역·서머타임 대응 가능

---

## 18. 프로덕션 가짜 차량 사진

### 증상
백엔드 연동 완료 후에도 OCR 실패·bbox 못 찾은 데이터에 `car1.jpg`(개발용 더미 차량 사진)이 표시됨. 발표나 시연 시 "실제 차량 데이터처럼" 보여 오해 유발.

### 원인
`plateImg()`의 최종 폴백이 무조건 `/car1.jpg`:
```js
return p.plateCropImageUrl
    || p.cropUrl
    || p.imageUrl
    || '/car1.jpg'   // ❌ 프로덕션에서도 항상 보임
```

### 해결 방법
**Vite 환경 변수 `import.meta.env.DEV`로 모드별 분기**:

```js
// src/composables/useDashboardData.js
function plateImg(p) {
  if (!p) return ''
  return p.plateCropImageUrl
      || p.cropUrl
      || p.imageUrl
      || (import.meta.env.DEV ? '/car1.jpg' : '')
}
```

- `npm run dev` → DEV 모드, 데이터 없을 때 `car1.jpg` 표시 (시연·디자인 작업 편리)
- `npm run build` → PROD 모드, 빈 문자열 → 가짜 이미지 노출 0

### 보완 — 빈 이미지 placeholder
빈 문자열일 때 `<img>`가 깨지므로 템플릿에 가드 + placeholder 추가 (트러블슈팅 19번 참조).

---

## 19. 이미지 없을 때 img 깨짐

### 증상
백엔드 응답에 `plateCropImageUrl` / `imageUrl` 모두 null인데 프론트가 `<img :src="">`로 렌더 → 브라우저가 X 아이콘 표시. 보기 흉함.

### 원인
- bbox 못 찾은 OCR_FAILED는 crop URL이 null
- 백엔드 통신 실패 직후 imageUrl도 null인 케이스 존재
- 프로덕션에선 폴백 이미지도 없음 (#18 참조)

### 해결 방법
**`v-if`로 plateImg 결과 가드 + `v-else`로 placeholder div 표시**:

```vue
<!-- 메인 OCR 카드 -->
<img v-if="latestPlate.id && plateImg(latestPlate)"
     :src="plateImg(latestPlate)"
     class="v2-ocr-photo-img"
     :alt="latestPlate.num" />
<div v-else-if="latestPlate.id" class="v2-ocr-photo-empty">
  <i class="bi bi-image"></i>
  <span>이미지 없음</span>
</div>

<!-- OCR 썸네일 5개 -->
<img v-if="plateImg(p)" :src="plateImg(p)" class="v2-ocr-thumb-img" :alt="p.num" />
<div v-else class="v2-ocr-thumb-empty"><i class="bi bi-image"></i></div>

<!-- 검색 탭 OCR 모달 -->
<img v-if="plateImg(modalPlate)" :src="plateImg(modalPlate)" ... />
<div v-else class="v2-ocr-photo-empty">
  <i class="bi bi-image"></i>
  <span>이미지 없음</span>
</div>
```

### CSS
```css
.v2-ocr-photo-empty {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 6px;
  background: linear-gradient(135deg, #1a2b44, #0f1d30);
  color: rgba(228,238,255,.35);
  font-size: 12px;
}
.v2-ocr-photo-empty i { font-size: 28px; color: #60a5fa; opacity: .5; }
.v2-ocr-thumb-empty {
  width: 100%; aspect-ratio: 16/9;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,.04);
  border-radius: 3px;
}
```

---

## 공통 디버깅 팁

### LocalStorage 초기화
계정/테마/캐시 이상 동작 시:
```
F12 → Application → Local Storage → localhost → 전체 삭제 → 새로고침
```

OSM 도로 캐시만 초기화하려면:
- `osm-roads-v1-gangnam` 키 삭제

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

### 콘솔 경고 확인 (OSM 관련)
지도 로드 실패 시 콘솔에 다음 메시지 출력:
- `[OSM] 캐시 사용 (N개 도로)` — 정상, 24시간 캐시 적중
- `[OSM] {url} ← N개 도로 로드 완료` — 정상, 새로 받음
- `[OSM Overpass] {url} 실패: ...` — 해당 미러 실패, 다음 미러 시도
- `[OSM Overpass] 모든 미러 실패 — 도로 표시 생략` — 4개 미러 전부 실패, 배너 표시됨
- `[Leaflet HeatMap] 로드 실패: ...` — Leaflet 자체 초기화 실패 (드물게 발생)

---
