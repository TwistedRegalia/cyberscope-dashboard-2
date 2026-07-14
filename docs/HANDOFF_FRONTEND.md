# HANDOFF — Frontend "CyberScope" → Sesi Backend FastAPI

> Dokumen **self-contained** untuk memulai pengerjaan **backend FastAPI**. Frontend sudah selesai
> (mode mock) dan menunggu backend yang memenuhi **kontrak di dokumen ini**. Kamu **tidak perlu**
> membuka repo frontend — semua kontrak (API + data) di-inline di sini.
>
> Bahasa kerja: **Indonesia**. Sumber lain (opsional): `docs/HANDOFF_DASHBOARD.md`, `CONTEXT.md`,
> `dashboard/frontend/CLAUDE.md` §5–§6.

---

## 1. Ringkasan & status

**Proyek:** Dashboard klasifikasi & monitoring **diskursus vektor ancaman siber** di media sosial
Indonesia (X + YouTube). Skripsi S1 (Ray). **BUKAN** deteksi serangan live — konten yang *membicarakan*
ancaman. Taksonomi **E-ICTT (6 vektor)**.

**Frontend "CyberScope" — SELESAI** (branch `feat/dashboard-frontend`), berjalan **mode mock**
(backend belum ada). Dua halaman:
- **`/` Monitoring** — baca file statis `public/data/monitoring.json` (pra-agregat, TIDAK memanggil
  backend saat load). Kartu ringkas + distribusi 6 vektor (bar horizontal) + proporsi platform
  (100%-stacked) + tren waktu (kondisional) + drill-down contoh per vektor.
- **`/klasifikasi` Klasifikasi on-demand** — input teks / contoh siap-klik → `POST /classify` →
  label + confidence + bar 6 kelas; kasus "tidak relevan"; tombol **LIME** opsional → `POST /explain`.

Fitur: **dark mode** (toggle navbar). Stack: **Next.js 16 (App Router) + TypeScript + Tailwind v4 +
Recharts**, deploy target **Vercel**.

**Commit utama:** `622f246` M1 scaffold+token · `44c33ca` M2 shell/nav · `afa9044` M3 Monitoring ·
`3a224c6` M4 Klasifikasi · `953bde8` M5 LIME · `cd47148` M6 polish · `abcbc3f` rebrand CyberScope ·
`6e0055c` dark mode.

**Status backend:** `dashboard/backend/` **kosong** — belum dikerjakan. Itu tugas sesi ini.

---

## 2. Arsitektur data (PENTING — dua jalur berbeda)

| Kebutuhan frontend | Sumber | Peran backend |
|---|---|---|
| **Monitoring** (halaman `/`) | file **statis** `public/data/monitoring.json` | dihasilkan **sekali** via **batch inference** (script), lalu ditaruh di `public/data/`. **Bukan** endpoint runtime. |
| **Klasifikasi + LIME** (halaman `/klasifikasi`) | **API live** ke backend | endpoint `POST /classify`, `POST /explain`, `GET /health`. |

> Jadi backend punya **2 keluaran**: (a) **layanan FastAPI** (3 endpoint), dan (b) **script batch**
> yang menghasilkan `monitoring.json`. Keduanya memakai pipeline inferensi yang sama.

Frontend memilih mock vs nyata lewat env (lihat §6). Monitoring memakai mock/fixture bila
`monitoring.json` ber-flag `is_sample:true` (banner "DATA CONTOH" muncul).

---

## 3. Enam label kanonik (E-ICTT)

Backend **WAJIB** memakai string `label` kanonik ini persis (untuk kunci `probabilities`, field
`label`, dan kolom monitoring). `label_display` = teks tampilan (boleh dikirim balik agar konsisten).

| `label` (kanonik) | `label_display` |
|---|---|
| `phishing_rekayasa_sosial` | Phishing & Rekayasa Sosial |
| `penipuan_ewallet_qris` | Penipuan E-Wallet/QRIS |
| `malware_apk` | Malware APK |
| `judi_online_pinjol` | Judi Online & Pinjol |
| `peretasan_pencurian_identitas` | Peretasan & Pencurian Identitas |
| `deepfake_penipuan_ai` | Deepfake & Penipuan AI |

Tidak ada label ke-7 (`informasi_edukasi_siber` DITOLAK). Speaker Role R1–R5 **bukan** bagian v1 —
jangan dikembalikan. (Warna kategori = urusan frontend, backend tak perlu mengirim warna.)

---

## 4. Kontrak API — WAJIB dipenuhi backend

Base URL = `NEXT_PUBLIC_API_BASE_URL` (frontend). Tipe di bawah = TypeScript yang di-consume frontend
(`src/lib/types.ts`) — treat sebagai **skema respons yang mengikat**.

