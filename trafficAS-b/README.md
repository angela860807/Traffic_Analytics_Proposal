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
- **실시간 채팅:** 키워드 매칭 + 대시보드 실시간 상태 조회 기반 어시스턴트 (외부 API 의존 없음)
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
    └── 실시간 채팅 (로컬)
                       └── 키워드 매칭 + 대시보드 상태 실시간 조회
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
    ├── Vue Router ──→ / (메인) /sub/intro /sub/support /login /signup /dashboard
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
    └── 실시간 채팅 (로컬 키워드 매칭)
                          └── 대시보드 상태 실시간 조회 + 자동 이벤트 푸시
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
VITE_API_BASE_URL=http://localhost:8080       # Spring Boot 서버 주소
VITE_FASTAPI_BASE_URL=http://localhost:8000   # FastAPI 서버 주소 (비어있으면 데모 모드)
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
이메일 : admin@email.com
비밀번호 : 1234
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
│   │   ├── LoginView.vue             # 로그인
│   │   ├── SignupView.vue            # 회원가입
│   │   ├── SupportView.vue           # 고객지원
│   │   └── RoadDashboardView.vue     # 관리자 대시보드 (셸 + 오버뷰 탭)
│   │
│   ├── components/
│   │   ├── AppNav.vue                # 공통 네비게이션 (다크/라이트 토글)
│   │   ├── AppFab.vue                # 플로팅 버튼 (채팅/테마/상단이동)
│   │   ├── AppFooter.vue             # 공통 푸터 (4컬럼, 마케팅 페이지용)
│   │   ├── AuthModal.vue             # 로그인/회원가입 모달
│   │   ├── ChatTab.vue               # 실시간 채팅 (키워드 매칭 + 대시보드 상태 조회)
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

### 11-9 실시간 관제 어시스턴트 (채팅)

- **키워드 매칭** + 대시보드 실시간 상태(`useDashboardData`) 직접 조회로 즉답 — 외부 API 의존 없음
- 빠른 명령 칩 5개 (시스템 상태 / 카메라 현황 / 혼잡 TOP3 / 통행량 / 알림)
- 새 알림 발생 시 채팅창에 자동 푸시 (LIVE/OFF 토글)
- 헤더에 실시간 카메라 가동 수 표시 (5초 갱신)
- DEMO 모드 — 백엔드 미연동 시 8~15초마다 샘플 이벤트 시뮬레이션 (운영 환경에선 자동 OFF)

### 11-10 동적 날짜 처리

- 모든 시각 표시는 `todayStr`(`new Date()` 기반 로컬 yyyy-MM-dd)로 일원화
- 카메라 lastSeen / 이벤트 시각 / 시스템 정보 모두 자동 갱신
- 검색 탭 날짜 필터도 동일 기준으로 동작

### 11-11 카메라 Heartbeat 모니터링 + 자동 알람

- 카메라별 `📡 N초 전` heartbeat 배지 (실시간 갱신)
- 상태 3단계: `online` (녹색 펄스) / `warn` (주황) / `offline` (빨강 + 카드 강조)
- 임계값 기반 자동 알람 — 인식률 / FPS / heartbeat 끊김 초 사용자 설정 가능
- 디바운스(60초): 같은 카메라·같은 사유로 중복 알림 방지
- 음소거 토글 (점검 중인 카메라는 알람 제외)

### 11-12 고객 지원 (SupportView)

- 사이드바 + 컨텐츠 패널의 풀스크린 SaaS 레이아웃 (Slack/Discord 스타일)
- 3채널: **게시판** / **Q&A** / **실시간 채팅**
- 채널별 아이콘 + 활성 시 글로우 효과 + LIVE 펄스 도트
- 게시판: 검색·페이지네이션·댓글 CRUD·검색어 하이라이트
- Q&A: 질문·답변·관리자 권한·상태 배지(답변 대기/답변 완료)
- 채팅: 키워드 매칭 + 대시보드 실시간 상태 조회 어시스턴트 (외부 API 의존 없음, 자동 이벤트 푸시)

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

## 14. 디자인 시스템 / UI 일관성

### 14-1 공통 컴포넌트 — `AppFooter.vue`
- 4컬럼 구조 (브랜드 / 서비스 / 기술 / 팀·산출물)
- `MainView`, `IntroView`, `SupportView`에서 import해 일관된 푸터 유지
- 한 번 수정하면 페이지 동시 반영

