# 백엔드 트러블슈팅

이 문서는 Traffic Analytics 백엔드 개발 중 발생했거나 발생 가능성이 높았던 주요 문제와 해결 과정을 정리한 문서입니다.
범위는 `backend/traffic` Spring Boot 서버에 한정합니다.

## 1. OCR 실패 결과 저장 문제

### 문제

외부 분석 서버에서 차량은 감지했지만 번호판 OCR에 실패한 경우, 기존 흐름대로 처리하면 차량번호 없이 `vehicles` 또는 `vehicle_flow_events` 데이터가 생성될 수 있었다.

### 원인

초기 감지 로그 구조는 정상적으로 차량번호가 인식된 상황을 중심으로 설계되어 있었다. 따라서 차량번호가 없는 결과를 정상 감지와 동일하게 처리하면 차량 식별, 흐름 이벤트, 통계 데이터가 부정확해질 수 있었다.

### 해결

- `DetectionLogStatus.OCR_FAILED` 상태를 추가했다.
- 원본 감지 로그는 `detection_logs`에 저장하고, 분석 결과는 `detection_analysis_results`에 분리 저장했다.
- `OCR_FAILED` 상태일 때는 분석 결과만 저장하고 `vehicles`, `vehicle_flow_events`는 생성하지 않도록 처리했다.
- 차량번호가 없는 요청은 반드시 `OCR_FAILED` 상태로 들어오도록 검증 로직을 추가했다.

### 검증

`DetectionLogControllerIntegrationTest`에서 OCR 실패 요청을 전송한 뒤 다음을 확인했다.

- 감지 로그가 저장된다.
- 분석 결과가 `OCR_FAILED` 상태로 저장된다.
- 차량 데이터가 새로 생성되지 않는다.
- 차량 흐름 이벤트가 생성되지 않는다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/common/enums/DetectionLogStatus.java`
- `traffic/src/main/java/com/example/traffic/service/DetectionLogService.java`
- `traffic/src/main/java/com/example/traffic/domain/DetectionAnalysisResult.java`
- `traffic/src/test/java/com/example/traffic/controller/DetectionLogControllerIntegrationTest.java`

## 2. 중복 감지로 인한 교통량 과집계 문제

### 문제

같은 차량이 짧은 시간 안에 반복 감지되면 차량 흐름 이벤트가 중복 생성되어 시간대별 교통량과 혼잡도 통계가 실제보다 크게 집계될 수 있었다.

### 원인

카메라 기반 감지 시스템은 동일 차량을 여러 프레임에서 반복 감지할 수 있다. 백엔드에서 이를 모두 정상 흐름 이벤트로 저장하면 `vehicle_flow_events` 기준 통계가 부풀어 오른다.

### 해결

- `DetectionLogStatus.DUPLICATE_SKIPPED` 상태를 추가했다.
- 감지 결과는 추적을 위해 저장하되, 중복으로 판단된 경우 차량 흐름 이벤트는 생성하지 않도록 했다.
- 서비스 계층에서 최근 중복 여부를 확인한 뒤 `FLOW_EVENT_CREATED` 또는 `DUPLICATE_SKIPPED`로 상태를 분기했다.

### 검증

`DetectionLogControllerIntegrationTest`에서 `DUPLICATE_SKIPPED` 요청을 전송하고 다음을 확인했다.

- 감지 로그와 분석 결과는 저장된다.
- 분석 결과 상태가 `DUPLICATE_SKIPPED`로 저장된다.
- 차량 흐름 이벤트 수는 증가하지 않는다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/service/DetectionLogService.java`
- `traffic/src/main/java/com/example/traffic/service/VehicleFlowEventService.java`
- `traffic/src/main/java/com/example/traffic/repository/VehicleFlowEventRepository.java`
- `traffic/src/test/java/com/example/traffic/controller/DetectionLogControllerIntegrationTest.java`

## 3. 감지 로그와 분석 결과의 책임 분리

### 문제

감지 로그 테이블 하나에 원본 이미지 정보, OCR 결과, 처리 상태, 재처리 결과까지 모두 담으면 데이터 의미가 섞이고 확장성이 떨어질 수 있었다.

### 원인

외부 분석 서버 연동이 추가되면서 단순 감지 로그 외에도 다음 정보가 필요해졌다.

- OCR 성공/실패 상태
- 중복 처리 여부
- 번호판 crop 이미지 경로
- OCR 전처리 이미지 경로
- 분석 시도 회차
- 분석 처리 주체

이 정보들은 원본 감지 로그보다 "분석 결과"에 가까운 데이터였다.

### 해결

- 원본 감지 이벤트는 `DetectionLog`에 저장했다.
- OCR 및 분석 결과는 `DetectionAnalysisResult`로 분리했다.
- `DetectionResponse`는 두 데이터를 조합해 API 응답을 구성하도록 했다.

### 효과

