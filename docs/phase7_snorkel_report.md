# Phase 7 — Snorkel Weak Supervision: Laporan Progres

**Penelitian:** Klasifikasi Otomatis Diskursus Vektor Ancaman Siber (E-ICTT v2.1)
**Fase:** 7 (Weak Supervision Labeling) — pipeline penuh terakit di data saat ini
**Input:** `data/preprocessed_dataset.csv` (48.496 baris)
**Output:** `data/weak_labeled_dataset.csv` (48.496 baris, 13 kolom) → input Phase 8

---

## 1. Keputusan Metodologis Sesi Ini

| # | Keputusan | Pilihan |
|---|-----------|---------|
| A | Agregator | **LabelModel (utama) + formula manual (baseline)** |
| B | Arsitektur Layer 2 | **Per-vektor binary LabelModel + tie-break hierarki** |
| C | Penipuan jual-beli online | **`tidak_relevan`** (jaga phishing bersih) |
| D | Input LF | **`text_clean`** (bentuk informal dipertahankan; `text_normalized` untuk IndoBERT) |
| E | Urutan build | LF presisi 6 vektor → Layer 1 **diturunkan** dari anchor presisi |
| F | Scraping 3 vektor lemah | Jalan **paralel**; pipeline dirakit di data saat ini |

---

## 2. Arsitektur Pipeline

```
text_clean
   │
   ├─ 46 LF vektor (precise Tier1/2 + discovery Tier3) ─┐
   ├─ 4 LF negatif (jual-beli, emosional, off-topic,    │
   │   generik-siber)                                   │
   │                                                    ▼
   │                              Per-vektor binary LabelModel ×6
   │                                    → P(vektor) tiap baris
   │                                                    │
   │   Tie-break hierarki: malware>deepfake>ewallet>    │
   │   phishing>peretasan>judi  (prefer kandidat presisi)│
   │                                                    ▼
   │   Layer 1 (relevan) bila: anchor PRESISI nyala     │
   │   ATAU (discovery & P≥0.50 & bukan jual-beli/noise)│
   │                            → threshold P≥0.40      │
   ▼                                                    ▼
layer1_label ∈ {relevan, tidak_relevan}    layer2_label ∈ 6 vektor (jika relevan)
                                            speaker_role ∈ R1–R5 (metadata kasar)
                                            lm_confidence, manual_confidence
```

