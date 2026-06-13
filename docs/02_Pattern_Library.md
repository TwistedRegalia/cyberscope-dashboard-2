# Pattern Library Documentation — E-ICTT v2.1

**Penelitian:** Klasifikasi Otomatis Diskursus Vektor Ancaman Siber pada Media Sosial Indonesia
**Versi:** 1.0
**Status:** Documentation Phase (Pre-Code)
**Author:** Ray
**Tanggal:** Mei 2026

---

## 0. Pendahuluan

### 0.1 Tujuan Dokumen

Dokumen ini berisi **regex pattern library** untuk 6 vektor E-ICTT v2.1. Pattern di sini akan dipakai di dua tempat dalam pipeline:

1. **Discovery Filter (Phase 5 roadmap)** — pattern longgar untuk menyaring kandidat kelas dari raw scraping output. Tujuan: high-recall, OK ada false positive.
2. **Snorkel Labeling Functions (Phase 7 roadmap)** — pattern ketat dengan konteks untuk weak supervision. Tujuan: high-precision per labeling function.

Setiap pattern di dokumen ini punya **dual purpose** — tergantung mode penggunaan, threshold confidence-nya akan berbeda.

### 0.2 Struktur Pattern per Vektor

Setiap vektor memiliki 6 komponen pattern:

| Komponen | Confidence | Tujuan |
|----------|-----------|--------|
| **Tier 1 — High Precision** | 0.85-0.95 | Pattern eksplisit yang hampir pasti match vektor |
| **Tier 2 — Medium Precision** | 0.60-0.85 | Pattern umum yang butuh context confirmation |
| **Tier 3 — Discovery** | 0.40-0.60 | Pattern broad untuk menangkap variasi linguistik |
| **Negation Guards** | Adjustment | Pattern yang menyesuaikan role atau menurunkan confidence |
| **Context Amplifiers** | Boost +0.10-0.20 | Pattern yang boost confidence bila co-occur dengan Tier |
| **Speaker Role Hints** | Metadata | Pattern untuk identifikasi R1-R5 |

### 0.3 Konvensi Penulisan Regex

Semua pattern dalam dokumen ini menggunakan **Python regex syntax** dengan flags `re.IGNORECASE | re.UNICODE` secara default. Konvensi yang dipakai:

- `\b` — word boundary
- `\W{0,N}` — non-word characters dengan max jarak N (untuk context window)
- `[\s_-]*` — separator variants (space, underscore, hyphen)
- `(?:...)` — non-capturing group (untuk performance)
- `\W*` — flexible separator (lebih longgar dari `[\s_-]*`)

### 0.4 Justifikasi Linguistik Umum

Pattern di dokumen ini dirancang untuk menangkap **5 jenis variasi linguistik** yang umum di media sosial Indonesia:

1. **Variasi ejaan** — adaptasi loanword Inggris dengan typo dan variasi fonetik
2. **Singkatan dan abreviasi** — gaya media sosial yang gemar menyingkat
3. **Slang dan eufemisme** — bahasa khas komunitas (judi, hacking, scam)
4. **Code-mixing** — campuran Indonesia-Inggris-Jawa
5. **Konteks semantik** — bigram/trigram dengan jarak fleksibel

---

## 1. Vektor: `phishing_rekayasa_sosial`

### 1.1 Definisi Operasional

Diskursus publik tentang vektor phishing dan rekayasa sosial — komunikasi yang menyamar sebagai entitas terpercaya untuk mencuri kredensial, OTP, atau data sensitif. Mencakup laporan korban, peringatan edukatif, diskusi jurnalistik, dan promosi pelaku.

### 1.2 Tier 1 — High Precision Patterns

**P1.1 — Variasi Ejaan "Phishing"**

```regex
\b[pf][iy]+s+h*i*n+g*\b
```

*Match:* phishing, pishing, phising, pissing, phissing
*Tidak match:* fishing (jika tanpa konteks digital)
*Justifikasi:* Karakter awal `[pf]` menangkap typo umum p→f. Vokal `[iy]+` menangkap "phishing" vs "physhing". Tail `h*i*n+g*` menangkap variasi seperti "phising" (tanpa h) atau "phishin" (tanpa g).

**P1.2 — OTP Modus Eksplisit**

```regex
(?:minta|kasih|kirim|share|berikan|kasi|kasih\s*tau)\W{0,20}(?:otp|kode\W{0,5}(?:verif|otp|rahasia|sms))
```

*Match:* "minta OTP", "kasih kode verifikasi", "kirim kode rahasia"
*Tidak match:* "OTP aman", "jangan kasih OTP" (tapi P1.2 + negation guard akan tangkap nuansa)
*Justifikasi:* Window `\W{0,20}` menangkap "minta kode OTP sekarang" dengan jarak fleksibel. Variasi "kasi" menangkap penulisan informal tanpa "h".

**P1.3 — Modus Telepon Mengaku Institusi**

```regex
(?:telp(?:on)?|nelpon|ditelp(?:on)?|telepon|telpon)\W{0,30}(?:ngaku|mengaku|katanya|bilang|claim)\W{0,40}(?:bank|bca|bri|bni|mandiri|cimb|btn|cs|shopee|tokped|gojek|grab|ovo|dana|gopay)
```