- OCR 실패와 중복 처리 결과를 원본 로그와 별도로 추적할 수 있게 되었다.
- 향후 재분석, 모델 변경, 분석 회차 관리가 쉬워졌다.
- 원본 감지 데이터와 후처리 결과의 책임이 명확해졌다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/domain/DetectionLog.java`
- `traffic/src/main/java/com/example/traffic/domain/DetectionAnalysisResult.java`
- `traffic/src/main/java/com/example/traffic/service/DetectionAnalysisResultService.java`
- `traffic/src/main/java/com/example/traffic/dto/response/DetectionResponse.java`

## 4. 외부 분석 서버 연동 API 인증 문제

### 문제

외부 분석 서버가 감지 결과를 백엔드로 전송해야 하지만, 일반 사용자 JWT 인증을 그대로 적용하면 서버 간 통신이 막힐 수 있었다. 반대로 해당 API를 완전히 공개하면 임의 요청이 감지 로그로 저장될 위험이 있었다.

### 원인

`/api/v1/detection-logs`는 일반 브라우저 사용자가 호출하는 API가 아니라 FastAPI 등 내부 분석 서버가 호출하는 수집 API다. 사용자 로그인 인증과 서버 간 인증은 목적이 다르다.

### 해결

- Spring Security에서는 `POST /api/v1/detection-logs` 요청을 JWT 인증 대상에서 제외했다.
- 대신 컨트롤러에서 `X-Internal-Api-Key` 헤더를 검사하도록 했다.
- 내부 키는 `application.yml`의 `app.api.internal-key` 설정으로 관리했다.
- CORS 허용 헤더에 `X-Internal-Api-Key`를 추가했다.

### 검증

`DetectionLogControllerIntegrationTest`에서 내부 API Key 없이 요청했을 때 `401 Unauthorized`가 반환되는지 확인했다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/config/SecurityConfig.java`
- `traffic/src/main/java/com/example/traffic/controller/DetectionLogController.java`
- `traffic/src/main/resources/application.yml`
- `traffic/src/test/java/com/example/traffic/controller/DetectionLogControllerIntegrationTest.java`

## 5. DB 스키마 변경 반영 문제

### 문제

개발 중 엔티티 구조가 계속 바뀌면서 기존 DB 테이블과 애플리케이션 엔티티가 맞지 않는 문제가 발생할 수 있었다. 특히 감지 로그 파이프라인이 확장되면서 분석 결과 테이블, 차량 흐름 이벤트 분석 컬럼, 시간대별 통계 확장 컬럼이 추가로 필요해졌다.

### 원인

로컬 개발 환경에서는 `spring.jpa.hibernate.ddl-auto=update`가 단순 컬럼 추가에는 도움이 되지만, 제약조건 변경, 인덱스 추가, nullable 변경 같은 작업을 명확히 관리하기 어렵다.

### 해결

- 개발 중 필요한 DDL을 `traffic/docs/dev-migration-notes.md`에 정리했다.
- 실제 적용 가능한 SQL은 `traffic/src/main/resources/db/migration/*.sql`에 단계별로 분리해 두었다.
- `detection_logs.status`, `traffic_analysis_index.zone_id`, `detection_analysis_results`, `vehicle_flow_events.source_analysis_result_id` 등을 명시적으로 정리했다.
- `vehicle_flow_events`에는 속도와 체류 시간 컬럼을 추가했다.
- `hourly_traffic_stats`에는 평균 속도, 혼잡도, 평균 체류 시간, 중복 차량 수, 마지막 로그 ID 컬럼을 추가했다.
- 과속 위반과 검토 이력을 위해 `speed_violations`, `speed_violation_reviews` 테이블을 추가했다.

### 효과

- 팀원이 공유 DB를 사용할 때 필요한 변경 사항을 추적하기 쉬워졌다.
- `ddl-auto=update`에만 의존하지 않고 스키마 변경 의도를 문서화할 수 있게 되었다.

### 관련 파일

- `traffic/docs/dev-migration-notes.md`
- `traffic/src/main/resources/db/migration/001_backend_schema_updates.sql`
- `traffic/src/main/resources/db/migration/002_cleanup_detection_logs_legacy_columns.sql`
- `traffic/src/main/resources/db/migration/003_detection_type_unknown_and_analysis_index.sql`
- `traffic/src/main/resources/db/migration/004_make_flow_metrics_nullable_until_estimated.sql`
- `traffic/src/main/resources/db/migration/005_speed_violation_status_values.sql`
- `traffic/src/main/resources/db/migration/006_speed_violation_reviews.sql`
- `traffic/src/main/resources/application.yml`

## 6. 시간대별 통계 집계 기준 문제

### 문제

차량 흐름 이벤트를 그대로 화면에 조회하는 것만으로는 시간대별 교통량, 평균 속도, 체류 시간, 혼잡도 같은 지표를 제공하기 어려웠다.

