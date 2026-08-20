# Revisi 03 — Sel D2 dan pertanyaan penguji soal bobot 0,50

Berkas ini berdiri sendiri agar bisa dipakai di sesi terpisah tanpa membuka repo. Naskah acuan: `Ray Siraj_51423248_R4.docx`. Berkaitan dengan poin 6 dan poin 8 pada `REVISI_01.md`.

## Pertanyaan penguji

Penguji menunjuk Lampiran halaman L-30, bagian *late fusion - uji kestabilan bobot 0,50* yang memuat Sel D2, lalu mempertanyakan mengapa sistem memakai bobot 0,75:0,25 padahal pada w_neural 0,55 sampai 0,45 macro-F1 Layer 2 lebih tinggi.

Dua kekhawatiran yang menyertainya:

1. Apakah Sel D2 sebenarnya dipakai?
2. Apakah memasukkannya ke lampiran adalah kesalahan?

**Jawaban: Sel D2 dipakai, dan memasukkannya ke lampiran bukan kesalahan.** Uraiannya di bawah.

## Apa itu Sel D1 dan Sel D2

Keduanya ada di notebook `model-training-late-fusion-l2.ipynb` dan keduanya masuk lampiran.

**Sel D1** menjawab pertanyaan "sampel mana yang berubah prediksinya antara 0,75 dan 0,50". Keluarannya: tepat 4 sampel berubah, keempatnya berlabel asli judi yang sebelumnya diprediksi phishing oleh jalur neural, dan keempatnya berbalik menjadi benar. Tidak ada satu pun yang berbalik menjadi salah. Ringkasan di lampiran berbunyi "4 berbalik ke BENAR, 0 berbalik ke SALAH (net +4)".

**Sel D2** menjawab pertanyaan yang tertulis pada judul selnya sendiri: *apakah lonjakan 0.9814 stabil di sekitar 0.50, atau artefak titik?* Keluarannya:

| w_neural | macro-F1 | F1 phishing |
|---|---|---|
| 0,55 | 0,9780 | 0,9184 |
| 0,53 | 0,9780 | 0,9184 |
| 0,52 | 0,9780 | 0,9184 |
| 0,51 | 0,9797 | 0,9278 |
| 0,50 | 0,9814 | 0,9375 |
| 0,49 | 0,9814 | 0,9375 |
| 0,48 | 0,9814 | 0,9375 |
| 0,47 | 0,9814 | 0,9375 |
| 0,45 | 0,9814 | 0,9375 |

Sebagai pembanding, bobot 0,75:0,25 menghasilkan macro-F1 0,9747 dan jalur neural murni menghasilkan 0,9767.

Jawaban Sel D2: **stabil, bukan artefak titik.** Hasil ini dipakai sebagai dasar pernyataan "stabil di rentang 0,45 sampai 0,51, bukan artefak tie-breaking" yang tercatat pada dokumentasi ablation penelitian ini. Jadi sel tersebut bukan sisa percobaan yang tertinggal.

## Kenapa lampiran itu justru menguatkan, bukan melemahkan

Sel D2 dijalankan untuk menguji temuan yang **merugikan posisi penulis sendiri**. Setelah terlihat bahwa 0,50 unggul, langkah berikutnya bukan mengabaikannya, melainkan memeriksa apakah keunggulan itu nyata atau kebetulan. Ternyata nyata, dan hasilnya tetap dilaporkan apa adanya.

Itu justru praktik yang benar. Yang akan menjadi masalah adalah kebalikannya, yaitu menemukan keunggulan tersebut lalu tidak mencantumkannya.

**Celah yang sebenarnya ada di badan naskah, bukan di lampiran.** Subbab 3.10.3 hanya memuat mekanisme empat sampel dari Sel D1, lalu menyimpulkan "betapa rapuhnya keunggulan yang terlihat". Hasil Sel D2 tidak disebut sama sekali. Akibatnya pembaca melihat badan naskah menyebut keunggulan itu rapuh, sementara lampiran memperlihatkan dataran yang stabil sepanjang sembilan titik bobot, tanpa satu kalimat pun yang menjembatani keduanya. Penguji membaca lampiran, melihat ketidaksesuaian itu, lalu bertanya. Pertanyaannya sah.

