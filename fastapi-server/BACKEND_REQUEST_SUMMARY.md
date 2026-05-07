# Backend 수정 요청 요약

## 목적

FastAPI AI 서버가 Spring Boot 백엔드로 감지 결과를 전송할 때 JWT 대신 서버 간 내부 API Key를 사용한다.

## 요청 API

```text
POST /api/v1/detection-logs
Header: X-Internal-Api-Key: <팀 내부 키>
Content-Type: application/json
```

## 요청 DTO

`cameraId` 대신 `cameraCode`를 받도록 수정한다.

```json
{
  "cameraCode": "CAM_001",
  "plateNumber": "123가4567",
  "confidenceScore": 0.98,
  "imagePath": "storage/detections/2026/05/07/CAM_001_113000_frame.jpg",
  "imageUrl": "/static/detections/2026/05/07/CAM_001_113000_frame.jpg",
  "detectedAt": "2026-05-07T11:30:00",
  "detectionType": "PLATE"
}
```

## 백엔드 처리 요청

- `X-Internal-Api-Key` 헤더를 검증한다.
- 헤더가 없으면 `401 Unauthorized`를 반환한다.
- 헤더 값이 틀리면 `403 Forbidden`을 반환한다.
- `/api/v1/detection-logs`는 JWT 인증 대상에서 제외하되, Internal API Key 검증으로 보호한다.
- `cameraCode`로 `Camera`를 조회한다.
- 조회한 `Camera.directionType` 기준으로 최종 `IN/OUT`을 판단한다.
- `detection_logs`에 감지 결과를 저장한다.
- 중복이 아니면 `vehicle_flow_events`에도 저장한다.
- `plateNumber`는 OCR 실패 시 `null`이 올 수 있으므로 허용 여부를 결정한다.
- `imagePath`는 저장/추적용 경로로 사용한다.
- `imageUrl`은 Vue 화면 표시용 URL로 저장할지 여부를 결정한다.

## enum / 값 규칙

```text
detectionType: VEHICLE 또는 PLATE
confidenceScore: 0.0 이상 1.0 이하
detectedAt: ISO-8601 형식, 예: 2026-05-07T11:30:00
cameraCode: CAM_001, CAM_002 형식
```
