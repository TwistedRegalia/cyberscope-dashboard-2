# Instrumen Evaluasi Prototype — SUS + Kepuasan Pengguna (EUCS)

> Naskah kuesioner untuk **BAB 3.13 Evaluasi Prototype** (bagian SUS). Dashboard: **CyberScope**.
> Generator Google Form: `docs/sus_form_generator.gs`.
> Status: **instrumen siap; data responden belum dikumpulkan.** Jangan tulis skor apa pun di 3.13 sebelum Form benar-benar diisi.

---

## 1. Tujuan & cakupan

Dua instrumen, dua konstruk berbeda — **jangan dicampur jadi satu skor**:

| Instrumen | Mengukur | Item | Sumber |
|---|---|---:|---|
| **SUS** (System Usability Scale) | *Usability* — seberapa mudah sistem dipakai | 10 | Brooke (1996); adaptasi Indonesia: Sharfina & Santoso (2016) |
| **EUCS** (End-User Computing Satisfaction) | *Kepuasan pengguna* — seberapa puas terhadap isi, akurasi, bentuk, kemudahan, ketepatan waktu | 12 | Doll & Torkzadeh (1988) |

**Objek evaluasi:** dashboard CyberScope, dua halaman — `/` Monitoring dan `/klasifikasi`.

**Target responden** (sesuai `docs/HANDOFF_DASHBOARD.md` §10): profil **semi-teknis** — mahasiswa Informatika/Ilmu Komputer, dosen, praktisi IT. Bukan awam total, bukan pakar. **Minimal 5 responden, ideal 12–20.**

---

## 2. Skala

Skala persetujuan 5 titik, seluruh titik diberi label:

| Nilai | Label |
|---:|---|
| 1 | Sangat tidak setuju |
| 2 | Tidak setuju |
| 3 | Netral |
| 4 | Setuju |
| 5 | Sangat setuju |

Di Google Form skala ini dipasang sebagai **kolom Grid** (bukan *Linear Scale*, yang hanya memberi label di ujung bawah dan atas). Label kolom ditulis `1 (Sangat tidak setuju)` … `5 (Sangat setuju)` agar angkanya mudah ditarik dari hasil ekspor — lihat §6.

---

## 3. Naskah kuesioner

### Bagian 1 — Pembuka

Diisi Ray lewat blok `CONFIG` di `sus_form_generator.gs`: judul penulisan ilmiah, perkenalan peneliti, ringkasan apa yang telah dikerjakan. Draf penjelasan fitur + ajakan sudah tersedia di `CONFIG.DESKRIPSI_FITUR` dan boleh diedit bebas.

Inti yang **harus** ada di pembuka:
- Tautan dashboard: `https://cyberscope-webapp.vercel.app`
- Permintaan agar responden **mencoba dulu** kedua halaman sebelum mengisi.
- Estimasi pengisian **±5 menit**.
- Catatan *cold start*: backend berjalan di layanan gratis, kunjungan pertama bisa perlu **±25–60 detik** hingga badge berubah menjadi "Backend online" (lihat catatan keterbatasan §7 poin 4).
- Penegasan *reframing*: sistem ini **tidak mendeteksi serangan siber**; ia mengklasifikasikan **diskursus** — konten yang *membicarakan* ancaman.

### Bagian 2 — Profil responden

| # | Pertanyaan | Tipe | Wajib |
|---|---|---|---|
| P1 | Nama / inisial | Jawaban singkat | Tidak |
| P2 | Peran Anda | Pilihan ganda: Mahasiswa Informatika / Ilmu Komputer · Dosen · Praktisi IT / keamanan siber · Lainnya | Ya |
| P3 | Bagian mana yang sudah Anda coba? | Kotak centang: Halaman Monitoring · Halaman Klasifikasi · Tombol "Jelaskan dengan LIME" | Ya |

P2 dipakai untuk mendeskripsikan responden sebagai semi-teknis di 3.13. P3 adalah pengganti skenario tugas terstruktur: memungkinkan pelaporan cakupan pemakaian dan penyaringan responden yang belum mencoba apa pun (lihat §7 poin 3).

### Bagian 3 — SUS (10 item)

