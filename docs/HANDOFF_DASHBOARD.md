# HANDOFF — Sesi Pembuatan Dashboard (Prototyping)

> Handoff untuk sesi dashboard (kemungkinan di repo/direktori terpisah). Baca ini + `CONTEXT.md` §4a/§4b sebelum mulai. Kode asal ada di repo **PI2** (branch `feat/thesis-writing`).

---

## 1. Apa itu proyek ini

Klasifikasi otomatis **diskursus publik tentang vektor ancaman siber** di media sosial Indonesia (X + YouTube). **BUKAN** mendeteksi serangan langsung — mengklasifikasikan konten yang *membicarakan* ancaman (laporan korban, edukasi, promosi pelaku, diskusi netral). Skripsi S1, peneliti: Ray.

**Taksonomi E-ICTT v2.1 (6 label):**
| Label | Definisi singkat |
|---|---|
| `phishing_rekayasa_sosial` | Penipuan via rekayasa sosial: OTP, link palsu, mengatasnamakan institusi |
| `penipuan_ewallet_qris` | Modus e-wallet/QRIS: saldo terkuras, QR palsu, refund scam |
| `malware_apk` | File APK jahat (undangan/kurir/tilang), sniffing, install app berbahaya |
| `judi_online_pinjol` | Judi online (slot/gacor/maxwin) + pinjol ilegal + teror DC |
| `peretasan_pencurian_identitas` | Akun diretas/dibajak, kebocoran data, jual-beli identitas, SIM swap |
| `deepfake_penipuan_ai` | Deepfake, voice cloning, penipuan berbasis AI (tokoh publik, suara keluarga) |

**Speaker role (R1–R5, dimensi terpisah, bukan label utama):** R1 laporan korban · R2 kesaksian kasus orang lain · R3 peringatan/edukasi · R4 promosi/tindakan pelaku · R5 diskusi netral/jurnalistik.

---

## 2. Arsitektur inference (pipeline 2-lapis)

```
teks mentah
  → preprocessing (text_clean)
  → Model A (Layer 1, biner: relevan / tidak_relevan)
       └─ jika tidak_relevan → STOP
  → Model B (Layer 2, 6 vektor)  [+ anchor_score dari rule-based]
  → late fusion 0,75 neural : 0,25 rule-based
  → label vektor final
```

- **Layer 1 (Model A):** filter relevansi. Late fusion di L1 **menaikkan recall relevan** (0,9674→0,9761) — anchor = safety net di sini.
- **Layer 2 (Model B):** klasifikasi 6 vektor. Late fusion di L2 **redundan** (dipertahankan untuk interpretabilitas; neural sudah dominan).

---

## 3. Kelas model + cara memuat checkpoint

**Kelas arsitektur (identik untuk load):**
- `TripleHybridLayer1` — `src/phase9_model_a_layer1.py` (`make_model_class()`), classifier 2 kelas
- `TripleHybridLayer2` — `src/phase9_model_b_layer2.py` (`make_model_class()`), classifier 6 kelas
- Arsitektur: `IndoBERT-base-p1` (fine-tune penuh) → BiGRU(768→256 bidir) → BiLSTM(512→128 bidir) serial → masked-mean pool → dropout → Linear.

**PENTING — checkpoint disimpan sebagai `state_dict`, BUKAN objek model:**
```python
model = make_model_class()()          # instansiasi arsitektur
model.load_state_dict(torch.load("model_a_layer1_best.pt", map_location=device))
model.eval()
# JANGAN torch.load(model) langsung — yang tersimpan hanya bobot (state_dict).
```

**Checkpoint (TIDAK di Git — ada di Kaggle output / lokal Ray):**
| File | Ukuran | Sanity check setelah load |
|---|---|---|
| `model_a_layer1_best.pt` | ~470 MB | test macro-F1 ≈ **0,968** (recall relevan ≈ 0,967) |
| `model_b_layer2_best.pt` | ~470 MB | test macro-F1 ≈ **0,977** |

> **WAJIB sanity check setelah load** sebelum dipakai — bila macro-F1 tidak mendekati target, checkpoint/arsitektur tidak selaras (cek nama atribut layer, LABEL2ID order, max_len).

---

## 4. Preprocessing yang HARUS direplikasi

