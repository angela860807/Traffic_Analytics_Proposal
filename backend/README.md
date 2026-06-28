# 차량 흐름 분석 시스템 (Traffic Analytics System)

카메라 영상을 기반으로 차량을 감지하고 번호판을 인식하여, 차량의 유입·유출 흐름과 장비 상태를 분석하는 실시간 차량 모니터링 시스템입니다.

본 백엔드는 외부 AI 분석 서버가 전달한 감지 로그, 과속 위반 데이터, 카메라 헬스 샘플을 수집하고, OCR 분석 결과, 중복 감지 상태, 차량 흐름 이벤트, 시간대별 교통 통계, 예지보전 이상 이벤트와 정비 티켓을 관리하는 Spring Boot API 서버입니다. 또한 회원 인증, 공지사항, 게시글, 댓글, QnA 기능을 위한 REST API를 제공합니다.

---

# 기술 스택

- **Language**: Java 21
- **Framework**: Spring Boot 3.5.14
- **Database**: PostgreSQL
- **ORM**: Spring Data JPA
- **Security**: Spring Security & JWT (JJWT 0.12.6)
- **API 문서**: Swagger (Springdoc OpenAPI 2.8.5)
- **Realtime/Integration**: WebSocket, FastAPI 연동
- **Build Tool**: Gradle
- **Container**: Docker

---

# 시스템 아키텍처

본 백엔드는 외부 분석 서버, PostgreSQL, 프론트엔드 클라이언트 사이에서 교통 데이터의 저장과 조회를 담당합니다.

1. **Ingestion Layer**
   - 외부 AI 분석 서버가 차량 감지 결과를 전송합니다.
   - `POST /api/v1/detection-logs` 엔드포인트에서 감지 로그를 수신합니다.
   - `POST /api/speed-violations` 엔드포인트에서 과속 위반 데이터를 수신합니다.
   - `POST /internal/v1/camera-health-samples` 엔드포인트에서 카메라 상태 샘플을 수신합니다.
   - 서버 간 호출은 `X-Internal-Api-Key` 헤더로 검증합니다.

2. **Processing Layer**
   - 감지 요청의 필수값, 카메라 코드, 신뢰도 범위 등을 검증합니다.
   - OCR 성공, OCR 실패, 중복 감지 상태를 구분합니다.
   - 정상 감지 결과는 차량 정보와 차량 흐름 이벤트로 연결합니다.
   - 과속 위반 요청은 차량 흐름 이벤트, 차량번호, 카메라 코드 일치 여부를 검증한 뒤 위반 이력으로 저장합니다.
   - 카메라 상태 샘플은 룰 기반/성능 저하 평가 대상으로 저장하고, 이상 후보 이벤트로 연결합니다.

3. **Storage Layer**
   - PostgreSQL에 원본 감지 로그, 분석 결과, 차량, 카메라, 구역, 과속 위반, 검토 이력, 통계, 예지보전 데이터를 저장합니다.
   - Spring Data JPA Repository를 통해 영속성 계층을 관리합니다.

4. **Statistics Layer**
   - `VehicleFlowEvent` 데이터를 기준으로 시간대별 교통 통계를 집계합니다.
   - Spring Scheduler를 통해 주기적인 통계 집계가 가능하도록 구성했습니다.

5. **Predictive Maintenance Layer**
   - 카메라 헬스 샘플, 교통 컨텍스트, 모델 예측 로그를 기반으로 이상 이벤트를 관리합니다.
   - 운영자는 이상 이벤트 확인, 해결, 제외 처리와 정비 티켓 생성, 담당자 배정, 상태 변경을 수행할 수 있습니다.

---

# 프로젝트 구조

