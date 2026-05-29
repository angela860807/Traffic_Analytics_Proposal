# TAS — AI 기반 실시간 교통 관제 시스템

---

## 1. 개요

TAS는 도심 교통 흐름을 실시간으로 모니터링·분석하는 **AI 기반 교통 관제 웹 애플리케이션**입니다.
CCTV 기반 번호판 자동 인식(ANPR), 구간별 혼잡도, 차량 통행 흐름, 이벤트 로그, 통계, 자동 알림 등 관제센터 수준의 기능을 단일 SPA로 제공합니다.

5개 부서별 대시보드(교통정보센터 / 교통분석팀 / 시설운영팀 / 단속관리팀 / 경영전략본부)와 공용 마케팅 페이지(메인 / 시스템 소개 / 고객지원 / 로그인 / 회원가입)로 구성됩니다.

---

## 2. 기술 스택

### Frontend
- **Vue 3** (Composition API, `<script setup>`)
- **Vue Router 4** — 라우트 전부 lazy import
- **Vite 5** — 코드 분할 빌드
- **ECharts 6** — 통계/혼잡도 차트 (트리쉐이킹된 setup으로 등록)
- **Leaflet 1.9** — 지도 + OSM 도로 폴리라인
- **hls.js 1.6** — HLS 라이브 스트림 lazy load
- **lucide-vue-next 1.0** — 아이콘 (Bootstrap Icons 병용)
- **axios 1.16** — HTTP 클라이언트 (Bearer 토큰 자동 주입)
- **bcryptjs 3.0** — 로컬 테스트 계정 비밀번호 해시

### 백엔드 (별도 리포)
- Spring Boot — 도메인 엔티티, 인증, REST API
- FastAPI — 실시간 도로 혼잡도 / OCR
- YOLO + OCR — 차량/번호판 탐지

---

## 3. 라우트

`src/router/index.js` 정의. 모든 라우트가 `() => import(...)` 방식의 lazy load.

| Path | View | 인증 | 비고 |
|---|---|---|---|
| `/` | MainView | public | 랜딩 |
| `/sub/intro` | IntroView | public | 시스템 소개 |
| `/sub/support` | SupportView | public | 공지사항 |
| `/login` | LoginView | public | |
| `/signup` | SignupView | public | |
| `/admin/control` | ControlView | admin | 교통정보센터 |
| `/admin/review` | ReviewView | admin | 단속관리팀 |
| `/admin/analytics` | AnalyticsView | admin | 교통분석팀 |
| `/admin/ops` | OpsView | admin | 시설운영팀 |
| `/admin/super` | SuperView | admin | 경영전략본부 (관리자 디폴트 진입점) |

`/admin/*` 라우트는 네비게이션 가드로 보호 — 비로그인 / 비관리자 접근 시 차단.

---

## 4. 부서 대시보드

### 4-1 교통정보센터 (ControlView)
탭: `center` · `cams` · `reports` · `settings`
- 중앙 지도(Leaflet + OSM 도로) + 우측 카메라 패널 + 하단 VMS 전광판 제어
- 헤더에 실시간 알림 벨, 가이드 버튼, 부서 전환 셀렉터
- 단속 전송 버튼 → `useViolationQueue`로 단속관리팀 큐에 push

### 4-2 단속관리팀 (ReviewView)
단일 페이지(탭 없음). 좌측 이벤트 목록 + 우측 상세(영상 캡처 + OCR + 이벤트 정보 + 2차 검증).
- 더미 4건 상시 노출 (백엔드 실패해도 화면 유지)
- OCR / 이벤트 정보 박스 5:5 가로 분할, 속도 항목 강조
- 일일 / 주간 / 기간 지정 보고서 다운로드

### 4-3 교통분석팀 (AnalyticsView)
탭: `dashboard` · `ctx` · `insight` · `cmp` · `map` · `settings`
- 분석 기준(`ctx`) → 인사이트(`insight`) → 구간 비교(`cmp`) → 지도(`map`) 흐름
- ECharts 라인/바/게이지/파이 사용

### 4-4 시설운영팀 (OpsView)
탭: `status` · `cams` · `srv` · `net` · `alarm` · `fault` · `settings`
- 카메라/서버/네트워크/장애 모니터링
- 임계값·점검 주기·현장 출동 설정

