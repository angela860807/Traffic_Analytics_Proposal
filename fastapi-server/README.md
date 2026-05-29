# Traffic AI FastAPI Server

FastAPI 서버는 교통 분석 프로젝트에서 AI 추론과 영상 프레임 처리를 담당한다. 라즈베리파이 또는 로컬 영상에서 들어온 프레임을 받아 차량 bbox를 찾고, 이벤트 단위로 best frame을 고른 뒤 번호판 OCR 결과와 과속 정보를 Spring Boot 백엔드와 PostgreSQL에 저장한다.

최종 발표 흐름은 저해상도 프레임으로 차량 bbox/속도/preview를 빠르게 처리하고, 이벤트 종료 후 원본 best frame crop을 별도 high-res OCR API로 보내 OCR/DB 저장을 분리하는 구조다.

```text
local video / camera frame
  -> FastAPI /api/detections/stream-frame
  -> vehicle YOLO bbox
  -> stream event tracking
  -> speed tracking
  -> FINALIZED + bestCandidateFrameNumber
  -> original best frame crop
  -> /api/detections/stream-events/{event_id}/highres-ocr
  -> plate YOLO + OCR variants
  -> Spring Boot /api/v1/detection-logs
  -> optional Spring Boot /api/speed-violations
```

## 1. 최종 역할

- FastAPI 서버 상태 확인 및 API 문서 제공
- Raspberry Pi 또는 로컬 테스트 클라이언트의 이미지/프레임 수신
- 차량 YOLO 기반 bbox 탐지
- 차량 이벤트 시작, 유지, 종료 처리
- 이벤트 후보 프레임 scoring 및 best frame 선정
- 번호판 YOLO crop 및 PaddleOCR 인식
- OCR 전처리 variant 생성 및 best OCR 결과 선택
- `FLOW_EVENT_CREATED`, `OCR_FAILED`, `DUPLICATE_SKIPPED` 상태 분리
- bbox bottom-center 기반 속도 추정 및 과속 여부 판단
- Spring Boot 내부 API로 detection log, flow event, speed violation 저장
- OpenCV bbox preview 및 발표용 한글 pretty log 제공

## 2. 개발 흐름 요약

### 2.1 초기 FastAPI 골격

초기에는 모델과 Spring Boot 계약이 완성되기 전이었기 때문에 mock 기반 API로 흐름을 먼저 검증했다.

- `GET /health`
- `POST /api/detections/mock`
- `POST /api/detections/image`
- `POST /api/detections/mock/send`
- `POST /api/camera/frame`
- `GET /api/camera/latest.jpg`
- `GET /api/camera/live`

이 단계에서 Python 내부는 `snake_case`, 외부 JSON/API는 Spring/Vue와 맞추기 위해 `camelCase`로 정리했다. 이미지 저장은 FastAPI가 담당하고, DB에는 `imagePath`와 브라우저 표시용 `imageUrl`을 함께 넘기는 정책을 잡았다.

### 2.2 Raspberry Pi 연동

라즈베리파이는 추론을 수행하지 않고 촬영 및 업로드만 담당하도록 정리했다. 실제 YOLO/OCR 추론은 Windows PC의 FastAPI 서버에서 수행한다.

- Raspberry Pi health check
- 샘플 이미지 업로드
- 카메라 frame 업로드
- live preview 메모리 갱신
- OCR 초기 로딩을 고려한 60초 timeout 권장

### 2.3 Spring Boot / PostgreSQL 연동

FastAPI 분석 결과는 Spring Boot 내부 API로 전달한다.

```text
POST /api/v1/detection-logs
Header: X-Internal-Api-Key
```

상태 정책은 다음 기준으로 정리했다.

| 상태 | 의미 | 저장 범위 |
| --- | --- | --- |
| `ANALYSIS_ONLY` | FastAPI 분석 전용 | Spring 저장 없음 |
| `FLOW_EVENT_CREATED` | 번호판 OCR 성공 | detection log, analysis result, flow event |
| `OCR_FAILED` | 차량/번호판 후보는 있으나 OCR 실패 | detection log, analysis result |
| `DUPLICATE_SKIPPED` | 중복 window 안의 동일 번호판 | detection log, analysis result |