Input model = kolom **`text_clean`** dari `src/phase6_preprocess.py`:
- lowercase (case folding)
- URL → `[URL]`, `@user` → `[USER]`, hashtag → teks (# dilepas)
- emoji emosi → `[EMOSI_SEDIH/MARAH/UANG/TAKUT/WASPADA]`, emoji dekoratif dibuang
- slang cybercrime **dipertahankan** (pinjol, gacor, maxwin, qris) — JANGAN normalisasi
- **TIDAK** buang stopword, **TIDAK** stemming (BERT butuh konteks penuh)

**Tokenizer:** `indobenchmark/indobert-base-p1`, **`max_len=128`** (p99 token = 122; justifikasi di CONTEXT §Temuan #9).

Contoh transformasi konkret: `docs/phase6_preprocessing_examples.md`.

---

## 5. Rule-based (untuk late fusion)

`src/anchor_patterns.py` (v1.1) — `detect_vector_hints(text)` → `{vektor: jumlah_match}`.
- **anchor_score Layer 2:** share bukti per vektor = `count(v)/Σcount` (0 semua bila tak ada anchor → defer ke neural).
- **anchor_score Layer 1:** sinyal satu-arah `has_anchor → [tidak_relevan=0, relevan=1]`, else `[0,0]`.
- Fusion: `skor(v) = 0,75·P_neural(v) + 0,25·anchor(v)`.
- Logika lengkap: `src/phase9_late_fusion.py`.

---

## 6. Data tersedia (di repo PI2)

- `data/weak_labeled_dataset_v2.csv` — 55.300 baris, **9.212 relevan** (weak label Snorkel + metadata)
- `data/splits/` — split 80/10/10 (layer1_{train,val,test}, layer2_{train,val,test}) + `_split_manifest.json`
- Gold standard 357 sampel (`data/gold_annotation_sheet_*.csv`, `data/gold_key_HIDDEN.csv`) — JANGAN sebar key ke publik
- Distribusi relevan per vektor: judi 7.486 · ewallet 548 · phishing 492 · peretasan 365 · malware 214 · deepfake 107

---

## 7. Yang bisa divisualisasikan

- Distribusi 6 vektor (bar chart; tunjukkan imbalance judi dominan vs deepfake floor)
- Distribusi platform (YouTube 51.739 / X 3.561), speaker role
- Metrik model per layer (accuracy, macro-F1, per-class P/R/F1)
- Confusion matrix Model B 6×6 (`docs/phase9_xai_lime.md` §1 & `docs/phase9_fusion_ablation.md`)
- Temuan XAI LIME (token pendorong per vektor; dua-pola phishing-judi) — `docs/phase9_xai_lime.md`
- Kurva ablation fusion L1/L2 — `docs/phase9_fusion_ablation.md`

---

## 8. ⚠️ Pertanyaan lingkup yang BELUM diputuskan (WAJIB diputuskan di awal sesi dashboard)

**Apakah dashboard melakukan inference LIVE atau hanya visualisasi dataset?**
- **Inference live** → butuh checkpoint (~940 MB total) + PyTorch + transformers + tokenizer + replikasi preprocessing + anchor_patterns. Berat, tapi bisa klasifikasi teks baru.
- **Visualisasi dataset saja** → cukup baca CSV (`weak_labeled_dataset_v2.csv`, docs/*.md). Ringan, tak butuh model.

Keputusan ini menentukan **seluruh stack dependensi**. **= isi bagian 3.2 Analisis Kebutuhan.** Putuskan SEBELUM menulis kode dashboard.

---

## 9. Catatan integritas

- Bila dashboard dibuat di **repo terpisah**: catat **commit hash PI2** asal snapshot kode (mis. hasil `git rev-parse HEAD` di PI2 saat menyalin) di README dashboard.
- Perlakukan salinan kode (`phase9_model_*.py`, `anchor_patterns.py`, `phase6_preprocess.py`) sebagai **deployment artifact yang DIBEKUKAN** — jangan edit logika di salinan; bila model berubah di PI2, re-sync dengan hash baru.
- Checkpoint bukan milik Git — dokumentasikan sumbernya (Kaggle notebook output / path lokal Ray) di README dashboard.