Adaptasi Bahasa Indonesia dari Sharfina & Santoso (2016). Kata **"sistem ini"** dipertahankan apa adanya; bahwa "sistem ini" berarti dashboard CyberScope dijelaskan di deskripsi bagian, bukan dengan mengganti kata di dalam item.

| # | Pernyataan | Polaritas |
|---:|---|:---:|
| Q1 | Saya berpikir akan menggunakan sistem ini lagi. | + |
| Q2 | Saya merasa sistem ini rumit untuk digunakan. | − |
| Q3 | Saya merasa sistem ini mudah digunakan. | + |
| Q4 | Saya membutuhkan bantuan dari orang lain atau teknisi dalam menggunakan sistem ini. | − |
| Q5 | Saya merasa fitur-fitur sistem ini berjalan dengan semestinya. | + |
| Q6 | Saya merasa ada banyak hal yang tidak konsisten (tidak serasi) pada sistem ini. | − |
| Q7 | Saya merasa orang lain akan memahami cara menggunakan sistem ini dengan cepat. | + |
| Q8 | Saya merasa sistem ini membingungkan. | − |
| Q9 | Saya merasa tidak ada hambatan dalam menggunakan sistem ini. | + |
| Q10 | Saya perlu membiasakan diri terlebih dahulu sebelum menggunakan sistem ini. | − |

> ⚠️ **Kolom polaritas hanya ada di dokumen ini, tidak ditampilkan ke responden** (mencegah *priming*).
> ⚠️ **Urutan dan polaritas selang-seling positif–negatif tidak boleh diubah** — rumus skoring §6 bergantung padanya. Ini juga alasan SUS tidak boleh dipotong atau ditambah itemnya.

### Bagian 4 — Kepuasan Pengguna / EUCS (12 item)

Item diadaptasi ke konteks CyberScope. **Label dimensi tidak ditampilkan ke responden** — hanya untuk analisis (§6).

| # | Dimensi | Pernyataan |
|---:|---|---|
| K1 | Content | Dashboard CyberScope menyediakan informasi yang saya butuhkan tentang diskursus 6 vektor ancaman siber. |
| K2 | Content | Isi informasi yang disajikan (jumlah data, proporsi tiap vektor, platform asal) sesuai dengan kebutuhan saya. |
| K3 | Content | Keluaran yang ditampilkan (grafik distribusi, tabel detail per vektor, contoh komentar) sesuai dengan yang saya perlukan. |
| K4 | Content | Informasi yang disediakan dashboard sudah memadai. |
| K5 | Accuracy | Hasil klasifikasi yang diberikan dashboard terasa tepat dan masuk akal. |
| K6 | Accuracy | Saya puas dengan tingkat keyakinan (*confidence*) yang ditampilkan pada hasil klasifikasi. |
| K7 | Format | Keluaran dashboard disajikan dalam format yang bermanfaat (grafik, tabel, bar probabilitas). |
| K8 | Format | Informasi yang ditampilkan jelas dan mudah dibaca. |
| K9 | Ease of Use | Dashboard CyberScope ramah pengguna. |
| K10 | Ease of Use | Dashboard CyberScope mudah dioperasikan. |
| K11 | Timeliness | Saya memperoleh hasil klasifikasi dalam waktu yang wajar. |
| K12 | Timeliness | Informasi pada halaman Monitoring sesuai dengan data terakhir yang diproses sistem. |

Seluruh item EUCS berpolaritas **positif** — tidak ada pembalikan skor.

### Bagian 5 — Saran terbuka (opsional)

| # | Pertanyaan | Tipe |
|---|---|---|
| S1 | Bagian mana dari dashboard yang paling membantu Anda? Mengapa? | Paragraf |
| S2 | Apa yang menurut Anda perlu diperbaiki? | Paragraf |

Keduanya **tidak wajib**. Berguna sebagai data kualitatif pendamping di 3.13.

---

## 4. Rujukan fitur (agar item tetap sinkron dengan produk)

Item di atas menyebut fitur yang **benar-benar ada**. Sumber kebenaran: `docs/HANDOFF_WRITING.md` §9.3 dan `dashboard/frontend/src/lib/vectors.ts`.

