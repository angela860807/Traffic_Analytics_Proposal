# TAS-PM DB Performance Notes

Date: 2026-06-16  
DBMS: PostgreSQL 16  
Scope: predictive maintenance schema, seed, dashboard/baseline queries

## Purpose

This document records the DB-side performance checks for TAS-PM predictive maintenance.
Run `db/performance/load_test.sql` after applying migrations `001` through `008` and the demo seed.

## Run Order

```powershell
cd C:\bk\Traffic_Analytics_Proposal
psql -U traffic_migrator -d traffic -v ON_ERROR_STOP=1 -f backend\traffic\src\main\resources\db\migration\007_predictive_maintenance_schema.sql
psql -U traffic_migrator -d traffic -v ON_ERROR_STOP=1 -f backend\traffic\src\main\resources\db\migration\008_predictive_seed_policies.sql
psql -U traffic_app -d traffic -v ON_ERROR_STOP=1 -f db\seed\demo_seed.sql
psql -U traffic_app -d traffic -v ON_ERROR_STOP=1 -f db\validation\data_quality_checks.sql
psql -U traffic_readonly -d traffic -v ON_ERROR_STOP=1 -f db\performance\load_test.sql
```

Use the project team's actual local DB user if the separated roles have not been created yet.

## Measurement Targets

| Check | Target |
|---|---:|
| Latest camera health by camera | p95 under 2s |
| 60-minute health window | p95 under 2s |
| 14-day same-bucket baseline | p95 under 2s |
| Active anomaly dashboard list | p95 under 2s |
| Latest LSTM AE shadow prediction | p95 under 2s |

## Result Log

| Query | Rows | Execution Time | Buffers Summary | Notes |
|---|---:|---:|---|---|
| Latest camera health by camera | TBD | TBD | TBD |  |
| 60-minute health window | TBD | TBD | TBD |  |
| 14-day same-bucket baseline | TBD | TBD | TBD |  |
| Active anomaly dashboard list | TBD | TBD | TBD |  |
| Latest LSTM AE shadow prediction | TBD | TBD | TBD |  |

## Index Review

After running `load_test.sql`, check whether the following indexes are used:

| Table | Expected Index |
|---|---|
| camera_health_samples | idx_camera_health_samples_camera_sampled |
| camera_health_samples | idx_camera_health_samples_datasource_sampled |
| traffic_context_samples | idx_traffic_context_samples_camera_sampled |
| anomaly_events | idx_anomaly_events_status_severity_time |
| anomaly_events | ux_anomaly_events_active |
| model_prediction_logs | idx_model_prediction_logs_camera_evaluated |
| maintenance_tickets | idx_maintenance_tickets_status_priority |

## Notes

- Do not add more indexes until a measured query shows a bottleneck.
- Large historical tables can be considered for BRIN on `sampled_at`, but that is not part of the current MVP unless measurements require it.
- Demo seed and production-like bulk seed should be measured separately.
