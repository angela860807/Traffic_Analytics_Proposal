# 개발용 DB 마이그레이션 안내

현재 프로젝트는 로컬/팀 개발 편의를 위해 `spring.jpa.hibernate.ddl-auto=update`를 계속 사용한다.
아직 구조가 빠르게 바뀌는 단계라 Spring이 작은 엔티티 변경을 자동 반영할 수 있게 두는 것이 목적이다.

다만 팀 공유, 시연, 운영에 가까운 실행 환경에서는 스키마 변경 이력을 명시적으로 남겨야 한다.
따라서 DB 스키마 변경은 `src/main/resources/db/migration` 아래 SQL 파일로 기록하고 적용한다.

## 현재 마이그레이션

현재 번호판 탐지 파이프라인 스키마는 아래 파일을 기준으로 적용한다.

```text
src/main/resources/db/migration/001_backend_schema_updates.sql
```

해당 SQL은 가능한 범위에서 `IF NOT EXISTS`와 제약조건 존재 여부 확인을 사용해 반복 실행에 견디도록 작성했다.

## Docker Compose 환경에서 적용

프로젝트 루트에서 실행한다.

```powershell
docker compose up -d postgres-db
Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\001_backend_schema_updates.sql |
  docker exec -i traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f -
```

적용 후 주요 테이블을 확인한다.

```powershell
docker exec traffic-postgres psql -U postgres -d traffic -c "\dt"
docker exec traffic-postgres psql -U postgres -d traffic -c "\d detection_analysis_results"
```

## 반영 없이 사전 검증

시연 전 SQL 문법이나 팀원 DB 상태를 확인하고 싶을 때 사용한다.
`ROLLBACK`으로 끝나므로 실제 변경은 남지 않는다.

```powershell
$migration = Get-Content -Raw .\backend\traffic\src\main\resources\db\migration\001_backend_schema_updates.sql
"BEGIN;`n$migration`nROLLBACK;" |
  docker exec -i traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f -
```

## 프로젝트 규칙

- 당분간 `spring.jpa.hibernate.ddl-auto=update`는 유지한다.
- `data.sql`에는 기준 seed 데이터만 둔다. 스키마 DDL은 넣지 않는다.
- 앞으로 스키마가 바뀌면 이미 공유한 migration 파일을 수정하지 말고 새 번호의 SQL 파일을 추가한다.
- 수동 데이터 정리가 필요한 migration은 SQL 주석에 사전 확인 방법과 rollback 기대치를 적는다.
