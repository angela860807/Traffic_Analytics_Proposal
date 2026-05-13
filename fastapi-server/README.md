# Traffic AI Server

차량 흐름 분석 시스템의 FastAPI AI 서버입니다.

현재 단계에서는 실제 YOLO/OCR 모델과 Spring Boot API가 아직 확정되지 않았으므로, mock inference로 입력 파이프라인을 먼저 검증합니다.

## 역할

- Raspberry Pi 또는 카메라 클라이언트로부터 이미지 프레임 수신
- 서버 PC에서 YOLO/OCR 추론 수행 예정
- 감지 결과 생성
- 감지 이미지 저장
- 추후 Spring Boot Backend로 감지 결과 JSON 전송
- Raspberry Pi live preview 테스트 지원

## 현재 팀 합의

- Raspberry Pi는 추론하지 않고 카메라 프레임 수집/전송만 담당한다.
- FastAPI 서버 PC에서 YOLO/OCR 추론을 수행한다.
- 초기 테스트 입력은 base64 JSON으로 진행한다.
- 최종 목표 입력 방식은 multipart/form-data 이미지 업로드이다.
- `cameraCode`는 `CAM_001`, `CAM_002` 형식을 사용한다.
- `zoneCode`는 `ZONE_001`, `ZONE_002` 형식을 사용한다.
- `directionType`은 `IN`, `OUT`, `BOTH`를 사용한다.
- `detectionType`은 `VEHICLE`, `PLATE`를 사용한다.
- `confidenceScore` 기준값은 `0.7`로 시작한다.
- 이미지는 FastAPI 서버가 저장한다.
- 번호판 인식 실패 시 `plateNumber`는 `null`로 둔다.
- 번호판 인식 실패 결과도 Spring으로 전송하며 `detection_analysis_results.status=OCR_FAILED`로 저장한다.
- FastAPI 중복 판정 결과도 Spring으로 전송하며 `detection_analysis_results.status=DUPLICATE_SKIPPED`로 저장한다.
- `UNKNOWN` 문자열은 사용하지 않는다.
- 대시보드 통계는 `vehicle_flow_events` 기준으로 보여준다.

## 실행

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server

.\.venv\Scripts\Activate.ps1

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Raspberry Pi에서 접근해야 할 때는 외부 접속을 허용하도록 `0.0.0.0`으로 실행합니다.

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 문서

```text
http://127.0.0.1:8000/docs
```

## 환경변수

`.env.example`을 복사해서 `.env`를 만든 뒤 로컬 값에 맞게 수정합니다.

```powershell
Copy-Item .env.example .env
```

주요 설정:

```env
APP_NAME=traffic-ai-server
APP_ENV=local

SPRING_BACKEND_BASE_URL=http://127.0.0.1:8080
SPRING_DETECTION_PATH=/api/v1/detection-logs

DEFAULT_TIMEZONE=Asia/Seoul
DETECTION_CONFIDENCE_THRESHOLD=0.7
DUPLICATE_WINDOW_SECONDS=10
IMAGE_STORAGE_DIR=storage/detections
STATIC_DETECTIONS_URL_PREFIX=/static/detections
PUBLIC_BASE_URL=

MODEL_PATH=best.pt
OCR_LANG=korean
YOLO_CONF_THRESHOLD=0.5
YOLO_IOU_THRESHOLD=0.4
YOLO_MAX_DET=5
DETECTION_PREPROCESS_MODE=none
PLATE_CROP_PADDING_RATIO=0.10
OCR_MIN_CONFIDENCE=0.5
OCR_PREPROCESS_SCALE=2.0
OCR_ADAPTIVE_BLOCK_SIZE=31
OCR_ADAPTIVE_C=5
SAVE_PLATE_CROP=true
SAVE_OCR_PREPROCESSED_IMAGE=true
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

## 테스트용 샘플 이미지 생성

```powershell
python scripts/create_sample_image.py
```

생성 위치:

```text
samples/sample.jpg
```

## Base64 Mock Detection

```powershell
$imageBytes = [System.IO.File]::ReadAllBytes((Resolve-Path ".\samples\sample.jpg"))

