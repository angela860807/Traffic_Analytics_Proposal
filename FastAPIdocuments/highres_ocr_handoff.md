# Artifact 12 - High-Resolution OCR Handoff

작성일: 2026-05-21

## 1. 배경

현재 `stream_video_file.py`는 `--upload-scale`로 축소한 프레임을 FastAPI에 업로드한다. 서버는 이 축소된 이미지를 기준으로 차량 탐지, 번호판 crop, OCR, best frame 저장을 수행한다.

문제는 `--upload-scale`을 낮추면 노트북과 서버 처리 부담은 줄지만, 번호판 OCR 품질과 저장 이미지 품질도 같이 떨어진다는 점이다. 한 번 축소된 이미지는 서버에서 원본 화질로 복구할 수 없다.

다음 컨텍스트의 목표는 **탐지/추적은 저화질로 유지하면서, OCR 또는 best frame 저장 순간만 원본 화질을 활용하는 구조**를 추가하는 것이다.

## 2. 목표 구조

```text
low-res frame   -> YOLO 차량 탐지 / tracking / speed 계산
high-res crop   -> 번호판 OCR / best frame 저장
```

핵심 아이디어:

- 매 프레임 전체 원본을 보내지 않는다.
- 기존처럼 저화질 프레임으로 차량 탐지와 속도 추적을 유지한다.
- bbox가 잡힌 프레임 또는 best candidate 순간에만 원본 프레임 기준 crop을 추가로 보낸다.
- 서버는 저화질 bbox 좌표를 원본 좌표로 환산해서 OCR 품질을 높인다.

## 3. 추천 구현 방향

### 1순위: 원본 crop 추가 업로드

가장 추천하는 방식이다.

클라이언트 `stream_video_file.py`가 원본 프레임을 보관하고 있다가, 저화질 응답에서 bbox가 잡히면 원본 프레임에서 해당 영역을 crop해 추가 전송한다.

장점:

- 원본 전체 프레임을 보내는 것보다 전송량이 작다.
- OCR에 필요한 번호판/차량 영역만 고화질로 확보할 수 있다.
- 노트북 부담을 비교적 낮게 유지한다.

단점:

- bbox 좌표 스케일 환산이 정확해야 한다.
- 서버 API에 high-res crop 필드 또는 별도 endpoint가 필요하다.

### 2순위: 원본 frame 선택 업로드

bbox가 안정적인 프레임에서만 원본 전체 frame을 같이 보낸다.

장점:

- 구현이 단순하다.
- 서버가 원본 frame에서 자유롭게 crop을 다시 할 수 있다.

단점:

- 전송량이 크다.
- 노트북/네트워크 부담이 커질 수 있다.

## 4. 구현 제안

### A. 클라이언트 옵션 추가

대상 파일:

- `fastapi-server/scripts/stream_video_file.py`

추가 옵션 예시:

```powershell
--highres-ocr-crop `
--highres-crop-padding 0.25 `
--highres-jpeg-quality 85
```

옵션 의미:

- `--highres-ocr-crop`: bbox가 잡힌 프레임에서 원본 crop을 함께 전송한다.
- `--highres-crop-padding`: bbox 주변 여백 비율. 번호판이 bbox 경계 근처에 있을 수 있으므로 여백을 둔다.
- `--highres-jpeg-quality`: 고화질 crop JPEG 품질.

### B. 좌표 환산

현재 서버로 보내는 이미지는 `upload_scale`이 적용된 이미지다. 원본 좌표 환산은 다음 규칙을 쓴다.

```text
original_x = uploaded_x / upload_scale
original_y = uploaded_y / upload_scale
```

예:

```text
upload_scale = 0.50
low-res bbox = [100, 80, 300, 220]
original bbox = [200, 160, 600, 440]
```

crop에는 padding을 적용한다.

```text
padding_x = bbox_width * highres_crop_padding
padding_y = bbox_height * highres_crop_padding
```

프레임 경계를 넘지 않도록 clamp해야 한다.

### C. FastAPI endpoint 확장

대상 파일:

- `fastapi-server/app/api/routes/detection.py`

현재 `/api/detections/stream-frame`는 `image` multipart 필드를 받는다. 여기에 선택 필드를 추가하는 방식이 가장 단순하다.

추가 form/file 후보:

```text
image: 기존 저화질 프레임
highResCrop: 선택, 원본 기준 crop JPEG
highResCropScale: 선택, 원본 crop이 어떤 scale 기준인지 기록
highResCropBbox: 선택, 원본 좌표 bbox
```

권장:

- 첫 구현은 `highResCrop`만 추가한다.
- crop 좌표는 저장 메타데이터에 필요할 때만 추가한다.

### D. OCR 입력 우선순위

대상 파일 후보:

- `fastapi-server/app/services/stream_event_service.py`
- `fastapi-server/app/services/plate_detector.py`
- `fastapi-server/app/services/plate_recognizer.py`
- `fastapi-server/app/services/image_storage_service.py`

정책:

1. `highResCrop`이 있으면 OCR 후보 이미지로 우선 사용한다.
2. 없으면 기존 저화질 frame/crop 방식으로 fallback한다.
3. 저장 이미지도 high-res crop이 있으면 해당 이미지를 우선 저장한다.

주의:

- 차량 bbox crop과 번호판 crop은 다르다.
- 첫 구현은 "차량 bbox 주변 원본 crop"을 보내고, 서버의 plate detector가 그 안에서 번호판을 다시 찾는 방식이 안정적이다.
- 만약 클라이언트에서 번호판 crop까지 하려면 plate bbox가 필요하므로 구현 난도가 올라간다.

## 5. 기존 기능과의 관계

### upload-scale

`--upload-scale`은 계속 유지한다.

역할:

- 저화질 탐지/추적 프레임 크기 결정
- speed tracker 좌표 기준 결정

### preview scale

`--scale`은 GUI 표시용이다. OCR 품질과 직접 관련 없다.

### speed tracking

speed tracking은 계속 저화질 좌표 기준으로 동작한다. homography/ROI 설정도 현재 upload-scaled 좌표 기준을 유지한다.

### high-res crop

high-res crop은 OCR과 저장 이미지 품질 개선용이다. 속도 계산에는 사용하지 않는다.

## 6. 테스트 계획

### 1차 테스트: 기능 연결

목표:

- 기존 저화질 프레임 업로드가 깨지지 않는다.
- `--highres-ocr-crop` 옵션을 켰을 때 multipart에 crop이 포함된다.
- FastAPI가 선택 필드를 받아도 기존 응답 스키마가 유지된다.

검증:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_detection_api.py -q
```

### 2차 테스트: OCR 품질 비교

같은 영상 구간에서 두 번 실행한다.

기존 방식:

```powershell
.\.venv\Scripts\python.exe scripts\stream_video_file.py `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --fps 2 `
  --upload-scale 0.50 `
  --jpeg-quality 60 `
  --scale 0.22 `
  --preview-bbox `
  --realtime
```

고화질 crop 방식:

```powershell
.\.venv\Scripts\python.exe scripts\stream_video_file.py `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --fps 2 `
  --upload-scale 0.50 `
  --jpeg-quality 60 `
  --scale 0.22 `
  --preview-bbox `
  --realtime `
  --highres-ocr-crop `
  --highres-jpeg-quality 85
```

비교 항목:

- OCR plateNumber 정확도
- `plate_crop.jpg` 선명도
- `ocr.jpg` 선명도
- frame upload latency
- CPU 사용량
- FastAPI 응답 지연

## 7. 예상 Troubleshooting

### 1. high-res crop을 켰는데 OCR이 그대로 나쁨

가능 원인:

- 차량 bbox crop이 너무 넓어 번호판이 여전히 작다.
- padding이 너무 크다.
- 원본 영상 자체의 번호판 해상도가 낮다.
- plate detector가 crop 내부에서 번호판을 못 찾는다.

대응:

- `--highres-crop-padding`을 0.15~0.30 사이에서 조정한다.
- crop 저장 이미지를 직접 보고 번호판 크기를 확인한다.
- 필요하면 high-res vehicle crop 후 plate detector threshold를 별도 조정한다.

### 2. crop 위치가 어긋남

가능 원인:

- `upload_scale` 환산이 잘못됐다.
- bbox가 preview scale 좌표와 섞였다.
- response bbox 좌표 기준이 upload-scaled frame과 다르다.

대응:

- 좌표 환산은 반드시 `upload_scale` 기준으로만 한다.
- GUI 표시용 `--scale`은 OCR crop 계산에 사용하지 않는다.
- 디버그용으로 원본 crop bbox를 원본 frame에 그려 저장해 확인한다.

### 3. 속도가 갑자기 달라짐

가능 원인:

- high-res crop을 속도 계산 경로에 섞었다.

대응:

- speed tracker는 기존 저화질 frame/bbox 기준을 유지한다.
- high-res crop은 OCR/storage 전용으로만 사용한다.

### 4. 노트북이 더 느려짐

가능 원인:

- 원본 frame 전체를 너무 자주 인코딩했다.
- high-res crop 품질이 너무 높다.

대응:

- 원본 frame 전체 업로드 대신 crop만 보낸다.
- `--highres-jpeg-quality`를 75~85 사이로 둔다.
- high-res crop 전송 조건을 bbox confidence 또는 tracking 상태로 제한한다.

## 8. 다음 컨텍스트에서 바로 볼 파일

FastAPI:

- `fastapi-server/scripts/stream_video_file.py`
- `fastapi-server/app/api/routes/detection.py`
- `fastapi-server/app/services/stream_event_service.py`
- `fastapi-server/app/services/image_storage_service.py`
- `fastapi-server/app/services/plate_detector.py`
- `fastapi-server/app/services/plate_recognizer.py`
- `fastapi-server/tests/test_detection_api.py`

설정/샘플:

- `fastapi-server/samples/speed-config.cam001.json`
- `docker-compose.yml`
- `fastapi-server/.env.example`

문서:

- `FastAPIdocuments/과속탐지_최종복기_팀공유자료.md`
- `FastAPIdocuments/artifact_11_context_workflow_troubleshooting.md`

## 9. 완료 기준

다음 조건을 만족하면 high-res OCR 개선 1차 구현은 완료로 본다.

- `--highres-ocr-crop` 옵션이 추가된다.
- 옵션 off 상태에서 기존 동작이 유지된다.
- 옵션 on 상태에서 OCR/storage 경로가 high-res crop을 우선 사용한다.
- FastAPI 테스트가 통과한다.
- 동일 영상에서 기존 방식보다 plate crop 또는 OCR 이미지가 선명해진다.
- 테스트 후 DB 로그와 산출 이미지를 정리한다.
