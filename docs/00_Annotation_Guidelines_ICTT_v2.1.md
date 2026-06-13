# Annotation Guidelines — Extended Indonesian Cybercrime Threat Taxonomy (E-ICTT v2.1)

**Untuk Penelitian:** Klasifikasi Otomatis Diskursus Vektor Ancaman Siber pada Media Sosial Indonesia Menggunakan Pendekatan Hybrid Machine Learning Berbasis OSINT dan Explainable AI

**Versi Dokumen:** 2.1 (Revised — faithful to Arifman 2026, expanded discursive coverage)
**Penulis:** Ray (peneliti utama)
**Konteks:** Penelitian skripsi S1, ekstensi dari Arifman et al. (2026) dengan inspirasi metodologis dari Kristiansen et al. (2020)

---

## 1. Pendahuluan

### 1.1 Tujuan Dokumen

Dokumen ini berfungsi sebagai pedoman operasional bagi anotator manusia maupun perancang *labeling functions* (Snorkel) untuk mengklasifikasikan komentar YouTube dan tweet X berbahasa Indonesia ke dalam taksonomi E-ICTT v2.1. Tujuan utamanya adalah memastikan konsistensi anotasi antarpekerja (*inter-annotator agreement*) dan memberikan justifikasi metodologis yang dapat dipertanggungjawabkan secara akademis.

### 1.2 Filosofi Taksonomi: Diskursus Penuh, Bukan Tindakan

**Prinsip fundamental:** E-ICTT v2.1 mengklasifikasikan **diskursus publik tentang vektor ancaman siber**, bukan tindakan serangan siber yang sedang dilakukan melalui platform media sosial. Anotator harus selalu mengingat bahwa mayoritas konten media sosial berbentuk laporan pengalaman, peringatan edukatif, atau diskusi publik — bukan tindakan serangan langsung.

**Konsekuensi operasional kunci:** Setiap label vektor dalam E-ICTT v2.1 **secara inheren mencakup spektrum diskursif penuh**, yaitu:

1. **Laporan pengalaman korban** — narasi pengguna yang menjadi sasaran/korban vektor tersebut
2. **Peringatan edukatif** — tips, warning, atau panduan menghindari vektor tersebut
3. **Diskusi publik/jurnalistik** — pemberitaan, statistik, atau pembahasan kebijakan terkait vektor tersebut
4. **Promosi/tindakan pelaku** — konten yang mempromosikan atau memfasilitasi vektor tersebut (frekuensi rendah)
5. **Refleksi/sarkasme sosial** — komentar ironis, satir, atau kritik sosial terhadap vektor tersebut

Maka, "Tips menghindari phishing" tetap dilabeli `phishing_rekayasa_sosial` (sebagai diskursus edukatif tentang vektor phishing), bukan dialihkan ke label terpisah. Prinsip parsimony ini menjaga konsistensi taksonomi dengan kerangka Arifman 2026 sambil memperluas cakupan diskursif setiap label.

### 1.3 Posisi Terhadap Arifman et al. (2026)

E-ICTT v2.1 mempertahankan **6 label vektor** dari kerangka Arifman et al. (2026) sebagai struktur taksonomi inti, namun memperluas tiga dimensi:

| Dimensi | Arifman 2026 | E-ICTT v2.1 |
|---------|--------------|-------------|
| Jumlah label vektor | 5 (Indonesian Cybercrime Threat Taxonomy) | 6 (penambahan `deepfake_penipuan_ai` untuk vektor emerging) |
| Cakupan diskursif | Implisit | **Eksplisit mencakup 5 jenis diskursus per label** |
| Sumber data | X/Twitter (2.344 sampel) | YouTube + X (14.445 sampel preprocessed) |
| Metadata anotasi | Label tunggal | Label + speaker role (R1-R5) |
| Pipeline klasifikasi | Single-stage | Two-layer (relevance filter + vector classification) |

Penambahan label ke-6 (`deepfake_penipuan_ai`) dijustifikasi karena vektor ini merupakan ancaman emerging signifikan pasca-2024 yang belum tercakup dalam taksonomi Arifman, dan secara empiris terdistribusi cukup di dataset Anda untuk diperlakukan sebagai kategori tersendiri.

### 1.4 Cara Menggunakan Dokumen Ini

1. Baca seluruh Bagian 2 (Prinsip Umum) sebelum mulai menganotasi
2. Untuk setiap data point, jalankan **decision tree** di Bagian 5
3. Bila ragu, konsultasikan Bagian 4 (definisi per label) dan Bagian 6 (boundary cases)
4. Catat semua kasus ambigu untuk pembahasan reviewer

---

## 2. Prinsip Umum Anotasi

