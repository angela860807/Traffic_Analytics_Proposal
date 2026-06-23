# 예지보전 발표 및 시연 흐름

작성일: 2026-06-23

## 1. 발표 핵심 메시지

1차 프로젝트는 YOLO/OCR 기반 교통단속 시스템이었다.

이번 고도화는 그 탐지 시스템이 실제 운영 환경에서 계속 신뢰성 있게 동작하도록, 카메라와 분석 파이프라인의 품질 저하를 시계열 상태 데이터로 감지하고 이상 이벤트와 정비 프로세스까지 연결하는 예지보전 운영 기능을 추가한 것이다.

발표에서 반복해서 잡아야 할 메시지:

```text
차량을 탐지하는 AI에서, 그 AI 관제 시스템을 안정적으로 운영하는 시스템으로 확장했다.
```

## 2. 발표 구조

### 2-1. 1차 프로젝트 요약

- 차량 영상에서 YOLO로 차량 bbox를 탐지했다.
- 번호판 OCR로 차량 번호를 인식했다.
- 속도 계산 후 과속 여부를 판단했다.
- Spring Boot와 PostgreSQL에 로그를 저장했다.
- 프론트에서 과속 탐지 운영 화면을 제공했다.

### 2-2. 문제 제기

실제 운영에서는 탐지 모델만 잘 돌아가는 것으로 충분하지 않다.

- 카메라 FPS가 낮아지면 차량 탐지 누락 가능성이 증가한다.
- 프레임 드롭이 증가하면 추적과 속도 계산 신뢰도가 떨어진다.
- 영상 흐림이 심해지면 OCR 실패율이 올라간다.
- 분석 지연, CPU/메모리 포화, 네트워크 지연은 실시간 관제 품질을 낮춘다.

즉, 교통 탐지 시스템을 운영하려면 탐지 결과뿐 아니라 장비와 분석 파이프라인의 상태도 관리해야 한다.

### 2-3. 이번 고도화 목표

- 카메라와 분석 파이프라인의 상태 지표를 시계열로 수집한다.
- 과거 기준선과 최근 관측값을 비교한다.
- FPS 저하, 프레임 드롭, 지연 증가, 영상 흐림, 리소스 포화, 네트워크 불안정을 이상 이벤트로 감지한다.
- 심각한 이상은 정비 건으로 연결한다.
- 담당자 배정, 작업 시작, 해결, 종결, 변경 이력까지 운영 흐름을 남긴다.

### 2-4. 시스템 구조 설명

```text
초기 SQL seed
-> PostgreSQL에 누적 운영 데이터 적재
-> Vue /admin/ops 운영 화면에서 여러 카메라/이상/정비 현황 표시
-> 상태 샘플 CSV를 추가 주입
-> Spring Boot 내부 API 수집
-> FastAPI Rule 평가
-> Spring Boot 이상 이벤트/정비 건 저장
-> PostgreSQL 이력 저장
-> Vue /admin/ops 운영 화면 갱신
```

역할:

- FastAPI: 카메라 상태 이상 평가
- Spring Boot: 상태 샘플 저장, 이상 이벤트, 정비 건, 변경 이력 관리
- PostgreSQL: 시계열 상태 샘플과 운영 이력 저장
- Vue: 운영자가 판단 근거와 정비 흐름을 확인하는 화면

## 3. 시연 순서

### 3-1. 시연 전 준비

- Docker 서비스가 실행되어 있어야 한다.
- Spring Boot는 `http://localhost:8080`으로 접근 가능해야 한다.
- Frontend는 `http://localhost:5174`로 접근 가능해야 한다.
- 로그인 계정은 `admin@email.com / 1234`를 사용한다.
- 새 DB 환경에서는 Spring Boot Docker 환경변수 `DB_BOOTSTRAP_ENABLED=true` 기준으로 migration과 demo seed가 자동 적용된다.
- 발표용 누적 데이터는 `/admin/ops`의 `장애 주입` 데이터 소스에서 먼저 보여준다.

### 3-2. 시연 명령

발표 중 직접 실행할 명령은 아래 하나로 제한한다.
이 명령은 누적 운영 데이터 설명을 마친 뒤, 상단 데이터 소스를 `실데이터`로 바꾼 다음 실행한다.