*Match:* "ditelpon ngaku dari BCA", "nelpon katanya CS Shopee", "telepon mengaku petugas bank"
*Justifikasi:* Pattern ini menangkap **trinity phishing**: aktor (telepon) + claim (ngaku) + target (institusi finansial). Window 30+40 cukup untuk variasi sintaksis Indonesia.

**P1.4 — Link Mencurigakan Eksplisit**

```regex
(?:link|tautan|url)\W{0,20}(?:mencurigakan|aneh|gak\s*jelas|phising|tipu|nipu|palsu|bohongan)
```

*Match:* "link mencurigakan", "tautan aneh", "url palsu"
*Justifikasi:* "Gak jelas" sebagai eufemisme Indonesia untuk "mencurigakan" sering muncul.

### 1.3 Tier 2 — Medium Precision Patterns

**P2.1 — Klaim Hadiah/Kuota Palsu**

```regex
(?:klaim|dapat|menang|dapet)\W{0,15}(?:hadiah|kuota|pulsa|undian|voucher|cashback|reward)\W{0,30}(?:link|klik|wa|whatsapp|sms|telegram)
```

*Match:* "klaim hadiah lewat link", "dapat voucher klik wa"
*Justifikasi:* Pattern ini menangkap **modus iming-iming** yang sangat khas phishing Indonesia (XL kuota, Telkomsel pulsa, dll).

**P2.2 — Modus Undangan/File**

```regex
(?:undangan|invitation|nikah|menikah|surat|tagihan)\W{0,20}(?:pdf|file|kirim|wa|whatsapp|telegram)
```

*Match:* "undangan nikah wa pdf", "surat tagihan kirim file"
*Catatan:* Pattern ini bisa overlap dengan `malware_apk` jika menyebut "apk". Resolusi: jika ada "apk" di teks, prioritas ke `malware_apk` (lihat hierarki Bagian 5.2 E-ICTT v2.1).

**P2.3 — Konteks Rekayasa Sosial**

```regex
(?:modus|trik|cara)\W{0,20}(?:penipu(?:an)?|scam|tipu|nipu|fraud|kriminal)
```

*Match:* "modus penipuan online", "trik scam baru", "cara nipu"
*Justifikasi:* Pattern meta-diskursif — orang yang membahas "modus" sering R3 (edukator).

### 1.4 Tier 3 — Discovery Patterns

**P3.1 — Narasi Korban Generik dengan Konteks Digital**

```regex
(?:kena|hampir\s*kena|nyaris)\W{0,15}(?:tipu|nipu|scam|tipu[\s-]*menipu)\W{0,40}(?:online|wa|sms|telp|link|email)
```

*Match:* "kena tipu online", "hampir kena scam via wa"
*Justifikasi:* Pattern broad untuk korban yang tidak spesifik menyebut "phishing" tapi mendeskripsikan pengalaman.

**P3.2 — Pertanyaan Investigatif**

```regex
(?:asli|palsu|bener|beneran|valid|fake)\W{0,5}(?:gak|kah|ya|sih|engga|enggak)?\W{0,30}(?:link|telp|wa|sms|email|nomor|orang)
```

*Match:* "asli gak ya link ini", "bener gak nomor yang kirim wa"
*Justifikasi:* Pertanyaan investigatif sering dari calon korban yang ragu — high signal untuk diskursus phishing.

### 1.5 Negation Guards

**G1.1 — Indikator Edukator (R3)**

```regex
(?:jangan|hindari|waspad[ai]|hati[\s-]*hati|cara\s*menghindari|tips|trik|cek|verifikasi|verif)
```

*Efek:* Bila pattern ini muncul bersamaan dengan Tier 1/2, **set speaker_role = R3** (edukator). Tidak mengubah label vektor.

**G1.2 — Indikator Pertanyaan/Ragu (R1 calon korban)**

```regex
(?:apakah|apa|gimana|gmn)\W{0,15}(?:ini|itu|nih)\W{0,15}(?:penipu(?:an)?|scam|tipu|asli|palsu)
```

*Efek:* Set speaker_role = R1 (korban/calon korban yang bertanya).

### 1.6 Context Amplifiers

**A1.1 — Entitas Kredensial**

```regex
(?:otp|password|pin|kode\s*verif|kode\s*rahasia|sandi|kata\s*sandi)
```

*Efek:* Bila co-occur dengan Tier 2 atau Tier 3, **boost confidence +0.15**.

**A1.2 — Entitas Finansial**

```regex
(?:rekening|saldo|m[\s-]*banking|atm|kartu\s*kredit|cc|debit)
```

*Efek:* Bila co-occur dengan Tier 2 atau Tier 3, **boost confidence +0.10**.

### 1.7 Contoh Aplikasi

**Teks contoh 1:**
> "Tadi pagi ada yg telpon ngaku dari BCA, katanya akun aku ada transaksi mencurigakan, suruh kasih OTP buat verifikasi. Untung aku langsung tutup teleponnya."