```text
traffic
 ┣ src
 ┃ ┣ main
 ┃ ┃ ┣ java/com/example/traffic
 ┃ ┃ ┃ ┣ TrafficApplication.java
 ┃ ┃ ┃ ┣ common/enums
 ┃ ┃ ┃ ┃ ┣ DetectionLogStatus.java
 ┃ ┃ ┃ ┃ ┣ DetectionType.java
 ┃ ┃ ┃ ┃ ┣ Direction.java
 ┃ ┃ ┃ ┃ ┣ QnaStatus.java
 ┃ ┃ ┃ ┃ ┣ UserRole.java
 ┃ ┃ ┃ ┃ ┣ UserStatus.java
 ┃ ┃ ┃ ┃ ┣ VehicleStatus.java
 ┃ ┃ ┃ ┃ ┗ ZoneType.java
 ┃ ┃ ┃ ┣ config
 ┃ ┃ ┃ ┃ ┣ PredictiveDatabaseBootstrapRunner.java
 ┃ ┃ ┃ ┃ ┣ SchedulingConfig.java
 ┃ ┃ ┃ ┃ ┣ SecurityConfig.java
 ┃ ┃ ┃ ┃ ┗ SwaggerConfig.java
 ┃ ┃ ┃ ┣ controller
 ┃ ┃ ┃ ┃ ┣ CameraController.java
 ┃ ┃ ┃ ┃ ┣ DetectionLogController.java
 ┃ ┃ ┃ ┃ ┣ HourlyTrafficStatController.java
 ┃ ┃ ┃ ┃ ┣ MemberController.java
 ┃ ┃ ┃ ┃ ┣ CameraHealthSampleInternalController.java
 ┃ ┃ ┃ ┃ ┣ PredictiveDashboardController.java
 ┃ ┃ ┃ ┃ ┣ PredictiveOperationsController.java
 ┃ ┃ ┃ ┃ ┣ VehicleFlowEventController.java
 ┃ ┃ ┃ ┃ ┗ ...
 ┃ ┃ ┃ ┣ domain
 ┃ ┃ ┃ ┃ ┣ DetectionLog.java
 ┃ ┃ ┃ ┃ ┣ DetectionAnalysisResult.java
 ┃ ┃ ┃ ┃ ┣ Vehicle.java
 ┃ ┃ ┃ ┃ ┣ VehicleFlowEvent.java
 ┃ ┃ ┃ ┃ ┣ HourlyTrafficStat.java
 ┃ ┃ ┃ ┃ ┣ CameraHealthSample.java
 ┃ ┃ ┃ ┃ ┣ AnomalyEvent.java
 ┃ ┃ ┃ ┃ ┣ MaintenanceTicket.java
 ┃ ┃ ┃ ┃ ┗ ...
 ┃ ┃ ┃ ┣ dto
 ┃ ┃ ┃ ┃ ┣ request
 ┃ ┃ ┃ ┃ ┗ response
 ┃ ┃ ┃ ┣ etc
 ┃ ┃ ┃ ┃ ┣ BusinessException.java
 ┃ ┃ ┃ ┃ ┣ GlobalExceptionHandler.java
 ┃ ┃ ┃ ┃ ┣ TrafficStatScheduler.java
 ┃ ┃ ┃ ┃ ┗ PredictiveMaintenanceScheduler.java
 ┃ ┃ ┃ ┣ repository
 ┃ ┃ ┃ ┣ security
 ┃ ┃ ┃ ┃ ┣ CustomUserDetailsService.java
 ┃ ┃ ┃ ┃ ┣ JwtAuthenticationFilter.java
 ┃ ┃ ┃ ┃ ┗ JwtTokenProvider.java
 ┃ ┃ ┃ ┗ service
 ┃ ┃ ┗ resources
 ┃ ┃   ┣ application.yml
 ┃ ┃   ┣ data.sql
 ┃ ┃   ┗ db/migration
 ┃ ┗ test
 ┣ build.gradle
 ┣ Dockerfile
 ┗ settings.gradle
```

---

# 실행 및 빌드 가이드

## 1. PostgreSQL 설정

