"""
TAS-PM LSTM AutoEncoder 학습 스크립트
======================================
목적: CameraHealthSample 시계열 데이터로 정상 패턴 학습
      → 재구성 오차(Reconstruction Error) 기반 이상 감지

입력:  data/normal_samples2.csv  (정상 데이터 학습용 - v2: 카메라 10대, 30일)
       data/fault_samples2.csv   (장애 데이터 평가용)

출력:  model/lstm_ae_v2_ep25_thr999.pt      (학습된 모델)
       model/scaler_v2.pkl                   (정규화 스케일러)
       model/threshold_v2_ep25_thr999.json  (이상 판단 임계값)
       model/metrics_v2_ep25_thr999.json    (평가 지표)

변경 이력:
  v1:             카메라 3대, 14일, ep=50, thr=97
  v2 ep50:        카메라 10대, 30일, ep=50 → 과적합 (F1=0.2060)
  v2 ep25 thr97:  ep=25 → 오탐 12,960건
  v2 ep25 thr99:  thr=99.5 → 오탐 2,160건, WARNING>CRITICAL 역전
  v2 ep25 thr999: thr=99.9, critical=99.99 → 현재 버전
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import json
import pickle
import os

# ── 설정 ───────────────────────────────────────────────────────
SEQUENCE_LEN   = 30
BATCH_SIZE     = 64
EPOCHS         = 25
LEARNING_RATE  = 1e-3
HIDDEN_SIZE    = 128
NUM_LAYERS     = 2
DROPOUT        = 0.2
WARNING_PCT    = 99.9    # 정상 재구성 오차 99.9th → WARNING 임계값
CRITICAL_PCT   = 99.99   # 정상 재구성 오차 99.99th → CRITICAL 임계값
SEED           = 42

MODEL_PATH     = "model/lstm_ae_v2_ep25_thr999.pt"
SCALER_PATH    = "model/scaler_v2.pkl"
THRESHOLD_PATH = "model/threshold_v2_ep25_thr999.json"
METRICS_PATH   = "model/metrics_v2_ep25_thr999.json"

FEATURES = [
    "fps_avg",
    "frame_drop_rate",
    "latency_p95_ms",
    "blur_score_avg",
    "ocr_fail_rate",
    "cpu_usage_pct",
    "memory_usage_pct",
    "network_rtt_ms",
]

torch.manual_seed(SEED)
np.random.seed(SEED)
os.makedirs("model", exist_ok=True)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"디바이스: {device}")


# ══════════════════════════════════════════════════════════════
# 1. 데이터 로드 및 전처리
# ══════════════════════════════════════════════════════════════

def load_and_preprocess():
    print("\n[1] 데이터 로드 중...")
    df_normal = pd.read_csv("data/normal_samples2.csv")
    df_fault  = pd.read_csv("data/fault_samples2.csv")

    print(f"    정상: {len(df_normal):,}행 | 장애: {len(df_fault):,}행")

    df_normal[FEATURES] = df_normal[FEATURES].fillna(df_normal[FEATURES].median())
    df_fault[FEATURES]  = df_fault[FEATURES].fillna(df_fault[FEATURES].median())

    scaler = StandardScaler()
    normal_scaled = scaler.fit_transform(df_normal[FEATURES].values)
    fault_scaled  = scaler.transform(df_fault[FEATURES].values)

    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    print(f"    스케일러 저장 완료: {SCALER_PATH}")

    return normal_scaled, fault_scaled, df_fault


def make_sequences(data: np.ndarray, seq_len: int) -> np.ndarray:
    seqs = []
    for i in range(len(data) - seq_len + 1):
        seqs.append(data[i:i + seq_len])
    return np.array(seqs, dtype=np.float32)


# ══════════════════════════════════════════════════════════════
# 2. LSTM AutoEncoder 모델 정의
# ══════════════════════════════════════════════════════════════

class LSTMEncoder(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )

    def forward(self, x):
        _, (hidden, _) = self.lstm(x)
        return hidden[-1]


class LSTMDecoder(nn.Module):
    def __init__(self, hidden_size, output_size, seq_len, num_layers, dropout):
        super().__init__()
        self.seq_len = seq_len
        self.lstm = nn.LSTM(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, z):
        z_rep = z.unsqueeze(1).repeat(1, self.seq_len, 1)
        out, _ = self.lstm(z_rep)
        return self.fc(out)


class LSTMAutoEncoder(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, seq_len, dropout):
        super().__init__()
        self.encoder = LSTMEncoder(input_size, hidden_size, num_layers, dropout)
        self.decoder = LSTMDecoder(hidden_size, input_size, seq_len, num_layers, dropout)

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)


# ══════════════════════════════════════════════════════════════
# 3. 학습
# ══════════════════════════════════════════════════════════════

def train(model, loader, optimizer, criterion, epoch):
    model.train()
    total_loss = 0
    for batch in loader:
        x = batch[0].to(device)
        optimizer.zero_grad()
        x_hat = model(x)
        loss = criterion(x_hat, x)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)


# ══════════════════════════════════════════════════════════════
# 4. 재구성 오차 계산
# ══════════════════════════════════════════════════════════════

def reconstruction_errors(model, sequences: np.ndarray) -> np.ndarray:
    model.eval()
    errors = []
    dataset = TensorDataset(torch.tensor(sequences))
    loader  = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

    with torch.no_grad():
        for (x,) in loader:
            x = x.to(device)
            x_hat = model(x)
            mse = ((x - x_hat) ** 2).mean(dim=(1, 2))
            errors.extend(mse.cpu().numpy().tolist())

    return np.array(errors)


# ══════════════════════════════════════════════════════════════
# 5. 평가
# ══════════════════════════════════════════════════════════════

def evaluate(model, normal_seqs, fault_seqs, df_fault, warning_thr, critical_thr):
    print("\n[4] 평가 중...")

    normal_errors = reconstruction_errors(model, normal_seqs)
    fault_errors  = reconstruction_errors(model, fault_seqs)

    fault_labels = df_fault["is_fault"].values[SEQUENCE_LEN - 1:]
    fault_labels = fault_labels[:len(fault_errors)]

    all_errors = np.concatenate([normal_errors, fault_errors])
    all_labels = np.concatenate([
        np.zeros(len(normal_errors)),
        fault_labels
    ])
    all_preds = (all_errors >= warning_thr).astype(int)

    precision = precision_score(all_labels, all_preds, zero_division=0)
    recall    = recall_score(all_labels, all_preds, zero_division=0)
    f1        = f1_score(all_labels, all_preds, zero_division=0)

    try:
        auc = roc_auc_score(all_labels, all_errors)
    except Exception:
        auc = 0.0

    false_alarms = int((normal_errors >= warning_thr).sum())

    print(f"    Precision : {precision:.4f}")
    print(f"    Recall    : {recall:.4f}")
    print(f"    F1        : {f1:.4f}")
    print(f"    ROC-AUC   : {auc:.4f}")
    print(f"    오탐 수    : {false_alarms}건 / {len(normal_errors)}개 정상 시퀀스")

    metrics = {
        "precision": round(precision, 4),
        "recall":    round(recall, 4),
        "f1":        round(f1, 4),
        "roc_auc":   round(auc, 4),
        "false_alarm_count": false_alarms,
        "normal_seq_count":  len(normal_errors),
        "fault_seq_count":   len(fault_errors),
        "warning_threshold": round(float(warning_thr), 6),
        "critical_threshold": round(float(critical_thr), 6),
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"    평가 지표 저장 완료: {METRICS_PATH}")

    return metrics


# ══════════════════════════════════════════════════════════════
# 6. 메인
# ══════════════════════════════════════════════════════════════

def main():
    normal_scaled, fault_scaled, df_fault = load_and_preprocess()

    print("\n[2] 시퀀스 생성 중...")
    normal_seqs = make_sequences(normal_scaled, SEQUENCE_LEN)
    fault_seqs  = make_sequences(fault_scaled,  SEQUENCE_LEN)
    print(f"    정상 시퀀스: {normal_seqs.shape}")
    print(f"    장애 시퀀스: {fault_seqs.shape}")

    # Train / Val 분리 (시간 순서 유지, 앞 80% 학습)
    split = int(len(normal_seqs) * 0.8)
    train_seqs = normal_seqs[:split]
    val_seqs   = normal_seqs[split:]

    train_ds = TensorDataset(torch.tensor(train_seqs))
    val_ds   = TensorDataset(torch.tensor(val_seqs))
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False)

    input_size = len(FEATURES)
    model = LSTMAutoEncoder(
        input_size=input_size,
        hidden_size=HIDDEN_SIZE,
        num_layers=NUM_LAYERS,
        seq_len=SEQUENCE_LEN,
        dropout=DROPOUT,
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.MSELoss()
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", patience=3, factor=0.5
    )

    print(f"\n[3] 학습 시작 (epoch={EPOCHS}, seq_len={SEQUENCE_LEN}, hidden={HIDDEN_SIZE})")
    best_val_loss = float("inf")
    for epoch in range(1, EPOCHS + 1):
        train_loss = train(model, train_loader, optimizer, criterion, epoch)

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for (x,) in val_loader:
                x = x.to(device)
                val_loss += criterion(model(x), x).item()
        val_loss /= len(val_loader)
        scheduler.step(val_loss)

        if epoch % 5 == 0 or epoch == 1:
            print(f"    Epoch {epoch:3d}/{EPOCHS} | train={train_loss:.6f} | val={val_loss:.6f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), MODEL_PATH)

    print(f"\n    최적 모델 저장 완료: {MODEL_PATH} (val_loss={best_val_loss:.6f})")

    model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=True))

    # 임계값 계산 (WARNING < CRITICAL 보장)
    normal_errors = reconstruction_errors(model, normal_seqs)
    warning_thr  = float(np.percentile(normal_errors, WARNING_PCT))
    critical_thr = float(np.percentile(normal_errors, CRITICAL_PCT))

    # WARNING > CRITICAL 역전 방지
    if warning_thr >= critical_thr:
        critical_thr = warning_thr * 1.1
        print(f"    ⚠️  WARNING >= CRITICAL 역전 감지 → CRITICAL을 WARNING × 1.1로 조정")

    threshold = {
        "warning_threshold":  round(warning_thr, 6),
        "critical_threshold": round(critical_thr, 6),
        "basis": f"normal reconstruction error {WARNING_PCT}th / {CRITICAL_PCT}th percentile",
        "sequence_len": SEQUENCE_LEN,
        "features": FEATURES,
    }
    with open(THRESHOLD_PATH, "w") as f:
        json.dump(threshold, f, indent=2, ensure_ascii=False)
    print(f"\n    임계값 저장 완료: {THRESHOLD_PATH}")
    print(f"    WARNING  임계값: {warning_thr:.6f}")
    print(f"    CRITICAL 임계값: {critical_thr:.6f}")

    metrics = evaluate(model, normal_seqs, fault_seqs, df_fault, warning_thr, critical_thr)

    print("\n══ 학습 완료 ══")
    print(f"  F1={metrics['f1']:.4f} | ROC-AUC={metrics['roc_auc']:.4f} | 오탐={metrics['false_alarm_count']}건")


if __name__ == "__main__":
    main()