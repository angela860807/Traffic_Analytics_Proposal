# Artifact 11 - Context Workflow & Troubleshooting

작성일: 2026-05-20

## 1. 문서 목적

이 문서는 이번 컨텍스트에서 진행한 과속 탐지 작업의 실제 흐름을 복기하기 위한 작업일지다. 기능이 추가됐다가 정리된 부분, 용어가 바뀐 부분, 테스트 중 발견된 문제와 해결 방향을 팀원이 따라올 수 있도록 workflow와 troubleshooting 중심으로 정리했다.

별도 팀 공유 요약 문서는 다음 파일로 분리했다.

- `FastAPIdocuments/과속탐지_최종복기_팀공유자료.md`

## 2. 전체 Workflow

### 1단계. 기존 산출물 검수

초기에는 `artifact_10_speed_detection_worklog_troubleshooting.md`와 과속 탐지 요약 문서를 검수했다. 잔여 리스크는 크게 세 가지였다.

- 과속 저장 실패 시 재시도/실패 정책이 부족했다.
- 속도 설정 검증이 런타임 처리 중에 늦게 터질 수 있었다.
- 속도 정확도는 실측 전까지 참고값으로 다뤄야 했다.

### 2단계. 과속 저장 실패/재시도 정책

FastAPI가 Spring Boot로 과속 저장을 보낼 때 실패할 수 있으므로 retry 정책을 추가했다.

- 429 또는 5xx 응답은 재시도 대상이다.
- 네트워크 오류도 지정 횟수까지 재시도한다.
- 최종 실패해도 원본 flow event 저장은 성공으로 유지한다.
- 응답에는 `speedViolationSent=false`, `speedViolationSendError`를 남긴다.

### 3단계. 설정 검증을 startup 단계로 이동

속도 설정 JSON이나 tracking 설정이 잘못되면 프레임 처리 중 이미지 오류처럼 보일 수 있었다. 그래서 FastAPI lifespan startup에서 속도 설정을 먼저 검증하도록 바꿨다.

기대 효과:

- 잘못된 `SPEED_CAMERA_CONFIGS_JSON`은 서버 시작 단계에서 바로 실패한다.
- 운영 중 프레임마다 같은 설정을 반복 파싱하지 않는다.
- 오류 원인이 이미지 처리인지 설정 문제인지 구분이 쉬워진다.

### 4단계. Homography 추가

처음 속도는 Line A/B 사이의 고정 거리 `distanceMeters`를 기준으로 계산했다. 하지만 카메라 원근 때문에 화면 픽셀 거리와 실제 도로 거리가 다르다.

그래서 homography를 추가했다.

- `imagePoints`: 영상 위 보정점 4개
- `worldPointsMeters`: 실제 평면 좌표 4개
- bbox bottom-center를 실제 미터 좌표로 투영
- 투영된 이동거리로 속도 계산

단, 현장 실측 전까지는 여전히 참고값이다.

### 5단계. ROI와 Line A/B 지정 실험

처음에는 GUI에서 다음을 모두 직접 찍는 방식을 만들었다.

- ROI 4점
- Line A 2점
- Line B 2점

테스트하면서 Line A/B를 직접 긋는 방식은 유지비가 크고 화면도 복잡해진다는 결론이 나왔다. 이후 Line A/B 직접 지정은 제거하고, ROI 4점만 지정하도록 축소했다.

### 6단계. TRACK_DELTA 방식으로 전환

Line crossing 방식은 차량이 선을 정확히 통과해야 속도가 안정적으로 나온다. 실제 테스트 영상에서는 bbox가 흔들리거나 선을 애매하게 통과하면서 `speed=-`가 자주 나왔다.

최종 기본값은 `TRACK_DELTA`로 정했다.

- Line A/B 통과 여부를 핵심 조건으로 쓰지 않는다.
- 일정 시간 동안 bbox bottom-center가 이동한 거리로 속도를 계산한다.
- 기본 모드는 화면 전체 또는 ROI 내부에서 지속적으로 속도를 추정한다.

### 7단계. ROI 기본값 정리

ROI를 너무 좁게 잡으면 bbox가 잠깐 벗어났을 때 추적이 끊기거나 보기 어색했다. 그래서 기본 동작은 전체 화면 기준으로 정리했다.

현재 GUI 정책:

- Enter만 누르면 전체 프레임 ROI로 시작한다.
- 4점을 찍으면 이번 실행에만 해당 ROI를 적용한다.
- `--save-speed-config-json`을 주지 않으면 파일에 저장하지 않는다.

