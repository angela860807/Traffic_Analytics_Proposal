# FastAPI Handoff And TODO

## Current Status

FastAPI 서버는 백엔드 없이 단독으로 이미지 입력 파이프라인을 검증한 상태입니다.

완료된 흐름:

```text
Raspberry Pi Camera
-> Picamera2 image capture
-> multipart/form-data upload
-> FastAPI /api/detections/image
-> mock detection result
-> local image storage
```

검증 완료:

```text
- FastAPI 서버 실행 정상
- /health 정상 응답
- base64 JSON mock detection 정상
- multipart image detection 정상
- Raspberry Pi에서 FastAPI PC로 이미지 업로드 정상
- FastAPI 서버 로그에서 Raspberry Pi 요청 200 OK 확인
- storage/detections 하위에 실제 캡처 이미지 저장 확인
- Raspberry Pi live preview 테스트 정상
```

## GitHub Upload Policy

라즈베리파이에서 작성한 파일은 기기 안에만 두지 말고, 재현 가능한 예제 코드는 FastAPI repo에 함께 보관하는 것을 권장합니다.

권장 구조:

```text
fastapi-server/
  examples/
    raspberry_pi_base64_client.py
    raspberry_pi_multipart_client.py
    raspberry_pi_camera_upload.py
    raspberry_pi_camera_upload_loop.py
    raspberry_pi_live_upload.py
```

별도 브랜치는 권장하지 않습니다.

이유:

```text
- 라즈베리파이 코드는 FastAPI 입력 클라이언트 예제이므로 같은 프로젝트 문맥에 속함
- 브랜치는 기능 개발/수정 흐름 관리용이지, 파트별 파일 보관용으로 쓰기에는 부적합
- 팀원이 clone 후 examples만 보고 재현할 수 있는 구조가 더 좋음
```

단, 아래 내용은 GitHub에 올리지 않습니다.

```text
- 실제 캡처 이미지
- storage/detections 하위 런타임 파일
- 로컬 .env
- 개인 PC IP가 박힌 운영용 파일
- 라즈베리파이 SSH 계정/비밀번호/개인 네트워크 정보
```

IP 주소는 예제 코드에 직접 고정하지 않고, 추후 환경변수 또는 config 파일로 분리하는 것이 좋습니다.

## Current FastAPI APIs

### Health Check

```text
GET /health
```

정상 응답:

```json
{
  "status": "ok",
  "service": "traffic-ai-server"
}
```

### Base64 Mock Detection

```text
POST /api/detections/mock
Content-Type: application/json
```

요청 예시:

```json
{
  "cameraCode": "CAM_001",
  "capturedAt": "2026-05-01T14:36:26",
  "imageBase64": "..."
}
```

### Multipart Image Detection

```text
POST /api/detections/image
Content-Type: multipart/form-data
```

필드:

```text
cameraCode: CAM_001
capturedAt: 2026-05-01T14:36:32
image: jpg or png file
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
    "detectedAt": "2026-05-01T14:36:32"
  }
}
```

### Camera Live Preview

```text
POST /api/camera/frame
GET  /api/camera/latest.jpg
GET  /api/camera/live
```

용도:

```text
- Raspberry Pi가 최신 프레임을 FastAPI로 계속 전송
- FastAPI PC 브라우저에서 /api/camera/live 로 실시간 화면 확인
- 이 기능은 테스트용 preview이며 이미지를 저장하지 않음
```

## Team Decisions Already Reflected

```text
- Raspberry Pi는 추론하지 않고 카메라 프레임 수집/전송만 담당
- FastAPI 서버 PC에서 YOLO/OCR 추론 예정
- 초기 테스트는 base64 JSON 허용
- 최종 목표 입력 방식은 multipart/form-data 이미지 업로드
- cameraCode 형식: CAM_001, CAM_002
- zoneCode 형식: ZONE_001, ZONE_002
- directionType: IN, OUT, BOTH
- detectionType: VEHICLE, PLATE
- confidenceScore 기본 기준값: 0.7
- 이미지는 FastAPI 서버가 저장
- 번호판 인식 실패 시 plateNumber는 null
- UNKNOWN 문자열은 사용하지 않음
- 대시보드 통계는 vehicle_flow_events 기준
```

## Environment Variables

로컬 `.env` 예시:

```env
APP_NAME=traffic-ai-server
APP_ENV=local

SPRING_BACKEND_BASE_URL=http://127.0.0.1:8080
SPRING_DETECTION_PATH=/api/detections

DEFAULT_TIMEZONE=Asia/Seoul
DETECTION_CONFIDENCE_THRESHOLD=0.7
DUPLICATE_WINDOW_SECONDS=10
IMAGE_STORAGE_DIR=storage/detections

MODEL_PATH=
OCR_LANG=korean
```

주의:

```text
.env는 로컬 설정 파일이므로 GitHub에 올리지 않는 것을 권장
필요하면 .env.example을 별도로 만들어 공유
```

## Verification Commands

FastAPI PC:

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

문법 검사:

```powershell
python -m compileall app
```

테스트:

```powershell
python -m pytest
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

저장 이미지 확인:

```powershell
Get-ChildItem -Recurse .\storage\detections |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 10
```

## FastAPI To Spring Boot TODO

백엔드 파일이 준비되면 아래 항목을 확정해야 합니다.

### 1. Spring Boot API 경로 확정

현재 임시값:

```text
POST /api/detections
```

확정 필요:

```text
- 실제 Controller 경로
- version prefix 사용 여부: /api/v1/...
- 단건 전송인지 batch 전송인지
```

### 2. FastAPI -> Spring Boot Request Body 확정

현재 FastAPI 내부 mock 결과:

```json
{
  "cameraCode": "CAM_001",
  "plateNumber": "123가4567",
  "detectionType": "PLATE",
  "directionType": "IN",
  "confidenceScore": 0.9321,
  "imagePath": "storage/detections/2026/05/01/CAM_001_143632_frame.jpg",
  "detectedAt": "2026-05-01T14:36:32"
}
```

확정 필요:

```text
- cameraCode만 보낼지 zoneCode도 보낼지
- directionType을 FastAPI가 보낼지 Spring Boot가 cameraCode 기준으로 판단할지
- plateNumber null 허용 여부
- imagePath가 로컬 경로인지 정적 URL인지
- detectedAt 포맷
- 단일 객체 전송인지 detections 배열 전송인지
```

### 3. Spring Boot Response Body 확정

권장 응답 예시:

```json
{
  "accepted": true,
  "receivedCount": 1,
  "createdLogCount": 1,
  "createdFlowEventCount": 1
}
```

확정 필요:

```text
- 성공 응답 필드
- validation 실패 응답
- 중복 감지 처리 결과를 응답에 포함할지 여부
```

### 4. Error Handling Contract

FastAPI에서 이미 처리 중인 오류:

```text
- imageBase64 must be valid image base64
- image must be jpeg or png
- image must be a valid jpg or png
- Spring Boot API is not reachable
- Spring Boot API returned error: {status_code}
```

백엔드 연동 후 확인 필요:

```text
- 400 validation error 형식
- 404 cameraCode not found 처리
- 409 duplicate 관련 응답 여부
- 500 backend error 처리
```

### 5. Image Path Access Policy

현재:

```text
FastAPI가 이미지를 storage/detections 하위에 저장하고 imagePath를 응답에 포함
```

확정 필요:

```text
- Spring Boot/Vue가 해당 imagePath에 접근해야 하는지
- FastAPI에서 정적 파일로 serving할지
- 파일 서버/NAS/S3 같은 외부 저장소를 사용할지
- imagePath 대신 imageUrl을 내려줄지
```

### 6. Direction Decision Owner

현재 mock:

```text
directionType = IN 고정
```

권장:

```text
Spring Boot가 cameraCode를 기준으로 cameras.direction_type을 조회해 IN/OUT 최종 판단
```

확정 필요:

```text
- FastAPI가 directionType을 계속 보낼지
- Spring Boot가 directionType을 무시하고 cameraCode 기준으로 판단할지
```

### 7. Duplicate Handling

팀 결정:

```text
중복 기준 시간은 10초로 시작
```

백엔드에서 확정 필요:

```text
- 동일 번호판 + 동일 카메라 기준인지
- 동일 번호판 + 동일 구역 기준인지
- 동일 방향 조건 포함 여부
- detection_logs에는 저장하고 vehicle_flow_events만 생성하지 않는 방식 유지
```

## YOLO/OCR TODO

현재는 mock detector/mock recognizer로 동작합니다.

### PlateDetector

해야 할 일:

```text
- MODEL_PATH 설정값을 사용해 YOLO 모델 로드
- 입력 이미지에서 차량 또는 번호판 영역 탐지
- 여러 탐지 결과 중 confidence가 가장 높은 번호판 탐지 결과 우선 사용
- 번호판 crop 저장을 위해 bbox 좌표 유지
```

### PlateRecognizer

해야 할 일:

```text
- detector bbox가 있으면 해당 영역을 번호판 이미지로 crop
- OCR 모델 실행
- 한글 번호판 문자열의 공백, 특수문자, 오인식 문자 정규화
- OCR confidence가 낮거나 읽을 수 없는 경우 plateNumber를 null로 처리
```

### InferenceService

해야 할 일:

```text
- mock detector와 mock recognizer를 실제 YOLO/OCR 서비스로 교체
- API 라우터가 모델 세부 구현에 의존하지 않도록 DetectionResult 구조 유지
- DETECTION_CONFIDENCE_THRESHOLD 설정값 적용
- OCR 실패 시 detectionType/plateNumber 정책 반영
```

## Work To Pause For 2 Days

이틀간 외부 PC에서 작업하는 동안 라즈베리파이 실기 작업은 보류합니다.

보류 항목:

```text
- Raspberry Pi camera live upload 추가 실험
- Raspberry Pi systemd 자동 실행
- Raspberry Pi 장시간 안정성 테스트
- 실제 현장 카메라 위치 조정
```

외부 PC에서 진행할 수 있는 항목:

```text
- FastAPI 코드 정리
- README 정리
- tests 보강
- Spring Boot 연동 계약 초안 정리
- YOLO/OCR 연결 지점 설계
- .env.example 작성
- GitHub 업로드 전 .gitignore 확인
```

## GitHub Before Upload Checklist

```text
- .venv 제외
- .env 제외
- storage/ 제외
- __pycache__/ 제외
- .pytest_cache/ 제외
- 실제 캡처 이미지 제외
- sample.jpg 제외 또는 scripts/create_sample_image.py로 재생성 가능하게 처리
- README/HANDOFF 문서 포함
- requirements.txt 포함
- tests 포함
```

추천 `.gitignore` 항목:

```gitignore
fastapi-server/.venv/
fastapi-server/.env
fastapi-server/storage/
fastapi-server/samples/*.jpg
fastapi-server/samples/*.png
fastapi-server/sample.jpg
fastapi-server/.pytest_cache/
fastapi-server/**/__pycache__/
```

