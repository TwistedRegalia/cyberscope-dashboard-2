#!/usr/bin/env python3
"""
refresh_vector_hint.py — Recompute HANYA kolom vector_hint pada unified_dataset.csv
menggunakan anchor_patterns.py v1.1 (row-stable).

Tidak menjalankan ulang filter/dedup Phase 5: jumlah baris, unified_id, dan SEMUA
kolom lain dipertahankan persis. Hanya `vector_hint` yang berubah (diagnostik kasar,
BUKAN label final — label final = Snorkel Phase 7).

Output:
  - data/unified_dataset.csv          : ditulis ulang (hanya vector_hint berubah)
  - data/vector_hint_refresh_report.md: perbandingan distribusi + sampel old vs new

Cara pakai:
  python src/refresh_vector_hint.py
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anchor_patterns import top_vector_hint  # noqa: E402

CSV = os.path.join("data", "unified_dataset.csv")
REPORT = os.path.join("data", "vector_hint_refresh_report.md")
SEED = 42
NOHINT = "NO_HINT (perlu Snorkel)"


def main():
    # Baca semua kolom sebagai string agar kolom selain vector_hint byte-stable
    # (orig_id berisi tweet ID besar; jangan biarkan pandas reinterpret jadi float).
    df = pd.read_csv(CSV, dtype=str, keep_default_na=False)
    n = len(df)
    assert "vector_hint" in df.columns and "text" in df.columns

    old = df["vector_hint"].copy()          # NO_HINT tersimpan sbg "" di CSV
    # `or ""` mengembalikan string "" untuk no-hint (hindari None->NaN coercion).
    new = df["text"].apply(lambda t: top_vector_hint(t) or "")
    df["vector_hint"] = new                 # HANYA kolom ini yang diubah

    # Tulis ulang (kolom & urutan tetap, hanya nilai vector_hint berbeda)
    df.to_csv(CSV, index=False, lineterminator="\n")

    # ---------- Laporan perbandingan ----------
    def dist(series):
        lab = series.apply(lambda v: NOHINT if v == "" else v)
        return lab.value_counts()

    od, nd = dist(old), dist(new)
    vectors = sorted(set(od.index) | set(nd.index),
                     key=lambda k: -nd.get(k, 0))

    L = ["# Vector Hint Refresh — Perbandingan (anchor_patterns v1.1)", "",
         f"Row-stable: {n:,} baris, semua kolom lain dipertahankan. "
         "Hanya `vector_hint` direcompute.", "",
         "## 1. Distribusi: Lama vs Baru", "",
         "| Vector Hint | Lama | % | Baru | % |", "|---|---|---|---|---|"]
    for k in vectors:
        ov, nv = int(od.get(k, 0)), int(nd.get(k, 0))
        L.append(f"| {k} | {ov:,} | {ov/n*100:.1f}% | {nv:,} | {nv/n*100:.1f}% |")
    no_old = int((old == "").sum())
    no_new = int((new == "").sum())
    L += ["",
          f"**NO_HINT: {no_old/n*100:.1f}% → {no_new/n*100:.1f}%** "
          f"({no_old:,} → {no_new:,}).",
          f"Newly hinted (was NO_HINT, now hinted): "
          f"{int(((old=='')&(new!='')).sum()):,}.",
          f"Lost hint (was hinted, now NO_HINT): "
          f"{int(((old!='')&(new=='')).sum()):,}.", ""]

    rng = df.assign(_old=old, _new=new)

    def sample_block(title, mask):
        block = [f"## {title}", ""]
        sub = rng[mask]
        if len(sub) == 0:
            return block + ["(kosong)", ""]
        for i, (_, r) in enumerate(sub.sample(min(20, len(sub)),
                                              random_state=SEED).iterrows(), 1):
            t = str(r["text"]).replace("\n", " ").replace("\r", " ")[:130]
            block.append(f"{i}. `[{r['source_category']}]` {t}")
        return block + [""]

    L += sample_block("2. 20 sampel acak NO_HINT — LAMA "
                      "(sebelum refinement)", old == "")
    L += sample_block("3. 20 sampel acak NO_HINT — BARU "
                      "(masih NO_HINT sesudah refinement → verifikasi off-topic)",
                      new == "")
    L += sample_block("4. 20 sampel acak NEWLY HINTED "
                      "(cek presisi: benar relevan?)", (old == "") & (new != ""))

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    # ---------- Ringkasan ke stdout ----------
    print(f"Rows: {n:,} (row-stable)")
    print(f"NO_HINT: {no_old/n*100:.1f}% -> {no_new/n*100:.1f}%")
    print(f"Newly hinted: {int(((old=='')&(new!='')).sum()):,} | "
          f"Lost: {int(((old!='')&(new=='')).sum()):,}")
    print("--- distribusi baru ---")
    for k in vectors:
        nv = int(nd.get(k, 0))
        print(f"  {k:35s} {nv:6d}  {nv/n*100:5.1f}%")
    print(f"Report -> {REPORT}")


if __name__ == "__main__":
    main()
