# TrafficAS — AI 기반 실시간 교통 관제 시스템

## 1. 프로젝트 개요

TrafficAS는 도심 교통 흐름을 실시간으로 모니터링하고 분석하는 **AI 기반 교통 관제 웹 애플리케이션**입니다.
CCTV 기반 번호판 자동 인식(ANPR), 구역별 혼잡도 히트맵, 차량 통행(진입/이탈) 흐름 분석, 이벤트 로그, 통계 분석, 자동 알림 등
실무 교통 관제 센터 수준의 기능을 단일 대시보드에서 제공합니다.

---

## 2. 프로젝트 구조 (Architecture)

본 프로젝트는 **Vue 3 + Vite 기반 SPA(Single Page Application)** 구조로 개발되었습니다.

- **Frontend:** Vue 3 (`<script setup>` Composition API) + Vue Router 4
- **실시간 통신:** WebSocket (`ws://localhost:8000/ws`) — 차량 감지 데이터 수신
- **백엔드 API:** FastAPI (`VITE_FASTAPI_BASE_URL`) — 혼잡도 데이터, 카메라 통계 등
- **AI 채팅:** Groq API (LLaMA 3.3-70B) 기반 교통 관제 어시스턴트
- **시각화:** ECharts (혼잡도/도넛/통계 차트), Leaflet (지도/히트맵), Canvas/SVG
- **드래그 재배치:** vuedraggable (SortableJS 기반)
- **배포:** Vite 정적 빌드 → 웹 서버 배포

### 연결 방식

