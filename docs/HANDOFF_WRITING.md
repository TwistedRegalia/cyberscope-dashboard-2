# HANDOFF — Sesi Penulisan Tesis

> Handoff untuk sesi penulisan (BAB 1–4). Baca ini + `CONTEXT.md` sebelum menulis. Angka di sini = sumber kebenaran; jangan mengarang, laporkan keterbatasan apa adanya.

---

## 1. Identitas penelitian

**Judul:** Klasifikasi Otomatis Diskursus Vektor Ancaman Siber pada Media Sosial Indonesia Menggunakan Pendekatan Hybrid Machine Learning Berbasis OSINT dan Explainable AI.
**Peneliti:** Ray (skripsi S1). **Bahasa:** Indonesia. **Sitasi:** APA.

**REFRAMING (prinsip fundamental):** penelitian ini **TIDAK** mendeteksi serangan siber langsung. Ia **mengklasifikasikan diskursus publik** tentang vektor ancaman — konten yang membicarakan ancaman (laporan korban R1, kesaksian R2, edukasi R3, promosi pelaku R4, diskusi netral R5). Setiap label mencakup seluruh spektrum diskursif ini. Prinsip ini memandu semua interpretasi.

---

## 2. Kerangka metodologi + struktur penulisan

**DUA metode paralel (Gambar 3.1), BUKAN CRISP-DM** (lihat `CONTEXT.md` §4a–§4c):
- **Metode Prototyping (dashboard):** Analisis Kebutuhan → Perancangan → Pengembangan Prototype → Evaluasi Prototype.
- **Metode Pengembangan Model:** Pengumpulan Data → Persiapan Dataset → Pemisahan Dataset → Hyperparameter Tuning → Modelling (IndoBERT→BiGRU→BiLSTM + Rule-based Regex) → Pengujian Data → Evaluation → Deployment.
- **Alur:** Perancangan memicu jalur model; Deployment kembali ke Pengembangan Prototype.

**4 Bab:** 1 Pendahuluan · 2 Tinjauan Pustaka · 3 Pembahasan (**semua hasil di sini**) · 4 Penutup.

**Cetak biru BAB 3:**
- 3.1 Gambaran Umum · 3.2 Analisis Kebutuhan · 3.3 Perancangan (3.3.1 model, 3.3.2 dashboard)
- 3.4 Pengumpulan Data · 3.5 Persiapan Dataset (3.5.1 Preprocessing, 3.5.2 Snorkel, 3.5.3 Gold Standard, 3.5.4 Validasi Weak Label)
- 3.6 Pemisahan Dataset · 3.7 Hyperparameter Tuning
- 3.8 Modelling (3.8.1 arsitektur dasar, 3.8.2 Model A, 3.8.3 Model B, 3.8.4 Late Fusion)
- 3.9 Pengujian Data · 3.10 Evaluasi (3.10.1 Model A, 3.10.2 Model B, 3.10.3 Ablation Fusion, 3.10.4 XAI LIME, 3.10.5 Perbandingan SOTA)
- 3.11 Deployment · 3.12 Pengembangan Prototype · 3.13 Evaluasi Prototype (Blackbox, SUS, uji data)

> **⚠️ 3.11–3.13 ditulis SETELAH dashboard selesai** — jalur Prototyping masih PERENCANAAN (`CONTEXT.md` §4c). Jangan tulis seolah sudah dikerjakan.
> Draf BAB 3 lama berbasis CRISP-DM = **bank materi**, perlu restrukturisasi ke kerangka ini.
> Lampiran data siap kutip: `docs/phase9_fusion_ablation.md`, `docs/phase9_xai_lime.md`, `docs/phase6_preprocessing_examples.md`.

---

## 3. Sebelas temuan (ringkas) — detail di `CONTEXT.md` §6

