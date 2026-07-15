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

> **✅ Dashboard SELESAI & LIVE** (frontend `https://cyberscope-webapp.vercel.app`, backend `https://twistedregalia-cyberscope-backend.hf.space`). Jalur Prototyping **bukan lagi** perencanaan — **3.11 Deployment / 3.12 Pengembangan Prototype / 3.13 Evaluasi Prototype kini ditulis dari fakta nyata di §9**. (SUS tetap **pending** — butuh responden.)
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
7. **Cold start HF Spaces free tier ~25–60 dtk** (unduh checkpoint + IndoBERT) — dimitigasi badge status + timeout frontend, tapi tetap keterbatasan deployment gratis; laporkan apa adanya di 3.11.
8. **LIME lambat** (opsional, non-blocking; frontend menandai "±30–60 detik") — bukan fitur real-time.
9. **SUS belum dijalankan** — butuh responden manusia (semi-teknis). Jangan tulis skor SUS sebelum ada; 3.13 bagian SUS = rencana/pending.
10. **Temporal monitoring 2013–2026** berasal dari `published_at` mentah → caveat Temuan #1 (X = snapshot 7 hari) & #2 (dua platform beda) TETAP berlaku; jangan klaim tren temporal X dari dashboard.

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
- **3.11–3.13 KINI boleh ditulis** (dashboard live, fakta §9) — tulis apa adanya; **SUS tetap dilaporkan sebagai pending/rencana**, bukan hasil.
- Angka dari file ini / `CONTEXT.md`; bila ragu, verifikasi ke sumber (`data/`, `docs/`, `src/`), jangan mengarang.

---

## 9. Prototype & Deployment — fakta untuk 3.11–3.13 (dashboard SELESAI + live)

> Semua fakta di sini **terverifikasi langsung** (dari `monitoring.json`, backend `README.md`/`requirements.txt`, dan URL live: `curl /health` 200 + uji klasifikasi di browser) saat sesi pembangunan/deploy. Bab 3.11–3.13 ditulis dari sini. **SUS tetap pending.**

### 9.1 Ikhtisar & URL live
- **Nama produk:** CyberScope. **Tipe:** dashboard klasifikasi on-demand + monitoring (Tipe 1, dua halaman).
- **Frontend (Vercel):** `https://cyberscope-webapp.vercel.app`
- **Backend (HF Spaces):** `https://twistedregalia-cyberscope-backend.hf.space`
- **Dua-jalur data (penting):** Monitoring (`/`) membaca **file statis** pra-agregat dari CDN Vercel — tak memanggil model saat load (nilai langsung terlihat, tanpa cold-start, tetap hidup walau Space tidur). Klasifikasi (`/klasifikasi`) memanggil **API live** backend.

### 9.2 Arsitektur & stack (untuk 3.12)
**Frontend:** Next.js 16.2.10 (App Router) · TypeScript · Tailwind CSS v4 · Recharts 3.9. Sistem desain **"Dub"** (light editorial, hairline border 1px `#e5e5e5`, satu aksen electric-blue `#2563eb`, radius terkunci). **Dark mode** via override nilai token pada `:root[data-theme="dark"]` (komponen tak ditulis ulang). Font Inter + Geist Mono (`next/font`).

**Backend:** FastAPI (3 endpoint) dijalankan lewat `space_app.py` (HF Spaces **SDK Gradio**, gratis; Docker SDK kini Pro-only). Pipeline inferensi 2-lapis: `text → clean_text → Model A (relevansi) → [tidak relevan → STOP] → Model B (6 vektor) + anchor → late fusion 0,75 neural : 0,25 rule-based → label + confidence`. **LIME menjelaskan komponen neural murni Model B.** Deps inti: torch, transformers≥4.30, lime, emoji, Sastrawi, fastapi, uvicorn, gradio, `spaces`.

**Struktur repo:** `dashboard/frontend/` (Next.js) + `dashboard/backend/` (`app/main.py`, `app/pipeline.py`, `app/schemas.py`, `scripts/build_monitoring.py`, `scripts/sanity_check.py`, `space_app.py`). Kelas model + preprocessing + anchor **di-reuse dari `src/`** (bukan latih ulang).

### 9.3 Dua halaman + fitur (untuk 3.12)
**`/` Monitoring** (dari PREDIKSI model, file statis):
- Kartu ringkas: total baris · relevan · rentang tanggal.
- **Funnel relevansi** (total → relevan Model A → komposisi 6 vektor Model B) — menceritakan pipeline 2-lapis.
- **Distribusi 6 vektor** (bar horizontal, klik → drill-down).
- **Proporsi platform** YouTube vs X per vektor (100%-stacked).
- **Tren waktu** (line, kondisional bila ≥3 periode berbeda).
- **Tabel detail 6 vektor** (jumlah · % · YouTube% · X%; aksesibel, drill-down).
- **Drill-down:** klik vektor → contoh komentar terklasifikasi ke vektor itu.

**`/klasifikasi` Klasifikasi on-demand** (API live):
- Input: **contoh siap-klik** (7 contoh, termasuk 1 off-topic) ATAU **tempel teks**.
- Hasil: label vektor (dapat dibaca, bukan indeks) + **confidence** + **bar probabilitas 6 kelas**.
- **Gate Model A:** bila tidak relevan → berhenti, tampil "tidak relevan", tak menampilkan vektor.
- **LIME opsional** (default mati, tombol terpisah): highlight token berbobot (+ mendukung / − menentang), non-blocking, ditandai lambat.
- **Badge status backend:** ping `/health` saat halaman dibuka (memeriksa → online/offline, sekaligus membangunkan Space); UX cold-start; pesan error ramah (timeout/jaringan/HTTP).

