# Traffic AI Server

차량 흐름 분석 시스템의 FastAPI AI 서버입니다.

현재 단계에서는 실제 YOLO/OCR 모델을 연결하기 전 단계이며, mock detection API로 Rasberry Pi 입력과 Spring Boot 전송 흐름을 검증합니다.

## 역할

- Rasberry Pi 또는 카메라 클라이언트로부터 이미지 프레임 수신
- YOLO/OCR 추론 결과 생성
- 감지 결과를 Spring Boot Backend로 JSON형태로 전송
- 모델 상태 및 서버 상태 확인 API 제공

## 실행 방법
```
가상화 설정(venv) 후 activate(가상화 모드로 전환)한 다음,

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```