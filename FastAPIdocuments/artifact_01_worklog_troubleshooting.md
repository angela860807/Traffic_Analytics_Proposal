# 1번 산출물

## 작업 요약

### 1. 프로젝트 역할 및 범위 정리

차량흐름 분석시스템 팀 프로젝트에서 담당 범위를 FastAPI 서버 구축으로 정리했다. 서브 역할로 백엔드 및 AI 모델 개발을 고려했지만, 초기 단계에서는 FastAPI 서버를 중심으로 작업하기로 했다.

초기 설계서, 중복 감지 정책, 표준 네이밍 규칙, 혼잡수준 기준 문서 등을 참고하여 FastAPI가 담당할 범위를 다음과 같이 정리했다.

- 라즈베리파이 또는 카메라 클라이언트에서 이미지 수신
- 서버 PC에서 YOLO/OCR 모델 추론 예정
- 탐지 결과 JSON 생성
- 이미지 저장 및 접근 경로 제공
- 추후 Spring Boot 백엔드로 탐지 결과 전송
- 모델 및 백엔드 파일 수령 전까지 mock 기반 API 흐름 검증

라즈베리파이는 직접 추론하지 않고, 카메라 촬영 및 이미지 전송 역할만 담당하는 방향으로 정리했다. 실제 추론은 FastAPI 서버 PC에서 수행하는 구조로 결정했다.

### 2. 개발 환경 및 기본 구조 준비

VS Code와 PowerShell 기준으로 FastAPI 작업 환경을 구성했다.

주요 준비 항목은 다음과 같다.

- Python 가상환경 구성
- FastAPI, uvicorn 실행 환경 정리
- `.env` 및 `.env.example` 환경 변수 구조 정리
- `requirements.txt` 라이브러리 목록 확인
- FastAPI 실행 명령어 정리
- `/health` API를 통한 서버 상태 확인

기본 실행 방식은 다음 구조로 정리했다.

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\fastapi-server
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

라즈베리파이 등 외부 장비에서 접근할 때는 다음처럼 `0.0.0.0`으로 실행하는 방식을 정리했다.

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. FastAPI API 초안 구성

백엔드와 YOLO/OCR 모델이 아직 완성되지 않은 상태였기 때문에, 실제 모델 대신 mock 응답을 사용하여 FastAPI API 흐름을 먼저 구성했다.

구성한 주요 API는 다음과 같다.

- `GET /health`
  - FastAPI 서버 상태 확인

- `POST /api/detections/mock`
  - base64 JSON 이미지 기반 mock 탐지 결과 생성

- `POST /api/detections/image`
  - multipart 이미지 업로드 기반 mock 탐지 결과 생성

- `POST /api/detections/mock/send`
  - mock 탐지 결과를 생성한 뒤 Spring Boot 백엔드로 전송하는 테스트용 API

- `POST /api/camera/frame`
  - 라즈베리파이 카메라 프레임 preview 테스트용 이미지 수신

- `GET /api/camera/latest.jpg`
  - 최신 카메라 프레임 확인

- `GET /api/camera/live`
  - FastAPI PC 브라우저에서 라즈베리파이 카메라 프레임을 live preview로 확인

### 4. 요청 및 응답 구조 정리

FastAPI 내부 Python 코드는 `snake_case`를 사용하고, 외부 API JSON은 Spring Boot 및 Vue와 맞추기 위해 `camelCase`를 사용하는 방향으로 정리했다.

예시는 다음과 같다.

```text
Python 내부: camera_code, plate_number, confidence_score
API JSON: cameraCode, plateNumber, confidenceScore
```

주요 응답 필드는 다음처럼 정리했다.

- `cameraCode`
  - 카메라 코드

- `plateNumber`
  - 인식된 차량 번호
  - 인식 실패 시 `null`

- `detectionType`
  - `VEHICLE` 또는 `PLATE`

- `directionType`
  - `IN`, `OUT`, `BOTH`
  - 최종 방향 판단은 Spring Boot의 `Camera` 정보 기준으로 처리하는 방향

- `confidenceScore`
  - 탐지 신뢰도

- `imagePath`
  - FastAPI 서버 내부 저장 경로
  - DB 저장 및 추적용

