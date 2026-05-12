# Raspberry Pi Client

Raspberry Pi는 카메라 프레임을 수집해서 Windows PC의 FastAPI 서버로 전송한다.
추론과 DB 저장은 PC 쪽 FastAPI/Spring Boot/PostgreSQL이 담당한다.

## 1. PC 서버 확인

현재 기본 PC FastAPI 주소:

```bash
http://192.168.10.91:8000
```

라즈베리파이에서 먼저 확인한다.

```bash
curl -I http://192.168.10.91:8000/docs
python health_check.py
```

PC IP가 바뀌면 환경변수로 덮어쓴다.

```bash
export FASTAPI_BASE_URL=http://<PC_LAN_IP>:8000
export CAMERA_CODE=CAM_001
```

## 2. 설치

```bash
python -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

`picamera2`와 `cv2`는 Raspberry Pi OS에서 apt 패키지로 설치한다.

```bash
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv
```

## 3. 실행 순서

샘플 이미지 생성:

```bash
python create_sample_image.py
```

샘플 이미지를 FastAPI로 보내고 Spring DB 저장까지 확인:

```bash
python upload_sample_image.py
```

카메라 단발 촬영 테스트:

```bash
python camera_capture_test.py
```

카메라 단발 촬영 후 DB 저장:

```bash
python camera_upload.py
```

5초마다 촬영 후 DB 저장:

```bash
python camera_upload_loop.py
```

live preview용 고빈도 프레임 전송:

```bash
python camera_live_upload.py
```

브라우저에서 확인:

```text
http://<PC_LAN_IP>:8000/api/camera/live
```

## 4. 업로드 대상

- DB 저장용: `POST /api/detections/image/send`
- 분석만 확인: `POST /api/detections/image`
- live preview 전용: `POST /api/camera/frame`

`.env`, `venv`, 캡처 이미지, 로그 파일은 Git에 올리지 않는다.
