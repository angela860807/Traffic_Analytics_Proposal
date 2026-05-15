-- Detection analysis contract update.
-- UNKNOWN means the AI result could not be confirmed as either PLATE or VEHICLE.

ALTER TABLE detection_analysis_results
DROP CONSTRAINT IF EXISTS detection_analysis_results_detection_type_check;

ALTER TABLE detection_analysis_results
ADD CONSTRAINT detection_analysis_results_detection_type_check
CHECK (detection_type IN ('PLATE', 'VEHICLE', 'UNKNOWN'));

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM traffic_analysis_index
        WHERE zone_id IS NULL
    ) THEN
        ALTER TABLE traffic_analysis_index
        ALTER COLUMN zone_id SET NOT NULL;
    END IF;
END $$;