- `imageUrl`
  - Vue 또는 브라우저에서 접근 가능한 이미지 URL

- `detectedAt`
  - 탐지 시각

### 5. 이미지 저장 정책 결정

이미지는 FastAPI 서버에서 저장하고, 저장 경로를 백엔드 DB에 공유하는 방향으로 정리했다.

단순히 로컬 파일 경로인 `imagePath`만 제공하면 Vue 브라우저에서 이미지를 직접 표시하기 어렵기 때문에, FastAPI에서 정적 파일 URL을 제공하도록 했다.

정리한 정책은 다음과 같다.

- `imagePath`
  - 서버 내부 파일 추적용 경로
  - DB 저장용

- `imageUrl`
  - 브라우저 및 Vue 화면 출력용 URL
  - 예: `/static/detections/2026/05/01/CAM_001_143632_frame.jpg`

팀 설명용 문장은 다음과 같이 정리했다.

```text
이미지는 FastAPI 서버가 저장하고, DB에는 저장 위치 추적을 위한 imagePath를 넘깁니다.
다만 Vue는 로컬 경로만으로 이미지를 표시할 수 없기 때문에, FastAPI가 정적 URL인 imageUrl도 함께 제공해서 브라우저에서 이미지를 바로 조회할 수 있게 했습니다.
```

### 6. directionType 처리 방향 결정

Spring Boot의 `Camera.java` Entity를 확인한 결과, 카메라 정보에 `directionType`이 포함되는 구조였다.

따라서 FastAPI가 직접 진입/진출 방향을 최종 판단하기보다, FastAPI는 `cameraCode`와 탐지 결과를 보내고 Spring Boot가 `cameraCode` 기준으로 카메라 정보를 조회하여 최종 `directionType`을 확정하는 방식이 더 적절하다고 판단했다.

정리한 역할 분담은 다음과 같다.

```text
FastAPI:
이미지 수신, YOLO/OCR 추론, 탐지 결과 생성

Spring Boot:
cameraCode 기준 Camera 정보 조회, directionType 최종 판단, DB 저장
```

현재 mock 응답의 `directionType = "IN"`은 임시값이며, 최종 병합 단계에서 Spring Boot 계약에 맞춰 조정하기로 했다.

### 7. 라즈베리파이 연동 방향 정리

라즈베리파이는 추론하지 않고 카메라 이미지를 촬영하여 FastAPI 서버로 전송하는 역할로 정리했다.

진행한 내용은 다음과 같다.

- 라즈베리파이 IP 확인
  - `192.168.10.116`

- WinSCP 및 원격 접속 흐름 확인

- 라즈베리파이에서 `capture.jpg` 저장 확인

- 라즈베리파이에서 FastAPI 서버로 이미지 전송 확인

- FastAPI 서버에서 `200 OK` 수신 확인

- 실제 캡처 이미지 저장 확인

- FastAPI PC에서 라즈베리파이 카메라 preview를 GUI처럼 브라우저로 확인하는 테스트 진행

라즈베리파이 관련 파일은 추후 정리하기로 하고, 현재 단계에서는 FastAPI 서버 브랜치에 직접 포함할지 여부를 보류했다.

### 8. 테스트 및 검증

FastAPI 단독 기능 기준으로 테스트를 작성하고 실행했다.

작성한 주요 테스트 항목은 다음과 같다.

- `/health` 정상 응답

- base64 이미지 탐지 요청 성공

- 잘못된 base64 요청 실패 처리

- multipart 이미지 업로드 성공

- 지원하지 않는 파일 형식 거부

- 깨진 이미지 파일 요청 거부

- Spring Boot 백엔드 연결 실패 시 503 응답 처리

검증 명령어는 다음과 같다.

```powershell
python -m compileall app
python -m pytest
```

최종 확인 시 가상환경 기준 테스트 결과는 다음과 같았다.

```text
7 passed
```

### 9. 문서화 작업

팀원 공유 및 다음 작업자를 위한 문서를 정리했다.

작성 또는 정리한 문서 성격은 다음과 같다.

- `README.md`
  - 실행 방법, API 테스트 방법, 환경 변수, 오류 응답 정리

