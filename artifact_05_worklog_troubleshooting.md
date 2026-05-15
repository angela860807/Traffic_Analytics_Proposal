# 5번 산출물

## 작업 요약

### 1. 1차 병합 이후 Raspberry Pi 연동 방향 정리

- 인수인계 문서 `HANDOFF_RASPBERRY_PI.md`를 확인했다.
- 현재 전체 구조는 `Raspberry Pi -> FastAPI(:8000) -> Spring Boot(:8080) -> PostgreSQL` 흐름으로 정리했다.
- Vue는 `/api`를 Spring으로, `/static`과 `/ws`를 FastAPI로 프록시하는 구조로 파악했다.
- Raspberry Pi의 1차 목표는 실제 카메라 프레임을 Windows PC의 FastAPI 서버로 전송하는 것으로 정리했다.
- PC LAN IP는 `192.168.10.91`로 확인했다.
- PC에서 `http://192.168.10.91:8000/docs` 접근이 `200 OK`로 확인되어 FastAPI 외부 포트 노출은 정상으로 판단했다.

### 2. FastAPI 수신/저장 흐름 점검

- FastAPI 수신 prefix는 `/api/detections`로 확인했다.
- 주요 API를 다음처럼 분리했다.
  - 분석만 수행: `POST /api/detections/image`
  - 분석 후 Spring 전송 및 DB 저장: `POST /api/detections/image/send`
  - base64 mock 전송: `POST /api/detections/mock/send`
  - live preview 프레임 수신: `POST /api/camera/frame`
- multipart 이미지 업로드 형식은 `cameraCode`, `capturedAt`, `image` 필드를 사용한다.
- FastAPI는 이미지를 저장하고 `imagePath`, `imageUrl`을 생성한 뒤 Spring으로 JSON payload를 전송한다.
- Spring 내부 전송에는 `X-Internal-Api-Key` 헤더를 사용한다.

### 3. FastAPI 안정화 수정

- `/api/detections/image/send`에 이미지 MIME type 검증을 추가했다.
- `/api/detections/image/send`에 Spring 전송 실패 예외 처리를 추가했다.
  - 잘못된 이미지: `400`
  - Spring HTTP 오류: `502`
  - Spring 연결 실패: `503`
  - 내부 런타임 오류: `500`
- `backend_client.py`의 헤더 오타를 `Content_Type`에서 `Content-Type`으로 수정했다.
- OCR 번호판 정규식이 한글 번호판을 유지하도록 정리했다.
- mock 번호판 예시는 `123가4567` 기준으로 맞췄다.
- Docker 재빌드 후 multipart POST로 FastAPI -> Spring -> PostgreSQL 저장 흐름을 확인했다.
- DB 저장 확인 시 실제 컬럼명은 `log_id`가 아니라 `detection_log_id`임을 확인했다.

### 4. `data.sql` 처리

- Spring `backend/traffic/src/main/resources/data.sql`은 팀 기준 파일이라 직접 수정하지 않기로 했다.
- 깨진 기본 사용자 이름을 수정하는 내용은 별도 참고 SQL로 분리했다.
- 별도 파일: `data_sql_utf8_reference.sql`
- 참고 SQL 내용은 다음 목적이다.
  - `user1@email.com`의 이름을 `이용자`로 수정
  - `admin@email.com`의 이름을 `관리자`로 수정

### 5. Raspberry Pi 디렉토리 정리

- Raspberry Pi 파일은 프로젝트 루트의 `raspberry-pi/` 디렉토리에 두는 것으로 정리했다.
- 기존 오타 `rasberry`를 `raspberry`로 일괄 정리했다.
- `fastapi-server/examples`의 예제 파일명도 다음처럼 수정했다.
  - `rasberry_pi_base64_client.py` -> `raspberry_pi_base64_client.py`
  - `rasberry_pi_multipart_client.py` -> `raspberry_pi_multipart_client.py`
- `fastapi-server/README.md` 안의 `Rasberry` / `rasberry` 문구를 모두 `Raspberry` / `raspberry`로 수정했다.

### 6. Raspberry Pi 클라이언트 구조 개선

