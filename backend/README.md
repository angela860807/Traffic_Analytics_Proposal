# 🚦 교통 관리 시스템 (Traffic Management System)

AI 기반 실시간 교통 탐지 로그를 수집하고, 이를 시각별로 통계화하여 교통 흐름을 분석하는 지능형 교통 관리 백엔드 시스템입니다.

---

# 🛠 Tech Stack

- **Language**: Java 21
- **Framework**: Spring Boot 3.5.14
- **Database**: PostgreSQL
- **ORM**: Spring Data JPA
- **Security**: Spring Security & JWT (JJWT 0.12.6)
- **Documentation**: Swagger (SpringDoc OpenAPI 2.8.5)
- **Build Tool**: Gradle

---

# 🏛 시스템 아키텍처 (System Architecture)

본 시스템은 대량의 데이터 처리를 위한 성능 최적화와 시스템 간 보안을 고려하여 설계되었습니다.

1. **Ingestion Layer**
   - AI 서버가 탐지한 차량 데이터를 전용 API(`X-Internal-Api-Key`)를 통해 수신

2. **Processing Layer**
   - `ObjectProvider` 자기 참조 기반 트랜잭션 분리
   - 데이터 검증 후 비동기 흐름 분석 수행

3. **Storage Layer**
   - PostgreSQL 기반 로그 및 통계 데이터 저장
   - Spring Data JPA를 통한 영속성 관리

4. **Analysis Layer**
   - Spring Scheduler 기반 시간 단위 통계 자동 집계

---

# 📂 프로젝트 구조 (Project Structure)

```text
└─com.example.traffic
    │  TrafficApplication.java
    │
    ├─common.enums
    │      DetectionType.java
    │      Direction.java
    │      QnaStatus.java
    │      UserRole.java
    │      UserStatus.java
    │      VehicleStatus.java
    │      ZoneType.java
    │
    ├─config
    │      SchedulingConfig.java
    │      SecurityConfig.java
    │      SwaggerConfig.java
    │
    ├─controller
    │      CameraController.java
    │      CommentController.java
    │      DetectionLogController.java
    │      HourlyTrafficStatController.java
    │      MemberController.java
    │      NoticeController.java
    │      PostController.java
    │      QnaController.java
    │      VehicleController.java
    │      VehicleFlowEventController.java
    │      ZoneController.java
    │
    ├─domain
    │      Camera.java
    │      Comment.java
    │      DetectionLog.java
    │      HourlyTrafficStat.java
    │      Member.java
    │      Notice.java
    │      Post.java
    │      QnaAnswer.java
    │      QnaQuestion.java
    │      Vehicle.java
    │      VehicleFlowEvent.java
    │      Zone.java
    │
    ├─dto
    │  ├─request
    │  │      CameraSaveRequest.java
    │  │      DetectionRequest.java
    │  │      LoginRequest.java
    │  │      ...
    │  │
    │  └─response
    │          CommonResponse.java
    │          DetectionResponse.java
    │          TokenResponse.java
    │          ...
    │
    ├─etc
    │      BusinessException.java
    │      GlobalExceptionHandler.java
    │      TrafficStatScheduler.java
    │
    ├─repository
    │      DetectionLogRepository.java
    │      ZoneRepository.java
    │      ...
    │
    ├─security
    │      CustomUserDetailsService.java
    │      JwtAuthenticationFilter.java
    │      JwtTokenProvider.java
    │
    └─service
           DetectionLogService.java
           HourlyTrafficStatService.java
           VehicleFlowEventService.java
           ...
```

---

# 🚀 실행 및 빌드 가이드

## 1. PostgreSQL 설정

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/traffic
spring.datasource.username=postgres
spring.datasource.password=1004
```

## 2. 프로젝트 빌드

### 전체 빌드

```bash
./gradlew build
```

### 테스트 제외 빌드

```bash
./gradlew build -x test
```

---

# ▶️ 서버 실행

```bash
./gradlew bootRun
```

## 정상 실행 로그 예시

```text
HikariPool-1 - Start completed.
Started TrafficApplication in 8.421 seconds
```

---

# 📘 API 문서

## Swagger UI

```text
http://localhost:8080/swagger-ui.html
```

## AI 서버 인증 헤더

```http
X-Internal-Api-Key: traffic-ai-internal-key-2026
```

---

# ⚠️ 예외 처리 규약

- `BusinessException` 기반 사용자 정의 예외 처리
- `GlobalExceptionHandler`를 통한 전역 예외 응답 관리
- AI 데이터 오류 및 외부 요청 실패에 대해 일관된 HTTP 응답 반환

### 예시 응답

```json
{
  "success": false,
  "message": "Invalid detection data",
  "status": 400
}
```

---

# 📈 주요 기능

- AI 차량 탐지 로그 실시간 수집
- 차량 이동 흐름 분석
- 시간대별 교통 통계 자동 집계
- JWT 기반 인증/인가 처리
- Swagger 기반 REST API 문서 제공
- Scheduler 기반 배치 통계 처리

---

# 🔐 보안 구조

- Spring Security 기반 인증 처리
- JWT Access Token 기반 사용자 인증
- 내부 AI 서버 전용 API Key 인증 분리
- 권한(Role) 기반 API 접근 제어

---

# 🧩 핵심 서비스

| Service | Description |
|---|---|
| `DetectionLogService` | AI 탐지 로그 저장 및 검증 |
| `VehicleFlowEventService` | 차량 흐름 이벤트 분석 |
| `HourlyTrafficStatService` | 시간 단위 통계 집계 |
| `JwtTokenProvider` | JWT 생성 및 검증 |
| `TrafficStatScheduler` | 스케줄 기반 통계 자동 처리 |

---

# 🗄 Database

## 주요 테이블

- `detection_log`
- `vehicle`
- `vehicle_flow_event`
- `hourly_traffic_stat`
- `zone`
- `camera`
- `member`

---

# 📌 개발 환경

| 항목 | 버전 |
|---|---|
| Java | 21 |
| Spring Boot | 3.5.14 |
| PostgreSQL | 16+ |
| Gradle | 8+ |
