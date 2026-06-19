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
- `/admin/ops` anomaly/ticket 실제 API 연결 완료
  - anomaly-events, maintenance-tickets 목록을 실제 API 결과로 표시
  - resolve/dismiss, assign/status 버튼을 실제 mutation API에 연결
- Docker E2E anomaly/ticket 생성 검증 완료
  - Spring 상태 샘플 ingest 후 FastAPI Rule 평가 호출
  - `anomaly_events` 6건, `maintenance_tickets` 3건 생성 확인
  - FastAPI Docker healthcheck는 모델 artifact 미설정 `DEGRADED`도 liveness 정상으로 인정
- 터미널 테스트 한글 표시 방식 정리 완료
  - API 필드는 계약 유지상 영어 camelCase 유지
  - PowerShell `Select-Object @{Name='한글명';Expression={...}}` 방식으로 표시만 한글화

현행 기준 남은 작업:

1. `/admin/ops` 브라우저 클릭 검증
   - 실제 6개 anomaly와 3개 P1 ticket 표시 확인
   - assign/status 버튼 클릭 후 API 재조회 확인
   - resolve/dismiss 버튼 클릭 후 상태 변경 확인
   - 화면에서 403이 나면 local fallback 계정이 아니라 `admin@email.com / 1234`로 다시 로그인

2. 발표 시나리오 고정
   - `sample.mp4` 기반 영상 주입으로 수집 흐름을 보여준다.
   - Rule trigger CSV로 장비 품질 저하를 재현한다.
   - `/admin/ops`에서 위험 카메라, 이상 이벤트, 정비 티켓을 확인한다.
   - 티켓 상태 변경으로 운영 조치 흐름을 마무리한다.

3. 운영자용 한글 라벨/설명 보강
   - 화면에 `FPS_DEGRADATION`, `FRAME_DROP_DEGRADATION`, `RESOURCE_SATURATION` 같은 enum/변수명이 그대로 노출되어 비개발자 관리자 입장에서 원인 파악이 어렵다.
   - anomaly type, detection method, severity, ticket status, data source를 운영자 친화적인 한글 라벨로 변환한다.
   - 표에는 짧은 한글 라벨을 보여주고, tooltip/detail에는 “무엇이 나빠졌는지 / 왜 조치가 필요한지”를 한 문장으로 설명한다.
   - API 계약 필드는 영어 camelCase/enum을 유지하고, 프론트 표시 계층에서만 한글화한다.

4. 새 DB/migration 재현성 확인
   - 로컬 DB 보정 SQL 없이 007/008 migration과 seed만으로 E2E가 재현되는지 확인
   - `maintenance_ticket_number_seq`, `detector_versions`, `anomaly_policies` seed/default 누락 여부 확인

5. Event/Ticket lifecycle 고도화
   - 정상 3회 연속 감지 후 `RECOVERED` 자동 전환
   - `RECOVERED` 후 재발 시 recurrence 증가 및 `OPEN` 복귀
   - WARNING 지속/반복 기반 P2 티켓 자동 생성
   - MTTA/MTTR 계산을 summary에 반영

6. Baseline/TrafficContext 고도화
   - 계약서의 요일/30분 시간대 bucket 기준 baseline 정교화
   - `camera_links` 기반 인접 카메라 교차검증 데이터 채우기
   - `Direction.BOTH` 집계 정책 확정
   - 빈 window에 `INSUFFICIENT` row를 만들지 여부 결정

7. 테스트 보강
   - Spring operations API service/controller 테스트
   - Rule/degradation orchestration 테스트
   - SHADOW 후보가 event/ticket을 만들지 않는 테스트
   - TrafficContext aggregation 통합 테스트
   - Frontend predictive API/client/route guard/OpsView mutation 테스트

8. Demo profile 정리
   - `application-demo.yml`
   - `ddl-auto=validate`
   - seed 재실행 없이 migration 기반 기동
   - demo 시연 전 DB volume 초기화/유지 정책 결정

작성일: 2026-06-18
최종 현행화: 2026-06-19

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

## 4-2. 2026-06-19 추가 완료/남은 작업

추가 완료:

- `/admin/ops` anomaly-events 목록을 실제 `GET /api/v1/predictive/anomaly-events` 결과로 바인딩.
- `/admin/ops` maintenance-tickets 목록을 실제 `GET /api/v1/predictive/maintenance-tickets` 결과와 anomaly detail의 `ticket` 필드로 바인딩.
- anomaly resolve/dismiss 버튼을 실제 `POST /api/v1/predictive/anomaly-events/{eventId}/resolve`, `dismiss` API에 연결.
- ticket assign/status 버튼을 실제 `POST /api/v1/predictive/maintenance-tickets/{ticketId}/assign`, `status` API에 연결.
- API 계약서 3-5/3-6/3-8/3-9/3-10/3-12/3-13 기준으로 query/body/response 필드명 대조 완료.
- `npm run build` 성공. Vite CJS deprecation 및 chunk size warning만 있음.

계약 대조 메모:

- anomaly-events 목록: `dataSource`, `page`, `size`, `sort=firstDetectedAt,desc`.
- anomaly detail: `detector`, `policyCode`, `trend`, `suspectedCauses`, `evidence`, `ticket`, `shadowModel`.
- resolve body: `{ confirmedCause, resolutionNote }`.
- dismiss body: `{ reason }`.
- maintenance-tickets 목록: `page`, `size`, `sort=createdAt,desc`.
- assign body: `{ assigneeId, note }`.
- ticket status body: `{ toStatus, note }`.

다음 우선 작업:

1. FastAPI predictive 평가 결과가 anomaly/ticket 자동 생성까지 이어지는 E2E 시나리오 검증.
2. baseline learning 이후 anomaly event/ticket이 생성되는 샘플 조건 또는 정책 임계값 확정.
3. `/admin/ops`에서 실제 anomaly/ticket이 생겼을 때 resolve/dismiss/assign/status 버튼 브라우저 클릭 검증.
4. 발표용 시나리오 문장과 클릭 순서 고정.
5. E2E가 너무 늦어지면 `FAULT_INJECTED` 또는 `SIMULATED` dataSource 시연 보조 경로 결정.

Docker 반영:

```powershell
docker compose up -d --build frontend
```

Spring backend 이미지까지 최신화해야 하는 환경이면:

```powershell
docker compose up -d --build spring-backend frontend
```

## 4-3. 2026-06-19 Docker E2E 검증 완료 후 인계

완료:

- `/admin/ops` anomaly/ticket 영역을 실제 API 결과로 연결했다.
- Spring 상태 샘플 ingest 후 FastAPI Rule 평가를 호출하고, ACTIVE 후보를 `anomaly_events`, `anomaly_event_evidence`, `maintenance_tickets`까지 저장하는 Docker E2E를 확인했다.
- Rule detector가 확실히 발화하는 COMPLETE 샘플 CSV를 추가했다.
  - `tools/predictive_demo/camera-health-rule-trigger-samples.csv`
- Spring 컨테이너의 FastAPI 호출 주소를 compose DNS 기준으로 맞췄다.
  - `FASTAPI_BASE_URL=http://fastapi-server:8000`
- FastAPI Docker 이미지에서 `predictive_ml` import가 가능하도록 `fastapi-server/Dockerfile`을 보강했다.
- Spring `RestClient` 요청 factory와 rule orchestration transaction을 보정했다.
- FastAPI health detector manifest field를 FastAPI response schema에 맞췄다.
- FastAPI Docker healthcheck는 `UP` 또는 `DEGRADED`를 정상 liveness로 인정하도록 조정했다.
  - 모델 아티팩트가 없어도 Rule detector API는 정상 응답하기 때문이다.

최종 확인된 기대값:

- summary:
  - `totalCameras=1`
  - `criticalCameras=1`
  - `baselineLearningCameras=0`
  - `openAnomalies=6`
  - `predictedRisks=0`
  - `overdueTickets=0`
- anomaly-events:
  - 총 6건.
  - `FPS_DEGRADATION`, `FRAME_DROP_DEGRADATION`, `LATENCY_DEGRADATION`, `BLUR_DEGRADATION`, `RESOURCE_SATURATION`, `NETWORK_INSTABILITY`
  - CRITICAL 3건, WARNING 3건.
- maintenance-tickets:
  - 총 3건.
  - CRITICAL 이벤트에 대해 `P1`, `OPEN` 티켓 자동 생성.

재현 명령:

```powershell
docker compose up -d --build spring-backend fastapi-server frontend

.\tools\predictive_demo\import_health_samples.ps1 `
  -CsvPath "tools\predictive_demo\camera-health-rule-trigger-samples.csv" `
  -BaseUrl "http://localhost:8080" `
  -InternalApiKey "traffic-ai-internal-key-2026"
