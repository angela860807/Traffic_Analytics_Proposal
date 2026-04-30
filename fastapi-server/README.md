# Traffic AI Server

차량 흐름 분석 시스템의 FastAPI AI 서버입니다.

현재 단계에서는 실제 YOLO/OCR 모델을 연결하기 전 단계이며, mock detection API로 Rasberry Pi 입력과 Spring Boot 전송 흐름을 검증합니다.

## 역할

- Rasberry Pi 또는 카메라 클라이언트로부터 이미지 프레임 수신
- YOLO/OCR 추론 결과 생성
- 감지 결과를 Spring Boot Backend로 JSON형태로 전송
- 모델 상태 및 서버 상태 확인 API 제공

## 현재 팀 합의

- Raspberry Pi는 추론하지 않고 카메라 프레임 수집/전송만 담당한다.
- FastAPI 서버 PC에서 YOLO/OCR 추론을 수행한다.
- 초기 테스트 입력은 base64 JSON으로 진행한다.
- 최종 목표 입력 방식은 multipart/form-data 이미지 업로드이다.
- cameraCode는 CAM_001, CAM_002 형식을 사용한다.
- zoneCode는 ZONE_001, ZONE_002 형식을 사용한다.
- directionType은 IN, OUT, BOTH를 사용한다.
- detectionType은 VEHICLE, PLATE를 사용한다.
- confidenceScore 기준값은 0.7로 시작한다.
- 이미지는 FastAPI 서버가 저장한다.
- 번호판 인식 실패 시 plateNumber는 null로 둔다.
- UNKNOWN 문자열은 사용하지 않는다.
- 대시보드는 vehicle_flow_events 기준으로 통계를 보여준다.

## 실행

1. 가상화 활성화
2. pip install -r requirements.txt
3. python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000