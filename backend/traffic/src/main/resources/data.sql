INSERT INTO zones (zone_code, zone_name, zone_type, is_active, created_at)
VALUES ('ZONE_001', 'Main Entry Zone', 'ENTRY', true, now())
ON CONFLICT (zone_code) DO NOTHING;

INSERT INTO cameras (zone_id, camera_code, camera_name, stream_url, direction_type, is_active, created_at)
SELECT zone_id, 'CAM_001', '정문 진입 관제 카메라', null, 'IN', true, now()
FROM zones
WHERE zone_code = 'ZONE_001'
ON CONFLICT (camera_code) DO NOTHING;

INSERT INTO members (email, password, name, phone, role, status, created_at)
VALUES (
    'user1@email.com',
    '$2a$10$ycTu6wBS5/pbCrL23CJlbuAMZluVx9jSoqS0Z9TB3e10q5r6lvE6K',
    '이용자',
    '010-1234-5678',
    'USER',
    'ACTIVE',
    now()
)
ON CONFLICT (email) DO UPDATE
SET password = EXCLUDED.password,
    name = EXCLUDED.name,
    phone = EXCLUDED.phone,
    role = EXCLUDED.role,
    status = EXCLUDED.status;

INSERT INTO members (email, password, name, phone, role, status, created_at)
VALUES (
    'admin@email.com',
    '$2a$10$ycTu6wBS5/pbCrL23CJlbuAMZluVx9jSoqS0Z9TB3e10q5r6lvE6K',
    '관리자',
    '010-1234-1234',
    'ADMIN',
    'ACTIVE',
    now()
)
ON CONFLICT (email) DO UPDATE
SET password = EXCLUDED.password,
    name = EXCLUDED.name,
    phone = EXCLUDED.phone,
    role = EXCLUDED.role,
    status = EXCLUDED.status;
