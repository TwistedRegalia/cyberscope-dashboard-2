# Log Eksekusi Scraping — Tweet Harvest (X) & YouTube Data API v3

Log terminal **verbatim** dari eksekusi Phase 4 (Tweet Harvest) dan Phase 3 (YouTube Data API v3),
diekstrak dari transkrip sesi Claude Code
`~/.claude/projects/c--Users-Ray-Siraj-PI2/17a9b10e-4f2d-4799-9c28-75ff41b02b16.jsonl`.

Output disalin apa adanya — tidak dirapikan, tidak diringkas. Nilai buktinya justru pada keasliannya.
Satu-satunya perubahan: nilai `auth_token` (cookie X) dan `YOUTUBE_API_KEY` diganti placeholder.

**Tool:** `npx tweet-harvest@latest` (Helmi Satria) — CLI Node.js + Chromium/Playwright.
Autentikasi memakai cookie `auth_token` dari sesi browser X, bukan developer bearer token.

**Jangan di-commit.** File ini hanya untuk dilihat / di-screenshot.

---

## Run — `penipuan_ewallet_qris`

| | |
|---|---|
| Waktu eksekusi | `2026-06-20T19:59:03.685942` |
| Tab | `LATEST` |
| Query spec | `data/query_spec.json` |
| Limit per query | 500 |
| Total tweet | **531** |
| Summary file | `raw_additional_tweets/_summary_penipuan_ewallet_qris.json` |

**Perintah (PowerShell, cwd = `C:\Users\Ray Siraj\PI2`):**

```powershell
$env:TWITTER_AUTH_TOKEN = "<AUTH_TOKEN_DIMASK>"
.venv\Scripts\python.exe src\phase4_tweet_harvest.py --vektor penipuan_ewallet_qris
```

**Output terminal:**

```text
[Phase 4] Menjalankan 1 vektor: penipuan_ewallet_qris

[penipuan_ewallet_qris] 6 queries, limit=500, tab=LATEST
[penipuan_ewallet_qris:q1] tweet-harvest -s ""qris palsu" OR "qris tempel" OR "qris bodong" lang:id" -l 500 --tab LATEST
  ✓ 367 tweets → raw_additional_tweets\penipuan_ewallet_qris\q1.csv
[penipuan_ewallet_qris:q2] tweet-harvest -s "(saldo) (ovo OR dana OR gopay) (hilang OR raib OR amblas) lang:id" -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\penipuan_ewallet_qris\q2.csv
[penipuan_ewallet_qris:q3] tweet-harvest -s "("scan qr" OR "scan barcode" OR "scan qris") (balik OR refund OR "sala..." -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\penipuan_ewallet_qris\q3.csv
[penipuan_ewallet_qris:q4] tweet-harvest -s "(cashback OR "top up" OR promo) (ovo OR dana OR gopay) (palsu OR tipu)..." -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\penipuan_ewallet_qris\q4.csv
[penipuan_ewallet_qris:q5] tweet-harvest -s "(admin OR cs) (dana OR ovo OR gopay) (palsu OR tipu) lang:id" -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\penipuan_ewallet_qris\q5.csv
[penipuan_ewallet_qris:q6] tweet-harvest -s ""qris kotak amal" OR "qris parkiran" OR "qris spbu" lang:id" -l 500 --tab LATEST
  ✓ 164 tweets → raw_additional_tweets\penipuan_ewallet_qris\q6.csv

[Phase 4 Summary]
  Vectors: 1
  Queries executed: 6
  Total tweets: 531
  Empty queries: 4
  Failed queries: 0
  Output: raw_additional_tweets/
  Summary: raw_additional_tweets\_summary_penipuan_ewallet_qris.json
=== EXIT: 0 ===
```

---

## Run — `malware_apk`

| | |
|---|---|
| Waktu eksekusi | `2026-06-20T22:16:22.883735` |
| Tab | `LATEST` |
| Query spec | `data/query_spec_v2.json` |
| Limit per query | 500 |
| Total tweet | **95** |
| Summary file | `raw_additional_tweets/_summary_malware_apk.json` |

**Perintah (PowerShell, cwd = `C:\Users\Ray Siraj\PI2`):**

```powershell
$env:TWITTER_AUTH_TOKEN = "<AUTH_TOKEN_DIMASK>"
.venv\Scripts\python.exe src\phase4_tweet_harvest.py --spec data/query_spec_v2.json --vektor malware_apk
```

