# TrafficAS — AI 기반 실시간 교통 관제 시스템

## 1. 프로젝트 개요

TrafficAS는 도심 교통 흐름을 실시간으로 모니터링하고 분석하는 **AI 기반 교통 관제 웹 애플리케이션**입니다.
CCTV 기반 번호판 자동 인식(ANPR), 구역별 혼잡도 히트맵, 차량 통행(진입/이탈) 흐름 분석, 이벤트 로그, 통계 분석, 자동 알림 등
실무 교통 관제 센터 수준의 기능을 단일 대시보드에서 제공합니다.

---

## 2. 프로젝트 구조 (Architecture)

본 프로젝트는 **Vue 3 + Vite 기반 SPA(Single Page Application)** 구조로 개발되었습니다.

- **Frontend:** Vue 3 (`<script setup>` Composition API) + Vue Router 4
- **백엔드 API:** FastAPI (`VITE_FASTAPI_BASE_URL`) — 도로 혼잡도, 최근 OCR 인식 결과 등
- **AI 채팅:** Groq API (LLaMA 3.3-70B) 기반 교통 관제 어시스턴트
- **시각화:** ECharts (혼잡도/도넛/통계 차트), Leaflet (지도/히트맵)
- **도로 geometry:** OpenStreetMap Overpass API + 24시간 localStorage 캐시
- **배포:** Vite 정적 빌드 → 웹 서버 배포

### 연결 방식

```
브라우저 (Vue 3 SPA)
    │
    ├── REST API ───→ FastAPI 서버 (${VITE_FASTAPI_BASE_URL})
    │                  ├── /api/v1/road-congestion   (도로 혼잡도)
    │                  └── /api/v1/plates/recent     (최근 OCR 인식)
    │
    ├── Overpass API → overpass-api.de (다중 미러 + 캐시)
    │                  └── 강남/서초/송파 주요 도로 geometry
    │
    └── Groq API ───→ LLaMA 3.3-70B
                       └── AI 교통 관제 어시스턴트
```

---

## 3. 데모 영상

> 프로젝트 주요 기능 시연 영상입니다.

데모 영상 보기
(여기에 영상 링크 추가)

※ YouTube에 업로드 후 링크를 넣어주세요.

---

## 5. 프로젝트 소개

도심 교통 혼잡은 시민 생활과 물류에 직접적인 영향을 미치지만, 관제 정보가 분산되어 있어 통합 모니터링이 어렵다는 문제가 있습니다.

본 프로젝트는 이러한 문제를 해결하기 위해 **CCTV 기반 실시간 차량 감지 데이터를 통합하여 한 화면에서 교통 상황을 파악할 수 있는 관제 대시보드**를 개발하였습니다.

관리자는 웹 브라우저를 통해 실시간 도로 영상, 번호판 인식 로그, 차량 진입/이탈 흐름, 혼잡도 히트맵, 이벤트 감지, 통계 데이터를 확인할 수 있으며, AI 어시스턴트를 통해 자연어로 교통 정보를 조회할 수 있습니다.

---

## 6. 기술 스택

### 6-1 Frontend

- Vue 3 (Composition API, `<script setup>`)
- Vue Router 4 — 라우트별 lazy loading (`() => import(...)`)
- Vite 5 — 코드 분할 빌드
- ECharts 6 (혼잡도/도넛/통계 차트)
- Leaflet 1.9 + VWorld 다크 / CartoDB Dark Matter 타일
- OpenStreetMap Overpass API (실제 도로 geometry)
- `defineAsyncComponent` — 대시보드 탭 on-demand 로딩
- Bootstrap Icons 1.11.3 (CDN)
- Pretendard Variable, Syne, IBM Plex Mono, JetBrains Mono (폰트)

### 6-2 백엔드 / AI

- FastAPI REST 호출 (`/api/v1/road-congestion`, `/api/v1/plates/recent`)
- Spring Boot (Java 백엔드 — 도메인 엔티티 / DB)
- YOLO + OCR 엔진 (차량/번호판 감지)
- Groq API — LLaMA 3.3-70B-Versatile (교통 관제 어시스턴트)
- HTMLVideoElement (실시간 CCTV 영상 6분할)

