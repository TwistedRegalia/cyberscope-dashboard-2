#!/usr/bin/env python3
"""
phase8_kappa_analysis.py — IAA + validasi weak label (DIPAKAI SETELAH anotasi).

Jalankan setelah annotator A & B mengisi gold_annotation_sheet_A/B.csv (kolom
annotator_layer1 / annotator_layer2 / annotator_speaker_role).

Input (data/):
  - gold_annotation_sheet_A.csv  (terisi annotator A)
  - gold_annotation_sheet_B.csv  (terisi annotator B)
  - gold_key_HIDDEN.csv

Menghitung:
  (a) Inter-annotator Cohen's Kappa: Layer 1, Layer 2 (vektor), + per-label one-vs-rest.
  (b) Akurasi weak label (Snorkel) vs gold proxy (subset SEPAKAT A==B).
  (c) Per-class precision weak label.

Output:
  - Console: metrik di atas.
  - data/gold_disagreements.csv : baris A != B (Layer 1 atau Layer 2 vektor) untuk
    rekonsiliasi reviewer ketiga (gold final yang ketat butuh langkah ini).

Catatan: 'gold final' yang ketat = hasil rekonsiliasi reviewer ketiga atas disagreement.
Sebelum itu, metrik weak-label dihitung pada subset SEPAKAT sebagai proxy.
"""
import argparse
import sys

import pandas as pd

VEKTOR = ["phishing_rekayasa_sosial", "penipuan_ewallet_qris", "malware_apk",
          "judi_online_pinjol", "peretasan_pencurian_identitas", "deepfake_penipuan_ai"]


def _norm(s):
    return str(s).strip().lower()


def _interpret(k):
    if k >= 0.80:
        return "(Excellent — siap gold standard)"
    if k >= 0.60:
        return "(Substantial — refinement guidelines)"
    return "(Insufficient — revisi guidelines major)"


def _kappa(a, b):
    from sklearn.metrics import cohen_kappa_score
    return cohen_kappa_score(list(a), list(b))


