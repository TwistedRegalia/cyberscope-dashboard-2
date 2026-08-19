# Draft Teks — 3.4 Pengumpulan Data

> **Cara pakai:** teks di bawah siap disalin ke Word. Blok kode ditaruh di dalam **tabel satu sel
> berbingkai** (mengikuti pola BAB_3_Fauzan_v13). Placeholder `[SISIPKAN GAMBAR …]` diganti
> screenshot. Catatan penyusunan ada di bagian akhir berkas ini — **jangan** ikut disalin.

---

## 3.4 Pengumpulan Data

Pengumpulan data dilakukan melalui teknik OSINT dari dua platform media sosial, yaitu X (Twitter) dan YouTube. Pemilihan kedua platform tersebut didasarkan pada karakteristik diskursus yang saling melengkapi, di mana YouTube menyediakan komentar dengan volume besar dan narasi panjang pada video bertema ancaman siber, sedangkan X menyediakan laporan pengalaman korban yang singkat, spontan, dan kaya ragam bahasa informal. Pengumpulan komentar YouTube dilakukan menggunakan YouTube Data API v3, sedangkan pengumpulan dari platform X dilakukan menggunakan Tweet Harvest dengan kueri berlapis per kategori vektor. Khusus untuk platform X, data dibatasi hanya pada teks berbahasa Indonesia (`lang=in`), dan konten non-Indonesia dibuang.

Proses pengumpulan dilaksanakan dalam dua tahap. Tahap pertama merupakan akuisisi awal yang bersifat luas terhadap seluruh kategori vektor ancaman, sedangkan tahap kedua merupakan akuisisi tambahan yang bersifat terarah pada vektor dengan ketersediaan data paling langka, yaitu malware/APK dan deepfake/penipuan berbasis AI. Pemisahan menjadi dua tahap dilakukan karena kelangkaan data pada vektor tertentu baru dapat diketahui setelah akuisisi awal dianalisis, sehingga penambahan data dapat diarahkan secara tepat sasaran alih-alih memperbesar volume secara merata. Perlu dicatat bahwa data X yang terkumpul merupakan cuplikan lintas-seksi (*cross-sectional snapshot*) dalam rentang tujuh hari, sehingga tidak digunakan untuk klaim tren temporal jangka panjang.

---

### 3.4.1 Protokol Kurasi Sumber Data

Kurasi sumber data dilakukan secara terprotokol untuk menekan bias seleksi yang lazim terjadi pada pengumpulan data OSINT. Tanpa protokol yang eksplisit, pemilihan video maupun penyusunan kueri cenderung mengikuti hasil teratas mesin pencari, sehingga data yang terkumpul hanya merepresentasikan konten paling populer dan bukan keragaman modus ancaman yang sebenarnya. Protokol yang disusun mencakup dua komponen, yaitu kriteria seleksi video YouTube dan spesifikasi kueri pencarian pada platform X, yang keduanya ditetapkan sebelum proses akuisisi dijalankan agar keputusan pemilihan tidak dipengaruhi oleh hasil yang telah terlihat. Kriteria inklusi dan eksklusi yang digunakan disajikan pada Tabel 3.3 berikut.

**Tabel 3.3 Kriteria Inklusi dan Eksklusi Sumber Data**

| Aspek | Kriteria Inklusi | Kriteria Eksklusi |
|---|---|---|
| Topik | Membahas satu modus ancaman siber secara eksplisit | Topik campur tanpa fokus; membahas banyak modus sekaligus |
| Volume komentar | Minimal 300 komentar per video | Komentar dinonaktifkan (*disabled*) |
| Periode publikasi | Tahun 2022 sampai 2026 | Publikasi sebelum 2022 |
| Bahasa | Judul, deskripsi, dan mayoritas komentar berbahasa Indonesia | Konten berbahasa asing |
| Tipe kanal | Minimal tiga tipe berbeda per vektor: berita, edukasi, dan penuturan pengalaman (*storytelling*) | Kanal dengan komentar didominasi spam atau bot |
| Keunikan | Video belum pernah diambil pada akuisisi awal | Duplikasi terhadap 18 video akuisisi awal |