### 6-3 인증 / 상태 관리

- LocalStorage 기반 사용자 인증
- Vue Composables (`useAuth`, `useTheme`, `useDashboardData`, `useStats`)
- Vue Router Navigation Guard (관리자 전용 라우트 보호)
- Overpass 응답 24시간 localStorage 캐시

### 6-4 협업 / DevOps

- GitHub
- Vite Build

---

## 7. 시스템 아키텍처

```
사용자 (브라우저)
    │
    ▼
Vue 3 SPA (Vite)
    │
    ├── Vue Router ──→ / (메인) /sub/intro /sub/usage /sub/support /login /signup /dashboard
    │
    ├── useAuth.js ───────→ LocalStorage (사용자 세션)
    ├── useDashboardData ─→ 공유 상태 (KPI / OCR / 카메라 / 카메라 혼잡도 / 설정)
    │
    ├── FastAPI ──────→ ${VITE_FASTAPI_BASE_URL}/api/v1/...
    │                     ├── road-congestion       (도로별 혼잡도 갱신)
    │                     └── plates/recent?limit   (최근 OCR 결과)
    │
    ├── Overpass API → 다중 미러 (overpass-api.de / kumi.systems / private.coffee / lz4)
    │                     └── 강남/서초/송파 motorway~secondary 도로
    │
    └── Groq API ─────→ LLaMA 3.3-70B
                          └── AI 교통 관제 어시스턴트 (한국어 전용)
```

---

## 8. 프로젝트 링크

### 8-1 GitHub Repository

https://github.com/dhwldrjekd1

### 8-2 프로젝트 산출물 (Notion)

(링크 추가)

---

## 9. 실행 방법

### 9-1 프로젝트 클론

```bash
git clone https://github.com/dhwldrjekd1/trafficAS-b.git
cd trafficAS-b
```

### 9-2 의존성 설치

```bash
npm install
```

### 9-3 환경 변수 설정 (`.env`)

```env
VITE_FASTAPI_BASE_URL=http://localhost:8000   # FastAPI 서버 주소 (비어있으면 데모 모드)
VITE_GROQ_API_KEY=gsk_...                     # Groq API 키 (선택)
```

> `VITE_FASTAPI_BASE_URL`이 비어있으면 모든 API 호출이 우회되고 데모 데이터(랜덤)로 동작합니다.

### 9-4 개발 서버 실행

```bash
npm run dev
```

### 9-5 프로덕션 빌드

```bash
npm run build
npm run preview
```

### 9-6 웹 접속

```
http://localhost:5173
```

### 9-7 관리자 계정

```
이메일 : admin@trafficAS.com
비밀번호 : admin1234
```

> 관리자 계정으로 로그인해야 대시보드(`/dashboard`) 접근이 가능합니다.

---

## 10. 프로젝트 구조

