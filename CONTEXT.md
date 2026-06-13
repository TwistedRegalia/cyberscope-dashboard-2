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
| 6 | Preprocessing | 🔜 **BERIKUTNYA** |
| 7 | Snorkel Labeling Functions | ⏳ Belum |
| 8 | Gold Standard Annotation | ⏳ Belum |

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

4. **Vector hint 77% NO_HINT di Phase 5** — ini ARTEFAK anchor discovery yang konservatif, BUKAN indikasi 77% data tidak relevan. Keputusan relevansi sebenarnya = tugas Snorkel (Phase 7). Vector hint hanya diagnostik kasar.

5. **Bug morfologi pattern:** `\bpinjol\b` melewatkan "pinjolnya/pinjolku". Perbaiki di pattern library Snorkel — tambah handling suffix Indonesia (-nya, -ku, -mu, -lah).

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

## 8. PHASE 6 — PREPROCESSING (Langkah Berikutnya)

Tujuan: transformasi teks bersih → siap tokenisasi IndoBERT.

Komponen yang harus dibangun (lihat detail di `01_Technical_Roadmap.md` Bagian 8):

1. **Case folding** — lowercase
2. **URL/mention/hashtag handling** — URL→[URL], @user→[USER], #judol→ekstrak "judol"
3. **Emoji handling** — emoji emosi (😢😡💸)→tag, decorative→strip
4. **Slang normalization** — kamus slang Indonesia (gw→saya, gak→tidak) + PERTAHANKAN slang cybercrime (gacor, rungkad — bermakna)
5. **Stemming Sastrawi** — opsional, untuk fitur tambahan
6. **Stopword** — JANGAN buang untuk BERT, hanya untuk fitur Tier-2

**Output Phase 6:** `preprocessed_dataset.csv` dengan kolom `text_original`, `text_clean`, `text_normalized`.

**PENTING:** Pertahankan `text_original`. Transformasi di kolom terpisah agar tidak ada information loss.

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

### Data (folder `data/`)
- `unified_dataset.csv` — OUTPUT PHASE 5, INPUT PHASE 6 (48.496 baris)
- Folder raw CSV (59 file) — simpan untuk reproducibility
- `master_dataset.csv` lama — arsip pembanding (jangan dipakai untuk training)

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