### 원인

대시보드에서는 원본 이벤트 목록보다 요약된 통계가 필요하다. 하지만 통계를 요청 시점마다 계산하면 조회 비용이 커지고, 화면에서 같은 기준의 데이터를 안정적으로 사용하기 어렵다.

### 해결

- `HourlyTrafficStat` 엔티티를 두고 시간대별 집계 결과를 저장했다.
- `HourlyTrafficStatService.aggregateHourlyStats()`에서 특정 구역과 시간대를 기준으로 차량 흐름 이벤트를 집계했다.
- 스케줄러에서 주기적으로 집계 서비스를 호출할 수 있도록 `TrafficStatScheduler`를 구성했다.

### 집계 항목

- 진입 차량 수
- 진출 차량 수
- 평균 속도
- 평균 체류 시간
- 중복 감지 수
- 혼잡도 점수

### 관련 파일

- `traffic/src/main/java/com/example/traffic/domain/HourlyTrafficStat.java`
- `traffic/src/main/java/com/example/traffic/service/HourlyTrafficStatService.java`
- `traffic/src/main/java/com/example/traffic/etc/TrafficStatScheduler.java`
- `traffic/src/main/java/com/example/traffic/controller/HourlyTrafficStatController.java`

## 7. API 응답 형식 일관성 문제

### 문제

기능별 컨트롤러가 늘어나면서 API 응답 형식이 제각각이면 프론트엔드 연동과 에러 처리가 복잡해질 수 있었다.

### 원인

회원, 게시글, 공지사항, QnA, 감지 로그, 통계 등 여러 도메인이 각각 응답을 반환하면 성공/실패 여부, 메시지, 데이터 구조가 달라질 가능성이 높았다.

### 해결

- 성공 응답은 `CommonResponse`를 사용했다.
- 실패 응답은 `ErrorResponse`를 사용했다.
- 예외는 `BusinessException`과 `GlobalExceptionHandler`에서 공통 형식으로 처리했다.
- 도메인별 응답 DTO를 분리해 컨트롤러 응답 구조를 명확하게 했다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/dto/response/CommonResponse.java`
- `traffic/src/main/java/com/example/traffic/dto/response/ErrorResponse.java`
- `traffic/src/main/java/com/example/traffic/etc/BusinessException.java`
- `traffic/src/main/java/com/example/traffic/etc/GlobalExceptionHandler.java`

## 8. 인증과 공개 API 권한 분리 문제

### 문제

모든 API를 인증 대상으로 묶으면 공지사항 조회, 게시글 조회, QnA 조회, Swagger 문서 접근, 외부 분석 서버 수집 API까지 막힐 수 있었다. 반대로 모두 공개하면 관리자 기능과 사용자 기능의 권한 통제가 어려워진다.

### 원인

백엔드는 다음과 같이 성격이 다른 API를 함께 제공한다.

- 로그인 없이 조회 가능한 공개 API
- 로그인 사용자가 작성/수정하는 API
- 관리자만 접근해야 하는 API
- 내부 분석 서버가 호출하는 API
- Swagger 문서 API

### 해결

- Spring Security 설정에서 HTTP Method와 경로별 권한을 분리했다.
- 공지사항/게시글/QnA 조회는 공개하고, 작성/답변/관리 기능은 인증 또는 관리자 권한을 요구하도록 했다.
- Swagger 문서 경로는 개발 편의를 위해 공개했다.
- 내부 수집 API는 JWT 대신 내부 API Key를 사용하도록 분리했다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/config/SecurityConfig.java`
- `traffic/src/main/java/com/example/traffic/security/JwtAuthenticationFilter.java`
- `traffic/src/main/java/com/example/traffic/security/JwtTokenProvider.java`
- `traffic/src/main/java/com/example/traffic/security/CustomUserDetailsService.java`

## 9. 통합 테스트용 DB 제약조건 문제

### 문제

감지 로그 구조가 변경되면서 테스트 환경의 기존 테이블 제약조건이 새 로직과 충돌할 수 있었다. 특히 OCR 실패 시 차량번호나 감지 타입이 비어 있을 수 있는 케이스가 문제가 될 수 있었다.

### 원인

초기 스키마는 정상 OCR 성공 케이스를 기준으로 `plate_number`, `detection_type` 같은 컬럼을 필수값으로 보는 흐름이 있었다. 그러나 OCR 실패 결과까지 저장하려면 일부 값은 nullable 처리가 필요했다.

### 해결

- 통합 테스트 실행 전에 `@Sql`로 테스트에 필요한 제약조건을 완화했다.
- 이후 마이그레이션 SQL에도 nullable 변경과 상태 체크 제약조건을 반영했다.

### 관련 파일

- `traffic/src/test/java/com/example/traffic/controller/DetectionLogControllerIntegrationTest.java`
- `traffic/src/main/resources/db/migration/001_backend_schema_updates.sql`

