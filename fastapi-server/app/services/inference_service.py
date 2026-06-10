from datetime import datetime

from app.core.config import (
    DETECTION_CONFIDENCE_THRESHOLD,
    SAVE_OCR_PREPROCESSED_IMAGE,
    SAVE_PLATE_CROP,
    SAVE_VEHICLE_CROP,
)
from app.schemas.detection import DetectionResult, RaspberryFrameRequest
from app.services.image_decoder import ImageDecoder
from app.services.image_storage_service import ImageStorageService
from app.services.image_preprocessor import (
    build_plate_ocr_variants,
    crop_vehicle_square,
    crop_plate_with_padding,
    preprocess_frame_for_detection,
)
from app.services.plate_detector import PlateDetector
from app.services.plate_detector import PlateDetection
from app.services.plate_recognizer import PlateRecognizer
from app.services.camera_health_collector import CameraHealthCollector
from app.services.vehicle_detector import VehicleDetection
from app.services.vehicle_detector import VehicleDetector


class InferenceService:
    def __init__(
        self,
        *,
        health_collector: CameraHealthCollector | None = None,
    ) -> None:
        self.image_decoder = ImageDecoder()
        self.image_storage_service = ImageStorageService()
        self.vehicle_detector = VehicleDetector()
        self.plate_detector = PlateDetector()
        self.plate_recognizer = PlateRecognizer()
        self.health_collector = health_collector

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
        high_res_crop_bytes: bytes | None = None,
        vehicle_detection: VehicleDetection | None = None,
    ) -> DetectionResult:
        return self.detect_from_image_bytes_sync(
            camera_code=camera_code,
            captured_at=captured_at,
            image_bytes=image_bytes,
            high_res_crop_bytes=high_res_crop_bytes,
            vehicle_detection=vehicle_detection,
        )

    def detect_from_image_bytes_sync(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        image_bytes: bytes,
        high_res_crop_bytes: bytes | None = None,
        vehicle_detection: VehicleDetection | None = None,
    ) -> DetectionResult:
        image = self.image_decoder.decode_image_bytes(image_bytes)
        high_res_ocr_image = (
            self.image_decoder.decode_image_bytes(high_res_crop_bytes)
            if high_res_crop_bytes is not None
            else None
        )

        return self._detect(
            image=image,
            camera_code=camera_code,
            captured_at=captured_at,
            high_res_ocr_image=high_res_ocr_image,
            vehicle_detection=vehicle_detection,
        )

    async def detect_from_saved_image(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        image_path: str,
        vehicle_detection: VehicleDetection | None = None,
    ) -> DetectionResult:
        image = self.image_decoder.decode_image_file(image_path)

        return self._detect(
            image=image,
            camera_code=camera_code,
            captured_at=captured_at,
            existing_image_path=image_path,
            vehicle_detection=vehicle_detection,
        )

    def detect_plate_bbox_from_image(self, image) -> PlateDetection:
        detection_image = preprocess_frame_for_detection(image)
        return self.plate_detector.detect(detection_image)

    def detect_vehicle_bbox_from_image(self, image) -> VehicleDetection:
        detection_image = preprocess_frame_for_detection(image)
        return self.vehicle_detector.detect(detection_image)

    def _detect(
        self,
        *,
        image,
        camera_code: str,
        captured_at: datetime,
        existing_image_path: str | None = None,
        high_res_ocr_image=None,
        vehicle_detection: VehicleDetection | None = None,
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
        frame_image_path = image_path
        frame_image_url = image_url
        vehicle_crop_image_path = None
        vehicle_crop_image_url = None
        plate_crop_image_path = None
        plate_crop_image_url = None
        ocr_image_path = None
        ocr_image_url = None
        processing_status = "OCR_COMPLETED"

        if vehicle_detection is None:
            vehicle_detection = self.detect_vehicle_bbox_from_image(image)

        if vehicle_detection.bbox is None:
            plate_number = None
            detection_type = "UNKNOWN"
            confidence_score = 0.0
            processing_status = "NO_VEHICLE"
        else:
            if SAVE_VEHICLE_CROP:
                vehicle_crop = crop_vehicle_square(
                    image,
                    vehicle_detection.bbox,
                )
                vehicle_crop_image_path = (
                    self.image_storage_service.save_detection_image(
                        image=vehicle_crop,
                        camera_code=camera_code,
                        captured_at=captured_at,
                        suffix="vehicle_crop",
                    )
                )
                vehicle_crop_image_url = (
                    self.image_storage_service.build_detection_image_url(
                        vehicle_crop_image_path,
                    )
                )
            ocr_source_image = (
                high_res_ocr_image
                if high_res_ocr_image is not None
                else image
            )
            plate_detection = self.detect_plate_bbox_from_image(ocr_source_image)
            confidence_score = vehicle_detection.confidence_score

            if (
                plate_detection.bbox is None
                or plate_detection.confidence_score < DETECTION_CONFIDENCE_THRESHOLD
            ):
                plate_number = None
                detection_type = "VEHICLE"
                processing_status = "PLATE_NOT_DETECTED"
            else:
                plate_crop = crop_plate_with_padding(
                    ocr_source_image,
                    plate_detection.bbox,
                )

                if SAVE_PLATE_CROP:
                    plate_crop_image_path = (
                        self.image_storage_service.save_detection_image(
                            image=plate_crop,
                            camera_code=camera_code,
                            captured_at=captured_at,
                            suffix="plate_crop",
                        )
                    )
                    plate_crop_image_url = (
                        self.image_storage_service.build_detection_image_url(
                            plate_crop_image_path,
                        )
                    )

                ocr_variants = build_plate_ocr_variants(plate_crop)
                try:
                    recognition = (
                        self.plate_recognizer.recognize_best(ocr_variants)
                        if hasattr(self.plate_recognizer, "recognize_best")
                        else self.plate_recognizer.recognize(ocr_variants[-1][1])
                    )
                except Exception:
                    self._record_ocr_result(
                        camera_code=camera_code,
                        captured_at=captured_at,
                        failed=True,
                    )
                    raise
                ocr_image = (
                    recognition.variant_image
                    if recognition.variant_image is not None
                    else ocr_variants[-1][1]
                )

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

                plate_number = recognition.text
                detection_type = "PLATE" if plate_number else "VEHICLE"
                confidence_score = plate_detection.confidence_score
                processing_status = (
                    "OCR_COMPLETED" if plate_number else "OCR_FAILED"
                )
                self._record_ocr_result(
                    camera_code=camera_code,
                    captured_at=captured_at,
                    failed=not bool(plate_number),
                )

        return DetectionResult(
            camera_code=camera_code,
            plate_number=plate_number,
            detection_type=detection_type,
            direction_type="IN",
            confidence_score=confidence_score,
            image_path=image_path,
            image_url=image_url,
            frame_image_path=frame_image_path,
            frame_image_url=frame_image_url,
            vehicle_crop_image_path=vehicle_crop_image_path,
            vehicle_crop_image_url=vehicle_crop_image_url,
            plate_crop_image_path=plate_crop_image_path,
            plate_crop_image_url=plate_crop_image_url,
            ocr_image_path=ocr_image_path,
            ocr_image_url=ocr_image_url,
            detected_at=captured_at,
            processing_status=processing_status,
        )

    def _record_ocr_result(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        failed: bool,
    ) -> None:
        if self.health_collector is None:
            return
        self.health_collector.record_ocr_result(
            camera_code=camera_code,
            captured_at=captured_at,
            failed=failed,
        )


# TODO:
# Replace the mock detector/recognizer with the real YOLO/OCR services.
# Keep DetectionResult stable so API callers do not depend on model internals.