**Catatan desain:**
- Tier 1/2/3 dipakai sebagai **disiplin desain LF** (mana yang dipercaya presisi), bukan confidence hard-coded. LabelModel belajar akurasi tiap LF dari pola agreement.
- Relevansi Layer 1 **digerakkan anchor presisi**, bukan discovery — supaya noise jual-beli/scam-generik tidak masuk `relevan` (Temuan #5).
- LF discovery (reuse anchor v1.1, morfologi SUF) memulihkan recall + memberi overlap antar-LF agar LabelModel per-vektor bisa belajar.

---

## 3. Inventory Labeling Functions

Total **50 LF** (46 vektor + 4 negatif):

| Vektor | Tier-1 | Tier-2 | Tier-3/disc | Σ |
|--------|:--:|:--:|:--:|:--:|
| phishing_rekayasa_sosial | 5 | 3 (incl. anchor-gate) | 1 | 9 |
| judi_online_pinjol | 5 | 2 | 1 | 8 |
| penipuan_ewallet_qris | 3 | 2 | 1 | 6 |
| malware_apk | 3 | 2 | 1 | 6 |
| peretasan_pencurian_identitas | 4 | 2 | 1 | 7 |
| deepfake_penipuan_ai | 3 | 2 | — | 5 |
| **Negatif (Layer 1)** | — | — | — | 4 |

Phishing **strict**: narasi korban hanya vote phishing bila ada anchor kredensial/institusi/soceng; anchor-gate memulihkan recall presisi-aman. Jual-beli tanpa anchor → di-override LF negatif → `tidak_relevan`.

---

## 4. Hasil — Distribusi Final

**Layer 1:** relevan **7.979** | tidak_relevan **40.517**

**Layer 2 (relevan):**

| Vektor | Baris | Status scraping (§5.4) |
|--------|------:|------------------------|
| judi_online_pinjol | 7.425 | cukup |
| phishing_rekayasa_sosial | 391 | cukup (kualitas) |
| deepfake_penipuan_ai | 58 | **scrape** |
| peretasan_pencurian_identitas | 46 | **scrape** |
| malware_apk | 36 | **scrape** |
| penipuan_ewallet_qris | 23 | **scrape** |

**speaker_role (relevan):** R2 7.243 · R3 601 · R5 69 · R1 62 · R4 4

> Catatan: angka `relevan` per vektor lemah turun ke level **precise-only** karena relevansi sengaja digerakkan anchor presisi (keputusan E). Coverage discovery (ewallet 461 / malware 340 / peretasan 1.199 / deepfake 116) menunjukkan sinyal lebih luas ada di data, tetapi sengaja **tidak** dipromosikan ke `relevan` tanpa anchor presisi demi menjaga kualitas weak-label. Inilah justifikasi kuat untuk scraping terarah.

---

## 5. Validasi

- **Jual-beli routing (keputusan C):** sisa bocor ke phishing = **8 / 391** (dari 287 di pilot Layer 1). Praktis bersih.
- **LabelModel non-degenerate:** 30 nilai confidence unik, mean 0,945, min 0,428 — bukan kolaps ke prior. Korelasi lm vs manual = **0,733** (konvergen tapi tak identik → kedua metode saling memvalidasi).
- **Precision spot-check kelas tipis:** sampel ewallet (QRIS palsu), malware ("waspada apk undangan"), peretasan (spyware/doxxing), deepfake ("krisis deepfake / AI manips") — semua on-topic.

---

## 6. Limitasi (Jujur, untuk Bab 4)

1. **Kelas lemah starved:** ewallet/malware/deepfake/peretasan < 100–50 baris presisi. Per-vektor LabelModel-nya bersandar nyaris seluruhnya pada sedikit LF presisi (overlap tipis) → confidence kurang ter-kalibrasi untuk kelas ini. **Mitigasi: scraping terarah (jalan paralel) → re-run.**
2. **Bleed ewallet→judi:** sebagian konten QRIS/DANA terlabel judi (anchor judi broad: pinjaman/slot). Limitasi tie-break + pola broad. Akan dikoreksi di gold-standard.
3. **speaker_role kasar:** heuristik regex, bukan model. Cukup sebagai metadata, bukan ground truth.
4. **Relevansi konservatif:** memilih presisi di atas recall → sebagian konten relevan implisit (korban tanpa anchor eksplisit) masuk `tidak_relevan`. Trade-off sadar.

---

## 7. Langkah Berikutnya

- **Paralel (sisi Ray):** stratified scraping 3 vektor lemah (ewallet, malware, deepfake) via YouTube API + Apify/Tweet Harvest → masuk ke pool → re-run pipeline ini.
- **Phase 8 (Gold Standard):** sampling 357 dari `weak_labeled_dataset.csv`, 2 anotator + guidelines v2.1, Cohen's Kappa (≥0,80 overall), spot-check 50, rekonsiliasi → gold standard final.
- **Etika riset:** baris distress (G4.2, bunuh diri/depresi + pinjol) sudah dapat helper `is_distress()` di kode; perlu protokol penanganan sebelum publikasi dataset.

---

## 8. File yang Dihasilkan

```
src/phase7_labeling.py     — 46 LF vektor (precise + discovery), 6 vektor
src/phase7_layer1.py       — LF Layer 1 (positif reuse anchor + 4 negatif)
src/phase7_pipeline.py     — agregasi penuh (LabelModel + tie-break + Layer 1)
src/phase7_pilot_run.py    — runner pilot phishing+judi (LFAnalysis)
src/phase7_layer1_run.py   — runner pilot Layer 1
data/weak_labeled_dataset.csv — OUTPUT (input Phase 8)
docs/phase7_snorkel_report.md — laporan ini
```
