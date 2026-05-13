from datetime import datetime
from pathlib import Path

import requests

from config import HEALTH_URL, REQUEST_TIMEOUT_SECONDS
from fastapi_client import (
    FastApiClientError,
    summarize_detection_response,
    upload_detection_image_file,
)


IMAGE_PATH = Path("sample.jpg")


def check_health() -> None:
    response = requests.get(
        HEALTH_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    print(f"health ok: {response.json()}")


def upload_sample() -> None:
    if not IMAGE_PATH.exists():
        raise FastApiClientError(
            "sample.jpg not found. run `python create_sample_image.py` first."
        )

    result = upload_detection_image_file(
        IMAGE_PATH,
        captured_at=datetime.now(),
    )
    print(summarize_detection_response(result))


def main() -> None:
    check_health()
    upload_sample()


if __name__ == "__main__":
    main()