### 2.1 Arsitektur Klasifikasi Dua Lapis

E-ICTT v2.1 menggunakan pipeline dua lapis yang terinspirasi dari Kristiansen et al. (2020), namun dengan taksonomi orisinal:

- **Layer 1 — Relevance Filter (binary):** menentukan apakah konten berkaitan dengan vektor ancaman siber spesifik atau tidak. Output: `relevan` atau `tidak_relevan`.
- **Layer 2 — Vector Classification (multi-class):** menentukan vektor ancaman spesifik untuk konten yang lolos Layer 1. Output: salah satu dari 6 label E-ICTT v2.1.

Setiap data point dianotasi pada kedua layer secara berurutan.

### 2.2 Kriteria "Anchor" untuk Relevansi

Konten dianggap **relevan** (lolos Layer 1) hanya bila terdapat *anchor* ke vektor ancaman spesifik, yaitu salah satu dari:

- Penyebutan eksplisit istilah/modus dari salah satu 6 vektor (lihat glossary di Bagian 9)
- Penyebutan implisit yang dapat di-trace ke vektor tertentu (misal "saldo amblas" + konteks scan → e-wallet)
- Laporan pengalaman, peringatan, atau diskusi yang substansinya menyentuh modus operandi vektor tertentu

Konten yang membahas keamanan siber secara generik tanpa anchor ke vektor spesifik (misal "ayo jaga data pribadi" tanpa konteks) → `tidak_relevan`. Ini menjaga taksonomi tetap **vector-focused** dan tidak melebar ke domain general cybersecurity awareness yang di luar scope penelitian.

### 2.3 Kategorisasi Peran Pembicara (Speaker Role)

Untuk setiap konten yang dilabeli sebagai relevan, anotator wajib mengidentifikasi peran pembicara sebagai **metadata tambahan** (tidak menggantikan label vektor, melainkan melengkapinya):

| Kode | Peran | Deskripsi |
|------|-------|-----------|
| `R1` | Korban | Pembicara melaporkan pengalaman pribadi sebagai sasaran/korban ancaman |
| `R2` | Saksi | Pembicara melaporkan pengalaman orang lain yang dikenal atau kasus publik |
| `R3` | Edukator | Pembicara memberi peringatan, tips keamanan, atau informasi protektif |
| `R4` | Pelaku | Pembicara mempromosikan, menawarkan, atau memfasilitasi tindakan siber ilegal |
| `R5` | Netral/Jurnalistik | Pembicara mendiskusikan ancaman secara akademis/jurnalistik tanpa pengalaman pribadi |

Metadata peran ini penting untuk:

- Analisis komposisi dataset di Bab 4 tesis
- Future work multi-task learning (vector + role)
- Validasi kualitas data (jika 99% data adalah `R5` netral, ada bias sampling)
- Defense saat sidang: menjawab kritik "kenapa korban dan pelaku punya label yang sama"

### 2.4 Aturan Label Tunggal (Single-Label)

Untuk versi 2.1, satu konten dilabeli dengan **satu label dominan** dari Layer 2. Bila konten menyentuh dua vektor sekaligus, gunakan **hierarki prioritas** di Bagian 5.2.

### 2.5 Konteks Linguistik Indonesia

Anotator harus mempertimbangkan:

- **Slang dan singkatan:** "gacor", "WD" (withdraw), "JP" (jackpot), "limit", "topup", "saldo amblas"
- **Code-mixing:** percampuran Bahasa Indonesia, Inggris, dan bahasa daerah
- **Eufemisme:** "main slot" (judi online), "jasa pulihkan akun" (peretasan), "investasi crypto" (kadang scam)
- **Ironi dan sarkasme:** "wah modal recehan jadi miliaran, the power of slot online" — konteks ironis terhadap promosi judi

### 2.6 Sumber Data dan Karakteristiknya

| Platform | Karakteristik | Implikasi Anotasi |
|----------|---------------|-------------------|
| YouTube comments | Lebih panjang, naratif, banyak laporan korban | Banyak `R1`, `R2`, `R3` |
| X (Twitter) | Pendek, padat, sering edukatif/promosi | Banyak `R3`, `R4`, `R5` |

Anotator harus menyesuaikan ekspektasi berdasarkan platform asal.

---

## 3. Layer 1 — Relevance Filter

### 3.1 Label: `relevan`

**Definisi:** Konten yang secara substantif berkaitan dengan salah satu 6 vektor ancaman siber E-ICTT, baik sebagai laporan pengalaman, peringatan, diskusi, maupun promosi/tindakan.

**Kriteria inklusi (minimal satu terpenuhi, dengan anchor ke vektor spesifik):**

