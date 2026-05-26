import argparse
from collections import deque
from dataclasses import dataclass, field
import json
import os
import queue
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import requests

STREAM_FRAME_PATH = "/api/detections/stream-frame"
HIGHRES_OCR_PATH = "/api/detections/stream-frame/highres-ocr"
WINDOW_NAME = "Traffic Stream + BBox Preview"
SPEED_ZONE_WINDOW_NAME = "Speed Zone Config"


@dataclass
class UploadTask:
    frame_number: int
    captured_at: datetime
    frame_bytes: bytes
    high_res_crop_bytes: bytes | None = None
    high_res_crop_frame_number: int | None = None


@dataclass
class UploadState:
    lock: threading.Lock = field(default_factory=threading.Lock)
    latest_response_body: dict[str, Any] | None = None
    latest_response_frame_number: int | None = None
    responses_by_frame: dict[int, dict[str, Any]] = field(default_factory=dict)
    uploaded_count: int = 0
    finalized_count: int = 0
    dropped_count: int = 0
    error: str | None = None
    stopped_by_finalized_limit: bool = False


@dataclass
class PreviewTracker:
    tracker: Any
    bbox_xyxy: tuple[int, int, int, int]
    response_frame_number: int
    last_frame_number: int
    confidence_score: float = 0.0


@dataclass
class PreviewOverlay:
    bbox_xyxy: tuple[int, int, int, int]
    response_frame_number: int
    confidence_score: float = 0.0


@dataclass
class PreviewFrame:
    frame_number: int
    frame: Any


@dataclass(frozen=True)
class SpeedOverlayConfig:
    roi: list[tuple[int, int]] = field(default_factory=list)
    line_a: tuple[int, int, int, int] | None = None
    line_b: tuple[int, int, int, int] | None = None
    homography_points: list[tuple[int, int]] = field(default_factory=list)
    speed_mode: str = "TRACK_DELTA"


