import type { ReactNode } from "react";
import { Card } from "@/components/ui/Card";

interface ChartCardProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
}

/** Kartu pembungkus chart dengan judul + subjudul seragam. */
export function ChartCard({ title, subtitle, action, children }: ChartCardProps) {
  return (
    <Card>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-[15px] font-semibold text-charcoal">{title}</h3>
          {subtitle && <p className="mt-0.5 text-[13px] text-fog">{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </Card>
  );
}
