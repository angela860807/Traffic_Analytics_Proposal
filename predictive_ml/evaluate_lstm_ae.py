"""
TAS-PM LSTM AutoEncoder 상세 평가 스크립트
==========================================
목적:
  1. Lead Time 측정 - 장애 시작 몇 분 전에 감지했는가
  2. 시나리오별 성능 분석 - 어떤 장애를 잘 잡는지
  3. 오탐 시간대 분석 - 언제 오탐이 많이 발생하는지

입력:
  data/fault_samples.csv
  model/lstm_ae.pt
  model/scaler.pkl
  model/threshold.json

출력:
  results/lead_time_report.csv     : 시나리오별 Lead Time
  results/scenario_metrics.csv     : 시나리오별 F1/Precision/Recall
  results/evaluation_summary.json  : 전체 요약
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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"디바이스: {device}")


# ══════════════════════════════════════════════════════════════
# 모델 정의 (train_lstm_ae.py 와 동일)
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
    # 모델
    model = LSTMAutoEncoder().to(device)
    model.load_state_dict(torch.load("model/lstm_ae.pt",
                                     map_location=device,
                                     weights_only=True))
    model.eval()

    # 스케일러
    with open("model/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    # 임계값
    with open("model/threshold_thr95.json") as f:
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
    """
    시나리오별로 장애 시작 시각 vs 모델 첫 감지 시각 차이 계산
    각 시나리오 구조: 정상(120분) → 장애(240분) → 회복(120분)
    """
    print("\n[1] Lead Time 측정 중...")

    # EXTERNAL_TRAFFIC은 장비 정상이므로 제외
    fault_types = [ft for ft in df_fault["fault_type"].unique()
                   if ft not in ("NORMAL", "EXTERNAL_TRAFFIC_NORMAL_DEVICE")]

    results = []

    for fault_type in fault_types:
        # 해당 시나리오 데이터만 추출
        df_scenario = df_fault[
            (df_fault["fault_type"].isin([fault_type, "NORMAL"])) &
            (df_fault.index >= df_fault[df_fault["fault_type"] == fault_type].index.min() - 120)
        ].copy().reset_index(drop=True)

        # 시나리오 전체 데이터 (정상 앞뒤 포함)
        # fault_samples는 시나리오별로 순서대로 저장됨
        # → fault_type 변하는 지점 찾기
        scenario_mask = df_fault["fault_type"] == fault_type
        if scenario_mask.sum() == 0:
            continue

        # 해당 시나리오 인덱스 범위
        fault_indices = df_fault[scenario_mask].index
        start_idx = max(0, fault_indices.min() - 120)  # 앞 정상 120분 포함
        end_idx   = fault_indices.max() + 120           # 뒤 회복 120분 포함

        df_seg = df_fault.iloc[start_idx:end_idx + 1].reset_index(drop=True)

        if len(df_seg) < SEQUENCE_LEN:
            continue

        # 스케일링 및 시퀀스 생성
        scaled = scaler.transform(df_seg[FEATURES].fillna(0).values).astype(np.float32)
        seqs   = make_sequences(scaled)
        errors = get_reconstruction_errors(model, seqs)

        # 장애 시작 인덱스 (시퀀스 기준)
        fault_start_in_seg = df_seg[df_seg["fault_type"] == fault_type].index.min()
        fault_start_seq    = max(0, fault_start_in_seg - SEQUENCE_LEN + 1)

        # 모델이 WARNING 이상으로 처음 감지한 시퀀스 인덱스
        detected_indices = np.where(errors >= warning_thr)[0]

        if len(detected_indices) == 0:
            lead_time = None
            detected  = False
        else:
            first_detection = detected_indices[0]
            # Lead Time = 장애 시작 시퀀스 - 첫 감지 시퀀스 (분 단위)
            lead_time = int(fault_start_seq - first_detection)
            detected  = True

        results.append({
            "fault_type":         fault_type,
            "fault_start_seq":    int(fault_start_seq),
            "first_detection_seq": int(detected_indices[0]) if detected else None,
            "lead_time_minutes":  lead_time,
            "detected":           detected,
        })

        status = f"{lead_time}분 전 감지" if (detected and lead_time and lead_time > 0) \
                 else ("감지 못함" if not detected else "장애 후 감지")
        print(f"  {fault_type:<30} → {status}")

    df_lead = pd.DataFrame(results)
    df_lead.to_csv("results/lead_time_report.csv", index=False)
    print(f"\n  저장 완료: results/lead_time_report.csv")
    return df_lead


# ══════════════════════════════════════════════════════════════
# 2. 시나리오별 성능 분석
# ══════════════════════════════════════════════════════════════

def analyze_by_scenario(model, scaler, warning_thr, df_fault):
    """시나리오별 Precision / Recall / F1 계산"""
    print("\n[2] 시나리오별 성능 분석 중...")

    fault_types = [ft for ft in df_fault["fault_type"].unique()
                   if ft != "NORMAL"]

    scenario_results = []

    for fault_type in fault_types:
        # 해당 시나리오 + 같이 있는 NORMAL 구간
        mask = df_fault["fault_type"].isin([fault_type, "NORMAL"])
        df_seg = df_fault[mask].reset_index(drop=True)

        if len(df_seg) < SEQUENCE_LEN:
            continue

        scaled = scaler.transform(df_seg[FEATURES].fillna(0).values).astype(np.float32)
        seqs   = make_sequences(scaled)
        errors = get_reconstruction_errors(model, seqs)

        labels = df_seg["is_fault"].values[SEQUENCE_LEN - 1:]
        labels = labels[:len(errors)]
        preds  = (errors >= warning_thr).astype(int)

        p = precision_score(labels, preds, zero_division=0)
        r = recall_score(labels, preds, zero_division=0)
        f = f1_score(labels, preds, zero_division=0)

        scenario_results.append({
            "fault_type": fault_type,
            "precision":  round(p, 4),
            "recall":     round(r, 4),
            "f1":         round(f, 4),
            "total_seq":  len(errors),
            "fault_seq":  int(labels.sum()),
        })

        print(f"  {fault_type:<35} P={p:.3f} R={r:.3f} F1={f:.3f}")

    df_scenario = pd.DataFrame(scenario_results)
    df_scenario.to_csv("results/scenario_metrics.csv", index=False)
    print(f"\n  저장 완료: results/scenario_metrics.csv")
    return df_scenario


# ══════════════════════════════════════════════════════════════
# 3. 전체 요약 저장
# ══════════════════════════════════════════════════════════════

def save_summary(df_lead, df_scenario, warning_thr, critical_thr):
    detected   = df_lead[df_lead["detected"] == True]
    early      = detected[detected["lead_time_minutes"] > 0]
    avg_lead   = round(float(early["lead_time_minutes"].mean()), 1) if len(early) > 0 else 0
    max_lead   = int(early["lead_time_minutes"].max()) if len(early) > 0 else 0

    summary = {
        "warning_threshold":        round(float(warning_thr), 6),
        "critical_threshold":       round(float(critical_thr), 6),
        "scenario_count":           len(df_lead),
        "detected_count":           int(detected.shape[0]),
        "early_detection_count":    len(early),
        "avg_lead_time_minutes":    avg_lead,
        "max_lead_time_minutes":    max_lead,
        "best_scenario":            df_scenario.loc[df_scenario["f1"].idxmax(), "fault_type"] if len(df_scenario) > 0 else "",
        "worst_scenario":           df_scenario.loc[df_scenario["f1"].idxmin(), "fault_type"] if len(df_scenario) > 0 else "",
        "avg_f1":                   round(float(df_scenario["f1"].mean()), 4) if len(df_scenario) > 0 else 0,
    }

    with open("results/evaluation_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n  저장 완료: results/evaluation_summary.json")
    return summary


# ══════════════════════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════════════════════

def main():
    # 모델·설정 로드
    model, scaler, threshold_cfg = load_model_and_config()
    warning_thr  = threshold_cfg["warning_threshold"]
    critical_thr = threshold_cfg["critical_threshold"]
    print(f"WARNING 임계값: {warning_thr:.6f}")
    print(f"CRITICAL 임계값: {critical_thr:.6f}")

    # 장애 데이터 로드
    df_fault = pd.read_csv("data/fault_samples.csv")
    print(f"장애 데이터: {len(df_fault):,}행")

    # 분석 실행
    df_lead     = measure_lead_time(model, scaler, warning_thr, df_fault)
    df_scenario = analyze_by_scenario(model, scaler, warning_thr, df_fault)
    summary     = save_summary(df_lead, df_scenario, warning_thr, critical_thr)

    # 최종 출력
    print("\n" + "═" * 50)
    print("  평가 최종 요약")
    print("═" * 50)
    print(f"  평균 Lead Time  : {summary['avg_lead_time_minutes']}분")
    print(f"  최대 Lead Time  : {summary['max_lead_time_minutes']}분")
    print(f"  평균 F1         : {summary['avg_f1']}")
    print(f"  가장 잘 잡는 장애: {summary['best_scenario']}")
    print(f"  가장 못 잡는 장애: {summary['worst_scenario']}")
    print("═" * 50)
    print("\n결과 파일:")
    print("  results/lead_time_report.csv")
    print("  results/scenario_metrics.csv")
    print("  results/evaluation_summary.json")


if __name__ == "__main__":
    main()
