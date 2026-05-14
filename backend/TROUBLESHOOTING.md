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
- 실제 적용 가능한 SQL은 `traffic/src/main/resources/db/migration/001_backend_schema_updates.sql`에 분리해 두었다.
- `detection_logs.status`, `traffic_analysis_index.zone_id`, `detection_analysis_results`, `vehicle_flow_events.source_analysis_result_id` 등을 명시적으로 정리했다.
- `vehicle_flow_events`에는 속도와 체류 시간 컬럼을 추가했다.
- `hourly_traffic_stats`에는 평균 속도, 혼잡도, 평균 체류 시간, 중복 차량 수, 마지막 로그 ID 컬럼을 추가했다.

### 효과

- 팀원이 공유 DB를 사용할 때 필요한 변경 사항을 추적하기 쉬워졌다.
- `ddl-auto=update`에만 의존하지 않고 스키마 변경 의도를 문서화할 수 있게 되었다.

### 관련 파일

- `traffic/docs/dev-migration-notes.md`
- `traffic/src/main/resources/db/migration/001_backend_schema_updates.sql`
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

## 참고 테스트 명령어

Windows PowerShell 기준:

```powershell
cd C:\ksm\Traffic_Analytics_Proposal\backend\traffic
.\gradlew.bat test
```

특정 테스트만 실행:

```powershell
cd C:\ksm\Traffic_Analytics_Proposal\backend\traffic
.\gradlew.bat test --tests "com.example.traffic.controller.DetectionLogControllerIntegrationTest"
```
