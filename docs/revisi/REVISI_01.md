# Revisi 01 — Naskah PI

Naskah acuan: `Ray Siraj_51423248_R4.docx`. Sembilan poin dari penguji.

Penanda lokasi memakai potongan kalimat yang ada di naskah, cari dengan Ctrl+F.

---

## Poin 1 — Perbarui jurnal, usahakan 5 sampai 10 tahun terakhir

### Kondisi sekarang

89 entri: 37 terbit 2021 ke atas (42%), 43 terbit sebelum 2021, 9 tanpa tahun. Bila batasnya 10 tahun, 58 entri terbit 2016 ke atas (65%).

Angka itu tidak buruk. Yang lebih rawan dipersoalkan justru bukan usia, melainkan dua rujukan yang bukan sumber ilmiah: satu blog pribadi dan satu artikel blog kampus.

### Yang wajib dipertahankan, beserta alasan siap pakai

Jangan ganti entri berikut. Kalau ditanya kenapa masih memakai sumber lama, alasannya ada di kolom kanan.

| Entri | Alasan |
|---|---|
| Landis & Koch (1977) | Sumber asli ambang interpretasi Cohen Kappa yang dipakai menilai κ 0,925. Menggantinya memutus rantai rujukan ke definisi ambang itu sendiri. |
| Brooke (1996) | Instrumen SUS itu sendiri. Skor 81,33 dihitung memakai rumus dari makalah ini. |
| Hochreiter & Schmidhuber (1997) | Makalah asli LSTM. |
| Schuster & Paliwal (1997) | Makalah asli arsitektur rekuren dua arah, dasar BiGRU dan BiLSTM. |
| Cho dkk. (2014) | Makalah asli GRU. |
| Devlin dkk. (2019) | Makalah asli BERT. |
| Wilie dkk. (2020) | Makalah asli IndoBERT dan IndoNLU, yaitu model yang dipakai. |
| Ratner dkk. (2017) | Makalah asli Snorkel. |
| Ribeiro dkk. (2016) | Makalah asli LIME. |
| Lundberg & Lee (2017) | Makalah asli SHAP, dipakai sebagai pembanding konseptual. |
| Kingma & Ba (2017), Loshchilov & Hutter (2018) | Makalah asli Adam dan AdamW, yaitu optimizer yang dipakai. |
| Vaswani dkk. | Makalah asli Transformer. |
| Bangor dkk. (2008), Lewis (2018), Sauro (2016) | Rujukan baku penafsiran skor SUS beserta grade-nya. |
| Sokolova & Lapalme (2009) | Rujukan baku definisi metrik klasifikasi multikelas. |
| Fielding (2000) | Disertasi asal gaya arsitektur REST. |
| Goodfellow dkk. (2016) | Buku rujukan baku deep learning. |

Kalimat pembelaan bila diminta: rujukan tersebut adalah sumber primer dari metode yang dipakai, bukan sumber pendukung yang bisa disegarkan. Penyegaran dilakukan pada rujukan pendukung dan pembanding empiris, yang seluruhnya terbit 2021 ke atas.

### Yang perlu diganti

Enam entri berikut lemah atau tua tanpa alasan kuat. Empat di antaranya bisa diganti dengan sumber yang **sudah ada di daftar pustaka Anda**, jadi tidak perlu mencari apa pun.

| Ganti entri ini | Dengan | Catatan |
|---|---|---|
| Andre (2018), blog `andre.id` tentang struktur navigasi | Vaughan & Borch (2011), sudah Anda sitasi | Vaughan adalah sumber asli taksonomi struktur navigasi linear, hirarki, non-linear, dan campuran. Blog pribadi harus dikeluarkan. |
| PuTI (2025), artikel blog Telkom University tentang flowchart | Pressman & Maxim (2020) atau Sommerville (2016), sudah Anda sitasi | Flowchart adalah materi baku rekayasa perangkat lunak. |
| GeeksforGeeks (n.d.) tentang confusion matrix | Sokolova & Lapalme (2009), sudah Anda sitasi | Situs tutorial bukan rujukan ilmiah. |
| Mitchell (2013), buku Machine Learning | Russell & Norvig (2021), sudah Anda sitasi | Buku Mitchell adalah cetak ulang edisi 1997. |
| Nidhra (2012) tentang black box testing | Santi dkk. (2022), sudah Anda sitasi | Lebih baru, berbahasa Indonesia, dan konteks pengujiannya sama. |
| Glassman & Kang (2012) tentang OSINT | Browne dkk. (2024), entri baru di bawah | Boleh dipertahankan berdampingan bila definisi OSINT-nya dikutip langsung, tetapi klaim tentang praktik OSINT terkini sebaiknya bersandar pada yang 2024. |

