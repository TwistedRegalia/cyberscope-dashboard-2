# HANDOFF — Sesi Penulisan Tesis

> Handoff untuk sesi penulisan (BAB 1–4). Baca ini + `CONTEXT.md` sebelum menulis. Angka di sini = sumber kebenaran; jangan mengarang, laporkan keterbatasan apa adanya.

---

## 1. Identitas penelitian

**Judul:** Klasifikasi Otomatis Diskursus Vektor Ancaman Siber pada Media Sosial Indonesia Menggunakan Pendekatan Hybrid Machine Learning Berbasis OSINT dan Explainable AI.
**Peneliti:** Ray (skripsi S1). **Bahasa:** Indonesia. **Sitasi:** APA.

**REFRAMING (prinsip fundamental):** penelitian ini **TIDAK** mendeteksi serangan siber langsung. Ia **mengklasifikasikan diskursus publik** tentang vektor ancaman — konten yang membicarakan ancaman (laporan korban R1, kesaksian R2, edukasi R3, promosi pelaku R4, diskusi netral R5). Setiap label mencakup seluruh spektrum diskursif ini. Prinsip ini memandu semua interpretasi.

---

## 2. Kerangka metodologi + struktur penulisan

Lihat `CONTEXT.md` §4a (dua metode: Prototyping + Pengembangan Model — **BUKAN CRISP-DM**) dan §4b (cetak biru BAB 3, 3.1–3.13). Ringkas:
- **4 Bab:** 1 Pendahuluan · 2 Tinjauan Pustaka · 3 Pembahasan (semua hasil di sini) · 4 Penutup.
- Draf BAB 3 lama berbasis CRISP-DM = **bank materi**, perlu restrukturisasi ke kerangka dua-metode.
- Lampiran data: `docs/phase9_fusion_ablation.md`, `docs/phase9_xai_lime.md`, `docs/phase6_preprocessing_examples.md`.

---

## 3. Sebelas temuan (ringkas) — detail di `CONTEXT.md` §6

1. **Timestamp X = snapshot 7 hari** (13–20 Mei 2026), BUKAN rentang multi-tahun. `created_at` akurat (verified Snowflake). Posisikan X sebagai cross-sectional OSINT snapshot; jangan klaim tren temporal X.
2. **Timestamp YouTube valid** (2022–2026, `publishedAt`). Karakteristik temporal dua platform BERBEDA — jelaskan terpisah.
3. **Selection bias YouTube:** hanya 18 video awal, top 5 = 50% data → alasan utama scraping stratified tambahan.
4. **NO_HINT 77,4%→70,2%** setelah anchor v1.1. ⚠️ phishing hint melonjak 3,7%→10,4% (bucket "scam umbrella" menyerap narasi korban generik) — diawasi di Snorkel.
5. **Bug morfologi pattern** (`pinjol` melewatkan "pinjolnya") — diperbaiki v1.1 via suffix klitik.
6. **QC Phase 7:** reproducibility terverifikasi; 11 dead LF; **pengungkit utama kelas lemah = scraping, bukan refine LF**.
7. **Scraping tambahan → `unified_dataset_v2.csv` (55.300).** Sintaks query menentukan yield (triple-conjunction=0); filter `lang=in` esensial; malware+deepfake genuinely scarce di X → YouTube = pengungkit. Relevan v1→v2: ewallet 23→548, peretasan 46→365, malware 36→214, deepfake 62→107 (floor).
8. **Gold Standard (357):** IAA EXCELLENT (κ L1 0,925 / L2 0,976 / role 0,825); weak-label tervalidasi subset sepakat n=311 (akurasi L1 90,0% / L2 96,9%). Gold = VALIDASI saja.
9. **Phase 9 training:** Model A + B (Triple-Hybrid), split 80/10/10 seed 42, max_len 128 (p99=122). Metrik = imitasi weak label, bukan gold manusia.
10. **Late fusion:** L1 recall relevan +0,87pp (safety net); L2 redundan (interpretabilitas). Ablation 0,50:0,50=0,9814 TIDAK dipilih (test-set optimization).
11. **XAI LIME:** sinyal domain tervalidasi (`apk` +0,91); confusion phishing-judi **DUA-POLA** (A scam-umbrella, B sinyal judi tersirat) — Temuan #4 terkonfirmasi SEBAGIAN; idx 778 = ambiguitas gold.