@dataclass
class SpeedZoneSelectionState:
    points: list[tuple[int, int]] = field(default_factory=list)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stream a local video file to FastAPI /api/detections/stream-frame.",
    )
    parser.add_argument(
        "--video",
        required=True,
        help="Path to a local mp4/avi video file.",
    )
    parser.add_argument(
        "--fastapi-base-url",
        default="http://127.0.0.1:8000",
        help="FastAPI base URL.",
    )
    parser.add_argument(
        "--camera-code",
        default="CAM_001",
        help="Camera code sent with each frame.",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=5.0,
        help="Target frame upload FPS.",
    )
    parser.add_argument(
        "--video-speed-ratio",
        type=float,
        default=1.0,
        help=(
            "Playback speed ratio of the video compared with real/original time. "
            "Use 0.70 when the video is slowed to 70%% speed so capturedAt time "
            "is compressed for speed calculation."
        ),
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=70,
        help="JPEG quality for uploaded frames.",
    )
    parser.add_argument(
        "--upload-scale",
        type=float,
        default=0.6,
        help=(
            "Resize frames before upload to reduce server YOLO load. "
            "1.0 uploads original resolution."
        ),
    )
    parser.add_argument(
        "--highres-ocr-crop",
        action="store_true",
        help="Attach a high-resolution vehicle crop for OCR when a recent bbox is available.",
    )
    parser.add_argument(
        "--highres-crop-padding",
        type=float,
        default=0.25,
        help="Padding ratio around the original-resolution bbox crop sent for OCR.",
    )
    parser.add_argument(
        "--highres-jpeg-quality",
        type=int,
        default=85,
        help="JPEG quality for high-resolution OCR crops.",
    )
    parser.add_argument(
        "--finalized-highres-ocr",
        action=argparse.BooleanOptionalAction,
        default=False,
        help=(
            "After FINALIZED, synchronously call the legacy high-res OCR endpoint. "
            "Disabled by default because stream-frame now queues OCR in FastAPI."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="HTTP request timeout in seconds.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maximum number of frames to upload. 0 means no limit.",
    )
    parser.add_argument(
        "--stop-after-finalized",
        type=int,
        default=0,
        help="Optional early stop after this many FINALIZED events. 0 means play the whole video once.",
    )
    parser.add_argument(
        "--flush-frames",
        type=int,
        default=4,
        help="No-detection blank frames sent after EOF to close any active bbox event.",
    )
    parser.add_argument(
        "--realtime",
        action="store_true",
        help="Sleep between uploads to approximate the target FPS.",
    )
    parser.add_argument(
        "--preview-bbox",
        action="store_true",
        help="Open an OpenCV window and draw bbox overlay from FastAPI stream response.",
    )
    parser.add_argument(
        "--preview-fps",
        type=float,
        default=12.0,
        help="Maximum OpenCV GUI redraw FPS. 0 displays every decoded video frame.",
    )
    parser.add_argument(
        "--preview-tracker",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Track response bbox between server responses. Disable for smoother low-end CPU preview.",
    )
    parser.add_argument(
        "--bbox-hold-seconds",
        type=float,
        default=1.4,
        help="Keep drawing the latest response bbox for this many seconds without OpenCV tracking.",
    )
    parser.add_argument(
        "--preview-max-event-age-seconds",
        type=float,
        default=3.8,
        help="Hide preview bbox when the active stream event is older than this. 0 disables.",
    )
    parser.add_argument(
        "--preview-max-bbox-area-ratio",
        type=float,
        default=0.32,
        help="Hide preview bbox when it covers more than this ratio of the frame. 0 disables.",
    )
    parser.add_argument(
        "--preview-min-bbox-confidence",
        type=float,
        default=0.45,
        help="Hide preview bbox when vehicle confidence is below this value. 0 disables.",
    )
    parser.add_argument(
        "--preview-primary-bbox-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Draw only the primary vehicle bbox in preview instead of every candidate bbox.",
    )
    parser.add_argument(
        "--preview-max-response-lag-seconds",
        type=float,
        default=0.25,
        help="Hide preview bbox when the matched server response is older than this many video seconds. 0 requires the exact response frame.",
    )
    parser.add_argument(
        "--model-path",
        default=None,
        help="Deprecated. BBox preview now uses FastAPI response data, not a local model.",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=0.35,
        help="OpenCV preview display scale. 1.0 keeps the original video size.",
    )
    parser.add_argument(
        "--window-width",
        type=int,
        default=960,
        help="Initial OpenCV window width. Use 1920 for full HD preview.",
    )
    parser.add_argument(
        "--window-height",
        type=int,
        default=540,
        help="Initial OpenCV window height. Use 1080 for full HD preview.",
    )
    parser.add_argument(
        "--preview-all-frames",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Display skipped source frames too, reusing the latest bbox overlay.",
    )
    parser.add_argument(
        "--async-upload",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Upload frames in a background worker so OpenCV preview does not block on YOLO.",
    )
    parser.add_argument(
        "--upload-queue-size",
        type=int,
        default=1,
        help="Max queued upload frames in async mode. Old frames are dropped when the queue is full.",
    )
    parser.add_argument(
        "--preview-delay-seconds",
        type=float,
        default=2.0,
        help="Delay GUI playback so bbox responses can be drawn on their matching frames.",
    )
    parser.add_argument(
        "--speed-config-json",
        default=None,
        help=(
            "Optional SPEED_CAMERA_CONFIGS_JSON value or JSON file path used only "
            "to draw ROI, lineA/B, and homography image points on preview."
        ),
    )
    parser.add_argument(
        "--configure-speed-zone",
        action="store_true",
        help=(
            "Open the first upload-scaled video frame and click ROI 4 points "
            "for this run. Press Enter without points to use the full frame."
        ),
    )
    parser.add_argument(
        "--save-speed-config-json",
        default=None,
        help=(
            "Optional output JSON file path used with --configure-speed-zone. "
            "When omitted, the clicked speed zone is used only for this run."
        ),
    )
    parser.add_argument(
        "--roi-width-meters",
        type=float,
        default=14.0,
        help="World width in meters for the clicked ROI homography rectangle.",
    )
    parser.add_argument(
        "--roi-height-meters",
        type=float,
        default=14.0,
        help="World height in meters for the clicked ROI homography rectangle.",
    )
    parser.add_argument(
        "--distance-meters",
        type=float,
        default=14.0,
        help="Fallback lineA/lineB distance in meters when homography is unavailable.",
    )
    parser.add_argument(
        "--speed-limit-kmh",
        type=float,
        default=50.0,
        help="Speed limit written to the generated speed config JSON.",
    )
    return parser


def summarize_response(frame_number: int, response_body: dict[str, Any]) -> str:
    data = response_body.get("data") or {}
    speed_violation = response_body.get("speedViolation") or {}
    speed_measurements = response_body.get("speedMeasurements") or []
    speed_text = "-"
    over_speed = False
    if speed_violation:
        over_speed = True
        speed_text = format_speed_text(speed_violation, prefix="VIOLATION:")
    elif speed_measurements:
        measurement = speed_measurements[0]
        over_speed = bool(measurement.get("isViolation", False))
        speed_text = format_speed_text(measurement)
    return (
        f"frame={frame_number} "
        f"streamStatus={response_body.get('streamStatus')} "
        f"eventId={response_body.get('eventId') or '-'} "
        f"frameCount={response_body.get('frameCount')} "
        f"bestFrame={response_body.get('bestCandidateFrameNumber') or '-'} "
        f"analysisStatus={response_body.get('analysisStatus') or '-'} "
        f"speed={speed_text} "
        f"overSpeed={over_speed} "
        f"speedSent={response_body.get('speedViolationSent', False)} "
        f"plateNumber={data.get('plateNumber') or '-'}"
    )


def format_speed_text(measurement: dict[str, Any], *, prefix: str = "") -> str:
    return (
        f"{prefix}{measurement.get('measuredSpeed', '-')}/"
        f"{measurement.get('speedLimit', '-')}"
    )


def post_frame(
    *,
    url: str,
    camera_code: str,
    captured_at: datetime,
    frame_number: int | None,
    frame_bytes: bytes,
    timeout: float,
    speed_config_json: str | None = None,
    high_res_crop_bytes: bytes | None = None,
    high_res_crop_frame_number: int | None = None,
) -> dict[str, Any]:
    data = {
        "cameraCode": camera_code,
        "capturedAt": captured_at.isoformat(timespec="milliseconds"),
    }
    if frame_number is not None:
        data["frameNumber"] = str(frame_number)
    if speed_config_json is not None:
        data["speedConfigJson"] = speed_config_json

    files = {
        "image": ("video-frame.jpg", frame_bytes, "image/jpeg"),
    }
    if high_res_crop_bytes is not None:
        if high_res_crop_frame_number is not None:
            data["highResCropFrameNumber"] = str(high_res_crop_frame_number)
        files["highResCrop"] = (
            "highres-crop.jpg",
            high_res_crop_bytes,
            "image/jpeg",
        )

    response = requests.post(
        url,
        data=data,
        files=files,
        timeout=timeout,
    )

    if response.status_code == 404:
        raise RuntimeError(
            f"stream-frame endpoint was not found at {url}. "
            "Restart FastAPI or rebuild the Docker container so the latest route is loaded."
        )

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        body = response.text[:500]
        raise RuntimeError(
            f"request failed: status={response.status_code}, body={body}"
        ) from exc

    return response.json()


def post_highres_ocr(
    *,
    url: str,
    camera_code: str,
    captured_at: str,
    frame_number: int,
    high_res_crop_bytes: bytes,
    timeout: float,
) -> dict[str, Any]:
    response = requests.post(
        url,
        data={
            "cameraCode": camera_code,
            "capturedAt": captured_at,
            "frameNumber": str(frame_number),
        },
        files={
            "highResCrop": (
                "best-frame-highres-crop.jpg",
                high_res_crop_bytes,
                "image/jpeg",
            ),
        },
        timeout=timeout,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        body = response.text[:500]
        raise RuntimeError(
            f"high-res OCR request failed: status={response.status_code}, body={body}"
        ) from exc

    return response.json()


def check_stream_endpoint(base_url: str, timeout: float) -> None:
    openapi_url = f"{base_url.rstrip('/')}/openapi.json"

    try:
        response = requests.get(openapi_url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"FastAPI is not reachable at {openapi_url}: {exc}"
        ) from exc

    paths = response.json().get("paths", {})

    if STREAM_FRAME_PATH not in paths:
        raise RuntimeError(
            f"{STREAM_FRAME_PATH} is not registered on the running FastAPI server. "
            "Restart FastAPI or rebuild/recreate the Docker container before streaming video."
        )


def make_blank_frame_bytes(width: int, height: int, jpeg_quality: int) -> bytes:
    blank_frame = np.zeros((height, width, 3), dtype=np.uint8)
    success, buffer = cv2.imencode(
        ".jpg",
        blank_frame,
        [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality],
    )

    if not success:
        raise RuntimeError("failed to encode blank flush frame")

    return buffer.tobytes()


def encode_upload_frame(
    frame,
    *,
    upload_scale: float,
    jpeg_quality: int,
) -> bytes | None:
    upload_frame = frame

    if upload_scale != 1.0:
        upload_frame = cv2.resize(
            frame,
            None,
            fx=upload_scale,
            fy=upload_scale,
            interpolation=cv2.INTER_AREA,
        )

    success, buffer = cv2.imencode(
        ".jpg",
        upload_frame,
        [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality],
    )

    if not success:
        return None

    return buffer.tobytes()


def resize_for_upload(frame, *, upload_scale: float):
    if upload_scale == 1.0:
        return frame.copy()

    return cv2.resize(
        frame,
        None,
        fx=upload_scale,
        fy=upload_scale,
        interpolation=cv2.INTER_AREA,
    )


def draw_text(
    frame,
    text: str,
    origin: tuple[int, int],
    color=(255, 255, 255),
    font_scale: float = 0.45,
) -> None:
    x, y = origin
    shadow_thickness = max(1, round(font_scale * 3))
    cv2.putText(
        frame,
        text,
        (x + 1, y + 1),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 0, 0),
        shadow_thickness,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        1,
        cv2.LINE_AA,
    )


def has_speed_violation(response_body: dict[str, Any] | None) -> bool:
    if not isinstance(response_body, dict):
        return False

    speed_violation = response_body.get("speedViolation")
    if isinstance(speed_violation, dict):
        return bool(speed_violation.get("isViolation", True))

    speed_measurements = response_body.get("speedMeasurements") or []
    if isinstance(speed_measurements, list):
        return any(
            isinstance(measurement, dict)
            and bool(measurement.get("isViolation", False))
            for measurement in speed_measurements
        )

    return False


def parse_speed_overlay_config(
    raw_value: str | None,
    *,
    camera_code: str,
) -> SpeedOverlayConfig | None:
    config_source = raw_value or os.getenv("SPEED_CAMERA_CONFIGS_JSON")
    if not config_source:
        return None

    config_source = read_speed_config_source(config_source)

    raw_configs = json.loads(config_source)
    if not isinstance(raw_configs, list):
        raise ValueError("speed overlay config must be a JSON array")

    raw_config = next(
        (
            item
            for item in raw_configs
            if isinstance(item, dict) and item.get("cameraCode") == camera_code
        ),
        None,
    )
    if raw_config is None:
        return None

    homography = raw_config.get("homography") or {}
    return SpeedOverlayConfig(
        roi=parse_preview_points(raw_config.get("roi") or []),
        line_a=parse_preview_line(raw_config.get("lineA")),
        line_b=parse_preview_line(raw_config.get("lineB")),
        homography_points=parse_preview_points(homography.get("imagePoints") or []),
        speed_mode=str(raw_config.get("speedMode", "TRACK_DELTA")).upper(),
    )


def read_speed_config_source(config_source: str) -> str:
    source_text = config_source.strip()
    source_path = Path(config_source)
    if not source_text.startswith("[") and source_path.exists():
        return source_path.read_text(encoding="utf-8")
    return config_source


def parse_preview_line(raw_line: Any) -> tuple[int, int, int, int] | None:
    if raw_line is None:
        return None
    values = [int(value) for value in raw_line]
    if len(values) != 4:
        raise ValueError("preview line must contain four integers")
    return (values[0], values[1], values[2], values[3])


def parse_preview_points(raw_points: Any) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    for raw_point in raw_points:
        values = [int(value) for value in raw_point]
        if len(values) != 2:
            raise ValueError("preview point must contain two integers")
        points.append((values[0], values[1]))
    return points


def build_speed_zone_config(
    *,
    camera_code: str,
    roi_points: list[tuple[int, int]],
    line_a_points: list[tuple[int, int]],
    line_b_points: list[tuple[int, int]],
    distance_meters: float,
    speed_limit_kmh: float,
    roi_width_meters: float,
    roi_height_meters: float,
) -> list[dict[str, Any]]:
    if len(roi_points) != 4:
        raise ValueError("ROI must contain exactly four clicked points")
    if len(line_a_points) != 2:
        raise ValueError("Line A must contain exactly two clicked points")
    if len(line_b_points) != 2:
        raise ValueError("Line B must contain exactly two clicked points")
    if distance_meters <= 0:
        raise ValueError("--distance-meters must be greater than 0")
    if speed_limit_kmh <= 0:
        raise ValueError("--speed-limit-kmh must be greater than 0")
    if roi_width_meters <= 0 or roi_height_meters <= 0:
        raise ValueError("--roi-width-meters and --roi-height-meters must be greater than 0")

    return [
        {
            "cameraCode": camera_code,
            "speedMode": "TRACK_DELTA",
            "lineA": flatten_line_points(line_a_points),
            "lineB": flatten_line_points(line_b_points),
            "roi": [[x, y] for x, y in roi_points],
            "distanceMeters": distance_meters,
            "speedLimitKmh": speed_limit_kmh,
            "enabled": True,
            "homography": {
                "imagePoints": [[x, y] for x, y in roi_points],
                "worldPointsMeters": [
                    [0, 0],
                    [roi_width_meters, 0],
                    [roi_width_meters, roi_height_meters],
                    [0, roi_height_meters],
                ],
            },
        }
    ]


def build_full_frame_speed_zone_config(
    *,
    camera_code: str,
    frame_width: int,
    frame_height: int,
    distance_meters: float,
    speed_limit_kmh: float,
    roi_width_meters: float,
    roi_height_meters: float,
) -> list[dict[str, Any]]:
    right = max(1, frame_width - 1)
    bottom = max(1, frame_height - 1)
    return build_speed_zone_config(
        camera_code=camera_code,
        roi_points=[
            (0, 0),
            (right, 0),
            (right, bottom),
            (0, bottom),
        ],
        line_a_points=[(0, 0), (right, 0)],
        line_b_points=[(0, bottom), (right, bottom)],
        distance_meters=distance_meters,
        speed_limit_kmh=speed_limit_kmh,
        roi_width_meters=roi_width_meters,
        roi_height_meters=roi_height_meters,
    )


def flatten_line_points(points: list[tuple[int, int]]) -> list[int]:
    first, second = points
    return [first[0], first[1], second[0], second[1]]


def split_clicked_speed_zone_points(
    points: list[tuple[int, int]],
) -> tuple[list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]]]:
    if len(points) == 4:
        return points, [points[0], points[1]], [points[3], points[2]]
    if len(points) == 8:
        return points[:4], points[4:6], points[6:8]
    raise ValueError("speed zone selection requires 4 ROI points")


