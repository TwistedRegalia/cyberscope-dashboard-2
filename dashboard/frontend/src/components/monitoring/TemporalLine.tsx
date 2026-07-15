"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { memo } from "react";
import { VECTOR_META, isVectorLabel, type VectorLabel } from "@/lib/vectors";
import { formatNumber } from "@/lib/format";
import type { TemporalItem } from "@/lib/types";
import { ChartCard } from "./ChartCard";

type WideRow = { period: string } & Partial<Record<VectorLabel, number>>;

export const TemporalLine = memo(function TemporalLine({
  temporal,
}: {
  temporal: TemporalItem[];
}) {
  const periods = Array.from(new Set(temporal.map((t) => t.period))).sort();
  const labels = Array.from(new Set(temporal.map((t) => t.label))).filter(
    isVectorLabel,
  );

  const rows: WideRow[] = periods.map((p) => {
    const row: WideRow = { period: p };
    temporal
      .filter((t) => t.period === p)
      .forEach((t) => {
        if (isVectorLabel(t.label)) row[t.label] = t.count;
      });
    return row;
  });

  return (
    <ChartCard
      title="Tren waktu"
      subtitle="Jumlah komentar per bulan (vektor teratas)"
    >
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={rows} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
            <XAxis
              dataKey="period"
              tick={{ fontSize: 11, fill: "var(--color-fog)" }}
              axisLine={{ stroke: "var(--color-ash)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "var(--color-fog)" }}
              tickFormatter={(v) => formatNumber(Number(v))}
              axisLine={false}
              tickLine={false}
              width={44}
            />
            <Tooltip content={<TemporalTooltip />} />
            <Legend iconType="plainline" wrapperStyle={{ fontSize: 12 }} />
            {labels.map((label) => (
              <Line
                key={label}
                type="monotone"
                dataKey={label}
                name={VECTOR_META[label].display}
                stroke={VECTOR_META[label].color}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
});

function TemporalTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ name?: string; value?: number; color?: string; dataKey?: string | number }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-ash bg-canvas-white px-3 py-2 text-[13px] shadow-sm">
      <div className="mb-1 font-medium text-charcoal">{label}</div>
      <div className="tabular space-y-0.5">
        {payload.map((p) => (
          <div key={String(p.dataKey)} className="flex items-center gap-2 text-fog">
            <span
              className="size-2 rounded-full"
              style={{ backgroundColor: p.color }}
            />
            {p.name}: {formatNumber(Number(p.value ?? 0))}
          </div>
        ))}
      </div>
    </div>
  );
}