### Entri baru, sudah diverifikasi ke Crossref

Salin apa adanya. Tetap buka tautannya sekali untuk memastikan.

Browne, T. O., Abedin, M., & Chowdhury, M. J. M. (2024). A systematic review on research utilising artificial intelligence for open source intelligence (OSINT) applications. *International Journal of Information Security*, *23*(4), 2911–2938. https://doi.org/10.1007/s10207-024-00868-2

Xiong, Y., Chen, G., & Cao, J. (2024). Research on public service request text classification based on BERT-BiLSTM-CNN feature fusion. *Applied Sciences*, *14*(14), 6282. https://doi.org/10.3390/app14146282

Entri kedua dipakai juga pada poin 9. Bila ingin tambahan berkonteks Indonesia, ada Murfi dkk. (2022), *BERT-Based Combination of Convolutional and Recurrent Neural Network for Indonesian Sentiment Analysis*, arXiv:2211.05273. Cek dulu apakah sudah terbit di jurnal, karena versi arXiv adalah pracetak.

### Sembilan entri tanpa tahun

Dokumentasi Python, Kaggle, Hugging Face, Next.js, TypeScript, dan Vercel bukan masalah keilmuan, tetapi formatnya perlu dirapikan: cantumkan pemilik sebagai penulis korporat dan tahun akses, misalnya `Vercel. (2026). Vercel documentation. Diakses 3 Agustus 2026, dari https://vercel.com/docs`. Entri GeeksforGeeks dikeluarkan sesuai tabel di atas.

### Hasil akhir bila seluruh usulan dijalankan

Enam entri keluar, dua entri baru masuk, total menjadi 85. Entri 2021 ke atas menjadi 38 dari 85 atau 45 persen. Bila delapan dokumentasi web diberi tahun akses 2026, porsi rujukan mutakhir menjadi 46 dari 85 atau 54 persen.

---

## Poin 2 — Jelaskan data dari akuisisi sampai matang, tunjukkan sampelnya

Subbab 3.4 dan 3.5 sudah memuat protokol kurasi, kode pemanggilan API, kode prapemrosesan, dan contoh hasil prapemrosesan. Yang belum ada dan diminta penguji: wujud data mentahnya, dan satu baris data yang ditelusuri utuh dari mentah sampai masuk berkas latih. Tiga sisipan berikut menutup kekurangan itu.

### Sisipan 2a — wujud data mentah

**Lokasi:** subbab 3.4.4, sebelum kalimat "Seluruh berkas hasil akuisisi awal dan tambahan dikonsolidasikan".

**Tindakan:** sisipkan paragraf berikut beserta satu tabel baru.

**Teks:**

Sebelum dikonsolidasikan, hasil akuisisi tersimpan sebagai berkas CSV terpisah, yaitu satu berkas per video untuk YouTube dan satu berkas per kueri untuk platform X, dengan struktur kolom berbeda mengikuti keluaran masing-masing perkakas. Perbedaan struktur inilah yang kemudian diseragamkan pada tahap konsolidasi. Contoh keluaran mentah kedua sumber disajikan pada Tabel 3.x.

**Tabel 3.x Contoh Keluaran Mentah Akuisisi**

| Sumber | Kolom keluaran | Contoh isi satu baris |
|---|---|---|
| YouTube Data API v3 | comment_id, author, text, likes, replies, published_at, is_reply | Ugzt0-z7rTHjXW2OGbR4AaABAg; @DigitalSentinel-***; "Biar gak apes kena link aneh, HP gue udah ada Norton Mobile Security"; 0; 0; 2025-10-25T19:49:34Z; False |
| X melalui Tweet Harvest | conversation_id_str, created_at, favorite_count, full_text, id_str, lang, quote_count, reply_count, retweet_count, tweet_url, user_id_str, username | 1646500877778448387; 2023-04-13T13:09:34.000Z; 5; "Ssst, hati-hati QRIS palsu! ... https://t.co/Jm5rHj2WPY"; in; 0; 1; 0; tautan tweet; @Sapawarga*** |

Berdasarkan Tabel 3.x, keluaran YouTube memuat penanda balasan pada kolom is_reply yang menjadi dasar penyaringan balasan berkualitas rendah, sedangkan keluaran platform X memuat kolom lang yang menjadi dasar pembatasan bahasa Indonesia. Nama akun ditampilkan tersamar karena identitas pengguna tidak digunakan sebagai fitur dan dihapus pada tahap persiapan data.

**Sumber:** kolom YouTube dari `raw_additional_youtube/malware_apk/BzmlRE8xRMU.csv`, kolom X dari `raw_additional_tweets/penipuan_ewallet_qris/q1.csv`.

