from datetime import datetime
from pathlib import Path

from fastapi_client import summarize_detection_response, upload_detection_image_file

IMAGE_PATH = Path("sample.jpg")


def main() -> None:
    result = upload_detection_image_file(
        IMAGE_PATH,
        captured_at=datetime.now(),
    )
    print(summarize_detection_response(result))


if __name__ == "__main__":
    main()