- `raspberry-pi/config.py`를 추가해 공통 설정을 분리했다.
  - `FASTAPI_BASE_URL`
  - `CAMERA_CODE`
  - `REQUEST_TIMEOUT_SECONDS`
  - `CAPTURE_INTERVAL_SECONDS`
  - `LIVE_FRAME_INTERVAL_SECONDS`
  - `JPEG_QUALITY`
  - `CAMERA_WIDTH`
  - `CAMERA_HEIGHT`
- `raspberry-pi/fastapi_client.py`를 통해 FastAPI 업로드 로직을 공통화했다.
- DB 저장용 업로드는 `/api/detections/image/send`를 사용하도록 정리했다.
- live preview용 업로드는 `/api/camera/frame`을 유지했다.
- `camera_upload.py`, `camera_upload_loop.py`, `upload_sample_image.py`는 DB 저장 endpoint를 사용하도록 맞췄다.
- `camera_live_upload.py`는 preview endpoint를 사용하도록 유지했다.
- `camera_capture_test.py`와 `camera_upload.py`는 예외가 발생해도 `picam2.stop()`이 실행되도록 `try/finally`를 적용했다.
- `fastapi_client.py`의 `datetime | None` 타입 표기를 `Optional[datetime]`으로 바꿔 Python 3.9 환경에서도 실행 가능하게 했다.

### 7. Raspberry Pi 실행 환경 정리

- WinSCP는 파일 복사용, VSCode Remote SSH는 Raspberry Pi 내부 실행용으로 정리했다.
- Raspberry Pi에서 무거운 pip OpenCV 설치를 피하기 위해 `opencv-python`을 `requirements.txt`에서 제거했다.
- `requirements.txt`에는 가벼운 Python 의존성만 남겼다.
  - `requests`
  - `python-dotenv`
- `picamera2`와 `cv2`는 Raspberry Pi OS의 apt 패키지로 설치하는 방식으로 정리했다.
- 권장 venv 생성 방식은 다음과 같다.

