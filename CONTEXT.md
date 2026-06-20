# CONTEXT.md — Handoff untuk Claude Code

> **Cara pakai dokumen ini:** Letakkan file ini di root project Anda. Saat membuka Claude Code, mulai dengan: *"Baca CONTEXT.md untuk memahami project ini, lalu bantu saya lanjut ke Phase 6."* Claude Code akan punya konteks penuh tanpa Anda perlu menjelaskan ulang.

---

## 1. Identitas Penelitian

**Judul:** Klasifikasi Otomatis Diskursus Vektor Ancaman Siber pada Media Sosial Indonesia Menggunakan Pendekatan Hybrid Machine Learning Berbasis OSINT dan Explainable AI

**Peneliti:** Ray (skripsi S1)

**Arsitektur model target:** Triple-Hybrid IndoBERT + BiGRU + BiLSTM + Rule-based Regex, late fusion 0.75:0.25, XAI via SHAP/LIME.

**Environment:** Python, Kaggle T4 GPU untuk training. Bahasa kerja: Indonesia.

---

## 2. REFRAMING PENTING (Prinsip Fundamental)

Penelitian ini **TIDAK** mendeteksi serangan siber yang sedang berlangsung. Penelitian ini **mengklasifikasikan diskursus publik tentang vektor ancaman siber** — yaitu konten media sosial yang berbentuk:

1. Laporan pengalaman korban (R1)
2. Kesaksian kasus orang lain (R2)
3. Peringatan/edukasi (R3)
4. Promosi/tindakan pelaku (R4)
5. Diskusi netral/jurnalistik (R5)

Setiap label vektor mencakup **seluruh spektrum diskursif** ini, bukan hanya tindakan serangan. Prinsip ini memandu semua keputusan labeling.

---

## 3. Taksonomi E-ICTT v2.1 (6 Label)

Dikembangkan dari Arifman et al. (2026) yang punya 5 label; penelitian ini menambah `deepfake_penipuan_ai` sebagai vektor emerging.

1. `phishing_rekayasa_sosial`
2. `penipuan_ewallet_qris`
3. `malware_apk`
4. `judi_online_pinjol`
5. `peretasan_pencurian_identitas`
6. `deepfake_penipuan_ai`

**CATATAN:** Label ke-7 `informasi_edukasi_siber` (pernah diusulkan di v2.0) sudah **DITOLAK** karena menciptakan double-coverage dengan 6 label vektor. Jangan tambahkan kembali.

Pipeline klasifikasi **2 lapis**:
- **Layer 1:** relevance filter (relevan / tidak_relevan) — kriteria "anchor" ke vektor spesifik
- **Layer 2:** vector classification (6 label) — hanya untuk yang lolos Layer 1

Metadata tambahan: `speaker_role` (R1-R5) sebagai dimensi terpisah, bukan label utama.

---

## 4. Status Pipeline (Technical Roadmap 8 Fase)

| Phase | Nama | Status |
|-------|------|--------|
| 0 | Audit data | ✅ SELESAI |
| 1 | Pattern Library | ✅ Terdokumentasi (perlu refinement di Snorkel) |
| 2 | Scraping Plan tambahan | ✅ SIAP (eksekusi conditional pada hasil Snorkel) |
| 3 | YouTube Data API v3 | ⏳ Belum (hanya untuk scraping tambahan jika diperlukan) |
| 4 | Tweet scraping (Jalur C) | ⏳ Belum (hanya untuk scraping tambahan) |
| 5 | Filter & Dedup | ✅ SELESAI — output `unified_dataset.csv` (48.496 baris) |
| 6 | Preprocessing | ✅ SELESAI — output `preprocessed_dataset.csv` (48.496 baris, 18 kolom) |
| 7 | Snorkel Labeling Functions | ✅ SELESAI — pipeline penuh terakit, `weak_labeled_dataset.csv` (lihat `docs/phase7_snorkel_report.md`) |
| 3 (scraping) | YouTube API v3 Scraper | ✅ SIAP — script: `src/phase3_youtube_scrape.py`, input: `data/video_candidates.csv` |
| 4 (scraping) | Tweet Harvest Query Runner | ✅ SIAP — script: `src/phase4_tweet_harvest.py`, input: `data/query_spec.json` |
| 7.1 | Scraping 4 vektor lemah (paralel) | ⏳ READY FOR USER EXECUTION — ewallet/malware/deepfake/peretasan < 1.000 → run scripts + merge |
| 8 | Gold Standard Annotation | 🔜 **BERIKUTNYA** — sampling 357 dari weak_labeled_dataset.csv (post-merge) |

---

