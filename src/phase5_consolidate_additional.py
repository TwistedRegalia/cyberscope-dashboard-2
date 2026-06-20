#!/usr/bin/env python3
"""
phase5_consolidate_additional.py — Merge scraping tambahan (Phase 3 + 4) ke unified
Penelitian E-ICTT v2.1

Menggabungkan output scraping tambahan:
  - raw_additional_youtube/{vektor}/{video_id}.csv   (Phase 3, skema BARU)
  - raw_additional_tweets/{vektor}/q{idx}.csv         (Phase 4, skema native Tweet Harvest)
ke dalam unified_dataset.csv yang sudah ada (48.496 baris), lalu menulis
unified_dataset_v2.csv.

KONSISTENSI METODOLOGIS:
- Filtering memakai fungsi yang SAMA dengan Phase 5 (apply_filters dari
  phase5_consolidate.py) → reply quality filter, low-signal, dedup-within, dst.
- Decision #2: tweet hanya lang=='in' (buang non-Indonesia).
- Decision #3: reply YouTube lewat quality filter (sudah di apply_filters).
- Cross-dedup: baris baru yang teks-nya (normalized) sudah ada di unified lama → dibuang.
- unified_id baru melanjutkan urutan dari max existing (tidak menimpa ID lama).
- vector_hint diisi ulang via add_diagnostic_hints (diagnostik kasar, BUKAN label final).

Cara pakai:
    python src/phase5_consolidate_additional.py
    # opsi: --existing data/unified_dataset.csv --out data/unified_dataset_v2.csv

Output:
    - data/unified_dataset_v2.csv
    - docs/phase5_merge_report.md
    - data/phase5_merge_stats.json
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime

import pandas as pd

# Reuse logika Phase 5 (filter identik) + helper
from phase5_consolidate import (
    apply_filters,
    add_diagnostic_hints,
    clean_text_basic,
    snowflake_to_datetime,
)

# Kolom skema unified final (urutan harus cocok dengan unified_dataset.csv)
UNIFIED_COLS = [
    "unified_id", "platform", "source_category", "source_file", "text",
    "orig_id", "published_at", "published_at_verified", "is_reply", "author",
    "like_count", "reply_count", "lang", "video_id", "vector_hint",
]


def _coerce_is_reply(val):
    """is_reply Phase 3 ditulis sebagai 'True'/'False'/bool/0/1 → normalisasi ke 0/1."""
    if pd.isna(val):
        return 0
    if isinstance(val, str):
        return 1 if val.strip().lower() in ("true", "1", "yes") else 0
    try:
        return 1 if int(val) == 1 else 0
    except (ValueError, TypeError):
        return 1 if bool(val) else 0


def load_new_youtube(yt_dir):
    """
    Load output Phase 3 (skema BARU):
      comment_id, author, text, likes, replies, published_at, is_reply
    Struktur: {yt_dir}/{vektor}/{video_id}.csv  (vektor = nama subfolder).
    """
    rows, log = [], []
    if not os.path.isdir(yt_dir):
        return pd.DataFrame(rows), log

    for vektor in sorted(os.listdir(yt_dir)):
        vdir = os.path.join(yt_dir, vektor)
        if not os.path.isdir(vdir):
            continue
        for f in sorted(glob.glob(os.path.join(vdir, "*.csv"))):
            video_id = os.path.splitext(os.path.basename(f))[0]
            try:
                df = pd.read_csv(f)
            except Exception as e:
                log.append((f, 0, f"ERROR: {e}"))
                continue
            for _, r in df.iterrows():
                pub = r.get("published_at", None)
                rows.append({
                    "platform": "YouTube",
                    "source_category": vektor,
                    "source_file": f"{vektor}/{os.path.basename(f)}",
                    "video_id": video_id,
                    "text": r.get("text", ""),
                    "orig_id": str(r.get("comment_id", "")),
                    "published_at": pub,
                    "published_at_verified": pub,  # YT timestamp valid (Temuan #2)
                    "is_reply": _coerce_is_reply(r.get("is_reply", 0)),
                    "author": r.get("author", ""),
                    "like_count": r.get("likes", 0),
                    "reply_count": r.get("replies", 0),
                    "lang": "in",
                })
            log.append((f, len(df), f"video_id={video_id}, vektor={vektor}"))
    return pd.DataFrame(rows), log


def load_new_tweets(tw_dir, keep_lang="in"):
    """
    Load output Phase 4 (skema native Tweet Harvest, identik sesi*.csv lama):
      conversation_id_str, created_at, favorite_count, full_text, id_str,
      in_reply_to_screen_name, lang, quote_count, reply_count, retweet_count,
      tweet_url, user_id_str, username
    Struktur: {tw_dir}/{vektor}/q{idx}.csv  (vektor = nama subfolder).
    Decision #2: hanya lang=='in'.
    """
    rows, log = [], []
    if not os.path.isdir(tw_dir):
        return pd.DataFrame(rows), log

    for vektor in sorted(os.listdir(tw_dir)):
        vdir = os.path.join(tw_dir, vektor)
        if not os.path.isdir(vdir):
            continue
        for f in sorted(glob.glob(os.path.join(vdir, "*.csv"))):
            try:
                df = pd.read_csv(f)
            except Exception as e:
                log.append((f, 0, f"ERROR: {e}"))
                continue
            n_raw = len(df)
            if "lang" in df.columns and keep_lang:
                df = df[df["lang"] == keep_lang]
            for _, r in df.iterrows():
                tweet_id = r.get("id_str", None)
                recon = snowflake_to_datetime(tweet_id) if pd.notna(tweet_id) else None
                rows.append({
                    "platform": "X",
                    "source_category": vektor,
                    "source_file": f"{vektor}/{os.path.basename(f)}",
                    "video_id": "",
                    "text": r.get("full_text", ""),
                    "orig_id": str(tweet_id) if pd.notna(tweet_id) else "",
                    "published_at": r.get("created_at", None),
                    "published_at_verified": recon.isoformat() if recon else None,
                    "is_reply": 1 if pd.notna(r.get("in_reply_to_screen_name")) else 0,
                    "author": r.get("username", ""),
                    "like_count": r.get("favorite_count", 0),
                    "reply_count": r.get("reply_count", 0),
                    "lang": r.get("lang", ""),
                })
            log.append((f, n_raw, f"lang={keep_lang}: {len(df)}, vektor={vektor}"))
    return pd.DataFrame(rows), log


def next_uid_start(existing_df):
    """Tentukan index awal unified_id baru = max numeric suffix + 1."""
    if "unified_id" not in existing_df.columns or existing_df.empty:
        return 0
    nums = (
        existing_df["unified_id"].astype(str)
        .str.extract(r"(\d+)", expand=False)
        .dropna().astype(int)
    )
    return int(nums.max()) + 1 if len(nums) else len(existing_df)


def main():
    ap = argparse.ArgumentParser(description="Merge Phase 3+4 scraping ke unified")
    ap.add_argument("--existing", default="data/unified_dataset.csv")
    ap.add_argument("--yt-dir", default="raw_additional_youtube")
    ap.add_argument("--tw-dir", default="raw_additional_tweets")
    ap.add_argument("--out", default="data/unified_dataset_v2.csv")
    ap.add_argument("--report", default="docs/phase5_merge_report.md")
    ap.add_argument("--stats", default="data/phase5_merge_stats.json")
    args = ap.parse_args()

    if not os.path.exists(args.existing):
        print(f"ERROR: existing dataset tidak ditemukan: {args.existing}", file=sys.stderr)
        sys.exit(1)

    print(f"[1/6] Load existing unified: {args.existing}")
    existing = pd.read_csv(args.existing, dtype=str, keep_default_na=False)
    print(f"      {len(existing):,} baris")

    print(f"[2/6] Load scraping baru (YouTube + X) ...")
    df_yt, log_yt = load_new_youtube(args.yt_dir)
    df_tw, log_tw = load_new_tweets(args.tw_dir)
    print(f"      YouTube baru: {len(df_yt):,} | X baru: {len(df_tw):,}")

    if len(df_yt) == 0 and len(df_tw) == 0:
        print("ERROR: Tidak ada data baru. Jalankan Phase 3/4 dulu, atau cek path "
              f"{args.yt_dir}/ dan {args.tw_dir}/.", file=sys.stderr)
        sys.exit(1)

    df_new = pd.concat([df_yt, df_tw], ignore_index=True)
    raw_new_total = len(df_new)

    print(f"[3/6] Filter (logika identik Phase 5) ...")
    df_new_clean, fstats = apply_filters(df_new)
    print(f"      Setelah filter internal: {len(df_new_clean):,}")

    print(f"[4/6] Cross-dedup vs existing ({len(existing):,} baris) ...")
    existing_keys = set(existing["text"].astype(str).apply(clean_text_basic))
    new_key = df_new_clean["text"].astype(str).apply(clean_text_basic)
    dup_mask = new_key.isin(existing_keys)
    n_cross_dup = int(dup_mask.sum())
    df_new_unique = df_new_clean[~dup_mask].copy()
    print(f"      Buang {n_cross_dup:,} duplikat lintas-batch → sisa {len(df_new_unique):,}")

    print(f"[5/6] Tambah vector_hint + unified_id ...")
    df_new_unique = add_diagnostic_hints(df_new_unique)
    start = next_uid_start(existing)
    df_new_unique = df_new_unique.reset_index(drop=True)
    df_new_unique.insert(
        0, "unified_id",
        ["UID" + str(start + i).zfill(6) for i in range(len(df_new_unique))]
    )

    # Samakan kolom dengan existing (tambah yang hilang, urutkan)
    for col in UNIFIED_COLS:
        if col not in df_new_unique.columns:
            df_new_unique[col] = ""
    df_new_unique = df_new_unique[UNIFIED_COLS]

    print(f"[6/6] Gabung + tulis output ...")
    for col in UNIFIED_COLS:
        if col not in existing.columns:
            existing[col] = ""
    merged = pd.concat([existing[UNIFIED_COLS], df_new_unique], ignore_index=True)
    merged.to_csv(args.out, index=False)

    # ---- Stats per vektor (kelas lemah) ----
    new_by_vektor = (
        df_new_unique.groupby("source_category").size().sort_values(ascending=False)
        .to_dict()
    )
    stats = {
        "executed_at": datetime.utcnow().isoformat(),
        "existing_rows": len(existing),
        "raw_new_total": raw_new_total,
        "new_youtube_raw": len(df_yt),
        "new_x_raw": len(df_tw),
        "after_internal_filter": len(df_new_clean),
        "cross_batch_duplicates": n_cross_dup,
        "new_rows_added": len(df_new_unique),
        "merged_total": len(merged),
        "new_by_vektor": {k: int(v) for k, v in new_by_vektor.items()},
        "filter_breakdown": {k: int(v) for k, v in fstats.items()
                             if isinstance(v, (int, float))},
    }
    os.makedirs(os.path.dirname(args.stats) or ".", exist_ok=True)
    with open(args.stats, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    # ---- Report markdown ----
    lines = [
        "# Phase 5 (revisi) — Merge Scraping Tambahan",
        "",
        f"Digabung dari Phase 3 (YouTube) + Phase 4 (X) ke `{os.path.basename(args.existing)}`.",
        "",
        "## 1. Ringkasan",
        "",
        f"- Existing: **{len(existing):,}** baris",
        f"- Raw baru (YT {len(df_yt):,} + X {len(df_tw):,}): **{raw_new_total:,}**",
        f"- Setelah filter internal: **{len(df_new_clean):,}**",
        f"- Duplikat lintas-batch dibuang: **{n_cross_dup:,}**",
        f"- Baris baru ditambahkan: **{len(df_new_unique):,}**",
        f"- **Total merged: {len(merged):,}** → `{args.out}`",
        "",
        "## 2. Baris baru per source_category (vektor asal scraping)",
        "",
        "| Vektor | Baris baru |",
        "|--------|-----------|",
    ]
    for k, v in new_by_vektor.items():
        lines.append(f"| {k} | {v:,} |")
    lines += [
        "",
        "## 3. Vector hint pada data baru (diagnostik kasar, BUKAN label final)",
        "",
        "| Vector Hint | Jumlah |",
        "|-------------|--------|",
    ]
    vh = df_new_unique["vector_hint"].replace("", "NO_HINT").value_counts(dropna=False)
    for k, v in vh.items():
        lines.append(f"| {k if pd.notna(k) and k != '' else 'NO_HINT'} | {v:,} |")
    lines += [
        "",
        "---",
        "",
        "*Langkah berikut: re-run Phase 6 (preprocess) lalu Phase 7 (Snorkel) pada "
        f"`{os.path.basename(args.out)}`. `source_category`/`vector_hint` BUKAN label final.*",
    ]
    os.makedirs(os.path.dirname(args.report) or ".", exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nSelesai!")
    print(f"  - Dataset: {args.out} ({len(merged):,} baris, +{len(df_new_unique):,})")
    print(f"  - Report : {args.report}")
    print(f"  - Stats  : {args.stats}")
    if new_by_vektor:
        print(f"  - Baris baru per vektor:")
        for k, v in new_by_vektor.items():
            print(f"      {k}: +{v:,}")


if __name__ == "__main__":
    main()