```
trafficAS-b/
│
├── src/
│   ├── views/
│   │   ├── MainView.vue              # 메인 랜딩 페이지 (Hero / 시스템 소개 / Features / CTA)
│   │   ├── IntroView.vue             # 서비스 소개
│   │   ├── UsageView.vue             # 이용 방법
│   │   ├── LoginView.vue             # 로그인
│   │   ├── SignupView.vue            # 회원가입
│   │   ├── SupportView.vue           # 고객지원
│   │   └── RoadDashboardView.vue     # 관리자 대시보드 (셸 + 오버뷰 탭)
│   │
│   ├── components/
│   │   ├── AppNav.vue                # 공통 네비게이션 (다크/라이트 토글)
│   │   ├── AppFab.vue                # 플로팅 버튼 (채팅/테마/상단이동)
│   │   ├── AuthModal.vue             # 로그인/회원가입 모달
│   │   ├── ChatTab.vue               # AI 채팅 (Groq API)
│   │   ├── BoardTab.vue              # 커뮤니티 게시판
│   │   ├── QnaTab.vue                # Q&A
│   │   ├── HeroStats.vue             # 메인 히어로 통계 카운터
│   │   │
│   │   └── dashboard/
│   │       ├── MonitoringTab.vue     # 실시간 카메라 상세 모니터링 (인식률/FPS/신뢰도)
│   │       ├── EventsTab.vue         # 이벤트 로그 + 등급별 필터
│   │       ├── SearchTab.vue         # 차량/번호판 검색 + OCR 상세 모달
│   │       ├── StatsTab.vue          # 통계 분석 (ECharts 4종)
│   │       └── SettingsTab.vue       # 시스템 설정
│   │
│   ├── composables/
│   │   ├── useAuth.js                # 인증 상태 관리
│   │   ├── useTheme.js               # 다크/라이트 테마
│   │   ├── useStats.js               # 메인 페이지 통계
│   │   └── useDashboardData.js       # 대시보드 공유 상태
│   │                                 #  ├── plates / cameraGroups / camCongestion
│   │                                 #  ├── plateImg / plateStatus 헬퍼
│   │                                 #  └── tickCamCongestion (3초 갱신)
│   │
│   ├── data/
│   │   └── weather.js                # 강남/서초/송파 날씨 프리셋
│   │
│   ├── styles/
│   │   ├── base.css                  # 전역 + 네이비 테마 변수
│   │   ├── light.css                 # 라이트 모드 오버라이드
│   │   └── dashboard.css             # 대시보드 전용 (외부 분리, 2,170줄)
│   │
│   └── router/
│       └── index.js                  # 라우터 + 네비게이션 가드
│
├── public/
│   ├── car1.jpg                      # OCR 미리보기용 차량 이미지
│   ├── road1.mp4 ~ road8.mp4         # 실시간 CCTV 영상 데모
│   ├── hero-main.mp4 / detect-video.mp4 / classify-video.mp4   # 랜딩 페이지 비디오
│   └── favicon.ico
│
├── index.html
├── vite.config.js
└── package.json
```

---

## 11. 주요 기능

### 11-1 대시보드 메뉴 6탭

- **대시보드 (overview)** — 셸 내부, KPI / 실시간 카메라 / 차량 통행 / OCR / HeatMap / 카메라 상태 / OCR 로그
- **모니터링** — 카메라별 상세 통계 (인식률·검출수·FPS·신뢰도, 2초마다 실시간 갱신)
- **이벤트** — 등급별 필터(중요/경고/정보) 이벤트 로그
- **검색** — LIVE 배지 + 결과 고정 토글 + 7가지 조건 필터 + OCR 상세 모달
- **통계** — 요일별 통행량, 시간대별 진입/이탈 추이, 도로별 정체, 카메라별 비교 (ECharts)
- **설정** — 알림 / 임계값 / 중복 제거 정책 / 시스템 정보

### 11-2 차량 통행 (IN / OUT) 분석

- KPI: 총 감지 / 진입(IN) / 이탈(OUT) / 중복 제거
- 차량 통행 분석 카드: 진입·이탈 카운트 + 12시간 추이 스파크라인
- OCR 로그에 흐름 방향(진입/이탈) 컬럼 표시
- 통계 탭에 시간대별 IN/OUT 추이 + 카메라별 IN/OUT 비교 차트

### 11-3 번호판 인식 (ANPR)

- 실시간 OCR 인식 결과 (사진 + 번호판 시각 오버레이 + 6항목 메타정보)
- **차량 이미지 위 번호판 합성**: `car1.jpg`의 실제 번호판 위치(45.3%, 52.8%)에 더미 번호판 텍스트 오버레이, `container query`(`cqw`)로 컨테이너 너비에 비례해 자동 스케일
- 최근 5건 썸네일
- 인식 상태 배지: 정상 / 실패 / 중복 (FLOW_EVENT_CREATED / OCR_FAILED / DUPLICATE_SKIPPED)
- 클릭 시 그 plate가 메인 OCR 카드에 표시 (`최신` 버튼으로 자동 트래킹 복귀)

### 11-4 차량 검색 (Search Tab)

