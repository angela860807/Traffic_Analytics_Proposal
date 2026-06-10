# TAS-PM Spring Boot 작업 TODO

## 1. 목표와 담당 파트

Spring Boot는 예지보전의 시스템 오브 레코드다. 상태 샘플과 교통 맥락을 저장하고, FastAPI 탐지 결과를 정책에 따라 이상 이벤트·정비 티켓으로 변환하며, Frontend API와 권한·SLA·이력을 제공한다.

| 역할 | 담당 파트 |
|---|---|
| 구현 소유 | Spring Boot 파트 |
| PostgreSQL schema 계약 협업 | DB 파트 |
| 내부 탐지 API 연동 | FastAPI 파트 |

Controller, Service, Repository, DTO, Entity를 분리하고 Entity를 API에 직접 노출하지 않는다.

Spring Boot 파트의 단독 소유 범위는 `backend/traffic/src/main/java/**`다. migration SQL, seed SQL, 인덱스 SQL은 DB 파트가 소유한다.

## 2. 도메인 구조

권장 package:

```text
predictive/
  controller/
  service/
  repository/
  domain/
  dto/
    request/
    response/
  client/
  scheduler/
  exception/
  mapper/
```

핵심 Entity:

```text
CameraHealthSample
TrafficContextSample
CameraLink
AnomalyPolicy
DetectorVersion
AnomalyEvent
AnomalyEventEvidence
ModelPredictionLog
MaintenanceTicket
MaintenanceTicketHistory
```

## 3. JPA·DB 계약 연동

- [ ] ERD 기준 Entity 작성
- [ ] Enum을 `STRING`으로 매핑
- [ ] Repository와 조회 projection 작성
- [ ] Entity 연관관계의 fetch 전략 명시
- [ ] DB 파트가 제공한 migration과 JPA mapping 일치 확인
- [ ] PostgreSQL 16 기준 JDBC·Hibernate mapping 확인
- [ ] `TIMESTAMPTZ`를 `OffsetDateTime`으로 매핑
- [ ] `NUMERIC`을 `BigDecimal`로 매핑
- [ ] `JSONB`를 Hibernate 6 `@JdbcTypeCode(SqlTypes.JSON)`로 매핑
- [ ] identity PK에 `GenerationType.IDENTITY` 적용
- [ ] 로컬 `ddl-auto=update`, 팀 공용·시연 `ddl-auto=validate` profile 분리
- [ ] 팀 공용·시연 profile의 `spring.sql.init.mode=never` 적용
- [ ] schema 변경 요청을 컬럼명·타입·null·기본값 형태로 DB 파트에 전달

Spring Boot 파트는 migration 파일을 직접 작성하지 않는다. DB 제약조건 위반은 서비스 예외로 변환하되 제약조건 자체의 소유자는 DB 파트다.

PostgreSQL 오류 매핑:

```text
23505 unique_violation -> 409 CONFLICT 또는 DUPLICATE_RESOURCE
23503 foreign_key_violation -> 400 INVALID_REQUEST
23514 check_violation -> 400 INVALID_REQUEST
```

## 4. 데이터 수집·집계

### 4-1. 카메라 상태 수집

- [ ] `POST /internal/v1/camera-health-samples`
- [ ] `X-Internal-Api-Key` 인증
- [ ] DTO validation
- [ ] `idempotencyKey`와 업무 unique 기준 PostgreSQL `ON CONFLICT` upsert
- [ ] 지연 샘플 저장 및 실시간 평가 제외 플래그 처리
- [ ] 수집 성공 후 Rule 평가 작업 호출

트랜잭션:

- 샘플 저장은 단일 트랜잭션이다.
- FastAPI 호출은 DB 트랜잭션 밖에서 수행한다.
- 탐지 서비스 실패 시 샘플 저장은 롤백하지 않고 재평가 대상을 기록한다.
- JPA `save()`로 upsert를 흉내 내지 않고 PostgreSQL native query의 `ON CONFLICT`를 사용한다.

### 4-2. 교통 맥락 집계

- [ ] 5분 scheduler 구현
- [ ] `vehicle_flow_events` 차량 수·속도 집계
- [ ] `detection_analysis_results` OCR 시도·성공·실패 집계
- [ ] `speed_violations` 과속 건수 집계
- [ ] 원천 event ID 범위와 처리 건수 로그
- [ ] 동일 구간 재실행 시 PostgreSQL `ON CONFLICT` upsert
- [ ] 품질 상태 계산

교통 맥락 자체로 `AnomalyEvent`나 `MaintenanceTicket`을 생성하지 않는다.

## 5. 기준선·탐지 orchestration

### 5-1. Rule 평가

