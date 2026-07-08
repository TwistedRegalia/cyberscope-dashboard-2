# Phase 9 — XAI LIME pada Model B (Layer 2) — Tabel Token (Data untuk Bab 4)

**Tanggal:** 8 Jul 2026 · **Branch:** `feat/phase9-training`
**Objek penjelasan:** `predict_fn` = **komponen NEURAL murni** (softmax Model B). Dalam late fusion 0,75:0,25, neural = **bobot dominan (0,75)**, jadi XAI ini merepresentasikan penggerak keputusan utama pipeline. Komponen anchor (0,25) transparan secara terpisah (rule-based dapat dibaca langsung).

**Metodologi:**
- LIME **level-kata** (`split_expression=\W+`, `bow=True`) — sub-tokenisasi IndoBERT terjadi **di dalam** `predict_fn`, tak terlihat LIME. Token yang dijelaskan = **kata utuh** (`apk`, bukan `ap`+`##k`).
- `num_samples=500`, `num_features=10`, `random_state=42`.
- Sanity-first: checkpoint dimuat + macro-F1 test 0,9767 dikonfirmasi sebelum XAI.
- **Sampel bertarget (bukan acak)** — dipilih untuk memvalidasi temuan: 4 boundary phishing-judi + 3 sampel benar per vektor.
- Bobot **+** = token mendorong KE kelas tsb; **−** = mendorong MENJAUH.

Arsip logika predict_fn/fusion: [`src/phase9_late_fusion.py`](../src/phase9_late_fusion.py). Temuan naratif: `CONTEXT.md` Temuan #11.

---

## 1. Ikhtisar sampel

| idx | gold | neural (conf) | p_phish | p_judi | teks (ringkas) |
|---:|---|---|---:|---:|---|
| 25 | judi | phishing (0,643) | 0,643 | 0,303 | "…bongkar trik dukun dan **judol/penipu**…yg **nipu** lu dan orang lain…" |
| 558 | judi | phishing (0,846) | 0,846 | 0,086 | "…**judi** dibackingi irjen sambo…**tambang batubara** ilegal…" |
| 719 | judi | phishing (0,963) | 0,963 | 0,019 | "…semenjak gua pilih **jurusan kehutanan**, temen gua juga **kalah judi**…" |
| 778 | judi | phishing (0,978) | 0,978 | 0,008 | "…saldo **rekt bca** sya tiba2 hilang…tdk prnh **pinjaman online**…" |
| 4 | malware | malware (0,940) | 0,040 | 0,006 | "ciri-ciri kena **apk** jahat atau kena hack…" |
| 6 | judi | judi (0,989) | 0,003 | 0,989 | "…saya tidak mau maen **slot** lagi…**judi online**…" |
| 156 | deepfake | deepfake (0,978) | 0,004 | 0,005 | "…kalo salah ngomong tinggal bilang **deepfake** dan **ai**" |

> **Gradien confidence penting:** kasus scam-umbrella (idx 25) = confidence **terendah** (0,643) karena token judi eksplisit (`judol`) melawan token penipuan. Kasus token-netral (idx 719/778) = confidence **tinggi** (0,96–0,98) karena sinyal judi memang lemah/tersirat → model percaya diri default ke phishing. Confidence itu sendiri membedakan Pola A vs Pola B.

---

## 2. Boundary phishing-judi — token pendorong KEDUA kelas

Teks lengkap tiap sampel di bawah tabelnya. Kolom kiri = dorong ke **phishing** (prediksi neural), kolom kanan = dorong ke **judi** (gold).

### idx 25 (conf phishing 0,643) — **POLA A (scam umbrella)**
> "lah lu marcel pesulap merah bisa bongkar trik dukun dan judol/penipu,tapi lu ngak bisa bongkar dimana keberadaan owner dekha reset yg nipu lu dan orang lain kan aneh,gua nantang lu buat nyari owner de…"

| # | → phishing | bobot | → judi | bobot |
|---:|---|---:|---|---:|
| 1 | judol | −0,5377 | judol | +0,5450 |
| 2 | **nipu** | **+0,3983** | nipu | −0,3865 |
| 3 | **penipu** | **+0,1395** | dan | −0,1179 |
| 4 | dan | +0,1116 | penipu | −0,1165 |
| 5 | keberadaan | +0,0769 | keberadaan | −0,0757 |
| 6 | bisa | +0,0668 | 2025 | +0,0690 |
| 7 | 2025 | −0,0627 | bisa | −0,0572 |
| 8 | lu | +0,0583 | aneh | −0,0570 |
| 9 | aneh | +0,0562 | lu | −0,0487 |
| 10 | marcel | −0,0333 | dukun | −0,0463 |