def main():
    ap = argparse.ArgumentParser(description="Phase 8 IAA + weak-label validation")
    ap.add_argument("--sheet-a", default="data/gold_annotation_sheet_A.csv")
    ap.add_argument("--sheet-b", default="data/gold_annotation_sheet_B.csv")
    ap.add_argument("--key", default="data/gold_key_HIDDEN.csv")
    ap.add_argument("--out-disagree", default="data/gold_disagreements.csv")
    args = ap.parse_args()

    A = pd.read_csv(args.sheet_a, dtype=str, keep_default_na=False)
    B = pd.read_csv(args.sheet_b, dtype=str, keep_default_na=False)
    key = pd.read_csv(args.key, dtype=str, keep_default_na=False)

    a_filled = (A["annotator_layer1"].str.strip() != "").sum()
    b_filled = (B["annotator_layer1"].str.strip() != "").sum()
    if a_filled == 0 or b_filled == 0:
        print(f"[!] Sheet belum dianotasi (A terisi={a_filled}/{len(A)}, "
              f"B terisi={b_filled}/{len(B)}).")
        print("    Isi kolom annotator_layer1/annotator_layer2 di KEDUA sheet dulu, "
              "lalu jalankan ulang.")
        sys.exit(0)
    if a_filled < len(A) or b_filled < len(B):
        print(f"[warn] Anotasi belum lengkap (A {a_filled}/{len(A)}, B {b_filled}/{len(B)}). "
              "Metrik dihitung pada baris yang terisi di KEDUANYA.\n")

    # rename kolom annotator -> _A / _B, lalu merge by sample_id
    Aa = A.rename(columns={c: c + "_A" for c in A.columns if c.startswith("annotator")})
    Bb = B.rename(columns={c: c + "_B" for c in B.columns if c.startswith("annotator")})
    m = (Aa.merge(Bb[["sample_id"] + [c for c in Bb.columns if c.endswith("_B")]],
                  on="sample_id")
          .merge(key, on="sample_id"))

    for col in ["annotator_layer1_A", "annotator_layer1_B",
                "annotator_layer2_A", "annotator_layer2_B"]:
        m[col] = m[col].map(_norm)
    m["weak_layer1"] = m["weak_layer1"].map(_norm)
    m["weak_layer2"] = m["weak_layer2"].map(_norm)

    both = m[(m.annotator_layer1_A != "") & (m.annotator_layer1_B != "")].copy()

    # ---------- (a) IAA ----------
    print(f"== (a) Inter-Annotator Agreement (n={len(both)}) ==")
    k1 = _kappa(both.annotator_layer1_A, both.annotator_layer1_B)
    print(f"  Kappa Layer 1 (relevan/tidak_relevan): {k1:.3f}  {_interpret(k1)}")

    rel_both = both[(both.annotator_layer1_A == "relevan") &
                    (both.annotator_layer1_B == "relevan")]
    if len(rel_both) >= 2 and (rel_both.annotator_layer2_A.nunique() > 1
                               or rel_both.annotator_layer2_B.nunique() > 1):
        k2 = _kappa(rel_both.annotator_layer2_A, rel_both.annotator_layer2_B)
        print(f"  Kappa Layer 2 (vektor, both-relevan n={len(rel_both)}): "
              f"{k2:.3f}  {_interpret(k2)}")
    else:
        print(f"  Kappa Layer 2: subset both-relevan terlalu kecil ({len(rel_both)})")

    print("  Per-label Kappa (one-vs-rest):")
    for v in ["relevan"] + VEKTOR:
        if v == "relevan":
            a = (both.annotator_layer1_A == "relevan").astype(int)
            b = (both.annotator_layer1_B == "relevan").astype(int)
        else:
            a = (both.annotator_layer2_A == v).astype(int)
            b = (both.annotator_layer2_B == v).astype(int)
        if a.nunique() > 1 or b.nunique() > 1:
            print(f"    {v:32} kappa={_kappa(a, b):.3f}")
        else:
            print(f"    {v:32} (tak ada kasus positif)")

    # ---------- (b)+(c) weak label vs gold proxy (sepakat A==B) ----------
    agree1 = both[both.annotator_layer1_A == both.annotator_layer1_B].copy()
    print(f"\n== (b) Validasi weak label — gold proxy = SEPAKAT A==B (n={len(agree1)}) ==")
    if len(agree1):
        acc1 = (agree1.weak_layer1 == agree1.annotator_layer1_A).mean()
        print(f"  Akurasi weak Layer 1: {acc1:.3f}")

    gold_rel = agree1[(agree1.annotator_layer1_A == "relevan") &
                      (agree1.annotator_layer2_A == agree1.annotator_layer2_B)]
    if len(gold_rel):
        acc2 = (gold_rel.weak_layer2 == gold_rel.annotator_layer2_A).mean()
        print(f"  Akurasi weak Layer 2 (sepakat-relevan n={len(gold_rel)}): {acc2:.3f}")
        print("\n== (c) Per-class precision weak label (gold = annotator sepakat) ==")
        for v in VEKTOR:
            pred = gold_rel[gold_rel.weak_layer2 == v]
            if len(pred):
                prec = (pred.annotator_layer2_A == v).mean()
                print(f"  {v:32} precision={prec:.3f}  (n_pred={len(pred)})")
            else:
                print(f"  {v:32} (weak tak memprediksi di subset gold)")

    # ---------- disagreements -> file (reviewer ketiga) ----------
    dis = m[(m.annotator_layer1_A != m.annotator_layer1_B) |
            ((m.annotator_layer1_A == "relevan") & (m.annotator_layer1_B == "relevan") &
             (m.annotator_layer2_A != m.annotator_layer2_B))].copy()
    cols = ["sample_id", "text",
            "annotator_layer1_A", "annotator_layer2_A",
            "annotator_layer1_B", "annotator_layer2_B",
            "weak_layer1", "weak_layer2", "vector_hint", "source_category"]
    dis[[c for c in cols if c in dis.columns]].to_csv(args.out_disagree, index=False)
    print(f"\n[saved] {args.out_disagree}  ({len(dis)} disagreement untuk reviewer ketiga)")


if __name__ == "__main__":
    main()