### Sisipan 2b — perjalanan satu baris data

**Lokasi:** akhir subbab 3.5.4, setelah kalimat "Hasil pada Tabel 3.11 menunjukkan bahwa pendekatan weak supervision mampu menghasilkan label dengan akurasi tinggi".

**Tindakan:** sisipkan paragraf berikut beserta satu tabel baru.

**Teks:**

Untuk memperlihatkan keseluruhan tahapan secara utuh, satu baris data ditelusuri sejak bentuk mentahnya hingga bentuk akhir yang diterima model. Baris yang dipilih adalah data berindeks UID053698, yaitu sebuah tweet edukasi mengenai QRIS palsu, karena memuat seluruh jenis transformasi sekaligus, yakni emoji, tautan, dan ragam bahasa informal. Penelusurannya disajikan pada Tabel 3.y.

**Tabel 3.y Perjalanan Satu Baris Data dari Bentuk Mentah hingga Siap Latih**

| Tahap | Kolom | Isi |
|---|---|---|
| Akuisisi | full_text | Ssst, hati-hati QRIS palsu! 🤫 Biar nggak gampang kegocek kayak Bang Messi, yuk cari tahu gimana cara bedain QRIS asli dan palsu 🫣 Langsung aja cek postingan berikut ini 💁🏼‍♂️ https://t.co/Jm5rHj2WPY |
| Konsolidasi | unified_id, platform, lang, published_at | UID053698; X; in; 2023-04-13 |
| Prapemrosesan | text_clean | ssst, hati-hati qris palsu! biar nggak gampang kegocek kayak bang messi, yuk cari tahu gimana cara bedain qris asli dan palsu [EMOSI_TAKUT] langsung aja cek postingan berikut ini [EMOSI_WASPADA] [URL] |
| Prapemrosesan | text_normalized, tidak dipakai model | ssst, hati-hati qris palsu! biar tidak gampang kegocek seperti bang messi, yuk cari tahu bagaimana cara bedain qris asli dan palsu [EMOSI_TAKUT] langsung saja cek postingan berikut ini [EMOSI_WASPADA] [URL] |
| Prapemrosesan | text_stemmed, tidak dipakai model | ... biar tidak gampang **gocek** seperti bang messi ... cek postingan **ikut** ini ... |
| Pelabelan | layer1_label, layer2_label, speaker_role, lm_confidence | relevan; penipuan_ewallet_qris; R3; 0,8732 |
| Pemisahan | berkas tujuan | layer1_train.csv dan layer2_val.csv |

Berdasarkan Tabel 3.y, tahap prapemrosesan mengubah emoji bermuatan emosi menjadi token penanda, mengganti tautan dengan token URL, dan menurunkan seluruh huruf menjadi huruf kecil, sementara ragam informal seperti nggak, aja, dan gimana sengaja dipertahankan pada kolom text_clean karena justru menjadi penanda khas diskursus media sosial. Kolom text_normalized dan text_stemmed dihasilkan sebagai pembanding dan tidak digunakan sebagai masukan model. Kolom text_stemmed pada baris ini sekaligus memperlihatkan alasannya, yaitu proses stemming mengubah kata kegocek menjadi gocek dan mengubah kata berikut menjadi ikut, sehingga makna kalimat bergeser. Baris tersebut selanjutnya memperoleh label relevan pada Layer 1 dan label penipuan_ewallet_qris pada Layer 2 dengan tingkat keyakinan label sebesar 0,8732, lalu ditempatkan pada data latih Layer 1 dan data validasi Layer 2 sesuai pemisahan yang dijalankan terpisah bagi kedua lapis.

**Sumber:** `data/preprocessed_dataset_v2.csv`, `data/weak_labeled_dataset_v2.csv`, dan berkas pada `data/splits/`, seluruhnya baris UID053698.

Catatan: dua kata yang dicetak tebal pada baris text_stemmed hanya penanda untuk Anda. Di Word cukup tulis biasa, atau beri cetak miring bila ingin ditonjolkan.

### Sisipan 2c — definisi data matang

**Lokasi:** akhir subbab 3.6, setelah pemaparan proporsi pemisahan.

**Tindakan:** sisipkan satu paragraf sebagai penutup rangkaian persiapan data.

**Teks:**

Dengan selesainya pemisahan, data dinyatakan siap dilatihkan. Bentuk akhir yang diterima model bukan lagi berkas mentah hasil akuisisi, melainkan enam berkas terpisah yang hanya memuat kolom identitas, kolom teks bersih, dan kolom label, yaitu unified_id, platform, source_category, vector_hint, text_clean, dan label. Bagi Model A tersedia 44.240 baris data latih, 5.530 baris data validasi, dan 5.530 baris data uji, sedangkan bagi Model B tersedia 7.369 baris data latih, 921 baris data validasi, dan 922 baris data uji. Seluruh kolom lain, termasuk nama akun, tautan asal, dan metrik keterlibatan, tidak diikutsertakan sehingga pemodelan berlangsung sepenuhnya pada tataran teks.

