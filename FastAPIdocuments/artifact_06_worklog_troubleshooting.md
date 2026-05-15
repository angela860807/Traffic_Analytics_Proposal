# 6번 산출물

## 작업 요약

### 1. Raspberry Pi - FastAPI - Spring 연동 흐름 검토

- 기존 연동 흐름은 `Raspberry Pi -> FastAPI -> Spring -> DB` 구조로 정리했다.
- FastAPI는 번호판 인식 성공 결과만 Spring으로 보내는 구조에서, 번호판 미인식과 중복 판정 결과도 Spring으로 보내는 구조로 확장했다.
- 목적은 정의서의 “프레임 단위 detection_logs 저장” 요구에 더 가깝게 맞추고, 왜 통계에 반영되지 않았는지 추적 가능하게 만드는 것이다.

### 2. FastAPI 처리 상태 확장

- 번호판 미인식 결과는 `OCR_FAILED` 상태로 Spring에 전송하도록 설계했다.
- FastAPI 중복 판정 결과는 `DUPLICATE_SKIPPED` 상태로 Spring에 전송하도록 설계했다.
- 정상 인식 결과는 기존처럼 Spring으로 전송하고 flow event 생성 대상으로 처리한다.
- FastAPI 응답에는 `analysisStatus`를 추가해, 상태값이 원본 로그가 아니라 분석 결과 상태라는 점을 분리했다.

### 3. 번호판 OCR Crop 저장 설계

- 대시보드에서 이전 로그를 클릭하면 해당 시점의 번호판 OCR 이미지를 다시 볼 수 있도록 crop 저장이 필요하다고 판단했다.
- 브라우저 대시보드를 캡처하는 방식이 아니라, FastAPI가 분석에 사용한 같은 원본 프레임에서 원본 이미지와 번호판 crop, OCR 전처리 이미지를 저장하는 방향으로 설계했다.
- 저장 파일명 규칙은 다음처럼 정리했다.
  - `*_frame.jpg`: 원본 프레임
  - `*_plate_crop.jpg`: 번호판 crop
  - `*_ocr.jpg`: OCR 전처리 이미지

### 4. FastAPI Crop/OCR 이미지 필드 반영

- `DetectionResult`에 다음 필드를 추가했다.
  - `plateCropImagePath`
  - `plateCropImageUrl`
  - `ocrImagePath`
  - `ocrImageUrl`
- FastAPI는 crop/OCR 이미지를 저장한 뒤 path/url을 응답과 Spring 전송 payload에 포함하도록 수정했다.
- bbox가 없으면 crop/ocr URL은 null로 두고 OCR 실패 흐름으로 처리하도록 정리했다.
- bbox가 있고 OCR만 실패한 경우에는 원본/crop/ocr 이미지를 저장하고, `plateNumber=null`, `analysisStatus=OCR_FAILED` 흐름으로 처리한다.

### 5. Raspberry Pi 수정

- Raspberry Pi는 crop/OCR 처리를 하지 않고 원본 프레임 업로드만 담당하는 것으로 역할을 유지했다.
- RPi 콘솔 출력에는 `imageUrl`뿐 아니라 `plateCropImageUrl`, `ocrImageUrl`, `analysisStatus`도 표시하도록 정리했다.
- 현장 테스트 시 업로드 결과만 보고도 원본/crop/OCR 이미지 생성 여부와 처리 상태를 확인할 수 있게 했다.

### 6. Append-only DB 설계 반영

- 팀 피드백에 따라 `detection_logs`는 원본 로그만 쌓는 append-only 테이블로 유지하는 방향이 더 안전하다고 판단했다.
- OCR 성공/실패, 중복 판정, crop/OCR 이미지, flow event 생성 여부는 별도 테이블인 `detection_analysis_results`에 저장하는 설계를 작성했다.
- 약한 서버를 가정해 UPDATE를 줄이고, 짧은 트랜잭션과 INSERT 중심 구조로 가는 것을 원칙으로 정리했다.

### 7. Backend / Frontend 병합 전 TODO 문서 작성

- Backend와 Frontend 변경분을 나중에 받을 때 검토할 체크리스트를 `TODO_3rd_merge_review.md`로 작성했다.
- 주요 검토 항목은 다음과 같다.
  - Backend가 `detection_logs.status`에 의존하지 않는지
  - `detection_analysis_results` 테이블/엔티티/저장 흐름이 추가됐는지
  - Frontend가 OCR 패널 표시 시 `plateCropImageUrl`을 우선 사용하는지
  - 이전 로그 클릭 시 해당 로그의 crop 이미지와 OCR 결과가 표시되는지

## 트러블 슈팅 로그

### 1. `TrafficAnalysisIndex.java`, `HourlyTrafficStatService.java` 병합 충돌

- 충돌 파일:
  - `TrafficAnalysisIndex.java`
  - `HourlyTrafficStatService.java`
  - 연관 repository 파일
- 원인:
  - zone 단위 분석 인덱스 변경과 기존 통계 집계 방식이 병합되면서 충돌이 발생했다.
- 처리:
  - `TrafficAnalysisIndex`는 `zone_id` 기준 index/unique 제약을 유지하고 `zone_id nullable=false`로 정리했다.
  - `HourlyTrafficStatService`는 단순 IN/OUT count 방식보다 최신 집계 흐름인 평균 속도, 체류시간, 중복 차량 수, 혼잡도 계산 방식으로 정리했다.
  - 최신 집계 로직이 참조하는 `VehicleFlowEvent.speed/stayTime`, `HourlyTrafficStat` 확장 필드, 응답 DTO, repository 쿼리도 함께 보정했다.
