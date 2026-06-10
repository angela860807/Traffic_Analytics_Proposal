# TAS-PM FastAPI 작업 TODO

## 1. 목표와 담당 파트

FastAPI는 영상 처리 과정에서 CCTV 상태 지표를 수집하고, AI 모델 파트가 제공한 `predictive_ml` 패키지를 내부 API로 서비스한다. 탐지 수식·모델 학습·임계값 실험은 AI 모델 파트, 이벤트·티켓 저장은 Spring Boot 파트가 담당한다.

| 역할 | 담당 파트 |
|---|---|
| 구현 소유 | FastAPI 파트 |
| AI 패키지 계약 협업 | AI 모델 파트 |
| Spring 내부 API 협업 | Spring Boot 파트 |

단독 소유 범위:

```text
fastapi-server/app/**
fastapi-server/tests/**
fastapi-server/Dockerfile
fastapi-server/requirements.txt
```

FastAPI 파트는 `predictive_ml/**`의 detector 구현과 평가 코드를 수정하지 않는다.

## 2. 권장 구조

```text
fastapi-server/app/
  api/routes/
    predictive_detection.py
  services/
    camera_health_collector.py
    predictive_detector_adapter.py
    backend_health_client.py
    delivery_queue.py
  schemas/
    camera_health.py
    predictive_detection.py
  core/
    config.py
    security.py
    logging.py
```

`predictive_detector_adapter.py`는 Pydantic DTO를 `predictive_ml` 입력 객체로 변환하고 결과를 API 응답으로 변환하는 역할만 한다.

## 3. CCTV 상태 지표 수집

1분 단위 `CameraHealthSample`:

- [ ] `fpsAvg`
- [ ] `frameDropRate`
- [ ] `latencyP95Ms`
- [ ] `blurScoreAvg`
- [ ] `brightnessScoreAvg`
- [ ] `detectionCount`
- [ ] `ocrAttemptCount`
- [ ] `ocrFailureCount`
- [ ] `ocrFailRate`
- [ ] `cpuUsagePct`
- [ ] `memoryUsagePct`
- [ ] `diskUsagePct`
- [ ] `networkRttMs` 또는 측정 불가 시 `null`
- [ ] `lastFrameAt`
- [ ] `qualityStatus`
- [ ] `dataSource`

정책:

- 측정 불가 값은 `null`로 보낸다.
- 프레임 없음과 FPS 0을 구분한다.
- OCR 시도 0건이면 실패율은 `null`이다.
- 1분 window 시작 시각을 `sampledAt`으로 사용한다.
- raw frame과 번호판 원문을 상태 로그에 남기지 않는다.
- MVP는 카메라 1대당 edge processor 1대를 가정한다.

## 4. Spring Boot 상태 샘플 전송

- [ ] `POST /internal/v1/camera-health-samples` client 구현
- [ ] `X-Internal-Api-Key`, `X-Request-Id` 전달
- [ ] timeout 3초
- [ ] 지수 backoff retry 최대 3회
- [ ] 제한된 로컬 재전송 큐
- [ ] 재전송 시 원래 `sampledAt`과 `idempotencyKey` 유지
- [ ] 큐 포화 시 drop metric 기록
- [ ] 영상 추론 thread와 전송 thread 분리

## 5. 내부 탐지 API

### 5-1. Rule 평가

```http
POST /internal/v1/anomaly-detection/camera-health/evaluate
```

- [ ] Pydantic 요청·응답 schema
- [ ] `predictive_ml.detect_rules()` 호출
- [ ] AI 결과의 Enum과 API 계약 검증
- [ ] detector version을 응답에 포함

### 5-2. 기준선·추세·교통 맥락 평가

```http
POST /internal/v1/anomaly-detection/camera-degradation/evaluate
```

- [ ] 최근 샘플·기준선·교통 맥락 schema
- [ ] `predictive_ml.detect_degradation()` 호출
- [ ] `READY`, `LEARNING` 기준선 상태 전달
- [ ] trend와 evidence 응답 변환

### 5-3. 상태

```http
GET /internal/v1/anomaly-detection/health
```

- [ ] 서비스 상태
- [ ] 설치된 AI 패키지 버전
- [ ] 활성 detector 이름·버전·방식
- [ ] AI 패키지 import 실패 상태