**Sumber:** `data/splits/_split_manifest.json`.

---

## Poin 3 — Abstrak terlalu padat, satu paragraf panjang, lebihi 200 kata

ABSTRAK sekarang 338 kata, ABSTRACT 405 kata. Keduanya dipangkas ke batas 200 kata. Yang dibuang: rincian delapan tahap pengembangan model, penyebutan Badan Siber dan Sandi Negara, uraian panjang ablation study, dan pengulangan angka accuracy yang sudah terwakili macro-F1. Yang dipertahankan: masalah, tujuan, sumber dan ukuran data, arsitektur, hasil kedua model, XAI, dan prototipe beserta skor SUS.

### 3a — ABSTRAK (194 kata)

**Lokasi:** halaman ABSTRAK, paragraf yang dimulai "Eskalasi ancaman siber di Indonesia yang tercatat pada laporan tahunan Badan Siber dan Sandi Negara".

**Tindakan:** ganti seluruh paragraf.

**Teks:**

Eskalasi ancaman siber di Indonesia disertai pergeseran modus dari eksploitasi teknis menuju rekayasa sosial, sehingga jejak ancaman turut terekam pada diskursus publik di media sosial. Pemanfaatannya terkendala ketiadaan taksonomi yang sesuai dengan konteks ancaman lokal, keterbatasan data berlabel pada teks informal berbahasa Indonesia, serta kecenderungan penelitian terdahulu berhenti pada satu vektor ancaman tanpa perwujudan sistem. Penelitian ini membangun sistem klasifikasi otomatis diskursus vektor ancaman siber pada media sosial Indonesia menggunakan arsitektur triple-hybrid yang dilengkapi Explainable AI. Data dihimpun dari platform X dan YouTube menggunakan teknik Open Source Intelligence sebanyak 78.269 baris mentah dan menyisakan 55.300 baris setelah penyaringan. Pelabelan otomatis menggunakan framework Snorkel dengan 56 labeling function menghasilkan 9.212 baris relevan pada enam vektor E-ICTT, divalidasi terhadap 357 sampel gold standard dengan tingkat kesepakatan antaranotator almost perfect agreement. Model disusun sebagai pipeline dua lapis yang memadukan IndoBERT-base-p1 dengan BiGRU dan BiLSTM serta komponen berbasis aturan melalui late fusion berbobot 0,75 dan 0,25. Model A mencapai macro-F1 0,9680 dengan recall kelas relevan 0,9674, sedangkan Model B mencapai macro-F1 0,9767 atas 922 data uji. Interpretasi LIME memperlihatkan model mempelajari sinyal domain yang benar. Model diwujudkan ke dalam prototipe dashboard CyberScope dengan skor System Usability Scale 81,33.

### 3b — ABSTRACT (200 kata)

**Lokasi:** halaman ABSTRACT, paragraf yang dimulai "The escalation of cyber threats in Indonesia recorded in the annual reports".

**Tindakan:** ganti seluruh paragraf.

**Teks:**

The escalation of cyber threats in Indonesia has been accompanied by a shift from technical exploitation towards social engineering, leaving traces in public discourse on social media. Its use is hindered by the absence of a locally suited taxonomy, the scarcity of labelled data for informal Indonesian text, and previous studies stopping at a single vector without realising a working system. This study builds an automatic classification system for such discourse using a triple-hybrid architecture with Explainable AI. Data were collected from X and YouTube through Open Source Intelligence, comprising 78,269 raw records reduced to 55,300 after filtering. Automatic labelling with Snorkel using 56 labeling functions yielded 9,212 relevant records across the six E-ICTT vectors, validated against 357 gold-standard samples with almost perfect inter-annotator agreement. The model is a two-layer pipeline combining IndoBERT-base-p1 with BiGRU and BiLSTM alongside a rule-based component through late fusion weighted 0.75 and 0.25. Model A achieved a macro-F1 of 0.9680 with a relevant-class recall of 0.9674, while Model B achieved a macro-F1 of 0.9767 on 922 test records. LIME interpretation showed that the model learns correct domain signals. The model was realised into the CyberScope dashboard prototype, with a System Usability Scale score of 81.33.

Kata kunci, baris identitas, dan baris jumlah halaman tidak diubah.

---

## Poin 4 — Istilah asing belum konsisten dicetak miring

### Yang dimiringkan

Miringkan pada setiap kemunculan di dalam kalimat naratif:

pipeline, hyperparameter, late fusion, weak supervision, dropout, pooling, masked-mean pooling, cross-sectional snapshot, fine-tuning, framework, preprocessing, noise, slang, code-mixing, anchor, anchor share, relevance detector, vector separator, class weight, focal loss, oversampling, learning rate, batch size, epoch, optimizer, softmax, argmax, encoder, embedding, self-attention, attention head, hidden size, tokenizer, training set, validation set, test set, confusion matrix, false positive, false negative, accuracy, precision, recall, sweep, knee, ablation study, gold standard, labeling function, inter-annotator agreement, almost perfect agreement, state dictionary, checkpoint, blackbox testing, usability, cold start, backend, frontend, deployment, scraping, query, rate limit, cookie, real-time, on-demand, drill-down, funnel, storytelling, payload.

### Yang tidak dimiringkan

- Nama produk, pustaka, dan platform: IndoBERT, BERT, BiGRU, BiLSTM, PyTorch, Snorkel, LIME, SHAP, FastAPI, Next.js, React, TypeScript, Kaggle, Hugging Face Spaces, Vercel, Tweet Harvest, CyberScope, X, YouTube.
- Nama berkas, kelas, fungsi, kolom, dan variabel: text_clean, clean_text, TripleHybridLayer2, layer1_train.csv, unified_id.
- Singkatan yang sudah menjadi nama: OSINT, API, CSV, GPU, URL, QRIS, APK, SUS, E-ICTT, ICTT.
- Kata yang sudah terserap KBBI: data, internet, komputer, digital, aplikasi, sistem, format, teks, dokumen, video, audio, media sosial.
- Nama kategori vektor: phishing_rekayasa_sosial, judi_online_pinjol, dan seterusnya. Ini nama label, bukan istilah asing lepas.

### Cara mengerjakan di Word

1. Ctrl+H, isi Find what dan Replace with dengan kata yang sama.
2. Klik Replace with, lalu Format, lalu Font, pilih Italic, klik OK.
3. Replace All, ulangi untuk istilah berikutnya.
4. Setelah selesai semua, periksa blok kode. Find and Replace juga mengenai teks di dalam tabel kode, jadi seleksi tiap tabel kode lalu tekan Ctrl+I sekali untuk mengembalikannya menjadi tegak.
5. Periksa juga daftar pustaka, karena judul artikel berbahasa Inggris tidak boleh ikut berubah gaya.

Kerjakan satu istilah dalam satu kali Replace All, jangan memakai wildcard, agar mudah dibatalkan kalau salah.

---

## Poin 5 — Kenapa class weight, bukan focal loss atau SMOTE

**Lokasi:** subbab 3.7, kalimat "Penanganan ketidakseimbangan kelas menggunakan class weights dinilai memadai, sehingga fungsi loss yang lebih kompleks seperti focal loss tidak diperlukan, mengingat kategori kecil seperti deepfake dan malware telah menunjukkan performa yang baik pada eksperimen awal."

**Tindakan:** ganti kalimat itu dengan tiga paragraf berikut. Kalimat sebelum dan sesudahnya, yaitu tentang learning rate dan tentang bobot late fusion, tetap.

**Teks:**

Penanganan ketidakseimbangan kelas pada penelitian ini menggunakan class weight berbasis inverse frequency, yaitu pembobotan yang memperbesar kontribusi galat kelas minoritas pada fungsi loss tanpa mengubah komposisi data. Dua alternatif yang lazim dipertimbangkan, yaitu Synthetic Minority Over-sampling Technique (SMOTE) dan focal loss, tidak dipilih dengan pertimbangan berikut.

SMOTE bekerja dengan menyintesis data baru melalui interpolasi linear antartetangga terdekat pada ruang fitur numerik yang bersifat kontinu. Masukan model pada penelitian ini bukan vektor fitur statis, melainkan barisan token diskret yang representasinya dibentuk ulang oleh IndoBERT pada setiap proses fine-tuning, sehingga hasil interpolasi antardua barisan token tidak memiliki padanan teks yang sah dan justru merusak struktur bahasa yang hendak dipelajari. Selain itu, penerapan oversampling pada kategori deepfake yang hanya memuat 86 baris data latih berisiko membuat model menghafal segelintir contoh yang digandakan, bukan mempelajari polanya. Kedua keluarga penanganan tersebut, yaitu penanganan pada tataran data dan penanganan pada tataran fungsi loss, dibahas Johnson dan Khoshgoftaar (2019) serta Henning dkk. (2023) beserta kelebihan dan keterbatasan masing-masing.

