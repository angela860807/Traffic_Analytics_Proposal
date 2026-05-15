# 7번 산출물

## 작업 요약

### 1. FastAPI - YOLO/OCR - Spring Boot - Frontend 3차 병합 검수

- 팀 프로젝트의 3차 병합 단계에서 FastAPI, Raspberry Pi, Spring Boot Backend, Vue Frontend 연동 흐름을 검수했다.
- 첨부 설계 문서를 기준으로 최종 DB 방향을 정리했다.
- 최종 기준은 `detection_logs`를 append-only 원본 프레임 로그로 유지하고, OCR/crop/상태 결과는 `detection_analysis_results`에 저장하는 구조로 판단했다.
- 정상 번호판 인식 건만 `vehicle_flow_events`를 생성하고, `OCR_FAILED`, `DUPLICATE_SKIPPED`는 flow event를 만들지 않는 계약으로 검수했다.

### 2. FastAPI 이미지 업로드 Smoke Test

- `no_plate.jpg`, `plate.jpg`를 루트 디렉토리에 두고 FastAPI 업로드 API를 직접 테스트했다.
- 초기 테스트에서는 두 이미지 모두 `OCR_FAILED`가 반환되었다.
- 원인은 실제 YOLO 모델 `best.pt`가 아직 FastAPI 컨테이너에 연결되지 않아 bbox/crop/OCR 단계가 정상 수행되지 않았기 때문으로 확인했다.

### 3. Spring Backend 계약 검수

- Spring 내부 API `POST /api/v1/detection-logs`의 정상/중복/미인식 경로를 검수했다.
- 정상 인식 경로는 `FLOW_EVENT_CREATED`, 중복 경로는 `DUPLICATE_SKIPPED`, 번호판 미인식 경로는 `OCR_FAILED`로 저장되는 흐름을 확인했다.
- 잘못된 confidence 값, API key 누락, 번호판 없는 정상 처리 요청 등 오류 케이스도 검수했다.
- 사용자가 pgAdmin4에서 직접 `vehicle_flow_events` 등 DB 테이블 작동을 확인했다.

### 4. Frontend 병합 검수 및 수정

- 실제 라우팅되는 대시보드 화면이 `RoadDashboardView.vue`임을 확인했다.
- 기존 대시보드는 존재하지 않는 FastAPI `/api/v1/plates/recent` 경로 또는 랜덤 데모 번호판 데이터에 의존하고 있었다.
- Vue 대시보드를 Spring `GET /api/v1/detection-logs` 기반으로 변경했다.
- `logId`, `directionType`, `plateCropImageUrl`, `ocrImageUrl`, `status` 등 Spring 응답 필드를 프론트 표시 모델에 매핑했다.
- 랜덤 번호판 생성 fallback을 제거하여 최종 병합 검수에서 API 장애가 숨겨지지 않도록 했다.
- 공용 axios client를 추가하고, API 호출을 `trafficAS-b/src/api/client.js`로 모았다.

### 5. best.pt 모델 연결 및 YOLO/OCR 실검증

- `fastapi-server/models/best.pt` 위치에 모델 파일을 배치했다.
- Docker Compose에 `MODEL_PATH=/app/models/best.pt`와 `./fastapi-server/models:/app/models:ro` 마운트를 추가했다.
- 모델 연결 후 YOLO 로그에서 `license_plate` 검출이 확인되었다.
- 이후 PaddleOCR 런타임 문제를 해결한 뒤 `plate.jpg` 업로드에서 번호판 `161리5391` 인식에 성공했다.
- FastAPI 응답에서 `detectionType=PLATE`, crop 이미지, OCR 이미지, 원본 frame 이미지 경로가 모두 생성됨을 확인했다.

### 6. FastAPI 응답 상태 정렬

- FastAPI가 Spring 저장 성공 후에도 `SENT_TO_BACKEND`를 반환해 프론트/DB 최종 상태와 혼선이 있었다.
- Spring `POST /api/v1/detection-logs`가 단순 `logId` 대신 `DetectionResponse` 전체를 반환하도록 수정했다.
- FastAPI는 Spring 응답의 `data.status`를 읽어 `analysisStatus`로 반환하도록 수정했다.
- 최종적으로 `FLOW_EVENT_CREATED`, `DUPLICATE_SKIPPED`, `OCR_FAILED`가 FastAPI 응답과 Spring DB 상태에서 일관되도록 맞췄다.

