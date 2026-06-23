-- Keep active anomaly de-duplication scoped to each data source.
-- REAL demo injections must not conflict with seeded FAULT_INJECTED events
-- for the same camera and anomaly type.

DROP INDEX IF EXISTS ux_anomaly_events_active;

CREATE UNIQUE INDEX IF NOT EXISTS ux_anomaly_events_active
    ON anomaly_events (target_camera_id, anomaly_type, data_source)
    WHERE status IN ('OPEN', 'ACKNOWLEDGED', 'RECOVERED');
