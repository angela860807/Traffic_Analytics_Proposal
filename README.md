# TrafficAS — AI 기반 실시간 교통 관제 시스템

## 1. 프로젝트 개요

TrafficAS는 도심 교통 흐름을 실시간으로 모니터링하고 분석하는 **AI 기반 교통 관제 웹 애플리케이션**입니다.  
CCTV 기반 번호판 자동 인식(ANPR), 구역별 혼잡도 히트맵, 이벤트 로그, 통계 분석, 자동 알림 등  
실무 교통 관제 센터 수준의 기능을 단일 대시보드에서 제공합니다.

---

## 2. 프로젝트 구조 (Architecture)

본 프로젝트는 **Vue 3 + Vite 기반 SPA(Single Page Application)** 구조로 개발되었습니다.

- **Frontend:** Vue 3 (`<script setup>` Composition API) + Vue Router 4
- **실시간 통신:** WebSocket (`ws://localhost:8000/ws`) 연동 — 차량 감지 데이터 수신
- **AI 채팅:** Groq API (LLaMA 3.3-70B) 기반 교통 관제 AI 어시스턴트
- **시각화:** Canvas 2D API (차트, 도로 애니메이션), SVG (도넛 차트)
- **배포:** Vite 정적 빌드 → 웹 서버 배포

### 연결 방식

```
브라우저 (Vue 3 SPA)
    │
    ├── WebSocket ──→ 백엔드 서버 (ws://localhost:8000/ws)
    │                  └── YOLO-ITS CCTV 감지 데이터
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



## 5. 프로젝트 소개

도심 교통 혼잡은 시민 생활과 물류에 직접적인 영향을 미치지만, 관제 정보가 분산되어 있어 통합 모니터링이 어렵다는 문제가 있습니다.

본 프로젝트는 이러한 문제를 해결하기 위해 **CCTV 기반 실시간 차량 감지 데이터를 통합하여 한 화면에서 교통 상황을 파악할 수 있는 관제 대시보드**를 개발하였습니다.

관리자는 웹 브라우저를 통해 실시간 도로 현황, 번호판 인식 로그, 이벤트 감지, 통계 데이터를 확인할 수 있으며, AI 어시스턴트를 통해 자연어로 교통 정보를 조회할 수 있습니다.

---

## 6. 기술 스택

### 6-1 Frontend

- Vue 3 (Composition API, `<script setup>`)
- Vue Router 4
- Vite 5
- Canvas 2D API
- CSS Custom Properties (다크/라이트 테마)
- IBM Plex Mono, Pretendard Variable (폰트)

### 6-2 실시간 / AI

- WebSocket (YOLO-ITS CCTV 연동)
- Groq API — LLaMA 3.3-70B-Versatile
- Canvas requestAnimationFrame (도로 애니메이션)

### 6-3 인증 / 상태 관리

- LocalStorage 기반 사용자 인증
- Vue Composables (useAuth, useTheme)
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
    ├── useAuth.js ──→ LocalStorage (사용자 세션)
    │
    ├── WebSocket ──→ ws://localhost:8000/ws
    │                   └── 실시간 차량 / 번호판 데이터
    │
    └── Groq API ──→ LLaMA 3.3-70B
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
│   │   ├── MainView.vue         # 메인 소개 페이지
│   │   ├── IntroView.vue        # 서비스 소개
│   │   ├── UsageView.vue        # 이용 방법
│   │   ├── LoginView.vue        # 로그인
│   │   ├── SignupView.vue       # 회원가입
│   │   ├── SupportView.vue      # 고객지원
│   │   └── DashboardView.vue    # 관리자 대시보드 (쉘)
│   │
│   ├── components/
│   │   ├── AppNav.vue           # 공통 네비게이션
│   │   ├── AppFab.vue           # 플로팅 버튼 (채팅, 테마, 상단이동)
│   │   ├── AuthModal.vue        # 로그인/회원가입 모달
│   │   ├── ChatTab.vue          # AI 채팅 (Groq API)
│   │   ├── BoardTab.vue         # 커뮤니티 게시판
│   │   ├── QnaTab.vue           # Q&A
│   │   ├── HeroStats.vue        # 메인 히어로 통계
│   │   │
│   │   └── dashboard/
│   │       ├── OverviewTab.vue  # 도로 현황 (Canvas 애니메이션)
│   │       ├── PlatesTab.vue    # 번호판 인식 로그
│   │       ├── EventsTab.vue    # 이벤트 로그 타임라인
│   │       ├── StatsTab.vue     # 통계 분석 (Canvas 차트)
│   │       └── AlertsTab.vue    # 알림 관리
│   │
│   ├── composables/
│   │   ├── useAuth.js           # 인증 상태 관리
│   │   └── useTheme.js          # 다크/라이트 테마
│   │
│   ├── utils/
│   │   └── levelColor.js        # 심각도별 색상 유틸
│   │
│   └── router/
│       └── index.js             # 라우터 + 네비게이션 가드
│
├── public/                      # 정적 파일 (road1.mp4 등)
├── index.html
├── vite.config.js
└── package.json
```

---

## 11. 주요 기능

### 11-1 실시간 도로 현황 (Overview)

- Canvas 기반 도로 세그먼트 애니메이션 (차량 이동 시뮬레이션)
- 구간별 속도 / 혼잡도 실시간 표시 (원활 / 지체 / 혼잡)
- KPI 카드 (감지 차량, 평균 속도, 입출차, 혼잡지수)
- 풀스크린 CCTV 영상 모달

### 11-2 번호판 인식 (ANPR)

- 실시간 번호판 인식 로그 테이블
- 최신 캡처 히어로 카드 (노란 번호판 스타일)
- 방향(IN/OUT), 카메라, 신뢰도 표시
- 번호판 검색 기능

### 11-3 이벤트 로그

- 타임라인 형식 이벤트 목록 (교통사고, 도로공사, 차량고장 등)
- 심각도별 색상 구분 (긴급 / 주의 / 일반)
- 긴급 이벤트 pulse 애니메이션
- 유형별 집계 / SVG 도넛 차트

### 11-4 통계 분석

- 시간대별 통행량 Canvas 차트 (Bezier 곡선)
- 구역별 혼잡도 히트맵
- 실시간 집계 패널

### 11-5 알림 시스템

- 혼잡도 임계값 자동 감지 → 알림 자동 누적
- 심각도별 SVG 도넛 분포 차트
- 슬라이더 기반 임계속도 설정 (혼잡 / 지체)
- 팝업 알림 (우하단, 5초 자동 소멸)

### 11-6 AI 교통 어시스턴트

- Groq API (LLaMA 3.3-70B) 기반 한국어 전용 챗봇
- 교통 관제 특화 시스템 프롬프트

---

## 12. 기대 효과

- 교통 관제 정보 통합 제공으로 대응 속도 향상
- CCTV 기반 번호판 자동 인식으로 수동 모니터링 부담 감소
- 실시간 혼잡도 알림으로 선제적 교통 관리 가능
- Vue 3 컴포넌트 기반 확장 가능한 구조

---

## 13. 향후 개선 사항

- 실제 YOLO 모델 연동 및 실시간 스트리밍 영상 표시
- 지도 기반 구역 시각화 (Kakao Map / Leaflet)
- 사용자별 알림 구독 설정
- 모바일 반응형 대시보드
- 데이터 내보내기 (CSV / PDF 리포트)
- 다중 관제 센터 지원

---
