# 🚦 교통 관리 시스템 (Traffic Management System)

본 프로젝트는 AI 기반의 실시간 교통 탐지 로그를 수집하고, 이를 시각별로 통계화하여 교통 흐름을 분석하는 **지능형 교통 관리 백엔드 시스템**입니다.

## 🛠 Tech Stack
* **Language**: Java 21
* **Framework**: Spring Boot 3.5.14
* **Database**: PostgreSQL
* **ORM**: Spring Data JPA
* **Security**: Spring Security & JWT (JJWT 0.12.6)
* **Documentation**: Swagger (SpringDoc OpenAPI 2.8.5)
* **Build Tool**: Gradle

---

## 🔍 프로젝트 핵심 로직 및 설계 특징

### 1. 고성능 로그 수집 및 데이터 방어 (`DetectionLogService`)
* **트랜잭션 최적화**: `ObjectProvider`를 통한 자기 참조 방식을 활용하여 데이터 검증과 저장 로직의 트랜잭션을 분리함으로써 데이터베이스 연결 시간을 최소화했습니다.
* **엄격한 데이터 검증**: AI 서버로부터 수신되는 필수 값(`cameraCode`, `detectedAt` 등)과 신뢰도 점수(0.0~1.0)에 대한 유효성을 철저히 검증합니다.
* **유연한 엔티티 관리**: 미등록 차량 탐지 시 실시간으로 차량 정보를 생성하여 데이터 누락을 방지합니다.

### 2. 하이브리드 보안 아키텍처 (`SecurityConfig`)
* **사용자 권한 제어**: JWT 기반의 Stateless 인증을 통해 관리자(ADMIN)와 일반 사용자의 API 접근 권한을 세밀하게 분리했습니다.
* **시스템 간 전용 인증**: AI 서버의 로그 전송 API는 성능 최적화를 위해 JWT 대신 전용 헤더(`X-Internal-Api-Key`) 검증 방식을 채택했습니다.

### 3. 실시간 통계 자동화 (`TrafficStatScheduler`)
* **스케줄링**: 매 시 정각(`0 0 * * * *`) 스케줄러가 작동하여 직전 1시간 동안의 구역별 교통 데이터를 자동으로 집계 및 통계화합니다.
* **방향성 분석**: 카메라의 설치 방향 정보를 기반으로 차량의 진입 및 진출 흐름(`VehicleFlowEvent`)을 분석합니다.

---

## 🚀 실행 및 빌드 가이드

### 1. 데이터베이스 설정
PostgreSQL 서버가 구동 중이어야 하며, 아래 설정이 필요합니다.

* **DB Name**: `traffic`
* **Port**: `5432`
* **Account**: `postgres` / `1004`

### 2. 빌드 명령어

#### 전체 빌드 및 테스트
```bash
./gradlew build
```

#### 테스트 제외 빌드
```bash
./gradlew build -x test
```

### 3. 서버 구동 확인
서버 실행 시 콘솔에서 아래 로그를 확인하세요.

* `HikariPool-1 - Start completed` : DB 연결 성공 확인
* `Started TrafficApplication in ... seconds` : 서버 정상 구동 완료

---

## 📂 API Documentation

애플리케이션 실행 후 아래 주소에서 대화형 API 문서를 확인할 수 있습니다.

### Swagger UI
```text
http://localhost:8080/swagger-ui.html
```

---

## ⚠️ 예외 처리 규약

* AI 응답 값 오류 또는 비즈니스 로직 위반 시 `BusinessException`을 통해 일관된 에러 응답과 HTTP 상태 코드(예: `502 Bad Gateway`, `400 Bad Request`)를 반환합니다.