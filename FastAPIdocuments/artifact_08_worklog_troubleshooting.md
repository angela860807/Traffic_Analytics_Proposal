# 8번 산출물

작성일: 2026-05-15

## 작업 요약

### 1. 병합 후 프로젝트 정리

- 3차 병합 이후 남은 작업 목록을 확인했다.
- 임시 PR 공유 문서, smoke test 산출물, 테스트 DB 행 정리 방향을 정했다.
- `ddl-auto=update`는 유지하되, 공유/시연 DB 스키마 변경은 명시 SQL migration으로 관리하는 방향으로 정리했다.
- `data.sql`에 있던 임시 DDL을 분리하고, 수동 적용용 migration SQL을 `backend/traffic/src/main/resources/db/migration/001_backend_schema_updates.sql`로 정리했다.
- `backend/traffic/docs/dev-migration-notes.md`에 migration 적용 방법과 개발 규칙을 문서화했다.

### 2. 테스트 미디어 관리 정책 정리

- 루트에 `test-media` 디렉터리를 두고 실제 차량 이미지, 테스트 영상, smoke test 산출물, 모델 피드백 샘플을 로컬에서 보관하도록 정리했다.
- 실제 테스트 이미지/영상은 Git에 올리지 않고, `.gitkeep`과 `README.md`만 추적하도록 `.gitignore`를 조정했다.
- `test-media`는 자동 저장 경로가 아니라 사람이 테스트 자료를 분류해서 넣어두는 로컬 보관함이라는 점을 명확히 했다.
- 자동 생성/저장 파일의 위치는 다음처럼 정리했다.

```text
create_sample_image.py       -> Raspberry Pi 로컬 sample.jpg
camera_capture_test.py       -> Raspberry Pi 로컬 capture.jpg
upload_sample_image.py       -> PC FastAPI storage/detections
integration_smoke_test.py    -> PC FastAPI storage/detections
camera_upload.py             -> PC FastAPI storage/detections
camera_upload_loop.py        -> PC FastAPI storage/detections
camera_live_upload.py        -> DB/파일 저장 없음, live preview 메모리 갱신
```

### 3. 내부 README/문서 한글화 및 최신화

- 팀원이 읽어야 하는 내부 README와 진행 문서를 한글 기준으로 정리했다.
- FastAPI, Raspberry Pi, test-media 관련 README를 현재 구현 상태에 맞춰 최신화했다.
- `fastapi-server/README.md`에는 현재 API, 저장 경로, `analysisStatus`, 모델 경로, 테스트 방법, 영상 처리 범위를 정리했다.
- `raspberry-pi/README.md`에는 설치, `.env`, 실행 순서, 업로드 API 구분, 자동 저장 위치, 영상 처리 범위를 정리했다.
- `raspberry-pi/FASTAPI_RASPBERRY_PI_PROGRESS.md`는 예전 진행 메모에서 현재 연동 현황 문서로 재정리했다.
- `fastapi-server/.env.example`의 `MODEL_PATH`를 `models/best.pt`로 맞췄다.
- `raspberry-pi/.env.example`과 `raspberry-pi/config.py`의 `REQUEST_TIMEOUT_SECONDS` 기본값을 60초로 맞췄다.

### 4. Raspberry Pi 연동 테스트 지원

- Raspberry Pi 클라이언트를 `~/traffic-ai-client`에 두고 실행하는 흐름을 확인했다.
- PC 쪽 Docker Compose 서비스 상태를 확인하고 Spring, FastAPI, PostgreSQL, Frontend를 실행했다.
- Raspberry Pi에서 `health_check.py`, `upload_sample_image.py`, 카메라 업로드 스크립트 실행 중 발생한 문제를 확인했다.
- OCR 초기 로딩 때문에 10초 timeout으로는 부족할 수 있어 timeout을 60초로 권장하고 문서와 코드에 반영했다.
- Raspberry Pi 테스트는 health check, 샘플 업로드, 카메라 업로드, live preview까지 완료된 상태로 정리했다.

### 5. FastAPI - Spring 탐지 파이프라인 정리

- FastAPI 모델 경로는 `fastapi-server/models/best.pt`로 정리했다.
- FastAPI 저장소는 `fastapi-server/storage/detections`를 사용한다.
- Spring 내부 API는 `POST /api/v1/detection-logs`이며 `X-Internal-Api-Key`가 필요하다.
- FastAPI 응답 상태는 아래 기준으로 정리했다.