- `NEXT_HANDOFF.md`
  - 다음 컨텍스트 또는 외부 PC 작업용 인수인계 문서

- `TEAM_SHARE_2026-05-04.md`
  - 팀 공유용 작업 요약

- `FASTAPI_STUDY_GUIDE.md`
  - 본인이 발표하거나 설명할 수 있도록 FastAPI 구조와 이론을 정리한 학습 문서

기존 `HANDOFF_FASTAPI_TODO.md`는 새로 작성한 `NEXT_HANDOFF.md`로 대체 가능하다고 정리했다.

### 10. Git 및 PR 준비

브랜치 병합 전 PR 작성 문구를 정리했다.

PR 제목 추천:

```text
feat: FastAPI 이미지 수신 및 Mock 탐지 파이프라인 구축
```

PR 설명에는 다음 내용을 포함하도록 정리했다.

- 작업 개요
- 주요 작업 내용
- API 요약
- 이미지 저장 정책
- 테스트 결과
- 후속 작업
- 리뷰 요청 사항

또한 `.gitignore` 위치와 역할별 관리 방식에 대해 논의했다.

결론은 다음과 같다.

- 루트 `.gitignore`는 팀 공통 ignore 관리에 적합

- FastAPI 전용 ignore는 `fastapi-server/.gitignore`로 분리 가능

- 팀 프로젝트에서는 충돌을 줄이기 위해 역할별 폴더 내부 `.gitignore`를 사용하는 것도 좋은 방식

PR 직전 `main`과 `woong` 브랜치 차이를 확인했으며, 최종 확인 시 코드 오류는 없었고 테스트도 통과했다.

다만 `main` 대비 차이가 이미지 샘플 및 런타임 저장 이미지 위주로 잡히는 것을 확인했다.

현재는 샘플 파일이므로 유지해도 되지만, 최종 제출 전에는 다음 항목을 정리하는 것을 추천했다.

- `fastapi-server/sample.jpg`
- `fastapi-server/storage/detections/.../*.jpg`

`fastapi-server/samples/sample.jpg`는 테스트 샘플로 남길 수 있으나, 최종 정책에 따라 제거 가능하다.

## 트러블슈팅 로그

### 1. `/api/detections/mock/send` Internal Server Error

#### 상황

PowerShell에서 다음 요청을 실행했을 때 Internal Server Error가 발생했다.

```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/detections/mock/send" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

#### 원인

`/mock/send` API는 mock 탐지 결과를 생성한 뒤 Spring Boot 백엔드로 전송하는 API이다. 당시 Spring Boot 백엔드 서버 또는 해당 API가 준비되지 않아 연결 과정에서 오류가 발생했다.

#### 해결

백엔드 연결 실패를 FastAPI에서 처리하도록 예외 응답을 정리했다.

정리된 오류 응답:

```text
Spring Boot API is not reachable
```

또한 백엔드 연동이 필요한 API와 FastAPI 단독 검증 API를 구분해서 사용하도록 정리했다.

FastAPI 단독 테스트:

```text
POST /api/detections/mock
POST /api/detections/image
```

백엔드 전송 포함 테스트:

```text
POST /api/detections/mock/send
```

### 2. `/api/detections/mock` 요청에서 body 누락 오류

#### 상황

PowerShell에서 base64 mock detection 요청 시 다음 오류가 발생했다.

```text
{"detail":[{"type":"missing","loc":["body"],"msg":"Field required","input":null}]}
```

#### 원인

요청 body가 제대로 전달되지 않았거나, `$body` 변수가 올바르게 생성되지 않은 상태에서 API를 호출했다.

#### 해결

이미지를 base64 문자열로 변환하고 JSON body를 다시 생성한 뒤 요청했다.

정리한 요청 방식:

```powershell
$imageBytes = [System.IO.File]::ReadAllBytes((Resolve-Path ".\sample.jpg"))

