/**
 * SATU lapisan akses data. Komponen TIDAK pernah fetch langsung — semua lewat sini.
 *
 * - Monitoring: baca file statis `public/data/monitoring.json` (di-serve frontend).
 *   Selama backend belum ada, file itu = fixture dev ber-flag `is_sample`.
 * - Klasifikasi/LIME: fetch ke NEXT_PUBLIC_API_BASE_URL, atau MOCK bila backend
 *   belum ada. Menukar ke nyata = set NEXT_PUBLIC_API_BASE_URL (+ USE_MOCK=false),
 *   TANPA ubah komponen.
 */
import type { ClassifyResponse, MonitoringData } from "./types";
import { mockClassify } from "./mock/classify";

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
