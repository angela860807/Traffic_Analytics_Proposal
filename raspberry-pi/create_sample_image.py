from pathlib import Path

import cv2
import numpy as np


def main() -> None:
    image = np.zeros((240, 480, 3), dtype=np.uint8)

    cv2.rectangle(image, (120, 90), (360, 150), (255, 255, 255), -1)
    cv2.putText(
        image,
        "CAM_001",
        (155, 128),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 0, 0),
        2,
        cv2.LINE_AA,
    )

    output_path = Path("sample.jpg")
    success = cv2.imwrite(str(output_path), image)

    if not success:
        raise RuntimeError("failed to create sample image")

    print(f"created: {output_path}")


if __name__ == "__main__":
    main()