$body = @{
    cameraCode = "CAM_001"
    capturedAt = "2026-04-30T10:30:00"
    imageBase64 = [Convert]::ToBase64String($imageBytes)
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/detections/mock" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

정상 응답을 확인했다.

### 3. multipart 테스트에서 sample image 경로 오류

#### 상황

multipart 이미지 업로드 테스트 중 다음 오류가 발생했다.

```text
Get-Item : 'C:\path\to\sample.jpg' 경로는 존재하지 않으므로 찾을 수 없습니다.
```

#### 원인

예시 경로인 `C:\path\to\sample.jpg`를 실제 파일 경로로 바꾸지 않고 그대로 사용했다.

#### 해결

실제 존재하는 `sample.jpg` 또는 `samples/sample.jpg`를 사용하도록 수정했다.

예시:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/detections/image" `
    -F "cameraCode=CAM_001" `
    -F "capturedAt=2026-04-30T10:30:00" `
    -F "image=@sample.jpg;type=image/jpeg"
```

정상 응답을 확인했다.

### 4. PowerShell `Invoke-RestMethod -Form` 미지원 문제

#### 상황

multipart 요청을 PowerShell에서 실행할 때 다음 오류가 발생했다.

```text
Invoke-RestMethod : 매개 변수 이름 'Form'과(와) 일치하는 매개 변수를 찾을 수 없습니다.
```

#### 원인

사용 중인 Windows PowerShell 버전에서 `Invoke-RestMethod -Form` 옵션을 지원하지 않았다.

#### 해결

multipart 요청은 `curl.exe`를 사용하는 방식으로 정리했다.

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/detections/image" `
    -F "cameraCode=CAM_001" `
    -F "capturedAt=2026-04-30T10:30:00" `
    -F "image=@samples/sample.jpg;type=image/jpeg"
```

### 5. `python -m pytest` 실행 시 테스트 0개 수집

#### 상황

초기 테스트 실행 시 다음 결과가 나왔다.

```text
collected 0 items
no tests ran
```

#### 원인

아직 테스트 파일이 없거나, pytest가 인식할 수 있는 파일명 규칙을 따르는 테스트 파일이 준비되지 않았다.

#### 해결

`tests/test_detection_api.py`를 작성했다.

이후 테스트 항목이 수집되고 정상 실행되었다.

최종 결과:

```text
7 passed
```

### 6. `scripts/create_sample_image.py` 파일 없음

#### 상황

다음 명령 실행 시 파일을 찾을 수 없다는 오류가 발생했다.

```powershell
python scripts/create_sample_image.py
```

오류:

```text
can't open file '...\scripts\create_sample_image.py': [Errno 2] No such file or directory
```

#### 원인

샘플 이미지를 생성하는 스크립트가 아직 작성되지 않았다.

#### 해결

`scripts/create_sample_image.py`를 작성하여 테스트용 샘플 이미지를 생성하도록 했다.

실행 결과 `samples/sample.jpg`가 생성되었다.

### 7. 라즈베리파이 예제 client 연결 거부

#### 상황

다음 예제 실행 시 연결 거부 오류가 발생했다.

```powershell
python examples/raspberry_pi_base64_client.py
python examples/raspberry_pi_multipart_client.py
```

오류 의미:

```text
대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다
```

#### 원인

FastAPI 서버가 실행 중이지 않거나, 라즈베리파이 또는 예제 client가 접근하는 서버 주소와 포트가 맞지 않았다.

#### 해결

FastAPI 서버를 먼저 실행한 뒤 예제 client를 다시 실행했다.

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

외부 장비 접근 시:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

이후 base64 client와 multipart client 모두 정상 응답을 확인했다.

### 8. `rasberry` / `raspberry` 파일명 오타

#### 상황

라즈베리파이 예제 파일명이 `rasberry_pi_base64_client.py`, `rasberry_pi_multipart_client.py`처럼 작성되었다.

#### 원인

`raspberry`의 철자에서 `p`가 빠진 파일명이 사용되었다.

#### 처리

기능상 오류는 아니므로 즉시 수정하지 않고, 최종 정리 시 파일명 수정 후보로 남겼다.

### 9. README 한글 깨짐처럼 보이는 문제

#### 상황

PowerShell에서 `README.md`를 `Get-Content`로 확인했을 때 한글이 깨진 것처럼 보였다.

#### 원인

파일 자체가 깨진 것이 아니라 PowerShell 콘솔 인코딩 표시 문제일 가능성이 높았다.

#### 확인

Python UTF-8 기준으로 파일을 읽어보면 정상적으로 읽히는 것을 확인했다.

#### 처리

문서 파일은 UTF-8 기준으로 유지하고, PowerShell 표시 문제로 판단했다.

### 10. `python -m pytest`에서 pytest 모듈 없음

#### 상황

브랜치 검사 중 기본 Python으로 테스트를 실행했을 때 다음 오류가 발생했다.

```text
No module named pytest
```

#### 원인

시스템 기본 Python에는 pytest가 설치되어 있지 않았고, 프로젝트 가상환경에는 pytest가 설치되어 있었다.

#### 해결

가상환경 Python으로 테스트를 실행했다.

```powershell
.\.venv\Scripts\python.exe -m pytest
```

결과:

```text
7 passed
```

### 11. main과 브랜치 차이가 이미지 파일만 남은 문제

#### 상황

PR 전 `main`과 `woong` 브랜치 차이를 확인했을 때 코드가 아니라 이미지 파일만 차이로 잡혔다.

확인된 파일:

```text
fastapi-server/sample.jpg
fastapi-server/samples/sample.jpg
fastapi-server/storage/detections/.../*.jpg
```

#### 의미

FastAPI 코드와 문서 작업은 이미 `main`에 대부분 반영된 상태로 보이며, 남은 차이는 샘플 이미지 및 런타임 저장 이미지였다.

#### 처리 방향

현재 학원 프로젝트 단계에서는 샘플 파일이 테스트 재현에 도움이 되므로 당장은 유지해도 된다고 판단했다.

다만 최종 제출 전에는 다음처럼 정리하는 것을 추천했다.

- `storage/detections/` 런타임 이미지 제거
- 루트의 `sample.jpg` 제거
- `samples/sample.jpg`는 테스트 정책에 따라 유지 또는 제거
- `.gitignore`에 런타임 이미지 제외 규칙 유지

### 12. `.gitignore` 위치와 충돌 가능성

#### 상황

`.gitignore`가 `fastapi-server` 폴더 밖 또는 루트에 있을 경우, 다른 팀원 브랜치와 충돌할 수 있는지 논의했다.

#### 정리

루트 `.gitignore`는 저장소 전체 공통 규칙을 관리하는 정상적인 위치이다. 다만 여러 팀원이 동시에 수정하면 충돌은 발생할 수 있다.

추천 구조:

```text
루트 .gitignore
→ IDE, OS, 로그 등 팀 공통 ignore

fastapi-server/.gitignore
→ Python 가상환경, cache, storage, samples 등 FastAPI 전용 ignore

backend/.gitignore 또는 backend/traffic/.gitignore
→ Spring Boot build, out, .gradle 등 백엔드 전용 ignore

frontend/.gitignore
→ node_modules, dist 등 Vue 전용 ignore
```

학원 프로젝트 기준으로는 루트 `.gitignore`에 모든 내용을 몰아넣기보다, 역할별 폴더 안에 전용 `.gitignore`를 두는 방식이 충돌을 줄일 수 있다고 정리했다.

## 이후 작업 대기 항목

현재 FastAPI 단독 구조는 검증이 완료된 상태이며, 다음 작업은 외부 파트 파일 수령 후 진행한다.

### YOLO/OCR 모델 수령 후

- 모델 파일 확장자 확인
- 입력 이미지 크기 확인
- YOLO 출력 구조 확인
- class label 확인
- bounding box 좌표 형식 확인
- OCR 입력이 원본인지 crop인지 확인
- OCR 출력이 문자열만인지 confidence 포함인지 확인
- `PlateDetector` 실제 구현
- `PlateRecognizer` 실제 구현
- `InferenceService`에서 crop 및 OCR 흐름 연결

### Spring Boot 백엔드 파일 수령 후

- API 경로 확인
- DTO 필드명 확인
- enum 값 확인
- 날짜 형식 확인
- 응답 형식 확인
- FastAPI 내부 스키마 alias 또는 변환 계층에서 백엔드 필드명에 맞춤
- `BackendClient` 최종 수정
- FastAPI-Spring Boot 통합 테스트

### 최종 제출 전

- runtime image 정리
- sample image 정책 확정
- `.gitignore` 최종 확인
- README 최신화
- PR 설명 최신화
- 테스트 재실행

