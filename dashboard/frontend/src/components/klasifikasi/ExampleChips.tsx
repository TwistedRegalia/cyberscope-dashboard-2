"use client";

import { useRef } from "react";
import { CLASSIFY_EXAMPLES, type ClassifyExamplePool } from "@/lib/examples";
import { VECTOR_META } from "@/lib/vectors";

interface Props {
  onPick: (text: string) => void;
  disabled?: boolean;
}

/** Contoh siap-klik per vektor (+ satu off-topic untuk uji "tidak relevan"). */
export function ExampleChips({ onPick, disabled }: Props) {
  // Penghitung siklus per chip. useRef, bukan useState: indeks tak memengaruhi
  // tampilan sehingga tak boleh memicu re-render deretan chip.
  const nextIndex = useRef<Record<string, number>>({});

  /** Contoh ditampilkan bergantian berurutan: 1 -> 2 -> 3 -> 4 -> 5 -> 1. */
  function handlePick(ex: ClassifyExamplePool) {
    const i = nextIndex.current[ex.hint] ?? 0;
    nextIndex.current[ex.hint] = (i + 1) % ex.texts.length;
    onPick(ex.texts[i]);
  }

  return (
    <div className="flex flex-wrap gap-2">
      {CLASSIFY_EXAMPLES.map((ex) => {
        const color = ex.label ? VECTOR_META[ex.label].color : undefined;
        return (
          <button
            key={ex.hint}
            type="button"
            disabled={disabled}
            onClick={() => handlePick(ex)}
            className="inline-flex items-center gap-2 rounded-full border border-ash bg-canvas-white px-3 py-1.5 text-[13px] text-charcoal transition-colors hover:bg-paper-mist focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-electric-blue disabled:opacity-50"
          >
            {color ? (
              <span
                aria-hidden
                className="size-2 rounded-full"
                style={{ backgroundColor: color }}
              />
            ) : (
              <span
                aria-hidden
                className="size-2 rounded-full border border-smoke"
              />
            )}
            {ex.hint}
          </button>
        );
      })}
    </div>
  );
}
