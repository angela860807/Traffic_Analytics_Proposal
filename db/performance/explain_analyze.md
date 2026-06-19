# TAS-PM DB Performance / Validation Notes

Date: 2026-06-17 ~ 2026-06-18  
DBMS: PostgreSQL 16 Docker container (`traffic-postgres`)  
Database: `traffic`  
Schema: `public`  
Scope: predictive maintenance migration, demo seed, validation checks, performance/index checks

## Purpose

This document records the DB-side verification performed before handing the predictive maintenance DB artifacts to the backend part. The goal was to confirm that migrations `007` and `008`, demo seed data, validation SQL, and performance/index checks can run on the local PostgreSQL container.

## Environment

```text
Project path: C:\bk\Traffic_Analytics_Proposal
Branch: kyung
Container: traffic-postgres
PostgreSQL port: 5432 -> 5432
DB user: postgres
DB name: traffic
```

PowerShell was used because local `psql` was not available on the Windows PATH. SQL files were copied into the container and executed with `docker exec`.

## Run Order

```powershell
docker cp backend\traffic\src\main\resources\db\migration\007_predictive_maintenance_schema.sql traffic-postgres:/tmp/007.sql
docker exec traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f /tmp/007.sql

docker cp backend\traffic\src\main\resources\db\migration\008_predictive_seed_policies.sql traffic-postgres:/tmp/008.sql
docker exec traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f /tmp/008.sql

docker cp db\seed\demo_seed.sql traffic-postgres:/tmp/demo_seed.sql
docker exec traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f /tmp/demo_seed.sql

docker cp db\validation\data_quality_checks.sql traffic-postgres:/tmp/data_quality_checks.sql
docker exec traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f /tmp/data_quality_checks.sql

docker cp db\performance\load_test.sql traffic-postgres:/tmp/load_test.sql
docker exec traffic-postgres psql -U postgres -d traffic -v ON_ERROR_STOP=1 -f /tmp/load_test.sql
```

## Migration Results

| Step | Result | Notes |
|---|---|---|
| `007_predictive_maintenance_schema.sql` | Success | Tables, indexes, and `maintenance_ticket_number_seq` were created. |
| `008_predictive_seed_policies.sql` | Success | `detector_versions` 5 rows and initial `anomaly_policies` were inserted. |
| Table check | Success | `\dt` showed 26 tables including existing TAS tables and predictive maintenance tables. |

Predictive maintenance tables confirmed:

```text
anomaly_event_evidence
anomaly_events
anomaly_policies
camera_health_samples
camera_links
detector_versions
maintenance_ticket_histories
maintenance_tickets
model_prediction_logs
traffic_context_samples
```

## Demo Seed Result

`demo_seed.sql` completed with `COMMIT` after troubleshooting and fixes.

Final seed summary:

| Table / Data Group | Row Count |
|---|---:|
| members total | 4 |
| camera_health_samples SIMULATED | 674 |
| camera_health_samples FAULT_INJECTED | 75 |
| traffic_context_samples | 24 |
| camera_links | 4 |
| anomaly_events SIMULATED | 1 |
| anomaly_events FAULT_INJECTED | 3 |
| anomaly_event_evidence | 3 |
| model_prediction_logs | 7 |
| maintenance_tickets | 3 |
| maintenance_ticket_histories | 7 |

## Troubleshooting During Verification

| Issue | Cause | Fix |
|---|---|---|
| `members_role_check` violation for `OPERATOR` | Existing `members.role` constraint allowed only `USER`, `ADMIN`. | Extended `members_role_check` to allow `OPERATOR`, `MAINTAINER`. |
| FK violation for `camera_id=2` | Clean local DB had only `CAM_001`; demo seed expects cameras 1~5. | Added base zone/camera bootstrap to `demo_seed.sql`. |
| `chk_traffic_context_ocr_counts` violation | Demo traffic context row had `ocr_success_count + ocr_failure_count > ocr_attempt_count`. | Adjusted failure count formula in `demo_seed.sql`. |
| `invalid byte sequence for encoding UTF8` | File was rewritten with an incompatible encoding during local PowerShell editing. | Restored committed UTF-8 seed and rewrote it as UTF-8 without BOM. |
| `feature_schema_version` length violation | `camera-health-sequence-v1` exceeded `VARCHAR(20)`. | Expanded `feature_schema_version` to `VARCHAR(100)` in `007` migration. |
| pgAdmin connection confusion | pgAdmin displayed another local DB connection and failed to show `traffic`. | Continued verification with Docker `psql`, which directly confirmed the target DB. |