*Analisis:*
- Match P1.3 (telpon + ngaku + BCA) — confidence 0.90
- Match P1.2 (kasih OTP) — confidence 0.92
- Match A1.1 (OTP) — amplifier +0.15
- Match G1.2 (—) — tidak match
- **Final:** label `phishing_rekayasa_sosial`, role R1, confidence 0.95+

**Teks contoh 2:**
> "Reminder: Bank apa pun di Indonesia GAK PERNAH minta OTP, PIN, atau password lewat telepon/SMS/WA. Kalau ada yang minta, itu 100% penipu."

*Analisis:*
- Match P1.2 (minta OTP) — confidence 0.92
- Match A1.1 (OTP, PIN, password) — amplifier +0.15
- Match G1.1 (jangan-equivalent via "GAK PERNAH") — set R3
- **Final:** label `phishing_rekayasa_sosial`, role R3, confidence 0.90+

**Teks contoh 3 (false positive check):**
> "Saya suka fishing di laut tiap weekend"

*Analisis:*
- Match P1.1 (fishing) — confidence 0.85 (warning: false positive risk)
- Tidak match Tier 2 atau amplifier
- Tidak ada konteks digital
- **Final:** TIDAK label (confidence threshold tidak terlampaui karena tidak ada amplifier)

---

## 2. Vektor: `penipuan_ewallet_qris`

### 2.1 Definisi Operasional

Diskursus publik tentang penipuan spesifik pada ekosistem e-wallet (GoPay, OVO, DANA, ShopeePay) dan QRIS — termasuk QRIS palsu, manipulasi saldo, dan modus terkait.

### 2.2 Tier 1 — High Precision Patterns

**P1.1 — QRIS Palsu Eksplisit**

```regex
\bqris\b\W{0,15}(?:palsu|tempel|fake|bohongan|aspal|tipu|bodong)
```

*Match:* "QRIS palsu", "QRIS tempel", "qris aspal"
*Justifikasi:* "Tempel" adalah slang spesifik Indonesia untuk QRIS yang ditempel ilegal di tempat publik.

**P1.2 — Saldo E-wallet Hilang dengan Platform Eksplisit**

```regex
(?:saldo|isi)\W{0,5}(?:ovo|dana|gopay|shopeepay|spaylater|linkaja|ovopay)\W{0,30}(?:hilang|terkuras|raib|amblas|kuras|kosong|berkurang|amblas|abis)
```

*Match:* "saldo OVO hilang", "saldo DANA amblas", "saldo GoPay kuras"
*Justifikasi:* Kombinasi platform + verba kehilangan adalah signal sangat kuat.

**P1.3 — Modus Scan QR Balik**

```regex
(?:salah\s*transfer|salah\s*kirim|kelebihan)\W{0,40}(?:scan|qr|qris)\W{0,20}(?:balik|kembali|refund)
```

*Match:* "salah transfer minta scan QR balik", "kelebihan transfer scan qris kembali"
*Justifikasi:* Pattern ini menangkap **modus reverse scan** yang khas Indonesia.

### 2.3 Tier 2 — Medium Precision Patterns

**P2.1 — E-wallet + Penipuan Generik**

```regex
(?:ovo|dana|gopay|shopeepay|linkaja|jenius)\W{0,30}(?:tipu|nipu|scam|penipu(?:an)?|bobol|hack)
```

*Match:* "OVO kena tipu", "DANA scam", "GoPay dibobol"

**P2.2 — Modus Tukar Saldo / Top-up Palsu**

```regex
(?:tukar|tuker|topup|top[\s-]*up|isi[\s-]*ulang)\W{0,20}(?:saldo|ewallet|e-wallet|dompet[\s-]*digital)\W{0,30}(?:bonus|murah|cepet|palsu|tipu)
```

*Match:* "tukar saldo bonus", "topup murah", "isi ulang dompet digital palsu"

**P2.3 — QR/QRIS dengan Konteks Lokasi Publik**

```regex
\bqr(?:is)?\b\W{0,40}(?:parkir(?:an)?|kotak\s*amal|masjid|mushola|pom\s*bensin|toilet)
```

*Match:* "QRIS parkiran", "QR kotak amal masjid"
*Justifikasi:* Lokasi publik adalah indikator kuat QRIS palsu dalam konteks Indonesia.

### 2.4 Tier 3 — Discovery Patterns

**P3.1 — Saldo Hilang Generik**

```regex
(?:saldo|rekening)\W{0,20}(?:tiba[\s-]*tiba|mendadak|kosong|nol)\W{0,20}(?:hilang|amblas|kuras)?
```

*Match:* "saldo tiba-tiba kosong", "rekening mendadak nol"
*Catatan:* Pattern ini bisa overlap dengan `peretasan_pencurian_identitas`. Resolusi: jika menyebut e-wallet, prioritas `penipuan_ewallet_qris`.

**P3.2 — Modus Cashback/Promo Palsu E-wallet**

```regex
(?:cashback|promo|diskon|kupon)\W{0,30}(?:ovo|dana|gopay|shopeepay|linkaja|e[\s-]*wallet)\W{0,30}(?:palsu|bohong|tipu|fake)
```

*Match:* "cashback OVO palsu", "promo DANA bohongan"

### 2.5 Negation Guards

**G2.1 — Indikator Edukator (R3)**

