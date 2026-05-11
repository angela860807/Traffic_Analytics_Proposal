import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify YOLO/PaddleOCR inference with a local image.",
    )
    parser.add_argument(
        "--image",
        default="samples/sample.jpg",
        help="Path to a local jpg/png image.",
    )
    parser.add_argument(
        "--camera-code",
        default="CAM_001",
        help="Camera code sent through the inference pipeline.",
    )
    parser.add_argument(
        "--captured-at",
        default=None,
        help="Captured timestamp in ISO-8601 format. Defaults to current time.",
    )
    return parser


async def run_verification(args: argparse.Namespace) -> dict:
    image_path = Path(args.image)
    captured_at = (
        datetime.fromisoformat(args.captured_at)
        if args.captured_at
        else datetime.now().replace(microsecond=0)
    )

    report = {
        "ok": False,
        "modelPath": None,
        "ocrLang": None,
        "image": str(image_path),
        "cameraCode": args.camera_code,
        "capturedAt": captured_at.isoformat(),
        "checks": [],
    }

    try:
        from app.core.config import MODEL_PATH, OCR_LANG
        from app.services.inference_service import InferenceService
    except ModuleNotFoundError as exc:
        report["checks"].append(
            {
                "name": "python-dependencies",
                "ok": False,
                "message": f"missing Python dependency: {exc.name}",
            }
        )
        return report

    report["modelPath"] = MODEL_PATH
    report["ocrLang"] = OCR_LANG

    if not MODEL_PATH:
        report["checks"].append(
            {
                "name": "MODEL_PATH",
                "ok": False,
                "message": "MODEL_PATH is empty. Set it to a YOLOv11 model file before real verification.",
            }
        )
        return report

    if not Path(MODEL_PATH).exists():
        report["checks"].append(
            {
                "name": "MODEL_PATH",
                "ok": False,
                "message": f"model file does not exist: {MODEL_PATH}",
            }
        )
        return report

    if not image_path.exists():
        report["checks"].append(
            {
                "name": "image",
                "ok": False,
                "message": f"image file does not exist: {image_path}",
            }
        )
        return report

    service = InferenceService()

    try:
        result = await service.detect_from_saved_image(
            camera_code=args.camera_code,
            captured_at=captured_at,
            image_path=str(image_path),
        )
    except Exception as exc:
        report["checks"].append(
            {
                "name": "inference",
                "ok": False,
                "message": f"{type(exc).__name__}: {exc}",
            }
        )
        return report

    report["checks"].append(
        {
            "name": "inference",
            "ok": True,
            "message": "YOLO/PaddleOCR pipeline completed.",
        }
    )
    report["result"] = result.model_dump(by_alias=True, mode="json")
    report["ok"] = True

    return report


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    report = asyncio.run(run_verification(args))

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
