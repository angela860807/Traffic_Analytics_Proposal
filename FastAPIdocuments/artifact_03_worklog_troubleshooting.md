# 3번 산출물

## 작업 요약

- FastAPI 프로젝트의 `README.md`와 `NEXT_HANDOFF.md`를 확인해 현재 AI 서버 역할, API 흐름, 보류 사항을 파악했다.
- FastAPI 내부 구조를 확인해 `routes`, `schemas`, `services`, `config` 중심으로 구성되어 있음을 확인했다.
- 기존 API 흐름이 base64 mock detection, multipart image detection, camera live preview로 나뉘어 있음을 확인했다.
- `.venv` 기준 `python -m compileall app`와 `python -m pytest`를 실행해 기존 테스트 통과 상태를 확인했다.
- YOLO `.pt` 파일은 번호판 bbox 탐지, OCR은 번호판 문자 인식 역할로 분리하는 방향을 정리했다.
- `ocr01_paddle.py`, `ocr02_paddle.py`를 검토해 YOLO 탐지 후 번호판 crop을 PaddleOCR로 인식하는 구조를 확인했다.
- YOLO/OCR 연동 준비를 위해 `PlateDetector`, `PlateRecognizer`, `InferenceService` 수정 방향을 정리했다.
- 번호판 crop 처리를 위한 `plate_cropper.py` 추가 방향을 정리했다.
- YOLO/OCR 관련 환경변수와 의존성 추가 항목을 정리했다.
- 사용자가 YOLO/OCR 준비 코드를 직접 수정한 뒤 변경 상태를 검토했다.
- `ocr03_paddle.py`를 검토해 개선된 OCR 전처리 방식을 확인했다.
- `ocr03_paddle.py`의 2배 확대, Gaussian blur, adaptive threshold 전처리 방식을 FastAPI 구조에 반영했다.
- OCR 전처리 설정값 `OCR_PREPROCESS_SCALE`, `OCR_ADAPTIVE_BLOCK_SIZE`, `OCR_ADAPTIVE_C`를 추가했다.
- `SAVE_PLATE_CROP` 옵션으로 전처리된 번호판 crop 저장을 선택 가능하게 준비했다.
- YOLO/OCR 반영 후 `python -m compileall app` 검증을 수행했다.
- YOLO/OCR 반영 후 `.venv` 기준 `python -m pytest`를 실행해 테스트 통과를 확인했다.
- Internal API Key 연동 가이드를 검토했다.
- FastAPI에서 백엔드 호출 시 `X-Internal-Api-Key` 헤더를 추가해야 함을 확인했다.
- `cameraId` 대신 `cameraCode`를 백엔드 DTO에서 받는 방향이 더 적합하다고 판단했다.
- 백엔드가 `cameraCode`로 `Camera`를 조회하고 `Camera.directionType` 기준으로 IN/OUT을 판단하는 방향을 정리했다.
- API key 관련 FastAPI 수정 예시 코드를 정리해 전달했다.
- `/mock/send`는 Spring Boot 병합 테스트용 전송 엔드포인트로 유지하면 된다고 검토했다.
- 백엔드에 전달할 수정 요청 요약 문서 `BACKEND_REQUEST_SUMMARY.md`를 작성했다.
- 백엔드 답변을 반영해 `imageUrl`은 선택값, 나머지 DTO 필드는 필수, `plateNumber=null`은 불가 정책으로 정리했다.
- Spring Boot 수정 완료 후 진행할 작업 순서를 FastAPI-Spring Boot 통신, `/mock/send` 테스트, `/image/send` 추가, 실제 모델 테스트 순으로 정리했다.

## 트러블 슈팅 로그

- `rg --files` 실행 시 `rg.exe` 접근 권한 오류가 발생해 PowerShell `Get-ChildItem` 기반 탐색으로 대체했다.
- `README.md`와 `NEXT_HANDOFF.md`를 기본 인코딩으로 읽었을 때 한글이 깨져 `Get-Content -Encoding UTF8`로 다시 읽어 해결했다.
- 전체 파일 탐색 시 `.venv` 내부 파일이 너무 많아 타임아웃이 발생해 `.venv`, `.pytest_cache`, `storage` 등을 제외하고 앱 파일만 좁혀 확인했다.
- 전역 Python에서 `python -m pytest` 실행 시 `No module named pytest`가 발생해 프로젝트 `.venv`의 Python으로 테스트를 실행했다.
- 사용자가 수정한 중간 상태에서 `inference_service.py`가 `crop_plate_with_padding()`을 호출하지만 import와 구현 파일이 없어 보완 필요 사항으로 확인했다.
- `plate_recognizer.py`가 `PlateRecognizer` 클래스가 아닌 dataclass 형태로 잘못 구성된 상태를 확인하고 전체 교체 방향을 안내했다.
- YOLO/OCR 모델이 아직 최종 확정되지 않아 실제 추론 완료가 아니라 교체 가능한 어댑터 구조를 준비하는 방향으로 정리했다.
- `ocr01_paddle.py`와 `ocr02_paddle.py` 차이는 padding 및 중복 bbox 처리 여부임을 확인하고, FastAPI에는 crop과 전처리를 별도 서비스로 분리하는 방향을 잡았다.
- `ocr03_paddle.py`에서 인식률 개선 포인트가 OCR 전처리임을 확인하고 기존 fixed threshold 방식 대신 adaptive threshold 방식을 반영했다.
- Internal API Key 연동 코드를 한 차례 직접 반영했으나, 사용자가 직접 수정하기를 원해 해당 변경을 되돌리고 코드 예시만 전달했다.
- API key 테스트 추가 과정에서 mock `httpx.Response`에 request 객체가 없어 `raise_for_status()` 호출 시 오류가 발생했으며, 실제 응답 형태에는 request 객체가 필요함을 확인했다.
- 백엔드 DTO의 `cameraId` 요구사항은 FastAPI와 Raspberry Pi 입력 기준인 `cameraCode`와 맞지 않아, 백엔드가 `cameraCode`를 받고 내부에서 `Camera`를 조회하는 방향으로 협의했다.
- 백엔드에서 `plateNumber=null` 불가 정책이 확정되어 OCR 실패 결과는 Spring Boot로 전송하지 않는 방향으로 정리했다.
- `imageUrl`은 백엔드 DTO에서 선택값으로 확정되어 FastAPI 전송 시 `exclude_none=True`를 사용하는 방향을 정리했다.

## 다음 작업

- 백엔드 수정 완료 후 FastAPI의 `backend_client.py`에 Internal API Key 헤더를 실제 반영한다.
- `.env`와 `.env.example`에 `SPRING_DETECTION_PATH=/api/v1/detection-logs`와 `BACKEND_INTERNAL_API_KEY`를 설정한다.
- `/api/detections/mock/send`로 FastAPI-Spring Boot 통신과 DB 저장 여부를 먼저 검증한다.
- 실제 이미지 기반 운영 흐름을 위해 `/api/detections/image/send` 추가를 검토한다.
- 최종 YOLO `.pt` 모델 파일을 받은 뒤 `MODEL_PATH`를 설정하고 샘플 이미지로 런타임 테스트를 진행한다.