```regex
(?:cara\s*cek|cek\s*qris|verifikasi\s*qris|hati[\s-]*hati|jangan\s*sembarang(?:an)?\s*scan)
```

**G2.2 — Indikator Diskusi Otoritas (R5)**

```regex
(?:bi|bank\s*indonesia|ojk|kominfo|aspi|asosiasi\s*pembayaran)
```

### 2.6 Context Amplifiers

**A2.1 — Entitas E-wallet Spesifik**

```regex
(?:ovo|dana|gopay|shopeepay|linkaja|jenius|spaylater|ewa|e[\s-]*wallet|dompet\s*digital)
```

*Efek:* Boost +0.15 bila co-occur dengan Tier 2/3.

**A2.2 — Verba Kehilangan Finansial**

```regex
(?:hilang|terkuras|raib|amblas|kuras|kosong|abis|berkurang|menghilang)
```

*Efek:* Boost +0.10.

### 2.7 Contoh Aplikasi

**Teks contoh 1:**
> "Saldo OVO aku amblas Rp 750rb setelah scan QRIS di parkiran liar dekat stasiun"

*Analisis:*
- Match P1.2 (saldo OVO amblas) — confidence 0.92
- Match P2.3 (QRIS parkiran) — confidence 0.78
- Match A2.1 (OVO) + A2.2 (amblas) — amplifier +0.25
- **Final:** label `penipuan_ewallet_qris`, role R1, confidence 0.95+

**Teks contoh 2:**
> "Lagi viral QRIS palsu di kotak amal masjid, saldo masuk ke rekening penipu bukan ke masjid"

*Analisis:*
- Match P1.1 (QRIS palsu) — confidence 0.95
- Match P2.3 (QRIS kotak amal masjid) — confidence 0.80
- Match G2.2 (—) tidak match
- **Final:** label `penipuan_ewallet_qris`, role R2 atau R5, confidence 0.95+

---

## 3. Vektor: `malware_apk`

### 3.1 Definisi Operasional

Diskursus publik tentang malware berbasis aplikasi Android (file .apk) yang disebar via WhatsApp, Telegram, SMS, atau platform messaging — termasuk modus undangan nikah, kurir paket, surat tilang, kartu fisik.

### 3.2 Tier 1 — High Precision Patterns

**P1.1 — APK + Modus Khas Indonesia**

```regex
\.?apk\b\W{0,30}(?:undangan|nikah|kurir|j[\s&]*t|jne|sicepat|paket|tilang|surat|kartu)
```

*Match:* "apk undangan", "apk kurir J&T", "apk tilang"
*Justifikasi:* Pattern ini menangkap **trinity malware Indonesia**: file extension + modus + delivery entity.

**P1.2 — APK + Penipuan Eksplisit**

```regex
\.?apk\b\W{0,30}(?:penipu(?:an)?|tipu|nipu|scam|bahaya|virus|malware|trojan)
```

*Match:* "apk penipuan", "apk tipu", "apk berbahaya"

**P1.3 — Kena APK / Install APK**

```regex
(?:kena|install|pasang|download|terkecoh)\W{0,15}(?:file\s*)?\.?apk\b
```

*Match:* "kena APK", "install file apk", "download apk", "pasang APK"

### 3.3 Tier 2 — Medium Precision Patterns

**P2.1 — APK + Sumber Mencurigakan**

```regex
\.?apk\b\W{0,30}(?:wa|whatsapp|telegram|sms|dm|kirim(?:an)?)
```

*Match:* "apk dari wa", "apk telegram", "apk kiriman sms"

**P2.2 — Modus Kurir/Paket Tanpa Eksplisit APK**

```regex
(?:kurir|paket|pengiriman|j[\s&]*t|jne|sicepat|posaja|ninja)\W{0,40}(?:foto|file|kirim|attach(?:ment)?)\W{0,20}(?:wa|whatsapp|telegram)
```

*Match:* "kurir J&T kirim foto paket via WA"
*Justifikasi:* Pattern ini menangkap modus yang belum eksplisit "apk" tapi mendeskripsikan modus klasik.

**P2.3 — Banking App Drained**

```regex
(?:m[\s-]*banking|mobile\s*banking|atm|saldo\s*bank)\W{0,30}(?:terkuras|kuras|amblas|hilang|raib|abis|bobol)
```

*Match:* "m-banking terkuras", "saldo bank amblas"
*Catatan:* Pattern ini bisa overlap dengan `peretasan_pencurian_identitas`. Resolusi: jika ada "APK" di context (3 kalimat sebelum/sesudah), prioritas `malware_apk`.

### 3.4 Tier 3 — Discovery Patterns

**P3.1 — Aplikasi Mencurigakan Generik**

```regex
(?:aplikasi|app|application)\W{0,15}(?:mencurigakan|aneh|gak\s*jelas|bahaya|tipu|scam|virus)
```

*Match:* "aplikasi mencurigakan", "app aneh"

**P3.2 — Install dari Luar Play Store**

```regex
(?:install|download|pasang)\W{0,30}(?:luar|bukan)\W{0,15}(?:play\s*store|playstore|google\s*play)
```

