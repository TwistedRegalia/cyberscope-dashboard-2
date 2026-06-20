# Phase 4 — Tweet Harvest Execution Guide

Panduan menjalankan `src/phase4_tweet_harvest.py` untuk scraping tweets per vektor.

## Prerequisites

```bash
# Install Tweet Harvest
pip install tweet-harvest

# Set up Twitter API access
# Option 1: Via Tweet Harvest CLI
tweet-harvest --auth

# Option 2: Manual Bearer token
export TWITTER_BEARER_TOKEN="your-bearer-token"
```

**Catatan:** Bearer token perlu dari Twitter Developer Portal atau via Tweet Harvest auth flow.

---

## Query Specification

Script membaca dari `data/query_spec.json`, yang sudah berisi 6-7 queries per vektor:

**`penipuan_ewallet_qris`** (X-driven, 6 queries):
- QRIS palsu / bodong
- Saldo OVO/DANA hilang / raib / amblas
- Scan QR balik / refund
- Cashback palsu / promo palsu
- Admin / CS palsu
- QRIS kotak amal / parkiran / SPBU

**`malware_apk`** (X+YT balanced, 6 queries):
- APK undangan nikah → rekening terkuras
- APK kurir / paket / JNT
- APK tilang / pajak / PLN / BPJS
- Install APK saldo/rekening bobol
- Sniffing APK / m-banking
- APK sumber / download APK bahaya

**`deepfake_penipuan_ai`** (X+YT comparable, 6 queries):
- Voice cloning suara AI → transfer anak/keluarga
- Deepfake tokoh publik → investasi / crypto / giveaway
- Deepfake penipuan / scam / tipu / bodong
- AI video call palsu / deepfake sextortion
- Deepfake suara / video mirip / palsu
- Deteksi deepfake / cek deepfake

**`peretasan_pencurian_identitas`** (reference, 6 queries):
- Akun/email diretas / hack / bobol
- Kebocoran data / privacy breach
- SIM swap / sim swapping
- Doxing / alamat dibocorkan
- Pencurian identitas / data / foto
- Jasa hack / jasa bobol / hacker

Setiap query: `lang:id` (Indonesia only), limit 500 tweets (konservatif, hindari ban).

---

## Eksekusi

### Langkah 1: Verifikasi dependencies

```bash
python -c "import tweet_harvest; print(tweet_harvest.__version__)"
# Expected: 2.7.1 atau lebih baru
```

### Langkah 2: Jalankan script

```bash
python src/phase4_tweet_harvest.py
```

**Output:**
- `raw_additional_tweets/{vektor}/q{idx}.jsonl` → raw Tweet Harvest output
- `raw_additional_tweets/{vektor}/q{idx}.csv` → converted untuk phase5_consolidate.py
- `raw_additional_tweets/_summary.json` → metadata (timestamp, jumlah tweets, failed queries)

### Langkah 3: Monitor progress

Terminal akan menampilkan:
```
[Phase 4] Loaded 4 vectors from data/query_spec.json

[penipuan_ewallet_qris] 6 queries, limit=500, lang=id
[penipuan_ewallet_qris:q1] Running: tweet-harvest --query "qris palsu"... lang:id --limit 500 --format jsonl
  ✓ Scraped 248 tweets → raw_additional_tweets/penipuan_ewallet_qris/q1.jsonl
  → Converted to CSV: raw_additional_tweets/penipuan_ewallet_qris/q1.csv (248 rows)
...
```

---

## Realistic Volume Expectations

Berdasarkan retention analysis dari Phase 5:

| Vektor | Platform | Observed retention | Expected raw for ~400 relevan |
|--------|----------|--------------------|-----------------------------|
| ewallet | X | 9.2% | 4,300-5,000 tweets |
| ewallet | YouTube | 0.05% | ~8,000 komentar (tidak viable) |
| malware | X | ~2% | 7,000-10,000 tweets |
| malware | YouTube | 2.05% | 7,000-8,000 komentar |
| deepfake | X | 3.8% | 5,000-6,000 tweets |
| deepfake | YouTube | 2.7% | 7,000-8,000 komentar |
| peretasan | X | ~1-2% | 10,000+ tweets |
| peretasan | YouTube | ~2-3% | 7,000-8,000 komentar |

