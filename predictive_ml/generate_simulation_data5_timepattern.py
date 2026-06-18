"""
Generate v5 simulation data with richer normal time patterns.

Method 3 goal:
    Increase normal-data diversity so the LSTM-AE threshold is estimated from
    a more realistic normal distribution.

Outputs:
    data/normal_samples5_timepattern.csv
    data/fault_samples5_timepattern.csv
    data/all_samples5_timepattern.csv

Run from the tas-pm-ai project root:
    python generate_simulation_data5_timepattern.py
"""

from datetime import timedelta
import os

import numpy as np
import pandas as pd

import generate_simulation_data3 as sim


OUTPUT_NORMAL = "data/normal_samples5_timepattern.csv"
OUTPUT_FAULT = "data/fault_samples5_timepattern.csv"
OUTPUT_ALL = "data/all_samples5_timepattern.csv"

SEED = 142
rng = np.random.default_rng(SEED)


def time_pattern(ts, camera_id):
    hour = ts.hour
    minute = ts.minute
    weekday = ts.weekday()

    # Keep the old day/night concept, but add morning/evening peaks, weekend
    # dampening, camera-specific offset, and smooth daily variation.
    if 7 <= hour < 20:
        base_load = 1.0
    elif 20 <= hour < 23:
        base_load = 0.7
    else:
        base_load = 0.4

    morning_peak = np.exp(-((hour + minute / 60 - 8.5) ** 2) / 3.0) * 0.18
    evening_peak = np.exp(-((hour + minute / 60 - 18.0) ** 2) / 4.0) * 0.15
    weekend_factor = 0.88 if weekday >= 5 else 1.0
    camera_factor = {1: 1.00, 2: 0.92, 3: 1.08}.get(camera_id, 1.0)
    daily_wave = 1.0 + 0.06 * np.sin(2 * np.pi * (ts.timetuple().tm_yday % 14) / 14)

    load = (base_load + morning_peak + evening_peak) * weekend_factor * camera_factor * daily_wave
    return float(np.clip(load, 0.25, 1.35))


def generate_normal_sample_v5(ts, camera_id):
    load = time_pattern(ts, camera_id)
    hour = ts.hour
    is_night = hour < 7 or hour >= 22
    is_rush = 7 <= hour < 10 or 17 <= hour < 20

    fps = rng.normal(loc=8 + 22 * load, scale=1.8 + 0.6 * is_rush)
    fps = float(np.clip(fps, 0, 30))

    frame_drop_base = 0.004 + 0.018 * max(0.0, load - 0.75)
    frame_drop = frame_drop_base + rng.beta(a=1.2, b=26) * 0.12
    frame_drop = float(np.clip(frame_drop, 0, 1))

    latency = rng.normal(
        loc=430 - 120 * load + 70 * is_rush,
        scale=55 + 20 * is_rush,
    )
    latency = int(np.clip(latency, 100, 900))

    blur_mean = 0.75 - 0.05 * is_night + 0.02 * rng.normal()
    blur = rng.normal(loc=blur_mean, scale=0.06)
    blur = float(np.clip(blur, 0, 1))

    ocr_alpha = 2.2 + 0.4 * is_night
    ocr_beta = 10.0 - 1.5 * is_night
    ocr_fail = rng.beta(a=ocr_alpha, b=max(2.0, ocr_beta))
    ocr_fail = float(np.clip(ocr_fail, 0, 1))

    cpu = rng.normal(loc=22 + 48 * load + 5 * is_rush, scale=9)
    cpu = float(np.clip(cpu, 0, 100))

    memory = rng.normal(loc=58 + 3 * (camera_id - 2), scale=6)
    memory = float(np.clip(memory, 0, 100))

    rtt = rng.normal(loc=58 + 18 * max(0.0, load - 0.9) + 8 * is_rush, scale=17)
    rtt = int(np.clip(rtt, 10, 260))

    return {
        "camera_id": camera_id,
        "sampled_at": ts.isoformat(),
        "fps_avg": round(fps, 2),
        "frame_drop_rate": round(frame_drop, 4),
        "latency_p95_ms": latency,
        "blur_score_avg": round(blur, 4),
        "ocr_fail_rate": round(ocr_fail, 4),
        "cpu_usage_pct": round(cpu, 2),
        "memory_usage_pct": round(memory, 2),
        "network_rtt_ms": rtt,
        "data_source": "SIMULATED",
        "quality_status": "COMPLETE",
        "fault_type": "NORMAL",
        "is_fault": 0,
    }


