from dataclasses import dataclass
import json
from typing import Any

import cv2
import numpy as np

from app.core.config import (
    SPEED_CAMERA_CONFIGS_JSON,
    SPEED_DEFAULT_DISTANCE_METERS,
    SPEED_DEFAULT_LIMIT_KMH,
    SPEED_DEFAULT_LINE_A,
    SPEED_DEFAULT_LINE_B,
    SPEED_DEFAULT_MODE,
    SPEED_DETECTION_ENABLED,
    SPEED_MAX_REASONABLE_KMH,
    SPEED_MIN_ELAPSED_SECONDS,
    SPEED_TRACK_DELTA_MIN_ELAPSED_SECONDS,
    SPEED_TRACK_DELTA_WINDOW_SECONDS,
    SPEED_TRACK_MAX_DISTANCE_PIXELS,
    SPEED_TRACK_TTL_SECONDS,
)

SPEED_MODE_LINE_CROSSING = "LINE_CROSSING"
SPEED_MODE_TRACK_DELTA = "TRACK_DELTA"
SUPPORTED_SPEED_MODES = {SPEED_MODE_LINE_CROSSING, SPEED_MODE_TRACK_DELTA}


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class MetricPoint:
    x: float
    y: float


@dataclass(frozen=True)
class VirtualLine:
    start: Point
    end: Point


@dataclass(frozen=True)
class HomographyConfig:
    image_points: tuple[MetricPoint, ...]
    world_points_meters: tuple[MetricPoint, ...]
    matrix: tuple[tuple[float, float, float], ...]


@dataclass(frozen=True)
class SpeedCameraConfig:
    camera_code: str
    line_a: VirtualLine
    line_b: VirtualLine
    distance_meters: float
    speed_limit_kmh: float
    speed_mode: str = SPEED_MODE_TRACK_DELTA
    enabled: bool = True
    roi: tuple[Point, ...] | None = None
    homography: HomographyConfig | None = None


@dataclass(frozen=True)
class SpeedTrackingConfig:
    max_match_distance_pixels: float
    track_ttl_seconds: float
    min_elapsed_seconds: float
    max_reasonable_kmh: float
    track_delta_window_seconds: float = 1.0
    track_delta_min_elapsed_seconds: float = 0.3


_speed_camera_configs_cache: dict[str, SpeedCameraConfig] | None = None
_speed_tracking_config_cache: SpeedTrackingConfig | None = None


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
        speed_mode=_parse_speed_mode(SPEED_DEFAULT_MODE),
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
    if _speed_camera_configs_cache is None:
        validate_speed_settings()

    configs = _speed_camera_configs_cache or {}
    return configs.get(camera_code, build_default_speed_config(camera_code))


def get_speed_tracking_config() -> SpeedTrackingConfig:
    if _speed_tracking_config_cache is None:
        validate_speed_settings()

    if _speed_tracking_config_cache is None:
        raise RuntimeError("speed tracking config cache was not initialized")

    return _speed_tracking_config_cache


def build_speed_tracking_config() -> SpeedTrackingConfig:
    config = SpeedTrackingConfig(
        max_match_distance_pixels=SPEED_TRACK_MAX_DISTANCE_PIXELS,
        track_ttl_seconds=SPEED_TRACK_TTL_SECONDS,
        min_elapsed_seconds=SPEED_MIN_ELAPSED_SECONDS,
        max_reasonable_kmh=SPEED_MAX_REASONABLE_KMH,
        track_delta_window_seconds=SPEED_TRACK_DELTA_WINDOW_SECONDS,
        track_delta_min_elapsed_seconds=SPEED_TRACK_DELTA_MIN_ELAPSED_SECONDS,
    )
    _validate_tracking_config(config)
    return config


def validate_speed_settings() -> None:
    default_config = build_default_speed_config("__validation__")
    _validate_camera_config(default_config)
    camera_configs = load_speed_camera_configs(SPEED_CAMERA_CONFIGS_JSON)
    tracking_config = build_speed_tracking_config()

    global _speed_camera_configs_cache, _speed_tracking_config_cache
    _speed_camera_configs_cache = camera_configs
    _speed_tracking_config_cache = tracking_config


def reset_speed_settings_cache() -> None:
    global _speed_camera_configs_cache, _speed_tracking_config_cache
    _speed_camera_configs_cache = None
    _speed_tracking_config_cache = None


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

    config = SpeedCameraConfig(
        camera_code=camera_code,
        line_a=parse_virtual_line(raw_config.get("lineA", SPEED_DEFAULT_LINE_A)),
        line_b=parse_virtual_line(raw_config.get("lineB", SPEED_DEFAULT_LINE_B)),
        distance_meters=distance_meters,
        speed_limit_kmh=speed_limit_kmh,
        speed_mode=_parse_speed_mode(raw_config.get("speedMode", SPEED_DEFAULT_MODE)),
        enabled=_parse_bool(raw_config.get("enabled", SPEED_DETECTION_ENABLED)),
        roi=_parse_roi(raw_config.get("roi")),
        homography=_build_homography_config(raw_config.get("homography")),
    )
    _validate_camera_config(config)
    return config


