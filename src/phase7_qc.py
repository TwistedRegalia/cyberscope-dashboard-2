#!/usr/bin/env python3
"""
phase7_qc.py — Quality control untuk Labeling Functions Phase 7 (LFAnalysis).

Memvalidasi klaim report (coverage, conflict) secara independen pada KODE yang
sudah diintegrasikan. TIDAK menulis ulang weak_labeled_dataset.csv — read-only QC.

Metrik (snorkel LFAnalysis):
  - Coverage  : % baris di mana LF tidak ABSTAIN
  - Overlaps  : % baris di mana LF firing bersama >=1 LF lain
  - Conflicts : % baris di mana LF firing & ada LF lain yang vote BERBEDA
  - Dead LF   : LF dengan coverage 0 (perlu dibuang/diperbaiki)

Output: docs/phase7_qc_report.md
Cara pakai: python src/phase7_qc.py
"""
import sys
import numpy as np
import pandas as pd
from snorkel.labeling import PandasLFApplier, LFAnalysis

sys.path.insert(0, "src")
import phase7_labeling as L
import phase7_layer1 as L1

REPORT = "docs/phase7_qc_report.md"


def _coverage(Lm):
    return (Lm != -1).any(axis=1).mean()


def _overlap(Lm):
    fired = (Lm != -1).sum(axis=1)
    return (fired >= 2).mean()


def _conflict_distinct(Lm):
    """% baris dgn >=2 label BERBEDA yang firing (di antara LF non-abstain)."""
    out = 0
    for row in Lm:
        vals = set(v for v in row if v != -1)
        if len(vals) >= 2:
            out += 1
    return out / len(Lm)


def main():
    print("Loading preprocessed_dataset.csv ...")
    df = pd.read_csv("data/preprocessed_dataset.csv")
    df["text_clean"] = df["text_clean"].fillna("")
    n = len(df)

    vec_lfs = L.ALL_LFS
    pos_lfs = L1.POSITIVE_LFS
    neg_lfs = L1.NEGATIVE_LFS
    l1_lfs = pos_lfs + neg_lfs

    print(f"Applying {len(vec_lfs)} vector LFs + {len(l1_lfs)} Layer-1 LFs over {n:,} rows ...")
    Lvec = PandasLFApplier(vec_lfs).apply(df=df, progress_bar=False)
    Ll1 = PandasLFApplier(l1_lfs).apply(df=df, progress_bar=False)

    vec_sum = LFAnalysis(Lvec, vec_lfs).lf_summary()
    l1_sum = LFAnalysis(Ll1, l1_lfs).lf_summary()

    # agregat
    vec_cov = _coverage(Lvec)
    vec_ovl = _overlap(Lvec)
    vec_con = _conflict_distinct(Lvec)
    dead_vec = vec_sum.index[vec_sum["Coverage"] == 0].tolist()

    pos_cov = _coverage(Ll1[:, :len(pos_lfs)])
    neg_cov = _coverage(Ll1[:, len(pos_lfs):])
    # konflik relevan-vs-tidak_relevan: ada positif (1) DAN negatif (0) firing
    pos_fire = (Ll1[:, :len(pos_lfs)] == L1.RELEVAN).any(axis=1)
    neg_fire = (Ll1[:, len(pos_lfs):] == L1.TIDAK_RELEVAN).any(axis=1)
    l1_conflict = (pos_fire & neg_fire).mean()
    dead_l1 = l1_sum.index[l1_sum["Coverage"] == 0].tolist()

    # ---------- report ----------
    R = ["# Phase 7 — QC Labeling Functions (LFAnalysis)", "",
         f"Read-only QC pada kode terintegrasi. Dataset: `preprocessed_dataset.csv` ({n:,} baris).",
         f"Target roadmap: coverage >60% (ruang label), conflict <30%.", "",
         "## 1. Vektor LFs (Layer 2)", "",
         f"- Jumlah LF: **{len(vec_lfs)}**",
         f"- Coverage gabungan (>=1 vektor LF firing): **{vec_cov*100:.1f}%** "
         f"({int(vec_cov*n):,} baris)",
         f"- Overlap (>=2 LF firing): **{vec_ovl*100:.1f}%**",
         f"- Conflict (>=2 vektor BERBEDA firing): **{vec_con*100:.1f}%**",
         f"- Dead LF (coverage 0): **{len(dead_vec)}**"
         + (f" → {dead_vec}" if dead_vec else ""), "",
         "### Per-LF (vektor)", "",
         vec_sum.round(4).to_markdown(), "",
         "## 2. Layer-1 LFs (relevansi)", "",
         f"- Positif (RELEVAN) coverage: **{pos_cov*100:.1f}%**",
         f"- Negatif (TIDAK_RELEVAN) coverage: **{neg_cov*100:.1f}%**",
         f"- Konflik relevan-vs-tidak_relevan (pos & neg sama-sama firing): "
         f"**{l1_conflict*100:.2f}%**",
         f"- Dead LF: **{len(dead_l1)}**" + (f" → {dead_l1}" if dead_l1 else ""), "",
         "### Per-LF (Layer 1)", "",
         l1_sum.round(4).to_markdown(), "",
         "## 3. Interpretasi", "",
         f"- Coverage vektor {vec_cov*100:.1f}% < 60% adalah WAJAR: dataset didominasi "
         "konten off-topic (lihat Temuan #4); coverage tinggi hanya diharapkan pada "
         "subset relevan, bukan seluruh 48k. Conflict adalah metrik kualitas utama di sini.",
         f"- Conflict vektor {vec_con*100:.1f}% "
         + ("MEMENUHI" if vec_con < 0.30 else "MELEBIHI") + " target <30%.",
         "- Empirical accuracy per-LF butuh gold standard → diukur di Phase 8.", ""]

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(R))

    print("\n===== QC RINGKAS =====")
    print(f"Vektor: {len(vec_lfs)} LF | coverage {vec_cov*100:.1f}% | "
          f"overlap {vec_ovl*100:.1f}% | conflict {vec_con*100:.1f}% | dead {len(dead_vec)}")
    print(f"Layer1: pos cov {pos_cov*100:.1f}% | neg cov {neg_cov*100:.1f}% | "
          f"konflik rel-vs-tr {l1_conflict*100:.2f}% | dead {len(dead_l1)}")
    if dead_vec:
        print(f"  DEAD vektor LF: {dead_vec}")
    print(f"Report -> {REPORT}")


if __name__ == "__main__":
    main()
