from datetime import datetime

import cv2
import requests
from picamera2 import Picamera2

from config import (
    CAMERA_CODE,
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    DETECTION_IMAGE_SEND_URL,
    REQUEST_TIMEOUT_SECONDS,
)

def capture_frame_as_jpeg() -> bytes:
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"format": "RGB888", "size": (CAMERA_WIDTH, CAMERA_HEIGHT)}
    )
    picam2.configure(config)
    picam2.start()
    
    frame = picam2.capture_array()
    picam2.stop()
    
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    success, buffer = cv2.imencode(".jpg", frame_bgr)
    
    if not success:
        raise RuntimeError("failed to encode camera frame")
    
    return buffer.tobytes()

def upload_image(image_bytes:bytes) -> dict:
    data = {
        "cameraCode": CAMERA_CODE,
        "capturedAt": datetime.now().replace(microsecond=0).isoformat(),
    }
    
    files = {
        "image" : ("capture.jpg", image_bytes, "image/jpeg"),
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
    image_bytes = capture_frame_as_jpeg()
    result = upload_image(image_bytes)
    print(result)
    
if __name__ == "__main__":
    main()
