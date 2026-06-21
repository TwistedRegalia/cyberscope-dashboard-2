# Phase 5 (revisi) — Merge Scraping Tambahan

Digabung dari Phase 3 (YouTube) + Phase 4 (X) ke `unified_dataset.csv`.

## 1. Ringkasan

- Existing: **48,496** baris
- Raw baru (YT 0 + X 1,955): **1,955**
- Setelah filter internal: **1,843**
- Duplikat lintas-batch dibuang: **7**
- Baris baru ditambahkan: **1,836**
- **Total merged: 50,332** → `data/unified_dataset_v2.csv`

## 2. Baris baru per source_category (vektor asal scraping)

| Vektor | Baris baru |
|--------|-----------|
| peretasan_pencurian_identitas | 1,176 |
| penipuan_ewallet_qris | 525 |
| malware_apk | 84 |
| deepfake_penipuan_ai | 51 |

## 3. Vector hint pada data baru (diagnostik kasar, BUKAN label final)

| Vector Hint | Jumlah |
|-------------|--------|
| peretasan_pencurian_identitas | 1,042 |
| penipuan_ewallet_qris | 524 |
| malware_apk | 82 |
| NO_HINT | 69 |
| phishing_rekayasa_sosial | 64 |
| deepfake_penipuan_ai | 36 |
| judi_online_pinjol | 19 |

---

*Langkah berikut: re-run Phase 6 (preprocess) lalu Phase 7 (Snorkel) pada `unified_dataset_v2.csv`. `source_category`/`vector_hint` BUKAN label final.*