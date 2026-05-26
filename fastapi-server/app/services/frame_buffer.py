from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from threading import Lock

from app.core.config import PRE_BUFFER_SECONDS, STREAM_FPS

@dataclass
class LatestFrame:
    camera_code: str
    captured_at: datetime
    content_type: str
    image_bytes: bytes
    frame_number: int | None = None


@dataclass
class BufferedFrame(LatestFrame):
    bbox: tuple[int, int, int, int] | None = None
    bboxes: list[tuple[int, int, int, int]] | None = None
    track_id: int | None = None
    high_res_crop_bytes: bytes | None = None
    high_res_crop_content_type: str | None = None
    confidence_score: float = 0.0
    candidate_score: float = 0.0
    blur_score: float = 0.0
    frame_width: int | None = None
    frame_height: int | None = None


class FrameBuffer:
    def __init__(self, max_frames_per_camera: int | None = None) -> None:
        self._lock = Lock()
        self._latest_frame: LatestFrame | None = None
        self._max_frames_per_camera = max_frames_per_camera or max(
            1,
            int(PRE_BUFFER_SECONDS * STREAM_FPS),
        )
        self._frames_by_camera: dict[str, deque[BufferedFrame]] = defaultdict(
            lambda: deque(maxlen=self._max_frames_per_camera),
        )

    def set_frame(self, frame: LatestFrame) -> None:
        with self._lock:
            self._latest_frame = frame
            self._add_frame_locked(
                BufferedFrame(
                    camera_code=frame.camera_code,
                    captured_at=frame.captured_at,
                    content_type=frame.content_type,
                    image_bytes=frame.image_bytes,
                )
            )

    def add_frame(self, frame: BufferedFrame) -> None:
        with self._lock:
            self._latest_frame = frame
            self._add_frame_locked(frame)

    def get_frame(self) -> LatestFrame | None:
        with self._lock:
            return self._latest_frame

    def get_recent_frames(self, camera_code: str) -> list[BufferedFrame]:
        with self._lock:
            return list(self._frames_by_camera[camera_code])

    def clear(self) -> None:
        with self._lock:
            self._latest_frame = None
            self._frames_by_camera.clear()

    def _add_frame_locked(self, frame: BufferedFrame) -> None:
        self._frames_by_camera[frame.camera_code].append(frame)


frame_buffer = FrameBuffer()