## Validation SQL Result

`data_quality_checks.sql` executed successfully.

Checks returning 0 rows:

```text
duplicate camera health samples
duplicate idempotency keys
future sample timestamps
metric range violations
camera health OCR count violations
orphan camera health samples
duplicate traffic context samples
traffic context OCR count violations
active duplicate anomaly events
tickets without anomaly events
invalid ticket histories
invalid model prediction severity/window/threshold values
SHADOW prediction direct anomaly FK violation
```

Expected demo scenario warnings:

| Check | Rows | Interpretation |
|---|---:|---|
| `baseline_source_mixed_by_camera_day` | 3 | Expected because demo data intentionally includes `SIMULATED` and `FAULT_INJECTED` on the same day for cameras 2, 3, 4. |
| `insufficient_baseline_samples` | 2 | Expected: camera 5 is a baseline-learning scenario, and camera 3 `FAULT_INJECTED` is an injected fault segment. |
| `model_prediction_logs_has_no_anomaly_event_fk` | OK | Expected SHADOW behavior. |

## Performance / Index Check Result

`load_test.sql` executed successfully. The final `pg_stat_user_indexes` output confirmed that key indexes were exercised during the check.

Indexes observed with scans:

| Table | Index | Observation |
|---|---|---|
| `anomaly_events` | `ux_anomaly_events_active` | Used by active anomaly checks. |
| `anomaly_events` | `anomaly_events_pkey` | Used. |
| `anomaly_events` | `idx_anomaly_events_camera_status` | Used. |
| `anomaly_events` | `idx_anomaly_events_status_severity_time` | Used. |
| `camera_health_samples` | `uq_camera_health_samples_idempotency` | Heavily used during seed conflict checks. |
| `camera_health_samples` | `idx_camera_health_samples_datasource_sampled` | Used. |
| `maintenance_tickets` | `maintenance_tickets_pkey` | Used. |
| `maintenance_tickets` | `uq_maintenance_tickets_anomaly_event` | Used. |
| `model_prediction_logs` | `uq_model_prediction_logs_camera_detector_evaluated` | Used. |
| `traffic_context_samples` | `uq_traffic_context_camera_zone_sampled` | Used. |

Some indexes showed `idx_scan = 0` in the demo run. This is acceptable for the current MVP because the dataset is small and the load test does not cover every production API query path. Additional indexes should be added only after measured bottlenecks appear.

## Screenshot Evidence

Screenshots were captured during verification and are currently in the Codex clipboard temp directory. They should be copied into a stable project/report folder before final documentation submission if image evidence is required.

Captured evidence includes:

```text
007/008 migration success output
table list after migration
members_role_check violation and fix
camera FK violation and camera bootstrap fix
traffic context OCR count violation
feature_schema_version length violation
successful demo_seed COMMIT and row-count summary
validation SQL output
performance/index usage output
```

Latest clipboard screenshot observed:

```text
C:\Users\User\AppData\Local\Temp\codex-clipboard-502f6c97-16f9-4ec7-a706-5b18416888ed.png
```

## Handoff Notes

- Root `db/` remains the DB part artifact source.
- A backend-local copy is also provided under `backend/traffic/src/main/resources/db/` for backend verification convenience.
- Backend branch `min` can cherry-pick commit `ff3f16a` from `kyung` to import the DB verification fixes and backend-local DB artifacts.
- `TIMESTAMP` is intentionally kept instead of `TIMESTAMPTZ` to match the existing phase-1 Spring backend `LocalDateTime` mapping decision.

## Current Status

DB implementation and local verification are complete for handoff.

Remaining checks are owned by integration steps:

```text
Spring Entity/JPA mapping validation
Spring ddl-auto=validate or equivalent backend startup validation
Backend service behavior for duplicate/constraint errors
AI export query usage during AI/FastAPI integration
```
