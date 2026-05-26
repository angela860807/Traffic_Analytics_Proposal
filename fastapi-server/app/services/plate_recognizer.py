import re
from dataclasses import dataclass

import numpy as np

from app.core.config import OCR_LANG, OCR_MIN_CONFIDENCE


@dataclass
class PlateRecognition:
    text: str | None
    confidence_score: float
    variant_name: str | None = None
    variant_image: np.ndarray | None = None


class PlateRecognizer:
    def __init__(self) -> None:
        self._ocr = None

    def recognize(self, plate_image: np.ndarray) -> PlateRecognition:
        return self._recognize_single(plate_image)

    def recognize_best(
        self,
        variants: list[tuple[str, np.ndarray]],
    ) -> PlateRecognition:
        best_recognition: PlateRecognition | None = None

        for variant_name, variant_image in variants:
            recognition = self._recognize_single(
                variant_image,
                variant_name=variant_name,
            )

            if best_recognition is None:
                best_recognition = recognition
                continue

            if self._is_better_recognition(recognition, best_recognition):
                best_recognition = recognition

        if best_recognition is None:
            return PlateRecognition(
                text=None,
                confidence_score=0.0,
            )

        return best_recognition

    def _recognize_single(
        self,
        plate_image: np.ndarray,
        *,
        variant_name: str | None = None,
    ) -> PlateRecognition:
        ocr = self._load_ocr()
        ocr_result = ocr.ocr(plate_image)

        text, confidence_score = self._merge_ocr_result(ocr_result)
        normalized_text = self._normalize_plate_number(text)

        if not normalized_text or confidence_score < OCR_MIN_CONFIDENCE:
            return PlateRecognition(
                text=None,
                confidence_score=confidence_score,
                variant_name=variant_name,
                variant_image=plate_image,
            )

        return PlateRecognition(
            text=normalized_text,
            confidence_score=confidence_score,
            variant_name=variant_name,
            variant_image=plate_image,
        )

    def _is_better_recognition(
        self,
        candidate: PlateRecognition,
        current: PlateRecognition,
    ) -> bool:
        if candidate.text and not current.text:
            return True
        if not candidate.text and current.text:
            return False

        candidate_shape_score = self._score_korean_plate_shape(candidate.text)
        current_shape_score = self._score_korean_plate_shape(current.text)
        if candidate_shape_score != current_shape_score:
            return candidate_shape_score > current_shape_score

        return candidate.confidence_score > current.confidence_score

    def _score_korean_plate_shape(self, text: str | None) -> int:
        if not text:
            return 0

        score = 0
        text_length = len(text)

        if 7 <= text_length <= 8:
            score += 10
        elif 6 <= text_length <= 9:
            score += 4

        hangul_count = len(re.findall(r"[\uac00-\ud7a3]", text))
        digit_count = len(re.findall(r"\d", text))

        if hangul_count == 1:
            score += 20
        elif hangul_count > 1:
            score += 5

        if digit_count >= 6:
            score += 10

        if re.fullmatch(r"\d{2,3}[\uac00-\ud7a3]\d{4}", text):
            score += 100
        elif re.search(r"\d{2,3}[\uac00-\ud7a3]\d{3,4}", text):
            score += 50

        return score

    def _load_ocr(self):
        if self._ocr is None:
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(
                lang=OCR_LANG,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                text_rec_score_thresh=OCR_MIN_CONFIDENCE,
                enable_mkldnn=False,
            )

        return self._ocr

    def _merge_ocr_result(self, ocr_result) -> tuple[str | None, float]:
        if not ocr_result:
            return None, 0.0

        first_result = ocr_result[0]

        if isinstance(first_result, dict):
            return self._merge_paddleocr_v3_result(first_result)

        if not first_result:
            return None, 0.0

        ocr_lines = []

        for line in first_result:
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

        return self._merge_sorted_lines(ocr_lines)

    def _merge_paddleocr_v3_result(self, ocr_result: dict) -> tuple[str | None, float]:
        texts = ocr_result.get("rec_texts") or []
        scores = ocr_result.get("rec_scores") or []
        boxes = ocr_result.get("rec_boxes")

        if boxes is None or len(boxes) == 0:
            boxes = ocr_result.get("rec_polys")

        if boxes is None:
            boxes = []

        if not texts:
            return None, 0.0

        ocr_lines = []

        for index, text in enumerate(texts):
            prob = float(scores[index]) if index < len(scores) else 0.0
            box = boxes[index] if index < len(boxes) else None
            x_min = self._extract_min_x(box) if box is not None else index

            ocr_lines.append(
                {
                    "text": text,
                    "prob": prob,
                    "x": x_min,
                }
            )

        return self._merge_sorted_lines(ocr_lines)

    def _merge_sorted_lines(self, ocr_lines: list[dict]) -> tuple[str | None, float]:
        if not ocr_lines:
            return None, 0.0

        ocr_lines.sort(key=lambda item: item["x"])

        full_text = "".join(item["text"] for item in ocr_lines)
        avg_prob = sum(item["prob"] for item in ocr_lines) / len(ocr_lines)

        return full_text, avg_prob

    def _extract_min_x(self, box) -> float:
        points = np.asarray(box)

        if points.ndim == 1:
            return float(points[0])

        return float(points[:, 0].min())

    def _normalize_plate_number(self, text: str | None) -> str | None:
        if not text:
            return None

        normalized = re.sub(r"[^0-9\uac00-\ud7a3]", "", text)

        return normalized or None
