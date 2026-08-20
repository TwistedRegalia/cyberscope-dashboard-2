# Revisi 02 — Poin 9: kenapa BiGRU dan BiLSTM, bukan IndoBERT saja

Berkas ini sengaja berdiri sendiri agar bisa dipakai sebagai bahan di sesi terpisah tanpa membuka repo. Naskah acuan: `Ray Siraj_51423248_R4.docx`.

## Pertanyaan penguji

> Jelaskan mengapa penambahan BiGRU dan BiLSTM lebih baik daripada IndoBERT saja.

## Konteks yang perlu diketahui lebih dulu

Penelitian ini mengklasifikasikan diskursus vektor ancaman siber pada media sosial Indonesia, bukan mendeteksi serangan. Klasifikasinya berjalan sebagai pipeline dua lapis: Model A menyaring relevansi, Model B menetapkan satu dari enam vektor taksonomi E-ICTT. Keduanya memakai arsitektur yang sama dan hanya berbeda pada lapisan keluaran.

Arsitekturnya: IndoBERT-base-p1 sebagai encoder, lalu BiGRU yang mengubah representasi 768 dimensi menjadi 256 dimensi per arah sehingga keluarannya 512, lalu BiLSTM yang mengubahnya menjadi 128 dimensi per arah sehingga keluarannya 256, kemudian masked-mean pooling, dropout, dan lapisan linear. Komponen keempat berupa aturan regex bekerja pada tahap inferensi melalui late fusion berbobot 0,75 neural dan 0,25 aturan.

Angka yang relevan untuk menjawab poin ini:

- Model B mencapai accuracy 0,9881 dan macro-F1 0,9767 pada 922 data uji.
- IndoBERT memuat sekitar 124,5 juta parameter, sedangkan BiGRU, BiLSTM, dan lapisan linear pada Model B hanya 2.234.886 parameter, yaitu sekitar 1,8 persen dari keseluruhan model.
- Model B dilatih atas 7.369 baris, 461 batch per epoch, berhenti pada epoch kelima dengan early stopping.

## Batasan yang menentukan bentuk jawaban

**Ablasi IndoBERT tanpa lapisan rekuren tidak pernah dijalankan.** Sudah diperiksa di seluruh kode sumber, tiga notebook pelatihan, dan seluruh dokumentasi proyek. Satu-satunya ablasi yang ada adalah penyapuan bobot late fusion, dan itu menjawab pertanyaan yang berbeda.

Konsekuensinya, poin ini **tidak boleh dijawab dengan klaim keunggulan berdasarkan hasil pengujian sendiri**. Kalau naskah mengklaim lebih dari yang diuji lalu penguji menuntut angkanya, posisi penulis justru melemah. Jawaban di bawah bertumpu pada tiga hal yang sah: alasan rancangan, bukti dari penelitian lain, dan penempatan kebaruan penelitian ini.

## Bukti literatur, beserta batas kekuatannya masing-masing

### Talaat (2023) — menjawab pertanyaan secara langsung

Talaat, A. S. (2023). Sentiment analysis classification system using hybrid BERT models. *Journal of Big Data*, *10*(1), 110. https://doi.org/10.1186/s40537-023-00781-w

Sudah ada di daftar pustaka naskah. Makalah ini menyusun empat arsitektur yang memadukan BERT dengan BiLSTM dan BiGRU, lalu membandingkannya terhadap **model BERT standalone** dan tujuh metode pembelajaran mesin klasik. Hasilnya, arsitektur usulan yang memuat lapisan BiGRU memberi hasil terbaik.

Inilah satu-satunya rujukan yang benar-benar membandingkan transformer tanpa lapisan rekuren melawan transformer dengan lapisan rekuren.

**Kaveat yang wajib ikut ditulis:** datanya berbahasa Inggris dan model dasarnya DistilBERT serta RoBERTa, bukan IndoBERT pada teks Indonesia. Jadi rujukan ini menunjukkan polanya, bukan membuktikannya pada kasus penelitian ini.

### Mujilahwati dkk. (2026) — membenarkan pemakaian dua lapisan sekaligus

Mujilahwati, S., Zamroni, M. R., & Sholihin, M. (2026). Hybrid deep learning approach for Indonesian hoax detection: A comparative evaluation with IndoBERT. *International Journal of Advances in Applied Sciences*, *15*(1), 322–332. https://doi.org/10.11591/ijaas.v15.i1.pp322-332

Arsitektur intinya sama persis dengan penelitian ini, yaitu IndoBERT dipadukan BiGRU dan BiLSTM, diuji atas 4.312 artikel berita Indonesia dengan 10-fold cross-validation. Tabel 4 makalah itu berjudul *Comparison of the hybrid model with the baseline*, isinya:

| Model berbasis IndoBERT | Accuracy % | Recall % | Precision % | F1-score % | Waktu (detik) |
|---|---|---|---|---|---|
| BiGRU | 95,54 | 96,15 | 95,01 | 95,58 | 231,04 |
| BiLSTM | 95,94 | 96,66 | 95,30 | 95,97 | 280,94 |
| BiGRU-BiLSTM hybrid | 98,73 | 99,01 | 98,04 | 98,98 | 172,72 |

Dua hal yang layak dikutip. Pertama, gabungan kedua lapisan mengungguli masing-masing lapisan secara terpisah dengan selisih sekitar tiga poin persentase, dan makalah itu menyatakan keunggulan tersebut konsisten di seluruh 10 fold. Kedua, gabungan itu justru **lebih cepat dilatih**, yaitu 172,72 detik dibandingkan 231,04 dan 280,94 detik, sehingga penambahan lapisan tidak berarti penambahan biaya.

**Dua kaveat yang wajib diketahui.** Baseline pada tabel itu adalah IndoBERT+BiGRU dan IndoBERT+BiLSTM, **bukan IndoBERT saja**, sehingga makalah ini tidak menjawab pertanyaan penguji secara langsung. Selain itu, dua baris baseline tersebut diberi penanda rujukan ke sumber lain, sehingga angkanya kemungkinan dikutip dari penelitian terdahulu dan bukan dijalankan ulang oleh penulisnya. Jangan menyebut makalah ini sebagai bukti bahwa hibrida mengalahkan IndoBERT saja.

### Xiong dkk. (2024) — pola serupa pada tugas lain

Xiong, Y., Chen, G., & Cao, J. (2024). Research on public service request text classification based on BERT-BiLSTM-CNN feature fusion. *Applied Sciences*, *14*(14), 6282. https://doi.org/10.3390/app14146282

Fusi fitur BERT dengan BiLSTM dan CNN mengungguli arsitektur hibrida pembanding pada klasifikasi teks pengaduan layanan publik. Nilainya sebagai penguat pola, bukan bukti langsung.

## Teks sisipan untuk naskah

**Lokasi:** subbab 3.8.1 Arsitektur Dasar Triple-Hybrid, setelah kalimat "Lapisan rekuren karenanya berperan sebagai kepala pemroses yang ringan di atas encoder, bukan komponen yang memikul beban representasi utama."

**Tindakan:** sisipkan empat paragraf berikut.

**Teks:**

Penambahan lapisan rekuren di atas IndoBERT dilandasi perbedaan cara kedua komponen memperlakukan urutan. Mekanisme self-attention memperhitungkan seluruh token secara serentak dan memperoleh informasi posisi melalui positional encoding, sedangkan peringkasan kalimat pada penggunaan umum diambil dari token khusus di awal barisan atau dari perataan seluruh token. Lapisan rekuren dua arah membaca barisan token secara berurutan dari dua sisi, sehingga progresi antarbagian kalimat dimodelkan secara eksplisit. Karakteristik tersebut sejalan dengan bentuk diskursus ancaman siber yang umumnya tersusun sebagai rangkaian peristiwa, misalnya menerima tautan, menekan tautan, lalu kehilangan saldo, di mana urutan kejadian menentukan makna sekaligus peran pembicara.

Kedua lapisan rekuren yang dipakai memiliki pembagian peran. BiGRU dengan struktur gerbang yang lebih sederhana meringkas representasi 768 dimensi menjadi 512 dimensi, kemudian BiLSTM yang memiliki gerbang tambahan beserta memori sel menyaringnya menjadi 256 dimensi. Penyusunan bertingkat tersebut menghasilkan penyempitan representasi secara bertahap dengan biaya yang kecil, yaitu 2.234.886 parameter atau sekitar 1,8 persen dari keseluruhan model, sehingga penambahannya tidak memperbesar risiko overfitting secara berarti dan tidak menambah waktu pelatihan secara mencolok.

