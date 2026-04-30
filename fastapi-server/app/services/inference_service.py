import base64

from app.schemas.detection import DetectionResult, RaspberryFrameRequest


class InferenceService:
    async def detect_from_frame(
        self,
        request: RaspberryFrameRequest,
    ) -> DetectionResult:
        # TODO: replace this mock logic with YOLO/OCR pipeline.
        base64.b64decode(request.image_base64, validate=True)

        return DetectionResult(
            camera_code=request.camera_code,
            plate_number="123가4567",
            detection_type="PLATE",
            direction_type="IN",
            confidence_score=0.9321,
            image_path=None,
            detected_at=request.captured_at,
        )
