import time
from datetime import datetime

import cv2
import requests
from picamera2 import Picamera2

from config import (
    CAMERA_CODE,
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    CAPTURE_INTERVAL_SECONDS,
    DETECTION_IMAGE_SEND_URL,
    REQUEST_TIMEOUT_SECONDS,
)


def upload_image(image_bytes: bytes, captured_at: datetime) -> dict:
    data = {
        "cameraCode": CAMERA_CODE,
        "capturedAt": captured_at.replace(microsecond=0).isoformat(),
    }

    files = {
        "image": ("capture.jpg", image_bytes, "image/jpeg"),
    }

    response = requests.post(
        DETECTION_IMAGE_SEND_URL,
        data=data,
        files=files,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    response.raise_for_status()
    return response.json()


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
                result = upload_image(buffer.tobytes(), captured_at)
                print(result)
            except requests.RequestException as exc:
                print(f"upload failed: {exc}")

            time.sleep(CAPTURE_INTERVAL_SECONDS)

    finally:
        picam2.stop()


if __name__ == "__main__":
    main()
