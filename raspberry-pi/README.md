# 라즈베리파이 클라이언트

Raspberry Pi에서 카메라 프레임을 캡처하고 Windows PC의 FastAPI 서버로 전송하는 클라이언트입니다. 추론, 이미지 저장, Spring DB 저장은 PC 쪽 FastAPI/Spring Boot/PostgreSQL이 담당합니다.

## 1. PC 서버 확인

현재 팀 테스트 기준 FastAPI 주소:

```bash
http://192.168.10.91:8000
```

PC IP가 바뀌면 `.env` 또는 환경 변수의 `FASTAPI_BASE_URL`을 수정합니다.

```bash
curl -I http://<PC_LAN_IP>:8000/docs
python health_check.py
```

## 2. 설치

```bash
cd ~/traffic-ai-client
python -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

`picamera2`와 `cv2`는 Raspberry Pi OS의 apt 패키지를 사용합니다.

```bash
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv
```

## 3. 환경 변수

`.env.example`을 `.env`로 복사한 뒤 PC IP를 맞춥니다.

```bash
cp .env.example .env
```

권장 예시:

```env
FASTAPI_BASE_URL=http://192.168.10.91:8000
CAMERA_CODE=CAM_001
REQUEST_TIMEOUT_SECONDS=60
CAPTURE_INTERVAL_SECONDS=5
LIVE_FRAME_INTERVAL_SECONDS=0.2
JPEG_QUALITY=80
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
```

OCR 모델 초기 로딩 때문에 첫 업로드는 10초를 넘길 수 있습니다. `REQUEST_TIMEOUT_SECONDS=60`을 권장합니다.

## 4. 실행 순서

Health check:

```bash
python health_check.py
```

샘플 이미지 생성:

```bash
python create_sample_image.py
```

샘플 이미지를 FastAPI로 보내고 Spring DB 저장까지 확인:

```bash
python upload_sample_image.py
```

Health check와 샘플 업로드를 한 번에 확인:

```bash
python integration_smoke_test.py
```

카메라 단발 캡처 테스트:

```bash
python camera_capture_test.py
```

카메라 단발 캡처 후 DB 저장:

```bash
python camera_upload.py
```

5초마다 캡처 후 DB 저장:

```bash
python camera_upload_loop.py
```

live preview용 프레임 전송:

```bash
python camera_live_upload.py
```

PC 브라우저에서 확인:

```text
http://<PC_LAN_IP>:8000/api/camera/live
```

## 5. 업로드 API 구분

| 용도 | API |
| --- | --- |
| DB 저장용 | `POST /api/detections/image/send` |
| 분석만 확인 | `POST /api/detections/image` |
| live preview 전용 | `POST /api/camera/frame` |

## 6. DB 저장 상태 확인

업로드 스크립트는 FastAPI 응답의 `analysisStatus`를 기준으로 최종 저장 상태를 출력합니다.

```text
analysisStatus=FLOW_EVENT_CREATED   정상 인식, detection_logs/analysis_results/flow_events 저장
analysisStatus=OCR_FAILED           번호판 미인식, detection_logs/analysis_results 저장
analysisStatus=DUPLICATE_SKIPPED    중복 판정, detection_logs/analysis_results 저장
analysisStatus=ANALYSIS_ONLY        /api/detections/image 분석 전용 응답
```

DB에서는 원본 수신 여부를 `detection_logs`, 처리 결과를 `detection_analysis_results.status`, 차량 흐름 생성을 `vehicle_flow_events`에서 확인합니다.

## 7. 파일 관리

Raspberry Pi 로컬의 `.env`, `venv`, 캡처 이미지, 로그 파일은 Git에 올리지 않습니다.

`test-media`는 스크립트가 자동으로 저장하는 경로가 아닙니다. 실제 차량 이미지, 테스트 영상, smoke test 산출물을 사람이 분류해서 보관하는 로컬 테스트 자료함입니다.

스크립트별 자동 생성 위치는 아래와 같습니다.

| 명령 | 자동 생성/저장 위치 |
| --- | --- |
| `python create_sample_image.py` | Raspberry Pi 현재 디렉터리의 `sample.jpg` |
| `python camera_capture_test.py` | Raspberry Pi 현재 디렉터리의 `capture.jpg` |
| `python upload_sample_image.py` | PC FastAPI의 `fastapi-server/storage/detections` |
| `python integration_smoke_test.py` | PC FastAPI의 `fastapi-server/storage/detections` |
| `python camera_upload.py` | PC FastAPI의 `fastapi-server/storage/detections` |
| `python camera_upload_loop.py` | PC FastAPI의 `fastapi-server/storage/detections` |
| `python camera_live_upload.py` | DB/파일 저장 없음, FastAPI 메모리 최신 프레임만 갱신 |

보관할 가치가 있는 테스트용 이미지와 영상은 PC 프로젝트 루트의 `test-media` 아래에 수동으로 정리합니다.

```text
test-media/images/positive
test-media/images/negative
test-media/videos
test-media/smoke-runs
test-media/model-feedback
```

실제 테스트 파일은 Git ignore 대상입니다.

## 8. 영상 처리 범위

현재 코드는 `.mp4` 같은 영상 파일을 녹화하거나 영상 파일을 읽어 처리하지 않습니다. 대신 `camera_upload_loop.py`가 카메라 프레임을 일정 간격으로 JPEG로 캡처해 FastAPI에 업로드합니다.

업로드된 각 프레임은 FastAPI에서 `원본 저장 -> YOLO 탐지 -> 번호판 crop 저장 -> OCR 전처리 이미지 저장 -> OCR -> Spring DB 저장` 순서로 처리됩니다. 즉, 실시간 촬영 중 프레임 단위 번호판 인식과 이미지 저장은 가능합니다.

추후 실제 영상 파일 저장, 영상 파일 재처리, FPS 기반 프레임 샘플링, 탐지 순간 전후 클립 보관이 필요하면 별도 작업으로 추가해야 합니다.
