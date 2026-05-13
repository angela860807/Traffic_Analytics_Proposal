-- Development migration notes for backend schema changes.
-- Apply manually when the local PostgreSQL schema is behind the Spring entities.

-- 1. detection_logs.status legacy column
-- Kept for existing shared DBs during stabilization. New code writes status to
-- detection_analysis_results instead of updating detection_logs.
ALTER TABLE detection_logs
ADD COLUMN IF NOT EXISTS status VARCHAR(30) NOT NULL DEFAULT 'RECEIVED';

CREATE INDEX IF NOT EXISTS idx_status
ON detection_logs(status);

-- Append-only detection_logs no longer writes result columns. Keep legacy
-- columns nullable until they are removed after stabilization.
ALTER TABLE detection_logs
ALTER COLUMN plate_number DROP NOT NULL;

ALTER TABLE detection_logs
ALTER COLUMN detection_type DROP NOT NULL;

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

-- 5. detection_analysis_results append-only processing result table
CREATE TABLE IF NOT EXISTS detection_analysis_results (
    analysis_result_id BIGSERIAL PRIMARY KEY,
    detection_log_id BIGINT NOT NULL REFERENCES detection_logs(detection_log_id),
    attempt_no INTEGER NOT NULL DEFAULT 1,
    processor_type VARCHAR(30) NOT NULL DEFAULT 'FASTAPI_OCR',
    status VARCHAR(30) NOT NULL,
    plate_number VARCHAR(20),
    detection_type VARCHAR(20) NOT NULL,
    confidence_score NUMERIC(5,4),
    plate_crop_image_path TEXT,
    plate_crop_image_url TEXT,
    ocr_image_path TEXT,
    ocr_image_url TEXT,
    processed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analysis_results_log_id
ON detection_analysis_results(detection_log_id);

CREATE INDEX IF NOT EXISTS idx_analysis_results_status_created
ON detection_analysis_results(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_analysis_results_plate_created
ON detection_analysis_results(plate_number, created_at DESC);

ALTER TABLE vehicle_flow_events
ADD COLUMN IF NOT EXISTS source_analysis_result_id BIGINT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'vehicle_flow_events'
          AND constraint_name = 'fk_flow_event_analysis_result'
    ) THEN
        ALTER TABLE vehicle_flow_events
        ADD CONSTRAINT fk_flow_event_analysis_result
        FOREIGN KEY (source_analysis_result_id)
        REFERENCES detection_analysis_results(analysis_result_id);
    END IF;
END $$;
