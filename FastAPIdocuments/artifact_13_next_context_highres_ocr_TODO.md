# Artifact 13 - Next Context High-Resolution OCR TODO

작성일: 2026-05-22

## 1. 바로 확인할 것

- [ ] FastAPI 컨테이너를 재빌드/재시작한다.

```powershell
docker compose up -d --build fastapi-server
```

- [ ] FastAPI 로그에서 모델 경로가 `best.pt`로 잡히는지 확인한다.
- [ ] `TOP_N_OCR_FRAMES=1`이 적용되어 있는지 확인한다.
- [ ] `/api/detections/stream-frame/highres-ocr-batch`가 더 이상 사용되지 않는지 확인한다.
- [ ] `ocrCandidates` 응답 필드가 더 이상 클라이언트 로직에 남아 있지 않은지 확인한다.
- [ ] 기존 `analysisStatus`가 `FLOW_EVENT_CREATED`, `OCR_FAILED`, `DUPLICATE_SKIPPED` 중 하나로만 내려오는지 확인한다.

## 2. 기본 실행 명령

현재 권장 테스트 명령은 아래 기준이다.

```powershell
.\.venv\Scripts\python.exe scripts\stream_video_file.py `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --configure-speed-zone `
  --video-speed-ratio 0.40 `
  --roi-height-meters 35.0 `
  --roi-width-meters 35.0 `
  --distance-meters 35.0 `
  --fps 2 `
  --preview-fps 6 `
  --jpeg-quality 60 `
  --upload-scale 0.50 `
  --scale 0.22 `
  --preview-delay-seconds 10.0 `
  --bbox-hold-seconds 1.5 `
  --no-preview-tracker `
  --realtime `
  --preview-bbox `
  --highres-ocr-crop `
  --highres-crop-padding 0.25 `
  --highres-jpeg-quality 85
```

확인 포인트:

- [ ] GUI가 frame 1 또는 첫 bbox 상태에서 멈추지 않는다.
- [ ] 콘솔에 `streamStatus=TRACKING` 이후 `FINALIZED`가 나온다.
- [ ] `FINALIZED` 응답에 `bestFrame=` 값이 찍힌다.
- [ ] high-res OCR 수행 시 `highresFrame=... analysisStatus=... plateNumber=...` 로그가 찍힌다.
- [ ] high-res OCR 때문에 preview가 장시간 멈추지 않는다.

## 3. OCR 품질 확인 TODO

- [ ] 저장된 원본 frame/crop/OCR 이미지를 한 이벤트 기준으로 비교한다.
- [ ] `*_plate_crop.jpg`가 실제 원본 영상 화질 기반인지 확인한다.
- [ ] `*_ocr.jpg`가 너무 뭉개지거나 글자 획이 끊기지 않는지 확인한다.
- [ ] `resized`, `clahe`, `sharpened`, `clahe_sharpened`, `otsu`, `adaptive` 중 어떤 variant가 자주 선택되는지 로그를 추가할지 결정한다.
- [ ] OCR 실패 케이스에서 plate detector bbox가 맞는지 먼저 확인한다.
- [ ] plate detector bbox가 맞는데 OCR만 실패하면 전처리/recognizer 문제로 분리한다.
- [ ] plate detector bbox가 틀리면 전처리보다 detector/model 개선 대상으로 분리한다.

## 4. 성능/GUI 안정화 TODO

- [ ] `--upload-scale 0.50`에서 GUI 반응성과 bbox 표시가 안정적인지 확인한다.
- [ ] 안정적이면 `--upload-scale 0.40`, `0.35`, `0.30` 순서로 낮춰본다.
- [ ] upload scale을 낮춰도 OCR은 원본 best frame 재캡쳐를 쓰므로 OCR 품질이 크게 떨어지지 않는지 확인한다.
- [ ] upload scale을 낮췄을 때 bbox 자체가 약해지면 YOLO 탐지 입력 화질 한계로 판단한다.
- [ ] `--fps 2` 기준으로 안정화한 뒤 필요하면 `--fps 3`을 테스트한다.
- [ ] `--highres-jpeg-quality`는 우선 85를 유지하고, 네트워크/처리 부담이 크면 75~80으로 낮춰본다.
- [ ] `--highres-crop-padding`은 0.25 기준으로 시작하고, 번호판이 crop 밖으로 밀리면 0.30~0.40을 테스트한다.