- Menyebut vektor ancaman spesifik (phishing, QRIS palsu, APK, judol, pinjol ilegal, peretasan, deepfake)
- Menyebut modus serangan terkait vektor tertentu (Telegram scam, link WA, OTP, dll)
- Melaporkan kerugian finansial/data akibat vektor spesifik
- Memberi tips/peringatan keamanan tentang vektor tertentu
- Mempromosikan layanan ilegal terkait vektor (jasa hack, slot, pinjol ilegal)
- Menyebut entitas pelaku/kasus terkait vektor (Bjorka, kebocoran dukcapil, dll)
- Berita/statistik tentang vektor spesifik dari otoritas (BSSN, OJK, Kominfo)

**Kriteria eksklusi:**

- Tidak menyebut konteks vektor sama sekali
- Reaksi emosional umum tanpa substansi ("ngeri banget", "kacau")
- Spam komersial non-siber (jualan baju, kuliner)
- Konten cybersecurity generik tanpa anchor ke vektor spesifik ("ayo jaga data pribadi" tanpa konteks)

**Contoh `relevan`:**

> "Tadi aku dapet WA katanya dari Shopee, suruh klik link buat klaim hadiah. Untung gak aku klik." → anchor: phishing via link WA

> "Cara cek apakah QRIS palsu: pastikan nama merchant sesuai sama toko fisiknya." → anchor: QRIS palsu

> "WD lancar bos, slot pragmatic anti rungkad, link di bio." → anchor: promosi judol

> "BSSN merilis statistik serangan APK meningkat 40% Q3 2024" → anchor: malware APK

**Contoh `tidak_relevan`:**

> "Wah jaman sekarang serem banget ya" → tidak ada anchor

> "Saya beli baju online kemarin kualitasnya jelek" → non-siber

> "Anjir kacau bgt dunia sekarang 😭" → tidak ada anchor

> "Ayo bersama jaga keamanan data pribadi kita" → cybersecurity generik tanpa anchor vektor

### 3.2 Label: `tidak_relevan`

**Definisi:** Konten tanpa muatan substantif terkait vektor ancaman siber spesifik E-ICTT.

**Sub-kategori (opsional, untuk analisis):**

- `tr_komersial` — spam jualan non-siber
- `tr_emosional` — reaksi umum tanpa substansi
- `tr_offtopic` — diskusi yang sama sekali tidak berkaitan
- `tr_generik_siber` — cybersecurity generik tanpa anchor vektor
- `tr_ambigu` — menyebut istilah cyber tapi tidak substantif

**Tips operasional:** Jika anotator menghabiskan lebih dari 30 detik untuk memutuskan, kemungkinan besar konten tersebut adalah `tr_ambigu` — labeli sebagai `tidak_relevan`.

---

## 4. Layer 2 — Vector Classification

### 4.1 Label: `phishing_rekayasa_sosial`

**Definisi:** Diskursus publik yang berkaitan dengan vektor phishing dan rekayasa sosial — upaya menipu korban melalui komunikasi yang menyamar sebagai entitas terpercaya untuk mendapatkan kredensial, OTP, atau data sensitif. Label ini mencakup **seluruh spektrum diskursif**: laporan korban, peringatan edukatif, diskusi publik/jurnalistik, promosi pelaku, dan refleksi sarkasme tentang vektor ini.

**Kriteria inklusi (sebagai diskursus tentang salah satu modus berikut):**

- Modus telepon mengaku petugas bank/operator/instansi pemerintah
- Link phishing via SMS, WA, DM yang menyamar sebagai institusi resmi
- Permintaan OTP, password, PIN dari pihak tidak dikenal
- Skenario rekayasa sosial (penipuan berbasis manipulasi psikologis, urgensi palsu)
- Modus penipuan hadiah, undian, klaim kuota, refund
- Email phishing
- Modus impersonasi (mengaku saudara, teman, atasan)
- Berita/statistik/kebijakan terkait phishing
- Tips dan edukasi anti-phishing

**Kriteria eksklusi:**

- Phishing yang spesifik menargetkan e-wallet/QRIS dengan modus utama eksploitasi fitur e-wallet → `penipuan_ewallet_qris`
- Phishing yang menggunakan APK malware → `malware_apk`
- Phishing yang menggunakan deepfake/AI voice → `deepfake_penipuan_ai`

**Contoh diskursus per peran:**

*Korban (R1):*
> "Tadi pagi ada yg telpon ngaku dari BCA, katanya akun aku ada transaksi mencurigakan, suruh kasih OTP buat verifikasi. Untung aku langsung tutup teleponnya."

*Saksi (R2):*
> "Mama temenku kemarin kena penipuan undangan nikah, dia klik linknya terus diminta data, akhirnya rekeningnya kuras 8 juta"

