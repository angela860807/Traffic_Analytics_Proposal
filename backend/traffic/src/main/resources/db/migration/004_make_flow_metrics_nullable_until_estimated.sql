-- Speed and stay time are future analysis metrics.
-- Keep them NULL until an explicit estimation rule is implemented.

ALTER TABLE vehicle_flow_events
ALTER COLUMN speed DROP DEFAULT;

ALTER TABLE vehicle_flow_events
ALTER COLUMN stay_time DROP DEFAULT;

UPDATE vehicle_flow_events
SET speed = NULL
WHERE speed = 0.00;

UPDATE vehicle_flow_events
SET stay_time = NULL
WHERE stay_time = 0;
