interface BrandMarkProps {
  className?: string;
}

/**
 * Logomark "CyberScope" — mark bertema scope (reticle/teropong sasaran):
 * cincin + crosshair + titik tengah. Mengikat ke nama (…Scope) dan fungsi
 * memantau/menyorot. Memakai currentColor → warnai via `text-electric-blue`.
 */
export function BrandMark({ className }: BrandMarkProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
      fill="none"
      role="img"
      aria-hidden
    >
      <circle cx="12" cy="12" r="7.5" stroke="currentColor" strokeWidth="2" />
      <path
        d="M12 1.5v4M12 18.5v4M1.5 12h4M18.5 12h4"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="12" cy="12" r="2.4" fill="currentColor" />
    </svg>
  );
}