*Edukator (R3):*
> "Reminder: Bank apa pun di Indonesia GAK PERNAH minta OTP, PIN, atau password lewat telepon/SMS/WA. Kalau ada yang minta, itu 100% penipu."

*Pelaku (R4) — jarang, biasanya tersamar:*
> "Yang akun WA-nya kena hack, DM gw, garansi balik dalam 1 jam, harga nego"

*Netral/Jurnalistik (R5):*
> "Menurut laporan Kominfo, modus phishing meningkat 40% di kuartal ini, terutama via WhatsApp"

### 4.2 Label: `penipuan_ewallet_qris`

**Definisi:** Diskursus publik yang berkaitan dengan penipuan spesifik pada ekosistem dompet digital (GoPay, OVO, DANA, ShopeePay) dan pembayaran QRIS — termasuk QRIS palsu, manipulasi saldo, dan modus terkait. Label ini mencakup **seluruh spektrum diskursif** tentang vektor ini.

**Kriteria inklusi (sebagai diskursus tentang salah satu modus berikut):**

- QRIS palsu/tempel di tempat publik (parkiran, kotak amal, masjid)
- Modus tukar saldo, isi saldo bonus
- Penipuan top-up berbasis link
- Klaim cashback/promo palsu di e-wallet
- Modus refund e-wallet
- Hack/akses ilegal akun e-wallet (jika fokus pada e-wallet, bukan akun umum)
- Modus pembelian palsu yang minta scan QR balik
- Berita/statistik/kebijakan terkait penipuan e-wallet
- Tips dan edukasi anti-penipuan e-wallet/QRIS

**Kriteria eksklusi:**

- Jika modusnya phishing umum (telepon mengaku CS bank, walau menyebut e-wallet) → `phishing_rekayasa_sosial`
- Jika modusnya install APK → `malware_apk`
- Pertanyaan teknis biasa tentang e-wallet (cara top-up, dll) tanpa konteks penipuan → `tidak_relevan`

**Contoh diskursus per peran:**

*Korban (R1):*
> "Saldo OVO aku amblas Rp 750rb setelah scan QRIS di parkiran liar dekat stasiun"

*Saksi (R2):*
> "Lagi viral QRIS palsu di kotak amal masjid, saldo masuk ke rekening penipu bukan ke masjid"

*Edukator (R3):*
> "Cara cek QRIS asli: setelah scan, nama merchant di aplikasi harus sesuai dengan toko/lokasi yang dituju. Kalau beda, BATALKAN."

*Netral/Jurnalistik (R5):*
> "BI mengeluarkan imbauan resmi terkait maraknya QRIS palsu di area publik"

**Catatan boundary:** Label ini punya overlap historis tinggi dengan `phishing_rekayasa_sosial` (di dataset Anda sebelumnya, F1 ewallet hanya 0.6875). Aturan keputusan: **fokus pada modus utama**, bukan pada platform yang disebut.

### 4.3 Label: `malware_apk`

**Definisi:** Diskursus publik yang berkaitan dengan malware berbasis aplikasi Android (file .apk) yang disebar via WhatsApp, Telegram, SMS, atau platform messaging lainnya — termasuk modus undangan nikah, kurir paket, surat tilang, kartu fisik, dan varian lain. Label ini mencakup **seluruh spektrum diskursif** tentang vektor ini.

**Kriteria inklusi (sebagai diskursus tentang salah satu modus berikut):**

- File APK yang dikirim via WA/Telegram/DM
- Modus undangan nikah, kurir J&T/JNE/SiCepat, surat tilang elektronik, foto paket
- Aplikasi pihak ketiga di luar Play Store yang mencurigakan
- Modus install aplikasi modifikasi (mod APK)
- Aplikasi yang minta akses SMS/notifikasi mencurigakan
- Penyebutan trojan banking Android (Anubis, Cerberus, dll)
- Berita/statistik/kebijakan terkait malware APK
- Tips dan edukasi anti-malware APK

**Kriteria eksklusi:**

- Malware desktop/PC murni → biasanya `tidak_relevan` di dataset media sosial Indonesia
- Phishing tanpa APK → `phishing_rekayasa_sosial`

**Contoh diskursus per peran:**

*Korban (R1):*
> "Bapak saya kena APK undangan nikah, langsung saldo BCA Rp 23 juta amblas dalam 5 menit"

*Saksi (R2):*
> "Tetangga saya kena APK kurir J&T, semua m-banking dan e-wallet-nya diakses penipu"

*Edukator (R3):*
> "JANGAN PERNAH install APK dari WhatsApp/Telegram. Selalu install dari Play Store resmi. Cek juga izin aplikasi sebelum install."