기본 로컬 DB 설정은 `traffic/src/main/resources/application.yml`에 정의되어 있습니다.

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/traffic
spring.datasource.username=postgres
spring.datasource.password=1004
```

운영 또는 공유 환경에서는 DB 비밀번호, JWT secret, 내부 API Key, FastAPI 주소를 환경 변수로 분리하는 것을 권장합니다.

```properties
INTERNAL_API_KEY=traffic-ai-internal-key-2026
FASTAPI_BASE_URL=http://localhost:8000
DB_BOOTSTRAP_ENABLED=false
```

## 2. 프로젝트 이동

Windows PowerShell 기준:

```powershell
cd C:\Users\smn12\OneDrive\바탕 화면\본프로젝트\backend\traffic
```

## 3. 프로젝트 빌드

### 전체 빌드

```powershell
.\gradlew.bat build
```

### 테스트 제외 빌드

```powershell
.\gradlew.bat build -x test
```

---

# 서버 실행

```powershell
.\gradlew.bat bootRun
```

서버는 기본적으로 다음 주소에서 실행됩니다.

```text
http://localhost:8080
```

## 정상 실행 로그 예시

```text
HikariPool-1 - Start completed.
Started TrafficApplication in 8.421 seconds
```

---

# API 문서

## Swagger UI

서버 실행 후 Swagger UI에서 전체 API 명세를 확인할 수 있습니다.

```text
http://localhost:8080/swagger-ui/index.html
```

OpenAPI JSON 문서는 다음 주소에서 확인할 수 있습니다.

```text
http://localhost:8080/v3/api-docs
```

## AI 서버 인증 헤더

외부 AI 분석 서버가 감지 로그, 과속 위반 데이터, 카메라 헬스 샘플을 전송할 때 사용하는 내부 인증 헤더입니다.

```http
X-Internal-Api-Key: traffic-ai-internal-key-2026
```

---

# 주요 API

README에는 핵심 엔드포인트만 요약했습니다. 전체 요청/응답 스키마와 세부 파라미터는 Swagger UI에서 확인할 수 있습니다.

| 기능 | Method | Endpoint |
| --- | --- | --- |
| 회원가입 | POST | `/api/auth/signup` |
| 로그인 | POST | `/api/auth/login` |
| 로그아웃 | POST | `/api/auth/logout` |
| 회원 정보 조회 | GET | `/api/auth/me/{id}` |
| 감지 로그 수신 | POST | `/api/v1/detection-logs` |
| 최근 감지 로그 조회 | GET | `/api/v1/detection-logs` |
| 감지 로그 검색 | GET | `/api/v1/detection-logs/search` |
| 카메라 헬스 샘플 수신 | POST | `/internal/v1/camera-health-samples` |
| 과속 위반 저장 | POST | `/api/speed-violations` |
| 과속 위반 목록/기간 조회 | GET | `/api/speed-violations` |
| 차량별 과속 위반 조회 | GET | `/api/speed-violations/vehicle/{vehicleId}` |
| 카메라별 과속 위반 조회 | GET | `/api/speed-violations/camera/{cameraId}` |
| 상태별 과속 위반 조회 | GET | `/api/speed-violations/status/{violationStatus}` |
| 과속 위반 상태 변경 | PATCH | `/api/speed-violations/{violationId}/status` |
| 과속 위반 건수 조회 | GET | `/api/speed-violations/stats/count` |
| 시간대별 통계 조회 | GET | `/api/stats/hourly` |
| 시간대별 통계 집계 | POST | `/api/stats/hourly/aggregate` |
| 카메라 등록 | POST | `/api/cameras` |
| 카메라 목록 조회 | GET | `/api/cameras` |
| 카메라 상세 조회 | GET | `/api/cameras/{cameraId}` |
| 카메라 수정 | PUT | `/api/cameras/{cameraId}` |
| 구역 등록 | POST | `/api/zones` |
| 구역 목록 조회 | GET | `/api/zones` |
| 구역 수정 | PUT | `/api/zones/{zoneId}` |
| 차량 상세 조회 | GET | `/api/vehicles/{vehicleId}` |
| 차량 상태 변경 | PATCH | `/api/vehicles/{vehicleId}/status` |
| 차량 흐름 통계 조회 | GET | `/api/flow-events/stats/count` |
| 차량별 흐름 이벤트 조회 | GET | `/api/flow-events/vehicle/{vehicleId}` |
| 공지사항 등록 | POST | `/api/notices` |
| 공지사항 목록 조회 | GET | `/api/notices` |
| 공지사항 상세 조회 | GET | `/api/notices/{id}` |
| 게시글 등록 | POST | `/api/posts` |
| 게시글 목록 조회 | GET | `/api/posts` |
| 게시글 상세 조회 | GET | `/api/posts/{id}` |
| 댓글 등록 | POST | `/api/comments/post/{postId}` |
| 댓글 목록 조회 | GET | `/api/comments/post/{postId}` |
| QnA 질문 등록 | POST | `/api/qna/questions` |
| QnA 질문 목록 조회 | GET | `/api/qna/questions` |
| QnA 질문 상세 조회 | GET | `/api/qna/questions/{id}` |
| QnA 답변 등록 | POST | `/api/qna/questions/{id}/answers` |
| 예지보전 요약 조회 | GET | `/api/v1/predictive/summary` |
| 카메라 운영 상태 조회 | GET | `/api/v1/predictive/cameras` |
| 카메라 헬스 이력 조회 | GET | `/api/v1/predictive/cameras/{cameraId}/health-history` |
| 교통 컨텍스트 조회 | GET | `/api/v1/predictive/traffic-context` |
| 이상 이벤트 목록 조회 | GET | `/api/v1/predictive/anomaly-events` |
| 이상 이벤트 상세 조회 | GET | `/api/v1/predictive/anomaly-events/{eventId}` |
| 이상 이벤트 확인 처리 | POST | `/api/v1/predictive/anomaly-events/{eventId}/acknowledge` |
| 이상 이벤트 해결 처리 | POST | `/api/v1/predictive/anomaly-events/{eventId}/resolve` |
| 이상 이벤트 제외 처리 | POST | `/api/v1/predictive/anomaly-events/{eventId}/dismiss` |
| 정비 티켓 목록 조회 | GET | `/api/v1/predictive/maintenance-tickets` |
| 정비 티켓 생성 | POST | `/api/v1/predictive/maintenance-tickets` |
| 정비 티켓 담당자 배정 | POST | `/api/v1/predictive/maintenance-tickets/{ticketId}/assign` |
| 정비 티켓 상태 변경 | POST | `/api/v1/predictive/maintenance-tickets/{ticketId}/status` |
| 정비 티켓 이력 조회 | GET | `/api/v1/predictive/maintenance-tickets/{ticketId}/histories` |
| 예지보전 정책 조회 | GET | `/api/v1/predictive/policies` |
| 예지보전 정책 수정 | PATCH | `/api/v1/predictive/policies/{policyCode}` |

---

# 예외 처리 규약

- `BusinessException` 기반으로 비즈니스 예외를 처리합니다.
- `GlobalExceptionHandler`에서 Validation, JSON 파싱, 인증 실패, 서버 예외를 공통 처리합니다.
- 성공 응답은 `CommonResponse` 형식을 사용합니다.
- 실패 응답은 `ErrorResponse` 형식을 사용합니다.

### 성공 응답 예시

```json
{
  "success": true,
  "data": {},
  "message": "요청이 성공적으로 처리되었습니다."
}
```

### 실패 응답 예시

```json
{
  "code": "BUSINESS_ERROR",
  "message": "Invalid detection data"
}
```

---

# 주요 기능

- AI 차량 감지 로그 실시간 수신
- 감지 로그와 OCR 분석 결과 분리 저장
- `OCR_FAILED`, `FLOW_EVENT_CREATED`, `DUPLICATE_SKIPPED` 상태 관리
- 차량 이동 흐름 이벤트 생성
- 과속 위반 저장 및 검토 상태 변경 이력 관리
- 시간대별 교통 통계 자동 집계
- 카메라 헬스 샘플 수집 및 중복 저장 방지
- 교통 컨텍스트 샘플 집계
- 예지보전 이상 이벤트 생성, 확인, 해결, 제외 처리
- 정비 티켓 생성, 담당자 배정, 상태 변경, 이력 관리
- 예지보전 정책 조회 및 수정
- 카메라 및 구역 관리
- JWT 기반 회원가입 / 로그인 / 인증 처리
- 공지사항, 게시글, 댓글, QnA API 제공
- Swagger 기반 REST API 문서 제공

---

# 보안 구조

- Spring Security 기반 인증/인가 처리
- JWT Access Token 기반 사용자 인증
- 역할(Role) 기반 API 접근 제어
- 내부 AI 분석 서버 전용 API Key 인증 분리
- CORS 허용 Origin 및 Header 제한
- 프론트엔드 연동 중 일부 조회/검토 API는 임시 공개 상태이며, JWT 연동 완료 후 인증 적용이 필요합니다.

## CORS 허용 Origin

- `http://localhost:5173`
- `http://127.0.0.1:5173`
- `http://localhost:5174`
- `http://127.0.0.1:5174`