### 2.4 Docker / 프론트 통합

프로젝트 전체는 Docker Compose로 묶었다.

```text
postgres-db       5432
spring-backend    8080
fastapi-server    8000
frontend          5174 -> nginx 80
```

프론트는 `/api`를 Spring Boot로, `/static/detections`를 FastAPI 정적 파일로 프록시하는 방향으로 정리했다. FastAPI 산출 이미지는 `fastapi-server/storage/detections` 아래 날짜별로 저장된다.

### 2.5 BBox 트리거 기반 frame buffering

처음에는 몇 초마다 한 장을 캡처하는 방식도 검토했지만, 차량 번호판이 선명하게 잡히는 순간을 놓치기 쉬웠다. 최종 방향은 bbox 이벤트 기반 buffering이다.

```text
pre-buffer 유지
  -> 차량 bbox 감지
  -> event tracking
  -> 후보 frame 누적
  -> 차량 미검출 또는 max duration 도달
  -> best frame 선택
  -> OCR/DB 저장
```

이 버퍼는 디스크가 아니라 메모리 ring buffer이며, 이벤트가 없으면 자동 폐기된다.

### 2.6 Dual YOLO 구조

번호판 bbox만 기준으로 이벤트를 만들면 차량은 지나갔지만 번호판이 작거나 흐린 경우 이벤트 자체를 놓칠 수 있었다. 그래서 분석 흐름을 차량 탐지와 번호판 탐지로 분리했다.

```text
vehicle YOLO
  -> vehicle bbox event trigger
  -> plate YOLO inside candidate frame/crop
  -> OCR
```

정책:

- 차량 bbox 없음: DB 저장하지 않음
- 차량 bbox 있음 + OCR 실패: `OCR_FAILED`
- 번호판 OCR 성공: `FLOW_EVENT_CREATED`
- 동일 번호판 중복: `DUPLICATE_SKIPPED`

`UNKNOWN`은 영상 stream에서 매 프레임 저장하면 로그가 과도해져 적극 사용하지 않는다.

### 2.7 과속 탐지

초기에는 Line A/B 통과 시간을 기준으로 속도를 계산했지만, 테스트 영상에서는 선 통과 순간이 불안정했다. 최종 기본 모드는 `TRACK_DELTA`다.

- 차량 bbox 하단 중앙점(bottom-center)을 차량 위치로 사용
- 일정 시간 동안 이동한 거리를 추정
- `거리 / 시간 * 3.6`으로 km/h 계산
- 최근 speed measurement 최대 5개를 median smoothing
- 제한속도는 최종 발표 기준 `70.0km/h`

과속 저장 조건:

- OCR 성공
- Spring flow event id 확보
- 과속 측정값 존재
- 중복 요청은 Spring에서 멱등 처리

### 2.8 ROI / Homography

ROI와 homography 구조는 지원한다. 다만 발표 최종본에서는 현장 실측값이 없는 상태에서 무리하게 homography를 적용하면 오히려 속도값이 흔들릴 수 있어, lightweight 추정과 median smoothing을 우선 사용한다.

정리된 시연 근사값:

```text
roi-height-meters = 22.0
roi-width-meters  = 10.5
distance-meters   = 22.0
speed-limit-kmh   = 70.0
```

### 2.9 High-Resolution OCR

`--upload-scale`을 낮추면 YOLO/preview는 가벼워지지만 OCR 품질이 떨어진다. 이를 해결하기 위해 탐지/preview는 저해상도 frame으로 유지하고, OCR 저장 순간만 원본 best frame crop을 사용한다.

최종 채택 구조:

```text
low-res upload frame
  -> vehicle bbox / speed / stream status
  -> FINALIZED
  -> bestCandidateFrameNumber + bestCandidateBbox 반환

client
  -> original video seek
  -> original crop = uploaded bbox / upload_scale
  -> POST /stream-events/{event_id}/highres-ocr

FastAPI
  -> plate detector
  -> OCR preprocessing variants
  -> recognize_best
  -> Spring 저장
```

