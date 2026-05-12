-- Development migration notes for backend schema changes.
-- Apply manually when the local PostgreSQL schema is behind the Spring entities.

-- 1. detection_logs.status
ALTER TABLE detection_logs
ADD COLUMN IF NOT EXISTS status VARCHAR(30) NOT NULL DEFAULT 'RECEIVED';

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

-- 3. vehicle_flow_events analysis columns
ALTER TABLE vehicle_flow_events
ADD COLUMN IF NOT EXISTS speed NUMERIC(5, 2) DEFAULT 0.00;

ALTER TABLE vehicle_flow_events
ADD COLUMN IF NOT EXISTS stay_time BIGINT DEFAULT 0;

-- 4. hourly_traffic_stats extended analysis columns
ALTER TABLE hourly_traffic_stats
ADD COLUMN IF NOT EXISTS average_speed NUMERIC(5, 2) NOT NULL DEFAULT 0.00;

ALTER TABLE hourly_traffic_stats
ADD COLUMN IF NOT EXISTS congestion_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00;

ALTER TABLE hourly_traffic_stats
ADD COLUMN IF NOT EXISTS average_stay_time NUMERIC(10, 2) NOT NULL DEFAULT 0.00;

ALTER TABLE hourly_traffic_stats
ADD COLUMN IF NOT EXISTS duplicate_vehicle_count INTEGER NOT NULL DEFAULT 0;

ALTER TABLE hourly_traffic_stats
ADD COLUMN IF NOT EXISTS last_log_id BIGINT NOT NULL DEFAULT 0;

-- 5. detection_logs 컬럼 4개 추가
ALTER TABLE detection_logs
  ADD COLUMN IF NOT EXISTS plate_crop_image_path TEXT,
  ADD COLUMN IF NOT EXISTS plate_crop_image_url TEXT,
  ADD COLUMN IF NOT EXISTS ocr_image_path TEXT,
  ADD COLUMN IF NOT EXISTS ocr_image_url TEXT;
