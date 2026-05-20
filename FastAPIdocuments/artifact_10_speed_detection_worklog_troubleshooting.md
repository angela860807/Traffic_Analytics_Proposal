# Artifact 10 - Speed Detection Worklog & Troubleshooting

작성일: 2026-05-19

## 작업일지

1. Spring Boot 속도 위반 저장 API 확인 - FastAPI에서 과속 이벤트를 전송할 백엔드 계약을 검증하기 위해.
2. PostgreSQL 및 Docker 서비스 상태 확인 - FastAPI, Spring Boot, DB 연동 테스트의 실행 기반을 보장하기 위해.
3. FastAPI 속도 설정 구조 추가 - 카메라별 가상 라인, 실제 거리, 제한속도, 추적 파라미터를 환경변수로 관리하기 위해.
4. SpeedTracker 구현 - YOLO 차량 bbox의 bottom-center 이동을 추적해 두 가상 라인 통과 시간으로 차량 속도를 계산하기 위해.
5. StreamEventService 속도 측정 연동 - 차량 이벤트 TRACKING/FINALIZED 흐름에 속도 측정값과 과속 여부를 포함하기 위해.
6. Spring Boot speed violation 전송 클라이언트 추가 - 과속이며 flowEventId가 생성된 이벤트만 `/api/speed-violations`로 저장하기 위해.
7. Stream frame 응답 스키마 확장 - `speedMeasurements`, `speedViolation`, `speedViolationSent`를 OpenAPI 응답으로 제공하기 위해.
8. 테스트 영상 실행 파라미터 튜닝 - 번호판 OCR 화질과 bbox 추적 안정성 사이의 균형점을 찾기 위해.
9. 로그 출력 정리 - bbox 좌표를 제거하고 `speed`, `overSpeed`, `speedSent` 중심으로 현장 테스트 로그를 읽기 쉽게 만들기 위해.
10. 비과속 차량 속도 로그 유지 - 과속 차량뿐 아니라 정상 주행 차량의 속도도 FINALIZED 로그에서 확인하기 위해.
11. 속도 고정값 원인 수정 - `capturedAt` 밀리초 절삭과 프레임 단위 라인 통과 시간으로 인한 36.0/50.4 고정값 현상을 줄이기 위해.
12. 라인 통과 시각 보간 추가 - 이전 bbox 위치와 현재 bbox 위치 사이에서 실제 라인 통과 시점을 추정해 속도 계산을 더 연속적으로 만들기 위해.
13. FastAPI 테스트 보강 및 실행 - 속도 계산, 과속 전송, 비과속 속도 유지가 회귀 없이 동작하는지 검증하기 위해.
14. Docker FastAPI 재빌드 및 재기동 - 로컬 코드 변경을 실제 테스트 서버 컨테이너에 반영하기 위해.
15. 속도 설정 startup 검증 추가 - 가상 라인, 카메라별 설정, 추적 파라미터 오류를 프레임 처리 중 이미지 오류로 섞지 않고 서버 시작 단계에서 탐지하기 위해.
16. 속도 정확도 표시 보강 - 현재 속도값이 현장 보정 전 추정값임을 응답의 `isEstimated`, `accuracyLevel`, `accuracyNote`와 테스트 로그 `[est]`로 명시하기 위해.
17. Homography 기반 거리 보정 추가 - 카메라별 보정점이 있으면 두 라인 통과 지점을 실제 평면 좌표로 투영해 `distanceMeters` 고정값보다 현장 측정에 가까운 거리로 속도를 계산하기 위해.
18. ROI 기반 측정 구역 추가 - 테스트 영상 기준으로 지정한 ROI 안의 차량만 속도 추적 대상으로 삼고, preview 화면에 ROI/Line A/B/homography 포인트를 함께 표시하기 위해.
19. 테스트 영상 클릭 설정 모드 추가 - 첫 업로드 스케일 프레임에서 ROI 4점, Line A 2점, Line B 2점을 직접 찍어 속도 설정 JSON을 저장하기 위해.
20. Track delta 속도 모드 추가 - Line A/B 통과 의존을 줄이고 bbox bottom-center 이동거리와 경과시간으로 화면 전체 기준 속도를 계속 추정하기 위해.

## 최종 처리 요약

