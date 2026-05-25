# Artifact 14 - Demo Workflow Troubleshooting & Handoff

작성일: 2026-05-25

## 1. 문서 목적

2026-05-25 시연 준비 과정에서 진행한 프론트엔드, Docker, FastAPI 영상 스트리밍, OCR 캡처 표시, DB 로그 확인 내용을 커밋 전 기준으로 정리한다.

이번 문서는 다음 컨텍스트가 이어받을 때 바로 확인해야 할 실행 명령, 런타임 산출물 위치, 남은 리스크를 함께 남기는 인수인계 문서다.

## 2. 오늘 처리한 주요 변경

### 2.1 프론트엔드 포트와 진입 경로 정리

- Docker/Vite 기본 프론트 포트를 `5174`로 통일했다.
- `/`와 `/home`이 같은 `MainView`를 보도록 정리했다.
- `/admin`은 `/admin/super`로 이동한다.
- 우측 상단 대시보드 버튼은 `/admin/super`로 이동하도록 변경했다.
- `/admin/control`, `/admin/review` 직접 접근이 가능해야 한다.

관련 파일:

- `docker-compose.yml`
- `trafficAS-b/vite.config.js`
- `trafficAS-b/src/router/index.js`
- `trafficAS-b/src/components/AppNav.vue`
- `trafficAS-b/src/views/MainView.vue`
- `trafficAS-b/src/components/AppFooter.vue`
- `trafficAS-b/public/main1.png`
- `trafficAS-b/public/dashboard.png`
- `trafficAS-b/public/TAS.png`
- `trafficAS-b/public/TAS.ico`

### 2.2 Docker frontend build 실패 대응

`npm ci` 실패 원인은 `vitest@4.x`가 Vite 8 계열 의존성을 끌어오면서 lockfile과 충돌한 문제로 판단했다.

처리:

- `trafficAS-b/package.json`의 `vitest`를 `^2.1.9`로 고정했다.
- `trafficAS-b/package-lock.json`을 갱신했다.

검증:

- `npm run build` 통과
- `npm test -- --run` 통과
- `docker compose up -d --build frontend` 통과 확인 이력 있음

주의:

- `npm audit fix --force`는 Vite 8로 강제 업그레이드할 수 있어 시연 전에는 금지한다.

### 2.3 FastAPI 영상 스트리밍 시연 품질 보정

`fastapi-server/scripts/stream_video_file.py` 기본값을 시연 안정성 기준으로 조정했다.

현재 기본값:

- `--fps 5`
- `--preview-fps 12`
- `--jpeg-quality 70`
- `--upload-scale 0.60`
- `--preview-tracker` 기본 OFF
- `--bbox-hold-seconds 1.4`
- `--preview-delay-seconds 2.0`
- `--preview-max-event-age-seconds 3.8`
- `--preview-max-bbox-area-ratio 0.32`

수정 이유:

- `fps`를 낮추면 bbox 갱신 간격이 벌어져 더 못 따라간다.
- `preview-tracker`는 bbox 첫 응답 시 OpenCV tracker 초기화/재추적 비용으로 GUI가 멈출 수 있어 기본 OFF로 변경했다.
- bbox가 차량과 떨어져 보이던 문제는 좌표 보정이 중복 적용된 버그였다. `select_response_bbox()`에서 이미 원본 좌표로 환산한 bbox를 `draw_preview()`가 다시 확대하고 있었다.
- `eventAge`가 너무 오래된 bbox와 과도하게 큰 false positive bbox는 GUI 표시에서만 숨기도록 했다. 서버 저장/분석 로직은 그대로 둔다.

관련 파일:

- `fastapi-server/scripts/stream_video_file.py`

검증:

- `.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py` 통과

### 2.4 Review 페이지 OCR 이미지 표시 개선

Review 페이지의 차량 정보(OCR) 탭에서 번호판 crop 이미지가 과하게 확대되어 글자가 잘리는 문제가 있었다.

처리:

- 이미지 위에 표시되던 번호판 텍스트 오버레이 제거
- `.plate-snap img`를 `object-fit: cover`에서 `object-fit: contain`으로 변경
- OCR 이미지 박스를 `3.2/1` 비율로 넓혀 번호판 전체 글자가 보이도록 조정

