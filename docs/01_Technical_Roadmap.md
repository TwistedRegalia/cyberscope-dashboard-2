# Technical Roadmap — Data Pipeline E-ICTT v2.1

**Penelitian:** Klasifikasi Otomatis Diskursus Vektor Ancaman Siber pada Media Sosial Indonesia
**Versi:** 1.0
**Status:** Pre-Implementation
**Author:** Ray
**Tanggal:** Mei 2026

---

## 0. Eksekutif Ringkasan

Dokumen ini memetakan **8 fase teknis** dari kondisi data saat ini (17.374 raw dengan masalah selection bias) menuju dataset final yang siap untuk fine-tuning IndoBERT + BiGRU + BiLSTM. Setiap fase punya **deliverable konkret**, **kriteria sukses**, dan **estimasi durasi** untuk membantu Anda time-box pekerjaan.

Pendekatan keseluruhan: **Opsi C (Hybrid Validation)** — data lama dipertahankan sebagai training pool dengan eksplisit limitasi, sementara stratified scraping baru menjadi *held-out test set* yang lebih balanced. Ini menunjukkan kesadaran metodologis sambil tidak membuang investasi sebelumnya.

---

## 1. Peta Fase Pipeline

```
PHASE 0  : Audit Data Existing                  [1-2 hari]
PHASE 1  : Pattern Library Development          [3-5 hari]
PHASE 2  : Stratified Scraping Planning         [2-3 hari]
PHASE 3  : YouTube Data API v3 Implementation   [3-5 hari]
PHASE 4  : Tweet Scraping (Tweet Harvest + Apify backup) [3-5 hari]
PHASE 5  : Post-Scraping Filter & Dedup         [2-3 hari]
PHASE 6  : Preprocessing Pipeline               [3-4 hari]
PHASE 7  : Snorkel Labeling Functions           [5-7 hari]
PHASE 8  : Gold Standard Annotation             [7-10 hari]
═══════════════════════════════════════════════════════════
TOTAL                                            [29-44 hari]
```

Total estimasi: **6-9 minggu** untuk dataset siap modeling. Buffer 20% direkomendasikan untuk thesis schedule.

---

## 2. PHASE 0 — Audit Data Existing

### 2.1 Tujuan

Memahami secara empiris karakteristik 17.374 raw data Anda agar dapat diposisikan sebagai *training pool* dengan limitasi yang jelas, bukan dibuang begitu saja.

### 2.2 Deliverable

- `audit_report.md` berisi:
  - Distribusi temporal (jumlah data per bulan 2023-2026)
  - Distribusi platform (YouTube vs X, dengan persentase)
  - Distribusi panjang teks (median, P25, P75, max)
  - Distribusi keyword/topik dominan (top 30 unigram dan bigram)
  - Estimasi distribusi vektor (via keyword crude scan)
- `audit_notebook.ipynb` reproducible

### 2.3 Kriteria Sukses

- Anda dapat menjawab dengan data: "Mengapa F1 ewallet hanya 0.69 dan malware 0.95?"
- Anda dapat menjelaskan ke penguji distribusi temporal dan sumber data Anda

### 2.4 Risiko & Mitigasi

- **Risiko:** Data terlalu skewed ke satu vektor → mitigasi via stratified scraping di Phase 3-4
- **Risiko:** Banyak duplikasi tidak terdeteksi → mitigasi via Phase 5 dedup

---

## 3. PHASE 1 — Pattern Library Development

### 3.1 Tujuan

Membangun **regex pattern library** yang akan dipakai dua kali dalam pipeline:
1. **Discovery filter** (post-scraping, longgar, high-recall)
2. **Snorkel labeling functions** (pre-weak supervision, ketat, high-precision)

### 3.2 Komponen Pattern per Vektor

Setiap dari 6 vektor E-ICTT v2.1 harus memiliki:

- **Tier 1** — pattern high-precision (confidence 0.85+)
- **Tier 2** — pattern medium-precision (confidence 0.60-0.85)
- **Tier 3** — pattern discovery (confidence 0.40-0.60, butuh kombinasi)
- **Negation guards** — pattern yang menyesuaikan role atau confidence
- **Context amplifiers** — pattern yang boost confidence bila co-occur
- **Speaker role hints** — pattern untuk identifikasi R1-R5 (lihat E-ICTT v2.1 Bagian 2.3)

### 3.3 Deliverable

- `patterns_library.md` — dokumentasi lengkap (lihat dokumen terpisah)
- Penjelasan justifikasi linguistik tiap pattern
- Contoh aplikasi (match dan non-match)
- Roadmap konversi ke Python code di phase berikutnya

### 3.4 Kriteria Sukses

- Setiap vektor punya minimum 8-12 pattern terdokumentasi
- Setiap pattern punya minimal 3 contoh match dan 2 contoh non-match
- Reviewer eksternal bisa memahami justifikasi tanpa konteks tambahan

### 3.5 Risiko & Mitigasi

- **Risiko:** Pattern over-fit ke contoh tertentu → mitigasi via pilot scraping kecil untuk validasi
- **Risiko:** Pattern miss varian linguistik → mitigasi via iterative refinement di Phase 7

---

## 4. PHASE 2 — Stratified Scraping Planning

### 4.1 Tujuan

Menyusun rencana scraping yang **systematic** dan **dapat direplikasi**, dengan target distribusi seimbang per vektor.

### 4.2 Target Distribusi Final Dataset

Mengasumsikan **Opsi C (Hybrid Validation)**:

| Komponen | Sumber | Target Size | Tujuan |
|----------|--------|-------------|--------|
| Training pool (lama) | 17.374 raw → 14.445 preprocessed | ~14.445 | Training utama |
| Test set independen (baru) | Stratified scraping | ~3.000-5.000 | Validasi generalisasi |
| Total dataset final | | ~17.000-19.000 | |

Target per vektor di test set baru:

| Vektor | Target Min | Target Max | Source Mix |
|--------|-----------|-----------|-----------|
| phishing_rekayasa_sosial | 500 | 800 | YT + X |
| penipuan_ewallet_qris | 400 | 700 | YT + X |
| malware_apk | 400 | 700 | YT + X |
| judi_online_pinjol | 500 | 800 | YT + X |
| peretasan_pencurian_identitas | 400 | 700 | YT + X |
| deepfake_penipuan_ai | 300 | 500 | YT + X |
| tidak_relevan | 500 | 800 | YT + X |

### 4.3 Deliverable

- `scraping_plan.md` berisi:
  - Daftar 30-50 video YouTube terpilih (judul, channel, URL, target vektor, estimasi komentar)
  - Daftar query Tweet Harvest per vektor (boolean operator optimized), siap dipakai juga untuk Apify bila triggered
  - Timeline scraping (hari per hari, dengan rate limit consideration)
  - Protokol dokumentasi (apa yang harus dicatat per scraping session)
- `video_candidates.csv` — sheet kandidat video dengan kolom verifikasi

### 4.4 Kriteria Sukses

- Setiap vektor punya minimum 6 video YouTube kandidat dan 5 query X
- Reviewer dapat replikasi scraping dari plan tanpa bertanya
- Plan menghasilkan distribusi yang **ex-ante balanced** (bukan hope-balanced)

### 4.5 Risiko & Mitigasi

- **Risiko:** Video kandidat sudah dihapus saat eksekusi → mitigasi: pilih 50% lebih banyak kandidat
- **Risiko:** Query Tweet Harvest hasil sedikit → mitigasi: longgarkan boolean, switch ke Apify (trigger T2)
- **Risiko:** Kuota YouTube API habis → mitigasi: spread across multiple days, cache results

---

## 5. PHASE 3 — YouTube Data API v3 Implementation

### 5.1 Tujuan

Migrasi dari YTDT ke **YouTube Data API v3 langsung** untuk reproducibility dan kontrol penuh.

### 5.2 Setup Requirement

- Google Cloud Console project dengan YouTube Data API v3 enabled
- API key dengan kuota 10.000 units/hari (default gratis)
- Python environment dengan `google-api-python-client`, `pandas`, `tqdm`
- Storage strategy (CSV per video, atau SQLite database)

