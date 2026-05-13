import base64
from pathlib import Path

import cv2
import numpy as np


class ImageDecoder:
    def decode_base64_image(self, image_base64: str) -> np.ndarray:
        image_bytes = base64.b64decode(image_base64, validate=True)
        return self.decode_image_bytes(image_bytes)

    def decode_image_bytes(self, image_bytes: bytes) -> np.ndarray:
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("image must be a valid jpg or png")

        return image

    def decode_image_file(self, image_path: str) -> np.ndarray:
        path = Path(image_path)

        if not path.exists():
            raise ValueError("image file does not exist")

        image = cv2.imread(str(path))

        if image is None:
            raise ValueError("image file must be a valid jpg or png")

        return image
