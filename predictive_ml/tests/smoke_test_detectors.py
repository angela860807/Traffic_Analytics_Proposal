from __future__ import annotations

from datetime import datetime, timedelta

from predictive_ml import (
    BaselineMetric,
    CameraSample,
    DegradationDetectionInput,
    RuleDetectionInput,
    TrendPoint,
    detect_degradation,
    detect_rules,
    get_detector_manifest,
)


def main() -> None:
    now = datetime(2026, 6, 16, 12, 0, 0)
    sample = CameraSample(
        camera_id=1,
        sampled_at=now,
        fps_avg=7.5,
        frame_drop_rate=0.12,
        latency_p95_ms=800,
        blur_score_avg=0.2,
        ocr_fail_rate=0.1,
        cpu_usage_pct=72,
        memory_usage_pct=65,
        network_rtt_ms=70,
        last_frame_age_seconds=10,
        ocr_attempt_count=40,
    )

    rule_result = detect_rules(
        RuleDetectionInput(
            sample=sample,
            consecutive_windows={"fps_avg": 3},
        )
    )
    assert rule_result.status == "WARNING"
    assert rule_result.detector.method == "RULE"
    assert rule_result.candidates[0].anomaly_type == "FPS_DEGRADATION"

    baselines = {
        "fps_avg": BaselineMetric(median=28.0, mad=1.0, sample_count=42),
    }
    trends = {
        "fps_avg": [
            TrendPoint(sampled_at=now - timedelta(minutes=14 - i), value=20.0 - (i * 1.0))
            for i in range(15)
        ]
    }
    degradation_result = detect_degradation(
        DegradationDetectionInput(
            sample=sample,
            baselines=baselines,
            trends=trends,
            prediction_horizon_minutes=10,
        )
    )
    assert degradation_result.status in {"WARNING", "CRITICAL"}
    assert degradation_result.baseline_status == "READY"
    assert degradation_result.detector.method == "TREND_PROJECTION"
    assert get_detector_manifest()["package"]["name"] == "tas-predictive-ml"
    print("predictive_ml detector smoke test passed")


if __name__ == "__main__":
    main()
