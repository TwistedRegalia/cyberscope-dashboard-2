# Phase 3 & 4 Execution Checkpoint Guide

Panduan step-by-step untuk eksekusi Phase 3 (YouTube API) dan Phase 4 (Tweet Harvest) dengan monitoring per-vektor.

---

## Pre-Execution Checklist

- [ ] `data/video_candidates.csv` filled with 5-6 videos per vektor (run `docs/04_Phase3_Video_Selection_Guide.md` protocol)
- [ ] YouTube API key obtained from Google Cloud Console
- [ ] Node.js v18+ installed (test: `node --version`)
- [ ] Secondary X account prepared (for Tweet Harvest, mitigasi suspend/ban)
- [ ] `data/query_spec.json` ready (auto-generated, no edit needed)

---

## PHASE 3: YouTube API Comment Scraping

### Setup

```powershell
# 1. Get API key from Google Cloud Console
# 2. Set env var (Windows PowerShell):
$env:YOUTUBE_API_KEY = "AIzaSy..."  # paste your key

# Verify:
echo $env:YOUTUBE_API_KEY  # should show key, not empty
```

### Execute

```powershell
# Run Phase 3 scraper (processes all videos in video_candidates.csv)
python src/phase3_youtube_scrape.py
```

**What it does:**
- Reads each video_id from `data/video_candidates.csv`
- Calls YouTube API to fetch all comments (top-level + replies)
- Saves to `raw_additional_youtube/{vektor}/{video_id}.csv`
- **Duration:** ~2-3 min per video (depends on comment count), 20 videos = ~40-60 min total

**Monitor output:**
```
[Phase 3] Scraping 22 videos from data/video_candidates.csv
[penipuan_ewallet_qris] Scraping dQw4w9WgXcQ (QRIS Palsu di...)...
  → Scraped 456 comments from dQw4w9WgXcQ
  ✓ Saved 456 comments to raw_additional_youtube/penipuan_ewallet_qris/dQw4w9WgXcQ.csv
...
[Phase 3 Summary]
  Total videos: 22
  Successful: 20
  Failed: 2
  Total comments scraped: 8,942
```

**Expected output structure:**
```
raw_additional_youtube/
├── penipuan_ewallet_qris/
│   ├── dQw4w9WgXcQ.csv
│   ├── aAbBcCdDeE.csv
│   └── ...
├── malware_apk/
│   ├── xXyYzZaaBb.csv
│   └── ...
└── ...
```

### Troubleshooting Phase 3

**"YOUTUBE_API_KEY not set"**
- Env var lupa. Set: `$env:YOUTUBE_API_KEY = "key"`

**"Video not found (404)"**
- Video dihapus atau private. Catatan di output; skip saja.

**"Comments are disabled (403)"**
- Video ada tapi komentar disabled. Output akan catat; skip.

**"Quota exceeded (429)"**
- YouTube API quota habis untuk hari ini. Tunggu 24 jam atau naikkan quota di Google Cloud Console.

---

## PHASE 4: Tweet Harvest Per-Vector Execution

**Strategy:** Jalankan **satu vektor per kali**, bukan seluruh query_spec sekaligus. Ini allows:
- Monitor account health antar-vektor (jika ada 429, langsung tau mana vektor)
- Rate-limit mitigation: cooldown antar-vektor manual
- Lebih transparan (user tahu progress per-step)

### Setup

```powershell
# 1. Login ke akun X sekunder di browser
# 2. Buka DevTools (F12) → Application → Cookies → https://x.com
# 3. Cari cookie bernama "auth_token", copy VALUE-nya (panjang, mirip "calon...")
# 4. Set env var:
$env:TWITTER_AUTH_TOKEN = "paste-value-disini"

# Verify:
echo $env:TWITTER_AUTH_TOKEN  # should show token, not empty
npx --version                 # should show "x.y.z"
```

### Execute Per Vector

> Bentuk posisional di bawah (`..._single_vector.py <vektor>`) adalah wrapper tipis;
> ekuivalen dengan `python src/phase4_tweet_harvest.py --vektor <vektor>`. Tambah
> `<query_idx>` (atau `--query <idx>`) untuk uji 1 query dulu sebelum membakar kuota akun.
> Cek daftar vektor: `python src/phase4_tweet_harvest.py --list`.

**Order (recommended based on platform viability):**

1. **`penipuan_ewallet_qris`** — X-driven (9.2% retention, YouTube dead)
   ```powershell
   python src/phase4_tweet_harvest_single_vector.py penipuan_ewallet_qris
   ```

2. **`malware_apk`** — balanced (2% X, 2% YouTube)
   ```powershell
   # Wait 5-10 minutes after ewallet (cooldown)
   python src/phase4_tweet_harvest_single_vector.py malware_apk
   ```

3. **`deepfake_penipuan_ai`** — balanced (3.8% X, 2.7% YouTube)
   ```powershell
   # Wait 5-10 minutes after malware
   python src/phase4_tweet_harvest_single_vector.py deepfake_penipuan_ai
   ```

4. **`peretasan_pencurian_identitas`** — reference (optional, lower priority)
   ```powershell
   # Wait 5-10 minutes after deepfake
   python src/phase4_tweet_harvest_single_vector.py peretasan_pencurian_identitas
   ```

### Monitor Output Per Vector

