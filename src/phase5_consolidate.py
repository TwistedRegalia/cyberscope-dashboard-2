#!/usr/bin/env python3
"""
phase5_consolidate.py — Konsolidasi, Filter, dan Dedup
Penelitian E-ICTT v2.1

Menggabungkan 59 file CSV (41 X Tweet Harvest + 18 YouTube) menjadi satu
dataset unified yang bersih, dengan menerapkan keputusan metodologis:

KEPUTUSAN YANG DITERAPKAN:
1. X: hanya lang=in (buang non-Indonesia)
2. YouTube top-level: dipertahankan semua (setelah dedup + filter dasar)
3. YouTube reply: quality filter (min 5 kata + anchor vektor + bukan pure afirmasi)
4. Dedup: exact text (cross-platform aware)
5. Filter dasar: buang teks terlalu pendek, low-signal, terlalu panjang
6. Timestamp X: validasi via Snowflake (created_at terbukti akurat)
7. Metadata source category dipertahankan (dari nama file) untuk audit

Cara pakai:
    python phase5_consolidate.py --rawdir ./raw --outdir ./output

Output:
    - unified_dataset.csv     : dataset bersih unified
    - phase5_filter_report.md : laporan filtering
    - phase5_stats.json       : statistik mentah
"""

import argparse
import glob
import json
import os
import re
from datetime import datetime, timezone

import pandas as pd

# Import pattern library (harus di direktori yang sama)
from anchor_patterns import has_anchor, top_vector_hint, detect_vector_hints


# ============================================================
# KONFIGURASI
# ============================================================

TWITTER_EPOCH = 1288834974657  # ms

# Pemetaan prefix sesi -> kategori sumber (vektor asal scraping)
X_CATEGORY_MAP = {
    'sesi1': 'phishing_rekayasa_sosial',
    'sesi1b': 'phishing_rekayasa_sosial',
    'sesi1c': 'phishing_rekayasa_sosial',
    'sesi2': 'penipuan_ewallet_qris',
    'sesi2b': 'penipuan_ewallet_qris',
    'sesi3': 'malware_apk',
    'sesi3b': 'malware_apk',
    'sesi4': 'judi_online_pinjol',
    'sesi4b': 'judi_online_pinjol',
    'sesi4c': 'judi_online_pinjol',
    'sesi4d': 'judi_online_pinjol',
    'sesi5': 'peretasan_pencurian_identitas',
    'sesi5b': 'peretasan_pencurian_identitas',
    'sesi5c': 'peretasan_pencurian_identitas',
    'sesi5d': 'peretasan_pencurian_identitas',
    'sesi5e': 'peretasan_pencurian_identitas',
    'sesi6': 'deepfake_penipuan_ai',
    'sesi6b': 'deepfake_penipuan_ai',
    'sesi6c': 'deepfake_penipuan_ai',
    'sesi6d': 'deepfake_penipuan_ai',
    'sesi6e': 'deepfake_penipuan_ai',
}

# Pemetaan kategori YouTube (dari nama file yt-<kategori>-<videoid>)
YT_CATEGORY_MAP = {
    'phishing': 'phishing_rekayasa_sosial',
    'ewallet': 'penipuan_ewallet_qris',
    'malware': 'malware_apk',
    'pinjol': 'judi_online_pinjol',
    'judi': 'judi_online_pinjol',
    'hack': 'peretasan_pencurian_identitas',
    'deepfake': 'deepfake_penipuan_ai',
}

# Pure afirmasi set (untuk reply filter)
PURE_AFIRMASI = {
    'iya', 'iyaa', 'iyaaa', 'bener', 'benar', 'betul', 'setuju', 'sama',
    'wkwk', 'wkwkwk', 'anjir', 'anjay', 'parah', 'ngeri', 'serem', 'gilaa', 'gila',
    'astaga', 'ya', 'yaa', 'yup', 'yoi', 'mantap', 'mantul', 'nice', 'ok', 'oke',
    'sip', 'hadir', 'up', 'naik', 'real', 'fakta', 'bjir', 'njir', 'hadeh', 'duh',
    'aduh', 'kak', 'min', 'bang', 'wah', 'waduh', 'true', 'yes', 'no', 'ga', 'gak',
    'engga', 'nggak', 'hmm', 'ehh', 'eh', 'lah', 'kok', 'masa', 'mantapp', 'keren',
}


# ============================================================
# FUNGSI UTILITAS
# ============================================================