*Match:* "install dari luar play store", "download bukan dari playstore"

### 3.5 Negation Guards

**G3.1 — Indikator Edukator (R3)**

```regex
(?:jangan\s*install|hindari|hati[\s-]*hati|waspad[ai]|cek\s*izin|periksa\s*izin)
```

**G3.2 — Indikator Diskusi Otoritas (R5)**

```regex
(?:bssn|kominfo|csirt|cert|laporan\s*resmi|statistik)
```

### 3.6 Context Amplifiers

**A3.1 — Entitas Finansial Android**

```regex
(?:m[\s-]*banking|mobile\s*banking|bca|bri|bni|mandiri|livin|jago|seabank|blu)
```

*Efek:* Boost +0.15.

**A3.2 — Sumber Pengiriman**

```regex
(?:wa|whatsapp|telegram|sms|dm|grup\s*wa|grup\s*telegram)
```

*Efek:* Boost +0.10.

### 3.7 Contoh Aplikasi

**Teks contoh 1:**
> "Bapak saya kena APK undangan nikah, langsung saldo BCA Rp 23 juta amblas dalam 5 menit"

*Analisis:*
- Match P1.1 (apk undangan) — confidence 0.95
- Match P1.3 (kena APK) — confidence 0.93
- Match P2.3 (saldo bank amblas) — confidence 0.78
- Match A3.1 (BCA) — amplifier +0.15
- **Final:** label `malware_apk`, role R1 (saksi keluarga = R2 sebenarnya), confidence 0.95+

---

## 4. Vektor: `judi_online_pinjol`

### 4.1 Definisi Operasional

Diskursus publik tentang judi online ilegal (slot, casino, togel) dan pinjaman online ilegal (pinjol ilegal, fintech tidak terdaftar OJK) — mencakup promosi, laporan korban, dan diskusi kebijakan.

### 4.2 Tier 1 — High Precision Patterns

**P1.1 — Slang Judol Eksplisit**

```regex
\b(?:gacor|maxwin|rungkad|anti[\s-]*rungkad|wd\s*lancar|jp[\s-]*gede|jackpot[\s-]*hari[\s-]*ini)\b
```

*Match:* "gacor", "maxwin", "anti rungkad", "WD lancar", "JP gede"
*Justifikasi:* Slang ini sangat domain-specific judi online Indonesia dan hampir tidak ada konteks lain.

**P1.2 — Judi Online Eksplisit**

```regex
\b(?:judi\s*online|judol|jdl|judi\s*slot|slot\s*online|casino\s*online|togel\s*online)\b
```

*Match:* "judi online", "judol", "slot online"

**P1.3 — Pinjol Ilegal Eksplisit**

```regex
\bpinjol\b\W{0,15}(?:ilegal|gak\s*resmi|tidak\s*terdaftar|bodong|nakal|abal[\s-]*abal)
```

*Match:* "pinjol ilegal", "pinjol bodong", "pinjol abal-abal"

**P1.4 — Modus Penagihan Pinjol Kasar**

```regex
(?:diteror|teror|ancam(?:an)?|kasar|galak)\W{0,30}(?:pinjol|debt\s*collector|dc\b|penagih)
```

*Match:* "diteror pinjol", "penagih kasar"

### 4.3 Tier 2 — Medium Precision Patterns

**P2.1 — Pinjaman Online Generik**

```regex
(?:pinjaman|pinjam|hutang|utang)\W{0,15}(?:online|app|aplikasi)\W{0,30}(?:bunga|tinggi|cekik|gila|merampok)
```

*Match:* "pinjaman online bunga tinggi", "pinjam app aplikasi cekik"

**P2.2 — Sebar Data Pinjol**

```regex
(?:sebar|sebarkan|disebar)\W{0,20}(?:data|foto\s*ktp|kontak|nomor|wa)\W{0,30}(?:pinjol|debt|penagih)
```

*Match:* "sebar foto KTP pinjol", "data disebar penagih"

**P2.3 — Slot Generik dengan Konteks Promosi**

```regex
\bslot\b\W{0,30}(?:bonus|new\s*member|deposit|link|daftar|bio|register)
```

*Match:* "slot bonus new member", "slot link daftar di bio"

### 4.4 Tier 3 — Discovery Patterns

**P3.1 — Modal vs Hasil (Konteks Judol)**

```regex
(?:modal|deposit)\W{0,15}(?:rb|ribu|recehan|kecil|jt|juta)\W{0,40}(?:jadi|menang|wd|withdraw)\W{0,15}(?:jt|juta|m|miliar|gede)
```

*Match:* "modal 10rb jadi 10jt", "deposit recehan menang gede"
*Justifikasi:* Pattern promosi klasik judol — modal kecil hasil besar.

**P3.2 — OJK Terdaftar Cek**

```regex
(?:cek|periksa|verifikasi)\W{0,20}(?:ojk|sikapiuangmu|legal(?:itas)?)
```

*Match:* "cek OJK", "verifikasi legalitas"
*Note:* Ini umumnya R3 (edukator).

### 4.5 Negation Guards

**G4.1 — Indikator Edukator (R3)**