## 6. AI 패키지 통합 계약

FastAPI가 호출할 공개 인터페이스:

```python
detect_rules(request: RuleDetectionInput) -> DetectionResult
detect_degradation(request: DegradationDetectionInput) -> DetectionResult
predict_anomaly(request: ModelPredictionInput) -> ShadowPredictionResult
get_detector_manifest() -> DetectorManifest
```

- [ ] 로컬 editable install 또는 wheel 설치 방식 확정
- [ ] Python 버전과 의존성 충돌 확인
- [ ] 입력 객체를 dict 임의 조작 없이 명시적으로 변환
- [ ] AI 패키지 예외를 `INTERNAL_DETECTOR_UNAVAILABLE`로 매핑
- [ ] 후보가 없을 때 정상 빈 배열 응답
- [ ] package version과 detector version 구분
- [ ] LSTM AutoEncoder `.pt`, scaler, threshold metadata를 시작 시 1회 로드
- [ ] artifact SHA-256과 feature schema version 검증
- [ ] feature 순서·누락 feature 불일치 시 추론 거부
- [ ] 모델 결과를 `shadowCandidates`로만 반환
- [ ] 기준선 상태가 `LEARNING`이면 모델 추론을 건너뜀

FastAPI에는 Rule, z-score, EWMA, 추세 기울기 계산식을 중복 구현하지 않는다.

## 7. 예외·보안·관측성

- [ ] 내부 API key 검증
- [ ] Pydantic validation error 표준화
- [ ] requestId, cameraId, detectorVersion 구조화 로그
- [ ] 요청 body 크기 제한
- [ ] endpoint별 처리 시간 metric
- [ ] AI adapter 호출 시간 metric
- [ ] Spring 전송 성공·재시도·drop metric
- [ ] 부분 후보 반환 없이 명시적 실패 응답

## 8. 테스트

파트 테스트는 다음 3개만 수행하고 전체 E2E와 성능 검증은 최종 병합 담당이 수행한다.

- [ ] 상태 지표 1분 집계·결측값·idempotency key 단위 테스트
- [ ] AI artifact 로딩·feature schema 검증·SHADOW 응답 변환 단위 테스트
- [ ] AI fixture와 Spring Boot mock을 사용한 두 탐지 endpoint 인계 스모크 테스트

탐지 정확도와 lead time 평가는 AI 모델 파트의 책임이다.

## 9. 배포·실행

- [ ] Docker 이미지에 `predictive_ml` wheel 포함
- [ ] 검증 완료된 LSTM AutoEncoder `.pt`와 scaler·threshold 포함
- [ ] Spring URL과 내부 API key 환경변수화
- [ ] metric window와 retry queue 크기 환경변수화
- [ ] `/internal/v1/anomaly-detection/health` health check
- [ ] CPU·메모리 제한 적용
- [ ] AI 패키지 버전 시작 로그 출력

## 10. 일정

| 날짜 | 작업 |
|---|---|
| 6/10 | 상태 지표 계약·AI package interface 확정 |
| 6/11 | 1분 상태 collector |
| 6/12 | Spring 전송 client·재전송 큐 |
| 6/13 | 내부 탐지 endpoint·Pydantic schema |
| 6/14 | AI package adapter |
| 6/15 | 보안·예외·로그·metric |
| 6/16 | 최소 단위 테스트 |
| 6/17 | Spring·AI 인계 스모크 테스트 |
| 6/18 | Docker·계약 최종 확인 |
| 6/19 | 버퍼·최종 시연 |

## 11. 완료 조건

- [ ] 1분 상태 샘플이 Spring Boot에 멱등하게 전달된다.
- [ ] 두 탐지 API와 health API가 계약대로 동작한다.
- [ ] FastAPI 내부에 detector 계산식이 중복되지 않는다.
- [ ] AI 패키지 버전과 detector version이 노출된다.
- [ ] LSTM AutoEncoder가 SHADOW 모드로 로드되고 운영 candidate와 분리된다.
- [ ] 최소 자동 테스트 3개와 Spring·AI 인계 계약이 통과한다.
- [ ] 상태 수집 실패가 기존 영상 분석을 중단시키지 않는다.