**Baca:** `judol` (+0,545) mendorong judi dengan benar, TAPI `nipu` (+0,398) + `penipu` (+0,140) menariknya ke phishing dan **menang** (confidence phishing 0,643). Kosakata penipuan generik mengalahkan sinyal judi eksplisit → **konfirmasi Temuan #4 (scam umbrella)**.

### idx 558 (conf phishing 0,846) — **POLA B (token netral)**
> "berita yg lg rame di medsos: judi dibackingi irjen sambo (sudah dipecat), tambang batubara ilegal dibackingi komjen agus adrianto (kabareskrim mabes polri), narkoba malah yg mengedarkannya irjen teddy"

| # | → phishing | bobot | → judi | bobot |
|---:|---|---:|---|---:|
| 1 | batubara | +0,4527 | judi | +0,5008 |
| 2 | judi | −0,4488 | batubara | −0,4308 |
| 3 | tambang | +0,2864 | tambang | −0,2694 |
| 4 | di | +0,0862 | di | −0,1021 |
| 5 | polri | +0,0719 | polri | −0,0623 |
| 6 | penipuan | +0,0629 | teddy | −0,0589 |
| 7 | kabareskrim | −0,0517 | akan | +0,0525 |
| 8 | sambo | +0,0492 | rame | −0,0497 |
| 9 | online | +0,0466 | akan | −0,0437 |
| 10 | akan | −0,0437 | kabareskrim | +0,0377 |

**Baca:** `judi` (+0,501) mendorong judi dengan benar, tapi **dikalahkan** kata kontekstual NETRAL `batubara` (+0,453) + `tambang` (+0,286) yang mendorong phishing. `penipuan` hanya +0,063 (marginal). Ini **BUKAN** scam umbrella — model default ke phishing karena konteks berita non-siber, bukan kosakata penipuan.

### idx 719 (conf phishing 0,963) — **POLA B (token netral)**
> "sama bang, semenjak gua pilih jurusan kehutanan, temen gua juga kalah judi gua senyumin aja, dibilangin bandel sih"

| # | → phishing | bobot | → judi | bobot |
|---:|---|---:|---|---:|
| 1 | kehutanan | +0,4933 | judi | +0,4787 |
| 2 | judi | −0,4611 | kehutanan | −0,4829 |
| 3 | jurusan | +0,2771 | jurusan | −0,2728 |
| 4 | senyumin | +0,1230 | senyumin | −0,1181 |
| 5 | gua | +0,1124 | gua | −0,1112 |
| 6 | juga | +0,0853 | kalah | +0,0837 |
| 7 | kalah | −0,0697 | juga | −0,0822 |
| 8 | pilih | −0,0469 | pilih | +0,0545 |
| 9 | temen | −0,0343 | temen | +0,0364 |
| 10 | bandel | +0,0319 | sih | −0,0314 |

**Baca:** `judi` (+0,479) benar mendorong judi, tapi kalah oleh `kehutanan` (+0,493) + `jurusan` (+0,277) — kata **sama sekali tak terkait siber**. Sinyal judi tersirat ("kalah judi" sbg anekdot) → model tak menangkapnya. **Pola B murni.**

### idx 778 (conf phishing 0,978) — **AMBIGUITAS GOLD LABEL**
> "min, saldo rekt bca sya tiba2 hilang 1 jt tanpa mutasii. dan nama sya jga bersih tdk prnh mencicil dan tidak prnh pinjaman online sama sekalih. tlng dibantu min."

| # | → phishing | bobot | → judi | bobot |
|---:|---|---:|---|---:|
| 1 | rekt | +0,2285 | rekt | −0,2102 |
| 2 | bca | +0,1089 | bca | −0,1029 |
| 3 | mencicil | −0,0921 | mencicil | +0,0882 |
| 4 | pinjaman | −0,0727 | pinjaman | +0,0696 |
| 5 | mutasii | +0,0662 | mutasii | −0,0619 |
| 6 | nama | +0,0589 | nama | −0,0547 |
| 7 | tiba2 | −0,0386 | tiba2 | +0,0394 |
| 8 | 1 | −0,0328 | 1 | +0,0324 |
| 9 | sya | −0,0301 | sya | +0,0288 |
| 10 | dan | +0,0235 | dan | −0,0224 |

**Baca:** token dominan `rekt`/`bca`/`mutasii` (soal rekening bank) mendorong prediksi; `pinjaman`/`mencicil` (basis label gold=judi/pinjol) justru mendorong judi tapi **lemah** (+0,07–0,09). Teks **ambigu**: keluhan saldo BCA hilang yang kebetulan menyebut "pinjaman online". Sebagian "kesalahan" = **ambiguitas anotasi**, bukan kelemahan model semata.

---

## 3. Sampel benar — validasi sinyal domain