def scale_point(
    point: tuple[int, int],
    *,
    response_coord_scale: float,
    coord_scale: float,
) -> tuple[int, int]:
    return (
        int(round(point[0] * response_coord_scale * coord_scale)),
        int(round(point[1] * response_coord_scale * coord_scale)),
    )


def draw_speed_overlay(
    frame,
    overlay: SpeedOverlayConfig,
    *,
    response_coord_scale: float,
    coord_scale: float,
    font_scale: float,
) -> None:
    overlay_thickness = 1
    if overlay.roi:
        roi_points = np.array(
            [
                scale_point(
                    point,
                    response_coord_scale=response_coord_scale,
                    coord_scale=coord_scale,
                )
                for point in overlay.roi
            ],
            dtype=np.int32,
        )
        cv2.polylines(
            frame,
            [roi_points],
            isClosed=True,
            color=(0, 255, 0),
            thickness=overlay_thickness,
        )
        draw_text(frame, "ROI", tuple(roi_points[0]), (0, 255, 0), font_scale)

    if overlay.line_a is not None and overlay.speed_mode != "TRACK_DELTA":
        x1, y1, x2, y2 = overlay.line_a
        start = scale_point((x1, y1), response_coord_scale=response_coord_scale, coord_scale=coord_scale)
        end = scale_point((x2, y2), response_coord_scale=response_coord_scale, coord_scale=coord_scale)
        cv2.line(frame, start, end, (255, 255, 255), overlay_thickness)
        draw_text(frame, "Line A", (start[0], max(18, start[1] - 8)), (255, 255, 255), font_scale)

    if overlay.line_b is not None and overlay.speed_mode != "TRACK_DELTA":
        x1, y1, x2, y2 = overlay.line_b
        start = scale_point((x1, y1), response_coord_scale=response_coord_scale, coord_scale=coord_scale)
        end = scale_point((x2, y2), response_coord_scale=response_coord_scale, coord_scale=coord_scale)
        cv2.line(frame, start, end, (255, 255, 255), overlay_thickness)
        draw_text(frame, "Line B", (start[0], max(18, start[1] - 8)), (255, 255, 255), font_scale)

    for index, point in enumerate(overlay.homography_points, start=1):
        center = scale_point(point, response_coord_scale=response_coord_scale, coord_scale=coord_scale)
        cv2.circle(frame, center, 3, (0, 255, 0), 1)
        draw_text(
            frame,
            f"H{index}",
            (center[0] + 7, center[1] - 7),
            (0, 255, 0),
            font_scale,
        )


def draw_speed_zone_selection(
    frame,
    points: list[tuple[int, int]],
) -> Any:
    display = frame.copy()
    overlay = SpeedOverlayConfig(
        roi=points[:4],
        homography_points=points[:4],
    )
    draw_speed_overlay(
        display,
        overlay,
        response_coord_scale=1.0,
        coord_scale=1.0,
        font_scale=0.5,
    )

    for index, point in enumerate(points, start=1):
        cv2.circle(display, point, 5, (255, 255, 255), -1)
        draw_text(display, str(index), (point[0] + 8, point[1] + 18), (255, 255, 255), 0.5)

    next_label = next_speed_zone_point_label(len(points))
    draw_text(
        display,
        f"Click {next_label} | u: undo  r: reset  Enter: start  ESC/q: cancel",
        (12, 28),
        (255, 255, 255),
        0.55,
    )
    draw_text(
        display,
        "ROI order: top-left, top-right, bottom-right, bottom-left",
        (12, 56),
        (255, 255, 255),
        0.50,
    )
    return display


def next_speed_zone_point_label(count: int) -> str:
    labels = (
        "ROI 1/4",
        "ROI 2/4",
        "ROI 3/4",
        "ROI 4/4",
    )
    if count == 0:
        return "ROI 1/4 or Enter for full frame"
    if count >= len(labels):
        return "Enter to start"
    return labels[count]


def on_speed_zone_mouse(event, x, y, _flags, userdata) -> None:
    state: SpeedZoneSelectionState = userdata
    if event == cv2.EVENT_LBUTTONDOWN and len(state.points) < 4:
        state.points.append((int(x), int(y)))