### 5.3 Komponen Script

Script modular dengan 4 komponen utama:

1. **Video metadata fetcher** — ambil title, description, channel, publish date, view count, comment count
2. **Comment thread fetcher** — `commentThreads.list` dengan pagination, cost ~1 unit per call
3. **Reply fetcher** (opsional) — `comments.list` untuk reply ke top-level comments
4. **Quota tracker** — log unit usage per session untuk plan ke depan

### 5.4 Deliverable

- `youtube_scraper.py` (modular, testable)
- `youtube_scraping_log.csv` — log per session (video_id, comments_fetched, quota_used, timestamp)
- `raw_youtube_comments/` directory berisi per-video CSV

### 5.5 Kriteria Sukses

- Script dapat scrape 1 video dengan 1.000+ komentar tanpa intervensi manual
- Quota usage terlacak dan dapat diestimasi sebelum next session
- Output format konsisten dan siap untuk Phase 5 (filter + dedup)

### 5.6 Risiko & Mitigasi

- **Risiko:** API kuota habis di tengah scraping → mitigasi: built-in quota tracker dengan graceful stop
- **Risiko:** Comments disabled di video target → mitigasi: error handling, log video skipped
- **Risiko:** Comment terlalu panjang (>5000 char) → mitigasi: truncate dengan flag, atau split

---

## 6. PHASE 4 — Tweet Scraping Implementation (Strategi Jalur C)

### 6.1 Tujuan

Eksekusi scraping tweet X dengan **strategi dua jalur (Jalur C)**: Tweet Harvest sebagai jalur utama (gratis), dan Apify `apidojo/twitter-scraper-lite` sebagai jalur cadangan (berbayar) yang hanya diaktifkan bila jalur utama menemui tembok. Strategi ini meminimalkan risiko finansial sambil mempertahankan jaring pengaman.

### 6.2 Filosofi Strategi Dua Jalur

Pendekatan ini lahir dari trade-off riil:

- **Tweet Harvest** gratis tapi berisiko (rate-limit, kemungkinan ban akun pribadi, reproducibility lebih lemah)
- **Apify** reproducible dan tidak berisiko akun, tapi berbayar dan menarik dari debit card

Jalur C menyelesaikan dilema ini dengan menjadikan Apify sebagai **contingency yang dipicu kondisi spesifik**, bukan default. Anda tidak subscribe Apify sampai benar-benar diperlukan.

### 6.3 Sub-Fase 4A — Primary Path: Tweet Harvest

**Setup Requirement:**

- Node.js (LTS) terinstall
- Tweet Harvest v2.7.1 via `npx tweet-harvest@latest`
- auth_token dari akun X (extract dari cookie browser setelah login)
- **Rekomendasi:** gunakan akun X sekunder/khusus riset, bukan akun utama, untuk mitigasi risiko ban

**Strategi Query:**

Tweet Harvest menerima Twitter advanced search syntax. Setiap vektor punya 3-5 query dengan boolean operators:

```
# Template per vektor:
"<Tier 1 keyword> OR <varian ejaan> (<context amplifier>) -<noise terms> lang:id since:2023-01-01 until:2026-06-01"
```

Contoh untuk phishing:
```
"phishing OR pishing OR phising (OTP OR penipuan OR link OR modus) -lowongan -kerja lang:id"
```

Parameter CLI Tweet Harvest yang relevan:
- `-t` / `--token` — auth_token
- `-s` / `--search-keyword` — query string
- `-l` / `--limit` — batas jumlah tweets
- `-f` / `--from` dan `--to` — date range
- `-e` / `--export-format` — csv atau xlsx (sejak v2.7.0)

**Protokol Eksekusi:**

1. Jalankan per vektor secara berurutan (bukan paralel) untuk hindari trigger rate-limit agresif
2. Beri jeda antar-query (manual delay beberapa menit)
3. Set `--limit` konservatif per run (misal 300-500) untuk hindari sesi panjang yang rawan ban
4. Monitor apakah browser Chromium yang dibuka Tweet Harvest masih berjalan normal atau ter-block

