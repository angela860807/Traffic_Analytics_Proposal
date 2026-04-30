from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from app.core.config import IMAGE_STORAGE_DIR


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