```text
ANALYSIS_ONLY        FastAPI 분석 전용, Spring DB 저장 없음
FLOW_EVENT_CREATED   정상 인식, detection_logs / analysis_results / flow_events 저장
OCR_FAILED           번호판 미인식, detection_logs / analysis_results 저장
DUPLICATE_SKIPPED    중복 판정, detection_logs / analysis_results 저장
```

- 원본 프레임, 번호판 crop, OCR 전처리 이미지 저장 정책을 문서화했다.
- live preview는 DB 저장 없이 FastAPI 메모리 최신 프레임만 갱신하는 기능으로 정리했다.

### 6. QNA 기능 테스트 및 정리

- 기존 프론트 QNA는 정적 데이터/localStorage 중심이었고, 실제 QNA API 연동이 부족했다.
- `trafficAS-b/src/components/QnaTab.vue`를 실제 API 연동형으로 정리했다.
- QNA 목록 조회, 질문 등록, 상세 조회, 관리자 답변 등록 흐름을 확인했다.
- 답변 수정은 현재 백엔드 API가 없어 제외하고, 관리자 답변 등록 기준으로 정리했다.
- 로그인하지 않은 사용자가 질문을 등록하려 할 때 로그인 모달을 열도록 처리했다.
- QNA 테스트 데이터는 DB에서 초기화했다.

### 7. 기본 계정 및 로그인 정리

- 관리자와 일반 사용자 seed 계정의 비밀번호를 `"1234"` 기준 BCrypt 해시로 설정했다.
- 현재 DB에도 동일하게 반영했다.
- 로그인 API로 아래 계정의 토큰 발급 성공을 확인했다.

```text
user1@email.com / 1234
admin@email.com / 1234
```

- 로그인 실패 시 500이 아니라 401 `AUTHENTICATION_FAILED`를 내려주도록 `GlobalExceptionHandler`에 `BadCredentialsException` 처리를 추가했다.
- 프론트 문서의 관리자 계정 안내도 `admin@email.com / 1234`로 맞췄다.

### 8. DB 테스트 데이터 초기화

- QNA 테스트 데이터 초기화:

```text
qna_questions 0
qna_answers   0
```

- FastAPI 캡처/업로드 테스트로 생긴 탐지 관련 DB 데이터도 초기화했다.

```text
detection_logs             0
detection_analysis_results 0
vehicle_flow_events        0
vehicles                   0
hourly_traffic_stats       0
```

- 기본 seed 계정, zone, camera는 유지했다.

### 9. 최종 검수

- `.\gradlew.bat test` 성공을 확인했다.
- `npm.cmd run build` 성공을 확인했다.
- Spring QNA API `GET /api/qna/questions` 200을 확인했다.
- FastAPI health 200을 확인했다.
- Docker 서비스는 PostgreSQL, Spring, FastAPI, Frontend가 정상 실행되는 상태를 확인했다.
- `git diff --check`는 실질 오류 없이 LF/CRLF 경고만 확인했다.
- Spring 시작 로그에 `ddl-auto=update`로 인한 numeric default DDL warning이 남아 있으나 앱은 정상 기동하는 것으로 확인했다.

### 10. BBox 트리거 기반 프레임 버퍼링 설계서 작성

- 달리는 차량 번호판 인식에서 주기 캡처 방식의 한계를 논의했다.
- 몇 초마다 한 장 캡처하는 방식은 번호판이 화면 중앙에 선명하게 잡히는 순간을 놓치기 쉽다는 점을 정리했다.
- 대안으로 BBox 트리거 기반 프레임 버퍼링 구조를 제안했다.
- FastAPI에서 처리하고 Raspberry Pi는 프레임 전송만 담당하는 구조로 정리했다.
- “평소에 프레임을 계속 짧은 버퍼에 저장”한다는 의미를 디스크 저장이 아니라 메모리 ring buffer로 설명했다.
- 서버/용량이 넉넉하지 않은 상황에서도 최근 1~2초만 메모리에 유지하고 이벤트가 없으면 자동 폐기하므로 현실적인 방식이라고 정리했다.
- 팀 공유용 DOCX 설계서 `BBox_Trigger_Frame_Buffering_Design.docx`를 작성했다.
- 문서에는 문제 배경, 제안 구조, 핵심 요소, 장점, FastAPI 처리 책임, 구현 순서, 권장 파라미터, 테스트 계획을 포함했다.

