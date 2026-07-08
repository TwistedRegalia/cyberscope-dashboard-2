#!/usr/bin/env python3
"""
phase9_model_a_layer1.py — Model A (Layer 1 relevance) SKELETON.

Triple-Hybrid (CONTEXT §1) untuk Layer 1 (relevan / tidak_relevan):
    IndoBERT-base-p1 (fine-tune penuh) -> BiGRU -> BiLSTM (serial)
    -> masked mean pool -> dropout -> classifier biner.

Imbalance relevan(9.212) : tidak_relevan(46.088) ditangani via CLASS WEIGHTS
(inverse frequency, 'balanced'). LR 2e-5, early stopping (monitor val macro-F1),
simpan best checkpoint. Metrik: accuracy, macro-F1, RECALL kelas relevan (diperhatikan
khusus), confusion matrix.

===================== JALANKAN DI KAGGLE T4 (GPU), BUKAN LOKAL =====================
Dependencies (Kaggle biasanya sudah ada; jika tidak: pip install):
    torch, transformers>=4.30, scikit-learn, pandas, numpy
Device: otomatis pakai CUDA bila ada (skeleton akan WARNING bila CPU-only — training
penuh di CPU tidak praktis).

Input: data/splits/layer1_{train,val,test}.csv  (dari phase9_data_split.py)
Output: checkpoint best (model_a_layer1_best.pt) + metrik test di stdout.

CATATAN late fusion (0,75 neural : 0,25 rule-based): di-skeleton ini ditandai sebagai
TODO TERPISAH (lihat `rule_score_layer1` + `fuse_predictions`) agar jalur NEURAL bisa
jalan & dievaluasi dulu; fusion anchor pattern menyusul.
"""
import argparse
import sys

import numpy as np
import pandas as pd

# --- dependency neural di-import lazy di main() agar file bisa di-lint tanpa torch ---

BERT_NAME = "indobenchmark/indobert-base-p1"
LABEL2ID = {"tidak_relevan": 0, "relevan": 1}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}


# ============================================================
# DATASET
# ============================================================
def build_dataset(df, tokenizer, max_len):
    import torch
    from torch.utils.data import TensorDataset
    texts = df["text_clean"].fillna("").astype(str).tolist()
    labels = df["label"].map(LABEL2ID).astype(int).tolist()
    enc = tokenizer(texts, truncation=True, padding="max_length",
                    max_length=max_len, return_tensors="pt")
    return TensorDataset(enc["input_ids"], enc["attention_mask"],
                         torch.tensor(labels, dtype=torch.long))


# ============================================================
# MODEL: IndoBERT -> BiGRU -> BiLSTM -> classifier
# ============================================================
def make_model_class():
    import torch.nn as nn
    from transformers import AutoModel

    class TripleHybridLayer1(nn.Module):
        def __init__(self, bert_name=BERT_NAME, gru_hidden=256, lstm_hidden=128,
                     n_classes=2, dropout=0.3):
            super().__init__()
            self.bert = AutoModel.from_pretrained(bert_name)
            h = self.bert.config.hidden_size                    # 768
            self.bigru = nn.GRU(h, gru_hidden, batch_first=True, bidirectional=True)
            self.bilstm = nn.LSTM(2 * gru_hidden, lstm_hidden,
                                  batch_first=True, bidirectional=True)
            self.dropout = nn.Dropout(dropout)
            self.classifier = nn.Linear(2 * lstm_hidden, n_classes)

        def forward(self, input_ids, attention_mask):
            seq = self.bert(input_ids=input_ids,
                            attention_mask=attention_mask).last_hidden_state  # (B,T,768)
            g, _ = self.bigru(seq)                                            # (B,T,2*gru)
            l, _ = self.bilstm(g)                                             # (B,T,2*lstm)
            mask = attention_mask.unsqueeze(-1).float()
            pooled = (l * mask).sum(1) / mask.sum(1).clamp(min=1e-9)          # masked mean
            return self.classifier(self.dropout(pooled))

    return TripleHybridLayer1


# ============================================================
# EVALUASI
# ============================================================
def evaluate(model, loader, device):
    import torch
    from sklearn.metrics import (accuracy_score, f1_score, recall_score,
                                 confusion_matrix)
    model.eval()
    preds, gold = [], []
    with torch.no_grad():
        for input_ids, attn, y in loader:
            logits = model(input_ids.to(device), attn.to(device))
            preds.extend(logits.argmax(1).cpu().tolist())
            gold.extend(y.tolist())
    return {
        "accuracy": accuracy_score(gold, preds),
        "macro_f1": f1_score(gold, preds, average="macro"),
        "recall_relevan": recall_score(gold, preds, pos_label=LABEL2ID["relevan"],
                                       zero_division=0),
        "confusion_matrix": confusion_matrix(
            gold, preds, labels=[0, 1]).tolist(),
    }


