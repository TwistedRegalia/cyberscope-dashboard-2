import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface PillProps {
  /** Warna titik indikator (mis. warna vektor). Opsional. */
  color?: string;
  children: ReactNode;
  className?: string;
}

/**
 * Pill Dub: radius 9999px, hairline border. Titik warna opsional sebagai
 * indikator kategori — TETAP didampingi label teks (color-not-only).
 */
export function Pill({ color, children, className }: PillProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-full border border-ash bg-canvas-white px-3 py-1 text-[13px] text-charcoal",
        className,
      )}
    >
      {color && (
        <span
          aria-hidden
          className="size-2 shrink-0 rounded-full"
          style={{ backgroundColor: color }}
        />
      )}
      {children}
    </span>
  );
}
