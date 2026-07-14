"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { VECTOR_META, isVectorLabel, type VectorLabel } from "@/lib/vectors";
import { formatNumber, formatPct } from "@/lib/format";
import type { VectorDistributionItem } from "@/lib/types";
import { ChartCard } from "./ChartCard";

interface Row extends VectorDistributionItem {
  short: string;
  color: string;
}

interface Props {
  data: VectorDistributionItem[];
  selected?: VectorLabel | null;
  onSelect?: (label: VectorLabel) => void;
}

/**
 * Distribusi 6 vektor — bar HORIZONTAL diurut descending (aturan no-pie-overuse
 * untuk >5 kategori), label nilai langsung, warna VECTOR_META. Klik batang →
 * pilih vektor untuk drill-down. Warna bukan satu-satunya pembawa makna:
 * label kategori + nilai selalu tampak.
 */
export function VectorDistribution({ data, selected, onSelect }: Props) {
  const rows: Row[] = [...data]
    .sort((a, b) => b.count - a.count)
    .map((d) => {
      const meta = VECTOR_META[d.label];
      return {
        ...d,
        short: meta?.short ?? d.label_display,
        color: meta?.color ?? "#737373",
      };
    });

  function handleClick(entry: unknown) {
    if (!onSelect) return;
    const e = entry as { label?: string; payload?: { label?: string } };
    const label = e.payload?.label ?? e.label;
    if (label && isVectorLabel(label)) onSelect(label);
  }

  return (
    <ChartCard
      title="Distribusi 6 vektor"
      subtitle="Prediksi Model B · klik batang untuk melihat contoh"
    >
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={rows}
            layout="vertical"
            margin={{ top: 4, right: 52, bottom: 4, left: 8 }}
            barCategoryGap={10}
          >
            <CartesianGrid horizontal={false} stroke="var(--chart-grid)" />
            <XAxis
              type="number"
              tick={{ fontSize: 11, fill: "var(--color-fog)" }}
              tickFormatter={(v) => formatNumber(Number(v))}
              axisLine={{ stroke: "var(--color-ash)" }}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="short"
              width={112}
              tick={{ fontSize: 12, fill: "var(--color-charcoal)" }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={{ fill: "var(--color-paper-mist)" }}
              content={<DistTooltip />}
            />
            <Bar
              dataKey="count"
              radius={[0, 4, 4, 0]}
              cursor={onSelect ? "pointer" : undefined}
              onClick={handleClick}
              isAnimationActive={false}
            >
              {rows.map((r) => (
                <Cell
                  key={r.label}
                  fill={r.color}
                  fillOpacity={selected && selected !== r.label ? 0.35 : 1}
                />
              ))}
              <LabelList
                dataKey="count"
                position="right"
                formatter={(v) => formatNumber(Number(v))}
                style={{ fontSize: 11, fill: "var(--color-steel)" }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}

function DistTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: Row }>;
}) {
  if (!active || !payload?.length) return null;
  const r = payload[0].payload;
  return (
    <div className="rounded-lg border border-ash bg-canvas-white px-3 py-2 text-[13px] shadow-sm">
      <div className="flex items-center gap-2 font-medium text-charcoal">
        <span
          className="size-2 rounded-full"
          style={{ backgroundColor: r.color }}
        />
        {r.label_display}
      </div>
      <div className="tabular mt-1 text-fog">
        {formatNumber(r.count)} komentar · {formatPct(r.pct)}
      </div>
    </div>
  );
}
