# HANDOFF — Sesi Pembuatan Dashboard (Prototyping)

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

## 2. Lingkup yang SUDAH diputuskan (isi 3.2 Analisis Kebutuhan)

**Tipe 1 + batch manual — TANPA penjadwal otomatis:**
1. **Klasifikasi on-demand** — pengguna menempel teks → pipeline penuh → label + confidence.
2. **Visualisasi dataset** — distribusi, metrik, confusion matrix, XAI.
3. **Tombol ambil data manual** — trigger scraping (bukan scheduler).

**Alasan tanpa otomasi (jujur, masuk 3.2):** scraping X butuh `auth_token` (cookie sesi — kedaluwarsa, tak bisa diperbarui otomatis, risiko suspend); YouTube API punya kuota harian. Manual-triggered lebih andal & jujur daripada scheduler rapuh.

---

## 3. Arsitektur inference (pipeline 2-lapis)

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

## 4. Kelas model + cara memuat checkpoint

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

## 5. Preprocessing yang WAJIB direplikasi

Input model = kolom **`text_clean`** dari `src/phase6_preprocess.py`:
- lowercase · URL → `[URL]` · `@user` → `[USER]` · hashtag → teks (# dilepas) · emoji emosi → `[EMOSI_SEDIH/MARAH/UANG/TAKUT/WASPADA]`, emoji dekoratif dibuang.
- slang cybercrime **dipertahankan** (pinjol, gacor, maxwin, qris) — JANGAN normalisasi.
- **TIDAK** buang stopword, **TIDAK** stemming.

**Tokenizer:** `indobenchmark/indobert-base-p1`, **`max_len=128`**. Contoh transformasi: `docs/phase6_preprocessing_examples.md`.

---

## 6. Rule-based (untuk fusion)

`src/anchor_patterns.py` (v1.1) — `detect_vector_hints(text)` → `{vektor: jumlah_match}`.
- anchor_score L2 = share bukti `count(v)/Σcount` (0 semua → defer neural).
- anchor_score L1 = satu-arah `has_anchor → [tidak_relevan=0, relevan=1]`, else `[0,0]`.
- Fusion: `skor(v) = 0,75·P_neural(v) + 0,25·anchor(v)`. Logika: `src/phase9_late_fusion.py`.

---

## 7. Data + bahan visualisasi

- `data/weak_labeled_dataset_v2.csv` — 55.300 baris, **9.212 relevan**.
- `data/splits/` — split 80/10/10. Gold standard 357 (`data/gold_*.csv`; JANGAN sebar key).
- **Distribusi 6 vektor (relevan):** judi 7.486 · ewallet 548 · phishing 492 · peretasan 365 · malware 214 · deepfake 107. Platform: YouTube 51.739 / X 3.561.
- Metrik model, confusion matrix Model B 6×6, kurva ablation fusion → `docs/phase9_fusion_ablation.md`.
- Temuan XAI (token per vektor, dua-pola phishing-judi) → `docs/phase9_xai_lime.md`.

---

## 8. Kendala non-fungsional (input untuk 3.2)

| Kendala | Nilai / mitigasi |
|---|---|
| Inference CPU | ~1–3 dtk per teks (Model A + B) |
| Memori | ~3 GB saat kedua model dimuat bersamaan |
| **LIME lambat di CPU** | 2–5 menit @ `num_samples=500` → **turunkan ke 100–150**, jadikan **tombol opsional terpisah** dengan **indikator progres** (jangan blok UI) |
| Scraping X | butuh `auth_token` manual (cookie kedaluwarsa; risiko suspend) |
| YouTube API | kuota harian |

---

## 9. Untuk 3.13 Evaluasi Prototype

- **Blackbox testing** + **uji data** (klasifikasi teks contoh per vektor).
- **SUS (System Usability Scale)** butuh **responden manusia**: **min 5, ideal 12–20**. → **Ray perlu mengamankan responden sejak awal** (rekrut + jadwal), karena ini bottleneck non-teknis yang tak bisa dikejar di akhir.

---

## 10. Catatan integritas

- Karena dashboard di **subdirektori** `PI2/dashboard/`: impor langsung `from src...`, tak perlu snapshot commit-hash antar-repo. Checkpoint tetap di luar Git (dokumentasikan sumbernya di `dashboard/README`).
- Bagian tesis **3.11 Deployment, 3.12 Pengembangan Prototype, 3.13 Evaluasi Prototype** ditulis **SETELAH** dashboard selesai — jangan tulis seolah sudah dikerjakan.