### 14-2 폰트 시스템
- **한글 본문**: Pretendard Variable (가독성)
- **헤딩 (랜딩)**: Syne 700/800 (디스플레이용)
- **코드 / 라벨**: IBM Plex Mono / JetBrains Mono
- 본문 14~15px / 라벨 11px / 헤딩 clamp() 반응형

### 14-3 컬러 토큰 (`base.css`)
- `--bg / --bg2 / --bg3` 배경 3단계
- `--t / --t2 / --t3` 텍스트 명도 3단계
- `--a / --ba / --glow` 강조 / 보더 / 글로우
- 다크 ↔ 라이트는 `.theme-navy.light` 변수만 재정의

### 14-4 페이지별 푸터 정책
| 페이지 유형 | 푸터 |
|---|---|
| 랜딩 / 소개 / 고객 지원 | `<AppFooter />` 마케팅 푸터 |
| 로그인 / 회원가입 | 풀스크린 폼 — 푸터 없음 |
| 관리자 대시보드 | 한 줄짜리 © (관제 UI 전용) |

---

## 15. 향후 개선 사항

- 실제 FastAPI 백엔드 연동 실전 검증 (`.env`의 `VITE_FASTAPI_BASE_URL` 채우면 즉시 통신 시도)
- WebSocket 도입 (현재는 3초 폴링)
- ECharts 트리쉐이킹 — 사용 차트 타입만 import해서 대시보드 청크 추가 100KB 절감
- 비디오 자산 트랜스코드 (현재 280MB+ → 720p로 약 30MB까지 절감 가능)
- 검색 결과 서버사이드 페이지네이션 + 가상 스크롤
- 차량 이미지 다양화 + 번호판 좌표 메타데이터 기반 자동 합성
- 에러 / 로딩 상태 통합 안내 (토스트 시스템)
- 사용자별 알림 구독 설정
- 모바일 반응형 대시보드
- 데이터 내보내기 (CSV / PDF 리포트)
- 다중 관제 센터 지원
- 차량 이동 이력 추적 (camera-to-camera 경로 시각화)
- SEO 메타(Open Graph, Twitter Card) + 모니터링(Sentry 등) 도입

---

## 16. 인덱스 / 고객지원 페이지 리뉴얼 (2026-05-15)

### 16-1 메인(MainView) 변경 요약
- **HERO**: 좌측 텍스트 / 우측 이미지(`/main1.png`) 사이드바이사이드.
  - 그리드 비율 3:7, 우측 이미지가 화면 끝까지 풀블리드(`margin-right: calc(60px - (50vw - 50%))`).
  - 좌측 30%까지 mask gradient로 텍스트 영역과 자연스럽게 페이드.
  - 우측 이미지 영역 `align-self: stretch`로 박스 위/아래 가득.
- **4 FEATURE 카드**: 히어로 끝선에 살짝 걸치도록 `margin-top: -50px` + `z-index: 5`.
  - 아이콘 + 제목 같은 행(flex row), 카드 우상단 화살표 링크.
- **SOLUTION 개요**: 좌측 대시보드 스크린샷 / 우측 카피 + 체크리스트. 그리드 `1.25fr / 1fr`, gap 80px + `padding-left: 40px`.
- **SERVICE PROCESS**: 4스텝 아이콘 원형. 번호 원이 아이콘 좌상단에 absolute 오버랩 + `box-shadow`. 옆 스텝과 dashed line으로 연결(`.process-line`).
- **CORE FEATURES**: 5개 항목 가로 정렬, 아이콘 좌 / 텍스트 우, 세로 구분선(`border-right`).
- **CTA**: 파란 그라데이션 카드. 데모/문의 버튼.
- **파트너 섹션**: 삭제.
- **Bootstrap arrow-right 아이콘**: 모든 버튼/링크에서 제거.
- **Lucide 도입**: 데이터 수집(`Cctv`), 핵심기능 5개 (`Cctv`/`ScanText`/`BellRing`/`BarChart3`/`Network`)는 Lucide, 나머지는 Bootstrap Icons.