### 6.4 Trigger Conditions — Kapan Switch ke Apify

Aktifkan Sub-Fase 4B (Apify) **hanya jika** salah satu kondisi berikut terjadi:

| Trigger | Deskripsi | Tindakan |
|---------|-----------|----------|
| **T1 — Akun terkena suspend/limit** | Akun X ter-rate-limit berat atau suspended saat scraping | Stop Tweet Harvest, switch ke Apify |
| **T2 — Volume tidak tercapai** | Setelah semua query dijalankan, total tweet relevan < 50% target untuk satu/lebih vektor | Gunakan Apify untuk vektor underrepresented saja |
| **T3 — Data quality rendah** | Output Tweet Harvest banyak corrupt/incomplete (field hilang, encoding error) | Validasi sample, jika sistemik switch ke Apify |
| **T4 — Reproducibility requirement** | Penguji/pembimbing eksplisit minta reproducible scraping pipeline | Gunakan Apify untuk subset yang perlu reproducible |

Selama tidak ada trigger, **tetap di Tweet Harvest** dan lewati Sub-Fase 4B.

### 6.5 Sub-Fase 4B — Contingency Path: Apify (Conditional)

**HANYA dijalankan bila ada trigger di 6.4.**

**Setup Requirement:**

- Akun Apify
- API token Apify (Console → Settings → Integrations)
- Python `apify-client` library
- Actor: `apidojo/twitter-scraper-lite` (ID: `nfp1fpt5gUlBwPcor`)

**PROTEKSI BUDGET WAJIB (sebelum scraping apa pun):**

1. **Set Spending Limit dulu** di Apify Console → Billing → Limits. Set di angka aman (misal $10). Ini mencegah debit card tertarik melebihi batas meski ada bug/query error.
2. **Catat tanggal billing cycle** agar tahu kapan harus cancel.
3. **Set `maxItems` eksplisit** di setiap run (jangan biarkan `Infinity`).

**Catatan Pricing (Free Plan vs Paid):**

- Free plan hanya Demo Mode: maksimum 10 items per run — TIDAK cukup untuk volume riil
- Untuk scraping nyata wajib paid plan (event-based pricing aktif)
- Standard Query $0.016 (termasuk ~40 tweets pertama) + per-item cost berdasarkan tier batch
- Estimasi total untuk 6 vektor ~5.000 tweets: **~$4-5**

**Protokol Cancel yang Aman:**

1. Subscribe paid plan
2. Set spending limit segera
3. Scrape semua dalam 1-2 hari (front-load semua kerja)
4. Verifikasi output lengkap dan tersimpan permanen
5. Cancel di Billing settings — subscription tetap aktif sampai akhir cycle, tidak diperpanjang
6. Monitor invoice final untuk memastikan tidak ada overage tak terduga

### 6.6 Deliverable

Jalur utama (selalu):
- `tweet_harvest_scraping_plan.md` — daftar query final per vektor dengan tanggal eksekusi
- `tweet_harvest_log.csv` — log per run (query, date_range, tweets_fetched, timestamp)
- `raw_tweets_harvest/` directory berisi per-query CSV

Jalur cadangan (bila triggered):
- `apify_scraper.py` — script Python dengan `apify-client`
- `apify_scraping_log.csv` — log per run (query, run_id, items_fetched, cost, timestamp)
- `raw_tweets_apify/` directory
- `trigger_justification.md` — dokumentasi trigger mana yang aktif dan kenapa

### 6.7 Kriteria Sukses

- Setiap vektor menghasilkan minimum 200 tweets relevan setelah filter awal
- Query terdokumentasi dan dapat direplikasi (Tweet Harvest: dokumentasi query + tanggal; Apify: + run ID)
- Jika Apify dipakai: total budget tidak melebihi spending limit yang di-set
- Sumber scraping (Tweet Harvest vs Apify) tercatat per data point untuk transparansi metodologi

### 6.8 Risiko & Mitigasi

