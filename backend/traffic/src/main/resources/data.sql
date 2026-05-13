INSERT INTO zones (zone_code, zone_name, zone_type, is_active, created_at)
VALUES ('ZONE_001', 'Main Entry Zone', 'ENTRY', true, now())
ON CONFLICT (zone_code) DO NOTHING;

INSERT INTO cameras (zone_id, camera_code, camera_name, stream_url, direction_type, is_active, created_at)
SELECT zone_id, 'CAM_001', 'Entry Camera 1', null, 'IN', true, now()
FROM zones
WHERE zone_code = 'ZONE_001'
ON CONFLICT (camera_code) DO NOTHING;

ALTER TABLE detection_logs ALTER COLUMN plate_number DROP NOT NULL;
ALTER TABLE detection_logs ALTER COLUMN detection_type DROP NOT NULL;

ALTER TABLE detection_logs DROP CONSTRAINT IF EXISTS detection_logs_status_check;
ALTER TABLE detection_logs
ADD CONSTRAINT detection_logs_status_check
CHECK (status IN ('RECEIVED', 'OCR_FAILED', 'FLOW_EVENT_CREATED', 'DUPLICATE_SKIPPED'));


INSERT INTO members (email, password, name, phone, role, status, created_at)
VALUES (
    'user1@email.com',
    '$2y$10$UxDhYVBOy1yX6q8T25kmdu19pXXn4YuBZ8Tpiw6LPP6sCA2K.T2RK',
    '이용자',
    '010-1234-5678',
    'USER',
    'ACTIVE',
    now()
)
ON CONFLICT DO NOTHING;

INSERT INTO members (email, password, name, phone, role, status, created_at)
VALUES (
    'admin@email.com',
    '$2y$10$UxDhYVBOy1yX6q8T25kmdu19pXXn4YuBZ8Tpiw6LPP6sCA2K.T2RK',
    '관리자',
    '010-1234-1234',
    'ADMIN',
    'ACTIVE',
    now()
)
ON CONFLICT DO NOTHING;
