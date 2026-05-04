# FastAPI Next Handoff

작성일: 2026-05-04

## 현재 결론

FastAPI 파트는 백엔드와 YOLO/OCR 파일 없이 진행 가능한 준비 작업을 완료했습니다.

현재 더 진행하려면 아래 두 가지가 필요합니다.

```text
1. Spring Boot 백엔드 Controller/DTO/API 계약
2. 실제 YOLO/OCR 모델 파일 및 추론 방식
```

따라서 다음 작업자는 이 문서를 기준으로 현재 상태를 확인하고, 백엔드 또는 모델 파일이 준비되면 연동 작업을 이어가면 됩니다.

## 완료된 범위

```text
- FastAPI 기본 서버 구성
- /health API 구성
- base64 JSON mock detection API 구성
- multipart/form-data image detection API 구성
- Raspberry Pi -> FastAPI 이미지 업로드 검증
- Raspberry Pi live preview API 구성 및 검증
- 이미지 저장 경로 생성
- imagePath + imageUrl 응답 정책 결정 및 반영
- /static/detections 정적 이미지 접근 검증
- mock inference 서비스 구조 구성
- 테스트 코드 작성
- pytest 7개 통과
- README.md 정리
- HANDOFF_FASTAPI_TODO.md 정리
- .env.example 추가
- .gitignore 정리
```

## 현재 주요 API

### Health Check

```text
GET /health
```

### Base64 Mock Detection

```text
POST /api/detections/mock
Content-Type: application/json
```

### Multipart Image Detection

```text
POST /api/detections/image
Content-Type: multipart/form-data
```

### Raspberry Pi Live Preview

```text
POST /api/camera/frame
GET  /api/camera/latest.jpg
GET  /api/camera/live
```

## 현재 응답 정책

FastAPI detection 응답은 아래 형태를 기준으로 합니다.

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
    "imagePath": "storage/detections/2026/05/04/CAM_001_103000_frame.jpg",
    "imageUrl": "/static/detections/2026/05/04/CAM_001_103000_frame.jpg",
    "detectedAt": "2026-05-04T10:30:00"
  }
}
```

정책 의미:

```text
imagePath:
  FastAPI 서버 내부 저장 경로.
  DB 저장/추적용으로 사용.

imageUrl:
  Vue 또는 브라우저 표시용 URL.
  FastAPI의 /static/detections 경로로 접근 가능.
```

## directionType 정책

백엔드 `Camera.java` 확인 결과, `Camera` 엔티티에 `Direction directionType` 필드가 있습니다.

따라서 최종 IN/OUT 판단은 아래 방향으로 정리했습니다.

```text
FastAPI:
  이미지 탐지, OCR, confidence, imagePath/imageUrl 생성 담당.

Spring Boot:
  cameraCode 기준으로 Camera.directionType 조회.
  최종 IN/OUT 판단.
  detection_logs / vehicle_flow_events 저장.
```

현재 FastAPI mock 응답의 `directionType="IN"`은 임시값입니다.

## 실행 방법

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server

.\.venv\Scripts\Activate.ps1

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Raspberry Pi에서 접근해야 하는 경우:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 검증 명령어

```powershell
python -m compileall app
python -m pytest
```

현재 기준:

```text
compileall 성공
pytest 7 passed
```

## 다음 작업 1: Spring Boot 연동

백엔드 파일을 받으면 아래 순서로 확인합니다.

```text
1. Spring Boot 감지 결과 수신 Controller 경로 확인
2. Request DTO 필드 확인
3. Response DTO 필드 확인
4. FastAPI backend_client.py의 SPRING_DETECTION_PATH 조정
5. FastAPI -> Spring Boot payload 필드명 조정
6. /api/detections/mock/send 테스트
7. Spring Boot DB 저장 여부 확인
```

확정해야 할 항목:

```text
- API 경로
- 요청 필드명
- 응답 필드명
- imagePath/imageUrl 저장 여부
- plateNumber null 허용 여부
- directionType 처리 방식
- 단건 전송인지 배열 전송인지
```

## 다음 작업 2: YOLO/OCR 연결

모델 파일 또는 모델 방식이 확정되면 아래 순서로 진행합니다.

```text
1. MODEL_PATH 설정
2. PlateDetector에 YOLO 모델 로딩 추가
3. 차량/번호판 bbox 추출
4. PlateRecognizer에 OCR 연결
5. OCR 결과 정규화
6. confidence threshold 적용
7. OCR 실패 시 plateNumber null 처리
8. 번호판 crop 저장 정책 반영
9. 기존 mock 테스트와 별도 모델 테스트 추가
```

현재 모델 연결 예정 파일:

```text
app/services/plate_detector.py
app/services/plate_recognizer.py
app/services/inference_service.py
```

## 다음 작업 3: 번호판 crop 정책

아직 미확정입니다.

확정 필요:

```text
- 원본 프레임만 저장할지
- 번호판 crop도 저장할지
- 차량 crop도 저장할지
- Vue 대시보드에서 어떤 이미지를 보여줄지
```

추천 방향:

```text
1차:
  원본 프레임 저장 유지

2차:
  YOLO bbox 확보 후 번호판 crop 저장 추가

후순위:
  차량 crop 저장
```

## GitHub 업로드 주의

올리지 않을 것:

```text
.venv/
.env
storage/
__pycache__/
.pytest_cache/
실제 캡처 이미지
sample.jpg
개인 IP가 박힌 라즈베리파이 실행 파일
```

올릴 것:

```text
app/
tests/
examples/
scripts/
samples/README.md
README.md
HANDOFF_FASTAPI_TODO.md
NEXT_HANDOFF.md
.env.example
requirements.txt
```

## 이어받는 사람에게

백엔드와 YOLO/OCR이 아직 없으면 FastAPI 쪽 추가 구현은 크게 필요하지 않습니다.

지금은 아래 작업만 유지하면 됩니다.

```text
- 테스트 통과 유지
- README 최신화
- 백엔드 DTO/API 계약 나오면 backend_client.py와 schema 조정
- 모델 파일 나오면 detector/recognizer 구현
```

