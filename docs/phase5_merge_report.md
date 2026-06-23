# Phase 5 (revisi) — Merge Scraping Tambahan

Digabung dari Phase 3 (YouTube) + Phase 4 (X) ke `unified_dataset.csv`.

## 1. Ringkasan

- Existing: **48,496** baris
- Raw baru (YT 6,663 + X 1,955): **8,618**
- Setelah filter internal: **6,830**
- Duplikat lintas-batch dibuang: **26**
- Baris baru ditambahkan: **6,804**
- **Total merged: 55,300** → `data/unified_dataset_v2.csv`

## 2. Baris baru per source_category (vektor asal scraping)

| Vektor | Baris baru |
|--------|-----------|
| malware_apk | 4,060 |
| peretasan_pencurian_identitas | 1,176 |
| deepfake_penipuan_ai | 1,043 |
| penipuan_ewallet_qris | 525 |

## 3. Vector hint pada data baru (diagnostik kasar, BUKAN label final)

| Vector Hint | Jumlah |
|-------------|--------|
| NO_HINT | 3,586 |
| peretasan_pencurian_identitas | 1,180 |
| malware_apk | 762 |
| phishing_rekayasa_sosial | 610 |
| penipuan_ewallet_qris | 541 |
| judi_online_pinjol | 76 |
| deepfake_penipuan_ai | 49 |

---

*Langkah berikut: re-run Phase 6 (preprocess) lalu Phase 7 (Snorkel) pada `unified_dataset_v2.csv`. `source_category`/`vector_hint` BUKAN label final.*