- [ ] 새 상태 샘플 저장 후 최근 연속 구간 조회
- [ ] 활성 Rule 정책 조회
- [ ] `POST /internal/v1/anomaly-detection/camera-health/evaluate` 호출
- [ ] timeout 3초, 제한된 retry 적용
- [ ] 응답 후보를 이벤트 서비스에 전달

### 5-2. 기준선·추세 평가

- [ ] 5분마다 카메라별 평가
- [ ] 최근 60분 유효 상태 샘플 조회
- [ ] Trend Projection에는 마지막 15분, LSTM AutoEncoder에는 전체 60분 전달
- [ ] 최근 14일 동일 30분 시간대 정상 기준선 조회
- [ ] 최소 기준선 표본 30개 확인
- [ ] 현재·인접 카메라 교통 맥락 조회
- [ ] `POST /internal/v1/anomaly-detection/camera-degradation/evaluate` 호출
- [ ] 기준선 부족 시 `BASELINE_LEARNING` 상태 제공
- [ ] `shadowCandidates`를 `model_prediction_logs`에 멱등 저장
- [ ] SHADOW 후보를 이벤트 처리 서비스에 전달하지 않음

기준선 제외:

```text
운영 profile: data_source != REAL
demo profile: data_source != SIMULATED
quality_status != COMPLETE
is_imputed = true
활성 이상 이벤트 구간
운영자가 DISMISSED가 아닌 장애로 확정한 구간
```

운영과 demo 기준선은 절대 합치지 않는다. `FAULT_INJECTED` 현재 구간은 demo profile에서 `SIMULATED` 정상 기준선과만 비교한다.

## 6. 이벤트 처리

- [ ] detector·정책 코드 유효성 검증
- [ ] 카메라 존재 여부 검증
- [ ] `AnomalyEvent`와 evidence를 한 트랜잭션으로 저장
- [ ] PostgreSQL partial unique 충돌 시 기존 활성 이벤트 갱신
- [ ] 심각도 상향만 자동 적용
- [ ] 정상 3회 연속 시 `RECOVERED`
- [ ] 30분 내 재발 시 `OPEN` 복귀와 recurrence 증가
- [ ] acknowledge·resolve·dismiss 상태 전이 검증
- [ ] 해결 시 confirmed cause·resolution note 필수
- [ ] 오탐 시 reason 필수

저장 필드:

```text
detectionMethod
detectorVersion
policyCode
baselineFrom / baselineTo / baselineSampleCount
trendSlope / trendConfidence
predictionHorizonMinutes / projectedThresholdCrossingAt
suspectedCauses
evidence
```

활성 이벤트 생성·갱신은 하나의 `@Transactional` 경계에서 처리한다. partial unique 충돌이 발생하면 새 이벤트를 재시도하지 않고 기존 활성 이벤트를 잠금 조회해 갱신한다.

SHADOW 모델 결과는 별도 트랜잭션으로 저장한다. `operatingMode != ACTIVE`인 detector 결과가 `AnomalyEventService`로 전달되면 예외 처리한다.

## 7. Health Score

- [ ] 최신 유효 지표 조회
- [ ] 정책 기준으로 지표별 0~100 점수 변환
- [ ] 가중 평균 계산
- [ ] 유효 지표 4개 미만은 `INSUFFICIENT_DATA`
- [ ] 기준선 표본 부족은 `BASELINE_LEARNING`
- [ ] 카메라 오프라인은 점수 0, 상태 `OFFLINE`
- [ ] 목록 조회의 N+1 방지

Health Score는 고장 확률이 아니라 운영 요약 지표임을 응답 문서와 발표에 명시한다.

## 8. 정비 티켓·SLA

자동 생성:

```text
CRITICAL 또는 CAMERA_OFFLINE -> P1
WARNING 15분 지속 -> P2
24시간 내 같은 WARNING 3회 -> P2
10분 내 CRITICAL 도달 예측 -> P2
운영자 수동 생성 -> P3 기본
```

- [ ] 이벤트당 티켓 하나 보장
- [ ] 티켓 번호 원자적 발급
- [ ] 배정 시 `OPEN -> ASSIGNED`
- [ ] 허용 상태 전이 검증
- [ ] 모든 변경을 history에 append
- [ ] P1/P2/P3 SLA 계산
- [ ] overdue 계산
- [ ] MTTA·MTTR 계산 API 제공
- [ ] `CLOSED` 권한 제한

상태 전이:

```text
OPEN -> ASSIGNED
ASSIGNED -> IN_PROGRESS
IN_PROGRESS -> RESOLVED
RESOLVED -> CLOSED
```

관리자 강제 종료가 필요하면 별도 endpoint와 감사 로그를 사용하고 일반 상태 변경에 섞지 않는다.

## 9. Frontend API