## 10. 분석 이미지 경로 추적 문제

### 문제

외부 분석 서버에서 원본 프레임뿐 아니라 번호판 crop 이미지와 OCR 전처리 이미지를 함께 생성하면서, 백엔드가 어떤 이미지를 어떤 분석 결과와 연결해야 하는지 명확히 관리할 필요가 생겼다.

### 원인

초기 감지 로그는 원본 이미지 경로 중심으로 구성되어 있었다. 하지만 OCR 실패 분석, 번호판 영역 확인, 재처리 검증을 위해서는 원본 이미지와 별도로 crop 이미지 및 OCR 전처리 이미지 경로를 저장해야 했다.

### 해결

- 원본 감지 이미지는 `DetectionLog`의 `imagePath`, `imageUrl`에 저장했다.
- 번호판 crop 이미지와 OCR 전처리 이미지는 `DetectionAnalysisResult`에 저장했다.
- API 응답인 `DetectionResponse`에서 원본 로그 정보와 분석 이미지 정보를 함께 반환하도록 구성했다.

### 효과

- 원본 감지 로그와 OCR 분석 산출물을 분리해서 추적할 수 있게 되었다.
- OCR 실패나 낮은 신뢰도 결과를 검토할 때 필요한 근거 이미지를 API 응답으로 확인할 수 있게 되었다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/domain/DetectionLog.java`
- `traffic/src/main/java/com/example/traffic/domain/DetectionAnalysisResult.java`
- `traffic/src/main/java/com/example/traffic/dto/request/DetectionRequest.java`
- `traffic/src/main/java/com/example/traffic/dto/response/DetectionResponse.java`

## 11. Swagger 문서 접근 경로 혼동 문제

### 문제

Springdoc OpenAPI 설정 이후 Swagger UI 접근 경로가 문서마다 다르게 안내되면 API 테스트 과정에서 혼동이 생길 수 있었다.

### 원인

Springdoc 버전에 따라 `/swagger-ui.html`로 접근해도 리다이렉트되는 경우가 있지만, 현재 프로젝트에서는 `/swagger-ui/index.html`을 명시하는 편이 더 정확하다.

### 해결

- README의 Swagger UI 경로를 `http://localhost:8080/swagger-ui/index.html`로 정리했다.
- OpenAPI JSON 경로도 `http://localhost:8080/v3/api-docs`로 함께 안내했다.

### 관련 파일

- `traffic/build.gradle`
- `traffic/src/main/java/com/example/traffic/config/SwaggerConfig.java`
- `README.md`

## 12. 과속 위반 저장 API와 차량 흐름 이벤트 연결 문제

### 문제

외부 분석 서버에서 과속 위반 데이터를 별도로 전송할 때, 단순히 차량번호와 속도만 저장하면 기존 차량 흐름 이벤트와 위반 이력이 분리될 수 있었다. 또한 같은 흐름 이벤트에 대해 과속 위반 요청이 반복 전송되면 중복 위반 데이터가 생성될 수 있었다.

### 원인

과속 위반은 독립적인 이벤트가 아니라 이미 생성된 `vehicle_flow_events`를 기준으로 판단되는 후속 데이터다. 따라서 요청의 `flowEventId`, 차량번호, 카메라 코드가 기존 흐름 이벤트와 일치하는지 검증하지 않으면 잘못된 차량 또는 카메라에 위반 이력이 연결될 수 있다.

### 해결