관련 파일:

- `trafficAS-b/src/views/admin/ReviewView.vue`
- `trafficAS-b/src/views/admin/ReviewView.css`

검증:

- `npm run build` 통과

## 3. 현재 시연 실행 명령

작업 디렉터리:

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal\fastapi-server
```

시연용 스트리밍 명령:

```powershell
.\.venv\Scripts\python.exe scripts\stream_video_file.py `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --configure-speed-zone `
  --video-speed-ratio 0.40 `
  --roi-height-meters 35.0 `
  --roi-width-meters 35.0 `
  --distance-meters 35.0 `
  --scale 0.45 `
  --realtime `
  --preview-bbox `
  --async-upload `
  --highres-ocr-crop `
  --highres-crop-padding 0.35 `
  --highres-jpeg-quality 90 `
  --preview-max-event-age-seconds 3.8 `
  --preview-max-bbox-area-ratio 0.32
```

프론트 재빌드:

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal
docker compose up -d --build frontend
```

## 4. DB 로그 정리

조회 기준:

- DB: Docker Postgres `traffic-postgres`
- Database: `traffic`
- User: `postgres`
- 조회일: 2026-05-25

현재 집계:

| 항목 | 건수 |
| --- | ---: |
| `detection_logs` | 145 |
| `detection_analysis_results` | 140 |
| `speed_violations` | 22 |
| 2026-05-25 detection logs | 83 |

분석 결과 상태별:

| status | 건수 |
| --- | ---: |
| `FLOW_EVENT_CREATED` | 54 |
| `DUPLICATE_SKIPPED` | 67 |
| `OCR_FAILED` | 19 |

탐지 타입별:

| detection_type | 건수 |
| --- | ---: |
| `PLATE` | 121 |
| `VEHICLE` | 19 |

최신 확인된 OCR 성공 예시:

| detected_at | plate_number | status | confidence |
| --- | --- | --- | ---: |
| 2026-05-25 22:55:14.644 | 13무9795 | `FLOW_EVENT_CREATED` / `DUPLICATE_SKIPPED` | 0.876 |
| 2026-05-25 22:55:09.124 | 169서8444 | `FLOW_EVENT_CREATED` / `DUPLICATE_SKIPPED` | 0.878 |
| 2026-05-25 22:55:03.684 | 47무9540 | `FLOW_EVENT_CREATED` / `DUPLICATE_SKIPPED` | 0.867 |

DB 확인 명령:

```powershell
docker exec traffic-postgres psql -U postgres -d traffic -c "select count(*) as detection_logs from detection_logs; select count(*) as analysis_results from detection_analysis_results; select count(*) as speed_violations from speed_violations;"
```

```powershell
docker exec traffic-postgres psql -U postgres -d traffic -c "select status, count(*) from detection_analysis_results group by status order by status; select detection_type, count(*) from detection_analysis_results group by detection_type order by detection_type;"
```

```powershell
docker exec traffic-postgres psql -U postgres -d traffic -c "select l.detection_log_id, l.camera_id, l.image_path, l.detected_at, r.status, r.plate_number, r.detection_type, round(r.confidence_score::numeric, 3) as confidence_score, r.plate_crop_image_path, r.ocr_image_path from detection_logs l left join detection_analysis_results r on r.detection_log_id = l.detection_log_id order by l.detected_at desc limit 12;"
```

정리 기준:

- DB 로그는 Docker volume `traffic_postgres_data`에 있는 런타임 데이터다.
- 커밋 대상이 아니므로 삭제하지 않는다.
- 시연 전에는 최신 로그가 Review 페이지에 보이는지 확인하는 용도로 보존한다.
- DB 초기화가 필요할 때만 별도 백업 후 volume 삭제를 검토한다.

## 5. OCR 캡처 산출물 정리

산출물 위치:

```text
fastapi-server/storage/detections/2026/05/25
```

현재 산출물 집계:

| 유형 | 파일 패턴 | 개수 |
| --- | --- | ---: |
| 원본 프레임 | `*_frame.jpg` | 35 |
| 번호판 crop | `*_plate_crop.jpg` | 29 |
| OCR 전처리 이미지 | `*_ocr.jpg` | 29 |

최신 산출물 예시:

