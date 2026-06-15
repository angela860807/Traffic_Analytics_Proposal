"""
TAS-PM 시뮬레이션 데이터 생성 스크립트
========================================
목적: LSTM AutoEncoder 학습 및 평가용 CameraHealthSample 데이터 생성

출력 파일:
  - data/normal_samples.csv      : 정상 구간 (학습용)
  - data/fault_samples.csv       : 장애 구간 (평가용, 라벨 포함)
  - data/all_samples.csv         : 전체 합본 (시각화/분석용)

장애 시나리오 (06_FastAPI_작업_TODO 기준):
  1. CAMERA_OFFLINE        - 프레임 완전 중단
  2. FPS_DEGRADATION       - FPS 점진적 저하
  3. FRAME_DROP            - 프레임 드롭율 급증
  4. LATENCY_DEGRADATION   - 처리 지연 증가
  5. BLUR_DEGRADATION      - 블러 점수 저하
  6. OCR_QUALITY           - OCR 실패율 급증
  7. RESOURCE_SATURATION   - CPU/Memory 포화
  8. NETWORK_INSTABILITY   - RTT 급증·간헐적 spike
  9. EXTERNAL_TRAFFIC      - 교통량 감소 (장비 정상)

변경 이력:
  v1: 카메라 3대, 정상 14일
  v2: 카메라 10대, 정상 30일 (방법 1·2 적용)
"""

import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

# ── 시드 고정 (재현 가능) ───────────────────────────────────────
SEED = 42
rng = np.random.default_rng(SEED)

# ── 출력 폴더 ──────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)

# ── 설정 ───────────────────────────────────────────────────────
N_CAMERAS = 10                 # 카메라 수 (v1: 3 → v2: 10)
NORMAL_DAYS = 30               # 정상 데이터 기간 (v1: 14일 → v2: 30일)
FAULT_DAYS = 3                 # 장애 시나리오 기간 (일)
SAMPLE_INTERVAL_MIN = 1        # 샘플 주기 (분)
START_TIME = datetime(2026, 5, 1, 0, 0, 0)


# ══════════════════════════════════════════════════════════════
# 1. 정상 패턴 생성 헬퍼
# ══════════════════════════════════════════════════════════════

def time_of_day_factor(hour: int) -> float:
    """시간대별 부하 계수 (낮 > 밤)"""
    if 7 <= hour < 20:
        return 1.0        # 주간: 정상 부하
    elif 20 <= hour < 23:
        return 0.7        # 저녁: 약간 낮음
    else:
        return 0.4        # 심야: 낮음


def generate_normal_sample(ts: datetime, camera_id: int) -> dict:
    """1개 정상 샘플 생성"""
    hour = ts.hour
    factor = time_of_day_factor(hour)

    # FPS: 주간 24~30, 심야 10~15
    fps = rng.normal(loc=24 * factor + 8, scale=1.5)
    fps = float(np.clip(fps, 0, 30))

    # Frame drop rate: 정상 0.01~0.05
    frame_drop = rng.beta(a=1, b=30) * 0.1
    frame_drop = float(np.clip(frame_drop, 0, 1))

    # Latency P95 (ms): 정상 200~600
    latency = rng.normal(loc=400 - 150 * factor, scale=50)
    latency = int(np.clip(latency, 100, 800))

    # Blur score: 정상 0.6~0.9 (높을수록 선명)
    blur = rng.normal(loc=0.75, scale=0.05)
    blur = float(np.clip(blur, 0, 1))

    # OCR fail rate: 정상 0.05~0.20
    ocr_fail = rng.beta(a=2, b=10)
    ocr_fail = float(np.clip(ocr_fail, 0, 1))

    # CPU: 주간 40~70%, 심야 20~40%
    cpu = rng.normal(loc=55 * factor + 15, scale=8)
    cpu = float(np.clip(cpu, 0, 100))

    # Memory: 비교적 안정적 50~70%
    memory = rng.normal(loc=60, scale=5)
    memory = float(np.clip(memory, 0, 100))

    # Network RTT (ms): 정상 30~100
    rtt = rng.normal(loc=60, scale=15)
    rtt = int(np.clip(rtt, 10, 200))

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


# ══════════════════════════════════════════════════════════════
# 2. 장애 시나리오별 샘플 생성
# ══════════════════════════════════════════════════════════════