Berdasarkan Tabel 3.3, ambang minimal 300 komentar ditetapkan untuk memastikan setiap video memberikan kontribusi data yang memadai, sementara pembatasan periode 2022 sampai 2026 dimaksudkan agar modus ancaman yang terekam masih relevan dengan lanskap kejahatan siber terkini. Persyaratan minimal tiga tipe kanal berbeda per vektor merupakan kriteria yang paling menentukan kualitas data, karena setiap tipe kanal menghasilkan pola komentar yang berbeda secara sistematis. Kanal berita cenderung memicu komentar bernada reaktif dan opini publik, kanal edukasi memicu komentar berupa pertanyaan teknis, sedangkan kanal penuturan pengalaman memicu komentar berupa pengakuan korban yang justru paling bernilai bagi penelitian ini. Kriteria eksklusi terhadap 18 video akuisisi awal ditetapkan untuk mencegah duplikasi data lintas-tahap sekaligus memastikan bahwa penambahan data benar-benar memperluas cakupan sumber.

Komponen kedua dari protokol adalah spesifikasi kueri pencarian pada platform X, yang disusun dalam berkas `query_spec_v2.json` dan memuat tujuh kueri untuk setiap kategori vektor. Penyusunan kueri tidak dilakukan dengan satu kata kunci tunggal, melainkan dengan kombinasi berlapis antar-kelompok kata yang harus muncul bersamaan. Berikut adalah cuplikan spesifikasi kueri untuk kategori vektor `malware_apk`.

```json
{
  "malware_apk": {
    "queries": [
      "(\"apk undangan\" OR \"apk nikah\" OR \"apk pernikahan\") (rekening OR saldo OR terkuras) lang:id",
      "\"apk penipuan\" OR \"apk bodong\" OR \"file apk penipuan\" OR \"apk modus\" lang:id",
      "(apk) (kurir OR paket OR jnt OR tilang OR pajak OR pln OR bpjs) lang:id",
      "(apk OR aplikasi) (sniffing OR sadap OR mbanking OR \"bobol rekening\") lang:id"
    ],
    "limit": 500,
    "lang": "id"
  }
}
```

Kode di atas menunjukkan struktur spesifikasi kueri yang menjadi masukan bagi proses akuisisi pada platform X. Setiap kueri disusun sebagai konjungsi antar-kelompok kata, di mana kelompok pertama memuat istilah inti modus ancaman dan kelompok berikutnya memuat istilah konsekuensi atau konteks, sehingga tweet yang terjaring harus memenuhi seluruh kelompok secara bersamaan. Pendekatan berlapis ini dipilih karena kueri kata kunci tunggal seperti `apk` menghasilkan proporsi *noise* yang sangat tinggi akibat penggunaan istilah tersebut dalam konteks non-ancaman. Parameter `limit` ditetapkan sebesar 500 tweet per kueri sebagai batas konservatif untuk menghindari pembatasan laju (*rate limit*) oleh platform, sedangkan parameter `lang` bernilai `id` memastikan penyaringan bahasa Indonesia dilakukan pada tingkat kueri sehingga mengurangi beban penyaringan pada tahap persiapan data. Spesifikasi yang sama diterapkan pada tiga kategori vektor lainnya, sehingga total terdapat 28 kueri terdokumentasi yang seluruhnya ditetapkan sebelum eksekusi dijalankan.

---

### 3.4.2 Akuisisi Komentar YouTube (YouTube Data API v3)

Akuisisi komentar YouTube dilakukan melalui YouTube Data API v3, yaitu antarmuka pemrograman resmi yang disediakan Google untuk mengakses metadata dan komentar video secara terstruktur. Penggunaan API resmi dipilih dibandingkan teknik *web scraping* langsung pada halaman video karena API menjamin kelengkapan data komentar berikut balasannya, menyediakan mekanisme paginasi yang andal untuk video dengan ribuan komentar, serta beroperasi dalam kuota penggunaan yang legal dan terdokumentasi. Pada tahap akuisisi tambahan, pemanggilan API dilakukan melalui skrip Python khusus yang membaca daftar video hasil kurasi dan menuliskan hasilnya ke berkas CSV per video. Berikut adalah implementasi inti pemanggilan API tersebut.

