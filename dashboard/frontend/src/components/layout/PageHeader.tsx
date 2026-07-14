import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  subtitle?: ReactNode;
  /** Aksi opsional di kanan (mis. badge status backend). */
  actions?: ReactNode;
}

/** Header halaman seragam (dipakai Monitoring & Klasifikasi). */
export function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  return (
    <div className="mb-6 flex items-start justify-between gap-4">
      <div>
        <h1 className="font-display text-[30px] leading-[1.2] text-charcoal">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-1 max-w-2xl text-[15px] text-fog">{subtitle}</p>
        )}
      </div>
      {actions && <div className="shrink-0">{actions}</div>}
    </div>
  );
}
