import base64
from datetime import datetime
from pathlib import Path

import requests

FASTAPI_URL = "http://127.0.0.1:8000/api/detections/mock"
IMAGE_PATH = Path("samples/sample.jpg")


def main() -> None:
    image_base64 = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")
    
    payload = {
        "cameraCode" : "CAM_001",
        "capturedAt" : datetime.now().replace(microsecond=0).isoformat(),
        "imageBase64" : image_base64,
    }
    
    response = requests.post(FASTAPI_URL, json=payload, timeout=10)
    response.raise_for_status()
    
    print(response.json())
    
if __name__ == "__main__":
    main()