```text
CAM_001_225514_frame.jpg
CAM_001_225514_plate_crop.jpg
CAM_001_225514_ocr.jpg
CAM_001_225509_frame.jpg
CAM_001_225509_plate_crop.jpg
CAM_001_225509_ocr.jpg
CAM_001_225503_frame.jpg
CAM_001_225503_plate_crop.jpg
CAM_001_225503_ocr.jpg
```

산출물 확인 명령:

```powershell
Get-ChildItem -Path fastapi-server\storage\detections\2026\05\25 -File |
  Group-Object { if ($_.Name -match '_ocr\.') { 'ocr' } elseif ($_.Name -match '_plate_crop\.') { 'plate_crop' } elseif ($_.Name -match '_frame\.') { 'frame' } else { 'other' } } |
  Select-Object Name,Count
```

정리 기준:

- `storage/detections`는 FastAPI 런타임 산출물이다.
- 커밋 대상이 아니며, 시연 증거와 Review 페이지 이미지 확인에 필요하므로 현재는 삭제하지 않는다.
- OCR crop이 Review 페이지에서 보이지 않으면 DB의 `plate_crop_image_path`, `ocr_image_path`와 실제 파일 존재 여부를 같이 확인한다.
- 시연 이후 정리가 필요하면 날짜별 폴더 단위로 백업 후 삭제한다.

## 6. 남은 리스크와 빠른 대응

### 6.1 첫 실행 렉

원인:

- 차량 YOLO, 번호판 YOLO, PaddleOCR이 첫 요청 시 lazy-load 된다.

현재 대응:

- 시연 전에 warm-up 성격으로 짧게 한 번 실행하고 FastAPI 서버를 유지한다.

향후 개선:

- FastAPI startup 또는 `/health/warmup` 엔드포인트에서 모델/OCR을 사전 로딩한다.

### 6.2 bbox가 늦거나 남는 문제

현재 대응:

- preview tracker 기본 OFF
- bbox 좌표 이중 보정 버그 수정
- event age / bbox area 기반 GUI 표시 필터 추가

주의:

- GUI 표시 필터는 서버의 실제 이벤트 저장/분석을 바꾸지 않는다.
- false positive 자체를 줄이려면 YOLO threshold, ROI, 모델 교체 또는 후처리 개선이 필요하다.

### 6.3 OCR 품질

현재 대응:

- high-res OCR crop 사용
- Review 페이지에서 crop 전체가 보이도록 표시 방식 개선

주의:

- 번호판이 원본 영상에서 작거나 흐리면 OCR은 여전히 실패할 수 있다.
- `upload-scale`을 높이면 OCR/차량 bbox 품질은 좋아지지만 CPU와 지연이 증가한다.

## 7. 커밋 전 확인 체크리스트

- `git status --short`로 변경 파일 확인
- `trafficAS-b`에서 `npm run build` 실행
- `fastapi-server`에서 `.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py` 실행
- 프론트 Docker는 사용자가 직접 실행
- DB/OCR 산출물은 커밋 대상이 아니므로 삭제하지 않음

## 8. 다음 컨텍스트 인수인계

다음 작업자가 바로 확인할 것:

1. 프론트 기본 접속은 `http://localhost:5174`다.
2. `/home`과 `/`는 같은 홈 화면이다.
3. 관리자 화면 직접 진입은 `/admin/control`, `/admin/review`, `/admin/super` 기준이다.
4. Review 페이지 OCR 이미지는 overlay 없이 `contain`으로 보여야 한다.
5. `stream_video_file.py`는 시연용 기본값이 이미 조정되어 있으므로 명령어가 짧아져도 동일하게 동작한다.
6. DB는 정상 조회됐고, 최신 로그/이미지 산출물도 2026-05-25 경로에 존재한다.
7. 시연 전 첫 실행 렉은 모델 lazy-load 가능성이 높으므로 warm-up run 후 본 시연을 시작한다.
8. 런타임 산출물(`fastapi-server/storage`, Postgres volume)은 커밋하지 않는다.

현재 남은 우선순위:

1. 시연 전 Docker frontend rebuild
2. `localhost:5174/admin/review`에서 OCR crop 표시 확인
3. `sample.mp4` 스트리밍 1회 warm-up
4. 본 시연 실행

