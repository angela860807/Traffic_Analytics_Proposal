package com.example.traffic.service;

import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.util.PredictiveTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class TrafficContextAggregationService {

    private static final int WINDOW_MINUTES = 5;

    private final NamedParameterJdbcTemplate jdbcTemplate;

    @Transactional
    public int aggregatePreviousCompletedWindow(DataSourceType dataSource) {
        LocalDateTime windowEnd = floorToFiveMinutes(LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE));
        return aggregateWindow(dataSource, windowEnd.minusMinutes(WINDOW_MINUTES), windowEnd);
    }

    @Transactional
    public int aggregateWindow(DataSourceType dataSource, LocalDateTime windowStart, LocalDateTime windowEnd) {
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("dataSource", dataSource.name())
                .addValue("windowStart", windowStart)
                .addValue("windowEnd", windowEnd);

        return jdbcTemplate.update("""
                WITH flow_by_camera AS (
                    SELECT
                        camera_id,
                        COUNT(*)::INTEGER AS vehicle_count,
                        AVG(speed)::NUMERIC(7,2) AS avg_speed_kmh,
                        COUNT(speed)::INTEGER AS speed_measurement_count,
                        SUM(CASE WHEN flow_direction = 'IN' THEN 1 ELSE 0 END)::INTEGER AS in_count,
                        SUM(CASE WHEN flow_direction = 'OUT' THEN 1 ELSE 0 END)::INTEGER AS out_count,
                        MIN(flow_event_id) AS source_from_flow_event_id,
                        MAX(flow_event_id) AS source_to_flow_event_id
                    FROM vehicle_flow_events
                    WHERE event_at >= :windowStart
                      AND event_at < :windowEnd
                    GROUP BY camera_id
                ),
                ocr_by_camera AS (
                    SELECT
                        dl.camera_id,
                        COUNT(*)::INTEGER AS ocr_attempt_count,
                        SUM(CASE
                            WHEN dar.status <> 'OCR_FAILED'
                             AND dar.plate_number IS NOT NULL
                             AND dar.plate_number <> ''
                            THEN 1 ELSE 0
                        END)::INTEGER AS ocr_success_count,
                        SUM(CASE
                            WHEN dar.status = 'OCR_FAILED'
                              OR dar.plate_number IS NULL
                              OR dar.plate_number = ''
                            THEN 1 ELSE 0
                        END)::INTEGER AS ocr_failure_count
                    FROM detection_analysis_results dar
                    JOIN detection_logs dl
                      ON dl.detection_log_id = dar.detection_log_id
                    WHERE dar.processed_at >= :windowStart
                      AND dar.processed_at < :windowEnd
                    GROUP BY dl.camera_id
                ),
                violation_by_camera AS (
                    SELECT
                        camera_id,
                        COUNT(*)::INTEGER AS speed_violation_count
                    FROM speed_violations
                    WHERE violated_at >= :windowStart
                      AND violated_at < :windowEnd
                    GROUP BY camera_id
                ),
                target_cameras AS (
                    SELECT camera_id FROM flow_by_camera
                    UNION
                    SELECT camera_id FROM ocr_by_camera
                    UNION
                    SELECT camera_id FROM violation_by_camera
                )
                INSERT INTO traffic_context_samples (
                    camera_id,
                    zone_id,
                    sampled_at,
                    window_minutes,
                    vehicle_count,
                    avg_speed_kmh,
                    speed_measurement_count,
                    speed_violation_count,
                    ocr_attempt_count,
                    ocr_success_count,
                    ocr_failure_count,
                    in_count,
                    out_count,
                    data_source,
                    quality_status,
                    is_imputed,
                    source_from_flow_event_id,
                    source_to_flow_event_id,
                    idempotency_key,
                    created_at,
                    updated_at
                )
                SELECT
                    c.camera_id,
                    c.zone_id,
                    :windowStart,
                    5,
                    COALESCE(f.vehicle_count, 0),
                    f.avg_speed_kmh,
                    COALESCE(f.speed_measurement_count, 0),
                    COALESCE(v.speed_violation_count, 0),
                    COALESCE(o.ocr_attempt_count, 0),
                    COALESCE(o.ocr_success_count, 0),
                    COALESCE(o.ocr_failure_count, 0),
                    COALESCE(f.in_count, 0),
                    COALESCE(f.out_count, 0),
                    :dataSource,
                    CASE
                        WHEN COALESCE(f.vehicle_count, 0) = 0
                         AND COALESCE(o.ocr_attempt_count, 0) = 0
                        THEN 'INSUFFICIENT'
                        ELSE 'COMPLETE'
                    END,
                    FALSE,
                    f.source_from_flow_event_id,
                    f.source_to_flow_event_id,
                    CONCAT('traffic-context-', :dataSource, '-', c.camera_id, '-', TO_CHAR(CAST(:windowStart AS timestamp), 'YYYYMMDDHH24MI')),
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                FROM target_cameras tc
                JOIN cameras c
                  ON c.camera_id = tc.camera_id
                LEFT JOIN flow_by_camera f
                  ON f.camera_id = c.camera_id
                LEFT JOIN ocr_by_camera o
                  ON o.camera_id = c.camera_id
                LEFT JOIN violation_by_camera v
                  ON v.camera_id = c.camera_id
                ON CONFLICT (camera_id, zone_id, sampled_at)
                DO UPDATE SET
                    vehicle_count = EXCLUDED.vehicle_count,
                    avg_speed_kmh = EXCLUDED.avg_speed_kmh,
                    speed_measurement_count = EXCLUDED.speed_measurement_count,
                    speed_violation_count = EXCLUDED.speed_violation_count,
                    ocr_attempt_count = EXCLUDED.ocr_attempt_count,
                    ocr_success_count = EXCLUDED.ocr_success_count,
                    ocr_failure_count = EXCLUDED.ocr_failure_count,
                    in_count = EXCLUDED.in_count,
                    out_count = EXCLUDED.out_count,
                    data_source = EXCLUDED.data_source,
                    quality_status = EXCLUDED.quality_status,
                    is_imputed = EXCLUDED.is_imputed,
                    source_from_flow_event_id = EXCLUDED.source_from_flow_event_id,
                    source_to_flow_event_id = EXCLUDED.source_to_flow_event_id,
                    updated_at = CURRENT_TIMESTAMP
                """, params);
    }

    private LocalDateTime floorToFiveMinutes(LocalDateTime value) {
        int flooredMinute = (value.getMinute() / WINDOW_MINUTES) * WINDOW_MINUTES;
        return value.withMinute(flooredMinute).withSecond(0).withNano(0);
    }
}
