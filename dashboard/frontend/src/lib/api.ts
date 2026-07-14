/**
 * SATU lapisan akses data. Komponen TIDAK pernah fetch langsung — semua lewat sini.
 *
 * - Monitoring: baca file statis `public/data/monitoring.json` (di-serve frontend).
 *   Selama backend belum ada, file itu = fixture dev ber-flag `is_sample`.
 * - Klasifikasi/LIME: fetch ke NEXT_PUBLIC_API_BASE_URL, atau MOCK bila backend
 *   belum ada. Menukar ke nyata = set NEXT_PUBLIC_API_BASE_URL (+ USE_MOCK=false),
 *   TANPA ubah komponen.
 */
import type {
  ClassifyResponse,
  ExplainResponse,
  HealthResponse,
  MonitoringData,
} from "./types";
import type { VectorLabel } from "./vectors";
import { mockClassify } from "./mock/classify";
import { mockExplain } from "./mock/explain";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

/** Pakai mock bila diminta eksplisit ATAU bila base URL backend belum diset. */
export const USE_MOCK =
  process.env.NEXT_PUBLIC_USE_MOCK === "true" || API_BASE === "";

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Baca data monitoring dari file statis.
 * Return `null` bila file tak ada / gagal parse → halaman tampil empty state.
 */
export async function getMonitoring(): Promise<MonitoringData | null> {
  try {
    const res = await fetch("/data/monitoring.json", { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as MonitoringData;
  } catch {
    return null;
  }
}

/**
 * Klasifikasi on-demand (pipeline Model A → Model B → fusion).
 * Mock: heuristik kata kunci. Nyata: POST {API_BASE}/classify.
 * Throw bila backend gagal → UI tampilkan error state.
 */
export async function classify(text: string): Promise<ClassifyResponse> {
  if (USE_MOCK) {
    await delay(450); // simulasi latensi supaya loading state terlihat
    return mockClassify(text);
  }
  const res = await fetch(`${API_BASE}/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`Gagal klasifikasi (HTTP ${res.status})`);
  return (await res.json()) as ClassifyResponse;
}

/**
 * Penjelasan XAI (LIME) — LAMBAT (backend nyata ±30–60 dtk). num_samples clamp
 * 100..150. Mock cepat (~1,5 dtk) supaya demo bisa dipakai, tapi UI tetap
 * menandai proses lambat. Async & non-blocking (dipanggil dari LimePanel).
 */
export async function explain(
  text: string,
  label: VectorLabel,
  numSamples = 120,
): Promise<ExplainResponse> {
  const clamped = Math.min(150, Math.max(100, numSamples));
  if (USE_MOCK) {
    await delay(1500);
    return mockExplain(text, label, clamped);
  }
  const res = await fetch(`${API_BASE}/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, num_samples: clamped }),
  });
  if (!res.ok) throw new Error(`Gagal LIME (HTTP ${res.status})`);
  return (await res.json()) as ExplainResponse;
}

/**
 * Status backend (untuk badge / peringatan cold-start). Return null dalam mode
 * mock atau bila gagal dihubungi.
 */
export async function health(): Promise<HealthResponse | null> {
  if (USE_MOCK || API_BASE === "") return null;
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as HealthResponse;
  } catch {
    return null;
  }
}
