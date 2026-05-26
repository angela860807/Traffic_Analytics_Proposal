# Artifact 15 - Realtime Detection Pipeline TODO

작성일: 2026-05-26

## 목적

현재 FastAPI 영상 스트리밍, YOLO 차량/번호판 탐지, PaddleOCR 인식, Spring Boot 저장 흐름을 시연 가능한 수준까지 구성했다. 다만 실무형 실시간 시스템으로 확장하려면 스트림 응답, OCR 후처리, DB 저장이 한 요청 안에서 서로 영향을 주는 구조를 분리해야 한다.

이 문서는 지금 당장 수정하지 않고, 이후 개선 작업에서 우선순위를 잡기 위한 TODO 목록이다.

## 현재 핵심 한계

현재 `/api/detections/stream-frame`는 프레임 수신 후 차량 YOLO, 이벤트 추적, best frame 선택, 번호판 YOLO, PaddleOCR, Spring DB 저장까지 한 흐름 안에서 처리한다. 느린 PC에서는 YOLO/OCR/DB 전송 시간이 길어지고, async 업로드를 켜면 프레임이 드롭되며, async 업로드를 끄면 영상이 끊기는 문제가 생긴다.

## 1순위 TODO - 실시간 응답과 OCR/DB 저장 분리

- `/stream-frame`는 차량 bbox, event status, best candidate 정보만 빠르게 반환한다.
- 이벤트 종료 후 OCR/DB 저장은 background queue 또는 worker로 넘긴다.
- 응답 지연이 bbox preview 품질에 영향을 주지 않게 한다.
- OCR 실패/성공/중복 처리 결과는 별도 상태 조회 API 또는 WebSocket/SSE로 전달하는 방식을 검토한다.

## 2순위 TODO - 차량 Tracking 도입

- YOLO 단발 bbox 기반 이벤트를 track id 기반 이벤트로 전환한다.
- ByteTrack 또는 BoT-SORT 계열 적용을 검토한다.
- 일시적인 미검출 프레임에서도 같은 차량 이벤트가 유지되도록 한다.
- track TTL, max distance, ROI 조건을 명시적으로 설정한다.

## 3순위 TODO - 차량 bbox 후처리 강화

- ROI 밖 bbox 제거
- 너무 큰 bbox 제거
- 너무 작은 bbox 제거
- 가로세로비가 비정상적인 bbox 제거
- confidence만 보지 말고 면적, 위치, 중심점, 차로 영역을 함께 평가한다.
- preview 표시용 필터와 실제 이벤트 저장용 필터를 분리한다.

## 4순위 TODO - OCR 후처리 개선

- 한국 번호판 형식 점수 적용: `\d{2,3}[가-힣]\d{4}`
- 숫자-only 후보보다 번호판 형식에 맞는 한글 포함 후보를 우선한다.
- 자주 발생하는 오인식 보정 테이블을 둔다.
- OCR variant별 결과, confidence, 선택 사유를 debug log로 남긴다.
- plate crop 품질 점수와 OCR 결과를 함께 저장한다.

## 5순위 TODO - 산출 이미지 계약 정리

현재 API/DB에는 frame, plate crop, OCR image 중심으로 저장된다. 차량 정사각형 crop은 시연 흐름에서 사용되지만 API 계약상 명확한 필드로 분리되어 있지 않다.

추가 검토 필드:

- `frameImageUrl`
- `vehicleCropImageUrl`
- `plateCropImageUrl`
- `ocrImageUrl`
- `bestCandidateFrameNumber`
- `bestCandidateBbox`
- `processingStatus`

## 6순위 TODO - 평가 지표 만들기

- 차량 bbox recall/precision
- 번호판 bbox recall/precision
- OCR exact match accuracy
- stream-frame p50/p95 latency
- event finalize latency
- dropped frame count
- duplicate skipped count
- OCR failed count

## 권장 개선 순서

1. 실시간 bbox 응답과 OCR/DB 저장 분리
2. bbox tracking 도입
3. ROI/면적/비율 기반 차량 bbox 후처리
4. OCR 한국 번호판 후처리 강화
5. 산출 이미지/API 필드 정리
6. 평가셋과 latency 지표 기반 튜닝