**Output terminal:**

```text
[Phase 4] Menjalankan 1 vektor: malware_apk

[malware_apk] 7 queries, limit=500, tab=LATEST
[malware_apk:q1] tweet-harvest -s "("apk undangan" OR "apk nikah" OR "apk pernikahan") (rekening OR saldo..." -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\malware_apk\q1.csv
[malware_apk:q2] tweet-harvest -s ""apk penipuan" OR "apk bodong" OR "file apk penipuan" OR "apk modus" l..." -l 500 --tab LATEST
  ✓ 35 tweets → raw_additional_tweets\malware_apk\q2.csv
[malware_apk:q3] tweet-harvest -s "(apk) (kurir OR paket OR jnt OR tilang OR pajak OR pln OR bpjs OR "cek..." -l 500 --tab LATEST
  ✓ 11 tweets → raw_additional_tweets\malware_apk\q3.csv
[malware_apk:q4] tweet-harvest -s "("kena apk" OR "install apk" OR "klik apk" OR "download apk") (saldo O..." -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\malware_apk\q4.csv
[malware_apk:q5] tweet-harvest -s "(apk OR aplikasi) (sniffing OR sadap OR mbanking OR "bobol rekening") ..." -l 500 --tab LATEST
  ✓ 5 tweets → raw_additional_tweets\malware_apk\q5.csv
[malware_apk:q6] tweet-harvest -s "(apk OR malware) (bahaya OR waspada OR "hati-hati" OR modus OR penipua..." -l 500 --tab LATEST
  ✓ 44 tweets → raw_additional_tweets\malware_apk\q6.csv
[malware_apk:q7] tweet-harvest -s "("undangan digital" OR "undangan online" OR "undangan nikah") (apk OR ..." -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\malware_apk\q7.csv

[Phase 4 Summary]
  Vectors: 1
  Queries executed: 7
  Total tweets: 95
  Empty queries: 3
  Failed queries: 0
  Output: raw_additional_tweets/
  Summary: raw_additional_tweets\_summary_malware_apk.json
=== EXIT: 0 ===
```

---

## Run — `deepfake_penipuan_ai`

| | |
|---|---|
| Waktu eksekusi | `2026-06-21T00:03:36.334048` |
| Tab | `LATEST` |
| Query spec | `data/query_spec_v2.json` |
| Limit per query | 500 |
| Total tweet | **549** |
| Summary file | `raw_additional_tweets/_summary_deepfake_penipuan_ai.json` |

**Perintah (PowerShell, cwd = `C:\Users\Ray Siraj\PI2`):**

```powershell
$env:TWITTER_AUTH_TOKEN = "<AUTH_TOKEN_DIMASK>"
.venv\Scripts\python.exe src\phase4_tweet_harvest.py --spec data/query_spec_v2.json --vektor deepfake_penipuan_ai
```

**Output terminal:**

```text
[Phase 4] Menjalankan 1 vektor: deepfake_penipuan_ai

[deepfake_penipuan_ai] 7 queries, limit=500, tab=LATEST
[deepfake_penipuan_ai:q1] tweet-harvest -s "("voice cloning" OR "suara ai" OR "voice ai" OR "kloning suara") (peni..." -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\deepfake_penipuan_ai\q1.csv
[deepfake_penipuan_ai:q2] tweet-harvest -s "deepfake (investasi OR crypto OR giveaway OR penipuan OR scam) lang:id" -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\deepfake_penipuan_ai\q2.csv
[deepfake_penipuan_ai:q3] tweet-harvest -s "deepfake (penipuan OR scam OR tipu OR bodong OR modus OR palsu) lang:i..." -l 500 --tab LATEST
  ⚠ 0 tweets (tidak ada hasil untuk query ini)
[deepfake_penipuan_ai:q4] tweet-harvest -s "("video call palsu" OR "ai palsu" OR "video editan" OR "wajah palsu") ..." -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\deepfake_penipuan_ai\q4.csv
[deepfake_penipuan_ai:q5] tweet-harvest -s "deepfake (suara OR video OR wajah OR mirip OR palsu) lang:id" -l 500 --tab LATEST
  ✓ 0 tweets → raw_additional_tweets\deepfake_penipuan_ai\q5.csv
[deepfake_penipuan_ai:q6] tweet-harvest -s ""deteksi deepfake" OR "cek deepfake" OR "ciri deepfake" OR "cara tahu ..." -l 500 --tab LATEST
  ✓ 31 tweets → raw_additional_tweets\deepfake_penipuan_ai\q6.csv
[deepfake_penipuan_ai:q7] tweet-harvest -s ""penipuan ai" OR "scam ai" OR "tipu pakai ai" OR "modus ai" lang:id" -l 500 --tab LATEST
  ✓ 518 tweets → raw_additional_tweets\deepfake_penipuan_ai\q7.csv

[Phase 4 Summary]
  Vectors: 1
  Queries executed: 7
  Total tweets: 549
  Empty queries: 5
  Failed queries: 0
  Output: raw_additional_tweets/
  Summary: raw_additional_tweets\_summary_deepfake_penipuan_ai.json
=== EXIT: 0 ===
```

