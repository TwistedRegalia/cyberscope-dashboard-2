import type { VectorLabel } from "./vectors";

export interface ClassifyExample {
  /** Vektor yang diharapkan (null = contoh off-topic untuk uji "tidak relevan"). */
  label: VectorLabel | null;
  /** Label chip singkat. */
  hint: string;
  text: string;
}

/**
 * Contoh siap-klik untuk menghilangkan hambatan input (§3.2).
 * Teks demo (bukan angka riset) — jelas contoh input, bukan hasil model.
 */
export const CLASSIFY_EXAMPLES: ClassifyExample[] = [
  {
    label: "judi_online_pinjol",
    hint: "Judi & Pinjol",
    text: "situs slot gacor maxwin lagi rame, banyak yang kena rungkad sampai kejerat pinjol",
  },
  {
    label: "penipuan_ewallet_qris",
    hint: "E-Wallet/QRIS",
    text: "saldo dana saya hilang setelah scan qris yang ternyata palsu ditempel di merchant",
  },
  {
    label: "malware_apk",
    hint: "Malware APK",
    text: "hati-hati apk undangan pernikahan dari wa itu mencuri akses m-banking di hp",
  },
  {
    label: "phishing_rekayasa_sosial",
    hint: "Phishing",
    text: "ada yang telepon ngaku dari bank minta kode otp buat verifikasi akun katanya",
  },
  {
    label: "peretasan_pencurian_identitas",
    hint: "Peretasan",
    text: "akun instagram teman saya dibajak lalu dipakai minta pulsa ke semua kontak",
  },
  {
    label: "deepfake_penipuan_ai",
    hint: "Deepfake AI",
    text: "beredar video deepfake tokoh publik yang promosi investasi bodong pakai suara ai",
  },
  {
    label: null,
    hint: "Off-topic",
    text: "resep nasi goreng spesial buat sarapan keluarga di pagi hari yang cerah",
  },
];
