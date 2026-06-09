# TAS-PM Frontend 작업 TODO

## 1. 목표와 담당

기존 교통 흐름·과속 화면은 유지하고, 운영자가 CCTV의 현재 상태, 악화 예측, 판단 근거, 정비 진행 상황을 한 흐름으로 처리하는 Vue 화면을 추가한다.

| 역할 | 담당 |
|---|---|
| 주 담당 | 최동윤 |
| 데이터·화면 검증 지원 | 박지영 |
| API 계약 협업 | 김승민 |

Vue 3 Composition API를 사용하며 view, component, composable, store, router, API client를 분리한다.

## 2. 화면 범위

```text
/admin/predictive
/admin/predictive/cameras/:cameraId
/admin/predictive/anomalies
/admin/predictive/anomalies/:eventId
/admin/predictive/maintenance
/admin/predictive/policies
```

`OPERATOR`, `MAINTAINER`, `ADMIN`만 진입할 수 있도록 route meta와 auth guard를 적용한다.

## 3. 권장 구조

```text
src/
  api/
    predictiveApi.js
  components/predictive/
    HealthStatusBadge.vue
    DataSourceBadge.vue
    CameraHealthTable.vue
    HealthMetricChart.vue
    PredictionRiskPanel.vue
    AnomalyEvidenceTable.vue
    TrafficContextPanel.vue
    TicketStatusControl.vue
  composables/
    usePredictiveQuery.js
    usePolling.js
  stores/
    predictiveStore.js
  views/admin/predictive/
    PredictiveDashboardView.vue
    CameraHealthDetailView.vue
    AnomalyEventListView.vue
    AnomalyEventDetailView.vue
    MaintenanceTicketView.vue
    AnomalyPolicyView.vue
```

실제 프로젝트의 현재 폴더 규칙과 이름이 다르면 기존 규칙을 우선한다.

## 4. API client

공유 axios 인스턴스를 사용한다. view 또는 component에서 직접 axios를 호출하지 않는다.

```text
GET    /api/v1/predictive/summary
GET    /api/v1/predictive/cameras
GET    /api/v1/predictive/cameras/{cameraId}/health-history
GET    /api/v1/predictive/traffic-context
GET    /api/v1/predictive/anomaly-events
GET    /api/v1/predictive/anomaly-events/{eventId}
POST   /api/v1/predictive/anomaly-events/{eventId}/acknowledge
POST   /api/v1/predictive/anomaly-events/{eventId}/resolve
POST   /api/v1/predictive/anomaly-events/{eventId}/dismiss
GET    /api/v1/predictive/maintenance-tickets
POST   /api/v1/predictive/maintenance-tickets
POST   /api/v1/predictive/maintenance-tickets/{ticketId}/assign
POST   /api/v1/predictive/maintenance-tickets/{ticketId}/status
GET    /api/v1/predictive/policies
PATCH  /api/v1/predictive/policies/{policyCode}
```

## 5. 화면별 TODO

### 5-1. 예지보전 대시보드

- [ ] 정상·저하·위험·오프라인·기준선 학습 중 카메라 수 표시
- [ ] 활성 이상, 악화 예측, SLA 초과 티켓 표시
- [ ] MTTA·MTTR 표시
- [ ] Health Score 오름차순 카메라 목록 제공
- [ ] 최근 예측 위험과 CRITICAL 이벤트 우선 표시
- [ ] `dataSource` 필터 기본값을 `REAL`로 설정
- [ ] 30초 polling, 탭 비활성 시 중단
- [ ] `loading`, `empty`, `error`, `stale` 상태 구현

완료 조건:

- 운영자가 30초 안에 우선 점검 카메라와 미처리 티켓을 식별할 수 있다.
- 비실제 데이터에 `SIMULATED`, `FAULT_INJECTED`, `MOCK` 배지가 보인다.

### 5-2. 카메라 상세

- [ ] 카메라 기본 정보와 현재 Health Score 표시
- [ ] FPS, frame drop, latency, blur, OCR 실패율, CPU·메모리, RTT 시계열 표시
- [ ] 기준선 median과 WARNING·CRITICAL 임계선 표시
- [ ] 최근 15분과 향후 10분 예측선을 구분 표시
- [ ] `BASELINE_LEARNING`이면 현재·필요 표본 수 표시
- [ ] 동일 시간대 교통 맥락과 인접 카메라 차량 수 표시
- [ ] 활성 이상 이벤트와 티켓으로 이동 링크 제공

차트 정책:

- 실측은 실선, 기준선은 점선, 예측은 별도 색상의 점선으로 표시한다.
- 데이터가 없는 구간을 0으로 연결하지 않는다.
- tooltip에 시간, 관측값, 기준값, 임계값, 출처를 표시한다.

