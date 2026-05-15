from dataclasses import dataclass, field

import numpy as np

from app.core.config import (
    VEHICLE_CLASS_NAMES,
    VEHICLE_MODEL_SOURCE,
    VEHICLE_YOLO_CONF_THRESHOLD,
    VEHICLE_YOLO_IOU_THRESHOLD,
    VEHICLE_YOLO_MAX_DET,
)


@dataclass
class VehicleDetectionBox:
    bbox: tuple[int, int, int, int]
    confidence_score: float
    class_name: str


@dataclass
class VehicleDetection:
    detection_type: str
    confidence_score: float
    bbox: tuple[int, int, int, int] | None = None
    boxes: list[VehicleDetectionBox] = field(default_factory=list)


class VehicleDetector:
    def __init__(self) -> None:
        self._model = None

    def detect(self, image: np.ndarray) -> VehicleDetection:
        if not VEHICLE_MODEL_SOURCE:
            return VehicleDetection(
                detection_type="UNKNOWN",
                confidence_score=0.0,
                bbox=None,
            )

        model = self._load_model()

        results = model(
            image,
            conf=VEHICLE_YOLO_CONF_THRESHOLD,
            iou=VEHICLE_YOLO_IOU_THRESHOLD,
            max_det=VEHICLE_YOLO_MAX_DET,
        )

        detections: list[VehicleDetectionBox] = []
        allowed_classes = set(VEHICLE_CLASS_NAMES)

        for result in results:
            names = getattr(result, "names", getattr(model, "names", {}))
            boxes = sorted(
                result.boxes,
                key=lambda box: float(box.conf[0]),
                reverse=True,
            )

            for box in boxes:
                class_id = int(box.cls[0])
                class_name = str(names.get(class_id, class_id)).lower()

                if class_name not in allowed_classes:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence_score = float(box.conf[0])
                detections.append(
                    VehicleDetectionBox(
                        bbox=(x1, y1, x2, y2),
                        confidence_score=confidence_score,
                        class_name=class_name,
                    )
                )

        if not detections:
            return VehicleDetection(
                detection_type="UNKNOWN",
                confidence_score=0.0,
                bbox=None,
            )

        best_detection = detections[0]
        return VehicleDetection(
            detection_type="VEHICLE",
            confidence_score=best_detection.confidence_score,
            bbox=best_detection.bbox,
            boxes=detections,
        )

    def _load_model(self):
        if self._model is None:
            from ultralytics import YOLO

            self._model = YOLO(VEHICLE_MODEL_SOURCE)

        return self._model