```regex
(?:jangan|hindari|stop|berhenti|jauhi|bahaya(?:nya)?|hancurkan)\W{0,15}(?:judol|judi|pinjol|slot)
```

**G4.2 — Indikator Korban Distress (R1)**

```regex
(?:hancur|bunuh\s*diri|mau\s*mati|stress|depresi|terjerat|terlilit)\W{0,30}(?:judol|judi|pinjol|hutang|utang)
```

### 4.6 Context Amplifiers

**A4.1 — Entitas Otoritas**

```regex
(?:ojk|sikapiuangmu|bssn|kominfo|satgas\s*pasti|satgas\s*waspada)
```

*Efek:* Boost +0.10, dan kemungkinan besar R5.

**A4.2 — Bahasa Promosi Klasik**

```regex
(?:link\s*di\s*bio|daftar\s*sekarang|bonus\s*100|new\s*member|wd\s*proses\s*cepat)
```

*Efek:* Boost +0.20, dan kemungkinan besar R4 (pelaku).

### 4.7 Contoh Aplikasi

**Teks contoh 1:**
> "Slot gacor maxwin 100jt, link daftar di bio, bonus new member 100%"

*Analisis:*
- Match P1.1 (gacor, maxwin) — confidence 0.95
- Match P2.3 (slot bonus new member) — confidence 0.80
- Match A4.2 (link di bio, bonus 100, new member) — amplifier +0.20
- **Final:** label `judi_online_pinjol`, role R4 (pelaku/promotor), confidence 0.97+

**Teks contoh 2:**
> "Sudah 3 bulan diteror penagih pinjol, foto KTP saya disebar ke seluruh kontak HP. Mau bunuh diri rasanya."

*Analisis:*
- Match P1.4 (diteror penagih pinjol) — confidence 0.92
- Match P2.2 (foto KTP disebar) — confidence 0.85
- Match G4.2 (bunuh diri + pinjol) — set R1 + flag for content warning
- **Final:** label `judi_online_pinjol`, role R1, confidence 0.95+
- **Catatan:** Konten dengan G4.2 perlu special handling dalam dataset (etika riset).

---

## 5. Vektor: `peretasan_pencurian_identitas`

### 5.1 Definisi Operasional

Diskursus publik tentang peretasan akun (sosial media, email, m-banking), pencurian data pribadi, kebocoran data, dan pencurian identitas digital.

### 5.2 Tier 1 — High Precision Patterns

**P1.1 — Akun Sosial Media Diretas**

```regex
(?:akun)\W{0,20}(?:ig|instagram|wa|whatsapp|fb|facebook|twitter|tiktok|tt|telegram|tg)\W{0,30}(?:diretas|dihack|dibobol|dibajak|dicuri|hilang|kena\s*hack)
```

*Match:* "akun IG diretas", "akun WA dibajak", "akun FB dihack"

**P1.2 — Kebocoran Data Skala Besar**

```regex
(?:kebocoran|bocor(?:an)?|leak(?:age)?)\W{0,30}(?:data|dukcapil|pdp|pribadi|nik|kk|ktp)
```

*Match:* "kebocoran data dukcapil", "leak NIK"

**P1.3 — Entitas Bjorka dan Kasus Spesifik**

```regex
\b(?:bjorka|hackerone|breach\s*forums?|raidforums?)\b
```

*Match:* "Bjorka", "Breach Forums"
*Justifikasi:* Nama-nama spesifik kasus peretasan Indonesia.

**P1.4 — SIM Swap Fraud**

```regex
(?:sim[\s-]*swap|tukar\s*sim|nomor\s*diambil\s*alih|nomor\s*dibajak)
```

*Match:* "SIM swap", "nomor dibajak"

### 5.3 Tier 2 — Medium Precision Patterns

**P2.1 — Pencurian Data Pribadi**

```regex
(?:curi|dicuri|pencurian|hilang)\W{0,20}(?:data|identitas|nik|ktp|kk|foto\s*ktp)
```

*Match:* "curi data pribadi", "pencurian identitas"

**P2.2 — Doxing**

```regex
\b(?:doxing|doxxing|dox(?:x)?ed|dox(?:x)?ing)\b|(?:sebar(?:kan)?|disebar)\W{0,20}(?:identitas|alamat|nomor|data\s*pribadi)
```

*Match:* "doxing", "sebar identitas", "alamat disebar"

**P2.3 — Akun Diambil Alih (Generik)**

```regex
(?:akun|aku|account)\W{0,30}(?:diambil\s*alih|takeover|takeover|hijack|dibobol)
```

*Match:* "akun diambil alih", "account dibobol"

### 5.4 Tier 3 — Discovery Patterns

**P3.1 — Akun Dipake Nipu**

```regex
(?:akun|aku|account)\W{0,20}(?:dipake|dipakai|disalahgunakan)\W{0,30}(?:nipu|tipu|scam|minta\s*pulsa|minta\s*transfer)
```

*Match:* "akun dipake nipu followers", "account disalahgunakan tipu"

**P3.2 — Jasa Pulihkan Akun (Eufemisme Pelaku)**

```regex
(?:jasa)\W{0,15}(?:pulihkan|kembalikan|recover|hack|bobol)\W{0,15}(?:akun|ig|wa|fb)
```

