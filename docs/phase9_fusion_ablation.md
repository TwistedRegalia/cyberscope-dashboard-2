# Phase 9 — Late Fusion Ablation (Data untuk Bab 4)

**Tanggal:** 6 Jul 2026 · **Branch:** `feat/phase9-training`
**Skema fusion:** inference-time, `skor = W_neural · P_neural + W_rule · anchor` (W_rule = 1 − W_neural). Model A & B **tidak** dilatih ulang (checkpoint dimuat; sanity check reproduksi macro-F1 Model A 0,9680 & Model B 0,9767 → valid).

**Definisi anchor:**
- **Layer 2** (6 vektor): `anchor(v) = count_match(v) / Σ count_match` (share bukti; 0 semua bila tak ada anchor → defer ke neural).
- **Layer 1** (relevansi): sinyal **satu-arah** — `has_anchor → [tidak_relevan=0, relevan=1]`; tanpa anchor → `[0, 0]` (defer neural, tidak menekan ke tidak_relevan).

Arsip logika: [`src/phase9_late_fusion.py`](../src/phase9_late_fusion.py). Pola anchor: [`src/anchor_patterns.py`](../src/anchor_patterns.py).

---

## 1. Layer 2 (6-vektor) — sweep bobot

| W_neural | W_rule | macro-F1 | F1_phishing |
|---:|---:|---:|---:|
| 1,00 | 0,00 | 0,9767 | 0,9109 |
| 0,95 | 0,05 | 0,9767 | 0,9109 |
| 0,90 | 0,10 | 0,9767 | 0,9109 |
| 0,85 | 0,15 | 0,9747 | 0,9000 |
| 0,80 | 0,20 | 0,9747 | 0,9000 |
| **0,75** | **0,25** | **0,9747** | **0,9000** |
| 0,70 | 0,30 | 0,9747 | 0,9000 |
| 0,60 | 0,40 | 0,9747 | 0,9000 |
| 0,50 | 0,50 | 0,9814 | 0,9375 |

**Confusion matrix @ 0,75:0,25** (baris = gold, kolom = pred):

|  | phish | ewallet | malware | judi | peretasan | deepfake |
|---|---:|---:|---:|---:|---:|---:|
| **phishing** | 45 | 0 | 0 | 4 | 0 | 0 |
| **ewallet** | 0 | 55 | 0 | 0 | 0 | 0 |
| **malware** | 0 | 0 | 22 | 0 | 0 | 0 |
| **judi** | 6 | 0 | 2 | 741 | 0 | 0 |
| **peretasan** | 0 | 0 | 0 | 0 | 37 | 0 |
| **deepfake** | 0 | 0 | 0 | 0 | 0 | 10 |

**Baca:**
- Rule ≤ 0,10 → **inert** (identik neural 0,9767): softmax Model B terlalu confident, kontribusi anchor tenggelam.
- Rule 0,15–0,40 → **turun** ke 0,9747 (1 sampel phishing bocor ke judi).
- 0,50:0,50 → **naik** ke 0,9814. **Verifikasi (Sel D1/D2):** stabil di rentang W_neural **0,45–0,51** (bukan artefak tie-breaking); mekanisme = koreksi **4 sampel boundary phishing↔judi, semuanya gold=judi yang neural over-prediksi sebagai phishing** (konsisten scam-umbrella).
- **Keputusan: bobot final = 0,75:0,25 (rancangan a priori).** 0,50 **tidak dipilih** karena teridentifikasi pada test set (test-set optimization / bias evaluasi). Nilai rule-based di L2 = **interpretabilitas (XAI)**, bukan akurasi.

---

## 2. Layer 1 (relevansi) — sweep bobot

| W_neural | W_rule | macro-F1 | recall_relevan | precision_relevan | FN | FP |
|---:|---:|---:|---:|---:|---:|---:|
| 1,00 | 0,00 | 0,9680 | 0,9674 | 0,9272 | 30 | 70 |
| 0,95 | 0,05 | 0,9677 | 0,9674 | 0,9262 | 30 | 71 |
| 0,90 | 0,10 | 0,9677 | 0,9685 | 0,9253 | 29 | 72 |
| 0,85 | 0,15 | 0,9675 | 0,9707 | 0,9226 | 27 | 75 |
| 0,80 | 0,20 | 0,9678 | 0,9739 | 0,9209 | 24 | 77 |
| **0,75** | **0,25** | **0,9679** | **0,9761** | **0,9192** | **22** | **79** |
| 0,70 | 0,30 | 0,9665 | 0,9794 | 0,9120 | 19 | 87 |
| 0,60 | 0,40 | 0,9478 | 0,9859 | 0,8526 | 13 | 157 |
| 0,50 | 0,50 | 0,7810 | 1,0000 | 0,5047 | 0 | 904 |

**Confusion matrix @ 0,75:0,25** = `[[TN=4530, FP=79], [FN=22, TP=899]]` (neural: `[[4539,70],[30,891]]`).

**Baca:**
- Recall relevan **naik monoton** seiring W_rule; FN turun 30→22→…→0. **rule-based BERKONTRIBUSI FUNGSIONAL** di sini (anchor = relevance detector sesuai desain).
- Pada **0,75:0,25**: recall 0,9674→0,9761 (+0,87pp), **8 FN diselamatkan**, biaya +9 FP, **macro-F1 datar** (0,9680→0,9679).
- Di ≥0,40 rule: FP meledak (→904) & macro-F1 kolaps → **knee di ~0,75**.
- Untuk filter tahap-1, recall tinggi = tujuan benar (relevan yang terbuang hilang permanen; FP masih disaring Layer 2).

---

## 3. Kesimpulan (untuk Bab 4)

| Layer | Peran rule-based | Bukti kuantitatif @ 0,75:0,25 |
|---|---|---|
| **Layer 1 (relevansi)** | **Fungsional** — safety net recall | recall relevan +0,87pp (0,9674→0,9761), 8 FN diselamatkan, macro-F1 datar |
| **Layer 2 (vektor)** | **Interpretabilitas (XAI)** — redundan diskriminatif | macro-F1 0,9767→0,9747 (−1 sampel); 0,50 lebih baik tapi test-set optimization → ditolak |

**Sintesis:** neural memikul beban diskriminatif utama; anchor = *relevance detector* (kekuatan Layer 1), bukan *vector separator* (kelemahan Layer 2) — persis rasional arsitektur Triple-Hybrid + rule-based late fusion 0,75:0,25.