---

## Run — `peretasan_pencurian_identitas`

| | |
|---|---|
| Waktu eksekusi | `2026-06-21T00:23:31.744479` |
| Tab | `LATEST` |
| Query spec | `data/query_spec_v2.json` |
| Limit per query | 500 |
| Total tweet | **1344** |
| Summary file | `raw_additional_tweets/_summary_peretasan_pencurian_identitas.json` |

**Perintah (PowerShell, cwd = `C:\Users\Ray Siraj\PI2`):**

```powershell
$env:TWITTER_AUTH_TOKEN = "<AUTH_TOKEN_DIMASK>"
.venv\Scripts\python.exe src\phase4_tweet_harvest.py --spec data/query_spec_v2.json --vektor peretasan_pencurian_identitas
```

**Output terminal:**

```text
[Phase 4] Menjalankan 1 vektor: peretasan_pencurian_identitas

[peretasan_pencurian_identitas] 7 queries, limit=500, tab=LATEST
[peretasan_pencurian_identitas:q1] tweet-harvest -s "(akun OR email OR instagram OR ig OR facebook OR wa OR whatsapp) (dire..." -l 500 --tab LATEST
  ✓ 204 tweets → raw_additional_tweets\peretasan_pencurian_identitas\q1.csv
[peretasan_pencurian_identitas:q2] tweet-harvest -s ""kebocoran data" OR "data bocor" OR "data pribadi bocor" OR "kebocoran..." -l 500 --tab LATEST
  ✓ 280 tweets → raw_additional_tweets\peretasan_pencurian_identitas\q2.csv
[peretasan_pencurian_identitas:q3] tweet-harvest -s ""sim swap" OR "sim swapping" OR "nomor diambil alih" OR "nomor dibajak..." -l 500 --tab LATEST
  ⚠ 0 tweets (tidak ada hasil untuk query ini)
[peretasan_pencurian_identitas:q4] tweet-harvest -s "(doxing OR "data pribadi disebar" OR "alamat dibocorkan" OR "foto dise..." -l 500 --tab LATEST
  ⚠ 0 tweets (tidak ada hasil untuk query ini)
[peretasan_pencurian_identitas:q5] tweet-harvest -s "(pencurian OR curi OR dicuri OR mencuri) (identitas OR "data pribadi" ..." -l 500 --tab LATEST
  ⚠ 0 tweets (tidak ada hasil untuk query ini)
[peretasan_pencurian_identitas:q6] tweet-harvest -s ""jasa hack" OR "jasa bobol" OR "hacker online" OR "jasa pulihkan akun"..." -l 500 --tab LATEST
  ✓ 500 tweets → raw_additional_tweets\peretasan_pencurian_identitas\q6.csv
[peretasan_pencurian_identitas:q7] tweet-harvest -s ""akun saya diretas" OR "akun dihack" OR "ig dibobol" OR "wa dibajak" O..." -l 500 --tab LATEST
  ✓ 360 tweets → raw_additional_tweets\peretasan_pencurian_identitas\q7.csv

[Phase 4 Summary]
  Vectors: 1
  Queries executed: 7
  Total tweets: 1344
  Empty queries: 3
  Failed queries: 0
  Output: raw_additional_tweets/
  Summary: raw_additional_tweets\_summary_peretasan_pencurian_identitas.json
=== EXIT: 0 ===
```

---

## Run — `malware_apk (tab TOP)`

| | |
|---|---|
| Waktu eksekusi | `2026-06-21T00:44:34.749466` |
| Tab | `TOP` |
| Query spec | `data/query_spec_v2.json` |
| Limit per query | 500 |
| Total tweet | **49** |
| Summary file | `raw_additional_tweets/_summary_malware_apk_top.json` |

