"""
TAS-PM LSTM AutoEncoder 학습 스크립트
======================================
목적: CameraHealthSample 시계열 데이터로 정상 패턴 학습
      → 재구성 오차(Reconstruction Error) 기반 이상 감지

입력:  data/normal_samples.csv  (정상 데이터 학습용)
       data/fault_samples.csv   (장애 데이터 평가용)

출력:  model/lstm_ae.pt          (학습된 모델)
       model/scaler.pkl          (정규화 스케일러)
       model/threshold.json      (이상 판단 임계값)
       model/metrics.json        (평가 지표)
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
SEQUENCE_LEN   = 30       # 60분치 시퀀스 (문서 스펙)
BATCH_SIZE     = 64
EPOCHS         = 50   # 로컬 CPU 기준. GPU 환경에서는 30~50으로 늘릴 것
LEARNING_RATE  = 1e-3
HIDDEN_SIZE    = 128
NUM_LAYERS     = 2
DROPOUT        = 0.2
THRESHOLD_PCT  = 95      # 정상 재구성 오차 95th percentile → WARNING 임계값
SEED           = 42

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
    df_normal = pd.read_csv("data/normal_samples.csv")
    df_fault  = pd.read_csv("data/fault_samples.csv")

    print(f"    정상: {len(df_normal):,}행 | 장애: {len(df_fault):,}행")

    # 결측값 처리
    df_normal[FEATURES] = df_normal[FEATURES].fillna(df_normal[FEATURES].median())
    df_fault[FEATURES]  = df_fault[FEATURES].fillna(df_fault[FEATURES].median())

    # 정규화 (정상 데이터 기준으로 fit)
    scaler = StandardScaler()
    normal_scaled = scaler.fit_transform(df_normal[FEATURES].values)
    fault_scaled  = scaler.transform(df_fault[FEATURES].values)

    # 스케일러 저장
    with open("model/scaler_thr95.pkl", "wb") as f:
        pickle.dump(scaler, f)
    print("    스케일러 저장 완료: model/scaler.pkl")

    return normal_scaled, fault_scaled, df_fault


def make_sequences(data: np.ndarray, seq_len: int) -> np.ndarray:
    """슬라이딩 윈도우로 시퀀스 생성 (N, seq_len, features)"""
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
        # x: (batch, seq_len, features)
        _, (hidden, _) = self.lstm(x)
        # hidden: (num_layers, batch, hidden_size) → 마지막 레이어
        return hidden[-1]   # (batch, hidden_size)


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
        # z: (batch, hidden_size) → 시퀀스 복원
        z_rep = z.unsqueeze(1).repeat(1, self.seq_len, 1)  # (batch, seq_len, hidden)
        out, _ = self.lstm(z_rep)
        return self.fc(out)   # (batch, seq_len, features)


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
    """시퀀스별 평균 MSE 반환"""
    model.eval()
    errors = []
    dataset = TensorDataset(torch.tensor(sequences))
    loader  = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

    with torch.no_grad():
        for (x,) in loader:
            x = x.to(device)
            x_hat = model(x)
            mse = ((x - x_hat) ** 2).mean(dim=(1, 2))  # (batch,)
            errors.extend(mse.cpu().numpy().tolist())

    return np.array(errors)


# ══════════════════════════════════════════════════════════════
# 5. 평가
# ══════════════════════════════════════════════════════════════

def evaluate(model, normal_seqs, fault_seqs, df_fault, warning_thr, critical_thr):
    print("\n[4] 평가 중...")

    normal_errors = reconstruction_errors(model, normal_seqs)
    fault_errors  = reconstruction_errors(model, fault_seqs)

    # 장애 라벨 (시퀀스 단위 → 마지막 타임스텝 라벨 사용)
    fault_labels = df_fault["is_fault"].values[SEQUENCE_LEN - 1:]
    fault_labels = fault_labels[:len(fault_errors)]

    # WARNING 임계값 기준 이진 예측
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

    # 오탐 수 (정상인데 WARNING 이상)
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
    with open("model/metrics_thr95.json", "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print("    평가 지표 저장 완료: model/metrics.json")

    return metrics


# ══════════════════════════════════════════════════════════════
# 6. 메인
# ══════════════════════════════════════════════════════════════

def main():
    # 데이터 준비
    normal_scaled, fault_scaled, df_fault = load_and_preprocess()

    print("\n[2] 시퀀스 생성 중...")
    normal_seqs = make_sequences(normal_scaled, SEQUENCE_LEN)
    fault_seqs  = make_sequences(fault_scaled,  SEQUENCE_LEN)
    print(f"    정상 시퀀스: {normal_seqs.shape}")
    print(f"    장애 시퀀스: {fault_seqs.shape}")

    # Train / Val 분리 (시간 순서 유지, 앞 80% 학습)
    # CPU 환경: 최대 5000 시퀀스만 사용
    if len(normal_seqs) > 5000:
        idx = np.random.choice(len(normal_seqs), 5000, replace=False)
        idx.sort()
        normal_seqs = normal_seqs[idx]
    split = int(len(normal_seqs) * 0.8)
    train_seqs = normal_seqs[:split]
    val_seqs   = normal_seqs[split:]

    train_ds = TensorDataset(torch.tensor(train_seqs))
    val_ds   = TensorDataset(torch.tensor(val_seqs))
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False)

    # 모델 초기화
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

    # 학습
    print(f"\n[3] 학습 시작 (epoch={EPOCHS}, seq_len={SEQUENCE_LEN}, hidden={HIDDEN_SIZE})")
    best_val_loss = float("inf")
    for epoch in range(1, EPOCHS + 1):
        train_loss = train(model, train_loader, optimizer, criterion, epoch)

        # Validation loss
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

        # Best 모델 저장
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "model/lstm_ae_thr95.pt")

    print(f"\n    최적 모델 저장 완료: model/lstm_ae.pt (val_loss={best_val_loss:.6f})")

    # 최적 모델 로드
    model.load_state_dict(torch.load("model/lstm_ae_thr95.pt", map_location=device))

    # 임계값 설정 (정상 재구성 오차 분포 기반)
    normal_errors = reconstruction_errors(model, normal_seqs)
    warning_thr  = float(np.percentile(normal_errors, THRESHOLD_PCT))
    critical_thr = float(np.percentile(normal_errors, 99))

    threshold = {
        "warning_threshold":  round(warning_thr, 6),
        "critical_threshold": round(critical_thr, 6),
        "basis": f"정상 재구성 오차 {THRESHOLD_PCT}th / 99th percentile",
        "sequence_len": SEQUENCE_LEN,
        "features": FEATURES,
    }
    with open("model/threshold_thr95.json", "w") as f:
        json.dump(threshold, f, indent=2, ensure_ascii=False)
    print(f"\n    임계값 저장 완료: model/threshold.json")
    print(f"    WARNING  임계값: {warning_thr:.6f}")
    print(f"    CRITICAL 임계값: {critical_thr:.6f}")

    # 평가
    metrics = evaluate(model, normal_seqs, fault_seqs, df_fault, warning_thr, critical_thr)

    print("\n══ 학습 완료 ══")
    print(f"  F1={metrics['f1']:.4f} | ROC-AUC={metrics['roc_auc']:.4f} | 오탐={metrics['false_alarm_count']}건")


if __name__ == "__main__":
    main()
