import re
from dataclasses import dataclass

import numpy as np

from app.core.config import OCR_LANG, OCR_MIN_CONFIDENCE


@dataclass
class PlateRecognition:
    text: str | None
    confidence_score: float


class PlateRecognizer:
    def __init__(self) -> None:
        self._ocr = None

    def recognize(self, plate_image: np.ndarray) -> PlateRecognition:
        ocr = self._load_ocr()
        ocr_result = ocr.ocr(plate_image)

        text, confidence_score = self._merge_ocr_result(ocr_result)
        normalized_text = self._normalize_plate_number(text)

        if not normalized_text or confidence_score < OCR_MIN_CONFIDENCE:
            return PlateRecognition(
                text=None,
                confidence_score=confidence_score,
            )

        return PlateRecognition(
            text=normalized_text,
            confidence_score=confidence_score,
        )

    def _load_ocr(self):
        if self._ocr is None:
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(
                lang=OCR_LANG,
                use_angle_cls=True,
            )

        return self._ocr

    def _merge_ocr_result(self, ocr_result) -> tuple[str | None, float]:
        if not ocr_result or not ocr_result[0]:
            return None, 0.0

        ocr_lines = []

        for line in ocr_result[0]:
            points = line[0]
            text = line[1][0]
            prob = float(line[1][1])

            x_min = min(point[0] for point in points)

            ocr_lines.append(
                {
                    "text": text,
                    "prob": prob,
                    "x": x_min,
                }
            )

        ocr_lines.sort(key=lambda item: item["x"])

        full_text = "".join(item["text"] for item in ocr_lines)
        avg_prob = sum(item["prob"] for item in ocr_lines) / len(ocr_lines)

        return full_text, avg_prob

    def _normalize_plate_number(self, text: str | None) -> str | None:
        if not text:
            return None

        normalized = re.sub(r"[^0-9가-힣]", "", text)

        return normalized or None
