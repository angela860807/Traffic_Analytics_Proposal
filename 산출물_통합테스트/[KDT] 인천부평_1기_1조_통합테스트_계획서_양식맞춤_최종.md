# 통합테스트 계획서

## 1. 테스트 계획

### 1.1 테스트 목적
- Docker Compose 기반 최종 실행 환경에서 Frontend, FastAPI, Spring Boot, PostgreSQL 간 연동 상태를 검증한다.
- 프론트엔드 분석 요청부터 FastAPI 분석 처리, Spring Boot 저장 API 호출, PostgreSQL 저장, 프론트엔드 조회 화면 표시까지 전체 흐름을 확인한다.
- 발표 및 시연 환경에서 실제 사용자 흐름이 정상 동작하는지 확인한다.
- 각 모듈이 단독으로 정상 동작하는 것을 넘어, API 계약과 데이터 필드가 모듈 사이에서 누락 없이 전달되는지 확인한다.
- 장애 발생 시 어느 구간에서 문제가 발생했는지 추적할 수 있도록 단계별 관찰 지점을 정의한다.

### 1.2 테스트 범위
- Docker Compose 전체 서비스 실행
- Frontend에서 FastAPI 분석 기능 호출
- FastAPI 분석 결과의 Spring Boot 저장 API 전송
- Spring Boot의 PostgreSQL 저장 및 조회
- Spring Boot 조회 API 응답의 프론트엔드 표시

### 1.3 테스트 일정
| 단계 | 일정 | 담당자 | 비고 |
|---|---|---|---|
| 통합 환경 준비 | 2026-06-04 | QA/통합 담당 | Docker Compose 실행 |
| 통합 시나리오 수행 | 2026-06-04 | QA/통합 담당 | API/DB/화면 확인 |
| 결과서 작성 | 2026-06-04 | QA/통합 담당 | 캡처 증빙 정리 |

### 1.4 역할 및 책임
- FastAPI 담당: 분석 API 및 Spring Boot 전송 검증
- Spring Boot 담당: 저장 API, 조회 API, DB 저장 검증
- Frontend 담당: 분석 요청 화면 및 결과 조회 화면 검증
- QA/통합 담당: 전체 흐름 수행, 캡처 증빙 수집, 결과서 작성

### 1.5 통합 대상 구성
| 구간 | 송신 모듈 | 수신 모듈 | 주요 데이터 | 검증 포인트 |
|---|---|---|---|---|
| 1 | Frontend | FastAPI | cameraCode, capturedAt, image/frame | 분석 요청 정상 수신 및 결과 응답 |
| 2 | FastAPI | Spring Boot | plateNumber, detectionType, confidenceScore, imagePath, detectedAt | 저장 API 응답 및 상태값 확인 |
| 3 | Spring Boot | PostgreSQL | detection_logs, detection_analysis_results, speed_violations | 테이블 row 생성 및 최신 데이터 조회 |
| 4 | Frontend | Spring Boot | 감지 로그/과속 위반 조회 요청 | API 응답 기반 화면 표시 |

## 2. 테스트 전략
- End-to-End 흐름 테스트
- API 연동 테스트
- DB 저장 확인 테스트
- 화면 표시 확인 테스트
- Docker 실행 환경 확인

### 2.1 선행 조건
- Docker Desktop 실행 상태
- PostgreSQL, Spring Boot, FastAPI, Frontend 컨테이너 실행 가능 상태
- Spring Boot 내부 API Key와 FastAPI 환경변수의 저장 API 경로 일치
- 프론트엔드 API base URL이 Docker/nginx 프록시 기준으로 요청 가능한 상태
- 테스트용 이미지 또는 mock 분석 요청 데이터 준비

### 2.2 종료 조건
- 전체 컨테이너가 정상 실행된다.
- 프론트엔드에서 FastAPI 분석 요청이 수행된다.
- FastAPI 분석 결과가 Spring Boot 저장 API로 전달된다.
- PostgreSQL에서 감지 로그/분석 결과/과속 위반 데이터가 조회된다.
- Spring Boot 조회 API 응답이 확인된다.
- 프론트엔드 화면에서 저장/조회 결과가 표시된다.

### 2.3 실패 판단 기준
- 컨테이너 빌드 또는 실행 실패
- FastAPI 분석 API 4xx/5xx 응답
- FastAPI to Spring Boot 저장 요청 실패 또는 API Key 오류
- DB 테이블에 저장 row 미생성
- Spring Boot 조회 API 응답 실패
- 프론트엔드 화면에서 결과 표시 누락

## 3. 테스트 실행
| 테스트 ID | 항목 | 시나리오 | 기대 결과 |
|---|---|---|---|
| IT-1.1 | Docker 전체 실행 | docker compose up --build 수행 | 전체 서비스 정상 실행 |
| IT-1.2 | Frontend to FastAPI | 프론트에서 분석 요청 수행 | FastAPI 분석 결과 응답 |
| IT-1.3 | FastAPI to Spring Boot | 분석 결과 저장 API 전송 | Spring Boot 저장 응답 반환 |
| IT-1.4 | Spring Boot to PostgreSQL | 감지 로그/분석 결과/과속 위반 저장 확인 | DB row 조회 가능 |
| IT-1.5 | Spring Boot API 조회 | 감지 로그/과속 위반 조회 API 호출 | 정상 응답 |
| IT-1.6 | Frontend 결과 표시 | 저장/조회 결과를 프론트 화면에서 확인 | 화면 정상 표시 |

### 3.1 상세 통합 시나리오
| 단계 | 수행 내용 | 확인 데이터 | 증빙 |
|---|---|---|---|
| 1 | Docker Compose로 전체 서비스 실행 | 컨테이너 빌드/기동 로그 | IT_001 |
| 2 | 프론트엔드에서 분석 요청 수행 | FastAPI 분석 결과 표시 | IT_003 |
| 3 | FastAPI가 Spring Boot 저장 API 호출 | 저장 응답, logId/상태값 | IT_004 |
| 4 | PostgreSQL 감지 로그 조회 | detection_logs 최신 row | IT_005_01 |
| 5 | PostgreSQL 분석 결과 조회 | detection_analysis_results 최신 row | IT_005_02 |
| 6 | PostgreSQL 과속 위반 조회 | speed_violations 조회 결과 | IT_005_03 |
| 7 | Spring Boot 조회 API 확인 | 감지 로그/과속 위반 API 응답 | API_002, API_003 |
| 8 | 프론트엔드 화면 확인 | 감지 로그 화면 표시 | FE_003 |
