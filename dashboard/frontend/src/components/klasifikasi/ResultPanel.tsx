import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ProbabilityBars } from "./ProbabilityBars";
import { RelevanceNotice } from "./RelevanceNotice";
import { LimePanel } from "./LimePanel";
import { getVectorMeta } from "@/lib/vectors";
import { formatPct } from "@/lib/format";
import type { ClassifyResponse } from "@/lib/types";

interface Props {
  result: ClassifyResponse;
  /** Teks yang diklasifikasi — diperlukan untuk LIME. */
  inputText: string;
}

export function ResultPanel({ result, inputText }: Props) {
  // Model A gate: tidak relevan → berhenti, jangan tampilkan vektor.
  if (!result.relevant || !result.label) {
    return <RelevanceNotice />;
  }

  const meta = getVectorMeta(result.label);

  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            aria-hidden
            className="size-3 rounded-full"
            style={{ backgroundColor: meta.color }}
          />
          <h3 className="text-[18px] font-semibold text-charcoal">
            {meta.display}
          </h3>
        </div>
        <Badge tone="blue">{formatPct(result.confidence)} yakin</Badge>
      </div>
      <p className="mt-1 text-[13px] text-fog">
        Vektor dengan keyakinan tertinggi · latensi {result.latency_ms} ms
      </p>

      <div className="mt-5">
        <p className="mb-2 text-[12px] font-medium uppercase tracking-wide text-steel">
          Probabilitas 6 vektor
        </p>
        <ProbabilityBars probabilities={result.probabilities} top={result.label} />
      </div>

      <LimePanel
        key={`${result.label}-${inputText}`}
        text={inputText}
        label={result.label}
      />
    </Card>
  );
}
