from __future__ import annotations

import json
import os
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import ModelPredictionInput, ShadowPredictionResult, ShadowTopFeature

DETECTOR_NAME = "camera-lstm-autoencoder"
DETECTOR_VERSION = "1.0.0"
ARTIFACT_VERSION = "v6_timepattern_precursor_thr999"
FEATURE_SCHEMA_VERSION = "camera-health-sequence-v1"

DEFAULT_FEATURES = [
    "fps_avg",
    "frame_drop_rate",
    "latency_p95_ms",
    "blur_score_avg",
    "ocr_fail_rate",
    "cpu_usage_pct",
    "memory_usage_pct",
    "network_rtt_ms",
]


@dataclass
class _ArtifactBundle:
    model: Any
    scaler: Any
    threshold: dict[str, Any]
    feature_schema: dict[str, Any]
    device: Any


_ARTIFACT_CACHE: _ArtifactBundle | None = None


def predict_anomaly(request: ModelPredictionInput) -> ShadowPredictionResult:
    """Run v6 LSTM-AE in SHADOW mode and return an API-contract friendly result."""
    input_window_from = request.sequence[0].sampled_at if request.sequence else None
    input_window_to = request.sequence[-1].sampled_at if request.sequence else None

    try:
        bundle = _load_artifacts()
        features = _feature_names(bundle)
        sequence_len = int(bundle.feature_schema.get("sequence_len", 30))
        if len(request.sequence) < sequence_len:
            return _skipped(
                request,
                input_window_from,
                input_window_to,
                "sequence_length_below_required",
            )

        sequence = request.sequence[-sequence_len:]
        matrix = _sample_matrix(sequence, features)
        scaled = bundle.scaler.transform(matrix)
        error, feature_errors = _reconstruction_error(bundle, scaled)

        warning_threshold = float(bundle.threshold["warning_threshold"])
        critical_threshold = float(bundle.threshold["critical_threshold"])
        predicted_severity = None
        if error >= critical_threshold:
            predicted_severity = "CRITICAL"
        elif error >= warning_threshold:
            predicted_severity = "WARNING"

        return ShadowPredictionResult(
            camera_id=request.camera_id,
            evaluated_at=request.sampled_at,
            input_window_from=input_window_from,
            input_window_to=input_window_to,
            anomaly_score=min(1.0, error / critical_threshold) if critical_threshold > 0 else None,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            predicted_anomaly=predicted_severity is not None,
            predicted_severity=predicted_severity,
            feature_schema_version=FEATURE_SCHEMA_VERSION,
            top_features=_top_features(features, feature_errors),
        )
    except Exception as exc:
        return _skipped(
            request,
            input_window_from,
            input_window_to,
            f"lstm_inference_unavailable:{type(exc).__name__}",
        )


def _load_artifacts() -> _ArtifactBundle:
    global _ARTIFACT_CACHE
    if _ARTIFACT_CACHE is not None:
        return _ARTIFACT_CACHE

    import torch
    import torch.nn as nn

    class LSTMEncoder(nn.Module):
        def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0,
            )

        def forward(self, x):
            _, (hidden, _) = self.lstm(x)
            return hidden[-1]

    class LSTMDecoder(nn.Module):
        def __init__(self, hidden_size: int, output_size: int, seq_len: int, num_layers: int, dropout: float):
            super().__init__()
            self.seq_len = seq_len
            self.lstm = nn.LSTM(
                input_size=hidden_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0,
            )
            self.fc = nn.Linear(hidden_size, output_size)

        def forward(self, z):
            z_rep = z.unsqueeze(1).repeat(1, self.seq_len, 1)
            out, _ = self.lstm(z_rep)
            return self.fc(out)

    class LSTMAutoEncoder(nn.Module):
        def __init__(self, input_size: int, hidden_size: int, num_layers: int, seq_len: int, dropout: float):
            super().__init__()
            self.encoder = LSTMEncoder(input_size, hidden_size, num_layers, dropout)
            self.decoder = LSTMDecoder(hidden_size, input_size, seq_len, num_layers, dropout)

        def forward(self, x):
            z = self.encoder(x)
            return self.decoder(z)

    model_dir = _model_dir()
    threshold = _read_json(model_dir / "threshold_v6_timepattern_precursor_thr999.json")
    feature_schema = _read_json(model_dir / "feature_schema_v6_timepattern_precursor.json")
    _validate_feature_schema(feature_schema, threshold)

    with (model_dir / "scaler_v6_timepattern_precursor.pkl").open("rb") as f:
        scaler = pickle.load(f)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LSTMAutoEncoder(
        input_size=len(_feature_names_from_schema(feature_schema)),
        hidden_size=128,
        num_layers=2,
        seq_len=int(feature_schema["sequence_len"]),
        dropout=0.2,
    ).to(device)
    model_path = model_dir / "lstm_ae_v6_timepattern_precursor_thr999.pt"
    try:
        state = torch.load(model_path, map_location=device, weights_only=True)
    except TypeError:
        state = torch.load(model_path, map_location=device)
    model.load_state_dict(state)
    model.eval()

    _ARTIFACT_CACHE = _ArtifactBundle(
        model=model,
        scaler=scaler,
        threshold=threshold,
        feature_schema=feature_schema,
        device=device,
    )
    return _ARTIFACT_CACHE


