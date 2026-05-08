INSERT INTO zones (zone_code, zone_name, zone_type, is_active, created_at)
VALUES ('ZONE_001', 'Main Entry Zone', 'ENTRY', true, now())
ON CONFLICT (zone_code) DO NOTHING;

INSERT INTO cameras (zone_id, camera_code, camera_name, stream_url, direction_type, is_active, created_at)
SELECT zone_id, 'CAM_001', 'Entry Camera 1', null, 'IN', true, now()
FROM zones
WHERE zone_code = 'ZONE_001'
ON CONFLICT (camera_code) DO NOTHING;
