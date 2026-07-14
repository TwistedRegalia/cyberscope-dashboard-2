"use client";

import { useState } from "react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { ClassifyInput } from "@/components/klasifikasi/ClassifyInput";
import { ExampleChips } from "@/components/klasifikasi/ExampleChips";
import { ResultPanel } from "@/components/klasifikasi/ResultPanel";
import { classify } from "@/lib/api";
import type { ClassifyResponse } from "@/lib/types";

type Status = "idle" | "loading" | "done" | "error";

export default function KlasifikasiPage() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<ClassifyResponse | null>(null);
  const [resultText, setResultText] = useState("");
  const [error, setError] = useState("");

  async function run(input?: string) {
    const t = (input ?? text).trim();
    if (!t) return;
    setStatus("loading");
    setError("");
    setResult(null);
    try {
      const r = await classify(t);
      setResult(r);
      setResultText(t);
      setStatus("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Terjadi kesalahan tak terduga");
      setStatus("error");
    }
  }

  function pick(exampleText: string) {
    setText(exampleText);
    void run(exampleText);
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Klasifikasi on-demand"
        subtitle="Tempel teks atau pilih contoh siap-klik untuk mendapatkan vektor + tingkat keyakinan."
      />

      <Card>
        <p className="mb-2 text-[12px] font-medium uppercase tracking-wide text-steel">
          Contoh siap-klik
        </p>
        <ExampleChips onPick={pick} disabled={status === "loading"} />
        <div className="mt-4">
          <ClassifyInput
            value={text}
            onChange={setText}
            onSubmit={() => void run()}
            loading={status === "loading"}
          />
        </div>
      </Card>

      {status === "loading" && <Skeleton className="h-44" />}

      {status === "error" && (
        <Card>
          <p className="text-[14px] text-charcoal">
            Gagal memproses klasifikasi: {error}. Silakan coba lagi.
          </p>
        </Card>
      )}

      {status === "done" && result && (
        <ResultPanel result={result} inputText={resultText} />
      )}
    </div>
  );
}
