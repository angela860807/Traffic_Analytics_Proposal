import argparse
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cv2


SCENARIOS = [
    {
        "name": "normal",
        "label": "Normal baseline",
        "start_sec": 0,
        "fps_avg": 24.0,
        "frame_drop_rate": 0.01,
        "latency_p95_ms": 480,
        "blur_score_avg": 0.12,
        "ocr_fail_rate": 0.05,
        "cpu_usage_pct": 42.0,
        "memory_usage_pct": 48.0,
        "network_rtt_ms": 80,
        "quality_status": "COMPLETE",
    },
    {
        "name": "blur",
        "label": "Blur degradation",
        "start_sec": 40,
        "fps_avg": 22.0,
        "frame_drop_rate": 0.04,
        "latency_p95_ms": 650,
        "blur_score_avg": 0.82,
        "ocr_fail_rate": 0.28,
        "cpu_usage_pct": 49.0,
        "memory_usage_pct": 53.0,
        "network_rtt_ms": 92,
        "quality_status": "PARTIAL",
    },
    {
        "name": "low_fps",
        "label": "Low FPS / frame drops",
        "start_sec": 80,
        "fps_avg": 8.5,
        "frame_drop_rate": 0.42,
        "latency_p95_ms": 1200,
        "blur_score_avg": 0.25,
        "ocr_fail_rate": 0.18,
        "cpu_usage_pct": 78.0,
        "memory_usage_pct": 72.0,
        "network_rtt_ms": 140,
        "quality_status": "PARTIAL",
    },
    {
        "name": "dropout",
        "label": "Camera dropout / critical",
        "start_sec": 160,
        "fps_avg": 2.0,
        "frame_drop_rate": 0.88,
        "latency_p95_ms": 5200,
        "blur_score_avg": 0.95,
        "ocr_fail_rate": 0.96,
        "cpu_usage_pct": 93.0,
        "memory_usage_pct": 91.0,
        "network_rtt_ms": 1250,
        "quality_status": "INSUFFICIENT",
    },
]


def open_capture(source: Path):
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {source}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1280)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 720)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    return cap, fps, width, height, frame_count


def transform_frame(frame, scenario_name: str, frame_index: int, fps: float):
    if scenario_name == "blur":
        return cv2.GaussianBlur(frame, (31, 31), 0)

    if scenario_name == "dropout":
        if int(frame_index / max(fps, 1)) % 4 == 2:
            return frame * 0
        if frame_index % 5 == 0:
            frame = cv2.GaussianBlur(frame, (25, 25), 0)
        return frame

    return frame


def write_clip(source: Path, output: Path, scenario: dict, duration_sec: int):
    cap, fps, width, height, frame_count = open_capture(source)
    start_frame = int(scenario["start_sec"] * fps)
    max_start = max(frame_count - int(duration_sec * fps), 0)
    start_frame = min(start_frame, max_start)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    output.parent.mkdir(parents=True, exist_ok=True)
    writer_fps = fps
    writer = cv2.VideoWriter(
        str(output),
        cv2.VideoWriter_fourcc(*"mp4v"),
        writer_fps,
        (width, height),
    )
    if not writer.isOpened():
        cap.release()
        raise RuntimeError(f"Cannot write video: {output}")

    frames_to_write = int(duration_sec * fps)
    written = 0
    held_low_fps_frame = None
    hold_interval = max(int(fps // 2), 8)
    for i in range(frames_to_write):
        ok, frame = cap.read()
        if not ok:
            break

        if scenario["name"] == "low_fps":
            if held_low_fps_frame is None or i % hold_interval == 0:
                held_low_fps_frame = frame.copy()
            out = held_low_fps_frame.copy()
            if i % hold_interval > hold_interval * 0.65:
                h, w = out.shape[:2]
                cv2.rectangle(out, (0, int(h * 0.45)), (w, int(h * 0.55)), (0, 0, 0), -1)
            writer.write(out)
            written += 1
            continue

        writer.write(transform_frame(frame, scenario["name"], i, fps))
        written += 1

    writer.release()
    cap.release()
    return written, writer_fps


def write_health_csv(output: Path, camera_id: int, zone_id: int, start_at: datetime):
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "scenario",
        "camera_id",
        "zone_id",
        "sampled_at",
        "fps_avg",
        "frame_drop_rate",
        "latency_p95_ms",
        "blur_score_avg",
        "ocr_fail_rate",
        "cpu_usage_pct",
        "memory_usage_pct",
        "network_rtt_ms",
        "quality_status",
        "data_source",
    ]
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for idx, scenario in enumerate(SCENARIOS):
            row = {key: scenario[key] for key in fields if key in scenario}
            row.update(
                {
                    "scenario": scenario["name"],
                    "camera_id": camera_id,
                    "zone_id": zone_id,
                    "sampled_at": (start_at + timedelta(minutes=idx * 5)).isoformat(),
                    "data_source": "REAL",
                }
            )
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Generate predictive maintenance demo video clips and mock health samples.")
    parser.add_argument("--source", default="test-media/videos/sample.mp4")
    parser.add_argument("--video-output-dir", default="test-media/videos/predictive-demo")
    parser.add_argument("--sample-output", default="test-media/smoke-runs/predictive-demo/camera-health-samples.csv")
    parser.add_argument("--duration-sec", type=int, default=20)
    parser.add_argument("--camera-id", type=int, default=1)
    parser.add_argument("--zone-id", type=int, default=1)
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        raise FileNotFoundError(source)

    video_output_dir = Path(args.video_output_dir)
    for scenario in SCENARIOS:
        output = video_output_dir / f"sample_{scenario['name']}.mp4"
        written, out_fps = write_clip(source, output, scenario, args.duration_sec)
        print(f"{output} | {scenario['label']} | frames={written} | fps={out_fps}")

    start_at = datetime.now(timezone.utc).astimezone()
    sample_output = Path(args.sample_output)
    write_health_csv(sample_output, args.camera_id, args.zone_id, start_at)
    print(f"{sample_output} | mock health samples written")


if __name__ == "__main__":
    main()
