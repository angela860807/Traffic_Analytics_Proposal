# Artifact 17 - 2026-05-28 Workflow Troubleshooting

작성일: 2026-05-28

## 1. 문서 목적

2026-05-28 하루 동안 진행한 FastAPI, YOLO 차량 bbox, OCR/DB 저장, Vue 단속관리 화면, 시연용 로그 정리 작업을 시간 흐름대로 정리한다.

이번 작업의 핵심은 "학원 PC에서도 발표 가능한 수준으로 bbox 시연을 안정화할 수 있는가"였다. 결론적으로 OCR/DB 저장 병목은 상당히 줄였고, bbox 시연은 현재 코드와 학원 PC 환경에서 가능한 현실적 한계까지 조정했다. 남은 끊김은 단순 설정 문제가 아니라 YOLO 추론, OpenCV GUI, HTTP 업로드, tracker를 한 프로세스에서 동시에 수행하는 구조적 한계에 가깝다.

## 2. 초반 작업 흐름

### 2.1 Review 화면 OCR crop 표시 개선

문제:

- 단속관리팀 Review 화면에서 OCR 번호판 crop 이미지가 너무 확대되어 번호판 전체가 보이지 않았다.
- crop 이미지 위에 번호판 결과 텍스트 overlay가 겹쳐 보였다.

처리:

- `ReviewView.vue`에서 번호판 overlay 표시를 제거했다.
- `ReviewView.css`에서 번호판 crop 이미지를 `object-fit: contain`으로 바꿔 번호판 전체가 보이게 했다.
- 배경과 padding을 추가해 번호판 이미지가 잘리지 않게 했다.

프론트 담당자에게 전달할 핵심:

```css
.plate-snap img {
  object-fit: contain;
  background: #000;
  padding: 8px;
}
```

그리고 번호판 텍스트 overlay DOM/CSS는 제거한다.

### 2.2 단속관리팀 제한속도 70 통일

문제:

- Vue 단속관리 화면에서는 제한속도를 70으로 보여주기로 했지만, FastAPI 로그와 Docker 환경값은 50으로 남아 있었다.

처리:

- `trafficAS-b/src/views/admin/ReviewView.vue`
  - Review 화면 기준 제한속도 상수를 70으로 통일했다.
- `trafficAS-b/src/composables/useViolationQueue.js`
  - 기본 제한속도 70 적용.
- `trafficAS-b/src/composables/useReportDownload.js`
  - 보고서 샘플 제한속도 70 적용.
- `fastapi-server/app/core/config.py`
  - `SPEED_DEFAULT_LIMIT_KMH` 기본값 `50.0 -> 70.0`.
- `fastapi-server/scripts/stream_video_file.py`
  - `--speed-limit-kmh` 기본값 `50.0 -> 70.0`.
- `fastapi-server/samples/speed-config.cam001.json`
  - `speedLimitKmh: 70.0`.
- `docker-compose.yml`
  - `SPEED_DEFAULT_LIMIT_KMH: 70.0`.
  - `SPEED_CAMERA_CONFIGS_JSON` 내부 `speedLimitKmh: 70.0`.

주의:

- 실행 명령어에 `--speed-limit-kmh 50.0`을 직접 넣으면 기본값보다 명령어 값이 우선된다.
- 최종 시연 명령어에는 반드시 `--speed-limit-kmh 70.0`을 명시한다.

## 3. FastAPI 영상 처리 파이프라인 개선

### 3.1 OCR/DB 저장과 bbox 스트리밍 분리

문제:

- bbox 시연 중 OCR/DB 저장 순간 GUI가 약 3초 정도 멈추는 문제가 있었다.
- 기존에는 stream frame 업로드 경로에서 고해상도 crop, OCR, DB 저장까지 한 흐름에 섞여 있었다.
- 이 때문에 bbox preview 목적의 저해상도 업로드가 OCR 저장 작업에 같이 끌려가며 병목이 발생했다.

처리:

- FastAPI `/api/detections/stream-frame`에 `deferHighresOcr` 옵션을 추가했다.
- stream frame이 `FINALIZED`되면 OCR을 바로 수행하지 않고, event result를 임시 저장한다.
- 새 엔드포인트를 추가했다.

