/**
 * Banner "DATA CONTOH" — muncul saat monitoring.json ber-flag is_sample.
 * Integritas: angka fixture TIDAK boleh dikira hasil model nyata.
 */
export function SampleBanner() {
  return (
    <div
      role="note"
      className="mb-6 flex items-start gap-3 rounded-xl border border-[#fcd34d] bg-[#fffbeb] px-4 py-3"
    >
      <span
        aria-hidden
        className="mt-1 size-2 shrink-0 rounded-full bg-[#d97706]"
      />
      <p className="text-[13px] leading-relaxed">
        <span className="font-semibold text-[#92400e]">
          DATA CONTOH — bukan hasil model.
        </span>{" "}
        <span className="text-[#b45309]">
          Angka di halaman ini adalah fixture pengembangan. Ganti{" "}
          <code className="rounded bg-[#fef3c7] px-1 py-0.5 font-mono text-[12px]">
            public/data/monitoring.json
          </code>{" "}
          dengan output batch inference Model A+B untuk data nyata.
        </span>
      </p>
    </div>
  );
}
