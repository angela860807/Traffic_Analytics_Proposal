from datetime import datetime

import cv2
from picamera2 import Picamera2

from fastapi_client import summarize_detection_response, upload_detection_image

from config import (
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
)

def capture_frame_as_jpeg() -> bytes:
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
    
    success, buffer = cv2.imencode(".jpg", frame_bgr)
    
    if not success:
        raise RuntimeError("failed to encode camera frame")
    
    return buffer.tobytes()

def main() -> None:
    image_bytes = capture_frame_as_jpeg()
    result = upload_detection_image(image_bytes, captured_at=datetime.now())
    print(summarize_detection_response(result))


if __name__ == "__main__":
    main()