- **Risiko:** Akun X kena ban saat Tweet Harvest → mitigasi: pakai akun sekunder, set limit konservatif, switch ke Apify (T1)
- **Risiko:** Volume tidak tercapai → mitigasi: trigger T2, Apify untuk vektor underrepresented
- **Risiko:** Debit card tertarik tak terduga (jika pakai Apify) → mitigasi: WAJIB set spending limit sebelum scraping
- **Risiko:** Lupa cancel Apify → mitigasi: set reminder kalender saat subscribe, cancel segera setelah scraping selesai
- **Risiko:** Inkonsistensi format antara Tweet Harvest dan Apify → mitigasi: normalisasi schema di Phase 5

### 6.9 Dokumentasi Metodologi (untuk Tesis)

Apa pun jalur yang dipakai, tulis di Bab 3 dengan jujur. Template:

> "Pengumpulan data X (Twitter) menggunakan pendekatan dua jalur. Jalur utama menggunakan Tweet Harvest v2.7.1, sebuah tool berbasis browser automation (Playwright). [Jika Apify dipakai:] Untuk vektor dengan volume tidak mencukupi, digunakan Apify Actor apidojo/twitter-scraper-lite sebagai pelengkap, yang menyediakan reproducibility lebih baik melalui Actor ID yang persisten. Setiap data point mencatat sumber scraping-nya untuk transparansi. Keterbatasan Tweet Harvest dalam hal reproducibility (ketergantungan pada session cookie) diakui sebagai limitasi metodologis."

---

## 7. PHASE 5 — Post-Scraping Filter & Dedup

### 7.1 Tujuan

Membersihkan raw scraping output sebelum preprocessing dengan **dua tahap**:

1. **Discovery filter** — buang yang clearly noise (terlalu pendek, link only, emoji only, bot)
2. **Deduplication** — buang duplikat exact dan near-duplicate

### 7.2 Filter Criteria

Buang konten yang memenuhi salah satu:

- Length < 5 karakter (setelah strip whitespace)
- Length > 2.000 karakter (likely spam/copypasta)
- Hanya emoji/punctuation tanpa kata
- Match pattern URL spam (link saja tanpa teks substantif)
- Match pattern bot signature (mention massal, repeating chars)

### 7.3 Deduplication Strategy

Tiga level:

1. **Exact dedup** — hash MD5 dari text normalized
2. **Near-dedup** — Jaccard similarity > 0.85 di shingles 5-gram
3. **Cross-platform dedup** — content yang sama muncul di YT dan X (rare tapi mungkin)

### 7.4 Deliverable

- `post_scrape_filter.py` — script filter + dedup
- `filtered_dataset.csv` — output bersih siap untuk preprocessing
- `filter_stats.md` — laporan: berapa di-filter, alasan apa

### 7.5 Kriteria Sukses

- Reduction rate documented (misal 17.374 → 14.445 = 16.9% filtered, sesuai metodologi Anda)
- Tidak ada exact duplicate di output
- Sample manual 100 entries menunjukkan kualitas content lulus filter

### 7.6 Risiko & Mitigasi

- **Risiko:** Filter terlalu agresif buang konten valid → mitigasi: tuning conservative, sample manual check
- **Risiko:** Near-dedup miss varian penting → mitigasi: threshold sensitivity test

---

## 8. PHASE 6 — Preprocessing Pipeline

### 8.1 Tujuan

Transformasi text bersih menjadi format yang siap untuk tokenisasi IndoBERT.

### 8.2 Komponen Preprocessing

Berdasarkan metodologi Anda yang sudah ada (Sastrawi + slang normalization):

1. **Case folding** — lowercase semua
2. **URL/mention/hashtag handling**:
   - URL → token `[URL]` (atau kosong, tergantung kebijakan)
   - Mention `@user` → token `[USER]`
   - Hashtag `#judol` → ekstrak content `judol`
3. **Emoji handling**:
   - Emoji informatif (😢, 😡, 💸) → tag emosi
   - Emoji decorative → strip