**Contoh ewallet:** 
- 6 queries × 500 limit = up to 3,000 tweets raw
- At 9.2% retention → ~276 relevan (di bawah target 400)
- **Solution:** Jika kurang, run fase lagi dengan queries tambahan atau turun limit untuk lebih fresh data

---

## Post-Scraping Workflow

Setelah Phase 4 selesai:

1. **Verifikasi output:**
   ```bash
   ls -lh raw_additional_tweets/
   # Seharusnya ada: penipuan_ewallet_qris/, malware_apk/, deepfake_penipuan_ai/, peretasan_pencurien_identitas/, _summary.json
   ```

2. **Count total tweets:**
   ```bash
   find raw_additional_tweets -name "*.csv" -exec wc -l {} + | tail -1
   ```

3. **Merge dengan YouTube (Phase 3 output):**
   ```bash
   # Pastikan raw_additional_youtube/ ada (dari Phase 3)
   # Kedua folder akan diproses oleh script merge (Phase 5 revisi)
   ```

4. **Re-run Phase 5 (consolidate) dengan data tambahan:**
   ```bash
   python src/phase5_consolidate_additional.py
   # Output: raw_combined/ (gabung old + new)
   # Lalu: unified_dataset_v2.csv (48.496 + new_rows)
   ```

5. **Re-run Phase 6-7 (preprocessing + Snorkel) pada dataset baru**

---

## Troubleshooting

**Q: "tweet-harvest not found"**  
A: `pip install tweet-harvest` (pastikan di venv yang sama dengan project)

**Q: "429 Too Many Requests"**  
A: Script otomatis throttle 2 detik antar-query. Jika masih dapat error, tunggu 10 menit, jalankan ulang.

**Q: "No tweets for query X"**  
A: Mungkin query terlalu spesifik atau tidak ada tweets matching 2023-2026 (ingat, snapshot 7 hari). Coba relaksasi query atau skip (akan catat di failed_queries).

**Q: Bearer token tidak valid**  
A: `export TWITTER_BEARER_TOKEN="..."` harus token valid dari Twitter API. Re-auth via `tweet-harvest --auth`.

**Q: Output files kosong**  
A: Kemungkinan tweet-harvest format berubah. Cek `_summary.json` untuk failed queries. Manual cek output format:
   ```bash
   head -c 200 raw_additional_tweets/penipuan_ewallet_qris/q1.jsonl
   ```

---

## Expected Retention Post-Merge

Setelah gabung YouTube + X dan re-run Snorkel Phase 7:

| Vektor | Before (raw 48.496) | Target raw new | Estimated relevan new | After total |
|--------|---------------------|-----------------|----------------------|-------------|
| ewallet | 23 | 4,500 | ~410 | 400-450 |
| malware | 36 | 8,000 | ~360-380 | 400-450 |
| deepfake | 62 | 6,000 | ~210-250 | 270-310 |
| peretasan | 46 | 10,000 | ~150-200 | 200-250 |

Target akhir: **≥350-400 per kelas lemah** untuk phase weights / focal loss di training (Phase 9).

---

## Query Customization (Jika Diperlukan)

Jika ingin tambah/edit queries, modifikasi `data/query_spec.json`:

```json
{
  "penipuan_ewallet_qris": {
    "queries": [
      "existing query",
      "\"new query pattern\" lang:id"
    ],
    "limit": 500,
    "lang": "id"
  }
}
```

Lalu jalankan `phase4_tweet_harvest.py` lagi — script akan menambahkan queries baru.

---

*Guide update: 20 Jun 2026*