```ts
type VectorLabel =
  | "phishing_rekayasa_sosial" | "penipuan_ewallet_qris" | "malware_apk"
  | "judi_online_pinjol" | "peretasan_pencurian_identitas" | "deepfake_penipuan_ai";
```

### 4.1 `POST /classify`
```jsonc
// request
{ "text": "string" }

// response (ClassifyResponse)
{
  "relevant": true,                          // Model A (Layer 1)
  "label": "judi_online_pinjol",             // VectorLabel | null (null bila tidak relevan)
  "label_display": "Judi Online & Pinjol",   // string | null
  "confidence": 0.96,                         // 0..1 (prob kelas terpilih)
  "probabilities": {                          // Record<VectorLabel, number>, 6 kunci, 0..1
    "phishing_rekayasa_sosial": 0.02, "penipuan_ewallet_qris": 0.01,
    "malware_apk": 0.00, "judi_online_pinjol": 0.96,
    "peretasan_pencurian_identitas": 0.01, "deepfake_penipuan_ai": 0.00
  },
  "latency_ms": 1800
}
```
- **`relevant=false`** → `label=null`, `label_display=null` (frontend berhenti, tampil "tidak relevan",
  TIDAK menampilkan vektor). `probabilities` boleh 0 semua.
- Target respons **< 3 dtk** (di luar LIME).
- `probabilities` **harus** memuat keenam kunci VectorLabel (frontend mengurut & membuat bar dari sini).

### 4.2 `POST /explain` — LIME (opsional, lambat)
```jsonc
// request
{ "text": "string", "num_samples": 120 }     // frontend clamp 100..150

// response (ExplainResponse)
{
  "label": "judi_online_pinjol",              // VectorLabel
  "tokens": [                                  // ExplainToken[]
    { "token": "maxwin", "weight": 0.41 },     // weight bertanda: + mendukung, - menentang label
    { "token": "kena",   "weight": -0.08 }
  ],
  "num_samples": 120,
  "elapsed_ms": 42000
}
```
- Frontend meng-highlight token (intensitas ∝ |weight|, hijau=+ / merah=−) dan menampilkan angka.
- **Lambat by design** (backend CPU ~30–60 dtk). Frontend sudah non-blocking + indikator progres.
- Frontend hanya memanggil `/explain` untuk teks yang **relevan** (punya `label`).

### 4.3 `GET /health`
```jsonc
{ "status": "ok", "models_loaded": true, "model_a_f1": 0.968, "model_b_f1": 0.977 }
```
Dipakai untuk badge status / peringatan cold-start (opsional di UI).

---

## 5. Kontrak data Monitoring — `monitoring.json`

Dihasilkan backend via **batch inference SEKALI** atas dataset relevan, lalu file ditaruh di
`dashboard/frontend/public/data/monitoring.json` (hapus `is_sample` untuk data nyata). Skema yang
di-consume frontend:

```jsonc
{
  "is_sample": false,                          // hapus/false untuk data NYATA (true → banner "DATA CONTOH")
  "generated_at": "2026-07-14T00:00:00Z",
  "total_rows": 55300,
  "relevant_rows": 9212,                       // hasil Model A (Layer 1)
  "date_range": { "start": "2022-01", "end": "2026-06" }, // atau null
  "vector_distribution": [                      // dari PREDIKSI Model B (bukan Snorkel)
    { "label": "judi_online_pinjol", "label_display": "Judi Online & Pinjol", "count": 6800, "pct": 0.7382 }
    // ... 6 item (satu per vektor)
  ],
  "platform_by_vector": [
    { "label": "judi_online_pinjol", "youtube_pct": 0.97, "x_pct": 0.03, "youtube_count": 6600, "x_count": 200 }
    // ... 6 item
  ],
  "temporal": [                                 // null bila tanggal tak layak (<3 periode berbeda → frontend sembunyikan)
    { "period": "2025-06", "label": "judi_online_pinjol", "count": 1260 }
  ],
  "samples_by_vector": {                        // drill-down; cap ~20–50 per vektor
    "judi_online_pinjol": [
      { "text": "…", "confidence": 0.96, "platform": "youtube", "date": "2025-05" }  // platform: "youtube"|"x", date: "YYYY-MM"|null
    ]
  }
}
```

> **ATURAN INTEGRITAS (WAJIB):** angka monitoring = **prediksi Model A+B**, **BUKAN** label lemah
> Snorkel. Angka Snorkel (judi 7.486 · ewallet 548 · phishing 492 · peretasan 365 · malware 214 ·
> deepfake 107) **tidak boleh** dipakai sebagai isi monitoring. `pct` = `count / relevant_rows`.

---

## 6. Integrasi frontend ↔ backend

- Frontend beralih mock→nyata via **env** (tanpa ubah komponen):
  `NEXT_PUBLIC_API_BASE_URL=<url-backend>` dan `NEXT_PUBLIC_USE_MOCK=false`.
  (Default: mock aktif bila API base kosong.)