Pilihan tersebut sejalan dengan temuan penelitian terdahulu. Talaat (2023) membandingkan beberapa arsitektur yang memadukan model bahasa terlatih dengan BiLSTM dan BiGRU terhadap model bahasa terlatih yang berdiri sendiri, dan memperoleh hasil terbaik pada arsitektur yang memuat lapisan BiGRU, meskipun pengujian tersebut dilakukan pada teks berbahasa Inggris dengan model dasar yang berbeda. Pada konteks bahasa Indonesia, Mujilahwati dkk. (2026) menguji IndoBERT yang dipadukan BiGRU, IndoBERT yang dipadukan BiLSTM, dan gabungan keduanya atas 4.312 artikel dengan 10-fold cross-validation, dan memperoleh accuracy 98,73 persen beserta F1-score 98,98 persen pada gabungan keduanya, dibandingkan 95,54 persen dan 95,94 persen pada masing-masing lapisan secara terpisah. Menariknya, gabungan tersebut justru memerlukan waktu pelatihan yang lebih singkat, yaitu 172,72 detik dibandingkan 231,04 detik dan 280,94 detik, sehingga penyusunan kedua lapisan sekaligus tidak berarti penambahan biaya komputasi. Pola serupa dilaporkan Xiong dkk. (2024) pada klasifikasi teks pengaduan layanan publik.

Perlu dinyatakan secara terbuka bahwa penelitian ini tidak menjalankan ablasi terhadap arsitektur, yaitu tidak melatih varian IndoBERT tanpa lapisan rekuren sebagai pembanding langsung. Susunan triple-hybrid pada penelitian ini karenanya merupakan adopsi rancangan yang telah tervalidasi pada penelitian terdahulu untuk teks berbahasa Indonesia, bukan klaim keunggulan berdasarkan pengujian internal. Hal ini konsisten dengan penempatan kebaruan penelitian ini yang tidak terletak pada arsitektur neural, melainkan pada penerapan taksonomi E-ICTT enam vektor melalui pipeline dua lapis, pembingkaian diskursus sebagai landasan pelabelan, pembangunan korpus melalui weak supervision, serta perwujudan model ke dalam prototipe yang dilengkapi interpretabilitas. Ablasi arsitektur dicatat sebagai pengembangan lanjutan.

## Jawaban lisan untuk sidang

Dua sampai tiga kalimat, kalau ditanya langsung:

> Arsitektur triple-hybrid ini saya adopsi dari penelitian rujukan, bukan saya klaim sebagai kebaruan. Mujilahwati dkk. sudah memvalidasi susunan IndoBERT dengan BiGRU dan BiLSTM untuk teks berbahasa Indonesia dan menunjukkan gabungan kedua lapisan mengungguli masing-masing lapisan secara terpisah, sementara Talaat menunjukkan pola yang sama terhadap model bahasa terlatih yang berdiri sendiri. Saya sendiri tidak menjalankan ablasi arsitektur, jadi saya tidak mengklaim keunggulan itu sebagai temuan penelitian ini, dan saya cantumkan sebagai keterbatasan sekaligus saran penelitian lanjutan.

Kunci sikapnya: jangan mempertahankan klaim yang tidak diuji. Kebaruan penelitian ini ada di taksonomi, pembingkaian diskursus, weak supervision, korpus OSINT, dan interpretabilitas, dan itu sudah dinyatakan pada subbab Kontribusi dan Kebaruan Penelitian.

## Tambahan untuk Saran (BAB 4)

**Lokasi:** paragraf saran mengenai sisi model.

**Teks:**

Ablasi arsitektur perlu dijalankan dengan melatih varian IndoBERT tanpa lapisan rekuren, varian dengan BiGRU saja, dan varian dengan BiLSTM saja pada pemisahan data yang sama, sehingga kontribusi tiap lapisan terhadap performa dapat diukur secara langsung dan tidak hanya disandarkan pada temuan penelitian terdahulu.

## Bila kelak ingin dibuktikan sendiri

Ablasi ini murah. Model B hanya dilatih atas 7.369 baris dengan 461 batch per epoch dan berhenti pada epoch kelima, sehingga satu proses pelatihan varian tanpa lapisan rekuren diperkirakan 15 sampai 20 menit pada Kaggle T4. Yang perlu diubah hanya kelas modelnya, yaitu menghapus BiGRU dan BiLSTM lalu memasang lapisan linear langsung di atas hasil pooling, dengan split, seed, dan hyperparameter dipertahankan persis.

Satu peringatan sebelum menjalankannya. Model B sudah mencapai macro-F1 0,9767 pada tugas yang relatif terpisah, sehingga ada kemungkinan nyata varian IndoBERT saja mencapai angka setara atau lebih baik. Bila itu yang terjadi, hasilnya tetap wajib dilaporkan dan justifikasi arsitektur harus disesuaikan. Ablasi adalah pertanyaan yang jawabannya belum diketahui, bukan konfirmasi atas keputusan yang sudah diambil.

## Temuan sampingan, di luar poin 9

Paragraf penutup subbab Kontribusi dan Kebaruan Penelitian memuat rujukan silang yang belum selesai, tertulis "Tabel 2._" pada kalimat terakhir. Perbaiki nomornya saat menyunting.
