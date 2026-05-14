from dataclasses import dataclass, field

import numpy as np

from app.core.config import (
    MODEL_PATH,
    YOLO_CONF_THRESHOLD,
    YOLO_IOU_THRESHOLD,
    YOLO_MAX_DET,
)


@dataclass
class PlateDetectionBox:
    bbox: tuple[int, int, int, int]
    confidence_score: float


@dataclass
class PlateDetection:
    detection_type: str
    confidence_score: float
    bbox: tuple[int, int, int, int] | None = None
    boxes: list[PlateDetectionBox] = field(default_factory=list)


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

        detections: list[PlateDetectionBox] = []

        for result in results:
            boxes = sorted(
                result.boxes,
                key=lambda box: float(box.conf[0]),
                reverse=True,
            )

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence_score = float(box.conf[0])
                detections.append(
                    PlateDetectionBox(
                        bbox=(x1, y1, x2, y2),
                        confidence_score=confidence_score,
                    )
                )

        if not detections:
            return PlateDetection(
                detection_type="VEHICLE",
                confidence_score=0.0,
                bbox=None,
            )

        best_detection = detections[0]
        return PlateDetection(
            detection_type="PLATE",
            confidence_score=best_detection.confidence_score,
            bbox=best_detection.bbox,
            boxes=detections,
        )

    def _load_model(self):
        if self._model is None:
            from ultralytics import YOLO

            self._model = YOLO(MODEL_PATH)

        return self._model
