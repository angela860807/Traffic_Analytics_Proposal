from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Mapping


EXPECTED_FEATURES = (
    "fpsAvg",
    "frameDropRate",
    "latencyP95Ms",
    "blurScoreAvg",
    "ocrFailRate",
    "cpuUsagePct",
    "memoryUsagePct",
    "networkRttMs",
)
REQUIRED_ARTIFACT_FILES = (
    "lstm_ae.pt",
    "scaler.pkl",
    "threshold.json",
    "metrics.json",
    "feature_schema.json",
    "training_manifest.json",
)


@dataclass(frozen=True)
class PredictiveArtifactStatus:
    status: str
    model_dir: str
    feature_schema_version: str | None = None
    verified_files: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


@dataclass
class PredictiveArtifactValidator:
    model_dir: Path
    required: bool = False
    expected_sha256: Mapping[str, str] = field(default_factory=dict)

    def inspect(self) -> PredictiveArtifactStatus:
        if not self.model_dir.exists():
            status = "MISSING" if self.required else "NOT_CONFIGURED"
            return PredictiveArtifactStatus(
                status=status,
                model_dir=str(self.model_dir),
                errors=(f"model directory does not exist: {self.model_dir}",),
            )

        errors: list[str] = []
        verified_files: list[str] = []
        for filename in REQUIRED_ARTIFACT_FILES:
            path = self.model_dir / filename
            if not path.is_file():
                errors.append(f"required artifact is missing: {filename}")
                continue
            verified_files.append(filename)

        for filename, expected_hash in self.expected_sha256.items():
            path = self.model_dir / filename
            if not path.is_file():
                errors.append(f"checksum target is missing: {filename}")
                continue
            actual_hash = self._sha256(path)
            if actual_hash.lower() != expected_hash.lower():
                errors.append(f"SHA-256 mismatch: {filename}")

        feature_schema_version = None
        schema_path = self.model_dir / "feature_schema.json"
        if schema_path.is_file():
            try:
                feature_schema_version = self._validate_feature_schema(
                    schema_path
                )
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"invalid feature_schema.json: {exc}")

        status = "READY" if not errors else "INVALID"
        return PredictiveArtifactStatus(
            status=status,
            model_dir=str(self.model_dir),
            feature_schema_version=feature_schema_version,
            verified_files=tuple(sorted(verified_files)),
            errors=tuple(errors),
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as artifact_file:
            for chunk in iter(lambda: artifact_file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _validate_feature_schema(path: Path) -> str:
        payload = json.loads(path.read_text(encoding="utf-8"))
        version = payload.get("featureSchemaVersion") or payload.get("version")
        if not isinstance(version, str) or not version.strip():
            raise ValueError("feature schema version is required")

        raw_features = payload.get("features")
        if not isinstance(raw_features, list):
            raise ValueError("features must be a list")

        feature_names = []
        for item in raw_features:
            if isinstance(item, str):
                feature_names.append(item)
            elif isinstance(item, dict) and isinstance(item.get("name"), str):
                feature_names.append(item["name"])
            else:
                raise ValueError("each feature must be a name or object")

        if tuple(feature_names) != EXPECTED_FEATURES:
            raise ValueError(
                "feature order mismatch: "
                f"expected={list(EXPECTED_FEATURES)} actual={feature_names}"
            )
        return version
