import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface EmptyStateProps {
  title: string;
  description?: ReactNode;
  icon?: ReactNode;
  action?: ReactNode;
  className?: string;
}

/**
 * Empty state seragam — dipakai saat data belum ada / gagal muat.
 * JANGAN karang angka: tampilkan pesan + panduan.
 */
export function EmptyState({
  title,
  description,
  icon,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-smoke bg-paper-mist px-6 py-12 text-center",
        className,
      )}
    >
      {icon && <div className="text-fog">{icon}</div>}
      <p className="text-[15px] font-medium text-charcoal">{title}</p>
      {description && (
        <p className="max-w-md text-[14px] text-fog">{description}</p>
      )}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