### 4-5 경영전략본부 (SuperView)
탭: `dashboard` · `perms` · `users` · `org` · `sys` · `audit` · `reports` · `ops` · `map` · `events` · `cams` · `ocr` · `stats` · `settings`
- 전 부서 KPI / 운영 현황 / 카메라 / OCR / 통계 통합 요약
- 권한·조직·감사 로그·시스템 설정 관리

---

## 5. 컴포저블 (`src/composables/`)

| 파일 | 역할 |
|---|---|
| `useAuth.js` | 로그인/회원가입/로그아웃, JWT 파싱, 로컬 테스트 계정 fallback |
| `useDashboardData.js` | 차량 카운트, OCR 레코드, 카메라 피드 (모의 데이터) |
| `useStats.js` | 통계 계산 (위반, 통행량) |
| `useTheme.js` | 테마 토글 (다크 모드 제거 후 stub로 유지) |
| `useOSMRoads.js` | OSM Overpass API 도로 geometry 로드 + 24h 캐시 |
| `useVideoUtils.js` | `captureFrameDataURL`, `seekVideo`, `enterFullscreen` 등 |
| `useVideoOptimize.js` | HLS.js 최적화 |
| `useViolationQueue.js` | localStorage 기반 부서간 위반 전송 큐 (관제 → 단속) |
| `useReportDownload.js` | 부서별 CSV 보고서 템플릿 + UTF-8 BOM |
| `echartsSetup.js` | ECharts 트리쉐이킹 setup (Line/Bar/Gauge/Pie + CanvasRenderer) |

---

## 6. 컴포넌트 (`src/components/`)

### 공용
- `AppNav.vue` — 메인 네비게이션
- `AppFooter.vue` — 푸터 (마케팅 페이지용)
- `AppFab.vue` — 플로팅 액션 버튼 (상단 이동)
- `AuthModal.vue` — 로그인/회원가입 모달
- `HeroStats.vue` — KPI 카운터
- `GuideOverlay.vue` / `GuideModal.vue` — 단계별 강조 + 말풍선 사용자 가이드

### 서포트 탭
- `BoardTab.vue` — 공지사항 게시판
- `QnaTab.vue` — Q&A
- `ChatTab.vue` — 실시간 키워드 매칭 채팅

### 대시보드용
- `dashboard/OverviewTab.vue` — KPI 통합
- `dashboard/CamerasTab.vue` — 카메라 그리드
- `dashboard/PlatesTab.vue` — OCR 레코드 테이블
- `dashboard/AlertsTab.vue` — 실시간 알림
- `dashboard/SideWeather.vue` — 사이드 날씨 위젯
- `dashboard/DeptSwitcher.vue` — 부서 전환 드롭다운

---

## 7. API / 백엔드 연결

### 환경 변수
```env
VITE_API_BASE_URL=http://localhost:8080       # Spring Boot
VITE_FASTAPI_BASE_URL=http://localhost:8000   # FastAPI (비어있으면 데모 모드)
```

### Axios 클라이언트 (`src/api/client.js`)
- 단일 axios 인스턴스
- localStorage `tas_access_token` 자동 Bearer 주입
- 헬퍼: `apiGet`, `apiPatch`

### 엔드포인트
| 경로 | 메서드 | 위치 |
|---|---|---|
| `/api/auth/signup` | POST | `useAuth.js` (fetch) |
| `/api/auth/login` | POST | `useAuth.js` (fetch) |
| `/api/speed-violations` | GET | `src/api/speedViolations.js` |
| `/api/speed-violations/{id}/status` | PATCH | `src/api/speedViolations.js` |

### 외부 API
- **Overpass API** (overpass-api.de 외 4개 미러) — OSM 도로 geometry, 24h localStorage 캐시
- **HLS 라이브 스트림** — hls.js로 lazy load, 클릭 전 다운로드 0

### 데모 모드
환경 변수 비어있으면 API 호출이 우회되고 컴포저블 내장 더미 데이터로 동작합니다. 단속관리팀 ReviewView도 백엔드 실패 시 더미 4건으로 폴백합니다.

---

