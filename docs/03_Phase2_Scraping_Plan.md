# Phase 2 — Scraping Plan (Tambahan untuk 3 Vektor Lemah)

**Penelitian:** Klasifikasi Otomatis Diskursus Vektor Ancaman Siber pada Media Sosial Indonesia
**Versi:** 1.0
**Status:** Siap (eksekusi dikondisikan hasil Snorkel)
**Author:** Ray

---

## 0. Konteks dan Prinsip

### 0.1 Tujuan

Menyiapkan rencana scraping tambahan untuk **3 vektor lemah** yang teridentifikasi di audit Phase 0:

| Vektor | Total saat ini (raw, by source) | Status |
|--------|--------------------------------|--------|
| `malware_apk` | 2.902 | Lemah — hanya 3 video YT |
| `penipuan_ewallet_qris` | 3.362 | Lemah — hanya 2 video YT |
| `deepfake_penipuan_ai` | 2.724 | Lemah — hanya 3 video YT |

Bandingkan dengan vektor kuat: `judi_online_pinjol` (21.880) dan `peretasan_pencurian_identitas` (21.791).

### 0.2 Prinsip Eksekusi: Conditional on Snorkel

**Scraping ini TIDAK langsung dieksekusi.** Urutan yang disepakati:

1. Jalankan relevance filter + Snorkel re-kategorisasi pada seluruh ~50K data existing
2. Periksa distribusi vektor **setelah** re-kategorisasi (cross-vector mining mungkin mengangkat kelas minoritas)
3. Tentukan vektor mana yang **masih** < 1.000 sampel relevan setelah Snorkel
4. Eksekusi scraping HANYA untuk vektor yang masih kurang

Logikanya: komentar di video judi/hack mungkin sebenarnya membahas malware/ewallet/deepfake. Snorkel akan me-relabel berdasarkan konten aktual, bukan asal video. Mungkin kelas minoritas terangkat tanpa scraping.

### 0.3 Mengapa Bukan Claude yang Memilih Video

Pemilihan video spesifik memerlukan data real-time yang tidak dapat diverifikasi dari pengetahuan model: video ID aktual, jumlah komentar saat ini, status komentar (aktif/disabled), dan ketersediaan video. Memilih "dari ingatan" berisiko menghasilkan rekomendasi yang tidak akurat dan justru menciptakan selection bias acak.

Sebagai gantinya, dokumen ini menyediakan **protokol pencarian sistematis** yang Anda eksekusi sendiri di YouTube. Pendekatan ini lebih defensible secara metodologis karena:
- Transparan dan dapat direplikasi (reviewer bisa mengikuti protokol yang sama)
- Berbasis kriteria objektif, bukan pilihan subjektif
- Terdokumentasi sebagai bagian dari metodologi penelitian

---

## 1. Target Kuantitatif

### 1.1 Target per Vektor Lemah

Target tambahan untuk mencapai minimum sehat per kelas:

| Vektor | Target tambahan | Sumber prioritas |
|--------|----------------|------------------|
| `malware_apk` | +2.000-3.000 komentar/tweet | YouTube (3-4 video baru) + X |
| `penipuan_ewallet_qris` | +2.000-3.000 | YouTube (3-4 video baru) + X |
| `deepfake_penipuan_ai` | +1.500-2.500 | YouTube (3-4 video baru) + X |

### 1.2 Target Diversity (bukan hanya volume)

Lebih penting dari volume: **diversity sumber**. Target struktural:

- Minimum **5-6 video unik** per vektor lemah (saat ini hanya 2-3)
- Video dari **channel berbeda** (hindari satu channel mendominasi)
- Mix tipe channel: berita mainstream, edukasi cybersecurity, storytelling korban

---

## 2. Protokol Pemilihan Video YouTube

### 2.1 Kriteria Inklusi Video

Setiap video kandidat harus memenuhi SEMUA kriteria berikut:

1. **Topik eksplisit** menyentuh vektor target (cek judul + deskripsi + 60 detik pertama)
2. **Minimum 300 komentar** (cek di bawah video; target ideal 500+)
3. **Komentar aktif** (tidak disabled)
4. **Publikasi 2022-2026** (relevansi temporal dengan dataset existing)
5. **Berbahasa Indonesia** (audiens dan komentar mayoritas Indonesia)

