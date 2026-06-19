# TAS-PM DB TODO Progress - 2026-06-16

## Completed Today

- Added predictive maintenance schema migration:
  - `backend/traffic/src/main/resources/db/migration/007_predictive_maintenance_schema.sql`
- Added initial detector/policy seed migration:
  - `backend/traffic/src/main/resources/db/migration/008_predictive_seed_policies.sql`
- Added demo seed:
  - `db/seed/demo_seed.sql`
- Replaced validation SQL with executable checks:
  - `db/validation/data_quality_checks.sql`
- Added performance check folder and files:
  - `db/performance/load_test.sql`
  - `db/performance/explain_analyze.md`

## Important Project Decision

- Time columns remain `TIMESTAMP`, not `TIMESTAMPTZ`.
- Reason: the existing phase-1 backend already uses `TIMESTAMP`, and the team chose schema compatibility over changing the time type during this phase.

## Current DB Folder Shape

```text
backend/traffic/src/main/resources/db/migration/
  001_backend_schema_updates.sql
  002_cleanup_detection_logs_legacy_columns.sql
  003_detection_type_unknown_and_analysis_index.sql
  004_make_flow_metrics_nullable_until_estimated.sql
  005_speed_violation_status_values.sql
  006_speed_violation_reviews.sql
  007_predictive_maintenance_schema.sql
  008_predictive_seed_policies.sql

db/
  seed/demo_seed.sql
  queries/camera_baseline.sql
  queries/predictive_dashboard.sql
  validation/data_quality_checks.sql
  performance/load_test.sql
  performance/explain_analyze.md
  retention/purge_old_samples.sql
  security/roles.sql
```

## Next Checks Before Commit

```powershell
cd C:\bk\Traffic_Analytics_Proposal
git status
```

If PostgreSQL is available:

```powershell
psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f backend\traffic\src\main\resources\db\migration\007_predictive_maintenance_schema.sql
psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f backend\traffic\src\main\resources\db\migration\008_predictive_seed_policies.sql
psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f db\seed\demo_seed.sql
psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f db\validation\data_quality_checks.sql
psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f db\performance\load_test.sql
```

## Remaining DB Work

- Run migration on a clean local PostgreSQL DB.
- Run demo seed and validation SQL.
- Paste `EXPLAIN ANALYZE` results into `db/performance/explain_analyze.md`.
- Confirm Spring Boot JPA mapping with backend 담당자.
- Commit DB work separately from AI work.