## 5. KEPUTUSAN METODOLOGIS YANG SUDAH FINAL

Jangan ubah keputusan ini tanpa alasan kuat — semuanya hasil diskusi panjang:

1. **Sumber data:** Bangun ulang dari raw mentah (70.241 baris, 59 file CSV). `master_dataset.csv` lama (17.374) DIPENSIUNKAN, hanya untuk pembanding hasil.

2. **Bahasa X:** Hanya `lang=in`. Non-Indonesia dibuang.

3. **Reply YouTube:** Include dengan quality filter (Opsi 1) — min 5 kata + ada anchor vektor + bukan pure afirmasi.

4. **Scraping tambahan:** Direncanakan untuk 3 vektor lemah (malware_apk, penipuan_ewallet_qris, deepfake_penipuan_ai), via YouTube + X. EKSEKUSI DITUNDA sampai distribusi pasca-Snorkel diketahui. Threshold: vektor dengan < 1.000 sampel relevan setelah Snorkel.

5. **Tweet scraping tool:** Jalur C — Tweet Harvest v2.7.1 sebagai primary (gratis), Apify `apidojo/twitter-scraper-lite` sebagai backup (hanya jika ada trigger: akun banned, volume kurang, dll). Apify perlu paid plan + WAJIB set spending limit dulu.

6. **Balance:** Kejar balance VEKTOR, bukan balance platform. Rasio 85:15 YouTube:X tidak masalah.

---

## 6. TEMUAN PENTING dari Audit & Phase 5

Catat untuk Bab 3 & Bab 4 tesis:

1. **Timestamp X = snapshot 7 hari (13-20 Mei 2026), BUKAN rentang 2023-2026.** Tweet Harvest mengabaikan filter `since:until:`. Timestamp `created_at` AKURAT (terverifikasi via Twitter Snowflake ID). Jangan klaim rentang multi-tahun untuk X. Posisikan sebagai cross-sectional OSINT snapshot.

2. **YouTube timestamp VALID** (2022-2026, dari `publishedAt`). Karakteristik temporal kedua platform BERBEDA, jelaskan terpisah.

3. **Selection bias YouTube:** Hanya 18 video sumber. Top 5 video = 50% data. Inilah alasan utama stratified scraping tambahan untuk vektor lemah.

4. **Vector hint NO_HINT 77.4% → 70.2% setelah anchor v1.1 (14 Jun 2026).** Refinement `src/anchor_patterns.py` (morfologi suffix + narasi korban implisit + eufemisme/slang) menurunkan NO_HINT dari 77.4% ke 70.2%, dengan 3.509 baris newly-hinted (presisi ~80%) dan 0 lost. Recompute bersifat **row-stable** (`src/refresh_vector_hint.py` — hanya kolom `vector_hint` berubah, kolom lain byte-identik). Tidak dipaksa ke target 45-55% karena terverifikasi via sampel bahwa sisa NO_HINT mayoritas **genuine off-topic** (komentar fan YouTube pada 18 video, mis. "BRI di hati", "mantap bang"). Vector hint tetap **diagnostik kasar** — keputusan relevansi + label = tugas Snorkel (Phase 7). Laporan: `data/vector_hint_refresh_report.md`.
   - ⚠️ **Diawasi di Phase 7:** `phishing_rekayasa_sosial` hint melonjak 3.7% → 10.4% karena pattern narasi scam generik ("kena tipu/ditipu/modus/korban penipuan"). Ini bucket "scam umbrella" yang menyerap narasi korban tak-spesifik. **Pastikan LF phishing di Snorkel TIDAK menjadi keranjang semua penipuan** — gunakan amplifier kredensial/OTP/institusi (Pattern Library 1.6) untuk membatasi, dan biarkan hierarki prioritas E-ICTT 5.2 + LF vektor spesifik mengoreksi mis-attribution.

5. **Bug morfologi pattern — SUDAH DIPERBAIKI di `anchor_patterns.py` v1.1.** `\bpinjol\b` dulu melewatkan "pinjolnya/pinjolku"; sekarang bare anchor menerima suffix klitik ID via konstanta `SUF` (-nya/-ku/-mu/-lah/-kah/-in/-an). Saat porting ke Snorkel LF (Phase 7), bawa handling suffix yang sama.