### 2.2 Kriteria Eksklusi Video

Hindari video yang:

- Sudah ada di dataset (cek 18 video ID existing — lihat Lampiran A)
- Komentar didominasi spam/bot promosi judi (kecuali untuk vektor judi)
- Topik terlalu campur (membahas 10 modus sekaligus tanpa fokus)
- Channel dengan engagement palsu (komentar generic, bukan diskusi riil)

### 2.3 Search Query per Vektor (untuk Anda eksekusi di YouTube)

Gunakan query ini di search bar YouTube, lalu filter hasil dengan kriteria 2.1-2.2.

**Untuk `malware_apk`:**
```
penipuan APK undangan modus
APK kurir paket bobol rekening
malware APK sniffing m-banking
cara kerja penipuan file APK
korban APK undangan nikah cerita
```

**Untuk `penipuan_ewallet_qris`:**
```
QRIS palsu modus penipuan
penipuan saldo OVO DANA hilang
modus QRIS tempel parkiran
penipuan e-wallet ShopeePay GoPay
cara cek QRIS asli palsu
```

**Untuk `deepfake_penipuan_ai`:**
```
deepfake penipuan tokoh publik
voice cloning AI penipuan suara
deepfake investasi crypto bodong
penipuan AI suara mirip keluarga
modus penipuan deepfake Indonesia
```

### 2.4 Tipe Channel yang Direkomendasikan

Untuk memastikan diversity diskursif, targetkan 3 tipe channel:

| Tipe | Contoh karakteristik | Diskursus dominan |
|------|---------------------|-------------------|
| Berita mainstream | Kompas TV, CNN Indonesia, tvOne, Detik | R1 (korban relate), R5 (jurnalistik) |
| Edukasi cybersecurity | Channel tech reviewer, edukasi keamanan, konten OJK/BSSN | R3 (edukator) |
| Storytelling korban | Channel cerita penipuan, podcast, review modus | R1, R2 (saksi), R3 |

### 2.5 Form Dokumentasi Video Terpilih

Untuk setiap video yang lolos kriteria, catat di `video_candidates.csv`:

| Field | Deskripsi |
|-------|-----------|
| `vektor` | Vektor target (malware/ewallet/deepfake) |
| `video_id` | ID video (dari URL: youtube.com/watch?v=**VIDEO_ID**) |
| `video_title` | Judul video |
| `channel_name` | Nama channel |
| `channel_type` | berita / edukasi / storytelling |
| `publish_date` | Tanggal publikasi |
| `comment_count` | Estimasi jumlah komentar |
| `verified_topic` | Ya/Tidak (sudah cek topik sesuai vektor) |
| `notes` | Catatan tambahan |

Target: 5-6 video terverifikasi per vektor lemah = 15-18 video baru total.

---

## 3. Protokol Scraping X (Twitter) Tambahan

### 3.1 Strategi

Sesuai Jalur C (Tweet Harvest primary, Apify backup). Untuk 3 vektor lemah, tambahkan query yang menargetkan **sub-aspek yang belum tercakup** di scraping sebelumnya.

### 3.2 Query Tambahan per Vektor

Berdasarkan pattern library E-ICTT v2.1, dengan boolean operator dan `lang:id`.

**Untuk `malware_apk`** (existing: 637 tweets, sudah ada sesi3, sesi3b):
```
"apk undangan" OR "apk kurir" OR "apk tilang" lang:id
"kena apk" OR "install apk" (saldo OR rekening OR bobol) lang:id
"file apk" (wa OR whatsapp) (penipuan OR bahaya) lang:id
"sniffing" (apk OR mbanking OR rekening) lang:id
```

**Untuk `penipuan_ewallet_qris`** (existing: 310 tweets, sudah ada sesi2, sesi2b):
```
"qris palsu" OR "qris tempel" lang:id
"saldo" (ovo OR dana OR gopay OR shopeepay) (hilang OR amblas OR raib) lang:id
"scan qris" (tipu OR palsu OR penipuan) lang:id
"modus qris" OR "qris parkiran" lang:id
```

