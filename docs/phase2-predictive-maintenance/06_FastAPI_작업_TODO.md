# TAS-PM FastAPI 작업 TODO

## 1. 목표와 담당

FastAPI는 CCTV 상태 지표를 생성하고, 설명 가능한 Rule·통계·추세 detector로 고장 징후 후보를 반환한다. 이벤트 중복, 업무 상태, 티켓 생성은 Spring Boot가 책임진다.

| 역할 | 담당 |
|---|---|
| detector·API 주 담당 | 박재웅 |
| 데이터셋·장애 주입·평가 | 박지영 |
| 데이터 계약·통합 QA | 전보경 |

## 2. 권장 구조

```text
app/
  routers/
    internal_detection.py
  services/
    health_metric_service.py
    rule_detector.py
    robust_zscore_detector.py
    trend_projection_detector.py
    traffic_context_validator.py
    cause_inference_service.py
  repositories/
    metric_buffer_repository.py
  schemas/
    camera_health.py
    detection.py
    common.py
  core/
    config.py
    security.py
    logging.py
  tests/
```

router, service, repository, Pydantic schema를 분리한다. SQL 저장이 필요하면 SQLAlchemy와 Alembic을 사용하며, MVP에서는 탐지 상태의 원장은 Spring Boot DB로 유지한다.

## 3. 상태 지표 생성

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
- [ ] `networkRttMs`
- [ ] `lastFrameAt`
- [ ] `qualityStatus`
- [ ] `dataSource`

정책:

- 측정 불가 값은 `null`로 보낸다.
- 프레임이 없을 때 FPS를 임의의 0으로 채우지 않고 `lastFrameAt`과 함께 판단한다.
- OCR 시도 0건이면 실패율은 `null`이다.
- 집계 window 시작 시각을 `sampledAt`으로 사용한다.
- 재전송에 동일 `idempotencyKey`를 사용한다.

## 4. Spring Boot 수집 연동

- [ ] `POST /internal/v1/camera-health-samples` client 구현
- [ ] timeout 3초
- [ ] 지수 backoff retry 최대 3회
- [ ] 로컬 제한 큐에 미전송 샘플 보관
- [ ] 재전송 시 원래 `sampledAt` 유지
- [ ] 큐 포화 시 drop 수 metric 기록
- [ ] `X-Internal-Api-Key`, `X-Request-Id` 전달

수집 실패가 영상 분석 전체를 중단시키지 않도록 비동기로 분리한다.

## 5. 내부 탐지 API

### 5-1. Rule 평가

```http
POST /internal/v1/anomaly-detection/camera-health/evaluate
```

Pydantic:

```text
CameraHealthEvaluationRequest
CameraHealthPoint
PolicyInput
DetectionResponse
AnomalyCandidate
EvidenceItem
```

### 5-2. 기준선·추세·교통 맥락 평가

```http
POST /internal/v1/anomaly-detection/camera-degradation/evaluate
```

Pydantic:

```text
CameraDegradationEvaluationRequest
BaselineInput
BaselineMetric
TrafficContextInput
TrendPolicyInput
DetectionResponse
```

### 5-3. 상태

```http
GET /internal/v1/anomaly-detection/health
```

응답에 활성 detector 이름·버전·방식을 포함한다.

## 6. Rule Detector

초기 detector:

```text
CAMERA_OFFLINE
FPS_DEGRADATION
FRAME_DROP_DEGRADATION
LATENCY_DEGRADATION
BLUR_DEGRADATION
OCR_QUALITY_DEGRADATION
RESOURCE_SATURATION
NETWORK_INSTABILITY
```

- [ ] 정책 임계값을 요청으로 받아 코드 하드코딩 최소화
- [ ] 연속 구간 수 검증
- [ ] 품질 불충분 샘플 제외
- [ ] OCR 최소 20건 조건
- [ ] 원인 후보와 evidence 반환
- [ ] 입력을 수정하지 않는 순수 함수 형태로 구현

버전:

```text
camera-rule / 1.1.0 / RULE
```

## 7. Robust Z-Score Detector

입력 기준선은 Spring Boot가 최근 14일의 동일 30분 시간대에서 계산해 전달한다.