## 5. 코드 정리 TODO

- [ ] `fastapi-server/README.md`의 모델명 설명이 `best3.pt`로 남아 있으면 `best.pt` 기준으로 갱신한다.
- [ ] README의 “top-N frame OCR” 표현이 현재 최종 상태와 맞는지 확인한다.
- [ ] `TOP_N_OCR_FRAMES` 설정은 현재 사용하지 않거나 1 고정 성격이므로 유지/삭제 여부를 결정한다.
- [ ] `stream_event_service.py` 로그의 “OCR candidates selected” 문구가 단일 best candidate 의미와 맞는지 정리한다.
- [ ] `plate_recognizer.py`에서 PaddleOCR deprecation warning(`ocr` 대신 `predict`) 대응 필요 여부를 확인한다.
- [ ] OCR variant 선택 결과를 저장하거나 로그로 남기는 debug 옵션을 추가할지 결정한다.

## 6. 테스트 TODO

- [ ] 현재 상태에서 FastAPI 테스트를 다시 실행한다.

```powershell
cd fastapi-server
.\.venv\Scripts\python.exe -m pytest tests\test_detection_api.py -q
```

- [ ] `stream_video_file.py` 문법 검사를 실행한다.

```powershell
cd fastapi-server
.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py
```

- [ ] `git diff --check`로 trailing whitespace 또는 EOF 문제를 확인한다.
- [ ] high-res crop 없이 `/stream-frame` 기존 동작이 유지되는지 확인한다.
- [ ] high-res crop 포함 multipart 요청이 200으로 처리되는지 확인한다.
- [ ] 잘못된 high-res crop content-type이 400을 반환하는지 확인한다.
- [ ] `/highres-ocr` 단일 endpoint가 Spring Boot로 결과를 저장하는지 확인한다.

## 7. 다음 개선 후보

우선순위 높은 순서:

1. 실제 촬영 영상에서 원본 frame crop과 OCR 전처리 이미지 샘플을 10~20건 모아 실패 유형을 분류한다.
2. plate detector가 맞는 실패와 틀린 실패를 분리한다.
3. OCR 전처리 variant 선택 결과를 로그에 남겨 어떤 전처리가 유효한지 확인한다.
4. 번호판 전용 detector 또는 OCR 모델 교체/재학습 파일을 받으면 현재 `best.pt` 기준 파이프라인에 대입한다.
5. 원본 영상 화질 한계가 큰 경우 촬영 조건 개선안을 따로 정리한다.

## 8. 보류한 아이디어

다음 항목은 다시 적용하기 전에 별도 성능 설계가 필요하다.

- [ ] TOP-N 원본 프레임 voting
- [ ] `/highres-ocr-batch`
- [ ] high-res OCR 전용 background worker
- [ ] frame finalize마다 여러 후보 OCR 동시 실행

보류 이유:

- GUI preview가 멈춘 것처럼 보일 정도로 반응성이 나빠졌다.
- 데모/수동 검증에서는 OCR 소폭 개선보다 실시간 화면 조작 가능성이 더 중요하다.
- 재도입하려면 FastAPI 서버 작업 큐, 클라이언트 preview thread, OCR worker를 명확히 분리해야 한다.

## 9. Notion용 다음 작업 요약

1. FastAPI 재빌드 후 `best.pt`, `TOP_N_OCR_FRAMES=1`, `/highres-ocr` 단일 경로 상태를 확인한다.
2. 기존 영상 스트리밍 명령으로 GUI가 멈추지 않고 `TRACKING -> FINALIZED -> highresFrame` 로그가 이어지는지 검증한다.
3. 저장된 frame/crop/OCR 이미지를 비교해 원본 best frame 재캡쳐가 실제로 적용되는지 확인한다.
4. OCR 실패를 plate detector 실패와 recognizer/전처리 실패로 분류한다.
5. `--upload-scale`, `--fps`, `--highres-crop-padding`, `--highres-jpeg-quality` 조합을 조심스럽게 튜닝한다.
6. README와 로그 문구에서 TOP-N/batch 흔적을 정리하고 현재 단일 best-frame 구조에 맞춘다.
7. 테스트는 `pytest tests/test_detection_api.py -q`, `py_compile`, `git diff --check`를 기본 세트로 유지한다.
8. TOP-N voting과 batch OCR은 GUI 안정화 설계 전까지 재도입하지 않는다.