- 속도 계산 기준: 차량 bbox의 bottom-center가 `lineA`와 `lineB`를 통과한 시각 차이.
- 속도 공식: `distanceMeters / elapsedSeconds * 3.6`.
- 과속 판정: `measuredSpeed > speedLimit`.
- 과속 저장 조건: OCR 성공, 중복 아님, Spring Boot flowEventId 생성 성공, 과속 측정값 존재.
- 과속 저장 실패 정책: flow event 저장 성공 후 speed violation 저장만 실패하면 즉시 재시도하고, 최종 실패 시 전체 stream 응답은 성공으로 유지하되 `speedViolationSent=false`, `speedViolationSendError`로 원인을 남긴다.
- 중복 과속 저장 정책: `DUPLICATE_SKIPPED`라도 Spring Boot가 최근 동일 차량/구역 flow event를 찾으면 기존 `flowEventId`를 응답하고, FastAPI는 그 id로 speed violation 저장을 시도한다. 이미 같은 flow event에 과속 기록이 있으면 Spring Boot는 기존 기록을 반환해 멱등 처리한다.
- 설정 검증 정책: FastAPI lifespan startup에서 속도 설정을 검증하고 캐싱한다. 잘못된 `SPEED_CAMERA_CONFIGS_JSON`, 라인 좌표, 거리/제한속도/추적 파라미터는 서버 시작 실패로 드러낸다.
- Homography 보정 정책: 카메라 설정에 `homography.imagePoints`와 `homography.worldPointsMeters`가 있으면 lineA/lineB 통과 위치를 실제 평면 좌표로 변환해 거리와 속도를 계산하고 `accuracyLevel=HOMOGRAPHY_ESTIMATED`로 응답한다.
- 속도 모드 정책: 기본은 `speedMode=TRACK_DELTA`이며 bbox bottom-center 이동거리와 경과시간으로 속도를 추정한다. 기존 Line A/B 방식은 `speedMode=LINE_CROSSING`일 때만 사용한다.
- ROI 측정 정책: 카메라 설정에 `roi` polygon이 있으면 차량 bbox bottom-center가 ROI 안에 있는 경우만 속도 추적 대상으로 사용한다. ROI가 없으면 기존처럼 전체 프레임을 대상으로 한다.
- 속도 정확도 정책: 보정점이 없거나 투영이 불가능하면 기존 `distanceMeters` 방식으로 fallback하고 `accuracyLevel=ESTIMATED`로 응답한다. 두 경우 모두 현장 검증 전에는 `isEstimated=true`인 참고값이며 테스트 로그는 `[homography-est]` 또는 `[est]`로 구분한다.
- 테스트 설정 방식: `stream_video_file.py --configure-speed-zone`로 첫 프레임에서 ROI 4점을 클릭 지정한다. 아무 점도 찍지 않고 Enter를 누르면 전체 프레임을 ROI로 쓰며, Line A/B는 호환용 자동값으로만 생성된다.
- 일반 속도 로그: 비과속이어도 `speedMeasurements`를 응답에 유지해 `speed=측정속도/제한속도 overSpeed=False`로 출력.
- 과속 로그: `speed=VIOLATION:측정속도/제한속도 overSpeed=True`.
- `speedSent`: 과속 여부가 아니라 Spring Boot speed violation 저장 성공 여부.

## 현 테스트 기준값

```yaml
SPEED_DETECTION_ENABLED: "true"
SPEED_DEFAULT_DISTANCE_METERS: 14.0
SPEED_DEFAULT_LIMIT_KMH: 50.0
SPEED_DEFAULT_LINE_A: 356,289,1000,289
SPEED_DEFAULT_LINE_B: 356,433,1000,433
SPEED_CAMERA_CONFIGS_JSON: '[{"cameraCode":"CAM_001","lineA":[356,289,1000,289],"lineB":[356,433,1000,433],"roi":[[356,289],[1000,289],[1000,433],[356,433]],"distanceMeters":14.0,"speedLimitKmh":50.0,"enabled":true,"homography":{"imagePoints":[[356,289],[1000,289],[356,433],[1000,433]],"worldPointsMeters":[[0,0],[14,0],[0,14],[14,14]]}}]'
SPEED_TRACK_MAX_DISTANCE_PIXELS: 180.0
SPEED_TRACK_TTL_SECONDS: 4.0
SPRING_SPEED_VIOLATION_RETRY_ATTEMPTS: 2
SPRING_SPEED_VIOLATION_RETRY_DELAY_SECONDS: 0.2
```

권장 테스트 실행값:

```powershell
.\.venv\Scripts\python.exe scripts\stream_video_file.py `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --speed-config-json .\samples\speed-config.cam001.json `
  --fps 2 `
  --preview-fps 6 `
  --jpeg-quality 60 `
  --upload-scale 0.50 `
  --scale 0.22 `
  --preview-delay-seconds 10.0 `
  --bbox-hold-seconds 1.5 `
  --no-preview-tracker `
  --realtime `
  --preview-bbox
```

ROI/Line A/B 클릭 설정:

```powershell
.\.venv\Scripts\python.exe scripts\stream_video_file.py `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
  --upload-scale 0.50 `
  --configure-speed-zone `
  --save-speed-config-json .\samples\speed-config.cam001.json `
  --roi-width-meters 14.0 `
  --roi-height-meters 14.0 `
  --distance-meters 14.0 `
  --speed-limit-kmh 50.0
```

## Troubleshooting

### 1. `speed=-`만 출력됨