```text
POST /api/detections/stream-events/{event_id}/highres-ocr
```

- `stream_video_file.py`는 `--finalized-highres-ocr` 옵션을 사용할 때:
  - bbox 스트리밍은 저해상도 프레임으로 계속 수행
  - event가 FINALIZED된 뒤 원본 영상의 best frame으로 다시 찾아감
  - 원본 best frame에서 차량 crop을 정사각형으로 생성
  - 해당 crop을 event-specific highres OCR 엔드포인트로 전송
  - OCR/DB 저장은 bbox GUI 루프와 분리

결과:

- 큰 멈춤은 줄었다.
- 산출물은 한 차량당 차량 원본 crop과 번호판 최종 best frame crop 중심으로 정리하는 방향이 되었다.
- `--highres-ocr-crop`은 일반 stream upload마다 crop을 붙이는 방식이라 최종 명령어에서는 제외하는 것이 좋다.

관련 파일:

- `fastapi-server/app/api/routes/detection.py`
- `fastapi-server/scripts/stream_video_file.py`
- `fastapi-server/tests/test_detection_api.py`

검증:

```powershell
.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py app\api\routes\detection.py
.\.venv\Scripts\python.exe -m pytest tests\test_detection_api.py
```

당시 전체 테스트는 `64 passed` 기준으로 통과했다.

## 4. bbox GUI 시연 안정화 과정

### 4.1 bbox 잔상 문제

증상:

- 차량이 지나가거나 사라졌는데 bbox가 빈 도로 위에 남아 있었다.
- bbox가 허공에 남아 다음 차량 인식을 방해하는 것처럼 보였다.

시도:

- `bbox-hold-seconds` 조정
- `preview-max-response-lag-seconds` 조정
- `preview-max-event-age-seconds` 조정
- `preview-min-bbox-confidence` 완화
- `preview-primary-bbox-only` on/off
- tracker 사용 여부 조정

최종 처리:

- `streamStatus`가 `IDLE` 또는 `FINALIZED`이면 bbox를 그리지 않게 처리했다.
- active overlay와 tracker를 강제로 비우는 로직을 넣었다.
- `bbox-hold-seconds`는 최종적으로 0 또는 매우 짧은 값만 추천한다.

현재 판단:

- bbox를 오래 유지하면 차량이 사라진 뒤 빈 공간에 남는다.
- bbox를 너무 빨리 끊으면 탐지가 깜빡인다.
- 발표용으로는 `bbox-hold-seconds 0`이 가장 안전하다.

### 4.2 bbox가 한 템포 늦게 따라오는 문제

증상:

- bbox가 차량 뒤를 따라오는 느낌이 있었다.
- 특히 `preview-delay`와 tracker를 함께 사용할 때 어긋남이 커졌다.

원인 분석:

- `preview-delay-seconds`로 GUI는 과거 frame을 보여준다.
- 그런데 tracker용 frame buffer가 충분하지 않거나, 응답 frame을 못 찾을 때 최신 frame에서 tracker를 시작하면 bbox가 어긋난다.
- tracker 재생성 시 과거 frame을 한꺼번에 replay하면 bbox는 이어지지만 CPU가 튀고 GUI가 끊겼다.

처리:

- tracker frame history 길이를 `preview delay + 2초`로 늘렸다.
- 응답 frame을 frame history에서 못 찾으면 tracker를 만들지 않게 했다.
- tracker 재생성 시 과거 frame을 한꺼번에 replay하는 로직은 제거했다.

결론:

- tracker는 정확도 보조로는 도움이 되지만, 학원 PC에서는 비용이 크다.
- 최종적으로는 tracker를 켜더라도 `--preview-tracker-max-age-seconds`를 짧게 둔다.
- 그래도 끊기면 `--preview-tracker`를 빼는 것이 맞다.

### 4.3 bbox 탐지율과 GUI 끊김의 trade-off

관찰:

- `fps`, `upload-scale`, `preview-delay`, `response-lag`를 타이트하게 잡으면 bbox 싱크는 좋아질 수 있다.
- 하지만 학원 PC에서는 처리 여유가 줄어 GUI가 더 끊긴다.
- 반대로 조금 느슨하게 잡으면 bbox가 살짝 둔해도 전체 시연은 더 안정적으로 보인다.

