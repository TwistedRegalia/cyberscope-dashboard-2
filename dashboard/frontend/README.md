# Frontend — Dashboard Monitoring Ancaman Siber

Frontend web dashboard untuk skripsi: **monitoring** distribusi 6 vektor ancaman siber (prediksi
model atas dataset) + **klasifikasi on-demand** (teks → vektor + confidence, XAI LIME opsional).

Panduan lengkap: `CLAUDE.md` (repo ini) · sistem visual: `../../docs/DESIGN.md` (Dub) · lingkup &
riset: `../../docs/HANDOFF_DASHBOARD.md`, `../../CONTEXT.md`.

## Stack

Next.js 16 (App Router) · TypeScript · Tailwind v4 (token Dub) · Recharts · deploy Vercel.

## Menjalankan

```bash
npm install
cp .env.local.example .env.local   # sesuaikan bila backend sudah ada
npm run dev                         # http://localhost:3000
```

- `npm run build` — build produksi · `npm run start` — serve hasil build · `npm run lint` — ESLint.

## Mode data (mock ↔ nyata)

Semua akses data lewat satu lapisan `src/lib/api.ts`.

- **Monitoring** membaca file statis `public/data/monitoring.json`. File saat ini adalah **fixture
  dev** ber-flag `is_sample` (muncul banner "DATA CONTOH"). Ganti dengan output **batch inference
  Model A+B** untuk data nyata (hapus `is_sample`). Bila file hilang → empty state, bukan angka karangan.
- **Klasifikasi & LIME** memakai **mock heuristik** selama `NEXT_PUBLIC_API_BASE_URL` kosong (banner
  "Mode demo"). Untuk model nyata: set `NEXT_PUBLIC_API_BASE_URL` ke backend FastAPI dan
  `NEXT_PUBLIC_USE_MOCK=false`. Kontrak API di `CLAUDE.md` §6 (`/classify`, `/explain`, `/health`).

> Integritas: angka monitoring = prediksi model (bukan label lemah Snorkel); hasil klasifikasi mock
> BUKAN model nyata. Kedua hal ditandai eksplisit di UI.

## Struktur

```
src/
├── app/                  # / (Monitoring) · /klasifikasi · layout + globals (token Dub)
├── components/
│   ├── layout/           # AppShell, NavBar, PageHeader
│   ├── ui/               # primitif Dub (Card, Button, Pill, Badge, EmptyState, Spinner, Skeleton)
│   ├── monitoring/       # SummaryCards, VectorDistribution, PlatformStacked, TemporalLine, Drilldown
│   └── klasifikasi/      # ClassifyInput, ExampleChips, ProbabilityBars, ResultPanel, LimePanel
└── lib/                  # api (satu lapisan), types (kontrak), vectors (VECTOR_META), format, mock/
public/data/monitoring.json   # fixture dev (ganti dg output batch inference)
```

## Deploy (Vercel)

Import repo → root project `dashboard/frontend` → set env `NEXT_PUBLIC_API_BASE_URL` (+ `NEXT_PUBLIC_USE_MOCK=false`)
bila backend siap. Tanpa env, dashboard berjalan dalam mode mock + fixture.