- **`/` Monitoring:** kartu ringkas (Total baris · Relevan (Model A) · Rentang tanggal) · funnel relevansi · distribusi 6 vektor (bar horizontal, klik → *drill-down*) · proporsi platform YouTube vs X · tren waktu · tabel detail per vektor · contoh komentar per vektor.
- **`/klasifikasi`:** 7 contoh siap-klik (termasuk 1 *off-topic*) atau tempel teks · label vektor + *confidence* + bar probabilitas 6 kelas · gate "tidak relevan" · LIME opsional (±30–60 detik) · badge status backend.
- **Enam label vektor (tampilan UI):** Phishing & Rekayasa Sosial · Penipuan E-Wallet/QRIS · Malware APK · Judi Online & Pinjol · Peretasan & Pencurian Identitas · Deepfake & Penipuan AI.

**Tidak ada** di v1 — jangan sekali-kali ditanyakan: login/akun, filter, pencarian, *date picker*, ekspor/unduh, peta, pembaruan *real-time*, dan Speaker Role R1–R5.

---

## 5. Prosedur pelaksanaan

1. Isi `CONFIG` di `docs/sus_form_generator.gs`, jalankan di script.google.com → Form terbentuk.
2. Kirim 1 respons percobaan → cek ekspor ke Sheets → **hapus respons percobaan**.
3. Sebar tautan ke calon responden semi-teknis. Kumpulkan **min 5, target 12–20**.
4. Ekspor respons → hitung skor (§6) → tulis 3.13.
5. Setelah ada hasil, perbarui `docs/HANDOFF_WRITING.md` §6 poin 9 dan §9.6 dari "pending" menjadi hasil nyata.

---

## 6. Panduan skoring

### 6.1 Ubah teks ekspor menjadi angka

Google Forms mengekspor jawaban grid sebagai teks, mis. `4 (Setuju)`. Ambil angkanya:

```
=VALUE(LEFT(B2;1))          // locale Indonesia (pemisah argumen titik koma)
=VALUE(LEFT(B2,1))          // locale English
```

Nama kolom hasil ekspor berbentuk `Judul grid [Teks baris]`, satu kolom per item.

### 6.2 SUS

Untuk tiap responden, dengan jawaban Q1–Q10 sudah berupa angka 1–5:

- Item **ganjil** (Q1, Q3, Q5, Q7, Q9): kontribusi = `skor − 1`
- Item **genap** (Q2, Q4, Q6, Q8, Q10): kontribusi = `5 − skor`
- **Skor SUS = jumlah 10 kontribusi × 2,5** → rentang **0–100**

Misal Q1–Q10 ada di kolom `B2:K2`:

```
=((B2-1)+(5-C2)+(D2-1)+(5-E2)+(F2-1)+(5-G2)+(H2-1)+(5-I2)+(J2-1)+(5-K2))*2.5
```

Skor akhir penelitian = **rata-rata skor SUS seluruh responden**. Laporkan juga **SD** dan **n**.

> ⚠️ **Skor SUS bukan persentase.** SUS 72 ≠ "72% pengguna puas". Tulis sebagai skor pada rentang 0–100.

### 6.3 Interpretasi SUS

Acuan utama: rata-rata industri **68** (Sauro & Lewis, 2016) — di atas 68 berarti di atas rerata.

Rentang penerimaan dan *adjective rating* dari Bangor et al. (2009):

| Skor SUS | Adjective rating | Acceptability |
|---|---|---|
| > 80,3 | Excellent | Acceptable |
| 68 – 80,3 | Good | Acceptable |
| 51 – 68 | OK | Marginal |
| < 51 | Poor / Awful | Not acceptable |

> ⚠️ Tabel ini gabungan lazim dari rentang *acceptability* dan *adjective rating* Bangor et al. (2009); batas persisnya bervariasi antar penyajian. **Verifikasi ke sumber asli sebelum dikutip di skripsi**, dan sebut acuan yang Anda pakai secara eksplisit.

### 6.4 EUCS

