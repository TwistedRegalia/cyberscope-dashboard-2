import { VECTOR_LABELS, VECTOR_META, type VectorLabel } from "@/lib/vectors";
import { formatPct } from "@/lib/format";
import { cn } from "@/lib/cn";

interface Props {
  probabilities: Record<VectorLabel, number>;
  top: VectorLabel | null;
}

/**
 * Bar probabilitas 6 vektor (diurut descending). Ringan (div, bukan chart).
 * Warna VECTOR_META + label + persen → color-not-only.
 */
export function ProbabilityBars({ probabilities, top }: Props) {
  const rows = VECTOR_LABELS.map((label) => ({
    ...VECTOR_META[label],
    p: probabilities[label] ?? 0,
  })).sort((a, b) => b.p - a.p);

  return (
    <ul className="space-y-2">
      {rows.map((r) => {
        const isTop = r.label === top;
        return (
          <li
            key={r.label}
            className="grid grid-cols-[132px_1fr_52px] items-center gap-3"
          >
            <span
              className={cn(
                "truncate text-[13px]",
                isTop ? "font-semibold text-charcoal" : "text-steel",
              )}
            >
              {r.display}
            </span>
            <span className="block h-2.5 overflow-hidden rounded-full bg-paper-mist">
              <span
                className="block h-full rounded-full"
                style={{
                  width: `${Math.max(r.p * 100, 1.5)}%`,
                  backgroundColor: r.color,
                  opacity: isTop ? 1 : 0.55,
                }}
              />
            </span>
            <span className="tabular text-right text-[12px] text-fog">
              {formatPct(r.p)}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