- `POST /api/speed-violations` 엔드포인트를 추가했다.
- `SpeedViolationCreateRequest`로 과속 위반 저장 요청을 분리했다.
- 내부 분석 서버 호출이므로 `X-Internal-Api-Key` 헤더를 검증하도록 했다.
- 측정 속도가 제한 속도보다 큰 경우에만 저장하도록 검증했다.
- 요청의 `flowEventId`, 차량번호, 카메라 코드가 기존 `VehicleFlowEvent`와 일치하는지 확인했다.
- 같은 `flowEventId`로 이미 저장된 위반이 있으면 새로 생성하지 않고 기존 위반 정보를 반환하도록 처리했다.
- 과속 위반 저장 시 `VehicleFlowEvent`의 속도 값도 함께 갱신했다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/controller/SpeedViolationController.java`
- `traffic/src/main/java/com/example/traffic/service/SpeedViolationService.java`
- `traffic/src/main/java/com/example/traffic/domain/SpeedViolation.java`
- `traffic/src/main/java/com/example/traffic/dto/request/SpeedViolationCreateRequest.java`
- `traffic/src/main/java/com/example/traffic/repository/SpeedViolationRepository.java`
- `traffic/src/main/java/com/example/traffic/config/SecurityConfig.java`

## 13. 과속 위반 검토 상태 변경 이력 누락 문제

### 문제

과속 위반 상태를 `UNPROCESSED`, `CONFIRMED`, `REJECTED` 등으로 변경할 수 있어도, 누가 어떤 사유로 상태를 변경했는지 남지 않으면 검토 흐름을 추적하기 어렵다.

### 원인

초기 과속 위반 모델은 현재 상태만 저장하는 구조였다. 상태 변경 이력이 없으면 프론트엔드 검토 화면이나 운영 감사 관점에서 변경 근거를 확인할 수 없다.

### 해결

- `PATCH /api/speed-violations/{violationId}/status` 엔드포인트를 추가했다.
- `SpeedViolationStatusRequest`에 변경 상태, 사유, 메모, 검토자 값을 받을 수 있도록 했다.
- `SpeedViolationReview` 엔티티와 `speed_violation_reviews` 테이블을 추가했다.
- 상태 변경 시 기존 상태와 변경 상태를 함께 저장하고, 최신 검토 이력을 응답에 포함하도록 했다.
- 프론트엔드 연동 단계에서는 조회 및 상태 변경 API를 임시 공개하고, JWT 연동 완료 후 인증 대상으로 전환할 수 있도록 `SecurityConfig`에 TODO를 명시했다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/controller/SpeedViolationController.java`
- `traffic/src/main/java/com/example/traffic/service/SpeedViolationService.java`
- `traffic/src/main/java/com/example/traffic/domain/SpeedViolationReview.java`
- `traffic/src/main/java/com/example/traffic/dto/request/SpeedViolationStatusRequest.java`
- `traffic/src/main/java/com/example/traffic/repository/SpeedViolationReviewRepository.java`
- `traffic/src/main/resources/db/migration/006_speed_violation_reviews.sql`

## 14. 프론트엔드 개발 서버 포트 변경으로 인한 CORS 차단 문제

### 문제

Vue 개발 서버가 `5173`이 아닌 `5174` 포트에서 실행될 때 브라우저에서 백엔드 API 호출이 CORS 정책에 의해 차단될 수 있었다.

### 원인

Spring Security CORS 설정은 허용 Origin을 명시적으로 제한한다. 기존 설정에는 `localhost:5173`, `127.0.0.1:5173`만 포함되어 있어 Vite가 다른 포트로 실행되는 경우 요청이 허용되지 않았다.

### 해결

`SecurityConfig`의 CORS 허용 Origin에 `5174` 포트를 추가했다.

```java
configuration.setAllowedOrigins(List.of(
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
));
```

### 관련 파일

- `traffic/src/main/java/com/example/traffic/config/SecurityConfig.java`

## 15. 예지보전 카메라 헬스 샘플 수집 API 누락 문제

### 문제

FastAPI 서버에서 카메라 상태 샘플을 Spring Boot로 전송해야 했지만, 백엔드에 수신 엔드포인트가 없으면 내부 연동 요청이 `404 Not Found`로 실패할 수 있었다.

### 원인

예지보전 기능은 기존 차량 감지 로그와 별도의 데이터 흐름을 가진다. 기존에는 `POST /api/v1/detection-logs`와 `POST /api/speed-violations` 중심으로 내부 수집 API가 구성되어 있었고, 카메라 헬스 샘플을 저장하는 전용 내부 API가 필요했다.

### 해결

- `POST /internal/v1/camera-health-samples` 엔드포인트를 추가했다.
- 내부 서버 간 호출이므로 `X-Internal-Api-Key` 헤더를 검증하도록 했다.
- `CameraHealthSampleCreateRequest`와 `CameraHealthSampleSaveResponse`로 요청/응답 DTO를 분리했다.
- 저장 후 최신 샘플을 기준으로 룰 기반 이상 평가가 이어지도록 `PredictiveRuleEvaluationOrchestrationService`를 호출했다.
- 룰 평가가 실패해도 샘플 저장 자체는 실패하지 않도록 예외를 로그로 남기고 흐름을 분리했다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/controller/CameraHealthSampleInternalController.java`
- `traffic/src/main/java/com/example/traffic/service/CameraHealthSampleIngestionService.java`
- `traffic/src/main/java/com/example/traffic/service/PredictiveRuleEvaluationOrchestrationService.java`
- `traffic/src/main/java/com/example/traffic/repository/CameraHealthSampleRepository.java`
- `traffic/src/main/resources/db/migration/007_predictive_maintenance_schema.sql`

## 16. Spring/FastAPI/AI 모델 계약 불일치 문제

### 문제

예지보전 기능을 Spring Boot, FastAPI, predictive ML 모듈이 함께 사용하면서 요청 필드명이나 응답 구조가 조금만 달라도 검증 오류나 매핑 오류가 발생할 수 있었다.

### 원인

카메라 헬스 샘플, 룰 평가 결과, 성능 저하 평가 결과는 여러 서버를 거쳐 이동한다. 이때 Spring의 API 계약, FastAPI 스키마, predictive ML dataclass가 각각 따로 바뀌면 다음 문제가 생긴다.

- 정책 필드명 불일치
- detector 응답 구조 매핑 실패
- 운영 화면에서 필요한 상태값 누락
- 테스트 fixture와 실제 모델 계약 불일치

### 해결

- FastAPI 어댑터에서 predictive ML 결과를 API 응답 DTO에 맞게 명시적으로 변환하도록 정리했다.
- Spring에서는 예지보전 대시보드/운영 API의 요청 DTO와 응답 DTO를 분리했다.
- `PredictiveDetectionClient`를 통해 FastAPI 호출 지점을 별도로 관리했다.
- 이상 후보 저장은 `PredictiveAnomalyEventIngestionService`에서 담당하도록 분리했다.
- 카메라 헬스 샘플 저장 이후 룰 평가, 스케줄 기반 성능 저하 평가, 운영 API 조회 흐름을 각각 서비스로 나누었다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/client/PredictiveDetectionClient.java`
- `traffic/src/main/java/com/example/traffic/service/PredictiveAnomalyEventIngestionService.java`
- `traffic/src/main/java/com/example/traffic/service/PredictiveDegradationEvaluationOrchestrationService.java`
- `traffic/src/main/java/com/example/traffic/service/PredictiveDashboardQueryService.java`
- `fastapi-server/app/services/predictive_detector_adapter.py`
- `fastapi-server/tests/predictive/test_predictive_adapter.py`

