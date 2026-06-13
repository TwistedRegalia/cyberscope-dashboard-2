#!/usr/bin/env python3
"""
Phase 0 — Audit Script untuk master_dataset.csv
Penelitian: Klasifikasi Otomatis Diskursus Vektor Ancaman Siber (E-ICTT v2.1)

Tujuan: Menganalisis karakteristik dataset raw untuk memahami:
- Distribusi platform, label, temporal
- Kualitas teks (panjang, duplikasi, noise)
- Potensi bias dan limitasi metodologis

Cara pakai:
    python audit_dataset.py --input master_dataset.csv --outdir ./audit_output

Output:
    - audit_report.md       : laporan markdown lengkap
    - audit_stats.json      : statistik mentah untuk referensi
    - figures/              : visualisasi (jika matplotlib tersedia)

Script ini adaptif terhadap variasi nama kolom dan robust terhadap missing data.
"""

import argparse
import json
import os
import sys
from collections import Counter
import re


def load_dataset(path):
    """Load CSV dengan deteksi separator otomatis."""
    import pandas as pd
    # Coba comma dulu, fallback ke separator lain
    for sep in [',', ';', '\t']:
        try:
            df = pd.read_csv(path, sep=sep)
            if df.shape[1] > 1:
                return df
        except Exception:
            continue
    # Last resort
    return pd.read_csv(path)


def detect_columns(df):
    """Deteksi kolom kunci secara adaptif berdasarkan nama umum."""
    cols = {c.lower(): c for c in df.columns}
    mapping = {}

    # Text column
    for cand in ['full_text', 'text', 'content', 'comment', 'tweet', 'komentar']:
        if cand in cols:
            mapping['text'] = cols[cand]
            break

    # Label column
    for cand in ['ictt_label', 'label', 'category', 'kategori', 'class']:
        if cand in cols:
            mapping['label'] = cols[cand]
            break

    # Platform column
    for cand in ['platform', 'source_platform', 'sumber']:
        if cand in cols:
            mapping['platform'] = cols[cand]
            break

    # Date column
    for cand in ['created_at', 'date', 'timestamp', 'tanggal', 'datetime']:
        if cand in cols:
            mapping['date'] = cols[cand]
            break

    # Year column
    for cand in ['source_year', 'year', 'tahun']:
        if cand in cols:
            mapping['year'] = cols[cand]
            break

    # Language column
    for cand in ['lang', 'language', 'bahasa']:
        if cand in cols:
            mapping['lang'] = cols[cand]
            break

    # ID column
    for cand in ['content_id', 'id', 'tweet_id', 'comment_id']:
        if cand in cols:
            mapping['id'] = cols[cand]
            break

    # Video ID (YouTube)
    for cand in ['video_id', 'videoid', 'video']:
        if cand in cols:
            mapping['video_id'] = cols[cand]
            break

    return mapping


def basic_stats(df, colmap):
    """Statistik dasar dataset."""
    stats = {}
    stats['total_rows'] = int(len(df))
    stats['total_columns'] = int(df.shape[1])
    stats['columns'] = list(df.columns)
    stats['detected_columns'] = colmap
    return stats


def text_quality_analysis(df, colmap):
    """Analisis kualitas teks: panjang, duplikasi, noise."""
    import pandas as pd
    text_col = colmap.get('text')
    if not text_col:
        return {'error': 'No text column detected'}

    s = df[text_col].astype(str)
    text_len = s.str.len()
    word_count = s.str.split().str.len()

    result = {
        'char_length': {
            'mean': round(float(text_len.mean()), 2),
            'std': round(float(text_len.std()), 2),
            'min': int(text_len.min()),
            'p25': int(text_len.quantile(0.25)),
            'median': int(text_len.median()),
            'p75': int(text_len.quantile(0.75)),
            'max': int(text_len.max()),
        },
        'word_count': {
            'mean': round(float(word_count.mean()), 2),
            'std': round(float(word_count.std()), 2),
            'min': int(word_count.min()),
            'median': int(word_count.median()),
            'max': int(word_count.max()),
        },
        'noise_indicators': {
            'very_short_lt5': int((text_len < 5).sum()),
            'short_lt10': int((text_len < 10).sum()),
            'very_long_gt1000': int((text_len > 1000).sum()),
            'very_long_gt2000': int((text_len > 2000).sum()),
            'single_word': int((word_count <= 1).sum()),
        },
        'duplicates': {
            'exact_text_duplicates': int(df[text_col].duplicated().sum()),
        }
    }

    # Emoji-only / punctuation-only detection
    def is_low_signal(t):
        t = str(t).strip()
        # Hapus emoji, whitespace, punctuation
        cleaned = re.sub(r'[^\w\s]', '', t)
        cleaned = re.sub(r'\s+', '', cleaned)
        return len(cleaned) < 3

    low_signal = s.apply(is_low_signal).sum()
    result['noise_indicators']['low_signal_emoji_punct'] = int(low_signal)

    if colmap.get('id'):
        result['duplicates']['exact_id_duplicates'] = int(df[colmap['id']].duplicated().sum())

    return result