### 7. 공유 전 정리 작업

- 기존 더미 detection 로그와 테스트 데이터 삭제 요청에 따라 DB 테스트 행을 정리했다.
- `detection_logs`, `detection_analysis_results`, `vehicle_flow_events`, `vehicles` 테스트 행을 0건으로 정리했다.
- `zones`, `cameras` 기준 데이터는 유지했다.
- FastAPI 저장소의 OCR/frame/crop 산출 이미지 파일을 삭제했다.
- 루트에는 외부 공유용 `plate.jpg`만 남기고 `no_plate.jpg`, FastAPI/Raspberry Pi 샘플 이미지는 삭제했다.
- 각 디렉토리에 흩어진 `.gitignore`, `.dockerignore`를 루트 기준으로 통합했다.
- Docker build context를 루트로 맞추고 각 Dockerfile의 `COPY` 경로를 조정했다.

### 8. 팀 공유 문서 및 PR 문서 생성

- 팀 공유용 DOCX 파일을 생성했다.
- 파일명: `Traffic_Analytics_3rd_Merge_Team_Share.docx`
- 문서에는 작업 결과, 수정내역과 이유, 재빌드 가이드, smoke test 기준, 다음 작업, 새 컨텍스트 인계 메모를 포함했다.
- DOCX는 렌더링 QA를 통해 페이지와 표가 깨지지 않는지 확인했다.
- PR 본문용 요약 문서도 생성했다.
- 파일명: `PR_3rd_Merge_Summary.md`
- 다음 컨텍스트용 TODO 문서도 생성했다.
- 파일명: `TODO.md`

## 트러블 슈팅 로그

### 1. FastAPI 업로드가 계속 `OCR_FAILED`로 반환됨

- 증상: `no_plate.jpg`, `plate.jpg` 모두 `OCR_FAILED`로 반환되었다.
- 원인: 실제 YOLO 모델이 FastAPI 컨테이너에 연결되어 있지 않았다.
- 조치:
  - `fastapi-server/models/best.pt` 경로 확인
  - `docker-compose.yml`에 `MODEL_PATH=/app/models/best.pt` 추가
  - `./fastapi-server/models:/app/models:ro` 볼륨 마운트 추가
- 결과: YOLO 로그에서 `license_plate` 검출이 확인되었다.

### 2. Docker 빌드 중 C드라이브 용량 부족

- 증상: FastAPI 재빌드 중 라이브러리 설치 공간이 부족했다.
- 확인:
  - `docker system df -v` 기준 Docker 내부 이미지/빌드 캐시는 줄었지만 C드라이브 용량은 크게 회복되지 않았다.
  - 실제 대용량 파일은 `C:\Users\mbc_04\AppData\Local\Docker\wsl\disk\docker_data.vhdx`로 확인되었다.
  - 크기는 약 84GB 수준이었다.
- 조치 가이드:
  - Docker Desktop 종료
  - `wsl --shutdown`
  - `Optimize-VHD` 또는 `diskpart compact vdisk` 방식으로 VHDX compact 안내
- 주의:
  - `docker compose down -v`
  - `docker system prune -a --volumes`
  - `docker volume prune`
  - 위 명령은 PostgreSQL DB 볼륨 삭제 위험이 있어 사용 금지로 안내했다.

### 3. PaddleOCR oneDNN/PIR 런타임 오류

- 증상:
  - FastAPI 업로드 시 500 오류 발생
  - 오류 메시지: `ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]`
- 확인:
  - YOLO는 `license_plate`를 정상 검출했다.
  - 오류는 YOLO 이후 PaddleOCR 단계에서 발생했다.
- 원인:
  - PaddleOCR 3.4.1 CPU 런타임에서 oneDNN/MKL-DNN 경로를 타며 오류가 발생했다.
- 조치:
  - Dockerfile에 `FLAGS_use_onednn=0`, `FLAGS_use_mkldnn=0` 추가
  - `libgomp1` 설치 추가
  - PaddleOCR 초기화에 `enable_mkldnn=False` 추가
  - 문서 방향/보정 계열 옵션 비활성화
  - PaddleOCR 3.x 결과 포맷 파싱 추가
- 결과:
  - 500 오류가 사라졌다.
  - `plate.jpg`에서 `161리5391` 인식 성공.

