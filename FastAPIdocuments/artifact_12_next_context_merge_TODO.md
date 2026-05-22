# Artifact 12 - Next Context Merge TODO

작성일: 2026-05-21

## 1. 바로 확인할 것

- [ ] `docker compose up -d --build`로 Spring 백엔드 재빌드/재시작
- [ ] Spring 로그에서 `speed_violations.violation_status check constraint synchronized.` 확인
- [ ] review 페이지에서 `미과속(REJECTED)` 클릭 시 더 이상 DB 제약조건 오류가 나지 않는지 확인
- [ ] review 페이지에서 `보류(UNPROCESSED)` 클릭 후 이벤트 목록에도 `보류`로 유지되는지 확인
- [ ] `과속 확정(NOTIFIED)` 상태인 건에서 `종결/보관(CLOSED)` 버튼이 STEP 1/2 없이 활성화되는지 확인
- [ ] `시스템 오류` 선택 시 `과속 확정(NOTIFIED)` 버튼이 비활성화되는지 확인
- [ ] `CLOSED` 상태에서 모든 검증/변경 버튼이 막히는지 확인

## 2. 프론트 병합 검수 TODO

- [ ] 팀원이 넘긴 최신 프론트 레이아웃과 현재 `ReviewView.vue` 변경분 충돌 여부 확인
- [ ] 공통 axios client 사용 여부 유지 확인
- [ ] `/api/speed-violations` API 호출이 흩어진 fetch/axios 호출로 다시 생기지 않았는지 확인
- [ ] `ReviewView.css`에서 비활성 버튼 opacity 정책이 유지되는지 확인
- [ ] 캡처 이미지 없음, crop 이미지 없음, OCR 신뢰도 없음 상태 UI 확인
- [ ] 날짜 변경 시 목록 reload와 선택 이벤트 초기화 동작 확인
- [ ] 자동 새로고침 시 선택 이벤트가 사라지지 않는지 확인
- [ ] 이미지 경로가 날짜 디렉토리 변경에도 `/static/detections/YYYY/MM/DD/...`로 정상 매핑되는지 확인

## 3. 백엔드 병합 검수 TODO

- [ ] `ViolationStatus` enum 값이 `UNPROCESSED`, `NOTIFIED`, `REJECTED`, `CLOSED`로 유지되는지 확인
- [ ] `PATCH /api/speed-violations/{violationId}/status`가 최신 코드와 충돌 없이 남아 있는지 확인
- [ ] `SpeedViolationResponse`에 프론트가 쓰는 필드가 유지되는지 확인
  - `violationId`
  - `flowEventId`
  - `plateNumber`
  - `measuredSpeed`
  - `speedLimit`
  - `violationStatus`
  - `confidenceScore`
  - `violationImagePath` 또는 `violationImageUrl`
  - `plateCropImagePath` 또는 `plateCropImageUrl`
- [ ] `GlobalExceptionHandler`의 DB 제약조건 오류 메시지가 프론트에서 읽을 수 있는 형태인지 확인
- [ ] Spring Security 임시 permit 정책을 팀 인증 정책과 맞춰 재정리할지 결정
- [ ] 장기적으로 `SpeedViolationStatusConstraintInitializer`를 Flyway/Liquibase migration으로 대체할지 결정

## 4. API smoke test TODO

Spring 백엔드 기동 후:

```powershell
curl.exe "http://localhost:8080/api/speed-violations"
```

확인:

- [ ] 응답이 200인지
- [ ] `data` 배열이 내려오는지
- [ ] `violationStatus` 값이 4개 enum 중 하나인지
- [ ] 속도 값이 `measuredSpeed`, `speedLimit`으로 내려오는지
- [ ] OCR 신뢰도 `confidenceScore`가 0~1 범위인지

상태 변경:

```powershell
curl.exe -X PATCH 'http://localhost:8080/api/speed-violations/{violationId}/status' `
  -H "Content-Type: application/json" `
  --data-raw '{"violationStatus":"REJECTED"}'
```

PowerShell에서는 `cmd` 방식의 `\"` JSON escape가 깨질 수 있다. 가장 안전한 방식은 `Invoke-RestMethod`를 쓰는 것이다.

```powershell
$body = @{ violationStatus = "REJECTED" } | ConvertTo-Json
Invoke-RestMethod `
  -Method Patch `
  -Uri 'http://localhost:8080/api/speed-violations/{violationId}/status' `
  -ContentType 'application/json' `
  -Body $body
```

확인:

- [ ] `REJECTED` 저장 성공
- [ ] DB `speed_violations.violation_status`가 `REJECTED`로 변경
- [ ] 프론트 목록에서 `미과속`으로 표시

## 5. 화면 수동 테스트 시나리오

### 시나리오 A. 실제 과속 확정

- [ ] 이벤트 선택
- [ ] STEP 1 `실제 과속` 선택
- [ ] STEP 2 사유 선택
- [ ] STEP 3에서 `과속 확정`만 활성화되는지 확인
- [ ] `과속 확정` 클릭
- [ ] 목록 상태가 `과속 확정`으로 바뀌는지 확인
- [ ] 같은 건에서 `종결/보관`이 상시 활성화되는지 확인
- [ ] `종결/보관` 클릭 후 `CLOSED` 상태가 되는지 확인

### 시나리오 B. 시스템 오류로 미과속 처리

- [ ] 이벤트 선택
- [ ] STEP 1 `시스템 오류` 선택
- [ ] STEP 2 사유 선택
- [ ] `과속 확정` 버튼이 비활성화되는지 확인
- [ ] `미과속` 클릭
- [ ] DB 제약조건 오류 없이 저장되는지 확인
- [ ] 목록 상태가 `미과속`으로 바뀌는지 확인

### 시나리오 C. 시스템 오류로 보류 처리

- [ ] 이벤트 선택
- [ ] STEP 1 `시스템 오류` 선택
- [ ] STEP 2 사유 선택
- [ ] `보류` 클릭
- [ ] 실제 속도가 제한속도를 넘었더라도 목록 상태가 `보류`로 유지되는지 확인

### 시나리오 D. CLOSED 잠금

- [ ] `종결/보관` 처리된 이벤트 선택
- [ ] STEP 1 버튼 비활성화 확인
- [ ] STEP 2 사유/메모 비활성화 확인
- [ ] STEP 3 최종결정 버튼 전체 비활성화 확인

## 6. 확정된 운영 정책

- [x] `CLOSED`로 보낸 뒤 되돌리기 기능은 만들지 않는다.
- [x] `NOTIFIED`에서 `CLOSED`로 바로 가는 경우 사유를 받지 않는다.
- [x] `NOTIFIED` 상태에서는 `종결/보관(CLOSED)` 버튼만 바로 활성화한다.
- [x] 정상 속도 차량은 review 페이지에서 다루지 않는다.
- [x] review 페이지는 과속 후보인 `speed_violations` 데이터만 표시한다.
- [x] 정상 속도 차량은 추후 별도 교통 흐름 분석 페이지에서 미과속/과속 차량과 함께 데이터로 다룬다.
- [x] `stay_time`은 계속 미사용/NULL 정책으로 두고 review 프론트 표시에서 제외한다.

- [x] 명시 보류 상태는 프론트 localStorage가 아니라 백엔드 `speed_violation_reviews` 검증 이력으로 저장한다.