- 검증:
  - 충돌 마커 제거 확인
  - `compileTestJava` 성공

### 2. 최신 집계 로직과 도메인 필드 불일치

- 문제:
  - 병합 중 선택한 최신 `HourlyTrafficStatService` 로직이 `avgSpeed`, `stayTime`, `updateStats()`를 사용했지만, 현재 도메인에는 해당 필드와 메서드가 없었다.
- 처리:
  - `HourlyTrafficStat`에 평균 속도, 혼잡도, 평균 체류시간, 중복 차량 수, lastLogId 필드를 추가했다.
  - `VehicleFlowEvent`에 `speed`, `stayTime` 필드를 추가했다.
  - 응답 DTO에도 필요한 필드를 맞췄다.
- 결과:
  - 최신 집계 방식과 도메인 구조가 맞도록 정리했다.

### 3. `detection_logs.status` 설계 변경

- 문제:
  - 처음에는 `detection_logs.status`를 추가해 `RECEIVED`, `OCR_FAILED`, `FLOW_EVENT_CREATED`, `DUPLICATE_SKIPPED`를 저장하는 구조로 설계했다.
  - 이후 팀 피드백으로, 원본 로그 테이블에 처리 상태를 UPDATE하는 방식은 약한 서버에서 위험할 수 있다는 의견이 나왔다.
- 판단:
  - `detection_logs`는 원본 로그만 INSERT하는 append-only 테이블로 두는 것이 안전하다고 판단했다.
- 처리:
  - 처리 상태는 `detection_analysis_results.status`에 저장하는 설계로 변경했다.
  - FastAPI/RPi 문서와 출력 표현에서 `detection_logs.status` 표현을 제거했다.
  - FastAPI 응답에는 `analysisStatus`를 명시했다.

### 4. 번호판 crop 저장 후 응답/payload 누락

- 문제:
  - FastAPI가 crop/OCR 이미지를 저장하더라도, 저장된 path/url을 `DetectionResult`에 담지 않으면 Spring과 Frontend가 사용할 수 없었다.
- 처리:
  - `DetectionResult`에 crop/OCR 이미지 path/url 필드를 추가했다.
  - `inference_service.py`에서 저장된 파일 경로와 URL을 결과 객체에 담도록 수정했다.
- 결과:
  - FastAPI 응답과 Spring 전송 payload에 원본 이미지, 번호판 crop, OCR 전처리 이미지 URL이 함께 포함되도록 정리했다.

### 5. bbox 없음에도 임시 번호판이 들어가던 문제

- 문제:
  - mock inference 흐름에서 bbox가 없는데도 임시 번호판 `123가4567`이 들어가는 fallback 로직이 있었다.
- 위험:
  - bbox가 없으면 번호판 위치를 찾지 못한 것이므로 OCR 실패로 처리해야 하는데, 임시 번호판이 들어가면 실제 테스트 결과가 왜곡된다.
- 처리:
  - bbox가 없으면 `plateNumber=null`, `detectionType=VEHICLE`, `analysisStatus=OCR_FAILED` 흐름으로 가도록 정리했다.

### 6. RPi 콘솔 상태명 혼동

- 문제:
  - RPi 콘솔 출력이 `backendStatus`라는 이름을 사용해, 상태값이 백엔드 저장 상태인지 분석 결과 상태인지 혼동될 수 있었다.
- 처리:
  - `backendStatus`를 `analysisStatus`로 변경했다.
  - FastAPI 응답의 `analysisStatus`를 우선 사용하고, 없을 때만 메시지 기반 fallback을 사용하도록 정리했다.
- 결과:
  - 현장 테스트 로그에서 OCR_FAILED, DUPLICATE_SKIPPED, SENT_TO_BACKEND, ANALYSIS_ONLY 의미가 더 명확해졌다.

### 7. DOCX 설계서 생성 중 한글 파일명 오류

- 문제:
  - DOCX 설계서 생성 시 한글 파일명 경로가 PowerShell 인코딩 문제로 깨져 저장 오류가 발생했다.
- 처리:
  - 문서 내용은 한글로 유지하고, 파일명은 ASCII 기반 `DetectionLogs_AppendOnly_DB_Design.docx`로 변경했다.
- 결과:
  - 문서 생성과 렌더링 검증을 완료했다.

## 생성/수정한 주요 산출물

- `DetectionLogs_AppendOnly_DB_Design.docx`
  - append-only DB 추가 설계서
- `TODO_3rd_merge_review.md`
  - 3차 병합 전 Backend / Frontend 검토 TODO
- FastAPI 수정
  - `fastapi-server/app/schemas/detection.py`
  - `fastapi-server/app/api/routes/detection.py`
  - `fastapi-server/app/services/inference_service.py`
  - `fastapi-server/app/services/backend_client.py`
  - `fastapi-server/tests/test_detection_api.py`
- Raspberry Pi 수정
  - `raspberry-pi/fastapi_client.py`
  - `raspberry-pi/README.md`
  - `raspberry-pi/FASTAPI_RASPBERRY_PI_PROGRESS.md`

## 검증 기록

- FastAPI 테스트:
  - `fastapi-server\.venv\Scripts\python.exe -m pytest tests/test_detection_api.py`
  - 결과: `19 passed`
- FastAPI compile:
  - `python -m compileall app`
  - 결과: 성공
- Raspberry Pi compile:
  - `python -m compileall .`
  - 결과: 성공
- Backend 충돌 해결 후 compile:
  - `.\gradlew.bat compileTestJava`
  - 결과: 성공
