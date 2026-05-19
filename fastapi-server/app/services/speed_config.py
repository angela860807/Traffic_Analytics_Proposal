from dataclasses import dataclass
import json
from typing import Any

from app.core.config import (
    SPEED_CAMERA_CONFIGS_JSON,
    SPEED_DEFAULT_DISTANCE_METERS,
    SPEED_DEFAULT_LIMIT_KMH,
    SPEED_DEFAULT_LINE_A,
    SPEED_DEFAULT_LINE_B,
    SPEED_DETECTION_ENABLED,
    SPEED_MAX_REASONABLE_KMH,
    SPEED_MIN_ELAPSED_SECONDS,
    SPEED_TRACK_MAX_DISTANCE_PIXELS,
    SPEED_TRACK_TTL_SECONDS,
)


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class VirtualLine:
    start: Point
    end: Point


@dataclass(frozen=True)
class SpeedCameraConfig:
    camera_code: str
    line_a: VirtualLine
    line_b: VirtualLine
    distance_meters: float
    speed_limit_kmh: float
    enabled: bool = True


@dataclass(frozen=True)
class SpeedTrackingConfig:
    max_match_distance_pixels: float
    track_ttl_seconds: float
    min_elapsed_seconds: float
    max_reasonable_kmh: float


def parse_virtual_line(value: str | list[int] | tuple[int, ...]) -> VirtualLine:
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",")]
        if len(parts) != 4:
            raise ValueError("virtual line must contain four comma-separated integers")
        coordinates = [int(part) for part in parts]
    else:
        coordinates = [int(part) for part in value]
        if len(coordinates) != 4:
            raise ValueError("virtual line must contain four integers")

    x1, y1, x2, y2 = coordinates
    if x1 == x2 and y1 == y2:
        raise ValueError("virtual line start and end points must differ")

    return VirtualLine(start=Point(x=x1, y=y1), end=Point(x=x2, y=y2))


def build_default_speed_config(camera_code: str) -> SpeedCameraConfig:
    return SpeedCameraConfig(
        camera_code=camera_code,
        line_a=parse_virtual_line(SPEED_DEFAULT_LINE_A),
        line_b=parse_virtual_line(SPEED_DEFAULT_LINE_B),
        distance_meters=SPEED_DEFAULT_DISTANCE_METERS,
        speed_limit_kmh=SPEED_DEFAULT_LIMIT_KMH,
        enabled=SPEED_DETECTION_ENABLED,
    )


def load_speed_camera_configs(raw_json: str) -> dict[str, SpeedCameraConfig]:
    if not raw_json.strip():
        return {}

    try:
        raw_configs = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError("SPEED_CAMERA_CONFIGS_JSON must be valid JSON") from exc

    if not isinstance(raw_configs, list):
        raise ValueError("SPEED_CAMERA_CONFIGS_JSON must be a JSON array")

    configs: dict[str, SpeedCameraConfig] = {}
    for raw_config in raw_configs:
        config = _build_camera_config(raw_config)
        configs[config.camera_code] = config

    return configs


def get_speed_camera_config(camera_code: str) -> SpeedCameraConfig:
    configs = load_speed_camera_configs(SPEED_CAMERA_CONFIGS_JSON)
    return configs.get(camera_code, build_default_speed_config(camera_code))


def build_speed_tracking_config() -> SpeedTrackingConfig:
    return SpeedTrackingConfig(
        max_match_distance_pixels=SPEED_TRACK_MAX_DISTANCE_PIXELS,
        track_ttl_seconds=SPEED_TRACK_TTL_SECONDS,
        min_elapsed_seconds=SPEED_MIN_ELAPSED_SECONDS,
        max_reasonable_kmh=SPEED_MAX_REASONABLE_KMH,
    )


def _build_camera_config(raw_config: Any) -> SpeedCameraConfig:
    if not isinstance(raw_config, dict):
        raise ValueError("each speed camera config must be an object")

    camera_code = str(raw_config.get("cameraCode", "")).strip()
    if not camera_code:
        raise ValueError("speed camera config cameraCode is required")

    distance_meters = float(
        raw_config.get("distanceMeters", SPEED_DEFAULT_DISTANCE_METERS)
    )
    speed_limit_kmh = float(
        raw_config.get("speedLimitKmh", SPEED_DEFAULT_LIMIT_KMH)
    )

    if distance_meters <= 0:
        raise ValueError("distanceMeters must be greater than 0")
    if speed_limit_kmh <= 0:
        raise ValueError("speedLimitKmh must be greater than 0")

    return SpeedCameraConfig(
        camera_code=camera_code,
        line_a=parse_virtual_line(raw_config.get("lineA", SPEED_DEFAULT_LINE_A)),
        line_b=parse_virtual_line(raw_config.get("lineB", SPEED_DEFAULT_LINE_B)),
        distance_meters=distance_meters,
        speed_limit_kmh=speed_limit_kmh,
        enabled=bool(raw_config.get("enabled", SPEED_DETECTION_ENABLED)),
    )