def _model_dir() -> Path:
    configured = os.getenv("TAS_PM_LSTM_AE_MODEL_DIR")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2] / "model"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate_feature_schema(feature_schema: dict[str, Any], threshold: dict[str, Any]) -> None:
    schema_features = _feature_names_from_schema(feature_schema)
    threshold_features = threshold.get("features", [])
    if schema_features != DEFAULT_FEATURES:
        raise ValueError("feature schema does not match expected v6 feature order")
    if threshold_features and threshold_features != schema_features:
        raise ValueError("threshold feature order does not match feature schema")
    if feature_schema.get("feature_schema_version") != FEATURE_SCHEMA_VERSION:
        raise ValueError("unsupported feature schema version")


def _feature_names(bundle: _ArtifactBundle) -> list[str]:
    return _feature_names_from_schema(bundle.feature_schema)


def _feature_names_from_schema(feature_schema: dict[str, Any]) -> list[str]:
    return list(feature_schema.get("features", []))


def _sample_matrix(sequence, features: list[str]):
    import numpy as np

    rows: list[list[float]] = []
    for sample in sequence:
        if sample.quality_status != "COMPLETE" or sample.is_imputed or sample.is_late_sample:
            raise ValueError("sample quality is not eligible for LSTM inference")
        row: list[float] = []
        for feature in features:
            value = getattr(sample, feature)
            if value is None:
                raise ValueError(f"missing feature: {feature}")
            row.append(float(value))
        rows.append(row)
    return np.array(rows, dtype="float32")


def _reconstruction_error(bundle: _ArtifactBundle, scaled_matrix):
    import numpy as np
    import torch

    x = torch.tensor(scaled_matrix, dtype=torch.float32, device=bundle.device).unsqueeze(0)
    with torch.no_grad():
        x_hat = bundle.model(x)
        diff = (x - x_hat) ** 2
        overall_error = diff.mean(dim=(1, 2)).cpu().numpy()[0]
        feature_errors = diff.mean(dim=1).cpu().numpy()[0]
    return float(overall_error), np.asarray(feature_errors, dtype="float64")


def _top_features(features: list[str], feature_errors, limit: int = 3) -> list[ShadowTopFeature]:
    total = float(feature_errors.sum())
    ranked = sorted(
        zip(features, feature_errors.tolist()),
        key=lambda item: item[1],
        reverse=True,
    )[:limit]
    return [
        ShadowTopFeature(
            feature_name=_to_camel_case(name),
            feature_value=round((float(value) / total) if total > 0 else 0.0, 6),
        )
        for name, value in ranked
    ]


def _to_camel_case(name: str) -> str:
    first, *rest = name.split("_")
    return first + "".join(part.capitalize() for part in rest)


def _skipped(
    request: ModelPredictionInput,
    input_window_from,
    input_window_to,
    reason: str,
) -> ShadowPredictionResult:
    return ShadowPredictionResult(
        camera_id=request.camera_id,
        evaluated_at=request.sampled_at,
        input_window_from=input_window_from,
        input_window_to=input_window_to,
        predicted_anomaly=False,
        feature_schema_version=FEATURE_SCHEMA_VERSION,
        skipped_reason=reason,
    )
