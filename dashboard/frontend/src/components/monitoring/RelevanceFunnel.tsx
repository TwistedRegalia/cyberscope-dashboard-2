import { memo, useMemo } from "react";
import { getVectorMeta } from "@/lib/vectors";
import { formatNumber, formatPct } from "@/lib/format";
import type { MonitoringData } from "@/lib/types";
import { ChartCard } from "./ChartCard";

/**
 * Funnel relevansi — menampilkan rantai pipeline 2-lapis sebagai ikhtisar.
 * Semua angka = field langsung monitoring.json (total_rows, relevant_rows, pct),
 * tidak ada yang dihitung ulang: Σ 6 vektor = relevant_rows (konsisten).
 * Presentasional (bukan target drill-down) — CSS/flex, tanpa recharts.
 */
export const RelevanceFunnel = memo(function RelevanceFunnel({
  data,
}: {
  data: MonitoringData;
}) {
  const { total_rows, relevant_rows, vector_distribution } = data;
  const relevantPct = total_rows > 0 ? relevant_rows / total_rows : 0;

  const segments = useMemo(
    () => vector_distribution.toSorted((a, b) => b.count - a.count),
    [vector_distribution],
  );

  const compositionLabel =
    `Komposisi ${formatNumber(relevant_rows)} data relevan: ` +
    segments
      .map((s) => `${getVectorMeta(s.label).display} ${formatPct(s.pct)}`)
      .join(", ");

  return (
    <ChartCard
      title="Alur klasifikasi"
      subtitle="Dari total data ke 6 vektor (Model A -> Model B)"
    >
      <div className="space-y-4">
        <FunnelStage
          label="Total baris"
          value={formatNumber(total_rows)}
          caption="100%"
          pct={1}
          tone="var(--funnel-total)"
        />
        <FunnelStage
          label="Relevan - Model A"
          value={formatNumber(relevant_rows)}
          caption={formatPct(relevantPct)}
          pct={relevantPct}
          tone="var(--color-electric-blue)"
        />

        <div>
          <p className="mb-2 text-[12px] font-medium uppercase tracking-wide text-steel">
            Komposisi 6 vektor · Model B
          </p>
          <div
            role="img"
            aria-label={compositionLabel}
            className="flex h-9 w-full overflow-hidden rounded-md"
          >
            {segments.map((s, i) => {
              const meta = getVectorMeta(s.label);
              const wide = s.pct >= 0.15;
              return (
                <div
                  key={s.label}
                  title={`${meta.display}: ${formatNumber(s.count)} (${formatPct(s.pct)})`}
                  className="flex items-center justify-center overflow-hidden whitespace-nowrap px-1 text-[12px] text-white"
                  style={{
                    width: `${s.pct * 100}%`,
                    backgroundColor: meta.color,
                    boxShadow:
                      i < segments.length - 1
                        ? "inset -1px 0 0 var(--color-canvas-white)"
                        : undefined,
                  }}
                >
                  {wide && `${meta.short} · ${formatPct(s.pct)}`}
                </div>
              );
            })}
          </div>
          <p className="mt-2 text-[13px] text-fog">
            Proporsi 6 vektor atas {formatNumber(relevant_rows)} data relevan,
            rincian angka di tabel bawah.
          </p>
        </div>
      </div>
    </ChartCard>
  );
});

function FunnelStage({
  label,
  value,
  caption,
  pct,
  tone,
}: {
  label: string;
  value: string;
  caption: string;
  pct: number;
  tone: string;
}) {
  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between gap-3 text-[13px]">
        <span className="font-medium text-charcoal">{label}</span>
        <span className="text-fog">
          <span className="tabular text-charcoal">{value}</span> · {caption}
        </span>
      </div>
      <div className="h-8 w-full overflow-hidden rounded-md bg-paper-mist">
        <div
          className="h-full rounded-md"
          style={{ width: `${Math.max(pct * 100, 1.5)}%`, backgroundColor: tone }}
        />
      </div>
    </div>
  );
}