## 8. 디렉터리 구조

```
trafficAS-b/
├── src/
│   ├── api/
│   │   ├── client.js                 # axios 인스턴스 + 토큰 주입
│   │   └── speedViolations.js        # 과속 위반 API
│   ├── views/
│   │   ├── MainView.vue              # 랜딩
│   │   ├── IntroView.vue             # 시스템 소개
│   │   ├── SupportView.vue           # 공지사항
│   │   ├── LoginView.vue
│   │   ├── SignupView.vue
│   │   └── admin/
│   │       ├── ControlView.vue       # 교통정보센터
│   │       ├── ReviewView.vue        # 단속관리팀
│   │       ├── AnalyticsView.vue     # 교통분석팀
│   │       ├── OpsView.vue           # 시설운영팀
│   │       └── SuperView.vue         # 경영전략본부
│   ├── components/
│   │   ├── AppNav.vue / AppFooter.vue / AppFab.vue
│   │   ├── AuthModal.vue / HeroStats.vue
│   │   ├── GuideOverlay.vue / GuideModal.vue
│   │   ├── BoardTab.vue / QnaTab.vue / ChatTab.vue
│   │   └── dashboard/
│   │       ├── OverviewTab.vue / CamerasTab.vue
│   │       ├── PlatesTab.vue / AlertsTab.vue
│   │       ├── SideWeather.vue / DeptSwitcher.vue
│   ├── composables/                  # 10개 (위 5절 참고)
│   ├── data/
│   │   ├── weather.js
│   │   └── guides/                   # 부서별 가이드 단계 데이터 5개
│   ├── styles/
│   │   ├── base.css                  # 전역 + 변수
│   │   ├── light.css                 # 라이트 모드
│   │   └── admin-shared.css          # 5개 부서 공용 스타일
│   └── router/
│       └── index.js                  # 라우트 + 가드
├── public/
│   ├── TAS.png / TAS.ico             # 로고
│   ├── main1.png / dashboard.png     # 메인/대시보드 일러스트
│   ├── sub3.png / hero-poster.jpg
│   ├── system_road_network_illustration.png
│   ├── hero-banner.mp4 / classify-video.mp4
│   ├── 1.mp4 / 1_web.mp4
│   └── road1.mp4 ~ road6.mp4         # 카메라 데모 영상
├── index.html
├── vite.config.js
└── package.json
```

---

## 9. 실행 방법

### 9-1 의존성 설치
```bash
npm install
```

### 9-2 환경 변수 (`.env`)
```env
VITE_API_BASE_URL=http://localhost:8080
VITE_FASTAPI_BASE_URL=http://localhost:8000
```
비워두면 자동으로 데모 모드.

### 9-3 개발 서버
```bash
npm run dev
# http://localhost:5173
```

### 9-4 프로덕션 빌드
```bash
npm run build
npm run preview
```

### 9-5 LAN 공유
```bash
npm run dev -- --host
# 출력의 Network: http://192.168.x.x:5173/ 공유
```

### 9-6 관리자 테스트 계정
```
이메일: admin@email.com
비밀번호: 1234
```
로그인 후 `/admin/super`로 진입, 좌상단 DeptSwitcher로 부서 전환.

---

## 10. 주요 기능 요약

### 5개 부서 대시보드
공통 셸: 사이드바(메뉴 + 사이드 날씨) + 상단 헤더(시계 + 자동 새로고침 + 알림 벨 + 가이드 + 부서 전환 + 사용자) + 본문 그리드.

### 단속관리팀 검토 워크플로
- 좌측 이벤트 목록 (날짜별 그룹, 페이지네이션)
- 우측 상세: 영상 캡처 + OCR(번호판 크롭/신뢰도) + 이벤트 정보(속도 메트릭 3종 강조) + 2차 검증(STEP 1~3)
- 검토 히스토리 자동 기록
- 일일/주간/기간 지정 CSV 다운로드

### 관제센터 → 단속관리팀 큐 패턴
관제센터 카메라 컨트롤바의 빨간 단속 전송 버튼 클릭 → 현재 프레임 캡처 + 메타데이터를 localStorage 큐에 push → 단속관리팀이 마운트 시 흡수해 상단에 `CTRL` 출처 배지로 표시.