1. **Timestamp X = snapshot 7 hari** (13–20 Mei 2026), BUKAN multi-tahun. `created_at` akurat (Snowflake). X = cross-sectional OSINT snapshot; jangan klaim tren temporal X.
2. **Timestamp YouTube valid** (2022–2026). Karakteristik temporal dua platform BERBEDA — jelaskan terpisah.
3. **Selection bias YouTube:** 18 video awal, top 5 = 50% data → alasan scraping stratified tambahan.
4. **NO_HINT 77,4%→70,2%** setelah anchor v1.1. ⚠️ phishing hint melonjak (bucket "scam umbrella").
5. **Bug morfologi** (`pinjol` melewatkan "pinjolnya") — diperbaiki v1.1 (suffix klitik).
6. **QC Phase 7:** reproducibility terverifikasi; 11 dead LF; **pengungkit kelas lemah = scraping, bukan refine LF**.
7. **Scraping tambahan → `unified_dataset_v2.csv` (55.300).** Sintaks query menentukan yield; `lang=in` esensial; malware+deepfake scarce di X → YouTube = pengungkit.
8. **Gold Standard (357):** IAA EXCELLENT (κ L1 0,925 / L2 0,976 / role 0,825); weak-label tervalidasi (L1 90,0% / L2 96,9%). Gold = VALIDASI saja.
9. **Phase 9 training:** Model A + B (Triple-Hybrid), split 80/10/10 seed 42, max_len 128. Metrik = imitasi weak label, bukan gold manusia.
10. **Late fusion:** L1 recall relevan +0,87pp (safety net); L2 redundan (interpretabilitas). 0,50:0,50 TIDAK dipilih (test-set optimization).
11. **XAI LIME:** sinyal domain tervalidasi (`apk` +0,91); confusion phishing-judi **DUA-POLA** — Temuan #4 terkonfirmasi SEBAGIAN; idx 778 = ambiguitas gold.

---

## 4. Angka lengkap (sumber kebenaran)

### 4.1 Dataset lineage
`70.241 raw (59 file)` → filter+dedup → `48.496 (v1)` → scraping tambahan+dedup → `55.300 (v2)` → Snorkel → **`9.212 relevan`**.
- Platform v2: YouTube 51.739 · X 3.561.
- Snorkel LF: **46 LF vektor + 10 LF Layer-1 = 56 total** (seed 42). *(Draf yang menyebut "30 LF" SALAH — verifikasi source: `src/phase7_labeling.py` = 46 `@labeling_function`, `src/phase7_layer1.py` = 10.)*

### 4.2 Distribusi relevan per vektor (v1 → v2)
| Vektor | v1 | v2 |
|---|---:|---:|
| judi_online_pinjol | 7.425 | **7.486** |
| penipuan_ewallet_qris | 23 | **548** |
| phishing_rekayasa_sosial | 391 | **492** |
| peretasan_pencurian_identitas | 46 | **365** |
| malware_apk | 36 | **214** |
| deepfake_penipuan_ai | 62 | **107** (floor) |
| **Total relevan** | 7.983 | **9.212** |

