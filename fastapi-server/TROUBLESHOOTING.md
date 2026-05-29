# Traffic AI FastAPI Troubleshooting

FastAPIdocuments의 artifact 1~17에서 반복적으로 나온 문제와 최종 대응 기준을 정리한다. 발표 전에는 1~5번만 먼저 확인하고, 문제가 생기면 해당 섹션으로 내려가면 된다.

## 1. 발표 전 빠른 점검

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal
docker compose config --quiet
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-WebRequest http://127.0.0.1:5174/ -UseBasicParsing
```

정상 기준:

```text
postgres-db       Up / 5432
spring-backend    Up / 8080
fastapi-server    Up / 8000
frontend          Up / 5174
```

FastAPI health:

```json
{
  "status": "ok",
  "service": "traffic-ai-server"
}
```

## 2. Docker Compose YAML 오류

증상:

```text
yaml: line 62: could not find expected ':'
```

주요 원인:

- pull/merge 후 `docker-compose.yml`에 conflict marker가 남아 있음
- 예: `<<<<<<< HEAD`, `=======`, `>>>>>>> commit`

확인:

```powershell
rg -n "^(<<<<<<< .+|=======$|>>>>>>> .+)" .
docker compose config --quiet
```

해결:

- marker 사이의 양쪽 설정 중 최종값을 선택한다.
- 발표 기준 제한속도는 `70.0`이다.
- `SPEED_CAMERA_CONFIGS_JSON` 내부 `speedLimitKmh`도 같이 맞춘다.

## 3. FastAPI 변경이 반영되지 않음

증상:

- 코드 수정 후 API 동작이 그대로임
- 새 endpoint가 404
- `/openapi.json`에 새 path가 없음

해결:

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal
docker compose up -d --build fastapi-server
```

로컬 uvicorn 실행 중이면 프로세스를 재시작한다.

## 4. 모델 파일을 찾지 못함

증상:

- YOLO 모델 로딩 실패
- `/app/models/best.pt` 또는 `models/best.pt` 없음

확인:

```powershell
Get-ChildItem .\fastapi-server\models
docker compose config | Select-String "MODEL_PATH|PLATE_MODEL_PATH"
```

최종 기준:

```text
fastapi-server/models/best.pt
MODEL_PATH=/app/models/best.pt
PLATE_MODEL_PATH=/app/models/best.pt
```

주의:

- `.pt` 모델 파일은 Git에 올리지 않는다.
- Docker에서는 `fastapi-server/models:/app/models:ro` 볼륨으로 읽는다.

## 5. 최종 시연 명령이 너무 무거움

증상:

- OpenCV GUI가 끊김
- bbox가 한참 늦게 따라옴
- 터미널 로그는 나오지만 화면 반응이 둔함

가장 먼저 뺄 옵션:

```powershell
--preview-tracker
--preview-tracker-max-age-seconds 0.35
```

그 다음 낮출 값:

```powershell
--fps 4
--preview-fps 8
--upload-scale 0.50
```

판단 기준:

- 발표용은 완전 실시간보다 안정적으로 보이는 것이 중요하다.
- tracker는 정확도 보조가 될 수 있지만 저사양 PC에서는 비용이 크다.

## 6. bbox 잔상이 빈 도로에 남음

원인:

- bbox hold 시간이 길거나 오래된 response를 계속 표시함
- `FINALIZED` 이후에도 overlay/tracker가 유지됨

최종 권장값:

```powershell
--bbox-hold-seconds 0
--preview-max-event-age-seconds 0
--preview-max-response-lag-seconds 0.35
```

현재 정책:

- `streamStatus=IDLE` 또는 `FINALIZED`이면 bbox를 오래 그리지 않는다.
- active overlay와 tracker를 비워 차량이 지나간 뒤 잔상을 줄인다.

## 7. bbox가 차량 뒤를 따라옴

원인:

- GUI는 `preview-delay-seconds`만큼 과거 frame을 보여준다.
- 응답 frame과 표시 frame이 어긋나면 bbox가 뒤늦게 보인다.
- tracker를 최신 frame에서 시작하면 과거 frame GUI와 싱크가 맞지 않는다.

대응:

- `preview-delay-seconds`를 너무 낮추지 않는다.
- `preview-max-response-lag-seconds`는 너무 작게 잡으면 bbox가 자주 버려진다.
- tracker가 부담이면 제거한다.

최종 기준:

```powershell
--preview-delay-seconds 6.5
--preview-max-response-lag-seconds 0.35
```

## 8. OCR/DB 저장 순간 GUI가 멈춤

초기 문제:

- `/stream-frame` 요청 안에서 차량 탐지, OCR, DB 저장까지 한 번에 처리했다.
- 이벤트 종료 순간 high-res crop/OCR/Spring 저장이 preview를 같이 막았다.

