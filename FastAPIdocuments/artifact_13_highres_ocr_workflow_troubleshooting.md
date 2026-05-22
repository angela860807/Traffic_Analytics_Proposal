# Artifact 13 - High-Resolution OCR Workflow & Troubleshooting

작성일: 2026-05-22

## 1. 문서 목적

이번 작업은 FastAPI 영상 스트리밍 경로에서 번호판 OCR 품질을 높이기 위해 `high-res crop`, 원본 영상 best frame 재캡쳐, OCR 전처리 ensemble을 순차적으로 적용하고, 이후 GUI가 멈춘 TOP-N voting 시도를 철회한 과정을 정리한 것이다.

최종 기준은 다음과 같다.

- 차량 탐지, bbox 표시, 속도 계산은 기존 저화질 업로드 프레임 기준을 유지한다.
- OCR 품질 개선은 이벤트 종료 후 best frame 원본 재캡쳐와 전처리 ensemble에만 적용한다.
- TOP-N 원본 프레임 voting/batch OCR은 GUI 반응성 문제 때문에 제거한다.
- Spring Boot로 내려가는 `analysisStatus` 계약은 기존 방식 그대로 유지한다.

관련 파일:

- `fastapi-server/app/api/routes/detection.py`
- `fastapi-server/app/services/frame_buffer.py`
- `fastapi-server/app/services/stream_event_service.py`
- `fastapi-server/app/services/inference_service.py`
- `fastapi-server/app/services/image_preprocessor.py`
- `fastapi-server/app/services/plate_recognizer.py`
- `fastapi-server/scripts/stream_video_file.py`
- `fastapi-server/tests/test_detection_api.py`

## 2. 전체 Workflow

### 1단계. FastAPI stream-frame 수신 계약 확장

`POST /api/detections/stream-frame`에 선택 입력을 추가했다.

- `frameNumber`
- `highResCrop`
- `highResCropFrameNumber`

기존 `image`는 그대로 유지했다. 이 이미지는 저화질 탐지, bbox 표시, 속도 계산용이다. `highResCrop`은 OCR/storage 후보용으로만 사용하고 속도 계산에는 섞지 않는다.

문제 방지:

- `image`와 `highResCrop`은 `image/jpeg`, `image/png`만 허용한다.
- 잘못된 content-type은 400으로 응답한다.
- 기존 클라이언트가 `highResCrop` 없이 요청해도 기존 흐름이 깨지지 않게 optional로 처리한다.

### 2단계. BufferedFrame에 high-res OCR 후보 저장

`BufferedFrame`에 다음 필드를 추가했다.

- `frame_number`
- `high_res_crop_bytes`
- `high_res_crop_content_type`

이 값은 이벤트 finalize 시 OCR 후보로만 사용한다. 탐지 bbox, 속도 측정, preview overlay는 기존 저화질 프레임 기준을 유지한다.

### 3단계. StreamEventService에서 best candidate 메타데이터 반환

이벤트 종료 시 frame buffer에서 candidate score가 가장 높은 프레임을 고른다.

응답에는 단일 best candidate 정보만 포함한다.

- `bestCandidateFrameNumber`
- `bestCandidateBbox`
- `bestCandidateCapturedAt`

이 메타데이터는 클라이언트가 원본 영상에서 해당 프레임을 다시 찾아 crop하는 데 사용한다.

### 4단계. InferenceService에서 OCR 전용 high-res 입력 우선 사용

`detect_from_image_bytes()`에 `high_res_crop_bytes` 선택 인자를 추가했다.

적용 원칙:

- 차량 탐지와 속도 기준 bbox는 기존 저화질 이미지 기준을 유지한다.
- 번호판 탐지와 OCR은 `high_res_crop_bytes`가 있으면 해당 이미지를 우선 사용한다.
- `high_res_crop_bytes`가 없으면 기존 저화질 frame으로 fallback한다.

### 5단계. 클라이언트에서 원본 best frame 재캡쳐 방식 적용

초기 high-res 방식은 최근 bbox 또는 preview tracker bbox 기반 crop을 다음 업로드에 붙이는 구조였다. 그러나 사용자가 원하는 것은 “서버가 best frame으로 고른 정확한 영상 프레임을 원본 영상에서 다시 캡쳐해 OCR하는 방식”이었다.