def snowflake_to_datetime(tweet_id):
    """Validasi/rekonstruksi timestamp dari Twitter Snowflake ID."""
    try:
        tid = int(tweet_id)
        ms = (tid >> 22) + TWITTER_EPOCH
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    except Exception:
        return None


def clean_text_basic(text):
    """Normalisasi ringan untuk dedup (bukan preprocessing final)."""
    if not isinstance(text, str):
        return ""
    t = text.strip().lower()
    t = re.sub(r'\s+', ' ', t)
    return t


def word_count(text):
    return len(str(text).split())


def is_pure_afirmasi(text):
    cleaned = re.sub(r'[^\w\s]', '', str(text).lower()).strip()
    words = cleaned.split()
    if len(words) == 0:
        return True
    return all(w in PURE_AFIRMASI for w in words)


def is_low_signal(text):
    """Teks tanpa konten bermakna (emoji/punctuation only)."""
    cleaned = re.sub(r'[^\w\s]', '', str(text))
    cleaned = re.sub(r'\s+', '', cleaned)
    return len(cleaned) < 3


# ============================================================
# LOADER PER PLATFORM
# ============================================================

def load_x_files(rawdir):
    """Load semua file X (sesi*), petakan ke skema unified."""
    files = sorted(glob.glob(os.path.join(rawdir, 'sesi*.csv')))
    rows = []
    log = []

    for f in files:
        basename = os.path.basename(f)
        prefix = basename.replace('.csv', '').split('-')[0]
        source_cat = X_CATEGORY_MAP.get(prefix, 'unknown')

        try:
            df = pd.read_csv(f)
        except Exception as e:
            log.append((basename, 0, f"ERROR: {e}"))
            continue

        n_raw = len(df)
        # Filter lang=in
        if 'lang' in df.columns:
            df = df[df['lang'] == 'in']
        n_after_lang = len(df)

        for _, r in df.iterrows():
            tweet_id = r.get('id_str', None)
            created = r.get('created_at', None)
            # Validasi timestamp via snowflake
            recon = snowflake_to_datetime(tweet_id) if pd.notna(tweet_id) else None

            rows.append({
                'platform': 'X',
                'source_category': source_cat,
                'source_file': basename,
                'text': r.get('full_text', ''),
                'orig_id': str(tweet_id) if pd.notna(tweet_id) else '',
                'published_at': created,
                'published_at_verified': recon.isoformat() if recon else None,
                'is_reply': 1 if pd.notna(r.get('in_reply_to_screen_name')) else 0,
                'author': r.get('username', ''),
                'like_count': r.get('favorite_count', 0),
                'reply_count': r.get('reply_count', 0),
                'lang': r.get('lang', ''),
            })

        log.append((basename, n_raw, f"lang=in: {n_after_lang}"))

    return pd.DataFrame(rows), log


def load_yt_files(rawdir):
    """Load semua file YouTube (yt-*), petakan ke skema unified."""
    files = sorted(glob.glob(os.path.join(rawdir, 'yt-*.csv')))
    rows = []
    log = []

    for f in files:
        basename = os.path.basename(f)
        parts = basename.replace('.csv', '').split('-')
        category_raw = parts[1] if len(parts) > 1 else 'unknown'
        video_id = parts[-1] if len(parts) > 2 else 'unknown'
        source_cat = YT_CATEGORY_MAP.get(category_raw, 'unknown')

        try:
            df = pd.read_csv(f)
        except Exception as e:
            log.append((basename, 0, f"ERROR: {e}"))
            continue

        n_raw = len(df)

        for _, r in df.iterrows():
            rows.append({
                'platform': 'YouTube',
                'source_category': source_cat,
                'source_file': basename,
                'video_id': video_id,
                'text': r.get('text', ''),
                'orig_id': str(r.get('id', '')),
                'published_at': r.get('publishedAt', None),
                'published_at_verified': r.get('publishedAt', None),  # YT timestamp valid
                'is_reply': int(r.get('isReply', 0)) if pd.notna(r.get('isReply')) else 0,
                'author': r.get('authorName', ''),
                'like_count': r.get('likeCount', 0),
                'reply_count': r.get('replyCount', 0),
                'lang': 'in',  # asumsi YT Indonesia
            })

        log.append((basename, n_raw, f"video_id: {video_id}"))

    return pd.DataFrame(rows), log


# ============================================================
# FILTERING PIPELINE
# ============================================================