- **LIVE 배지** — 헤더에 녹색 펄스 도트 + "N초 전 갱신" 카운터
- **결과 고정 토글** — 데이터가 실시간으로 흔들리지 않게 스냅샷 잠금
- **+N건 대기 카운터** — 고정 모드 중 신규 결과 누적, 클릭 시 즉시 실시간 복귀
- **신규 행 글로우** — 새 plate 들어오면 행이 1.8초간 파란색으로 깜빡
- **7가지 필터** — 날짜 범위 / 시간 범위 / 차량 번호 / 카메라 / 흐름 방향 / 인식 상태 / 최소 신뢰도
- **빠른 프리셋** — `[오늘]` `[최근 7일]`
- **OCR 상세 모달** — 행 클릭 시 큰 사진 + 번호판 + 세부정보 팝업 (배경/X 버튼/Esc 닫기)

### 11-5 실시간 카메라 모니터링

- 메인 대시보드: 6분할 3×2 그리드 (실시간 영상)
- 모니터링 탭: 카메라별 상세 패널
  - LIVE 도트 (펄스 애니메이션) + CAM-ID
  - 영상 위 OCR 신뢰도 프로그레스 바
  - 인식률 / 검출 수 / FPS / 가동 시간
  - 카메라 클릭 시 풀스크린 모달

### 11-6 혼잡도 히트맵 (Leaflet + OSM Overpass)

- VWorld 다크 (메인) / CartoDB Dark Matter (폴백) 타일
- **실제 도로 geometry**: OpenStreetMap Overpass API로 강남/서초/송파 motorway~secondary 도로를 동적 로드
  - 4개 미러 순차 시도 (overpass-api.de / kumi.systems / private.coffee / lz4)
  - 성공 응답 24시간 localStorage 캐시 → 재방문 시 즉시 표시
  - 모두 실패 시 어긋난 폴백 대신 안내 배너 + 재시도 버튼
- 도로 등급별 굵기 차등 (motorway 6px / trunk 5.5 / primary 5 / secondary 4)
- 도로명 한글(`name:ko`) 우선, 영문/태그명 폴백
- 3초마다 도로 색상 실시간 갱신 (`applyRoadCongestion`)
- **혼잡 지점 드롭다운** — 사이드바 카메라 그룹 24개(online 23개)와 동일 리스트, 각 카메라별 혼잡도 ±15% 흔들림 → 정렬 순서/색/% 실시간 변경
- 클릭 시 `flyTo` 부드러운 이동
- 전체 보기 — CSS 토글 방식 (검은 화면 없음)
- 줌 한계 설정 (`minZoom: 10`, `maxZoom: 20`, `maxNativeZoom`)

### 11-7 날씨 / 대기 환경 패널 (사이드바 상단)

- 강남구 → 서초구 → 송파구 5초마다 자동 슬라이드 (수동 클릭도 가능)
- 9가지 날씨 프리셋 (맑음/구름/비/눈/뇌우/안개/미세먼지 등) + 한국어 라벨
- 미세먼지 / 초미세먼지 / 오존 등급 색상 (좋음/보통/나쁨/매우나쁨)
- 확대 모달: 3개 구 가로 카드 + 내일 예보 (최고/최저, 강수확률, 미세먼지)

### 11-8 알림 시스템

- 헤더 종 아이콘 + 카운트 뱃지
- 알림 패널: 12건 표시 + 편집 모드 (개별 X 삭제 / 전체 삭제)
- 외부 클릭 시 자동 닫힘

### 11-9 AI 교통 어시스턴트

- Groq API (LLaMA 3.3-70B) 기반 한국어 전용 챗봇
- 교통 관제 특화 시스템 프롬프트

### 11-10 동적 날짜 처리

- 모든 시각 표시는 `todayStr`(`new Date()` 기반 로컬 yyyy-MM-dd)로 일원화
- 카메라 lastSeen / 이벤트 시각 / 시스템 정보 모두 자동 갱신
- 검색 탭 날짜 필터도 동일 기준으로 동작

---

