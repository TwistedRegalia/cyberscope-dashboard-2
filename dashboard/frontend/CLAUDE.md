# CLAUDE.md — Frontend Dashboard Monitoring Ancaman Siber

> **Cara pakai:** File ini dibaca otomatis oleh Claude Code saat bekerja di repo frontend.
> Letakkan di root workspace frontend (mis. `PI2/dashboard/frontend/CLAUDE.md`).
> **Sumber kebenaran** ada di tiga dokumen — baca bila butuh detail:
> - `HANDOFF_DASHBOARD.md` — lingkup, pipeline inference, kendala, integritas
> - `CONTEXT.md` — identitas riset, taksonomi E-ICTT, kerangka metodologi
> - `DESIGN.md` — sistem visual "Dub" + seluruh design token (WAJIB untuk styling)
>
> Bahasa kerja: **Indonesia**. Copy UI dalam Bahasa Indonesia; istilah teknis/kode boleh Inggris.

---

## 1. Apa yang dibangun (dan apa yang TIDAK)

Frontend **web monitoring dashboard** untuk skripsi S1 (peneliti: Ray). Sistem mengklasifikasikan **diskursus publik tentang vektor ancaman siber** di media sosial Indonesia (X + YouTube) — **BUKAN** deteksi serangan live, melainkan konten yang *membicarakan* ancaman (laporan korban, edukasi, promosi pelaku, diskusi netral).

Target pengguna: analis lembaga (BSSN/Bareskrim/OJK) + responden evaluasi semi-teknis (mahasiswa informatika, dosen).

**Lingkup FINAL — Tipe 1, dua kemampuan saja:**
1. **Monitoring** — visualisasi distribusi 6 vektor dari **prediksi model** atas dataset.
2. **Klasifikasi on-demand** — contoh siap-klik / tempel teks → hasil vektor + confidence, XAI opsional.

**DI LUAR LINGKUP — jangan bangun (keputusan final):**
- ❌ Tombol scraping / ambil data live (rapuh di HF Spaces, `auth_token` X kedaluwarsa)
- ❌ Upload CSV
- ❌ Penjadwal otomatis / batch periodik
- ❌ Visualisasi Speaker Role R1–R5 → **DITUNDA, bukan v1** (model tidak memprediksi role)
- ❌ Auth / akun pengguna, multi-tenant, i18n, dark mode — over-engineering, tak dibutuhkan v1

> Prinsip Ray: **no over-engineering.** Bangun dua halaman itu, tidak lebih. Kalau ragu apakah suatu fitur masuk lingkup, tanya dulu — jangan berasumsi menambah.

---

## 2. Tech stack & konvensi

| Aspek | Keputusan |
|---|---|
| Framework | **Next.js (App Router) + TypeScript** |
| Styling | **Tailwind CSS v4** — pakai blok `@theme` dari `DESIGN.md` (Quick Start → Tailwind v4) |
| Charts | **Recharts** (donut, bar, line). Styling manual ke token Dub. (Tremor boleh, tapi override warnanya) |
| Fonts | Inter (`next/font/google`), Geist Mono (`next/font/google` → `Geist_Mono`). Satoshi = display-only; jika lisensi/aset tak tersedia, pakai substitusi **Inter weight 500, letter-spacing -0.02em** (sesuai DESIGN.md) |
| Deploy | **Vercel** |
| State | React state (`useState`/`useReducer`). Tidak perlu state manager global untuk v1 |
| Env | `NEXT_PUBLIC_API_BASE_URL` → base URL backend FastAPI di HF Spaces |

**Konvensi kerja:**
- Commit Git per komponen selesai (checkpoint sebelum/sesudah perubahan besar).
- Sample-before-execute: sebelum transform data, inspeksi beberapa baris nyata dulu.
- Jangan fabrikasi data. File data hilang → tampilkan **empty state**, jangan karang angka.
- Ikuti `DESIGN.md` sebagai sumber kebenaran visual — jangan improvisasi warna/radius di luar kosakata token.

---

## 3. Struktur halaman

