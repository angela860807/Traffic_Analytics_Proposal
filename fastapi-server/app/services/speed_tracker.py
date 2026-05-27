from dataclasses import dataclass, field
from datetime import datetime
import math
from statistics import median

from app.schemas.speed import (
    ESTIMATED_SPEED_ACCURACY_NOTE,
    HOMOGRAPHY_SPEED_ACCURACY_NOTE,
    SpeedMeasurementResult,
)
from app.services.speed_config import (
    HomographyConfig,
    Point,
    SpeedCameraConfig,
    SpeedTrackingConfig,
    SPEED_MODE_LINE_CROSSING,
    SPEED_MODE_TRACK_DELTA,
    VirtualLine,
    get_speed_camera_config,
    get_speed_tracking_config,
)

SPEED_SMOOTHING_WINDOW_SIZE = 5


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
    line_a_crossed_position: Point | None = None
    line_b_crossed_at: datetime | None = None
    line_b_crossed_position: Point | None = None
    position_history: list[tuple[datetime, Point]] = field(default_factory=list)
    speed_history_kmh: list[float] = field(default_factory=list)


class SpeedTracker:
    def __init__(
        self,
        *,
        tracking_config: SpeedTrackingConfig | None = None,
    ) -> None:
        self.tracking_config = tracking_config
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

        tracking_config = self._get_tracking_config()

        tracks = self._tracks_by_camera.setdefault(camera_code, {})
        self._expire_tracks(tracks, captured_at)

        measurements: list[SpeedMeasurementResult] = []
        matched_track_ids: set[int] = set()

        for detection in detections:
            position = self._bottom_center(detection.bbox)
            if not self._is_inside_roi(position, config.roi):
                continue

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
                if config.speed_mode == SPEED_MODE_TRACK_DELTA:
                    measurement = self._update_track_delta(
                        track=track,
                        bbox=detection.bbox,
                        position=position,
                        captured_at=captured_at,
                        camera_config=config,
                        tracking_config=tracking_config,
                    )
                    if measurement is not None:
                        measurements.append(measurement)
                    matched_track_ids.add(track.track_id)
                    continue

                measurement = self._update_track(
                    track=track,
                    bbox=detection.bbox,
                    position=position,
                    captured_at=captured_at,
                    camera_config=config,
                    tracking_config=tracking_config,
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
            position_history=[(captured_at, position)],
        )
        tracks[track.track_id] = track
        self._next_track_id += 1
        return track

    def _update_track_delta(
        self,
        *,
        track: VehicleTrackState,
        bbox: tuple[int, int, int, int],
        position: Point,
        captured_at: datetime,
        camera_config: SpeedCameraConfig,
        tracking_config: SpeedTrackingConfig,
    ) -> SpeedMeasurementResult | None:
        track.bbox = bbox
        track.position = position
        track.last_seen_at = captured_at
        track.position_history.append((captured_at, position))
        self._prune_position_history(
            track=track,
            captured_at=captured_at,
            tracking_config=tracking_config,
        )

        previous_seen_at, previous_position = track.position_history[0]
        elapsed_seconds = (captured_at - previous_seen_at).total_seconds()
        if elapsed_seconds < tracking_config.track_delta_min_elapsed_seconds:
            return None

        distance_meters, accuracy_level, accuracy_note = (
            self._calculate_point_distance_meters(
                camera_config=camera_config,
                start_position=previous_position,
                end_position=position,
            )
        )
        if distance_meters <= 0:
            return None

        raw_speed = (distance_meters / elapsed_seconds) * 3.6
        if raw_speed > tracking_config.max_reasonable_kmh:
            return None
        measured_speed = self._smooth_speed(track, raw_speed)

        return SpeedMeasurementResult(
            track_id=track.track_id,
            measured_speed=round(measured_speed, 2),
            speed_limit=camera_config.speed_limit_kmh,
            distance_meters=round(distance_meters, 3),
            elapsed_seconds=round(elapsed_seconds, 3),
            is_violation=measured_speed > camera_config.speed_limit_kmh,
            speed_mode=SPEED_MODE_TRACK_DELTA,
            accuracy_level=accuracy_level,
            accuracy_note=accuracy_note,
            measured_at=captured_at,
        )

    def _prune_position_history(
        self,
        *,
        track: VehicleTrackState,
        captured_at: datetime,
        tracking_config: SpeedTrackingConfig,
    ) -> None:
        cutoff_seconds = tracking_config.track_delta_window_seconds
        track.position_history = [
            (seen_at, position)
            for seen_at, position in track.position_history
            if (captured_at - seen_at).total_seconds() <= cutoff_seconds
        ]
        if not track.position_history:
            track.position_history = [(captured_at, track.position)]

    def _update_track(
        self,
        *,
        track: VehicleTrackState,
        bbox: tuple[int, int, int, int],
        position: Point,
        captured_at: datetime,
        camera_config: SpeedCameraConfig,
        tracking_config: SpeedTrackingConfig,
    ) -> SpeedMeasurementResult | None:
        previous_position = track.position
        previous_seen_at = track.last_seen_at

        if (
            track.line_a_crossed_at is None
            and self._is_between_lines(
                previous_position,
                camera_config.line_a,
                camera_config.line_b,
            )
            and self._is_moving_toward_line(
                previous_position,
                position,
                camera_config.line_b,
            )
        ):
            track.line_a_crossed_at = self._estimate_previous_crossed_at(
                previous_position=previous_position,
                current_position=position,
                previous_seen_at=previous_seen_at,
                captured_at=captured_at,
                line=camera_config.line_a,
            )
            track.line_a_crossed_position = self._estimate_previous_crossed_position(
                previous_position=previous_position,
                current_position=position,
                line=camera_config.line_a,
            )

        if (
            track.line_a_crossed_at is None
            and self._crossed_line(previous_position, position, camera_config.line_a)
        ):
            track.line_a_crossed_at = self._estimate_crossed_at(
                previous_position=previous_position,
                current_position=position,
                previous_seen_at=previous_seen_at,
                captured_at=captured_at,
                line=camera_config.line_a,
            )
            track.line_a_crossed_position = self._estimate_crossed_position(
                previous_position=previous_position,
                current_position=position,
                line=camera_config.line_a,
            )

        if (
            track.line_a_crossed_at is not None
            and track.line_b_crossed_at is None
            and self._crossed_line(previous_position, position, camera_config.line_b)
        ):
            track.line_b_crossed_at = self._estimate_crossed_at(
                previous_position=previous_position,
                current_position=position,
                previous_seen_at=previous_seen_at,
                captured_at=captured_at,
                line=camera_config.line_b,
            )
            track.line_b_crossed_position = self._estimate_crossed_position(
                previous_position=previous_position,
                current_position=position,
                line=camera_config.line_b,
            )

        track.bbox = bbox
        track.position = position
        track.last_seen_at = captured_at

        if track.line_a_crossed_at is None or track.line_b_crossed_at is None:
            return None

        elapsed_seconds = (
            track.line_b_crossed_at - track.line_a_crossed_at
        ).total_seconds()
        if elapsed_seconds < tracking_config.min_elapsed_seconds:
            return None

        distance_meters, accuracy_level, accuracy_note = self._calculate_distance_meters(
            camera_config=camera_config,
            track=track,
        )
        raw_speed = (distance_meters / elapsed_seconds) * 3.6
        if raw_speed > tracking_config.max_reasonable_kmh:
            return None
        measured_speed = self._smooth_speed(track, raw_speed)

        # Prevent duplicate speed events for the same track after a valid measurement.
        track.line_a_crossed_at = None
        track.line_a_crossed_position = None
        track.line_b_crossed_at = None
        track.line_b_crossed_position = None

        return SpeedMeasurementResult(
            track_id=track.track_id,
            measured_speed=round(measured_speed, 2),
            speed_limit=camera_config.speed_limit_kmh,
            distance_meters=round(distance_meters, 3),
            elapsed_seconds=round(elapsed_seconds, 3),
            is_violation=measured_speed > camera_config.speed_limit_kmh,
            speed_mode=SPEED_MODE_LINE_CROSSING,
            accuracy_level=accuracy_level,
            accuracy_note=accuracy_note,
            measured_at=captured_at,
        )

    def _match_track(
        self,
        *,
        tracks: dict[int, VehicleTrackState],
        position: Point,
        matched_track_ids: set[int],
    ) -> VehicleTrackState | None:
        tracking_config = self._get_tracking_config()
        best_track: VehicleTrackState | None = None
        best_distance = tracking_config.max_match_distance_pixels

        for track in tracks.values():
            if track.track_id in matched_track_ids:
                continue

            distance = self._distance(position, track.position)
            if distance <= best_distance:
                best_track = track
                best_distance = distance

        return best_track

    def _smooth_speed(self, track: VehicleTrackState, speed_kmh: float) -> float:
        track.speed_history_kmh.append(speed_kmh)
        if len(track.speed_history_kmh) > SPEED_SMOOTHING_WINDOW_SIZE:
            track.speed_history_kmh = track.speed_history_kmh[
                -SPEED_SMOOTHING_WINDOW_SIZE:
            ]

        return float(median(track.speed_history_kmh))

    def _expire_tracks(
        self,
        tracks: dict[int, VehicleTrackState],
        captured_at: datetime,
    ) -> None:
        tracking_config = self._get_tracking_config()
        expired_track_ids = [
            track_id
            for track_id, track in tracks.items()
            if (captured_at - track.last_seen_at).total_seconds()
            > tracking_config.track_ttl_seconds
        ]

        for track_id in expired_track_ids:
            del tracks[track_id]

    def _crossed_line(self, previous: Point, current: Point, line: VirtualLine) -> bool:
        previous_side = self._point_side(previous, line)
        current_side = self._point_side(current, line)
        return previous_side == 0 or current_side == 0 or previous_side != current_side

    def _estimate_crossed_at(
        self,
        *,
        previous_position: Point,
        current_position: Point,
        previous_seen_at: datetime,
        captured_at: datetime,
        line: VirtualLine,
    ) -> datetime:
        fraction = self._estimate_crossing_fraction(
            previous_position=previous_position,
            current_position=current_position,
            line=line,
        )
        return previous_seen_at + (captured_at - previous_seen_at) * fraction

    def _estimate_crossed_position(
        self,
        *,
        previous_position: Point,
        current_position: Point,
        line: VirtualLine,
    ) -> Point:
        fraction = self._estimate_crossing_fraction(
            previous_position=previous_position,
            current_position=current_position,
            line=line,
        )
        return self._interpolate_point(
            previous_position=previous_position,
            current_position=current_position,
            fraction=fraction,
        )

    def _estimate_crossing_fraction(
        self,
        *,
        previous_position: Point,
        current_position: Point,
        line: VirtualLine,
    ) -> float:
        previous_value = self._signed_line_value(previous_position, line)
        current_value = self._signed_line_value(current_position, line)

        if previous_value == current_value:
            fraction = 1.0
        elif previous_value == 0:
            fraction = 0.0
        elif current_value == 0:
            fraction = 1.0
        else:
            fraction = abs(previous_value) / (
                abs(previous_value) + abs(current_value)
            )

        return max(0.0, min(1.0, fraction))

    def _estimate_previous_crossed_at(
        self,
        *,
        previous_position: Point,
        current_position: Point,
        previous_seen_at: datetime,
        captured_at: datetime,
        line: VirtualLine,
    ) -> datetime:
        previous_value = abs(self._signed_line_value(previous_position, line))
        current_value = abs(self._signed_line_value(current_position, line))
        movement_value = abs(current_value - previous_value)

        if movement_value == 0:
            return previous_seen_at

        frame_delta = captured_at - previous_seen_at
        return previous_seen_at - frame_delta * (previous_value / movement_value)

    def _estimate_previous_crossed_position(
        self,
        *,
        previous_position: Point,
        current_position: Point,
        line: VirtualLine,
    ) -> Point:
        previous_value = abs(self._signed_line_value(previous_position, line))
        current_value = abs(self._signed_line_value(current_position, line))
        movement_value = abs(current_value - previous_value)

        if movement_value == 0:
            return previous_position

        fraction = -(previous_value / movement_value)
        return self._interpolate_point(
            previous_position=previous_position,
            current_position=current_position,
            fraction=fraction,
        )

    def _interpolate_point(
        self,
        *,
        previous_position: Point,
        current_position: Point,
        fraction: float,
    ) -> Point:
        return Point(
            x=round(
                previous_position.x
                + (current_position.x - previous_position.x) * fraction
            ),
            y=round(
                previous_position.y
                + (current_position.y - previous_position.y) * fraction
            ),
        )

    def _calculate_distance_meters(
        self,
        *,
        camera_config: SpeedCameraConfig,
        track: VehicleTrackState,
    ) -> tuple[float, str, str]:
        if (
            camera_config.homography is not None
            and track.line_a_crossed_position is not None
            and track.line_b_crossed_position is not None
        ):
            world_a = self._project_to_world(
                track.line_a_crossed_position,
                camera_config.homography,
            )
            world_b = self._project_to_world(
                track.line_b_crossed_position,
                camera_config.homography,
            )
            if world_a is not None and world_b is not None:
                return (
                    self._distance_between_world_points(world_a, world_b),
                    "HOMOGRAPHY_ESTIMATED",
                    HOMOGRAPHY_SPEED_ACCURACY_NOTE,
                )

        return (
            camera_config.distance_meters,
            "ESTIMATED",
            ESTIMATED_SPEED_ACCURACY_NOTE,
        )

    def _calculate_point_distance_meters(
        self,
        *,
        camera_config: SpeedCameraConfig,
        start_position: Point,
        end_position: Point,
    ) -> tuple[float, str, str]:
        if camera_config.homography is not None:
            world_start = self._project_to_world(
                start_position,
                camera_config.homography,
            )
            world_end = self._project_to_world(
                end_position,
                camera_config.homography,
            )
            if world_start is not None and world_end is not None:
                return (
                    self._distance_between_world_points(world_start, world_end),
                    "HOMOGRAPHY_ESTIMATED",
                    HOMOGRAPHY_SPEED_ACCURACY_NOTE,
                )

        return (
            self._distance(start_position, end_position),
            "ESTIMATED",
            ESTIMATED_SPEED_ACCURACY_NOTE,
        )

    def _project_to_world(
        self,
        point: Point,
        homography: HomographyConfig,
    ) -> tuple[float, float] | None:
        matrix = homography.matrix
        denominator = matrix[2][0] * point.x + matrix[2][1] * point.y + matrix[2][2]
        if abs(denominator) < 1e-9:
            return None

        world_x = (
            matrix[0][0] * point.x + matrix[0][1] * point.y + matrix[0][2]
        ) / denominator
        world_y = (
            matrix[1][0] * point.x + matrix[1][1] * point.y + matrix[1][2]
        ) / denominator
        return (world_x, world_y)

    def _distance_between_world_points(
        self,
        first: tuple[float, float],
        second: tuple[float, float],
    ) -> float:
        return math.hypot(first[0] - second[0], first[1] - second[1])

    def _is_inside_roi(
        self,
        point: Point,
        roi: tuple[Point, ...] | None,
    ) -> bool:
        if roi is None:
            return True

        inside = False
        previous = roi[-1]
        for current in roi:
            if self._is_point_on_segment(point, previous, current):
                return True

            crosses_y = (current.y > point.y) != (previous.y > point.y)
            if crosses_y:
                intersection_x = (
                    (previous.x - current.x)
                    * (point.y - current.y)
                    / (previous.y - current.y)
                    + current.x
                )
                if point.x < intersection_x:
                    inside = not inside

            previous = current

        return inside

    def _is_point_on_segment(self, point: Point, start: Point, end: Point) -> bool:
        cross_product = (
            (point.y - start.y) * (end.x - start.x)
            - (point.x - start.x) * (end.y - start.y)
        )
        if cross_product != 0:
            return False

        return (
            min(start.x, end.x) <= point.x <= max(start.x, end.x)
            and min(start.y, end.y) <= point.y <= max(start.y, end.y)
        )

    def _is_between_lines(
        self,
        point: Point,
        first_line: VirtualLine,
        second_line: VirtualLine,
    ) -> bool:
        first_value = self._signed_line_value(point, first_line)
        second_value = self._signed_line_value(point, second_line)
        return first_value == 0 or second_value == 0 or first_value * second_value < 0

    def _is_moving_toward_line(
        self,
        previous_position: Point,
        current_position: Point,
        line: VirtualLine,
    ) -> bool:
        previous_distance = abs(self._signed_line_value(previous_position, line))
        current_distance = abs(self._signed_line_value(current_position, line))
        return current_distance < previous_distance

    def _point_side(self, point: Point, line: VirtualLine) -> int:
        value = self._signed_line_value(point, line)

        if value == 0:
            return 0
        return 1 if value > 0 else -1

    def _signed_line_value(self, point: Point, line: VirtualLine) -> int:
        return (
            (line.end.x - line.start.x) * (point.y - line.start.y)
            - (line.end.y - line.start.y) * (point.x - line.start.x)
        )

    def _bottom_center(self, bbox: tuple[int, int, int, int]) -> Point:
        x1, _, x2, y2 = bbox
        return Point(x=round((x1 + x2) / 2), y=y2)

    def _distance(self, first: Point, second: Point) -> float:
        return math.hypot(first.x - second.x, first.y - second.y)

    def _get_tracking_config(self) -> SpeedTrackingConfig:
        if self.tracking_config is None:
            self.tracking_config = get_speed_tracking_config()
        return self.tracking_config