### idx 4 — malware_apk (conf 0,940)
> "ciri-ciri kena apk jahat atau kena hack tahun 2023 paling lengkap [URL] ini solusi totalnya"

| token | bobot |
|---|---:|
| **apk** | **+0,9072** |
| ciri | +0,0028 |
| 2023 | +0,0026 |
| tahun | +0,0021 |
| ini | +0,0020 |
| paling | +0,0015 |
| jahat | −0,0007 |
| lengkap | −0,0007 |
| kena | −0,0005 |
| hack | −0,0001 |

**Baca:** `apk` **+0,907 mendominasi mutlak** — model belajar sinyal vektor yang benar, bukan artefak.

### idx 6 — judi_online_pinjol (conf 0,989)
> "bismillah, insa allah setelah nonton vidio ini saya tidak mau maen slot lagi… biar semua orang tau klo judi online it…"

| token | bobot |
|---|---:|
| **slot** | **+0,2253** |
| **judi** | **+0,2018** |
| penipuan | −0,0761 |
| itu | +0,0498 |
| mau | +0,0484 |
| bro | −0,0433 |
| bismillah | −0,0391 |
| nonton | +0,0365 |
| malah | +0,0355 |
| ini | −0,0275 |

**Baca:** `slot` (+0,225) + `judi` (+0,202) = sinyal domain judi eksplisit. Menariknya `penipuan` (−0,076) justru mendorong MENJAUH dari judi — sisi lain dari boundary Pola A.

### idx 156 — deepfake_penipuan_ai (conf 0,978)
> "enak politikus sekarang, kalo salah ngomong tinggal bilang deepfake dan ai"

| token | bobot |
|---|---:|
| **deepfake** | **+0,3896** |
| **ai** | **+0,2971** |
| ngomong | +0,0491 |
| bilang | +0,0435 |
| dan | +0,0406 |
| enak | +0,0403 |
| sekarang | −0,0309 |
| tinggal | −0,0251 |
| salah | +0,0111 |
| politikus | −0,0054 |

**Baca:** `deepfake` (+0,390) + `ai` (+0,297) = kosakata native vektor deepfake (Temuan #7e) — model menangkap sinyal domain asli meski kelas terkecil (107 relevan).

---

## 4. Agregasi token boundary (4 sampel, bobot terjumlah)

| Token → PHISHING | Σbobot | | Token → JUDI | Σbobot |
|---|---:|---|---|---:|
| kehutanan | +0,493 | | judi | +0,979 |
| batubara | +0,453 | | judol | +0,545 |
| **nipu** | **+0,398** | | mencicil | +0,088 |
| tambang | +0,286 | | kalah | +0,084 |
| jurusan | +0,277 | | pinjaman | +0,070 |
| rekt | +0,228 | | 2025 | +0,069 |
| **penipu** | **+0,140** | | pilih | +0,055 |
| dan | +0,135 | | akan | +0,052 |
| senyumin | +0,123 | | tiba2 | +0,039 |
| gua | +0,112 | | kabareskrim | +0,038 |

**Token 'scam umbrella' yang mendorong phishing:** `nipu` (+0,398), `penipu` (+0,140), `penipuan` (+0,063).

---

## 5. Kesimpulan (untuk Bab 4)

| Temuan | Bukti | Implikasi |
|---|---|---|
| **1. Sinyal domain benar** | `apk` +0,907 · `slot`/`judi` +0,225/+0,202 · `deepfake`/`ai` +0,390/+0,297 | Model belajar semantik vektor nyata → kredibilitas |
| **2a. Pola A (scam umbrella)** | idx 25: `nipu`/`penipu` mengalahkan `judol` | Konfirmasi Temuan #4 (sebagian) |
| **2b. Pola B (token netral)** | idx 558/719: `batubara`/`kehutanan` mengalahkan `judi` | Kesalahan juga dari sinyal judi tersirat, BUKAN hanya scam umbrella |
| **3. Ambiguitas gold** | idx 778: token rekening bank; teks ambigu | Sebagian error = ambiguitas anotasi |

**Sintesis jujur:** confusion phishing-judi **terkonfirmasi SEBAGIAN** sebagai scam-umbrella (Temuan #4). Dua-pola menunjukkan penyebab ganda: (A) kosakata penipuan generik menang atas sinyal judi eksplisit; (B) model gagal menangkap referensi judi tersirat pada konteks non-siber. Bukan penjelasan tunggal.

**Catatan interpretasi:** LIME = aproksimasi lokal linear → token tak-intuitif (kata sambung `dan`, `gua`) wajar muncul. XAI ini pada komponen neural (0,75); anchor (0,25) dibaca terpisah. **Nilai tesis:** memenuhi komponen Explainable AI di judul dengan bukti konkret + analisis dua-pola = pembacaan data teliti (bukan over-claim).
