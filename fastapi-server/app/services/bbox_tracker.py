from dataclasses import dataclass
from datetime import datetime
from math import hypot

from app.core.config import (
    STREAM_TRACK_MAX_CENTER_DISTANCE_PIXELS,
    STREAM_TRACK_MIN_IOU,
    STREAM_TRACK_TTL_SECONDS,
)
from app.services.vehicle_detector import VehicleDetectionBox


@dataclass
class TrackedBbox:
    track_id: int
    bbox: tuple[int, int, int, int]
    confidence_score: float


@dataclass
class _TrackState:
    track_id: int
    bbox: tuple[int, int, int, int]
    confidence_score: float
    last_seen_at: datetime


class BboxTracker:
    def __init__(
        self,
        *,
        ttl_seconds: float = STREAM_TRACK_TTL_SECONDS,
        min_iou: float = STREAM_TRACK_MIN_IOU,
        max_center_distance_pixels: float = STREAM_TRACK_MAX_CENTER_DISTANCE_PIXELS,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.min_iou = min_iou
        self.max_center_distance_pixels = max_center_distance_pixels
        self._tracks_by_camera: dict[str, dict[int, _TrackState]] = {}
        self._next_track_id = 1

    def update(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        boxes: list[VehicleDetectionBox],
    ) -> list[TrackedBbox]:
        tracks = self._tracks_by_camera.setdefault(camera_code, {})
        self._expire_tracks(tracks, captured_at)

        tracked: list[TrackedBbox] = []
        matched_track_ids: set[int] = set()

        for box in sorted(boxes, key=lambda item: item.confidence_score, reverse=True):
            track = self._match_track(
                tracks=tracks,
                bbox=box.bbox,
                matched_track_ids=matched_track_ids,
            )
            if track is None:
                track = self._create_track(
                    tracks=tracks,
                    bbox=box.bbox,
                    confidence_score=box.confidence_score,
                    captured_at=captured_at,
                )
            else:
                track.bbox = box.bbox
                track.confidence_score = box.confidence_score
                track.last_seen_at = captured_at

            matched_track_ids.add(track.track_id)
            tracked.append(
                TrackedBbox(
                    track_id=track.track_id,
                    bbox=track.bbox,
                    confidence_score=track.confidence_score,
                )
            )

        return sorted(tracked, key=lambda item: item.confidence_score, reverse=True)

    def clear(self) -> None:
        self._tracks_by_camera.clear()
        self._next_track_id = 1

    def _create_track(
        self,
        *,
        tracks: dict[int, _TrackState],
        bbox: tuple[int, int, int, int],
        confidence_score: float,
        captured_at: datetime,
    ) -> _TrackState:
        track = _TrackState(
            track_id=self._next_track_id,
            bbox=bbox,
            confidence_score=confidence_score,
            last_seen_at=captured_at,
        )
        tracks[track.track_id] = track
        self._next_track_id += 1
        return track

    def _match_track(
        self,
        *,
        tracks: dict[int, _TrackState],
        bbox: tuple[int, int, int, int],
        matched_track_ids: set[int],
    ) -> _TrackState | None:
        best_track = None
        best_score = -1.0

        for track in tracks.values():
            if track.track_id in matched_track_ids:
                continue

            iou = self._iou(track.bbox, bbox)
            distance = self._center_distance(track.bbox, bbox)
            if iou < self.min_iou and distance > self.max_center_distance_pixels:
                continue

            distance_score = max(
                0.0,
                1.0 - (distance / max(self.max_center_distance_pixels, 1.0)),
            )
            score = (iou * 0.7) + (distance_score * 0.3)
            if score > best_score:
                best_track = track
                best_score = score

        return best_track

    def _expire_tracks(
        self,
        tracks: dict[int, _TrackState],
        captured_at: datetime,
    ) -> None:
        expired_ids = [
            track_id
            for track_id, track in tracks.items()
            if (captured_at - track.last_seen_at).total_seconds() > self.ttl_seconds
        ]
        for track_id in expired_ids:
            del tracks[track_id]

    def _center_distance(
        self,
        a: tuple[int, int, int, int],
        b: tuple[int, int, int, int],
    ) -> float:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        acx = ax1 + ((ax2 - ax1) / 2)
        acy = ay1 + ((ay2 - ay1) / 2)
        bcx = bx1 + ((bx2 - bx1) / 2)
        bcy = by1 + ((by2 - by1) / 2)
        return float(hypot(acx - bcx, acy - bcy))

    def _iou(
        self,
        a: tuple[int, int, int, int],
        b: tuple[int, int, int, int],
    ) -> float:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b

        inter_x1 = max(ax1, bx1)
        inter_y1 = max(ay1, by1)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)
        inter_w = max(0, inter_x2 - inter_x1)
        inter_h = max(0, inter_y2 - inter_y1)
        inter_area = inter_w * inter_h

        area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
        area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
        union_area = area_a + area_b - inter_area

        if union_area <= 0:
            return 0.0

        return inter_area / union_area
