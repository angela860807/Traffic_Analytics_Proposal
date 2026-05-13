from datetime import datetime

from app.core.config import DUPLICATE_WINDOW_SECONDS
from app.schemas.detection import DetectionResult


class DuplicateDetectionGuard:
    """
    Process-local duplicate guard for reducing repeated sends to Spring.

    This is a best-effort network-saving check only. It is reset when FastAPI
    restarts and is not shared across workers, so Spring/DB remains the source
    of truth for final duplicate handling.
    """

    def __init__(self, window_seconds: int = DUPLICATE_WINDOW_SECONDS) -> None:
        self.window_seconds = window_seconds
        self._recent_detections: dict[tuple[str, str], datetime] = {}

    def is_duplicate(self, result: DetectionResult) -> bool:
        if not result.plate_number:
            return False

        key = self._build_key(result)
        previous_detected_at = self._recent_detections.get(key)

        if previous_detected_at is None:
            return False

        elapsed_seconds = abs((result.detected_at - previous_detected_at).total_seconds())

        return elapsed_seconds <= self.window_seconds

    def remember(self, result: DetectionResult) -> None:
        if not result.plate_number:
            return

        self._recent_detections[self._build_key(result)] = result.detected_at

    def clear(self) -> None:
        self._recent_detections.clear()

    def _build_key(self, result: DetectionResult) -> tuple[str, str]:
        return (result.camera_code, result.plate_number)