```powershell
.\tools\predictive_demo\import_health_samples.ps1 `
  -CsvPath "tools\predictive_demo\camera-health-rule-trigger-samples.csv" `
  -BaseUrl "http://localhost:8080" `
  -InternalApiKey "traffic-ai-internal-key-2026"
```

확인 포인트:

- `bad_fps_1` ~ `bad_fps_4`
- `Created : True`
- `Status : Imported`

### 3-3. 화면 클릭 순서

1. `http://localhost:5174/admin/ops` 접속
2. `admin@email.com / 1234` 로그인
3. 상단 KPI 확인
   - 전체 카메라 20대
   - 열린 이상 이벤트 15건
   - 정비 건 21건
   - 예측 위험 3건
4. 이상 이벤트 목록에서 `LATENCY_DEGRADATION`, `NETWORK_INSTABILITY`, `FPS_DEGRADATION` 중 1건 상세 클릭
5. 상단 `우선 조치 이상 상세` 확인
6. `시계열 판단 근거 요약` 설명
   - 과거 기준
   - 최근 관측
   - 조치 기준선
   - 현재 / 정상 범위 / 조치 기준 / 판정
7. 하단 정비 건 현황표로 이동
8. `CLOSED` 또는 `RESOLVED` 정비 건의 `이력` 버튼 클릭
9. 정비 변경 이력 timeline 확인
   - `OPEN -> ASSIGNED`
   - `ASSIGNED -> IN_PROGRESS`
   - `IN_PROGRESS -> RESOLVED`
   - `RESOLVED -> CLOSED`

## 4. 시연 멘트 초안

시연 시작:

```text
이제 이번 고도화의 핵심인 예지보전 운영 흐름을 보여드리겠습니다.
1차 프로젝트에서는 차량을 탐지하고 과속 여부를 판단하는 데 집중했다면,
이번에는 그 탐지 시스템이 실제 운영 중 품질 저하 없이 유지될 수 있는지를 관리하는 기능을 추가했습니다.
```

상태 샘플 주입:

```text
실제 운영에서는 카메라나 분석 서버에서 FPS, 프레임 드롭, 지연 시간, 영상 흐림 같은 상태 지표가 계속 수집된다고 가정했습니다.
먼저 SQL seed로 여러 카메라의 누적 운영 데이터를 보여드렸고,
이제 실시간 상황을 재현하기 위해 준비된 상태 샘플을 추가로 주입하겠습니다.
```

KPI 화면:

```text
초기 화면은 장애 주입 데이터 기준으로 운영 현황을 보여줍니다.
현재 전체 카메라 20대, 열린 이상 이벤트 15건, 정비 건 21건이 확인됩니다.
이후 실데이터 필터로 전환해 샘플을 주입하면 방금 들어온 상태 샘플 기반의 이벤트 흐름도 확인할 수 있습니다.
```

시계열 판단 근거:

```text
이상 상세에서는 단순히 장애라고 표시하는 것이 아니라,
과거 기준선과 최근 관측값, 조치 기준선을 비교해서 왜 조치가 필요한지 보여줍니다.
운영자는 현재 값이 정상 범위에서 얼마나 벗어났는지 보고 판단할 수 있습니다.
```

정비 이력:

```text
이상 이벤트는 정비 건으로 연결되고, 담당자 배정부터 작업 시작, 해결, 종결까지의 이력이 남습니다.
이 부분은 실제 관제 시스템에서 장애 대응 과정과 감사 이력을 남기는 흐름을 고려한 부분입니다.
```

마무리:

```text
결과적으로 이번 고도화는 AI 탐지 결과만 보여주는 데서 끝나지 않고,
탐지 시스템 자체의 운영 품질을 시계열로 관리하고 정비 프로세스까지 연결했다는 점에 의미가 있습니다.
```

## 5. 백업 플랜

시연 중 서버, 네트워크, 브라우저 문제가 발생하면 아래 캡처를 순서대로 보여준다.

