import type { VectorLabel } from "./vectors";

export type Platform = "youtube" | "x";

/* ============ Monitoring (kontrak file statis, CLAUDE.md §5) ============ */

export interface VectorDistributionItem {
  label: VectorLabel;
  label_display: string;
  count: number;
  pct: number; // 0..1
}

export interface PlatformByVectorItem {
  label: VectorLabel;
  youtube_pct: number; // 0..1
  x_pct: number; // 0..1
  youtube_count: number;
  x_count: number;
}

export interface TemporalItem {
  period: string; // "2025-07"
  label: VectorLabel;
  count: number;
}

export interface SampleItem {
  text: string;
  confidence: number; // 0..1
  platform: Platform;
  date: string | null; // "2025-07" | null
}

export interface MonitoringData {
  generated_at: string;
  total_rows: number;
  relevant_rows: number; // hasil Model A (Layer 1)
  date_range: { start: string; end: string } | null;
  vector_distribution: VectorDistributionItem[]; // dari PREDIKSI Model B
  platform_by_vector: PlatformByVectorItem[];
  temporal: TemporalItem[] | null; // null bila tanggal tak layak
  samples_by_vector: Partial<Record<VectorLabel, SampleItem[]>>;
  /** true = fixture dev (bukan hasil model) → tampilkan banner "DATA CONTOH". */
  is_sample?: boolean;
}

/* ============ Klasifikasi on-demand (kontrak API, CLAUDE.md §6) ============ */

export interface ClassifyResponse {
  relevant: boolean; // Model A (Layer 1)
  label: VectorLabel | null; // null bila tidak relevan
  label_display: string | null;
  confidence: number; // 0..1
  probabilities: Record<VectorLabel, number>; // 6 vektor (Layer 2)
  latency_ms: number;
}

export interface ExplainToken {
  token: string;
  weight: number; // + mendukung label, - menentang
}

export interface ExplainResponse {
  label: VectorLabel;
  tokens: ExplainToken[];
  num_samples: number;
  elapsed_ms: number;
}

export interface HealthResponse {
  status: string;
  models_loaded: boolean;
  model_a_f1: number;
  model_b_f1: number;
}
