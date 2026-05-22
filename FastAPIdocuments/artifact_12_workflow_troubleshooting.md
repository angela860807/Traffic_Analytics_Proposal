# Artifact 12 - Frontend Merge Workflow & Troubleshooting

작성일: 2026-05-21

## 1. 문서 목적

이번 컨텍스트에서는 프론트 파일을 받은 뒤 `review` 화면을 Spring 과속 단속 API와 맞추고, 이미지/번호판 crop 표시, OCR 신뢰도 표시, 2차 검증 버튼 정책, DB 상태 제약조건 문제를 정리했다.

이 문서는 다음 컨텍스트에서 병합 작업을 이어갈 때 왜 현재 코드가 이렇게 되어 있는지 빠르게 따라올 수 있도록 workflow와 troubleshooting 중심으로 정리한다.

관련 문서:

- `FastAPIdocuments/artifact_11_context_workflow_troubleshooting.md`
- `FastAPIdocuments/frontend_speed_api_contract.md`
- `FastAPIdocuments/artifact_12_next_context_merge_TODO.md`

## 2. 전체 Workflow

### 1단계. 프론트 파일 수령 후 기존 산출물 검수

프론트 파일을 받은 뒤 먼저 다음 문서를 기준으로 병합 방향을 확인했다.

- `artifact_11_context_workflow_troubleshooting.md`
- `frontend_speed_api_contract.md`

초기 판단:

- 백엔드 API 필드명은 정의서 기준으로 맞게 작성되어 있었으므로 백엔드를 프론트 이름에 맞춰 바꾸지 않는다.
- 프론트에서 API 응답 필드를 매핑하는 방향으로 정리한다.
- 프론트 레이아웃은 팀원이 크게 바꿨지만, 병합 전 TODO의 핵심은 동일하다.

### 2단계. Vue dev server 포트와 403 Forbidden 정리

프론트 dev server가 `localhost:5174`로 뜨는 상황이 확인되었다.

조치:

- Spring Security CORS 허용 origin에 `http://localhost:5174`를 포함했다.
- 과속 단속 조회/상태변경 API는 프론트 병합 검증을 위해 임시 permit 처리했다.
- `/api/speed-violations/**` 조회와 `/api/speed-violations/*/status` 상태 변경이 프론트에서 호출 가능하도록 정리했다.

주의:

- JWT/Auth가 실제로 연결되면 이 permit 정책은 다시 권한 기반으로 정리해야 한다.

### 3단계. review 페이지를 실제 Spring API에 연결

`ReviewView.vue`는 기존 seed/localStorage 기반 이벤트 대신 Spring 과속 단속 API를 조회하도록 바꿨다.

주요 변경:

- `GET /api/speed-violations?start&end`로 날짜별 과속 이벤트 조회
- `PATCH /api/speed-violations/{violationId}/status`로 상태 변경
- 공통 axios client 기반 API 모듈 사용
- 로딩, 빈 값, 오류 메시지 표시 추가
- 선택 이벤트가 새로고침 후에도 목록에 있으면 유지

관련 파일:

- `trafficAS-b/src/api/client.js`
- `trafficAS-b/src/api/speedViolations.js`
- `trafficAS-b/src/views/admin/ReviewView.vue`

### 4단계. 캡처 이미지와 번호판 crop 이미지 표시

프론트 상세 화면에서 기존 하드코딩 영상(`/0513.mp4`)이 이미지 없는 이벤트에 재생되는 문제가 있었다.

조치:

- 하드코딩 mp4 fallback 제거
- 실시간/캡처 탭 중 실시간 탭 제거
- 최근 단속 3건 UI 제거
- 저장된 캡처 이미지가 없으면 이미지 없음 placeholder 표시
- `violationImagePath`를 `/static/detections/YYYY/MM/DD/...` 형태로 변환
- 번호판 crop은 `*_frame.jpg` 기준으로 `*_plate_crop.jpg`를 추론
- Vite proxy에서 `/static/detections`를 FastAPI 정적 파일 경로로 전달

관련 파일:

- `trafficAS-b/src/views/admin/ReviewView.vue`
- `trafficAS-b/vite.config.js`

### 5단계. OCR 신뢰도 표시 정책 정리

DB의 `detection_analysis_results.confidence_score`는 0~1 범위 값이다.

프론트 표시 정책:

- API/DB 내부 값은 0~1 그대로 유지
- 화면에서는 `confidenceScore * 100`
- 소수점 1자리까지 표시
- 예: `0.934` -> `93.4%`

추가로 review 상단 OCR 평균 값도 0~1 평균을 100 곱해서 `%`로 표시하도록 수정했다.

관련 파일:

- `backend/traffic/src/main/java/com/example/traffic/dto/response/SpeedViolationResponse.java`
- `trafficAS-b/src/views/admin/ReviewView.vue`

### 6단계. 과속 상태 enum과 상태 변경 API 정리

프론트 2차 검증 탭에서 사용할 상태값은 다음으로 확정했다.

| 화면 표시 | enum |
| --- | --- |
| 보류 | `UNPROCESSED` |
| 과속 확정 | `NOTIFIED` |
| 미과속 | `REJECTED` |
| 종결/보관 | `CLOSED` |

백엔드 변경:

- `ViolationStatus` enum에 위 4개 상태 반영
- `PATCH /api/speed-violations/{violationId}/status` 추가
- 요청 DTO: `SpeedViolationStatusRequest`
- 응답 DTO는 JPA Entity를 직접 노출하지 않고 `SpeedViolationResponse` 사용
- 상태 변경 실패 시 프론트에서 읽을 수 있는 오류 메시지 반환

관련 파일:

- `backend/traffic/src/main/java/com/example/traffic/common/enums/ViolationStatus.java`
- `backend/traffic/src/main/java/com/example/traffic/dto/request/SpeedViolationStatusRequest.java`
- `backend/traffic/src/main/java/com/example/traffic/controller/SpeedViolationController.java`
- `backend/traffic/src/main/java/com/example/traffic/service/SpeedViolationService.java`
- `backend/traffic/src/main/java/com/example/traffic/etc/GlobalExceptionHandler.java`

### 7단계. `REJECTED` 저장 시 DB 제약조건 오류 해결

프론트에서 `미과속(REJECTED)`을 누르면 다음 메시지가 발생했다.

```text
데이터제약조건 위반입니다. 상태값 또는 DB 제약조건을 확인해주세요
```

원인:

- Java enum은 `REJECTED`를 허용하지만 기존 PostgreSQL check constraint가 새 상태값을 아직 허용하지 않았다.
- `src/main/resources/db/migration/*.sql` 파일은 작성되어 있었지만 현재 프로젝트에는 Flyway/Liquibase가 연결되어 있지 않아 자동 실행되지 않는다.

조치:

- Spring 기동 시 PostgreSQL인 경우 `speed_violations.violation_status` 관련 check constraint를 찾아 제거
- 새 check constraint를 `UNPROCESSED`, `NOTIFIED`, `REJECTED`, `CLOSED` 기준으로 재생성

관련 파일:

- `backend/traffic/src/main/java/com/example/traffic/config/SpeedViolationStatusConstraintInitializer.java`
- `backend/traffic/src/main/resources/db/migration/005_speed_violation_status_values.sql`

주의:

- 이미 떠 있는 Spring 컨테이너에는 반영되지 않는다.
- `docker compose up -d --build` 또는 Spring 백엔드 재시작이 필요하다.

## 3. 2차 검증 버튼 최종 정책

최종 확정된 정책은 아래와 같다.

- STEP 1에서 `실제 과속` 또는 `시스템 오류`를 먼저 선택해야 한다.
- STEP 2에서 사유를 선택해야 한다.
- STEP 3은 STEP 1, STEP 2 완료 후 활성화된다.
- `실제 과속` 선택 시 `과속 확정(NOTIFIED)`만 활성화된다.
- `시스템 오류` 선택 시 `보류(UNPROCESSED)`, `미과속(REJECTED)`, `종결/보관(CLOSED)`만 활성화된다.
- `시스템 오류` 선택 시 `과속 확정(NOTIFIED)`은 의미가 없으므로 비활성화된다.
- `보류(UNPROCESSED)`를 클릭하면 이벤트 목록 상태도 명시적으로 `보류`로 표시한다.
- 최초 조회 시 아직 처리되지 않은 `UNPROCESSED` 이벤트는 속도 기준에 따라 기본 상태를 `과속` 또는 `미과속`으로 표시할 수 있다.
- 현재 상태와 같은 버튼은 기본적으로 비활성화한다.
- 예외적으로 `시스템 오류` 경로에서는 `보류(UNPROCESSED)`를 다시 선택할 수 있다.
- `종결/보관(CLOSED)`은 `과속 확정(NOTIFIED)` 상태인 건에서 상시 활성화된다.
- `과속 확정(NOTIFIED)` 상태에서 `종결/보관(CLOSED)`으로 넘길 때는 STEP 1, STEP 2를 다시 거치지 않아도 된다.
- `시스템 오류` 검증을 거친 경우에도 `종결/보관(CLOSED)` 선택이 가능하다.
- `CLOSED` 상태는 최종 종결 상태로 간주한다.
- `CLOSED` 상태에서는 STEP 1, STEP 2, STEP 3 전체를 비활성화하고 더 이상 상태 변경을 허용하지 않는다.
- `CLOSED`로 보낸 뒤 되돌리기 기능은 만들지 않는다.
- `NOTIFIED`에서 `CLOSED`로 바로 가는 경우에는 사유를 받지 않는다.
- `NOTIFIED` 상태에서는 `종결/보관(CLOSED)` 버튼만 바로 활성화한다.