- **CORS:** backend WAJIB mengizinkan origin frontend (domain Vercel + `http://localhost:3000` saat dev).
- Endpoint & body **persis** §4 (`POST /classify {text}`, `POST /explain {text,num_samples}`,
  `GET /health`). Bentuk mock ada di `dashboard/frontend/src/lib/mock/{classify,explain}.ts` sebagai
  **referensi perilaku** (heuristik kata kunci — ganti dengan model nyata).
- Frontend memanggil API lewat satu lapisan `src/lib/api.ts` — tak ada asumsi lain di komponen.

---

## 7. Bahan backend yang SUDAH ADA di repo

Semua ada di repo yang sama (`PI2/`) — backend tinggal memakai ulang, **jangan latih ulang**:

- **Checkpoint** (`models/`, di-**gitignore**, ~483MB masing-masing):
  `model_a_layer1_best.pt`, `model_b_layer2_best.pt`. **= `state_dict`, BUKAN objek model.**
  ```python
  model = make_model_class()()                 # dari src/phase9_model_a_layer1.py / _b_layer2.py
  model.load_state_dict(torch.load(path, map_location=device)); model.eval()
  ```
  Sanity check setelah load: test macro-F1 **A≈0,968** (recall relevan ≈0,967) / **B≈0,977**.
- **Arsitektur (Triple-Hybrid):** `IndoBERT-base-p1` (fine-tune penuh) → BiGRU(768→256 bidir) →
  BiLSTM(512→128 bidir) serial → masked-mean pool → dropout → Linear. Kelas: `TripleHybridLayer1`
  (2 kelas) / `TripleHybridLayer2` (6 kelas).
- **Preprocessing WAJIB direplikasi** (`src/phase6_preprocess.py`) — input model = kolom `text_clean`:
  lowercase · URL→`[URL]` · `@user`→`[USER]` · hashtag→teks · emoji emosi→`[EMOSI_*]` · slang
  cybercrime DIPERTAHANKAN (pinjol/gacor/maxwin/qris) · TIDAK buang stopword · TIDAK stemming.
  Tokenizer `indobenchmark/indobert-base-p1`, **`max_len=128`**.
- **Rule-based / anchor** (`src/anchor_patterns.py`, `detect_vector_hints(text)`) + **late fusion
  0,75 neural : 0,25 rule** (`src/phase9_late_fusion.py`). Pipeline:
  ```
  text → text_clean → Model A (relevan?) → [tidak → STOP] → Model B (6 vektor) + anchor
       → skor = 0,75·P_neural + 0,25·anchor → label + confidence
  ```
  Catatan: fusion **fungsional di L1** (recall relevan +0,87pp), **interpretabilitas di L2** (neural dominan).
- **LIME** menjelaskan komponen **neural Model B** (level-kata, `num_samples` 100–150 di CPU).
  Referensi metodologi: `docs/phase9_xai_lime.md`.
- **Data untuk batch monitoring:** `data/weak_labeled_dataset_v2.csv` (55.300 baris, **9.212 relevan**),
  `data/splits/`. Jalankan Model A+B atas baris relevan → agregasi ke skema §5.
- **Kendala (untuk keputusan deploy):** CPU ~1–3 dtk/teks (A+B), **~3 GB RAM** saat kedua model dimuat,
  LIME lambat (turunkan num_samples). Target deploy: **HF Spaces** (CPU).

---

## 8. Sisa pekerjaan (peta besar)

1. **Backend FastAPI** (sesi ini) — 3 endpoint §4 + script batch → `monitoring.json` §5.
2. **Deploy** — backend ke HF Spaces; frontend ke Vercel; set env §6; pastikan CORS.
3. **Ganti fixture** — taruh `monitoring.json` nyata (hapus `is_sample`) di `public/data/`.
4. **Tesis 3.11 Deployment / 3.12 Pengembangan Prototype / 3.13 Evaluasi Prototype** — ditulis
   **SETELAH** dashboard live. **SUS**: 5–20 responden semi-teknis (mahasiswa informatika/dosen) —
   bottleneck non-teknis, amankan lebih awal.

---

## 9. Larangan / integritas (jangan dilanggar)

- Monitoring = **prediksi model**, bukan Snorkel (§5). Jangan hardcode angka karangan.
- Metrik `/health` harus dari sanity check nyata (0,968 / 0,977), bukan tebakan.
- Jangan tambah label ke-7; jangan kembalikan Speaker Role R1–R5.
- Late fusion bobot **0,75:0,25 a priori** (jangan "optimize" ke test set — lihat HANDOFF §10/ablation).
- Checkpoint tetap **di luar Git** (`models/` sudah di-gitignore).