## 트러블 슈팅 로그

### 1. Raspberry Pi health check timeout

**증상**

```text
Connection to 192.168.10.91 timed out.
GET /health connect timeout
```

**원인**

- Raspberry Pi에서 PC FastAPI 서버에 접근하려 했지만 PC 쪽 서비스가 실행 중이지 않거나 네트워크 접근이 준비되지 않은 상태였다.

**조치**

- PC에서 Docker Compose로 PostgreSQL, Spring Boot, FastAPI 서버를 실행했다.
- FastAPI `/health` 접근이 정상인지 확인했다.
- Raspberry Pi에서 다시 health check를 수행했다.

**결과**

- PC와 Raspberry Pi 양쪽에서 health check가 통과했다.

### 2. `upload_sample_image.py` 실행 시 `sample.jpg` 없음

**증상**

```text
FileNotFoundError: No such file or directory: 'sample.jpg'
```

**원인**

- `upload_sample_image.py`는 현재 디렉터리의 `sample.jpg`를 업로드하도록 작성되어 있는데, 샘플 이미지가 생성되어 있지 않았다.

**조치**

- 먼저 `python create_sample_image.py`를 실행해 `sample.jpg`를 생성하도록 안내했다.

**결과**

- 샘플 이미지 파일 누락 문제를 해결했다.

### 3. 이미지 업로드 시 read timeout

**증상**

```text
Read timed out. (read timeout=10.0)
```

**원인**

- FastAPI 서버에서 YOLO/OCR, 특히 OCR 초기 로딩 시간이 10초를 넘을 수 있었다.
- 클라이언트 기본 timeout이 10초라 첫 요청에서 timeout이 발생했다.
- 서버에서는 실제 처리가 뒤늦게 성공할 수 있었다.

**조치**

- Raspberry Pi `.env`와 문서에서 `REQUEST_TIMEOUT_SECONDS=60`을 권장했다.
- `raspberry-pi/.env.example`과 `raspberry-pi/config.py` 기본값도 60초로 맞췄다.

**결과**

- OCR 초기 로딩을 고려한 안정적인 timeout 설정으로 정리했다.

### 4. QNA API 직접 테스트 시 한글이 깨져 보임

**증상**

- PowerShell 출력에서 QNA 제목, 내용, 답변의 한글이 `???` 또는 mojibake처럼 보였다.

**원인**

- 실제 파일/DB UTF-8 문제라기보다 PowerShell 콘솔 인코딩 표시 문제로 판단했다.

**조치**

- Python `repr` 또는 브라우저/DB 확인으로 실제 UTF-8 내용을 구분했다.
- 임시 테스트 데이터는 DB에서 삭제했다.

**결과**

- QNA 테스트 데이터는 초기화했고, 문서/소스 파일은 UTF-8 기준으로 유지했다.

### 5. 기본 seed 계정 로그인 실패

**증상**

- `admin1234` 등 기존 문서에 있던 비밀번호로 로그인 시 500 또는 로그인 실패가 발생했다.

**원인**

- `data.sql`의 BCrypt 해시가 문서에 적힌 비밀번호와 일치하지 않았다.
- 로그인 실패 예외가 전역 예외 처리에서 500으로 잡히는 문제도 있었다.

**조치**

- 기본 계정 비밀번호를 `"1234"` 기준 BCrypt 해시로 재설정했다.
- 현재 DB에도 즉시 반영했다.
- `BadCredentialsException`을 401로 처리하도록 전역 예외 처리에 추가했다.
- 문서의 계정 정보를 `admin@email.com / 1234`로 수정했다.

**결과**

- `user1@email.com / 1234`, `admin@email.com / 1234` 모두 로그인 성공을 확인했다.

### 6. QNA 프론트가 실제 API와 연결되지 않음

**증상**

- QNA 화면이 정적 샘플 데이터와 localStorage 답변 중심으로 동작했다.
- 실제 백엔드 QNA 데이터와 연동되지 않았다.

**원인**

- 프론트 QNA 탭이 API 기반 구현으로 전환되지 않은 상태였다.

**조치**