```bash
python -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

- `--system-site-packages`를 사용하는 이유는 apt로 설치한 `python3-picamera2`, `python3-opencv`를 venv 안에서도 인식시키기 위해서다.

### 8. Raspberry Pi 테스트 범위 정리

- YOLO/OCR 모델이 오기 전까지 가능한 테스트 범위는 다음으로 정리했다.
  - Raspberry Pi 카메라 작동 확인
  - 카메라 프레임 캡처 확인
  - 캡처 이미지를 FastAPI로 multipart POST
  - FastAPI mock 결과 생성
  - Spring Boot 전송
  - PostgreSQL `detection_logs` 저장 확인
  - Vue dashboard 조회 확인
- YOLO/OCR 모델이 오기 전에는 실제 번호판 검출, 실제 OCR 인식, 실제 confidence 반영은 할 수 없다.

### 9. FastAPI worklog 검토

- `FastAPI_worklog_2026-05-11.docx` 내용을 확인했다.
- worklog 기준 FastAPI 작업 내용은 다음과 같았다.
  - Spring 전송 기본 경로를 `/api/v1/detection-logs`로 정리
  - Spring 오류 body 일부를 FastAPI 502 detail과 warning log에 포함
  - FastAPI 중복 제거는 보조 로직이고 최종 기준은 Spring/DB라는 책임 범위 명시
  - OCR 번호판 정규화 테스트 추가
- 현재 코드와 대조한 결과 FastAPI 단위 테스트는 `17 passed`로 확인했다.
- `python -m compileall app tests`도 성공했다.
- FastAPI 쪽 2차 병합 전 필수 추가 구현은 거의 완료된 상태로 판단했다.
- 다만 Docker Desktop API 오류 때문에 당시 컨테이너 실검증은 제한이 있었다.

### 10. FastAPI README 정리

- `fastapi-server/README.md`의 예전 Spring path 예시를 현재 코드 기준으로 수정했다.
  - 기존: `/api/detections`
  - 현재: `/api/v1/detection-logs`
- YOLO/OCR 관련 환경변수 예시를 README에 추가했다.
- mock inference 단계에서는 번호판이 `123가4567`로 고정되므로, `DUPLICATE_WINDOW_SECONDS` 안에서 반복 요청하면 Spring 전송이 생략될 수 있다는 주의사항을 추가했다.

## 트러블 슈팅 로그

### 1. PowerShell 출력 인코딩 깨짐

- 증상:
  - `HANDOFF_RASPBERRY_PI.md`, Java 파일, SQL 파일 출력에서 한글이 깨져 보였다.
- 원인:
  - PowerShell 기본 출력 인코딩과 파일 UTF-8 인코딩 표시가 맞지 않아 콘솔에서 깨져 보였다.
- 대응:
  - `Get-Content -Encoding UTF8`로 다시 확인했다.
  - 실제 파일 내용과 콘솔 표시를 구분해서 판단했다.
- 결과:
  - 인수인계 문서의 핵심 내용은 정상적으로 파악했다.

### 2. `rg --files` 실행 실패

- 증상:
  - `rg --files` 실행 시 `Access is denied`가 발생했다.
- 원인:
  - 로컬 환경에서 `rg.exe` 실행 권한 문제가 있었다.
- 대응:
  - PowerShell `Get-ChildItem -Recurse` 기반으로 대체 검색했다.
  - 큰 디렉토리 검색 시 `.venv`, `build`, `storage`, `node_modules` 등을 제외했다.
- 결과:
  - 프로젝트 파일 구조와 필요한 파일을 확인했다.

### 3. 전체 재귀 검색 타임아웃

- 증상:
  - 프로젝트 전체에서 `rasberry` 검색 시 타임아웃이 발생했다.
- 원인:
  - `.venv`, build 산출물, storage 등 대량 파일이 포함되어 검색 범위가 너무 컸다.
- 대응:
  - 검색 제외 디렉토리를 명시했다.
  - `raspberry-pi`, `fastapi-server`, `backend`, `trafficAS-b` 등 주요 경로 중심으로 나눠 검색했다.
- 결과:
  - `rasberry` 오타가 남은 파일명과 README 내용을 찾아 수정했다.

### 4. `data.sql` 수정 권한 문제

- 증상:
  - Spring `data.sql`의 깨진 한글 사용자명을 수정했으나, 해당 파일은 사용자가 수정하면 안 되는 팀 기준 파일이었다.
- 대응:
  - `data.sql`은 원래 상태로 되돌렸다.
  - 수정 SQL은 별도 참고 파일 `data_sql_utf8_reference.sql`로 분리했다.
- 결과:
  - 팀 기준 파일을 건드리지 않고, 필요 시 사용할 수 있는 참고 SQL만 남겼다.

### 5. DB 확인 쿼리 컬럼명 오류

- 증상:
  - `select log_id ... from detection_logs` 실행 시 `column "log_id" does not exist` 오류가 발생했다.
- 원인:
  - 실제 DB 컬럼명은 `log_id`가 아니라 `detection_log_id`였다.
- 대응:
  - `\d detection_logs`로 실제 테이블 구조를 확인했다.
  - DB 확인 쿼리를 `detection_log_id` 기준으로 변경했다.
- 결과:
  - 최신 detection log가 정상 조회되었다.

### 6. FastAPI multipart DB 저장 확인

- 증상:
  - Raspberry Pi 연동 전 실제 multipart 요청이 DB까지 저장되는지 확인이 필요했다.
- 대응:
  - 기존 저장 이미지 파일을 이용해 PC에서 `curl.exe`로 `/api/detections/image/send` 요청을 보냈다.
  - 응답에서 `accepted: true`, `message: Detection result sent to backend`를 확인했다.
  - PostgreSQL에서 `detection_logs` 최신 row를 확인했다.
- 결과:
  - `plate_number = 123가4567`, `image_path`, `image_url`, `confidence_score = 0.9321` 저장을 확인했다.

### 7. FastAPI 정적 이미지 확인 방법

- 질문:
  - 터미널에는 성공이라고 나오는데 FastAPI에서 저장 결과를 어떻게 확인하는지 문의했다.
- 답변:
  - 응답 JSON의 `imageUrl`을 PC 브라우저에서 열어 확인한다.
  - 예: `http://192.168.10.91:8000/static/detections/...jpg`
  - Windows 저장 폴더 `fastapi-server/storage/detections`에서도 확인할 수 있다.
  - 목록 조회는 FastAPI가 아니라 Spring `/api/v1/detection-logs` 역할이라고 정리했다.

### 8. Raspberry Pi Python 버전 호환성

- 증상:
  - `datetime | None` 타입 힌트는 Python 3.10 이상에서만 안전하다.
  - Raspberry Pi OS가 Python 3.9일 가능성을 고려해야 했다.