# ============================================================
# TRAINING
# ============================================================
def train(args):
    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoTokenizer
    from sklearn.utils.class_weight import compute_class_weight

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda":
        print("[WARNING] CUDA tidak terdeteksi — fine-tune IndoBERT di CPU TIDAK praktis. "
              "Jalankan di Kaggle T4.", file=sys.stderr)

    tok = AutoTokenizer.from_pretrained(BERT_NAME)
    tr = pd.read_csv(args.train, dtype=str, keep_default_na=False)
    va = pd.read_csv(args.val, dtype=str, keep_default_na=False)
    te = pd.read_csv(args.test, dtype=str, keep_default_na=False)

    dl_tr = DataLoader(build_dataset(tr, tok, args.max_len),
                       batch_size=args.batch_size, shuffle=True)
    dl_va = DataLoader(build_dataset(va, tok, args.max_len), batch_size=args.batch_size)
    dl_te = DataLoader(build_dataset(te, tok, args.max_len), batch_size=args.batch_size)

    # class weights (inverse frequency, balanced) untuk imbalance ~5:1
    y_tr = tr["label"].map(LABEL2ID).astype(int).to_numpy()
    cw = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_tr)
    class_weights = torch.tensor(cw, dtype=torch.float, device=device)
    print(f"class_weights (tidak_relevan, relevan) = {cw.round(3).tolist()}")

    Model = make_model_class()
    model = Model(dropout=args.dropout).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights)

    best_f1, patience = -1.0, 0
    for epoch in range(1, args.epochs + 1):
        model.train()
        for input_ids, attn, y in dl_tr:
            opt.zero_grad()
            logits = model(input_ids.to(device), attn.to(device))
            loss = loss_fn(logits, y.to(device))
            loss.backward()
            opt.step()
        val = evaluate(model, dl_va, device)
        print(f"[epoch {epoch}] val macro-F1={val['macro_f1']:.4f} "
              f"recall_relevan={val['recall_relevan']:.4f} acc={val['accuracy']:.4f}")
        # early stopping monitor val macro-F1
        if val["macro_f1"] > best_f1:
            best_f1, patience = val["macro_f1"], 0
            torch.save(model.state_dict(), args.ckpt)
            print(f"  -> best checkpoint disimpan: {args.ckpt}")
        else:
            patience += 1
            if patience >= args.patience:
                print(f"  early stopping (patience {args.patience}).")
                break

    # evaluasi test dgn best checkpoint
    model.load_state_dict(torch.load(args.ckpt, map_location=device))
    test = evaluate(model, dl_te, device)
    print("\n===== TEST (Model A / Layer 1) =====")
    print(f"  accuracy        : {test['accuracy']:.4f}")
    print(f"  macro-F1        : {test['macro_f1']:.4f}")
    print(f"  recall relevan  : {test['recall_relevan']:.4f}")
    print(f"  confusion (rows=gold [tidak_relevan, relevan]): {test['confusion_matrix']}")


# ============================================================
# LATE FUSION — TODO TERPISAH (0,75 neural : 0,25 rule-based)
# ============================================================
def rule_score_layer1(text):
    """
    TODO: skor relevansi rule-based dari src/anchor_patterns.py
    (mis. has_anchor(text) -> 1.0/0.0, atau normalisasi jumlah anchor).
    Dipakai HANYA saat inference untuk late fusion; tidak memengaruhi training neural.
    """
    raise NotImplementedError("Late fusion rule-based — TODO terpisah (anchor_patterns).")


def fuse_predictions(p_neural_relevan, text, w_neural=0.75, w_rule=0.25):
    """TODO: final = 0.75 * P_neural(relevan) + 0.25 * rule_score_layer1(text)."""
    return w_neural * p_neural_relevan + w_rule * rule_score_layer1(text)


def main():
    ap = argparse.ArgumentParser(description="Model A — Layer 1 relevance (Kaggle T4)")
    ap.add_argument("--train", default="data/splits/layer1_train.csv")
    ap.add_argument("--val", default="data/splits/layer1_val.csv")
    ap.add_argument("--test", default="data/splits/layer1_test.csv")
    ap.add_argument("--ckpt", default="model_a_layer1_best.pt")
    ap.add_argument("--max-len", type=int, default=128, dest="max_len")
    ap.add_argument("--batch-size", type=int, default=16, dest="batch_size")
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--patience", type=int, default=2)
    ap.add_argument("--dropout", type=float, default=0.3)
    args = ap.parse_args()
    train(args)


if __name__ == "__main__":
    main()
