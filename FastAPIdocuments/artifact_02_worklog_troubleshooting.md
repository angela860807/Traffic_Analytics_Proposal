# 2번 산출물

## 작업 요약

백엔드 초안 검토부터 FastAPI 연동 준비까지 단계적으로 점검했다.

처음에는 백엔드 압축 파일 기준으로 검토하려 했으나 `backend.zip`은 작업공간에 없었고, 실제 검토 대상은 `C:\jwdev\Traffic_Analytics_Proposal\backend\traffic` 디렉토리였다. 이후 `git pull`이 누락되어 파일이 부족했던 점을 확인하고 원격 변경분을 반영한 뒤 다시 검토했다.

첨부 기준 문서인 표준 네이밍 규칙, 차량 흐름 분석 시스템 설계 초안, 중복 감지 처리 정책 보완 설명을 기준으로 백엔드 구조를 비교했다. 초기 백엔드는 도메인 엔티티 중심이었고, 이후 controller, service, repository, dto, enum, security 계층이 추가되었다.

1차 검토에서는 DTO 계층 부재, JPA 엔티티 직접 노출, 컬럼명 불일치, 중복 감지 정책 미구현, enum 미사용, 테스트 DB 환경 의존성을 주요 문제로 정리했다. 이 내용을 백엔드 담당자에게 전달하기 위해 `백엔드_초안_검토_전달사항.txt` 파일을 작성했다.

이후 백엔드 2차 수정 검토에서는 기존 피드백 문서에 현재 프로젝트와 맞지 않는 파일명들이 포함되어 있음을 확인했다. `DeviceService`, `SafetyEventService`, `DemoApplicationTests` 등은 현재 차량 흐름 분석 백엔드에 존재하지 않았고, 실제 파일명인 `DetectionLogService`, `VehicleFlowEventService`, `TrafficApplicationTests` 기준으로 다시 정리했다. 이 결과를 `backend_코드충돌위험_소극검토.docx`로 생성했다.

그 다음에는 초급반 프로젝트 기준으로 작동 중인 부분의 자잘한 위험은 제외하고, 큰 문제만 추려 수정 내역 형태로 정리했다. 주요 항목은 잘못된 파일명 정정, `DetectionLogService`의 `detectionType` 저장 누락, 중복 감지 기준 이중화, `-1L` 성공 응답 문제, `ddl-auto:update`와 기존 DB 컬럼 충돌 가능성, `HourlyTrafficStat` 기본키 컬럼명 정렬이었다.

백엔드 3차 수정 이후에는 FastAPI 병합 전 백엔드 단독 검수를 진행했다. `compileJava`는 성공했고, `test`는 실패했지만 원인은 로컬 PostgreSQL `localhost:5432` 접속 실패였다. 따라서 코드 컴파일 충돌보다는 테스트 환경 문제로 판단했다.

FastAPI와 Spring Boot 백엔드 간 인증 방식은 일반 사용자 JWT 로그인 방식보다 서버 간 전용 API Key 방식이 적합하다고 판단했다. 이에 따라 `X-Internal-Api-Key` 헤더를 사용하는 방식을 추천했고, FastAPI 담당자가 따라 할 수 있도록 `fastapi_internal_api_key_연동가이드.md` 파일을 작성했다.

이후 백엔드 최종 수정 요청 사항으로 `POST /api/v1/detection-logs`에 `X-Internal-Api-Key`를 적용하고, 요청 DTO를 `cameraId` 대신 `cameraCode` 기준으로 바꾸는 방안을 검토했다. 요청 DTO는 `cameraCode`, `plateNumber`, `confidenceScore`, `imagePath`, `imageUrl`, `detectedAt`, `detectionType`으로 정리되었다.

마지막으로 API Key 값을 `traffic-ai-internal-key-2026`으로 정하고, Vue 화면 표시를 위해 `imageUrl`을 엔티티와 응답 DTO에도 추가해야 한다는 피드백을 전달했다. 최종 확인 결과 백엔드에는 API Key 값, `imageUrl` 요청 DTO, 엔티티 저장 필드, 저장 로직, 응답 DTO가 모두 반영되었다.

최종 판단은 FastAPI와 백엔드 통합을 진행해도 된다는 결론이었다. 단, 백엔드 테스트는 여전히 PostgreSQL 미기동으로 실패하므로, 통합 테스트 전 DB 실행 또는 테스트 전용 설정 분리가 필요하다고 정리했다.