*Netral/Jurnalistik (R5):*
> "Laporan BSSN: serangan malware berbasis APK meningkat signifikan sepanjang 2024-2025"

### 4.4 Label: `judi_online_pinjol`

**Definisi:** Diskursus publik yang berkaitan dengan judi online ilegal (slot, casino online, togel online) dan pinjaman online ilegal (pinjol ilegal, fintech tidak terdaftar OJK) — mencakup promosi, laporan korban, dan diskusi kebijakan. Label ini mencakup **seluruh spektrum diskursif** tentang vektor ini.

**Kriteria inklusi (sebagai diskursus tentang salah satu modus berikut):**

- Promosi slot online ("gacor", "anti rungkad", "WD lancar")
- Link bandar judi online
- Laporan kerugian akibat judol
- Modus pinjol ilegal (penagihan kasar, sebar data kontak)
- Bunga pinjol ekstrim, jeratan utang
- Aplikasi pinjol tidak terdaftar OJK
- Kasus bunuh diri terkait pinjol/judol
- Promosi judol terselubung di akun selebgram/influencer
- Berita/statistik/kebijakan terkait judol/pinjol ilegal (pemblokiran OJK, dll)
- Tips dan edukasi anti-judol/pinjol ilegal

**Kriteria eksklusi:**

- Investasi legitimate yang sedang dibahas → `tidak_relevan`
- Pinjaman bank konvensional → `tidak_relevan`
- Diskusi judi konvensional (kartu, dadu) tanpa aspek online → `tidak_relevan`

**Catatan khusus:** Label ini menggabungkan dua sub-domain (judol + pinjol) karena dalam praktiknya keduanya sering muncul bersamaan (korban judol meminjam ke pinjol ilegal). Pertimbangkan memisahkan keduanya jika data Anda cukup untuk *fine-grained labeling* di iterasi mendatang.

**Contoh diskursus per peran:**

*Korban (R1):*
> "Sudah 3 bulan diteror penagih pinjol, foto KTP saya disebar ke seluruh kontak HP. Mau bunuh diri rasanya."

*Saksi (R2):*
> "Adik saya kalah judol 50 juta, sekarang pinjam ke 8 pinjol berbeda, hidupnya hancur"

*Edukator (R3):*
> "Cek legalitas pinjol di sikapiuangmu.ojk.go.id sebelum daftar. Pinjol legal terdaftar OJK, ada batas bunga, dan tidak boleh akses kontak."

*Pelaku (R4):*
> "Slot gacor maxwin 100jt, link daftar di bio, bonus new member 100%"

*Netral/Jurnalistik (R5):*
> "OJK telah memblokir 1.218 pinjol ilegal sepanjang 2024 menurut data terbaru"

### 4.5 Label: `peretasan_pencurian_identitas`

**Definisi:** Diskursus publik yang berkaitan dengan peretasan akun (sosial media, email, m-banking), pencurian data pribadi, kebocoran data, dan pencurian identitas digital. Label ini mencakup **seluruh spektrum diskursif** tentang vektor ini.

**Kriteria inklusi (sebagai diskursus tentang salah satu modus berikut):**

- Akun sosial media diretas (IG, WA, FB, Twitter, TikTok)
- Akun e-commerce diretas (Shopee, Tokopedia, Lazada)
- Pembobolan email
- Pencurian data pribadi (NIK, KK, foto KTP)
- Kebocoran data (Bjorka, dukcapil leak, dll)
- Modus jual beli data pribadi
- Doxing
- Akun gaming diretas
- SIM swap fraud
- Akun WhatsApp dibajak
- Berita/statistik/kebijakan terkait peretasan dan kebocoran data
- Tips dan edukasi pengamanan akun

**Kriteria eksklusi:**

- Peretasan yang menggunakan phishing sebagai vektor → tetap `peretasan_pencurian_identitas` jika fokus adalah hasil/dampak peretasan, gunakan `phishing_rekayasa_sosial` jika fokus pada modus
- Peretasan via APK → `malware_apk`
- Penyusupan via deepfake → `deepfake_penipuan_ai`

**Contoh diskursus per peran:**

*Korban (R1):*
> "Akun IG saya 80k followers diretas, sekarang dipake nipu followers minta pulsa atas nama saya"

*Saksi (R2):*
> "Teman saya akun gaming-nya diretas, item senilai 5 juta dijual semua sama hackernya"

*Edukator (R3):*
> "Aktifkan 2FA di semua akun penting. Jangan pernah pakai password yang sama di berbagai platform."

*Netral/Jurnalistik (R5):*
> "Kebocoran data dukcapil oleh Bjorka tahun lalu masih jadi sumber penipuan sampai sekarang"

### 4.6 Label: `deepfake_penipuan_ai`

