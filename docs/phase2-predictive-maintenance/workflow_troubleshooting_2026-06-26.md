# 예지보전 발표 시연 Workflow / Troubleshooting

작성일: 2026-06-26

## 0. 작업 목표

발표 시연 흐름을 `PPT -> /admin/ops 실제 시연 -> PPT 복귀` 한 번의 왕복으로 정리하고, 예지보전 화면이 실데이터 주입 전후 변화를 직관적으로 보여주도록 조정했다.

## 1. 주요 변경 요약

1. 발표용 디렉터리 정리
   - `presentation/ppt-captures/`에 PPT 삽입용 캡처 이미지를 모았다.
   - YOLO/OCR 로그, 번호판 OCR 운영 화면, health sample CSV, 장애 주입 화면, 이상 이벤트 표, 우선조치 상세, 정비 이력 모달 캡처를 구분했다.

2. 발표 대본 정리
   - `예지보전_시연파트_대본_가이드_2026-06-23.txt`를 발표자 행동 지침 형태로 수정했다.
   - 클릭/이동 작업은 `[]`로 구분했다.
   - 실제 말로 읽을 발표문은 완성형 문장으로 유지했다.
   - 4번 이후 흐름은 캡처 설명이 아니라 실제 프론트 화면에서 설명하는 방식으로 바꿨다.

3. reset/import 시연 데이터 정리
   - `reset_health_demo.ps1`이 실데이터 이상 이벤트, 정비 건, 예측 로그, REAL health sample을 초기화하도록 강화했다.
   - 초기화 후에는 정상 카메라 health sample만 남겨, 실데이터 주입 전에는 이상 이벤트가 없는 상태가 되도록 했다.
   - `camera-health-rule-trigger-samples.csv`는 6개 이상 이벤트가 생성되도록 조정했다.

4. Docker compose 빌드 의존성 정리
   - `docker-compose.yml`의 `depends_on`을 제거했다.
   - `docker compose build frontend`처럼 특정 서비스만 빌드할 수 있도록 했다.

5. `/admin/ops` 로딩 오류 수정
   - `filteredCams`를 선언 전 참조하던 watcher 때문에 `/admin/ops`가 빈 화면이 되는 문제를 수정했다.
   - 로컬 `npm run build`로 확인했다.

6. 장비현황 탭 정리
   - 카메라 상태 목록에 실제 페이지네이션을 추가했다.
   - 이상 이벤트가 있는 카메라를 우선 배치했다.
   - 카메라명 옆에 `이상 1 · P1 심각`처럼 이상 건수와 위험도를 표시했다.
   - 행 전체 빨간 글씨는 제거하고, 이상 배지만 강조하도록 정리했다.
   - 열린 P1/심각 이상은 상태를 `위험`, P2/경고 이상은 `저하`로 표시해 장애/이상관리 탭과 일관성을 맞췄다.

7. 장애/이상관리 탭 정리
   - 하드코딩 mock 목록을 제거하고 Spring Boot API 데이터 기준으로 표시했다.
   - `장애만` 필터를 제거하고 예지보전 이상 이벤트 중심으로 정리했다.
   - 목록 정렬을 `P1 -> P2 -> P3` 위험도 높은 순으로 변경했다.
   - 정비 상태 배지 색상을 상태별로 명확히 구분했다.

8. 우선조치 이상 상세 정리
   - 상단 메타 카드 중 `이상 상태`, `정비 상태`, `탐지 방식`, `우선순위`, `탐지기` 카드를 제거했다.
   - `문제 장비`, `위험도`, `인지된 문제` 3개 카드만 한 줄로 남겼다.

## 2. 현재 시연 Workflow

### 2-1. 초기화

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\predictive_demo\reset_health_demo.ps1
```

기대 상태:

- REAL 기준 anomaly event 0건
- REAL 기준 maintenance ticket 0건
- 정상 카메라 health sample만 존재

### 2-2. 실데이터 주입

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\predictive_demo\import_health_samples.ps1 `
  -CsvPath "tools\predictive_demo\camera-health-rule-trigger-samples.csv" `
  -BaseUrl "http://localhost:8080" `
  -InternalApiKey "traffic-ai-internal-key-2026"