**Perintah (PowerShell, cwd = `C:\Users\Ray Siraj\PI2`):**

```powershell
$env:TWITTER_AUTH_TOKEN = "<AUTH_TOKEN_DIMASK>"
.venv\Scripts\python.exe src\phase4_tweet_harvest.py --spec data/query_spec_v2.json --vektor malware_apk --tab TOP
```

**Output terminal:**

```text
[Phase 4] Menjalankan 1 vektor: malware_apk

[malware_apk] 7 queries, limit=500, tab=TOP
[malware_apk:q1] tweet-harvest -s "("apk undangan" OR "apk nikah" OR "apk pernikahan") (rekening OR saldo..." -l 500 --tab TOP
  ⚠ 0 tweets (tidak ada hasil untuk query ini)
[malware_apk:q2] tweet-harvest -s ""apk penipuan" OR "apk bodong" OR "file apk penipuan" OR "apk modus" l..." -l 500 --tab TOP
  ⚠ 0 tweets (tidak ada hasil untuk query ini)
[malware_apk:q3] tweet-harvest -s "(apk) (kurir OR paket OR jnt OR tilang OR pajak OR pln OR bpjs OR "cek..." -l 500 --tab TOP
  ⚠ 0 tweets (tidak ada hasil untuk query ini)
[malware_apk:q4] tweet-harvest -s "("kena apk" OR "install apk" OR "klik apk" OR "download apk") (saldo O..." -l 500 --tab TOP
  ✓ 0 tweets → raw_additional_tweets\malware_apk\q4_top.csv
[malware_apk:q5] tweet-harvest -s "(apk OR aplikasi) (sniffing OR sadap OR mbanking OR "bobol rekening") ..." -l 500 --tab TOP
  ✓ 5 tweets → raw_additional_tweets\malware_apk\q5_top.csv
[malware_apk:q6] tweet-harvest -s "(apk OR malware) (bahaya OR waspada OR "hati-hati" OR modus OR penipua..." -l 500 --tab TOP
  ✓ 44 tweets → raw_additional_tweets\malware_apk\q6_top.csv
[malware_apk:q7] tweet-harvest -s "("undangan digital" OR "undangan online" OR "undangan nikah") (apk OR ..." -l 500 --tab TOP
  ✓ 0 tweets → raw_additional_tweets\malware_apk\q7_top.csv

[Phase 4 Summary]
  Vectors: 1
  Queries executed: 7
  Total tweets: 49
  Empty queries: 5
  Failed queries: 0
  Output: raw_additional_tweets/
  Summary: raw_additional_tweets\_summary_malware_apk_top.json
=== EXIT: 0 ===
```

---

## Run — Phase 3, YouTube Data API v3

Log yang ter-capture di transkrip **parsial** (snapshot interim saat proses masih berjalan — 3 dari 8 video). Run selesai penuh: 8 video, 6.663 komentar, output di `raw_additional_youtube/`.

**Perintah:**

```powershell
$env:YOUTUBE_API_KEY = "<YOUTUBE_API_KEY_DIMASK>"
.venv\Scripts\python.exe src\phase3_youtube_scrape.py
```

**Output terminal (parsial):**

```text
[Phase 3] Scraping 8 videos from data\video_candidates.csv
[malware_apk] Scraping WSuZimJFmnQ (Undangan Nikah (APK Virus) ini kita instal..!!!)...
  → Scraped 1077 comments from WSuZimJFmnQ
  ✓ Saved 1077 comments to raw_additional_youtube\malware_apk\WSuZimJFmnQ.csv
[malware_apk] Scraping BzmlRE8xRMU (Jadi Korban Phising Undangan Nikah Via WA Uang Rp1.4 Miliar Raib | Kabar Siang)...
  → Scraped 1240 comments from BzmlRE8xRMU
  ✓ Saved 1240 comments to raw_additional_youtube\malware_apk\BzmlRE8xRMU.csv
[malware_apk] Scraping kwCAtmS6gHY (PENIPUAN UNDANGAN WHATSAPP PERNIKAHAN serta Solusinya)...
```

---

## Verifikasi Output di Disk