def distribution_analysis(df, colmap):
    """Analisis distribusi kategori utama."""
    result = {}

    for key in ['platform', 'label', 'lang', 'year']:
        col = colmap.get(key)
        if col:
            vc = df[col].value_counts(dropna=False)
            result[key] = {str(k): int(v) for k, v in vc.items()}

    # Crosstab platform x label
    if colmap.get('platform') and colmap.get('label'):
        import pandas as pd
        ct = pd.crosstab(df[colmap['label']], df[colmap['platform']])
        result['crosstab_label_platform'] = {
            str(idx): {str(c): int(ct.loc[idx, c]) for c in ct.columns}
            for idx in ct.index
        }

    return result


def imbalance_analysis(df, colmap):
    """Analisis ketidakseimbangan label."""
    label_col = colmap.get('label')
    if not label_col:
        return {'error': 'No label column'}

    vc = df[label_col].value_counts()
    max_count = int(vc.max())
    min_count = int(vc.min())

    return {
        'num_classes': int(len(vc)),
        'max_class': {'label': str(vc.idxmax()), 'count': max_count},
        'min_class': {'label': str(vc.idxmin()), 'count': min_count},
        'imbalance_ratio': round(max_count / min_count, 2) if min_count > 0 else None,
        'per_class_percentage': {
            str(k): round(v / len(df) * 100, 2) for k, v in vc.items()
        }
    }


def video_source_analysis(df, colmap):
    """Analisis sumber video YouTube (untuk deteksi selection bias)."""
    video_col = colmap.get('video_id')
    platform_col = colmap.get('platform')
    if not video_col:
        return {'note': 'No video_id column — skip video source analysis'}

    # Filter hanya YouTube jika ada platform
    yt = df[df[video_col].notna()]
    if len(yt) == 0:
        return {'note': 'No YouTube data with video_id'}

    video_counts = yt[video_col].value_counts()
    result = {
        'unique_videos': int(yt[video_col].nunique()),
        'total_youtube_comments': int(len(yt)),
        'comments_per_video': {
            'mean': round(float(video_counts.mean()), 2),
            'median': int(video_counts.median()),
            'max': int(video_counts.max()),
            'min': int(video_counts.min()),
        },
        'top_10_videos_by_comments': {
            str(k): int(v) for k, v in video_counts.head(10).items()
        },
        'concentration': {
            'top_5_videos_share_pct': round(
                video_counts.head(5).sum() / len(yt) * 100, 2),
            'top_10_videos_share_pct': round(
                video_counts.head(10).sum() / len(yt) * 100, 2),
        }
    }

    # Video per label (selection bias indicator)
    if colmap.get('label'):
        label_col = colmap['label']
        video_label = yt.groupby(video_col)[label_col].agg(
            lambda x: x.value_counts().index[0])
        label_video_counts = video_label.value_counts()
        result['videos_per_label'] = {
            str(k): int(v) for k, v in label_video_counts.items()
        }

    return result


def temporal_analysis(df, colmap):
    """Analisis distribusi temporal."""
    result = {}
    year_col = colmap.get('year')
    if year_col:
        vc = df[year_col].value_counts(dropna=False)
        result['by_year'] = {str(k): int(v) for k, v in vc.items()}

    date_col = colmap.get('date')
    if date_col:
        import pandas as pd
        try:
            dates = pd.to_datetime(df[date_col], errors='coerce')
            valid = dates.notna().sum()
            result['date_parsing'] = {
                'parseable': int(valid),
                'unparseable': int(len(df) - valid),
            }
            if valid > 0:
                result['date_range'] = {
                    'earliest': str(dates.min()),
                    'latest': str(dates.max()),
                }
        except Exception as e:
            result['date_error'] = str(e)

    return result


