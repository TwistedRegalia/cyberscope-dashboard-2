"use client";

import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading?: boolean;
}

export function ClassifyInput({ value, onChange, onSubmit, loading }: Props) {
  return (
    <div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={4}
        placeholder="Tempel teks komentar atau tweet di sini…"
        aria-label="Teks untuk diklasifikasi"
        className="w-full resize-y rounded-md border border-midnight-ink bg-canvas-white px-3 py-2 text-[15px] text-charcoal placeholder:text-fog focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-electric-blue"
      />
      <div className="mt-3 flex items-center gap-3">
        <Button
          variant="primary"
          onClick={onSubmit}
          disabled={loading || value.trim() === ""}
        >
          {loading ? (
            <>
              <Spinner label="Memproses" /> Memproses…
            </>
          ) : (
            "Klasifikasikan"
          )}
        </Button>
        <Button
          variant="ghost"
          onClick={() => onChange("")}
          disabled={loading || value === ""}
        >
          Bersihkan
        </Button>
      </div>
    </div>
  );
}
