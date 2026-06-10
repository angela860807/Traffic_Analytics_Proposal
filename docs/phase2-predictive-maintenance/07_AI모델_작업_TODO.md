# TAS-PM AI 모델 작업 TODO

## 1. 목표와 담당 파트

AI 모델 파트는 CCTV 상태 시계열에서 이상과 악화 징후를 판단하는 재사용 가능한 Python 패키지, 학습 artifact, 장애 주입 데이터셋, 임계값과 평가 결과를 제공한다. FastAPI router·Pydantic·통신 코드는 수정하지 않는다.

| 역할 | 담당 파트 |
|---|---|
| 구현 소유 | AI 모델 파트 |
| 패키지 연동 협업 | FastAPI 파트 |
| PostgreSQL 읽기 전용 데이터 추출 협업 | DB 파트 |

단독 소유 범위:

```text
predictive_ml/**
```

## 2. 권장 구조

```text
predictive_ml/
  pyproject.toml
  src/predictive_ml/
    contracts.py
    rule_detector.py
    robust_zscore_detector.py
    trend_projection_detector.py
    traffic_context_validator.py
    cause_inference.py
    feature_pipeline.py
    lstm_autoencoder.py
    artifact_loader.py
    manifest.py
  configs/
    detector-policy.yaml
  datasets/
    manifests/
  fault_injection/
  evaluation/
  artifacts/
  tests/
  reports/
```

패키지는 FastAPI나 DB에 의존하지 않는 순수 Python 모듈로 만든다.

## 3. 입력·출력 계약

공개 인터페이스:

```python
detect_rules(request: RuleDetectionInput) -> DetectionResult
detect_degradation(request: DegradationDetectionInput) -> DetectionResult
predict_anomaly(request: ModelPredictionInput) -> ShadowPredictionResult
get_detector_manifest() -> DetectorManifest
```

- [ ] `cameraId + sampledAt` grain 고정
- [ ] 요청에는 최근 60분 상태 이력을 받고 Trend는 마지막 15분, LSTM AE는 전체 60분 사용
- [ ] 향후 10분 prediction horizon
- [ ] 결측·보간·품질 상태 필드 정의
- [ ] API 계약과 동일한 Enum 사용
- [ ] 입력 객체를 수정하지 않는 순수 함수로 구현
- [ ] 결과에 detector 이름·버전·정책 코드·evidence 포함
- [ ] 학습 모델 결과에 `operatingMode=SHADOW`, score, threshold, feature schema 포함

AI 패키지는 이벤트 ID, 티켓, 사용자 권한, DB Entity를 알지 못한다.

## 4. 데이터셋 구성

### 4-1. 실제 로그

- [ ] 기존 FastAPI 처리 로그에서 상태 지표 추출
- [ ] PostgreSQL export의 `TIMESTAMPTZ`를 timezone-aware datetime으로 로딩
- [ ] PostgreSQL `NUMERIC`을 분석용 `float64`로 변환할 때 원본 precision 기록
- [ ] 카메라·시간 단위 정렬과 중복 제거
- [ ] 시간대와 `sampledAt` 검증
- [ ] 원본 영상·번호판 비식별 또는 저장 제외
- [ ] `REAL` 데이터와 실험 데이터를 분리
- [ ] 데모용 `SIMULATED` 정상 기준선 30개 이상 생성
- [ ] 동일 `scenarioId`로 정상 기준선과 `FAULT_INJECTED` 구간 연결

### 4-2. 라벨 정책

```text
NORMAL
DEGRADING
FAILURE
RECOVERY
```

- [ ] 장애 주입 시작·종료 시각 기록
- [ ] `DEGRADING` 시작 기준 정의
- [ ] 장애 주입 유형과 `AnomalyType` 매핑
- [ ] 운영자 확정 원인과 오탐 결과를 후속 라벨로 사용
- [ ] 미래 정보가 feature에 섞이지 않도록 leakage 검사

### 4-3. 데이터 manifest

```text
datasetVersion
scenarioId
cameraIds
from / to
dataSource
scenario
randomSeed
sampleCount
labelDistribution
preprocessingVersion
```

목표 시뮬레이션 데이터:

| 파일 | 행 수 | 용도 |
|---|---:|---|
| `normal_samples.csv` | 60,480 | 카메라 3대 × 정상 14일 학습·검증·정상 테스트 |
| `fault_samples.csv` | 4,320 | 9가지 장애 시나리오 테스트 |