| Vektor | File | Baris data |
|---|---|---|
| `deepfake_penipuan_ai` | `q1.csv` | 0 |
| `deepfake_penipuan_ai` | `q2.csv` | 0 |
| `deepfake_penipuan_ai` | `q4.csv` | 0 |
| `deepfake_penipuan_ai` | `q5.csv` | 0 |
| `deepfake_penipuan_ai` | `q6.csv` | 31 |
| `deepfake_penipuan_ai` | `q7.csv` | 518 |
| `malware_apk` | `q1.csv` | 0 |
| `malware_apk` | `q2.csv` | 35 |
| `malware_apk` | `q3.csv` | 11 |
| `malware_apk` | `q4.csv` | 0 |
| `malware_apk` | `q4_top.csv` | 0 |
| `malware_apk` | `q5.csv` | 5 |
| `malware_apk` | `q5_top.csv` | 5 |
| `malware_apk` | `q6.csv` | 44 |
| `malware_apk` | `q6_top.csv` | 44 |
| `malware_apk` | `q7.csv` | 0 |
| `malware_apk` | `q7_top.csv` | 0 |
| `penipuan_ewallet_qris` | `q1.csv` | 367 |
| `penipuan_ewallet_qris` | `q2.csv` | 0 |
| `penipuan_ewallet_qris` | `q3.csv` | 0 |
| `penipuan_ewallet_qris` | `q4.csv` | 0 |
| `penipuan_ewallet_qris` | `q5.csv` | 0 |
| `penipuan_ewallet_qris` | `q6.csv` | 164 |
| `peretasan_pencurian_identitas` | `q1.csv` | 204 |
| `peretasan_pencurian_identitas` | `q2.csv` | 280 |
| `peretasan_pencurian_identitas` | `q6.csv` | 500 |
| `peretasan_pencurian_identitas` | `q7.csv` | 360 |
| | **TOTAL** | **2568** |

| Video YouTube | Komentar |
|---|---|
| `deepfake_penipuan_ai/ITOOU6SEFeY.csv` | 1217 |
| `malware_apk/BzmlRE8xRMU.csv` | 1240 |
| `malware_apk/EMRjGpd3Lgs.csv` | 807 |
| `malware_apk/kwCAtmS6gHY.csv` | 900 |
| `malware_apk/LGb-OVrI9c0.csv` | 341 |
| `malware_apk/W98rn22grBs.csv` | 205 |
| `malware_apk/WbTVicAk82Q.csv` | 876 |
| `malware_apk/WSuZimJFmnQ.csv` | 1077 |
| **TOTAL** | **6663** |

---

## Lampiran — Riwayat PowerShell (`ConsoleHost_history.txt`, baris 670–705)

Jejak di prompt PowerShell. Perhatikan `npx tweet-harvest@latest` tercatat tanpa argumen (dijalankan interaktif pada fase PI), sedangkan run Phase 4 di atas dijalankan lewat script.

```text
 670  cd PI
 671  npx tweet-harvest@latest
 672  npx tweet-harvest@latest
 673  pip install pandas openpyxl
 674  /c:/Users/Ray Siraj/PI/.venv/Scripts/python.exe -m pip install pandas openpyxl
 675  pip install pandas openpyxl
 676  cd C:\Users\Ray Siraj\PI`
 677  python build_master_csv.py
 678  python master_csv.py 
 679  python testing_dataset.py
 680  python penipuan-tweets-data.py
 681  python master_csv.py
 682  python master_csv.py
 683  python master_csv.py
 684  (Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& "c:\Users\Ray Siraj\PI\.venv\Scripts\Activate.ps1")
 685  (Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& "c:\Users\Ray Siraj\PI\.venv\Scripts\Activate.ps1")
 686  python master_csv.py
 687  python -m pip install pandas
 688  python master_csv.py
 689  python diagnose_dataset.py
 690  python master_csv.py
 691  python diagnose_x.py
 692  python master_csv.py
 693  Copy-Item (Get-PSReadLineOption).HistorySavePath .\powershell-history.txt
 694  (Get-PSReadLineOption).HistorySavePath
 695  (Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& "c:\Users\Ray Siraj\PI\.venv\Scripts\Activate.ps1")
 696  (Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& "c:\Users\Ray Siraj\PI\.venv\Scripts\Activate.ps1")
 697  .venv\Scripts\Activate.ps1
 698  py -m venv .venv
 699  .venv\Scripts\Activate.ps1
 700  pip install snorkel
 701  deactivate
 702  .venv\Scripts\Activate.ps1
 703  pip install snorkel
 704  (Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& "c:\Users\Ray Siraj\PI2\.venv\Scripts\Activate.ps1")
 705  python phase3_youtube_scrape.py
```