### 8단계. 테스트 영상 속도 보정

테스트 영상 자체가 원본보다 느린 속도로 재생되는 상황이 있었다. 이 경우 실제 차량 속도보다 낮게 계산된다.

`--video-speed-ratio`를 추가했다.

- `1.0`: 영상 시간이 실제 시간과 같다고 본다.
- `0.70`: 영상이 원본 속도의 70%라고 보고 시간 간격을 압축한다.
- `0.30`: 더 느린 영상에 대한 강한 보정이다.

이 값은 측정 거리와 함께 속도에 직접 영향을 준다.

### 9단계. 로그 정리

튜닝 중에는 로그에 많은 정보를 붙였다.

- `[homography-est]`
- `mode=TRACK_DELTA`
- `dist=...`
- `elapsed=...`
- `accuracy=HOMOGRAPHY_ESTIMATED`

최종 테스트가 안정된 뒤에는 기본 로그를 간결하게 정리했다.

현재 기본 로그 예시:

```text
speed=VIOLATION:66.34/50.0 overSpeed=True speedSent=True
speed=36.0/50.0 overSpeed=False speedSent=False
```

### 10단계. Spring Boot 저장값 보강

`speed_violations`에는 과속이 저장되지만, `vehicle_flow_events.speed`는 계속 `NULL`이었다.

원인:

- flow event는 번호판 이벤트 저장 시 먼저 생성된다.
- 과속 측정값은 이후 별도 `/api/speed-violations` 요청으로 들어온다.
- 기존에는 이 두 저장 흐름이 `vehicle_flow_events.speed`를 갱신하지 않았다.

수정:

- 과속 저장 성공 시 `VehicleFlowEvent.updateSpeed(measuredSpeed)`를 호출한다.
- 중복 과속 POST도 기존 violation을 반환하면서 flow event speed를 보정한다.

주의:

- 기존 DB row는 자동으로 backfill되지 않는다.
- 새 과속 저장부터 반영된다.
- 백엔드 컨테이너가 최신 코드로 재빌드되어야 실제 DB에 반영된다.

### 11단계. 데이터 및 이미지 정리

테스트 종료 후 다음을 정리했다.

- `fastapi-server/storage/detections`
- `.codex_docx_render`
- `speed_violations`
- `detection_analysis_results`
- `vehicle_flow_events`
- `hourly_traffic_stats`
- `traffic_analysis_index`
- `detection_logs`
- `vehicles`

루트에 잘못 생긴 `--fps`, `--video` 같은 0바이트 임시 파일도 삭제했다.

## 3. Troubleshooting

### 1. `speed=-`만 출력됨

가능 원인:

- 추적이 충분히 오래 유지되지 않았다.
- ROI가 너무 좁아 bbox bottom-center가 밖으로 나갔다.
- Line crossing 방식에서 선 통과가 감지되지 않았다.
- homography 또는 거리 설정이 잘못됐다.

해결:

- 기본 모드를 `TRACK_DELTA`로 사용한다.
- ROI를 전체 화면으로 시작한다.
- `SPEED_TRACK_DELTA_MIN_ELAPSED_SECONDS`와 `SPEED_TRACK_DELTA_WINDOW_SECONDS`를 확인한다.
- 테스트 영상이면 `--video-speed-ratio`도 함께 확인한다.

### 2. 속도가 1~10km/h처럼 너무 낮게 나옴

가능 원인:

- 테스트 영상이 실제보다 느리게 재생된다.
- `capturedAt` 간격이 실제 원본 시간보다 길게 잡힌다.
- homography의 실제 거리 값이 작게 잡혔다.

해결:

- `--video-speed-ratio`를 적용한다.
- 예: 영상이 원본 속도의 70%면 `--video-speed-ratio 0.70`.
- 그래도 낮으면 ROI의 `worldPointsMeters` 실제 거리 가정을 다시 본다.

### 3. `--video-speed-ratio 0.30`인데도 20~30km/h만 나옴

가능 원인:

- 영상 자체의 실제 주행 속도가 낮다.
- homography world 좌표의 실제 거리 가정이 작다.
- bbox 기준점 이동량이 생각보다 짧다.

해결:

- 로그의 `speed`만 보지 말고 테스트 영상 구간별 실제 이동 거리를 다시 잡는다.
- `roi-width-meters`, `roi-height-meters`를 현장 기준에 맞춘다.
- 필요하면 테스트용으로만 값을 조정하고 문서에 "참고값"임을 남긴다.