Dua route. Prinsip: **nilai terlihat saat dibuka**, respons cepat, hasil dapat dipahami pengguna non-harian.

### `/` — Monitoring (default saat buka)
Menampilkan gambaran dataset dari **PREDIKSI MODEL (Model A+B)** — **BUKAN label lemah Snorkel** (koheren dengan klaim "klasifikasi otomatis"). Data dibaca dari file statis pra-agregat (§5), **tidak** memanggil model saat halaman dibuka.

- **Kartu ringkas:** total baris, jumlah relevan, rentang tanggal.
- **Distribusi 6 vektor** (donut/bar) dari prediksi Model B.
- **Proporsi platform** per vektor (YouTube vs X) — stacked bar.
- **Tren waktu** (line) — **kondisional**, hanya jika kolom tanggal cukup tersebar dan bermakna. Jika tidak → sembunyikan panel, jangan paksa tampil.
- **Drill-down sederhana:** klik satu vektor → **panel expand** berisi contoh komentar terklasifikasi ke vektor itu (bukan halaman baru).

### `/klasifikasi` — Klasifikasi on-demand
- **Input fleksibel:** pengguna memilih **contoh teks siap-klik** ATAU **menempel teks sendiri** (hilangkan hambatan input).
- Klik → panggil backend → tampilkan **label vektor (dapat dibaca, bukan indeks)** + **confidence** (bar probabilitas 6 kelas).
- Jika Model A memutuskan **tidak relevan** → tampilkan status "tidak relevan", berhenti (jangan tampilkan vektor).
- **Tombol XAI opsional (LIME):** default **mati**, terpisah, klik saat perlu. **~30–60 dtk** → tampilkan **indikator progres**, **jangan blok UI**, beri peringatan bahwa proses lambat.

---

## 4. Enam label E-ICTT (kanonik)

Selalu pakai `label` kanonik untuk logika; `label_display` untuk tampilan. Jangan tambah/kurang label (label ke-7 `informasi_edukasi_siber` sudah DITOLAK — jangan munculkan).

| `label` (kanonik) | `label_display` (UI) |
|---|---|
| `phishing_rekayasa_sosial` | Phishing & Rekayasa Sosial |
| `penipuan_ewallet_qris` | Penipuan E-Wallet/QRIS |
| `malware_apk` | Malware APK |
| `judi_online_pinjol` | Judi Online & Pinjol |
| `peretasan_pencurian_identitas` | Peretasan & Pencurian Identitas |
| `deepfake_penipuan_ai` | Deepfake & Penipuan AI |

**Palet warna kategorikal (USULAN AWAL — Ray finalkan):** DESIGN.md melarang "banyak warna kromatik pada satu komponen", tapi **chart kategorikal adalah pengecualian** (tiap irisan = kategori data, bukan dekorasi). Titik awal dari token aksen Dub:

| Vektor | Warna | Token |
|---|---|---|
| phishing_rekayasa_sosial | `#2563eb` | electric-blue |
| judi_online_pinjol | `#ea580c` | tangerine |
| penipuan_ewallet_qris | `#16a34a` | vivid-green |
| peretasan_pencurian_identitas | `#7c3aed` | lavender |
| malware_apk | `#1e40af` | deep-sapphire |
| deepfake_penipuan_ai | `#737373` | fog (netral) |

Definisikan sekali sebagai konstanta `VECTOR_META` (label → {display, color}) dan pakai di semua chart + badge agar konsisten.

---

## 5. Kontrak data — Monitoring (file statis)

Monitoring **tidak** memanggil backend saat load (hindari cold-start HF Spaces + penuhi "nilai saat dibuka"). Sumbernya file pra-agregat yang dihasilkan **sekali** oleh batch inference Model A+B (langkah persiapan backend, HANDOFF §3.1/§8), lalu di-serve statis oleh frontend.

**File:** `public/data/monitoring.json` — bentuk yang di-*consume* frontend:

