# Next Context TODO - Predictive Maintenance Merge

## 2026-06-19 현행화 요약

현재 확인된 완료 범위:

- Spring 운영 API 10개 구현 완료
  - `GET /api/v1/predictive/anomaly-events`
  - `GET /api/v1/predictive/anomaly-events/{eventId}`
  - `POST /api/v1/predictive/anomaly-events/{eventId}/acknowledge`
  - `POST /api/v1/predictive/anomaly-events/{eventId}/resolve`
  - `POST /api/v1/predictive/anomaly-events/{eventId}/dismiss`
  - `GET /api/v1/predictive/maintenance-tickets`
  - `POST /api/v1/predictive/maintenance-tickets`
  - `POST /api/v1/predictive/maintenance-tickets/{ticketId}/assign`
  - `POST /api/v1/predictive/maintenance-tickets/{ticketId}/status`
  - `PATCH /api/v1/predictive/policies/{policyCode}`
- `GET /api/v1/predictive/summary?dataSource=REAL` 500 수정 완료
  - PostgreSQL nullable `zoneId` 타입 추론 문제 해결
  - `calculateHealthScore` null metric NPE 해결
  - `INSUFFICIENT_DATA` 카메라를 `baselineLearningCameras` 집계에 포함
- 사용자 확인 결과:
  - summary 응답 정상
  - `totalCameras=1`, `baselineLearningCameras=1`
  - 프론트 `/admin/ops` 설정 탭에서 ADMIN 정책 임계값 수정 가능 확인
- 프론트 1차 병합 보정 완료
  - `/admin/ops` 라우터 권한: `OPERATOR`, `MAINTAINER`, `ADMIN` 진입 허용
  - JWT role 파싱: `ROLE_ADMIN` 같은 접두어 role 정규화
  - 정책 수정 권한: `canEditPolicy` 연결
  - 공통 `DataState.vue` 추가
- `/admin/ops` 실제 API 1차 바인딩 완료
  - summary KPI는 `GET /api/v1/predictive/summary` 우선 사용
  - cameras 목록은 `GET /api/v1/predictive/cameras` 결과를 기존 화면 모델로 변환
  - policies 목록/수정 후 재조회는 `GET /api/v1/predictive/policies` 결과를 UI 기본값과 병합
- 터미널 테스트 한글 표시 방식 정리 완료
  - API 필드는 계약 유지상 영어 camelCase 유지
  - PowerShell `Select-Object @{Name='한글명';Expression={...}}` 방식으로 표시만 한글화

현행 기준 남은 작업:

1. `/admin/ops` anomaly/ticket 실제 API 데이터 바인딩
   - anomaly-events, maintenance-tickets를 `predictiveApi.js` 호출 결과로 교체
   - loading/empty/error 상태는 `DataState.vue`로 통일
   - pagination/sort/filter는 route query와 동기화

2. anomaly/ticket mutation 프론트 연결
   - acknowledge/resolve/dismiss 버튼을 실제 API에 연결
   - maintenance ticket 생성/배정/상태 변경을 실제 API에 연결
   - 성공 후 목록/detail 재조회
   - 409/403/400 에러 메시지 표시

3. 실제 시연 데이터 준비
   - REAL 데이터는 현재 카메라 1대가 데이터 부족/기준선 학습 상태로만 확인됨
   - 이상 이벤트, evidence, prediction log, maintenance ticket이 생기는 샘플 ingest 경로 확인 필요
   - FastAPI -> Spring evaluation -> anomaly event/ticket 생성까지 Docker compose E2E 확인 필요

4. Event/Ticket lifecycle 고도화
   - 정상 3회 연속 감지 후 `RECOVERED` 자동 전환
   - `RECOVERED` 후 재발 시 recurrence 증가 및 `OPEN` 복귀
   - WARNING 지속/반복 기반 P2 티켓 자동 생성
   - MTTA/MTTR 계산을 summary에 반영

5. Baseline/TrafficContext 고도화
   - 계약서의 요일/30분 시간대 bucket 기준 baseline 정교화
   - `camera_links` 기반 인접 카메라 교차검증 데이터 채우기
   - `Direction.BOTH` 집계 정책 확정
   - 빈 window에 `INSUFFICIENT` row를 만들지 여부 결정

