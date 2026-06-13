# Phase 5 — Filter & Dedup Report

Konsolidasi 59 file CSV menjadi dataset unified E-ICTT v2.1.

---

## 1. Ringkasan

- **Input total (raw gabungan):** 69,651
- **Output total (bersih):** 48,496
- **Reduction rate:** 30.4%

## 2. Breakdown Filtering

| Filter | Dibuang |
|--------|---------|
| Empty/null | 10 |
| Low-signal (emoji/punct) | 805 |
| Terlalu pendek (<10 char) | 2,777 |
| Terlalu panjang (>2000 char) | 21 |
| Reply low-quality | 15,312 |
| Duplikat exact | 2,230 |

## 3. Reply Quality Filter (Opsi 1)

Kriteria: min 5 kata + ada anchor vektor + bukan pure afirmasi

- Reply input: 17,815
- Reply lolos: 2,503 (14.0%)

## 4. Distribusi Dataset Final

### 4.1 Per Platform

| Platform | Jumlah |
|----------|--------|
| YouTube | 46,771 |
| X | 1,725 |

### 4.2 Per Source Category (asal scraping, BUKAN label final)

| Source Category | Jumlah |
|-----------------|--------|
| judi_online_pinjol | 17,249 |
| peretasan_pencurian_identitas | 16,100 |
| phishing_rekayasa_sosial | 9,200 |
| penipuan_ewallet_qris | 2,231 |
| deepfake_penipuan_ai | 1,961 |
| malware_apk | 1,755 |

### 4.3 Vector Hint (diagnostik crude, BUKAN label final)

Estimasi distribusi berdasarkan anchor pattern. Label final ditentukan Snorkel.

| Vector Hint | Jumlah |
|-------------|--------|
| NO_HINT (perlu Snorkel) | 37,545 |
| judi_online_pinjol | 7,242 |
| phishing_rekayasa_sosial | 1,781 |
| peretasan_pencurian_identitas | 1,104 |
| penipuan_ewallet_qris | 417 |
| malware_apk | 291 |
| deepfake_penipuan_ai | 116 |

### 4.4 Reply vs Top-level

| Tipe | Jumlah |
|------|--------|
| Top-level/Tweet | 46,599 |
| Reply | 1,897 |

---

*Catatan: `source_category` dan `vector_hint` BUKAN label final. Label diskursif final ditentukan via Snorkel weak supervision (Phase 7) dengan relevance filter dan hierarki prioritas E-ICTT v2.1.*