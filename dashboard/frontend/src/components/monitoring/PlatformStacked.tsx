"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { memo } from "react";
import { getVectorMeta } from "@/lib/vectors";
import { formatNumber, formatPct } from "@/lib/format";
import type { PlatformByVectorItem } from "@/lib/types";
import { ChartCard } from "./ChartCard";

// Platform = dimensi non-vektor → dua tone netral (bukan warna vektor).
// Mengikuti tema: light (gelap/abu di atas putih) ↔ dark (terang/abu redup).
const YT_COLOR = "var(--platform-youtube)";
const X_COLOR = "var(--platform-x)";

interface Row {
  label: string;
  short: string;
  display: string;
  youtube_count: number;
  x_count: number;
  total: number;
}

export const PlatformStacked = memo(function PlatformStacked({
  data,
}: {
  data: PlatformByVectorItem[];
}) {
  const rows: Row[] = data
    .map((d) => {
      const m = getVectorMeta(d.label);
      return {
        label: d.label,
        short: m.short,
        display: m.display,
        youtube_count: d.youtube_count,
        x_count: d.x_count,
        total: d.youtube_count + d.x_count,
      };
    })
    .sort((a, b) => b.total - a.total);

  return (
    <ChartCard
      title="Proporsi platform per vektor"
      subtitle="YouTube vs X — proporsi per vektor (100%)"
    >
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={rows}
            layout="vertical"
            stackOffset="expand"
            margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
            barCategoryGap={10}
          >
            <CartesianGrid horizontal={false} stroke="var(--chart-grid)" />
            <XAxis
              type="number"
              domain={[0, 1]}
              tick={{ fontSize: 11, fill: "var(--color-fog)" }}
              tickFormatter={(v) => formatPct(Number(v), 0)}
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
              content={<PlatformTooltip />}
            />
            <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
            <Bar
              dataKey="youtube_count"
              name="YouTube"
              stackId="p"
              fill={YT_COLOR}
              isAnimationActive={false}
            />
            <Bar
              dataKey="x_count"
              name="X"
              stackId="p"
              fill={X_COLOR}
              radius={[0, 4, 4, 0]}
              isAnimationActive={false}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
});

function PlatformTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: Row }>;
}) {
  if (!active || !payload?.length) return null;
  const r = payload[0].payload;
  const total = r.total || 1;
  return (
    <div className="rounded-lg border border-ash bg-canvas-white px-3 py-2 text-[13px] shadow-sm">
      <div className="font-medium text-charcoal">{r.display}</div>
      <div className="tabular mt-1 space-y-0.5 text-fog">
        <div>
          YouTube: {formatNumber(r.youtube_count)} ({formatPct(r.youtube_count / total)})
        </div>
        <div>
          X: {formatNumber(r.x_count)} ({formatPct(r.x_count / total)})
        </div>
      </div>
    </div>
  );
}