- Skor tiap dimensi = **rata-rata item anggotanya** (Content = K1–K4; Accuracy = K5–K6; Format = K7–K8; Ease of Use = K9–K10; Timeliness = K11–K12).
- Skor kepuasan total = rata-rata seluruh 12 item.
- Laporkan **mean dan SD per dimensi** — bukan hanya angka total. Dimensi terendah adalah bahan pembahasan perbaikan yang paling berguna.
- Skala tetap 1–5; **jangan** dikonversi ke 0–100 (itu konvensi SUS, bukan EUCS).

---

## 7. Catatan adaptasi & keterbatasan

Sesuai gaya penulisan di `docs/HANDOFF_WRITING.md` §8 — adaptasi diakui terbuka, tidak disembunyikan. Semua poin di bawah **wajib** masuk ke 3.13.

1. **EUCS diadaptasi skalanya.** Instrumen asli Doll & Torkzadeh (1988) memakai item berbentuk **pertanyaan** dengan skala **frekuensi** (*almost never → almost always*). Di sini item diubah menjadi **pernyataan** dengan **skala persetujuan** 1–5. Adaptasi ini lazim pada penelitian sistem informasi di Indonesia, tetapi tetap harus dinyatakan eksplisit — jangan diklaim sebagai EUCS asli tanpa modifikasi.
2. **Dimensi *Ease of Use* EUCS tumpang tindih dengan SUS.** Ini disengaja dan wajar: dua instrumen mengukur hal serupa dari sudut berbeda, hasilnya berfungsi sebagai bukti konvergen. Bukan duplikasi yang perlu ditutupi.
3. **Tidak ada skenario tugas terstruktur.** Responden mencoba dashboard secara bebas, sehingga tiap orang menilai pengalaman yang berbeda-beda. Ini **keterbatasan nyata**; item P3 ("bagian mana yang sudah dicoba") adalah mitigasi parsial. **Jangan** menyebut evaluasi ini *controlled usability test*.
4. **Cold start 25–60 detik** (`HANDOFF_WRITING.md` §6 poin 7) dijelaskan di pembuka Form agar responden tidak mengira sistem rusak. Konsekuensinya dua arah: tanpa penjelasan, dimensi *Timeliness* tertekan tidak adil; dengan penjelasan, penilaian bisa terangkat. Catat sebagai keterbatasan apa adanya.
5. **n kecil (5–20)** → interval kepercayaan lebar. Laporkan SUS sebagai **indikasi**, bukan dasar uji hipotesis atau generalisasi populasi.
6. **Responden semi-teknis ≠ pengguna sasaran nominal.** Pengguna sasaran dashboard adalah analis lembaga (BSSN/Bareskrim/OJK); yang mengisi kuesioner adalah proksi semi-teknis. Sebutkan kesenjangan ini.
7. **Item K1 memakai kata "diskursus"**, bukan "deteksi serangan" — menjaga *reframing* fundamental penelitian (`HANDOFF_WRITING.md` §1). Jangan diganti saat menyunting Form.
8. **Uji reliabilitas (Cronbach's α)** boleh dihitung untuk EUCS bila n memadai, tapi pada n≈12–20 angkanya tidak stabil. Bila dilaporkan, sertakan n.

---

## 8. Daftar pustaka (APA)

> Verifikasi nomor halaman dan detail terbitan ke sumber asli sebelum masuk daftar pustaka skripsi.

- Bangor, A., Kortum, P., & Miller, J. (2009). Determining what individual SUS scores mean: Adding an adjective rating scale. *Journal of Usability Studies, 4*(3), 114–123.
- Brooke, J. (1996). SUS: A "quick and dirty" usability scale. In P. W. Jordan, B. Thomas, B. A. Weerdmeester, & I. L. McClelland (Eds.), *Usability evaluation in industry* (pp. 189–194). Taylor & Francis.
- Doll, W. J., & Torkzadeh, G. (1988). The measurement of end-user computing satisfaction. *MIS Quarterly, 12*(2), 259–274.
- Sauro, J., & Lewis, J. R. (2016). *Quantifying the user experience: Practical statistics for user research* (2nd ed.). Morgan Kaufmann.
- Sharfina, Z., & Santoso, H. B. (2016). An Indonesian adaptation of the System Usability Scale (SUS). *2016 International Conference on Advanced Computer Science and Information Systems (ICACSIS)*, 145–148.
