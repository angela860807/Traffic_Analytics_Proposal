"""
TAS-PM LSTM AutoEncoder 상세 평가 스크립트 (v2)
==========================================
목적:
  1. Lead Time 측정 - 장애 시작 몇 분 전에 감지했는가
  2. 시나리오별 성능 분석 - 어떤 장애를 잘 잡는지

입력:
  data/fault_samples3.csv
  model/lstm_ae_v3_thr999.pt
  model/scaler_v3.pkl
  model/threshold_v3_thr999.json

출력:
  results/lead_time_report_v6_timepattern_precursor.csv
  results/scenario_metrics_v6_timepattern_precursor.csv
  results/evaluation_summary_v6_timepattern_precursor.json
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import precision_score, recall_score, f1_score
import json
import pickle
import os

os.makedirs("results", exist_ok=True)

SEQUENCE_LEN = 30
BATCH_SIZE   = 64
FEATURES = [
    "fps_avg", "frame_drop_rate", "latency_p95_ms",
    "blur_score_avg", "ocr_fail_rate",
    "cpu_usage_pct", "memory_usage_pct", "network_rtt_ms",
]

MODEL_PATH     = "model/lstm_ae_v6_timepattern_precursor_thr999.pt"
SCALER_PATH    = "model/scaler_v6_timepattern_precursor.pkl"
THRESHOLD_PATH = "model/threshold_v6_timepattern_precursor_thr999.json"
FAULT_DATA     = "data/fault_samples6_timepattern_precursor.csv"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"디바이스: {device}")


# ══════════════════════════════════════════════════════════════
# 모델 정의
# ══════════════════════════════════════════════════════════════

class LSTMEncoder(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True,
                            dropout=dropout if num_layers > 1 else 0)
    def forward(self, x):
        _, (h, _) = self.lstm(x)
        return h[-1]

class LSTMDecoder(nn.Module):
    def __init__(self, hidden_size, output_size, seq_len, num_layers, dropout):
        super().__init__()
        self.seq_len = seq_len
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers,
                            batch_first=True,
                            dropout=dropout if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_size, output_size)
    def forward(self, z):
        z_rep = z.unsqueeze(1).repeat(1, self.seq_len, 1)
        out, _ = self.lstm(z_rep)
        return self.fc(out)

class LSTMAutoEncoder(nn.Module):
    def __init__(self, input_size=8, hidden_size=128, num_layers=2,
                 seq_len=30, dropout=0.2):
        super().__init__()
        self.encoder = LSTMEncoder(input_size, hidden_size, num_layers, dropout)
        self.decoder = LSTMDecoder(hidden_size, input_size, seq_len, num_layers, dropout)
    def forward(self, x):
        return self.decoder(self.encoder(x))


# ══════════════════════════════════════════════════════════════
# 유틸
# ══════════════════════════════════════════════════════════════

def load_model_and_config():
    model = LSTMAutoEncoder().to(device)
    model.load_state_dict(torch.load(MODEL_PATH,
                                     map_location=device,
                                     weights_only=True))
    model.eval()

    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)

    with open(THRESHOLD_PATH) as f:
        threshold = json.load(f)

    return model, scaler, threshold


def get_reconstruction_errors(model, sequences: np.ndarray) -> np.ndarray:
    errors = []
    ds = TensorDataset(torch.tensor(sequences, dtype=torch.float32))
    loader = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=False)
    with torch.no_grad():
        for (x,) in loader:
            x = x.to(device)
            x_hat = model(x)
            mse = ((x - x_hat) ** 2).mean(dim=(1, 2))
            errors.extend(mse.cpu().numpy().tolist())
    return np.array(errors)


def make_sequences(data: np.ndarray) -> np.ndarray:
    seqs = []
    for i in range(len(data) - SEQUENCE_LEN + 1):
        seqs.append(data[i:i + SEQUENCE_LEN])
    return np.array(seqs, dtype=np.float32)


# ══════════════════════════════════════════════════════════════
# 1. Lead Time 측정
# ══════════════════════════════════════════════════════════════

def measure_lead_time(model, scaler, warning_thr, df_fault):
    print("\n[1] Lead Time 측정 중...")

    scenario_keys = [
        key for key in df_fault["scenario_key"].dropna().unique()
        if key != "EXTERNAL_TRAFFIC_NORMAL_DEVICE"
    ]

    results = []

    for scenario_key in scenario_keys:
        scenario_mask = df_fault["scenario_key"] == scenario_key
        fault_mask = scenario_mask & (df_fault["fault_phase"] == "FAULT")
        if fault_mask.sum() == 0:
            continue

        scenario_indices = df_fault[scenario_mask].index
        start_idx = scenario_indices.min()
        end_idx = scenario_indices.max()

        df_seg = df_fault.iloc[start_idx:end_idx + 1].reset_index(drop=True)

        if len(df_seg) < SEQUENCE_LEN:
            continue

        scaled = scaler.transform(df_seg[FEATURES].fillna(0).values).astype(np.float32)
        seqs   = make_sequences(scaled)
        errors = get_reconstruction_errors(model, seqs)

        fault_start_in_seg = df_seg[df_seg["fault_phase"] == "FAULT"].index.min()
        fault_start_seq    = max(0, fault_start_in_seg - SEQUENCE_LEN + 1)

        detected_indices = np.where(errors >= warning_thr)[0]

        if len(detected_indices) == 0:
            lead_time = None
            detected  = False
        else:
            first_detection = detected_indices[0]
            lead_time = int(fault_start_seq - first_detection)
            detected  = True

        results.append({
            "fault_type":          scenario_key,
            "fault_start_seq":     int(fault_start_seq),
            "first_detection_seq": int(detected_indices[0]) if detected else None,
            "lead_time_minutes":   lead_time,
            "detected":            detected,
        })

        status = f"{lead_time}분 전 감지" if (detected and lead_time and lead_time > 0) \
                 else ("장애 시작 시점 감지" if detected and lead_time == 0 else None)
        status = status if status is not None \
                 else ("감지 못함" if not detected else "장애 후 감지")
        print(f"  {scenario_key:<35} → {status}")

    df_lead = pd.DataFrame(results)
    df_lead.to_csv("results/lead_time_report_v6_timepattern_precursor.csv", index=False)
    print(f"\n  저장 완료: results/lead_time_report_v6_timepattern_precursor.csv")
    return df_lead


# ══════════════════════════════════════════════════════════════
# 2. 시나리오별 성능 분석
# ══════════════════════════════════════════════════════════════

def analyze_by_scenario(model, scaler, warning_thr, df_fault):
    print("\n[2] 시나리오별 성능 분석 중...")

    scenario_keys = [
        key for key in df_fault["scenario_key"].dropna().unique()
        if key != "EXTERNAL_TRAFFIC_NORMAL_DEVICE"
    ]

    scenario_results = []

    for scenario_key in scenario_keys:
        df_seg = df_fault[df_fault["scenario_key"] == scenario_key].reset_index(drop=True)

        if len(df_seg) < SEQUENCE_LEN:
            continue

        scaled = scaler.transform(df_seg[FEATURES].fillna(0).values).astype(np.float32)
        seqs   = make_sequences(scaled)
        errors = get_reconstruction_errors(model, seqs)

        # Predictive-maintenance label: precursor + actual fault are positive.
        labels = df_seg["risk_label"].values[SEQUENCE_LEN - 1:]
        labels = labels[:len(errors)]
        preds  = (errors >= warning_thr).astype(int)

        p = precision_score(labels, preds, zero_division=0)
        r = recall_score(labels, preds, zero_division=0)
        f = f1_score(labels, preds, zero_division=0)

        scenario_results.append({
            "fault_type": scenario_key,
            "precision":  round(p, 4),
            "recall":     round(r, 4),
            "f1":         round(f, 4),
            "total_seq":  len(errors),
            "risk_seq":   int(labels.sum()),
        })

        print(f"  {scenario_key:<35} P={p:.3f} R={r:.3f} F1={f:.3f}")

    df_scenario = pd.DataFrame(scenario_results)
    df_scenario.to_csv("results/scenario_metrics_v6_timepattern_precursor.csv", index=False)
    print(f"\n  저장 완료: results/scenario_metrics_v6_timepattern_precursor.csv")
    return df_scenario


# ══════════════════════════════════════════════════════════════
# 3. 전체 요약 저장
# ══════════════════════════════════════════════════════════════

def save_summary(df_lead, df_scenario, warning_thr, critical_thr):
    detected = df_lead[df_lead["detected"] == True].copy()

    # lead_time_minutes interpretation:
    #   positive: detected before fault start
    #   zero: detected at fault start
    #   negative: detected after fault start
    early = detected[detected["lead_time_minutes"] > 0]
    same  = detected[detected["lead_time_minutes"] == 0]
    late  = detected[detected["lead_time_minutes"] < 0]

    avg_lead = round(float(early["lead_time_minutes"].mean()), 1) if len(early) > 0 else 0
    max_lead = int(early["lead_time_minutes"].max()) if len(early) > 0 else 0

    late_delay = -late["lead_time_minutes"]
    avg_detection_delay = round(float(late_delay.mean()), 1) if len(late_delay) > 0 else 0
    max_detection_delay = int(late_delay.max()) if len(late_delay) > 0 else 0

    summary = {
        "model":                    MODEL_PATH,
        "warning_threshold":        round(float(warning_thr), 6),
        "critical_threshold":       round(float(critical_thr), 6),
        "scenario_count":           len(df_lead),
        "detected_count":           int(detected.shape[0]),
        "early_detection_count":    len(early),
        "same_time_detection_count": len(same),
        "late_detection_count":      len(late),
        "avg_lead_time_minutes":    avg_lead,
        "max_lead_time_minutes":    max_lead,
        "avg_detection_delay_minutes": avg_detection_delay,
        "max_detection_delay_minutes": max_detection_delay,
        "best_scenario":            df_scenario.loc[df_scenario["f1"].idxmax(), "fault_type"] if len(df_scenario) > 0 else "",
        "worst_scenario":           df_scenario.loc[df_scenario["f1"].idxmin(), "fault_type"] if len(df_scenario) > 0 else "",
        "avg_f1":                   round(float(df_scenario["f1"].mean()), 4) if len(df_scenario) > 0 else 0,
    }

    with open("results/evaluation_summary_v6_timepattern_precursor.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n  저장 완료: results/evaluation_summary_v6_timepattern_precursor.json")
    return summary


# ══════════════════════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════════════════════

def main():
    model, scaler, threshold_cfg = load_model_and_config()
    warning_thr  = threshold_cfg["warning_threshold"]
    critical_thr = threshold_cfg["critical_threshold"]
    print(f"WARNING  임계값: {warning_thr:.6f}")
    print(f"CRITICAL 임계값: {critical_thr:.6f}")

    df_fault = pd.read_csv(FAULT_DATA)
    print(f"장애 데이터: {len(df_fault):,}행")

    df_lead     = measure_lead_time(model, scaler, warning_thr, df_fault)
    df_scenario = analyze_by_scenario(model, scaler, warning_thr, df_fault)
    summary     = save_summary(df_lead, df_scenario, warning_thr, critical_thr)

    print("\n" + "═" * 50)
    print("  평가 최종 요약")
    print("═" * 50)
    print(f"  평균 조기 감지 Lead Time : {summary['avg_lead_time_minutes']}분")
    print(f"  최대 조기 감지 Lead Time : {summary['max_lead_time_minutes']}분")
    print(f"  평균 장애 후 감지 지연   : {summary['avg_detection_delay_minutes']}분")
    print(f"  최대 장애 후 감지 지연   : {summary['max_detection_delay_minutes']}분")
    print(f"  평균 F1         : {summary['avg_f1']}")
    print(f"  가장 잘 잡는 장애: {summary['best_scenario']}")
    print(f"  가장 못 잡는 장애: {summary['worst_scenario']}")
    print("═" * 50)
    print("\n결과 파일:")
    print("  results/lead_time_report_v6_timepattern_precursor.csv")
    print("  results/scenario_metrics_v6_timepattern_precursor.csv")
    print("  results/evaluation_summary_v6_timepattern_precursor.json")


if __name__ == "__main__":
    main()