권장 방향:

- YOLO 업로드 FPS는 낮게 유지한다.
- GUI FPS는 너무 높이지 않는다.
- `upload-scale`은 0.60 정도가 현실적이다.
- `preview-max-response-lag-seconds`는 너무 낮추면 bbox가 자주 버려진다.

현재 결론:

- 완전 실시간보다는 "조금 느리지만 안정적으로 보이는 설정"이 발표용으로 더 낫다.

## 5. GUI 로그와 터미널 로그 정리

### 5.1 GUI 상단 로그

요구:

- GUI 상단 흰색 frame/debug 줄은 제거한다.
- GUI에는 핵심 정보만 보인다.
  - tracking 상태
  - 번호판 결과
  - 계산 속도 결과
- 차량이 사라진 뒤에도 로그가 너무 오래 남으면 어색하다.

처리:

- GUI overlay 로그는 bbox가 사라진 뒤 최대 약 3초 정도만 유지되게 조정했다.
- OCR 결과가 늦게 와도 로그 표시 시간을 계속 연장하지 않게 했다.
- 차량이 완전히 지나가면 초기화되는 느낌이 나도록 했다.

### 5.2 터미널 로그 pretty wrapper

문제:

- Python raw 로그는 `frame`, `frameCount`, `bestFrame`, `analysisStatus` 등이 섞여 있어 발표자가 아닌 사람이 이해하기 어려웠다.
- 한글 로그가 필요했다.
- 이벤트별 구분선이 필요했다.

처리:

- Node wrapper를 추가했다.

```text
fastapi-server/scripts/pretty_stream_video_file.js
```

- Python script를 child process로 실행하고 stdout을 읽어 발표용 로그로 변환한다.
- raw `frame=...`, `ocrStatus ...`, `uploadedFrames=...` 로그를 사람이 읽기 쉬운 한국어 문장으로 변환한다.

예시:

```text
● 차량 추적 중
● 과속 차량 감지  75.6 / 70km/h
● 번호판 인식 결과  70가0777  저장 완료
● 차량 분석 완료  계산 속도=75.6km/h 과속
=============================================================================
```

수정 이력:

- 처음에는 구분선이 번호판 인식 결과 직후 찍혀서 차량 분석 완료가 다음 이벤트처럼 보였다.
- 이후 `번호판 인식 결과`와 `차량 분석 완료`가 둘 다 나온 뒤 구분선이 찍히도록 변경했다.
- 색상은 여러 번 바꿔봤지만 최종적으로 최초 색상 구성이 가장 보기 편하다고 판단해 되돌렸다.

주의:

- PowerShell 기본 콘솔에서는 한글이 깨질 수 있다.
- 실행 전 아래를 시도할 수 있다.

```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:NODE_DISABLE_COLORS = "0"
chcp 65001
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
```

- 그래도 깨지면 Windows Terminal + PowerShell 7 + Cascadia Mono 또는 D2Coding 폰트가 가장 안정적이다.

## 6. 오늘 최종 실행 명령어

작업 위치:

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server
```

최종 권장 명령어:

```powershell
node scripts\pretty_stream_video_file.js `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --auto-full-frame-speed-zone `
  --video-speed-ratio 0.50 `
  --roi-height-meters 22.0 `
  --roi-width-meters 10.5 `
  --distance-meters 22.0 `
  --speed-limit-kmh 70.0 `
  --scale 0.40 `
  --realtime `
  --preview-bbox `
  --preview-tracker `
  --preview-tracker-max-age-seconds 0.35 `
  --async-upload `
  --upload-queue-size 2 `
  --preview-delay-seconds 6.5 `
  --finalized-highres-ocr `
  --highres-crop-padding 0.35 `
  --highres-jpeg-quality 90 `
  --fps 5 `
  --preview-fps 10 `
  --upload-scale 0.60 `
  --bbox-hold-seconds 0 `
  --preview-max-event-age-seconds 0 `
  --preview-max-bbox-area-ratio 0.45 `
  --preview-min-bbox-confidence 0.20 `
  --preview-max-response-lag-seconds 0.35 `
  --no-preview-primary-bbox-only