Focal loss menambahkan parameter pemfokus gamma yang menurunkan bobot data yang sudah mudah diklasifikasikan agar model lebih memperhatikan data sulit. Penambahan tersebut membawa satu hyperparameter baru yang menuntut penyetelan tersendiri, sedangkan pembobotan kelas terbukti sudah memadai sebagaimana dipaparkan pada subbab evaluasi Model B, yaitu F1-score sebesar 0,96 untuk kategori malware dan 1,00 untuk kategori deepfake yang justru merupakan dua kategori terkecil. Fungsi focal loss tetap disiapkan pada kode pelatihan sebagai opsi yang dapat diaktifkan melalui parameter loss, namun tidak diaktifkan karena tidak diperlukan. Perlu dicatat secara jujur bahwa keputusan tersebut diambil berdasarkan kecukupan hasil pembobotan kelas, bukan berdasarkan perbandingan langsung antara keduanya dalam satu eksperimen terkendali. Perbandingan terkendali antara class weight, focal loss, dan teknik penyeimbangan lain merupakan salah satu arah pengembangan lanjutan.

**Sumber angka:** F1 per kategori dari Tabel 3.14 pada naskah; jumlah 86 baris latih deepfake dari `data/splits/_split_manifest.json`; opsi focal loss dari `src/phase9_model_b_layer2.py`.

**Tambahan untuk Saran (BAB 4):** sisipkan pada paragraf saran sisi model, setelah kalimat tentang penanganan ketidakseimbangan kelas.

Perbandingan terkendali antara class weight berbasis inverse frequency, focal loss, dan teknik penyeimbangan pada tataran data juga perlu dijalankan pada rancangan eksperimen yang sama, sehingga pemilihan penanganan ketidakseimbangan kelas tidak hanya bersandar pada kecukupan hasil, melainkan pada perbandingan yang terukur.

---

## Poin 6 — Kenapa bertahan pada bobot 0,75 padahal 0,50 menghasilkan macro-F1 tertinggi

Pertanyaan penguji menyebut "w=0.75 untuk neural dan w=0.50 untuk rule-based". Perlu diluruskan lebih dulu: bobot sistem akhir adalah **0,75 untuk jalur neural dan 0,25 untuk jalur aturan**, jumlahnya satu. Angka 0,50 yang dimaksud adalah konfigurasi pembanding 0,50 berbanding 0,50 yang muncul pada sweep, bukan salah satu sisi dari konfigurasi terpilih. Luruskan ini lebih dulu saat menjawab, karena selebihnya pertanyaannya sah.

Naskah sudah menjawab sebagian pada subbab 3.10.3, yaitu bahwa keunggulan itu teridentifikasi pada data uji sehingga memilihnya menimbulkan bias evaluasi. Yang perlu ditambahkan adalah bukti bahwa keunggulan tersebut memang rapuh.

**Lokasi:** subbab 3.10.3, setelah kalimat "Bobot 0,75:0,25 dipertahankan sebagai keputusan rancangan a priori, dan angka empat sampel tersebut justru memperlihatkan betapa rapuhnya keunggulan yang terlihat."

**Tindakan:** sisipkan dua paragraf berikut.

**Teks:**

Kerapuhan tersebut dapat ditunjukkan dari tiga sisi. Pertama, selisih macro-F1 sebesar 0,0067 bertumpu pada empat sampel dari 922 data uji atau setara 0,43 persen, dan tidak disertai uji signifikansi statistik, sehingga selisih itu berada dalam rentang yang wajar disebabkan variasi acak. Kedua, keempat sampel tersebut berasal dari satu pasangan kategori yang sama, yaitu batas antara phishing dan judi, sehingga keunggulannya bersifat lokal pada satu titik kebingungan model dan bukan peningkatan kemampuan memisahkan keenam kategori secara menyeluruh. Ketiga, dan yang paling menentukan, bobot 0,50 berbanding 0,50 justru merusak Layer 1, yaitu precision kelas relevan anjlok menjadi 0,5047 yang berarti hampir separuh prediksi relevan sebenarnya keliru. Sebuah bobot yang unggul pada satu lapis tetapi runtuh pada lapis lain menunjukkan bahwa keunggulannya terikat pada karakteristik data uji tertentu, bukan sifat umum dari mekanisme fusion.

Prosedur yang sah untuk memilih bobot 0,50 sebenarnya tersedia, yaitu menjalankan sweep pada data validasi, mengunci bobot terpilih, lalu baru mengukurnya sekali pada data uji. Prosedur tersebut tidak ditempuh pada penelitian ini karena sweep dijalankan setelah pelatihan selesai sebagai sarana ablation study, bukan sebagai tahap penyetelan. Karena itu bobot 0,75 berbanding 0,25 dipertahankan sebagaimana ditetapkan sejak awal pada ruang lingkup penelitian, dan penyetelan bobot melalui data validasi dicatat sebagai pengembangan lanjutan.

