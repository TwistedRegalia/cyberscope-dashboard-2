import { cn } from "@/lib/cn";

interface SpinnerProps {
  className?: string;
  /** Label untuk screen reader. */
  label?: string;
}

/** Spinner ringan (hormati prefers-reduced-motion via utilitas motion-safe). */
export function Spinner({ className, label = "Memuat…" }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label={label}
      className={cn(
        "inline-block size-4 rounded-full border-2 border-ash border-t-electric-blue motion-safe:animate-spin",
        className,
      )}
    />
  );
}
