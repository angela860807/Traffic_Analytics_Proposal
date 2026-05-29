# 🔧 TAS — 트러블슈팅 가이드

---

## 목차

### 환경 / 실행
1. [vite 명령 인식 실패 (`'vite' is not recognized`)](#1-vite-명령-인식-실패)
2. [Vite 캐시 꼬임 — HMR 이상 동작](#2-vite-캐시-꼬임)
3. [Vite proxy http error — `/api/...` ECONNREFUSED](#3-vite-proxy-http-error)
4. [백엔드 부재 시에도 화면 보이게 — 데모 모드 동작](#4-백엔드-부재-시-데모-모드)

### 라우터 / 인증
5. [관리자 대시보드 접근 차단 (`/admin/*` 리다이렉트)](#5-관리자-대시보드-접근-차단)
6. [JWT role 누락 — 부서 진입 거부](#6-jwt-role-누락)

### Leaflet / OSM
7. [Leaflet 컨테이너 크기 0 — 지도가 안 보임](#7-leaflet-컨테이너-크기-0)
8. [Leaflet 줌 인 시 검은 화면 / 타일 누락](#8-leaflet-줌-인-시-검은-화면)
9. [드롭다운이 지도 뒤로 가려지는 z-index 문제](#9-드롭다운-z-index)
10. [Overpass API 모든 미러 실패 — 어긋난 폴백 대신 안내 배너](#10-overpass-모든-미러-실패)
11. [OSM way 단편으로 도로 색이 끊겨 보임](#11-osm-way-단편-색-끊김)

### ECharts
12. [ECharts 차트가 표시되지 않음 (탭 전환 후)](#12-echarts-차트가-표시되지-않음)
13. [ECharts 트리쉐이킹 — 번들 절반 이하로](#13-echarts-트리쉐이킹)

### 영상 / 미디어
14. [영상 동시 재생 시 랙 발생](#14-영상-동시-재생-시-랙)
15. [`object-fit: cover` vs `contain` — 번호판 크롭 잘림](#15-object-fit-cover-vs-contain)
16. [비디오 프레임 자동 캡처 — 선명도 휴리스틱](#16-프레임-자동-캡처)
17. [HLS 라이브 스트림(.m3u8) Chrome 재생 — hls.js lazy load](#17-hls-라이브-스트림)

### CSS / 레이아웃
18. [CSS Grid → Flex column 전환으로 박스 높이 균등 분배](#18-grid-vs-flex-column)
19. [`object-fit: cover`로 히어로 이미지가 잘리는 문제](#19-히어로-이미지-잘림)
20. [Vue scoped CSS에서 자식 컴포넌트 가득 채우기 실패](#20-scoped-자식-가득-채우기)
21. [CSS `:has()` 셀렉터로 조건부 스크롤 활성화](#21-has-조건부-스크롤)
22. [한글 헤드라인이 단어 중간에서 잘리는 문제](#22-한글-헤드라인-잘림)
23. [`.t-sub` 클래스가 헤더 타이틀을 흐리게 만드는 문제](#23-t-sub-헤더-흐림)
24. [img를 `filter: brightness(0) invert(1)`로 흰색 만들기](#24-img-흰색-처리)

### 화면 폴백 / 에러
25. [API 실패 시 화면이 통째로 비는 문제 (loadError 단독 분기)](#25-api-실패-loaderror-단독-분기)
26. [이미지 없을 때 img 깨짐 — `@error` 핸들러](#26-img-깨짐)
27. [날짜 하드코딩 — 어느 날 시연해도 "오늘"처럼 보이게](#27-날짜-하드코딩)

### Vue / SFC
28. [Vue SFC `<style>` 외부 파일로 빼기 — scoped 유지하면서 파일 분리](#28-style-외부화)
29. [ECharts zombie 인스턴스 — `v-if` 탭 전환 후 차트 안 그려짐](#29-echarts-zombie-인스턴스)

### Git / 협업
30. [PR 충돌 해결 패턴 — 양쪽 변경 모두 살리기](#30-pr-충돌-양쪽-살리기)
31. [미해결 머지 마커가 그대로 commit된 파일](#31-미해결-머지-마커-commit)
32. [`git reset --hard origin/main`로 working tree 변경 분실](#32-reset-hard-working-tree-분실)
33. [`git add -A`로 의도하지 않은 파일까지 staged](#33-git-add-a-실수)

---

## 1. vite 명령 인식 실패

### 증상
```
> vite
'vite'은(는) 내부 또는 외부 명령... 이 아닙니다.
```

### 원인
`node_modules`가 없거나 깨졌음. PowerShell에서 `npx vite`도 안 먹히는 경우 있음.

### 해결
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 2. Vite 캐시 꼬임

### 증상
- HMR이 옛 코드를 계속 보여줌
- import한 컴포저블이 `undefined`로 들어옴

### 해결
```bash
rm -rf node_modules/.vite
npm run dev
```

브라우저 캐시도 무시(Ctrl+Shift+R).

---

## 3. Vite proxy http error

### 증상
```
[vite] http proxy error: /api/speed-violations
Error: connect ECONNREFUSED 127.0.0.1:8080
```

### 원인
Spring(8080) / FastAPI(8000) 백엔드가 안 떠있음.

### 해결
- 백엔드 실행 → 자동 회복
- 또는 데모 모드로 동작시키려면 `.env`의 `VITE_API_BASE_URL` 비우기

ReviewView는 백엔드 실패 시에도 더미 4건이 폴백으로 표시됩니다 (25번 참고).

---

## 4. 백엔드 부재 시 데모 모드

### 동작 방식
- `VITE_FASTAPI_BASE_URL`이 비어있으면 도로 혼잡도/OCR API 모두 우회되고 컴포저블 내장 더미 사용
- 단속관리팀 ReviewView는 catch에서 `loadError`를 set하지 않고 더미 폴백
- 모든 시각 표시는 `new Date()` 기반 — 어느 날 시연해도 자연스러움

### 시연 체크리스트
```bash
# 백엔드 둘 다 꺼두고
npm run dev
# /admin/super → DeptSwitcher로 부서 순회
# ReviewView 4건 표시, ControlView 지도 + 카메라 정상
```

---

## 5. 관리자 대시보드 접근 차단

### 증상
`/admin/control` 직접 입력했더니 메인으로 리다이렉트.

### 원인
`src/router/index.js`의 네비게이션 가드 — `useAuth().isAdmin`이 false면 차단.

### 해결
1. `/login` → admin@email.com / 1234 로그인
2. `/admin/super` 진입 (관리자 디폴트 경로)
3. DeptSwitcher로 다른 부서 이동

---

## 6. JWT role 누락

### 증상
로그인은 성공했는데 부서 대시보드 버튼이 안 보이거나 가드가 차단.

### 원인
백엔드가 발급한 JWT의 payload에 `role: "ADMIN"`이 없음. `useAuth.js`의 `parseJwt`가 role을 못 읽으면 `isAdmin = false`.

### 해결
- 백엔드 응답 JWT를 jwt.io에 붙여 payload 확인
- 로컬 fallback 계정 사용: useAuth가 백엔드 응답이 비정상이면 로컬 4종 계정으로 떨어짐 (super/analytics/ops/review)

---

## 7. Leaflet 컨테이너 크기 0

### 증상
지도가 회색 박스만 보이고 타일이 안 옴.

### 원인
컨테이너 div가 mount 시점에 `height: 0`이라 Leaflet이 viewport를 계산 못 함. flex/grid 안에 들어가면 자주 발생.

### 해결
```js
import { nextTick } from 'vue';
onMounted(async () => {
  await nextTick();
  map = L.map(el).setView([37.5, 127], 11);
  // ResizeObserver로 후속 크기 변화 추적
  new ResizeObserver(() => map?.invalidateSize()).observe(el);
});
```

CSS로 `.map-host { min-height: 320px }` 같은 명시적 높이 부여도 함께.

---

## 8. Leaflet 줌 인 시 검은 화면

### 증상
줌 14 이상에서 타일이 안 옴 → 검은 화면.

### 원인
VWorld 다크 타일의 maxZoom이 낮음.

### 해결
```js
L.map(el, { minZoom: 10, maxZoom: 20 });
L.tileLayer(vworldUrl, { maxNativeZoom: 18, maxZoom: 20 }).addTo(map);
```
`maxNativeZoom`을 넘어가면 Leaflet이 가까운 타일을 확대해서 표시.

폴백 타일(CartoDB Dark Matter)도 같이 깔아두면 안전.

---

## 9. 드롭다운 z-index

### 증상
헤더 알림 벨 / 부서 셀렉터 / 검색 드롭다운이 Leaflet 지도에 가려짐.

### 원인
Leaflet은 내부적으로 z-index 400~600을 씀.

### 해결
드롭다운에 명시적으로 큰 z-index:
```css
.hdr-bell-pop { z-index: 1500; }
.dept-switcher .dropdown { z-index: 1500; }
```

`position: relative` 또는 `fixed`로 stacking context도 확보.

---

## 10. Overpass 모든 미러 실패

### 증상
강남/서초/송파 도로 geometry 로드 실패. 어긋난 폴백 좌표 쓰면 지도와 도로가 안 맞음.

### 해결
`useOSMRoads.js`는 4개 미러(overpass-api.de / kumi.systems / private.coffee / lz4) 순차 시도 → 모두 실패 시 어긋난 정적 폴백 대신 **안내 배너 + 재시도 버튼**.

성공 응답은 24시간 localStorage 캐시 → 다음 진입 시 즉시 표시.

---

## 11. OSM way 단편 색 끊김

### 증상
같은 도로의 OSM way 조각마다 혼잡도 색이 끊겨서 보임.

### 원인
초기 구현에서 `Math.random()`으로 way마다 혼잡도 부여 → 조각마다 다른 색.

### 해결
`useOSMRoads.js`에서 **도로 이름 hash 기반 안정 혼잡도**로 변경:
```js
function hashCode(s) {
  let h = 0;
  for (const c of s) h = (h * 31 + c.charCodeAt(0)) | 0;
  return Math.abs(h);
}
const congestionLevel = hashCode(roadName) % 5;
```
같은 이름의 way 조각은 항상 같은 색.

---

## 12. ECharts 차트가 표시되지 않음

### 증상
탭 전환 후 차트가 빈 박스로 보이거나 크기가 0.

### 원인
- 컨테이너 크기 0에서 `init` 호출됨
- 또는 `v-if` 탭에서 unmount/mount 반복으로 인스턴스가 zombie 상태

### 해결
```js
onMounted(async () => {
  await nextTick();
  const chart = echarts.init(el);  // el은 ref로
  chart.setOption(option);
  new ResizeObserver(() => chart.resize()).observe(el);
});
onUnmounted(() => chart?.dispose());
```

탭 전환 시엔 `v-if` 대신 `v-show` 사용 또는 visited tab 패턴(README 11-1 참고).

---

## 13. ECharts 트리쉐이킹

### Before
```js
import * as echarts from 'echarts';  // 전체 ~376KB gzip
```

### After (`src/composables/echartsSetup.js`)
```js
import * as echarts from 'echarts/core';
import { LineChart, BarChart, GaugeChart, PieChart } from 'echarts/charts';
import {
  GridComponent, TooltipComponent, LegendComponent,
  MarkLineComponent, MarkAreaComponent, MarkPointComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([
  LineChart, BarChart, GaugeChart, PieChart,
  GridComponent, TooltipComponent, LegendComponent,
  MarkLineComponent, MarkAreaComponent, MarkPointComponent,
  CanvasRenderer,
]);

export { echarts };
```

`200KB`로 절감. 4개 부서 뷰가 공유.

---

## 14. 영상 동시 재생 시 랙

### 증상
6개 영상 동시 재생하면 FPS 급락.

### 해결
- `<video preload="metadata">` (auto 금지)
- 보이지 않을 때 `pause()` (`IntersectionObserver`)
- HLS는 클릭 시 lazy mount (17번 참고)

---

## 15. object-fit cover vs contain

### 증상
OCR 캡처 박스(`aspect-ratio: 2/1`)에 길쭉한 번호판 크롭 이미지를 표시하니 좌우/상하가 잘려 번호 일부가 보이지 않음.

### 원인
```css
.plate-snap img { object-fit: cover; }
```
`cover`는 컨테이너를 가득 채우려고 비율 안 맞는 부분을 잘라냄. 번호판처럼 **모든 픽셀이 의미 있는 이미지**엔 부적합.

### 해결
```css
.plate-snap img {
  object-fit: contain;
  background: #000;
  padding: 8px;
}
```

### 교훈
- 사진/풍경 → `cover`
- 번호판/문서/스캔 이미지 → `contain` 필수
- `contain`은 빈 영역이 생기므로 `background` 색을 명시

---

## 16. 프레임 자동 캡처

### 패턴
영상에서 가장 선명한 프레임을 외부 라이브러리 없이 선택.

```js
async function pickSharpestFrame(videoEl, baseT, windowSec = 1.6, samples = 8) {
  const canvas = document.createElement('canvas');
  canvas.width = videoEl.videoWidth;
  canvas.height = videoEl.videoHeight;
  const ctx = canvas.getContext('2d');
  let best = { t: baseT, score: -Infinity };
  for (let i = 0; i < samples; i++) {
    const t = baseT - windowSec / 2 + (windowSec * i) / (samples - 1);
    await seekVideo(videoEl, t);
    ctx.drawImage(videoEl, 0, 0);
    const score = edgeStrength(ctx, canvas.width, canvas.height);
    if (score > best.score) best = { t, score };
  }
  await seekVideo(videoEl, best.t);
  return canvas.toDataURL('image/jpeg', 0.9);
}
```

`edgeStrength`는 인접 픽셀 차이 합. ReviewView OCR 캡처 자동 버튼에서 사용.

---

## 17. HLS 라이브 스트림

### 증상
`.m3u8` URL을 `<video>`에 그대로 넣으면 Chrome에서 재생 안 됨.

### 해결 — hls.js lazy load
```js
async function attachHls(videoEl, url) {
  if (videoEl.canPlayType('application/vnd.apple.mpegurl')) {
    videoEl.src = url;  // Safari/iOS는 native 지원
    return;
  }
  const { default: Hls } = await import('hls.js');  // 클릭 시점에만 다운로드
  const hls = new Hls();
  hls.loadSource(url);
  hls.attachMedia(videoEl);
}
```

ControlView 카메라 마커 클릭 → 모달 열림 시점에만 hls.js 다운로드.

---

## 18. Grid vs Flex column

### 증상
이벤트 정보 카드의 행 개수가 6→5로 줄자, 2열 grid가 박스 하단에 빈 여백을 만듦.

### 해결
```css
.evt-info { display: flex; flex-direction: column; }
.ei-grid {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex: 1;
}
.ei-row { flex: 1; }
```
행 개수가 변해도 박스를 자동으로 채움.

### 교훈
- "박스 안에 N개 항목을 균등 배치"는 **grid보다 flex column이 단순/안전**
- grid는 명확한 격자(라벨/값 정렬, multi-column 카드)에 적합

---

## 19. 히어로 이미지 잘림

### 증상
히어로 박스 `height: 480px`에 이미지 넣었더니 좌우가 잘림.

### 원인
`object-fit: cover` + 박스/이미지 비율 불일치.

### 해결
```css
.hero-img { height: 100%; object-fit: contain; }
```
또는 박스 높이를 이미지 비율에 맞춰 `aspect-ratio` 사용.

---

## 20. scoped 자식 가득 채우기

### 증상
`<style scoped>` 부모에서 자식 컴포넌트가 박스를 못 채움.

### 해결
`:deep()` 셀렉터로 자식 루트 강제:
```css
.panel-inner :deep(> *) { width: 100%; height: 100%; }
```

---

## 21. :has() 조건부 스크롤

### 패턴
부모 컨테이너의 스크롤을 특정 자식 존재 여부로 토글.

```css
.content { overflow: hidden; }
.content:has(.tab-panel-cmp),
.content:has(.tab-panel-map) { overflow: auto; }
```
dashboard 탭은 스크롤 없이 viewport-fit, 나머지는 auto.

---

## 22. 한글 헤드라인 잘림

### 증상
"우리가 만듭니다" → "우리가 만듭/니다" (어절 중간에서 줄바꿈).

### 해결
```css
.headline { word-break: keep-all; }
```
어절 단위 줄바꿈. 본문 전체에 일괄 적용 권장.

---

## 23. .t-sub 헤더 흐림

### 증상
admin 헤더 타이틀이 흐리게(opacity: 0.85) 나옴.

### 원인
`<a class="t-sub t-main">` 처럼 `t-sub` 클래스가 잉여 첨부됨 → `.t-sub`의 `opacity: .8`이 적용.

### 해결
헤더 타이틀에서 `t-sub` 제거. `.t-main`만 사용 (22px / 700 / `#0c1f40`).

---

## 24. img 흰색 처리

### 패턴
컬러 로고를 어두운 배경 위에 흰색으로 표시.

```css
.brand-img-light { filter: brightness(0) invert(1) drop-shadow(0 1px 2px rgba(0,0,0,0.3)); }
```
LoginView / SignupView 좌측 패널에서 `TAS.png` 흰색 처리에 사용.

---

## 25. API 실패 loadError 단독 분기

### 증상
백엔드 미기동 상태에서 단속관리팀 진입 시 이벤트 목록이 통째로 비고 빨간 에러 메시지만 표시.

### 원인
```vue
<tr v-else-if="loadError"><td>{{ loadError }}</td></tr>
<template v-else v-for="grp in groupedEvents">...</template>
```
`loadError`가 truthy면 본 목록 렌더링을 막는 단독 분기. 빈 큐를 보여줄 마지노선이 없음.

### 해결 — 더미 fallback + 에러 메시지 미표시
```js
const DUMMY_REVIEW_EVENTS = [/* 4건 */];
const speedEvents = ref(DUMMY_REVIEW_EVENTS.map(e => ({ ...e })));

async function loadSpeedViolationEvents() {
  try {
    const rows = await listSpeedViolations(...);
    speedEvents.value = [...DUMMY_REVIEW_EVENTS.map(e => ({...e})), ...rows.map(mapSpeedViolation)];
  } catch (err) {
    console.warn(err);
    speedEvents.value = DUMMY_REVIEW_EVENTS.map(e => ({...e}));
    // loadError는 set 하지 않음 → 본 목록 분기로 진입
  }
}
```

### 교훈
시연 환경에선 "에러 메시지로 화면을 가리는" 패턴보다 **마지막 가용 상태(또는 더미)로 폴백** 패턴이 안전. 단 결재/금전 화면처럼 실패 인지가 중요한 곳엔 적용 금지.

---

## 26. img 깨짐

### 패턴
이미지 로드 실패 시 빈 박스 + placeholder 표시.

```vue
<img v-if="src && !broken" :src="src" @error="broken = true" />
<div v-else class="img-ph"><i class="bi bi-image"></i></div>
```

ReviewView OCR 캡처 / 차량 이미지에서 사용.

---

## 27. 날짜 하드코딩

### 증상
어제 만든 더미 데이터의 시각이 다음 날엔 "어제 사고"처럼 보임.

### 해결
모든 시각 표시를 `new Date()` 기반으로 일원화:
```js
function todayStr() {
  const d = new Date();
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
}
```
카메라 lastSeen / 이벤트 시각 / 시스템 정보 모두 동적 계산.

단, DUMMY_REVIEW_EVENTS처럼 정적인 시연 데이터는 의도적으로 고정 날짜(예: 2026-05-28)를 둠 — 시연 시 데모 모드인 게 명확해서 OK.

---

## 28. style 외부화

### 패턴
Vue SFC에서 `<style scoped>`를 외부 CSS 파일로 빼면서도 scoped 동작 유지.

```vue
<style scoped src="./MyView.css"></style>
```
빌드 결과 동일, 단지 IDE 인지 부하/검색만 가벼워짐.

추출 시:
```bash
sed -n '<style 시작줄>,<끝줄-1>p' X.vue > X.css
# X.vue의 style 블록 → 한 줄로 src=
```

ReviewView/ControlView/AnalyticsView/OpsView/SuperView 전부 이 방식.

---

## 29. ECharts zombie 인스턴스

### 증상
`v-if`로 탭 전환 후 차트가 안 그려짐.

### 원인
이전 인스턴스가 dispose 안 된 채로 같은 DOM에 다시 init.

### 해결
```js
onUnmounted(() => {
  chart?.dispose();
  chart = null;
});
```
또는 `v-show` + 한 번만 init.

또는 `defineAsyncComponent` + 첫 방문한 탭만 마운트하는 visited 패턴 (README 11-1 참고).

---

## 30. PR 충돌 양쪽 살리기

### 증상
PR 머지 시 양쪽 변경이 모두 의미 있어서 어느 한쪽 채택이 어려움.

### 패턴
```bash
git checkout main && git pull
git checkout my-branch
git merge main
# 충돌 파일 열어서 양쪽 변경을 모두 통합
git add <file>
git commit
```

특히 QnaTab 같은 공용 컴포넌트는 변경 종류(스타일/로직)가 다르면 양쪽 다 살리는 게 정상.

---

## 31. 미해결 머지 마커 commit

### 증상
원격 main pull 시 `Element is missing end tag` 같은 컴파일 에러 — 자세히 보니 원격 파일 안에 `<<<<<<< Updated upstream`, `>>>>>>> Stashed changes` 마커가 그대로 들어있음.

### 원인
누군가 `git stash pop` 충돌을 해결 안 한 채로 add/commit. Git은 텍스트로만 보고 막지 않음.

### 해결
1. `git stash push` 로컬 변경 보호
2. `git pull --rebase`
3. 충돌 파일 열어서 마커 영역을 올바른 한쪽으로 정리 (양쪽 모두 망가져 있을 수 있어 새로 작성)
4. `git add <file>` + `git rebase --continue`
5. `git push`
6. `git stash pop`

### 예방
- 커밋 전 `grep -rn "<<<<<<<\\|>>>>>>>" .`
- pre-commit hook으로 차단 (`git diff --cached --check`)
- 충돌 해결 직후 빌드/HMR 통과 확인

---

## 32. reset --hard로 working tree 분실

### 증상
다른 도구/세션이 `git reset --hard origin/main` 실행 → uncommit 변경분이 통째로 사라짐. `git stash list`에도 없음.

### 진단
```bash
git reflog -10
# reset: moving to origin/main ← 범인
```

### 해결
- commit된 변경은 `git reset --hard <reflog-hash>`로 복구 가능
- **commit 안 된 변경은 stash로 빠지지 않는 한 복구 불가** — 수동 재작성 외 방법 없음

### 예방
- 큰 작업 중 `.md` 같은 untracked 문서가 있으면 임시 commit (`WIP: docs`)
- 외부 도구가 working tree에 손대는 환경이면 `git stash push -u`로 untracked까지 보호
- 한 시간 이상 누적된 변경은 한 번씩 commit으로 snapshot

---

## 33. git add -A 실수

### 증상
`.claude/settings.local.json` 같은 로컬 전용 파일이 staged.

### 원인
`git add -A` / `git add .`는 모든 untracked + modified를 일괄 staging.

### 해결
```bash
git restore --staged .claude/settings.local.json
echo ".claude/" >> .gitignore
git add .gitignore
git commit -m "chore: ignore .claude local settings"
```

### 예방
```bash
git status --short                # 변경 미리보기
git add src/ public/TAS.* *.md    # 명시적 패턴
git add -p                        # 인터랙티브
git diff --cached --stat          # staged 재검토
```

### 교훈
- `.env`, `.claude/`, `.vscode/`, OS별 설정 파일은 `.gitignore` 필수
- `git add -A`는 작은 작업이거나 모든 변경이 확실히 검토된 경우만