**Definisi:** Diskursus publik yang berkaitan dengan penyalahgunaan AI generatif untuk penipuan — termasuk deepfake video, voice cloning, AI-generated scam content, dan konten manipulatif berbasis AI. Label ini mencakup **seluruh spektrum diskursif** tentang vektor ini.

**Kriteria inklusi (sebagai diskursus tentang salah satu modus berikut):**

- Deepfake video tokoh publik untuk promosi scam
- Voice cloning untuk modus "anak/saudara minta uang"
- AI-generated phishing content yang sangat personal
- Deepfake porno untuk pemerasan/sextortion
- AI chatbot scam (impersonasi CS palsu)
- Konten AI-generated yang menyebar misinfo cyber
- Berita/statistik/kebijakan terkait penipuan berbasis AI
- Tips dan edukasi anti-deepfake scam

**Kriteria eksklusi:**

- Diskusi AI murni (non-penipuan) → `tidak_relevan`
- Deepfake untuk hiburan/parodi tanpa unsur penipuan → `tidak_relevan`
- Penipuan biasa tanpa elemen AI → label vektor lain yang sesuai

**Catatan:** Label ini relatif baru dan mungkin memiliki sampel terbatas. Anotator harus waspada terhadap konten yang **mengklaim** sebagai deepfake padahal sebenarnya bukan.

**Contoh diskursus per peran:**

*Korban (R1):*
> "Mama saya hampir transfer Rp 15 juta karena ditelpon suara mirip banget sama saya, ternyata AI voice clone"

*Saksi (R2):*
> "Video deepfake Jokowi promosi investasi crypto bodong viral lagi di FB"

*Edukator (R3):*
> "Sekarang scammer pakai AI voice cloning. Buat *safe word* keluarga, dan selalu verifikasi via video call sebelum transfer uang."

*Netral/Jurnalistik (R5):*
> "Penelitian menunjukkan deepfake scam meningkat 3000% sejak 2023 secara global"

---

## 5. Decision Tree dan Tie-Breaking

### 5.1 Decision Tree Umum

```
START
  │
  ▼
Apakah konten menyebut konteks vektor ancaman siber spesifik secara substantif?
  │
  ├── TIDAK ada anchor → tidak_relevan (STOP)
  │
  └── YA, ada anchor → lanjut ke Layer 2
            │
            ▼
       Apakah konten menyebut SATU vektor spesifik dari 6 label?
            │
            ├── YA, satu vektor → labeli dengan vektor tersebut + catat peran (R1-R5)
            │
            └── MENYEBUT 2+ VEKTOR → gunakan hierarki prioritas (Bagian 5.2)
```

### 5.2 Hierarki Prioritas untuk Multi-Vector Content

Bila satu konten menyentuh dua vektor, gunakan urutan prioritas berikut (urutan = tingkat spesifisitas modus serangan):

1. **Vektor delivery mechanism** (cara serangan disampaikan) > vektor target (apa yang dicuri)
2. **Urutan resolusi konflik:**
   - `malware_apk` > vektor lain (APK adalah delivery yang sangat spesifik)
   - `deepfake_penipuan_ai` > vektor lain (AI element adalah pembeda utama)
   - `phishing_rekayasa_sosial` > `peretasan_pencurian_identitas` (jika phishing adalah modusnya)
   - `penipuan_ewallet_qris` > `phishing_rekayasa_sosial` (jika target spesifik e-wallet dan modusnya juga e-wallet specific seperti QRIS palsu)
   - `judi_online_pinjol` adalah kategori sui generis — biasanya tidak overlap

**Contoh aplikasi:**

> "Akun BCA mobile saya kuras gara-gara klik APK undangan nikah"
>
> → Vektor: `malware_apk` (APK adalah delivery mechanism utama)
> → Bukan `peretasan_pencurian_identitas` meski hasilnya pembobolan akun

> "Ditelpon orang ngaku dari Shopee minta OTP, akhirnya akun ShopeePay diambil alih"
>
> → Vektor: `phishing_rekayasa_sosial` (modus utama adalah social engineering via telepon)
> → Bukan `penipuan_ewallet_qris` meski targetnya e-wallet

> "Suara mirip anak saya minta transfer ke pinjol untuk bayar hutang"
>
> → Vektor: `deepfake_penipuan_ai` (AI voice cloning adalah pembeda)
> → Bukan `judi_online_pinjol` meski pinjol disebut

### 5.3 Aturan Konteks Ironi/Sarkasme

Jika konten secara literal tampak mempromosikan vektor ilegal tetapi konteksnya jelas ironis/kritis (komentar mengejek di bawah video edukatif, sarkasme jelas dari emoji/punctuation), labeli sesuai **intent komunikatif**, bukan kata-kata literal.