**Example output (penipuan_ewallet_qris, 6 queries):**
```
============================================================
[Phase 4] Running 6 queries for: penipuan_ewallet_qris
  limit=500, tab=LATEST, delay=3s
  Output: raw_additional_tweets/penipuan_ewallet_qris/
============================================================

[penipuan_ewallet_qris:q1] Scraping: "qris palsu" OR "qris bodong" lang:id
  Command: npx --yes tweet-harvest@latest --search-keyword ...
  ✓ 248 tweets → raw_additional_tweets/penipuan_ewallet_qris/q1.csv

[penipuan_ewallet_qris:q2] Scraping: (saldo) (ovo OR dana) ...
  ✓ 312 tweets → raw_additional_tweets/penipuan_ewallet_qris/q2.csv

...

============================================================
[penipuan_ewallet_qris Summary]
  Queries executed: 6
  Total tweets: 1,847
  Empty queries: 0
  Failed queries: 0
  Output: raw_additional_tweets/penipuan_ewallet_qris/
============================================================
```

**Expected output structure:**
```
raw_additional_tweets/
├── penipuan_ewallet_qris/
│   ├── q1.csv  (248 tweets)
│   ├── q2.csv  (312 tweets)
│   ├── q3.csv  (156 tweets)
│   ├── q4.csv  (420 tweets)
│   ├── q5.csv  (385 tweets)
│   ├── q6.csv  (226 tweets)
│   └── _summary.json  (metadata)
├── malware_apk/
│   ├── q1.csv
│   └── ...
└── ...
```

### Troubleshooting Phase 4

**"TWITTER_AUTH_TOKEN not set"**
- Env var lupa. Set: `$env:TWITTER_AUTH_TOKEN = "xxxx"`

**"429 Too Many Requests"**
- Rate-limit hit. Script otomatis throttle 2s antar-query. Jika masih dapat:
  - Tunggu 15-30 menit
  - Coba run ulang dari vektor yang sama (resume dengan next query_idx)
  - Atau switch ke akun X lain

**"0 tweets (no results for query X)"**
- Query terlalu spesifik atau match sangat sedikit. Normal — catat di log.

**"No tweets for this vector" (semua 6 query kosong)**
- Akun mungkin suspended atau shadow-banned. Try akun baru.

**"npx not found"**
- Node.js belum install. Download: https://nodejs.org (LTS)

---

## Post-Execution: Merge & Consolidate

Setelah PHASE 3 dan PHASE 4 selesai, merge data baru dengan existing dataset:

### 1. Verify outputs exist

```bash
# Cek Phase 3 output
ls -lh raw_additional_youtube/*/  # should show .csv files per video_id

# Cek Phase 4 output
ls -lh raw_additional_tweets/*/   # should show q1.csv, q2.csv, ... per vektor
```

### 2. Count raw tweets/comments

```bash
# YouTube comments
find raw_additional_youtube -name "*.csv" -exec wc -l {} + | tail -1
# Example: ~9,000 comments total

# X tweets
find raw_additional_tweets -name "*.csv" -exec wc -l {} + | tail -1
# Example: ~8,000 tweets total (minus 4 header rows = ~7,984 tweets)
```

### 3. Run Phase 5 Merge Script

**Script:** `src/phase5_consolidate_additional.py` ✅ **sudah dibuat** — mengimpor
`apply_filters`/`add_diagnostic_hints` dari `phase5_consolidate.py` agar logika filter IDENTIK Phase 5.

```powershell
python src/phase5_consolidate_additional.py
# opsi: --existing data/unified_dataset.csv --out data/unified_dataset_v2.csv
```

Apa yang dilakukan:
1. Baca YouTube CSV (skema baru Phase 3) + X CSV (skema native Tweet Harvest) → skema unified
2. Filter SAMA dengan Phase 5: `lang=='in'` (X), reply quality (≥5 kata + anchor + bukan
   pure afirmasi), low-signal, dedup exact (via `apply_filters` yang diimpor)
3. **Cross-dedup**: buang baris baru yang teks (normalized) sudah ada di `unified_dataset.csv`
4. `vector_hint` dihitung ulang (diagnostik kasar) + `unified_id` melanjutkan urutan lama
5. Tulis `data/unified_dataset_v2.csv`

**Output:**
- `data/unified_dataset_v2.csv` (48.496 + baris baru unik)
- `docs/phase5_merge_report.md` — baris baru per vektor + cross-batch dedup + vector_hint baru
- `data/phase5_merge_stats.json` — statistik mentah

### 4. Run Phase 6-7 on Enlarged Dataset

```bash
# Phase 6 recompute (text preprocessing)
python src/phase6_preprocess.py --input unified_dataset_v2.csv --output preprocessed_dataset_v2.csv

# Phase 7 recompute (Snorkel labeling)
python src/phase7_pipeline.py --input preprocessed_dataset_v2.csv --output weak_labeled_dataset_v2.csv
```

### 5. Check Weak Vector Distribution Post-Merge

Expected improvement:
```
BEFORE (current weak_labeled_dataset.csv):
  ewallet: 23 relevan
  malware: 36 relevan
  deepfake: 62 relevan
  peretasan: 46 relevan

AFTER (weak_labeled_dataset_v2.csv, estimated):
  ewallet: 400-450 relevan (+360-430)
  malware: 400-450 relevan (+360-410)
  deepfake: 270-310 relevan (+200-250)
  peretasan: 200-250 relevan (+150-200)
```

If not achieved, comment in CONTEXT.md why + next steps.

---

## Checklist Execution

- [ ] Phase 3 completed (YouTube: ~9,000 comments)
- [ ] Phase 4 completed (X: ~8,000 tweets)
- [ ] `raw_additional_youtube/` verified with ≥5-6 video per vektor
- [ ] `raw_additional_tweets/` verified with ≥6 CSV files per vektor
- [ ] Phase 5 merge script executed → `unified_dataset_v2.csv` generated
- [ ] Merge report shows weak vectors improved ≥350/vektor
- [ ] Phase 6-7 recomputed on v2 dataset
- [ ] `weak_labeled_dataset_v2.csv` verifikasi distribusi vektor

---

*Checkpoint: 20 Jun 2026*
