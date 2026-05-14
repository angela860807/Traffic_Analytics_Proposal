# 로컬 테스트 미디어

이 디렉터리는 git에 올리지 않는 로컬 전용 공간이다.
실제 차량 이미지, 큰 테스트 영상, smoke test 산출물처럼 저장소에 포함하면 안 되는 파일을 여기에 둔다.

- `images/positive`: `FLOW_EVENT_CREATED`가 기대되는 번호판 이미지
- `images/negative`: `OCR_FAILED`가 기대되는 번호판 없음/미인식 이미지
- `videos`: 로컬 테스트 영상 또는 RTSP 캡처 파일
- `smoke-runs`: 수동 smoke test 중 생긴 임시 파일
- `model-feedback/false-positive`: 번호판이 아닌데 번호판으로 잘못 잡힌 오탐 샘플
- `model-feedback/false-negative`: 번호판이 있는데 놓친 미탐 샘플

커밋해도 되는 작은 합성 fixture만 `fastapi-server/samples` 아래에 둔다.