### 4. PaddleOCR 결과 포맷 변경 문제

- 증상:
  - PaddleOCR 3.x는 기존 2.x 스타일 리스트 구조가 아니라 `rec_texts`, `rec_scores`, `rec_boxes` 중심의 dict 결과를 반환했다.
- 조치:
  - `plate_recognizer.py`에서 PaddleOCR 3.x dict 결과 파싱 로직 추가
  - 텍스트를 x좌표 기준으로 정렬해 병합하도록 처리
- 결과:
  - OCR 결과를 번호판 문자열로 안정적으로 병합할 수 있게 되었다.

### 5. 번호판 정규화 regex 깨짐

- 증상:
  - 번호판 정규화 코드에서 한글 범위가 깨져 있었다.
  - OCR이 성공해도 한글 문자가 제거되거나 정규화가 실패할 위험이 있었다.
- 조치:
  - 정규식을 `[^0-9가-힣]` 기준으로 복구했다.
- 결과:
  - 한국 번호판 문자열 `161리5391`을 정상 유지했다.

### 6. FastAPI 응답 상태와 Spring 최종 상태 불일치

- 증상:
  - FastAPI 응답은 `SENT_TO_BACKEND`
  - Spring/DB 최종 상태는 `FLOW_EVENT_CREATED`
  - 사용자 입장에서 어떤 상태가 최종 상태인지 혼란이 있었다.
- 원인:
  - Spring POST 응답이 단순 `logId`만 반환해 FastAPI가 최종 처리 상태를 알 수 없었다.
- 조치:
  - Spring POST 응답을 `DetectionResponse`로 변경
  - FastAPI가 Spring 응답의 `data.status`를 `analysisStatus`로 반환
  - FastAPI `AnalysisStatus` 스키마에 `RECEIVED`, `FLOW_EVENT_CREATED` 추가
- 결과:
  - FastAPI 응답과 대시보드/DB 상태가 같은 상태값을 사용하게 되었다.

### 7. Frontend 대시보드가 실제 DB가 아닌 데모 데이터를 표시

- 증상:
  - 라우팅된 대시보드가 랜덤 번호판 데이터를 생성했다.
  - 존재하지 않는 FastAPI `/api/v1/plates/recent` 경로를 조회하고 있었다.
- 조치:
  - `RoadDashboardView.vue`에서 Spring `/api/v1/detection-logs` 조회로 변경
  - 랜덤 demo fallback 제거
  - Spring 응답 필드 매핑 추가
- 결과:
  - 실제 DB detection log와 crop/OCR 이미지 상태를 프론트에서 확인할 수 있게 되었다.

### 8. `.gitignore`와 `.dockerignore` 분산 문제

- 증상:
  - 하위 디렉토리별 ignore 파일이 흩어져 있었다.
  - Docker 빌드 context가 각 서비스별이라 루트 `.dockerignore` 통합이 바로 적용되기 어려웠다.
- 조치:
  - 루트 `.gitignore`, `.dockerignore` 생성
  - 하위 `.gitignore`, `trafficAS-b/.dockerignore` 제거
  - Docker Compose build context를 루트 기준으로 변경
  - 각 Dockerfile의 `COPY` 경로를 루트 기준으로 수정
- 결과:
  - 팀 공유 시 ignore 정책을 루트에서 한 번에 관리할 수 있게 되었다.

## 검증 기록

- `docker compose config --quiet` 통과
- Spring 통합 테스트 통과
  - `DetectionLogControllerIntegrationTest`
- FastAPI 주요 수정 파일 `py_compile` 통과
- Vue frontend build 통과 기록 확인
- `plate.jpg` end-to-end smoke test 성공
- DB 테스트 로그 정리 후 카운트 확인
- 팀 공유 DOCX 렌더링 QA 완료

## 최종 상태

- 루트에는 외부 공유용 `plate.jpg`만 남겼다.
- FastAPI 저장 이미지 산출물은 삭제했다.
- DB 테스트 로그는 삭제했다.
- 팀 공유 문서와 PR 요약 문서, 다음 작업 TODO를 생성했다.
- 다음 컨텍스트에서는 Raspberry Pi 실제 업로드, YOLO 모델 관리, 실제 영상 처리, OCR 후처리 고도화를 이어가면 된다.