**Sumber angka:** `docs/phase9_fusion_ablation.md`, tabel sweep Layer 1 dan Layer 2.

**Tambahan untuk Saran (BAB 4):**

Penetapan bobot late fusion juga dapat ditingkatkan dengan menjalankan penyapuan bobot pada data validasi, sehingga bobot terpilih memiliki dasar empiris tanpa menimbulkan bias evaluasi terhadap data uji.

---

## Poin 7 — Latar belakang mengkritik penelitian yang tidak mewujudkan sistem, tetapi pemantauan belum real-time

Pertanyaan ini menuduh adanya kesenjangan antara kritik dan hasil. Jawabannya bertumpu pada satu hal: yang dijanjikan adalah perwujudan model menjadi sistem yang berjalan, bukan pemantauan real-time. Kata real-time tidak pernah muncul pada Tujuan Penulisan maupun Ruang Lingkup.

**Lokasi:** subbab 3.11, setelah paragraf yang dimulai "Lingkungan deployment pada tier gratis memiliki karakteristik yang memengaruhi rancangan sistem".

**Tindakan:** sisipkan dua paragraf berikut.

**Teks:**

Rancangan dua jalur data tersebut perlu ditegaskan kaitannya dengan tujuan penelitian. Kritik terhadap penelitian terdahulu pada latar belakang diarahkan pada berhentinya penelitian di tataran pelaporan metrik tanpa perwujudan sistem yang dapat digunakan, bukan pada ketiadaan pemantauan yang berjalan seketika. Kesenjangan itulah yang ditutup oleh penelitian ini, yaitu model tidak berhenti sebagai berkas checkpoint melainkan diwujudkan menjadi layanan inferensi yang dapat diakses publik dan antarmuka yang dapat dicoba langsung. Pada halaman klasifikasi, teks yang dimasukkan pengguna diproses oleh kedua model secara langsung pada saat itu juga, sehingga jalur tersebut sepenuhnya berjalan waktu nyata terhadap masukan pengguna.

Adapun halaman pemantauan menampilkan hasil inferensi atas seluruh 55.300 baris data yang telah dihitung sebelumnya dan disimpan sebagai berkas pra-agregat. Pilihan tersebut bukan keterbatasan teknis yang tidak disadari, melainkan konsekuensi dari batasan yang telah dinyatakan pada ruang lingkup, yaitu akuisisi pada platform X bergantung pada token sesi yang masa berlakunya terbatas dan akuisisi pada YouTube dibatasi kuota harian, sehingga penjadwal akuisisi otomatis akan menjadi titik rapuh yang justru menurunkan keandalan sistem. Pemutakhiran data pemantauan secara berkala melalui pipeline akuisisi terjadwal dan basis data terpusat merupakan pengembangan lanjutan yang telah dicantumkan pada saran penelitian. Dengan demikian, tujuan mewujudkan model ke dalam prototipe yang berfungsi dan teruji tercapai, sedangkan pemantauan berkelanjutan berada di luar cakupan yang ditetapkan sejak awal.

### Penghalusan Tujuan Penulisan

**Lokasi:** Tujuan Penulisan butir kelima, kalimat "sehingga sistem yang dihasilkan dapat dimanfaatkan sebagai sistem peringatan dini dan pendukung keputusan bagi analis keamanan."

**Tindakan:** ganti penggal akhir kalimat itu. Frasa lama terbaca menjanjikan sistem operasional, dan itulah celah yang dipakai pertanyaan penguji.

**Teks pengganti:**

sehingga sistem yang dihasilkan dapat menjadi dasar bagi pengembangan sistem peringatan dini dan pendukung keputusan bagi analis keamanan.

---

## Poin 8 — Jelaskan perbandingan late fusion yang terbaik

Naskah sudah memaparkan kedua lapis pada subbab 3.10.3, tetapi tabel sweep hanya tersedia untuk Layer 1 dan hanya memuat tiga baris bobot, sedangkan Layer 2 diuraikan dalam bentuk narasi tanpa tabel. Penguji meminta perbandingan yang terbaca sekaligus. Dua sisipan berikut menutupnya.

### Sisipan 8a — tabel sweep Layer 2

**Lokasi:** subbab 3.10.3, setelah kalimat "Pada Layer 2, perilaku komponen aturan sangat berbeda."

**Tindakan:** sisipkan tabel baru. Perhatikan penomoran, lihat catatan di akhir berkas ini.

**Tabel 3.z Sweep Bobot Late Fusion pada Layer 2**

