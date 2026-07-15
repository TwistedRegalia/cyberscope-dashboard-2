import { memo, useMemo } from "react";
import { getVectorMeta, type VectorLabel } from "@/lib/vectors";
import { formatNumber, formatPct } from "@/lib/format";
import { cn } from "@/lib/cn";
import type {
  PlatformByVectorItem,
  VectorDistributionItem,
} from "@/lib/types";
import { ChartCard } from "./ChartCard";

interface Props {
  distribution: VectorDistributionItem[];
  platform: PlatformByVectorItem[];
  selected: VectorLabel | null;
  onSelect: (label: VectorLabel) => void;
}

/**
 * Tabel detail 6 vektor — semua nilai adalah field langsung dari monitoring.json
 * (hanya diformat, tidak dihitung ulang). Padanan tabular untuk chart distribusi:
 * sekaligus target drill-down yang mudah diakses (tombol per baris, keyboard-friendly).
 */
export const VectorTable = memo(function VectorTable({
  distribution,
  platform,
  selected,
  onSelect,
}: Props) {
  // Gabungkan proporsi platform ke tiap vektor berdasarkan label.
  const platformByLabel = useMemo(
    () => new Map(platform.map((p) => [p.label, p])),
    [platform],
  );

  const rows = useMemo(
    () => distribution.toSorted((a, b) => b.count - a.count),
    [distribution],
  );

  return (
    <ChartCard
      title="Detail per vektor"
      subtitle="Jumlah, proporsi, dan sebaran platform tiap vektor (klik untuk contoh)"
    >
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-[14px]">
          <caption className="sr-only">
            Distribusi enam vektor ancaman siber: jumlah, persentase, dan
            proporsi platform YouTube dan X. Klik nama vektor untuk melihat
            contoh komentar.
          </caption>
          <thead>
            <tr className="border-b border-ash text-left text-[12px] font-medium uppercase tracking-wide text-steel">
              <th scope="col" className="py-2 pr-3 font-medium">
                Vektor
              </th>
              <th scope="col" className="py-2 px-3 text-right font-medium">
                Jumlah
              </th>
              <th scope="col" className="py-2 px-3 text-right font-medium">
                %
              </th>
              <th scope="col" className="py-2 px-3 text-right font-medium">
                YouTube
              </th>
              <th scope="col" className="py-2 pl-3 text-right font-medium">
                X
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const meta = getVectorMeta(row.label);
              const plat = platformByLabel.get(row.label);
              const isSelected = selected === row.label;
              return (
                <tr
                  key={row.label}
                  className={cn(
                    "border-b border-ash last:border-0",
                    isSelected && "bg-tint-blue",
                  )}
                >
                  <th scope="row" className="py-1 pr-3 font-normal">
                    <button
                      type="button"
                      onClick={() => onSelect(row.label)}
                      aria-pressed={isSelected}
                      className="flex w-full items-center gap-2 rounded-md px-1 py-1.5 text-left text-charcoal transition-colors hover:bg-paper-mist focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-electric-blue"
                    >
                      <span
                        aria-hidden
                        className="size-2.5 shrink-0 rounded-full"
                        style={{ backgroundColor: meta.color }}
                      />
                      {meta.display}
                    </button>
                  </th>
                  <td className="tabular px-3 py-2 text-right text-charcoal">
                    {formatNumber(row.count)}
                  </td>
                  <td className="tabular px-3 py-2 text-right text-fog">
                    {formatPct(row.pct)}
                  </td>
                  <td className="tabular px-3 py-2 text-right text-fog">
                    {plat ? formatPct(plat.youtube_pct) : "—"}
                  </td>
                  <td className="tabular py-2 pl-3 text-right text-fog">
                    {plat ? formatPct(plat.x_pct) : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </ChartCard>
  );
});