### 16-2 고객지원(SupportView) 변경 요약
시안 기반 풀스크린에서 일반 페이지로 재구성:
1. **HERO**: 좌측 라벨 `CUSTOMER SUPPORT` + h1 `고객 지원` + 4채널(공지사항 / 질문답변 / 실시간채팅 / 운영시간) 그리드. 우측 `/support_headset_hero.png` 헤드셋 일러스트. 히어로 박스 사이즈 `height: 480px` 고정 + 이미지는 `height: 100%; object-fit: contain`으로 박스 안에 정확히 맞춤. 좌측 mask gradient로 텍스트 영역과 어우러짐.
2. **MAIN 레이아웃**: 280px 사이드바 + 콘텐츠 패널(`<BoardTab>` / `<QnaTab>` / `<ChatTab>`).
   - 사이드바: 4개 카드(공지사항 / 질문답변 / 실시간채팅[Live 펄스 뱃지] / 운영시간[disabled])
   - 패널: 흰 카드 + 라운드 + `padding: 32px 36px` + `min-height: 720px`. `.panel-inner :deep(> *)`로 자식 컴포넌트가 박스 가득 채우게 강제.
3. **VALUES**: 4개 카드(빠른 응답 / 전문 기술 지원 / 다양한 채널 / 안전한 서비스), 짧은 파란 선 액센트.
4. **CTA**: 헤드셋 아이콘 + `실시간 채팅 시작` 버튼 — 클릭 시 `tab = 'chat'`.
5. **AppFooter** 포함.

### 16-3 헤더 / 푸터 톤 정리
- **AppNav**: 메뉴 링크 색 `--t3 (24%)` → `--t 100%` + `weight: 600`, 호버 색은 `--a`(파랑)로 일관.
- **AppFooter**: 본문/링크는 `--t opacity: 0.62`(보조 정보 톤)로 약하게, 호버 시 `--a + opacity:1`로 부각.

### 16-4 폰트 / 색상 톤 통일
- 본문 설명류는 `var(--t2)` 대신 **`var(--t) + opacity: 0.62~0.78`**로 통일 → 다크/라이트 모드 둘 다 또렷.
- 하이라이트(`<em>`) 컬러: 라이트 `#4f9cf9`, 다크 `#60a5fa` — 평소 `--a`보다 한 톤 밝은 시안 블루.
- 한글 본문은 `word-break: keep-all` 적용으로 어절 단위 줄바꿈.

### 16-5 의존성 추가
```json
"dependencies": {
  "lucide-vue-next": "^0.x"
}
```

### 16-6 LAN/팀 공유 메모
로컬 데모 공유:
```bash
npm run dev -- --host
```
출력의 `Network: http://192.168.x.x:5173/`를 같은 WiFi 팀원에게 공유. 외부망은 `npx cloudflared tunnel --url http://localhost:5173`.

---

## 17. 사용법 제거 · 공지사항 단순화 · 시스템 소개 전면 개편 · 다크모드 제거 (2026-05-15 후속)

### 17-1 라우트/네비게이션 변경
- **사용법 페이지(`/sub/usage`) 통째 삭제** — UsageView.vue 파일 + 라우터 import + AppNav/AppFooter 링크 + light.css 전용 룰까지 정리
- **고객 지원 → 공지사항** 명칭 변경 (URL `/sub/support` 유지). 페이지 내부도 Q&A·실시간 채팅 탭 제거하고 **BoardTab 단일 렌더**로 단순화

### 17-2 시스템 소개(IntroView) 전면 재작성
시안 기반으로 6개 섹션 구조:
1. **HERO** — `SYSTEM INTRODUCTION` 라벨 / `시스템 소개` h1 / 2줄 카피 / 우측 일러스트 (그라데이션 풀블리드)
2. **시스템 아키텍처** — 4개 카드(Camera·Edge AI → AI Detection → Data Platform → Dashboard/API), 카드 내부 `[01] | English/Korean` 헤더 + `[아이콘 좌 / 불릿 우]` 본문, 카드 사이 `<ChevronRight />` 연결
3. **데이터 라이프사이클** — 5단계 원형 아이콘 + dashed 점선, 카드별 80~84px 원 안에 Lucide 아이콘
4. **핵심 모듈** — 4개 카드 (가운데 정렬), 번호·제목·그래픽·설명·태그칩 3개
5. **연동 및 배포** — 좌측 박스(Integration 4개: REST/WebSocket/SDK/Export) + ChevronRight + 우측 박스(Deployment 3개: Cloud/On-premise/Hybrid)
6. **비즈니스 임팩트** (다크 네이비 배너) — 6개 KPI(97%+/50ms/90%/40%+/99.9%/무제한), 배경에 옅은 48×48 그리드 + radial mask 패턴, 카드 hover 시 lift + 값 색상 시안 블루로 변경

