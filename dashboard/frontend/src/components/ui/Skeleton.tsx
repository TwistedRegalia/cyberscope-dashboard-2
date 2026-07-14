import { cn } from "@/lib/cn";

/** Placeholder loading (hormati prefers-reduced-motion). */
export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "rounded-md bg-paper-mist motion-safe:animate-pulse",
        className,
      )}
    />
  );
}
