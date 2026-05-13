from datetime import datetime

from app.core.config import (
    DETECTION_CONFIDENCE_THRESHOLD,
    SAVE_OCR_PREPROCESSED_IMAGE,
    SAVE_PLATE_CROP,
)
from app.schemas.detection import DetectionResult, RaspberryFrameRequest
from app.services.image_decoder import ImageDecoder
from app.services.image_storage_service import ImageStorageService
from app.services.image_preprocessor import (
    crop_plate_with_padding,
    preprocess_frame_for_detection,
    preprocess_plate_for_ocr,
)
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

    async def detect_from_saved_image(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        image_path: str,
    ) -> DetectionResult:
        image = self.image_decoder.decode_image_file(image_path)

        return self._detect(
            image=image,
            camera_code=camera_code,
            captured_at=captured_at,
            existing_image_path=image_path,
        )

    def _detect(
        self,
        *,
        image,
        camera_code: str,
        captured_at: datetime,
        existing_image_path: str | None = None,
    ) -> DetectionResult:
        if existing_image_path is None:
            image_path = self.image_storage_service.save_detection_image(
                image=image,
                camera_code=camera_code,
                captured_at=captured_at,
                suffix="frame",
            )
        else:
            image_path = existing_image_path.replace("\\", "/")

        image_url = self.image_storage_service.build_detection_image_url(image_path)
        plate_crop_image_path = None
        plate_crop_image_url = None
        ocr_image_path = None
        ocr_image_url = None

        detection_image = preprocess_frame_for_detection(image)
        detection = self.plate_detector.detect(detection_image)
        confidence_score = detection.confidence_score

        if detection.bbox is None:
            plate_number = None
            detection_type = "VEHICLE"
            confidence_score = 0.0
        elif detection.confidence_score < DETECTION_CONFIDENCE_THRESHOLD:
            plate_number = None
            detection_type = "VEHICLE"
        else:
            plate_crop = crop_plate_with_padding(image, detection.bbox)

            if SAVE_PLATE_CROP:
                plate_crop_image_path = self.image_storage_service.save_detection_image(
                    image=plate_crop,
                    camera_code=camera_code,
                    captured_at=captured_at,
                    suffix="plate_crop",
                )
                plate_crop_image_url = self.image_storage_service.build_detection_image_url(
                    plate_crop_image_path,
                )

            ocr_image = preprocess_plate_for_ocr(plate_crop)

            if SAVE_OCR_PREPROCESSED_IMAGE:
                ocr_image_path = self.image_storage_service.save_detection_image(
                    image=ocr_image,
                    camera_code=camera_code,
                    captured_at=captured_at,
                    suffix="ocr",
                )
                ocr_image_url = self.image_storage_service.build_detection_image_url(
                    ocr_image_path,
                )

            recognition = self.plate_recognizer.recognize(ocr_image)

            plate_number = recognition.text
            detection_type = "PLATE" if plate_number else "VEHICLE"

        return DetectionResult(
            camera_code=camera_code,
            plate_number=plate_number,
            detection_type=detection_type,
            direction_type="IN",
            confidence_score=confidence_score,
            image_path=image_path,
            image_url=image_url,
            plate_crop_image_path=plate_crop_image_path,
            plate_crop_image_url=plate_crop_image_url,
            ocr_image_path=ocr_image_path,
            ocr_image_url=ocr_image_url,
            detected_at=captured_at,
        )


# TODO:
# Replace the mock detector/recognizer with the real YOLO/OCR services.
# Keep DetectionResult stable so API callers do not depend on model internals.