```jsonc
{
  "generated_at": "2026-07-13T00:00:00Z",
  "total_rows": 55300,
  "relevant_rows": 9212,                 // hasil Model A (Layer 1)
  "date_range": { "start": "2022-01", "end": "2026-06" } | null,
  "vector_distribution": [               // dari PREDIKSI Model B, bukan Snorkel
    { "label": "judi_online_pinjol", "label_display": "Judi Online & Pinjol", "count": 0, "pct": 0.0 }
  ],
  "platform_by_vector": [
    { "label": "judi_online_pinjol", "youtube_pct": 0.0, "x_pct": 0.0, "youtube_count": 0, "x_count": 0 }
  ],
  "temporal": [                          // null bila tanggal tak layak ditampilkan
    { "period": "2025-07", "label": "phishing_rekayasa_sosial", "count": 0 }
  ],
  "samples_by_vector": {                 // untuk drill-down; cap ~20–50 per vektor
    "judi_online_pinjol": [
      { "text": "…", "confidence": 0.96, "platform": "youtube", "date": "2025-07" }
    ]
  }
}
```

> **Integritas (WAJIB):** angka monitoring = **prediksi model**, jangan campur dengan distribusi label lemah Snorkel (angka Snorkel: judi 7.486 · ewallet 548 · phishing 492 · peretasan 365 · malware 214 · deepfake 107 — itu **bukan** yang ditampilkan monitoring). Bila `monitoring.json` belum ada, render empty state + instruksi bahwa batch inference perlu dijalankan dulu.

---

## 6. Kontrak API — Klasifikasi on-demand (backend FastAPI @ HF Spaces)

Base URL: `process.env.NEXT_PUBLIC_API_BASE_URL`. Backend memuat pipeline 2-lapis (Model A → Model B → late fusion 0,75:0,25). Detail model = urusan backend (HANDOFF §4–§7); frontend hanya konsumsi kontrak ini.

### `POST /classify`
```jsonc
// request
{ "text": "string" }

// response
{
  "relevant": true,                          // Model A (Layer 1)
  "label": "judi_online_pinjol" | null,      // null bila tidak relevan
  "label_display": "Judi Online & Pinjol",
  "confidence": 0.96,                         // 0..1
  "probabilities": {                          // 6 vektor (Layer 2), untuk bar chart
    "phishing_rekayasa_sosial": 0.02, "penipuan_ewallet_qris": 0.01,
    "malware_apk": 0.00, "judi_online_pinjol": 0.96,
    "peretasan_pencurian_identitas": 0.01, "deepfake_penipuan_ai": 0.00
  },
  "latency_ms": 1800
}
```
Target respons **< 3 dtk** (XAI dikecualikan). `relevant=false` → tampil "tidak relevan", jangan lanjut ke vektor.

### `POST /explain` — LIME (opsional, lambat)
```jsonc
// request
{ "text": "string", "num_samples": 120 }     // clamp 100..150

// response
{
  "label": "judi_online_pinjol",
  "tokens": [ { "token": "maxwin", "weight": 0.41 }, { "token": "kena", "weight": -0.08 } ],
  "num_samples": 120,
  "elapsed_ms": 42000
}
```
`weight` bertanda: positif = mendukung label, negatif = menentang. Render sebagai highlight token (intensitas ∝ |weight|). **Async, indikator progres, jangan blok UI.**

### `GET /health`
```jsonc
{ "status": "ok", "models_loaded": true, "model_a_f1": 0.968, "model_b_f1": 0.977 }
```
Boleh dipakai untuk badge status backend + memperingatkan cold-start.

> Backend belum dibangun (status: PERENCANAAN). Kontrak di atas adalah **kesepakatan** yang backend & frontend implementasikan bersama. Kalau backend memutuskan bentuk lain, **update kontrak ini dulu** sebelum coding, jangan diam-diam menyimpang.

---

## 7. Aturan non-fungsional (arah SUS tinggi)

