# Phase 3 — Video Selection Guide

Panduan langkah-demi-langkah untuk mengisi `data/video_candidates.csv` sebelum menjalankan `src/phase3_youtube_scrape.py`.

## Ringkas

Cari 5-6 video unik per vektor lemah yang memenuhi kriteria protokol (topik eksplisit, min 300 komentar, aktif, 2022-2026, Indonesia). Pilih dari ≥3 tipe channel berbeda (berita/edukasi/storytelling) per vektor. **Jangan** pilih 18 video existing (lihat Lampiran A di `docs/03_Phase2_Scraping_Plan.md`).

---

## Protokol Per Vektor

### 1. `penipuan_ewallet_qris` — Target 5-6 video

**Modus yang dijaga:**
- QRIS palsu / tempel lokasi publik (parkiran, kotak amal, SPBU)
- Scan QR "balik" / refund scam
- Promo / cashback e-wallet palsu
- Saldo OVO/DANA raib / terkuras
- Admin / CS palsu

**Search queries di YouTube (copy-paste ke search bar):**
```
QRIS palsu modus penipuan
penipuan saldo OVO DANA hilang
modus QRIS tempel parkiran
penipuan e-wallet ShopeePay GoPay
cara cek QRIS asli palsu
```

**Cara memilih video:**
1. Jalankan query di YouTube
2. Cari video dengan judul yang relevan ke salah satu dari 5 modus di atas
3. **Klik video**, buka deskripsi, tonton 60 detik pertama
4. Verifikasi: topik sesuai modus? Komentar aktif (bukan disabled)?
5. Scroll ke bawah, lihat jumlah komentar
6. **Jika ≥ 300 komentar** dan kriteria terpenuhi → catat video ID (dari URL)

**Kriteria eksklusi (jangan pilih):**
- Video sudah ada di list (18 video existing, lampiran)
- Komentar didominasi spam/bot (cek sampel 10 komentar)
- Topik campur (pembahasan 10 jenis modus tanpa fokus)

**Tipe channel yang diinginkan (pilih mix):**
- **Berita mainstream**: Kompas TV, CNN Indonesia, tvOne, Detik, iNews
- **Edukasi cybersecurity**: channel tech reviewer, channel edukasi keamanan, konten OJK/BSSN
- **Storytelling korban**: channel cerita penipuan, podcast, review modus

---

### 2. `malware_apk` — Target 5-6 video

**Modus yang dijaga:**
- APK undangan nikah → rekening terkuras
- APK kurir / paket
- APK surat tilang / pajak / PLN / BPJS
- m-banking / saldo terkuras
- Edukasi jangan install dari WA

**Search queries:**
```
penipuan APK undangan modus
APK kurir paket bobol rekening
malware APK sniffing m-banking
cara kerja penipuan file APK
korban APK undangan nikah cerita
```

**Prosedur:** Sama seperti ewallet (≥300 komentar, topik eksplisit, ≥3 tipe channel).

---

### 3. `deepfake_penipuan_ai` — Target 5-6 video

**Modus yang dijaga:**
- Voice clone suara keluarga → transfer
- Deepfake tokoh publik → investasi / crypto / giveaway
- AI-generated scam content
- Video call deepfake / sextortion
- Edukasi deteksi deepfake

**Search queries:**
```
deepfake penipuan tokoh publik
voice cloning AI penipuan suara
deepfake investasi crypto bodong
penipuan AI suara mirip keluarga
modus penipuan deepfake Indonesia
```

**Prosedur:** Sama.

---

### 4. `peretasan_pencurien_identitas` — Target 5-6 video

**Modus yang dijaga:**
- SIM swap / pencurian nomor (hack nomor induk)
- Akun diretas
- Kebocoran data pribadi
- Doxing
- Jasa hack / bobol akun

**Search queries:**
```
akun diretas email instagram facebook
kebocoran data pribadi identitas
sim swap pencurian nomor
doxing alamat pribadi dibocorkan
jasa hack bobol akun
```

**Prosedur:** Sama.

---

## Tabel Template

| vektor | video_id | video_title | channel_name | channel_type | publish_date | comment_count | verified_topic | notes |
|--------|----------|-------------|--------------|--------------|--------------|---------------|----------------|-------|
| penipuan_ewallet_qris | _aBc1234 | "QRIS Palsu di Parkiran: Cara Kerja..." | Kompas TV | berita | 2024-05-15 | 450 | Ya | Fokus QRIS lokasi publik |
| penipuan_ewallet_qris | dEf5678 | "Saldo OVO Raib Dalam Semalam: Studi Kasus" | Cyber Talk ID | edukasi | 2025-03-10 | 320 | Ya | Narasi korban, edukasi |
| malware_apk | gHi9012 | "APK Undangan Nikah Bobol Rekening: Apa Itu?" | iNews | berita | 2024-11-20 | 580 | Ya | Jelas topik & modus |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Cara isi:**
- `video_id`: Ambil dari URL. Jika URL = `youtube.com/watch?v=dQw4w9WgXcQ`, maka video_id = `dQw4w9WgXcQ`
- `publish_date`: Format YYYY-MM-DD
- `comment_count`: Estimasi dari UI YouTube (scroll ke bawah lihat "X comments")
- `verified_topic`: "Ya" jika sudah cek judul + deskripsi + 60s pertama dan sesuai modus
- `notes`: Catatan singkat (modus spesifik, karakteristik channel, alasan memilih)

---

## Checklist Sebelum Submit

- [ ] Total 20-24 video (5-6 per vektor)
- [ ] Setiap vektor punya ≥3 tipe channel berbeda (berita/edukasi/storytelling)
- [ ] Setiap video ≥300 komentar
- [ ] Video ID tidak ada di 18 video existing (cek Lampiran A di Phase2_Scraping_Plan.md)
- [ ] Semua video publikasi 2022-2026
- [ ] Semua video berbahasa Indonesia (judul + deskripsi + komentar mayoritas)
- [ ] Komentar aktif (bukan disabled) — bisa verify dengan lihat ada/tidaknya "Comments are turned off"
- [ ] `verified_topic` = "Ya" untuk setiap video (sudah validasi topik sesuai modus)

---

## Setelah Selesai Isi

1. Simpan `data/video_candidates.csv`
2. Jalankan:
   ```bash
   export YOUTUBE_API_KEY="your-api-key"
   python src/phase3_youtube_scrape.py
   ```
3. Output akan masuk ke `raw_additional_youtube/{vektor}/{video_id}.csv`
4. Laporan: `raw_additional_youtube/_summary.json` (berapa total komentar per vektor)

---

## Troubleshooting

**Q: Bagaimana cari 18 video existing untuk dihindari?**  
A: Lihat `docs/03_Phase2_Scraping_Plan.md` Lampiran A. Ada 18 video ID yang sudah di-scrape sebelumnya (jangan duplikasi).

**Q: Video sudah memenuhi kriteria tapi komentar disabled?**  
A: Hindari — tanpa komentar, data tidak berguna. Cari video lain.

**Q: Berapa lama proses YouTube API scraping?**  
A: ~2-3 menit per video (tergantung jumlah komentar). 20 video ≈ 40-60 menit total.

**Q: Bisa nggak vektor peretasan punya lebih dari 6 video?**  
A: Bisa — tapi prioritas: ewallet (ketat, sedikit video), malware, deepfake (relatif mudah), peretasan (paling banyak data existing, optional). Target minimum 5-6.

---

*Template update: 20 Jun 2026*
