# FastAPI - Raspberry Pi 연동 현황

작성일: 2026-05-14

## 현재 완료 상태

- Raspberry Pi는 카메라 프레임 캡처와 FastAPI 업로드만 담당한다.
- FastAPI는 PC에서 YOLO/OCR 추론, 이미지 저장, Spring Boot 전송을 담당한다.
- Spring Boot는 `POST /api/v1/detection-logs` 내부 API로 결과를 받아 DB에 저장한다.
- Raspberry Pi 실기 테스트는 health check, 샘플 업로드, 카메라 업로드, live preview까지 완료했다.

## 최종 데이터 흐름

```text
Raspberry Pi camera
  -> FastAPI /api/detections/image/send
  -> YOLO/OCR inference
  -> FastAPI storage/detections
  -> Spring Boot /api/v1/detection-logs
  -> PostgreSQL detection_logs / detection_analysis_results / vehicle_flow_events
  -> Vue dashboard
```

## 분석 상태

| 상태 | 의미 | 저장 결과 |
| --- | --- | --- |
| `FLOW_EVENT_CREATED` | 번호판 정상 인식 | detection log, analysis result, flow event 생성 |
| `OCR_FAILED` | 번호판 미인식 | detection log, analysis result만 생성 |
| `DUPLICATE_SKIPPED` | 중복 window 내 동일 번호판 | detection log, analysis result만 생성 |
| `ANALYSIS_ONLY` | FastAPI 분석 전용 | Spring DB 저장 없음 |

`UNKNOWN` 번호판 문자열은 사용하지 않는다. 번호판 미인식은 `plateNumber=null`과 `OCR_FAILED`로 표현한다.

## 이미지 저장 정책

- 원본 프레임: `*_frame.jpg`
- 번호판 crop: `*_plate_crop.jpg`
- OCR 전처리 이미지: `*_ocr.jpg`

Spring/Vue에는 아래 필드가 전달된다.

```text
imagePath / imageUrl
plateCropImagePath / plateCropImageUrl
ocrImagePath / ocrImageUrl
```

Docker Compose 기본값:

```env
IMAGE_STORAGE_DIR=storage/detections
MODEL_PATH=/app/models/best.pt
SAVE_PLATE_CROP=true
SAVE_OCR_PREPROCESSED_IMAGE=true
DETECTION_PREPROCESS_MODE=none
```

## 중복 처리

- 기준: `cameraCode + plateNumber + DUPLICATE_WINDOW_SECONDS`
- 기본 window: 10초
- 중복이어도 Spring으로 전송해 `DUPLICATE_SKIPPED` 분석 결과를 남긴다.
- 중복 결과는 `vehicle_flow_events`를 만들지 않는 것이 정상이다.

## Raspberry Pi 권장 설정

```env
FASTAPI_BASE_URL=http://<PC_LAN_IP>:8000
CAMERA_CODE=CAM_001
REQUEST_TIMEOUT_SECONDS=60
CAPTURE_INTERVAL_SECONDS=5
LIVE_FRAME_INTERVAL_SECONDS=0.2
JPEG_QUALITY=80
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
```

OCR 모델 초기 로딩 때문에 첫 요청은 10초 이상 걸릴 수 있다. 실기 테스트에서는 `REQUEST_TIMEOUT_SECONDS=60`을 권장한다.

## 검증 명령

FastAPI:

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server
python -m compileall app tests
python -m pytest tests/test_detection_api.py -q
```

Raspberry Pi:

```bash
python health_check.py
python integration_smoke_test.py
python camera_upload.py
python camera_live_upload.py
```

Live preview:

```text
http://<PC_LAN_IP>:8000/api/camera/live
```

## 공유 전 정리 기준

- DB 테스트 데이터는 비운다.
- `fastapi-server/storage/detections` 산출 이미지는 공유 전에 정리한다.
- `fastapi-server/models/best.pt`는 Git에 올리지 않고 팀 공유 방식으로 별도 전달한다.
- 실제 테스트 이미지/영상은 `test-media`에 로컬 보관하고 Git에는 올리지 않는다.

## 영상 처리 범위

- 현재 실시간 처리는 영상 파일이 아니라 프레임 단위 JPEG 업로드 방식이다.
- `camera_upload_loop.py`가 일정 간격으로 프레임을 캡처해 `/api/detections/image/send`로 보낸다.
- FastAPI는 프레임마다 원본 저장, YOLO 탐지, 번호판 crop 저장, OCR 전처리 이미지 저장, OCR, Spring DB 저장을 수행한다.
- `.mp4` 녹화, 영상 파일 재처리, 탐지 전후 클립 저장은 아직 구현되어 있지 않다.