def apply_fault(base: dict, fault_type: str, progress: float) -> dict:
    """
    base: 정상 샘플 dict
    fault_type: 장애 유형
    progress: 장애 진행도 0.0~1.0 (점진적 악화 표현)
    """
    s = base.copy()
    s["fault_type"] = fault_type
    s["is_fault"] = 1

    if fault_type == "CAMERA_OFFLINE":
        s["fps_avg"] = 0.0
        s["frame_drop_rate"] = 1.0
        s["latency_p95_ms"] = 9999
        s["blur_score_avg"] = 0.0
        s["ocr_fail_rate"] = 1.0

    elif fault_type == "FPS_DEGRADATION":
        s["fps_avg"] = round(max(1.0, base["fps_avg"] * (1 - progress * 0.88)), 2)
        s["frame_drop_rate"] = round(min(1.0, base["frame_drop_rate"] + progress * 0.5), 4)

    elif fault_type == "FRAME_DROP":
        s["frame_drop_rate"] = round(min(1.0, base["frame_drop_rate"] + progress * 0.75), 4)
        s["fps_avg"] = round(max(1.0, base["fps_avg"] * (1 - progress * 0.3)), 2)

    elif fault_type == "LATENCY_DEGRADATION":
        s["latency_p95_ms"] = int(base["latency_p95_ms"] + progress * 5600)
        s["fps_avg"] = round(max(1.0, base["fps_avg"] * (1 - progress * 0.4)), 2)

    elif fault_type == "BLUR_DEGRADATION":
        s["blur_score_avg"] = round(max(0.0, base["blur_score_avg"] - progress * 0.6), 4)
        s["ocr_fail_rate"] = round(min(1.0, base["ocr_fail_rate"] + progress * 0.4), 4)

    elif fault_type == "OCR_QUALITY":
        s["ocr_fail_rate"] = round(min(1.0, base["ocr_fail_rate"] + progress * 0.8), 4)
        s["blur_score_avg"] = round(max(0.0, base["blur_score_avg"] - progress * 0.2), 4)

    elif fault_type == "RESOURCE_SATURATION":
        s["cpu_usage_pct"] = round(min(100.0, base["cpu_usage_pct"] + progress * 38), 2)
        s["memory_usage_pct"] = round(min(100.0, base["memory_usage_pct"] + progress * 30), 2)
        s["fps_avg"] = round(max(1.0, base["fps_avg"] * (1 - progress * 0.5)), 2)
        s["latency_p95_ms"] = int(base["latency_p95_ms"] + progress * 2000)

    elif fault_type == "NETWORK_INSTABILITY":
        spike = rng.choice([1, 3, 8], p=[0.6, 0.3, 0.1])
        s["network_rtt_ms"] = int(base["network_rtt_ms"] * spike + progress * 800)
        s["latency_p95_ms"] = int(base["latency_p95_ms"] + progress * 1500)
        s["ocr_fail_rate"] = round(min(1.0, base["ocr_fail_rate"] + progress * 0.2), 4)

    elif fault_type == "EXTERNAL_TRAFFIC":
        s["is_fault"] = 0
        s["fault_type"] = "EXTERNAL_TRAFFIC_NORMAL_DEVICE"

    return s


# ══════════════════════════════════════════════════════════════
# 3. 전체 데이터 생성
# ══════════════════════════════════════════════════════════════

def generate_all_data():
    normal_rows = []
    fault_rows = []

    # ── 정상 데이터 ──────────────────────────────────────────
    print(f"정상 데이터 생성 중... (카메라 {N_CAMERAS}대 × {NORMAL_DAYS}일)")
    for cam_id in range(1, N_CAMERAS + 1):
        ts = START_TIME
        end = START_TIME + timedelta(days=NORMAL_DAYS)
        while ts < end:
            row = generate_normal_sample(ts, cam_id)
            normal_rows.append(row)
            ts += timedelta(minutes=SAMPLE_INTERVAL_MIN)
        print(f"  카메라 {cam_id} 완료")

    print(f"  → 정상 샘플 수: {len(normal_rows):,}")

    # ── 장애 데이터 ──────────────────────────────────────────
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

    fault_start = START_TIME + timedelta(days=NORMAL_DAYS)
    print(f"\n장애 데이터 생성 중... (시나리오 {len(fault_scenarios)}종)")

    for scenario_idx, fault_type in enumerate(fault_scenarios):
        cam_id = (scenario_idx % N_CAMERAS) + 1
        day_start = fault_start + timedelta(days=scenario_idx)

        # 장애 전 정상 구간 (2시간)
        ts = day_start
        for _ in range(120):
            row = generate_normal_sample(ts, cam_id)
            fault_rows.append(row)
            ts += timedelta(minutes=1)

        # 장애 구간 (4시간, 점진적 악화)
        fault_duration = 240
        for i in range(fault_duration):
            progress = i / fault_duration
            base = generate_normal_sample(ts, cam_id)
            row = apply_fault(base, fault_type, progress)
            fault_rows.append(row)
            ts += timedelta(minutes=1)

        # 장애 후 회복 구간 (2시간)
        for _ in range(120):
            row = generate_normal_sample(ts, cam_id)
            fault_rows.append(row)
            ts += timedelta(minutes=1)

        print(f"  [{scenario_idx+1}/{len(fault_scenarios)}] {fault_type} 완료")

    print(f"  → 장애 샘플 수: {len(fault_rows):,}")

    # ── DataFrame 변환 및 저장 ───────────────────────────────
    df_normal = pd.DataFrame(normal_rows)
    df_fault = pd.DataFrame(fault_rows)
    df_all = pd.concat([df_normal, df_fault], ignore_index=True)

    df_normal.to_csv("data/normal_samples2.csv", index=False)
    df_fault.to_csv("data/fault_samples2.csv", index=False)
    df_all.to_csv("data/all_samples2.csv", index=False)

    print(f"\n✅ 저장 완료")
    print(f"   data/normal_samples2.csv  : {len(df_normal):,}행")
    print(f"   data/fault_samples2.csv   : {len(df_fault):,}행")
    print(f"   data/all_samples2.csv     : {len(df_all):,}행")

    print(f"\n── 정상 데이터 기초 통계 ──")
    features = ["fps_avg", "frame_drop_rate", "latency_p95_ms",
                "blur_score_avg", "ocr_fail_rate", "cpu_usage_pct",
                "memory_usage_pct", "network_rtt_ms"]
    print(df_normal[features].describe().round(3).to_string())

    print(f"\n── 장애 유형별 샘플 수 ──")
    print(df_fault["fault_type"].value_counts().to_string())

    return df_normal, df_fault, df_all


if __name__ == "__main__":
    df_normal, df_fault, df_all = generate_all_data()
