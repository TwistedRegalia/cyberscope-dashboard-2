#!/usr/bin/env python3
"""
phase9_model_b_layer2.py — Model B (Layer 2 6-vektor) SKELETON.

Triple-Hybrid (CONTEXT §1) untuk Layer 2 (klasifikasi 6 vektor E-ICTT v2.1):
    IndoBERT-base-p1 (fine-tune penuh) -> BiGRU -> BiLSTM (serial)
    -> masked mean pool -> dropout -> classifier 6 kelas.

Imbalance parah (judi ~7.486 vs deepfake ~107, rasio ~70:1) ditangani via:
  - default: CLASS WEIGHTS balanced inverse-freq  (--loss weighted_ce)
  - opsi:    FOCAL LOSS gamma=2.0                 (--loss focal --focal-gamma 2.0)
    Aktifkan focal bila deepfake/malware test-F1 buruk; tidak perlu rewrite kode.

LR 2e-5, AdamW, early stopping (monitor val macro-F1), simpan best checkpoint.
Metrik: accuracy, macro-F1 (utama), per-class P/R/F1 (sklearn report), CM 6x6.

===================== JALANKAN DI KAGGLE T4 (GPU), BUKAN LOKAL =====================
Input : data/splits/layer2_{train,val,test}.csv  (dari phase9_data_split.py; 9.212 relevan)
Output: checkpoint (model_b_layer2_best.pt) + metrik test di stdout.

CATATAN late fusion (0.75 neural : 0.25 rule-based): TODO TERPISAH — stub
rule_score_layer2() + fuse_predictions() disediakan agar tanda-tangan jelas; jalur
neural dievaluasi dulu, fusion anchor pattern menyusul bersama Model A.
"""
import argparse
import sys

import numpy as np
import pandas as pd

BERT_NAME = "indobenchmark/indobert-base-p1"

LABEL2ID = {
    "phishing_rekayasa_sosial":      0,
    "penipuan_ewallet_qris":         1,
    "malware_apk":                   2,
    "judi_online_pinjol":            3,
    "peretasan_pencurian_identitas": 4,
    "deepfake_penipuan_ai":          5,
}
ID2LABEL  = {v: k for k, v in LABEL2ID.items()}
N_CLASSES = len(LABEL2ID)


