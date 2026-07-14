import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";

export default function KlasifikasiPage() {
  return (
    <div>
      <PageHeader
        title="Klasifikasi on-demand"
        subtitle="Tempel teks atau pilih contoh siap-klik untuk mendapatkan vektor + tingkat keyakinan. XAI (LIME) opsional."
      />
      <EmptyState
        title="Panel klasifikasi segera hadir"
        description="Input teks + contoh per vektor, hasil label + confidence + bar probabilitas 6 kelas akan tampil di M4 (memanggil POST /classify)."
      />
    </div>
  );
}
