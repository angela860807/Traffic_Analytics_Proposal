# Development Migration Notes

`spring.jpa.hibernate.ddl-auto=update` can create simple columns during local development, but keep the intended PostgreSQL DDL explicit so the team can apply it safely when a shared DB is used.

```sql
ALTER TABLE detection_logs
    ADD COLUMN IF NOT EXISTS status VARCHAR(30) NOT NULL DEFAULT 'RECEIVED';

ALTER TABLE detection_logs
    ALTER COLUMN plate_number DROP NOT NULL;

ALTER TABLE detection_logs
    DROP CONSTRAINT IF EXISTS detection_logs_status_check;

ALTER TABLE detection_logs
    ADD CONSTRAINT detection_logs_status_check
    CHECK (status IN ('RECEIVED', 'OCR_FAILED', 'FLOW_EVENT_CREATED', 'DUPLICATE_SKIPPED'));

CREATE INDEX IF NOT EXISTS idx_status
    ON detection_logs (status);

ALTER TABLE traffic_analysis_index
    ADD COLUMN IF NOT EXISTS zone_id BIGINT;

ALTER TABLE traffic_analysis_index
    ADD CONSTRAINT fk_traffic_analysis_index_zone
    FOREIGN KEY (zone_id)
    REFERENCES zones(zone_id);

CREATE INDEX IF NOT EXISTS idx_traffic_analysis_index_zone
    ON traffic_analysis_index(zone_id);

CREATE UNIQUE INDEX IF NOT EXISTS uk_traffic_analysis_index_zone
    ON traffic_analysis_index(zone_id);
```