6. 테스트 보강
   - Spring operations API service/controller 테스트
   - Rule/degradation orchestration 테스트
   - SHADOW 후보가 event/ticket을 만들지 않는 테스트
   - TrafficContext aggregation 통합 테스트
   - Frontend predictive API/client/route guard/OpsView mutation 테스트

7. Demo profile 정리
   - `application-demo.yml`
   - `ddl-auto=validate`
   - seed 재실행 없이 migration 기반 기동
   - demo 시연 전 DB volume 초기화/유지 정책 결정

작성일: 2026-06-18

## 1. 현재 병합 상태

빌드 상태:

- 사용자가 전체 build 완료.
- Codex 검증 기준으로는 Spring `compileJava`, FastAPI 관련 파일 `py_compile` 통과.
- 로컬 Python 기본 환경에는 `pytest`가 없어 FastAPI pytest는 미실행.

계약서 기준 완료된 핵심 범위:

- DB 007/008 predictive maintenance schema와 seed 기반 엔티티/DTO는 들어와 있음.
- Spring `POST /internal/v1/camera-health-samples` 구현.
- Spring 상태 샘플 upsert 후 Rule 평가 orchestration 구현.
- Spring dashboard 조회 API 일부 구현:
  - `GET /api/v1/predictive/summary`
  - `GET /api/v1/predictive/cameras`
  - `GET /api/v1/predictive/cameras/{cameraId}/health-history`
  - `GET /api/v1/predictive/traffic-context`
  - `GET /api/v1/predictive/policies`
- Spring 5분 교통 컨텍스트 집계 구현.
- Spring degradation orchestration 구현.
- Spring SHADOW 후보 저장을 `model_prediction_logs`로 제한.
- Spring CRITICAL ACTIVE 후보의 P1 `MaintenanceTicket` 자동 생성.
- FastAPI Rule/degradation adapter를 실제 `predictive_ml` 계약에 맞게 변환.
- FastAPI Rule 정책 필드를 계약서 ver2 기준으로 정리:
  - `warningConsecutiveWindows`
  - `criticalConsecutiveWindows`

## 2. 계약서 대조 결과

### 2-1. 일치 확인

API:

- `POST /internal/v1/camera-health-samples`: Spring 구현됨.
- `POST /internal/v1/anomaly-detection/camera-health/evaluate`: FastAPI 구현 및 Spring client 호출 경로 일치.
- `POST /internal/v1/anomaly-detection/camera-degradation/evaluate`: FastAPI 구현 및 Spring client 호출 경로 일치.
- `shadowCandidates`는 운영 event/ticket 생성 경로와 분리됨.

DB:

- `camera_health_samples` upsert 사용.
- `traffic_context_samples` 5분 집계 및 `ON CONFLICT` upsert 사용.
- `model_prediction_logs`에 SHADOW 결과 저장.
- `maintenance_ticket_number_seq`로 티켓 번호 생성.

ML 계약:

- `predictive_ml` 내부 dataclass는 snake_case metric key를 사용한다.
- Spring -> FastAPI 요청의 `recentHealthSamples`는 API 계약처럼 camelCase.
- Spring -> FastAPI 요청의 `baseline.metrics`는 현재 `fps_avg` 같은 ML 내부 metric key로 전달한다. FastAPI schema는 `dict[str, BaselineMetric]`라 수용 가능하고, detector 입력에는 이 형태가 맞다.

### 2-2. 주의할 불일치 또는 축소 구현

- 기준선 산출은 현재 최근 14일 전체 정상 샘플 median/MAD 기준이다. 계약서의 “동일 30분 시간대 bucket”까지는 아직 정밀 구현되지 않았다.
- degradation 평가에는 현재 `CAMERA_TREND_PROJECTION_V1` 정책 하나를 대표 policy로 넣는다. robust z-score 후보 policy code는 저장 시 fallback 처리한다.
- TrafficContext 집계에서 `Direction.BOTH`는 `in_count/out_count` 어디에도 더하지 않는다. 실제 의미에 따라 `BOTH`를 양쪽 집계에 넣을지 결정해야 한다.
- 교통 맥락 자체로 event/ticket을 만들지 않는 요구사항은 지켜졌다.
- P1 티켓 자동 생성은 `CRITICAL` 후보 기준으로 구현했다. `WARNING 15분 지속`, `24시간 내 3회 재발`, `10분 내 CRITICAL 예측` 기반 P2 생성은 아직 없다.