- 대응:
  - `typing.Optional`을 사용하도록 변경했다.
- 결과:
  - Python 3.9 환경에서도 실행 가능한 코드가 되었다.

### 9. Raspberry Pi 카메라 자원 정리

- 증상:
  - 단발 캡처 중 예외가 발생하면 `picam2.stop()`이 실행되지 않을 가능성이 있었다.
- 대응:
  - `camera_capture_test.py`, `camera_upload.py`에 `try/finally`를 적용했다.
- 결과:
  - 예외 발생 시에도 카메라 자원을 정리할 수 있게 되었다.

### 10. Raspberry Pi OpenCV 설치 부담

- 질문:
  - VSCode Remote SSH와 WinSCP를 사용하므로 Raspberry Pi 세팅이 너무 무거운지 문의했다.
- 판단:
  - `opencv-python`을 pip로 설치하는 것은 Raspberry Pi에서 무겁거나 꼬일 수 있다.
  - apt 패키지 `python3-opencv`를 쓰고 venv는 `--system-site-packages`로 만드는 방식이 더 가볍다.
- 대응:
  - `requirements.txt`에서 `opencv-python`을 제거했다.
  - README 설치 안내를 `python3-picamera2 python3-opencv` apt 설치 방식으로 정리했다.
- 결과:
  - pip 의존성은 `requests`, `python-dotenv`만 남아 가벼운 세팅이 되었다.

### 11. FastAPI 중복 제거로 인한 DB row 미증가 가능성

- 증상:
  - mock inference 단계에서는 번호판이 `123가4567`로 고정되어 반복 테스트 시 DB row가 매번 늘지 않을 수 있다.
- 원인:
  - FastAPI `DuplicateDetectionGuard`가 `cameraCode + plateNumber` 기준으로 window 안의 중복 전송을 생략한다.
- 대응:
  - README에 병합 테스트 주의사항을 추가했다.
  - DB row 증가를 매 요청마다 확인하려면 테스트 중 `DUPLICATE_WINDOW_SECONDS=0` 또는 충분한 요청 간격을 사용하도록 정리했다.
- 결과:
  - 중복 제거 정상 동작과 저장 실패를 구분할 수 있게 되었다.

### 12. Docker Desktop API 오류

- 증상:
  - `docker ps`, `docker exec` 등 일부 Docker 명령에서 Docker Desktop API 500 오류가 발생했다.
- 원인:
  - Docker Desktop 내부 API 상태 문제로 추정했다.
- 대응:
  - FastAPI 단위 테스트와 compileall로 코드 상태를 먼저 검증했다.
  - 컨테이너 기반 실검증은 Docker Desktop 재시작 후 다시 확인해야 하는 항목으로 남겼다.
- 결과:
  - 코드 단위 검증은 통과했지만, 당시 Docker 컨테이너 실검증은 제한되었다.

## 현재 기준 권장 테스트 순서

### PC

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal
docker compose up -d --build
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-WebRequest http://192.168.10.91:8000/docs -Method Head -UseBasicParsing
```

### Raspberry Pi

```bash
cd /home/pi/<project-folder>

sudo apt update
sudo apt install -y python3-picamera2 python3-opencv

python -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt

python health_check.py
python camera_capture_test.py
python camera_upload.py
```

### DB 확인

```powershell
docker exec traffic-postgres psql -U postgres -d traffic -c "select detection_log_id, plate_number, camera_id, image_path, image_url, confidence_score, detected_at from detection_logs order by detection_log_id desc limit 5;"
```

## 2차 병합 전 체크리스트

- FastAPI 단위 테스트 `17 passed` 유지
- `python -m compileall app tests` 성공 유지
- Docker 재빌드 후 `/api/detections/image/send` 실제 저장 재검증
- Spring DB 스키마에 `status`, `preprocessed_path` 또는 대응 컬럼 반영 여부 확인
- Raspberry Pi에서 `health_check.py` 성공 확인
- Raspberry Pi에서 `camera_capture_test.py`로 `capture.jpg` 생성 확인
- Raspberry Pi에서 `camera_upload.py` 실행 후 DB row 생성 확인
- mock inference 중복 방지 설정 때문에 반복 요청이 생략되는지 확인
- YOLO/OCR 모델 수령 후 `MODEL_PATH` 설정 및 `scripts/verify_yolo_ocr.py` 실행
