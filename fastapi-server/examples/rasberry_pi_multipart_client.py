from datetime import datetime
from pathlib import Path

import requests


FASTAPI_URL = "http://127.0.0.1:8000/api/detections/image"
IMAGE_PATH = Path("samples/sample.jpg")


def main() -> None:
    data = {
        "cameraCode": "CAM_001",
        "capturedAt": datetime.now().replace(microsecond=0).isoformat(),
    }

    with IMAGE_PATH.open("rb") as image_file:
        files = {
            "image": ("sample.jpg", image_file, "image/jpeg"),
        }

        response = requests.post(
            FASTAPI_URL,
            data=data,
            files=files,
            timeout=10,
        )

    response.raise_for_status()

    print(response.json())


if __name__ == "__main__":
    main()