최종 적용 구조:

1. GUI와 FastAPI stream-frame은 기존처럼 저화질 업로드 프레임으로 동작한다.
2. 서버가 이벤트 종료 시 best candidate frame number와 bbox를 응답한다.
3. 클라이언트가 `sample.mp4` 원본 영상에서 해당 frame number를 seek한다.
4. 저화질 bbox 좌표를 `1 / upload_scale`로 원본 좌표로 환산한다.
5. 원본 프레임에서 vehicle crop을 만든다.
6. 별도 `/api/detections/stream-frame/highres-ocr` endpoint로 high-res crop을 전송한다.
7. FastAPI가 high-res crop에서 plate detection과 OCR을 수행한 뒤 Spring Boot로 기존 상태 계약에 맞춰 저장한다.

주의:

- GUI 표시용 `--scale`은 OCR crop 좌표 계산에 절대 사용하지 않는다.
- 좌표 환산에는 `--upload-scale`만 사용한다.
- `analysisStatus`는 별도 high-res 상태를 만들지 않고 기존 `FLOW_EVENT_CREATED`, `OCR_FAILED`, `DUPLICATE_SKIPPED`를 그대로 사용한다.

### 6단계. OCR 전처리 ensemble 적용

원본 프레임 재캡쳐 후에도 핸드폰 촬영 영상 자체의 화질 한계가 있어 OCR 전처리 개선을 적용했다.

`image_preprocessor.py`에서 `build_plate_ocr_variants()`를 추가했다.

생성 variant:

- `resized`
- `clahe`
- `sharpened`
- `clahe_sharpened`
- `otsu`
- `adaptive`

`plate_recognizer.py`에서는 `recognize_best()`를 추가했다. 각 variant OCR 결과를 비교한 뒤 더 좋은 후보를 선택한다.

선택 기준:

- plate text가 있는 결과를 우선한다.
- text 길이가 더 긴 결과를 우선한다.
- 길이가 같으면 confidence가 높은 결과를 선택한다.

저장되는 OCR 전처리 이미지는 최종 선택된 variant 이미지다.

### 7단계. TOP-N 원본 프레임 voting 시도

OCR 품질을 더 높이기 위해 best frame 하나가 아니라 상위 N개 후보를 원본 프레임에서 재캡쳐하고 batch OCR 후 voting하는 방식을 시도했다.

추가했던 요소:

- `ocrCandidates` 응답 필드
- `PlateCandidateVoter`
- `/api/detections/stream-frame/highres-ocr-batch`
- 클라이언트 high-res OCR background queue/worker
- `TOP_N_OCR_FRAMES=3`

문제:

- GUI가 frame 1 bbox 상태에서 사실상 멈춘 것처럼 보였다.
- YOLO/preview 흐름과 batch high-res OCR이 같은 실행 경로에서 충돌하며 체감 반응성이 크게 나빠졌다.
- 데모와 수동 검증에서는 OCR 개선보다 GUI 조작 가능성이 더 중요했다.

결론:

- TOP-N voting은 제거했다.
- `TOP_N_OCR_FRAMES`는 1로 되돌렸다.
- 단일 best-frame 원본 재캡쳐와 OCR ensemble만 남겼다.

## 3. 최종 채택 구조

```text
low-res upload frame
  -> FastAPI vehicle detection
  -> bbox / speed / stream status
  -> event finalized
  -> bestCandidateFrameNumber + bestCandidateBbox 반환

client original video recapture
  -> seek sample.mp4 by bestCandidateFrameNumber
  -> original bbox = uploaded bbox / upload_scale
  -> high-res vehicle crop
  -> POST /api/detections/stream-frame/highres-ocr

FastAPI high-res OCR
  -> plate detector
  -> OCR preprocessing variants
  -> recognize_best
  -> Spring Boot 저장
```

## 4. Troubleshooting

### high-res crop을 켰는데 체감 개선이 작음

원인:

- crop이 원본 영상 프레임이 아니라 이미 `upload_scale`이 적용된 프레임에서 만들어졌을 수 있다.
- OCR은 crop 품질뿐 아니라 원본 영상의 초점, 모션 블러, 번호판 픽셀 수에 크게 좌우된다.

