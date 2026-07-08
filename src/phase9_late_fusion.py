#!/usr/bin/env python3
"""
phase9_late_fusion.py — ARSIP late fusion (0.75 neural : 0.25 rule-based) Model B.

============================ CATATAN PENTING ============================
Skrip ini adalah ARSIP / DOKUMENTASI REPO. Eksekusi SEBENARNYA dilakukan via
SEL KAGGLE INLINE (ditambahkan di bawah sel Model B), memanfaatkan `model` +
`tok` + `te`/`dl_te` yang sudah termuat di memori setelah training Model B.
Logika di file ini IDENTIK dengan sel-sel tersebut (single source of truth:
model class dari phase9_model_b_layer2, pattern dari anchor_patterns).
========================================================================

Late fusion = INFERENCE TIME. Model A & B TIDAK dilatih ulang.
    skor_final(v) = W_NEURAL * P_neural_B(v) + W_RULE * anchor_score(v)
Default W_NEURAL=0.75, W_RULE=0.25 (bisa diubah untuk ablation via --w-neural/--w-rule).

anchor_score(text) -> {vektor: [0,1]} = SHARE bukti anchor per vektor:
    jumlah match anchor vektor v / total match semua vektor.
    Bila teks tak punya anchor sama sekali -> semua 0.0 -> fusion otomatis
    defer ke neural (0.75*P_neural, argmax = argmax neural). Ini disengaja:
    saat rule-based tak bersinyal, jangan ganggu neural.

CATATAN metodologis: anchor dihitung pada `text_clean` (SAMA dgn input neural),
bukan teks mentah, agar kedua komponen menilai instance identik. Split CSV Phase 9
memang hanya membawa text_clean (lihat phase9_data_split.py KEEP).

Input : data/splits/layer2_test.csv + checkpoint model_b_layer2_best.pt
Output: macro-F1 SEBELUM (neural) vs SESUDAH fusion, per-class F1, confusion matrix,
        anchor coverage, delta.
"""
import argparse

import numpy as np
import pandas as pd

from anchor_patterns import detect_vector_hints
from phase9_model_b_layer2 import (make_model_class, build_dataset,
                                   LABEL2ID, ID2LABEL, N_CLASSES, BERT_NAME)


# ============================================================
# ANCHOR SCORE (rule-based, share bukti per vektor)
# ============================================================
def anchor_score(text):
    """{vektor: [0,1]} share bukti anchor. Semua 0.0 bila tak ada anchor -> defer neural."""
    hints  = detect_vector_hints(text)             # {vec: count} hanya vektor yg match
    scores = {v: 0.0 for v in LABEL2ID}
    total  = sum(hints.values())
    if total == 0:
        return scores
    for v, c in hints.items():
        scores[v] = c / total
    return scores


def anchor_matrix(texts):
    """(N, 6) matriks anchor_score selaras urutan id LABEL2ID (0..5)."""
    M = np.zeros((len(texts), N_CLASSES), dtype=float)
    for i, t in enumerate(texts):
        for v, val in anchor_score(t).items():
            M[i, LABEL2ID[v]] = val
    return M


# ============================================================
# NEURAL PROBS (softmax Model B; TIDAK melatih ulang)
# ============================================================
def neural_probs(model, loader, device):
    """(N, 6) softmax probs + gold, urutan loader (test shuffle=False -> stabil)."""
    import torch
    model.eval()
    probs, gold = [], []
    with torch.no_grad():
        for input_ids, attn, y in loader:
            logits = model(input_ids.to(device), attn.to(device))
            probs.append(torch.softmax(logits, dim=1).cpu().numpy())
            gold.extend(y.tolist())
    return np.concatenate(probs, axis=0), np.array(gold)


# ============================================================
# LAPORAN
# ============================================================
def report(tag, gold, pred):
    from sklearn.metrics import (accuracy_score, f1_score,
                                 classification_report, confusion_matrix)
    names   = [ID2LABEL[i] for i in range(N_CLASSES)]
    macro_f1 = f1_score(gold, pred, average="macro", zero_division=0)
    print(f"\n===== {tag} =====", flush=True)
    print(f"  accuracy : {accuracy_score(gold, pred):.4f}", flush=True)
    print(f"  macro-F1 : {macro_f1:.4f}", flush=True)
    print(classification_report(gold, pred, target_names=names, zero_division=0), flush=True)
    print("confusion (baris=gold, kolom=pred):", flush=True)
    print(confusion_matrix(gold, pred, labels=list(range(N_CLASSES))), flush=True)
    return macro_f1


def per_class_f1(gold, pred):
    from sklearn.metrics import f1_score
    return f1_score(gold, pred, average=None, labels=list(range(N_CLASSES)), zero_division=0)


def main():
    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoTokenizer

    ap = argparse.ArgumentParser(description="Late fusion Model B (arsip repo)")
    ap.add_argument("--test",       default="data/splits/layer2_test.csv")
    ap.add_argument("--ckpt",       default="model_b_layer2_best.pt")
    ap.add_argument("--max-len",    type=int,   default=128,  dest="max_len")
    ap.add_argument("--batch-size", type=int,   default=16,   dest="batch_size")
    ap.add_argument("--w-neural",   type=float, default=0.75, dest="w_neural")
    ap.add_argument("--w-rule",     type=float, default=0.25, dest="w_rule")
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(BERT_NAME)
    te  = pd.read_csv(args.test, dtype=str, keep_default_na=False)
    dl_te = DataLoader(build_dataset(te, tok, args.max_len), batch_size=args.batch_size)

    Model = make_model_class()
    model = Model().to(device)
    model.load_state_dict(torch.load(args.ckpt, map_location=device))

    # --- neural probs + anchor matrix (urutan identik: test shuffle=False) ---
    P, gold = neural_probs(model, dl_te, device)
    A = anchor_matrix(te["text_clean"].fillna("").astype(str).tolist())

    gold_csv = te["label"].map(LABEL2ID).to_numpy()
    assert (gold == gold_csv).all(), "Urutan loader != urutan CSV — fusion tak selaras!"

    # --- fusion ---
    pred_neural = P.argmax(1)
    fused       = args.w_neural * P + args.w_rule * A
    pred_fused  = fused.argmax(1)

    f_before = report("SEBELUM fusion (neural saja)", gold, pred_neural)
    f_after  = report(f"SESUDAH fusion ({args.w_neural}:{args.w_rule})", gold, pred_fused)

    # --- fokus phishing + delta per-class ---
    names = [ID2LABEL[i] for i in range(N_CLASSES)]
    f1_b, f1_a = per_class_f1(gold, pred_neural), per_class_f1(gold, pred_fused)
    print("\n== Delta F1 per-class (fusion - neural) ==", flush=True)
    for i, nm in enumerate(names):
        mark = "  <-- phishing" if nm == "phishing_rekayasa_sosial" else ""
        print(f"  {nm:32} {f1_b[i]:.4f} -> {f1_a[i]:.4f} ({f1_a[i]-f1_b[i]:+.4f}){mark}",
              flush=True)

    cov = (A.sum(1) > 0).mean()
    print(f"\nmacro-F1: {f_before:.4f} -> {f_after:.4f} (delta {f_after-f_before:+.4f})",
          flush=True)
    print(f"anchor coverage (baris uji dgn >=1 anchor): {cov*100:.1f}%", flush=True)


if __name__ == "__main__":
    main()