**Contoh:**

> "Wah modal 10rb jadi 10jt, the power of slot gacor 🤡🤡🤡"
>
> → Vektor: `judi_online_pinjol`
> → Peran: R5 (netral/sarkastis) — bukan R4 (pelaku), karena emoji clown menandakan kritik

---

## 6. Boundary Cases dan Confusion Matrix Aturan

Berikut pasangan label dengan overlap tinggi dan aturan resolusi:

### 6.1 `phishing_rekayasa_sosial` ↔ `penipuan_ewallet_qris`

**Pembeda kunci:** Apakah modus utama adalah manipulasi psikologis (phishing) atau eksploitasi spesifik fitur e-wallet (QRIS palsu)?

| Skenario | Label |
|----------|-------|
| Telpon ngaku CS OVO, minta OTP | `phishing_rekayasa_sosial` |
| Scan QRIS palsu di parkiran | `penipuan_ewallet_qris` |
| Link top-up palsu via WA | `phishing_rekayasa_sosial` |
| Modus "salah transfer, minta scan QR balik" | `penipuan_ewallet_qris` |

### 6.2 `phishing_rekayasa_sosial` ↔ `malware_apk`

**Pembeda kunci:** Apakah ada file APK yang terlibat?

| Skenario | Label |
|----------|-------|
| Link phishing yang minta input OTP di website | `phishing_rekayasa_sosial` |
| Link yang mengarah ke download APK | `malware_apk` |
| File undangan.apk dikirim WA | `malware_apk` |
| Email phishing dengan attachment APK | `malware_apk` |

### 6.3 `phishing_rekayasa_sosial` ↔ `peretasan_pencurian_identitas`

**Pembeda kunci:** Apakah fokus konten pada modus (phishing) atau pada hasil (akun diretas)?

| Skenario | Label |
|----------|-------|
| Cerita ditelpon penipu, hampir kena | `phishing_rekayasa_sosial` |
| Cerita akun IG dipake nipu setelah diretas | `peretasan_pencurian_identitas` |
| Tips menghindari phishing | `phishing_rekayasa_sosial` |
| Tips mengamankan akun setelah peretasan | `peretasan_pencurian_identitas` |

### 6.4 `judi_online_pinjol` ↔ `phishing_rekayasa_sosial`

Pinjol ilegal yang memakai modus phishing untuk verifikasi awal: tetap labeli `judi_online_pinjol` jika fokus diskursus adalah aktivitas pinjol-nya, bukan phishing-nya.

---

## 7. Protokol Inter-Annotator Agreement (IAA)

### 7.1 Setup Anotasi

- Minimal **2 anotator independen** untuk gold standard (357 sampel)
- **Spot-check oleh reviewer ketiga** untuk 50 sampel (sesuai metodologi Anda yang sudah ada)
- Anotator tidak boleh berdiskusi sebelum sesi rekonsiliasi
- Setiap anotator membaca dokumen ini lengkap sebelum mulai

### 7.2 Metrik IAA

Hitung Cohen's Kappa (κ) untuk dua anotator atau Fleiss' Kappa untuk 3+ anotator. Target minimal:

- κ ≥ 0.80 — Excellent (siap dijadikan gold standard)
- 0.60 ≤ κ < 0.80 — Substantial (perlu refinement guidelines)
- κ < 0.60 — Insufficient (guidelines harus direvisi major)

Laporkan κ secara per-label, bukan hanya overall — label dengan κ rendah perlu perhatian khusus di analisis.

### 7.3 Proses Rekonsiliasi

1. Anotasi independen oleh tiap anotator
2. Hitung κ awal
3. Identifikasi disagreement (kasus dengan label berbeda)
4. Diskusi terstruktur dengan referensi ke dokumen ini
5. Resolusi: konsensus atau keputusan reviewer ketiga
6. Update guidelines bila ditemukan ambiguitas sistematis
7. Anotasi ulang batch baru untuk validasi

### 7.4 Dokumentasi Kasus Sulit

Setiap anotator wajib mencatat:

- ID konten yang membuat ragu lebih dari 30 detik
- Alasan keraguan (overlap label, ironi, konteks tidak jelas)
- Keputusan final dan justifikasi

Catatan ini menjadi bahan untuk **revisi guidelines v2.2**.

---

## 8. Sample Annotation Form

Format CSV/spreadsheet yang direkomendasikan untuk anotator:

| Field | Tipe | Wajib | Deskripsi |
|-------|------|-------|-----------|
| `id` | string | Ya | ID unik data point |
| `text` | string | Ya | Teks asli komentar/tweet |
| `platform` | enum | Ya | youtube / x |
| `layer1_label` | enum | Ya | relevan / tidak_relevan |
| `layer2_label` | enum | Kondisional | Salah satu 6 label E-ICTT (jika layer1=relevan) |
| `speaker_role` | enum | Kondisional | R1-R5 (jika layer1=relevan) |
| `confidence` | int 1-5 | Ya | Tingkat keyakinan anotator |
| `notes` | string | Tidak | Catatan untuk kasus sulit |
| `annotator_id` | string | Ya | ID anotator |
| `timestamp` | datetime | Ya | Waktu anotasi |

---

## 9. Lampiran: Glossary Istilah Cybercrime Indonesia

| Istilah | Konteks | Vektor Terkait |
|---------|---------|----------------|
| Gacor | Slot online yang sering menang | `judi_online_pinjol` |
| WD | Withdraw, penarikan dana judol | `judi_online_pinjol` |
| Anti rungkad | Slogan promosi slot anti kalah | `judi_online_pinjol` |
| APK undangan | Malware undangan nikah | `malware_apk` |
| QRIS tempel | QRIS palsu yang ditempel di tempat publik | `penipuan_ewallet_qris` |
| Pinjol ilegal | Pinjaman online tidak terdaftar OJK | `judi_online_pinjol` |
| Sebar data | Penagih pinjol menyebar data kontak korban | `judi_online_pinjol` |
| Bjorka | Hacker yang membobol data instansi Indonesia | `peretasan_pencurian_identitas` |
| Sextortion | Pemerasan dengan konten seksual | `deepfake_penipuan_ai` (jika AI) |
| Voice cloning | Penipuan dengan suara AI mirip keluarga | `deepfake_penipuan_ai` |
| Saldo amblas | Saldo m-banking/e-wallet habis akibat penipuan | Bervariasi (lihat konteks modus) |
| Jasa pulihkan akun | Eufemisme untuk jasa hack akun | `peretasan_pencurian_identitas` |
| OTP | One-Time Password, target utama phishing | `phishing_rekayasa_sosial` |
| Modus kurir | Penipuan mengaku kurir kirim foto paket berisi APK | `malware_apk` |
| SIM swap | Pencurian nomor HP untuk akses OTP | `peretasan_pencurian_identitas` |

---

## 10. Catatan Versi dan Roadmap

### v2.0 (Deprecated)

- 7 label (6 vektor + 1 informasi_edukasi_siber)
- Ditinggalkan karena menciptakan double-coverage problem dengan vektor spesifik

### v2.1 (Saat ini)

- **6 label vektor** sesuai dan extending Arifman 2026
- Setiap label **mencakup spektrum diskursif penuh** (laporan korban, peringatan edukatif, diskusi publik/jurnalistik, promosi pelaku, refleksi sarkasme)
- Pipeline 2 lapis (relevance filter + vector classification)
- Metadata peran pembicara (R1-R5) sebagai dimensi tambahan
- Aturan tie-breaking eksplisit untuk multi-vector content
- Kriteria anchor untuk relevansi (menjaga taksonomi tetap vector-focused)

### v2.2 (Direncanakan setelah pilot annotation)

- Penyempurnaan boundary cases berdasarkan IAA awal
- Penambahan label hierarkis bila diperlukan (misal `judi_online` dan `pinjol_ilegal` dipisah)
- Expansion glossary berdasarkan istilah baru yang ditemukan di data

### v3.0 (Future work — tesis lanjutan)

- Multi-task: vector + role + sentiment + urgency
- Hierarchical labels (parent-child)
- Cross-lingual extension (Bahasa Indonesia + bahasa daerah)

---

## 11. Sitasi dan Acknowledgment Metodologis

Annotation guidelines ini dibangun di atas dan terinspirasi oleh:

- **Arifman, F., Mantoro, T., & Handayani, D. O. D. (2026).** A Hybrid Machine Learning Approach for Classifying Indonesian Cybercrime Discourse Using a Localized Threat Taxonomy. *Information*, 17(3), 301. (Sumber utama ICTT 5-dimensi yang menjadi basis taksonomi E-ICTT v2.1)
- **Kristiansen, L.-M., Agarwal, V., Franke, K., & Shah, R. S. (2020).** CTI-Twitter: Gathering Cyber Threat Intelligence from Twitter using Integrated Supervised and Unsupervised Learning. *2020 IEEE International Conference on Big Data*. (Inspirasi arsitektur pipeline dua lapis)
- **Ratner, A., et al. (2017).** Snorkel: Rapid Training Data Creation with Weak Supervision. (Dasar metodologis labeling functions yang akan dikembangkan dari guidelines ini)

---

*Akhir dokumen. Versi 2.1 ini siap digunakan untuk pilot annotation dan akan direvisi setelah IAA awal dianalisis.*