행 수가 달라지면 manifest에 실제 행 수와 생성 공식을 기록한다.

## 5. 장애 주입

| 시나리오 | 주입 방식 | 기대 이상 유형 |
|---|---|---|
| 카메라 오프라인 | 프레임 입력 중단 | `CAMERA_OFFLINE` |
| FPS 저하 | 프레임 처리 sleep 증가 | `FPS_DEGRADATION` |
| frame drop | 일정 비율 프레임 폐기 | `FRAME_DROP_DEGRADATION` |
| latency 증가 | 추론·OCR 지연 삽입 | `LATENCY_DEGRADATION` |
| blur 증가 | Gaussian blur 적용 | `BLUR_DEGRADATION` |
| OCR 품질 저하 | 저해상도·가림·노이즈 | `OCR_QUALITY_DEGRADATION` |
| 자원 포화 | CPU·메모리 metric fixture | `RESOURCE_SATURATION` |
| 네트워크 불안정 | RTT·전송 실패 fixture | `NETWORK_INSTABILITY` |
| 실제 교통 감소 | 인접 카메라 동시 감소, 장비 정상 | 이벤트 미생성 |

- [ ] 시나리오별 강도 2단계 이상
- [ ] 동일 random seed 재현
- [ ] `FAULT_INJECTED` 출처 사용
- [ ] 정상 데이터와 별도 저장
- [ ] 예상 탐지 결과 fixture 제공
- [ ] `normal_samples.csv`, `fault_samples.csv` 생성 스크립트 제공

## 6. Rule Detector

- [ ] 8개 이상 유형의 WARNING·CRITICAL 조건 구현
- [ ] 연속 window 조건
- [ ] OCR 최소 20건 조건
- [ ] 결측·품질 불충분 샘플 제외
- [ ] observed·threshold evidence 생성
- [ ] 원인 후보 생성

버전:

```text
camera-rule / 1.1.0 / RULE
```

## 7. Robust Z-Score Detector

```text
robust_z = (current - median) / (1.4826 * MAD)
```

- [ ] metric별 악화 방향 정의
- [ ] 기준선 표본 30개 미만 `LEARNING`
- [ ] MAD 0 fallback
- [ ] `|z| >= 3.5` WARNING
- [ ] `|z| >= 5.0` CRITICAL
- [ ] 기준선 기간·표본 수·점수 evidence

버전:

```text
camera-robust-zscore / 1.0.0 / ROBUST_Z_SCORE
```

## 8. Trend Projection Detector

```text
입력: 최근 15분
최소 유효 표본: 12
평활화: EWMA alpha=0.3
추세: EWMA 값에 대한 Theil-Sen 기울기
예측 구간: 향후 10분
최소 신뢰도: 0.60
```

- [ ] metric별 악화 방향
- [ ] EWMA 계산
- [ ] Theil-Sen 기울기 계산
- [ ] 시간과 EWMA 값의 Spearman 상관계수 절댓값을 신뢰도로 계산
- [ ] WARNING·CRITICAL 교차 예상 시각
- [ ] 예측 구간 밖 후보 제외
- [ ] 회복 추세 후보 제외
- [ ] trend 필드와 evidence 반환

버전:

```text
camera-trend-projection / 1.0.0 / TREND_PROJECTION
```

## 9. 교통 맥락 교차검증

- [ ] 인접 카메라 예상 이동 시간 반영
- [ ] 인접 카메라 동시 감소 시 `EXTERNAL_TRAFFIC_CHANGE`
- [ ] 특정 카메라만 감소하고 상태 지표가 악화하면 장비 원인 점수 상향
- [ ] OCR 단독 악화 시 `OCR_PIPELINE_DEGRADATION`
- [ ] FPS·지연·CPU 동시 악화 시 `AI_PROCESSING_OVERLOAD`
- [ ] 맥락 품질 불충분 시 점수 변경 금지
- [ ] 교통 맥락만으로 후보 생성 금지

버전:

```text
camera-context-cross-validator / 1.0.0 / CROSS_VALIDATION
```

## 10. 임계값 실험

- [ ] Rule 초기값으로 장애 주입 데이터 평가
- [ ] z-score 3.0·3.5·4.0 비교
- [ ] 추세 window 10·15·20분 비교
- [ ] prediction horizon 5·10·15분 비교
- [ ] 신뢰도 0.5·0.6·0.7 비교
- [ ] 최종 선택 근거 기록
- [ ] 운영 정책용 YAML 제공