def apply_filters(df):
    """
    Terapkan filter berjenjang. Mengembalikan (df_clean, filter_stats).
    """
    stats = {}
    stats['input_total'] = len(df)

    # Tambah kolom bantu
    df = df.copy()
    df['_text_str'] = df['text'].astype(str)
    df['_wc'] = df['_text_str'].apply(word_count)
    df['_char_len'] = df['_text_str'].str.len()
    df['_clean'] = df['_text_str'].apply(clean_text_basic)

    # FILTER 1: buang null/empty
    before = len(df)
    df = df[df['_text_str'].str.strip().str.len() > 0]
    stats['removed_empty'] = before - len(df)

    # FILTER 2: buang low-signal (emoji/punct only)
    before = len(df)
    df = df[~df['_text_str'].apply(is_low_signal)]
    stats['removed_low_signal'] = before - len(df)

    # FILTER 3: buang teks terlalu pendek (< 3 kata untuk top-level/X juga)
    # Catatan: reply punya filter lebih ketat di FILTER 5
    before = len(df)
    df = df[df['_char_len'] >= 10]  # min 10 karakter
    stats['removed_too_short'] = before - len(df)

    # FILTER 4: buang teks terlalu panjang (> 2000 char, likely copypasta/spam)
    before = len(df)
    df = df[df['_char_len'] <= 2000]
    stats['removed_too_long'] = before - len(df)

    # FILTER 5: REPLY QUALITY FILTER (Opsi 1)
    # Reply harus: min 5 kata + ada anchor + bukan pure afirmasi
    # Top-level dan X tidak terkena filter ketat ini
    is_reply_mask = df['is_reply'] == 1
    n_reply_before = is_reply_mask.sum()

    df['_has_anchor'] = df['_text_str'].apply(has_anchor)
    df['_pure_afirmasi'] = df['_text_str'].apply(is_pure_afirmasi)

    # Reply gagal jika: < 5 kata ATAU no anchor ATAU pure afirmasi
    reply_fail = is_reply_mask & (
        (df['_wc'] < 5) | (~df['_has_anchor']) | (df['_pure_afirmasi'])
    )
    stats['removed_reply_lowquality'] = int(reply_fail.sum())
    stats['reply_input'] = int(n_reply_before)
    stats['reply_passed'] = int(n_reply_before - reply_fail.sum())

    df = df[~reply_fail]

    # FILTER 6: DEDUP exact (berdasarkan _clean, cross-platform)
    before = len(df)
    df = df.drop_duplicates(subset=['_clean'], keep='first')
    stats['removed_duplicates'] = before - len(df)

    stats['output_total'] = len(df)

    # Bersihkan kolom bantu
    df = df.drop(columns=['_text_str', '_wc', '_char_len', '_clean',
                          '_has_anchor', '_pure_afirmasi'], errors='ignore')

    return df, stats


def add_diagnostic_hints(df):
    """Tambah kolom diagnostik vektor (crude pre-label, BUKAN final)."""
    df = df.copy()
    df['vector_hint'] = df['text'].astype(str).apply(top_vector_hint)
    return df


# ============================================================
# REPORTING
# ============================================================

