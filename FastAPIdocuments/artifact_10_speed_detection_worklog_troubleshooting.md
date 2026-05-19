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

## 최종 처리 요약

- 속도 계산 기준: 차량 bbox의 bottom-center가 `lineA`와 `lineB`를 통과한 시각 차이.
- 속도 공식: `distanceMeters / elapsedSeconds * 3.6`.
- 과속 판정: `measuredSpeed > speedLimit`.
- 과속 저장 조건: OCR 성공, 중복 아님, Spring Boot flowEventId 생성 성공, 과속 측정값 존재.
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
SPEED_TRACK_MAX_DISTANCE_PIXELS: 180.0
SPEED_TRACK_TTL_SECONDS: 4.0
```

권장 테스트 실행값:

```powershell
.\.venv\Scripts\python.exe scripts\stream_video_file.py `
  --video ..\test-media\videos\sample.mp4 `
  --camera-code CAM_001 `
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

## Troubleshooting

### 1. `speed=-`만 출력됨

- 원인: 차량 bottom-center가 두 가상 라인을 모두 통과하지 않았거나, bbox 추적이 중간에 끊김.
- 확인: `lineA`, `lineB`가 업로드 해상도 기준 좌표인지 확인한다.
- 조치: `upload-scale` 변경 시 라인 좌표도 같은 비율로 재보정한다.

### 2. `speed=36.0/50.0`, `speed=50.4/50.0`처럼 값이 고정됨

- 원인: 이전에는 테스트 스크립트가 `capturedAt` 밀리초를 제거했고, 서버도 라인 통과 시각을 프레임 시각으로만 처리했다.
- 조치: `capturedAt.isoformat(timespec="milliseconds")`로 전송하고, `SpeedTracker`에서 라인 통과 시각을 bbox 이동 구간 내에서 보간하도록 수정했다.

### 3. `overSpeed=True`인데 `speedSent=False`

- 원인: 과속 판정은 되었지만 Spring Boot에 저장할 `flowEventId`가 없거나, 중복 이벤트(`DUPLICATE_SKIPPED`)라 새 이벤트가 생성되지 않은 경우.
- 해석: `speedSent`는 과속 여부가 아니라 Spring Boot 과속 저장 성공 여부다.

### 4. `DUPLICATE_SKIPPED`인 과속 차량이 저장되지 않음

- 원인: 동일 번호판 중복 이벤트는 새 flow event를 만들지 않으므로 speed violation을 연결할 대상 id가 없다.
- 현재 정책: 중복 이벤트의 과속 저장은 스킵한다.
- 향후 선택지: Spring Boot에서 기존 flowEventId 조회 API를 제공하거나, 중복 과속을 별도 이벤트로 저장하는 정책을 정의한다.

### 5. 번호판 화질을 올리면 bbox가 불안정해짐

- 원인: `upload-scale`을 올리면 서버 추론 부담이 커지고 응답 지연이 증가해 preview bbox 동기화가 어려워진다.
- 현재 합의값: `upload-scale=0.50`, `jpeg-quality=60`, `fps=2`.
- 조치: OCR 화질이 더 필요하면 `upload-scale`보다 원본 영상/카메라 해상도, plate crop 저장, OCR 전처리를 우선 확인한다.

### 6. 실제 속도와 차이가 큼

- 원인: `distanceMeters`가 실제 도로상의 두 라인 간 물리 거리와 다르거나, 원근 보정이 없는 단순 2D 라인 방식의 한계.
- 조치: 실제 현장에서 두 라인 사이 거리를 측정해 `distanceMeters`를 재설정하고, 필요하면 차선별 homography 보정을 추가한다.

## 코드 검수 메모

- FastAPI 단위/통합 테스트: `34 passed`.
- Spring Boot 쪽 기존 테스트는 detection_logs 스키마 변경 후 맞지 않던 테스트 SQL을 제거해 통과 상태로 정리했다.
- 잔여 리스크: 현재 추적은 bbox bottom-center와 최근접 거리 매칭 기반이라 다중 차량 밀집 구간에서는 track swap 가능성이 있다.
- 잔여 리스크: 속도 정확도는 `distanceMeters`, 라인 좌표, 영상 FPS, YOLO bbox 안정성에 의존한다.
