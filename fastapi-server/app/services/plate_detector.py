from dataclasses import dataclass

import numpy as np


@dataclass
class PlateDetection:
    detection_type: str
    confidence_score: float
    bbox: tuple[int, int, int, int] | None = None


class PlateDetector:
    def detect(self, image: np.ndarray) -> PlateDetection:
        # TODO:
            # 1. Load YOLO model from MODEL_PATH.
            # 2. Detect vehicle or license plate regions from image.
            # 3. Return the highest-confidence plate detection first.
            # 4. Keep bbox coordinates for future crop-image storage.

        return PlateDetection(
            detection_type="PLATE",
            confidence_score=0.9321,
            bbox=None,
        )
