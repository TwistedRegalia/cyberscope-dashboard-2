#!/usr/bin/env python3
"""
phase8_gold_sampling.py — Phase 8 Gold Standard Sampling (E-ICTT v2.1)

Stratified hybrid-floor sampling dari weak_labeled_dataset_v2.csv untuk gold annotation
(blind, dua annotator independen). Total 357:

  - 297 relevan: alokasi per-vektor = LANTAI 35 + sisa proporsional (87) berdasar
    distribusi relevan v2 (judi 7486, ewallet 548, phishing 492, peretasan 365,
    malware 214, deepfake 107). Hasil: judi 106, ewallet 40, phishing 40,
    peretasan 38, malware 37, deepfake 36.
  - 60 tidak_relevan (validasi Layer 1), acak.

Reproducible: seed 42 (sampling tiap stratum + shuffle final).

Output (data/):
  - gold_annotation_sheet.csv      master blank (blind)
  - gold_annotation_sheet_A.csv    salinan annotator A
  - gold_annotation_sheet_B.csv    salinan annotator B
  - gold_key_HIDDEN.csv            JANGAN beri ke annotator (peta sample_id -> truth)

Blind-labeling safeguards:
  - sample_id ANONIM (G001..), BUKAN unified_id -> tak membocorkan asal/urutan.
  - sheet hanya teks ORIGINAL + kolom annotator kosong (tanpa platform/source/weak label).
  - urutan DIACAK (semua stratum tercampur) -> label tak bisa ditebak dari pengelompokan.

Catatan limitasi: kelas kecil (deepfake) memiliki fraksi sampling tinggi terhadap
populasi relevannya (36/107 ~ 34%) -> gold deepfake kurang independen vs kelas besar.
Didokumentasikan sebagai limitasi (CONTEXT Temuan #8).
"""
import argparse
import pandas as pd

SEED = 42

# Alokasi relevan per layer2 (LANTAI 35 + sisa proporsional 87 = 297).
RELEVAN_ALLOC = {
    "judi_online_pinjol": 106,
    "penipuan_ewallet_qris": 40,
    "phishing_rekayasa_sosial": 40,
    "peretasan_pencurian_identitas": 38,
    "malware_apk": 37,
    "deepfake_penipuan_ai": 36,
}
TIDAK_RELEVAN_N = 60

SHEET_COLS = ["sample_id", "text", "annotator_layer1", "annotator_layer2",
              "annotator_speaker_role", "annotator_confidence", "annotator_notes"]


def main():
    ap = argparse.ArgumentParser(description="Phase 8 gold standard sampling")
    ap.add_argument("--input", default="data/weak_labeled_dataset_v2.csv")
    ap.add_argument("--outdir", default="data")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    df = pd.read_csv(args.input, dtype=str, keep_default_na=False)
    rel = df[df["layer1_label"] == "relevan"]
    irr = df[df["layer1_label"] == "tidak_relevan"]

    # --- sample relevan per stratum (vektor) ---
    picks = []
    print("== Alokasi & ketersediaan stratum relevan (seed=%d) ==" % args.seed)
    for vec, n in RELEVAN_ALLOC.items():
        pool = rel[rel["layer2_label"] == vec]
        avail = len(pool)
        if avail < n:
            raise SystemExit(f"ERROR: '{vec}' hanya {avail} relevan, butuh {n}")
        frac = n / avail * 100
        flag = "   <-- fraksi tinggi (limitasi)" if frac >= 30 else ""
        print(f"  {vec:32} ambil {n:4} / {avail:5} ({frac:4.1f}%){flag}")
        picks.append(pool.sample(n=n, random_state=args.seed))

    # --- sample tidak_relevan (validasi Layer 1) ---
    if len(irr) < TIDAK_RELEVAN_N:
        raise SystemExit(f"ERROR: tidak_relevan hanya {len(irr)}, butuh {TIDAK_RELEVAN_N}")
    print(f"  {'tidak_relevan':32} ambil {TIDAK_RELEVAN_N:4} / {len(irr):5}")
    picks.append(irr.sample(n=TIDAK_RELEVAN_N, random_state=args.seed))

    gold = pd.concat(picks, ignore_index=True)
    # shuffle semua stratum (reproducible) SEBELUM assign sample_id -> id tak encode stratum
    gold = gold.sample(frac=1, random_state=args.seed).reset_index(drop=True)
    gold.insert(0, "sample_id", [f"G{i + 1:03d}" for i in range(len(gold))])

    total = len(gold)
    assert total == sum(RELEVAN_ALLOC.values()) + TIDAK_RELEVAN_N == 357, total

    # --- annotation sheet (blind) ---
    sheet = pd.DataFrame({
        "sample_id": gold["sample_id"],
        "text": gold["text"],
        "annotator_layer1": "",
        "annotator_layer2": "",
        "annotator_speaker_role": "",
        "annotator_confidence": "",
        "annotator_notes": "",
    })[SHEET_COLS]
    for suffix in ("", "_A", "_B"):
        sheet.to_csv(f"{args.outdir}/gold_annotation_sheet{suffix}.csv", index=False)

    # --- key (HIDDEN, JANGAN beri ke annotator) ---
    key = pd.DataFrame({
        "sample_id": gold["sample_id"],
        "unified_id": gold["unified_id"],
        "platform": gold["platform"],
        "source_category": gold["source_category"],
        "vector_hint": gold["vector_hint"],
        "weak_layer1": gold["layer1_label"],
        "weak_layer2": gold["layer2_label"],
        "weak_speaker_role": gold["speaker_role"],
        "lm_confidence": gold["lm_confidence"],
    })
    key.to_csv(f"{args.outdir}/gold_key_HIDDEN.csv", index=False)

    # --- verifikasi komposisi (dari key) ---
    print("\n== Verifikasi komposisi gold set ==")
    print(f"  Total: {total}")
    print(f"  Layer 1: relevan={(key.weak_layer1 == 'relevan').sum()}, "
          f"tidak_relevan={(key.weak_layer1 == 'tidak_relevan').sum()}")
    print("  Layer 2 (relevan):")
    for k, v in key[key.weak_layer1 == 'relevan']["weak_layer2"].value_counts().items():
        print(f"    {k:32} {v}")
    print("  Per platform:")
    for k, v in key["platform"].value_counts().items():
        print(f"    {k:12} {v}")

    print(f"\n[saved] {args.outdir}/gold_annotation_sheet.csv (+_A,_B)  357 baris, blind")
    print(f"[saved] {args.outdir}/gold_key_HIDDEN.csv  (357, JANGAN beri ke annotator)")


if __name__ == "__main__":
    main()