## 17. 예지보전 운영 API와 상태 전이 관리 문제

### 문제

이상 이벤트를 단순 조회만 제공하면 운영자가 이벤트를 확인했는지, 해결했는지, 제외 처리했는지 추적하기 어렵다. 또한 정비 티켓을 생성해도 담당자 배정과 상태 변경 이력이 없으면 실제 운영 화면과 연결하기 어렵다.

### 원인

예지보전 기능은 감지 데이터 저장보다 운영 프로세스에 가깝다. 이벤트 상태, 정비 티켓 상태, 담당자, 처리 사유, 이력이 함께 관리되어야 프론트엔드 운영 화면에서 일관된 흐름을 만들 수 있다.

### 해결

- `/api/v1/predictive/anomaly-events` 조회 API를 추가했다.
- 이상 이벤트 확인, 해결, 제외 처리 API를 추가했다.
- 정비 티켓 생성, 담당자 배정, 상태 변경 API를 추가했다.
- 정비 티켓 변경 이력을 `MaintenanceTicketHistory`로 분리했다.
- 운영 화면에서 담당자 후보를 조회할 수 있도록 `/api/v1/predictive/assignees` API를 추가했다.
- 정책 변경은 `/api/v1/predictive/policies/{policyCode}`에서 처리하도록 분리했다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/controller/PredictiveOperationsController.java`
- `traffic/src/main/java/com/example/traffic/service/PredictiveOperationsService.java`
- `traffic/src/main/java/com/example/traffic/domain/AnomalyEvent.java`
- `traffic/src/main/java/com/example/traffic/domain/MaintenanceTicket.java`
- `traffic/src/main/java/com/example/traffic/domain/MaintenanceTicketHistory.java`
- `traffic/src/main/resources/db/migration/009_predictive_ticket_history_backfill.sql`
- `traffic/src/main/resources/db/migration/010_anomaly_events_active_index_datasource.sql`

## 18. 예지보전 교통 컨텍스트 집계 시점 문제

### 문제

예지보전 판단에 차량 흐름, OCR 분석 결과, 과속 위반 데이터가 함께 필요하지만, 원본 데이터를 매번 실시간으로 계산하면 조회 비용이 커지고 평가 기준 시점이 흔들릴 수 있었다.

### 원인

예지보전 모델은 특정 시간 구간의 요약 지표를 입력으로 사용한다. 따라서 완료되지 않은 시간 구간을 집계하거나 매 요청마다 원본 테이블을 직접 계산하면 같은 화면에서도 결과가 달라질 수 있다.

### 해결

- `TrafficContextSample`을 두고 5분 단위 교통 컨텍스트를 저장하도록 했다.
- `TrafficContextAggregationService`에서 완료된 이전 구간만 집계하도록 했다.
- `PredictiveMaintenanceScheduler`에서 5분 주기로 교통 컨텍스트 집계와 카메라 성능 저하 평가를 실행하도록 했다.
- 실제 데이터와 시연 데이터를 구분할 수 있도록 `DataSourceType`을 사용했다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/domain/TrafficContextSample.java`
- `traffic/src/main/java/com/example/traffic/service/TrafficContextAggregationService.java`
- `traffic/src/main/java/com/example/traffic/etc/PredictiveMaintenanceScheduler.java`
- `traffic/src/main/java/com/example/traffic/common/enums/DataSourceType.java`
- `traffic/src/main/resources/db/migration/007_predictive_maintenance_schema.sql`