| Bobot neural | Bobot aturan | Macro-F1 | F1 phishing |
|---|---|---|---|
| 1,00 | 0,00 | 0,9767 | 0,9109 |
| 0,95 | 0,05 | 0,9767 | 0,9109 |
| 0,90 | 0,10 | 0,9767 | 0,9109 |
| 0,85 | 0,15 | 0,9747 | 0,9000 |
| 0,80 | 0,20 | 0,9747 | 0,9000 |
| 0,75 | 0,25 | 0,9747 | 0,9000 |
| 0,70 | 0,30 | 0,9747 | 0,9000 |
| 0,60 | 0,40 | 0,9747 | 0,9000 |
| 0,50 | 0,50 | 0,9814 | 0,9375 |

Bila tabel sweep Layer 1 ingin dilengkapi agar sebanding, baris lengkapnya adalah 1,00 dan 0,00 dengan macro-F1 0,9680 serta recall relevan 0,9674; 0,90 dan 0,10 dengan 0,9677 serta 0,9685; 0,85 dan 0,15 dengan 0,9675 serta 0,9707; 0,80 dan 0,20 dengan 0,9678 serta 0,9739; 0,75 dan 0,25 dengan 0,9679 serta 0,9761; 0,70 dan 0,30 dengan 0,9665 serta 0,9794; 0,60 dan 0,40 dengan 0,9478 serta 0,9859; 0,50 dan 0,50 dengan 0,7810 serta 1,0000.

### Sisipan 8b — paragraf perbandingan

**Lokasi:** subbab 3.10.3, sebelum paragraf penutup yang dimulai "Dari kedua lapis tersebut dapat disimpulkan bahwa jalur neural memikul beban diskriminatif utama".

**Tindakan:** sisipkan paragraf berikut.

**Teks:**

Perbandingan menyeluruh terhadap kedua lapis memperlihatkan bahwa konfigurasi terbaik tidak tunggal, melainkan bergantung pada tugas yang diemban masing-masing lapis. Pada Layer 1 yang bertugas menyaring relevansi, konfigurasi terbaik adalah 0,75 berbanding 0,25, karena pada titik itu recall kelas relevan naik dari 0,9674 menjadi 0,9761 dengan macro-F1 yang praktis tidak berubah, sedangkan penambahan bobot aturan melewati titik tersebut membuat jumlah false positive meningkat tajam hingga macro-F1 kolaps menjadi 0,7810 pada bobot 0,50. Pada Layer 2 yang bertugas memisahkan enam kategori, nilai macro-F1 tertinggi memang tercatat pada 0,50 berbanding 0,50 sebesar 0,9814, tetapi keunggulan itu bertumpu pada empat sampel dan runtuh bila diterapkan pada Layer 1, sehingga konfigurasi yang dipilih tetap 0,75 berbanding 0,25 dengan macro-F1 0,9747. Dengan demikian, konfigurasi 0,75 berbanding 0,25 merupakan satu-satunya bobot yang memberikan manfaat pada Layer 1 tanpa menimbulkan kerugian berarti pada Layer 2, dan atas dasar itulah bobot tersebut dipakai pada sistem akhir.

**Sumber angka:** `docs/phase9_fusion_ablation.md`.

---

## Poin 9 — Kenapa penambahan BiGRU dan BiLSTM lebih baik daripada IndoBERT saja

Poin ini dipindahkan ke berkas tersendiri, `REVISI_02.md`, karena isinya berubah setelah penggalian literatur dan perlu berdiri sendiri sebagai bahan sesi terpisah.

Ringkas perubahannya: Mujilahwati dkk. (2026) ternyata **tidak** memuat baseline IndoBERT-saja, sedangkan Talaat (2023) yang sudah ada di daftar pustaka justru membandingkan langsung terhadap model BERT standalone. Jawabannya juga di-reframe, dari mengklaim keunggulan menjadi menyatakan arsitektur diadopsi dari penelitian rujukan sementara kebaruan penelitian ini ada di tempat lain.

Jangan pakai versi lama poin 9 yang sempat ada di berkas ini.

---

## Catatan penomoran tabel

Sisipan ini menambah empat tabel baru, yaitu Tabel 3.x pada 3.4.4, Tabel 3.y pada 3.5.4, dan Tabel 3.z pada 3.10.3. Seluruh tabel setelahnya bergeser. Kalau caption dibuat lewat References lalu Insert Caption, penomoran bergeser otomatis dan cukup tekan Ctrl+A lalu F9 untuk memperbarui rujukan silang. Kalau nomor diketik manual, periksa Daftar Tabel dan seluruh kalimat yang menyebut nomor tabel setelah titik sisipan.

Nomor pasti baru bisa ditetapkan setelah Anda memutuskan sisipan mana yang dipakai, karena itu di berkas ini nomornya sengaja ditulis 3.x, 3.y, dan 3.z.
