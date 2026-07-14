/**
 * MOCK LIME — stand-in selama backend belum ada. Memberi bobot token:
 * positif (mendukung label) untuk kata kunci vektor terprediksi, negatif
 * (menentang) untuk kata kunci vektor lain, ~0 untuk sisanya. Bentuk sama
 * dengan ExplainResponse kontrak §6. BUKAN LIME nyata.
 */
import type { ExplainResponse, ExplainToken } from "@/lib/types";
import { VECTOR_LABELS, type VectorLabel } from "@/lib/vectors";
import { KEYWORDS } from "./classify";

function matches(keywords: string[], word: string): boolean {
  return keywords.some((k) => {
    const kk = k.trim();
    return kk === word || (kk.length > 3 && word.includes(kk));
  });
}

export function mockExplain(
  text: string,
  label: VectorLabel,
  numSamples: number,
): ExplainResponse {
  const words = text.toLowerCase().match(/[a-z0-9-]+/g) ?? [];
  const labelKw = KEYWORDS[label];
  const otherKw = VECTOR_LABELS.filter((l) => l !== label).flatMap(
    (l) => KEYWORDS[l],
  );

  const seen = new Set<string>();
  const tokens: ExplainToken[] = [];
  for (const w of words) {
    if (w.length < 2 || seen.has(w)) continue;
    seen.add(w);

    let weight: number;
    if (matches(labelKw, w)) {
      weight = 0.2 + Math.random() * 0.3; // mendukung label
    } else if (matches(otherKw, w)) {
      weight = -(0.03 + Math.random() * 0.12); // menentang label
    } else {
      weight = (Math.random() - 0.5) * 0.06; // dekat nol
    }
    tokens.push({ token: w, weight: Number(weight.toFixed(3)) });
  }

  tokens.sort((a, b) => Math.abs(b.weight) - Math.abs(a.weight));

  return {
    label,
    tokens: tokens.slice(0, 12),
    num_samples: numSamples,
    elapsed_ms: 30000 + Math.floor(Math.random() * 25000), // kosmetik (LIME nyata lambat)
  };
}