| 백업 화면 | 파일명 | 설명 |
|---|---|---|
| 상태 샘플 주입 성공 | `IT_01_PM_import_health_samples_success.png` | health sample import 성공 증빙 |
| Summary API 결과 | `IT_02_PM_summary_api_critical_1_events_6.png` | 실데이터 주입 후 summary 확인 |
| 이상 이벤트 조회 | `IT_03_PM_anomaly_events_total_6.png` | 실데이터 주입 후 anomaly-events 확인 |
| 정비 건 조회 | `IT_04_PM_maintenance_tickets_total_3.png` | 실데이터 주입 후 maintenance-tickets 확인 |
| 정비 이력 조회 | `IT_05_PM_ticket_histories_closed_flow.png` | CLOSED까지의 상태 전이 확인 |
| 운영 KPI 화면 | `IT_07_PM_ops_dashboard_kpi.png` | `/admin/ops` KPI 증빙 |
| 시계열 근거 화면 | `IT_08_PM_ops_time_series_evidence01.png`, `IT_08_PM_ops_time_series_evidence02.png` | 판단 근거 UI 증빙 |
| CLOSED 이력 버튼 | `IT_09_PM_ops_ticket_closed_history_button01.png` | 종결 정비 건 이력 조회 가능 증빙 |
| 이력 timeline 모달 | `IT_10_PM_ops_ticket_history_modal.png` | 변경 이력 timeline 증빙 |

시연 실패 시 설명 문장:

```text
현재 환경 문제로 실시간 화면 전환은 생략하고, 동일 시나리오를 사전에 실행한 캡처로 흐름을 설명드리겠습니다.
상태 샘플 주입 후 이상 이벤트와 정비 건이 생성되고, 운영 화면에서 판단 근거와 처리 이력을 확인할 수 있습니다.
```

## 6. 본 발표자 대본 작성 가이드

본 발표자는 시연 전에 아래 내용을 짧게 깔아주면 좋다.

### 6-1. 반드시 들어가야 할 내용

- 1차 프로젝트는 YOLO/OCR 기반 교통단속 시스템이었다.
- 이번 프로젝트는 탐지 모델 자체보다 운영 신뢰성 관리에 초점을 맞췄다.
- 실제 관제 환경에서는 영상 품질 저하, FPS 저하, 분석 지연, 리소스 포화가 탐지 정확도와 신뢰도에 영향을 준다.
- 그래서 카메라/분석 파이프라인 상태를 시계열 데이터로 보고, 기준선 대비 이상 여부를 판단하도록 고도화했다.
- 이상 이벤트는 단순 알림에 그치지 않고 정비 건, 담당자 배정, 상태 변경, 이력 관리까지 이어진다.

### 6-2. 강조하면 좋은 사업적 포인트

- CCTV 관제, 스마트시티, 교통안전센터, 도로시설 유지보수에 적용 가능하다.
- AI 모델 성능뿐 아니라 운영 중 장애 대응 시간과 관리 품질을 개선하는 방향이다.
- 장애가 발생한 뒤 대응하는 것이 아니라, 품질 저하 신호를 먼저 감지해 선제 조치할 수 있다.
- 이상 탐지, 정비 이력, 담당자 배정이 남기 때문에 운영 감사와 장애 재발 분석에도 활용 가능하다.

### 6-3. 인재 발굴 관점에서 보일 수 있는 강점

- AI 모델 데모에서 끝나지 않고 실제 운영 업무 흐름까지 연결했다.
- FastAPI, Spring Boot, Vue, PostgreSQL, Docker를 역할별로 분리해 구성했다.
- API 계약, 상태 전이, DTO, 이력 관리, 테스트 산출물까지 정리했다.
- 모델 결과를 화면에 보여주는 수준을 넘어, 운영자가 의사결정할 수 있는 근거 UI를 만들었다.

### 6-4. 피해야 할 표현

- “영상에서 직접 예지보전 데이터를 뽑았다”라고 말하지 않는다.
- 현재 시연은 영상 직접 분석이 아니라, 영상 품질 저하를 수치화한 health sample 기반 시연이다.
- 따라서 아래처럼 말하는 것이 정확하다.

```text
영상 품질 저하나 분석 지연 같은 운영 현상을 health sample로 모델링했고,
이를 시계열 이상 탐지와 정비 프로세스로 연결했습니다.
```

### 6-5. 시연 파트로 넘기는 연결 멘트

```text
이제 실제로 상태 샘플을 주입했을 때 시스템이 어떻게 위험 카메라를 식별하고,
이상 이벤트와 정비 건을 생성하며,
운영자가 어떤 근거를 보고 조치하는지 시연으로 확인해보겠습니다.
```

## 7. 2026-06-23 최종 시연 운영 메모

### 7-1. 주입 스크립트 최종 형태

발표 중 직접 실행할 명령어는 아래 하나로 고정한다.

