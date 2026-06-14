# Phase 7 — QC Labeling Functions (LFAnalysis)

Read-only QC pada kode terintegrasi. Dataset: `preprocessed_dataset.csv` (48,496 baris).
Target roadmap: coverage >60% (ruang label), conflict <30%.

> **Reproducibility (14 Jun 2026):** re-run `phase7_pipeline.py` lokal = output zip
> IDENTIK (relevan 7.979/tidak_relevan 40.517, |Δconf|=0). Integrasi sahih.
>
> **Dead-LF refine (A&B):** dari 11 dead LF awal → **9** setelah memperbaiki 2 LF
> deepfake (`ai_content_scam`, `tokoh_publik`): drop tail content-type / prefix
> "video", anchor AI+scam / tokoh+investasi TETAP wajib. Deepfake relevan **58 → 62**;
> conflict tetap 1.6%, Layer-1 conflict 0.00% (tanpa regresi).
>
> **KOREKSI temuan awal:** klaim "39 ewallet / 62 deepfake intent" di versi QC
> sebelumnya adalah **overcount** (co-occurrence token, bukan adjacency anchor).
> Probe adjacency-preserving menunjukkan recovery sebenarnya KECIL: deepfake +4
> (presisi 4/4), ewallet saldo_platform +3 (marginal, di-skip). Mayoritas dead LF
> kelas lemah = **scarcity asli** → target scraping (lihat CONTEXT §6).

## 1. Vektor LFs (Layer 2)

- Jumlah LF: **46**
- Coverage gabungan (>=1 vektor LF firing): **30.1%** (14,613 baris)
- Overlap (>=2 LF firing): **13.7%**
- Conflict (>=2 vektor BERBEDA firing): **1.6%**
- Dead LF (coverage 0): **9** → ['lf_phish_t2_hadiah_link', 'lf_judi_t2_pinjaman_bunga', 'lf_ewallet_t1_saldo_platform', 'lf_ewallet_t1_scan_balik', 'lf_ewallet_t2_qr_lokasi_publik', 'lf_ewallet_t3_promo_palsu', 'lf_malware_t2_bank_drained', 'lf_peretasan_t1_simswap', 'lf_deepfake_t1_suara_keluarga']

### Per-LF (vektor)

