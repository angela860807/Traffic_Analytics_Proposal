# 개발용 DB 마이그레이션 안내

현재 프로젝트는 로컬/팀 개발 편의를 위해 `spring.jpa.hibernate.ddl-auto=update`를 계속 사용한다.
아직 구조가 빠르게 바뀌는 단계라 Spring이 작은 엔티티 변경을 자동 반영할 수 있게 두는 것이 목적이다.

다만 팀 공유, 시연, 운영에 가까운 실행 환경에서는 스키마 변경 이력을 명시적으로 남겨야 한다.
따라서 DB 스키마 변경은 `src/main/resources/db/migration` 아래 SQL 파일로 기록하고 적용한다.

## 현재 마이그레이션

| 파일 | 내용 |
|---|---|
| `001_backend_schema_updates.sql` | 번호판 탐지 파이프라인 초기 스키마 |
| `002_cleanup_detection_logs_legacy_columns.sql` | detection_logs 레거시 컬럼 정리 |
| `003_detection_type_unknown_and_analysis_index.sql` | detection_type UNKNOWN 추가·인덱스 |
| `004_make_flow_metrics_nullable_until_estimated.sql` | 속도·체류시간 NULL 허용 |
| `005_speed_violation_status_values.sql` | 과속 위반 상태값 수정 |
| `006_speed_violation_reviews.sql` | 과속 위반 검토 이력 테이블 |
| `007_predictive_maintenance_schema.sql` | **2차 예지보전 신규 테이블 10개** |
| `008_predictive_seed_policies.sql` | **예지보전 초기 정책·detector 시드** |

001~006은 가능한 범위에서 `IF NOT EXISTS`와 제약조건 존재 여부 확인을 사용해 반복 실행에 견디도록 작성했다.
007·008도 동일하게 `IF NOT EXISTS`, `ON CONFLICT DO NOTHING`으로 반복 실행 안전하게 작성했다.

## Docker Compose 환경에서 적용

### 001~006 (기존)

프로젝트 루트에서 실행한다.

```powershell
docker compose up -d postgres-db
Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\001_backend_schema_updates.sql |
  docker exec -i traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f -
```

### 007·008 (2차 예지보전) — 반드시 007 → 008 순서로 적용

008은 007에서 만든 테이블에 데이터를 삽입하므로 순서를 지켜야 한다.

```powershell
# 1단계: postgres-db 컨테이너 실행 확인
docker compose up -d postgres-db

# 2단계: 007 적용 (예지보전 테이블 생성)
Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\007_predictive_maintenance_schema.sql |
  docker exec -i traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f -

# 3단계: 008 적용 (정책·detector 시드 데이터 삽입)
Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\008_predictive_seed_policies.sql |
  docker exec -i traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f -
```

## 반영 없이 사전 검증

시연 전 SQL 문법이나 팀원 DB 상태를 확인하고 싶을 때 사용한다.
`ROLLBACK`으로 끝나므로 실제 변경은 남지 않는다.

### 001~006 사전 검증

```powershell
$migration = Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\001_backend_schema_updates.sql
"BEGIN;`n$migration`nROLLBACK;" |
  docker exec -i traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f -
```

### 007·008 사전 검증 — 반드시 007 → 008 순서로 검증

007과 008을 하나의 트랜잭션으로 묶어서 검증하면 순서와 의존성을 한 번에 확인할 수 있다.

```powershell
# 007 단독 검증
$migration007 = Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\007_predictive_maintenance_schema.sql
"BEGIN;`n$migration007`nROLLBACK;" |
  docker exec -i traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f -

# 008 단독 검증 (007이 이미 적용된 상태에서 실행)
$migration008 = Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\008_predictive_seed_policies.sql
"BEGIN;`n$migration008`nROLLBACK;" |
  docker exec -i traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f -

# 007·008 통합 검증 (007 적용 전 상태에서 한 번에 확인)
$migration007 = Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\007_predictive_maintenance_schema.sql
$migration008 = Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\008_predictive_seed_policies.sql
"BEGIN;`n$migration007`n$migration008`nROLLBACK;" |
  docker exec -i traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f -
```

## 적용 후 확인

```powershell
# 전체 테이블 목록 확인
docker exec traffic-postgres psql -U postgres -d traffic -c "\dt"

# 예지보전 신규 테이블 확인
docker exec traffic-postgres psql -U postgres -d traffic -c "\d camera_health_samples"
docker exec traffic-postgres psql -U postgres -d traffic -c "\d anomaly_policies"
docker exec traffic-postgres psql -U postgres -d traffic -c "\d detector_versions"
docker exec traffic-postgres psql -U postgres -d traffic -c "\d anomaly_events"
docker exec traffic-postgres psql -U postgres -d traffic -c "\d maintenance_tickets"

# 시드 데이터 확인
docker exec traffic-postgres psql -U postgres -d traffic -c "SELECT detector_name, version, operating_mode, active FROM detector_versions;"
docker exec traffic-postgres psql -U postgres -d traffic -c "SELECT policy_code, anomaly_type, warning_threshold, critical_threshold FROM anomaly_policies ORDER BY id;"
```

## 프로젝트 규칙

- 당분간 `spring.jpa.hibernate.ddl-auto=update`는 유지한다.
- `data.sql`에는 기준 seed 데이터만 둔다. 스키마 DDL은 넣지 않는다.
- 앞으로 스키마가 바뀌면 이미 공유한 migration 파일을 수정하지 말고 새 번호의 SQL 파일을 추가한다.
- 수동 데이터 정리가 필요한 migration은 SQL 주석에 사전 확인 방법과 rollback 기대치를 적는다.
- **007 이후 신규 migration은 반드시 의존 테이블이 먼저 적용됐는지 확인 후 실행한다.**
