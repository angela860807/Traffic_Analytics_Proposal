import numpy as np


class PlateRecognizer:
    def recognize(self, image: np.ndarray) -> str | None:
        # TODO:
            # 1. 탐지 결과의 bbox가 있으면 해당 영역을 번호판 이미지로 crop한다.
            # 2. OCR 모델을 실행해 번호판 문자열을 인식한다.
            # 3. 한글 번호판 문자열의 공백, 특수문자, 오인식 문자를 정규화한다.
            # 4. OCR confidence가 낮거나 읽을 수 없는 경우 None을 반환한다.

        return "123가4567"