$body = @{
    cameraCode = "CAM_001"
    capturedAt = "2026-04-30T10:30:00"
    imageBase64 = [Convert]::ToBase64String($imageBytes)
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/detections/mock" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## Multipart Image Detection

Windows PowerShell 버전에 따라 `Invoke-RestMethod -Form`이 없을 수 있으므로 `curl.exe`를 사용합니다.

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/detections/image" `
    -F "cameraCode=CAM_001" `
    -F "capturedAt=2026-04-30T10:30:00" `
    -F "image=@samples/sample.jpg;type=image/jpeg"
```

정상 응답 예시:

```json
{
  "accepted": true,
  "message": "Detection result created from image",
  "data": {
    "cameraCode": "CAM_001",
    "plateNumber": "123가4567",
    "detectionType": "PLATE",
    "directionType": "IN",
    "confidenceScore": 0.9321,
    "imagePath": "storage/detections/2026/05/01/CAM_001_143632_frame.jpg",
    "imageUrl": "/static/detections/2026/05/01/CAM_001_143632_frame.jpg",
    "detectedAt": "2026-05-01T14:36:32"
  }
}
```

`imagePath`는 DB 저장/추적용 로컬 경로이고, `imageUrl`은 Vue 등 클라이언트가 이미지를 표시할 때 사용할 정적 파일 URL입니다.

예:

```text
http://127.0.0.1:8000/static/detections/2026/05/01/CAM_001_143632_frame.jpg
```

## Camera Live Preview

Raspberry Pi가 최신 프레임을 계속 전송하면 FastAPI PC 브라우저에서 live preview를 확인할 수 있습니다.

```text
POST /api/camera/frame
GET  /api/camera/latest.jpg
GET  /api/camera/live
```

브라우저 확인:

```text
http://<FASTAPI_PC_IP>:8000/api/camera/live
```

이 기능은 테스트용 preview이며 이미지를 저장하지 않습니다.

## Raspberry Pi 예제 클라이언트

로컬 샘플 이미지 기반 테스트:

```powershell
python examples/raspberry_pi_base64_client.py
python examples/raspberry_pi_multipart_client.py
```

Raspberry Pi 실기 파일은 `examples/`에 재현 가능한 형태로 보관합니다. 실제 캡처 이미지, 개인 IP, `.env`, `storage/` 파일은 Git에 올리지 않습니다.

## 자동 테스트

```powershell
python -m pytest
```

## 문법 검사

```powershell
python -m compileall app
```

## 병합 테스트 주의사항

mock inference 단계에서는 번호판이 `123가4567`로 고정됩니다.
`DUPLICATE_WINDOW_SECONDS` 안에 같은 `cameraCode`와 번호판이 반복되면 FastAPI가 Spring에 `DUPLICATE_SKIPPED` 분석 상태로 전송합니다. 따라서 `detection_analysis_results` row는 증가하지만 `vehicle_flow_events`는 증가하지 않는 것이 정상입니다.

## 에러 응답

```text
잘못된 base64:
imageBase64 must be valid image base64

지원하지 않는 파일 형식:
image must be jpeg or png

이미지 디코딩 실패:
image must be a valid jpg or png

백엔드 미연결:
Spring Boot API is not reachable

백엔드 오류 응답:
Spring Boot API returned error: {status_code}
```

## 현재 보류 사항

- Spring Boot API 경로와 응답 형식
- FastAPI에서 Spring Boot로 보낼 최종 JSON 필드명
- 실제 YOLO/OCR 모델 방식
- 번호판 crop 이미지 저장 방식
- Spring Boot/Vue에서 imageUrl을 어떻게 저장/노출할지 여부
- directionType을 Spring Boot가 cameraCode 기준으로 최종 판단하도록 연동 계약 반영
- Raspberry Pi 장시간 안정성 테스트
- 전체 통합 테스트
