# Traffic AI Server

## BBox Stream Frame Test

### 내용

`POST /api/detections/stream-frame`는 영상 또는 카메라 프레임을 JPEG multipart로 계속 받아서 FastAPI 메모리의 카메라별 ring buffer에 보관한다. YOLO bbox가 confidence 기준 이상으로 감지되면 이벤트를 시작하고, bbox가 사라진 뒤 `POST_MISS_FRAMES`만큼 지나거나 `MAX_EVENT_SECONDS`를 넘으면 이벤트를 종료한다. 이벤트 종료 시 후보 프레임을 scoring한 뒤 best frame 또는 top-N frame만 OCR하고 Spring Boot `/api/v1/detection-logs`로 저장한다.

### 요약

```text
video/camera frame
  -> /api/detections/stream-frame
  -> per-camera ring buffer
  -> bbox event tracking
  -> candidate scoring
  -> selected frame OCR
  -> Spring DB save
```

주요 설정값:

```env
STREAM_FPS=5
PRE_BUFFER_SECONDS=2
POST_MISS_FRAMES=5
MAX_EVENT_SECONDS=4
TOP_N_OCR_FRAMES=1
SAVE_EVENT_DEBUG=false
```

`SAVE_EVENT_DEBUG=true`로 설정하면 이벤트 종료 시 상위 후보 프레임 일부가 `storage/detections/debug/<yyyy>/<mm>/<dd>/<eventId>/` 아래에 저장된다.

### 목적

라즈베리파이 카메라 없이도 PC의 `.mp4` 파일로 bbox 기반 버퍼링 구조를 반복 검증하기 위한 절차다. 실제 시연 전 이벤트 시작/종료, OCR 성공/실패, Spring 저장 결과를 빠르게 확인할 수 있다.

### 실행 절차

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal
docker compose up -d postgres-db spring-backend fastapi-server
```

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server
.\.venv\Scripts\python.exe scripts\stream_video_file.py `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --fps 5 `
  --realtime
```

콘솔에서 `streamStatus=IDLE`, `streamStatus=TRACKING`, `streamStatus=FINALIZED` 흐름을 확인한다. `FINALIZED` 응답에서 `analysisStatus=FLOW_EVENT_CREATED`, `OCR_FAILED`, `DUPLICATE_SKIPPED` 중 하나가 나오면 Spring 저장 흐름까지 도달한 것이다.

차량 번호판 이미지를 수신하고, PC에서 YOLO/OCR 추론을 수행한 뒤 Spring Boot 백엔드로 탐지 결과를 전달하는 FastAPI 서버입니다.

## 현재 역할

- Raspberry Pi 또는 수동 테스트 클라이언트에서 이미지 수신
- 원본 프레임, 번호판 crop, OCR 전처리 이미지 저장
- YOLO 모델(`models/best.pt`)과 OCR 기반 번호판 인식
- 번호판 미인식, 정상 인식, 중복 인식 상태 분리
- Spring 내부 API `POST /api/v1/detection-logs`로 결과 전송
- `/api/camera/live` 기반 Raspberry Pi live preview 제공

## 실행

프로젝트 루트에서 Docker Compose 실행을 권장합니다.

```powershell
docker compose up -d postgres-db spring-backend fastapi-server
```

FastAPI만 로컬에서 실행할 때는 아래처럼 실행합니다.

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Raspberry Pi에서 접근해야 하므로 PC 방화벽과 같은 네트워크 대역을 확인합니다.

## 환경 변수

`.env.example`을 복사해 `.env`를 만들고 로컬 값에 맞게 수정합니다.

```powershell
Copy-Item .env.example .env
```

주요 값:

```env
SPRING_BACKEND_BASE_URL=http://127.0.0.1:8080
SPRING_DETECTION_PATH=/api/v1/detection-logs
BACKEND_INTERNAL_API_KEY=traffic-ai-internal-key-2026

DUPLICATE_WINDOW_SECONDS=10
IMAGE_STORAGE_DIR=storage/detections
STATIC_DETECTIONS_URL_PREFIX=/static/detections
MODEL_PATH=models/best.pt

DETECTION_PREPROCESS_MODE=none
SAVE_PLATE_CROP=true
SAVE_OCR_PREPROCESSED_IMAGE=true
```

Docker Compose에서는 `MODEL_PATH=/app/models/best.pt`와 `fastapi-server/models:/app/models:ro` 볼륨을 사용합니다.

## 주요 API