4. **Slang normalization**:
   - Kamus slang Indonesia (gw → saya, gak → tidak, dll)
   - Custom kamus cybercrime slang (gacor, rungkad, etc) — tetap dipertahankan karena bermakna
5. **Stemming Sastrawi** — opsional, untuk fitur tambahan (bukan menggantikan)
6. **Stopword handling** — JANGAN buang stopword untuk BERT, hanya untuk Tier-2 features

### 8.3 Deliverable

- `preprocessing.py` — modular pipeline
- `preprocessed_dataset.csv` — output dengan kolom: `id`, `text_original`, `text_clean`, `text_normalized`, `platform`, `timestamp`
- `slang_dictionary.csv` — kamus slang yang dipakai (untuk reproducibility)

### 8.4 Kriteria Sukses

- Sample 100 entries manual check menunjukkan transformasi sesuai ekspektasi
- Tidak ada information loss yang merugikan (misal slang cybercrime tidak di-strip)
- Format konsisten untuk Phase 7 (Snorkel)

### 8.5 Risiko & Mitigasi

- **Risiko:** Over-aggressive cleaning hilangkan signal → mitigasi: keep original text, transformasi di kolom terpisah
- **Risiko:** Slang dictionary tidak comprehensive → mitigasi: iterative expansion based on Phase 0 audit

---

## 9. PHASE 7 — Snorkel Labeling Functions

### 9.1 Tujuan

Konversi pattern library (Phase 1) menjadi **labeling functions (LFs)** Snorkel untuk weak supervision.

### 9.2 Struktur LFs

Setiap pattern Tier 1/2/3 menjadi LF:

```python
@labeling_function()
def lf_phishing_otp_modus(x):
    if re.search(r"(minta|kasih|kirim).{0,20}(OTP|kode\W{0,5}verif)", 
                  x.text, re.IGNORECASE):
        return PHISHING
    return ABSTAIN
```

Target jumlah LFs per vektor: **5-10 LFs** (mencakup Tier 1-3 + negation guards + amplifiers).

Total LFs untuk 6 vektor + tidak_relevan: **40-70 LFs**.

### 9.3 Snorkel Workflow

1. Apply LFs ke training pool (Phase 6 output)
2. Train `LabelModel` untuk aggregate LFs ke probabilistic label
3. Threshold confidence ≥ 0.4 (sesuai metodologi Anda)
4. Output: weak-labeled dataset

### 9.4 Deliverable

- `labeling_functions.py` — semua LFs terorganisir per vektor
- `lf_analysis.ipynb` — analisis coverage, conflict, overlap antar LFs
- `weak_labeled_dataset.csv` — output Snorkel dengan probabilistic labels

### 9.5 Kriteria Sukses

- Coverage > 60% (minimal 60% dataset ter-label oleh ≥1 LF)
- Conflict rate < 30%
- Sample manual check 100 entries menunjukkan label quality reasonable

### 9.6 Risiko & Mitigasi

- **Risiko:** Coverage rendah karena pattern terlalu strict → mitigasi: relax Tier 3 patterns
- **Risiko:** Conflict tinggi antar LFs → mitigasi: refine boundary rules, tambah negation guards

---

## 10. PHASE 8 — Gold Standard Annotation

### 10.1 Tujuan

Anotasi manual oleh 2+ anotator sesuai protokol di E-ICTT v2.1 Bagian 7 untuk gold standard validation.

### 10.2 Proses

1. Sampling 357 entries dari weak-labeled dataset (Phase 7)
2. Anotasi independen 2 anotator dengan guidelines E-ICTT v2.1
3. Hitung Cohen's Kappa
4. Spot-check 50 entries oleh reviewer ketiga
5. Rekonsiliasi disagreement
6. Final gold standard 357 entries siap untuk evaluation

### 10.3 Deliverable

- `gold_standard.csv` — 357 entries dengan label final + speaker role
- `iaa_report.md` — laporan Cohen's Kappa per label dan overall
- `annotation_log.md` — kasus sulit dan resolusinya untuk dokumentasi tesis

### 10.4 Kriteria Sukses

