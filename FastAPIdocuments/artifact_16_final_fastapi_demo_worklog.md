# Artifact 16 - Final FastAPI Demo Worklog

작성일: 2026-05-27

## 1. 목적

시연 직전 FastAPI 영상 분석 파이프라인의 마지막 보강 내용을 정리한다.

이번 작업은 새로운 모델 교체나 대규모 구조 변경이 아니라, 현재 시연이 끊기지 않는 상태를 유지하면서 실무자가 봤을 때 아쉬운 안정성, 속도값 튐, GUI 로그 표현을 보완하는 데 초점을 뒀다.

## 2. 오늘 최종 작업 요약

### 2.1 OpenCV preview 표시 안정화

`fastapi-server/scripts/stream_video_file.py`의 GUI 표시를 시연용으로 정리했다.

처리 내용:

- 상단 로그의 `IDLE`, `TRACKING`, `FINALIZED`를 한글 상태로 표시한다.
  - `IDLE` -> `대기`
  - `TRACKING` -> `추적 중`
  - `FINALIZED` -> `완료`
- 상단 로그에서 `Track ID`와 `차량 N대` 문구를 제거했다.
- `IDLE`, `FINALIZED` 상태에서는 bbox를 그리지 않도록 하여 차량이 지나간 뒤 허공에 bbox가 남는 현상을 줄였다.
- preview 시작 타이밍을 늦추기 위해 `--preview-delay-seconds` 기본값을 10초로 조정했다.
- 오래된 응답 bbox를 더 빨리 숨기도록 `--preview-max-response-lag-seconds` 기본값을 0.35초로 조정했다.

결과:

- 시연 화면이 과하게 복잡하지 않고, 상태/신뢰도 중심으로 보인다.
- bbox 잔상이 줄어들었다.
- 영상 재생과 상단 로그 타이밍이 이전보다 자연스러워졌다.

### 2.2 속도 계산값 median smoothing 적용

`fastapi-server/app/services/speed_tracker.py`에 속도값 median smoothing을 추가했다.

현재 속도 계산 요약:

- 차량 bbox의 하단 중앙점을 차량 위치로 본다.
- 최근 프레임 간 위치 이동거리를 도로 거리로 환산하고, `거리 / 시간 * 3.6`으로 km/h를 계산한다.
- 같은 차량 track의 최근 속도 측정값 최대 5개를 보관하고, 그 중앙값을 최종 `measuredSpeed`로 사용한다.

도입 이유:

- bbox 하단점이 프레임마다 흔들리면 순간 속도값이 튈 수 있다.
- 평균보다 median이 이상치에 강해서, 갑자기 튀는 속도값을 줄이기에 적합하다.
- 모델을 추가하지 않아 프로그램이 무거워지지 않는다.

주의:

- 5개가 모두 쌓여야 계산되는 구조는 아니다.
- 속도값이 1개면 1개 기준, 2개면 두 값의 중앙값, 3개 이상이면 누적된 값들의 median을 사용한다.
- 여기서 5개는 bbox frame 5개가 아니라 speed measurement 5개다.

발표 설명:

> 차량 bbox의 하단 중앙점을 차량 위치로 보고, 최근 프레임 간 이동거리를 실제 도로 거리로 환산한 뒤 `거리 / 시간 * 3.6`으로 km/h 속도를 추정합니다. 순간적인 bbox 흔들림으로 속도값이 튀지 않도록, 같은 차량 track의 최근 속도 측정값 최대 5개를 median smoothing해서 최종 표시/저장 속도로 사용합니다.

### 2.3 속도 ROI 거리값 정리

기존에는 전체 프레임을 35m x 35m로 보는 값이었지만, 시연 영상의 차선 점선 기준으로는 과대 추정 가능성이 있었다.

현재 시연용 거리값:

- `--roi-height-meters 22.0`
- `--roi-width-meters 10.5`
- `--distance-meters 22.0`

정리 이유:

- 화면 속 차선 점선 하나가 약 3m라고 볼 때, 전체 프레임 35m x 35m는 다소 과하다.
- 현재 영상에서는 세로 진행 방향을 약 18~24m, 가로 도로 폭을 약 9~12m로 보는 편이 더 현실적이다.
- 따라서 시연에서는 22m x 10.5m 근사값으로 정리했다.

발표 시 주의:

- 이 값은 실제 도로 측량값이 아니라 시연 영상 기준 근사값이다.
- 실제 현장 적용에서는 고정 카메라 캘리브레이션, 차선 기준점, 또는 Line A/B 기준선 방식이 필요하다.

### 2.4 Homography는 이번 시연에서 제외

homography는 코드에 이미 지원되어 있지만, 이번 시연에서는 도입하지 않기로 했다.

제외 이유:

- 현재 영상에서는 bbox 하단 중앙점이 차량 바퀴 접지점과 정확히 일치하지 않는다.
- ROI 4점 클릭 오차가 있으면 좌표 변환이 오히려 속도값을 더 흔들 수 있다.
- 낮은 FPS와 bbox 흔들림 조건에서는 homography가 항상 더 좋은 결과를 보장하지 않는다.

발표 표현:

> homography 기반 보정은 구조적으로 지원하지만, 현재 시연 영상에서는 bbox 위치 흔들림과 낮은 샘플링 FPS 때문에 오히려 편차가 커질 수 있어 lightweight 추정 방식과 median smoothing을 우선 적용했습니다. 실제 현장 적용 단계에서는 고정 카메라 캘리브레이션을 통해 homography 또는 Line A/B 기준선 방식을 적용할 수 있습니다.

### 2.5 OCR 상태 TTL cleanup 추가

`fastapi-server/app/api/routes/detection.py`의 `stream_ocr_statuses`는 메모리 dict로 OCR 상태를 보관한다.

문제:

- 서버가 오래 켜져 있으면 OCR 상태가 계속 누적될 수 있다.
- 서버 재시작 시 사라지는 메모리 상태이므로 운영 저장소는 아니다.

처리:

- `STREAM_OCR_STATUS_TTL_SECONDS = 600.0` 추가
- OCR 상태 저장 또는 조회 시 10분이 지난 상태를 정리한다.
- `stream_ocr_status_seen_at`으로 마지막 저장 시각을 monotonic time 기준으로 관리한다.

효과:

- 시연 중 누적되는 OCR 상태 메모리 사용량을 제한한다.
- Redis/DB를 추가하지 않고도 최소한의 실무 안정성을 확보했다.

### 2.6 Spring detection 전송 retry 추가

`fastapi-server/app/services/backend_client.py`의 Spring 전송 로직을 정리했다.

기존:

- speed violation 전송에는 retry가 있었다.
- detection log 전송은 일시적인 Spring 장애나 네트워크 실패 시 바로 실패했다.

처리:

- `_post_with_retry()` 공통 메서드를 추가했다.
- detection 전송과 speed violation 전송이 같은 retry 경로를 사용한다.
- transient failure, 429, 5xx 응답에 대해 설정된 횟수만큼 재시도한다.

효과:

- Spring Boot가 순간적으로 늦거나 재시작 중일 때 detection 저장 실패 가능성을 줄인다.
- 시연 중 DB 저장 누락 리스크가 줄어든다.

## 3. 최종 시연 명령어

작업 위치:

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal\fastapi-server
```

실행 명령:

```powershell
.\.venv\Scripts\python.exe scripts\stream_video_file.py `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --auto-full-frame-speed-zone `
  --video-speed-ratio 0.40 `
  --roi-height-meters 22.0 `
  --roi-width-meters 10.5 `
  --distance-meters 22.0 `
  --speed-limit-kmh 50.0 `
  --scale 0.45 `
  --realtime `
  --preview-bbox `
  --async-upload `
  --upload-queue-size 1 `
  --preview-delay-seconds 10.0 `
  --highres-ocr-crop `
  --highres-crop-padding 0.35 `
  --highres-jpeg-quality 90 `
  --fps 3 `
  --preview-fps 12 `
  --upload-scale 0.50 `
  --bbox-hold-seconds 0 `
  --preview-max-event-age-seconds 3.8 `
  --preview-max-bbox-area-ratio 0.32 `
  --preview-min-bbox-confidence 0.45 `
  --preview-max-response-lag-seconds 0.35 `
  --preview-primary-bbox-only
