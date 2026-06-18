# 통합테스트 결과서

## 1. 테스트 항목
- Docker 전체 실행
- Frontend to FastAPI 분석 요청
- FastAPI to Spring Boot 저장
- Spring Boot to PostgreSQL 저장
- Spring Boot 조회 API 응답
- Frontend 결과 화면 표시

## 1.1 통합 흐름 요약
본 통합테스트는 단일 기능의 정상 여부가 아니라, 사용자가 프론트엔드에서 분석을 요청했을 때 분석 결과가 백엔드와 DB를 거쳐 다시 조회 화면에 표시되는 전체 흐름을 검증하였다.
검증 흐름은 `Frontend → FastAPI → Spring Boot → PostgreSQL → Spring Boot API → Frontend` 순서로 수행하였다.

## 1.2 주요 인터페이스 확인 항목
| 인터페이스 | 확인 항목 |
|---|---|
| Frontend to FastAPI | 분석 요청 전송, 분석 결과 응답 표시 |
| FastAPI to Spring Boot | 내부 API Key, 저장 API 경로, 분석 결과 payload |
| Spring Boot to PostgreSQL | 감지 로그, 분석 결과, 과속 위반 테이블 저장 |
| Spring Boot to Frontend | 조회 API 응답 및 화면 표시 |

## 2. 테스트 결과
| 테스트 ID | 항목 | 시나리오 | 결과 |
|---|---|---|---|
| IT-1.1 | Docker 전체 실행 | docker compose up --build 수행 | 정상 |
| IT-1.2 | Frontend to FastAPI | 프론트에서 분석 요청 후 결과 확인 | 정상 |
| IT-1.3 | FastAPI to Spring Boot | FastAPI 분석 결과를 Spring Boot 저장 API로 전송 | 정상 |
| IT-1.4 | PostgreSQL 저장 | detection_logs, detection_analysis_results, speed_violations 조회 | 정상 |
| IT-1.5 | Spring Boot API 조회 | 감지 로그/과속 위반 조회 API 응답 확인 | 정상 |
| IT-1.6 | Frontend 결과 표시 | 감지 로그 화면에서 결과 표시 확인 | 정상 |
| 완료율 | - | 정상 6건, 오류 0건 | 100% |

## 2.1 단계별 확인 결과
| 단계 | 검증 내용 | 확인 결과 |
|---|---|---|
| Docker 실행 | 전체 서비스 빌드 및 실행 로그 확인 | 정상 |
| 분석 요청 | 프론트엔드에서 FastAPI 분석 결과 화면 확인 | 정상 |
| 저장 요청 | FastAPI가 Spring Boot 저장 API 응답 수신 | 정상 |
| DB 저장 | detection_logs, detection_analysis_results, speed_violations 조회 | 정상 |
| API 조회 | Spring Boot 감지 로그/과속 위반 조회 API 응답 | 정상 |
| 화면 표시 | 프론트엔드 감지 로그 화면 표시 | 정상 |

## 2.2 통합 관점 검토
- Docker Compose 기반으로 실행 환경을 통일하여 로컬 실행 편차를 줄였다.
- FastAPI 분석 결과가 Spring Boot 저장 API로 전달되는 경로를 확인하였다.
- 저장 API 응답뿐 아니라 PostgreSQL 테이블 조회를 통해 실제 저장 여부를 확인하였다.
- DB에 저장된 데이터가 Spring Boot 조회 API와 프론트엔드 화면에서 확인되는지 검증하였다.
- 통합 흐름 내 주요 실패 지점인 컨테이너 실행, API 응답, DB 저장, 화면 표시를 단계별로 분리하여 확인하였다.

## 3. 개선사항
- Docker 실행 및 API/DB 조회 절차를 README에 고정하여 재현성을 높인다.
- 통합 시나리오를 자동화 테스트로 확장하여 수동 캡처 의존도를 줄인다.
- 프론트엔드 테스트 코드와 실제 컴포넌트 구조를 동기화하여 단위테스트 실패 항목을 보완한다.
- FastAPI to Spring Boot 저장 실패 시 재시도 횟수, 오류 메시지, 실패 payload를 별도 로그로 남기는 방식을 강화한다.
- 프론트엔드에서 API 장애 상태를 사용자에게 명확히 표시할 수 있도록 error/empty/loading 상태 검증을 통합 시나리오에 추가한다.
