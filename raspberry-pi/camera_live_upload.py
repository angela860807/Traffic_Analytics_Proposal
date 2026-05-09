import time
from datetime import datetime

import cv2
from picamera2 import Picamera2

from fastapi_client import FastApiClientError, upload_live_frame

from config import (
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    JPEG_QUALITY,
    LIVE_FRAME_INTERVAL_SECONDS,
)


def main() -> None:
    picam2 = Picamera2()

    config = picam2.create_preview_configuration(
        main={
            "format": "RGB888",
            "size": (CAMERA_WIDTH, CAMERA_HEIGHT),
        }
    )

    picam2.configure(config)
    picam2.start()

    print("camera live upload started")
    print("press Ctrl + C to stop")

    try:
        while True:
            captured_at = datetime.now()

            frame = picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            success, buffer = cv2.imencode(
                ".jpg",
                frame_bgr,
                [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY],
            )

            if not success:
                print("failed to encode frame")
                time.sleep(LIVE_FRAME_INTERVAL_SECONDS)
                continue

            try:
                upload_live_frame(buffer.tobytes(), captured_at)
                print(f"uploaded frame at {captured_at.replace(microsecond=0).isoformat()}")
            except FastApiClientError as exc:
                print(f"upload failed: {exc}")

            time.sleep(LIVE_FRAME_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("stopping camera live upload")

    finally:
        picam2.stop()
        print("camera stopped")


if __name__ == "__main__":
    main()
