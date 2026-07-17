/**
 * Generator Google Form — Evaluasi Prototype CyberScope (SUS + EUCS).
 *
 * CARA PAKAI
 *   1. Buka https://script.google.com  ->  New project.
 *   2. Hapus isi Code.gs, tempel seluruh file ini.
 *   3. Isi blok CONFIG di bawah (semua yang bertanda <<ISI: ... >>).
 *   4. Pilih fungsi "createForm" di dropdown  ->  Run.
 *   5. Google akan meminta izin akses (Authorize) -> izinkan.
 *   6. Buka Execution log: URL edit + URL isi Form tercetak di sana.
 *
 * Naskah lengkap, pemetaan dimensi, dan panduan skoring: docs/EVALUASI_PROTOTYPE_KUESIONER.md
 *
 * JANGAN mengubah urutan atau polaritas 10 item SUS — rumus skoring bergantung
 * pada selang-seling positif/negatifnya.
 */

// ---------------------------------------------------------------------------
// CONFIG — satu-satunya bagian yang perlu diedit
// ---------------------------------------------------------------------------

const CONFIG = {
  FORM_TITLE: 'Evaluasi Usability & Kepuasan Pengguna — Dashboard CyberScope',

  JUDUL_PENELITIAN: '<<ISI: judul penulisan ilmiah lengkap>>',

  PENELITI: '<<ISI: nama, NPM, program studi, universitas>>',

  PERKENALAN: `<<ISI: perkenalan singkat + apa yang telah Anda kerjakan.
Contoh kerangka: siapa Anda, penelitian ini tentang apa, dashboard ini dibangun
sebagai bagian dari penelitian tersebut, dan mengapa masukan responden dibutuhkan.>>`,

  DESKRIPSI_FITUR: `CyberScope adalah dashboard yang mengklasifikasikan diskursus (percakapan publik) tentang 6 vektor ancaman siber di media sosial Indonesia — X dan YouTube.

Terdapat dua halaman:

1) Monitoring — menampilkan distribusi 6 vektor ancaman dari hasil prediksi model atas 55.300 data, dilengkapi alur klasifikasi, proporsi platform (YouTube vs X), tren waktu, tabel detail per vektor, serta contoh komentar yang muncul saat sebuah vektor diklik.

2) Klasifikasi — tempel teks sendiri atau pilih salah satu contoh siap-klik, lalu sistem menampilkan label vektor, tingkat keyakinan (confidence), bar probabilitas 6 kelas, dan penjelasan token (LIME) yang bersifat opsional.

Catatan penting: sistem ini TIDAK mendeteksi serangan siber. Sistem ini mengklasifikasikan konten yang MEMBICARAKAN ancaman — misalnya laporan korban, kesaksian, edukasi, promosi pelaku, atau diskusi netral.

Catatan teknis: backend berjalan di layanan gratis. Saat pertama kali dibuka, halaman Klasifikasi mungkin perlu sekitar 25–60 detik sampai badge status berubah menjadi "Backend online". Ini normal, bukan kerusakan.

Setelah mencoba fitur-fitur di atas, mohon bantuannya untuk mengisi kuesioner ini. Tidak ada jawaban benar atau salah — yang dinilai adalah sistemnya, bukan Anda.`,

  URL_DASHBOARD: 'https://cyberscope-webapp.vercel.app',

  ESTIMASI: 'sekitar 5 menit',
};

// ---------------------------------------------------------------------------
// Konstanta instrumen — jangan diubah tanpa membaca EVALUASI_PROTOTYPE_KUESIONER.md
// ---------------------------------------------------------------------------

/** Skala 5 titik. Angka disematkan di depan label agar mudah ditarik saat ekspor. */
const SKALA = [
  '1 (Sangat tidak setuju)',
  '2 (Tidak setuju)',
  '3 (Netral)',
  '4 (Setuju)',
  '5 (Sangat setuju)',
];