---

# 핵심 서비스

| Service | Description |
| --- | --- |
| `DetectionLogService` | AI 감지 로그 검증, 저장, 분석 결과 상태 분기 |
| `DetectionAnalysisResultService` | OCR 분석 결과 및 재처리 결과 저장 |
| `VehicleService` | 차량 조회 및 신규 차량 생성 |
| `VehicleFlowEventService` | 차량 흐름 이벤트 생성 및 중복 감지 판단 |
| `SpeedViolationService` | 과속 위반 저장, 조회, 상태 변경 및 검토 이력 저장 |
| `HourlyTrafficStatService` | 시간대별 교통 통계 집계 |
| `CameraHealthSampleIngestionService` | 카메라 헬스 샘플 검증, 저장, FastAPI 연동 데이터 수신 |
| `TrafficContextAggregationService` | 차량 흐름, 분석 결과, 위반 데이터를 기반으로 교통 컨텍스트 집계 |
| `PredictiveDashboardQueryService` | 예지보전 대시보드 요약, 카메라 상태, 이력 조회 |
| `PredictiveOperationsService` | 이상 이벤트 처리, 정비 티켓 생성/배정/상태 변경 |
| `PredictiveRuleEvaluationOrchestrationService` | 룰 기반 이상 평가 흐름 조율 |
| `PredictiveDegradationEvaluationOrchestrationService` | 성능 저하 평가 흐름 조율 |
| `PredictiveShadowPredictionService` | 모델 예측 결과 저장 및 조회 |
| `JwtTokenProvider` | JWT 생성 및 검증 |
| `TrafficStatScheduler` | 스케줄 기반 교통 통계 집계 호출 |
| `PredictiveMaintenanceScheduler` | 스케줄 기반 예지보전 평가 및 컨텍스트 집계 호출 |

