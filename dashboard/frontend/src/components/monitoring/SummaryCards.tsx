import { Card } from "@/components/ui/Card";
import { formatNumber, formatPct } from "@/lib/format";
import { cn } from "@/lib/cn";
import type { MonitoringData } from "@/lib/types";

function Stat({
  label,
  value,
  hint,
  valueClassName,
}: {
  label: string;
  value: string;
  hint?: string;
  valueClassName?: string;
}) {
  return (
    <Card>
      <p className="text-[12px] font-medium uppercase tracking-wide text-steel">
        {label}
      </p>
      <p
        className={cn(
          "font-display tabular mt-1 text-[30px] text-charcoal",
          valueClassName,
        )}
      >
        {value}
      </p>
      {hint && <p className="mt-0.5 text-[13px] text-fog">{hint}</p>}
    </Card>
  );
}

export function SummaryCards({ data }: { data: MonitoringData }) {
  const relevantPct = data.total_rows
    ? data.relevant_rows / data.total_rows
    : 0;
  const range = data.date_range
    ? `${data.date_range.start} – ${data.date_range.end}`
    : "—";

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      <Stat
        label="Total baris"
        value={formatNumber(data.total_rows)}
        hint="dataset terkumpul (X + YouTube)"
      />
      <Stat
        label="Relevan (Model A)"
        value={formatNumber(data.relevant_rows)}
        hint={`${formatPct(relevantPct)} dari total`}
      />
      <Stat
        label="Rentang tanggal"
        value={range}
        valueClassName="text-[22px]"
        hint="periode data"
      />
    </div>
  );
}
