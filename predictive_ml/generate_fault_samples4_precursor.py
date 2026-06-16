"""
Generate precursor-aware fault evaluation data.

This script keeps the existing normal training data, model, scaler, and
thresholds untouched. It only creates data/fault_samples4.csv for evaluation.

Run from the tas-pm-ai project root:
    python generate_fault_samples4_precursor.py
"""

from datetime import timedelta
import os

import pandas as pd

import generate_simulation_data3 as sim


OUTPUT_PATH = "data/fault_samples4.csv"

PRE_NORMAL_MINUTES = 60
PRECURSOR_MINUTES = 60
FAULT_MINUTES = 240
RECOVERY_MINUTES = 120

# Keep precursor below hard rule thresholds, but make it drift enough for
# trend/anomaly scoring. apply_fault multiplies this by the intensity max.
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


def generate_fault_samples4():
    os.makedirs("data", exist_ok=True)
    rows = []

    fault_start = sim.START_TIME + timedelta(days=sim.NORMAL_DAYS)
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

            # Non-maintenance external traffic remains a negative scenario.
            if fault_type == "EXTERNAL_TRAFFIC":
                for i in range(PRE_NORMAL_MINUTES + PRECURSOR_MINUTES):
                    row = sim.generate_normal_sample(ts, cam_id)
                    rows.append(enrich(
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
                    base = sim.generate_normal_sample(ts, cam_id)
                    row = sim.apply_fault(
                        base, fault_type, progress=1.0,
                        max_progress=max_progress,
                        intensity_label=intensity_label,
                    )
                    rows.append(enrich(
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
                    row = sim.generate_normal_sample(ts, cam_id)
                    rows.append(enrich(
                        row,
                        phase="RECOVERY",
                        scenario_key=scenario_key,
                        scenario_base=fault_type,
                        actual_fault_type=scenario_key,
                        is_pre_fault=False,
                        minutes_to_fault=None,
                    ))
                    ts += timedelta(minutes=1)

                print(f"[{idx:2d}] {scenario_key:<35} done")
                continue

            actual_fault_type = scenario_key

            # Clearly normal lead-in.
            for i in range(PRE_NORMAL_MINUTES):
                row = sim.generate_normal_sample(ts, cam_id)
                rows.append(enrich(
                    row,
                    phase="NORMAL",
                    scenario_key=scenario_key,
                    scenario_base=fault_type,
                    actual_fault_type=actual_fault_type,
                    is_pre_fault=False,
                    minutes_to_fault=PRECURSOR_MINUTES + (PRE_NORMAL_MINUTES - i),
                ))
                ts += timedelta(minutes=1)

            # Pre-fault drift: not a failure yet, but a predictive-risk window.
            for i in range(PRECURSOR_MINUTES):
                precursor_progress = ((i + 1) / PRECURSOR_MINUTES) * PRECURSOR_MAX_PROGRESS
                base = sim.generate_normal_sample(ts, cam_id)
                row = sim.apply_fault(
                    base, fault_type,
                    progress=precursor_progress,
                    max_progress=max_progress,
                    intensity_label=intensity_label,
                )
                row["fault_type"] = f"{actual_fault_type}_PRECURSOR"
                row["is_fault"] = 0
                rows.append(enrich(
                    row,
                    phase="PRECURSOR",
                    scenario_key=scenario_key,
                    scenario_base=fault_type,
                    actual_fault_type=actual_fault_type,
                    is_pre_fault=True,
                    minutes_to_fault=PRECURSOR_MINUTES - i,
                ))
                ts += timedelta(minutes=1)

            # Actual fault window.
            for i in range(FAULT_MINUTES):
                progress = i / FAULT_MINUTES
                base = sim.generate_normal_sample(ts, cam_id)
                row = sim.apply_fault(
                    base, fault_type,
                    progress=progress,
                    max_progress=max_progress,
                    intensity_label=intensity_label,
                )
                rows.append(enrich(
                    row,
                    phase="FAULT",
                    scenario_key=scenario_key,
                    scenario_base=fault_type,
                    actual_fault_type=actual_fault_type,
                    is_pre_fault=False,
                    minutes_to_fault=-i,
                ))
                ts += timedelta(minutes=1)

            # Recovery/normal tail.
            for i in range(RECOVERY_MINUTES):
                row = sim.generate_normal_sample(ts, cam_id)
                rows.append(enrich(
                    row,
                    phase="RECOVERY",
                    scenario_key=scenario_key,
                    scenario_base=fault_type,
                    actual_fault_type=actual_fault_type,
                    is_pre_fault=False,
                    minutes_to_fault=-(FAULT_MINUTES + i),
                ))
                ts += timedelta(minutes=1)

            print(f"[{idx:2d}] {scenario_key:<35} done")

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved: {OUTPUT_PATH}")
    print(f"Rows : {len(df):,}")
    print("\nPhase counts:")
    print(df["fault_phase"].value_counts().to_string())
    print("\nRisk labels:")
    print(df["risk_label"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    generate_fault_samples4()