### 4. ROI 4점을 찍었는데 시작이 안 됨

원인:

- 중간 구현에서 ROI 4점 방식으로 바뀌었지만, 스크립트 검증 조건이 예전 8점 방식으로 남아 있었다.

해결:

- `len(state.points) != 4`로 수정했다.
- 이제 4점 클릭 후 Enter로 시작된다.

### 5. 이전에 그린 ROI가 다음 실행에도 남음

원인:

- 클릭한 설정을 파일로 저장하거나 환경변수 설정으로 다시 읽고 있었다.

정리된 정책:

- `--save-speed-config-json`을 주지 않으면 이번 실행에만 적용한다.
- `--speed-config-json`이나 `SPEED_CAMERA_CONFIGS_JSON`을 주면 해당 설정을 다시 읽는다.

### 6. `speedSent=False`인데 `overSpeed=True`

의미:

- `overSpeed=True`는 과속 판정이다.
- `speedSent=False`는 Spring Boot 과속 저장 API 전송 실패 또는 저장 대상 flow event 부재다.

확인:

- `flowEventId`가 있는지 본다.
- Spring Boot `/api/speed-violations` 응답 오류를 확인한다.
- 중복 이벤트라면 최근 flow event id를 받아오는지 확인한다.

### 7. `vehicle_flow_events.speed`가 계속 NULL

가능 원인:

- 기존에 저장된 row라서 backfill되지 않았다.
- Spring Boot 컨테이너가 최신 코드로 재빌드되지 않았다.
- 과속 저장이 실제로 성공하지 않았다.
- 정상 속도 차량은 현재 flow event speed에 저장하지 않는다.

확인:

- `speed_violations` row가 생성됐는지 확인한다.
- 새 과속 이벤트 이후 `vehicle_flow_events.speed`를 확인한다.
- 필요하면 Spring Boot만 재빌드한다.

```powershell
docker compose up -d --build spring-backend
```

### 8. 로그가 너무 길고 튜닝값이 많이 보임

원인:

- 튜닝 단계에서는 mode, dist, elapsed, accuracy를 붙여 계산 원인을 확인했다.

최종 정책:

- 기본 로그에서는 제거했다.
- 필요 시 나중에 `--verbose-speed-log` 같은 디버그 옵션으로 다시 분리하는 것이 좋다.

### 9. Docker build를 Codex가 실행하지 않기로 한 이유

사용자 요청:

- Docker build/image 작업은 토큰과 시간을 많이 쓰므로 Codex가 직접 하지 않는다.
- Codex는 필요한 명령만 안내한다.

현재 원칙:

- 테스트/검수에 필요한 로컬 Python/Spring test는 실행한다.
- Docker image build/rebuild는 사용자에게 명령으로 안내한다.

### 10. 커밋 전 정리 명령

DB 로그 정리:

```powershell
docker exec traffic-postgres psql -U postgres -d traffic -c "TRUNCATE TABLE speed_violations, detection_analysis_results, vehicle_flow_events, hourly_traffic_stats, traffic_analysis_index, detection_logs, vehicles RESTART IDENTITY CASCADE;"
```

이미지 정리 대상:

```text
fastapi-server/storage/detections
.codex_docx_render
```

## 4. 커밋 전 검수 결과

커밋 직전 실행한 검증:

```powershell
.\.venv\Scripts\python.exe -m compileall scripts app
.\.venv\Scripts\python.exe -m pytest tests/test_detection_api.py -q
.\gradlew.bat test --tests com.example.traffic.controller.DetectionLogControllerIntegrationTest
git diff --check
```

결과:

- FastAPI compile 통과
- FastAPI tests: `49 passed`
- Spring integration test: `BUILD SUCCESSFUL`
- `git diff --check`: 공백 오류 없음
- 테스트 DB 로그: 0건으로 정리
- 테스트 산출 이미지: 0건으로 정리

## 5. 남은 TODO

- Spring Boot 최신 코드 재빌드 후 `vehicle_flow_events.speed`가 새 과속 이벤트에서 채워지는지 pgAdmin으로 확인한다.
- 프론트 병합 전에 속도 표시 소스를 결정한다. 후보는 `vehicle_flow_events.speed` 또는 `speed_violations.measured_speed`다.
- 정상 속도 차량도 저장/표시할지, 과속 차량만 표시할지 정책을 정한다.
- `stay_time`은 아직 계산 기준이 없으므로 프론트 표시에서 제외한다.
- 현장 적용 전에는 homography 기준점과 실제 도로 거리를 다시 실측한다.
