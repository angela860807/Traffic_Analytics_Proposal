"""
Generate v6 simulation data: Method 3 + Method 4.

Method 3:
    Richer normal time patterns.

Method 4:
    Pre-fault precursor window before the actual fault window.

Outputs:
    data/normal_samples6_timepattern_precursor.csv
    data/fault_samples6_timepattern_precursor.csv
    data/all_samples6_timepattern_precursor.csv

Run from the tas-pm-ai project root:
    python generate_simulation_data6_timepattern_precursor.py
"""

from datetime import timedelta
import os

import pandas as pd

import generate_simulation_data3 as sim
from generate_simulation_data5_timepattern import generate_normal_sample_v5


OUTPUT_NORMAL = "data/normal_samples6_timepattern_precursor.csv"
OUTPUT_FAULT = "data/fault_samples6_timepattern_precursor.csv"
OUTPUT_ALL = "data/all_samples6_timepattern_precursor.csv"

PRE_NORMAL_MINUTES = 60
PRECURSOR_MINUTES = 60
FAULT_MINUTES = 240
RECOVERY_MINUTES = 120
PRECURSOR_MAX_PROGRESS = 0.35

FAULT_SCENARIOS = [
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


def enrich(row, *, phase, scenario_key, scenario_base, actual_fault_type,
           is_pre_fault, minutes_to_fault):
    row["fault_phase"] = phase
    row["scenario_key"] = scenario_key
    row["scenario_base_type"] = scenario_base
    row["actual_fault_type"] = actual_fault_type
    row["is_pre_fault"] = int(is_pre_fault)
    row["will_fail_in_60min"] = int(is_pre_fault)
    row["risk_label"] = int(row.get("is_fault", 0) == 1 or is_pre_fault)
    row["minutes_to_fault"] = minutes_to_fault
    return row


def generate_normal_data():
    normal_rows = []
    print(f"정상 데이터 v6 생성 중... (카메라 {sim.N_CAMERAS}대 x {sim.NORMAL_DAYS}일)")
    for cam_id in range(1, sim.N_CAMERAS + 1):
        ts = sim.START_TIME
        end = sim.START_TIME + timedelta(days=sim.NORMAL_DAYS)
        while ts < end:
            normal_rows.append(generate_normal_sample_v5(ts, cam_id))
            ts += timedelta(minutes=sim.SAMPLE_INTERVAL_MIN)
    return normal_rows


def generate_fault_data():
    fault_rows = []
    fault_start = sim.START_TIME + timedelta(days=sim.NORMAL_DAYS)
    scenario_count = len(FAULT_SCENARIOS) * len(sim.FAULT_INTENSITIES)
    print(f"장애 데이터 v6 생성 중... ({scenario_count}개 시나리오)")

    idx = 0
    for fault_type in FAULT_SCENARIOS:
        for intensity_label, max_progress in sim.FAULT_INTENSITIES.items():
            idx += 1
            cam_id = ((idx - 1) % sim.N_CAMERAS) + 1
            day_start = fault_start + timedelta(days=idx - 1)
            ts = day_start

            intensity_upper = intensity_label.upper()
            scenario_key = (
                "EXTERNAL_TRAFFIC_NORMAL_DEVICE"
                if fault_type == "EXTERNAL_TRAFFIC"
                else f"{fault_type}_{intensity_upper}"
            )

            if fault_type == "EXTERNAL_TRAFFIC":
                for _ in range(PRE_NORMAL_MINUTES + PRECURSOR_MINUTES):
                    row = generate_normal_sample_v5(ts, cam_id)
                    fault_rows.append(enrich(
                        row,
                        phase="NORMAL",
                        scenario_key=scenario_key,
                        scenario_base=fault_type,
                        actual_fault_type=scenario_key,
                        is_pre_fault=False,
                        minutes_to_fault=None,
                    ))
                    ts += timedelta(minutes=1)

                for _ in range(FAULT_MINUTES):
                    base = generate_normal_sample_v5(ts, cam_id)
                    row = sim.apply_fault(
                        base, fault_type,
                        progress=1.0,
                        max_progress=max_progress,
                        intensity_label=intensity_label,
                    )
                    fault_rows.append(enrich(
                        row,
                        phase="EXTERNAL_TRAFFIC",
                        scenario_key=scenario_key,
                        scenario_base=fault_type,
                        actual_fault_type=scenario_key,
                        is_pre_fault=False,
                        minutes_to_fault=None,
                    ))
                    ts += timedelta(minutes=1)

                for _ in range(RECOVERY_MINUTES):
                    row = generate_normal_sample_v5(ts, cam_id)
                    fault_rows.append(enrich(
                        row,
                        phase="RECOVERY",
                        scenario_key=scenario_key,
                        scenario_base=fault_type,
                        actual_fault_type=scenario_key,
                        is_pre_fault=False,
                        minutes_to_fault=None,
                    ))
                    ts += timedelta(minutes=1)

                print(f"  [{idx:2d}/{scenario_count}] {scenario_key:<35} 완료")
                continue

            actual_fault_type = scenario_key

            for i in range(PRE_NORMAL_MINUTES):
                row = generate_normal_sample_v5(ts, cam_id)
                fault_rows.append(enrich(
                    row,
                    phase="NORMAL",
                    scenario_key=scenario_key,
                    scenario_base=fault_type,
                    actual_fault_type=actual_fault_type,
                    is_pre_fault=False,
                    minutes_to_fault=PRECURSOR_MINUTES + (PRE_NORMAL_MINUTES - i),
                ))
                ts += timedelta(minutes=1)

            for i in range(PRECURSOR_MINUTES):
                precursor_progress = ((i + 1) / PRECURSOR_MINUTES) * PRECURSOR_MAX_PROGRESS
                base = generate_normal_sample_v5(ts, cam_id)
                row = sim.apply_fault(
                    base, fault_type,
                    progress=precursor_progress,
                    max_progress=max_progress,
                    intensity_label=intensity_label,
                )
                row["fault_type"] = f"{actual_fault_type}_PRECURSOR"
                row["is_fault"] = 0
                fault_rows.append(enrich(
                    row,
                    phase="PRECURSOR",
                    scenario_key=scenario_key,
                    scenario_base=fault_type,
                    actual_fault_type=actual_fault_type,
                    is_pre_fault=True,
                    minutes_to_fault=PRECURSOR_MINUTES - i,
                ))
                ts += timedelta(minutes=1)

            for i in range(FAULT_MINUTES):
                progress = i / FAULT_MINUTES
                base = generate_normal_sample_v5(ts, cam_id)
                row = sim.apply_fault(
                    base, fault_type,
                    progress=progress,
                    max_progress=max_progress,
                    intensity_label=intensity_label,
                )
                fault_rows.append(enrich(
                    row,
                    phase="FAULT",
                    scenario_key=scenario_key,
                    scenario_base=fault_type,
                    actual_fault_type=actual_fault_type,
                    is_pre_fault=False,
                    minutes_to_fault=-i,
                ))
                ts += timedelta(minutes=1)

            for i in range(RECOVERY_MINUTES):
                row = generate_normal_sample_v5(ts, cam_id)
                fault_rows.append(enrich(
                    row,
                    phase="RECOVERY",
                    scenario_key=scenario_key,
                    scenario_base=fault_type,
                    actual_fault_type=actual_fault_type,
                    is_pre_fault=False,
                    minutes_to_fault=-(FAULT_MINUTES + i),
                ))
                ts += timedelta(minutes=1)

            print(f"  [{idx:2d}/{scenario_count}] {scenario_key:<35} 완료")

    return fault_rows


def generate_all_data():
    os.makedirs("data", exist_ok=True)

    df_normal = pd.DataFrame(generate_normal_data())
    df_fault = pd.DataFrame(generate_fault_data())
    df_all = pd.concat([df_normal, df_fault], ignore_index=True)

    df_normal.to_csv(OUTPUT_NORMAL, index=False)
    df_fault.to_csv(OUTPUT_FAULT, index=False)
    df_all.to_csv(OUTPUT_ALL, index=False)

    print("\n저장 완료")
    print(f"  {OUTPUT_NORMAL}: {len(df_normal):,}행")
    print(f"  {OUTPUT_FAULT}: {len(df_fault):,}행")
    print(f"  {OUTPUT_ALL}: {len(df_all):,}행")
    print("\n장애 phase 분포")
    print(df_fault["fault_phase"].value_counts().to_string())
    print("\nrisk_label 분포")
    print(df_fault["risk_label"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    generate_all_data()