def configure_speed_zone_from_video(args: argparse.Namespace, video_path: Path) -> str:
    if args.roi_width_meters <= 0 or args.roi_height_meters <= 0:
        raise SystemExit("--roi-width-meters and --roi-height-meters must be greater than 0")
    if args.distance_meters <= 0:
        raise SystemExit("--distance-meters must be greater than 0")
    if args.speed_limit_kmh <= 0:
        raise SystemExit("--speed-limit-kmh must be greater than 0")

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise SystemExit(f"failed to open video file: {video_path}")

    try:
        ok, frame = capture.read()
    finally:
        capture.release()

    if not ok:
        raise SystemExit(f"failed to read the first frame: {video_path}")

    upload_frame = resize_for_upload(frame, upload_scale=args.upload_scale)
    state = SpeedZoneSelectionState()
    cv2.namedWindow(SPEED_ZONE_WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(SPEED_ZONE_WINDOW_NAME, on_speed_zone_mouse, state)

    while True:
        cv2.imshow(SPEED_ZONE_WINDOW_NAME, draw_speed_zone_selection(upload_frame, state.points))
        key = cv2.waitKey(30) & 0xFF

        if key in {27, ord("q")}:
            cv2.destroyWindow(SPEED_ZONE_WINDOW_NAME)
            raise SystemExit("speed zone configuration cancelled")
        if key == ord("u") and state.points:
            state.points.pop()
        if key == ord("r"):
            state.points.clear()
        if key in {10, 13}:
            if not state.points:
                config = build_full_frame_speed_zone_config(
                    camera_code=args.camera_code,
                    frame_width=upload_frame.shape[1],
                    frame_height=upload_frame.shape[0],
                    distance_meters=args.distance_meters,
                    speed_limit_kmh=args.speed_limit_kmh,
                    roi_width_meters=args.roi_width_meters,
                    roi_height_meters=args.roi_height_meters,
                )
                break
            if len(state.points) != 4:
                print(
                    "need 4 ROI points before starting, or reset and press Enter "
                    f"for full frame; current={len(state.points)}"
                )
                continue
            roi_points = state.points
            config = build_speed_zone_config(
                camera_code=args.camera_code,
                roi_points=roi_points,
                line_a_points=[roi_points[0], roi_points[1]],
                line_b_points=[roi_points[3], roi_points[2]],
                distance_meters=args.distance_meters,
                speed_limit_kmh=args.speed_limit_kmh,
                roi_width_meters=args.roi_width_meters,
                roi_height_meters=args.roi_height_meters,
            )
            break

    config_json = json.dumps(config, ensure_ascii=False)
    if args.save_speed_config_json:
        output_path = Path(args.save_speed_config_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"savedSpeedConfig={output_path}")

    cv2.destroyWindow(SPEED_ZONE_WINDOW_NAME)
    print("speedConfigMode=full_frame_default" if not state.points else "speedConfigMode=clicked")
    print(config_json)
    return config_json


def draw_preview(
    *,
    frame,
    frame_number: int,
    response_body: dict[str, Any] | None,
    scale: float,
    wait_ms: int,
    tracker_bbox: tuple[int, int, int, int] | None = None,
    tracker_confidence: float = 0.0,
    response_coord_scale: float = 1.0,
    speed_overlay: SpeedOverlayConfig | None = None,
    max_event_age_seconds: float = 0.0,
    max_bbox_area_ratio: float = 0.0,
    min_bbox_confidence: float = 0.0,
    primary_bbox_only: bool = True,
) -> int:
    if scale != 1.0:
        display_frame = cv2.resize(
            frame,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA,
        )
        coord_scale = scale
    else:
        display_frame = frame.copy()
        coord_scale = 1.0

    overlay_font_scale = min(0.50, max(0.30, display_frame.shape[0] / 1080 * 0.55))
    overlay_line_height = max(18, round(overlay_font_scale * 52))
    response = response_body if isinstance(response_body, dict) else {}
    bbox = response.get("bbox")
    bboxes = response.get("bboxes") or []
    bbox_confidence = response.get("bboxConfidenceScore", 0.0)
    event_age_seconds = response.get("eventAgeSeconds", 0.0)
    speed_violation_active = has_speed_violation(response)
    bbox_color = (0, 0, 255) if speed_violation_active else (0, 255, 0)
    bbox_label_prefix = "OVERSPEED" if speed_violation_active else "VEHICLE"

    if primary_bbox_only and tracker_bbox is None:
        primary_bbox = bbox if bbox is not None else (bboxes[0] if bboxes else None)
        bbox = primary_bbox
        bboxes = [primary_bbox] if primary_bbox is not None else []

    if speed_overlay is not None:
        draw_speed_overlay(
            display_frame,
            speed_overlay,
            response_coord_scale=response_coord_scale,
            coord_scale=coord_scale,
            font_scale=overlay_font_scale,
        )

    if tracker_bbox is not None:
        bboxes = [list(tracker_bbox)]
        bbox = list(tracker_bbox)
        bbox_confidence = tracker_confidence

    if (
        max_event_age_seconds > 0
        and isinstance(event_age_seconds, (int, float))
        and event_age_seconds > max_event_age_seconds
    ):
        bboxes = []
        bbox = None

    if (
        min_bbox_confidence > 0
        and isinstance(bbox_confidence, (int, float))
        and bbox_confidence < min_bbox_confidence
    ):
        bboxes = []
        bbox = None

    bbox_response_coord_scale = 1.0 if tracker_bbox is not None else response_coord_scale
    display_area = max(display_frame.shape[0] * display_frame.shape[1], 1)

    for index, current_bbox in enumerate(bboxes):
        x1, y1, x2, y2 = [
            int(round(float(value) * bbox_response_coord_scale * coord_scale))
            for value in current_bbox
        ]
        bbox_area_ratio = (max(0, x2 - x1) * max(0, y2 - y1)) / display_area
        if max_bbox_area_ratio > 0 and bbox_area_ratio > max_bbox_area_ratio:
            continue

        color = bbox_color
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        label = (
            f"{'OVERSPEED ' if speed_violation_active else ''}TRACK {index + 1}"
            if tracker_bbox is not None
            else f"{bbox_label_prefix} {index + 1}"
        )

        if index == 0:
            label = f"{label} {bbox_confidence:.3f}"

        draw_text(
            display_frame,
            label,
            (x1, max(overlay_line_height, y1 - 8)),
            color,
            overlay_font_scale,
        )

    if not bboxes and bbox is not None:
        x1, y1, x2, y2 = [
            int(round(float(value) * response_coord_scale * coord_scale))
            for value in bbox
        ]
        bbox_area_ratio = (max(0, x2 - x1) * max(0, y2 - y1)) / display_area
        if max_bbox_area_ratio > 0 and bbox_area_ratio > max_bbox_area_ratio:
            bbox = None

    if not bboxes and bbox is not None:
        x1, y1, x2, y2 = [
            int(round(float(value) * response_coord_scale * coord_scale))
            for value in bbox
        ]
        color = bbox_color
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        draw_text(
            display_frame,
            f"{bbox_label_prefix} {bbox_confidence:.3f}",
            (x1, max(overlay_line_height, y1 - 8)),
            color,
            overlay_font_scale,
        )

    header = (
        f"frame={frame_number} "
        f"boxes={len(bboxes)} "
        f"bboxConf={bbox_confidence:.3f} "
        f"eventAge={event_age_seconds:.1f}s"
    )
    draw_text(display_frame, header, (12, overlay_line_height), font_scale=overlay_font_scale)

    if response:
        data = response.get("data") or {}
        status_text = (
            f"stream={response.get('streamStatus')} "
            f"analysis={response.get('analysisStatus') or '-'} "
            f"plate={data.get('plateNumber') or '-'}"
        )
        if speed_violation_active:
            speed_violation = response.get("speedViolation") or {}
            measured_speed = speed_violation.get("measuredSpeed")
            if isinstance(measured_speed, (int, float)):
                status_text += f" OVERSPEED={measured_speed:.1f}km/h"
            else:
                status_text += " OVERSPEED"
        draw_text(
            display_frame,
            status_text,
            (12, overlay_line_height * 2),
            (0, 0, 255) if speed_violation_active else (0, 255, 255),
            overlay_font_scale,
        )

    draw_text(
        display_frame,
        "q/ESC: quit  space: pause",
        (12, display_frame.shape[0] - 12),
        font_scale=overlay_font_scale,
    )

    cv2.imshow(WINDOW_NAME, display_frame)
    return cv2.waitKey(wait_ms) & 0xFF


def handle_preview_key(key: int) -> tuple[bool, bool]:
    if key in {27, ord("q")}:
        return True, False

    if key == ord(" "):
        return False, True

    return False, False


def configure_preview_window(width: int, height: int) -> None:
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, width, height)


def get_latest_response_body(upload_state: UploadState) -> dict[str, Any] | None:
    with upload_state.lock:
        return upload_state.latest_response_body


def get_latest_response_packet(
    upload_state: UploadState,
) -> tuple[int | None, dict[str, Any] | None]:
    with upload_state.lock:
        return (
            upload_state.latest_response_frame_number,
            upload_state.latest_response_body,
        )


def get_response_for_frame(
    upload_state: UploadState,
    frame_number: int,
    *,
    allow_latest_fallback: bool = True,
) -> dict[str, Any] | None:
    with upload_state.lock:
        response_body = upload_state.responses_by_frame.get(frame_number)

        if response_body is not None:
            return response_body

        if allow_latest_fallback:
            return upload_state.latest_response_body

        return None


def get_response_at_or_before_frame(
    upload_state: UploadState,
    frame_number: int,
) -> tuple[int | None, dict[str, Any] | None]:
    with upload_state.lock:
        eligible_frame_numbers = [
            response_frame_number
            for response_frame_number in upload_state.responses_by_frame
            if response_frame_number <= frame_number
        ]

        if not eligible_frame_numbers:
            return None, None

        response_frame_number = max(eligible_frame_numbers)
        return response_frame_number, upload_state.responses_by_frame[response_frame_number]