def top_terms_analysis(df, colmap, top_n=30):
    """Analisis top unigram dan bigram per dataset (crude, untuk insight topik)."""
    text_col = colmap.get('text')
    if not text_col:
        return {}

    # Stopword Indonesia minimal (untuk insight saja, bukan preprocessing final)
    stopwords = set("""
        yang di ke dari dan atau ini itu untuk dengan pada adalah ada tidak
        gak ga nggak ya nya saya aku kamu dia kita mereka juga sudah akan
        bisa mau ini itu ke si the a an is are was were be to of in on at
        kalo kalau kayak gitu gini aja deh sih lah kok dong nih kan udah
        biar tapi terus jadi banget bgt yg utk dgn klo
    """.split())

    all_words = []
    for t in df[text_col].astype(str):
        # Lowercase, hapus URL, mention, hashtag symbol, punctuation
        t = t.lower()
        t = re.sub(r'http\S+|www\.\S+', '', t)
        t = re.sub(r'@\w+', '', t)
        t = re.sub(r'#', '', t)
        t = re.sub(r'[^\w\s]', ' ', t)
        words = [w for w in t.split() if len(w) > 2 and w not in stopwords and not w.isdigit()]
        all_words.extend(words)

    unigram_counts = Counter(all_words)

    # Bigrams
    bigrams = []
    for t in df[text_col].astype(str):
        t = t.lower()
        t = re.sub(r'http\S+|www\.\S+', '', t)
        t = re.sub(r'@\w+', '', t)
        t = re.sub(r'[^\w\s]', ' ', t)
        words = [w for w in t.split() if len(w) > 2 and w not in stopwords and not w.isdigit()]
        bigrams.extend([f"{words[i]} {words[i+1]}" for i in range(len(words)-1)])

    bigram_counts = Counter(bigrams)

    return {
        'top_unigrams': dict(unigram_counts.most_common(top_n)),
        'top_bigrams': dict(bigram_counts.most_common(top_n)),
    }


