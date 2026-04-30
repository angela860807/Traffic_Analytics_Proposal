from dataclasses import dataclass

import numpy as np


@dataclass
class PlateDetection:
    detection_type: str
    confidence_score: float
    bbox: tuple[int, int, int, int] | None = None


class PlateDetector:
    def detect(self, image: np.ndarray) -> PlateDetection:
        # TODO: replace with YOLO model inference.
        return PlateDetection(
            detection_type="PLATE",
            confidence_score=0.9321,
            bbox=None,
        )