def _parse_roi(raw_roi: Any) -> tuple[Point, ...] | None:
    if raw_roi is None:
        return None
    if not isinstance(raw_roi, list):
        raise ValueError("roi must be a JSON array")
    if len(raw_roi) < 3:
        raise ValueError("roi must contain at least three points")

    points: list[Point] = []
    for raw_point in raw_roi:
        if not isinstance(raw_point, list | tuple) or len(raw_point) != 2:
            raise ValueError("roi entries must contain two integers")
        try:
            point = Point(x=int(raw_point[0]), y=int(raw_point[1]))
        except (TypeError, ValueError) as exc:
            raise ValueError("roi entries must contain two integers") from exc
        points.append(point)

    if len(set(points)) < 3:
        raise ValueError("roi must contain at least three distinct points")

    return tuple(points)


def _build_homography_config(raw_homography: Any) -> HomographyConfig | None:
    if raw_homography is None:
        return None
    if not isinstance(raw_homography, dict):
        raise ValueError("homography must be an object")

    image_points = _parse_metric_points(
        raw_homography.get("imagePoints"),
        field_name="homography.imagePoints",
    )
    world_points = _parse_metric_points(
        raw_homography.get("worldPointsMeters"),
        field_name="homography.worldPointsMeters",
    )

    if len(image_points) != len(world_points):
        raise ValueError(
            "homography.imagePoints and homography.worldPointsMeters must have "
            "the same length"
        )
    if len(image_points) < 4:
        raise ValueError("homography requires at least four point pairs")

    image_array = np.array(
        [[point.x, point.y] for point in image_points],
        dtype=np.float32,
    )
    world_array = np.array(
        [[point.x, point.y] for point in world_points],
        dtype=np.float32,
    )
    matrix, _ = cv2.findHomography(image_array, world_array, method=0)

    if matrix is None:
        raise ValueError("homography matrix could not be computed")

    return HomographyConfig(
        image_points=image_points,
        world_points_meters=world_points,
        matrix=tuple(tuple(float(value) for value in row) for row in matrix),
    )


def _parse_metric_points(raw_points: Any, *, field_name: str) -> tuple[MetricPoint, ...]:
    if not isinstance(raw_points, list):
        raise ValueError(f"{field_name} must be a JSON array")

    points: list[MetricPoint] = []
    for raw_point in raw_points:
        if not isinstance(raw_point, list | tuple) or len(raw_point) != 2:
            raise ValueError(f"{field_name} entries must contain two numbers")
        try:
            point = MetricPoint(x=float(raw_point[0]), y=float(raw_point[1]))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} entries must contain two numbers") from exc
        points.append(point)

    return tuple(points)


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False

    raise ValueError("enabled must be a boolean")


def _parse_speed_mode(value: Any) -> str:
    mode = str(value).strip().upper()
    if mode not in SUPPORTED_SPEED_MODES:
        supported = ", ".join(sorted(SUPPORTED_SPEED_MODES))
        raise ValueError(f"speedMode must be one of: {supported}")
    return mode


def _validate_camera_config(config: SpeedCameraConfig) -> None:
    if config.distance_meters <= 0:
        raise ValueError("distanceMeters must be greater than 0")
    if config.speed_limit_kmh <= 0:
        raise ValueError("speedLimitKmh must be greater than 0")
    if config.line_a == config.line_b:
        raise ValueError("lineA and lineB must differ")
    if config.speed_mode not in SUPPORTED_SPEED_MODES:
        raise ValueError("speedMode is invalid")


def _validate_tracking_config(config: SpeedTrackingConfig) -> None:
    if config.max_match_distance_pixels <= 0:
        raise ValueError("SPEED_TRACK_MAX_DISTANCE_PIXELS must be greater than 0")
    if config.track_ttl_seconds <= 0:
        raise ValueError("SPEED_TRACK_TTL_SECONDS must be greater than 0")
    if config.min_elapsed_seconds <= 0:
        raise ValueError("SPEED_MIN_ELAPSED_SECONDS must be greater than 0")
    if config.max_reasonable_kmh <= 0:
        raise ValueError("SPEED_MAX_REASONABLE_KMH must be greater than 0")
    if config.track_delta_window_seconds <= 0:
        raise ValueError("SPEED_TRACK_DELTA_WINDOW_SECONDS must be greater than 0")
    if config.track_delta_min_elapsed_seconds <= 0:
        raise ValueError("SPEED_TRACK_DELTA_MIN_ELAPSED_SECONDS must be greater than 0")
