from dataclasses import dataclass

import numpy as np


@dataclass
class PlateDetection:
    detection_type: str
    confidence_score: float
    bbox: tuple[int, int, int, int] | None = None


class PlateDetector:
    def detect(self, image: np.ndarray) -> PlateDetection:
        # TODO:
            # 1. MODEL_PATH 설정값을 사용해 YOLO 모델을 로드한다.
            # 2. 입력 이미지에서 차량 또는 번호판 영역을 탐지한다.
            # 3. 여러 탐지 결과 중 confidence가 가장 높은 번호판 탐지 결과를 우선 반환한다.
            # 4. 추후 번호판 crop 이미지 저장을 위해 bbox 좌표를 함께 유지한다.


        return PlateDetection(
            detection_type="PLATE",
            confidence_score=0.9321,
            bbox=None,
        )