def create_cv_tracker():
    tracker_factories = [
        ("TrackerKCF_create", cv2),
        ("TrackerMOSSE_create", cv2),
        ("TrackerMIL_create", cv2),
        ("TrackerCSRT_create", cv2),
    ]

    legacy = getattr(cv2, "legacy", None)
    if legacy is not None:
        tracker_factories.extend(
            [
                ("TrackerKCF_create", legacy),
                ("TrackerMOSSE_create", legacy),
                ("TrackerMIL_create", legacy),
                ("TrackerCSRT_create", legacy),
            ]
        )

    for factory_name, module in tracker_factories:
        factory = getattr(module, factory_name, None)

        if factory is not None:
            return factory()

    return None


def select_response_bbox(
    response_body: dict[str, Any] | None,
    *,
    response_coord_scale: float = 1.0,
    min_confidence: float = 0.0,
) -> tuple[tuple[int, int, int, int] | None, float]:
    if not isinstance(response_body, dict):
        return None, 0.0

    confidence_score = float(response_body.get("bboxConfidenceScore", 0.0))
    if min_confidence > 0 and confidence_score < min_confidence:
        return None, confidence_score

    bboxes = response_body.get("bboxes") or []
    bbox = bboxes[0] if bboxes else response_body.get("bbox")

    if bbox is None:
        return None, 0.0

    x1, y1, x2, y2 = [
        int(round(float(value) * response_coord_scale))
        for value in bbox
    ]
    return (x1, y1, x2, y2), confidence_score


def encode_highres_crop_from_bbox(
    frame,
    *,
    bbox: tuple[int, int, int, int],
    padding_ratio: float,
    jpeg_quality: int,
) -> bytes | None:
    height, width = frame.shape[:2]
    x1, y1, x2, y2 = bbox
    bbox_w = max(1, x2 - x1)
    bbox_h = max(1, y2 - y1)
    side = round(max(bbox_w, bbox_h) * (1 + (padding_ratio * 2)))
    side = max(1, min(side, width, height))

    center_x = x1 + (bbox_w / 2)
    center_y = y1 + (bbox_h / 2)
    left = round(center_x - (side / 2))
    top = round(center_y - (side / 2))
    left = min(max(0, left), max(0, width - side))
    top = min(max(0, top), max(0, height - side))
    right = left + side
    bottom = top + side

    if right <= left or bottom <= top:
        return None

    crop = frame[top:bottom, left:right]
    success, buffer = cv2.imencode(
        ".jpg",
        crop,
        [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality],
    )

    if not success:
        return None

    return buffer.tobytes()


def encode_highres_crop_from_video(
    *,
    video_path: Path,
    frame_number: int,
    bbox: tuple[int, int, int, int],
    padding_ratio: float,
    jpeg_quality: int,
) -> bytes | None:
    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            return None

        capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, frame_number - 1))
        ok, frame = capture.read()

        if not ok:
            return None

        return encode_highres_crop_from_bbox(
            frame,
            bbox=bbox,
            padding_ratio=padding_ratio,
            jpeg_quality=jpeg_quality,
        )
    finally:
        capture.release()


def build_finalized_highres_crop(
    *,
    video_path: Path,
    response_body: dict[str, Any],
    response_coord_scale: float,
    padding_ratio: float,
    jpeg_quality: int,
) -> tuple[bytes | None, int | None, str | None]:
    frame_number = response_body.get("bestCandidateFrameNumber")
    bbox = response_body.get("bestCandidateBbox")
    captured_at = response_body.get("bestCandidateCapturedAt")

    if not isinstance(frame_number, int) or bbox is None or captured_at is None:
        return None, None, None

    original_bbox = tuple(
        int(round(float(value) * response_coord_scale))
        for value in bbox
    )

    crop_bytes = encode_highres_crop_from_video(
        video_path=video_path,
        frame_number=frame_number,
        bbox=original_bbox,
        padding_ratio=padding_ratio,
        jpeg_quality=jpeg_quality,
    )

    return crop_bytes, frame_number, str(captured_at)


def should_run_finalized_highres_ocr(response_body: dict[str, Any] | None) -> bool:
    if not isinstance(response_body, dict):
        return False

    return (
        response_body.get("streamStatus") == "FINALIZED"
        and isinstance(response_body.get("bestCandidateFrameNumber"), int)
        and response_body.get("bestCandidateBbox") is not None
        and response_body.get("bestCandidateCapturedAt") is not None
    )


def summarize_highres_response(
    frame_number: int,
    response_body: dict[str, Any],
) -> str:
    data = response_body.get("data") or {}
    return (
        f"highresFrame={frame_number} "
        f"analysisStatus={response_body.get('analysisStatus') or '-'} "
        f"plateNumber={data.get('plateNumber') or '-'} "
        f"detectionType={data.get('detectionType') or '-'}"
    )


def build_highres_crop_for_upload(
    *,
    enabled: bool,
    use_async_upload: bool,
    upload_state: UploadState,
    source_frame_history: deque[tuple[int, Any]],
    latest_response_frame_number: int | None,
    latest_response_body: dict[str, Any] | None,
    response_coord_scale: float,
    padding_ratio: float,
    jpeg_quality: int,
) -> tuple[bytes | None, int | None]:
    if not enabled:
        return None, None

    if use_async_upload:
        response_frame_number, response_body = get_latest_response_packet(upload_state)
    else:
        response_frame_number = latest_response_frame_number
        response_body = latest_response_body

    if response_frame_number is None:
        return None, None

    bbox, _ = select_response_bbox(
        response_body,
        response_coord_scale=response_coord_scale,
    )

    if bbox is None:
        return None, None

    source_frame = find_frame_by_number(
        source_frame_history,
        response_frame_number,
    )
    if source_frame is None:
        return None, None

    high_res_crop_bytes = encode_highres_crop_from_bbox(
        source_frame,
        bbox=bbox,
        padding_ratio=padding_ratio,
        jpeg_quality=jpeg_quality,
    )

    return high_res_crop_bytes, response_frame_number


def find_frame_by_number(
    frame_history: deque[tuple[int, Any]],
    frame_number: int,
):
    for current_frame_number, frame in reversed(frame_history):
        if current_frame_number == frame_number:
            return frame

    return None


