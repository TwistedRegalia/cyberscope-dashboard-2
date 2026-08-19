# Catatan Slide 9 — Prapemrosesan & Pelabelan Data

Berkas hasil revisi: `PPT SIDANG RAY SIRAJ (revisi slide 9).pptx` (asli tidak diubah).
Hanya slide 9 yang disentuh.

## Temuan utama: `text_normalized` tidak pernah dipakai

Kolom `text_normalized` dan `text_stemmed` dihasilkan `src/phase6_preprocess.py`,
tetapi **tidak satu pun masuk ke model**. Bukti:

| Pemeriksaan | Hasil |
|---|---|
| Kolom `data/splits/*.csv` | `unified_id, platform, source_category, vector_hint, text_clean, label` |
| `_split_manifest.json` | `"feature_col": "text_clean"` |
| Tiga notebook training | Hanya `text_clean`; `text_normalized` nol kemunculan |
| `phase9_late_fusion.py`, dashboard backend | Nol |

Model dilatih pada `text_clean` karena bentuk informal (`gue`, `yg`, `ga`) justru
bagian dari sinyal diskursus media sosial. Slide sudah disesuaikan agar tidak
terbaca seolah normalisasi menyuapi model.

## Kondisi slide sekarang

**Kolom kiri — Prapemrosesan**
- Bullet normalisasi berbunyi `Normalisasi slang: gue → saya (tidak dipakai model)`
- Kotak justifikasi ditutup bukti empiris: *"Pada data ini stemming bahkan membalik
  makna: sebelumnya → belum."*
- Tabel contoh **2 baris** (Mentah → Bersih). Sumber: `data/preprocessed_dataset_v2.csv`,
  `UID000002`. Baris "Bersih" sebelumnya keliru berisi `text_normalized`, sudah diperbaiki
  jadi `text_clean` yang sebenarnya.

**Kolom kanan — Pelabelan**
- Empat bullet, yang terakhir `Mutu LF: conflict 1,6% · overlap 13,7% · konflik Layer-1 0,00%`
- Grafik distribusi dipadatkan (1,99" → 1,32")
- **Tabel 3.8** ditambahkan: 6 baris × 2 kolom, 7,5pt, nama kategori mengikuti
  `LABEL_NAMES` di `src/phase7_labeling.py:37`
- Kotak rasio ketimpangan diturunkan ke 9pt

**Catatan pembicara** (3.006 karakter) — definisi LF beserta kode aslinya, empat langkah
weak supervision, dan jawaban siap pakai untuk enam pertanyaan yang mungkin muncul.

## Sumber angka di slide

| Angka | Berkas |
|---|---|
| 56 LF (46 Layer 2 + 10 Layer 1) | `src/phase7_labeling.py` (`ALL_LFS`) + `src/phase7_layer1.py` |
| conflict 1,6% · overlap 13,7% · konflik Layer-1 0,00% · dead LF 9/46 | `docs/phase7_qc_report.md` |
| 55.300 → 9.212 relevan; distribusi 6 kategori | `data/splits/_split_manifest.json` |
| Contoh prapemrosesan | `data/preprocessed_dataset_v2.csv`, `UID000002` |
| Pola Tabel 3.8 | `docs/02_Pattern_Library.md`, `src/phase7_labeling.py` |

## Yang perlu diketahui sebelum menyentuh slide ini lagi

- **Batas bawah konten y = 6.00 inci**, bukan 7.50. `slideLayout3.xml` punya banner
  (`Picture 6`) di y=6.00–7.50. Posisi terbawah sekarang: kiri **5.47"**, kanan **5.98"**.
  Kolom kanan praktis tidak punya sisa ruang lagi.
- Slide berukuran **10 × 7.5 inci (4:3)**, bukan 16:9.
- `TextBox 17` dan `TextBox 7` memakai `spAutoFit` — PowerPoint menghitung ulang
  tingginya saat berkas dibuka. Bullet yang memanjang jadi dua baris akan menggeser
  segalanya ke bawah, dan di kolom kanan itu berarti menembus banner.
- Saat menambah baris tabel atau paragraf, **salin elemen XML yang sudah ada**
  (`copy.deepcopy`) lalu ganti teksnya. Membuat dari nol akan kehilangan format tema.
  Sel teks terpecah jadi banyak `<a:r>` karena pemeriksa ejaan; sisakan run pertama,
  buang sisanya. Bentuk hasil salinan wajib diberi `id` dan `name` baru.
- Berkas keluaran tidak bisa ditimpa selama masih terbuka di PowerPoint.

## Belum diverifikasi

Tampilan visual. LibreOffice tidak terpasang sehingga slide tidak bisa di-render
jadi gambar. Yang perlu dilihat langsung: kolom kanan kini memuat grafik, Tabel 3.8,
dan kotak rasio dalam 2,9 inci — perlu dipastikan masih terbaca dari jarak proyektor.
