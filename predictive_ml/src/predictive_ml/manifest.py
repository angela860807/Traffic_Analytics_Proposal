from __future__ import annotations


def get_detector_manifest() -> dict:
    return {
        "package": {
            "name": "tas-predictive-ml",
            "version": "0.1.0",
        },
        "detectors": [
            {
                "name": "camera-rule",
                "version": "1.1.0",
                "method": "RULE",
                "operatingMode": "ACTIVE",
                "active": True,
            },
            {
                "name": "camera-robust-zscore",
                "version": "1.0.0",
                "method": "ROBUST_Z_SCORE",
                "operatingMode": "ACTIVE",
                "active": True,
            },
            {
                "name": "camera-trend-projection",
                "version": "1.0.0",
                "method": "TREND_PROJECTION",
                "operatingMode": "ACTIVE",
                "active": True,
            },
            {
                "name": "camera-context-cross-validator",
                "version": "1.0.0",
                "method": "CROSS_VALIDATION",
                "operatingMode": "ACTIVE",
                "active": True,
            },
            {
                "name": "camera-lstm-autoencoder",
                "version": "1.0.0",
                "method": "LSTM_AUTOENCODER",
                "operatingMode": "SHADOW",
                "active": False,
                "modelFormat": "PYTORCH",
                "featureSchemaVersion": "camera-health-sequence-v1",
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