TOP-N 원본 frame voting과 batch OCR도 시도했지만 GUI 반응성이 크게 떨어져 제거했다. 최종본은 단일 best frame + OCR ensemble이다.

### 2.10 발표용 로그와 GUI

Python raw 로그는 발표자가 아닌 사람이 읽기 어려웠기 때문에 Node wrapper를 추가했다.

```text
scripts/pretty_stream_video_file.js
```

출력 예:

```text
● 차량 추적 중
● 과속 차량 감지  75.6 / 70km/h
● 번호판 인식 결과  70가0777  저장 완료
● 차량 분석 완료  계산 속도=75.6km/h 과속
=============================================================================
```

GUI에서는 `IDLE`/`FINALIZED` 상태에서 bbox를 오래 유지하지 않고, 차량이 지나간 뒤 허공에 bbox가 남는 현상을 줄였다.

## 3. 디렉터리 구조

```text
app/main.py                          # FastAPI 앱, router/static 등록
app/api/routes/detection.py          # 탐지, stream, OCR API
app/api/routes/camera_stream.py      # Raspberry Pi live preview
app/core/config.py                   # 환경 변수 설정
app/schemas/detection.py             # API request/response schema
app/schemas/speed.py                 # 속도/과속 schema
app/services/backend_client.py       # Spring Boot 전송
app/services/inference_service.py    # 차량/번호판/OCR orchestration
app/services/stream_event_service.py # stream event buffer/finalize
app/services/speed_tracker.py        # TRACK_DELTA/LINE_CROSSING 속도 계산
app/services/speed_config.py         # 카메라별 속도 설정/검증
app/services/vehicle_detector.py     # 차량 YOLO
app/services/plate_detector.py       # 번호판 YOLO
app/services/plate_recognizer.py     # PaddleOCR
app/services/image_preprocessor.py   # OCR 전처리 variants
scripts/stream_video_file.py         # 영상 업로드 + OpenCV preview
scripts/pretty_stream_video_file.js  # 발표용 로그 wrapper
tests/test_detection_api.py          # FastAPI 회귀 테스트
```

## 4. 실행

프로젝트 루트에서 Docker Compose 실행을 권장한다.

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal
docker compose up -d postgres-db spring-backend fastapi-server frontend
```

FastAPI만 로컬에서 실행할 때:

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal\fastapi-server
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## 5. 환경 변수

`.env.example`을 복사해 로컬 `.env`를 만들 수 있다.

```powershell
Copy-Item .env.example .env
```

핵심 값:

```env
SPRING_BACKEND_BASE_URL=http://127.0.0.1:8080
SPRING_DETECTION_PATH=/api/v1/detection-logs
SPRING_SPEED_VIOLATION_PATH=/api/speed-violations
BACKEND_INTERNAL_API_KEY=traffic-ai-internal-key-2026

IMAGE_STORAGE_DIR=storage/detections
STATIC_DETECTIONS_URL_PREFIX=/static/detections
MODEL_PATH=models/best.pt
PLATE_MODEL_PATH=models/best.pt
VEHICLE_MODEL_NAME=yolo11s.pt

STREAM_FPS=5
PRE_BUFFER_SECONDS=2
POST_MISS_FRAMES=5
MAX_EVENT_SECONDS=4
TOP_N_OCR_FRAMES=1
SAVE_EVENT_DEBUG=false