*Match:* "jasa pulihkan akun IG", "jasa hack WA"
*Justifikasi:* Eufemisme khas Indonesia untuk jasa hack ilegal.

### 5.5 Negation Guards

**G5.1 — Indikator Edukator (R3)**

```regex
(?:aktifkan|aktivasi)\W{0,10}(?:2fa|two[\s-]*factor|verifikasi\s*2\s*langkah)|password\s*manager|jangan\s*pakai\s*password\s*sama
```

**G5.2 — Indikator Pelaku (R4)**

```regex
(?:dm|kontak|hubungi|order)\W{0,30}(?:jasa|service)\W{0,20}(?:hack|bobol|pulihkan)
```

### 5.6 Context Amplifiers

**A5.1 — Platform Spesifik**

```regex
(?:ig|instagram|wa|whatsapp|fb|facebook|twitter|tiktok|gmail|shopee|tokped|tokopedia)
```

*Efek:* Boost +0.10.

**A5.2 — Verba Peretasan**

```regex
(?:hack|hacker|peretas|bobol|membobol|retas|meretas)
```

*Efek:* Boost +0.15.

### 5.7 Contoh Aplikasi

**Teks contoh 1:**
> "Akun IG saya 80k followers diretas, sekarang dipake nipu followers minta pulsa atas nama saya"

*Analisis:*
- Match P1.1 (akun IG diretas) — confidence 0.95
- Match P3.1 (akun dipake nipu, minta pulsa) — confidence 0.85
- Match A5.1 (IG) + A5.2 (diretas) — amplifier +0.25
- **Final:** label `peretasan_pencurian_identitas`, role R1, confidence 0.97+

---

## 6. Vektor: `deepfake_penipuan_ai`

### 6.1 Definisi Operasional

Diskursus publik tentang penyalahgunaan AI generatif untuk penipuan — deepfake video, voice cloning, AI scam content.

### 6.2 Tier 1 — High Precision Patterns

**P1.1 — Deepfake Eksplisit**

```regex
\b(?:deepfake|deep\s*fake|deep[\s-]*faked)\b
```

*Match:* "deepfake", "deep fake"

**P1.2 — Voice Cloning Eksplisit**

```regex
(?:voice|suara)\W{0,15}(?:clon(?:e|ing)|cloned|tiruan|palsu\s*ai|generated|ai)
```

*Match:* "voice cloning", "suara AI", "suara tiruan AI"

**P1.3 — Suara Mirip Keluarga + Modus Penipuan**

```regex
(?:suara|voice)\W{0,15}(?:mirip|sama|identik|kayak)\W{0,30}(?:anak|ortu|orang\s*tua|saudara|bapak|ibu|mama|papa)\W{0,40}(?:minta|transfer|kirim|urgent)
```

*Match:* "suara mirip anak minta transfer", "suara sama ibu kirim urgent"
*Justifikasi:* Pattern ini menangkap **modus klasik voice cloning Indonesia**.

### 6.3 Tier 2 — Medium Precision Patterns

**P2.1 — AI-Generated Content untuk Penipuan**

```regex
(?:ai|artificial\s*intelligence|chat\s*gpt|chatgpt|gemini|claude|llm)\W{0,30}(?:scam|tipu|nipu|penipu(?:an)?|fraud|generated)\W{0,30}(?:konten|content|gambar|foto|video|teks)
```

*Match:* "AI generated konten scam", "ChatGPT untuk tipu"

**P2.2 — Video Tokoh Publik untuk Promosi Scam**

```regex
(?:video|klip)\W{0,15}(?:jokowi|prabowo|sri\s*mulyani|erick\s*thohir|ridwan\s*kamil|anies)\W{0,40}(?:promosi|endorse|investasi|crypto|trading)
```

*Match:* "video Jokowi promosi crypto", "klip Prabowo endorse trading"
*Justifikasi:* Pattern menangkap kasus deepfake tokoh publik untuk scam investasi yang viral di Indonesia.

**P2.3 — Sextortion via AI**

```regex
(?:sextortion|ancam(?:an)?\s*sebar)\W{0,30}(?:foto|video|konten)\W{0,20}(?:ai|deepfake|generated|palsu)
```

*Match:* "sextortion video AI", "ancaman sebar foto deepfake"

### 6.4 Tier 3 — Discovery Patterns

**P3.1 — Telepon Suara Aneh + Minta Uang**

```regex
(?:ditelp(?:on)?|nelpon)\W{0,40}(?:suara\s*aneh|suara\s*beda|suara\s*gak\s*biasa)\W{0,40}(?:minta|transfer|kirim\s*uang)
```

*Match:* "ditelpon suara aneh minta transfer"

**P3.2 — Investasi Crypto/Trading Endorse Tokoh**

```regex
(?:investasi|trading|crypto|bitcoin)\W{0,30}(?:endorse|promosi|katanya|claim)\W{0,30}(?:tokoh|menteri|presiden|publik)
```

*Match:* "investasi crypto endorse menteri"

### 6.5 Negation Guards

**G6.1 — Indikator Edukator (R3)**

