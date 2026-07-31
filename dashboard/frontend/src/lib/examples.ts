import type { VectorLabel } from "./vectors";

export interface ClassifyExamplePool {
  /** Vektor yang diharapkan (null = contoh off-topic untuk uji "tidak relevan"). */
  label: VectorLabel | null;
  /** Label chip singkat. */
  hint: string;
  /** Kumpulan contoh; ditampilkan bergantian berurutan tiap klik. */
  texts: string[];
}

/**
 * Contoh siap-klik untuk menghilangkan hambatan input (§3.2).
 * Teks demo (bukan angka riset) — jelas contoh input, bukan hasil model.
 * Tiap pool berisi beberapa teks yang ditampilkan bergantian secara berurutan,
 * agar penguji dapat mengamati konsistensi model terhadap masukan berbeda pada
 * vektor yang sama dan urutannya tetap dapat direproduksi untuk tabel uji.
 */
export const CLASSIFY_EXAMPLES: ClassifyExamplePool[] = [
  {
    label: "judi_online_pinjol",
    hint: "Judi & Pinjol",
    texts: [
      "situs slot gacor maxwin lagi rame, banyak yang kena rungkad sampai kejerat pinjol",
      "tetangga saya galbay pinjol ilegal, tiap hari ditelepon debt collector sampai kantornya ikut dihubungi",
      "awalnya cuma iseng main judol receh, sekarang gaji sebulan habis buat topup terus",
      "banyak akun promosi situs judi nyampah di kolom komentar video orang, kok dibiarin aja",
      "depo terus tapi scatter gak keluar, wd lancar cuma di awal doang, judol emang bikin rungkad",
    ],
  },
  {
    label: "penipuan_ewallet_qris",
    hint: "E-Wallet/QRIS",
    texts: [
      "saldo dana saya hilang setelah scan qris yang ternyata palsu ditempel di merchant",
      "ada yang tempel stiker qris palsu di kotak amal masjid, uangnya masuk ke rekening pribadi",
      "waspada penipuan qris palsu, jangan scan barcode qris sembarangan di tempat umum",
      "modus qris palsu marak lagi, saldo dana korban langsung terkuras setelah scan barcode",
      "penipuan e-wallet makin marak, saldo ovo dan gopay korban raib setelah scan qris palsu",
    ],
  },
  {
    label: "malware_apk",
    hint: "Malware APK",
    texts: [
      "hati-hati file apk undangan pernikahan yang dikirim lewat wa, itu malware penguras m-banking",
      "jangan install apk cek resi yang dikirim lewat whatsapp, itu bisa baca sms otp kamu",
      "hp bapak saya kena install apk kurir paket, malware nya langsung menguasai m-banking",
      "beredar kiriman apk undangan nikah di grup keluarga, itu apk berbahaya jangan dibuka",
      "jangan download apk di luar playstore, banyak apk virus yang minta izin baca sms",
    ],
  },
  {
    label: "phishing_rekayasa_sosial",
    hint: "Phishing",
    texts: [
      "ada yang telepon ngaku dari bank minta kode otp buat verifikasi akun katanya",
      "dapat sms berisi link palsu atas nama bank, untung sadar itu phising sebelum isi data",
      "soceng lagi, ada yang telepon ngaku petugas bank minta kode otp dan data kartu",
      "jangan pernah kasih kode otp ke siapa pun walaupun ngaku dari customer service resmi",
      "kasus soceng makin marak, penipu mengatasnamakan cs bank buat minta kode otp nasabah",
    ],
  },
  {
    label: "peretasan_pencurian_identitas",
    hint: "Peretasan",
    texts: [
      "ada yang jual jasa hack akun instagram di twitter, ini pencurian identitas terang terangan",
      "kasus kebocoran data di indonesia makin parah, jutaan data dukcapil dan npwp bocor",
      "kebocoran data dukcapil bikin nik saya dipakai orang, ini pencurian identitas namanya",
      "email lama kena kebocoran data, sekarang passwordnya dipakai coba masuk ke akun saya yang lain",
      "kebocoran data pribadi ratusan juta warga bikin resah, pencurian identitas makin gampang",
    ],
  },
  {
    label: "deepfake_penipuan_ai",
    hint: "Deepfake AI",
    texts: [
      "beredar video deepfake tokoh publik yang promosi investasi bodong pakai suara ai",
      "video presiden promosi investasi itu deepfake, hasil ai voice yang mulutnya gak sinkron",
      "marak deepfake voice cloning, suara mirip anak dipakai nelpon ortu minta uang tebusan",
      "iklan investasi crypto pakai wajah menteri hasil deepfake, jelas ai generated",
      "sekarang video call bisa dipalsukan pakai deepfake real time, jangan langsung percaya",
    ],
  },
  {
    label: null,
    hint: "Off-topic",
    texts: [
      "resep nasi goreng spesial buat sarapan keluarga di pagi hari yang cerah",
      "besok kayaknya hujan deras, jangan lupa bawa payung kalau mau keluar rumah",
      "pertandingan tadi malam seru banget, gol di menit akhir bikin penonton berdiri semua",
      "jalanan macet parah dari tadi pagi, sepertinya ada perbaikan jalan di depan pasar",
      "musim panen tahun ini bagus, harga cabai di pasar juga mulai turun perlahan",
    ],
  },
];
