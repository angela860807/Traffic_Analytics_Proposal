from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from app.core.config import (
    IMAGE_STORAGE_DIR,
    PUBLIC_BASE_URL,
    STATIC_DETECTIONS_URL_PREFIX,
)


class ImageStorageService:
    def save_detection_image(
        self,
        *,
        image: np.ndarray,
        camera_code: str,
        captured_at: datetime,
        suffix: str = "frame",
    ) -> str:
        date_dir = captured_at.strftime("%Y/%m/%d")
        time_text = captured_at.strftime("%H%M%S")

        storage_dir = Path(IMAGE_STORAGE_DIR) / date_dir
        storage_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{camera_code}_{time_text}_{suffix}.jpg"
        file_path = storage_dir / file_name

        success = cv2.imwrite(str(file_path), image)

        if not success:
            raise RuntimeError("failed to save detection image")

        return str(file_path).replace("\\", "/")

    def build_detection_image_url(self, image_path: str) -> str:
        storage_root = Path(IMAGE_STORAGE_DIR)
        saved_path = Path(image_path)

        try:
            relative_path = saved_path.relative_to(storage_root)
        except ValueError:
            relative_path = saved_path.name

        relative_url_path = str(relative_path).replace("\\", "/")
        url_path = f"{STATIC_DETECTIONS_URL_PREFIX.rstrip('/')}/{relative_url_path}"

        if PUBLIC_BASE_URL:
            return f"{PUBLIC_BASE_URL}{url_path}"

        return url_path