- [ ] `GET /api/v1/predictive/summary`
- [ ] `GET /api/v1/predictive/cameras`
- [ ] `GET /api/v1/predictive/cameras/{cameraId}/health-history`
- [ ] `GET /api/v1/predictive/traffic-context`
- [ ] `GET /api/v1/predictive/anomaly-events`
- [ ] `GET /api/v1/predictive/anomaly-events/{eventId}`
- [ ] `POST /api/v1/predictive/anomaly-events/{eventId}/acknowledge`
- [ ] `POST /api/v1/predictive/anomaly-events/{eventId}/resolve`
- [ ] `POST /api/v1/predictive/anomaly-events/{eventId}/dismiss`
- [ ] `GET /api/v1/predictive/maintenance-tickets`
- [ ] `POST /api/v1/predictive/maintenance-tickets`
- [ ] `POST /api/v1/predictive/maintenance-tickets/{ticketId}/assign`
- [ ] `POST /api/v1/predictive/maintenance-tickets/{ticketId}/status`
- [ ] `GET /api/v1/predictive/policies`
- [ ] `PATCH /api/v1/predictive/policies/{policyCode}`

목록 API:

- `Pageable`의 size 최대 100
- 허용 정렬 필드 whitelist
- Enum·날짜 validation
- 역할별 데이터 변경 권한
- 조회 DTO projection으로 N+1 방지
- 이벤트 상세는 평가 시각이 가장 가까운 SHADOW 모델 점수를 선택적으로 포함

## 10. 예외·보안·관측성

- [ ] `@RestControllerAdvice` 공통 오류 응답
- [ ] validation field error 매핑
- [ ] 존재하지 않는 리소스 `404`
- [ ] 중복·상태 충돌 `409`
- [ ] JWT 역할 검사
- [ ] 내부 API key 별도 filter
- [ ] requestId MDC 적용
- [ ] cameraId, eventId, ticketId, policyCode, detectorVersion 구조화 로그
- [ ] FastAPI timeout·실패 metric
- [ ] scheduler 실행 시간·처리 건수 metric

## 11. 테스트

파트 테스트는 다음 3개만 수행하고 전체 E2E는 최종 병합 담당이 수행한다.

- [ ] 이벤트 중복 방지·심각도 상향·티켓 상태 전이 단위 테스트
- [ ] `operatingMode=SHADOW` 결과가 이벤트·티켓을 생성하지 않는 단위 테스트
- [ ] PostgreSQL migration 환경과 FastAPI WireMock을 사용한 상태 샘플 저장·이벤트 생성 인계 스모크 테스트

## 12. 일정

| 날짜 | 작업 |
|---|---|
| 6/9 | 계약·Enum·상태 전이 확정 |
| 6/10 | Entity, Repository, DB mapping 검증 |
| 6/11 | 상태 수집·교통 맥락 집계 |
| 6/12 | FastAPI client·Rule orchestration |
| 6/13~6/14 | 기준선·추세·SHADOW 모델 orchestration·이벤트 |
| 6/15~6/16 | 티켓·SLA·Frontend API |
| 6/17 | 최소 단위 테스트·인계 스모크 테스트 |
| 6/18 | 권한·API 계약 최종 확인 |
| 6/19 | 버퍼·최종 시연 |

## 13. 배포·실행

- Spring Boot는 기존 TAS 서비스 이미지에 포함한다.
- PostgreSQL migration 완료 후 애플리케이션을 시작한다.
- Spring Boot datasource는 PostgreSQL 전용 `traffic_app` 계정을 사용하고 superuser 접속을 금지한다.
- FastAPI base URL과 내부 API key는 환경변수로 주입한다.
- scheduler 다중 실행을 막기 위해 MVP는 Spring Boot 인스턴스 1개를 기준으로 한다. 다중 인스턴스 배포 시 분산 lock을 추가한다.
- Docker health check는 DB 연결, migration 상태, FastAPI health를 분리해 확인한다.

## 14. 완료 조건

- [ ] DB 파트의 `007`·`008` migration 적용 환경에서 JPA validation이 통과한다.
- [ ] 수집·집계가 멱등하게 동작한다.
- [ ] 교통 맥락만으로 정비 이벤트가 생성되지 않는다.
- [ ] Rule·통계·추세 후보가 같은 이벤트 계약으로 저장된다.
- [ ] LSTM AutoEncoder 결과는 별도 로그에 저장되고 이벤트·티켓을 만들지 않는다.
- [ ] 중복 이벤트·티켓이 생성되지 않는다.
- [ ] 이벤트와 티켓 상태 전이·권한이 강제된다.
- [ ] MTTA·MTTR과 SLA를 조회할 수 있다.
- [ ] API 계약과 최소 자동 테스트 3개가 통과한다.