- **Nilai tanpa input awal:** monitoring terisi begitu `/` dibuka (file statis, bukan fetch ke Space yang mungkin cold).
- **Respons cepat:** klasifikasi < 3 dtk; tampilkan skeleton/spinner saat menunggu.
- **Antarmuka jelas** untuk pengguna non-harian: navigasi eksplisit antar dua halaman, label & hasil mudah dibaca (bukan indeks kelas), confidence sebagai persentase + bar.
- **LIME jujur lambat:** tandai "±30–60 detik", progres terlihat, tidak menghalangi interaksi lain.
- **Accessibility dasar:** kontras teks ikut token (#171717 di atas putih), focus state jelas, jangan pakai warna sebagai satu-satunya pembawa makna (tambah label/ikon).

---

## 8. Sistem desain "Dub" — ringkas (detail: DESIGN.md)

Estetika: **light, editorial, near-white canvas** dipegang **hairline border 1px `#e5e5e5`** (bukan shadow), tipografi monokrom padat, **satu aksen electric blue `#2563eb`**. Padat & rapi: gap 8px, radius kartu 12px, tag pill 9999px, tombol ghost/outline ketimbang filled berat.

**Setup:** salin blok CSS custom properties + `@theme` Tailwind v4 dari DESIGN.md (Quick Start) ke `globals.css`. Jangan hardcode hex — pakai variabel token.

**Rujukan cepat:**
- Teks utama `#171717` · teks muted `#737373` · background `#ffffff` · surface alt `#f5f5f5` · border `#e5e5e5` · aksen `#2563eb` · primary action fill `#000000`
- Body 16px/1.5 (Inter 400) · data padat 14px · micro-label 11–12px · display 36–48px (Satoshi/Inter 500)
- Radius: tag/badge 9999px · tombol 8px · input 6px · kartu 12px · kartu besar 16px

**Do:**
- Border 1px `#e5e5e5` untuk semua kontainer; struktur dari border + spacing, **bukan** shadow.
- `#1e40af` (deep sapphire) / `#000000` fill = **satu** primary action per surface, hemat.
- Tint lembut (mint `#dcfce7`, biru `#dbeaff`) hanya untuk badge kecil / highlight, bukan surface besar.
- Kartu dashboard: putih, border 1px, radius 12px, tanpa shadow.

**Don't:**
- Jangan shadow berat untuk elevasi kartu.
- Jangan `#000000` untuk body text (pakai `#171717`/`#0a0a0a`).
- Jangan electric blue untuk fill background besar (itu highlight, bukan surface).
- Jangan Satoshi di ukuran body (display-only, 36px+).
- Jangan radius di luar kosakata (9999/16/12/8/6).

---

## 9. Definition of Done — v1

Frontend dianggap selesai bila:
1. `/` menampilkan distribusi 6 vektor, proporsi platform, tren waktu (jika layak), drill-down contoh per vektor — dari `monitoring.json`.
2. `/klasifikasi` menerima contoh siap-klik + teks tempel, memanggil `/classify`, menampilkan label + confidence + bar probabilitas, menangani kasus "tidak relevan".
3. Tombol LIME opsional memanggil `/explain`, render highlight token, dengan progres & non-blocking.
4. Empty/loading/error state tertangani (termasuk backend cold/gagal).
5. Semua styling memakai token Dub; lolos cek visual terhadap DESIGN.md.
6. Deploy ke Vercel, terhubung ke backend via `NEXT_PUBLIC_API_BASE_URL`.

---

## 10. Catatan integritas riset

- Monitoring = **prediksi model**, bukan weak label Snorkel (§5).
- Metrik & confidence harus dari sumber nyata; jangan hardcode angka karangan di UI.
- Late fusion **tidak** memperbaiki Layer 2 (dipertahankan untuk interpretabilitas); phishing F1 terendah (0,91) karena "scam umbrella" — bila menampilkan performa model, laporkan apa adanya.
- Checkpoint model (~470 MB ×2) **bukan** urusan repo frontend — itu di backend, di luar Git (HANDOFF §5).
- Speaker Role R1–R5 **bukan** v1. Jangan tampilkan seolah model memprediksinya.
- Bagian tesis **3.11 Deployment / 3.12 Pengembangan Prototype / 3.13 Evaluasi Prototype** ditulis **SETELAH** dashboard jadi — jangan tulis seolah sudah dikerjakan.