```

로그인 및 API 확인:

```powershell
$login = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8080/api/auth/login" `
  -ContentType "application/json" `
  -Body (@{
    email = "admin@email.com"
    password = "1234"
  } | ConvertTo-Json)

$headers = @{
  Authorization = "Bearer $($login.data.accessToken)"
}

Invoke-RestMethod `
  -Uri "http://localhost:8080/api/v1/predictive/summary?dataSource=REAL" `
  -Headers $headers

Invoke-RestMethod `
  -Uri "http://localhost:8080/api/v1/predictive/anomaly-events?dataSource=REAL&page=0&size=20&sort=firstDetectedAt,desc" `
  -Headers $headers

Invoke-RestMethod `
  -Uri "http://localhost:8080/api/v1/predictive/maintenance-tickets?page=0&size=20&sort=createdAt,desc" `
  -Headers $headers
```

브라우저 확인:

1. `http://localhost:5174/admin/ops` 접속.
2. `admin@email.com / 1234`로 로그인.
3. 상단 KPI에서 위험 카메라 1대, 열린 이상 6건을 확인.
4. anomaly/ticket 목록에서 6개 이상 이벤트와 3개 P1 티켓을 확인.
5. CRITICAL 이벤트의 ticket action 버튼으로 assign/status 변경이 되는지 클릭 검증.
6. 필요하면 anomaly resolve/dismiss 버튼을 클릭하고 API 재조회 후 상태 변화를 확인.

계약 대조 상태:

- 완료:
  - `GET /api/v1/predictive/anomaly-events`
  - `GET /api/v1/predictive/anomaly-events/{eventId}`
  - `POST /api/v1/predictive/anomaly-events/{eventId}/resolve`
  - `POST /api/v1/predictive/anomaly-events/{eventId}/dismiss`
  - `GET /api/v1/predictive/maintenance-tickets`
  - `POST /api/v1/predictive/maintenance-tickets/{ticketId}/assign`
  - `POST /api/v1/predictive/maintenance-tickets/{ticketId}/status`
- query/body/response field는 API 계약서 3-5/3-6/3-8/3-9/3-10/3-12/3-13 기준으로 맞췄다.
- API field는 계약 유지를 위해 영어 camelCase를 유지한다. 터미널 가독성은 `Select-Object @{Name='한글명';Expression={...}}` 형태의 출력 명령으로 보완한다.

터미널 한글 출력 예:

```powershell
$events = Invoke-RestMethod `
  -Uri "http://localhost:8080/api/v1/predictive/anomaly-events?dataSource=REAL&page=0&size=20&sort=firstDetectedAt,desc" `
  -Headers $headers

$events.content | Select-Object `
  @{Name='이벤트ID';Expression={$_.id}},
  @{Name='카메라';Expression={$_.cameraName}},
  @{Name='이상유형';Expression={$_.anomalyType}},
  @{Name='심각도';Expression={$_.severity}},
  @{Name='상태';Expression={$_.status}},
  @{Name='점수';Expression={$_.anomalyScore}},
  @{Name='최근감지';Expression={$_.lastDetectedAt}} |
  Format-Table -AutoSize

$tickets = Invoke-RestMethod `
  -Uri "http://localhost:8080/api/v1/predictive/maintenance-tickets?page=0&size=20&sort=createdAt,desc" `
  -Headers $headers

$tickets.content | Select-Object `
  @{Name='티켓ID';Expression={$_.id}},
  @{Name='티켓번호';Expression={$_.ticketNumber}},
  @{Name='이벤트ID';Expression={$_.anomalyEventId}},
  @{Name='우선순위';Expression={$_.priority}},
  @{Name='상태';Expression={$_.status}},
  @{Name='응답기한';Expression={$_.dueAckAt}},
  @{Name='착수기한';Expression={$_.dueStartAt}} |
  Format-Table -AutoSize
```

다음 우선 작업:

1. `/admin/ops`에서 실제 버튼 클릭 검증을 완료한다.
   - assign/status 변경.
   - resolve/dismiss 변경.
2. 발표 시나리오를 고정한다.
   - 영상 주입으로 카메라 상태 샘플 생성.
   - Rule trigger 샘플로 장비 품질 저하 재현.
   - `/admin/ops`에서 위험 카메라, 이상 이벤트, 정비 티켓 확인.
   - 티켓 상태 변경으로 운영 조치 흐름 설명.