```

기대 결과:

- REAL 기준 이상 이벤트 6건 생성
- 카메라 10: FPS 저하
- 카메라 11: 프레임 드롭
- 카메라 12: 지연 증가
- 카메라 13: 네트워크 불안정
- 카메라 14: 리소스 포화
- 카메라 17: 영상 흐림

### 2-3. 프론트 반영

```powershell
docker compose build frontend
docker compose up -d frontend
```

## 3. Troubleshooting

### 3-1. `/admin/ops`가 빈 화면으로 로딩됨

원인:

- Vue setup 단계에서 `filteredCams`를 선언 전에 참조하는 watcher가 실행됨

조치:

- 선언 순서에 맞지 않는 watcher를 제거하고, 필터/정렬 변경 watcher만 유지

확인:

```powershell
cd trafficAS-b
npm.cmd run build
```

### 3-2. reset 후에도 이상 이벤트가 남아 보임

원인:

- 기존 reset은 health sample만 일부 정리하고 anomaly event, ticket, prediction log를 충분히 비우지 못함

조치:

- `reset_health_demo.ps1`에서 REAL 기준 이상 이벤트, 정비 건, 예측 로그, health sample을 함께 정리
- 이후 정상 상태 health sample만 재삽입

### 3-3. 장비현황은 정상인데 장애/이상관리에는 P1 심각이 보임

원인:

- 장비 상태는 `healthStatus`, 장애/이상관리는 열린 anomaly event를 기준으로 표시해 서로 기준이 달랐음

조치:

- 장비현황의 카메라명 옆 배지에 `이상 N · P1 심각` 표시
- 열린 P1/심각 이벤트는 상태를 `위험`, P2/경고 이벤트는 `저하`로 표시

### 3-4. 카메라 행 전체가 빨간색으로 보여 가독성이 떨어짐

원인:

- 열린 이상 이벤트를 행의 `bad` class 조건으로 연결하면서 행 전체 스타일이 영향을 받음

조치:

- 행 스타일은 기존처럼 원본 장애 상태일 때만 적용
- 이상 위험도는 카메라명 옆 배지만 강조

### 3-5. 특정 서비스만 빌드하고 싶은데 전체가 빌드됨

원인:

- compose 서비스 간 `depends_on` 때문에 서비스 단위 빌드 흐름이 불편했음

조치:

- frontend, backend, fastapi-server 간 compose `depends_on` 제거

## 4. 검증

확인한 명령:

```powershell
cd trafficAS-b
npm.cmd run build
```

결과:

- Vite production build 통과
- `/admin/ops` 관련 Vue 템플릿/스크립트 문법 오류 없음

## 5. 남은 TODO

1. Docker 반영 후 최종 화면 확인
   - `docker compose build frontend`
   - `docker compose up -d frontend`
   - 브라우저 강력 새로고침 후 `/admin/ops` 확인

2. reset/import 리허설 재확인
   - reset 직후 REAL 기준 이상 이벤트 0건인지 확인
   - import 후 REAL 기준 이상 이벤트 6건이 생성되는지 확인

3. 발표 직전 캡처 최신화
   - 장비현황의 `이상 N · P1 심각` 배지 표시 반영본 캡처
   - 장애/이상관리의 P1/P2/P3 정렬 반영본 캡처
   - 우선조치 이상상세 3개 카드 반영본 캡처

4. 후속 개선
   - 장비현황의 하드코딩 운영 지표를 실제 API 값으로 점진 연동
   - 정비 이력 모달 외에도 정비 상태 변경 이력을 표 영역에서 더 명확히 노출
   - 백엔드 summary의 `criticalCameras`, `normalCameras` 기준과 프론트 표시 기준 일치 여부 검토