최종 대응:

```powershell
--finalized-highres-ocr
```

최종 흐름:

```text
stream-frame
  -> FINALIZED
  -> OCR_QUEUED
  -> client original best frame crop
  -> /stream-events/{event_id}/highres-ocr
  -> OCR/DB 저장
```

사용하지 말 것:

```powershell
--highres-ocr-crop
```

이 옵션은 일반 stream upload마다 crop을 붙이는 구버전 방식이라 발표 최종 명령에서는 제외한다.

## 9. high-res OCR을 켰는데 개선이 작음

가능 원인:

- 원본 영상 자체가 흐리거나 모션 블러가 있음
- 번호판 픽셀 수가 너무 작음
- crop은 선명하지만 plate detector가 번호판을 못 찾음
- `--scale`을 OCR 품질 옵션으로 오해함

확인:

- `--scale`은 GUI 표시 크기일 뿐 OCR 품질과 직접 관계 없다.
- OCR 좌표 환산은 `--upload-scale` 기준이다.
- 저장된 `vehicle_crop`, `plate_crop`, `ocr` 이미지를 직접 비교한다.

현재 최선:

- 원본 best frame 재캡쳐
- 정사각형 vehicle crop
- plate detector 재수행
- resize/CLAHE/sharpen/Otsu/adaptive OCR variants
- best OCR result 선택

## 10. TOP-N OCR voting을 다시 켜고 싶을 때

과거 시도:

- 상위 N개 원본 frame을 재캡쳐
- batch OCR
- voting으로 번호판 결정

결론:

- GUI가 frame 1 bbox 상태에서 멈춘 것처럼 보일 정도로 무거웠다.
- 발표 최종본에서는 제거했다.
- `TOP_N_OCR_FRAMES=1` 유지가 맞다.

## 11. `analysisStatus`가 예상과 다름

상태 해석:

| 상태 | 의미 |
| --- | --- |
| `ANALYSIS_ONLY` | FastAPI 분석만 수행, Spring 저장 없음 |
| `FLOW_EVENT_CREATED` | 번호판 OCR 성공 및 flow event 생성 |
| `OCR_FAILED` | 차량/번호판 후보는 있으나 OCR 실패 |
| `DUPLICATE_SKIPPED` | 중복 window 안의 동일 번호판 |

주의:

- high-res OCR 전용 상태를 따로 만들지 않는다.
- Spring/Vue 계약을 흔들지 않기 위해 기존 상태값만 사용한다.

## 12. Spring 저장 실패

증상:

```text
Spring Boot API is not reachable
503
```

확인:

```powershell
docker compose ps
Invoke-WebRequest http://127.0.0.1:8080 -UseBasicParsing
docker compose logs --tail=80 spring-backend
```

주요 원인:

- Spring 컨테이너가 아직 기동 중
- DB migration/DDL warning 중
- internal API key 불일치
- Spring Security permit/CORS 설정 문제

FastAPI는 Spring 내부 API 호출 시 `X-Internal-Api-Key`를 사용한다.

## 13. `overSpeed=True`인데 `speedSent=False`

의미:

- `overSpeed`는 FastAPI가 계산한 과속 여부다.
- `speedSent`는 Spring Boot `speed_violations` 저장 성공 여부다.

가능 원인:

- OCR 실패로 flow event id가 없음
- Spring 저장 실패
- 중복 이벤트에서 연결할 기존 flow event를 못 찾음
- 같은 flow event에 이미 과속 기록이 있어 멱등 처리됨

확인:

- stream 응답의 `analysisStatus`
- `flowEventId`
- `speedViolationSendError`
- Spring `/api/speed-violations` 응답

## 14. 속도가 `-`로만 나옴

가능 원인:

- 차량 bbox가 충분히 이어지지 않음
- ROI 밖으로 판단됨
- track TTL 안에 같은 차량으로 연결되지 않음
- `SPEED_DETECTION_ENABLED=false`

확인:

```powershell
rg -n "SPEED_DETECTION_ENABLED|SPEED_DEFAULT_MODE|SPEED_CAMERA_CONFIGS_JSON" docker-compose.yml fastapi-server\.env.example
```

현재 기본 모드는 `TRACK_DELTA`이며, 차량 bbox bottom-center 이동량으로 속도를 추정한다.

## 15. 속도값이 튐

원인:

- bbox 하단점이 프레임마다 흔들림
- 낮은 FPS
- 차량 bbox가 바뀌거나 track swap 발생
- ROI/homography 기준점이 영상과 맞지 않음

현재 대응:

- 최근 speed measurement 최대 5개 median smoothing
- 비현실적 속도는 `SPEED_MAX_REASONABLE_KMH`로 제한
- `isEstimated`, `accuracyLevel`로 추정값임을 명시

발표 설명:

```text
현재 속도는 시연 영상 기준 추정값이며, 실제 현장 적용 전에는 고정 카메라 캘리브레이션과 기준점 실측이 필요하다.
```

## 16. 제한속도가 50으로 보임

최종 발표 기준은 `70.0km/h`다.

확인:

```powershell
rg -n "SPEED_DEFAULT_LIMIT_KMH|speedLimitKmh|speed-limit-kmh" docker-compose.yml fastapi-server trafficAS-b
```

주의:

- 실행 명령에 `--speed-limit-kmh 50.0`을 직접 넣으면 명령어 값이 우선된다.
- Docker 환경변수, `.env.example`, sample config, 프론트 표시값이 같이 맞아야 한다.

## 17. Raspberry Pi health check timeout

증상:

```text
Connection timed out
GET /health connect timeout
```

대응:

- PC에서 FastAPI가 `0.0.0.0:8000`으로 실행 중인지 확인한다.
- Windows 방화벽과 같은 네트워크 대역을 확인한다.
- Raspberry Pi `.env`의 FastAPI host/IP를 확인한다.
- Docker Compose 기준 `8000:8000` 포트가 열려 있어야 한다.

## 18. Raspberry Pi 이미지 업로드 read timeout

원인:

- 첫 OCR 호출은 PaddleOCR/YOLO 초기 로딩으로 오래 걸릴 수 있다.
- 10초 timeout은 부족할 수 있다.

대응:

```env
REQUEST_TIMEOUT_SECONDS=60
```

또는 시연 전에 warmup을 수행한다.

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/detections/warmup
```

## 19. 한글 로그가 깨짐

PowerShell에서 아래를 먼저 실행한다.

```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:NODE_DISABLE_COLORS = "0"
chcp 65001
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
```

그래도 깨지면 Windows Terminal + PowerShell 7 + Cascadia Mono 또는 D2Coding 폰트를 사용한다.

## 20. Frontend에서 이미지가 안 보임

원인 후보:

- `imageUrl`이 아니라 로컬 `imagePath`만 사용
- FastAPI static mount 미동작
- nginx/Vite proxy에서 `/static/detections`가 FastAPI로 전달되지 않음
- 저장 파일이 `fastapi-server/storage/detections`에 없음

확인:

```powershell
Get-ChildItem .\fastapi-server\storage\detections -Recurse | Select-Object -First 20
Invoke-WebRequest http://127.0.0.1:8000/static/detections/... -UseBasicParsing
```

프론트는 브라우저에서 접근 가능한 `imageUrl` 계열을 사용해야 한다.

## 21. Review 화면 번호판 crop이 잘림

문제:

- crop 이미지가 확대되어 번호판 전체가 보이지 않음
- 번호판 텍스트 overlay가 이미지 위에 겹침

최종 UI 방향:

```css
.plate-snap img {
  object-fit: contain;
  background: #000;
  padding: 8px;
}
```

번호판 텍스트 overlay는 제거한다.

## 22. Spring DDL 경고

Spring 시작 로그에 아래 유형의 경고가 보일 수 있다.

```text
alter column congestion_score set data type numeric(5,2) default 0.00
ERROR: syntax error at or near "default"
```

원인:

- `ddl-auto: update`와 일부 `columnDefinition` 조합 때문에 Hibernate가 PostgreSQL에 맞지 않는 DDL을 생성한다.

판단:

- `Started TrafficApplication`까지 도달하고 API가 동작하면 발표 흐름에는 직접 영향이 없다.
- 발표 직전에는 보류하고, 이후 migration SQL 중심으로 정리하는 편이 안전하다.

## 23. 테스트와 캐시 정리

검증:

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal\fastapi-server
.\.venv\Scripts\python.exe -m py_compile scripts\stream_video_file.py app\api\routes\detection.py
.\.venv\Scripts\python.exe -m pytest tests\test_detection_api.py -q
```

정상 기준:

```text
64 passed
```

테스트 후 캐시는 삭제해도 된다.

```powershell
Remove-Item .pytest_cache -Recurse -Force
Get-ChildItem . -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

## 24. 남은 구조적 한계

- YOLO, HTTP upload, OpenCV preview, tracker가 한 스크립트 프로세스에 함께 있어 저사양 PC에서 병목이 생긴다.
- OCR/DB 저장은 분리됐지만 영속 queue가 아니므로 운영 장애 복구성은 제한적이다.
- 속도값은 현장 보정 전 추정값이다.
- OCR 품질은 원본 영상 품질에 크게 좌우된다.
- 다중 차량 밀집 구간에서는 bbox 기반 track이 바뀔 수 있다.

후속 개선은 worker queue, track id 기반 추적, 현장 calibration, OCR 후처리 강화, 지표 기반 튜닝 순서가 적절하다.
