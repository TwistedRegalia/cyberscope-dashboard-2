#!/usr/bin/env python3
"""
phase7_pipeline.py — Agregasi Phase 7 (arsitektur B).

Alur:
  1. Apply semua LF (6 vektor: precise Tier1/2 + discovery Tier3) + LF negatif Layer 1.
  2. Per-vektor binary LabelModel  -> P(vektor) tiap baris.
  3. Resolusi label: hierarki tie-break, prefer kandidat dgn LF presisi.
  4. Derive Layer 1 (relevan/tidak_relevan) dari anchor PRESISI (+ LF negatif).
  5. Threshold confidence >= 0.40 (metodologi).
  6. Formula confidence manual (Pattern Library §7.2) sebagai BASELINE pembanding.
  7. speaker_role (R1-R5) kasar sebagai metadata.

Output: data/weak_labeled_dataset.csv  (input Phase 8 Gold Standard).

Keputusan tertanam:
  - Jual-beli online -> tidak_relevan (LF negatif meng-override discovery phishing).
  - Layer 1 relevansi digerakkan anchor presisi (bukan discovery), sesuai keputusan Ray.
  - Hierarki: malware > deepfake > ewallet > phishing > peretasan > judi (CONTEXT §8).
"""
import sys, re, argparse
import numpy as np
import pandas as pd
from snorkel.labeling import PandasLFApplier
from snorkel.labeling.model import LabelModel

sys.path.insert(0, "src")
import phase7_labeling as L
import phase7_layer1 as L1

THRESHOLD = 0.40
REL_DISCOVERY_CONF = 0.50   # discovery-only baru 'relevan' bila P>=ini

HIERARCHY = [L.MALWARE, L.DEEPFAKE, L.EWALLET, L.PHISHING, L.PERETASAN, L.JUDI]

# Tier weight untuk formula manual (Pattern Library §7.2: max tier conf)
def _tier_weight(lf_name):
    if "_t1_" in lf_name:           return 0.90
    if "anchor_gate" in lf_name:    return 0.72
    if "korban_strict" in lf_name:  return 0.58
    if "_t2_" in lf_name:           return 0.72
    if "discovery" in lf_name:      return 0.45
    if "_t3_" in lf_name:           return 0.52
    return 0.50

def _is_precise(lf_name):
    return ("_t1_" in lf_name or "_t2_" in lf_name
            or "anchor_gate" in lf_name or "korban_strict" in lf_name)

# ---- helper: konflik jual-beli (override discovery phishing) ----
def _is_jualbeli_noise(t):
    return bool(L1._RE_JUALBELI.search(t)) and not L1._RE_PHISH_ANCHOR.search(t)

# ---- speaker role kasar (metadata, bukan label utama) ----
_RE_R3 = re.compile(r"(?:jangan|hindari|waspad[ai]|hati[\s-]*hati|tips|trik|cara\s*(?:cek|hindari)|aktifkan\s*2fa|jangan\s*(?:kasih|bagikan))", L._F)
_RE_R4 = re.compile(r"(?:link\s*(?:di\s*)?bio|daftar\s*sekarang|new\s*member|bonus\s*100|wd\s*(?:lancar|cepat)|jasa\s*(?:hack|pulihkan|bobol)|dm\s*(?:utk|untuk)?\s*order)", L._F)
_RE_R1 = re.compile(r"\b(?:gue|gua|aku|saya|gw)\b\W{0,40}(?:kena|korban|ketipu|ditipu|kehilangan|saldo.*amblas)", L._F)
_RE_R5 = re.compile(r"(?:bssn|ojk|kominfo|kemkomdigi|bjorka|menurut\s*(?:data|penelitian)|statistik|merilis|jurnal|riset)", L._F)
def _role(t):
    if _RE_R4.search(t): return "R4"
    if _RE_R3.search(t): return "R3"
    if _RE_R5.search(t): return "R5"
    if _RE_R1.search(t): return "R1"
    return "R2"