SPEED_DETECTION_ENABLED=true
SPEED_DEFAULT_LIMIT_KMH=70.0
SPEED_DEFAULT_DISTANCE_METERS=14.0
SPEED_DEFAULT_MODE=TRACK_DELTA
```

Docker Compose 기준 모델 경로:

```text
fastapi-server/models/best.pt
/app/models/best.pt
```

## 6. 주요 API

| 용도 | Method | Path |
| --- | --- | --- |
| Health check | GET | `/health` |
| 모델 warmup | POST | `/api/detections/warmup` |
| 이미지 분석만 | POST | `/api/detections/image` |
| 이미지 분석 후 저장 | POST | `/api/detections/image/send` |
| stream frame 처리 | POST | `/api/detections/stream-frame` |
| event OCR 상태 조회 | GET | `/api/detections/stream-events/{event_id}/ocr-status` |
| event high-res OCR 저장 | POST | `/api/detections/stream-events/{event_id}/highres-ocr` |
| Raspberry Pi frame 갱신 | POST | `/api/camera/frame` |
| Raspberry Pi latest image | GET | `/api/camera/latest.jpg` |
| Raspberry Pi live page | GET | `/api/camera/live` |

초기 개발용 `/mock`, `/mock/send` 경로도 남아 있지만 최종 발표 흐름은 stream frame과 high-res OCR 경로를 기준으로 한다.

## 7. 최종 시연 명령

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal\fastapi-server

node scripts\pretty_stream_video_file.js `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --auto-full-frame-speed-zone `
  --video-speed-ratio 0.50 `
  --roi-height-meters 22.0 `
  --roi-width-meters 10.5 `
  --distance-meters 22.0 `
  --speed-limit-kmh 70.0 `
  --scale 0.40 `
  --realtime `
  --preview-bbox `
  --preview-tracker `
  --preview-tracker-max-age-seconds 0.35 `
  --async-upload `
  --upload-queue-size 2 `
  --preview-delay-seconds 6.5 `
  --finalized-highres-ocr `
  --highres-crop-padding 0.35 `
  --highres-jpeg-quality 90 `
  --fps 5 `
  --preview-fps 10 `
  --upload-scale 0.60 `
  --bbox-hold-seconds 0 `
  --preview-max-event-age-seconds 0 `
  --preview-max-bbox-area-ratio 0.45 `
  --preview-min-bbox-confidence 0.20 `
  --preview-max-response-lag-seconds 0.35 `
  --no-preview-primary-bbox-only
```

tracker 때문에 GUI가 끊기면 아래 두 옵션을 제거한다.

```powershell
--preview-tracker
--preview-tracker-max-age-seconds 0.35
```

최종 명령에서는 `--highres-ocr-crop`을 사용하지 않는다. 이 옵션은 일반 stream upload마다 crop을 붙이는 구버전 방식이라 최종 발표 흐름에서는 제외한다.

## 8. 저장 산출물

```text
fastapi-server/storage/detections
  YYYY/MM/DD/
    *_frame.jpg
    *_vehicle_crop.jpg
    *_plate_crop.jpg
    *_ocr.jpg

fastapi-server/models/best.pt
```

`storage`, `models/*.pt`, 실제 테스트 영상/이미지는 Git 추적 대상이 아니다. 팀 공유용 테스트 자료는 루트 `test-media`에 로컬 보관한다.

## 9. 검증

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal\fastapi-server
.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py app\api\routes\detection.py
.\.venv\Scripts\python.exe -m pytest tests\test_detection_api.py -q
```

현재 기준:

```text
64 passed
```

Docker 설정 검증:

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal
docker compose config --quiet
docker compose ps
```

## 10. 현재 한계

- YOLO 추론, OpenCV GUI, HTTP 업로드, tracker가 발표 스크립트 한 프로세스에 묶여 있어 저사양 PC에서는 완전 실시간이 어렵다.
- 속도는 현장 실측 전 추정값이다. 실제 단속값으로 쓰려면 고정 카메라 캘리브레이션, 차선 기준점, homography/Line A/B 검증이 필요하다.
- OCR 품질은 원본 영상 초점, 모션 블러, 번호판 픽셀 수에 크게 의존한다.
- OCR 상태는 메모리 dict + TTL 구조라 서버 재시작 시 사라진다.
- background task는 시연용 경량 분리이며, 운영 수준의 영속 queue는 아니다.

## 11. 후속 개선 방향

1. stream frame 응답과 OCR/DB 저장을 worker queue로 완전히 분리
2. ByteTrack 또는 BoT-SORT 기반 track id 도입
3. ROI, 면적, aspect ratio 기반 차량 bbox 후처리 강화
4. 한국 번호판 형식 점수와 OCR 오인식 보정 테이블 강화
5. latency, dropped frame, OCR 실패율, false alarm rate 같은 지표 수집
6. 현장 카메라별 calibration/homography 설정 관리
7. 정상 속도 차량의 speed 저장 정책과 체류시간 계산 정책 추가
