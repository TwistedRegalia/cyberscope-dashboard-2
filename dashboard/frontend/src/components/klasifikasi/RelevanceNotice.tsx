/** Ditampilkan saat Model A menilai teks tidak relevan → berhenti (tak ke 6 vektor). */
export function RelevanceNotice() {
  return (
    <div className="rounded-xl border border-ash bg-paper-mist px-4 py-6 text-center">
      <p className="text-[15px] font-medium text-charcoal">
        Teks dinilai tidak relevan
      </p>
      <p className="mx-auto mt-1 max-w-md text-[14px] text-fog">
        Model A (filter relevansi) menilai teks ini bukan diskursus vektor
        ancaman siber, sehingga klasifikasi 6 vektor tidak dilanjutkan.
      </p>
    </div>
  );
}
