"use client";

import { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/Button";
import { getMonitoring } from "@/lib/api";
import type { MonitoringData } from "@/lib/types";
import type { VectorLabel } from "@/lib/vectors";
import { SampleBanner } from "@/components/monitoring/SampleBanner";
import { SummaryCards } from "@/components/monitoring/SummaryCards";
import { RelevanceFunnel } from "@/components/monitoring/RelevanceFunnel";
import { VectorTable } from "@/components/monitoring/VectorTable";
import { VectorDrilldown } from "@/components/monitoring/VectorDrilldown";
import { hasTemporal } from "@/lib/temporal";

// Chart (recharts) di-load via next/dynamic → keluar dari bundle awal route.
const chartFallback = () => <Skeleton className="h-[360px]" />;
const VectorDistribution = dynamic(
  () =>
    import("@/components/monitoring/VectorDistribution").then(
      (m) => m.VectorDistribution,
    ),
  { ssr: false, loading: chartFallback },
);
const PlatformStacked = dynamic(
  () =>
    import("@/components/monitoring/PlatformStacked").then(
      (m) => m.PlatformStacked,
    ),
  { ssr: false, loading: chartFallback },
);
const TemporalLine = dynamic(
  () =>
    import("@/components/monitoring/TemporalLine").then((m) => m.TemporalLine),
  { ssr: false, loading: chartFallback },
);

type State =
  | { status: "loading" }
  | { status: "empty" }
  | { status: "ready"; data: MonitoringData };

export default function MonitoringPage() {
  const [state, setState] = useState<State>({ status: "loading" });
  const [selected, setSelected] = useState<VectorLabel | null>(null);

  // Retry (dipanggil dari tombol/event handler → setState sinkron aman di sini).
  const load = useCallback(() => {
    setState({ status: "loading" });
    getMonitoring().then((data) => {
      setState(data ? { status: "ready", data } : { status: "empty" });
    });
  }, []);

  // Mount: state awal sudah "loading" → cukup fetch (setState hanya di callback async).
  useEffect(() => {
    let active = true;
    getMonitoring().then((data) => {
      if (!active) return;
      setState(data ? { status: "ready", data } : { status: "empty" });
    });
    return () => {
      active = false;
    };
  }, []);

  return (
    <div>
      <PageHeader
        title="Monitoring"
        subtitle="Distribusi 6 vektor ancaman siber dari prediksi model (Model A+B) atas dataset"
      />

      {state.status === "loading" && <LoadingSkeleton />}

      {state.status === "empty" && (
        <EmptyState
          title="Data monitoring belum tersedia"
          description={
            <>
              File{" "}
              <code className="font-mono text-[13px]">
                public/data/monitoring.json
              </code>{" "}
              tidak ditemukan. Jalankan batch inference Model A+B untuk
              menghasilkannya, lalu muat ulang.
            </>
          }
          action={
            <Button variant="outline" onClick={load}>
              Muat ulang
            </Button>
          }
        />
      )}

      {state.status === "ready" && (
        <div className="space-y-6">
          {state.data.is_sample && <SampleBanner />}
          <SummaryCards data={state.data} />
          <RelevanceFunnel data={state.data} />
          <div className="grid gap-6 lg:grid-cols-2">
            <VectorDistribution
              data={state.data.vector_distribution}
              selected={selected}
              onSelect={setSelected}
            />
            <PlatformStacked data={state.data.platform_by_vector} />
          </div>
          {hasTemporal(state.data.temporal) && (
            <TemporalLine temporal={state.data.temporal ?? []} />
          )}
          <VectorTable
            distribution={state.data.vector_distribution}
            platform={state.data.platform_by_vector}
            selected={selected}
            onSelect={setSelected}
          />
          <VectorDrilldown
            selected={selected}
            samples={selected ? state.data.samples_by_vector[selected] : undefined}
            onClose={() => setSelected(null)}
          />
        </div>
      )}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Skeleton className="h-[360px]" />
        <Skeleton className="h-[360px]" />
      </div>
    </div>
  );
}