## Kenapa jawaban saat presentasi terasa tidak menjawab

Tabel 3.15 pada subbab 3.10.3 berjudul *Sweep Bobot Late Fusion pada Layer 1*. Tabel itu memuat sweep **Layer 1**, sedangkan yang ditanyakan penguji adalah macro-F1 **Layer 2**.

Naskah tidak memiliki tabel sweep Layer 2 sama sekali. Perilaku Layer 2 hanya diuraikan dalam bentuk narasi. Karena itu, ketika ditanya soal angka Layer 2, satu-satunya tabel bobot yang tersedia untuk ditunjuk adalah tabel Layer 1.

Isi jawaban itu sendiri sebenarnya sahih, karena pada Layer 1 bobot 0,50 memang runtuh dengan precision kelas relevan hanya 0,5047 dan macro-F1 0,7810. Persoalannya, jawaban itu menjelaskan lapis yang berbeda dari yang ditanyakan. Sisipan 8a pada `REVISI_01.md` menambahkan tabel sweep Layer 2 ke naskah, sehingga celah ini tertutup.

## Inti pembelaan: dataran itu dihasilkan empat sampel yang sama

Ini argumen terkuat, dan pembaca dapat memeriksanya sendiri dengan aritmetika sederhana.

Keempat sampel yang berpindah berlabel asli judi. Karena itu perpindahannya tidak menyentuh true positive maupun false negative kelas phishing, dan hanya mengurangi false positive phishing. Dengan true positive 45 dan false negative 4 yang tetap, nilai F1 phishing dapat dibaca terbalik menjadi jumlah false positive:

| Bobot | F1 phishing | False positive phishing | Sampel terkoreksi |
|---|---|---|---|
| 0,75 | 0,9000 | 6 | 0 dari 4 |
| 0,55 sampai 0,52 | 0,9184 | 4 | 2 dari 4 |
| 0,51 | 0,9278 | 3 | 3 dari 4 |
| 0,50 ke bawah | 0,9375 | 2 | 4 dari 4 |

Perhitungannya: F1 sama dengan 2 kali TP dibagi jumlah 2 kali TP ditambah FP ditambah FN. Pada bobot 0,50, nilainya 90 dibagi 96 sama dengan 0,9375, yaitu persis angka yang tercetak di lampiran.

Artinya, seluruh dataran 0,45 sampai 0,55 bukan perbaikan yang meluas, melainkan **tangga dari empat sampel yang sama** yang terkoreksi satu per satu seiring bobot aturan diperbesar. Pada 0,52 sampai 0,55 dua di antaranya terkoreksi, pada 0,51 tiga, dan pada 0,50 ke bawah keempatnya.

Dari sini muncul rumusan yang menjawab pertanyaan penguji secara langsung: **kestabilan terhadap bobot bukanlah kestabilan statistik.** Sel D2 membuktikan angka tersebut tidak goyah bila bobot digeser. Sel D2 tidak membuktikan perbaikan tersebut akan bertahan pada data uji yang berbeda, sebab dasarnya tetap empat sampel dari 922 atau 0,43 persen, seluruhnya dari satu pasangan kategori yang sama, dan tanpa uji signifikansi statistik.

## Tiga alasan mempertahankan 0,75:0,25

1. **Dasar keunggulannya sempit.** Empat sampel dari 922, semuanya dari perbatasan phishing dan judi, tanpa uji signifikansi. Kestabilan terhadap bobot tidak mengubah kenyataan tersebut.
2. **Bobot yang sama meruntuhkan Layer 1.** Pada 0,50:0,50, precision kelas relevan Layer 1 turun menjadi 0,5047 dan macro-F1 menjadi 0,7810. Karena rancangan sistem memakai satu bobot untuk kedua lapis, bobot tersebut tidak dapat diadopsi.
3. **Memilihnya berarti menyetel dengan data uji.** Keunggulan 0,50 teridentifikasi pada data uji. Prosedur yang sah adalah menjalankan sweep pada data validasi, mengunci bobot terpilih, lalu mengukurnya sekali pada data uji. Prosedur itu tidak ditempuh, karena sweep dijalankan setelah pelatihan selesai sebagai sarana ablation study, bukan sebagai tahap penyetelan.