## 주요 산출 파일

- `백엔드_초안_검토_전달사항.txt`
- `backend_코드충돌위험_소극검토.docx`
- `fastapi_internal_api_key_연동가이드.md`

## 트러블 슈팅 로그

### 1. backend.zip 파일이 없음

문제:
요청에는 `backend.zip`이 첨부 파일로 언급되었지만 실제 작업공간 경로에는 존재하지 않았다.

확인:
`C:\jwdev\Traffic_Analytics_Proposal\backend.zip`을 확인했으나 파일이 없었다.

처리:
이미 풀려 있는 `C:\jwdev\Traffic_Analytics_Proposal\backend\traffic` 디렉토리를 실제 검토 대상으로 삼았다.


### 2. git pull 누락으로 백엔드 파일이 부족함

문제:
처음 확인한 백엔드에는 domain 중심 파일만 있었고 controller, service, repository, dto 계층이 부족했다.

확인:
`git status`에서 브랜치가 원격보다 뒤처진 상태였고, 이후 `git pull` 후 파일 구조가 확장되었다.

처리:
원격 변경분 반영 후 `controller`, `service`, `repository`, `dto`, `common/enums`, `security` 계층까지 포함한 상태로 다시 검토했다.


### 3. 기준 문서와 보완 설명서의 `is_duplicate` 정책 충돌

문제:
초기 설계서에는 `detection_logs.is_duplicate` 컬럼이 있었지만, 보완 설명서에서는 해당 컬럼을 제거하고 `vehicle_flow_events` 생성 여부로 중복을 판단한다고 되어 있었다.

처리:
보완 설명서를 최신 정책으로 보고, `is_duplicate` 컬럼 부재는 위반으로 보지 않았다.


### 4. 초기 JPA 매핑 오류

문제:
초기 `DetectionLog`에서 `Camera`, `Vehicle` 필드가 JPA 관계로 매핑되지 않아 Hibernate가 타입을 해석하지 못했다.

증상:
`Could not determine recommended JdbcType for Java type 'com.example.traffic.domain.Camera'`

처리:
이후 수정본에서 `@ManyToOne`, `@JoinColumn`이 반영되어 해당 문제는 해결된 것으로 확인했다.


### 5. DTO 계층 부재와 엔티티 직접 노출

문제:
초기 Controller들이 JPA Entity를 직접 요청/응답에 사용했다.

위험:
API 계약이 불명확해지고, Lazy 로딩/순환 참조/불필요한 필드 노출 위험이 있었다.

처리:
백엔드 담당자에게 request/response DTO 분리를 요청했고, 이후 `dto/request`, `dto/response` 패키지가 추가된 것을 확인했다.


### 6. 컬럼명 불일치

문제:
설계서 기준 `detection_log_id`, `hourly_stat_id`와 코드 필드명이 불일치할 가능성이 있었다.

처리:
`DetectionLog`에는 `@Column(name = "detection_log_id")`가 반영되었고, `HourlyTrafficStat`에는 `@Column(name = "hourly_stat_id")`가 반영된 것을 확인했다.


### 7. 테스트 실패 원인 분리

문제:
`gradlew test`가 계속 실패했다.

확인:
실패 원인은 코드 컴파일 오류가 아니라 로컬 PostgreSQL `localhost:5432` 접속 실패였다.

증상:
`Connection to localhost:5432 refused`
`Unable to determine Dialect without JDBC metadata`

처리:
`compileJava`가 성공하므로 코드 충돌은 아닌 것으로 판단했다. 다만 실제 테스트 통과를 위해서는 PostgreSQL 실행, Docker DB 실행, 또는 test profile/H2/Testcontainers 설정이 필요하다고 정리했다.


### 8. 기존 피드백 문서의 파일명 불일치

문제:
`백엔드초안수정2차.docx`에는 현재 프로젝트와 맞지 않는 파일명이 있었다.

예시:
`DeviceService`, `SafetyEventService`, `SafetyEventController`, `AiAnalysisClient`, `DemoApplicationTests`

처리:
현재 백엔드에 존재하는 `DetectionLogService`, `VehicleFlowEventService`, `TrafficApplicationTests` 기준으로 문서를 다시 작성했다.


### 9. 중복 감지 기준 이중화