def xyxy_to_xywh(bbox: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = bbox
    return (x1, y1, max(1, x2 - x1), max(1, y2 - y1))


def xywh_to_xyxy(bbox) -> tuple[int, int, int, int]:
    x, y, w, h = bbox
    return (
        int(round(x)),
        int(round(y)),
        int(round(x + w)),
        int(round(y + h)),
    )


def rebuild_tracker_from_response(
    *,
    response_frame_number: int,
    response_body: dict[str, Any] | None,
    frame_history: deque[tuple[int, Any]],
    response_coord_scale: float,
    min_bbox_confidence: float = 0.0,
) -> PreviewTracker | None:
    bbox, confidence_score = select_response_bbox(
        response_body,
        response_coord_scale=response_coord_scale,
        min_confidence=min_bbox_confidence,
    )

    if bbox is None:
        return None

    tracker = create_cv_tracker()

    if tracker is None:
        return None

    history = list(frame_history)
    start_index = next(
        (
            index
            for index, (frame_number, _frame) in enumerate(history)
            if frame_number == response_frame_number
        ),
        len(history) - 1,
    )
    start_frame_number, start_frame = history[start_index]
    tracker.init(start_frame, xyxy_to_xywh(bbox))
    current_bbox = bbox
    current_frame_number = start_frame_number

    for frame_number, frame in history[start_index + 1:]:
        ok, tracked_bbox = tracker.update(frame)

        if not ok:
            break

        current_bbox = xywh_to_xyxy(tracked_bbox)
        current_frame_number = frame_number

    return PreviewTracker(
        tracker=tracker,
        bbox_xyxy=current_bbox,
        response_frame_number=response_frame_number,
        last_frame_number=current_frame_number,
        confidence_score=confidence_score,
    )


def update_preview_tracker(
    tracker_state: PreviewTracker | None,
    *,
    frame_number: int,
    frame,
) -> PreviewTracker | None:
    if tracker_state is None:
        return None

    if frame_number <= tracker_state.last_frame_number:
        return tracker_state

    ok, tracked_bbox = tracker_state.tracker.update(frame)

    if not ok:
        return None

    tracker_state.bbox_xyxy = xywh_to_xyxy(tracked_bbox)
    tracker_state.last_frame_number = frame_number
    return tracker_state


def enqueue_upload_task(
    upload_queue: queue.Queue[UploadTask],
    upload_state: UploadState,
    task: UploadTask,
) -> None:
    try:
        upload_queue.put_nowait(task)
        return
    except queue.Full:
        pass

    try:
        upload_queue.get_nowait()
        upload_queue.task_done()
        with upload_state.lock:
            upload_state.dropped_count += 1
    except queue.Empty:
        pass

    upload_queue.put_nowait(task)


def upload_worker(
    *,
    upload_queue: queue.Queue[UploadTask],
    stop_event: threading.Event,
    upload_state: UploadState,
    url: str,
    highres_ocr_url: str,
    video_path: Path,
    camera_code: str,
    timeout: float,
    stop_after_finalized: int,
    highres_ocr_enabled: bool,
    response_coord_scale: float,
    highres_crop_padding: float,
    highres_jpeg_quality: int,
    speed_config_json: str | None = None,
) -> None:
    while True:
        if stop_event.is_set() and upload_queue.empty():
            break

        try:
            task = upload_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        try:
            response_body = post_frame(
                url=url,
                camera_code=camera_code,
                captured_at=task.captured_at,
                frame_number=task.frame_number,
                frame_bytes=task.frame_bytes,
                timeout=timeout,
                speed_config_json=speed_config_json,
                high_res_crop_bytes=task.high_res_crop_bytes,
                high_res_crop_frame_number=task.high_res_crop_frame_number,
            )

            if highres_ocr_enabled and should_run_finalized_highres_ocr(response_body):
                (
                    crop_bytes,
                    best_frame_number,
                    best_captured_at,
                ) = build_finalized_highres_crop(
                    video_path=video_path,
                    response_body=response_body,
                    response_coord_scale=response_coord_scale,
                    padding_ratio=highres_crop_padding,
                    jpeg_quality=highres_jpeg_quality,
                )
                if (
                    crop_bytes is None
                    or best_frame_number is None
                    or best_captured_at is None
                ):
                    raise RuntimeError(
                        "failed to capture original best frame for high-res OCR"
                    )

                highres_response_body = post_highres_ocr(
                    url=highres_ocr_url,
                    camera_code=camera_code,
                    captured_at=best_captured_at,
                    frame_number=best_frame_number,
                    high_res_crop_bytes=crop_bytes,
                    timeout=timeout,
                )
                print(
                    summarize_highres_response(
                        best_frame_number,
                        highres_response_body,
                    )
                )

            with upload_state.lock:
                upload_state.latest_response_body = response_body
                upload_state.latest_response_frame_number = task.frame_number
                upload_state.responses_by_frame[task.frame_number] = response_body

                for old_frame_number in list(upload_state.responses_by_frame):
                    if old_frame_number < task.frame_number - 300:
                        del upload_state.responses_by_frame[old_frame_number]

                upload_state.uploaded_count += 1

                if response_body.get("streamStatus") == "FINALIZED":
                    upload_state.finalized_count += 1

                    if (
                        stop_after_finalized
                        and upload_state.finalized_count >= stop_after_finalized
                    ):
                        upload_state.stopped_by_finalized_limit = True
                        stop_event.set()

            print(summarize_response(task.frame_number, response_body))
        except Exception as exc:
            with upload_state.lock:
                upload_state.error = f"{type(exc).__name__}: {exc}"
            stop_event.set()
        finally:
            upload_queue.task_done()

def main() -> None:
    args = build_parser().parse_args()
    video_path = Path(args.video)

    if not video_path.exists():
        raise SystemExit(f"video file does not exist: {video_path}")

    if args.fps <= 0:
        raise SystemExit("--fps must be greater than 0")

    if args.video_speed_ratio <= 0:
        raise SystemExit("--video-speed-ratio must be greater than 0")

    if args.scale <= 0:
        raise SystemExit("--scale must be greater than 0")

    if args.upload_scale <= 0:
        raise SystemExit("--upload-scale must be greater than 0")

    if args.highres_crop_padding < 0:
        raise SystemExit("--highres-crop-padding must be greater than or equal to 0")

    if args.highres_jpeg_quality < 1 or args.highres_jpeg_quality > 100:
        raise SystemExit("--highres-jpeg-quality must be between 1 and 100")

    if args.window_width <= 0 or args.window_height <= 0:
        raise SystemExit("--window-width and --window-height must be greater than 0")

    if args.upload_queue_size <= 0:
        raise SystemExit("--upload-queue-size must be greater than 0")

    if args.preview_delay_seconds < 0:
        raise SystemExit("--preview-delay-seconds must be greater than or equal to 0")

    if args.preview_fps < 0:
        raise SystemExit("--preview-fps must be greater than or equal to 0")

    if args.bbox_hold_seconds < 0:
        raise SystemExit("--bbox-hold-seconds must be greater than or equal to 0")

    if args.preview_max_event_age_seconds < 0:
        raise SystemExit(
            "--preview-max-event-age-seconds must be greater than or equal to 0"
        )

    if args.preview_max_bbox_area_ratio < 0:
        raise SystemExit(
            "--preview-max-bbox-area-ratio must be greater than or equal to 0"
        )

    if args.preview_min_bbox_confidence < 0 or args.preview_min_bbox_confidence > 1:
        raise SystemExit(
            "--preview-min-bbox-confidence must be between 0 and 1"
        )

    if args.preview_max_response_lag_seconds < 0:
        raise SystemExit(
            "--preview-max-response-lag-seconds must be greater than or equal to 0"
        )

    speed_config_json: str | None = None
    if args.configure_speed_zone:
        speed_config_json = configure_speed_zone_from_video(args, video_path)
        speed_overlay = parse_speed_overlay_config(
            speed_config_json,
            camera_code=args.camera_code,
        )
    else:
        try:
            speed_overlay = parse_speed_overlay_config(
                args.speed_config_json,
                camera_code=args.camera_code,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise SystemExit(f"invalid --speed-config-json: {exc}") from exc

        speed_config_json = (
            read_speed_config_source(args.speed_config_json)
            if args.speed_config_json
            else None
        )

    if args.preview_bbox:
        configure_preview_window(args.window_width, args.window_height)

    base_url = args.fastapi_base_url.rstrip("/")
    check_stream_endpoint(base_url, args.timeout)
    url = f"{base_url}{STREAM_FRAME_PATH}"
    highres_ocr_url = f"{base_url}{HIGHRES_OCR_PATH}"
    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        raise SystemExit(f"failed to open video file: {video_path}")

    source_fps = capture.get(cv2.CAP_PROP_FPS) or args.fps
    frame_step = max(1, round(source_fps / args.fps))
    preview_frame_step = (
        1
        if args.preview_fps == 0
        else max(1, round(source_fps / args.preview_fps))
    )
    preview_delay_frames = (
        round(source_fps * args.preview_delay_seconds)
        if args.preview_bbox
        else 0
    )
    preview_wait_ms = max(1, round(1000 / source_fps))
    response_coord_scale = 1.0 / args.upload_scale
    use_async_upload = args.preview_bbox and args.async_upload
    effective_preview_all_frames = (
        args.preview_all_frames
        or (args.preview_bbox and not use_async_upload)
    )
    use_preview_tracker = use_async_upload and args.preview_tracker
    uploaded_count = 0
    finalized_count = 0
    read_count = 0
    base_time = datetime.now()
    video_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    video_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    stopped_early = False
    latest_response_body: dict[str, Any] | None = None
    latest_response_frame_number: int | None = None
    upload_state = UploadState()
    upload_queue: queue.Queue[UploadTask] | None = None
    source_frame_history: deque[tuple[int, Any]] = deque(
        maxlen=max(30, round(source_fps * 12))
    )
    frame_history: deque[tuple[int, Any]] = deque(maxlen=max(30, round(source_fps * 6)))
    preview_buffer: deque[PreviewFrame] = deque(
        maxlen=max(30, preview_delay_frames + round(source_fps * 2))
    )
    active_tracker: PreviewTracker | None = None
    active_overlay: PreviewOverlay | None = None
    consumed_response_frame_number: int | None = None
    stop_event = threading.Event()
    worker_thread: threading.Thread | None = None

    if use_async_upload:
        upload_queue = queue.Queue(maxsize=args.upload_queue_size)
        worker_thread = threading.Thread(
            target=upload_worker,
            kwargs={
                "upload_queue": upload_queue,
                "stop_event": stop_event,
                "upload_state": upload_state,
                "url": url,
                "highres_ocr_url": highres_ocr_url,
                "video_path": video_path,
                "camera_code": args.camera_code,
                "timeout": args.timeout,
                "stop_after_finalized": args.stop_after_finalized,
                "highres_ocr_enabled": args.finalized_highres_ocr,
                "response_coord_scale": response_coord_scale,
                "highres_crop_padding": args.highres_crop_padding,
                "highres_jpeg_quality": args.highres_jpeg_quality,
                "speed_config_json": speed_config_json,
            },
            daemon=True,
        )
        worker_thread.start()

    print(
        json.dumps(
            {
                "video": str(video_path),
                "url": url,
                "cameraCode": args.camera_code,
                "sourceFps": source_fps,
                "targetFps": args.fps,
                "videoSpeedRatio": args.video_speed_ratio,
                "frameStep": frame_step,
                "stopAfterFinalized": args.stop_after_finalized,
                "flushFrames": args.flush_frames,
                "previewBbox": args.preview_bbox,
                "previewAllFrames": effective_preview_all_frames,
                "previewFps": args.preview_fps,
                "previewFrameStep": preview_frame_step,
                "previewTracker": use_preview_tracker,
                "bboxHoldSeconds": args.bbox_hold_seconds,
                "displayScale": args.scale,
                "uploadScale": args.upload_scale,
                "highresOcrCrop": args.highres_ocr_crop,
                "finalizedHighresOcr": args.finalized_highres_ocr,
                "highresCropPadding": args.highres_crop_padding,
                "highresJpegQuality": args.highres_jpeg_quality,
                "windowWidth": args.window_width,
                "windowHeight": args.window_height,
                "asyncUpload": use_async_upload,
                "uploadQueueSize": args.upload_queue_size,
                "previewDelaySeconds": args.preview_delay_seconds,
                "previewDelayFrames": preview_delay_frames,
                "previewMaxEventAgeSeconds": args.preview_max_event_age_seconds,
                "previewMaxBboxAreaRatio": args.preview_max_bbox_area_ratio,
                "previewMinBboxConfidence": args.preview_min_bbox_confidence,
                "previewPrimaryBboxOnly": args.preview_primary_bbox_only,
                "previewMaxResponseLagSeconds": args.preview_max_response_lag_seconds,
                "bboxSource": "fastapi-response" if args.preview_bbox else None,
                "speedOverlay": speed_overlay is not None,
                "speedConfigSent": speed_config_json is not None,
            },
            ensure_ascii=False,
        )
    )

    try:
        paused = False
        while True:
            with upload_state.lock:
                if upload_state.error:
                    raise RuntimeError(upload_state.error)

                if upload_state.stopped_by_finalized_limit:
                    print(
                        "stopReason=finalized_limit "
                        f"finalizedEvents={upload_state.finalized_count}"
                    )
                    stopped_early = True
                    break

            if paused:
                key = cv2.waitKey(50) & 0xFF
                if key in {27, ord("q")}:
                    print("stopReason=user_quit")
                    stopped_early = True
                    break
                if key == ord(" "):
                    paused = False
                continue

            ok, frame = capture.read()

            if not ok:
                break

            read_count += 1
            source_frame_history.append((read_count, frame.copy()))
            preview_buffer.append(PreviewFrame(read_count, frame.copy()))
            should_preview_frame = (
                args.preview_bbox
                and ((read_count - 1) % preview_frame_step == 0)
            )

            if use_preview_tracker:
                frame_history.append((read_count, frame.copy()))

            should_upload = (read_count - 1) % frame_step == 0

            if use_async_upload:
                if should_upload:
                    frame_bytes = encode_upload_frame(
                        frame,
                        upload_scale=args.upload_scale,
                        jpeg_quality=args.jpeg_quality,
                    )

                    if frame_bytes is None:
                        print(f"frame={read_count} encode_failed")
                    else:
                        (
                            high_res_crop_bytes,
                            high_res_crop_frame_number,
                        ) = build_highres_crop_for_upload(
                            enabled=args.highres_ocr_crop,
                            use_async_upload=use_async_upload,
                            upload_state=upload_state,
                            source_frame_history=source_frame_history,
                            latest_response_frame_number=latest_response_frame_number,
                            latest_response_body=latest_response_body,
                            response_coord_scale=response_coord_scale,
                            padding_ratio=args.highres_crop_padding,
                            jpeg_quality=args.highres_jpeg_quality,
                        )
                        captured_at = base_time + timedelta(
                            seconds=uploaded_count
                            * args.video_speed_ratio
                            / args.fps
                        )
                        enqueue_upload_task(
                            upload_queue,
                            upload_state,
                            UploadTask(
                                frame_number=read_count,
                                captured_at=captured_at,
                                frame_bytes=frame_bytes,
                                high_res_crop_bytes=high_res_crop_bytes,
                                high_res_crop_frame_number=(
                                    high_res_crop_frame_number
                                ),
                            ),
                        )
                        uploaded_count += 1

                display_frame_number = read_count
                display_frame = frame

                if preview_delay_frames > 0 and preview_buffer:
                    target_frame_number = max(1, read_count - preview_delay_frames)

                    while (
                        len(preview_buffer) > 1
                        and preview_buffer[1].frame_number <= target_frame_number
                    ):
                        preview_buffer.popleft()

                    if preview_buffer[0].frame_number <= target_frame_number:
                        display_packet = preview_buffer[0]
                        display_frame_number = display_packet.frame_number
                        display_frame = display_packet.frame

                if preview_delay_frames > 0:
                    response_frame_number, response_body = get_response_at_or_before_frame(
                        upload_state,
                        display_frame_number,
                    )
                else:
                    response_frame_number, response_body = get_latest_response_packet(upload_state)

                if (
                    response_frame_number is not None
                    and args.preview_max_response_lag_seconds >= 0
                ):
                    max_response_lag_frames = round(
                        source_fps * args.preview_max_response_lag_seconds
                    )
                    response_frame_lag = display_frame_number - response_frame_number
                    if response_frame_lag > max_response_lag_frames:
                        response_frame_number = None
                        response_body = None
                        active_overlay = None
                        active_tracker = None

                if (
                    should_preview_frame
                    and response_frame_number is not None
                    and response_frame_number != consumed_response_frame_number
                ):
                    if use_preview_tracker:
                        rebuilt_tracker = rebuild_tracker_from_response(
                            response_frame_number=response_frame_number,
                            response_body=response_body,
                            frame_history=frame_history,
                            response_coord_scale=response_coord_scale,
                            min_bbox_confidence=args.preview_min_bbox_confidence,
                        )

                        if rebuilt_tracker is not None:
                            active_tracker = rebuilt_tracker
                            active_overlay = None
                        else:
                            active_tracker = None
                            active_overlay = None
                    else:
                        bbox, confidence_score = select_response_bbox(
                            response_body,
                            response_coord_scale=response_coord_scale,
                            min_confidence=args.preview_min_bbox_confidence,
                        )

                        if bbox is not None:
                            active_overlay = PreviewOverlay(
                                bbox_xyxy=bbox,
                                response_frame_number=response_frame_number,
                                confidence_score=confidence_score,
                            )
                        else:
                            active_overlay = None
                            active_tracker = None

                    consumed_response_frame_number = response_frame_number

                if should_preview_frame:
                    hold_frames = round(source_fps * args.bbox_hold_seconds)

                    if (
                        active_overlay is not None
                        and display_frame_number - active_overlay.response_frame_number > hold_frames
                    ):
                        active_overlay = None

                    if use_preview_tracker:
                        active_tracker = update_preview_tracker(
                            active_tracker,
                            frame_number=display_frame_number,
                            frame=display_frame,
                        )
                    tracker_bbox = (
                        active_tracker.bbox_xyxy
                        if active_tracker is not None and use_preview_tracker
                        else None
                    )
                    tracker_confidence = (
                        active_tracker.confidence_score
                        if active_tracker is not None and use_preview_tracker
                        else 0.0
                    )
                    if tracker_bbox is None and active_overlay is not None:
                        tracker_bbox = active_overlay.bbox_xyxy
                        tracker_confidence = active_overlay.confidence_score

                    key = draw_preview(
                        frame=display_frame,
                        frame_number=display_frame_number,
                        response_body=response_body,
                        scale=args.scale,
                        wait_ms=preview_wait_ms if args.realtime else 1,
                        tracker_bbox=tracker_bbox,
                        tracker_confidence=tracker_confidence,
                        response_coord_scale=response_coord_scale,
                        speed_overlay=speed_overlay,
                        max_event_age_seconds=args.preview_max_event_age_seconds,
                        max_bbox_area_ratio=args.preview_max_bbox_area_ratio,
                        min_bbox_confidence=args.preview_min_bbox_confidence,
                        primary_bbox_only=args.preview_primary_bbox_only,
                    )
                    should_quit, should_toggle_pause = handle_preview_key(key)
                else:
                    key = cv2.waitKey(1) & 0xFF if args.preview_bbox else 255
                    should_quit, should_toggle_pause = handle_preview_key(key)

                if should_quit:
                    print("stopReason=user_quit")
                    stopped_early = True
                    break

                if should_toggle_pause:
                    paused = True

                if args.limit and uploaded_count >= args.limit:
                    print(f"stopReason=frame_limit limit={args.limit}")
                    stopped_early = True
                    break

                continue

            if not should_upload:
                if args.preview_bbox and effective_preview_all_frames:
                    if use_async_upload:
                        latest_response_body = get_latest_response_body(upload_state)

                    key = draw_preview(
                        frame=frame,
                        frame_number=read_count,
                        response_body=latest_response_body,
                        scale=args.scale,
                        wait_ms=preview_wait_ms if args.realtime else 1,
                        response_coord_scale=response_coord_scale,
                        speed_overlay=speed_overlay,
                        max_event_age_seconds=args.preview_max_event_age_seconds,
                        max_bbox_area_ratio=args.preview_max_bbox_area_ratio,
                        min_bbox_confidence=args.preview_min_bbox_confidence,
                        primary_bbox_only=args.preview_primary_bbox_only,
                    )
                    should_quit, should_toggle_pause = handle_preview_key(key)

                    if should_quit:
                        print("stopReason=user_quit")
                        stopped_early = True
                        break

                    if should_toggle_pause:
                        paused = True

                continue

            frame_bytes = encode_upload_frame(
                frame,
                upload_scale=args.upload_scale,
                jpeg_quality=args.jpeg_quality,
            )

            if frame_bytes is None:
                print(f"frame={read_count} encode_failed")
                continue

            (
                high_res_crop_bytes,
                high_res_crop_frame_number,
            ) = build_highres_crop_for_upload(
                enabled=args.highres_ocr_crop,
                use_async_upload=use_async_upload,
                upload_state=upload_state,
                source_frame_history=source_frame_history,
                latest_response_frame_number=latest_response_frame_number,
                latest_response_body=latest_response_body,
                response_coord_scale=response_coord_scale,
                padding_ratio=args.highres_crop_padding,
                jpeg_quality=args.highres_jpeg_quality,
            )

            captured_at = base_time + timedelta(
                seconds=uploaded_count * args.video_speed_ratio / args.fps
            )

            if use_async_upload and upload_queue is not None:
                enqueue_upload_task(
                    upload_queue,
                    upload_state,
                    UploadTask(
                        frame_number=read_count,
                        captured_at=captured_at,
                        frame_bytes=frame_bytes,
                        high_res_crop_bytes=high_res_crop_bytes,
                        high_res_crop_frame_number=high_res_crop_frame_number,
                    ),
                )
                uploaded_count += 1
                response_body = get_latest_response_body(upload_state)
                latest_response_body = response_body
            else:
                response_body = post_frame(
                    url=url,
                    camera_code=args.camera_code,
                    captured_at=captured_at,
                    frame_number=read_count,
                    frame_bytes=frame_bytes,
                    timeout=args.timeout,
                    speed_config_json=speed_config_json,
                    high_res_crop_bytes=high_res_crop_bytes,
                    high_res_crop_frame_number=high_res_crop_frame_number,
                )
                if args.finalized_highres_ocr and should_run_finalized_highres_ocr(
                    response_body
                ):
                    (
                        crop_bytes,
                        best_frame_number,
                        best_captured_at,
                    ) = build_finalized_highres_crop(
                        video_path=video_path,
                        response_body=response_body,
                        response_coord_scale=response_coord_scale,
                        padding_ratio=args.highres_crop_padding,
                        jpeg_quality=args.highres_jpeg_quality,
                    )
                    if (
                        crop_bytes is None
                        or best_frame_number is None
                        or best_captured_at is None
                    ):
                        raise RuntimeError(
                            "failed to capture original best frame for high-res OCR"
                        )

                    highres_response_body = post_highres_ocr(
                        url=highres_ocr_url,
                        camera_code=args.camera_code,
                        captured_at=best_captured_at,
                        frame_number=best_frame_number,
                        high_res_crop_bytes=crop_bytes,
                        timeout=args.timeout,
                    )
                    print(
                        summarize_highres_response(
                            best_frame_number,
                            highres_response_body,
                        )
                    )
                latest_response_body = response_body
                latest_response_frame_number = read_count
                uploaded_count += 1

                print(summarize_response(read_count, response_body))

            if args.preview_bbox:
                key = draw_preview(
                    frame=frame,
                    frame_number=read_count,
                    response_body=response_body,
                    scale=args.scale,
                    wait_ms=preview_wait_ms if args.realtime else 1,
                    response_coord_scale=response_coord_scale,
                    speed_overlay=speed_overlay,
                    max_event_age_seconds=args.preview_max_event_age_seconds,
                    max_bbox_area_ratio=args.preview_max_bbox_area_ratio,
                    min_bbox_confidence=args.preview_min_bbox_confidence,
                    primary_bbox_only=args.preview_primary_bbox_only,
                )
                should_quit, should_toggle_pause = handle_preview_key(key)

                if should_quit:
                    print("stopReason=user_quit")
                    stopped_early = True
                    break

                if should_toggle_pause:
                    paused = True

            if response_body and response_body.get("streamStatus") == "FINALIZED":
                finalized_count += 1

                if (
                    args.stop_after_finalized
                    and finalized_count >= args.stop_after_finalized
                ):
                    print(
                        "stopReason=finalized_limit "
                        f"finalizedEvents={finalized_count}"
                    )
                    stopped_early = True
                    break

            if args.limit and uploaded_count >= args.limit:
                print(f"stopReason=frame_limit limit={args.limit}")
                stopped_early = True
                break

            if args.realtime and not args.preview_bbox:
                time.sleep(1 / args.fps)
    finally:
        capture.release()
        stop_event.set()
        if upload_queue is not None:
            upload_queue.join()
        if worker_thread is not None:
            worker_thread.join(timeout=2)

    if use_async_upload:
        with upload_state.lock:
            finalized_count = upload_state.finalized_count

    if (
        not stopped_early
        and args.flush_frames > 0
        and not use_async_upload
    ):
        blank_frame_bytes = make_blank_frame_bytes(
            max(1, round(video_width * args.upload_scale)),
            max(1, round(video_height * args.upload_scale)),
            args.jpeg_quality,
        )

        for index in range(args.flush_frames):
            captured_at = base_time + timedelta(
                seconds=(uploaded_count + index)
                * args.video_speed_ratio
                / args.fps
            )
            response_body = post_frame(
                url=url,
                camera_code=args.camera_code,
                captured_at=captured_at,
                frame_number=None,
                frame_bytes=blank_frame_bytes,
                timeout=args.timeout,
                speed_config_json=speed_config_json,
            )
            uploaded_count += 1
            print(f"flush={index + 1} {summarize_response(read_count, response_body)}")

            if response_body.get("streamStatus") == "FINALIZED":
                finalized_count += 1
                break

            if args.realtime:
                time.sleep(1 / args.fps)

        print("stopReason=video_eof")
    elif not stopped_early:
        print("stopReason=video_eof")

    if args.preview_bbox:
        cv2.destroyAllWindows()

    print(
        f"uploadedFrames={uploaded_count} "
        f"readFrames={read_count} "
        f"finalizedEvents={finalized_count} "
        f"droppedUploadFrames={upload_state.dropped_count if use_async_upload else 0}"
    )


if __name__ == "__main__":
    main()
