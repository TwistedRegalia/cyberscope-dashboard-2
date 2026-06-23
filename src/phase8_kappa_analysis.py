#!/usr/bin/env python3
"""
phase8_kappa_analysis.py — IAA + validasi weak label (DIPAKAI SETELAH anotasi).

Jalankan setelah annotator A & B mengisi gold_annotation_sheet_A/B(_filled).csv
(kolom annotator_layer1 / annotator_layer2 / annotator_speaker_role).

Menghitung:
  (a) Inter-annotator Cohen's Kappa: Layer 1, Layer 2 (vektor), speaker_role,
      + per-label one-vs-rest.
  (b) [hanya tanpa --iaa-only] Akurasi weak label vs gold proxy (subset SEPAKAT A==B).
  (c) [hanya tanpa --iaa-only] Per-class precision weak label.

Output:
  - Console: metrik di atas.
  - data/gold_disagreements.csv : baris A != B (Layer 1 / Layer 2 / speaker_role),
    dengan kolom rekonsiliasi (final_*) KOSONG untuk reviewer ketiga / dosen.

--iaa-only : hanya IAA + disagreements; SKIP validasi weak label. Dipakai sebelum
gold standard final (menunggu rekonsiliasi reviewer ketiga).
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
        return "(Excellent)"
    if k >= 0.60:
        return "(Substantial)"
    return "(Insufficient -> revisi guidelines)"


def _kappa(a, b):
    from sklearn.metrics import cohen_kappa_score
    return cohen_kappa_score(list(a), list(b))


def _dims(r):
    """Dimensi disagreement untuk satu baris (L1 / L2 / role)."""
    if r.a_l1 != r.b_l1:
        return ["L1"]                       # L1 beda -> tidak cascade ke L2/role
    out = []
    if r.a_l1 == "relevan":                 # keduanya relevan (karena sama)
        if r.a_l2 != r.b_l2:
            out.append("L2")
        if r.a_role != r.b_role:
            out.append("role")
    return out


def main():
    ap = argparse.ArgumentParser(description="Phase 8 IAA + weak-label validation")
    ap.add_argument("--sheet-a", default="data/gold_annotation_sheet_A.csv")
    ap.add_argument("--sheet-b", default="data/gold_annotation_sheet_B.csv")
    ap.add_argument("--key", default="data/gold_key_HIDDEN.csv")
    ap.add_argument("--out-disagree", default="data/gold_disagreements.csv")
    ap.add_argument("--iaa-only", action="store_true",
                    help="Hanya IAA + disagreements; SKIP validasi weak label "
                         "(tunggu gold final pasca rekonsiliasi reviewer ketiga).")
    args = ap.parse_args()

    A = pd.read_csv(args.sheet_a, dtype=str, keep_default_na=False)
    B = pd.read_csv(args.sheet_b, dtype=str, keep_default_na=False)

    a_filled = (A["annotator_layer1"].str.strip() != "").sum()
    b_filled = (B["annotator_layer1"].str.strip() != "").sum()
    if a_filled == 0 or b_filled == 0:
        print(f"[!] Sheet belum dianotasi (A={a_filled}/{len(A)}, B={b_filled}/{len(B)}).")
        sys.exit(0)

    m = A[["sample_id", "text"]].copy()
    m["a_l1"] = A["annotator_layer1"].map(_norm)
    m["a_l2"] = A["annotator_layer2"].map(_norm)
    m["a_role"] = A["annotator_speaker_role"].map(_norm).str.upper()
    b = B.set_index("sample_id")
    m["b_l1"] = m["sample_id"].map(b["annotator_layer1"]).map(_norm)
    m["b_l2"] = m["sample_id"].map(b["annotator_layer2"]).map(_norm)
    m["b_role"] = m["sample_id"].map(b["annotator_speaker_role"]).map(_norm).str.upper()
    m = m.sort_values("sample_id").reset_index(drop=True)

    # ---------- (a) IAA ----------
    print(f"== (a) Inter-Annotator Agreement (n={len(m)}) ==")
    k1 = _kappa(m.a_l1, m.b_l1)
    print(f"  Kappa Layer 1 (relevan/tidak_relevan): {k1:.3f}  {_interpret(k1)}")

    rel_both = m[(m.a_l1 == "relevan") & (m.b_l1 == "relevan")]
    k2 = _kappa(rel_both.a_l2, rel_both.b_l2)
    print(f"  Kappa Layer 2 (vektor, both-relevan n={len(rel_both)}): "
          f"{k2:.3f}  {_interpret(k2)}")
    kr = _kappa(rel_both.a_role, rel_both.b_role)
    print(f"  Kappa speaker_role (both-relevan n={len(rel_both)}): "
          f"{kr:.3f}  {_interpret(kr)}")

    print("  Per-label Kappa (one-vs-rest):")
    for v in VEKTOR:
        a = (rel_both.a_l2 == v).astype(int)
        bb = (rel_both.b_l2 == v).astype(int)
        if a.nunique() > 1 or bb.nunique() > 1:
            print(f"    {v:32} kappa={_kappa(a, bb):.3f}")
        else:
            print(f"    {v:32} (tak ada kasus positif)")

    # ---------- disagreements -> file (reviewer ketiga) ----------
    dim_list = m.apply(_dims, axis=1)
    dis = m[dim_list.map(len) > 0].copy()
    dis["dim_beda"] = dim_list[dim_list.map(len) > 0].map(lambda d: " ".join(d))
    out = pd.DataFrame({
        "sample_id": dis.sample_id,
        "text": dis.text,
        "dim_beda": dis.dim_beda,
        "A_layer1": dis.a_l1, "B_layer1": dis.b_l1,
        "A_layer2": dis.a_l2, "B_layer2": dis.b_l2,
        "A_role": dis.a_role, "B_role": dis.b_role,
        "final_layer1": "", "final_layer2": "", "final_role": "",
        "catatan_reviewer": "",
    })
    out.to_csv(args.out_disagree, index=False)
    n_l1 = (dis.dim_beda.str.contains("L1")).sum()
    n_l2 = (dis.dim_beda.str.contains("L2")).sum()
    n_role = (dis.dim_beda.str.contains("role")).sum()
    print(f"\n[saved] {args.out_disagree}  ({len(out)} baris disagreement: "
          f"{n_l1} L1, {n_l2} L2, {n_role} role) — kolom final_* KOSONG (BELUM "
          f"direkonsiliasi, untuk reviewer ketiga)")

    # ---------- (b)+(c) weak label (di-skip saat --iaa-only) ----------
    if args.iaa_only:
        print("\n[--iaa-only] Validasi weak label DI-SKIP "
              "(menunggu gold standard final pasca rekonsiliasi).")
        return

    key = pd.read_csv(args.key, dtype=str, keep_default_na=False).set_index("sample_id")
    m["weak_l1"] = m.sample_id.map(key["weak_layer1"]).map(_norm)
    m["weak_l2"] = m.sample_id.map(key["weak_layer2"]).map(_norm)
    # Gold proxy = baris SEPAKAT PENUH A==B (L1+L2+role); 46 disagreement dikecualikan.
    agree = m[(m.a_l1 == m.b_l1) & (m.a_l2 == m.b_l2) & (m.a_role == m.b_role)].copy()
    n_excl = len(m) - len(agree)
    print(f"\n== (b) Validasi weak label — gold proxy SEPAKAT PENUH A==B "
          f"(n={len(agree)}; {n_excl} disagreement dikecualikan) ==")
    print(f"  Akurasi weak Layer 1: {(agree.weak_l1 == agree.a_l1).mean():.3f}  (n={len(agree)})")
    gold_rel = agree[agree.a_l1 == "relevan"]
    if len(gold_rel):
        print(f"  Akurasi weak Layer 2 (sepakat-relevan n={len(gold_rel)}): "
              f"{(gold_rel.weak_l2 == gold_rel.a_l2).mean():.3f}")
        print("\n== (c) Per-class precision weak label (gold = anotator sepakat) ==")
        for v in VEKTOR:
            pred = gold_rel[gold_rel.weak_l2 == v]
            if len(pred):
                print(f"  {v:32} precision={(pred.a_l2 == v).mean():.3f} (n_pred={len(pred)})")
            else:
                print(f"  {v:32} (weak tak memprediksi di subset gold)")


if __name__ == "__main__":
    main()