정책 변경은 실험 보고서와 버전을 함께 남긴다. 운영 DB에 직접 정책을 수정하지 않는다.

## 11. LSTM AutoEncoder 학습

### 11-1. 적용 이유

Rule, robust z-score, EWMA 추세는 학습 모델이 아니다. 실제 모델 학습 산출물은 정상 시계열의 다변량 패턴을 재구성하도록 학습하는 LSTM AutoEncoder로 구현한다.

### 11-2. 학습 데이터 Grain

```text
row grain = camera_id + sequence_end_at
input sequence = 직전 60분
timesteps = 60
features = 8
stride = 5분
prediction target = 현재 sequence의 이상 여부
training rows = NORMAL sequence only
evaluation labels = NORMAL / DEGRADING / FAILURE
```

- [ ] 카메라별 1분 샘플을 60분 sliding sequence로 변환
- [ ] 입력 shape을 `(batch, 60, 8)`로 고정
- [ ] split 경계를 넘는 sequence 제거
- [ ] train·validation·test 경계에 60분 purge gap 적용
- [ ] 장애 주입·복구 sequence는 train 제외
- [ ] 같은 `scenarioId`를 여러 split에 분산하지 않음

### 11-3. Feature

대상 metric:

```text
fpsAvg
frameDropRate
latencyP95Ms
blurScoreAvg
ocrFailRate
cpuUsagePct
memoryUsagePct
networkRttMs
```

- [ ] 카메라 ID를 feature로 직접 사용하지 않음
- [ ] feature별 scaler는 train 정상 timestep에만 fit
- [ ] scaler 적용 후 60×8 sequence 유지
- [ ] feature 이름·순서·dtype을 schema로 고정
- [ ] traffic context는 1차 모델 feature에서 제외하고 추론 후 교차검증에 사용

### 11-4. 분할과 최소 데이터

```text
train: 정상 14일 데이터의 최초 70%
validation: 정상 14일 데이터의 다음 15%
normal test: 정상 14일 데이터의 마지막 15%
fault test: 9가지 장애 시나리오
minimum normal training sequences: 1,000
random_state: 고정값
```

- 정상 sequence만 train과 validation에 사용한다.
- 정상 test와 장애 test를 합쳐 최종 성능을 평가한다.
- 최소 학습량을 충족하지 못하면 artifact 상태를 `EXPERIMENTAL`로 기록하고 FastAPI에 적재하지 않는다.

### 11-5. 학습·threshold

초기 설정:

```text
model = LSTM AutoEncoder
framework = PyTorch
input_size = 8
sequence_length = 60
hidden_size = 32
latent_size = 16
loss = MSE
optimizer = Adam
early_stopping = validation loss
random_seed = 42
```

- [ ] train 정상 sequence로 reconstruction loss 최소화
- [ ] validation loss 기준 early stopping
- [ ] sequence별 reconstruction error 계산
- [ ] train 정상 error 분포로 score를 0~1 calibration
- [ ] 정상 validation error의 99백분위수를 WARNING 초기값으로 설정
- [ ] 정상 validation error의 99.9백분위수를 CRITICAL 초기값으로 설정
- [ ] 카메라 1대·1일당 오탐 1건 이하 조건 우선
- [ ] 오탐 제약을 초과하면 threshold 상향
- [ ] test에서는 threshold 재조정 금지
- [ ] Rule·z-score·추세와 결과 비교

### 11-6. Artifact

학습 artifact:

```text
model/lstm_ae.pt
model/scaler.pkl
model/threshold.json
model/metrics.json
model/feature_schema.json
model/training_manifest.json
```

- [ ] `.pt`에는 state dict와 architecture config 저장
- [ ] scaler와 모델을 분리 저장
- [ ] threshold JSON에 WARNING·CRITICAL 재구성 오차 저장
- [ ] metrics JSON에 F1, ROC-AUC, 오탐 수, lead time 저장
- [ ] 각 artifact SHA-256 생성
- [ ] 학습 manifest와 평가 지표 저장
- [ ] 깨끗한 환경에서 load·predict 재현
- [ ] feature schema mismatch 시 명시적 예외
- [ ] artifact 경로를 Git에 하드코딩하지 않고 환경변수로 주입

버전:

```text
camera-lstm-autoencoder / 1.0.0 / LSTM_AUTOENCODER / SHADOW
```

### 11-7. SHADOW 운영