```
브라우저 (Vue 3 SPA)
    │
    ├── WebSocket ──→ 백엔드 서버 (ws://localhost:8000/ws)
    │                  └── YOLO-ITS CCTV 감지 데이터
    │
    ├── REST API ───→ FastAPI 서버
    │                  └── 차량 통행 흐름 / 혼잡도 / 카메라 통계
    │
    └── Groq API ──→ LLaMA 3.3-70B
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
- Vue Router 4
- Vite 5
- ECharts 6 (혼잡도/도넛/통계 차트)
- Leaflet 1.9 + OpenStreetMap / CartoDB Dark Matter / VWorld 다크 타일
- vuedraggable 4 (드래그 재배치)
- Bootstrap Icons 1.11.3 (CDN)
- Pretendard Variable, JetBrains Mono (폰트)

### 6-2 실시간 / AI

- WebSocket (YOLO-ITS CCTV 연동)
- FastAPI REST 호출 (`/api/v1/road-congestion` 등)
- Groq API — LLaMA 3.3-70B-Versatile
- HTMLVideoElement (실시간 CCTV 영상 6분할)

### 6-3 인증 / 상태 관리

- LocalStorage 기반 사용자 인증
- Vue Composables (`useAuth`, `useTheme`, `useDashboardData`)
- 대시보드 카드 순서도 LocalStorage 저장 (편집 모드)
- Vue Router Navigation Guard (관리자 전용 라우트 보호)

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
    ├── Vue Router ──→ / (메인) / /intro / /usage / /login / /signup / /dashboard
    │
    ├── useAuth.js ───────→ LocalStorage (사용자 세션)
    ├── useDashboardData ─→ 공유 상태 (KPI / OCR / 카메라 / 설정)
    │
    ├── WebSocket ────→ ws://localhost:8000/ws
    │                     └── 실시간 차량 / 번호판 데이터
    │
    ├── FastAPI ──────→ ${VITE_FASTAPI_BASE_URL}/api/v1/...
    │                     └── 혼잡도 / 카메라 통계 / 흐름 분석
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

### 9-3 개발 서버 실행

```bash
npm run dev
```

### 9-4 프로덕션 빌드

```bash
npm run build
npm run preview
```

### 9-5 웹 접속

```
http://localhost:5173
```

### 9-6 관리자 계정

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
│   │   ├── MainView.vue              # 메인 소개 페이지
│   │   ├── IntroView.vue             # 서비스 소개
│   │   ├── UsageView.vue             # 이용 방법
│   │   ├── LoginView.vue             # 로그인
│   │   ├── SignupView.vue            # 회원가입
│   │   ├── SupportView.vue           # 고객지원
│   │   └── RoadDashboardView.vue     # 관리자 대시보드 (셸 + 오버뷰 탭)
│   │
│   ├── components/
│   │   ├── AppNav.vue                # 공통 네비게이션
│   │   ├── AppFab.vue                # 플로팅 버튼 (채팅/테마/상단이동)
│   │   ├── AuthModal.vue             # 로그인/회원가입 모달
│   │   ├── ChatTab.vue               # AI 채팅 (Groq API)
│   │   ├── BoardTab.vue              # 커뮤니티 게시판
│   │   ├── QnaTab.vue                # Q&A
│   │   ├── HeroStats.vue             # 메인 히어로 통계
│   │   │
│   │   └── dashboard/
│   │       ├── MonitoringTab.vue     # 실시간 카메라 상세 모니터링 (인식률/FPS/신뢰도)
│   │       ├── EventsTab.vue         # 이벤트 로그 + 등급별 필터
│   │       ├── SearchTab.vue         # 차량/번호판 검색
│   │       ├── StatsTab.vue          # 통계 분석 (ECharts 4종)
│   │       └── SettingsTab.vue       # 시스템 설정 (알림/임계값/중복제거)
│   │
│   ├── composables/
│   │   ├── useAuth.js                # 인증 상태 관리
│   │   ├── useTheme.js               # 다크/라이트 테마
│   │   ├── useStats.js               # 메인 페이지 통계
│   │   └── useDashboardData.js       # 대시보드 공유 상태 (KPI/OCR/카메라/설정)
│   │
│   └── router/
│       └── index.js                  # 라우터 + 네비게이션 가드
│
├── public/                           # 정적 파일 (road1.mp4~road8.mp4 등)
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
- **검색** — 차량 번호 / 카메라 / 흐름 방향 / 신뢰도로 차량 검색
- **통계** — 요일별 통행량, 시간대별 진입/이탈 추이, 도로별 정체, 카메라별 비교 (ECharts)
- **설정** — 알림 / 임계값 / 중복 제거 정책 / 시스템 정보

### 11-2 차량 통행 (IN / OUT) 분석

- KPI: 총 감지 / 진입(IN) / 이탈(OUT) / 혼잡도
- 차량 통행 분석 카드: 진입·이탈 카운트 + 12시간 추이 스파크라인 + 중복 제거 안내
- OCR 로그에 흐름 방향(진입/이탈) 컬럼 표시
- 통계 탭에 시간대별 IN/OUT 추이 + 카메라별 IN/OUT 비교 차트

### 11-3 번호판 인식 (ANPR)

- 실시간 OCR 인식 결과 (번호판 시각화 + 6항목 메타정보)
- 최근 5건 썸네일
- OCR 로그 테이블 (시간/카메라/번호/방향/신뢰도)
- 중복 제거 정책 설정 (간격, 방향 분리, WebSocket 알림)

### 11-4 실시간 카메라 모니터링

- 메인 대시보드: 6분할 3×2 그리드 (실시간 영상)
- 모니터링 탭: 카메라별 상세 패널
  - LIVE 도트 (펄스 애니메이션) + CAM-ID
  - 영상 위 OCR 신뢰도 프로그레스 바
  - 인식률 / 검출 수 / FPS / 가동 시간
  - 카메라 클릭 시 풀스크린 모달

### 11-5 혼잡도 히트맵 (Leaflet)

- Leaflet + CartoDB Dark Matter 타일 (메인) / VWorld 다크 폴백
- 다층 글로우 펄스 라이프 마커 (12개 핫스팟)
- 혼잡 지점 드롭다운 → 클릭 시 `flyTo` 부드러운 이동
- 전체 보기 — CSS 토글 방식 (검은 화면 없음)
- 줌 한계 설정 (`minZoom: 10`, `maxZoom: 20`, `maxNativeZoom`)

### 11-6 날씨 / 대기 환경 패널 (사이드바 상단)

- 강남구 → 서초구 → 송파구 5초마다 자동 슬라이드 (수동 클릭도 가능)
- 9가지 날씨 프리셋 (맑음/구름/비/눈/뇌우/안개/미세먼지 등) + 한국어 라벨
- 미세먼지 / 초미세먼지 / 오존 등급 색상 (좋음/보통/나쁨/매우나쁨)
- 확대 모달: 3개 구 가로 카드 + 내일 예보 (최고/최저, 강수확률, 미세먼지)

### 11-7 알림 시스템

- 헤더 종 아이콘 + 카운트 뱃지
- 알림 패널: 12건 표시 + 편집 모드 (개별 X 삭제 / 전체 삭제)
- 외부 클릭 시 자동 닫힘

### 11-8 카드 드래그 재배치 (편집 모드)

- 헤더 **편집** 버튼 토글
- 4개 영역 드래그 가능:
  - 사이드바 2개 (날씨 / 카메라 그룹)
  - KPI 4개
  - Row 2 우측 2개 (시간대별 혼잡도 ↔ 차량 통행 분석)
  - Row 3 3개 (OCR / HeatMap / 카메라 상태)
- `localStorage` 자동 저장 (새로고침 후에도 유지)
- 버튼/입력/지도 영역은 `filter` 옵션으로 드래그 제외

### 11-9 AI 교통 어시스턴트

- Groq API (LLaMA 3.3-70B) 기반 한국어 전용 챗봇
- 교통 관제 특화 시스템 프롬프트

---

## 12. 기대 효과

- 교통 관제 정보 통합 제공으로 대응 속도 향상
- CCTV 기반 번호판 자동 인식 + 진입/이탈 흐름 분석으로 수동 모니터링 부담 감소
- 실시간 혼잡도 알림으로 선제적 교통 관리 가능
- 카드 드래그 재배치로 관제관 선호에 맞는 UI 커스터마이즈
- 날씨/대기 환경 통합으로 교통 영향 요인 동시 모니터링
- Vue 3 + Composable 컴포넌트 기반 확장 가능한 구조

---

## 13. 향후 개선 사항

- 실제 YOLO 모델 + FastAPI 연동 (`VITE_FASTAPI_BASE_URL` 설정 시 자동 동작)
- 카카오/VWorld API 키 정식 등록으로 한국어 라벨 강화
- 사용자별 알림 구독 설정
- 모바일 반응형 대시보드
- 데이터 내보내기 (CSV / PDF 리포트)
- 다중 관제 센터 지원
- 차량 이동 이력 추적 (camera-to-camera 경로 시각화)

---
