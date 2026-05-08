from datetime import datetime
from pathlib import Path

import requests

from config import CAMERA_CODE, DETECTION_IMAGE_SEND_URL, REQUEST_TIMEOUT_SECONDS

IMAGE_PATH = Path("sample.jpg")


def main() -> None:
    data = {
        "cameraCode": CAMERA_CODE,
        "capturedAt": datetime.now().replace(microsecond=0).isoformat(),
    }

    with IMAGE_PATH.open("rb") as image_file:
        files = {
            "image": ("sample.jpg", image_file, "image/jpeg"),
        }

        response = requests.post(
            DETECTION_IMAGE_SEND_URL,
            data=data,
            files=files,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
