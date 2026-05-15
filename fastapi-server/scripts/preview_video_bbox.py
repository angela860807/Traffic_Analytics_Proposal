import runpy
import sys


def main() -> None:
    print(
        "preview_video_bbox.py is kept for compatibility. "
        "Use stream_video_file.py --preview-bbox for combined streaming and GUI preview."
    )
    sys.argv = [
        "stream_video_file.py",
        *sys.argv[1:],
        "--preview-bbox",
    ]
    runpy.run_module("scripts.stream_video_file", run_name="__main__")


if __name__ == "__main__":
    main()