- 원인: 차량 bottom-center가 두 가상 라인을 모두 통과하지 않았거나, bbox 추적이 중간에 끊김.
- 확인: `roi`, `lineA`, `lineB`가 업로드 해상도 기준 좌표인지 확인한다.
- 조치: `upload-scale` 변경 시 ROI, 라인 좌표, homography `imagePoints`도 같은 비율로 재보정한다.

### 2. `speed=36.0/50.0`, `speed=50.4/50.0`처럼 값이 고정됨

- 원인: 이전에는 테스트 스크립트가 `capturedAt` 밀리초를 제거했고, 서버도 라인 통과 시각을 프레임 시각으로만 처리했다.
- 조치: `capturedAt.isoformat(timespec="milliseconds")`로 전송하고, `SpeedTracker`에서 라인 통과 시각을 bbox 이동 구간 내에서 보간하도록 수정했다.

### 3. `overSpeed=True`인데 `speedSent=False`

- 원인: 과속 판정은 되었지만 Spring Boot에 저장할 `flowEventId`가 없거나, 중복 이벤트(`DUPLICATE_SKIPPED`)라 새 이벤트가 생성되지 않은 경우.
- 해석: `speedSent`는 과속 여부가 아니라 Spring Boot 과속 저장 성공 여부다. `speedViolationSendError`가 있으면 flow event 저장은 성공했지만 과속 저장이 재시도 후에도 실패한 상태다.

### 4. `DUPLICATE_SKIPPED`인 과속 차량이 저장되지 않음

- 원인: 동일 번호판 중복 이벤트는 새 flow event를 만들지 않으므로 speed violation을 연결할 대상 id가 없다.
- 조치: Spring Boot가 중복 이벤트 저장 시 최근 기존 flow event를 조회해 `flowEventId`를 응답하도록 수정했다.
- 현재 정책: 중복 과속은 새 flow event를 만들지 않고 최근 기존 flow event에 연결한다. 같은 flow event의 speed violation 중복 POST는 기존 기록을 반환한다.
- 남은 선택지: 동일 flow event에 여러 과속 측정값을 모두 남겨야 한다면 `speed_violations`를 flow event 1건당 다건 저장 정책으로 확장해야 한다.

### 5. 번호판 화질을 올리면 bbox가 불안정해짐

- 원인: `upload-scale`을 올리면 서버 추론 부담이 커지고 응답 지연이 증가해 preview bbox 동기화가 어려워진다.
- 현재 합의값: `upload-scale=0.50`, `jpeg-quality=60`, `fps=2`.
- 조치: OCR 화질이 더 필요하면 `upload-scale`보다 원본 영상/카메라 해상도, plate crop 저장, OCR 전처리를 우선 확인한다.

### 6. 실제 속도와 차이가 큼

- 원인: `distanceMeters`가 실제 도로상의 두 라인 간 물리 거리와 다르거나, 원근 보정이 없는 단순 2D 라인 방식의 한계.
- 조치: 테스트 영상에서 측정할 구역을 `roi`로 좁히고, 같은 구역 안의 `lineA`, `lineB`, `homography.imagePoints`, `homography.worldPointsMeters`를 함께 설정한다.
- 현재 표시: homography 보정값은 `isEstimated=true`, `accuracyLevel=HOMOGRAPHY_ESTIMATED`, 보정점이 없으면 `accuracyLevel=ESTIMATED`로 응답한다.
- 주의: 예시 JSON의 world 좌표는 검증용 사각 평면 값이다. 현장 적용 전에는 실제 도로 기준점과 차선별 보정점을 다시 측량해야 한다.

### 7. 속도 설정 오류가 이미지 오류처럼 보임

- 원인: 이전에는 카메라별 속도 설정 JSON을 프레임 처리 중 매번 파싱해 설정 오류가 `image must be a valid jpg or png` 흐름과 섞일 수 있었다.
- 조치: FastAPI lifespan startup에서 `validate_speed_settings()`를 실행해 설정을 먼저 검증하고 캐싱하도록 변경했다.
- 기대 결과: 잘못된 속도 설정은 서버 시작 단계에서 즉시 실패하고, 정상 실행 중에는 프레임 처리마다 설정 JSON을 다시 파싱하지 않는다.

## 코드 검수 메모

- FastAPI 단위/통합 테스트: `49 passed`.
- Spring Boot 쪽 기존 테스트는 detection_logs 스키마 변경 후 맞지 않던 테스트 SQL을 제거해 통과 상태로 정리했다.
- 잔여 리스크: 현재 추적은 bbox bottom-center와 최근접 거리 매칭 기반이라 다중 차량 밀집 구간에서는 track swap 가능성이 있다.
- 잔여 리스크: 속도 정확도는 ROI 범위, homography 기준점 품질, 라인 좌표, 영상 FPS, YOLO bbox 안정성에 의존한다.
- 후속 검토: 동일 flow event에 여러 과속 측정값을 모두 남겨야 한다면 `speed_violations`를 flow event 1건당 다건 저장 정책으로 확장한다.