def main():
    ap = argparse.ArgumentParser(description="Phase 7 Snorkel aggregation")
    ap.add_argument("--input", default="data/preprocessed_dataset.csv",
                    help="CSV input (default: data/preprocessed_dataset.csv)")
    ap.add_argument("--output", default="data/weak_labeled_dataset.csv",
                    help="CSV output (default: data/weak_labeled_dataset.csv)")
    args = ap.parse_args()

    print(f"Loading {args.input} ...")
    df = pd.read_csv(args.input)
    df["text_clean"] = df["text_clean"].fillna("")
    n = len(df)
    print(f"  rows: {n}")

    # ---------- 1. Apply LFs ----------
    vec_lfs = L.ALL_LFS                       # 6 vektor (precise + discovery)
    neg_lfs = L1.NEGATIVE_LFS                 # LF tidak_relevan
    print(f"Applying {len(vec_lfs)} vector LFs + {len(neg_lfs)} negative LFs ...")
    Lvec = PandasLFApplier(lfs=vec_lfs).apply(df=df, progress_bar=False)
    Lneg = PandasLFApplier(lfs=neg_lfs).apply(df=df, progress_bar=False)
    lf_names = [lf.name for lf in vec_lfs]

    # peta kolom -> vektor; precise vs semua
    col_vec = []
    for lf in vec_lfs:
        # tentukan vektor dari LFS_BY_VECTOR
        for v, lfs in L.LFS_BY_VECTOR.items():
            if lf in lfs:
                col_vec.append(v); break
    col_vec = np.array(col_vec)
    precise_mask = np.array([_is_precise(nm) for nm in lf_names])

    # ---------- 2. Per-vektor binary LabelModel ----------
    print("Fitting per-vector binary LabelModels ...")
    P = np.zeros((n, 6))                      # P[:,V] = P(vektor V)
    for v in range(6):
        cols = np.where(col_vec == v)[0]
        Lv = Lvec[:, cols]
        # remap: label v -> 1, ABSTAIN -> -1
        Lb = np.where(Lv == v, 1, -1)
        fired = (Lb == 1).any(axis=1)
        p = max(fired.mean(), 1e-3)
        try:
            lm = LabelModel(cardinality=2, verbose=False)
            lm.fit(L_train=Lb, n_epochs=300, seed=42, class_balance=[1 - p, p])
            P[:, v] = lm.predict_proba(Lb)[:, 1]
        except Exception as e:
            # fallback: noisy-OR sederhana berbobot tier
            w = np.array([_tier_weight(lf_names[c]) for c in cols])
            hit = (Lb == 1)
            P[:, v] = 1 - np.prod(1 - hit * w, axis=1)
        # baris tanpa vote -> P rendah
        P[~fired, v] = 0.0

    # ---------- formula manual (baseline) ----------
    manual = np.zeros((n, 6))
    for v in range(6):
        cols = np.where(col_vec == v)[0]
        w = np.array([_tier_weight(lf_names[c]) for c in cols])
        hit = (Lvec[:, cols] == v)
        manual[:, v] = (hit * w).max(axis=1) if len(cols) else 0.0

    # ---------- 3-5. Resolusi label per baris ----------
    neg_fired = (Lneg != L1.ABSTAIN).any(axis=1)
    layer1, layer2, role, conf, mconf = [], [], [], [], []
    for i in range(n):
        t = df.at[i, "text_clean"]
        fired_v = {v for v in range(6) if (Lvec[i, col_vec == v] == v).any()}
        precise_v = {v for v in range(6)
                     if (Lvec[i, (col_vec == v) & precise_mask] == v).any()}
        if not fired_v:
            layer1.append("tidak_relevan"); layer2.append(""); role.append("")
            conf.append(0.0); mconf.append(0.0); continue

        pool = precise_v if precise_v else fired_v
        chosen = next(v for v in HIERARCHY if v in pool)
        Pc = P[i, chosen]; Mc = manual[i, chosen]
        has_precise = chosen in precise_v

        # Layer 1
        rel = False
        if has_precise:
            rel = True
        elif Pc >= REL_DISCOVERY_CONF and not neg_fired[i] and not _is_jualbeli_noise(t):
            rel = True
        # threshold confidence
        if rel and Pc < THRESHOLD:
            rel = False

        if rel:
            layer1.append("relevan"); layer2.append(L.LABEL_NAMES[chosen])
            role.append(_role(t)); conf.append(round(float(Pc), 4)); mconf.append(round(float(Mc), 4))
        else:
            layer1.append("tidak_relevan"); layer2.append(""); role.append("")
            conf.append(round(float(Pc), 4)); mconf.append(round(float(Mc), 4))

    df["layer1_label"]    = layer1
    df["layer2_label"]    = layer2
    df["speaker_role"]    = role
    df["lm_confidence"]   = conf
    df["manual_confidence"] = mconf

    # ---------- 6. Distribusi + simpan ----------
    print("\n===== DISTRIBUSI FINAL =====")
    print(df["layer1_label"].value_counts())
    print("\nLayer 2 (relevan saja):")
    print(df[df.layer1_label == "relevan"]["layer2_label"].value_counts())
    print("\nspeaker_role (relevan):")
    print(df[df.layer1_label == "relevan"]["speaker_role"].value_counts())
    print(f"\nlm vs manual confidence (relevan): corr = "
          f"{df[df.layer1_label=='relevan'][['lm_confidence','manual_confidence']].corr().iloc[0,1]:.3f}")

    out_cols = ["unified_id", "platform", "source_category", "published_at",
                "vector_hint", "layer1_label", "layer2_label", "speaker_role",
                "lm_confidence", "manual_confidence", "text", "text_clean", "text_normalized"]
    out = df[out_cols]
    out.to_csv(args.output, index=False)
    print(f"\n[saved] {args.output}  ({len(out)} baris, {len(out_cols)} kolom)")
    return df


if __name__ == "__main__":
    main()