**Untuk `deepfake_penipuan_ai`** (existing: 590 tweets, sudah ada sesi6 dan variannya):
```
"deepfake" (penipuan OR scam OR tipu OR bodong) lang:id
"voice cloning" OR "suara ai" (penipuan OR tipu OR transfer) lang:id
"deepfake" (jokowi OR prabowo OR menteri) (investasi OR crypto) lang:id
"ai voice" (mirip OR clone) (anak OR keluarga OR transfer) lang:id
```

### 3.3 Parameter Eksekusi Tweet Harvest

- `--limit 300-500` per query (konservatif, hindari ban)
- `--from` dan `--to`: rentang 2023-01-01 sampai 2026-06-01
- Jeda antar-query beberapa menit
- Pakai akun X sekunder (mitigasi risiko ban)
- Catatan: timestamp hasil mungkin = waktu scraping (limitasi Tweet Harvest, lihat Phase 0)

---

## 4. Trigger Eksekusi (Decision Gate)

Scraping tambahan dieksekusi berdasarkan keputusan setelah Snorkel:

```
Setelah relevance filter + Snorkel re-kategorisasi:
  │
  ▼
Cek distribusi vektor (label diskursif final, bukan source category)
  │
  ├── Vektor X punya ≥ 1.000 sampel relevan
  │       → TIDAK perlu scraping untuk vektor X
  │
  └── Vektor X punya < 1.000 sampel relevan
          → Eksekusi scraping untuk vektor X
          → YouTube (protokol Bagian 2) + X (protokol Bagian 3)
```

Threshold 1.000 dapat disesuaikan. Untuk thesis S1, 1.000 sampel relevan per kelas adalah minimum sehat sebelum mengandalkan class weights.

---

## 5. Deliverable Phase 2

Saat eksekusi (post-Snorkel):

- `video_candidates.csv` — daftar video terverifikasi per vektor lemah
- `additional_scraping_log.md` — log eksekusi (kapan, query apa, hasil berapa)
- `raw_additional_youtube/` — komentar dari video baru
- `raw_additional_tweets/` — tweet dari query baru
- `phase2_justification.md` — dokumentasi mengapa scraping dilakukan (hasil Snorkel yang memicu)

---

## 6. Catatan Metodologi untuk Tesis

Template dokumentasi di Bab 3:

> "Untuk mengatasi ketidakseimbangan kelas yang teridentifikasi pada analisis awal, dilakukan pengumpulan data tambahan terbatas untuk tiga vektor dengan representasi rendah (malware APK, penipuan e-wallet/QRIS, deepfake/AI). Pemilihan video YouTube tambahan dilakukan melalui protokol pencarian sistematis berbasis kriteria objektif (relevansi topik, jumlah komentar minimum, keragaman channel), bukan pemilihan subjektif, untuk menjaga reproducibility. Keputusan untuk melakukan scraping tambahan didasarkan pada distribusi kelas setelah proses weak supervision, sehingga menghindari pengumpulan data yang tidak diperlukan."

---

## Lampiran A — 18 Video ID Existing (Jangan Di-scrape Ulang)

| Vektor (asal) | Video ID |
|---------------|----------|
| deepfake | 4cbsS6uzVo0, o3tkFMIxQ8M, wY7ogQMosZk |
| ewallet | TMDtWt3QISk, h8y7MYOksSs |
| hack | 9OTIkyqdSsQ, R4oHk-U8HoA, kFytXQzrZuY, ofXjLXQAqxc |
| malware | 4mroFXh7ZsI, EEnuPdGUzYA, sr63o6csBKo |
| phishing | XgqqAZ1umH8, nIAgjse6hos, uTkGmGlKqIo |
| pinjol | 65AQJH5ihA8, riQMdj-ed6A, zRdanlyQiPk |

---

*Akhir dokumen. Eksekusi dikondisikan pada hasil Snorkel (Phase 7). Sampai saat itu, dokumen ini berstatus "siap, menunggu trigger".*