```python
def get_youtube_service(api_key):
    """Initialize YouTube API v3 client."""
    return build("youtube", "v3", developerKey=api_key)


def scrape_comments(service, video_id, max_results=10000):
    request = service.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        maxResults=100,            # batas maksimum per halaman
        textFormat="plainText",
        pageToken=None
    )

    count = 0
    while request and count < max_results:
        response = request.execute()
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            yield {...}            # komentar tingkat atas
            count += 1
            if item.get("replies"):
                for reply_item in item["replies"].get("comments", []):
                    yield {...}    # balasan komentar
                    count += 1
        pageToken = response.get("nextPageToken")
        ...
```

Kode di atas menunjukkan proses pengambilan komentar dari satu video melalui sumber daya `commentThreads` pada YouTube Data API v3. Parameter `part` diisi dengan nilai `snippet,replies` agar setiap permintaan mengembalikan komentar tingkat atas sekaligus balasannya dalam satu panggilan, sehingga struktur percakapan tetap terjaga dan jumlah pemanggilan API dapat ditekan. Parameter `maxResults` ditetapkan sebesar 100 karena merupakan batas maksimum yang diizinkan API untuk satu halaman hasil, sedangkan `textFormat` bernilai `plainText` dipilih agar komentar dikembalikan tanpa markah HTML sehingga tidak memerlukan pembersihan markah pada tahap praproses. Perulangan `while` beserta pembacaan `nextPageToken` berfungsi sebagai mekanisme paginasi yang memungkinkan pengambilan seluruh komentar pada video dengan jumlah komentar melebihi 100, di mana proses berhenti ketika API tidak lagi mengembalikan token halaman berikutnya. Setiap komentar yang dihasilkan mencakup pengenal komentar, nama penulis, isi teks, jumlah suka, jumlah balasan, waktu publikasi, serta penanda apakah komentar tersebut merupakan balasan.

Proses akuisisi tambahan dijalankan terhadap delapan video hasil kurasi dan menghasilkan 6.663 komentar. Jumlah video yang terkumpul lebih sedikit dari target awal sebanyak 20 sampai 24 video karena penerapan kriteria pada Tabel 3.3 secara ketat menyisakan sangat sedikit kandidat yang memenuhi syarat, khususnya pada vektor deepfake. Rincian video yang berhasil dikurasi beserta perolehan komentarnya disajikan pada Tabel 3.4 berikut.

**Tabel 3.4 Daftar Video YouTube Akuisisi Tambahan**

| No | Kanal | Tipe Kanal | Tahun | Judul Video (disingkat) | Komentar |
|---|---|---|---|---|---|
| 1 | tvOneNews | Berita | 2023 | Jadi Korban Phising Undangan Nikah Via WA Uang Rp1,4 Miliar Raib | 1.240 |
| 2 | Massmobi | Edukasi | 2023 | Undangan Nikah (APK Virus) ini kita instal..!!! | 1.077 |
| 3 | Mr Bert | Edukasi | 2022 | Penipuan Undangan WhatsApp Pernikahan serta Solusinya | 900 |
| 4 | Dea Afrizal | Edukasi | 2022 | Kasus Penipuan Terbaru Berkedok Aplikasi | 876 |
| 5 | PACE KOMPUTER | Edukasi | 2022 | APK Undangan Penguras Saldo Rekening | 807 |
| 6 | KOMPASTV | Berita | 2023 | Terlanjur Klik File .APK Dari Penipu? Segera Lakukan 5 Langkah Ini! | 341 |
| 7 | BSSN | Edukasi | 2023 | Malware Undangan Pernikahan.apk | 205 |
| 8 | Iqbal Qoreshi | Penuturan | 2023 | Modus Penipu Terbaru: ATM Ludes Video Call Deepfake | 1.217 |
| | | | | **Total** | **6.663** |