### 5-3. 이상 이벤트 목록

- [ ] 카메라, 유형, 심각도, 상태, 탐지 방식, 출처, 시간 필터
- [ ] 페이지·정렬 상태를 URL query와 동기화
- [ ] `TREND_PROJECTION` 이벤트에 `악화 예측` 표시
- [ ] 예상 임계치 도달까지 남은 시간 표시
- [ ] unknown Enum fallback 구현
- [ ] 필터 초기화 제공

### 5-4. 이상 이벤트 상세

- [ ] 관측값·기준값·임계값 비교
- [ ] robust z-score와 추세 기울기·신뢰도 표시
- [ ] 예상 임계치 도달 시각과 예측 구간 표시
- [ ] detector 이름·버전·정책 코드 표시
- [ ] 교통 맥락 교차검증 결과 표시
- [ ] 원인 후보와 운영자 확정 원인 구분
- [ ] 이벤트 확인, 해결, 오탐 종료 modal 구현
- [ ] 연결된 정비 티켓 표시

오탐 종료와 해결은 사유·조치 내용이 없으면 제출할 수 없다.

### 5-5. 정비 티켓

- [ ] P1·P2·P3, 상태, 담당자 필터
- [ ] SLA 초과와 남은 시간 표시
- [ ] 담당자 배정
- [ ] 허용 상태 전이만 노출
- [ ] `RESOLVED` 전환 시 조치 메모 필수
- [ ] 변경 이력 timeline 표시
- [ ] MTTA·MTTR 표시

Kanban은 목록과 상태 전이가 완성된 뒤 선택 구현한다.

### 5-6. 정책 관리

- [ ] 정책 코드, 이상 유형, 탐지 방식, 임계치, 활성 상태 표시
- [ ] 숫자 범위와 필수값 validation
- [ ] Rule, z-score, 추세 정책별 입력 항목 분리
- [ ] 수정 전 확인 modal
- [ ] 성공 후 서버 데이터를 재조회
- [ ] `ADMIN` 외 수정 UI 비활성화

## 6. 공통 상태·오류 정책

- API별 `loading`, `error`, `empty`를 명시한다.
- 중복 제출을 방지하도록 mutation 중 버튼을 비활성화한다.
- `401`은 로그인 만료, `403`은 권한 부족, `409`는 중복·상태 충돌 메시지를 표시한다.
- 서버 `fieldErrors`를 해당 입력에 연결한다.
- polling 실패 시 기존 데이터를 지우지 않고 stale 상태로 표시한다.
- 날짜 query는 offset이 포함된 ISO-8601로 전송한다.

## 7. 테스트

- [ ] API client URL·query·payload 단위 테스트
- [ ] route guard 역할별 테스트
- [ ] 대시보드 loading·empty·error 테스트
- [ ] 이벤트 필터와 URL 동기화 테스트
- [ ] 티켓 상태 전이·권한 테스트
- [ ] 예측 이벤트의 남은 시간 표시 테스트
- [ ] unknown Enum·null metric 렌더링 테스트
- [ ] 실제·시험 데이터 출처 배지 테스트

통합 시나리오:

1. FPS 악화 예측 이벤트가 목록에 표시된다.
2. 상세에서 추세와 교통 맥락 근거를 확인한다.
3. 운영자가 이벤트를 확인하고 담당자를 배정한다.
4. 정비 담당자가 작업을 시작하고 해결 메모를 남긴다.
5. 운영자가 티켓을 종료한다.

## 8. 일정

| 날짜 | 작업 |
|---|---|
| 6/9 | API 계약 확정, route·API client 골격 |
| 6/10~6/11 | 대시보드·카메라 상세 |
| 6/12~6/13 | 이상 목록·상세 |
| 6/14~6/15 | 티켓·정책 화면 |
| 6/16 | 권한·오류·반응형·접근성 |
| 6/17 | 장애 주입 통합 시나리오 |
| 6/18 | 회귀 테스트·발표 데이터 점검 |
| 6/19 | 버퍼·최종 시연 |

## 9. 완료 조건

- [ ] 6개 route가 동작한다.
- [ ] 모든 API 호출이 공유 client를 통한다.
- [ ] URL query, 권한, loading·empty·error 상태가 명시적이다.
- [ ] 교통 맥락이 CCTV 판단 보조 정보로 표현된다.
- [ ] 혼잡 상황이 정비 장애처럼 표시되지 않는다.
- [ ] Rule·통계·추세 이벤트의 근거가 구분된다.
- [ ] 이벤트부터 티켓 종료까지 시연할 수 있다.