# ============================================================
# FOCAL LOSS (opsi bila weighted_ce kurang cukup untuk kelas minoritas)
# ============================================================
def make_focal_loss(weight, gamma=2.0):
    """Kembalikan instance FocalLoss dengan class_weights & gamma dikunci closure."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class FocalLoss(nn.Module):
        def forward(self, logits, targets):
            ce  = F.cross_entropy(logits, targets, weight=weight, reduction="none")
            pt  = torch.exp(-ce)
            return ((1 - pt) ** gamma * ce).mean()

    return FocalLoss()


# ============================================================
# DATASET
# ============================================================
def build_dataset(df, tokenizer, max_len):
    import torch
    from torch.utils.data import TensorDataset
    texts  = df["text_clean"].fillna("").astype(str).tolist()
    labels = df["label"].map(LABEL2ID).astype(int).tolist()
    enc = tokenizer(texts, truncation=True, padding="max_length",
                    max_length=max_len, return_tensors="pt")
    return TensorDataset(enc["input_ids"], enc["attention_mask"],
                         torch.tensor(labels, dtype=torch.long))


# ============================================================
# MODEL: IndoBERT -> BiGRU -> BiLSTM -> classifier 6 kelas
# ============================================================
def make_model_class():
    import torch.nn as nn
    from transformers import AutoModel

    class TripleHybridLayer2(nn.Module):
        def __init__(self, bert_name=BERT_NAME, gru_hidden=256, lstm_hidden=128,
                     n_classes=N_CLASSES, dropout=0.3):
            super().__init__()
            self.bert   = AutoModel.from_pretrained(bert_name)
            h           = self.bert.config.hidden_size                 # 768
            self.bigru  = nn.GRU(h, gru_hidden, batch_first=True, bidirectional=True)
            self.bilstm = nn.LSTM(2 * gru_hidden, lstm_hidden,
                                  batch_first=True, bidirectional=True)
            self.dropout    = nn.Dropout(dropout)
            self.classifier = nn.Linear(2 * lstm_hidden, n_classes)

        def forward(self, input_ids, attention_mask):
            seq    = self.bert(input_ids=input_ids,
                               attention_mask=attention_mask).last_hidden_state  # (B,T,768)
            g, _   = self.bigru(seq)                                             # (B,T,512)
            l, _   = self.bilstm(g)                                              # (B,T,256)
            mask   = attention_mask.unsqueeze(-1).float()
            pooled = (l * mask).sum(1) / mask.sum(1).clamp(min=1e-9)            # masked mean
            return self.classifier(self.dropout(pooled))

    return TripleHybridLayer2


# ============================================================
# EVALUASI
# ============================================================
def evaluate(model, loader, device):
    import torch
    from sklearn.metrics import (accuracy_score, f1_score,
                                 classification_report, confusion_matrix)
    model.eval()
    preds, gold = [], []
    with torch.no_grad():
        for input_ids, attn, y in loader:
            logits = model(input_ids.to(device), attn.to(device))
            preds.extend(logits.argmax(1).cpu().tolist())
            gold.extend(y.tolist())

    target_names = [ID2LABEL[i] for i in range(N_CLASSES)]
    return {
        "accuracy": accuracy_score(gold, preds),
        "macro_f1": f1_score(gold, preds, average="macro", zero_division=0),
        "report":   classification_report(gold, preds,
                                          target_names=target_names, zero_division=0),
        "cm":       confusion_matrix(gold, preds, labels=list(range(N_CLASSES))).tolist(),
    }


def _print_cm(cm):
    short = [ID2LABEL[i].split("_")[0][:8] for i in range(N_CLASSES)]
    header = "             " + " ".join(f"{s:>10}" for s in short)
    print(header, flush=True)
    for i, row in enumerate(cm):
        print(f"  {short[i]:>10}  " + " ".join(f"{v:>10}" for v in row), flush=True)


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
              "Jalankan di Kaggle T4.", file=sys.stderr, flush=True)

    print("[1/3] Memuat tokenizer & CSV ...", flush=True)
    tok = AutoTokenizer.from_pretrained(BERT_NAME)
    tr  = pd.read_csv(args.train, dtype=str, keep_default_na=False)
    va  = pd.read_csv(args.val,   dtype=str, keep_default_na=False)
    te  = pd.read_csv(args.test,  dtype=str, keep_default_na=False)
    print(f"  train={len(tr):,}  val={len(va):,}  test={len(te):,}", flush=True)

    dl_tr = DataLoader(build_dataset(tr, tok, args.max_len),
                       batch_size=args.batch_size, shuffle=True)
    dl_va = DataLoader(build_dataset(va, tok, args.max_len), batch_size=args.batch_size)
    dl_te = DataLoader(build_dataset(te, tok, args.max_len), batch_size=args.batch_size)

    # class weights (balanced inverse-freq) — baseline untuk rasio ~70:1
    y_tr          = tr["label"].map(LABEL2ID).astype(int).to_numpy()
    cw            = compute_class_weight("balanced", classes=np.arange(N_CLASSES), y=y_tr)
    class_weights = torch.tensor(cw, dtype=torch.float, device=device)
    print("\nclass_weights (balanced):", flush=True)
    for i, w in enumerate(cw):
        print(f"  [{i}] {ID2LABEL[i]:40} {w:.4f}", flush=True)

    print(f"\n[2/3] Memuat model IndoBERT ({BERT_NAME}) ...", flush=True)
    Model = make_model_class()
    model = Model(dropout=args.dropout).to(device)
    opt   = torch.optim.AdamW(model.parameters(), lr=args.lr)

    if args.loss == "focal":
        loss_fn = make_focal_loss(weight=class_weights, gamma=args.focal_gamma)
        print(f"Loss: FocalLoss(gamma={args.focal_gamma}, class_weights=balanced)", flush=True)
    else:
        loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights)
        print("Loss: CrossEntropyLoss(class_weights=balanced)", flush=True)

    print(f"\n[3/3] Training dimulai "
          f"(max {args.epochs} epoch, patience {args.patience}, "
          f"batch {args.batch_size}, lr {args.lr}) ...\n", flush=True)

    best_f1, patience_cnt = -1.0, 0
    for epoch in range(1, args.epochs + 1):
        model.train()
        for step, (input_ids, attn, y) in enumerate(dl_tr, 1):
            opt.zero_grad()
            logits = model(input_ids.to(device), attn.to(device))
            loss   = loss_fn(logits, y.to(device))
            loss.backward()
            opt.step()
            if step % args.print_every == 0:
                print(f"  [ep {epoch} step {step}/{len(dl_tr)}] "
                      f"loss={loss.item():.4f}", flush=True)

        val = evaluate(model, dl_va, device)
        print(f"[epoch {epoch}] val macro-F1={val['macro_f1']:.4f}  "
              f"acc={val['accuracy']:.4f}", flush=True)

        if val["macro_f1"] > best_f1:
            best_f1, patience_cnt = val["macro_f1"], 0
            torch.save(model.state_dict(), args.ckpt)
            print(f"  -> best checkpoint disimpan (macro-F1={best_f1:.4f}): {args.ckpt}",
                  flush=True)
        else:
            patience_cnt += 1
            if patience_cnt >= args.patience:
                print(f"  early stopping (patience {args.patience}).", flush=True)
                break

    # ---- evaluasi test dengan best checkpoint ----
    model.load_state_dict(torch.load(args.ckpt, map_location=device))
    test = evaluate(model, dl_te, device)

    print("\n===== TEST (Model B / Layer 2) =====", flush=True)
    print(f"  accuracy  : {test['accuracy']:.4f}", flush=True)
    print(f"  macro-F1  : {test['macro_f1']:.4f}", flush=True)
    print("\nPer-class (precision / recall / F1-score / support):", flush=True)
    print(test["report"], flush=True)
    print("Confusion matrix (baris=gold, kolom=pred):", flush=True)
    _print_cm(test["cm"])


# ============================================================
# LATE FUSION — TODO TERPISAH (0.75 neural : 0.25 rule-based)
# ============================================================
def rule_score_layer2(text):
    """
    TODO: skor per-vektor rule-based dari src/anchor_patterns.py.
    Kembalikan dict {label_str: float} — mis. jumlah anchor hit, dinormalisasi 0-1.
    Dipakai HANYA saat inference; tidak memengaruhi training neural.
    """
    raise NotImplementedError("Late fusion rule-based — TODO terpisah (anchor_patterns).")


def fuse_predictions(p_neural, text, w_neural=0.75, w_rule=0.25):
    """TODO: final[label] = 0.75 * p_neural[label] + 0.25 * rule_score_layer2(text)[label]."""
    scores = rule_score_layer2(text)
    return {k: w_neural * p_neural.get(k, 0.0) + w_rule * v for k, v in scores.items()}


# ============================================================
# CLI
# ============================================================
def main():
    ap = argparse.ArgumentParser(description="Model B — Layer 2 vektor (Kaggle T4)")
    ap.add_argument("--train",       default="data/splits/layer2_train.csv")
    ap.add_argument("--val",         default="data/splits/layer2_val.csv")
    ap.add_argument("--test",        default="data/splits/layer2_test.csv")
    ap.add_argument("--ckpt",        default="model_b_layer2_best.pt")
    ap.add_argument("--max-len",     type=int,   default=128,          dest="max_len")
    ap.add_argument("--batch-size",  type=int,   default=16,           dest="batch_size")
    ap.add_argument("--lr",          type=float, default=2e-5)
    ap.add_argument("--epochs",      type=int,   default=6)
    ap.add_argument("--patience",    type=int,   default=2)
    ap.add_argument("--dropout",     type=float, default=0.3)
    ap.add_argument("--loss",        choices=["weighted_ce", "focal"], default="weighted_ce",
                    help="Fungsi loss: weighted_ce (default) atau focal (bila deepfake/malware F1 buruk)")
    ap.add_argument("--focal-gamma", type=float, default=2.0,          dest="focal_gamma",
                    help="Gamma untuk focal loss (default 2.0; aktif hanya saat --loss focal)")
    ap.add_argument("--print-every", type=int,   default=200,          dest="print_every",
                    help="Cetak loss tiap N step per epoch")
    args = ap.parse_args()
    train(args)


if __name__ == "__main__":
    main()