## 3. 다음 구현 TODO

### 3-1. Spring Boot API

우선순위 높음:

- `GET /api/v1/predictive/anomaly-events`
- `GET /api/v1/predictive/anomaly-events/{eventId}`
- `POST /api/v1/predictive/anomaly-events/{eventId}/acknowledge`
- `POST /api/v1/predictive/anomaly-events/{eventId}/resolve`
- `POST /api/v1/predictive/anomaly-events/{eventId}/dismiss`
- `GET /api/v1/predictive/maintenance-tickets`
- `POST /api/v1/predictive/maintenance-tickets`
- `POST /api/v1/predictive/maintenance-tickets/{ticketId}/assign`
- `POST /api/v1/predictive/maintenance-tickets/{ticketId}/status`
- `PATCH /api/v1/predictive/policies/{policyCode}`

구현 기준:

- Controller, Service, Repository, DTO 계층 분리.
- JPA entity 직접 노출 금지.
- 상태 전이 validation과 권한 검사는 서비스에서 명시.
- 목록 API는 page/size/sort whitelist 유지.

### 3-2. Event/Ticket Lifecycle

우선순위 높음:

- `OPEN -> ACKNOWLEDGED -> RECOVERED -> RESOLVED` 또는 기존 enum 기준으로 계약서와 상태 모델 재확정.
- 정상 3회 연속 감지 시 `RECOVERED` 처리.
- `RECOVERED` 상태에서 30분 내 재발 시 `OPEN` 복귀와 recurrence 증가.
- `WARNING` 지속/반복 기반 P2 티켓 자동 생성.
- `MaintenanceTicketHistory` append-only 기록.
- MTTA/MTTR 계산을 summary에 반영.

주의:

- 현재 CRITICAL은 P1 자동 생성만 구현되어 있다.
- 같은 `anomaly_event_id`에는 티켓을 중복 생성하지 않는다.

### 3-3. Baseline/Degradation

우선순위 중간:

- 계약서의 “동일 30분 시간대 14일 기준선”으로 baseline query 정밀화.
- baseline sample count가 부족하면 FastAPI 호출 전 `BASELINE_LEARNING` 처리할지 정책 결정.
- Trend Projection에는 마지막 15분, LSTM에는 전체 60분 sequence를 명시적으로 분리.
- 인접 카메라 교통량을 `camera_links` 기준으로 `adjacentCameraVehicleCounts`에 채우기.
- robust z-score와 trend projection policy code 저장 정책을 명확화.

### 3-4. TrafficContext

우선순위 중간:

- `Direction.BOTH` 집계 정책 결정.
- 원천 event ID 범위, 처리 건수, scheduler 소요 시간 로그 보강.
- 빈 window에도 `INSUFFICIENT` row를 만들지 여부 결정.
- `dataSource=SIMULATED` demo 집계 실행 경로 추가 여부 결정.

### 3-5. FastAPI/ML

우선순위 중간:

- 실제 의존성 환경에서 `pytest fastapi-server/tests/predictive/test_predictive_adapter.py` 실행.
- AI fixture로 Rule/degradation/SHADOW 응답 계약 테스트 추가.
- SHADOW artifact `READY/MISSING/INVALID/NOT_CONFIGURED` 상태별 smoke test.
- `shadowCandidates`가 event/ticket 생성 경로로 전달되지 않는 통합 테스트 추가.

### 3-6. Frontend

우선순위 중간:

- shared axios client 기준으로 predictive API client 작성.
- Vue 3 Composition API로 dashboard, event detail, ticket list/status 화면 연결.
- loading, empty, error 상태 구현.
- SHADOW 결과는 “비교 모델” 배지로 운영 이벤트와 구분.
- route query 상태와 pagination/sort를 URL에 명시.

### 3-7. Demo/E2E

우선순위 높음:

- PostgreSQL 007/008 migration 적용 확인.
- Spring `app.api.internal-key`와 FastAPI `BACKEND_INTERNAL_API_KEY` 일치 확인.
- FastAPI 기동 후 Spring에서 상태 샘플 ingest.
- 확인 SQL:

```powershell
docker exec traffic-postgres psql -U postgres -d traffic -c "select id, target_camera_id, anomaly_type, severity, status, last_detected_at from anomaly_events order by last_detected_at desc limit 20;"
docker exec traffic-postgres psql -U postgres -d traffic -c "select ticket_number, anomaly_event_id, priority, status, due_ack_at from maintenance_tickets order by created_at desc limit 20;"
docker exec traffic-postgres psql -U postgres -d traffic -c "select camera_id, predicted_anomaly, predicted_severity, evaluated_at from model_prediction_logs order by evaluated_at desc limit 20;"
docker exec traffic-postgres psql -U postgres -d traffic -c "select camera_id, sampled_at, vehicle_count, quality_status from traffic_context_samples order by sampled_at desc limit 20;"
```

## 4. 다음 컨텍스트 시작 권장 순서

1. `git status --short`로 현재 변경 파일 확인.
2. `docs/phase2-predictive-maintenance/merge_workflow_troubleshooting_2026-06-18.md`의 10장 확인.
3. 이 파일의 3-1 Spring Boot API부터 구현.
4. 이벤트 상세/티켓 API를 먼저 붙이고 frontend 연결로 넘어가기.
5. 마지막에 demo profile과 실제 시연 테스트를 수행.

## 4-1. 2026-06-19 현재 검증 완료 상태

완료:

- `test-media/videos/predictive-demo`의 4개 시연 영상(normal/blur/low_fps/dropout)을 기존 GUI로 1회씩 실행.
- `tools/predictive_demo/import_health_samples.ps1`로 4개 상태 샘플을 Spring internal API에 주입.
- `camera_health_samples.created_at` default 누락으로 인한 409를 확인하고 DB default 및 Spring insert 컬럼 보강.
- `GET /api/v1/predictive/cameras`에서 `healthScore=7.5`, `healthStatus=INSUFFICIENT_DATA`, `latestSampledAt` 표시 확인.
- `GET /api/v1/predictive/summary`에서 `totalCameras=1`, `baselineLearningCameras=1` 확인.
- `/admin/ops`에서 API 실패 시 demo fallback이 남지 않도록 수정.
- `/admin/ops` 카메라 상태 카드와 카메라 운영 현황 숫자를 실제 API 값으로 표시.
- `INSUFFICIENT_DATA`도 수집 중/기준선 학습 상태로 표시.
- Health 점수가 있으면 `0/4` 배지보다 `7.5` 점수를 우선 표시.
- frontend build 성공.

시연 확인 기대값:

- `/admin/ops` 첫 화면 KPI: 평균 Health Score `7.5`.
- `카메라 상태`: 전체 `1`, 정상 `0`, 수집 중 `1`, 위험 `0`.
- `Entry Camera 1`: 상태 `수집 중`, Health `7.5`, 최근 응답 시각 표시.

주의:

- 브라우저에서 `admin / 1234`, `ops / 1234`로 로그인하면 local fallback 계정이라 predictive API가 403으로 실패한다.
- 시연 로그인은 `admin@email.com / 1234`를 사용한다.
- frontend/Spring 코드 수정 후 Docker 화면 반영에는 각각 `docker compose up -d --build frontend`, `docker compose up -d --build spring-backend`가 필요하다.

다음 우선 작업:

1. `/admin/ops` anomaly-events 목록을 실제 API 결과로 바인딩.
2. maintenance-tickets 목록을 실제 API 결과로 바인딩.
3. anomaly acknowledge/resolve/dismiss, ticket assign/status 버튼을 실제 mutation API에 연결.
4. FastAPI predictive 평가 결과가 anomaly/ticket 자동 생성까지 이어지는 E2E 시나리오 검증.
5. 발표용 시나리오 문장과 클릭 순서 고정.

## 5. 참고 문서

- `DOCS/phase2-predictive-maintenance/01_요구사항_정의서.md`
- `DOCS/phase2-predictive-maintenance/02_ERD_설계서_revised (1).md`
- `DOCS/phase2-predictive-maintenance/03_API_계약서_ver2 (1).md`
- `DOCS/phase2-predictive-maintenance/05_SpringBoot_작업_TODO.md`
- `DOCS/phase2-predictive-maintenance/06_FastAPI_작업_TODO.md`
- `docs/phase2-predictive-maintenance/merge_review_issues_2026-06-18.txt`
- `docs/phase2-predictive-maintenance/merge_workflow_troubleshooting_2026-06-18.md`
