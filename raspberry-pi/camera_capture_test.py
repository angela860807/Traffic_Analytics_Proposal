from pathlib import Path

import cv2
from picamera2 import Picamera2

from config import CAMERA_HEIGHT, CAMERA_WIDTH


def main() -> None:
    output_path = Path("capture.jpg")

    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"format": "RGB888", "size": (CAMERA_WIDTH, CAMERA_HEIGHT)}
    )
    picam2.configure(config)
    picam2.start()

    try:
        frame = picam2.capture_array()
    finally:
        picam2.stop()

    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    success = cv2.imwrite(str(output_path), frame_bgr)

    if not success:
        raise RuntimeError("failed to save capture image")

    print(f"captured: {output_path}")


if __name__ == "__main__":
    main()
