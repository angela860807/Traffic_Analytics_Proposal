from __future__ import annotations


def get_detector_manifest() -> dict:
    return {
        "package": {
            "name": "tas-predictive-ml",
            "version": "0.1.0",
        },
        "detectors": [
            {
                "detectorName": "camera-rule",
                "version": "1.1.0",
                "detectionMethod": "RULE",
                "operatingMode": "ACTIVE",
            },
            {
                "detectorName": "camera-robust-zscore",
                "version": "1.0.0",
                "detectionMethod": "ROBUST_Z_SCORE",
                "operatingMode": "ACTIVE",
            },
            {
                "detectorName": "camera-trend-projection",
                "version": "1.0.0",
                "detectionMethod": "TREND_PROJECTION",
                "operatingMode": "ACTIVE",
            },
            {
                "detectorName": "camera-context-cross-validator",
                "version": "1.0.0",
                "detectionMethod": "CROSS_VALIDATION",
                "operatingMode": "ACTIVE",
                "status": "contract-pending",
            },
            {
                "detectorName": "camera-lstm-autoencoder",
                "version": "1.0.0",
                "detectionMethod": "LSTM_AUTOENCODER",
                "operatingMode": "SHADOW",
                "artifactVersion": "v6_timepattern_precursor_thr999",
            },
        ],
        "featureSchema": {
            "version": "camera-health-v1",
            "features": [
                "fps_avg",
                "frame_drop_rate",
                "latency_p95_ms",
                "blur_score_avg",
                "ocr_fail_rate",
                "cpu_usage_pct",
                "memory_usage_pct",
                "network_rtt_ms",
            ],
        },
    }
