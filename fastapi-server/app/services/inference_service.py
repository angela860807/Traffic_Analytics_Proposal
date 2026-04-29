from app.schemas.detection import DetectionResult

class IngerenceService:
    async def detect_from_image(
        self,
        *,
        camera_code: str,
        image_bytes: bytes,
    ) -> DetectionResult:
        # TODO: replace with YOLO/OCR pipeline.
        # Keep this interface stable so API code does not depend on model details.
        raise NotImplementedError