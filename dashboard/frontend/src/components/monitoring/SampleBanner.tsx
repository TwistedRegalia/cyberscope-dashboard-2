/**
 * Banner "DATA CONTOH" — muncul saat monitoring.json ber-flag is_sample.
 * Integritas: angka fixture TIDAK boleh dikira hasil model nyata.
 * Warna via var(--warn-*) agar adaptif light/dark.
 */
export function SampleBanner() {
  return (
    <div
      role="note"
      className="mb-6 flex items-start gap-3 rounded-xl border px-4 py-3"
      style={{
        backgroundColor: "var(--warn-bg)",
        borderColor: "var(--warn-border)",
      }}
    >
      <span
        aria-hidden
        className="mt-1 size-2 shrink-0 rounded-full"
        style={{ backgroundColor: "var(--warn-dot)" }}
      />
      <p
        className="text-[13px] leading-relaxed"
        style={{ color: "var(--warn-text)" }}
      >
        <span
          className="font-semibold"
          style={{ color: "var(--warn-strong)" }}
        >
          DATA CONTOH, bukan hasil model.
        </span>{" "}
        Angka di halaman ini adalah fixture pengembangan. Ganti{" "}
        <code
          className="rounded px-1 py-0.5 font-mono text-[12px]"
          style={{ backgroundColor: "var(--warn-code-bg)" }}
        >
          public/data/monitoring.json
        </code>{" "}
        dengan output batch inference Model A+B untuk data nyata.
      </p>
    </div>
  );
}
