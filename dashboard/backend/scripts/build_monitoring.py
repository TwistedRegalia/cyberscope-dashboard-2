"""Batch Model A + Model B + fusion over data/weak_labeled_dataset_v2.csv -> monitoring.json.

DESIGNED FOR KAGGLE T4 (GPU), NOT local CPU / HF Spaces. 55,300 rows through two
IndoBERT+BiGRU+BiLSTM models is too slow on CPU (Model A alone over 5,530 rows took
~450s CPU in local sanity checks - scaling to 55,300 rows would take well over an hour).
This script is meant to be run once, by hand, on Kaggle; HF Spaces only serves the 3
live endpoints (see app/main.py).

How to run on Kaggle:
  1. Enable GPU T4 (Notebook settings -> Accelerator -> GPU T4).
  2. Make sure the whole PI2/ repo is available with the same layout as local dev
     (src/, data/, models/, dashboard/backend/app/ all present), and the working
     directory is the repo root PI2/ when you invoke this script.
  3. pip install torch transformers pandas numpy scikit-learn emoji Sastrawi
     (Sastrawi/emoji are transitive - importing app.pipeline imports
     src.phase6_preprocess, which imports Sastrawi at module load time even though
     clean_text() itself isn't called here - text_clean is already preprocessed).
  4. python dashboard/backend/scripts/build_monitoring.py
  5. Output is written directly to dashboard/frontend/public/data/monitoring.json
     (drop-in path, HANDOFF_FRONTEND Sec 5.1) - from there: git add, commit, push;
     Vercel auto-deploys. Do this step outside Kaggle (git normally, e.g. after
     downloading the output file if Kaggle itself isn't your git remote).

INTEGRITY (CLAUDE.md Sec 6/Sec 11): every number in monitoring.json is a Model A+B
prediction. The weak-labeled layer1_label/layer2_label (Snorkel) columns are read
for provenance-comparison logging only and must never be written into the output.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "dashboard" / "backend"))

from src.anchor_patterns import detect_vector_hints, has_anchor  # noqa: E402
from src.phase9_model_a_layer1 import LABEL2ID as A_LABEL2ID  # noqa: E402
from src.phase9_model_b_layer2 import LABEL2ID as B_LABEL2ID  # noqa: E402
from app import pipeline  # noqa: E402

SAMPLES_PER_VECTOR = 40


def chunked_softmax(model, tokenizer, device, texts: list[str], batch_size: int):
    import numpy as np

    all_probs = []
    for i in range(0, len(texts), batch_size):
        chunk = texts[i : i + batch_size]
        all_probs.extend(pipeline._softmax_batch(model, tokenizer, device, chunk))
    return np.array(all_probs)


def normalize_platform(raw: str):
    if raw == "YouTube":
        return "youtube"
    if raw == "X":
        return "x"
    return None


def to_period(published_at):
    import pandas as pd

    if pd.isna(published_at):
        return None
    try:
        return pd.to_datetime(published_at, utc=True).strftime("%Y-%m")
    except (ValueError, TypeError):
        return None


def main() -> None:
    import numpy as np
    import pandas as pd

    ap = argparse.ArgumentParser(description="Batch inference -> monitoring.json (Kaggle T4)")
    ap.add_argument("--data", default=str(REPO_ROOT / "data" / "weak_labeled_dataset_v2.csv"))
    ap.add_argument(
        "--out", default=str(REPO_ROOT / "dashboard" / "frontend" / "public" / "data" / "monitoring.json")
    )
    ap.add_argument("--batch-size", type=int, default=32, dest="batch_size")
    ap.add_argument(
        "--limit", type=int, default=None, help="Truncate to first N rows (local smoke-testing only)"
    )
    args = ap.parse_args()

    pipeline.load_models()
    device = pipeline._state["device"]
    tokenizer = pipeline._state["tokenizer"]
    model_a = pipeline._state["model_a"]
    model_b = pipeline._state["model_b"]
    print(f"device={device}")

    df = pd.read_csv(args.data)
    if args.limit:
        df = df.head(args.limit).reset_index(drop=True)
    total_rows = len(df)
    texts_clean = df["text_clean"].fillna("").astype(str).tolist()
    print(f"total_rows={total_rows}")

    # --- Layer 1: relevance (fused 0.75 neural : 0.25 anchor, CLAUDE.md Sec 4) ---
    print("Model A inference...")
    p_a = chunked_softmax(model_a, tokenizer, device, texts_clean, args.batch_size)
    anchor_l1 = np.array([[0.0, 1.0] if has_anchor(t) else [0.0, 0.0] for t in texts_clean])
    fused_l1 = pipeline.W_NEURAL * p_a + pipeline.W_RULE * anchor_l1
    pred_relevant = fused_l1.argmax(axis=1) == A_LABEL2ID["relevan"]
    relevant_rows = int(pred_relevant.sum())
    print(f"relevant_rows={relevant_rows} / {total_rows}")

    df_rel = df[pred_relevant].reset_index(drop=True)
    texts_clean_rel = df_rel["text_clean"].fillna("").astype(str).tolist()

    # --- Layer 2: 6-vector classification (fused 0.75 neural : 0.25 anchor share) ---
    print("Model B inference...")
    id2label_b = sorted(B_LABEL2ID, key=B_LABEL2ID.get)
    if texts_clean_rel:
        p_b = chunked_softmax(model_b, tokenizer, device, texts_clean_rel, args.batch_size)
        anchor_share = np.zeros_like(p_b)
        for i, t in enumerate(texts_clean_rel):
            hints = detect_vector_hints(t)
            total_hints = sum(hints.values())
            if total_hints:
                for v, c in hints.items():
                    anchor_share[i, B_LABEL2ID[v]] = c / total_hints
        fused = pipeline.W_NEURAL * p_b + pipeline.W_RULE * anchor_share
        fused = fused / fused.sum(axis=1, keepdims=True)
        pred_idx = fused.argmax(axis=1)
        pred_label = [id2label_b[i] for i in pred_idx]
        pred_confidence = fused[np.arange(len(pred_idx)), pred_idx]
    else:
        pred_label = []
        pred_confidence = np.array([])

    df_rel = df_rel.assign(
        pred_label=pred_label,
        pred_confidence=pred_confidence,
        platform_norm=df_rel["platform"].map(normalize_platform),
        period=df_rel["published_at"].map(to_period),
    )

    # --- Aggregation (CLAUDE.md Sec 6) ---
    vector_distribution = []
    platform_by_vector = []
    samples_by_vector = {}

    for label in id2label_b:
        sub = df_rel[df_rel["pred_label"] == label]
        count = len(sub)
        vector_distribution.append(
            {
                "label": label,
                "label_display": pipeline.LABEL_DISPLAY[label],
                "count": count,
                "pct": (count / relevant_rows) if relevant_rows else 0.0,
            }
        )

        yt_count = int((sub["platform_norm"] == "youtube").sum())
        x_count = int((sub["platform_norm"] == "x").sum())
        denom = yt_count + x_count
        platform_by_vector.append(
            {
                "label": label,
                "youtube_pct": (yt_count / denom) if denom else 0.0,
                "x_pct": (x_count / denom) if denom else 0.0,
                "youtube_count": yt_count,
                "x_count": x_count,
            }
        )

        picked = (
            sub[sub["platform_norm"].notna()]
            .sort_values("pred_confidence", ascending=False)
            .head(SAMPLES_PER_VECTOR)
        )
        samples_by_vector[label] = [
            {
                "text": row["text"],
                "confidence": float(row["pred_confidence"]),
                "platform": row["platform_norm"],
                "date": row["period"],
            }
            for _, row in picked.iterrows()
        ]

    # --- Temporal + date_range ---
    valid_periods = sorted(p for p in df_rel["period"].dropna().unique())
    distinct_periods = set(valid_periods)
    if len(distinct_periods) >= 3:
        period_counts = (
            df_rel.dropna(subset=["period"]).groupby(["period", "pred_label"]).size()
        )
        temporal = [
            {"period": period, "label": label, "count": int(count)}
            for (period, label), count in period_counts.items()
        ]
        temporal.sort(key=lambda x: x["period"])
    else:
        temporal = None

    date_range = {"start": valid_periods[0], "end": valid_periods[-1]} if valid_periods else None

    result = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_rows": total_rows,
        "relevant_rows": relevant_rows,
        "date_range": date_range,
        "vector_distribution": vector_distribution,
        "platform_by_vector": platform_by_vector,
        "temporal": temporal,
        "samples_by_vector": samples_by_vector,
    }

    # --- Provenance-comparison logging only (NOT written to output - CLAUDE.md Sec 11) ---
    if "layer1_label" in df.columns:
        snorkel_relevant = int((df["layer1_label"] == "relevan").sum())
        print(f"(referensi saja, TIDAK ditulis ke JSON) Snorkel relevant_rows={snorkel_relevant}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