**Prinsip integritas UI:** tak fabrikasi angka — data hilang → **empty state**; fixture dev → banner **"DATA CONTOH"** (kini nonaktif karena data nyata sudah dipasang).

### 9.4 Deployment (untuk 3.11)
- **Frontend → Vercel:** build statis (5 route prerender) + CDN global. Env **build-time** `NEXT_PUBLIC_API_BASE_URL=<url-space>` + `NEXT_PUBLIC_USE_MOCK=false` (persisten di project). Domain produksi publik `cyberscope-webapp.vercel.app`.
- **Backend → HF Spaces (SDK Gradio, free tier):** checkpoint (~484 MB ×2) di **HF model repo privat**, diunduh saat startup via `hf_hub_download` (di luar Git Space); IndoBERT base terunduh saat instansiasi; model dimuat **sekali** saat startup.
- **`GET /health`** (dari sanity nyata `scripts/sanity_check.py`): `models_loaded=true`, `model_a_f1=0,9686`, `model_b_f1=0,9747`.
- **Cold start ~25–60 dtk** (unduh checkpoint + IndoBERT) → dimitigasi badge health frontend + timeout (classify 30 dtk, explain 120 dtk).
- **Latensi classify teramati ~239 ms (warm)** — jauh di bawah estimasi CPU 1–3 dtk pada dokumen desain → **indikasi inferensi GPU-backed (ZeroGPU** via paket `spaces`). *(Konfirmasi tier hardware Space bila butuh angka pasti di tulisan.)*
- **CORS:** backend izinkan `http://localhost:3000` + regex `https://.*\.vercel\.app$` (Gradio `strict_cors=False` juga permisif).
- **Integrasi terverifikasi end-to-end** di URL live (lihat 9.6).

### 9.5 Output monitoring NYATA — prediksi model (INTEGRITAS, untuk 3.12/3.13)
Batch inference Model A+B atas seluruh **55.300** baris → **9.748 diprediksi relevan** (Model A), lalu Model B + fusion. **Ini prediksi model, BUKAN weak label Snorkel.**

| Vektor | Monitoring (prediksi model) | (band.) Snorkel §4.2 |
|---|---:|---:|
| judi_online_pinjol | **7.645** (78,4%) | 7.486 |
| phishing_rekayasa_sosial | **704** (7,2%) | 492 |
| penipuan_ewallet_qris | **549** (5,6%) | 548 |
| peretasan_pencurian_identitas | **425** (4,4%) | 365 |
| malware_apk | **316** (3,2%) | 214 |
| deepfake_penipuan_ai | **109** (1,1%) | 107 |
| **Total relevan** | **9.748** | 9.212 |

- **Proporsi platform (prediksi):** ewallet ~99% X · judi ~96% YouTube · peretasan ~85% X · malware ~86% YouTube · phishing ~78% YouTube · deepfake ~56% YouTube.
- `date_range` monitoring **2013-05 .. 2026-06** (dari `published_at` mentah; caveat platform §3 Temuan #1/#2 tetap berlaku).

> **WAJIB di tulisan:** jangan tertukar angka monitoring (prediksi) dengan Snorkel (weak label) atau test set — ketiganya menjawab pertanyaan berbeda (lihat 9.7).

### 9.6 Evaluasi Prototype (untuk 3.13)
- **Blackbox testing (terverifikasi di URL live):** Monitoring memuat data nyata (tanpa banner DATA CONTOH; 11 surface chart render); classify per vektor → label + confidence + 6 bar; gate "tidak relevan" untuk off-topic; LIME → token berbobot; dark mode berfungsi; badge backend **online**; **nol error konsol**.
- **Uji data (contoh per vektor):** teks contoh → label + confidence, mis. contoh judi → **"Judi Online & Pinjol" 99,1%** (latensi ~239 ms); off-topic → "tidak relevan". Sarankan tabel uji **1 contoh/vektor + kasus negatif** di tulisan.
- **SUS (System Usability Scale) — PENDING:** butuh **responden manusia**, profil **semi-teknis** (mahasiswa informatika/dosen), **min 5, ideal 12–20**. Bottleneck non-teknis → amankan responden lebih awal. **Jangan tulis skor SUS sebelum dijalankan.**

### 9.7 Integritas dashboard (jangan dilanggar di 3.11–3.13)
- **Tiga angka "relevan" berbeda peran — jangan tertukar:**
  - **9.748** = prediksi Model A atas 55.300 → isi **monitoring** dashboard.
  - **9.212** = weak label Snorkel → label dataset training (§4.2).
  - **922** = subset test set Layer-2 → metrik model (§4.5).
- Monitoring = **prediksi model**, bukan Snorkel. Metrik `/health` dari **sanity nyata**, bukan tebakan.
- **Speaker Role R1–R5 TIDAK ada** di dashboard v1 (model tak memprediksinya; jangan tampilkan seolah ada).
- Tulis 3.11–3.13 apa adanya; **SUS belum ada → laporkan sebagai rencana/pending**, bukan hasil.