### 17-3 SVG 일러스트 폴백 메커니즘
`public/illustrations/` 폴더에 `hero.svg`/`arch-camera.svg`/`arch-ai.svg`/`arch-database.svg`/`arch-dashboard.svg`를 떨어뜨리면 자동으로 SVG 사용, 없으면 Lucide 아이콘으로 폴백:
```vue
<img v-if="a.svg && !a.svgBroken" :src="a.svg" @error="a.svgBroken = true" />
<component v-else :is="a.lucide" :size="64" />
```

### 17-4 다크 모드 제거 / 라이트 모드 단일화
- **`useTheme.js`**: `isDark = ref(false)` 고정, `toggle()`은 no-op 처리 (호환성 유지)
- **`AppFab.vue`**: 채팅/테마 토글 버튼 제거 → **↑ 맨 위로** 버튼만
- **`base.css`**: `scrollbar-gutter: stable` 제거(대시보드 양쪽 흰 공백 원인), html/body 라이트 톤(`#f1f5fb`) 직접 적용

### 17-5 톤 통일 및 디테일 정리
- 모든 페이지 `hero-tag` 폰트 → **14px / weight 700 / letter-spacing 0.16em**로 통일
- 모든 `.sec` 패딩 → **80px 60px**로 통일 (페이지별 60/80/100 혼재 해결)
- 푸터: `기술` 컬럼 제거(4→3 columns), 패딩 36/32 → **24/22**로 슬림화, `서비스`/`팀·산출물` 컬럼 **가운데 정렬**
- 헤더 메뉴/사용자명/버튼: opacity 24% → 100%, weight 600으로 또렷하게
- 푸터 링크: opacity 0.62로 보조 톤, 호버 시 `var(--a)` + opacity 1

### 17-6 BoardTab 폰트 전반 상향
공지사항 게시판 가독성 개선:
- info 14.5/300 → 16/500, 글쓰기 버튼 12.5/9·18 → 14/11·22
- 테이블 행 14 → 15.5px, 헤더 11 → 12.5px
- 댓글 본문 14/`--t2` → 15/`--t` 85%, 페이지네이션 12.5/34px → 14/36px

### 17-7 솔루션 개요 강화 (변주)
4분할 카드 단조로움 해소를 위해 솔루션 개요만 다른 비례로:
- 그리드 `1.25fr / 1fr` → **`1.5fr / 1fr`**로 대시보드 이미지 영역 확대
- 이미지 그림자 강화(`24px 60px → 32px 80px`) + 호버 시 미세 lift

### 17-8 메인 히어로 그라데이션·톤 다듬기
- 마스크 그라데이션: 6-stop → **11-stop ease-in 페이드** (0~42% 점진적)
- 이미지에 `filter: saturate(0.78) brightness(0.85)` 추가 → 톤다운

### 17-9 Lucide 아이콘 도입 확대
신규 사용: `Cctv`(데이터 수집/실시간 영상 분석), `BrainCircuit`(AI 엔진), `Database`(데이터 플랫폼), `LayoutDashboard`(대시보드), `Car`(차량 감지), `ArrowLeftRight`(IN/OUT), `BellRing`(이벤트 알림), `Plug`/`Radio`/`Code2`/`FileDown`(연동), `Cloud`/`Server`/`Network`(배포), `Crosshair`/`Zap`/`Bot`/`TrendingUp`/`ShieldCheck`/`Infinity`(KPI), `ChevronRight`(연결 화살표)

### 17-10 코드 클린업
- `src/components/HeroStats.vue` 삭제 — 사용처 0
- `light.css`의 `.step-vline`, `.stats-band.cyan` 등 죽은 룰 제거
- 모든 페이지의 dead import / 미사용 ref 점검 완료

### 17-11 한글 표기 수정
- "AI **검지** 엔진" → "AI **감지** 엔진" 일괄 수정 (4건)

---

## 18. 공지사항 상세보기 + 권한 분리 (2026-05-16)

### 18-1 공지사항 상세 페이지
목록에서 행 클릭 시 **목록 → 상세 페이지로 mutex 전환** (라우터 변경 없이 컴포넌트 내부 상태로 처리).

