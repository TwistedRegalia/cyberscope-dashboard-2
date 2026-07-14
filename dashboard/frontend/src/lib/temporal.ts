import type { TemporalItem } from "./types";

/**
 * Tren layak tampil hanya bila tanggal cukup tersebar (≥3 periode berbeda).
 * Dipisah dari komponen chart (yang menarik recharts) agar bisa diimpor page
 * tanpa membawa recharts ke bundle awal — chart-nya di-load via next/dynamic.
 */
export function hasTemporal(
  temporal: TemporalItem[] | null | undefined,
): boolean {
  if (!temporal || temporal.length === 0) return false;
  return new Set(temporal.map((t) => t.period)).size >= 3;
}
