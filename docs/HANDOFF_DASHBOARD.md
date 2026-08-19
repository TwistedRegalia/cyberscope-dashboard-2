# HANDOFF — Sesi Pembuatan Dashboard (Prototyping)

> ⚠️ **Dokumen historis (Jul 2026).** Dashboard **sudah dibangun, di-deploy, dan dievaluasi** — dokumen ini kini menjelaskan **kenapa lingkupnya dipilih begitu**, bukan pekerjaan yang menunggu. Status & fakta terkini: `CONTEXT.md` §4c dan `docs/HANDOFF_WRITING.md` §9.
>
> Handoff untuk sesi dashboard di **`PI2/dashboard/`** (subdirektori repo ini, bukan repo terpisah). Baca ini + `CONTEXT.md` §4a/§4b/§4c sebelum mulai.

---

## 1. Apa itu proyek ini

Klasifikasi otomatis **diskursus publik tentang vektor ancaman siber** di media sosial Indonesia (X + YouTube). **BUKAN** mendeteksi serangan langsung — mengklasifikasikan konten yang *membicarakan* ancaman (laporan korban, edukasi, promosi pelaku, diskusi netral). Skripsi S1, peneliti: Ray.

**Taksonomi E-ICTT v2.1 (6 label):**
| Label | Definisi singkat |
|---|---|
| `phishing_rekayasa_sosial` | Penipuan via rekayasa sosial: OTP, link palsu, telepon mengatasnamakan institusi/bank |
| `penipuan_ewallet_qris` | Modus e-wallet/QRIS: saldo terkuras, QR palsu/tempel, scan-balik/refund scam |
| `malware_apk` | File APK jahat (undangan/kurir/tilang/paket), sniffing, install app berbahaya |
| `judi_online_pinjol` | Judi online (slot/gacor/maxwin/togel) + pinjol ilegal + teror debt collector |
| `peretasan_pencurian_identitas` | Akun diretas/dibajak, kebocoran data, jual-beli identitas/KTP, SIM swap |
| `deepfake_penipuan_ai` | Deepfake, voice cloning, penipuan berbasis AI (tokoh publik, suara keluarga) |

**Speaker role (R1–R5, dimensi terpisah, BUKAN label utama):** R1 laporan korban · R2 kesaksian kasus orang lain · R3 peringatan/edukasi · R4 promosi/tindakan pelaku · R5 diskusi netral/jurnalistik.

