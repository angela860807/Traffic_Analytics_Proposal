# FastAPI - Raspberry Pi 작업 진행 문서

작성일: 2026-05-10

## 현재 완료 범위

### 1. 번호판 미인식 처리 정책

- FastAPI 분석 결과가 `detectionType=PLATE`이고 `plateNumber`가 있을 때만 Spring Boot로 전송한다.
- 번호판 미인식 결과도 Spring으로 전송하고 `detection_logs.status=OCR_FAILED`로 저장한다.
- `OCR_FAILED` 로그는 차량 번호가 없으므로 `vehicles`, `vehicle_flow_events`는 생성하지 않는다.

### 2. 원본 이미지 + crop + OCR 전처리 이미지 저장

- 원본 프레임은 항상 `*_frame.jpg`로 저장한다.
- YOLO bbox가 있는 경우 번호판 crop 이미지를 `*_plate_crop.jpg`로 저장한다.
- OCR 입력용 전처리 이미지를 `*_ocr.jpg`로 저장한다.
- Spring/Vue에 전달하는 `imagePath`, `imageUrl`은 원본 프레임 기준을 유지한다.
- Docker 실행 환경에서도 아래 설정을 기본 활성화했다.

```env
SAVE_PLATE_CROP=true
SAVE_OCR_PREPROCESSED_IMAGE=true
```

### 3. 저장 이미지 기반 YOLO/OCR 재처리 구조

- `ImageDecoder.decode_image_file(image_path)`로 기존 저장 이미지를 다시 읽을 수 있게 했다.
- `InferenceService.detect_from_saved_image(...)`를 추가해 저장된 원본 이미지 기준으로 YOLO/OCR을 재실행할 수 있게 했다.
- 재처리 시 기존 `*_frame.jpg`를 중복 저장하지 않고 기존 `imagePath`를 유지한다.
- crop/OCR 전처리 이미지는 현재 설정 기준대로 다시 생성된다.

### 4. 전처리 역할 분리

- 라즈베리파이는 촬영, JPEG 인코딩, FastAPI 업로드만 담당한다.
- FastAPI가 탐지용 전처리와 OCR용 전처리를 담당한다.
- `image_preprocessor.py`를 추가해 전처리 책임을 분리했다.

```text
preprocess_frame_for_detection()
  - YOLO 입력 전용 전처리
  - 기본값은 none으로 원본 유지
  - standard 설정 시 grayscale, blur, histogram equalization, sharpen 적용

crop_plate_with_padding()
  - YOLO bbox 기준 번호판 crop

preprocess_plate_for_ocr()
  - OCR 입력 전용 전처리
  - resize, grayscale, blur, adaptive threshold 적용
```

Docker/FastAPI 기본 설정:

```env
DETECTION_PREPROCESS_MODE=none
```

`standard`는 모델 성능을 확인한 뒤 켠다. YOLO 모델은 원본 이미지 분포에 맞춰 학습된 경우가 많으므로, 탐지 전처리는 기본 비활성화가 안전하다.

## 주요 변경 파일

- `fastapi-server/app/api/routes/detection.py`
- `fastapi-server/app/core/config.py`
- `fastapi-server/app/services/image_decoder.py`
- `fastapi-server/app/services/duplicate_detection_guard.py`
- `fastapi-server/app/services/image_preprocessor.py`
- `fastapi-server/app/services/inference_service.py`
- `fastapi-server/app/services/plate_cropper.py`
- `fastapi-server/scripts/verify_yolo_ocr.py`
- `fastapi-server/tests/test_detection_api.py`
- `fastapi-server/.env.example`
- `docker-compose.yml`

## 검증 결과

```powershell
python -m compileall app tests
```

위 문법 검사는 통과했다.

```powershell
python -m pytest tests/test_detection_api.py -q
```

현재 PC Python에는 `pytest`가 설치되어 있지 않아 실행하지 못했다.

## 다음 작업 후보

### 5. 중복 제거 기준 1차 구현

- `cameraCode + plateNumber + 시간 window` 기준으로 FastAPI의 Spring 전송 중복을 방지한다.
- 중복 window는 `DUPLICATE_WINDOW_SECONDS` 설정을 사용한다.
- 동일 번호판이 window 안에 다시 들어오면 Spring으로 전송하되 `detection_logs.status=DUPLICATE_SKIPPED`로 저장한다.
- 백엔드 저장 성공 후에만 중복 기준으로 기록한다.
- 최종 Tracking ID 기반 중복 제거는 YOLO/OCR 모델 검증 이후로 둔다.

### 6. YOLOv11 / PaddleOCR 실제 연결 검증

- `scripts/verify_yolo_ocr.py`를 추가했다.
- 실제 `MODEL_PATH`와 샘플 이미지를 기준으로 YOLO/PaddleOCR 파이프라인을 검증한다.
- 모델 파일이 없거나 이미지가 없으면 JSON 형태로 실패 원인을 출력한다.

실행 예시:

```powershell
cd fastapi-server
$env:MODEL_PATH="models/best.pt"
python scripts/verify_yolo_ocr.py --image samples/sample.jpg --camera-code CAM_001
```

출력은 JSON이며, `ok=true`면 실제 모델 추론 경로가 끝까지 완료된 것이다.

### 7. 실시간 화면 전송 방식 정리

- 보류한다.
- 1차는 현재 MJPEG `/api/camera/live`를 유지한다.
- WebSocket은 로그 push나 상태 이벤트가 필요할 때 2차 확장으로 진행한다.

## 작업일지 요약

- FastAPI에서 번호판 미인식 결과를 `OCR_FAILED` 상태로 Spring에 저장하도록 처리했다.
- 원본 프레임, 번호판 crop, OCR 전처리 이미지 저장 구조를 분리했다.
- 저장된 이미지로 YOLO/OCR을 다시 실행할 수 있는 재처리 서비스 경로를 만들었다.
- 라즈베리파이는 수집/업로드만 담당하고, 전처리는 FastAPI가 담당하도록 역할을 분리했다.
- 탐지 전처리와 OCR 전처리를 별도 함수로 나누고, 탐지 전처리는 기본 비활성화했다.
- 동일 `cameraCode + plateNumber`가 설정된 시간 안에 반복 인식되면 `DUPLICATE_SKIPPED` 상태로 Spring에 저장하도록 중복 방지 로직을 조정했다.
- 실제 YOLOv11/PaddleOCR 모델 연결을 확인할 수 있는 검증 스크립트를 추가했다.
- 실시간 화면 전송 방식 정리는 7번 작업으로 보류했다.