- Cohen's Kappa overall ≥ 0.80
- Cohen's Kappa per label ≥ 0.70 (target minimum)
- Spot-check reviewer ketiga menyetujui ≥ 90% keputusan

### 10.5 Risiko & Mitigasi

- **Risiko:** Anotator dropout/inkonsisten → mitigasi: pilot 30 entries dulu untuk training
- **Risiko:** Kappa rendah → mitigasi: revisi guidelines (v2.2), anotasi ulang
- **Risiko:** Imbalance per label tinggi → mitigasi: stratified sampling dari weak labels

---

## 11. Critical Path dan Dependensi

```
Phase 0 (Audit)
    ↓
Phase 1 (Pattern Library) ──→ Phase 7 (Snorkel LFs)
    ↓                              ↑
Phase 2 (Scraping Plan)            │
    ↓                              │
Phase 3 (YouTube) ─┐               │
                   ├──→ Phase 5 ──→ Phase 6 ──┘
Phase 4 (Tweet) ───┘   (Filter)   (Preprocess)
                                       ↓
                                   Phase 8 (Gold)
                                       ↓
                                   MODELING (Phase berikutnya)
```

**Bottleneck:** Phase 1 (Pattern Library) — quality di sini menentukan quality di Phase 5, 7, dan 8. Investasi waktu ekstra di sini akan terbayar di phase berikutnya.

**Critical path:** Phase 0 → 1 → 2 → 3 → 5 → 6 → 7 → 8. Phase 4 (Tweet scraping) dapat paralel dengan Phase 3 (YouTube).

---

## 12. Reproducibility Checklist

Untuk thesis-grade reproducibility, setiap phase harus menghasilkan:

- [ ] Script Python yang **deterministic** (set random seed)
- [ ] Configuration file (YAML/JSON) yang **terpisah dari code**
- [ ] Log file dengan timestamp, parameters, dan output stats
- [ ] README per phase dengan cara menjalankan
- [ ] Sample data (10-50 entries) untuk testing tanpa full data

Dokumentasi ini menjadi **Appendix B** di thesis Anda dan **kunci untuk replikasi** oleh penelitian lanjutan.

---

## 13. Tooling Stack Final

| Komponen | Tool | Justifikasi |
|----------|------|-------------|
| Language | Python 3.10+ | Standar NLP ecosystem |
| Notebook | Jupyter | Eksplorasi data + reproducibility |
| YouTube scraping | `google-api-python-client` | Direct API, defensible |
| Tweet scraping (utama) | Tweet Harvest v2.7.1 | Gratis, continuity dengan kerja sebelumnya |
| Tweet scraping (cadangan) | Apify apidojo/twitter-scraper-lite | Reproducible, no ban risk, dipakai bila triggered |
| Tweet scraping (lama) | Tweet Harvest v2.7.1 | Data existing, training pool |
| Data manipulation | `pandas`, `numpy` | Standar |
| Text processing | `re`, `sastrawi`, `nltk` | Sesuai metodologi |
| Weak supervision | `snorkel` | Sesuai metodologi |
| Annotation | Spreadsheet (Excel/Sheets) + format CSV | Sederhana, accessible |
| Version control | Git + GitHub | Mandatory untuk thesis |
| Storage | CSV + SQLite untuk index | Cukup untuk skala thesis |

---

## 14. Penutup

Roadmap ini bersifat **iteratif** — Anda akan kembali ke phase sebelumnya bila menemukan masalah di phase berikutnya. Misal, bila Phase 7 (Snorkel) menunjukkan coverage rendah, Anda mungkin perlu kembali ke Phase 1 (Pattern Library) untuk refine pattern.

Setiap deliverable di roadmap ini menjadi **artifact thesis** yang Anda lampirkan sebagai Appendix. Approach "documentation-first" yang Anda pilih akan terbayar saat sidang — Anda akan dapat menunjukkan bahwa **setiap keputusan teknis** sudah dipikirkan dan dijustifikasi sebelum dieksekusi.

---

*Akhir dokumen roadmap. Versi berikutnya akan dirilis setelah Phase 0 (Audit) selesai dengan insight dari data Anda.*