| 용도 | Method | Path | 저장/전송 |
| --- | --- | --- | --- |
| Health check | GET | `/health` | 없음 |
| Base64 분석만 | POST | `/api/detections/mock` | FastAPI 이미지 저장, Spring 미전송 |
| Multipart 분석만 | POST | `/api/detections/image` | FastAPI 이미지 저장, Spring 미전송 |
| Base64 분석 후 저장 | POST | `/api/detections/mock/send` | Spring 전송 |
| Multipart 분석 후 저장 | POST | `/api/detections/image/send` | Spring 전송 |
| Live preview frame | POST | `/api/camera/frame` | 메모리 최신 프레임만 갱신 |
| Live preview image | GET | `/api/camera/latest.jpg` | 없음 |
| Live preview page | GET | `/api/camera/live` | 없음 |

API 문서:

```text
http://127.0.0.1:8000/docs
```

## Health Check

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

정상 응답:

```json
{
  "status": "ok",
  "service": "traffic-ai-server"
}
```

## 수동 이미지 업로드

샘플 이미지는 `fastapi-server/samples` 또는 루트의 `test-media/images` 아래에 둡니다. 작은 합성 fixture만 `samples`에 두고, 실제 차량 이미지/영상은 Git에 올리지 않습니다.

Spring DB 저장까지 확인:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/detections/image/send" `
  -F "cameraCode=CAM_001" `
  -F "capturedAt=2026-05-14T10:30:00" `
  -F "image=@samples/sample.jpg;type=image/jpeg"
```

분석만 확인:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/detections/image" `
  -F "cameraCode=CAM_001" `
  -F "capturedAt=2026-05-14T10:30:00" `
  -F "image=@samples/sample.jpg;type=image/jpeg"
```

## 응답 상태

`analysisStatus` 기준으로 결과를 판단합니다.

| 상태 | 의미 | DB 저장 |
| --- | --- | --- |
| `ANALYSIS_ONLY` | FastAPI 분석 전용 응답 | Spring DB 저장 없음 |
| `FLOW_EVENT_CREATED` | 번호판 정상 인식 및 flow event 생성 | `detection_logs`, `detection_analysis_results`, `vehicle_flow_events` |
| `OCR_FAILED` | 번호판 미인식 | `detection_logs`, `detection_analysis_results` |
| `DUPLICATE_SKIPPED` | 중복 window 내 동일 번호판 | `detection_logs`, `detection_analysis_results` |

원본 이미지는 `imageUrl`, 번호판 crop은 `plateCropImageUrl`, OCR 전처리 이미지는 `ocrImageUrl`로 내려갑니다.

## 저장 경로

런타임 산출물은 Git에 올리지 않습니다.

```text
fastapi-server/storage/detections  # 원본/crop/OCR 산출 이미지
fastapi-server/models/best.pt      # YOLO 모델 파일
```

팀 공유용 테스트 이미지는 루트의 `test-media`에 두고, 실제 파일은 각자 로컬에 보관합니다.
`test-media`는 자동 저장 경로가 아니라 사람이 테스트 자료를 분류해 보관하는 로컬 폴더입니다.

## Raspberry Pi Live Preview

Raspberry Pi가 최신 프레임을 계속 전송하면 PC 브라우저에서 확인할 수 있습니다.

```text
http://<PC_LAN_IP>:8000/api/camera/live
```

이 기능은 preview 용도이며 DB 저장을 하지 않습니다.

## 영상 처리 범위

현재 FastAPI는 업로드된 이미지 1장 또는 Raspberry Pi가 주기적으로 보낸 프레임 1장을 처리합니다. `.mp4` 같은 영상 파일을 직접 읽거나 녹화하지는 않습니다.

실시간 촬영은 `camera_upload_loop.py`가 프레임을 JPEG로 샘플링해 `/api/detections/image/send`로 보내는 방식입니다. 이 경로에서는 YOLO가 번호판 bbox를 찾으면 번호판 crop과 OCR 전처리 이미지를 저장하고 OCR 결과를 Spring DB로 전송합니다.

영상 파일 저장/재처리나 탐지 순간 전후 클립 보관은 아직 별도 기능으로 구현되어 있지 않습니다.

## 검증

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server
python -m compileall app tests
python -m pytest tests/test_detection_api.py -q
```

YOLO/OCR 모델 직접 검증:

```powershell
$env:MODEL_PATH="models/best.pt"
python scripts/verify_yolo_ocr.py --image samples/sample.jpg --camera-code CAM_001
```

## 주의사항

- Spring 내부 API 호출에는 `X-Internal-Api-Key`가 필요합니다.
- `DUPLICATE_WINDOW_SECONDS` 안에 같은 `cameraCode + plateNumber`가 반복되면 `DUPLICATE_SKIPPED`로 저장됩니다.
- OCR 초기 로딩은 시간이 걸릴 수 있으므로 Raspberry Pi 클라이언트 timeout은 60초를 권장합니다.
- 테스트 후 DB를 비우려면 탐지 관련 테이블을 `detection_analysis_results`, `detection_logs`, `vehicle_flow_events`, `hourly_traffic_stats`, `vehicles` 기준으로 초기화합니다.