상세 페이지 구성:
- **상단 액션**: `← 목록으로` 버튼 + (관리자가 작성한 글에 한해) `삭제` 버튼
- **제목** + NEW 배지
- **메타 정보**: 작성자 · 날짜 · 조회수 · 댓글 수 (JetBrains Mono)
- **본문 영역**: `white-space: pre-wrap`으로 줄바꿈/공백 보존, `font-size: 15px / line-height: 1.85`
- **댓글 영역**: 기존 댓글 패널 구조 그대로 (목록 + 작성 폼 + 수정/삭제)

`목록으로` 클릭 시 `detailPost = null` → 검색바·페이지네이션 포함 원래 목록 복귀.

### 18-2 권한 매트릭스 정리
| 액션 | 비로그인 | 일반 회원 | 관리자 |
|---|---|---|---|
| 게시글 목록/검색/상세 조회 | ✓ | ✓ | ✓ |
| **글쓰기 버튼 노출** | ✗ | ✗ | ✓ |
| 댓글 작성 | ✗ | ✓ | ✓ |
| 본인 댓글 수정/삭제 | – | ✓ | ✓ |
| **타인 댓글 수정/삭제** | – | ✗ | ✓ |
| 관리자 작성 글 삭제 | – | – | ✓ |

구현:
- 글쓰기 버튼: `v-if="isAdmin"` (비관리자에게는 렌더링 자체 안 됨)
- `canEdit(c)` 함수: 관리자면 모든 댓글 true, 일반 회원은 `currentUser.email === c.authorEmail` 일 때만 true

### 18-3 시드 게시글 + 사용자 작성 글 분리
- `seedPosts` (불변, 컴포넌트 내 고정 6개)
- `customPosts` (reactive, `localStorage.tas_board_posts`에 영속화)
- `posts = computed(() => [...customPosts, ...seedPosts])` — 새 글이 항상 최상단
- 관리자 작성 글에만 삭제 권한 (`canEditPost`가 customPosts에 포함되는지 확인)

### 18-4 글쓰기 모달
관리자만 진입 가능한 인플레이스 모달:
- 제목(`maxlength: 100`) + 본문(`textarea rows=10`) 입력
- 등록 시 `Date.now()`를 id로 부여, 작성자=현재 로그인 사용자명, 날짜=`MM.DD`, isNew=true
- 빈 입력 시 등록 버튼 비활성화

### 18-5 메인 히어로 카피 수정
- `서비스 소개` → **`시스템 소개`** (메인 hero `.btn-g` 버튼)

### 18-6 주석 톤 정리
ASCII 박스 주석(`═══════ HERO ═══════`)과 친절한 한국어 설명 주석을 **짧은 소문자 영문 라벨**(`/* hero */`, `/* search */`, `/* table */`)로 통일. dead CSS 룰(`.cpanel`, `.chv`, `.post-body`, `.pb-meta`, `.pb-text`) 제거.

---

## 19. 6개 부서 대시보드 전면 개편 (2026-05-20)

운영기획팀 제거 → 5개 부서 체제로 재편하면서 각 부서의 핵심 역할에 맞춰 IA를 다듬었습니다.

### 19-1 운영기획팀(ReportsView) 제거 + 기능 분산
- **삭제**: `ReportsView.vue`, `/admin/reports` 라우트, DeptSwitcher/AppNav 메뉴, `reports/1234` 로컬 계정
- **흡수**:
  - 월간 운영성과 / 분기 KPI / 감사 로그 보고서 → **경영전략본부(SuperView) `reports` 탭**
  - 보고서 예약 / 자동 발행 / 최근 발행 목록 → **교통분석팀(AnalyticsView) `보고서 관리` 탭**
- 옛 `/admin/reports` 링크는 `/admin/super`로 redirect

### 19-2 부서별 보고서 다운로드 시스템
- 신규 `src/composables/useReportDownload.js` — 6개 부서별 보고서 템플릿(제목/헤더/샘플 데이터) 내장
- `downloadDeptReport(deptKey, reportKey, { date, endDate })` — CSV + UTF-8 BOM(한글 엑셀 호환)
- 헤더에 기간 자동 삽입, 파일명에 선택 날짜 반영
- ReviewView 헤더에 `<input type="date">` + 일일/주간 버튼, ControlView 보고서 탭에 `기준 날짜` 입력