- QNA 목록 조회, 상세 조회, 질문 등록, 관리자 답변 등록을 API 호출로 변경했다.
- 로그인 상태와 관리자 상태를 명시적으로 반영했다.
- 답변 수정 UI는 현재 백엔드 API가 없어 제외했다.

**결과**

- QNA API smoke test와 프론트 빌드를 통과했다.

### 7. Spring 시작 시 Hibernate DDL warning

**증상**

```text
alter column congestion_score set data type numeric(5,2) default 0.00
syntax error at or near "default"
```

**원인**

- `ddl-auto=update`가 PostgreSQL columnDefinition의 default 포함 타입 변경 DDL을 생성하면서 문법 warning이 발생했다.

**조치**

- 앱 자체는 정상 기동하고 API도 동작하는 것을 확인했다.
- 공유/시연 DB 변경은 명시 migration SQL로 관리하도록 문서화했다.

**결과**

- 현재 개발 단계에서는 `ddl-auto=update`를 유지하되, warning은 팀원에게 공유할 주의사항으로 남겼다.

### 8. FastAPI/Raspberry Pi README가 예전 상태를 반영

**증상**

- FastAPI README에 mock 중심 설명과 보류 사항이 남아 있었다.
- Raspberry Pi README에는 timeout 10초, 자동 저장 위치 설명 부족, 영상 처리 범위 설명 부족이 있었다.

**원인**

- 실제 통합 테스트와 구현이 진행된 뒤 문서가 최신 상태로 갱신되지 않았다.

**조치**

- FastAPI README, Raspberry Pi README, 진행 문서를 현재 완료 상태 기준으로 재작성했다.
- `.env.example` 값도 실제 권장값과 맞췄다.
- `test-media`의 역할과 자동 저장 위치를 명확히 했다.

**결과**

- 팀 공유용 문서 기준으로 현재 구현 상태와 주의사항을 반영했다.

### 9. `test-media`가 자동 저장 위치인지 혼동

**증상**

- Raspberry Pi 테스트 시 이미지가 `test-media`가 아니라 Raspberry Pi 로컬 또는 FastAPI `storage/detections`에 생성되어 혼동이 있었다.

**원인**

- `test-media`는 자동 산출 경로가 아니라 사람이 테스트 자료를 정리해두는 로컬 보관함인데, 이 설명이 충분히 명시되어 있지 않았다.

**조치**

- Raspberry Pi README와 FastAPI README에 자동 저장 위치와 `test-media` 역할을 명확히 추가했다.
- 실제 파일은 ignore하고 `.gitkeep`만 추적하도록 정리했다.

**결과**

- `test-media`는 수동 보관함, `storage/detections`는 FastAPI 자동 산출물 저장소로 역할이 분리되었다.

### 10. 달리는 차량 번호판 인식 타이밍 문제

**증상**

- 몇 초마다 캡처하는 방식으로는 차량 번호판이 정확히 중앙에 잡힌 이상적인 순간을 얻기 어렵다는 문제가 제기되었다.

**원인**

- 주기 캡처는 차량 속도, 흔들림, 조명, 각도, 번호판 위치에 따라 좋은 프레임을 놓칠 수 있다.

**논의한 개선 방향**

- 단순 주기 캡처보다 YOLO bbox가 감지되는 순간부터 사라질 때까지 전후 프레임을 확보하는 방식이 더 적합하다고 판단했다.
- FastAPI가 최근 프레임을 짧게 메모리 ring buffer에 보관하다가 bbox 감지를 이벤트로 묶고, 이벤트 종료 후 best frame을 골라 OCR하는 구조를 제안했다.

**결과**

- BBox 트리거 기반 프레임 버퍼링 설계서를 DOCX로 작성했다.

## 현재 남은 추가 작업 후보

- BBox 트리거 기반 프레임 버퍼링 실제 구현
- `/api/detections/stream-frame` 엔드포인트 추가
- FastAPI 카메라별 ring buffer 구현
- bbox 이벤트 상태 머신 구현
- 후보 프레임 scoring 구현
- top-N OCR 또는 다수결 OCR 결과 선택
- 영상 파일 직접 녹화 및 `.mp4` 재처리 기능
- 탐지 전후 클립 저장 기능
- Spring `ddl-auto=update` warning 원인 제거 또는 columnDefinition 정리
- QNA 답변 수정 API 및 UI 추가 여부 검토