## 19. 공유/시연 DB 스키마 검증 문제

### 문제

로컬 개발에서는 `ddl-auto=update`로 실행되더라도, 공유 DB나 시연 환경에서는 엔티티 변경이 자동 반영되면서 실제 마이그레이션 누락을 놓칠 수 있었다.

### 원인

`ddl-auto=update`는 개발 편의에는 좋지만, 팀원이 같은 DB를 사용하거나 Docker 기반 시연 환경을 구성할 때는 어떤 SQL이 먼저 적용되어야 하는지 명확히 보장하기 어렵다.

### 해결

- 예지보전 스키마를 `007`부터 `010`까지 단계별 SQL로 분리했다.
- 시연/공유 환경용 `application-demo.yml`을 추가했다.
- `application-demo.yml`에서는 `spring.jpa.hibernate.ddl-auto=validate`, `spring.sql.init.mode=never`로 설정해 스키마 불일치를 빠르게 확인하도록 했다.
- 필요한 경우 `PredictiveDatabaseBootstrapRunner`로 데모 시드 적용 여부를 환경변수로 제어할 수 있게 했다.

### 관련 파일

- `traffic/src/main/resources/application.yml`
- `traffic/src/main/resources/application-demo.yml`
- `traffic/src/main/java/com/example/traffic/config/PredictiveDatabaseBootstrapRunner.java`
- `traffic/src/main/resources/db/migration/007_predictive_maintenance_schema.sql`
- `traffic/src/main/resources/db/migration/008_predictive_seed_policies.sql`
- `traffic/src/main/resources/db/migration/009_predictive_ticket_history_backfill.sql`
- `traffic/src/main/resources/db/migration/010_anomaly_events_active_index_datasource.sql`

## 20. 파트별 Docker 빌드 컨텍스트 분리 문제

### 문제

백엔드, FastAPI, 프론트엔드를 함께 Docker로 빌드할 때 각 파트의 빌드 컨텍스트가 커지면 불필요한 파일까지 이미지 빌드에 포함되고, 빌드 시간이 길어질 수 있었다.

### 원인

프로젝트 루트에는 백엔드뿐 아니라 FastAPI 서버, 프론트엔드, 문서, 발표 자료, 예지보전 모델 파일 등이 함께 존재한다. 각 서비스 Dockerfile이 필요한 범위만 가져가지 않으면 빌드 컨텍스트가 비대해지고 파트별 독립 빌드가 어려워진다.

### 해결

- `backend/traffic`, `fastapi-server`, `trafficAS-b`에 각각 `.dockerignore`를 추가했다.
- 각 Dockerfile이 해당 파트의 파일만 기준으로 빌드되도록 정리했다.
- `docker-compose.yml`에서 서비스별 빌드 컨텍스트를 분리했다.
- FastAPI 쪽은 predictive ML vendor 모듈을 이미지 안에서 사용할 수 있도록 구성했다.

### 관련 파일

- `traffic/.dockerignore`
- `traffic/Dockerfile`
- `fastapi-server/.dockerignore`
- `fastapi-server/Dockerfile`
- `trafficAS-b/Dockerfile`
- `docker-compose.yml`

## 21. 예지보전 Repository와 보안 권한 규칙 누락 문제

### 문제

예지보전 테이블과 엔티티가 추가되었지만 Repository 조회 메서드와 Security 경로 규칙이 함께 정리되지 않으면, 화면 조회나 내부 연동에서 데이터 접근이 막히거나 필요한 조건 검색을 구현하기 어려울 수 있었다.

### 원인

예지보전 기능은 카메라 상태 샘플, 이상 이벤트, 근거 데이터, 정책, 정비 티켓, 모델 예측 로그처럼 여러 테이블을 함께 조회한다. 기존 차량 흐름 API보다 조회 조건과 권한 경로가 많아졌기 때문에 Repository와 보안 설정을 같이 확장해야 했다.

### 해결

