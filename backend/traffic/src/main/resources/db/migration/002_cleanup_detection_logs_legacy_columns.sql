-- Cleanup legacy detection_logs columns after moving analysis data to
-- detection_analysis_results.
--
-- Current ownership:
-- - detection_logs: source frame log only
-- - detection_analysis_results: OCR/status/confidence/crop/preprocessed result data

ALTER TABLE detection_logs
DROP CONSTRAINT IF EXISTS detection_logs_status_check;

DROP INDEX IF EXISTS idx_status;

ALTER TABLE detection_logs
DROP COLUMN IF EXISTS confidence_score CASCADE,
DROP COLUMN IF EXISTS detection_type CASCADE,
DROP COLUMN IF EXISTS plate_number CASCADE,
DROP COLUMN IF EXISTS preprocessed_path CASCADE,
DROP COLUMN IF EXISTS status CASCADE,
DROP COLUMN IF EXISTS vehicle_id CASCADE;