```

주의:

- `--preview-all-frames`는 학원 PC에서 더 무겁게 느껴져 최종 명령어에서는 제외했다.
- `--highres-ocr-crop`도 일반 stream upload마다 crop을 붙이는 방식이라 제외한다.
- `--finalized-highres-ocr`만 사용해 best frame 기반 OCR/DB 저장을 수행한다.
- tracker 때문에 끊기면 가장 먼저 `--preview-tracker`와 `--preview-tracker-max-age-seconds`를 빼고 테스트한다.

tracker 제외 대안:

```powershell
node scripts\pretty_stream_video_file.js `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --auto-full-frame-speed-zone `
  --video-speed-ratio 0.50 `
  --roi-height-meters 22.0 `
  --roi-width-meters 10.5 `
  --distance-meters 22.0 `
  --speed-limit-kmh 70.0 `
  --scale 0.40 `
  --realtime `
  --preview-bbox `
  --async-upload `
  --upload-queue-size 2 `
  --preview-delay-seconds 6.5 `
  --finalized-highres-ocr `
  --highres-crop-padding 0.35 `
  --highres-jpeg-quality 90 `
  --fps 5 `
  --preview-fps 10 `
  --upload-scale 0.60 `
  --bbox-hold-seconds 0 `
  --preview-max-event-age-seconds 0 `
  --preview-max-bbox-area-ratio 0.45 `
  --preview-min-bbox-confidence 0.20 `
  --preview-max-response-lag-seconds 0.35 `
  --no-preview-primary-bbox-only
```

## 7. 재빌드/재시작 기준

FastAPI route나 config 변경 반영:

- Docker 사용 시 FastAPI 컨테이너 rebuild/recreate 필요.

```powershell
docker compose up -d --build fastapi-server
```

- 로컬 uvicorn 사용 시 FastAPI 서버 재시작 필요.

프론트 변경 반영:

- Vue 변경은 `npm run build` 또는 frontend container rebuild 필요.

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\trafficAS-b
npm run build
```

단순 `scripts/stream_video_file.py`, `scripts/pretty_stream_video_file.js` 변경:

- 재빌드 불필요.
- 스크립트만 다시 실행하면 된다.

## 8. 검증 이력

오늘 진행 중 사용한 주요 검증:

```powershell
.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py
```

```powershell
.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py app\core\config.py
```

```powershell
.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py app\api\routes\detection.py
```

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_detection_api.py
```

```powershell
node --check scripts\pretty_stream_video_file.js
```

프론트:

```powershell
npm run build
```

## 9. 최종 판단

2주 정도의 작업과 오늘의 최종 튜닝 기준으로는 현재 상태가 발표용 MVP로는 현실적인 최선에 가깝다.

확보한 것:

- 차량 YOLO bbox 탐지
- 과속 시 빨간 bbox
- 번호판 OCR 결과 표시
- best frame 기반 차량 crop/OCR 저장
- OCR/DB 저장과 bbox 스트리밍 분리
- 터미널 발표용 한글 로그
- Review 화면 crop 표시 개선
- 제한속도 70 통일

남은 한계:

- 학원 PC에서는 bbox 탐지 중 GUI가 완전히 부드럽지는 않다.
- tracker를 강하게 쓰면 bbox는 이어지지만 CPU 사용량 때문에 끊김이 생긴다.
- tracker를 빼면 GUI는 가벼워지지만 bbox가 조금 끊기거나 늦게 보인다.
- 이는 코드 몇 줄보다 구조적 개선 영역에 가깝다.

후속 개선 방향:

1. GUI 표시 프로세스와 FastAPI 업로드 프로세스 완전 분리
2. YOLO 추론 worker/process 분리
3. GUI는 bbox 응답을 받아 그리기만 하는 구조로 변경
4. GPU, ONNX, OpenVINO, TensorRT 등 추론 최적화 검토
5. CCTV 샘플 기반 차량 bbox fine-tuning

발표 전 운영 전략:

- 명령어를 고정한다.
- PC별로 `fps`, `upload-scale`, `preview-delay`, `preview-tracker` 여부만 조정한다.
- 발표 직전에는 더 이상의 큰 구조 변경을 피한다.