확인:

- 로그의 `bestFrame`이 실제 원본 영상 frame number인지 확인한다.
- 저장된 `plate_crop.jpg`, `ocr.jpg`가 이전보다 선명한지 비교한다.
- `--scale` 값은 GUI 표시용이므로 OCR 품질 판단에서 제외한다.

### GUI가 bbox 상태에서 멈춤

원인:

- TOP-N 원본 프레임 voting/batch OCR을 붙이면 finalize 이후 고비용 작업이 추가된다.
- preview와 upload worker가 이미 바쁜 상태에서 high-res batch까지 붙으면 GUI가 응답하지 않는 것처럼 보일 수 있다.

조치:

- TOP-N batch endpoint와 voter 제거.
- `ocrCandidates` 응답 제거.
- high-res OCR은 단일 best frame 기준으로만 수행.
- `TOP_N_OCR_FRAMES=1` 유지.

### analysisStatus가 기존과 달라짐

원인:

- high-res OCR 전용 상태를 새로 만들면 Spring Boot와 프론트 계약이 흔들릴 수 있다.

조치:

- 별도 `HIGH_RES_OCR_PENDING` 같은 상태를 쓰지 않는다.
- 기존 `FLOW_EVENT_CREATED`, `OCR_FAILED`, `DUPLICATE_SKIPPED`만 사용한다.

### OCR 전처리 후에도 한계가 있음

원인:

- 핸드폰 촬영 원본 영상의 초점/흔들림/압축/번호판 픽셀 수 한계.
- 전처리는 이미지를 복구하는 것이 아니라 OCR이 읽기 좋은 후보를 늘리는 방식이다.

현재 최선:

- 원본 best frame 재캡쳐
- high-res vehicle crop
- plate detector 재수행
- CLAHE/sharpen/threshold ensemble
- best OCR result 선택

추가 개선 후보:

- 더 높은 해상도/프레임레이트 원본 영상 확보
- 번호판 전용 detector 재학습
- OCR 모델 fine-tuning
- motion blur가 적은 프레임을 고르는 blur/plate-size 기반 candidate scoring 강화

## 5. 검증 결과

실행한 검증:

```powershell
.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py app\services\plate_recognizer.py
.\.venv\Scripts\python.exe -m pytest tests\test_detection_api.py -q
git diff --check
```

결과:

- `py_compile` 통과
- `git diff --check` 통과
- `tests/test_detection_api.py`: 54 passed

## 6. Notion 한줄 요약

1. `/stream-frame`에 `frameNumber`, optional `highResCrop` 수신 계약을 추가해 기존 저화질 탐지 흐름을 깨지 않고 OCR용 고화질 입력을 받을 수 있게 했다.
2. `BufferedFrame`과 `StreamEventService`에 high-res crop과 best candidate frame metadata를 연결해 이벤트 종료 시 OCR 후보 프레임을 추적할 수 있게 했다.
3. `InferenceService`에서 차량 탐지/속도 계산은 저화질 기준으로 유지하고, 번호판 탐지/OCR은 high-res crop을 우선 사용하도록 분리했다.
4. 클라이언트에서 서버가 고른 `bestCandidateFrameNumber`를 원본 영상에서 다시 seek해 원본 화질 crop을 만든 뒤 `/highres-ocr`로 재전송하는 구조를 적용했다.
5. OCR 품질 개선을 위해 CLAHE, sharpen, Otsu, adaptive threshold 등 전처리 variant ensemble을 만들고 가장 좋은 OCR 결과를 선택하도록 했다.
6. `analysisStatus`는 Spring/프론트 계약 보호를 위해 기존 `FLOW_EVENT_CREATED`, `OCR_FAILED`, `DUPLICATE_SKIPPED` 흐름을 유지했다.
7. TOP-N 원본 프레임 voting/batch OCR을 시도했지만 GUI 반응성이 크게 떨어져 제거하고, 단일 best-frame 원본 재캡쳐 + OCR ensemble 상태로 되돌렸다.
8. 최종 검증으로 `py_compile`, `git diff --check`, `pytest tests/test_detection_api.py -q`를 수행했고 54개 테스트가 통과했다.