6. **QC Phase 7 + refine dead LF (14 Jun 2026).** Reproducibility pipeline terverifikasi (re-run = output zip IDENTIK). LFAnalysis: conflict vektor 1,6% (« target <30%), Layer-1 konflik relevan-vs-tidak_relevan 0,00%. Dari **11 dead LF** (coverage 0), 8 di kelas lemah diprobe:
   - **3 bug pola (terlalu ketat):** 2 diperbaiki = deepfake `ai_content_scam` (drop tail "konten/gambar") + `tokoh_publik` (drop prefix "video/klip"), anchor tetap wajib → **deepfake relevan 58 → 62**, dead LF 11 → 9. 1 dilewati = ewallet `saldo_platform` (recovery +3 marginal, ada borderline gagal-topup) → diselesaikan via scraping.
   - **5 scarcity asli (recovery 0):** `ewallet_scan_balik`, `ewallet_qr_lokasi_publik`, `ewallet_promo_palsu`, `malware_bank_drained`, `deepfake_suara_keluarga` → **konfirmasi target scraping terarah** (modus ini memang tidak ada di data 18-video + X snapshot).
   - ⚠️ **Koreksi:** klaim awal "39 ewallet / 62 deepfake intent = bug fixable" adalah **overcount** — itu co-occurrence token, bukan adjacency anchor. Probe yang menjaga anchor menunjukkan recovery sebenarnya kecil (deepfake +4 presisi 4/4). Pengungkit utama kelas lemah = **scraping**, bukan refine LF. Laporan: `docs/phase7_qc_report.md` (script: `src/phase7_qc.py`).

---

## 7. SKEMA unified_dataset.csv (Output Phase 5)

| Kolom | Deskripsi |
|-------|-----------|
| `unified_id` | ID unik (UID000000, dst) |
| `platform` | X / YouTube |
| `source_category` | Vektor asal scraping (BUKAN label final) |
| `source_file` | Nama file CSV asal |
| `text` | Teks asli komentar/tweet |
| `orig_id` | ID asli (tweet ID / comment ID) |
| `published_at` | Timestamp posting |
| `published_at_verified` | Timestamp terverifikasi (Snowflake untuk X) |
| `is_reply` | 1 jika reply, 0 jika top-level/tweet |
| `author` | Username/author |
| `like_count`, `reply_count` | Engagement metrics |
| `lang` | Bahasa |
| `video_id` | ID video (YouTube only) |
| `vector_hint` | Diagnostik kasar (BUKAN label final) |

**Distribusi:** 46.771 YouTube + 1.725 X = 48.496 total. 46.599 top-level + 1.897 reply.

---

## 8. PHASE 6 — PREPROCESSING (✅ SELESAI, 14 Jun 2026)

Tujuan: transformasi teks bersih → siap tokenisasi IndoBERT. Script: `src/phase6_preprocess.py`.

Komponen yang dibangun (detail di `01_Technical_Roadmap.md` Bagian 8):

1. **Case folding** — lowercase
2. **URL/mention/hashtag handling** — URL→[URL], @user→[USER], #judol→ekstrak "judol"
3. **Emoji handling** — emoji emosi (😢😡💸)→tag `[EMOSI_SEDIH/MARAH/UANG/TAKUT/WASPADA]`, decorative→strip
4. **Slang normalization** — kamus slang Indonesia (gw→saya, gak→tidak; 88 entri di `data/slang_dictionary.csv`) + PERTAHANKAN slang cybercrime (gacor, rungkad, maxwin, pinjol — bermakna). Filler (sih/deh/wkwk) TIDAK dibuang (itu pembuangan konteks).
5. **Stemming Sastrawi** — kolom terpisah `text_stemmed` (opsional)
6. **Stopword** — TIDAK dibuang (BERT butuh konteks penuh)

**Output Phase 6:** `data/preprocessed_dataset.csv` (48.496 baris, 18 kolom). Kolom BARU disisipkan setelah `text`:
- `text_clean` — input utama IndoBERT (konteks penuh, tanpa buang stopword/stemming)
- `text_normalized` — `text_clean` + slang→baku (cyber slang dipertahankan)
- `text_stemmed` — Sastrawi, kolom terpisah

**PENTING:** Kolom `text` (= "text_original" pada roadmap) dipertahankan apa adanya; semua 15 kolom existing byte-identik. Transformasi di kolom terpisah → tidak ada information loss.

**⚠️ Catatan `text_stemmed`:** Stemming Sastrawi punya **limitasi diketahui** (over-stemming yang kadang mengubah makna, mis. `sebelumnya`→`belum`). Karena itu `text_stemmed` **TIDAK dipakai sebagai input IndoBERT** — hanya disediakan sebagai opsi fitur **Tier-2 / baseline TF-IDF**. Pipeline BERT memakai `text_clean` (atau `text_normalized`) yang tidak distem.

