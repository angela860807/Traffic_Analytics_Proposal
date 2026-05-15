# 4번 산출물

## 작업 요약

### 1. FastAPI - Spring Boot - PostgreSQL 1차 연동 확인

- FastAPI에서 Spring Boot로 탐지 결과를 전송하고, Spring Boot가 PostgreSQL에 저장하는 흐름을 검수했다.
- `POST /api/detections/mock/send` 전송 테스트로 FastAPI -> Spring Boot -> DB 저장 흐름이 정상 동작하는 것을 확인했다.
- Spring Boot 조회 API `GET /api/v1/detection-logs`가 프론트/테스트에서 접근 가능하도록 임시 GET 허용 규칙을 추가했다.
- `DetectionResponse`에 `directionType`, `imagePath`, `imageUrl` 등 프론트 표시와 연동에 필요한 응답 필드를 확인했다.

### 2. Vue 프론트 1차 병합 및 API 연결

- Vue/Vite 프론트 구조를 확인하고, 디자인은 건드리지 않고 데이터 연결부만 수정했다.
- 공통 API 호출을 위해 `trafficAS-b/src/api/client.js`를 사용하도록 정리했다.
- `DashboardView.vue`에서 최근 탐지 로그, 입출차 flow count, zones, cameras, hourly stats 조회를 연결했다.
- hourly stats 데이터가 없을 때는 기존 mock 차트를 유지하도록 처리했다.
- 이미지 URL은 화면 디자인 변경 없이 `plates` 데이터 객체에 `imagePath`, `imageUrl`로 보존하도록 연결했다.

### 3. Docker Compose 통합

- 기존 `postgres-db`, `spring-backend`, `fastapi-server` 구성에 Vue 프론트 `frontend` 서비스를 추가했다.
- 프론트는 `Node build -> nginx 정적 파일 서빙` 구조의 Dockerfile로 구성했다.
- nginx 설정에서 `/api`는 Spring Boot, `/static`과 `/ws`는 FastAPI로 프록시하도록 구성했다.
- `docker compose up -d --build`로 전체 컨테이너 빌드 및 실행을 확인했다.
- 프론트는 `http://localhost:5173`, Spring Boot는 `http://localhost:8080`, FastAPI는 `http://localhost:8000` 기준으로 동작하도록 정리했다.

### 4. 회원가입/로그인 및 기본 계정 정리

- Spring Boot 회원가입 비밀번호 정책을 기존 `8자 이상 + 영문 + 숫자 + 특수문자`에서 `4자 이상`으로 완화했다.
- 프론트 회원가입 화면과 모달의 비밀번호 안내 및 검증 조건도 `4자 이상`으로 맞췄다.
- `data.sql`에 기본 일반 사용자와 관리자 계정을 자동 생성하도록 추가했다.
- 기본 계정은 `user1@email.com / 1234`, `admin@email.com / 1234`이다.
- 프론트 로그인은 기존 브라우저 `localStorage` 계정 조회 방식에서 Spring `/api/auth/login` 호출 방식으로 변경했다.
- 로그인 성공 시 JWT `accessToken`, `refreshToken`을 localStorage에 저장하고, JWT의 `ROLE_ADMIN`으로 관리자 여부를 판단하도록 수정했다.

### 5. 라즈베리파이 연동 준비

- 다음 단계 목표를 라즈베리파이에서 Windows PC의 FastAPI 서버 `:8000`으로 실제 카메라 프레임을 POST하는 것으로 정리했다.
- FastAPI Dockerfile이 `uvicorn app.main:app --host 0.0.0.0 --port 8000`으로 실행되며, compose에서도 `8000:8000` 포트가 열려 있음을 확인했다.
- 라즈베리파이 전송 후보 API를 정리했다.
- 실제 이미지 분석: `POST /api/detections/image`
- 실제 이미지 분석 후 Spring 전송: `POST /api/detections/image/send`
- base64 mock 전송: `POST /api/detections/mock/send`
- 새 채팅 인수인계용 문서 `HANDOFF_RASPBERRY_PI.md`를 작성했다.

## 트러블 슈팅 로그

### 1. `GET /api/v1/detection-logs` 403 Forbidden

증상:

- FastAPI mock 전송은 성공했지만 Spring 조회 API 호출 시 `403 Forbidden` 발생.
- `X-Internal-Api-Key` 헤더를 붙여도 GET 조회는 계속 403 발생.

원인:

- Spring Security에서 `POST /api/v1/detection-logs`만 허용되어 있었고, 프론트/테스트용 GET 조회는 인증이 필요한 상태였다.

조치:

- `SecurityConfig.java`에 Vue 1차 연동용 임시 GET 허용 규칙을 추가했다.
- 대상: `/api/v1/detection-logs/**`, `/api/flow-events/stats/count`, `/api/zones`, `/api/cameras`, `/api/stats/hourly`
- 나중에 JWT 연동 후 삭제할 수 있도록 `TODO(frontend-integration)` 주석을 남겼다.

결과:

- detection logs, zones, cameras, flow count 조회가 403 없이 동작했다.

### 2. Vue API 호출 경로 및 Vite proxy 혼선

증상:

- 프론트 API 호출이 Vite proxy를 타야 하는데 `.env`의 `VITE_API_BASE_URL=http://127.0.0.1:8080` 때문에 직접 Spring으로 요청되는 상태가 있었다.

원인:

- Docker/nginx 환경과 Vite dev 환경에서 API base URL 전략이 섞였다.
- 브라우저 입장에서는 `localhost:5173`과 `127.0.0.1:8080`이 서로 다른 origin이다.

조치:

- Docker/nginx 환경에서는 `VITE_API_BASE_URL=`로 비워 `/api` 상대경로를 사용하도록 정리했다.
- nginx가 `/api`를 Spring Boot로 프록시하도록 구성했다.

결과:

- `http://localhost:5173/api/...` 형태로 같은 origin에서 API 호출이 가능해졌다.

### 3. CORS preflight 403

증상:

- 브라우저 Network 탭에서 `content-type: application/json`, `referer: http://localhost:5173/` 요청에 대해 `403 Forbidden` 발생.
- 응답 헤더에 `vary: Origin`, `Access-Control-Request-Method`, `Access-Control-Request-Headers`가 보였다.

원인:

- 프론트가 `localhost:5173`에서 실행 중인데 API를 `127.0.0.1:8080`으로 직접 호출하면서 CORS preflight가 발생했다.
- Spring Security에 명시적인 CORS 허용 설정이 없었다.

조치:

- `.env`의 `VITE_API_BASE_URL`, `VITE_FASTAPI_BASE_URL`을 빈 값으로 변경했다.
- `SecurityConfig.java`에 CORS 설정을 추가했다.
- 허용 origin: `http://localhost:5173`, `http://127.0.0.1:5173`
- 허용 method: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`
- 허용 header: `Authorization`, `Content-Type`, `X-Internal-Api-Key`
- `OPTIONS /**`를 permitAll 처리했다.

결과:

- `OPTIONS /api/auth/login` preflight가 200으로 응답했다.
- `localhost:5173` 경유 로그인과 `8080` 직접 호출 모두 정상 동작했다.

### 4. 프론트 로그인 실패: DB에는 계정이 있는데 없는 정보로 표시

증상:

- DB `members`에는 계정이 존재하지만 프론트에서 `admin@email.com / 1234` 로그인 시 없는 정보처럼 표시됐다.

원인:

- `useAuth.js`의 `signup()`은 Spring API로 바뀌었지만, `login()`은 여전히 브라우저 `localStorage tas_users`에서 계정을 찾고 있었다.

조치:

- `useAuth.js`의 `login()`을 `/api/auth/login` 호출 방식으로 변경했다.
- 로그인 성공 시 JWT를 저장하고, JWT payload의 `auth` 값이 `ROLE_ADMIN`이면 관리자 권한으로 판단하도록 수정했다.
- `LoginView.vue`, `AuthModal.vue`에서 `await login(...)`을 사용하도록 수정했다.

결과:

- `user1@email.com / 1234`, `admin@email.com / 1234` 모두 프론트 nginx 경유 API 로그인 성공.

### 5. 회원가입 성공처럼 보이지만 DB `members`에 없음

증상:

- 프론트에서 회원가입을 했는데 `select * from members;` 조회 시 데이터가 없었다.

원인:

- 기존 프론트 회원가입 로직이 Spring API가 아니라 브라우저 `localStorage`에만 저장하고 있었다.

조치:

- `signup()`을 Spring `/api/auth/signup` 호출 방식으로 바꿨다.
- 이후 DB 저장은 Spring Boot가 담당하도록 정리했다.

결과:

- 프론트 가입 흐름이 DB 저장 구조로 연결될 수 있게 되었다.

### 6. 비밀번호 정책 불일치

증상:

- 프론트는 6자 이상만 검사했지만 Spring은 8자 이상, 영문, 숫자, 특수문자 조합을 요구했다.

원인:

- 백엔드 `SignupRequest`와 프론트 입력 검증 기준이 달랐다.

조치:

- 백엔드는 `@Pattern` 대신 `@Size(min = 4)`로 변경했다.
- 프론트 `SignupView.vue`, `AuthModal.vue`의 안내 문구와 검증 조건을 `4자 이상`으로 변경했다.

결과:

- `1234` 같은 4자 비밀번호가 회원가입/로그인 정책상 허용되었다.

### 7. `data.sql` 기본 계정 자동 생성

요구:

- Docker compose up 시 기본 일반 사용자와 관리자 계정을 자동 생성해야 했다.

조치:

- `backend/traffic/src/main/resources/data.sql`에 `members` insert를 추가했다.
- 비밀번호는 평문이 아니라 BCrypt 해시로 저장했다.
- 중복 실행 시 에러가 나지 않도록 `ON CONFLICT DO NOTHING`을 사용했다.

결과:

- 컨테이너 재기동 후 DB에서 두 계정이 조회되었다.
- 두 계정 모두 `1234`로 로그인 성공했다.

### 8. Docker 프론트 추가 및 nginx proxy

증상/요구:

- 백엔드, FastAPI, DB 외에 프론트도 Docker로 실행해야 했다.

조치:

- `trafficAS-b/Dockerfile` 추가.
- `trafficAS-b/nginx.conf` 추가.
- `trafficAS-b/.dockerignore` 추가.
- `docker-compose.yml`에 `frontend` 서비스 추가.

결과:

- `traffic-frontend` 컨테이너가 `5173:80`으로 실행되었다.
- `http://localhost:5173`에서 프론트 접속 가능.
- `/api` 프록시로 Spring Boot API 호출 가능.

### 9. nginx 502 Bad Gateway

증상:

- 프론트 nginx 경유 `/api/auth/login` 호출 시 간헐적으로 `502 Bad Gateway` 발생.

원인:

- Docker compose에서 컨테이너는 시작되었지만 Spring Boot 애플리케이션이 완전히 기동되기 전에 nginx가 요청을 전달했다.
- Spring 로그상 `Started TrafficApplication` 이전 요청에서 upstream connection refused가 발생했다.

조치:

- Spring Boot 로그의 `Started TrafficApplication` 출력 이후 재시도했다.

결과:

- Spring 완전 기동 후 같은 요청이 정상 성공했다.

### 10. hourly stats 빈 배열

증상:

- `/api/stats/hourly?statDate=...&zoneId=1` 호출은 성공하지만 빈 배열이 반환됐다.

원인:

- 해당 날짜/zone의 집계 row가 DB에 없었다.

조치:

- 프론트에서 hourly stats가 없거나 전체 값이 0이면 기존 mock chart를 유지하도록 처리했다.

결과:

- 통계 데이터가 없어도 화면이 깨지지 않았다.

### 11. PowerShell `npm` 실행 정책 문제

증상:

- PowerShell에서 `npm` 직접 실행 시 execution policy 문제 가능성이 있었다.

조치:

- Windows PowerShell에서는 `npm.cmd run build`, `npm.cmd run dev` 형태를 사용했다.

결과:

- Vue build가 정상 실행되었다.

### 12. `rg.exe` Access denied

증상:

- 일부 검색 작업에서 `rg.exe` 실행이 `Access is denied`로 실패했다.

조치:

- PowerShell `Get-ChildItem`과 `Select-String`으로 대체 검색했다.

결과:

- 코드 위치 및 설정 검색을 계속 진행할 수 있었다.

## 라즈베리파이 다음 단계 체크리스트

1. Windows PC LAN IP 확인

```powershell
ipconfig
```

2. PC에서 FastAPI 외부 접근 확인

```powershell
Invoke-RestMethod http://127.0.0.1:8000/docs
Invoke-RestMethod http://<PC_LAN_IP>:8000/docs
```

3. 라즈베리파이에서 FastAPI 접근 확인

```bash
curl -I http://<PC_LAN_IP>:8000/docs
```

4. 실제 이미지 분석 후 Spring DB 저장까지 확인

```bash
curl -X POST "http://<PC_LAN_IP>:8000/api/detections/image/send" \
  -F "cameraCode=CAM_001" \
  -F "capturedAt=2026-05-08T15:30:00" \
  -F "image=@frame.jpg;type=image/jpeg"
```

5. DB 저장 확인

```powershell
docker exec traffic-postgres psql -U postgres -d traffic -c "select log_id, plate_number, camera_id, image_path, image_url, confidence_score, detected_at from detection_logs order by log_id desc limit 5;"
```

## 새 컨텍스트 시작 메모

- 작업 폴더: `C:\jwdev\Traffic_Analytics_Proposal`
- 프론트: `http://localhost:5173`
- Spring Boot: `http://localhost:8080`
- FastAPI: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- 기본 관리자: `admin@email.com / 1234`
- 기본 사용자: `user1@email.com / 1234`
- 다음 핵심 작업: 라즈베리파이에서 PC LAN IP의 FastAPI `:8000`으로 카메라 프레임 POST 테스트