|                                |   j | Polarity      |   Coverage |   Overlaps |   Conflicts |
|:-------------------------------|----:|:--------------|-----------:|-----------:|------------:|
| lf_phish_t1_ejaan              |   0 | [np.int64(0)] |     0.0002 |     0.0002 |      0      |
| lf_phish_t1_otp_modus          |   1 | [np.int64(0)] |     0.0008 |     0.0008 |      0.0002 |
| lf_phish_t1_telpon_institusi   |   2 | [np.int64(0)] |     0.0002 |     0.0002 |      0      |
| lf_phish_t1_link_curiga        |   3 | [np.int64(0)] |     0.0009 |     0.0009 |      0.0002 |
| lf_phish_t1_soceng             |   4 | [np.int64(0)] |     0.0007 |     0.0007 |      0.0001 |
| lf_phish_t2_hadiah_link        |   5 | []            |     0      |     0      |      0      |
| lf_phish_t2_undangan_file      |   6 | [np.int64(0)] |     0.0001 |     0      |      0      |
| lf_phish_t2_anchor_gate        |   7 | [np.int64(0)] |     0.0107 |     0.0083 |      0.0035 |
| lf_phish_t3_korban_strict      |   8 | [np.int64(0)] |     0      |     0      |      0      |
| lf_phish_t3_discovery          |   9 | [np.int64(0)] |     0.1105 |     0.0171 |      0.0111 |
| lf_judi_t1_slang               |  10 | [np.int64(3)] |     0.0082 |     0.0075 |      0.0004 |
| lf_judi_t1_eksplisit           |  11 | [np.int64(3)] |     0.1079 |     0.1079 |      0.0062 |
| lf_judi_t1_pinjol_ilegal       |  12 | [np.int64(3)] |     0.0006 |     0.0006 |      0.0002 |
| lf_judi_t1_teror_pinjol        |  13 | [np.int64(3)] |     0.0002 |     0.0002 |      0      |
| lf_judi_t1_bare                |  14 | [np.int64(3)] |     0.0935 |     0.0935 |      0.0074 |
| lf_judi_t2_pinjaman_bunga      |  15 | []            |     0      |     0      |      0      |
| lf_judi_t2_slot_promo          |  16 | [np.int64(3)] |     0.0001 |     0.0001 |      0      |
| lf_judi_t3_modal_hasil         |  17 | [np.int64(3)] |     0      |     0      |      0      |
| lf_judi_t3_discovery           |  18 | [np.int64(3)] |     0.1582 |     0.1238 |      0.0106 |
| lf_ewallet_t1_qris_palsu       |  19 | [np.int64(1)] |     0.0004 |     0.0004 |      0.0001 |
| lf_ewallet_t1_saldo_platform   |  20 | []            |     0      |     0      |      0      |
| lf_ewallet_t1_scan_balik       |  21 | []            |     0      |     0      |      0      |
| lf_ewallet_t2_platform_tipu    |  22 | [np.int64(1)] |     0      |     0      |      0      |
| lf_ewallet_t2_qr_lokasi_publik |  23 | []            |     0      |     0      |      0      |
| lf_ewallet_t3_promo_palsu      |  24 | []            |     0      |     0      |      0      |
| lf_ewallet_t3_discovery        |  25 | [np.int64(1)] |     0.0095 |     0.0021 |      0.0018 |
| lf_malware_t1_apk_modus        |  26 | [np.int64(2)] |     0.0002 |     0.0002 |      0.0002 |
| lf_malware_t1_apk_bahaya       |  27 | [np.int64(2)] |     0.0001 |     0.0001 |      0      |
| lf_malware_t1_kena_apk         |  28 | [np.int64(2)] |     0.0005 |     0.0005 |      0      |
| lf_malware_t2_apk_sumber       |  29 | [np.int64(2)] |     0      |     0      |      0      |
| lf_malware_t2_bank_drained     |  30 | []            |     0      |     0      |      0      |
| lf_malware_t3_discovery        |  31 | [np.int64(2)] |     0.007  |     0.0029 |      0.0023 |
| lf_peretasan_t1_akun_diretas   |  32 | [np.int64(4)] |     0.0001 |     0.0001 |      0      |
| lf_peretasan_t1_kebocoran_data |  33 | [np.int64(4)] |     0.0003 |     0.0003 |      0.0001 |
| lf_peretasan_t1_kasus          |  34 | [np.int64(4)] |     0.0002 |     0.0002 |      0      |
| lf_peretasan_t1_simswap        |  35 | []            |     0      |     0      |      0      |
| lf_peretasan_t2_curi_data      |  36 | [np.int64(4)] |     0.0002 |     0.0002 |      0.0001 |
| lf_peretasan_t2_doxing         |  37 | [np.int64(4)] |     0.0002 |     0.0002 |      0      |
| lf_peretasan_t3_jasa_hack      |  38 | [np.int64(4)] |     0      |     0      |      0      |
| lf_peretasan_t3_discovery      |  39 | [np.int64(4)] |     0.0247 |     0.0042 |      0.0034 |
| lf_deepfake_t1_eksplisit       |  40 | [np.int64(5)] |     0.0011 |     0.0011 |      0.0003 |
| lf_deepfake_t1_voice_clone     |  41 | [np.int64(5)] |     0.0001 |     0.0001 |      0      |
| lf_deepfake_t1_suara_keluarga  |  42 | []            |     0      |     0      |      0      |
| lf_deepfake_t2_ai_content_scam |  43 | [np.int64(5)] |     0.0001 |     0.0001 |      0      |
| lf_deepfake_t2_tokoh_publik    |  44 | [np.int64(5)] |     0.0001 |     0      |      0      |
| lf_deepfake_t3_discovery       |  45 | [np.int64(5)] |     0.0024 |     0.0016 |      0.0007 |

## 2. Layer-1 LFs (relevansi)

- Positif (RELEVAN) coverage: **29.8%**
- Negatif (TIDAK_RELEVAN) coverage: **7.0%**
- Konflik relevan-vs-tidak_relevan (pos & neg sama-sama firing): **0.00%**
- Dead LF: **0**

### Per-LF (Layer 1)

|                       |   j | Polarity      |   Coverage |   Overlaps |   Conflicts |
|:----------------------|----:|:--------------|-----------:|-----------:|------------:|
| lf_rel_phishing       |   0 | [np.int64(1)] |     0.1105 |     0.011  |           0 |
| lf_rel_ewallet        |   1 | [np.int64(1)] |     0.0095 |     0.0017 |           0 |
| lf_rel_malware        |   2 | [np.int64(1)] |     0.007  |     0.0023 |           0 |
| lf_rel_judi           |   3 | [np.int64(1)] |     0.1582 |     0.0092 |           0 |
| lf_rel_peretasan      |   4 | [np.int64(1)] |     0.0247 |     0.0032 |           0 |
| lf_rel_deepfake       |   5 | [np.int64(1)] |     0.0024 |     0.0007 |           0 |
| lf_tr_emosional       |   6 | [np.int64(0)] |     0.0568 |     0.0278 |           0 |
| lf_tr_offtopic_pendek |   7 | [np.int64(0)] |     0.0305 |     0.0278 |           0 |
| lf_tr_generik_siber   |   8 | [np.int64(0)] |     0.001  |     0      |           0 |
| lf_tr_jualbeli        |   9 | [np.int64(0)] |     0.0093 |     0      |           0 |

## 3. Interpretasi

- Coverage vektor 30.1% < 60% adalah WAJAR: dataset didominasi konten off-topic (lihat Temuan #4); coverage tinggi hanya diharapkan pada subset relevan, bukan seluruh 48k. Conflict adalah metrik kualitas utama di sini.
- Conflict vektor 1.6% MEMENUHI target <30%.
- Empirical accuracy per-LF butuh gold standard → diukur di Phase 8.
