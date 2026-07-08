#!/usr/bin/env python3
"""
phase9_data_split.py — Phase 9 Data Split (E-ICTT v2.1)

Membuat DUA split stratified terpisah dari weak_labeled_dataset_v2.csv untuk pipeline
2-lapis (training di Kaggle T4):

  - Layer 1 (Model A): SEMUA baris, target = layer1_label (relevan / tidak_relevan).
  - Layer 2 (Model B): HANYA baris relevan, target = layer2_label (6 vektor).

Stratified 80/10/10 per kelas, seed 42 (reproducible). Fitur teks = text_clean
(input IndoBERT). Output split CSV (train/val/test) per layer + manifest JSON.

CATATAN keterbatasan: kelas deepfake hanya 107 relevan -> test set ~10-11 sampel
(10% dari 107). Estimasi metrik deepfake punya interval kepercayaan lebar; jangan
over-generalisasi (sejalan CONTEXT Temuan #7f/#8).

Cara pakai:
    python src/phase9_data_split.py
Output (data/splits/):
    layer1_{train,val,test}.csv  + layer2_{train,val,test}.csv  + _split_manifest.json
"""
import argparse
import json
import os

import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 42
# Kolom yang dibawa ke file split (unified_id = traceable index; text_clean = fitur).
KEEP = ["unified_id", "platform", "source_category", "vector_hint", "text_clean"]


def stratified_80_10_10(df, label_col, seed):
    """Split 80/10/10 stratified per label. Mengembalikan (train, val, test)."""
    train, temp = train_test_split(
        df, test_size=0.20, stratify=df[label_col], random_state=seed)
    val, test = train_test_split(
        temp, test_size=0.50, stratify=temp[label_col], random_state=seed)
    return train, val, test


def _dist(df, label_col):
    return {k: int(v) for k, v in df[label_col].value_counts().sort_index().items()}


def _save(parts, layer, cols, outdir):
    out = {}
    for name, part in parts.items():
        path = os.path.join(outdir, f"{layer}_{name}.csv")
        part[cols].to_csv(path, index=False)
        out[name] = {"n": len(part), "dist": _dist(part, "label")}
    return out


def main():
    ap = argparse.ArgumentParser(description="Phase 9 stratified data split")
    ap.add_argument("--input", default="data/weak_labeled_dataset_v2.csv")
    ap.add_argument("--outdir", default="data/splits")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    df = pd.read_csv(args.input, dtype=str, keep_default_na=False)
    for c in KEEP + ["layer1_label", "layer2_label"]:
        if c not in df.columns:
            raise SystemExit(f"ERROR: kolom '{c}' tidak ada di {args.input}")
    df["text_clean"] = df["text_clean"].fillna("")
    n_empty = int((df["text_clean"].str.strip() == "").sum())

    print(f"Input: {args.input}  ({len(df):,} baris)  seed={args.seed}")
    print(f"  text_clean kosong: {n_empty} (catat; relevansi=urusan Layer 1)")

    cols = KEEP + ["label"]

    # ---------- Layer 1: semua baris, target relevan/tidak_relevan ----------
    l1 = df.copy()
    l1["label"] = l1["layer1_label"]
    tr1, va1, te1 = stratified_80_10_10(l1, "label", args.seed)
    rep1 = _save({"train": tr1, "val": va1, "test": te1}, "layer1", cols, args.outdir)

    # ---------- Layer 2: hanya relevan, target 6 vektor ----------
    l2 = df[df["layer1_label"] == "relevan"].copy()
    l2["label"] = l2["layer2_label"]
    tr2, va2, te2 = stratified_80_10_10(l2, "label", args.seed)
    rep2 = _save({"train": tr2, "val": va2, "test": te2}, "layer2", cols, args.outdir)

    # ---------- Laporan ----------
    def show(title, total, rep):
        print(f"\n== {title} (total {total:,}) ==")
        labels = sorted(set().union(*[r["dist"].keys() for r in rep.values()]))
        head = f"{'label':32}" + "".join(f"{s:>10}" for s in ("train", "val", "test"))
        print(head)
        for lab in labels:
            row = f"{lab:32}"
            for s in ("train", "val", "test"):
                row += f"{rep[s]['dist'].get(lab, 0):>10}"
            print(row)
        row = f"{'TOTAL':32}"
        for s in ("train", "val", "test"):
            row += f"{rep[s]['n']:>10}"
        print(row)

    show("LAYER 1 — relevance (Model A)", len(l1), rep1)
    show("LAYER 2 — vektor (Model B)", len(l2), rep2)

    deepfake_test = rep2["test"]["dist"].get("deepfake_penipuan_ai", 0)
    print(f"\n[!] Keterbatasan: deepfake test = {deepfake_test} sampel "
          f"(kelas terkecil; CI lebar, jangan over-generalisasi).")

    manifest = {
        "input": args.input, "seed": args.seed, "ratio": "80/10/10",
        "feature_col": "text_clean", "text_clean_empty": n_empty,
        "layer1": {"total": len(l1), "target": "layer1_label", "splits": rep1},
        "layer2": {"total": len(l2), "target": "layer2_label", "splits": rep2},
    }
    mpath = os.path.join(args.outdir, "_split_manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\n[saved] {args.outdir}/layer1_*.csv, layer2_*.csv  + {mpath}")


if __name__ == "__main__":
    main()
