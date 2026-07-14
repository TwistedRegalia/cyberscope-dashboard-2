"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { explain } from "@/lib/api";
import type { ExplainResponse } from "@/lib/types";
import type { VectorLabel } from "@/lib/vectors";

type Status = "idle" | "loading" | "done" | "error";

function tint(weight: number): string {
  const alpha = Math.min(0.15 + Math.abs(weight), 0.85);
  // Mendukung = hijau, menentang = merah (didampingi tanda + angka → color-not-only).
  return weight >= 0
    ? `rgba(22, 163, 74, ${alpha})`
    : `rgba(220, 38, 38, ${alpha})`;
}

function signed(weight: number): string {
  const sign = weight >= 0 ? "+" : "−";
  return `${sign}${Math.abs(weight).toFixed(2)}`;
}

/**
 * Panel XAI (LIME) — OPSIONAL, default tidak jalan, dipicu tombol. Proses lambat
 * di backend nyata (±30–60 dtk) → indikator progres, non-blocking (state lokal,
 * bukan modal; interaksi lain tetap jalan). Highlight token: intensitas ∝ |bobot|.
 */
export function LimePanel({ text, label }: { text: string; label: VectorLabel }) {
  const [status, setStatus] = useState<Status>("idle");
  const [data, setData] = useState<ExplainResponse | null>(null);
  const [error, setError] = useState("");

  async function run() {
    setStatus("loading");
    setError("");
    setData(null);
    try {
      const r = await explain(text, label);
      setData(r);
      setStatus("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Terjadi kesalahan");
      setStatus("error");
    }
  }

  return (
    <div className="mt-5 border-t border-ash pt-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-[14px] font-medium text-charcoal">
            Penjelasan XAI (LIME)
          </p>
          <p className="text-[12px] text-fog">
            Opsional · lambat (±30–60 detik pada backend nyata) · tidak
            menghalangi interaksi lain.
          </p>
        </div>
        <Button variant="outline" onClick={run} disabled={status === "loading"}>
          {status === "loading" ? (
            <>
              <Spinner label="Memproses LIME" /> Memproses…
            </>
          ) : status === "done" ? (
            "Jalankan ulang"
          ) : (
            "Jelaskan dengan LIME"
          )}
        </Button>
      </div>

      {status === "loading" && (
        <div className="mt-3 flex items-center gap-2 text-[13px] text-fog">
          <Spinner label="Menghitung" />
          Menghitung atribusi token… mohon tunggu (±30–60 detik).
        </div>
      )}

      {status === "error" && (
        <p className="mt-3 text-[13px] text-charcoal">
          Gagal menjalankan LIME: {error}.
        </p>
      )}

      {status === "done" && data && (
        <div className="mt-3">
          <div className="mb-2 flex flex-wrap items-center gap-3 text-[12px] text-fog">
            <span className="inline-flex items-center gap-1">
              <span
                aria-hidden
                className="size-2 rounded-full"
                style={{ backgroundColor: "rgba(22,163,74,0.7)" }}
              />
              mendukung label
            </span>
            <span className="inline-flex items-center gap-1">
              <span
                aria-hidden
                className="size-2 rounded-full"
                style={{ backgroundColor: "rgba(220,38,38,0.7)" }}
              />
              menentang label
            </span>
            <span>· intensitas ∝ |bobot| · {data.num_samples} sampel</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {data.tokens.map((t, i) => (
              <span
                key={`${t.token}-${i}`}
                className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-[13px] text-charcoal"
                style={{ backgroundColor: tint(t.weight) }}
                title={`bobot ${signed(t.weight)}`}
              >
                {t.token}
                <span className="tabular text-[11px] text-graphite">
                  {signed(t.weight)}
                </span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