/** SUS 10 item — adaptasi Indonesia (Sharfina & Santoso, 2016). Urutan mengunci polaritas. */
const ITEM_SUS = [
  'Saya berpikir akan menggunakan sistem ini lagi.',
  'Saya merasa sistem ini rumit untuk digunakan.',
  'Saya merasa sistem ini mudah digunakan.',
  'Saya membutuhkan bantuan dari orang lain atau teknisi dalam menggunakan sistem ini.',
  'Saya merasa fitur-fitur sistem ini berjalan dengan semestinya.',
  'Saya merasa ada banyak hal yang tidak konsisten (tidak serasi) pada sistem ini.',
  'Saya merasa orang lain akan memahami cara menggunakan sistem ini dengan cepat.',
  'Saya merasa sistem ini membingungkan.',
  'Saya merasa tidak ada hambatan dalam menggunakan sistem ini.',
  'Saya perlu membiasakan diri terlebih dahulu sebelum menggunakan sistem ini.',
];

/** EUCS 12 item (Doll & Torkzadeh, 1988) diadaptasi ke konteks CyberScope.
 *  Urutan dimensi: Content 1-4, Accuracy 5-6, Format 7-8, Ease of Use 9-10, Timeliness 11-12.
 *  Nama dimensi sengaja TIDAK ditampilkan ke responden. */
const ITEM_EUCS = [
  'Dashboard CyberScope menyediakan informasi yang saya butuhkan tentang diskursus 6 vektor ancaman siber.',
  'Isi informasi yang disajikan (jumlah data, proporsi tiap vektor, platform asal) sesuai dengan kebutuhan saya.',
  'Keluaran yang ditampilkan (grafik distribusi, tabel detail per vektor, contoh komentar) sesuai dengan yang saya perlukan.',
  'Informasi yang disediakan dashboard sudah memadai.',
  'Hasil klasifikasi yang diberikan dashboard terasa tepat dan masuk akal.',
  'Saya puas dengan tingkat keyakinan (confidence) yang ditampilkan pada hasil klasifikasi.',
  'Keluaran dashboard disajikan dalam format yang bermanfaat (grafik, tabel, bar probabilitas).',
  'Informasi yang ditampilkan jelas dan mudah dibaca.',
  'Dashboard CyberScope ramah pengguna.',
  'Dashboard CyberScope mudah dioperasikan.',
  'Saya memperoleh hasil klasifikasi dalam waktu yang wajar.',
  'Informasi pada halaman Monitoring sesuai dengan data terakhir yang diproses sistem.',
];

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

function createForm() {
  peringatanPlaceholder_();

  const form = FormApp.create(CONFIG.FORM_TITLE);
  form.setDescription(deskripsiPembuka_());
  form.setProgressBar(true);
  form.setShowLinkToRespondAgain(false);
  aturPengumpulanEmail_(form);

  bagianProfil_(form);
  bagianSus_(form);
  bagianEucs_(form);
  bagianSaran_(form);

  Logger.log('Form berhasil dibuat.');
  Logger.log('URL edit  : ' + form.getEditUrl());
  Logger.log('URL isi   : ' + form.getPublishedUrl());
}

// ---------------------------------------------------------------------------
// Bagian-bagian form
// ---------------------------------------------------------------------------

function bagianProfil_(form) {
  form
    .addPageBreakItem()
    .setTitle('Profil Responden')
    .setHelpText('Data ini hanya dipakai untuk mendeskripsikan karakteristik responden pada laporan penelitian.');

  form
    .addTextItem()
    .setTitle('Nama / inisial')
    .setHelpText('Opsional — boleh dikosongkan atau diisi inisial saja.')
    .setRequired(false);

  form
    .addMultipleChoiceItem()
    .setTitle('Peran Anda')
    .setChoiceValues([
      'Mahasiswa Informatika / Ilmu Komputer',
      'Dosen',
      'Praktisi IT / keamanan siber',
    ])
    .showOtherOption(true)
    .setRequired(true);

  form
    .addCheckboxItem()
    .setTitle('Bagian mana yang sudah Anda coba?')
    .setHelpText('Boleh pilih lebih dari satu.')
    .setChoiceValues([
      'Halaman Monitoring',
      'Halaman Klasifikasi',
      'Tombol "Jelaskan dengan LIME"',
    ])
    .setRequired(true);
}

