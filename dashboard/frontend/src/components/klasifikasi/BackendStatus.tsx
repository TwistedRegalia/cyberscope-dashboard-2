"use client";

import { useEffect, useState } from "react";
import { Pill } from "@/components/ui/Pill";
import { Spinner } from "@/components/ui/Spinner";
import { USE_MOCK, health } from "@/lib/api";
import { formatPct } from "@/lib/format";
import type { HealthResponse } from "@/lib/types";

type State =
  | { status: "checking"; slow: boolean }
  | { status: "online"; data: HealthResponse }
  | { status: "offline" };

/**
 * Badge status backend untuk header /klasifikasi. Ping /health saat mount —
 * sekaligus MEMBANGUNKAN HF Space lebih awal (cold start terjadi sebelum user
 * mengetik). Non-blocking. Di mode mock: tak ditampilkan (MockModeNotice sudah
 * menjelaskan). Monitoring `/` tak memakai ini (data statis, tak sentuh backend).
 */
export function BackendStatus() {
  const [state, setState] = useState<State>({ status: "checking", slow: false });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (USE_MOCK) return;
    let active = true;
    // Setelah 8 dtk masih menunggu → jelaskan bahwa ini kemungkinan cold start.
    const slowTimer = setTimeout(() => {
      if (active) {
        setState((s) =>
          s.status === "checking" ? { status: "checking", slow: true } : s,
        );
      }
    }, 8000);
    health().then((data) => {
      if (!active) return;
      setState(data ? { status: "online", data } : { status: "offline" });
    });
    return () => {
      active = false;
      clearTimeout(slowTimer);
    };
  }, [reloadKey]);

  // Early-return SETELAH hooks (USE_MOCK konstan → urutan hook tetap konsisten).
  if (USE_MOCK) return null;

  if (state.status === "checking") {
    return (
      <Pill>
        <Spinner label="Memeriksa backend" />
        {state.slow ? "Membangunkan backend (cold start)…" : "Memeriksa backend…"}
      </Pill>
    );
  }

  if (state.status === "online") {
    const d = state.data;
    return (
      <span
        title={`Model dimuat: ${d.models_loaded ? "ya" : "belum"} · F1 Model A ${formatPct(d.model_a_f1)} · F1 Model B ${formatPct(d.model_b_f1)}`}
      >
        <Pill color="var(--color-vivid-green)">Backend online</Pill>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-2">
      <Pill color="#dc2626">Backend tak terjangkau</Pill>
      <button
        type="button"
        onClick={() => {
          setState({ status: "checking", slow: false });
          setReloadKey((k) => k + 1);
        }}
        className="rounded-lg px-2 py-1 text-[12px] text-electric-blue transition-colors hover:bg-paper-mist focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-electric-blue"
      >
        Coba lagi
      </button>
    </span>
  );
}