문제:
한때 `DetectionLogService`에서 2초 기준으로 로그 저장을 막고, `VehicleFlowEventService`에서 10초 기준으로 flow event 중복을 다시 판단하는 구조가 있었다.

위험:
원본 로그 보존 정책과 중복 이벤트 생성 정책이 섞일 수 있었다.

처리:
원본 로그는 저장하고, 중복이 아닌 경우에만 `vehicle_flow_events`를 생성하는 방향이 더 안전하다고 피드백했다.


### 10. `detectionType` 저장 누락

문제:
`DetectionLog.detectionType`은 필수 컬럼인데 저장 로직에서 값이 세팅되지 않는 문제가 있었다.

처리:
`DetectionRequest`에 `detectionType`을 필수로 두고, `DetectionLogService`에서 `request.getDetectionType()`을 builder에 세팅하도록 수정되었음을 확인했다.


### 11. `-1L` 성공 응답 문제

문제:
중복 감지 시 `-1L`을 성공 응답처럼 반환하는 구조가 있었다.

위험:
프론트엔드나 연동 서버가 실제 저장된 로그 ID로 오해할 수 있었다.

처리:
실제 저장된 경우에만 ID를 반환하고, 중복 여부는 별도 정책으로 다루는 방향을 제안했다.


### 12. FastAPI 인증 방식 결정

문제:
FastAPI가 백엔드에 감지 결과를 보낼 때 JWT 로그인을 사용할지, 내부 API Key를 사용할지 결정이 필요했다.

판단:
초급반 프로젝트 기준으로 FastAPI가 일반 사용자 로그인/JWT를 관리하는 방식은 과하다고 판단했다.

처리:
서버 간 통신용 `X-Internal-Api-Key` 방식을 추천했다.


### 13. API Key 값 결정

문제:
백엔드와 FastAPI가 같은 내부 키 값을 사용해야 했다.

결정:
`traffic-ai-internal-key-2026`

처리:
백엔드 `DetectionLogController`의 내부 키 값이 해당 문자열로 반영되었고, FastAPI도 같은 값을 `X-Internal-Api-Key` 헤더에 보내면 된다고 정리했다.


### 14. `cameraId`에서 `cameraCode`로 DTO 변경

문제:
FastAPI가 DB 내부 ID를 알기 어렵기 때문에 `cameraId` 대신 `cameraCode`를 보내는 방식이 더 적합했다.

처리:
`DetectionRequest`가 `cameraCode`를 받도록 변경되었고, `DetectionLogService`가 `cameraRepository.findByCameraCode()`로 카메라를 조회하도록 수정된 것을 확인했다.


### 15. `imageUrl` 저장/응답 누락

문제:
FastAPI 요청 DTO에는 `imageUrl`이 있었지만, 처음에는 엔티티 저장과 응답 DTO에 반영되지 않았다.

위험:
Vue 화면 표시용 URL이 백엔드 조회 응답으로 이어지지 않을 수 있었다.

처리:
`DetectionLog` 엔티티, `DetectionLogService` 저장 로직, `DetectionResponse` 응답 DTO에 `imageUrl`이 반영되었음을 최종 확인했다.


### 16. 최종 FastAPI 연동 DTO 규격

FastAPI가 백엔드로 보내야 하는 최종 요청 필드는 다음과 같이 정리되었다.

- `cameraCode`
- `plateNumber`
- `confidenceScore`
- `imagePath`
- `imageUrl`
- `detectedAt`
- `detectionType`

필수 필드는 `cameraCode`, `plateNumber`, `confidenceScore`, `imagePath`, `detectedAt`, `detectionType`이며, `imageUrl`은 선택 필드로 정리했다.


### 17. 최종 병합 판단

최종 확인 결과:

- API Key 반영 완료
- `cameraCode` 기반 카메라 조회 반영 완료
- `imageUrl` 요청, 저장, 응답 반영 완료
- `detectionType` 저장 반영 완료
- `compileJava` 성공
- `test` 실패 원인은 PostgreSQL 미접속

결론:
백엔드 코드 자체는 FastAPI와 통합해도 되는 상태로 판단했다. 이후 단계는 FastAPI 요청 payload와 백엔드 `DetectionRequest` DTO를 실제로 맞춰보고, DB 실행 상태에서 통합 테스트를 진행하는 것이다.