### 19-3 단속관리팀(ReviewView) — 2차 검증 워크플로
관제센터 영상 → 캡처 이미지 전달 → 사람이 2차 검증 → 최종 결정 흐름으로 재설계:
- **STEP 1** — 실제 과속인가? 두 버튼(실제 과속 / 시스템 오류)으로 양자택일
- **STEP 2** — 선택값에 따라 사유 옵션이 동적으로 바뀜
- **STEP 3** — 단속 확정 / 단속 무효 결정
- 검토 히스토리에 시스템 자동 감지 → 관제센터 캡처 이미지 전달 → 단속관리팀 결정 3단계 출처 추적

### 19-4 관제센터 → 단속관리팀 위반 전송 (큐 패턴)
- 신규 `src/composables/useViolationQueue.js` — localStorage 기반 위반 큐 (최대 20건 자동 cap)
- 관제센터 카메라 컨트롤바에 **빨간 단속 전송 버튼** — 클릭 시 현재 프레임 캡처 + 메타데이터(번호판/감지속도/제한속도/카메라ID) 생성 → 큐에 push
- 단속관리팀이 마운트 시 큐를 흡수해 이벤트 목록 상단에 표시 (`source: 'control'` 뱃지 + `CTRL` 표식)
- 이미지 이벤트는 비디오 대신 정지 이미지를 보여주고, OCR 캡처 슬롯에도 그 이미지 자동 채움

### 19-5 OCR 캡처 자동화 (선명도 휴리스틱)
ReviewView의 OCR 캡처 워크플로:
- **자동** 버튼 — 1.6초 구간 8프레임 샘플링 → 각 프레임의 엣지 강도 계산 → 가장 선명한 프레임 자동 선택
- **순간 캡처** — 영상 일시정지 + 그 프레임 크롭 (번호판 추정 영역만 480px로 확대)
- **프레임 스텝** — 0.1초씩 정밀 조정 후 자동 재캡처
- 외부 라이브러리 0, 캔버스 기반, ~40줄

### 19-6 교통정보센터(ControlView) — 메인 대시보드 핵심화
"관제센터가 메인 대시보드"라는 컨셉에 맞춰 흐름 중심으로 재정렬:
- **제거** (이관·삭제):
  - 긴급 처리 큐 / 선택 구간 속도 추이 / 선택 이벤트 상세 / 관제 가이드 / 빠른 작업 / 최근 이벤트 로그
  - 교통통계 탭 + 내용은 **교통분석팀 `교통통계` 탭**으로 이관
- **추가**:
  - **ITS Open API 실시간 지표 카드** (서울 한정 + zoom-gate)
  - 지도에 CCTV 마커 + 클릭 시 HLS 라이브 비디오 모달 (hls.js lazy load, 클릭 전 다운로드 0)
  - **🚨 실시간 알림 패널** → 헤더 🔔 종 아이콘 + 드롭다운으로 이동 (critical 시 빨간 펄스)
  - **📢 VMS 도로 전광판 제어** — 메시지 입력/템플릿 4종(사고/정체/기상/초기화)/송출 + LED 디스플레이 미리보기
- **레이아웃 (한 페이지 fit)**:
  - 좌측: 실시간 교통 흐름 지도 (1.4fr)
  - 우측 상단: 선택 카메라 (큰, 세로)
  - 우측 하단: VMS 전광판 제어 (콤팩트)
- 헤더에 날씨 칩 + 알림 종 인라인 배치

### 19-7 ECharts 트리쉐이킹 (성능)
- 신규 `src/composables/echartsSetup.js` — 사용 차트(Line/Bar/Gauge/Pie) + 컴포넌트(Grid/Tooltip/Legend/MarkLine/MarkArea/MarkPoint) + CanvasRenderer만 등록
- OpsView / AnalyticsView / RoadDashboardView / StatsTab 4파일이 공유
- 번들 ~53% 절감 (gzip 376kB → **200kB**), RoadDashboardView 688 → **88kB**
- 화면 출력은 1픽셀도 변화 없음

### 19-8 OSM 도로 모듈 통합
RoadDashboardView가 가지고 있던 로컬 `loadOSMRoads`/`renderOSMRoads`/`congestionColor` 구현을 공용 `src/composables/useOSMRoads.js`로 일원화. 도로 이름 hash 기반 안정 혼잡도 — 같은 도로의 모든 OSM way 조각이 같은 색으로 표시됨(이전 `Math.random()` 방식은 조각마다 색이 끊겨 보였음).

