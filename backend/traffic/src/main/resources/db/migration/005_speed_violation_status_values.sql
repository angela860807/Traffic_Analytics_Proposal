ALTER TABLE speed_violations
DROP CONSTRAINT IF EXISTS speed_violations_violation_status_check;

ALTER TABLE speed_violations
ADD CONSTRAINT speed_violations_violation_status_check
CHECK (violation_status IN ('UNPROCESSED', 'NOTIFIED', 'REJECTED', 'CLOSED'));
