-- Development migration notes for backend schema changes.
-- Apply manually when the local PostgreSQL schema is behind the Spring entities.

-- 1. detection_logs.status
ALTER TABLE detection_logs
ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED';

CREATE INDEX IF NOT EXISTS idx_status
ON detection_logs(status);

-- 2. traffic_analysis_index.zone_id
ALTER TABLE traffic_analysis_index
ADD COLUMN IF NOT EXISTS zone_id BIGINT;

-- Run only after confirming traffic_analysis_index has no rows with zone_id IS NULL.
ALTER TABLE traffic_analysis_index
ALTER COLUMN zone_id SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'traffic_analysis_index'
          AND constraint_name = 'fk_traffic_analysis_index_zone'
    ) THEN
        ALTER TABLE traffic_analysis_index
        ADD CONSTRAINT fk_traffic_analysis_index_zone
        FOREIGN KEY (zone_id) REFERENCES zones(zone_id);
    END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS uk_traffic_analysis_index_zone
ON traffic_analysis_index(zone_id);
