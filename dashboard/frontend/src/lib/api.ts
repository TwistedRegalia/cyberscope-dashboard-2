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
// Mock di-impor DINAMIS di dalam cabang USE_MOCK (lihat classify/explain) supaya
// kode heuristik TIDAK ikut ter-bundle saat produksi memakai backend nyata.

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

/** Pakai mock bila diminta eksplisit ATAU bila base URL backend belum diset. */
export const USE_MOCK =
  process.env.NEXT_PUBLIC_USE_MOCK === "true" || API_BASE === "";

/**
 * Batas waktu tiap panggilan API (ms). HF Spaces free tier tidur saat idle →
 * panggilan pertama = cold start (~30–60 dtk). Timeout mencegah spinner
 * menggantung tanpa batas; nilainya toleran terhadap cold-wake.
 */
const TIMEOUT = {
  classify: 30_000,
  explain: 120_000, // LIME lambat by design (CPU ~30–60 dtk)
  health: 70_000, // /health boleh memicu wake → beri ruang cold start
} as const;

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export type ApiErrorKind = "timeout" | "network" | "http";

/**
 * Error berlabel supaya UI bisa memberi pesan ramah (cold-start vs offline vs
 * HTTP). `message` sudah dalam Bahasa Indonesia siap-tampil.
 */
export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  constructor(kind: ApiErrorKind, message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = status;
  }
}

/**
 * fetch + timeout via AbortController → JSON ter-parse sebagai T.
 * Melempar ApiError: `timeout` (lewat batas waktu / cold start), `network`
 * (gagal terhubung — offline/CORS/DNS), atau `http` (respons non-2xx).
 */
async function fetchJson<T>(
  url: string,
  init: RequestInit,
  timeoutMs: number,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let res: Response;
  try {
    res = await fetch(url, { ...init, signal: controller.signal });
  } catch (e) {
    const name = (e as { name?: string } | null)?.name;
    if (name === "AbortError") {
      throw new ApiError(
        "timeout",
        "Permintaan melebihi batas waktu — backend mungkin sedang bangun (cold start). Coba lagi sebentar.",
      );
    }
    throw new ApiError(
      "network",
      "Tidak dapat terhubung ke backend (offline atau CORS). Periksa NEXT_PUBLIC_API_BASE_URL.",
    );
  } finally {
    clearTimeout(timer);
  }
  if (!res.ok) {
    throw new ApiError(
      "http",
      `Backend menolak permintaan (HTTP ${res.status}).`,
      res.status,
    );
  }
  return (await res.json()) as T;
}

/**
 * Baca data monitoring dari file statis.
 * Return `null` bila file tak ada / gagal parse → halaman tampil empty state.
 */
export async function getMonitoring(): Promise<MonitoringData | null> {
  try {
    const res = await fetch("/data/monitoring.json");
    if (!res.ok) return null;
    return (await res.json()) as MonitoringData;
  } catch {
    return null;
  }
}

/**
 * Klasifikasi on-demand (pipeline Model A → Model B → fusion).
 * Mock: heuristik kata kunci. Nyata: POST {API_BASE}/classify.
 * Melempar ApiError bila backend gagal/lambat → UI tampilkan pesan ramah.
 */
export async function classify(text: string): Promise<ClassifyResponse> {
  if (USE_MOCK) {
    const { mockClassify } = await import("./mock/classify");
    await delay(450); // simulasi latensi supaya loading state terlihat
    return mockClassify(text);
  }
  return fetchJson<ClassifyResponse>(
    `${API_BASE}/classify`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    },
    TIMEOUT.classify,
  );
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
    const { mockExplain } = await import("./mock/explain");
    await delay(1500);
    return mockExplain(text, label, clamped);
  }
  return fetchJson<ExplainResponse>(
    `${API_BASE}/explain`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, num_samples: clamped }),
    },
    TIMEOUT.explain,
  );
}

/**
 * Status backend (untuk badge / peringatan cold-start). Return null dalam mode
 * mock atau bila gagal dihubungi (badge memperlakukan null = offline).
 */
export async function health(): Promise<HealthResponse | null> {
  if (USE_MOCK || API_BASE === "") return null;
  try {
    return await fetchJson<HealthResponse>(
      `${API_BASE}/health`,
      { method: "GET", cache: "no-store" },
      TIMEOUT.health,
    );
  } catch {
    return null;
  }
}
