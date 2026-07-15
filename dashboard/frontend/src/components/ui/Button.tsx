import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

type Variant = "primary" | "outline" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const base =
  "inline-flex items-center justify-center gap-2 text-[14px] font-medium transition-colors " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-electric-blue focus-visible:ring-offset-2 " +
  "disabled:pointer-events-none disabled:opacity-50";

const variants: Record<Variant, string> = {
  // Satu primary action per surface (fill hitam Dub).
  primary: "rounded-lg bg-primary-action-fill px-4 py-2 text-canvas-white hover:bg-charcoal",
  // Workhorse: outline hairline.
  outline: "rounded-lg border border-ash bg-canvas-white px-4 py-2 text-charcoal hover:bg-paper-mist",
  // Nav / aksi ringan.
  ghost: "rounded-lg px-3 py-2 text-charcoal hover:bg-paper-mist",
};

export function Button({ variant = "outline", className, type, ...props }: ButtonProps) {
  return (
    <button
      type={type ?? "button"}
      className={cn(base, variants[variant], className)}
      {...props}
    />
  );
}
