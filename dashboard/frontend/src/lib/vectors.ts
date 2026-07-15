/**
 * VECTOR_META — sumber kebenaran tunggal untuk 6 vektor E-ICTT.
 * Dipakai SEMUA chart, badge, dan drill-down agar warna + label konsisten.
 *
 * - `label`   : kanonik, untuk logika/kunci data (JANGAN diubah).
 * - `display` : untuk tampilan UI penuh (bukan indeks kelas).
 * - `short`   : label ringkas untuk sumbu chart yang sempit.
 * - `color`   : palet kategorikal final (lihat rencana §6).
 *
 * Aturan integritas: 6 label ini FINAL. Tidak ada label ke-7
 * (`informasi_edukasi_siber` sudah ditolak). Speaker Role R1–R5 BUKAN v1.
 *
 * Palet: minimal disesuaikan dari CLAUDE.md §4 agar 6 kategori terpisah jelas —
 * malware biru-sapphire → teal (hindari dua biru mirip + bebaskan #1e40af utk CTA),
 * deepfake abu → magenta (identitas kategori). Semua ≥3:1 kontras di atas putih.
 * Warna TIDAK pernah jadi satu-satunya pembawa makna: selalu sertakan display + nilai.
 */

export type VectorLabel =
  | "phishing_rekayasa_sosial"
  | "penipuan_ewallet_qris"
  | "malware_apk"
  | "judi_online_pinjol"
  | "peretasan_pencurian_identitas"
  | "deepfake_penipuan_ai";

export interface VectorMeta {
  label: VectorLabel;
  display: string;
  short: string;
  color: string;
}

export const VECTOR_META: Record<VectorLabel, VectorMeta> = {
  phishing_rekayasa_sosial: {
    label: "phishing_rekayasa_sosial",
    display: "Phishing & Rekayasa Sosial",
    short: "Phishing",
    color: "#2563eb", // electric-blue (Dub)
  },
  penipuan_ewallet_qris: {
    label: "penipuan_ewallet_qris",
    display: "Penipuan E-Wallet/QRIS",
    short: "E-Wallet/QRIS",
    color: "#15803d", // green-700 (vivid-green digelapkan utk kontras)
  },
  malware_apk: {
    label: "malware_apk",
    display: "Malware APK",
    short: "Malware APK",
    color: "#0d9488", // teal-600 (ganti #1e40af)
  },
  judi_online_pinjol: {
    label: "judi_online_pinjol",
    display: "Judi Online & Pinjol",
    short: "Judi & Pinjol",
    color: "#ea580c", // tangerine (Dub)
  },
  peretasan_pencurian_identitas: {
    label: "peretasan_pencurian_identitas",
    display: "Peretasan & Pencurian Identitas",
    short: "Peretasan",
    color: "#7c3aed", // lavender (Dub)
  },
  deepfake_penipuan_ai: {
    label: "deepfake_penipuan_ai",
    display: "Deepfake & Penipuan AI",
    short: "Deepfake AI",
    color: "#db2777", // pink-600 (ganti fog)
  },
};

/** Urutan kanonik (taksonomi E-ICTT). Chart boleh mengurut ulang by value. */
export const VECTOR_LABELS: VectorLabel[] = [
  "phishing_rekayasa_sosial",
  "penipuan_ewallet_qris",
  "malware_apk",
  "judi_online_pinjol",
  "peretasan_pencurian_identitas",
  "deepfake_penipuan_ai",
];

export function isVectorLabel(value: string): value is VectorLabel {
  return value in VECTOR_META;
}

/** Ambil meta dengan aman; fallback netral bila label tak dikenal. */
export function getVectorMeta(label: string): VectorMeta {
  if (isVectorLabel(label)) return VECTOR_META[label];
  return {
    label: label as VectorLabel,
    display: label,
    short: label,
    color: "#737373",
  };
}