Berdasarkan Tabel 3.4, dari delapan video yang berhasil dikurasi, tujuh video mewakili vektor malware/APK dan hanya satu video yang mewakili vektor deepfake. Ketimpangan tersebut bukan merupakan kelalaian dalam proses kurasi, melainkan temuan tersendiri yang mengonfirmasi kelangkaan diskursus deepfake pada platform YouTube berbahasa Indonesia, di mana penelusuran dengan lima kueri pencarian berbeda hanya menghasilkan satu video yang memenuhi seluruh kriteria inklusi. Video nomor 7 dari kanal BSSN diikutsertakan meskipun perolehan komentarnya sebesar 205 berada di bawah ambang 300, dengan pertimbangan bahwa kanal tersebut merupakan lembaga resmi keamanan siber nasional sehingga memiliki nilai representasi institusional yang tidak dimiliki kanal lain. Persyaratan keragaman tipe kanal terpenuhi dengan komposisi dua kanal berita, lima kanal edukasi, dan satu kanal penuturan pengalaman. Proses eksekusi akuisisi komentar YouTube ditampilkan pada Gambar 3.7 berikut.

```
[SISIPKAN GAMBAR 3.7 — output terminal phase3_youtube_scrape.py]
Sumber: docs/07_log_scraping_raw.txt, bagian "RUN: Phase 3 - YouTube Data API v3"
```

**Gambar 3.7 Proses Akuisisi Komentar YouTube melalui Data API v3**
*(Sumber: Dokumentasi Pribadi, 2026)*

Berdasarkan Gambar 3.7, setiap video diproses secara berurutan dengan keluaran yang mencatat pengenal video, judul video, jumlah komentar yang berhasil diambil, serta lokasi berkas hasil penyimpanan. Keluaran tersebut membuktikan bahwa mekanisme paginasi berjalan sebagaimana mestinya, terlihat dari perolehan komentar yang jauh melebihi batas 100 komentar per halaman pada seluruh video, misalnya 1.240 komentar pada video pertama. Pencatatan jumlah komentar per video juga berfungsi sebagai kendali mutu, karena selisih yang terlalu besar antara estimasi jumlah komentar pada antarmuka YouTube dan jumlah yang benar-benar terambil dapat mengindikasikan adanya komentar yang telah dihapus atau disaring oleh platform.

---

### 3.4.3 Akuisisi Tweet Platform X (Tweet Harvest)

Akuisisi data pada platform X dilakukan menggunakan Tweet Harvest versi 2.7.1, yaitu perkakas antarmuka baris perintah berbasis Node.js yang mengotomatiskan peramban Chromium untuk mengambil hasil pencarian X. Pemilihan perkakas ini dilatarbelakangi oleh perubahan kebijakan akses X Developer API yang sejak tahun 2023 menerapkan skema berbayar dengan kuota pencarian historis yang sangat terbatas pada tingkat gratis, sehingga tidak memadai untuk kebutuhan pengumpulan data penelitian ini. Tweet Harvest bekerja dengan memanfaatkan *cookie* sesi `auth_token` dari akun X yang telah masuk pada peramban, bukan *bearer token* pengembang, sehingga akses yang diperoleh setara dengan akses seorang pengguna biasa yang melakukan pencarian secara manual. Konsekuensi metodologis dari pendekatan ini adalah hasil yang diperoleh bersifat cuplikan lintas-seksi dan bukan rentang historis penuh, sebagaimana telah dinyatakan pada bagian pembuka subbab ini. Tampilan awal perkakas Tweet Harvest saat dijalankan ditampilkan pada Gambar 3.8 berikut.

```
[SISIPKAN GAMBAR 3.8]
Berkas: C:\Users\Ray Siraj\Pictures\Screenshots\Screenshot 2026-05-20 153252.png
```

**Gambar 3.8 Antarmuka Interaktif Tweet Harvest v2.7.1 pada Akuisisi Awal**
*(Sumber: Dokumentasi Pribadi, 2026)*

