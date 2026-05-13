from dataclasses import dataclass

import numpy as np

from app.core.config import (
    MODEL_PATH,
    YOLO_CONF_THRESHOLD,
    YOLO_IOU_THRESHOLD,
    YOLO_MAX_DET,
)


@dataclass
class PlateDetection:
    detection_type: str
    confidence_score: float
    bbox: tuple[int, int, int, int] | None = None


class PlateDetector:
    def __init__(self) -> None:
        self._model = None

    def detect(self, image: np.ndarray) -> PlateDetection:
        if not MODEL_PATH:
            return PlateDetection(
                detection_type="PLATE",
                confidence_score=0.9321,
                bbox=None,
            )

        model = self._load_model()

        results = model(
            image,
            conf=YOLO_CONF_THRESHOLD,
            iou=YOLO_IOU_THRESHOLD,
            max_det=YOLO_MAX_DET,
        )

        best_detection: PlateDetection | None = None

        for result in results:
            boxes = sorted(
                result.boxes,
                key=lambda box: float(box.conf[0]),
                reverse=True,
            )

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence_score = float(box.conf[0])

                best_detection = PlateDetection(
                    detection_type="PLATE",
                    confidence_score=confidence_score,
                    bbox=(x1, y1, x2, y2),
                )
                break

        if best_detection is None:
            return PlateDetection(
                detection_type="VEHICLE",
                confidence_score=0.0,
                bbox=None,
            )

        return best_detection

    def _load_model(self):
        if self._model is None:
            from ultralytics import YOLO

            self._model = YOLO(MODEL_PATH)

        return self._model