```text
robust_z = (current - median) / (1.4826 * MAD)
```

- [ ] 악화 방향 정의
- [ ] 최소 기준선 표본 30개 검증
- [ ] MAD 0 fallback
- [ ] `|z| >= 3.5` WARNING 후보
- [ ] `|z| >= 5.0` CRITICAL 후보
- [ ] baseline source·기간·표본 수를 응답에 유지
- [ ] 미래 데이터가 기준선에 포함되지 않는 테스트

버전:

```text
camera-robust-zscore / 1.0.0 / ROBUST_Z_SCORE
```

## 8. Trend Projection Detector

MVP의 예지 기능이다.

```text
입력: 최근 15분 1분 샘플
최소 유효 표본: 12
평활화: EWMA alpha=0.3
추세: 강건 선형 기울기
예측 구간: 10분
최소 신뢰도: 0.60
```

- [ ] metric별 악화 방향 정의
- [ ] EWMA 계산
- [ ] 이상치 영향을 줄인 기울기 계산
- [ ] 기울기 신뢰도 계산
- [ ] 향후 WARNING·CRITICAL 임계치 교차 시각 계산
- [ ] 예측 구간 밖의 교차는 후보에서 제외
- [ ] `trendSlope`, `trendConfidence`, `predictionHorizonMinutes`, `projectedThresholdCrossingAt` 반환
- [ ] 단조 정상·악화·회복·노이즈 시계열 테스트

예측 후보 조건:

```text
valid_samples >= 12
AND trend_confidence >= 0.60
AND trend_direction = adverse
AND threshold_crossing_at <= evaluated_at + 10 minutes
```

버전:

```text
camera-trend-projection / 1.0.0 / TREND_PROJECTION
```

## 9. 교통 맥락 교차검증

교통 흐름 자체의 정비 이상을 만들지 않는다.

- [ ] 현재 카메라 탐지량과 인접 카메라 차량 수 비교
- [ ] 카메라 링크의 예상 이동 시간을 고려
- [ ] 여러 인접 카메라가 함께 감소하면 `EXTERNAL_TRAFFIC_CHANGE` 후보
- [ ] 특정 카메라만 감소하고 상태 지표가 악화하면 장비 원인 점수 상향
- [ ] OCR만 악화하면 `OCR_PIPELINE_DEGRADATION`
- [ ] FPS·지연·CPU 동시 악화면 `AI_PROCESSING_OVERLOAD`
- [ ] 교통 맥락 품질이 불충분하면 원인 점수를 변경하지 않음

응답은 CCTV `AnomalyCandidate`의 `suspectedCauses`와 evidence context만 보강한다.

버전:

```text
camera-context-cross-validator / 1.0.0 / CROSS_VALIDATION
```

## 10. 데이터·장애 주입

필수 시나리오:

| 시나리오 | 주입 |
|---|---|
| 카메라 오프라인 | 프레임 입력 중단 |
| FPS 저하 | 프레임 처리 sleep 증가 |
| frame drop | 일정 비율 프레임 폐기 |
| latency 증가 | 추론·OCR 지연 삽입 |
| blur 증가 | Gaussian blur 적용 |
| OCR 품질 저하 | 저해상도·가림·노이즈 적용 |
| 자원 포화 | CPU 부하 또는 metric fixture |
| 네트워크 불안정 | RTT 증가·간헐 전송 실패 fixture |
| 실제 교통량 감소 | 인접 카메라도 함께 감소, 장비 metric 정상 |

- [ ] 시나리오 시작·종료 시각 기록
- [ ] `FAULT_INJECTED` 출처 사용
- [ ] 실제 데이터와 별도 저장·평가
- [ ] 고장 유형·심각도·주입 강도를 manifest로 관리
- [ ] 동일 seed로 재현 가능하게 구현

공개 데이터:

- Caltrans PeMS는 교통 맥락 시계열 처리 검증에만 사용한다.
- NAB는 평가 방식 참고에 사용한다.
- MetroPT-3와 AI4I 모델을 CCTV 운영 모델로 직접 배포하지 않는다.

## 11. 평가 정책

데이터 계약:

```text
grain = camera_id + sampled_at
feature_window = 직전 15분
prediction_horizon = 향후 10분
label = 장애 주입 시작 또는 운영자 확정 장애
```

- [ ] 시간 순서 train·validation·test 분리
- [ ] 같은 장애 구간이 여러 split에 섞이지 않게 그룹화
- [ ] 미래·복구 후 정보 leakage 검사
- [ ] Precision, Recall, F1
- [ ] PR-AUC, ROC-AUC
- [ ] false alarm rate
- [ ] 카메라 1대·1일당 오탐 수
- [ ] confusion matrix
- [ ] 장애 시작 전후 lead time
- [ ] p95 inference latency
- [ ] detector version별 결과 저장

정확도 단독 평가는 금지한다. 운영 관점에서는 오탐 수와 사전 확보 시간인 lead time을 우선 제시한다.

## 12. 실험·버전 관리

- [ ] detector 설정을 YAML 또는 환경변수로 관리
- [ ] 설정 hash 생성
- [ ] 코드 commit, 데이터 manifest, 전처리 버전, metric 기록
- [ ] 결과 JSON schema 고정
- [ ] 동일 입력에 대한 재현 테스트
- [ ] Isolation Forest는 별도 실험 결과로만 비교

ONNX는 이후 학습 모델을 Spring 또는 edge 환경으로 옮겨야 할 때 검토한다. 현재 Rule·통계 detector에는 필요하지 않다.

## 13. 예외·보안·로그

- [ ] Pydantic validation error 표준화
- [ ] 내부 API key 검증
- [ ] requestId, cameraId, detectorVersion 구조화 로그
- [ ] raw frame·번호판 원문 로그 금지
- [ ] 탐지 요청 크기 제한
- [ ] detector별 처리 시간 metric
- [ ] 예외 시 부분 후보를 반환하지 않고 명시적 오류 응답

## 14. 테스트

- [ ] Rule 임계값·연속 구간 경계 테스트
- [ ] z-score 기준선 부족·MAD 0 테스트
- [ ] 추세 교차 시각·신뢰도 테스트
- [ ] 결측·보간·지연 샘플 테스트
- [ ] 교통 맥락 공동 감소·단일 감소 테스트
- [ ] Pydantic 요청·응답 계약 테스트
- [ ] Spring Boot API client mock 테스트
- [ ] 장애 주입 시나리오 회귀 테스트
- [ ] 100개 카메라 5분 평가 성능 테스트

## 15. 일정

| 날짜 | 작업 |
|---|---|
| 6/9 | schema·Enum·detector 계약 확정 |
| 6/10 | 1분 상태 metric·수집 client |
| 6/11 | Rule detector |
| 6/12 | robust z-score |
| 6/13~6/14 | trend projection |
| 6/15 | 교통 맥락 교차검증 |
| 6/16 | 장애 주입·평가 스크립트 |
| 6/17 | Spring Boot 통합 |
| 6/18 | 성능·회귀·발표 지표 |
| 6/19 | 버퍼·최종 시연 |

## 16. 배포·실행

- 기존 FastAPI 이미지에 detector 모듈을 포함하고 detector version을 이미지 tag와 별도로 응답한다.
- Spring Boot URL, 내부 API key, metric window, retry queue 크기는 환경변수로 주입한다.
- detector는 무상태로 실행하고 원본·이벤트 원장은 Spring Boot와 PostgreSQL에 둔다.
- 컨테이너 health check는 `/internal/v1/anomaly-detection/health`를 사용한다.
- CPU·메모리 제한을 명시하고 자원 포화 시험은 운영 profile과 분리한다.

## 17. 완료 조건

- [ ] 1분 상태 샘플이 멱등하게 Spring Boot에 수집된다.
- [ ] 두 내부 탐지 API와 health API가 계약대로 동작한다.
- [ ] Rule·z-score·추세 detector가 버전과 근거를 반환한다.
- [ ] 교통 맥락은 원인 검증에만 사용된다.
- [ ] 장애 주입 6종 이상이 재현된다.
- [ ] 오탐 수, lead time, 처리 지연을 포함한 평가 결과가 있다.
- [ ] Spring Boot 계약 테스트와 FastAPI 자동 테스트가 통과한다.
