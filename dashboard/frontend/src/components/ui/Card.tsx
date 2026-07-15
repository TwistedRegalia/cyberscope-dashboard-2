import type { HTMLAttributes } from "react";
import { cn } from "@/lib/cn";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Padding internal 16px (default). Set false untuk kontainer tanpa padding. */
  padded?: boolean;
}

/**
 * Kartu dashboard Dub: putih, border 1px #e5e5e5, radius 12px, TANPA shadow.
 * Struktur dari border + spacing, bukan elevasi.
 */
export function Card({ className, padded = true, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-ash bg-canvas-white",
        padded && "p-4",
        className,
      )}
      {...props}
    />
  );
}