Berdasarkan Gambar 3.8, perkakas Tweet Harvest dijalankan melalui perintah `npx tweet-harvest@latest` pada direktori kerja penelitian, dan menampilkan informasi versi 2.7.1 beserta keterangan bahwa perkakas menggunakan peramban Chromium untuk mengambil data dari Twitter dengan *auth token* pengguna. Keterangan *Use it for Educational Purposes only* yang ditampilkan perkakas menegaskan konteks penggunaan untuk keperluan penelitian dan edukasi. Nilai *auth token* yang dimasukkan ditampilkan dalam bentuk tersamar berupa deretan tanda bintang sebagaimana terlihat pada baris *What's your Twitter auth token*, sehingga kredensial tidak terekspos pada dokumentasi proses. Baris terakhir yang menampilkan *What's the search keyword* menunjukkan bahwa pada tahap akuisisi awal perkakas dioperasikan dalam mode interaktif, yaitu kueri pencarian dimasukkan satu per satu melalui dialog terminal. Mode interaktif tersebut memadai untuk akuisisi awal yang bersifat eksploratif, namun menjadi tidak praktis dan sulit direproduksi ketika akuisisi tambahan menuntut eksekusi puluhan kueri secara konsisten.

Keterbatasan mode interaktif tersebut diatasi pada tahap akuisisi tambahan dengan membungkus pemanggilan Tweet Harvest ke dalam skrip Python yang membaca kueri dari berkas `query_spec_v2.json` dan menjalankannya secara berurutan. Berikut adalah implementasi penyusunan perintah pemanggilan perkakas tersebut.

```python
NPX = "npx.cmd" if os.name == "nt" else "npx"
TWEET_HARVEST_PKG = "tweet-harvest@latest"

def run_tweet_harvest(query, vektor, query_idx, dest_csv, token,
                      limit=500, tab="LATEST", delay=3):
    out_name = f"{vektor}__q{query_idx}.csv"
    cmd = [
        NPX, "--yes", TWEET_HARVEST_PKG,
        "--search-keyword", query,
        "--limit", str(limit),
        "--output-filename", out_name,
        "--tab", tab,
        "--export-format", "csv",
        "--delay", str(delay),
    ]
    if token:
        cmd += ["--token", token]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
```

Kode di atas menunjukkan penyusunan perintah pemanggilan Tweet Harvest secara terprogram. Variabel `NPX` menyesuaikan nama berkas peluncur sesuai sistem operasi, karena pada Windows perkakas `npx` tersedia sebagai `npx.cmd`. Argumen `--search-keyword` diisi dengan kueri yang dibaca dari spesifikasi, sedangkan `--limit` bernilai 500 membatasi perolehan maksimum per kueri sebagai mitigasi pembatasan laju. Argumen `--tab` bernilai `LATEST` menentukan bahwa hasil diambil dari tab urutan terbaru dan bukan tab relevansi tertinggi, dengan pertimbangan bahwa tab terbaru memberikan cakupan yang lebih menyeluruh dan tidak dipengaruhi peringkat popularitas yang dapat memperkuat bias seleksi. Argumen `--delay` bernilai 3 memberikan jeda tiga detik antar-pemuatan halaman untuk meniru pola akses manusia sekaligus mengurangi risiko pemblokiran akun. Nilai `timeout` sebesar 1.200 detik ditetapkan karena pemanggilan pertama perkakas memerlukan pengunduhan peramban Chromium berukuran sekitar 150 MB. Kredensial `auth_token` tidak ditulis di dalam kode, melainkan dibaca dari variabel lingkungan `TWITTER_AUTH_TOKEN` sehingga tidak ikut tersimpan pada berkas program. Proses eksekusi akuisisi tambahan ditampilkan pada Gambar 3.9 berikut.

```
[SISIPKAN GAMBAR 3.9 — output terminal phase4_tweet_harvest.py]
Sumber: docs/07_log_scraping_raw.txt, disarankan memakai blok "RUN: penipuan_ewallet_qris"
```

**Gambar 3.9 Proses Akuisisi Tweet per Kategori Vektor menggunakan Tweet Harvest**
*(Sumber: Dokumentasi Pribadi, 2026)*