**⚠️ Aturan jual-beli → `tidak_relevan` (Keputusan C, `docs/phase7_snorkel_report.md`):** penipuan **jual-beli komersial generik** (thrift, tiket, barang) di-route ke `tidak_relevan` oleh LF negatif — supaya kelas phishing tak jadi keranjang semua penipuan (Temuan #5). **Nuansa:** jual-beli **data/KTP/rekening/akun** TETAP anchor `peretasan_pencurian_identitas` (relevan). Yang dibuang = jual-beli marketplace umum tanpa anchor vektor.

---

## 2. Lingkup FINAL (isi 3.2 Analisis Kebutuhan)

**Tipe 1 — klasifikasi on-demand + monitoring. Hanya dua kemampuan:**
1. **Monitoring** — visualisasi distribusi 6 vektor dari **prediksi model** atas dataset (detail §3.1).
2. **Klasifikasi on-demand** — contoh siap-klik / tempel teks → pipeline penuh → vektor + confidence, XAI opsional (detail §3.2).

**DIKELUARKAN dari lingkup (keputusan final, jujur untuk 3.2):**
- **TANPA scraping-triggered / tombol ambil data.** Menyulitkan pengguna + **rapuh di HF Spaces** (scraping X butuh `auth_token` cookie yang kedaluwarsa & berisiko suspend; YouTube API berkuota — lihat §9). Data monitoring = hasil batch inference statis, bukan pengambilan live.
- **TANPA upload CSV.** Kurang sejalan dengan klaim "klasifikasi otomatis" dan menambah hambatan bagi pengguna non-harian.

---

## 3. Desain & Alur Pengguna

Dua halaman. Prinsip utama: **nilai terlihat saat dibuka** (monitoring langsung terisi tanpa input), umpan balik cepat, hasil dapat dipahami responden **semi-teknis** (mahasiswa informatika, dosen).

### 3.1 Halaman utama — Monitoring (default saat buka)

Menampilkan gambaran dataset dari **PREDIKSI MODEL** (Model A+B), **bukan label Snorkel** — koheren dengan klaim "klasifikasi otomatis".

- **Distribusi 6 vektor** dari hasil prediksi (bar/donut), + **proporsi platform** (YouTube/X), + **tren waktu** bila kolom tanggal tersedia.
- **Drill-down sederhana:** klik satu vektor → **panel expand** berisi contoh komentar terklasifikasi ke vektor itu (bukan halaman baru yang kompleks).

**Prasyarat (langkah persiapan, BUKAN runtime):** jalankan **batch inference Model A+B SEKALI** atas dataset (9.212 relevan dari 55.300) → simpan **prediksi + confidence** ke file (mis. `data/dashboard_predictions.parquet`/`.csv`) → dashboard **membaca file** itu. Monitoring tak menjalankan model saat halaman dibuka; hanya panel klasifikasi (§3.2) yang memanggil model live.

### 3.2 Panel Klasifikasi (on-demand)

- **Input fleksibel — hilangkan hambatan:** pengguna memilih **contoh teks siap-klik** ATAU **menempel teks sendiri**.
- Klik → pipeline penuh (§4) → **hasil model**: vektor + **confidence**, label dapat dibaca (bukan indeks kelas).
- **Tombol XAI opsional:** LIME `num_samples=100–150`, **indikator loading**, ~30–60 dtk. Jangan blok UI; jangan jalankan otomatis (default mati, klik saat perlu).

### 3.3 Speaker Role R1–R5 — DITUNDA (bukan di v1)

⚠️ **Model A+B TIDAK memprediksi speaker role** — hanya relevansi (L1) + 6 vektor (L2). Menampilkan R1–R5 butuh salah satu:
- (a) **melatih model baru** khusus speaker role, atau
- (b) menampilkan dari **data terlabel** dengan **catatan eksplisit** bahwa sumbernya berbeda (bukan prediksi model dashboard).

Keputusan **ditunda**. **Dashboard v1 = 6 vektor saja.** Speaker role = kemungkinan ekstensi, bukan kebutuhan v1.

### 3.4 Kebutuhan untuk 3.2/3.3 tesis

**Fungsional:**
1. Visualisasi **distribusi prediksi model** per vektor (+ proporsi platform, tren waktu bila ada).
2. **Drill-down** vektor → contoh komentar terklasifikasi.
3. **Klasifikasi on-demand** (contoh siap-klik / tempel teks) → vektor + confidence.
4. **XAI opsional** (LIME) per klasifikasi.
5. **Contoh siap-pakai** untuk menghilangkan hambatan input.

**Non-fungsional (diarahkan ke SUS tinggi, responden semi-teknis):**
- **Nilai tanpa input awal** — monitoring terisi begitu halaman dibuka.
- **Respons cepat** — klasifikasi <3 dtk (XAI dikecualikan; opsional & ditandai lama).
- **Antarmuka jelas** untuk pengguna non-harian — navigasi eksplisit, label & hasil mudah dipahami.

---

## 4. Arsitektur inference (pipeline 2-lapis)

```
teks mentah
  → preprocessing (text_clean)
  → Model A (Layer 1, biner: relevan / tidak_relevan)
       └─ jika tidak_relevan → STOP (tampilkan "tidak relevan")
  → Model B (Layer 2, 6 vektor)  [+ anchor_score dari rule-based]
  → late fusion 0,75 neural : 0,25 rule-based
  → label vektor final + confidence
```

- **Layer 1:** filter relevansi. Fusion di L1 menaikkan recall relevan (0,9674→0,9761) — anchor = safety net.
- **Layer 2:** 6 vektor. Fusion di L2 redundan (dipertahankan untuk interpretabilitas; neural dominan).

---

## 5. Kelas model + cara memuat checkpoint

- `TripleHybridLayer1` — `src/phase9_model_a_layer1.py` (`make_model_class()`), classifier 2 kelas.
- `TripleHybridLayer2` — `src/phase9_model_b_layer2.py` (`make_model_class()`), classifier 6 kelas.
- Arsitektur: `IndoBERT-base-p1` (fine-tune penuh) → BiGRU(768→256 bidir) → BiLSTM(512→128 bidir) serial → masked-mean pool → dropout → Linear.

**PENTING — checkpoint = `state_dict`, BUKAN objek model:**
```python
model = make_model_class()()
model.load_state_dict(torch.load("checkpoints/model_a_layer1_best.pt", map_location=device))
model.eval()
# JANGAN torch.load(model) — yang tersimpan hanya bobot.
```

**Checkpoint (TIDAK di Git — dari Kaggle output / lokal Ray):**
| File | Ukuran | Sanity check WAJIB setelah load |
|---|---|---|
| `model_a_layer1_best.pt` | ~470 MB | test macro-F1 ≈ **0,968** (recall relevan ≈ 0,967) |
| `model_b_layer2_best.pt` | ~470 MB | test macro-F1 ≈ **0,977** |

> Simpan checkpoint di folder ber-**`.gitignore`** (mis. `dashboard/checkpoints/`). **WAJIB sanity check** pada test set setelah load — bila macro-F1 meleset, arsitektur/checkpoint tak selaras (cek nama atribut layer, LABEL2ID order, max_len). Jangan lanjut inference sebelum lolos.

---

## 6. Preprocessing yang WAJIB direplikasi

Input model = kolom **`text_clean`** dari `src/phase6_preprocess.py`:
- lowercase · URL → `[URL]` · `@user` → `[USER]` · hashtag → teks (# dilepas) · emoji emosi → `[EMOSI_SEDIH/MARAH/UANG/TAKUT/WASPADA]`, emoji dekoratif dibuang.
- slang cybercrime **dipertahankan** (pinjol, gacor, maxwin, qris) — JANGAN normalisasi.
- **TIDAK** buang stopword, **TIDAK** stemming.

**Tokenizer:** `indobenchmark/indobert-base-p1`, **`max_len=128`**. Contoh transformasi: `docs/phase6_preprocessing_examples.md`.

---

## 7. Rule-based (untuk fusion)

`src/anchor_patterns.py` (v1.1) — `detect_vector_hints(text)` → `{vektor: jumlah_match}`.
- anchor_score L2 = share bukti `count(v)/Σcount` (0 semua → defer neural).
- anchor_score L1 = satu-arah `has_anchor → [tidak_relevan=0, relevan=1]`, else `[0,0]`.
- Fusion: `skor(v) = 0,75·P_neural(v) + 0,25·anchor(v)`. Logika: `src/phase9_late_fusion.py`.

---

## 8. Data + bahan visualisasi

- `data/weak_labeled_dataset_v2.csv` — 55.300 baris, **9.212 relevan**.
- `data/splits/` — split 80/10/10. Gold standard 357 (`data/gold_*.csv`; JANGAN sebar key).
- **Distribusi 6 vektor (relevan, LABEL LEMAH Snorkel):** judi 7.486 · ewallet 548 · phishing 492 · peretasan 365 · malware 214 · deepfake 107. Platform: YouTube 51.739 / X 3.561.
- **File prediksi dashboard (dibuat SEKALI, §3.1):** batch inference Model A+B atas 9.212 relevan → simpan vektor + confidence → **sumber data monitoring**. Bedakan dari angka distribusi di atas: monitoring menampilkan **prediksi model**, bukan label lemah Snorkel.
- Metrik model, confusion matrix Model B 6×6, kurva ablation fusion → `docs/phase9_fusion_ablation.md`.
- Temuan XAI (token per vektor, dua-pola phishing-judi) → `docs/phase9_xai_lime.md`.

---

## 9. Kendala non-fungsional (input untuk 3.2)

| Kendala | Nilai / mitigasi |
|---|---|
| Inference CPU | ~1–3 dtk per teks (Model A + B) |
| Memori | ~3 GB saat kedua model dimuat bersamaan |
| **LIME lambat di CPU** | 2–5 menit @ `num_samples=500` → **turunkan ke 100–150**, jadikan **tombol opsional terpisah** dengan **indikator progres** (jangan blok UI) |
| Scraping X | butuh `auth_token` manual (cookie kedaluwarsa; risiko suspend) → alasan **TANPA scraping-triggered** (§2) |
| YouTube API | kuota harian → memperkuat keputusan data monitoring = batch statis |

---

## 10. Untuk 3.13 Evaluasi Prototype — ✅ SELESAI

- **Blackbox testing** + **uji data** per vektor: selesai, diuji langsung di URL live (Tabel 3.16 di naskah).
- **SUS: selesai — 15 responden semi-teknis, rata-rata 81,33** (median 82,50 · SD 7,13 · rentang 67,5–90,0), kategori *Excellent* & acceptable. Angka lengkap + catatan keterbatasan: `docs/HANDOFF_WRITING.md` §9.6.

> Dokumen ini = **riwayat keputusan desain** (kenapa lingkupnya begini). Untuk fakta hasil yang dipakai menulis, rujuk `docs/HANDOFF_WRITING.md` §9.

---

## 11. Catatan integritas

- Karena dashboard di **subdirektori** `PI2/dashboard/`: impor langsung `from src...`, tak perlu snapshot commit-hash antar-repo. Checkpoint tetap di luar Git (dokumentasikan sumbernya di `dashboard/README`).
- Bagian tesis **3.11 Deployment, 3.12 Pengembangan Prototype, 3.13 Evaluasi Prototype** ditulis **SETELAH** dashboard selesai — jangan tulis seolah sudah dikerjakan.
