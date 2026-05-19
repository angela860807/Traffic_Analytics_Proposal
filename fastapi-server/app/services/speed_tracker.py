from dataclasses import dataclass
from datetime import datetime
import math

from app.schemas.speed import SpeedMeasurementResult
from app.services.speed_config import (
    Point,
    SpeedCameraConfig,
    SpeedTrackingConfig,
    VirtualLine,
    build_speed_tracking_config,
    get_speed_camera_config,
)


@dataclass(frozen=True)
class VehicleTrackInput:
    bbox: tuple[int, int, int, int]
    confidence_score: float


@dataclass
class VehicleTrackState:
    track_id: int
    bbox: tuple[int, int, int, int]
    position: Point
    last_seen_at: datetime
    line_a_crossed_at: datetime | None = None
    line_b_crossed_at: datetime | None = None


class SpeedTracker:
    def __init__(
        self,
        *,
        tracking_config: SpeedTrackingConfig | None = None,
    ) -> None:
        self.tracking_config = tracking_config or build_speed_tracking_config()
        self._tracks_by_camera: dict[str, dict[int, VehicleTrackState]] = {}
        self._next_track_id = 1

    def process_detections(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        detections: list[VehicleTrackInput],
        camera_config: SpeedCameraConfig | None = None,
    ) -> list[SpeedMeasurementResult]:
        config = camera_config or get_speed_camera_config(camera_code)
        if not config.enabled:
            return []

        tracks = self._tracks_by_camera.setdefault(camera_code, {})
        self._expire_tracks(tracks, captured_at)

        measurements: list[SpeedMeasurementResult] = []
        matched_track_ids: set[int] = set()

        for detection in detections:
            position = self._bottom_center(detection.bbox)
            track = self._match_track(
                tracks=tracks,
                position=position,
                matched_track_ids=matched_track_ids,
            )

            if track is None:
                track = self._create_track(
                    tracks=tracks,
                    bbox=detection.bbox,
                    position=position,
                    captured_at=captured_at,
                )
            else:
                measurement = self._update_track(
                    track=track,
                    bbox=detection.bbox,
                    position=position,
                    captured_at=captured_at,
                    camera_config=config,
                )
                if measurement is not None:
                    measurements.append(measurement)

            matched_track_ids.add(track.track_id)

        return measurements

    def clear(self) -> None:
        self._tracks_by_camera.clear()
        self._next_track_id = 1

    def _create_track(
        self,
        *,
        tracks: dict[int, VehicleTrackState],
        bbox: tuple[int, int, int, int],
        position: Point,
        captured_at: datetime,
    ) -> VehicleTrackState:
        track = VehicleTrackState(
            track_id=self._next_track_id,
            bbox=bbox,
            position=position,
            last_seen_at=captured_at,
        )
        tracks[track.track_id] = track
        self._next_track_id += 1
        return track

    def _update_track(
        self,
        *,
        track: VehicleTrackState,
        bbox: tuple[int, int, int, int],
        position: Point,
        captured_at: datetime,
        camera_config: SpeedCameraConfig,
    ) -> SpeedMeasurementResult | None:
        previous_position = track.position

        if (
            track.line_a_crossed_at is None
            and self._crossed_line(previous_position, position, camera_config.line_a)
        ):
            track.line_a_crossed_at = captured_at

        if (
            track.line_a_crossed_at is not None
            and track.line_b_crossed_at is None
            and self._crossed_line(previous_position, position, camera_config.line_b)
        ):
            track.line_b_crossed_at = captured_at

        track.bbox = bbox
        track.position = position
        track.last_seen_at = captured_at

        if track.line_a_crossed_at is None or track.line_b_crossed_at is None:
            return None

        elapsed_seconds = (
            track.line_b_crossed_at - track.line_a_crossed_at
        ).total_seconds()
        if elapsed_seconds < self.tracking_config.min_elapsed_seconds:
            return None

        measured_speed = (camera_config.distance_meters / elapsed_seconds) * 3.6
        if measured_speed > self.tracking_config.max_reasonable_kmh:
            return None

        # Prevent duplicate speed events for the same track after a valid measurement.
        track.line_a_crossed_at = None
        track.line_b_crossed_at = None

        return SpeedMeasurementResult(
            track_id=track.track_id,
            measured_speed=round(measured_speed, 2),
            speed_limit=camera_config.speed_limit_kmh,
            distance_meters=camera_config.distance_meters,
            elapsed_seconds=round(elapsed_seconds, 3),
            is_violation=measured_speed > camera_config.speed_limit_kmh,
            measured_at=captured_at,
        )

    def _match_track(
        self,
        *,
        tracks: dict[int, VehicleTrackState],
        position: Point,
        matched_track_ids: set[int],
    ) -> VehicleTrackState | None:
        best_track: VehicleTrackState | None = None
        best_distance = self.tracking_config.max_match_distance_pixels

        for track in tracks.values():
            if track.track_id in matched_track_ids:
                continue

            distance = self._distance(position, track.position)
            if distance <= best_distance:
                best_track = track
                best_distance = distance

        return best_track

    def _expire_tracks(
        self,
        tracks: dict[int, VehicleTrackState],
        captured_at: datetime,
    ) -> None:
        expired_track_ids = [
            track_id
            for track_id, track in tracks.items()
            if (captured_at - track.last_seen_at).total_seconds()
            > self.tracking_config.track_ttl_seconds
        ]

        for track_id in expired_track_ids:
            del tracks[track_id]

    def _crossed_line(self, previous: Point, current: Point, line: VirtualLine) -> bool:
        previous_side = self._point_side(previous, line)
        current_side = self._point_side(current, line)
        return previous_side == 0 or current_side == 0 or previous_side != current_side

    def _point_side(self, point: Point, line: VirtualLine) -> int:
        value = (
            (line.end.x - line.start.x) * (point.y - line.start.y)
            - (line.end.y - line.start.y) * (point.x - line.start.x)
        )

        if value == 0:
            return 0
        return 1 if value > 0 else -1

    def _bottom_center(self, bbox: tuple[int, int, int, int]) -> Point:
        x1, _, x2, y2 = bbox
        return Point(x=round((x1 + x2) / 2), y=y2)

    def _distance(self, first: Point, second: Point) -> float:
        return math.hypot(first.x - second.x, first.y - second.y)