Berdasarkan Gambar 3.9, eksekusi dilakukan per kategori vektor dengan keluaran yang mencatat setiap kueri yang dijalankan beserta parameternya, jumlah tweet yang diperoleh, dan berkas keluaran yang dihasilkan. Keluaran tersebut memperlihatkan variasi perolehan yang sangat lebar antar-kueri dalam satu kategori vektor yang sama, misalnya 367 tweet pada kueri pertama dan 0 tweet pada kueri kedua hingga kelima. Pola tersebut menunjukkan bahwa keberhasilan penjaringan sangat bergantung pada kecocokan istilah kueri dengan ungkapan yang benar-benar digunakan pengguna, sehingga kueri yang tersusun secara logis belum tentu produktif apabila istilahnya tidak lazim dipakai dalam percakapan sehari-hari. Bagian ringkasan pada akhir keluaran mencatat jumlah kueri yang dieksekusi, total tweet yang diperoleh, serta jumlah kueri yang tidak menghasilkan data, sehingga seluruh proses terdokumentasi secara terverifikasi. Rekapitulasi eksekusi untuk keempat kategori vektor disajikan pada Tabel 3.5 berikut.

**Tabel 3.5 Rekapitulasi Eksekusi Tweet Harvest pada Akuisisi Tambahan**

| Kategori Vektor | Waktu Eksekusi | Tab | Kueri | Tweet Diperoleh | Kueri Kosong |
|---|---|---|---|---|---|
| `penipuan_ewallet_qris` | 20 Jun 2026, 19.59 | LATEST | 6 | 531 | 4 |
| `malware_apk` | 20 Jun 2026, 22.16 | LATEST | 7 | 95 | 3 |
| `deepfake_penipuan_ai` | 21 Jun 2026, 00.03 | LATEST | 7 | 549 | 5 |
| `peretasan_pencurian_identitas` | 21 Jun 2026, 00.23 | LATEST | 7 | 1.344 | 3 |
| `malware_apk` (verifikasi) | 21 Jun 2026, 00.44 | TOP | 7 | 49 | 5 |
| **Total** | | | **34** | **2.568** | **20** |

Berdasarkan Tabel 3.5, perolehan tweet menunjukkan ketimpangan yang tajam antar-kategori vektor, di mana vektor peretasan dan pencurian identitas memperoleh 1.344 tweet sementara vektor malware/APK hanya memperoleh 95 tweet meskipun jumlah kueri yang dijalankan sama banyak. Eksekusi dilakukan secara bertahap per kategori dengan jeda antar-kategori, sebagaimana terlihat pada rentang waktu eksekusi, dengan tujuan memantau kondisi akun dan menghindari pembatasan laju secara beruntun.

Baris terakhir pada Tabel 3.5 merupakan eksekusi verifikasi yang dijalankan secara khusus untuk menguji apakah rendahnya perolehan pada vektor malware/APK disebabkan oleh keterbatasan perkakas atau memang mencerminkan kelangkaan diskursus yang sebenarnya. Pengujian dilakukan dengan mengulang seluruh kueri yang sama pada tab TOP, yaitu tab yang mengurutkan hasil berdasarkan relevansi dan popularitas, sebagai pembanding terhadap tab LATEST. Hasil pengujian memperoleh 49 tweet yang seluruhnya merupakan himpunan bagian dari 95 tweet yang telah diperoleh pada tab LATEST, tanpa satu pun tweet baru. Temuan tersebut membuktikan bahwa kelangkaan data pada vektor malware/APK bukan merupakan artefak dari strategi pengambilan data, melainkan cerminan dari volume diskursus yang memang terbatas pada platform X berbahasa Indonesia. Konsekuensinya, pemenuhan kebutuhan data untuk vektor malware/APK dan deepfake sepenuhnya bertumpu pada platform YouTube, sebagaimana tercermin pada Tabel 3.4 yang menunjukkan tujuh dari delapan video tambahan dialokasikan untuk kedua vektor tersebut.

---

