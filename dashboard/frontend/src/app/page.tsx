"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import { getMonitoring } from "@/lib/api";
import type { MonitoringData } from "@/lib/types";
import type { VectorLabel } from "@/lib/vectors";
import { SampleBanner } from "@/components/monitoring/SampleBanner";
import { SummaryCards } from "@/components/monitoring/SummaryCards";
import { VectorDistribution } from "@/components/monitoring/VectorDistribution";
import { PlatformStacked } from "@/components/monitoring/PlatformStacked";
import { TemporalLine, hasTemporal } from "@/components/monitoring/TemporalLine";
import { VectorDrilldown } from "@/components/monitoring/VectorDrilldown";

type State =
  | { status: "loading" }
  | { status: "empty" }
  | { status: "ready"; data: MonitoringData };

export default function MonitoringPage() {
  const [state, setState] = useState<State>({ status: "loading" });
  const [selected, setSelected] = useState<VectorLabel | null>(null);

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
        subtitle="Distribusi 6 vektor ancaman siber dari prediksi model (Model A+B) atas dataset — bukan label lemah Snorkel."
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
              menghasilkannya, lalu muat ulang halaman.
            </>
          }
        />
      )}

      {state.status === "ready" && (
        <div className="space-y-6">
          {state.data.is_sample && <SampleBanner />}
          <SummaryCards data={state.data} />
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
