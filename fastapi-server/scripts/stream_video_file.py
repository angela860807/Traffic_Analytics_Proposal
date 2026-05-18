import argparse
from collections import deque
from dataclasses import dataclass, field
import json
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
WINDOW_NAME = "Traffic Stream + BBox Preview"


@dataclass
class UploadTask:
    frame_number: int
    captured_at: datetime
    frame_bytes: bytes


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
        default=3.0,
        help="Target frame upload FPS.",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=55,
        help="JPEG quality for uploaded frames.",
    )
    parser.add_argument(
        "--upload-scale",
        type=float,
        default=0.5,
        help=(
            "Resize frames before upload to reduce server YOLO load. "
            "1.0 uploads original resolution."
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
        default=8.0,
        help="Maximum OpenCV GUI redraw FPS. 0 displays every decoded video frame.",
    )
    parser.add_argument(
        "--preview-tracker",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Track response bbox between server responses. Disable for smoother low-end CPU preview.",
    )
    parser.add_argument(
        "--bbox-hold-seconds",
        type=float,
        default=0.6,
        help="Keep drawing the latest response bbox for this many seconds without OpenCV tracking.",
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
    return parser


def summarize_response(frame_number: int, response_body: dict[str, Any]) -> str:
    data = response_body.get("data") or {}
    return (
        f"frame={frame_number} "
        f"streamStatus={response_body.get('streamStatus')} "
        f"eventId={response_body.get('eventId') or '-'} "
        f"frameCount={response_body.get('frameCount')} "
        f"analysisStatus={response_body.get('analysisStatus') or '-'} "
        f"plateNumber={data.get('plateNumber') or '-'} "
        f"message={response_body.get('message', '')}"
    )


def post_frame(
    *,
    url: str,
    camera_code: str,
    captured_at: datetime,
    frame_bytes: bytes,
    timeout: float,
) -> dict[str, Any]:
    response = requests.post(
        url,
        data={
            "cameraCode": camera_code,
            "capturedAt": captured_at.replace(microsecond=0).isoformat(),
        },
        files={
            "image": ("video-frame.jpg", frame_bytes, "image/jpeg"),
        },
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

    if tracker_bbox is not None:
        bboxes = [list(tracker_bbox)]
        bbox = list(tracker_bbox)
        bbox_confidence = tracker_confidence

    for index, current_bbox in enumerate(bboxes):
        x1, y1, x2, y2 = [
            int(round(float(value) * response_coord_scale * coord_scale))
            for value in current_bbox
        ]
        color = (0, 255, 0)
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        label = f"TRACK {index + 1}" if tracker_bbox is not None else f"VEHICLE {index + 1}"

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
        color = (0, 255, 0)
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        draw_text(
            display_frame,
            f"VEHICLE {bbox_confidence:.3f}",
            (x1, max(overlay_line_height, y1 - 8)),
            color,
            overlay_font_scale,
        )

    event_age_seconds = response.get("eventAgeSeconds", 0.0)
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
        draw_text(
            display_frame,
            status_text,
            (12, overlay_line_height * 2),
            (0, 255, 255),
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
) -> tuple[tuple[int, int, int, int] | None, float]:
    if not isinstance(response_body, dict):
        return None, 0.0

    bboxes = response_body.get("bboxes") or []
    bbox = bboxes[0] if bboxes else response_body.get("bbox")

    if bbox is None:
        return None, 0.0

    x1, y1, x2, y2 = [
        int(round(float(value) * response_coord_scale))
        for value in bbox
    ]
    return (x1, y1, x2, y2), float(response_body.get("bboxConfidenceScore", 0.0))


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
) -> PreviewTracker | None:
    bbox, confidence_score = select_response_bbox(
        response_body,
        response_coord_scale=response_coord_scale,
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
    camera_code: str,
    timeout: float,
    stop_after_finalized: int,
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
                frame_bytes=task.frame_bytes,
                timeout=timeout,
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

    if args.scale <= 0:
        raise SystemExit("--scale must be greater than 0")

    if args.upload_scale <= 0:
        raise SystemExit("--upload-scale must be greater than 0")

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

    if args.preview_bbox:
        configure_preview_window(args.window_width, args.window_height)

    base_url = args.fastapi_base_url.rstrip("/")
    check_stream_endpoint(base_url, args.timeout)
    url = f"{base_url}{STREAM_FRAME_PATH}"
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
    use_preview_tracker = use_async_upload and args.preview_tracker
    uploaded_count = 0
    finalized_count = 0
    read_count = 0
    base_time = datetime.now()
    video_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    video_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    stopped_early = False
    latest_response_body: dict[str, Any] | None = None
    upload_state = UploadState()
    upload_queue: queue.Queue[UploadTask] | None = None
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
                "camera_code": args.camera_code,
                "timeout": args.timeout,
                "stop_after_finalized": args.stop_after_finalized,
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
                "frameStep": frame_step,
                "stopAfterFinalized": args.stop_after_finalized,
                "flushFrames": args.flush_frames,
                "previewBbox": args.preview_bbox,
                "previewAllFrames": args.preview_all_frames,
                "previewFps": args.preview_fps,
                "previewFrameStep": preview_frame_step,
                "previewTracker": use_preview_tracker,
                "bboxHoldSeconds": args.bbox_hold_seconds,
                "displayScale": args.scale,
                "uploadScale": args.upload_scale,
                "windowWidth": args.window_width,
                "windowHeight": args.window_height,
                "asyncUpload": use_async_upload,
                "uploadQueueSize": args.upload_queue_size,
                "previewDelaySeconds": args.preview_delay_seconds,
                "previewDelayFrames": preview_delay_frames,
                "bboxSource": "fastapi-response" if args.preview_bbox else None,
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
                        captured_at = base_time + timedelta(seconds=uploaded_count / args.fps)
                        enqueue_upload_task(
                            upload_queue,
                            upload_state,
                            UploadTask(
                                frame_number=read_count,
                                captured_at=captured_at,
                                frame_bytes=frame_bytes,
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
                        )

                        if rebuilt_tracker is not None:
                            active_tracker = rebuilt_tracker
                            active_overlay = None
                    else:
                        bbox, confidence_score = select_response_bbox(
                            response_body,
                            response_coord_scale=response_coord_scale,
                        )

                        if bbox is not None:
                            active_overlay = PreviewOverlay(
                                bbox_xyxy=bbox,
                                response_frame_number=response_frame_number,
                                confidence_score=confidence_score,
                            )

                    consumed_response_frame_number = response_frame_number

                if should_preview_frame:
                    hold_frames = round(source_fps * args.bbox_hold_seconds)

                    if (
                        active_overlay is not None
                        and read_count - active_overlay.response_frame_number > hold_frames
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
                if args.preview_bbox and args.preview_all_frames:
                    if use_async_upload:
                        latest_response_body = get_latest_response_body(upload_state)

                    key = draw_preview(
                        frame=frame,
                        frame_number=read_count,
                    response_body=latest_response_body,
                    scale=args.scale,
                    wait_ms=preview_wait_ms if args.realtime else 1,
                    response_coord_scale=response_coord_scale,
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

            captured_at = base_time + timedelta(seconds=uploaded_count / args.fps)

            if use_async_upload and upload_queue is not None:
                enqueue_upload_task(
                    upload_queue,
                    upload_state,
                    UploadTask(
                        frame_number=read_count,
                        captured_at=captured_at,
                        frame_bytes=frame_bytes,
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
                    frame_bytes=frame_bytes,
                    timeout=args.timeout,
                )
                latest_response_body = response_body
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
            captured_at = base_time + timedelta(seconds=(uploaded_count + index) / args.fps)
            response_body = post_frame(
                url=url,
                camera_code=args.camera_code,
                captured_at=captured_at,
                frame_bytes=blank_frame_bytes,
                timeout=args.timeout,
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
