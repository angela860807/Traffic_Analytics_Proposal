import cv2
import numpy as np

from app.core.config import (
    DETECTION_PREPROCESS_MODE,
    OCR_ADAPTIVE_BLOCK_SIZE,
    OCR_ADAPTIVE_C,
    OCR_PREPROCESS_SCALE,
    PLATE_CROP_PADDING_RATIO,
)


def preprocess_frame_for_detection(image: np.ndarray) -> np.ndarray:
    if DETECTION_PREPROCESS_MODE == "none":
        return image

    if DETECTION_PREPROCESS_MODE != "standard":
        raise ValueError("DETECTION_PREPROCESS_MODE must be none or standard")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)
    equalized = cv2.equalizeHist(denoised)
    sharpen_kernel = np.array(
        [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0],
        ],
        dtype=np.float32,
    )
    sharpened = cv2.filter2D(equalized, -1, sharpen_kernel)

    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)


def crop_plate_with_padding(
    image: np.ndarray,
    bbox: tuple[int, int, int, int],
    padding_ratio: float = PLATE_CROP_PADDING_RATIO,
) -> np.ndarray:
    image_h, image_w = image.shape[:2]
    x1, y1, x2, y2 = bbox

    box_w = x2 - x1
    box_h = y2 - y1

    pad_x = int(box_w * padding_ratio)
    pad_y = int(box_h * padding_ratio)

    px1 = max(0, x1 - pad_x)
    py1 = max(0, y1 - pad_y)
    px2 = min(image_w, x2 + pad_x)
    py2 = min(image_h, y2 + pad_y)

    plate_crop = image[py1:py2, px1:px2]

    if plate_crop.size == 0:
        raise ValueError("plate crop is empty")

    return plate_crop


def preprocess_plate_for_ocr(plate_crop: np.ndarray) -> np.ndarray:
    resized = cv2.resize(
        plate_crop,
        None,
        fx=OCR_PREPROCESS_SCALE,
        fy=OCR_PREPROCESS_SCALE,
        interpolation=cv2.INTER_CUBIC,
    )

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    block_size = OCR_ADAPTIVE_BLOCK_SIZE
    if block_size % 2 == 0:
        block_size += 1

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        OCR_ADAPTIVE_C,
    )

    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
