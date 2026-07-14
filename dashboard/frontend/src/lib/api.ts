/**
 * SATU lapisan akses data. Komponen TIDAK pernah fetch langsung — semua lewat sini.
 *
 * - Monitoring: baca file statis `public/data/monitoring.json` (di-serve frontend).
 *   Selama backend belum ada, file itu = fixture dev ber-flag `is_sample`.
 *   Menukar ke data nyata = ganti file (hapus flag), tanpa ubah komponen.
 * - Klasifikasi/LIME (M4/M5): fetch ke NEXT_PUBLIC_API_BASE_URL atau mock.
 */
import type { MonitoringData } from "./types";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

/**
 * Baca data monitoring dari file statis.
 * Return `null` bila file tak ada / gagal parse → halaman tampil empty state
 * (JANGAN mengarang angka).
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