---

# Database

## 주요 테이블

- `detection_logs`
- `detection_analysis_results`
- `vehicles`
- `vehicle_flow_events`
- `speed_violations`
- `speed_violation_reviews`
- `hourly_traffic_stats`
- `traffic_analysis_index`
- `camera_health_samples`
- `traffic_context_samples`
- `detector_versions`
- `model_prediction_logs`
- `anomaly_policies`
- `anomaly_events`
- `anomaly_event_evidences`
- `maintenance_tickets`
- `maintenance_ticket_histories`
- `zones`
- `cameras`
- `members`
- `posts`
- `comments`
- `notices`
- `qna_questions`
- `qna_answers`

## 마이그레이션 참고

스키마 변경 참고 SQL은 아래 경로에 정리되어 있습니다.

```text
traffic/src/main/resources/db/migration/001_backend_schema_updates.sql
traffic/src/main/resources/db/migration/002_cleanup_detection_logs_legacy_columns.sql
traffic/src/main/resources/db/migration/003_detection_type_unknown_and_analysis_index.sql
traffic/src/main/resources/db/migration/004_make_flow_metrics_nullable_until_estimated.sql
traffic/src/main/resources/db/migration/005_speed_violation_status_values.sql
traffic/src/main/resources/db/migration/006_speed_violation_reviews.sql
traffic/src/main/resources/db/migration/007_predictive_maintenance_schema.sql
traffic/src/main/resources/db/migration/008_predictive_seed_policies.sql
traffic/src/main/resources/db/migration/009_predictive_ticket_history_backfill.sql
traffic/src/main/resources/db/migration/010_anomaly_events_active_index_datasource.sql
```

공유/시연 환경에서는 `application-demo.yml` 프로필을 사용하여 `ddl-auto=validate`, `spring.sql.init.mode=never` 설정으로 스키마를 검증하는 구성을 권장합니다.

---

# 개발 환경

| 항목 | 버전 |
| --- | --- |
| Java | 21 |
| Spring Boot | 3.5.14 |
| PostgreSQL | 16+ |
| Gradle | Wrapper 사용 |

---

# 테스트

전체 테스트 실행:

```powershell
.\gradlew.bat test
```

감지 로그 통합 테스트만 실행:

```powershell
.\gradlew.bat test --tests "com.example.traffic.controller.DetectionLogControllerIntegrationTest"
```

예지보전 운영 서비스 테스트만 실행:

```powershell
.\gradlew.bat test --tests "com.example.traffic.service.PredictiveOperationsServiceTest"
```

---

# 관련 문서

- [Backend Troubleshooting](./TROUBLESHOOTING.md)
- [Development Migration Notes](./traffic/docs/dev-migration-notes.md)