```powershell
.\tools\predictive_demo\import_health_samples.ps1 `
  -CsvPath "tools\predictive_demo\camera-health-rule-trigger-samples.csv" `
  -BaseUrl "http://localhost:8080" `
  -InternalApiKey "traffic-ai-internal-key-2026"
```

현재 CSV는 `bad_fps_1` ~ `bad_fps_4` 샘플을 `REAL` 데이터소스로 주입한다. 따라서 시연 화면에서는 누적 운영 데이터는 `장애 주입(FAULT_INJECTED)`로 먼저 보여주고, 스크립트 주입 결과는 `실데이터(REAL)`로 전환해서 확인한다.

### 7-2. 발표에서 설명할 핵심 포인트

- 주입 스크립트는 영상 파일을 직접 분석하는 단계가 아니라, 영상 품질 저하를 health sample 수치로 모델링한 입력이다.
- 같은 카메라와 같은 이상 유형의 활성 이벤트가 이미 있으면 새 행을 계속 만들지 않고 기존 이벤트를 갱신한다.
- 따라서 전체 이상 건수가 그대로여도 실패가 아니다.
- 발표에서는 "중복 장애를 계속 늘리지 않고 하나의 활성 이벤트에 시계열 근거를 누적한다"라고 설명한다.
- 새로 들어온 샘플은 `lastDetectedAt` 갱신과 상세 카드의 시계열 판단 근거 증가로 확인한다.

### 7-3. 발표자가 화면에서 확인할 순서

1. `/admin/ops` 접속 후 `장애 주입(FAULT_INJECTED)` 데이터소스로 누적 운영 현황을 먼저 보여준다.
2. 이상 이벤트 및 정비 건 현황에서 기존 이벤트, 정비 상태, 페이지네이션을 보여준다.
3. PowerShell에서 health sample 주입 명령을 실행한다.
4. `/admin/ops` 상단 데이터소스를 `실데이터(REAL)`로 바꾼다.
5. 이상 이벤트 목록을 최신순으로 확인한다.
6. 카메라 1번 관련 이벤트 상세를 열어 시계열 판단 근거가 쌓였는지 확인한다.
7. 정비 건이 이미 있으면 이력/상태 변경 모달로 이어서 보여준다.

### 7-4. 테스트 확인 명령어

```powershell
$login = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8080/api/auth/login" `
  -ContentType "application/json" `
  -Body (@{
    email = "admin@email.com"
    password = "1234"
  } | ConvertTo-Json)

$headers = @{ Authorization = "Bearer $($login.data.accessToken)" }

Invoke-RestMethod `
  -Uri "http://localhost:8080/api/v1/predictive/summary?dataSource=REAL" `
  -Headers $headers

Invoke-RestMethod `
  -Uri "http://localhost:8080/api/v1/predictive/anomaly-events?dataSource=REAL&page=0&size=100&sort=lastDetectedAt,desc" `
  -Headers $headers
```

DB에서 evidence 누적을 확인할 때:

```powershell
docker exec traffic-postgres psql -U postgres -d traffic -c "select ae.id, ae.anomaly_type, count(ev.id) as evidence_count, max(ev.sampled_at) as latest_evidence from anomaly_events ae left join anomaly_event_evidence ev on ev.anomaly_event_id=ae.id where ae.data_source='REAL' and ae.target_camera_id=1 group by ae.id, ae.anomaly_type order by latest_evidence desc;"
```

### 7-5. 예상 질문 대응

Q. 스크립트를 다시 실행했는데 전체 이상 건수가 늘지 않는 이유는?

A. 같은 카메라와 같은 이상 유형의 활성 이벤트가 있으면 기존 이벤트를 갱신하기 때문이다. 실제 관제에서는 같은 장애를 매번 새 티켓으로 만들면 중복 처리가 생기므로, 하나의 활성 이벤트에 최근 감지 시각과 판단 근거를 누적하는 방식이 더 적절하다.

Q. 준비한 blur, dropout, low_fps, normal 영상은 왜 직접 주입하지 않는가?

A. 이번 시연은 영상 자체를 다시 분석하는 단계가 아니라, 영상 품질 저하가 운영 지표로 변환된 이후의 예지보전 흐름을 보여주는 단계다. 영상은 health sample 지표가 어떤 상황을 의미하는지 설명하는 보조 자료로 사용하고, 실제 시스템 입력은 CSV health sample로 통일한다.