- [ ] FastAPI에 artifact 인계
- [ ] 운영 detector와 동일 window로 추론
- [ ] `shadowCandidates`로만 반환
- [ ] 카메라 기준선이 `LEARNING`이면 추론하지 않음
- [ ] 설명 feature는 feature별 평균 재구성 오차 상위 3개로 계산
- [ ] 자동 이벤트·티켓 생성 금지
- [ ] 모델 score와 Rule·통계 판단의 일치·불일치 사례 저장

## 12. 평가

분할:

- 시간 순서 train·validation·test
- 같은 장애 시나리오 구간을 하나의 split에 유지
- 동일 카메라 반복 데이터 편향 확인
- 기준선에 미래·장애·복구 후 데이터 포함 금지

지표:

- [ ] Precision, Recall, F1
- [ ] PR-AUC, ROC-AUC
- [ ] confusion matrix
- [ ] false alarm rate
- [ ] 카메라 1대·1일당 오탐 수
- [ ] 장애 시작 전·후 lead time
- [ ] detector 처리 지연
- [ ] 유형별·카메라별 결과

Rule처럼 확률을 출력하지 않는 detector에는 PR-AUC·ROC-AUC를 억지로 적용하지 않고 threshold sweep 결과가 있을 때만 계산한다.

LSTM AutoEncoder는 reconstruction error threshold sweep으로 PR-AUC·ROC-AUC를 계산하고, 운영 관점에서는 false alarm rate와 lead time을 우선한다.

## 13. 실험·버전 관리

- [ ] package version
- [ ] detector별 version
- [ ] config hash
- [ ] Git commit
- [ ] dataset manifest
- [ ] preprocessing version
- [ ] 평가 결과 JSON·CSV
- [ ] 재현 명령어

LSTM AutoEncoder는 MVP의 학습 모델이며 SHADOW API에 연결한다. Isolation Forest는 일정이 허용될 경우 동일 데이터의 비교 baseline으로만 수행한다.

## 14. FastAPI 인계

인계 산출물:

```text
wheel 또는 설치 가능한 local package
공개 함수 문서
입력·출력 fixture
detector manifest
기본 policy YAML
예외 목록
package test 결과
LSTM AutoEncoder `.pt`
scaler.pkl
threshold.json
metrics.json
artifact SHA-256
feature schema
```

- [ ] FastAPI 환경에서 wheel 설치 확인
- [ ] package import·version 조회 확인
- [ ] detector 계산식이 FastAPI에 복제되지 않았는지 확인
- [ ] artifact와 feature schema 검증

## 15. 테스트

파트 테스트는 다음 3개만 수행한다. 모델 성능 지표 산출은 학습·평가 업무이며 자동 테스트 개수에 포함하지 않는다.

- [ ] 시간 분리·purge gap·scaler fit 범위를 확인하는 데이터 누수 단위 테스트
- [ ] 동일 입력에서 저장 전후 LSTM AutoEncoder 점수와 threshold 판정이 일치하는 단위 테스트
- [ ] fixture로 `predict_anomaly`의 SHADOW 입력·출력 계약을 확인하는 FastAPI 인계 스모크 테스트

## 16. 일정

| 날짜 | 작업 |
|---|---|
| 6/10 | package 구조·입출력 계약·라벨 정의 |
| 6/11 | 데이터 추출·manifest·장애 주입 골격 |
| 6/12 | Rule detector |
| 6/13 | robust z-score |
| 6/14 | trend projection |
| 6/15~6/16 | LSTM AutoEncoder sequence·학습·threshold |
| 6/17 | 교통 맥락·평가·FastAPI artifact 인계 |
| 6/18 | 최소 테스트·발표 지표 |
| 6/19 | 버퍼·최종 시연 |

## 17. 완료 조건

- [ ] `predictive_ml` 패키지가 FastAPI 없이 단독 테스트된다.
- [ ] 장애 주입 8종과 정상 교통 감소 1종이 재현된다.
- [ ] Rule·z-score·추세·교차검증 결과가 동일 계약으로 반환된다.
- [ ] 최종 임계값 선택 근거가 있다.
- [ ] LSTM AutoEncoder `.pt`, scaler, threshold와 feature schema가 재현된다.
- [ ] 학습·validation·test 시간 분리와 leakage 검사가 통과한다.
- [ ] SHADOW 추론이 운영 이벤트·티켓을 생성하지 않는다.
- [ ] 오탐 수와 lead time을 포함한 평가 보고서가 있다.
- [ ] wheel·artifact·fixture·manifest가 FastAPI 파트에 전달된다.