def generate_markdown_report(all_stats, colmap):
    """Generate laporan markdown dari semua statistik."""
    lines = []
    lines.append("# Audit Report — master_dataset.csv")
    lines.append("")
    lines.append("**Phase 0 — Technical Roadmap E-ICTT v2.1**")
    lines.append("")
    lines.append("Laporan ini dihasilkan otomatis oleh `audit_dataset.py` untuk memahami "
                 "karakteristik dataset raw sebelum tahap scraping stratified dan modeling.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 1. Overview
    b = all_stats['basic']
    lines.append("## 1. Overview Dataset")
    lines.append("")
    lines.append(f"- **Total baris:** {b['total_rows']:,}")
    lines.append(f"- **Total kolom:** {b['total_columns']}")
    lines.append(f"- **Kolom terdeteksi:** {', '.join(b['columns'])}")
    lines.append("")
    lines.append("Pemetaan kolom kunci yang terdeteksi:")
    lines.append("")
    lines.append("| Peran | Kolom |")
    lines.append("|-------|-------|")
    for role, col in colmap.items():
        lines.append(f"| {role} | `{col}` |")
    lines.append("")

    # 2. Distribusi
    d = all_stats['distribution']
    lines.append("## 2. Distribusi Kategori")
    lines.append("")
    if 'platform' in d:
        lines.append("### 2.1 Distribusi Platform")
        lines.append("")
        lines.append("| Platform | Jumlah | Persentase |")
        lines.append("|----------|--------|------------|")
        total = b['total_rows']
        for k, v in d['platform'].items():
            lines.append(f"| {k} | {v:,} | {round(v/total*100, 1)}% |")
        lines.append("")

    if 'label' in d:
        lines.append("### 2.2 Distribusi Label ICTT")
        lines.append("")
        lines.append("| Label | Jumlah | Persentase |")
        lines.append("|-------|--------|------------|")
        total = b['total_rows']
        for k, v in sorted(d['label'].items(), key=lambda x: -x[1]):
            lines.append(f"| {k} | {v:,} | {round(v/total*100, 1)}% |")
        lines.append("")

    if 'crosstab_label_platform' in d:
        lines.append("### 2.3 Crosstab Label × Platform")
        lines.append("")
        ct = d['crosstab_label_platform']
        platforms = list(next(iter(ct.values())).keys())
        header = "| Label | " + " | ".join(platforms) + " | Total |"
        sep = "|-------|" + "|".join(["-------"] * (len(platforms)+1)) + "|"
        lines.append(header)
        lines.append(sep)
        for label, counts in ct.items():
            row_total = sum(counts.values())
            row = f"| {label} | " + " | ".join(str(counts[p]) for p in platforms) + f" | {row_total} |"
            lines.append(row)
        lines.append("")

    # 3. Imbalance
    im = all_stats['imbalance']
    lines.append("## 3. Analisis Ketidakseimbangan Label")
    lines.append("")
    lines.append(f"- **Jumlah kelas:** {im['num_classes']}")
    lines.append(f"- **Kelas terbesar:** `{im['max_class']['label']}` ({im['max_class']['count']:,})")
    lines.append(f"- **Kelas terkecil:** `{im['min_class']['label']}` ({im['min_class']['count']:,})")
    lines.append(f"- **Imbalance ratio:** {im['imbalance_ratio']}:1")
    lines.append("")

    # 4. Temporal
    t = all_stats['temporal']
    lines.append("## 4. Analisis Temporal")
    lines.append("")
    if 'by_year' in t:
        lines.append("### 4.1 Distribusi per Tahun")
        lines.append("")
        lines.append("| Tahun | Jumlah |")
        lines.append("|-------|--------|")
        for k, v in t['by_year'].items():
            lines.append(f"| {k} | {v:,} |")
        lines.append("")
    if 'date_range' in t:
        lines.append(f"- **Rentang tanggal:** {t['date_range']['earliest']} — {t['date_range']['latest']}")
        lines.append("")
    if 'date_parsing' in t:
        lines.append(f"- **Tanggal parseable:** {t['date_parsing']['parseable']:,} / "
                     f"unparseable: {t['date_parsing']['unparseable']:,}")
        lines.append("")

    # 5. Text Quality
    tq = all_stats['text_quality']
    lines.append("## 5. Kualitas Teks")
    lines.append("")
    if 'char_length' in tq:
        cl = tq['char_length']
        lines.append("### 5.1 Panjang Teks (karakter)")
        lines.append("")
        lines.append(f"- Mean: {cl['mean']} | Median: {cl['median']} | "
                     f"P25: {cl['p25']} | P75: {cl['p75']}")
        lines.append(f"- Min: {cl['min']} | Max: {cl['max']}")
        lines.append("")
    if 'word_count' in tq:
        wc = tq['word_count']
        lines.append("### 5.2 Jumlah Kata")
        lines.append("")
        lines.append(f"- Mean: {wc['mean']} | Median: {wc['median']} | Max: {wc['max']}")
        lines.append("")
    if 'noise_indicators' in tq:
        ni = tq['noise_indicators']
        lines.append("### 5.3 Indikator Noise")
        lines.append("")
        lines.append("| Indikator | Jumlah |")
        lines.append("|-----------|--------|")
        lines.append(f"| Teks < 5 karakter | {ni.get('very_short_lt5', 0):,} |")
        lines.append(f"| Teks < 10 karakter | {ni.get('short_lt10', 0):,} |")
        lines.append(f"| Teks > 1000 karakter | {ni.get('very_long_gt1000', 0):,} |")
        lines.append(f"| Teks > 2000 karakter | {ni.get('very_long_gt2000', 0):,} |")
        lines.append(f"| Single word | {ni.get('single_word', 0):,} |")
        lines.append(f"| Low signal (emoji/punct) | {ni.get('low_signal_emoji_punct', 0):,} |")
        lines.append("")
    if 'duplicates' in tq:
        dup = tq['duplicates']
        lines.append("### 5.4 Duplikasi")
        lines.append("")
        lines.append(f"- Exact text duplicates: {dup.get('exact_text_duplicates', 0):,}")
        if 'exact_id_duplicates' in dup:
            lines.append(f"- Exact ID duplicates: {dup['exact_id_duplicates']:,}")
        lines.append("")

    # 6. Video Source (selection bias)
    vs = all_stats.get('video_source', {})
    if vs and 'unique_videos' in vs:
        lines.append("## 6. Analisis Sumber Video (Selection Bias)")
        lines.append("")
        lines.append(f"- **Jumlah video unik:** {vs['unique_videos']:,}")
        lines.append(f"- **Total komentar YouTube:** {vs['total_youtube_comments']:,}")
        cpv = vs['comments_per_video']
        lines.append(f"- **Komentar per video:** mean {cpv['mean']}, median {cpv['median']}, "
                     f"max {cpv['max']}, min {cpv['min']}")
        lines.append("")
        conc = vs['concentration']
        lines.append(f"- **Konsentrasi:** top 5 video = {conc['top_5_videos_share_pct']}% data, "
                     f"top 10 video = {conc['top_10_videos_share_pct']}% data")
        lines.append("")
        if 'videos_per_label' in vs:
            lines.append("### 6.1 Jumlah Video per Label (dominan)")
            lines.append("")
            lines.append("| Label | Jumlah Video |")
            lines.append("|-------|--------------|")
            for k, v in sorted(vs['videos_per_label'].items(), key=lambda x: -x[1]):
                lines.append(f"| {k} | {v} |")
            lines.append("")

    # 7. Top Terms
    tt = all_stats.get('top_terms', {})
    if tt.get('top_unigrams'):
        lines.append("## 7. Top Terms (Insight Topik)")
        lines.append("")
        lines.append("### 7.1 Top 30 Unigram")
        lines.append("")
        uni = tt['top_unigrams']
        lines.append(", ".join(f"{k} ({v})" for k, v in list(uni.items())[:30]))
        lines.append("")
        lines.append("### 7.2 Top 30 Bigram")
        lines.append("")
        bi = tt['top_bigrams']
        lines.append(", ".join(f"{k} ({v})" for k, v in list(bi.items())[:30]))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Laporan dihasilkan otomatis. Interpretasi dan rekomendasi tindak lanjut "
                 "dibahas terpisah dalam diskusi metodologi.*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit dataset Phase 0")
    parser.add_argument('--input', required=True, help='Path ke master_dataset.csv')
    parser.add_argument('--outdir', default='./audit_output', help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print(f"[1/8] Loading dataset dari {args.input} ...")
    df = load_dataset(args.input)
    print(f"      Loaded: {df.shape[0]} baris, {df.shape[1]} kolom")

    print("[2/8] Deteksi kolom ...")
    colmap = detect_columns(df)
    print(f"      Detected: {colmap}")

    print("[3/8] Statistik dasar ...")
    basic = basic_stats(df, colmap)

    print("[4/8] Analisis distribusi ...")
    distribution = distribution_analysis(df, colmap)

    print("[5/8] Analisis ketidakseimbangan ...")
    imbalance = imbalance_analysis(df, colmap)

    print("[6/8] Analisis temporal + kualitas teks ...")
    temporal = temporal_analysis(df, colmap)
    text_quality = text_quality_analysis(df, colmap)

    print("[7/8] Analisis sumber video + top terms ...")
    video_source = video_source_analysis(df, colmap)
    top_terms = top_terms_analysis(df, colmap)

    all_stats = {
        'basic': basic,
        'distribution': distribution,
        'imbalance': imbalance,
        'temporal': temporal,
        'text_quality': text_quality,
        'video_source': video_source,
        'top_terms': top_terms,
    }

    print("[8/8] Generate laporan ...")
    report = generate_markdown_report(all_stats, colmap)

    report_path = os.path.join(args.outdir, 'audit_report.md')
    with open(report_path, 'w') as f:
        f.write(report)

    json_path = os.path.join(args.outdir, 'audit_stats.json')
    with open(json_path, 'w') as f:
        json.dump(all_stats, f, indent=2, ensure_ascii=False)

    print(f"\nSelesai!")
    print(f"  - Laporan: {report_path}")
    print(f"  - Stats JSON: {json_path}")


if __name__ == '__main__':
    main()