**Temuan QC pasca-run (text_clean, setelah strip tag):**
- Baris yang menjadi degenerate KARENA preprocessing (orig ≥5 kata → <3 kata bermakna): **hanya 3** (emoji/timestamp junk). Tag-only (cuma `[URL]`/`[EMOSI]`): **30** (0.06%).
- `<3 kata bermakna` total 2.091 (4.31%) — tapi 2.088 di antaranya MEMANG komentar pendek dari asalnya ("kasihan bgt", "sudah nonton"), BUKAN artefak preprocessing.
- Kesimpulan: jauh di bawah ambang diskusi (>500) untuk degradasi preprocessing → tidak perlu filter tambahan. Komentar pendek genuine = urusan relevansi Snorkel (Phase 7), bukan Phase 6.

---

## 9. PHASE 7 — SNORKEL (Setelah Preprocessing)

Konversi Pattern Library (lihat `02_Pattern_Library.md`) menjadi labeling functions:
- Setiap pattern Tier 1/2/3 → satu LF
- Target 40-70 LFs untuk 6 vektor + relevance filter
- LabelModel aggregate → probabilistic label, threshold confidence ≥ 0.4
- Target coverage > 60%, conflict < 30%

Perbaikan yang harus dilakukan di sini:
- Handle morfologi Indonesia (suffix -nya, -ku, -mu)
- Tambah pattern untuk bahasa naratif/implisit (banyak di NO_HINT)
- Implementasi Layer 1 relevance filter yang proper

---

## 9a. PHASE 3 — YouTube Data API v3 Scraper

**Script:** `src/phase3_youtube_scrape.py`

**Input Requirements:**
- `YOUTUBE_API_KEY` env var (obtain from Google Cloud Console)
- `data/video_candidates.csv` — user-filled spreadsheet dengan kolom:
  - `vektor` (penipuan_ewallet_qris, malware_apk, deepfake_penipuan_ai, peretasan_pencurian_identitas)
  - `video_id` (dari URL youtube.com/watch?v=**VIDEO_ID**)
  - `video_title`, `channel_name`, `channel_type` (berita/edukasi/storytelling)
  - `publish_date`, `comment_count`, `verified_topic` (Ya/Tidak), `notes`

**Protocol untuk mengisi video_candidates.csv** (lihat `docs/03_Phase2_Scraping_Plan.md` Bagian 2):
1. Gunakan search query per vektor (Bagian 2.3)
2. Filter dengan kriteria inklusi (Bagian 2.1): topik eksplisit, min 300 komentar, komentar aktif (tidak disabled), publikasi 2022-2026, berbahasa Indonesia
3. Hindari kriteria eksklusi (Bagian 2.2): jangan pilih 18 video existing (lihat Lampiran A), hindari spam, topik campur, engagement palsu
4. Target 5-6 video unik per vektor lemah dari ≥3 tipe channel berbeda
5. Catat untuk setiap video: judul, nama channel, tipe channel, tanggal publikasi, estimasi komentar

**Eksekusi:**
```bash
export YOUTUBE_API_KEY="your-api-key-here"
python src/phase3_youtube_scrape.py
```

**Output:** `raw_additional_youtube/{vektor}/{video_id}.csv` dengan kolom: comment_id, author, text, likes, replies, published_at, is_reply

**Dependencies:**
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## 9b. PHASE 4 — Tweet Harvest Query Runner

**Script:** `src/phase4_tweet_harvest.py`

**Input Requirements:**
- Tweet Harvest CLI installed: `pip install tweet-harvest`
- X/Twitter API credentials (Bearer token) — set up via Tweet Harvest auth
- `data/query_spec.json` — query specification (sudah auto-generated dengan queries per vektor)

**Query Specification** (`query_spec.json`):
- 6-7 queries per vektor yang menargetkan 5 scarcity modus + keragaman
- Contoh ewallet (X-driven, 9.2% retention):
  - QRIS palsu/tempel lokasi publik
  - Scan QR "balik"/refund ⚑ scarcity
  - Promo cashback e-wallet palsu ⚑ scarcity
  - Saldo OVO/DANA raib
  - Admin/CS palsu