### 19-9 공용 비디오/시간 유틸
중복 코드 정리 — 신규 `src/composables/useVideoUtils.js`:
- `padNum`, `fmtDateTime`, `fmtDate`, `fmtTime`
- `enterFullscreen(el)` — brower prefix 호환
- `captureFrameDataURL(videoEl, { outWidth, crop, quality })` — 옵션 크롭 캡처
- `seekVideo(videoEl, t)` — Promise 기반 seek

ControlView · ReviewView 두 곳에서 사용 (~75줄 중복 제거)

### 19-10 디자인 / 통일
- 6개 부서 사이드바 폰트 통일 (시설운영팀 기준 — 16px 본문, 17px 아이콘)
- `Traffic AS` 브랜드에서 파란 dot 모두 제거 (5개 파일 일괄)
- 부서 셸 베이스 폰트: Inter + Pretendard Variable + 시스템 폰트 fallback, `font-feature-settings: tnum cv11 ss01`
- 헤더 날씨 칩 — 날씨 상태별 아이콘 자동 매핑 (맑음=태양, 흐림=구름, 비=빗방울 등)
- 시설운영팀 사이드바 토글 버튼 — 파란 36×36 둥근 박스 + `arrow-bar-left/right` 아이콘

---

## 20. 파일 크기 정리 — CSS 외부화 + dead 룰 제거 (2026-05-20 후속)

대시보드 Vue 파일들이 너무 비대해져 IDE 인지 부하가 컸음. 안전한 방식으로 단계적 분리.

### 20-1 Vue SFC CSS 외부화 — `<style scoped src="...">` 패턴
Vue SFC가 `<style scoped src="./X.css"></style>` 패턴을 지원해, 스타일을 외부 CSS 파일로 빼면서도 **scoped 동작(데이터 attribute 자동 부착)은 그대로 유지**. 동작/렌더링 0 차이, 빌드 결과 번들 크기 동일.

| 파일 | Before | After (.vue) | + .css 파일 |
|---|---|---|---|
| OpsView | 6,284 | **2,996** (-52%) | OpsView.css 3,287 |
| AnalyticsView | 1,597 | **845** (-47%) | AnalyticsView.css 751 |
| ControlView | 1,302 | **691** (-47%) | ControlView.css 610 |
| ReviewView | 1,005 | **638** (-37%) | ReviewView.css 366 |

추출 절차:
```bash
sed -n '<style 시작줄>,<끝줄-1>p' X.vue > X.css
head -<script 끝줄> X.vue > /tmp/x.txt
cat /tmp/x.txt > X.vue
echo '<style scoped src="./X.css"></style>' >> X.vue
```

### 20-2 admin-shared.css — dead `.admin-shell` 룰 제거
운영기획팀(ReportsView) 제거 후 `.admin-shell` 셀렉터는 모든 Vue 파일에서 0회 사용. 그러나 admin-shared.css에는 464회 등장 → 전부 dead.

Python 스크립트로 안전하게 제거:
1. **Solo 룰** (`.admin-shell .xxx { ... }`): 블록 전체 삭제
2. **멀티셀렉터의 줄 단위 항목** (`.admin-shell .xxx,` 단독 라인): 라인 삭제
3. **`@media` / `@keyframes` / `@supports` 블록**: 보존 (regex 사고 방지)
4. **인라인 멀티셀렉터** (`.cc-shell, .admin-shell { ... }`): **건드리지 않음** — 이걸 regex로 정제하려다 한 번 라이트 테마 override를 깨뜨려서 검은 배경 나옴, 즉시 원복

**결과**: 2,897 → **2,333줄** (-564줄, -20%). 동작 변화 0.

### 20-3 전체 정리 효과
| 합계 | Before | After | 감소 |
|---|---|---|---|
| 5개 파일 합산 | 13,085줄 | **7,503줄** | **-43%** |

- 개발자 경험: IDE 스크롤·검색·점프 부담 절반 이하
- 런타임: 변화 0 (사용자 체감 차이 없음. 진짜 무게는 ECharts 트리쉐이킹·hls.js lazy load로 이미 줄였음)

### 20-4 시도했다가 원복한 것
- admin-shared.css **인라인 멀티셀렉터 정제** (`[^{}]+?` regex): CSS 블록 경계를 정확히 못 잡아 라이트 테마 override 블록까지 망가뜨림 → `git checkout` 원복
- 교훈: regex로 CSS 정제는 위험. 멀티셀렉터에서 한 토큰만 빼려면 proper CSS parser 사용해야 함

---
