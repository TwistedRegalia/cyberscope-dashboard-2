import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { getVectorMeta, type VectorLabel } from "@/lib/vectors";
import { formatPct } from "@/lib/format";
import type { SampleItem } from "@/lib/types";

interface Props {
  selected: VectorLabel | null;
  samples: SampleItem[] | undefined;
  onClose: () => void;
}

/** Panel expand contoh komentar untuk vektor terpilih (bukan halaman baru). */
export function VectorDrilldown({ selected, samples, onClose }: Props) {
  if (!selected) {
    return (
      <Card>
        <p className="text-[14px] text-fog">
          Klik satu vektor pada chart distribusi untuk melihat contoh komentar
          terklasifikasi ke vektor itu.
        </p>
      </Card>
    );
  }

  const meta = getVectorMeta(selected);
  const list = samples ?? [];

  return (
    <Card>
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            aria-hidden
            className="size-2.5 rounded-full"
            style={{ backgroundColor: meta.color }}
          />
          <h3 className="text-[15px] font-semibold text-charcoal">
            Contoh · {meta.display}
          </h3>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg px-2 py-1 text-[13px] text-fog transition-colors hover:bg-paper-mist hover:text-charcoal focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-electric-blue"
        >
          Tutup
        </button>
      </div>

      <p className="mb-3 text-[13px] text-fog">
        Komentar asli dari dataset, 40 dengan keyakinan tertinggi menurut model.
      </p>

      {list.length === 0 ? (
        <p className="text-[14px] text-fog">
          Tidak ada contoh tersimpan untuk vektor ini.
        </p>
      ) : (
        <ul className="space-y-2">
          {list.map((s, i) => (
            <li
              key={`${s.platform}-${i}`}
              className="rounded-lg border border-ash p-3"
            >
              <p className="text-[14px] leading-relaxed text-charcoal">
                {s.text}
              </p>
              <div className="mt-2 flex flex-wrap items-center gap-2 text-[12px] text-fog">
                <Badge tone="blue">{formatPct(s.confidence)} yakin</Badge>
                <span className="rounded-full bg-paper-mist px-2 py-0.5">
                  {s.platform === "x" ? "X" : "YouTube"}
                </span>
                {s.date && <span className="tabular">{s.date}</span>}
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