### OCR 캡처 자동화
ReviewView에서 1.6초 구간 8프레임 샘플링 → 엣지 강도 휴리스틱으로 가장 선명한 프레임 자동 선택 (외부 라이브러리 0, ~40줄).

### 혼잡도 지도
- VWorld 다크 / CartoDB Dark Matter 폴백
- OSM Overpass 도로 geometry (4개 미러 순차 시도, 24h 캐시)
- 도로 등급별 굵기 차등, 한글 도로명 우선

### 실시간 알림 벨
헤더 종 아이콘 + 카운트 뱃지 + critical 시 빨간 펄스. 4개 admin 뷰가 공용 마크업/스타일 사용.

### 사용자 가이드 (GuideOverlay)
라이브러리 0개로 직접 구현한 강조 박스 + 말풍선 오버레이. `Teleport to body` + `box-shadow: 9999px`로 외곽 어둡게. 키보드(←/→/ESC) 지원.

---

## 11. 성능 최적화

### 11-1 라우트 + 컴포넌트 lazy load
모든 라우트 `() => import(...)`. 메인 페이지 첫 진입 시 admin 코드/ECharts/Leaflet 미다운로드.

### 11-2 ECharts 트리쉐이킹
`src/composables/echartsSetup.js`에서 사용 차트(Line/Bar/Gauge/Pie) + 컴포넌트만 등록 → 번들 ~53% 절감.

### 11-3 OSM 도로 24h localStorage 캐시
사용자 1명당 24시간에 1회만 Overpass 외부 API 호출.

### 11-4 hls.js lazy load
카메라 마커 클릭 전엔 hls.js 자체를 다운로드하지 않음.

### 11-5 메모리 누수 방지
모든 컴포저블/뷰의 `onUnmounted`에서 setInterval, 이벤트 리스너, ECharts dispose, Leaflet remove 명시적 정리.

---

## 12. 디자인 시스템

- **컬러 토큰** (`base.css`): `--bg / --bg2 / --bg3`, `--t / --t2 / --t3`, `--a / --ba / --glow`
- **폰트**: Pretendard Variable(한글), Syne(헤딩), IBM Plex Mono / JetBrains Mono(코드·라벨)
- **테마**: 라이트 모드 단일화 (다크 모드 제거, `useTheme` stub 유지)
- **로고**: `/TAS.png` 56px, admin 사이드바엔 `.brand-img` 공통 클래스

---

## 13. 인증

- `useAuth.js`가 fetch로 `/api/auth/{signup,login}` 호출
- 응답 JWT를 localStorage `tas_access_token`에 저장
- axios 클라이언트가 모든 요청에 자동 Bearer 주입
- 백엔드 부재 시 로컬 테스트 계정 4종(`super`, `analytics`, `ops`, `review`)으로 fallback
- 라우터 가드가 `/admin/*` 보호

---

## 14. 알려진 데모 모드 동작

- `.env`의 `VITE_FASTAPI_BASE_URL`이 비어있으면 도로 혼잡도 / OCR / 최근 인식 API 모두 우회되고 컴포저블 내장 더미 사용
- 단속관리팀 ReviewView는 API 실패 시에도 더미 4건 표시 (`DUMMY_REVIEW_EVENTS`)
- 모든 시각 표시는 `new Date()` 기반으로 동적 계산되어 어느 날 실행해도 "오늘 발생한 이벤트"처럼 보임

---

## 15. 운영 메모

- **백엔드 두 개**: Spring(8080)이 인증/위반 도메인, FastAPI(8000)가 실시간 혼잡도/OCR. 둘 중 하나만 띄워도 일부 화면 동작.
- **시연 시**: 백엔드 둘 다 꺼도 됨. 데모 모드가 자연스럽게 동작하는지 ReviewView/ControlView 빠르게 확인.
- **빌드 산출물**: 메인 페이지 진입 시 약 51KB gzip, 부서 대시보드 첫 진입 시 +400KB 안팎 (ECharts/Leaflet 포함).

---

## 16. 외부 링크

- GitHub: https://github.com/angela860807/Traffic_Analytics_Proposal
- 산출물(Notion): (링크 추가)