function bagianSus_(form) {
  form
    .addPageBreakItem()
    .setTitle('Bagian A — Penggunaan Sistem')
    .setHelpText(
      'Pada bagian ini, "sistem ini" berarti dashboard CyberScope yang baru saja Anda coba. ' +
        'Jawablah berdasarkan kesan spontan Anda; tidak perlu lama berpikir untuk tiap pernyataan.'
    );

  tambahGridLikert_(
    form,
    'Seberapa setuju Anda dengan pernyataan berikut mengenai sistem ini?',
    '',
    ITEM_SUS
  );
}

function bagianEucs_(form) {
  form
    .addPageBreakItem()
    .setTitle('Bagian B — Kepuasan terhadap Informasi dan Tampilan')
    .setHelpText('Bagian ini menilai kepuasan Anda terhadap isi informasi, ketepatan hasil, tampilan, dan kecepatan dashboard.');

  tambahGridLikert_(
    form,
    'Seberapa setuju Anda dengan pernyataan berikut mengenai informasi dan tampilan dashboard?',
    '',
    ITEM_EUCS
  );
}

function bagianSaran_(form) {
  form
    .addPageBreakItem()
    .setTitle('Saran dan Masukan')
    .setHelpText('Opsional, tetapi sangat membantu. Boleh dilewati.');

  form
    .addParagraphTextItem()
    .setTitle('Bagian mana dari dashboard yang paling membantu Anda? Mengapa?')
    .setRequired(false);

  form
    .addParagraphTextItem()
    .setTitle('Apa yang menurut Anda perlu diperbaiki?')
    .setRequired(false);
}

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------

/** Satu grid Likert: baris = pernyataan, kolom = SKALA. Wajib diisi semua baris. */
function tambahGridLikert_(form, judul, bantuan, pernyataan) {
  const grid = form
    .addGridItem()
    .setTitle(judul)
    .setRows(pernyataan)
    .setColumns(SKALA)
    .setRequired(true);

  if (bantuan) {
    grid.setHelpText(bantuan);
  }
  return grid;
}

function deskripsiPembuka_() {
  return [
    CONFIG.JUDUL_PENELITIAN,
    CONFIG.PENELITI,
    '',
    CONFIG.PERKENALAN,
    '',
    CONFIG.DESKRIPSI_FITUR,
    '',
    'Tautan dashboard: ' + CONFIG.URL_DASHBOARD,
    'Estimasi waktu pengisian: ' + CONFIG.ESTIMASI,
  ].join('\n');
}

/**
 * Pengaturan email berbeda antara akun Gmail biasa dan Google Workspace, dan
 * API-nya pernah berganti (setCollectEmail -> setEmailCollectionType). Kegagalan
 * di sini tidak boleh menggagalkan pembuatan Form: default Forms memang tidak
 * mengumpulkan email.
 */
function aturPengumpulanEmail_(form) {
  try {
    if (FormApp.EmailCollectionType && typeof form.setEmailCollectionType === 'function') {
      form.setEmailCollectionType(FormApp.EmailCollectionType.DO_NOT_COLLECT);
      return;
    }
  } catch (err) {
    Logger.log('Catatan: setEmailCollectionType tidak tersedia (' + err + ').');
  }

  try {
    form.setCollectEmail(false);
  } catch (err) {
    Logger.log('Catatan: pengaturan email dilewati (' + err + '). Form tetap dibuat.');
  }
}

function peringatanPlaceholder_() {
  const belumDiisi = Object.keys(CONFIG).filter(function (k) {
    return String(CONFIG[k]).indexOf('<<ISI:') !== -1;
  });

  if (belumDiisi.length) {
    Logger.log('PERINGATAN: CONFIG berikut masih berisi placeholder -> ' + belumDiisi.join(', '));
    Logger.log('Form tetap dibuat; sunting teksnya langsung di Google Form atau isi CONFIG lalu jalankan ulang.');
  }
}
