from datetime import datetime

from app.core.config import DETECTION_CONFIDENCE_THRESHOLD
from app.schemas.detection import DetectionResult, RaspberryFrameRequest
from app.services.image_decoder import ImageDecoder
from app.services.image_storage_service import ImageStorageService
from app.services.plate_detector import PlateDetector
from app.services.plate_recognizer import PlateRecognizer


class InferenceService:
    def __init__(self) -> None:
        self.image_decoder = ImageDecoder()
        self.image_storage_service = ImageStorageService()
        self.plate_detector = PlateDetector()
        self.plate_recognizer = PlateRecognizer()

    async def detect_from_frame(
        self,
        request: RaspberryFrameRequest,
    ) -> DetectionResult:
        image = self.image_decoder.decode_base64_image(request.image_base64)

        return self._detect(
            image=image,
            camera_code=request.camera_code,
            captured_at=request.captured_at,
        )

    async def detect_from_image_bytes(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        image_bytes: bytes,
    ) -> DetectionResult:
        image = self.image_decoder.decode_image_bytes(image_bytes)

        return self._detect(
            image=image,
            camera_code=camera_code,
            captured_at=captured_at,
        )

    def _detect(
        self,
        *,
        image,
        camera_code: str,
        captured_at: datetime,
    ) -> DetectionResult:
        detection = self.plate_detector.detect(image)

        if detection.confidence_score < DETECTION_CONFIDENCE_THRESHOLD:
            plate_number = None
            detection_type = "VEHICLE"
        else:
            plate_number = self.plate_recognizer.recognize(image)
            detection_type = detection.detection_type

        image_path = self.image_storage_service.save_detection_image(
            image=image,
            camera_code=camera_code,
            captured_at=captured_at,
            suffix="frame",
        )
        image_url = self.image_storage_service.build_detection_image_url(image_path)

        return DetectionResult(
            camera_code=camera_code,
            plate_number=plate_number,
            detection_type=detection_type,
            direction_type="IN",
            confidence_score=detection.confidence_score,
            image_path=image_path,
            detected_at=captured_at,
            image_url=image_url,
        )

# TODO:
# mock detector와 mock recognizer를 실제 YOLO/OCR 서비스로 교체한다.
# API 라우터가 모델 세부 구현에 의존하지 않도록 DetectionResult 응답 구조는 안정적으로 유지한다.
