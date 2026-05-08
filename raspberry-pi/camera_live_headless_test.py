import time

from picamera2 import Picamera2

from config import CAMERA_HEIGHT, CAMERA_WIDTH


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

    frame_count = 0
    started_at = time.time()

    print("camera headless live test started")
    print("press Ctrl + C to stop")

    try:
        while True:
            frame = picam2.capture_array()
            frame_count += 1

            elapsed = time.time() - started_at

            if elapsed >= 1:
                height, width = frame.shape[:2]
                fps = frame_count / elapsed

                print(
                    f"camera running... "
                    f"resolution={width}x{height}, "
                    f"fps={fps:.2f}"
                )

                frame_count = 0
                started_at = time.time()

    except KeyboardInterrupt:
        print("Ctrl + C received. stopping camera.")

    finally:
        picam2.stop()
        print("camera stopped")


if __name__ == "__main__":
    main()
