# 단위테스트 계획서

## 문서 정보

- 프로젝트명: 번호판 인식 스마트 교통안전 시스템
- 팀명: 인천부평_1기_1조
- 작성일: 2026. 06. 04
- 작성 기준: Docker Compose 기반 최종 실행본, FastAPI/Spring Boot/Vue 3/PostgreSQL 연동 구조

## 1. 테스트 계획

### 1.1 테스트 목적

- FastAPI, Spring Boot, Vue 프론트엔드 주요 기능의 정상 동작 여부를 검증한다.
- API 계약, 응답 형식, DB 저장 결과, 화면 표시 상태가 최종 실행본 기준으로 일치하는지 확인한다.
- 자동화 테스트와 수동 API/DB 확인을 병행하여 발표 및 시연 환경에서 발생 가능한 결함을 조기에 식별한다.
- 테스트 수행 결과와 캡처 증빙을 남겨 산출물 제출 시 재현 가능한 근거를 확보한다.

### 1.2 테스트 범위

- FastAPI: Health Check, 이미지/영상 감지 처리, 번호판 정규화, 속도 설정/측정 로직, Spring Boot 전송 클라이언트
- Spring Boot: 감지 로그 저장, 분석 결과 저장, 중복 감지 처리, OCR 실패 처리, 과속 위반 조회/상태 처리
- Vue 프론트엔드: 주요 화면 렌더링, 감지 로그/대시보드 표시, 상태 컴포넌트 및 교통 혼잡도 유틸리티
- PostgreSQL: detection_logs, detection_analysis_results, speed_violations 저장 및 조회
- Docker Compose: PostgreSQL, Spring Boot, FastAPI, Frontend 컨테이너 빌드 및 실행

### 1.3 테스트 제외 범위

- YOLO/PaddleOCR 모델 자체의 학습 성능 평가
- 대규모 부하 테스트 및 장시간 안정성 테스트
- 운영 보안 진단, 침투 테스트, 접근 제어 정책 검증

### 1.4 테스트 일정

| 단계 | 일정 | 담당 | 비고 |
|---|---|---|---|
| 테스트 환경 준비 | 2026-06-04 | QA/통합 담당 | Docker Compose 및 의존성 설치 확인 |
| 단위테스트 실행 | 2026-06-04 | 각 파트 담당/QA | pytest, Gradle test, Vitest, Vite build |
| API/DB 확인 | 2026-06-04 | QA/통합 담당 | curl/Swagger/psql 기반 증빙 수집 |
| 결과서 작성 | 2026-06-04 | QA/통합 담당 | 캡처 이미지 및 결과 표 정리 |

### 1.5 역할 및 책임

| 역할 | 책임 |
|---|---|
| PM | 테스트 범위 승인 및 최종 산출물 검토 |
| FastAPI 담당 | AI 분석 API, OCR/번호판 처리, Spring Boot 전송 기능 검증 |
| Spring Boot 담당 | 저장 API, 조회 API, DB 연동, 예외 처리 검증 |
| Frontend 담당 | 화면 렌더링, API 응답 표시, 상태 처리 검증 |
| QA/통합 담당 | Docker 실행 환경, 전체 테스트 수행, 캡처 증빙 수집, 결과서 작성 |

## 2. 테스트 전략

### 2.1 테스트 유형

- 자동화 단위테스트: pytest, JUnit/Gradle, Vitest
- 빌드 검증: Vite production build
- API Smoke Test: FastAPI 및 Spring Boot 주요 API 응답 확인
- DB 저장 확인: PostgreSQL 테이블 조회
- 화면 확인: 프론트엔드 주요 화면 및 감지 결과 표시 확인

### 2.2 테스트 환경

| 구분 | 내용 |
|---|---|
| OS | Windows |
| Container | Docker Compose |
| DB | PostgreSQL 16 |
| Backend | Spring Boot 3.5.14, Java 21 |
| AI API | FastAPI, Python 3.12 |
| Frontend | Vue 3, Vite 5 |
| Node/NPM | Node v24.13.1, npm 11.8.0 |

### 2.3 테스트 도구

- pytest
- Gradle/JUnit
- Vitest
- Vite build
- Docker Compose
- Swagger UI
- curl/PowerShell Invoke-RestMethod
- PostgreSQL psql

## 3. 테스트 실행 계획

| 테스트 ID | 구분 | 테스트 항목 | 검증 기준 |
|---|---|---|---|
| UT-FAST-001 | FastAPI | pytest 자동화 테스트 | 전체 테스트 통과, 기능 실패 없음 |
| UT-FAST-002 | FastAPI | Health Check API | `/health` 200 응답 및 service/status 확인 |
| UT-SPR-001 | Spring Boot | Gradle/JUnit 테스트 | Spring context 및 감지 로그 통합 테스트 통과 |
| UT-FE-001 | Frontend | Vitest 테스트 | 컴포넌트/컴포저블 테스트 수행 결과 확인 |
| UT-FE-002 | Frontend | Vite production build | `npm run build` 정상 완료 |
| UT-API-001 | API | 감지 로그 조회 API | `/api/v1/detection-logs` 응답 확인 |
| UT-API-002 | API | 과속 위반 조회 API | `/api/speed-violations` 응답 확인 |
| UT-DB-001 | DB | 감지 로그 저장 조회 | `detection_logs` 최신 데이터 조회 가능 |
| UT-DB-002 | DB | 분석 결과 저장 조회 | `detection_analysis_results` 최신 데이터 조회 가능 |
| UT-DB-003 | DB | 과속 위반 조회 | `speed_violations` 조회 가능 |
| UT-INT-001 | 연동 | FastAPI to Spring Boot 저장 | FastAPI 분석 결과가 Spring Boot 저장 API로 전달됨 |
| UT-INT-002 | 화면 | 프론트 감지 결과 표시 | 프론트 화면에서 감지/조회 결과 확인 가능 |

## 4. 성공/실패 기준

- 성공: 명령어 종료 코드 0, API 200 응답, DB 조회 성공, 화면 표시 정상
- 실패: 테스트 suite 실패, API 4xx/5xx 오류, DB 저장 누락, 화면 표시 불가
- 경고: 테스트는 통과했으나 deprecation, chunk size, 캐시 도구 미설치 등 개선 권고가 있는 경우