---

## 4. Angka lengkap (sumber kebenaran)

### 4.1 Dataset lineage
`70.241 raw (59 file CSV)` → filter+dedup → `48.496 (unified v1)` → scraping tambahan+dedup → `55.300 (unified v2)` → Snorkel → **`9.212 relevan`**.
- Platform v2: YouTube 51.739 · X 3.561.
- Snorkel LF: **46 LF vektor + 10 LF Layer-1 relevance = 56 total** (seed 42). *(Catatan: draf yang menyebut "30 LF" salah — verifikasi ke `src/phase7_labeling.py` = 46, `src/phase7_layer1.py` = 10.)*

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
- Komposisi: 297 relevan (judi 106, ewallet 40, phishing 40, peretasan 38, malware 37, deepfake 36) + 60 tidak_relevan. Platform: 248 YouTube / 109 X.
- IAA (Cohen's κ): **L1 0,925 · L2 0,976 (n=264 both-relevan) · speaker_role 0,825**. Per-vektor κ ≥0,947 (malware/deepfake 1,00).
- Validasi weak-label (gold proxy subset sepakat n=311): **akurasi L1 90,0% · L2 96,9% (n=228)**. Per-class precision: ewallet/malware/judi/deepfake 1,00 · peretasan 0,964 · **phishing 0,906** (terendah, scam umbrella).
- 46 disagreement (10 L1, 5 L2, 34 role) **TIDAK direkonsiliasi** (gold = validasi via subset sepakat).

### 4.4 Model A (Layer 1, test set weak-label)
- accuracy **0,9819** · macro-F1 **0,9680** · recall relevan **0,9674**.
- CM `[[TN=4539, FP=70], [FN=30, TP=891]]`.
- early stopping ep3 (best ep1), ~20 mnt/epoch T4, class weights [0,6; 3,0].

### 4.5 Model B (Layer 2, test set weak-label, 922 relevan)
- accuracy **0,9881** · macro-F1 **0,9767**.
- Per-class F1: phishing **0,91** · ewallet 1,00 · malware 0,96 · judi 0,99 · peretasan 1,00 · deepfake 1,00.
- CM 6×6 (baris=gold): phishing [46,0,0,3,0,0] · ewallet [0,55,0,0,0,0] · malware [0,0,22,0,0,0] · judi [6,0,2,741,0,0] · peretasan [0,0,0,0,37,0] · deepfake [0,0,0,0,0,10].
- Loss weighted_ce cukup (focal tak diperlukan). Konfusi utama: phishing↔judi bidireksional.

### 4.6 Ablation late fusion (sweep lengkap: `docs/phase9_fusion_ablation.md`)
- **L1:** recall relevan 0,9674→**0,9761** @0,75:0,25 (8 FN diselamatkan, +9 FP, macro-F1 datar). Rule-based fungsional.
- **L2:** macro-F1 0,9767→0,9747 @0,75:0,25 (−1 phishing). **0,50:0,50=0,9814 (F1_phish 0,9375), stabil 0,45–0,51, TIDAK dipilih** — memilih bobot yang menang di test set = test-set optimization/bias evaluasi. Bobot final **0,75:0,25 (a priori)**.

### 4.7 XAI LIME (`docs/phase9_xai_lime.md`)
- Sinyal domain benar: `apk` +0,907 · `slot`/`judi` +0,225/+0,202 · `deepfake`/`ai` +0,390/+0,297.
- Dua-pola phishing-judi: **A** (idx 25: `nipu`/`penipu` mengalahkan `judol`) = scam umbrella; **B** (idx 558/719: token netral `batubara`/`kehutanan` mengalahkan `judi`) = sinyal judi tersirat. idx 778 = ambiguitas gold.

---

## 5. Hyperparameter + setup

| Item | Nilai | Justifikasi |
|---|---|---|
| max_len | 128 | p99 token = 122 (>128 hanya 0,90%) |
| split | 80/10/10 stratified | seed 42, reproducible |
| fine-tune | PENUH (IndoBERT) | bukan freeze |
| LR | 2e-5 | AdamW |
| batch | 16 | T4 |
| early stopping | patience 2, monitor **val macro-F1** | simpan best checkpoint |
| class weights | balanced inverse-freq | L1 ~[0,6;3,0]; L2 rasio ~70:1 |
| seed | 42 | seluruh pipeline |
| fusion | 0,75 neural : 0,25 rule-based | a priori |

---

## 6. ⚠️ Keterbatasan yang WAJIB dilaporkan (jangan disembunyikan)

1. **Kelas kecil, CI lebar:** deepfake test **n=10**, malware test **n=22** → metrik F1 kelas ini punya interval kepercayaan lebar; **jangan over-generalisasi**.
2. **Gold deepfake overlap 34%** (36/107 populasi relevannya) → gold deepfake kurang independen vs kelas besar.
3. **Metrik model = imitasi weak label Snorkel, BUKAN akurasi vs manusia.** Validasi vs manusia terpisah di gold standard (L1 90,0% / L2 96,9%). Dua angka menjawab pertanyaan berbeda — jaga jelas, jangan campur.
4. **46 disagreement gold tidak direkonsiliasi** — gold berfungsi sebagai validasi via subset sepakat (n=311), bukan test set. Sah secara metodologis, tapi catat eksplisit.
5. **X = snapshot 7 hari**, bukan multi-tahun (Temuan #1).
6. **deepfake 107 relevan = ceiling** dari sumber tersedia (scarcity nyata), bukan gap pipeline.

---

## 7. Diferensiasi SOTA (angkat PROAKTIF di 3.10.5 + BAB 2)

**Mujilahwati et al. 2026 (IJAAS)** memakai **arsitektur inti SAMA** — IndoBERT + BiGRU + BiLSTM serial, F1 **98,98%** — TAPI:
- Tugas: **klasifikasi biner hoax** (bukan 6-vektor ancaman siber).
- Dataset: **berita, 4.312 sampel** (bukan OSINT media sosial 55.300).

**Sikap jujur:** arsitektur neural **BUKAN** novelty Ray. Akui terbuka bahwa tulang punggung neural serupa sudah ada. **Novelty Ray:**
1. Taksonomi **E-ICTT** 6 label (extend Arifman 2026 + deepfake emerging).
2. **Framing diskursus** (bukan deteksi serangan) + speaker role R1–R5.
3. **Weak supervision (Snorkel)** untuk domain langka-data.
4. **Dataset OSINT** X+YouTube berbahasa Indonesia (skala + diversity).
5. **Late fusion** neural + rule-based anchor (pipeline 2-lapis).
6. **XAI (LIME)** untuk interpretabilitas keputusan.

Kontribusi = **rekayasa masalah + data + interpretabilitas + taksonomi**, bukan arsitektur. Ini posisi yang defensible di sidang.

---

## 8. Gaya penulisan

- Bahasa Indonesia akademik; sitasi **APA**.
- **Jangan over-claim.** Laporkan keterbatasan apa adanya (bagian 6). Bila hasil ambigu (mis. Temuan #4 dua-pola), tulis "terkonfirmasi sebagian" — jangan paksa jadi narasi tunggal.
- Bedakan tegas metrik weak-label vs validasi manusia.
- Angka dari file ini / `CONTEXT.md`; bila ragu, verifikasi ke sumber (`data/`, `docs/`, `src/`), jangan mengarang.