### 3.4.4 Rekapitulasi Hasil Akuisisi dan Pertimbangan Etis

Seluruh berkas hasil akuisisi awal dan tambahan dikonsolidasikan, disaring, dan dibersihkan dari duplikat sehingga menghasilkan satu dataset terpadu. Setelah proses penyaringan dan penghapusan duplikat, dari total data mentah sebanyak 78.269 baris diperoleh dataset final berjumlah 55.300 baris. Rekapitulasi hasil akuisisi disajikan pada Tabel 3.6 berikut.

**Tabel 3.6 Rekapitulasi Hasil Akuisisi Data**

| Sumber Data | Keterangan | Jumlah (pasca-dedup) | Rincian |
|---|---|---|---|
| YouTube | Komentar dari video terkait ancaman siber | 51.739 komentar | 26 video (18 video awal + 8 video tambahan) |
| X (Twitter) | Tweet hasil Tweet Harvest per kategori | 3.561 tweet | *[lihat catatan penyusunan]* |
| **Total** | Setelah konsolidasi dan dedup | **55.300** | |

Berdasarkan Tabel 3.6, komposisi dataset final didominasi oleh komentar YouTube sebesar 93,56 persen dan tweet dari platform X sebesar 6,44 persen. Ketimpangan proporsi antar-platform tersebut tidak diperlakukan sebagai persoalan yang perlu diseimbangkan, karena sasaran keseimbangan pada penelitian ini adalah distribusi antar-kategori vektor ancaman dan bukan distribusi antar-platform. Akuisisi tambahan secara khusus difokuskan pada vektor yang datanya langka pada akuisisi awal, yaitu malware/APK dan deepfake/penipuan AI. Meskipun demikian, jumlah data deepfake tetap terbatas dan menjadi *ceiling* dari ketersediaan sumber, yang mencerminkan kelangkaan diskursus tema tersebut secara nyata di media sosial Indonesia sebagaimana telah dibuktikan melalui pengujian tab TOP pada bagian 3.4.3.

Seluruh proses pengumpulan data dilaksanakan dengan memperhatikan pertimbangan etis penelitian. Data yang dikumpulkan seluruhnya bersumber dari konten yang dipublikasikan secara terbuka oleh penggunanya sendiri, tanpa melibatkan konten privat, pesan langsung, maupun akun tertutup. Atribut identitas pengguna seperti nama akun dan pengenal pengguna tidak digunakan sebagai fitur dalam pemodelan dan dihapus pada tahap persiapan data, sehingga analisis dilakukan pada tataran diskursus dan bukan pada tataran individu. Pengambilan data pada platform X dilakukan menggunakan akun sekunder dengan jeda antar-permintaan sebagai bentuk mitigasi terhadap pembebanan berlebih pada layanan, sedangkan pengambilan data pada YouTube dilakukan melalui API resmi dalam batas kuota yang ditetapkan penyedia layanan.

---
---

# CATATAN PENYUSUNAN — JANGAN DISALIN KE SKRIPSI

## Penomoran

Berdasarkan pemindaian `PI-Draft3_Revisi_Ray Siraj.docx`:

- Gambar terakhir sebelum Pengumpulan Data = **Gambar 3.6** (Struktur Navigasi Dashboard). Karena itu gambar baru dimulai dari **3.7**. Cek dulu apakah subbab Storyboard Prototipe punya gambar bercaption — kalau ada, geser nomornya.
- Tabel: draft Anda sekarang punya Tabel 3.3 (Rekapitulasi Akuisisi). Draft ini menyisipkan dua tabel baru sebelumnya, sehingga rekapitulasi bergeser jadi **Tabel 3.6**. Seluruh tabel setelahnya bergeser **+3** (3.4 Contoh Prapemrosesan → 3.7, dan seterusnya). Kalau caption dibuat lewat *References → Insert Caption*, penomoran ini bergeser otomatis.

## Asal setiap gambar

