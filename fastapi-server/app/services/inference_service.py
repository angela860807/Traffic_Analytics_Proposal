from datetime import datetime

from app.core.config import DETECTION_CONFIDENCE_THRESHOLD, SAVE_PLATE_CROP
from app.schemas.detection import DetectionResult, RaspberryFrameRequest
from app.services.image_decoder import ImageDecoder
from app.services.image_storage_service import ImageStorageService
from app.services.plate_cropper import crop_plate_with_padding, preprocess_plate_for_ocr
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

        if detection.bbox is None:
            if detection.detection_type == "PLATE":
                plate_number = "123가4567"
                detection_type = "PLATE"
            else:
                plate_number = None
                detection_type = "VEHICLE"
        elif detection.confidence_score < DETECTION_CONFIDENCE_THRESHOLD:
            plate_number = None
            detection_type = "VEHICLE"
        else:
            plate_crop = crop_plate_with_padding(image, detection.bbox)
            ocr_image = preprocess_plate_for_ocr(plate_crop)

            if SAVE_PLATE_CROP:
                self.image_storage_service.save_detection_image(
                    image=ocr_image,
                    camera_code=camera_code,
                    captured_at=captured_at,
                    suffix="plate",
                )

            recognition = self.plate_recognizer.recognize(ocr_image)

            plate_number = recognition.text
            detection_type = "PLATE" if plate_number else "VEHICLE"

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
# Replace the mock detector/recognizer with the real YOLO/OCR services.
# Keep DetectionResult stable so API callers do not depend on model internals.