### 4.3 Gold Standard (357 sampel)
- IAA (Cohen's κ): **L1 0,925 · L2 0,976 (n=264 both-relevan) · speaker_role 0,825**. Per-vektor κ ≥0,947.
- Validasi weak-label (gold proxy subset sepakat **n=311**): **akurasi L1 90,0% · L2 96,9% (n=228)**.
- Per-class precision: ewallet/malware/judi/deepfake 1,00 · peretasan 0,964 · **phishing 0,906** (terendah, scam umbrella).
- 46 disagreement (10 L1, 5 L2, 34 role) **TIDAK direkonsiliasi** (gold = validasi via subset sepakat).

### 4.4 Model A (Layer 1, test set weak-label)
accuracy **0,9819** · macro-F1 **0,9680** · recall relevan **0,9674** · CM `[[TN=4539, FP=70], [FN=30, TP=891]]`.

### 4.5 Model B (Layer 2, test set weak-label, 922 relevan)
- accuracy **0,9881** · macro-F1 **0,9767**.
- Per-class F1: phishing **0,91** · ewallet 1,00 · malware 0,96 · judi 0,99 · peretasan 1,00 · deepfake 1,00.
- CM 6×6 (baris=gold): phishing [46,0,0,3,0,0] · ewallet [0,55,0,0,0,0] · malware [0,0,22,0,0,0] · judi [6,0,2,741,0,0] · peretasan [0,0,0,0,37,0] · deepfake [0,0,0,0,0,10].

### 4.6 Ablation late fusion (sweep lengkap: `docs/phase9_fusion_ablation.md`)
- **L1 @0,75:0,25:** recall relevan 0,9674→**0,9761** (menyelamatkan **8 FN**; +9 FP; macro-F1 datar 0,9680→0,9679). Rule-based **fungsional**.
- **L2 @0,75:0,25 (a priori):** macro-F1 0,9767→**0,9747** (−1 phishing). **0,50:0,50 = 0,9814 (F1_phish 0,9375), stabil 0,45–0,51, TIDAK DIPILIH** (memilih bobot yang menang di test set = test-set optimization).

### 4.7 XAI LIME (`docs/phase9_xai_lime.md`)
- Sinyal domain benar: `apk` +0,907 · `slot`/`judi` +0,225/+0,202 · `deepfake`/`ai` +0,390/+0,297.
- Dua-pola phishing-judi: **A** (idx 25: `nipu`/`penipu` mengalahkan `judol`) = scam umbrella; **B** (idx 558/719: token netral mengalahkan `judi`) = sinyal judi tersirat. idx 778 = ambiguitas gold.

---

## 5. Hyperparameter + setup

| Item | Nilai | Justifikasi |
|---|---|---|
| max_len | 128 | p99 token = 122; **>128 hanya 0,9% terpotong** |
| split | 80/10/10 stratified | seed 42, reproducible |
| fine-tune | PENUH (IndoBERT) | bukan freeze |
| LR | 2e-5 | AdamW |
| batch | 16 | T4 |
| early stopping | patience 2, monitor **val macro-F1** | simpan best checkpoint |
| loss | **class weights (balanced)** — **BUKAN focal loss** | focal tidak diperlukan (deepfake/malware F1 sudah baik) |
| seed | 42 | seluruh pipeline |
| fusion | 0,75 neural : 0,25 rule-based | a priori |

---

## 6. ⚠️ Keterbatasan yang WAJIB dilaporkan (jangan disembunyikan)

1. **Kelas kecil, CI lebar:** deepfake test **n=10** (jangan over-claim F1=1,00), malware test **n=22**. Jangan over-generalisasi.
2. **Gold deepfake overlap 34%** (36/107 populasi) → gold deepfake kurang independen.
3. **Metrik model = imitasi weak label Snorkel, BUKAN akurasi vs manusia.** Validasi manusia terpisah di gold standard (L1 90,0% / L2 96,9%). Dua angka menjawab pertanyaan berbeda — jaga jelas.
4. **46 disagreement gold tidak direkonsiliasi** — gold = validasi via subset sepakat (n=311), **bukan test set**. Sah, tapi catat eksplisit.
5. **LIME = aproksimasi lokal linear** — token tak-intuitif (kata sambung `dan`/`gua`) wajar muncul.
6. **X = snapshot 7 hari**; **deepfake 107 = ceiling** dari sumber tersedia (scarcity nyata).

---

## 7. Diferensiasi SOTA (kritis — angkat PROAKTIF di BAB 2 + 3.10.5)

**Mujilahwati et al. (2026), IJAAS 15(1):322–332** memakai **arsitektur inti SAMA** — IndoBERT + BiGRU + BiLSTM serial, F1 **98,98%** — TAPI:
- Tugas: **klasifikasi biner hoax** (bukan 6-vektor ancaman siber).
- Dataset: **berita, 4.312 sampel (TurnBackHoax + Detik)** — bukan OSINT media sosial 55.300.

**Sikap jujur:** arsitektur neural **BUKAN** novelty Ray — akui terbuka tulang punggung neural serupa sudah ada. **JANGAN posisikan novelty di arsitektur.** **Novelty Ray:**
1. Taksonomi **E-ICTT** diskursus 6 label (extend Arifman 2026 + deepfake emerging).
2. **Framing diskursus** (bukan deteksi serangan) + speaker role R1–R5.
3. **Weak supervision (Snorkel)** untuk domain **langka-data**.
4. **Dataset OSINT** X+YouTube Indonesia (skala + diversity).
5. **XAI (LIME)** untuk interpretabilitas.

Kontribusi = **rekayasa masalah + data + taksonomi + interpretabilitas**, bukan arsitektur. Posisi defensible di sidang.

---

## 8. Gaya penulisan

- Bahasa Indonesia akademik; sitasi **APA**.
- **Jangan over-claim.** Laporkan keterbatasan apa adanya (bagian 6). Bila hasil ambigu (Temuan #4 dua-pola), tulis "terkonfirmasi sebagian" — jangan paksa narasi tunggal.
- Bedakan tegas metrik weak-label vs validasi manusia.
- **3.11–3.13 ditulis setelah dashboard** — jangan tulis seolah sudah dikerjakan.
- Angka dari file ini / `CONTEXT.md`; bila ragu, verifikasi ke sumber (`data/`, `docs/`, `src/`), jangan mengarang.
