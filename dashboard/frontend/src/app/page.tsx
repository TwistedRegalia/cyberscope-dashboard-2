import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Pill } from "@/components/ui/Pill";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { VECTOR_LABELS, VECTOR_META } from "@/lib/vectors";

/**
 * Halaman verifikasi M1 (SEMENTARA) — cek token desain Dub, font Inter,
 * VECTOR_META, dan primitif UI. Diganti shell + Monitoring pada M2/M3.
 */
export default function Home() {
  return (
    <main className="mx-auto w-full max-w-[1200px] px-6 py-12">
      <header className="mb-8">
        <Badge tone="blue" className="mb-3">
          M1 · Token desain
        </Badge>
        <h1 className="font-display text-[36px] leading-[1.11] text-charcoal">
          Sistem desain Dub aktif
        </h1>
        <p className="mt-2 max-w-2xl text-[16px] text-fog">
          Kanvas near-white, hairline border 1px, satu aksen{" "}
          <span className="text-electric-blue">electric blue</span>. Font Inter
          (body) + Geist Mono (
          <span className="font-mono text-[14px]">kode</span>).
        </p>
      </header>

      <section className="mb-8">
        <h2 className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-steel">
          Palet 6 vektor
        </h2>
        <div className="flex flex-wrap gap-2">
          {VECTOR_LABELS.map((label) => {
            const v = VECTOR_META[label];
            return (
              <Pill key={label} color={v.color}>
                {v.display}
              </Pill>
            );
          })}
        </div>
      </section>

      <section className="mb-8 grid gap-4 sm:grid-cols-2">
        <Card>
          <h3 className="mb-3 text-[14px] font-semibold text-charcoal">
            Tombol
          </h3>
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="primary">Primary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="outline" disabled>
              Disabled
            </Button>
          </div>
          <div className="mt-4 flex items-center gap-3">
            <Spinner />
            <span className="text-[14px] text-fog">Spinner + badge:</span>
            <Badge tone="mint">selesai</Badge>
            <Badge tone="neutral">netral</Badge>
          </div>
        </Card>

        <Card padded={false}>
          <div className="border-b border-ash p-4">
            <h3 className="text-[14px] font-semibold text-charcoal">
              Kartu (border, bukan shadow)
            </h3>
          </div>
          <div className="p-4 text-[14px] text-steel">
            Radius 12px, border{" "}
            <span className="font-mono text-[13px]">#e5e5e5</span>. Struktur dari
            border + spacing.
          </div>
        </Card>
      </section>

      <section>
        <h2 className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-steel">
          Empty state
        </h2>
        <EmptyState
          title="Belum ada data"
          description="Contoh empty state — dipakai saat monitoring.json belum tersedia. Tidak mengarang angka."
          action={<Button variant="outline">Aksi contoh</Button>}
        />
      </section>
    </main>
  );
}