def generate_report(load_log_x, load_log_yt, filter_stats, df_final):
    lines = []
    lines.append("# Phase 5 — Filter & Dedup Report")
    lines.append("")
    lines.append("Konsolidasi 59 file CSV menjadi dataset unified E-ICTT v2.1.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary
    lines.append("## 1. Ringkasan")
    lines.append("")
    lines.append(f"- **Input total (raw gabungan):** {filter_stats['input_total']:,}")
    lines.append(f"- **Output total (bersih):** {filter_stats['output_total']:,}")
    reduction = (1 - filter_stats['output_total'] / filter_stats['input_total']) * 100
    lines.append(f"- **Reduction rate:** {reduction:.1f}%")
    lines.append("")

    # Filter breakdown
    lines.append("## 2. Breakdown Filtering")
    lines.append("")
    lines.append("| Filter | Dibuang |")
    lines.append("|--------|---------|")
    lines.append(f"| Empty/null | {filter_stats['removed_empty']:,} |")
    lines.append(f"| Low-signal (emoji/punct) | {filter_stats['removed_low_signal']:,} |")
    lines.append(f"| Terlalu pendek (<10 char) | {filter_stats['removed_too_short']:,} |")
    lines.append(f"| Terlalu panjang (>2000 char) | {filter_stats['removed_too_long']:,} |")
    lines.append(f"| Reply low-quality | {filter_stats['removed_reply_lowquality']:,} |")
    lines.append(f"| Duplikat exact | {filter_stats['removed_duplicates']:,} |")
    lines.append("")

    # Reply filter detail
    lines.append("## 3. Reply Quality Filter (Opsi 1)")
    lines.append("")
    lines.append("Kriteria: min 5 kata + ada anchor vektor + bukan pure afirmasi")
    lines.append("")
    lines.append(f"- Reply input: {filter_stats['reply_input']:,}")
    lines.append(f"- Reply lolos: {filter_stats['reply_passed']:,} "
                 f"({filter_stats['reply_passed']/filter_stats['reply_input']*100:.1f}%)")
    lines.append("")

    # Distribusi final
    lines.append("## 4. Distribusi Dataset Final")
    lines.append("")
    lines.append("### 4.1 Per Platform")
    lines.append("")
    lines.append("| Platform | Jumlah |")
    lines.append("|----------|--------|")
    for k, v in df_final['platform'].value_counts().items():
        lines.append(f"| {k} | {v:,} |")
    lines.append("")

    lines.append("### 4.2 Per Source Category (asal scraping, BUKAN label final)")
    lines.append("")
    lines.append("| Source Category | Jumlah |")
    lines.append("|-----------------|--------|")
    for k, v in df_final['source_category'].value_counts().items():
        lines.append(f"| {k} | {v:,} |")
    lines.append("")

    lines.append("### 4.3 Vector Hint (diagnostik crude, BUKAN label final)")
    lines.append("")
    lines.append("Estimasi distribusi berdasarkan anchor pattern. Label final ditentukan Snorkel.")
    lines.append("")
    lines.append("| Vector Hint | Jumlah |")
    lines.append("|-------------|--------|")
    vh = df_final['vector_hint'].value_counts(dropna=False)
    for k, v in vh.items():
        lines.append(f"| {k if pd.notna(k) else 'NO_HINT (perlu Snorkel)'} | {v:,} |")
    lines.append("")

    lines.append("### 4.4 Reply vs Top-level")
    lines.append("")
    lines.append("| Tipe | Jumlah |")
    lines.append("|------|--------|")
    for k, v in df_final['is_reply'].value_counts().items():
        label = 'Reply' if k == 1 else 'Top-level/Tweet'
        lines.append(f"| {label} | {v:,} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Catatan: `source_category` dan `vector_hint` BUKAN label final. "
                 "Label diskursif final ditentukan via Snorkel weak supervision (Phase 7) "
                 "dengan relevance filter dan hierarki prioritas E-ICTT v2.1.*")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Phase 5 Consolidate & Filter")
    parser.add_argument('--rawdir', required=True, help='Direktori berisi file CSV mentah')
    parser.add_argument('--outdir', default='./phase5_output', help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print("[1/6] Loading file X (Tweet Harvest) ...")
    df_x, log_x = load_x_files(args.rawdir)
    print(f"      X loaded: {len(df_x):,} baris (setelah lang=in)")

    print("[2/6] Loading file YouTube ...")
    df_yt, log_yt = load_yt_files(args.rawdir)
    print(f"      YouTube loaded: {len(df_yt):,} baris")

    print("[3/6] Menggabungkan ...")
    df_all = pd.concat([df_x, df_yt], ignore_index=True)
    print(f"      Total gabungan: {len(df_all):,} baris")

    print("[4/6] Menerapkan filter ...")
    df_clean, filter_stats = apply_filters(df_all)
    print(f"      Setelah filter: {len(df_clean):,} baris")

    print("[5/6] Menambah diagnostik vector hint ...")
    df_clean = add_diagnostic_hints(df_clean)

    print("[6/6] Generate output ...")
    # Tambah ID unik
    df_clean = df_clean.reset_index(drop=True)
    df_clean.insert(0, 'unified_id', ['UID' + str(i).zfill(6) for i in range(len(df_clean))])

    # Simpan dataset
    out_csv = os.path.join(args.outdir, 'unified_dataset.csv')
    df_clean.to_csv(out_csv, index=False)

    # Simpan report
    report = generate_report(log_x, log_yt, filter_stats, df_clean)
    with open(os.path.join(args.outdir, 'phase5_filter_report.md'), 'w') as f:
        f.write(report)

    # Simpan stats JSON
    with open(os.path.join(args.outdir, 'phase5_stats.json'), 'w') as f:
        json.dump(filter_stats, f, indent=2, ensure_ascii=False)

    print(f"\nSelesai!")
    print(f"  - Dataset: {out_csv} ({len(df_clean):,} baris)")
    print(f"  - Report: {os.path.join(args.outdir, 'phase5_filter_report.md')}")
    print(f"  - Stats: {os.path.join(args.outdir, 'phase5_stats.json')}")


if __name__ == '__main__':
    main()
