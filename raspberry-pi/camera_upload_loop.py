import time
from datetime import datetime

import cv2
from picamera2 import Picamera2

from fastapi_client import (
    FastApiClientError,
    summarize_detection_response,
    upload_detection_image,
)

from config import (
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    CAPTURE_INTERVAL_SECONDS,
)


def main() -> None:
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"format": "RGB888", "size": (CAMERA_WIDTH, CAMERA_HEIGHT)}
    )
    picam2.configure(config)
    picam2.start()

    print("camera upload loop started")

    try:
        while True:
            captured_at = datetime.now()
            frame = picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            success, buffer = cv2.imencode(".jpg", frame_bgr)

            if not success:
                print("failed to encode frame")
                time.sleep(CAPTURE_INTERVAL_SECONDS)
                continue

            try:
                result = upload_detection_image(buffer.tobytes(), captured_at)
                print(summarize_detection_response(result))
            except FastApiClientError as exc:
                print(f"upload failed: {exc}")

            time.sleep(CAPTURE_INTERVAL_SECONDS)

    finally:
        picam2.stop()


if __name__ == "__main__":
    main()
