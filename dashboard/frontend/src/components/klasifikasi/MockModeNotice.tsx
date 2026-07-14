import { USE_MOCK } from "@/lib/api";

/**
 * Integritas: saat backend belum ada, hasil klasifikasi & LIME berasal dari mock
 * (heuristik), BUKAN model nyata. Tandai jelas (mirror banner "DATA CONTOH"
 * di Monitoring). Sembunyi otomatis saat backend nyata terhubung.
 */
export function MockModeNotice() {
  if (!USE_MOCK) return null;
  return (
    <div
      role="note"
      className="flex items-start gap-3 rounded-xl border border-ash bg-paper-mist px-4 py-3"
    >
      <span aria-hidden className="mt-1 size-2 shrink-0 rounded-full bg-fog" />
      <p className="text-[13px] leading-relaxed text-steel">
        <span className="font-semibold text-charcoal">Mode demo (mock).</span>{" "}
        Hasil klasifikasi &amp; LIME berasal dari heuristik contoh, bukan model
        nyata. Set{" "}
        <code className="rounded bg-canvas-white px-1 py-0.5 font-mono text-[12px]">
          NEXT_PUBLIC_API_BASE_URL
        </code>{" "}
        ke backend FastAPI (dan{" "}
        <code className="rounded bg-canvas-white px-1 py-0.5 font-mono text-[12px]">
          NEXT_PUBLIC_USE_MOCK=false
        </code>
        ) untuk pipeline model sebenarnya.
      </p>
    </div>
  );
}