```regex
(?:safe[\s-]*word|kata\s*sandi\s*keluarga|verifikasi\s*video\s*call|deepfake\s*detection|cara\s*deteksi)
```

**G6.2 — Indikator Diskusi Akademis (R5)**

```regex
(?:penelitian|studi|riset|research|paper|jurnal)\W{0,30}(?:deepfake|ai\s*scam|voice\s*clon(?:e|ing))
```

### 6.6 Context Amplifiers

**A6.1 — Verba Penipuan Finansial**

```regex
(?:transfer|kirim\s*uang|wa\s*minta|tf\s*sekarang|urgent\s*kirim)
```

*Efek:* Boost +0.20 untuk Tier 2/3.

### 6.7 Contoh Aplikasi

**Teks contoh 1:**
> "Mama saya hampir transfer Rp 15 juta karena ditelpon suara mirip banget sama saya, ternyata AI voice clone"

*Analisis:*
- Match P1.3 (suara mirip + saya + Anda implicit) — confidence 0.85
- Match P1.2 (voice clone, AI) — confidence 0.92
- Match A6.1 (transfer) — amplifier +0.20
- **Final:** label `deepfake_penipuan_ai`, role R1 atau R2, confidence 0.95+

---

## 7. Aturan Kombinasi dan Prioritas

### 7.1 Hierarki Resolusi Multi-Match

Bila satu teks match dengan multiple Tier 1 dari berbagai vektor, gunakan **hierarki prioritas** sesuai E-ICTT v2.1 Bagian 5.2:

1. `malware_apk` > vektor lain (jika ada APK)
2. `deepfake_penipuan_ai` > vektor lain (jika ada AI element)
3. `phishing_rekayasa_sosial` > `peretasan_pencurian_identitas` (jika fokus modus)
4. `penipuan_ewallet_qris` > `phishing_rekayasa_sosial` (jika modus e-wallet specific)
5. `judi_online_pinjol` adalah kategori sui generis

### 7.2 Aggregasi Confidence

Untuk Snorkel weak supervision, confidence aggregation menggunakan formula:

```
confidence_final = max(tier_confidence) + sum(amplifier_boost) - sum(guard_penalty)
```

Capped pada [0.0, 1.0]. Threshold cutoff untuk weak label: **≥ 0.4** sesuai metodologi Anda.

### 7.3 Role Resolution

Speaker role ditentukan oleh urutan prioritas pattern:

1. Jika match Negation Guard untuk R3 → role = R3 (edukator)
2. Jika match Negation Guard untuk R4 → role = R4 (pelaku)
3. Jika match pattern korban distress → role = R1
4. Jika match konteks otoritas/jurnalistik → role = R5
5. Jika ambigu → role = R2 (default saksi/diskusi umum)

---

## 8. Validasi Pattern Library

### 8.1 Metrik Kualitas

Setiap pattern di-evaluate pada 3 metrik:

| Metrik | Target | Cara Ukur |
|--------|--------|-----------|
| Precision | ≥ 0.80 untuk Tier 1, ≥ 0.60 untuk Tier 2 | Manual annotation 50 match per pattern |
| Recall (per vektor) | ≥ 0.70 overall | Match rate pada gold standard 357 |
| Coverage | ≥ 60% dataset | % data ter-match minimum 1 pattern |

### 8.2 Proses Iterasi

1. **Initial:** Pattern v1 dari dokumen ini
2. **Pilot Validation:** Apply ke 500 sampel random, hitung Precision/Recall
3. **Refinement:** Adjust Tier boundaries, tambah/kurangi pattern berdasarkan error analysis
4. **Final Validation:** Apply ke gold standard 357, validate metrik final
5. **Documentation:** Update v1.x dengan pattern final

### 8.3 Dokumentasi Per Pattern

Setiap pattern di code Phase 7 harus punya:

```python
@labeling_function()
def lf_phishing_p1_1_variasi_ejaan(x):
    """
    Pattern P1.1 — Variasi Ejaan Phishing
    Tier: 1 (High Precision)
    Reference: Pattern Library Documentation v1.0, Bagian 1.2
    Justification: Menangkap variasi typo phishing yang umum di media sosial ID
    Expected precision: 0.85
    """
    if re.search(r"\b[pf][iy]+s+h*i*n+g*\b", x.text, re.IGNORECASE):
        return PHISHING
    return ABSTAIN
```

---

## 9. Catatan Versi

### v1.0 (Dokumen ini)

- 6 vektor lengkap dengan Tier 1/2/3
- Negation guards dan context amplifiers
- Speaker role hints
- Contoh aplikasi per vektor

### v1.1 (Direncanakan setelah Pilot Validation)

- Refinement pattern berdasarkan precision/recall di pilot
- Penambahan pattern untuk varian linguistik baru yang ditemukan
- Adjustment threshold confidence

### v2.0 (Future)

- Expansion ke bahasa daerah (Jawa, Sunda)
- Multi-label patterns untuk content yang valid menyentuh 2 vektor
- Time-aware patterns (slang yang berubah per kuartal)

---

*Akhir dokumen pattern library. Dokumen ini menjadi referensi utama untuk Phase 5 (Filter) dan Phase 7 (Snorkel LFs) di Technical Roadmap.*
