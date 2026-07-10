# CONTEXT.md — Handoff untuk Claude Code

> **Cara pakai dokumen ini:** Letakkan file ini di root project Anda. Saat membuka Claude Code, mulai dengan: *"Baca CONTEXT.md untuk memahami project ini."* Claude Code akan punya konteks penuh tanpa Anda perlu menjelaskan ulang.

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
| 3 | YouTube Data API v3 | 🟡 BERIKUTNYA — deps terpasang, script siap; butuh kurasi `video_candidates.csv` (fokus malware/deepfake) + `YOUTUBE_API_KEY` |
| 4 | Tweet scraping (Jalur C) | ✅ DIJALANKAN (21 Jun 2026) — X via Tweet Harvest, +1.836 baris unik (lihat Temuan #7) |
| 5 | Filter & Dedup | ✅ SELESAI — output `unified_dataset.csv` (48.496 baris) |
| 6 | Preprocessing | ✅ SELESAI — v1 `preprocessed_dataset.csv`; **v2 `preprocessed_dataset_v2.csv` (55.300 baris)** via `--input/--output` |
| 7 | Snorkel Labeling Functions | ✅ SELESAI — v1 `weak_labeled_dataset.csv`; **v2 `weak_labeled_dataset_v2.csv` (9.212 relevan, seed 42)** (lihat Temuan #7) |
| 3 (scraping) | YouTube API v3 Scraper | ✅ SELESAI — 8 video (7 malware + 1 deepfake), 6.663 komentar → `raw_additional_youtube/` |
| 4 (scraping) | Tweet Harvest Query Runner | ✅ SELESAI — `query_spec_v2.json` (broadened), output `raw_additional_tweets/`, merge → `unified_dataset_v2.csv` |
| 7.1 | Scraping 4 vektor lemah | ✅ SELESAI (X+YT). Relevan v1→v2: ewallet 23→548, peretasan 46→365, malware 36→214, deepfake 62→107 (tetap floor) |
| 8 | Gold Standard Annotation | 🟢 SELESAI (23 Jun 2026) — A=Ray, B=Nabilla Putri. IAA EXCELLENT (κ L1 0,925/L2 0,976/role 0,825). Weak-label tervalidasi pada subset sepakat n=311: **akurasi L1 90,0% / L2 96,9%, precision 0,91–1,00** (Temuan #8). Gold = VALIDASI saja |
| 9 | Training Triple-Hybrid | 🟢 **Model A + B + Late Fusion + XAI SELESAI** (24 Jun–8 Jul 2026) — branch `feat/phase9-training`. Layer 1: acc 0,9819 · macro-F1 0,9680 · recall-relevan 0,9674. Layer 2: acc 0,9881 · **macro-F1 0,9767** (phishing F1 0,91 terendah — scam umbrella). Fusion 0,75:0,25 (a priori): L1 recall-relevan +0,87pp (→0,9761, 8 FN diselamatkan), L2 redundan/interpretabilitas. XAI LIME: sinyal domain tervalidasi (`apk` +0,91), confusion phishing-judi **dua-pola** (scam-umbrella + sinyal judi tersirat). Lihat Temuan #9–#11 |

---

## 4a. Kerangka Metodologi (Dua Metode — Gambar 3.1 tesis)

**PENTING (perubahan kerangka, Jul 2026):** Metodologi tesis memakai **DUA metode paralel**, BUKAN CRISP-DM. Referensi CRISP-DM lama pada draf apa pun **diganti** kerangka ini.

**Metode 1 — Prototyping (dashboard):**
`Analisis Kebutuhan → Perancangan → Pengembangan Prototype → Evaluasi Prototype`

**Metode 2 — Pengembangan Model:**
`Pengumpulan Data → Persiapan Dataset → Pemisahan Dataset → Hyperparameter Tuning → Modelling (IndoBERT→BiGRU→BiLSTM + Rule-based Regex) → Pengujian Data → Evaluation → Deployment`

**Alur antar-metode:** tahap **Perancangan** (Metode 1) memicu jalur **Pengembangan Model** (Metode 2); **Deployment** (Metode 2) kembali ke **Pengembangan Prototype** (Metode 1). Model = mesin di balik dashboard.

**Pemetaan pekerjaan AKTUAL (Phase lama) → kerangka baru:**

| Tahap kerangka | Pekerjaan aktual |
|---|---|
| Pengumpulan Data | Scraping OSINT X + YouTube (Phase 3/4), 70.241 raw |
| Persiapan Dataset | Preprocessing (Phase 6) · **Snorkel weak supervision (46 LF vektor + 10 LF Layer-1 = 56 total)** (Phase 7) · **Gold Standard (357 sampel, κ 0,925/0,976/0,825)** (Phase 8) · validasi weak-label |
| Pemisahan Dataset | Split 80/10/10 stratified, seed 42 (Phase 9) |
| Hyperparameter Tuning | max_len 128, LR 2e-5, batch 16, class weights (Phase 9) |
| Modelling | Model A + Model B (Triple-Hybrid) + **mekanisme late fusion 0,75:0,25** |
| Pengujian Data | Inference test set |
| Evaluation | Metrik Model A/B · **ablation late fusion** · **XAI LIME** · perbandingan SOTA |
| Deployment | **BELUM** (checkpoint tersimpan; belum ada layanan inferensi) |
| **Jalur Prototyping (dashboard)** | **BELUM dikerjakan — status: PERENCANAAN** (lihat `docs/HANDOFF_DASHBOARD.md`) |

Catatan pemetaan: late fusion = **mekanisme** di Modelling, **hasil/ablation** di Evaluation. XAI LIME = sub-bagian Evaluation.

---

## 4b. Struktur Penulisan Tesis (4 Bab) + Cetak Biru BAB 3

**4 Bab:** BAB 1 Pendahuluan · BAB 2 Tinjauan Pustaka · BAB 3 Pembahasan · BAB 4 Penutup. **Semua hasil masuk BAB 3.**

**Cetak biru BAB 3:**
- **3.1** Gambaran Umum
- **3.2** Analisis Kebutuhan
- **3.3** Perancangan — 3.3.1 model, 3.3.2 dashboard
- **3.4** Pengumpulan Data
- **3.5** Persiapan Dataset — 3.5.1 Preprocessing, 3.5.2 Snorkel, 3.5.3 Gold Standard, 3.5.4 Validasi Weak Label
- **3.6** Pemisahan Dataset
- **3.7** Hyperparameter Tuning
- **3.8** Modelling — 3.8.1 arsitektur dasar, 3.8.2 Model A, 3.8.3 Model B, 3.8.4 Late Fusion
- **3.9** Pengujian Data
- **3.10** Evaluasi — 3.10.1 Model A, 3.10.2 Model B, 3.10.3 Ablation Fusion, 3.10.4 XAI LIME, 3.10.5 Perbandingan SOTA
- **3.11** Deployment
- **3.12** Pengembangan Prototype
- **3.13** Evaluasi Prototype (Blackbox, SUS, uji data)

**Catatan:** draf BAB 3 lama berbasis CRISP-DM = **bank materi**, perlu **restrukturisasi** ke kerangka dua-metode ini. Handoff penulisan: `docs/HANDOFF_WRITING.md`.

---

## 5. KEPUTUSAN METODOLOGIS YANG SUDAH FINAL

Jangan ubah keputusan ini tanpa alasan kuat — semuanya hasil diskusi panjang:

1. **Sumber data:** Bangun ulang dari raw mentah (70.241 baris, 59 file CSV). `master_dataset.csv` lama (17.374) DIPENSIUNKAN, hanya untuk pembanding hasil.

2. **Bahasa X:** Hanya `lang=in`. Non-Indonesia dibuang.

3. **Reply YouTube:** Include dengan quality filter (Opsi 1) — min 5 kata + ada anchor vektor + bukan pure afirmasi.

4. **Scraping tambahan:** Direncanakan untuk 3 vektor lemah (malware_apk, penipuan_ewallet_qris, deepfake_penipuan_ai), via YouTube + X. EKSEKUSI DITUNDA sampai distribusi pasca-Snorkel diketahui. Threshold: vektor dengan < 1.000 sampel relevan setelah Snorkel.

   **Strategi: scraping dari sumber baru (bukan probe refinement dari data lama).** Probe *relevance-lever* (refine dead-LF Phase 7 untuk menyelamatkan relevansi dari 18 video lama) **sengaja dilewati — keputusan sadar**, konsisten dengan kesimpulan Temuan #6 (§6: pengungkit utama kelas lemah = scraping, bukan refine LF). Alasan: LF probe pada 18 video existing sudah menciptakan selection bias (5 video = 50% data). Menyelamatkan sisanya via pattern refinement menghadapi law of diminishing returns (recovery kecil, anchor tetap ketat). Sebaliknya, scraping sumber baru (YouTube channel berbeda + query X baru) memberikan **volume + diversity sekaligus**, menghindari over-fitting ke 18 video existing, dan memberi spatial coverage yang lebih luas di discourse landscape. Ini trade-off: scraping lebih mahal (manual curation + API calls) tapi hasil lebih defensible metodologis (explicit sampling protocol, no hidden selection bias).

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

7. **Phase 3+4 scraping tambahan DIJALANKAN (21 Jun 2026) — final `unified_dataset_v2.csv` (55.300 baris, +6.804).** Phase 4 X dulu (Tweet Harvest = Node CLI `npx tweet-harvest@latest`, auth `auth_token` cookie; X-only checkpoint 50.332), lalu Phase 3 YouTube → final 55.300. Hasil X unik pasca-filter+dedup: **peretasan +1.176, ewallet +525, malware +84, deepfake +51** (cross-batch dup minim → data aditif). Temuan metodologis (untuk Bab 3/4):
   - **a. Sintaks query menentukan yield.** Query `(a)(b)(c)` triple-conjunction → **0 hasil** di window LATEST; hanya **phrase-OR** dan **≤2-group** yang produktif. Karena itu `query_spec.json` lama (banyak 3-group) direvisi → `data/query_spec_v2.json` (broadened). Diagnostik 2-group `(dana OR ovo) (penipuan OR tipu)` = 69 hasil → grouping VALID, query lama hanya terlalu spesifik.
   - **b. Filter `lang=='in'` esensial (Decision #2 bekerja keras).** `lang:id` di-query bersifat soft; 1 query deepfake (`"scam ai"/"ai"`) mengembalikan 518 baris tapi **445 di antaranya `en`** (token cognate Inggris). Hanya 28 `in`. Tanpa filter ini dataset akan terkontaminasi multibahasa.
   - **c. malware + deepfake GENUINELY scarce di X Indonesia.** TOP-tab tidak menambah (TOP malware 49 ⊂ LATEST 95, identik). Mengonfirmasi Temuan #6 scarcity. **YouTube (Phase 3) = pengungkit utama untuk malware/deepfake**; ewallet + peretasan sudah X-covered.
   - **d. Operasional:** scraping per-vektor satu-per-satu (script `--vektor`/`--query`/`--spec`/`--tab`), 0 rate-limit (429) sepanjang ~4 vektor. Output tab-aware (`qN.csv` LATEST, `qN_top.csv` TOP) agar tidak saling timpa. Re-merge final harus dari `unified_dataset.csv` ASLI (bukan v2) dengan kedua raw dir hadir.
   - **e. YouTube (Phase 3) = pengungkit kelas lemah.** 8 video kurasi (7 malware + 1 deepfake — deepfake "scarcity terkonfirmasi", hanya 1 video viable), 6.663 komentar. Baris unik baru pasca-merge: **malware +4.060, deepfake +1.043** (vs X-only +84/+51). NO_HINT 53% (dilusi komentar fan YouTube — relevansi final diputuskan Snorkel, bukan anchor hint).
   - **f. Phase 6+7 re-run di v2 (seed 42, LF & metodologi IDENTIK v1 → beda murni dari data; v1 deepfake terverifikasi = 62 sama dgn baseline).** Relevan per vektor **v1→v2**: ewallet 23→**548** (24×), peretasan 46→**365** (8×), malware 36→**214** (6×), deepfake 62→**107** (1,7×, **tetap floor**); phishing 391→492 (spillover scam-umbrella, Temuan #4d); judi 7.425→7.486 (tak disasar). **Total relevan 7.983→9.212 (+1.229).** Relevance rate stabil **16,5%→16,7%** (query broad TIDAK menurunkan presisi). **deepfake 107 = ceiling realistis** dari sumber tersedia (scarcity nyata X+YT, bukan gap pipeline) → di Phase 9 tangani via **class weight / focal loss**, bukan ekspektasi data lebih. Output: `preprocessed_dataset_v2.csv`, `weak_labeled_dataset_v2.csv`. Phase 8 sampling dari v2.

8. **Phase 8 Gold Standard Sampling SIAP (22 Jun 2026) — 357 sampel blind dari `weak_labeled_dataset_v2.csv` (seed 42).** Stratified hybrid-floor: **297 relevan** (lantai 35/vektor + sisa proporsional 87 → judi 106, ewallet 40, phishing 40, peretasan 38, malware 37, deepfake 36) + **60 tidak_relevan** (validasi Layer 1). Komposisi platform: 248 YouTube / 109 X. Output blind: `gold_annotation_sheet{,_A,_B}.csv` — `sample_id` anonim (G001..), teks **ORIGINAL**, urutan **diacak**, TANPA platform/source/weak-label (tak bisa ditebak) + kolom annotator kosong (layer1/layer2/speaker_role/confidence/notes). Kunci `gold_key_HIDDEN.csv` (**JANGAN beri ke annotator** — peta sample_id→unified_id+weak label+source+hint). **2 annotator qualified (A & B)** label independen; reviewer ketiga rekonsiliasi disagreement (guidelines §7). Skrip: `src/phase8_gold_sampling.py` (sampling, reproducible) + `src/phase8_kappa_analysis.py` (Cohen's Kappa Layer1/Layer2/per-label + akurasi & per-class precision weak label + `gold_disagreements.csv` untuk reviewer ketiga). Target κ guidelines §7.2: ≥0,80 excellent, 0,60–0,80 substantial, <0,60 revisi major.
   - ⚠️ **Limitasi terdokumentasi: fraksi sampling deepfake 34% (36/107).** Karena deepfake = kelas terkecil (Temuan #7f), gold deepfake mencakup **34% populasi relevannya** — jauh di atas kelas besar (judi 1,4%, ewallet 7,3%, malware 17,3%). Implikasi: metrik gold deepfake **kurang independen** + interval kepercayaan lebih lebar; **jangan over-generalisasi** angka presisi/recall deepfake ke populasi. Konsekuensi langsung dari scarcity (Temuan #7c) — bukan kelemahan sampling design.
   - ✅ **Anotasi SELESAI (23 Jun 2026): A=Ray, B=Nabilla Putri, independen blind.** IAA **EXCELLENT semua dimensi** (target guidelines §7.2 ≥0,80): **Cohen's κ Layer 1 = 0,925**, **Layer 2 (vektor, n=264 both-relevan) = 0,976**, **speaker_role = 0,825**. Per-vektor κ (one-vs-rest): malware 1,00 · deepfake 1,00 · judi 0,974 · ewallet 0,971 · peretasan 0,966 · phishing 0,947 (semua ≥0,95). **46 disagreement** (10 Layer 1, 5 Layer 2, 34 speaker_role) → `data/gold_disagreements.csv` (kolom `final_*` **KOSONG**, menunggu rekonsiliasi reviewer ketiga/dosen). File: `gold_annotation_sheet_A_filled.csv`, `gold_annotation_sheet_B_filled.csv`.
   - ✅ **Akurasi weak-label SUDAH dihitung (23 Jun 2026). Keputusan metodologis FINAL: gold standard = VALIDASI saja** — test set Phase 9 diambil dari split `weak_labeled_dataset_v2.csv` (BUKAN dari gold), maka **rekonsiliasi 46 disagreement TIDAK diperlukan**. Gold proxy = **subset SEPAKAT PENUH A==B (n=311**; 46 disagreement dikecualikan; κ excellent = bukti subset ini reliable sbg gold). Hasil weak-label (Snorkel) vs gold: **Akurasi Layer 1 = 90,0%** (n=311); **Akurasi Layer 2 = 96,9%** (sepakat-relevan n=228). **Per-class precision:** ewallet 1,00 · malware 1,00 · judi 1,00 · deepfake 1,00 · peretasan 0,964 · **phishing 0,906** (terendah — konsisten "scam umbrella" Temuan #4, tetap sangat baik). Reproduksi: `phase8_kappa_analysis.py` (tanpa `--iaa-only`). `gold_disagreements.csv` tetap diarsipkan (kolom `final_*` kosong) untuk audit, bukan blocker.

9. **Phase 9 Training DIMULAI (24 Jun 2026) — branch `feat/phase9-training`. ARSITEKTUR FINAL: 2 model TERPISAH (pipeline 2-lapis), training di Kaggle T4.**
   - **Model A (Layer 1 relevance) — skeleton SIAP:** `IndoBERT-base-p1` (fine-tune **PENUH**) → **BiGRU**(768→256 bidir) → **BiLSTM**(512→128 bidir) **serial** → masked-mean pool → dropout → classifier biner. Imbalance relevan:tidak_relevan ≈ **1:5** → **class weights** (balanced inverse-freq). **LR 2e-5**, AdamW, **early stopping** monitor val macro-F1, simpan best checkpoint. Metrik: accuracy, macro-F1, **recall kelas relevan** (diperhatikan khusus), confusion matrix. Skrip: `src/phase9_model_a_layer1.py` (device CUDA auto; lazy-import torch). **Late fusion 0,75 neural : 0,25 rule-based (anchor) = TODO TERPISAH** (`rule_score_layer1`/`fuse_predictions` stub) — jalur neural jalan & dievaluasi dulu.
   - **Model B (Layer 2 vektor) — BELUM di-scaffold** (sengaja: tunggu Model A tervalidasi di Kaggle dulu).
   - **Data split — `src/phase9_data_split.py` (seed 42, 80/10/10 stratified, fitur `text_clean`):** Layer 1 = SEMUA 55.300 (relevan proporsional **16,7%** tiap split); Layer 2 = 9.212 relevan, 6 vektor (**deepfake di ketiga split: 86/11/10**). Output `data/splits/{layer1,layer2}_{train,val,test}.csv` + `_split_manifest.json`. ⚠️ **deepfake test = 10** (CI lebar, jangan over-generalisasi).
   - **Token length `text_clean` (tokenizer IndoBERT, incl [CLS]/[SEP]):** median 16, p90 49, p95 65, **p99 122**, max 549. **>128 token hanya 0,90%** keseluruhan (relevan-only 2,34%). → **`max_len=128` CUKUP** (cover p99); tidak perlu dinaikkan, truncation minimal (anchor umumnya di awal teks).
   - **Dependency Kaggle:** `torch`, `transformers` (≥4.30; terpasang lokal v5.x utk tokenizer), `scikit-learn`, `pandas`, `numpy`. Training **GPU-bound** → jalankan di Kaggle T4, BUKAN lokal.
   - ✅ **Model A TERVALIDASI (24 Jun 2026) — Layer 1 test set (weak-label):** Accuracy **0,9819** · Macro-F1 **0,9680** · Recall relevan **0,9674**. Confusion matrix: TN=4539 · FP=70 · FN=30 · TP=891. Training: early stopping epoch 3 (best checkpoint epoch 1), ~20 menit/epoch di T4, class weights [0,6; 3,0], LR 2e-5, batch 16, max_len 128.
   - ✅ **Model B TERVALIDASI (24 Jun 2026) — Layer 2 test set (weak-label, 922 sampel relevan):** Accuracy **0,9881** · Macro-F1 **0,9767**. Per-class F1: phishing **0,91** · ewallet 1,00 · malware 0,96 · judi 0,99 · peretasan 1,00 · deepfake 1,00. **Loss: weighted_ce CUKUP** — focal tidak diperlukan (deepfake/malware F1 sudah baik meski kelas kecil). **Temuan konfusi utama:** phishing↔judi leakage bidireksional (3 phishing diprediksi judi + 6 judi diprediksi phishing; 2 judi→malware) — konsisten dengan "scam umbrella" Temuan #4. Catat untuk Bab 4 sebagai limitasi diskursus overlap antar-vektor. Training: LR 2e-5, batch 16, max_len 128, early stopping.
   - ⚠️ **Interpretasi KRITIS (Bab 4):** Metrik Model A & B mengukur **seberapa baik model meniru weak label Snorkel**, **BUKAN akurasi vs gold manusia**. Validasi vs manusia ada di Phase 8: weak-label accuracy Layer 1 = 90,0% / Layer 2 = 96,9% (n=311 subset sepakat). Kedua angka menjawab pertanyaan berbeda — jaga perbedaan ini jelas di Bab 4 agar tidak misleading.
   - **Lesson learned Kaggle (berlaku untuk Model B):** Jalankan training via **inline cells**, bukan `subprocess.run()`. `subprocess` menyembunyikan semua `print()` lewat buffering — output training tidak terlihat di cell. Gunakan inline cells dengan `flush=True` dan step-200 prints selama training.

10. **Late Fusion (rule-based anchor, 0,75 neural : 0,25 rule) DIEVALUASI + DIVERIFIKASI (6 Jul 2026) — bobot rancangan 0,75:0,25 DIPERTAHANKAN. Kontribusi FUNGSIONAL di Layer 1, INTERPRETABILITAS di Layer 2.**
   - **Setup:** inference-time, `skor = 0,75·P_neural + 0,25·anchor`; model **TIDAK** dilatih ulang (checkpoint Model A/B dimuat; sanity check reproduksi macro-F1 0,9680/0,9767 → checkpoint valid). Anchor **L2** = share bukti per-vektor (`count(v)/Σcount`, 0 semua bila tak ada anchor → defer neural); anchor **L1** = sinyal **satu-arah** relevan (`has_anchor→[0,1]`, else `[0,0]` → tak menekan ke tidak_relevan). Notebook fusion = **load-only** (sesi training mati, checkpoint tersimpan; `anchor_patterns` di-embed verbatim). Sweep lengkap L1+L2 (data ablation Bab 4): `docs/phase9_fusion_ablation.md`. Arsip logika: `src/phase9_late_fusion.py`.
   - ✅ **Layer 1 (relevansi) — rule-based BERKONTRIBUSI FUNGSIONAL.** Fusion 0,75:0,25 menaikkan **recall relevan 0,9674 → 0,9761** (+0,87pp), **menyelamatkan 8 FN** (relevan yang neural lewatkan; FN 30→22), biaya **+9 FP** (70→79), **macro-F1 datar** (0,9680→0,9679; CM sesudah `[[4530,79],[22,899]]`; F1_relevan tetap ~0,947 — recall ditukar presisi seimbang). Kurva: recall naik monoton ke 1,0 & FN→0 saat w_rule naik, tapi FP meledak (→904) & macro-F1 kolaps di ≥0,40 rule; **knee di ~0,75**. Untuk filter tahap-1, recall tinggi = tujuan benar (relevan yang terbuang hilang permanen; FP masih disaring Layer 2) → **sesuai desain relevance filter**.
   - ⚠️ **Layer 2 (6-vektor) — bobot rancangan 0,75:0,25 DIPERTAHANKAN, redundan secara diskriminatif.** Fusion 0,75:0,25: macro-F1 **0,9747** vs neural **0,9767** (selisih dapat diabaikan, **−1 sampel phishing**). **Ablation: 0,50:0,50 mencapai macro-F1 0,9814 (F1_phish 0,9375), STABIL di rentang w_neural 0,45–0,51** (terverifikasi Sel D2 — **BUKAN artefak tie-breaking**). Mekanisme (Sel D1): koreksi **4 sampel boundary phishing-judi — semuanya gold=judi yang neural over-prediksi sebagai phishing** (konsisten "scam umbrella" Temuan #4); anchor judi mengembalikannya ke judi → presisi phishing naik. **TIDAK DIPILIH — keputusan metodologis: (1) bobot 0,50 teridentifikasi PADA test set → memilihnya = test-set optimization / bias evaluasi; (2) 0,75:0,25 = rancangan a priori. Nilai rule-based di L2 = interpretabilitas (XAI), bukan akurasi.**
   - **Kesimpulan (Bab 4):** neural memikul **beban diskriminatif utama**; rule-based memberi **interpretabilitas (L2) + kenaikan recall relevan (L1, +0,87pp / 8 FN)**. Anchor = *relevance detector* (kekuatan L1), bukan *vector separator* (kelemahan L2) — persis rasional Triple-Hybrid.

11. **XAI — LIME pada Model B (Layer 2) DIJALANKAN (8 Jul 2026) — validasi sinyal domain + analisis DUA-POLA phishing-judi.** LIME menjelaskan `predict_fn` = **komponen NEURAL murni** (softmax Model B; bobot **dominan 0,75** dalam fusion → merepresentasikan penggerak keputusan utama pipeline). Metodologi: LIME **level-kata** (bukan sub-token IndoBERT — `predict_fn` menokenisasi internal, LIME hanya melihat kata utuh spt "apk", bukan "ap"+"##k"), `num_samples=500`, `bow=True`, seed 42, pada **sampel bertarget (bukan acak)**: 4 boundary phishing-judi (idx 25/558/719/778, semua gold=judi neural=phishing) + 3 sampel benar (malware idx 4, judi idx 6, deepfake idx 156). Notebook load-only (checkpoint + sanity macro-F1 0,9767 dulu).
   - ✅ **Temuan 1 — model belajar sinyal domain BENAR (validasi kredibilitas):** malware idx 4 → token `apk` bobot **+0,907** (dominan mutlak); judi idx 6 → `slot` +0,225, `judi` +0,202; deepfake idx 156 → `deepfake` +0,390, `ai` +0,297. Model menangkap **semantik domain nyata**, bukan artefak korpus.
   - ⚠️ **Temuan 2 — confusion phishing-judi punya DUA POLA (nuansa penting; Temuan #4 terkonfirmasi SEBAGIAN — JANGAN over-claim sebagai konfirmasi penuh):**
     - **Pola A (konsisten scam-umbrella Temuan #4):** idx 25 → `nipu` **+0,398** & `penipu` **+0,140** mendorong phishing, **mengalahkan** `judol` +0,545 yang mendorong judi. Kosakata penipuan generik menang atas sinyal judi eksplisit.
     - **Pola B (menantang narasi sederhana):** idx 558 & 719 → pendorong phishing justru kata **kontekstual NETRAL** (`batubara` +0,453, `tambang` +0,286; `kehutanan` +0,493, `jurusan` +0,277), **BUKAN** scam-umbrella. Model default ke phishing karena **sinyal judi lemah/tersirat**, bukan karena kosakata penipuan.
     - **Kesimpulan jujur:** kesalahan boundary sebagian scam-umbrella (Pola A), sebagian **ketidakmampuan model menangkap referensi judi tersirat** (Pola B). Temuan #4 nyata tapi **bukan penjelasan tunggal**.
   - ⚠️ **Temuan 3 — keterbatasan (ambiguitas gold label):** idx 778 → token `rekt`/`bca`/`mutasii` (soal rekening bank) mendorong prediksi; gold=judi karena teks menyebut "pinjaman online". Teks itu sendiri **ambigu** (saldo BCA hilang vs judi/pinjol) → sebagian "kesalahan" mencerminkan **ambiguitas anotasi**, bukan kelemahan model semata.
   - **Catatan interpretasi:** LIME = aproksimasi lokal linear → token tak-intuitif (kata sambung "dan", "gua") wajar muncul. XAI ini pada komponen neural (0,75); komponen **anchor (0,25) transparan terpisah** (rule-based dapat dibaca langsung). **Nilai tesis:** memenuhi komponen Explainable AI di judul dengan bukti konkret; token domain benar memperkuat kredibilitas; analisis dua-pola = pembacaan data teliti (bukan over-claim).

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