def generate_all_data():
    os.makedirs("data", exist_ok=True)

    normal_rows = []
    fault_rows = []

    print(f"정상 데이터 v5 생성 중... (카메라 {sim.N_CAMERAS}대 x {sim.NORMAL_DAYS}일)")
    for cam_id in range(1, sim.N_CAMERAS + 1):
        ts = sim.START_TIME
        end = sim.START_TIME + timedelta(days=sim.NORMAL_DAYS)
        while ts < end:
            normal_rows.append(generate_normal_sample_v5(ts, cam_id))
            ts += timedelta(minutes=sim.SAMPLE_INTERVAL_MIN)

    fault_scenarios = [
        "CAMERA_OFFLINE",
        "FPS_DEGRADATION",
        "FRAME_DROP",
        "LATENCY_DEGRADATION",
        "BLUR_DEGRADATION",
        "OCR_QUALITY",
        "RESOURCE_SATURATION",
        "NETWORK_INSTABILITY",
        "EXTERNAL_TRAFFIC",
    ]

    fault_start = sim.START_TIME + timedelta(days=sim.NORMAL_DAYS)
    scenario_count = len(fault_scenarios) * len(sim.FAULT_INTENSITIES)
    print(f"장애 데이터 v5 생성 중... ({scenario_count}개 시나리오)")

    idx = 0
    for fault_type in fault_scenarios:
        for intensity_label, max_progress in sim.FAULT_INTENSITIES.items():
            idx += 1
            cam_id = ((idx - 1) % sim.N_CAMERAS) + 1
            day_start = fault_start + timedelta(days=idx - 1)
            ts = day_start

            for _ in range(120):
                fault_rows.append(generate_normal_sample_v5(ts, cam_id))
                ts += timedelta(minutes=1)

            fault_duration = 240
            for i in range(fault_duration):
                progress = i / fault_duration
                base = generate_normal_sample_v5(ts, cam_id)
                row = sim.apply_fault(
                    base, fault_type, progress,
                    max_progress, intensity_label,
                )
                fault_rows.append(row)
                ts += timedelta(minutes=1)

            for _ in range(120):
                fault_rows.append(generate_normal_sample_v5(ts, cam_id))
                ts += timedelta(minutes=1)

            print(f"  [{idx:2d}/{scenario_count}] {fault_type:<25} ({intensity_label}) 완료")

    df_normal = pd.DataFrame(normal_rows)
    df_fault = pd.DataFrame(fault_rows)
    df_all = pd.concat([df_normal, df_fault], ignore_index=True)

    df_normal.to_csv(OUTPUT_NORMAL, index=False)
    df_fault.to_csv(OUTPUT_FAULT, index=False)
    df_all.to_csv(OUTPUT_ALL, index=False)

    print("\n저장 완료")
    print(f"  {OUTPUT_NORMAL}: {len(df_normal):,}행")
    print(f"  {OUTPUT_FAULT}: {len(df_fault):,}행")
    print(f"  {OUTPUT_ALL}: {len(df_all):,}행")

    features = [
        "fps_avg", "frame_drop_rate", "latency_p95_ms",
        "blur_score_avg", "ocr_fail_rate", "cpu_usage_pct",
        "memory_usage_pct", "network_rtt_ms",
    ]
    print("\n정상 데이터 v5 기초 통계")
    print(df_normal[features].describe().round(3).to_string())


if __name__ == "__main__":
    generate_all_data()