```

FastAPI 컨테이너 반영:

```powershell
docker compose up -d --build fastapi-server
```

## 4. 검증 결과

실행한 검증:

```powershell
.\.venv\Scripts\python.exe -m py_compile app\api\routes\detection.py app\services\backend_client.py app\services\speed_tracker.py scripts\stream_video_file.py
```

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_detection_api.py
```

결과:

- `py_compile` 통과
- `tests/test_detection_api.py` 전체 63개 통과

경고:

- Paddle 관련 ccache 경고와 PaddleOCR `ocr()` deprecation warning이 있다.
- 시연 영향은 없지만, 장기적으로는 PaddleOCR API 변경 대응이 필요하다.

## 5. 실무 관점의 현재 한계

현재 상태는 시연 가능한 end-to-end pipeline이다.

다만 실무 운영 기준으로는 아래 한계가 남아 있다.

1. 차량 YOLO는 아직 `/stream-frame` 요청 경로에서 직접 실행된다.
2. OCR/DB 저장은 background task로 분리했지만, Celery/RQ 같은 영속 큐는 아니다.
3. OCR 상태는 메모리 dict라 서버 재시작 시 사라진다.
4. 속도 계산은 bbox 하단 중앙점 기반 추정값이다.
5. homography는 지원하지만, 현재 시연 영상에서는 안정적이지 않아 제외했다.
6. 실제 단속 수준의 정확도는 카메라 캘리브레이션, 차선 기준점, 고정 설치 환경이 필요하다.

## 6. 발표용 핵심 문장

FastAPI 파트 설명:

> FastAPI 서버는 영상 프레임을 받아 차량 YOLO로 bbox를 감지하고, 이벤트 단위로 best frame을 선택한 뒤 번호판 YOLO와 PaddleOCR을 통해 번호판을 인식합니다. 실시간 preview 응답과 OCR/DB 저장을 분리해 시연 중 화면 지연을 줄였고, OCR 상태는 별도 조회 API로 확인할 수 있게 구성했습니다.

속도 계산 설명:

> 차량 bbox의 하단 중앙점을 차량 위치로 보고, 최근 프레임 간 이동거리를 실제 도로 거리로 환산한 뒤 `거리 / 시간 * 3.6`으로 km/h 속도를 추정합니다. 순간적인 bbox 흔들림으로 속도값이 튀지 않도록, 같은 차량 track의 최근 속도 측정값 최대 5개를 median smoothing해서 최종 표시/저장 속도로 사용합니다.

한계와 확장 설명:

> 현재는 시연 영상 기준의 lightweight 추정 방식이며, 실제 현장 적용 단계에서는 고정 카메라 캘리브레이션, 차로별 기준선 A/B, homography 보정, 영속 작업 큐를 추가해 정확도와 장애 복구성을 높일 수 있습니다.

## 7. 다음 컨텍스트 인수인계

현재 마무리 기준 변경 파일:

- `fastapi-server/scripts/stream_video_file.py`
- `fastapi-server/app/services/speed_tracker.py`
- `fastapi-server/app/api/routes/detection.py`
- `fastapi-server/app/services/backend_client.py`
- `fastapi-server/tests/test_detection_api.py`

다음 작업자가 바로 확인할 것:

1. FastAPI 재빌드가 필요하다.
2. 시연 전 `/api/detections/warmup` 호출 또는 짧은 warm-up run을 권장한다.
3. 속도 거리값은 `22.0m x 10.5m` 근사값으로 정리했다.
4. homography는 이번 시연에서 사용하지 않는다.
5. OCR 상태는 10분 TTL 메모리 캐시다.
6. Spring detection 저장은 retry가 적용됐다.
7. 전체 FastAPI 테스트는 통과했다.