- 예지보전 도메인별 Repository를 추가했다.
- 카메라별 최신 샘플, 활성 이벤트, 정책 코드, 티켓 상태 같은 운영 화면 조회 조건을 Repository 메서드로 분리했다.
- `/internal/v1/**` 내부 수집 API와 `/api/v1/predictive/**` 운영 API 경로를 Security 설정에 반영했다.
- 내부 수집 API는 JWT가 아니라 API Key 검증 흐름으로 분리했다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/config/SecurityConfig.java`
- `traffic/src/main/java/com/example/traffic/repository/CameraHealthSampleRepository.java`
- `traffic/src/main/java/com/example/traffic/repository/AnomalyEventRepository.java`
- `traffic/src/main/java/com/example/traffic/repository/AnomalyEventEvidenceRepository.java`
- `traffic/src/main/java/com/example/traffic/repository/AnomalyPolicyRepository.java`
- `traffic/src/main/java/com/example/traffic/repository/MaintenanceTicketRepository.java`
- `traffic/src/main/java/com/example/traffic/repository/ModelPredictionLogRepository.java`
- `traffic/src/main/java/com/example/traffic/repository/TrafficContextSampleRepository.java`

## 22. SHADOW 모델 탐지 결과와 운영 이벤트 연결 문제

### 문제

AI 모델의 SHADOW 탐지 결과를 단순 로그로만 남기면 운영 화면의 이상 이벤트나 정비 흐름과 연결되지 않는다. 반대로 모델 결과를 바로 운영 이벤트로 확정하면 검증되지 않은 예측이 실제 알림처럼 보일 수 있었다.

### 원인

예지보전 모델은 룰 기반 탐지와 달리 실험/검증 단계의 예측 결과를 포함한다. 따라서 모델 예측 결과, 후보 이벤트, 실제 운영 이벤트를 같은 책임으로 처리하면 데이터 신뢰도와 운영 상태 관리가 섞일 수 있다.

### 해결

- 모델 예측 결과는 `ModelPredictionLog`로 저장했다.
- SHADOW 탐지 결과 처리는 `PredictiveShadowPredictionService`로 분리했다.
- 이상 후보 중복 방지와 활성 이벤트 판단은 `PredictiveAnomalyCandidateGuardService`에서 관리하도록 했다.
- 운영 이벤트 저장은 `PredictiveAnomalyEventIngestionService`에서 담당하게 하여 모델 결과와 운영 이벤트의 책임을 나누었다.

### 관련 파일

- `traffic/src/main/java/com/example/traffic/domain/ModelPredictionLog.java`
- `traffic/src/main/java/com/example/traffic/service/PredictiveShadowPredictionService.java`
- `traffic/src/main/java/com/example/traffic/service/PredictiveAnomalyCandidateGuardService.java`
- `traffic/src/main/java/com/example/traffic/service/PredictiveAnomalyEventIngestionService.java`
- `traffic/src/main/java/com/example/traffic/repository/ModelPredictionLogRepository.java`
- `traffic/src/main/java/com/example/traffic/client/PredictiveDetectionClient.java`

## 23. 예지보전 DB 검증과 성능 확인 자료 분리 문제

### 문제

예지보전 테이블이 추가된 뒤에는 단순히 애플리케이션이 실행되는지만 확인해서는 부족했다. 시연 데이터, 품질 검증 SQL, 성능 확인 SQL, 보존 정책 SQL이 흩어져 있으면 DB 담당자나 백엔드 담당자가 같은 기준으로 검증하기 어려웠다.

### 원인

예지보전 기능은 장기간 누적되는 샘플 데이터와 대시보드 조회 쿼리를 사용한다. 따라서 데이터 품질, 인덱스 성능, 시드 데이터, 오래된 샘플 정리 기준을 별도 리소스로 관리해야 했다.

### 해결

- DB 작업 진행 상황을 `db_todo_progress_2026_06_16.md`에 정리했다.
- 대시보드/기준선 조회 SQL을 `db/queries`에 분리했다.
- 데이터 품질 검증 SQL을 `db/validation`에 분리했다.
- 성능 확인용 `EXPLAIN ANALYZE` 결과와 부하 테스트 SQL을 `db/performance`에 정리했다.
- 오래된 샘플 정리 SQL을 `db/retention`에 분리했다.
- 데모 시드 데이터는 `db/seed`와 `traffic/src/main/resources/db/seed`에 정리했다.

### 관련 파일

- `traffic/src/main/resources/db/db_todo_progress_2026_06_16.md`
- `traffic/src/main/resources/db/queries/camera_baseline.sql`
- `traffic/src/main/resources/db/queries/predictive_dashboard.sql`
- `traffic/src/main/resources/db/validation/data_quality_checks.sql`
- `traffic/src/main/resources/db/performance/explain_analyze.md`
- `traffic/src/main/resources/db/performance/load_test.sql`
- `traffic/src/main/resources/db/retention/purge_old_samples.sql`
- `traffic/src/main/resources/db/seed/demo_seed.sql`
- `traffic/src/main/resources/db/seed/commercial_demo_seed.sql`

## 참고 테스트 명령어

Windows PowerShell 기준:

```powershell
cd C:\Users\smn12\OneDrive\바탕 화면\본프로젝트\backend\traffic
.\gradlew.bat test
```

특정 테스트만 실행:

```powershell
cd C:\Users\smn12\OneDrive\바탕 화면\본프로젝트\backend\traffic
.\gradlew.bat test --tests "com.example.traffic.controller.DetectionLogControllerIntegrationTest"
```

예지보전 운영 서비스 테스트:

```powershell
cd C:\Users\smn12\OneDrive\바탕 화면\본프로젝트\backend\traffic
.\gradlew.bat test --tests "com.example.traffic.service.PredictiveOperationsServiceTest"
```