## 12. 기대 효과

- 교통 관제 정보 통합 제공으로 대응 속도 향상
- CCTV 기반 번호판 자동 인식 + 진입/이탈 흐름 분석으로 수동 모니터링 부담 감소
- 실시간 혼잡도 알림으로 선제적 교통 관리 가능
- 날씨/대기 환경 통합으로 교통 영향 요인 동시 모니터링
- Vue 3 + Composable 컴포넌트 기반 확장 가능한 구조

---

## 13. 성능 최적화 — 사용자 부하 대응

### 13-1 라우트별 코드 분할 (Route-level Code Splitting)

```js
// src/router/index.js
const MainView          = () => import('@/views/MainView.vue')
const RoadDashboardView = () => import('@/views/RoadDashboardView.vue')
```

**효과**: 일반 사용자(메인 페이지 방문자)는 관리자용 대시보드 코드 + ECharts(~250KB) + Leaflet(~50KB)를 다운로드하지 않음.

### 13-2 대시보드 탭 On-demand 로딩

```js
// src/views/RoadDashboardView.vue
const StatsTab = defineAsyncComponent(() => import('@/components/dashboard/StatsTab.vue'))
```

**+ "처음 방문한 탭만 마운트" 패턴**:
```js
const visitedTabs = ref(new Set(['overview']))
watch(activeTab, (v) => { visitedTabs.value.add(v) })
```

```vue
<StatsTab v-if="visitedTabs.has('stats')" :active="..." />
```

**효과**: 관리자가 overview 탭만 보고 닫으면 다른 탭은 절대 로드 안 됨. `v-show` 대비 메모리·차트 인스턴스·타이머 사용량 0.

### 13-3 OSM 도로 데이터 24시간 localStorage 캐시

```js
const OVERPASS_CACHE_KEY = 'osm-roads-v1-gangnam'
const OVERPASS_CACHE_TTL = 24 * 60 * 60 * 1000
if (cached && Date.now() - cached.ts < CACHE_TTL) return cached.data
```

**효과**: 강남권 도로 geometry(~200KB)는 사용자 1명당 24시간에 1회만 외부 API 호출. 동시 접속자 100명이라도 Overpass 공용 서버 부담 최소화.

### 13-4 메모리 누수 방지

```js
onUnmounted(() => {
  clearInterval(dataT)
  clearInterval(districtT)
  Object.values(charts).forEach(c => c.dispose())
  heatMap?.remove()
  document.removeEventListener('keydown', onEscClose)
})
```

**효과**: 모든 타이머·이벤트 리스너·차트 인스턴스 명시적 정리. 장시간 켜놓는 관제 모니터링 특성상 필수.

### 13-5 빌드 결과 (Vite 프로덕션)

| 시나리오 | gzip 크기 |
|---|---|
| 메인 페이지 첫 진입 | **약 51 KB** (Vue + Router + MainView) |
| 대시보드 첫 진입 | +433 KB (RoadDashboardView + ECharts + Leaflet) |
| 통계 탭 첫 클릭 | +2.3 KB |
| 검색 탭 첫 클릭 | +3.4 KB |

---

## 14. 향후 개선 사항

## 14. 향후 개선 사항

- 실제 FastAPI 백엔드 연동 실전 검증 (`.env`의 `VITE_FASTAPI_BASE_URL` 채우면 즉시 통신 시도)
- WebSocket 도입 (현재는 3초 폴링)
- ECharts 트리쉐이킹 — 사용 차트 타입만 import해서 대시보드 청크 추가 100KB 절감
- 검색 결과 서버사이드 페이지네이션 + 가상 스크롤
- 차량 이미지 다양화 + 번호판 좌표 메타데이터 기반 자동 합성
- 에러 / 로딩 상태 통합 안내 (현재는 console.warn 중심)
- 사용자별 알림 구독 설정
- 모바일 반응형 대시보드
- 데이터 내보내기 (CSV / PDF 리포트)
- 다중 관제 센터 지원
- 차량 이동 이력 추적 (camera-to-camera 경로 시각화)

---