- Limit per query: 500 tweets konservatif (hindari rate-limit ban)
- Rentang temporal: 2023-01-01 sampai 2026-06-20 (Twitter Harvest bersifat snapshot, lihat Temuan #1)

**Eksekusi:**
```bash
python src/phase4_tweet_harvest.py
```

**Output:** 
- `raw_additional_tweets/{vektor}/q{idx}.jsonl` (raw Tweet Harvest output)
- Auto-convert ke `raw_additional_tweets/{vektor}/q{idx}.csv` untuk compatibility dengan phase5_consolidate.py
- `raw_additional_tweets/_summary.json` — metadata eksekusi

**Catatan:**
- Tweet Harvest mungkin memerlukan akun X sekunder (mitigasi rate-limit ban)
- Jeda 2 detik antar-query otomatis di script
- Output timestamp kemungkinan snapshot (lihat Temuan #1)

---

## 10. FILE INVENTORY (Bawa ke Project)

Letakkan semua file ini di project Anda:

### Dokumentasi (folder `docs/`)
- `CONTEXT.md` (file ini)
- `00_Annotation_Guidelines_ICTT_v2.1.md` — pedoman anotasi 6 label + speaker role
- `01_Technical_Roadmap.md` — roadmap 8 fase lengkap
- `02_Pattern_Library.md` — pattern regex per vektor (referensi untuk Snorkel)
- `03_Phase2_Scraping_Plan.md` — rencana scraping tambahan (conditional)

### Code (folder `src/`)
- `anchor_patterns.py` — pattern library Python (untuk filter & dasar Snorkel)
- `phase5_consolidate.py` — script konsolidasi (reproducibility, sudah dijalankan)
- `audit_dataset.py` — script audit (Phase 0, reusable)
- `phase6_preprocess.py` — text preprocessing pipeline (Phase 6, sudah dijalankan)
- `phase7_pipeline.py` — Snorkel aggregation (Phase 7, sudah dijalankan)
- `phase7_labeling.py` — 46 labeling functions per vektor (Phase 7)
- `phase7_layer1.py` — Layer-1 relevance filter LFs (Phase 7)
- `phase7_qc.py` — LF quality control via LFAnalysis (Phase 7)
- `refresh_vector_hint.py` — recompute vector_hint only (row-stable, Phase 5 refinement)
- `phase3_youtube_scrape.py` — YouTube API v3 comment scraper (Phase 3, baru)
- `phase4_tweet_harvest.py` — Tweet Harvest query runner (Phase 4, baru)

### Data (folder `data/`)
- `unified_dataset.csv` — OUTPUT PHASE 5, INPUT PHASE 6 (48.496 baris)
- `preprocessed_dataset.csv` — OUTPUT PHASE 6 (48.496 baris, 18 kolom dengan text_clean/text_normalized/text_stemmed)
- `weak_labeled_dataset.csv` — OUTPUT PHASE 7 (48.496 baris, weak labels + metadata)
- `slang_dictionary.csv` — slang→baku mapping (88 entri, dipakai Phase 6)
- `video_candidates.csv` — TEMPLATE untuk user fill (Phase 3 input, baru)
- `query_spec.json` — query specification per vektor (Phase 4 input, auto-generated, baru)
- Folder `raw/` (59 file CSV) — raw data awal (simpan untuk reproducibility)
- Folder `raw_additional_youtube/` — OUTPUT PHASE 3 (baru, belum ada)
- Folder `raw_additional_tweets/` — OUTPUT PHASE 4 (baru, belum ada)

### Referensi (folder `references/`)
- `State_of_the_Art.docx` — 12 jurnal SOTA
- CTI-Twitter paper (Kristiansen 2020) — rujukan arsitektur 2-lapis

---

## 11. SARAN ALUR KERJA DI CLAUDE CODE

1. Mulai: *"Baca CONTEXT.md, docs/01_Technical_Roadmap.md Bagian 8, dan docs/02_Pattern_Library.md. Kita lanjut Phase 6 Preprocessing."*

2. Setup environment dulu:
   ```bash
   pip install pandas sastrawi nltk snorkel transformers torch
   ```

3. Kerjakan per phase, commit ke Git setiap selesai satu komponen.

4. Untuk Phase 3/4 (scraping tambahan), Anda perlu:
   - YouTube Data API v3 key (Google Cloud Console)
   - Tweet Harvest auth token (akun X sekunder)
   - Jalankan di lokal, BUKAN di Kaggle (butuh kredensial pribadi)

5. Untuk Phase 7-8 (Snorkel + training), pindah ke Kaggle T4 GPU.

---

## 12. HAL YANG BELUM DIPUTUSKAN (Untuk Didiskusikan Nanti)

- Apakah perlu rekonstruksi timestamp X untuk analisis temporal? (Tidak, created_at sudah akurat — hanya interpretasi yang perlu jujur)
- Strategi handling konten distress (G4.2 di judi_online_pinjol) — etika riset, perlu protokol
- Apakah `judi_online_pinjol` dipisah jadi 2 label di iterasi mendatang?
- Split train/test final — apakah Opsi C (data lama sbg pembanding) atau murni data baru

---

*Dokumen ini adalah snapshot status per akhir Phase 5. Update saat phase berikutnya selesai.*
