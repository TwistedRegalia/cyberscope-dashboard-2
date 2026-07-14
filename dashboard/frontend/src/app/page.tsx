import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";

export default function MonitoringPage() {
  return (
    <div>
      <PageHeader
        title="Monitoring"
        subtitle="Distribusi 6 vektor ancaman siber dari prediksi model atas dataset — bukan label lemah Snorkel."
      />
      <EmptyState
        title="Panel monitoring segera hadir"
        description="Kartu ringkas, distribusi 6 vektor, proporsi platform (YouTube vs X), dan drill-down contoh per vektor akan tampil di M3 dari monitoring.json."
      />
    </div>
  );
}