3. 새 DB에서 migration만으로 같은 상태가 만들어지는지 확인한다.
   - 로컬 DB 보정 SQL 없이 007/008 migration과 seed가 정상 적용되는지 검증.
4. LSTM/SHADOW 모델 artifact가 발표 범위에 들어가면 `/app/models/predictive` 모델 파일과 artifact 검증 시나리오를 추가한다.
5. `congestion_score` Hibernate DDL warning은 별도 schema/migration 정리 작업으로 분리한다.

## 4-4. 2026-06-19 작업일지용 번호 요약

1. Spring predictive summary API 500 원인을 확인하고 PostgreSQL nullable `zoneId` 타입 추론 및 health score null metric 문제를 보정했다.
2. `/admin/ops` route/auth 권한과 JWT role 파싱을 정리해 `ADMIN`, `OPERATOR`, `MAINTAINER` 계정으로 predictive 화면 접근이 가능하게 했다.
3. `/admin/ops` 카메라 상태, KPI, 정책 목록/수정 화면을 실제 predictive API 응답 기준으로 표시하게 연결했다.
4. API 필드는 계약 유지를 위해 영어 camelCase를 유지하고, PowerShell 출력은 `Select-Object @{Name='한글명'}` 방식으로 한글 표시 예시를 정리했다.
5. 영상 기반 시연 자료를 `test-media/videos/predictive-demo` 기준으로 정리하고, 의미가 약한 `ocr_fail` 분류는 제외했다.
6. `/admin/ops` anomaly-events 목록을 실제 `GET /api/v1/predictive/anomaly-events` 응답으로 바인딩했다.
7. `/admin/ops` maintenance-tickets 목록을 실제 `GET /api/v1/predictive/maintenance-tickets` 응답과 anomaly detail의 `ticket` 필드로 바인딩했다.
8. anomaly resolve/dismiss, ticket assign/status 버튼을 실제 mutation API로 연결하고 성공 후 화면을 재조회하게 했다.
9. Spring 컨테이너가 FastAPI를 compose service DNS인 `http://fastapi-server:8000`으로 호출하도록 환경변수를 보정했다.
10. FastAPI Docker 이미지에서 `predictive_ml` 패키지를 import할 수 있도록 Dockerfile에 source 복사와 `PYTHONPATH` 설정을 추가했다.
11. Spring `RestClient` 요청 factory를 보정해 FastAPI 평가 요청 body가 안정적으로 전달되게 했다.
12. 상태 샘플 ingest 이후 anomaly/evidence/ticket 저장이 가능하도록 rule orchestration transaction을 read-only에서 일반 transaction으로 변경했다.
13. Rule detector가 확실히 발화하는 `tools/predictive_demo/camera-health-rule-trigger-samples.csv`를 추가했다.
14. 개발 DB에서 누락된 detector/policy seed, default, `maintenance_ticket_number_seq`를 보정해 로컬 E2E를 복구했다.
15. Spring 상태 샘플 ingest 후 FastAPI Rule 평가가 실행되고 `anomaly_events` 6건, `maintenance_tickets` 3건이 생성되는 것을 API와 DB로 확인했다.
16. FastAPI health manifest field를 response schema에 맞게 정리하고, 모델 artifact 미설정 `DEGRADED` 상태를 Rule 기반 시연 가능 상태로 문서화했다.
17. Docker healthcheck가 `UP` 또는 `DEGRADED`를 정상 liveness로 인정하도록 조정해 FastAPI 컨테이너가 `healthy`로 표시되게 했다.
18. workflow/troubleshooting과 next-context TODO 문서에 재현 명령, 기대값, 브라우저 확인 순서, 남은 작업을 정리했다.

## 5. 참고 문서

- `DOCS/phase2-predictive-maintenance/01_요구사항_정의서.md`
- `DOCS/phase2-predictive-maintenance/02_ERD_설계서_revised (1).md`
- `DOCS/phase2-predictive-maintenance/03_API_계약서_ver2 (1).md`
- `DOCS/phase2-predictive-maintenance/05_SpringBoot_작업_TODO.md`
- `DOCS/phase2-predictive-maintenance/06_FastAPI_작업_TODO.md`
- `docs/phase2-predictive-maintenance/merge_review_issues_2026-06-18.txt`
- `docs/phase2-predictive-maintenance/merge_workflow_troubleshooting_2026-06-18.md`
