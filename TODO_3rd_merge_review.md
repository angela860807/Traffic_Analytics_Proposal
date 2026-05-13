# 3차 병합 전 Backend / Frontend 검토 TODO

작성 기준: `DetectionLogs_AppendOnly_DB_Design.docx`

## 현재 판단

- FastAPI / Raspberry Pi는 현재 기준으로 큰 추가 수정 없이 진행 가능하다.
- FastAPI는 `analysisStatus`를 응답에 내려주고, Spring payload에는 기존 호환을 위해 `status` 값을 보낸다.
- Raspberry Pi는 원본 프레임 업로드만 담당하며, crop/OCR 처리는 FastAPI가 담당한다.
- 3차 병합 전 핵심 검토 대상은 Backend와 Frontend 변경분이다.

## Backend 수령 후 검토 TODO

- [ ] `detection_logs`가 원본 수신 로그 전용 append-only 테이블로 유지되는지 확인
  - `status`, `plateNumber`, `crop/ocr image` 같은 처리 결과 필드를 신규 로직에서 쓰지 않아야 한다.
  - 처리 후 `detection_logs` row를 UPDATE하는 코드가 없어야 한다.

- [ ] `detection_analysis_results` 테이블/엔티티가 추가됐는지 확인
  - 필수 필드: `detection_log_id`, `status`, `plate_number`, `detection_type`, `confidence_score`, `plate_crop_image_url`, `ocr_image_url`, `processed_at`, `created_at`
  - OCR 실패 시 `plate_number` null 허용 필요
  - `OCR_FAILED`, `DUPLICATE_SKIPPED`, `FLOW_EVENT_CREATED` 상태 저장 필요

- [ ] 저장 흐름이 분리됐는지 확인
  - FastAPI payload 수신
  - `detection_logs` INSERT
  - `detection_analysis_results` INSERT
  - 정상 인식일 때만 `vehicle_flow_events` INSERT

- [ ] `vehicle_flow_events` 연결 기준 확인
  - 가능하면 `source_analysis_result_id`를 추가해 어떤 분석 결과가 flow event로 이어졌는지 추적한다.
  - 기존 `source_detection_log_id`를 유지하더라도 신규 추적 기준은 analysis result 중심이어야 한다.

- [ ] migration SQL 검토
  - `detection_logs.status` 추가 SQL이 남아 있으면 제거 또는 폐기 처리
  - `detection_analysis_results` 생성 SQL 포함
  - 약한 서버 기준으로 인덱스는 최소 필요 항목만 생성
    - `detection_log_id`
    - `status, created_at`
    - `plate_number, created_at`

- [ ] Backend 테스트 검토
  - `detection_logs.status` 검증이 남아 있으면 실패 기준으로 본다.
  - 새 검증 기준:
    - 원본 로그 row 저장
    - 분석 결과 row 저장
    - OCR_FAILED / DUPLICATE_SKIPPED는 flow event 미생성
    - 정상 인식은 flow event 생성

## Frontend 수령 후 검토 TODO

- [ ] 실시간 로그 조회 API 응답 구조 확인
  - 화면에는 한 줄 로그처럼 보여도 내부 데이터는 `detection_logs + detection_analysis_results` 조합이어야 한다.
  - 프론트가 `detection_logs.status`에 의존하면 수정 필요

- [ ] OCR 패널 이미지 우선순위 확인
  - 1순위: `plateCropImageUrl`
  - 2순위: `imageUrl`
  - 없으면 빈 상태 또는 미인식 안내

- [ ] 이전 로그 클릭 동작 확인
  - 로그 row 클릭 시 해당 row의 crop 이미지와 OCR 결과가 OCR 패널에 표시되어야 한다.
  - 최신 자동 추적 모드와 수동 선택 모드가 충돌하지 않아야 한다.

- [ ] 상태 표시 기준 확인
  - `analysisStatus` 또는 analysis result의 `status`를 사용해야 한다.
  - `OCR_FAILED`: 번호판 미인식
  - `DUPLICATE_SKIPPED`: 중복으로 통계 미반영
  - `FLOW_EVENT_CREATED`: 통계 반영 완료

- [ ] 중복/OCR 실패 UX 확인
  - OCR_FAILED도 로그에는 남고, 원본 또는 crop 이미지가 있으면 확인 가능해야 한다.
  - DUPLICATE_SKIPPED는 통계 미반영 이유를 화면에서 설명할 수 있어야 한다.

## FastAPI / Raspberry Pi 병합 시 재확인 TODO

- [ ] FastAPI 응답에 `analysisStatus`가 포함되는지 확인
- [ ] FastAPI 응답에 `imageUrl`, `plateCropImageUrl`, `ocrImageUrl`이 포함되는지 확인
- [ ] Spring payload에 `status`, crop/ocr 이미지 필드가 포함되는지 확인
- [ ] Raspberry Pi 콘솔 출력이 `analysisStatus` 기준인지 확인
- [ ] Raspberry Pi는 crop/OCR을 직접 수행하지 않고 원본 프레임만 업로드하는지 확인

## 최종 통합 테스트 TODO

- [ ] 정상 번호판 인식
  - `detection_logs` 원본 row 생성
  - `detection_analysis_results.status = FLOW_EVENT_CREATED`
  - `vehicle_flow_events` 생성
  - 대시보드 OCR 패널 crop 표시

- [ ] OCR 실패, bbox 있음
  - 원본/crop/ocr 이미지 저장
  - `detection_analysis_results.status = OCR_FAILED`
  - flow event 미생성

- [ ] OCR 실패, bbox 없음
  - 원본 이미지만 저장
  - crop/ocr URL null 허용
  - `detection_analysis_results.status = OCR_FAILED`

- [ ] 중복 인식
  - `detection_analysis_results.status = DUPLICATE_SKIPPED`
  - flow event 미생성
  - 대시보드에서 통계 미반영 이유 확인 가능

- [ ] 이전 로그 클릭
  - 최신 OCR 패널 대신 클릭한 로그의 crop 이미지 표시
  - 다시 최신 모드로 복귀 가능