## Jawaban lisan siap ucap

> Sel D2 memang saya jalankan dengan sengaja, justru untuk menguji apakah keunggulan bobot 0,50 itu nyata atau kebetulan, dan hasilnya memang stabil sehingga saya laporkan apa adanya di lampiran. Yang perlu saya jelaskan adalah bahwa kestabilan terhadap bobot itu bukan kestabilan statistik. Seluruh dataran 0,45 sampai 0,55 dihasilkan oleh empat sampel yang sama dari 922 data uji, semuanya dari perbatasan phishing dan judi, dan pergeserannya bisa dilacak satu per satu dari nilai F1 phishing di lampiran itu. Selain itu, bobot yang sama justru meruntuhkan Layer 1 sampai precision kelas relevan tinggal 0,5047, padahal rancangan saya memakai satu bobot untuk kedua lapis. Dan yang paling menentukan, keunggulan itu saya temukan pada data uji, sehingga memilihnya berarti menyetel bobot dengan data yang seharusnya belum pernah dilihat model. Karena itu saya pertahankan bobot 0,75:0,25 yang ditetapkan sejak awal sebagai keputusan rancangan, dan penyetelan bobot melalui data validasi saya cantumkan sebagai saran penelitian lanjutan.

## Sisipan untuk naskah

**Lokasi:** subbab 3.10.3, setelah kalimat "Dengan kata lain, keunggulan nilai 0,9814 bertumpu pada empat sampel saja."

**Tindakan:** sisipkan dua paragraf berikut, sebelum paragraf yang dimulai "Meskipun demikian, bobot 0,50:0,50 tidak dipilih."

**Teks:**

Untuk memastikan bahwa keunggulan tersebut bukan sekadar artefak pada satu titik bobot, dilakukan penyapuan tambahan pada rentang sempit di sekitar 0,50. Hasilnya memperlihatkan nilai macro-F1 sebesar 0,9780 pada bobot 0,55 sampai 0,52, sebesar 0,9797 pada bobot 0,51, dan sebesar 0,9814 pada bobot 0,50 hingga 0,45. Keunggulan tersebut dengan demikian bersifat stabil terhadap perubahan bobot dan bukan artefak pemilihan titik, dan temuan ini dilaporkan apa adanya meskipun tidak mendukung bobot yang dipakai pada sistem akhir.

Kestabilan terhadap bobot tersebut perlu dibedakan dari kestabilan secara statistik. Penelusuran terhadap nilai F1-score kategori phishing memperlihatkan bahwa keseluruhan rentang tersebut dihasilkan oleh empat sampel yang sama, yaitu jumlah false positive kategori phishing menurun dari enam pada bobot 0,75 menjadi empat pada rentang 0,55 sampai 0,52, menjadi tiga pada bobot 0,51, dan menjadi dua pada bobot 0,50 ke bawah. Kenaikan nilai macro-F1 pada rentang tersebut karenanya bukan perbaikan kemampuan pemisahan antarkategori secara menyeluruh, melainkan koreksi bertahap atas empat sampel perbatasan yang sama, yaitu 0,43 persen dari 922 data uji, tanpa disertai uji signifikansi statistik.

**Sumber angka:** keluaran Sel D2 pada lampiran, dan confusion matrix Layer 2 pada Gambar 3.14.

## Bila ingin memilih 0,50 secara sah

Prosedurnya jelas dan tidak mahal, karena tidak perlu melatih ulang model. Muat checkpoint Model B, jalankan inferensi atas **data validasi** Layer 2 yang berjumlah 921 baris, lakukan penyapuan bobot pada data tersebut, kunci bobot terbaiknya, lalu ukur sekali pada data uji. Bila bobot yang menang pada data validasi ternyata juga 0,50, pemilihannya menjadi sah dan bukan lagi optimasi terhadap data uji.

Perlu diingat, prosedur ini juga bisa berakhir sebaliknya, yaitu bobot yang menang pada data validasi ternyata berbeda. Itu pun hasil yang berguna, karena memperkuat kesimpulan bahwa keunggulan 0,50 terikat pada data uji tertentu.