## 3.1 review 페이지 데이터 범위 최종 정책

- review 페이지는 과속 후보만 다룬다.
- 과속 후보의 기준 데이터는 `speed_violations`이다.
- 정상 속도 차량은 review 페이지에 표시하지 않는다.
- 정상 속도 차량은 추후 별도 교통 흐름 분석 페이지에서 미과속/과속 차량과 함께 데이터로 다룬다.
- 따라서 review 페이지에서는 정상 차량 목록, 정상 차량 속도, `stay_time`을 표시하지 않는다.

## 4. Troubleshooting 요약

### 403 Forbidden

증상:

- DB에는 데이터가 있지만 프론트에서 과속 이벤트 API 호출 시 403 발생

원인:

- 프론트 dev server가 `5174`로 변경되었고 Spring CORS/Security 허용 목록에 없었다.

해결:

- `SecurityConfig`에 `localhost:5174` 허용
- 병합 검증용 API permit 추가

### 이미지 없는 로그에서 mp4 재생

증상:

- 캡처 이미지가 없는 이벤트에서 하드코딩된 `/0513.mp4`가 재생됨

원인:

- 기존 review UI가 영상 fallback을 갖고 있었음

해결:

- 영상 fallback, 실시간 탭, 영상 컨트롤 제거
- 이미지 없음 placeholder로 대체

### OCR 신뢰도 0% 표시

증상:

- OCR 신뢰도가 0%처럼 보임

원인:

- DB/API 값이 0~1인데 프론트 표시에서 퍼센트 변환이 누락되거나 평균 계산이 잘못됨

해결:

- 개별 OCR 신뢰도는 `(value * 100).toFixed(1)%`
- 평균 OCR 신뢰도는 평균값에 100을 곱한 뒤 `%` 표시

### 보류 클릭 후 다시 과속/미과속으로 표시

증상:

- 사용자가 보류를 눌러도 목록에서 다시 속도 기준 `과속` 또는 `미과속`으로 보임

원인:

- DB 상태가 `UNPROCESSED`인 경우 프론트가 항상 속도 기준 기본 상태로 표시했음

해결:

- `speed_violation_reviews` 백엔드 검증 이력 테이블을 추가했다.
- 상태 변경 PATCH가 호출될 때마다 `fromStatus`, `toStatus`, 사유, 메모, 검토자, 검토시각을 저장한다.
- 응답 DTO에 `reviewedManually`, `latestReviewStatus`, `latestReviewReason`, `latestReviewMemo`, `latestReviewedBy`, `latestReviewedAt`을 포함한다.
- 프론트는 더 이상 localStorage를 사용하지 않는다.
- 최신 검증 이력이 `UNPROCESSED`인 건은 DB 상태가 `UNPROCESSED`라도 목록에서 명시적으로 `보류`로 표시한다.

### 미과속 클릭 시 데이터 제약조건 위반

증상:

- `REJECTED` 저장 시 데이터 제약조건 위반 발생

원인:

- DB check constraint가 이전 enum 값만 허용

해결:

- Spring 기동 시 check constraint를 새 enum 목록으로 동기화

## 5. 검증 결과

이번 컨텍스트에서 확인한 명령:

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\trafficAS-b
npm.cmd run build
```

결과:

- 성공
- Vite chunk size warning은 기존 번들 크기 경고이며 이번 변경의 실패는 아님

```powershell
cd C:\jwdev\Traffic_Analytics_Proposal\backend\traffic
.\gradlew.bat test --tests "com.example.traffic.controller.DetectionLogControllerIntegrationTest"
```

결과:

- 성공

## 6. 주의할 점

- `trafficAS-b/Dockerfile`은 작업 중 이미 수정된 상태였고, 이번 컨텍스트에서 직접 건드리지 않았다.
- DB 제약조건 갱신은 Spring 백엔드 재시작 이후에 적용된다.
- 현재 `SpeedViolationStatusConstraintInitializer`는 Flyway가 없는 상황의 실용적 보완책이다.
- 장기적으로는 DB schema 변경을 Flyway/Liquibase 같은 마이그레이션 도구로 옮기는 편이 좋다.
- 명시 보류 상태는 프론트 localStorage가 아니라 백엔드 `speed_violation_reviews` 검증 이력으로 저장한다.
