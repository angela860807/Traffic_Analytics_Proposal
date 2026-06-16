from __future__ import annotations

METRIC_DIRECTIONS: dict[str, str] = {
    "fps_avg": "LOWER_IS_WORSE",
    "frame_drop_rate": "HIGHER_IS_WORSE",
    "latency_p95_ms": "HIGHER_IS_WORSE",
    "blur_score_avg": "HIGHER_IS_WORSE",
    "ocr_fail_rate": "HIGHER_IS_WORSE",
    "cpu_usage_pct": "HIGHER_IS_WORSE",
    "memory_usage_pct": "HIGHER_IS_WORSE",
    "network_rtt_ms": "HIGHER_IS_WORSE",
}

METRIC_ANOMALY_TYPES: dict[str, str] = {
    "fps_avg": "FPS_DEGRADATION",
    "frame_drop_rate": "FRAME_DROP_DEGRADATION",
    "latency_p95_ms": "LATENCY_DEGRADATION",
    "blur_score_avg": "BLUR_DEGRADATION",
    "ocr_fail_rate": "OCR_QUALITY_DEGRADATION",
    "cpu_usage_pct": "RESOURCE_SATURATION",
    "memory_usage_pct": "RESOURCE_SATURATION",
    "network_rtt_ms": "NETWORK_INSTABILITY",
}

RULE_THRESHOLDS: dict[str, dict[str, float]] = {
    "last_frame_age_seconds": {"warning": 60.0, "critical": 180.0},
    "fps_avg": {"warning": 10.0, "critical": 5.0},
    "frame_drop_rate": {"warning": 0.30, "critical": 0.60},
    "latency_p95_ms": {"warning": 2000.0, "critical": 5000.0},
    "blur_score_avg": {"warning": 0.75, "critical": 0.90},
    "ocr_fail_rate": {"warning": 0.70, "critical": 0.90},
    "cpu_usage_pct": {"warning": 85.0, "critical": 95.0},
    "memory_usage_pct": {"warning": 85.0, "critical": 95.0},
    "network_rtt_ms": {"warning": 500.0, "critical": 1000.0},
}

RULE_CONSECUTIVE_WINDOWS: dict[str, int] = {
    "last_frame_age_seconds": 1,
    "fps_avg": 3,
    "frame_drop_rate": 3,
    "latency_p95_ms": 3,
    "blur_score_avg": 3,
    "ocr_fail_rate": 3,
    "cpu_usage_pct": 3,
    "memory_usage_pct": 3,
    "network_rtt_ms": 3,
}

METRIC_UNITS: dict[str, str] = {
    "fps_avg": "fps",
    "frame_drop_rate": "ratio",
    "latency_p95_ms": "ms",
    "blur_score_avg": "score",
    "ocr_fail_rate": "ratio",
    "cpu_usage_pct": "pct",
    "memory_usage_pct": "pct",
    "network_rtt_ms": "ms",
    "last_frame_age_seconds": "seconds",
}

SUSPECTED_CAUSES: dict[str, list[str]] = {
    "CAMERA_OFFLINE": ["CAMERA_POWER_OR_NETWORK", "NETWORK_CONGESTION"],
    "FPS_DEGRADATION": ["AI_PROCESSING_OVERLOAD", "CAMERA_POWER_OR_NETWORK"],
    "FRAME_DROP_DEGRADATION": ["AI_PROCESSING_OVERLOAD", "NETWORK_CONGESTION"],
    "LATENCY_DEGRADATION": ["AI_PROCESSING_OVERLOAD", "NETWORK_CONGESTION"],
    "BLUR_DEGRADATION": ["CAMERA_LENS_OR_FOCUS", "LOW_ILLUMINATION"],
    "OCR_QUALITY_DEGRADATION": ["OCR_PIPELINE_DEGRADATION", "CAMERA_LENS_OR_FOCUS"],
    "RESOURCE_SATURATION": ["AI_PROCESSING_OVERLOAD"],
    "NETWORK_INSTABILITY": ["NETWORK_CONGESTION", "CAMERA_POWER_OR_NETWORK"],
}