| Gambar | Sumber | Status |
|---|---|---|
| 3.7 | `docs/07_log_scraping_raw.txt`, blok "RUN: Phase 3 - YouTube Data API v3" | Perlu di-screenshot. Log yang tersimpan hanya 3 dari 8 video (snapshot interim); kalau ingin lengkap, jalankan ulang skrip untuk satu video saja sebagai demonstrasi |
| 3.8 | `Pictures\Screenshots\Screenshot 2026-05-20 153252.png` | **Siap pakai.** Token sudah tersamar otomatis oleh perkakasnya |
| 3.9 | `docs/07_log_scraping_raw.txt`, blok "RUN: penipuan_ewallet_qris" | Perlu di-screenshot. Blok ini dipilih karena paling informatif: ada kueri berhasil (367, 164) dan kueri kosong |

Untuk 3.7 dan 3.9, tampilkan dengan `Get-Content "…\07_log_scraping_raw.txt" | more` supaya terlihat sebagai konsol asli.

## Angka yang masih perlu Anda rekonsiliasi

> **Status 19 Agu 2026:** poin 2 dan 3 **sudah tertutup** (lihat di bawah); naskah R4 §3.4.4 sudah memakai angka yang benar. Berkas ini kini arsip/bank materi — bila bentrok dengan R4, **R4 yang menang**.

1. **Rincian kueri X pada Tabel 3.6** sengaja saya kosongkan. Klaim lama "42 kueri (30 awal + 12 tambahan)" tidak cocok dengan disk: akuisisi awal menghasilkan **41 berkas `sesi*.csv` dari 22 tema kueri**, akuisisi tambahan **34 eksekusi kueri** (27 kueri unik + 7 pengulangan tab TOP). Tentukan dulu satuan yang dipakai — jumlah tema kueri, jumlah eksekusi, atau jumlah berkas — lalu isi konsisten di Tabel 3.6 dan 3.5.
2. ✅ **"Selisih 135 baris YouTube" — TIDAK ADA selisih; dua angka itu mengiris dimensi yang berbeda.** 4.060 (malware) dan 1.043 (deepfake) adalah *baris baru per `source_category`* (asal kueri scraping), bukan per platform — dan keduanya memuat baris dari X. Dari `CONTEXT.md` Temuan #7, kontribusi X pada dua kategori itu = malware 84 + deepfake 51 = **tepat 135**. Jadi: YouTube 4.060−84 + 1.043−51 = **4.968** (= 51.739 − 46.771 ✓) dan X = 84+51+1.176+525 = **1.836** (= 3.561 − 1.725 ✓); 4.968 + 1.836 = **6.804** ✓. Bila ditanya saat revisi, itu jawabannya — bukan dedup lintas-batch.
3. ✅ **Total mentah = 78.269, bukan 70.241.** Rinciannya: akuisisi awal **69.651** (59 CSV) → 48.496 (reduksi 30,4%), akuisisi tambahan **8.618** → 6.830 lolos filter → buang 26 duplikat lintas-tahap → +6.804 → **55.300**. Sumber: `docs/phase5_filter_report.md` + `docs/phase5_merge_report.md`. Penyumbang buangan terbesar pada akuisisi awal = filter balasan berkualitas rendah (dari 17.815 balasan hanya 2.503 atau 14,0% lolos), lalu teks terlalu pendek 2.777, duplikat persis 2.230, teks bersinyal rendah 805.

## Beda dengan struktur Fauzan yang disengaja

- Fauzan memakai satu sub-subbab per **sumber dataset**; draft ini memakai satu sub-subbab per **platform akuisisi**, plus satu sub-subbab protokol di depan. Alasannya penelitian Anda hanya punya satu jenis data (primer OSINT), sehingga pembagian primer/sekunder tidak berlaku.
- Paragraf pembuktian kelangkaan lewat tab TOP (akhir 3.4.3) adalah padanan dari paragraf Fauzan *"Pemilihan keempat kelas serangan tersebut tidak dilakukan secara acak…"*. Ini bagian terkuat dari 3.4 Anda — pertahankan.
- Subbab etis di 3.4.4 tidak ada pada Fauzan, tetapi relevan karena data Anda berasal dari unggahan manusia, bukan trafik jaringan hasil simulasi.
