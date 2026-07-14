/**
 * MOCK klasifikasi — stand-in selama backend FastAPI belum ada.
 * Heuristik kata kunci per vektor (BUKAN model nyata) → menghasilkan bentuk
 * ClassifyResponse yang identik kontrak §6. Ditukar ke /classify nyata via
 * NEXT_PUBLIC_USE_MOCK (lihat lib/api.ts). Jangan dikira output model.
 */
import { VECTOR_LABELS, VECTOR_META, type VectorLabel } from "@/lib/vectors";
import type { ClassifyResponse } from "@/lib/types";

const KEYWORDS: Record<VectorLabel, string[]> = {
  judi_online_pinjol: [
    "slot", "gacor", "maxwin", "judol", "judi", "pinjol", "togel",
    "deposit", "rungkad", "debt collector", "dc ",
  ],
  penipuan_ewallet_qris: [
    "qris", "dana", "ovo", "gopay", "saldo", "cashback", "e-wallet",
    "ewallet", "scan", "top up", "topup", "refund",
  ],
  malware_apk: [
    "apk", "undangan", "resi", "paket", "kurir", "tilang", "install",
    "aplikasi",
  ],
  phishing_rekayasa_sosial: [
    "otp", "kode", "link", "m-banking", "mbanking", "verifikasi",
    "rekening", "bank", "klik", "sms", "admin",
  ],
  peretasan_pencurian_identitas: [
    "hack", "bobol", "dibajak", "diretas", "akun", "data bocor", "ktp",
    "sim swap", "identitas", "password", "kebocoran",
  ],
  deepfake_penipuan_ai: [
    "deepfake", "voice cloning", "kloning", "wajah", "video palsu",
    " ai ", "suara keluarga",
  ],
};

function emptyProbs(): Record<VectorLabel, number> {
  return Object.fromEntries(
    VECTOR_LABELS.map((l) => [l, 0]),
  ) as Record<VectorLabel, number>;
}

export function mockClassify(text: string): ClassifyResponse {
  const t = ` ${text.toLowerCase()} `;
  const hits = emptyProbs();
  let total = 0;
  for (const label of VECTOR_LABELS) {
    const n = KEYWORDS[label].filter((k) => t.includes(k)).length;
    hits[label] = n;
    total += n;
  }

  const latency_ms = 400 + Math.floor(Math.random() * 500);

  // Model A (mock): tanpa sinyal apa pun → tidak relevan, berhenti.
  if (total === 0) {
    return {
      relevant: false,
      label: null,
      label_display: null,
      confidence: 0,
      probabilities: emptyProbs(),
      latency_ms,
    };
  }

  // Distribusi lembut, vektor dengan hit terbanyak dominan.
  const eps = 0.02;
  const denom = total + eps * VECTOR_LABELS.length;
  const probabilities = emptyProbs();
  let top: VectorLabel = VECTOR_LABELS[0];
  for (const label of VECTOR_LABELS) {
    probabilities[label] = (hits[label] + eps) / denom;
    if (probabilities[label] > probabilities[top]) top = label;
  }

  return {
    relevant: true,
    label: top,
    label_display: VECTOR_META[top].display,
    confidence: probabilities[top],
    probabilities,
    latency_ms,
  };
}
