# CLAUDE.md - Backend FastAPI Dashboard CyberScope

> **Cara pakai:** File ini dibaca otomatis oleh Claude Code saat bekerja di `PI2/dashboard/backend/`.
> Ini adalah **kickoff** membangun backend FastAPI untuk dashboard "CyberScope" (skripsi S1, peneliti: Ray).
> Frontend SUDAH selesai dan menunggu backend yang memenuhi **kontrak di dokumen ini**.
>
> **Sumber kebenaran** (baca bila butuh detail, semua di repo yang sama `PI2/`):
> - `docs/HANDOFF_DASHBOARD.md` - lingkup, pipeline, kendala, integritas (paling otoritatif).
> - `docs/HANDOFF_FRONTEND.md` - kontrak API + skema `monitoring.json` yang di-consume frontend.
> - `CONTEXT.md` - identitas riset, taksonomi E-ICTT.
> - `docs/phase9_xai_lime.md` - metodologi LIME. `docs/phase9_fusion_ablation.md` - ablation fusion.
>
> Bahasa kerja: **Indonesia**. Istilah teknis/kode boleh Inggris.

---

## 1. Apa yang dibangun (dan apa yang TIDAK)

Backend punya **dua keluaran**, keduanya memakai pipeline inferensi yang sama:

1. **Layanan FastAPI** (3 endpoint) untuk halaman `/klasifikasi` frontend: `POST /classify`,
   `POST /explain` (LIME), `GET /health`.
2. **Script batch** yang menghasilkan `monitoring.json` untuk halaman `/` frontend (dibuat SEKALI,
   bukan endpoint runtime).

**DI LUAR LINGKUP - jangan lakukan:**
- Jangan **melatih ulang** model. Checkpoint sudah ada (`models/`), tinggal dimuat & di-inferensi.
- Jangan scraping / ambil data live, jangan upload CSV, jangan penjadwal batch otomatis.
- Jangan tambah **label ke-7** (`informasi_edukasi_siber` sudah ditolak).
- Jangan kembalikan **Speaker Role R1-R5** (Model A/B tidak memprediksinya; ditunda, bukan v1).
- Jangan "optimize" bobot fusion ke test set (0.75:0.25 adalah a priori).

> Prinsip Ray: **no over-engineering.** Bangun 3 endpoint + 1 script batch. Kalau ragu suatu hal masuk
> lingkup, tanya dulu.

---

## 2. Arsitektur pipeline 2-lapis (inference-time, TIDAK melatih ulang)

```
teks mentah (user paste / baris dataset)
  -> clean_text() -> text_clean            (preprocessing WAJIB, lihat §4)
  -> Model A (Layer 1: relevan / tidak_relevan)   [+ has_anchor -> fusion L1]
       -> jika TIDAK relevan: STOP  (respons relevant=false, label=null)
  -> Model B (Layer 2: 6 vektor) softmax          [+ anchor_share -> fusion L2]
  -> skor(v) = 0.75 * P_B(v) + 0.25 * anchor_share(v)
  -> label = argmax(skor) ; confidence = probabilitas kelas terpilih
```

- **Layer 1** = gerbang relevansi. Fusion menaikkan recall relevan (0.9674 -> 0.9761); anchor = jaring pengaman.
- **Layer 2** = 6 vektor. Fusion di L2 dipertahankan untuk interpretabilitas (neural dominan).
- Anchor dihitung atas **`text_clean`** (instance identik dengan input neural), bukan teks mentah.

---

## 3. Enam label E-ICTT (kanonik) + urutan indeks WAJIB

Pakai string `label` kanonik ini persis (kunci `probabilities`, field `label`, kolom monitoring).
`label_display` = teks tampilan.

| id | `label` (kanonik) | `label_display` |
|---:|---|---|
| 0 | `phishing_rekayasa_sosial` | Phishing & Rekayasa Sosial |
| 1 | `penipuan_ewallet_qris` | Penipuan E-Wallet/QRIS |
| 2 | `malware_apk` | Malware APK |
| 3 | `judi_online_pinjol` | Judi Online & Pinjol |
| 4 | `peretasan_pencurian_identitas` | Peretasan & Pencurian Identitas |
| 5 | `deepfake_penipuan_ai` | Deepfake & Penipuan AI |

> **PENTING:** urutan indeks di atas = `LABEL2ID` Model B (`src/phase9_model_b_layer2.py`). Output
> classifier index-i HARUS dipetakan ke label via `ID2LABEL[i]`. Salah urutan = semua prediksi kacau.
> Model A: `LABEL2ID = {tidak_relevan:0, relevan:1}`.

---

## 4. Peta reuse - pakai ulang dari `src/` (JANGAN tulis ulang model)

Semua ada di `PI2/src/`. Backend di subdirektori repo yang sama, jadi bisa impor langsung.

| Kebutuhan | File | Fungsi/objek |
|---|---|---|
| Kelas Model A | `src/phase9_model_a_layer1.py` | `make_model_class()` -> `TripleHybridLayer1`, `LABEL2ID`, `ID2LABEL` |
| Kelas Model B | `src/phase9_model_b_layer2.py` | `make_model_class()` -> `TripleHybridLayer2`, `LABEL2ID`, `ID2LABEL`, `N_CLASSES`, `BERT_NAME` |
| Preprocessing | `src/phase6_preprocess.py` | `clean_text(raw) -> text_clean` (lihat catatan bawah) |
| Anchor rule-based | `src/anchor_patterns.py` | `detect_vector_hints(text) -> {vec:count}`, `has_anchor(text) -> bool` |
| Rumus fusion | `src/phase9_late_fusion.py` | referensi (arsip CLI); rumusnya cukup 3 baris, re-implement di `pipeline.py` |

**Arsitektur (identik kedua model):** `IndoBERT-base-p1` (fine-tune penuh) -> `BiGRU(768->256, bidir)`
-> `BiLSTM(512->128, bidir)` serial -> masked-mean pool -> dropout -> `Linear`. Tokenizer
`indobenchmark/indobert-base-p1`, **`max_len=128`**.

**Muat checkpoint - checkpoint = `state_dict`, BUKAN objek model:**
```python
import torch
from src.phase9_model_b_layer2 import make_model_class  # + sys.path repo-root, lihat §8

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # HF Spaces = cpu
model_b = make_model_class()()                       # instansiasi (mengunduh IndoBERT utk arsitektur)
model_b.load_state_dict(torch.load("models/model_b_layer2_best.pt", map_location=device))
model_b.eval().to(device)
# JANGAN torch.load(model) langsung -> yang tersimpan hanya bobot.
```

**Preprocessing (`clean_text`):** model dilatih atas kolom `text_clean`. Untuk inference LIVE (user
paste teks mentah), terapkan `clean_text` dulu. Isi `clean_text` ringkas: lowercase; URL -> `[URL]`;
`@user` -> `[USER]`; hashtag -> teks (`#` dilepas); emoji emosi -> `[EMOSI_SEDIH/MARAH/UANG/TAKUT/WASPADA]`,
emoji dekoratif dibuang; TIDAK buang stopword, TIDAK stemming, slang cybercrime dipertahankan.
> Catatan dependency: `src/phase6_preprocess.py` meng-`import Sastrawi` di puncak modul (untuk stemming
> yang TIDAK dipakai inference). Agar Space ramping, **salin fungsi `clean_text()` + `EMOJI_TAG` +
> regex URL/MENTION/HASHTAG** ke `backend/preprocessing.py` (butuh lib `emoji` saja), dan jaga
> **byte-identik** dengan sumbernya. (Alternatif: `pip install Sastrawi` lalu impor langsung.)

**Fusion (re-implement 3 baris di `pipeline.py`, dari `phase9_late_fusion.py`):**
```python
# Layer 2 (6 vektor):
def anchor_share(text_clean):                 # {vec: [0,1]} share bukti anchor
    hints = detect_vector_hints(text_clean)   # {vec: count} hanya yg match
    total = sum(hints.values())
    scores = {v: 0.0 for v in LABEL2ID}
    if total: 
        for v, c in hints.items(): scores[v] = c / total
    return scores                             # semua 0 -> defer ke neural

fused = {v: 0.75 * p_b[v] + 0.25 * anchor_share(tc)[v] for v in LABEL2ID}
# Normalisasi jadi distribusi (agar sum=1 & konsisten dgn bar chart frontend):
s = sum(fused.values()) or 1.0
probabilities = {v: fused[v] / s for v in fused}
label = max(probabilities, key=probabilities.get)
confidence = probabilities[label]
# Sifat berguna: bila anchor semua 0, probabilities == softmax neural (0.75/0.75).

# Layer 1 (relevansi): anchor2 = [0,1] bila has_anchor(tc) else [0,0]
fused_l1 = 0.75 * softmax2 + 0.25 * anchor2   # softmax2 = [p_tidak, p_relevan]
relevant = int(fused_l1.argmax()) == 1
```

---

## 5. Kontrak API - WAJIB dipenuhi (dari `docs/HANDOFF_FRONTEND.md` §4)

Frontend memanggil lewat `NEXT_PUBLIC_API_BASE_URL`. Bentuk respons di bawah **mengikat** (dipetakan ke
`dashboard/frontend/src/lib/types.ts`). `VectorLabel` = 6 string kanonik §3.

### `POST /classify`
```jsonc
// request
{ "text": "string" }
// response
{
  "relevant": true,                          // Model A (Layer 1)
  "label": "judi_online_pinjol",             // VectorLabel | null (null bila tidak relevan)
  "label_display": "Judi Online & Pinjol",   // string | null
  "confidence": 0.91,                        // 0..1 (prob kelas terpilih, pasca-fusion)
  "probabilities": {                         // Record<VectorLabel, number>, WAJIB 6 kunci, 0..1
    "phishing_rekayasa_sosial": 0.02, "penipuan_ewallet_qris": 0.01, "malware_apk": 0.00,
    "judi_online_pinjol": 0.91, "peretasan_pencurian_identitas": 0.03, "deepfake_penipuan_ai": 0.03
  },
  "latency_ms": 1234
}
```
- **`relevant=false`** -> `label=null`, `label_display=null`, `probabilities` boleh 0 semua. Frontend
  berhenti (tampil "tidak relevan").
- Target respons **< 3 dtk** (di luar LIME). `probabilities` harus memuat keenam kunci.

### `POST /explain` - LIME (opsional, lambat)
```jsonc
// request
{ "text": "string", "num_samples": 120 }     // frontend clamp 100..150
// response
{
  "label": "judi_online_pinjol",             // VectorLabel (kelas yang dijelaskan)
  "tokens": [ { "token": "maxwin", "weight": 0.41 }, { "token": "kena", "weight": -0.08 } ],
  "num_samples": 120,
  "elapsed_ms": 42000
}
```
- `weight` bertanda: `+` mendukung label, `-` menentang. Frontend highlight token (intensitas ~ |weight|).
- Hanya dipanggil untuk teks **relevan**. Lambat by design (~30-60 dtk CPU) - frontend sudah non-blocking.

### `GET /health`
```jsonc
{ "status": "ok", "models_loaded": true, "model_a_f1": 0.968, "model_b_f1": 0.977 }
```
- Dipakai badge status backend + membangunkan Space (frontend ping saat `/klasifikasi` dibuka).
- Nilai F1 dari **sanity check nyata** (§10), bukan tebakan. Buat murah (return flag; jangan inferensi berat).

---

## 6. Batch inference -> `monitoring.json` (halaman `/`)

Halaman Monitoring membaca **file statis** `dashboard/frontend/public/data/monitoring.json` (bukan
endpoint). Dihasilkan SEKALI oleh script batch. Skema (dari `docs/HANDOFF_FRONTEND.md` §5):

```jsonc
{
  "is_sample": false,                         // HAPUS/false utk data nyata (true -> banner "DATA CONTOH")
  "generated_at": "2026-07-15T00:00:00Z",
  "total_rows": 55300,
  "relevant_rows": 9212,                      // hasil prediksi Model A
  "date_range": { "start": "2022-01", "end": "2026-06" }, // atau null
  "vector_distribution": [ { "label": "...", "label_display": "...", "count": 0, "pct": 0.0 } ], // 6 item
  "platform_by_vector":  [ { "label": "...", "youtube_pct": 0.0, "x_pct": 0.0, "youtube_count": 0, "x_count": 0 } ],
  "temporal": [ { "period": "2025-06", "label": "...", "count": 0 } ], // null bila <3 periode berbeda
  "samples_by_vector": { "judi_online_pinjol": [ { "text": "...", "confidence": 0.96, "platform": "youtube", "date": "2025-05" } ] }
}
```

**Langkah script** (`scripts/build_monitoring.py`):
1. Baca `data/weak_labeled_dataset_v2.csv` (55.300 baris). Kolom berguna: `text_clean` (SUDAH
   dipreproses -> pakai langsung untuk batch, tak perlu `clean_text` lagi), `platform`, `published_at`,
   `text` (mentah, untuk `samples_by_vector`).
2. **Model A** atas semua 55.300 (`text_clean`) -> prediksi relevan/tidak. `relevant_rows` = jumlah
   prediksi relevan; `total_rows` = 55.300.
3. **Model B + fusion** (§4) atas baris **prediksi relevan** -> label vektor + confidence per baris.
4. Agregasi:
   - `vector_distribution`: `count` per vektor; `pct = count / relevant_rows`.
   - `platform_by_vector`: dari kolom `platform` (inspeksi nilainya, **normalisasi ke `youtube`/`x`**),
     `youtube_count`/`x_count` + `youtube_pct`/`x_pct` per vektor.
   - `temporal`: dari `published_at` -> `YYYY-MM`, `count` per `(period, label)`. Set **null** bila <3
     periode berbeda (frontend menyembunyikan panel bila <3).
   - `samples_by_vector`: ~20-50 per vektor dari kolom **`text` mentah** (bukan `text_clean`), sertakan
     `confidence`, `platform` (`youtube`/`x`), `date` (`YYYY-MM`|null). Pilih confidence tertinggi / beragam.
5. Tulis ke `dashboard/frontend/public/data/monitoring.json` (indent 2, `ensure_ascii=False`, tanpa
   `is_sample`). Commit + push -> Vercel auto-deploy (drop-in, HANDOFF_FRONTEND §5.1).

> **INTEGRITAS (WAJIB):** angka monitoring = **prediksi Model A+B**, BUKAN kolom `layer2_label`/`layer1_label`
> (itu label lemah Snorkel). Distribusi Snorkel (judi 7.486, ewallet 548, phishing 492, peretasan 365,
> malware 214, deepfake 107) **tidak boleh** dipakai. `relevant_rows` juga = prediksi Model A (boleh
> berbeda dari 9.212 Snorkel; itu justru koheren dengan klaim "klasifikasi otomatis").

---

## 7. LIME (`/explain`) - jelaskan neural Model B

Referensi metodologi: `docs/phase9_xai_lime.md`. LIME menjelaskan komponen **neural Model B** (level kata).

```python
from lime.lime_text import LimeTextExplainer
CLASS_NAMES = [ID2LABEL[i] for i in range(6)]
explainer = LimeTextExplainer(class_names=CLASS_NAMES)

def predict_proba(texts):                 # List[str] -> np.ndarray (N,6)
    cleaned = [clean_text(t) for t in texts]   # LIME memberi teks terganggu; model butuh bersih
    return model_b_softmax(cleaned)            # softmax Model B, urutan LABEL2ID

# Jelaskan pada text_clean agar token selaras dgn input model:
tc = clean_text(user_text)
exp = explainer.explain_instance(tc, predict_proba, num_labels=1,
                                 labels=(pred_id,), num_samples=clamp(num_samples,100,150))
tokens = [{"token": w, "weight": round(wt, 3)} for w, wt in exp.as_list(label=pred_id)]
```
`num_samples` clamp 100-150 (CPU). `label` respons = kelas terpilih. Urutkan token by |weight| bila perlu.

---

## 8. Struktur backend + dependencies (disarankan)

```
dashboard/backend/
  app/
    main.py            # FastAPI, CORS, 3 endpoint, startup: muat model sekali
    pipeline.py        # load_models(), classify(text), explain(text,n), sanity_f1()
    schemas.py         # pydantic: ClassifyResponse, ExplainResponse, HealthResponse
  preprocessing.py     # clean_text() disalin dari src/phase6 (byte-identik)
  scripts/
    build_monitoring.py
  requirements.txt
  Dockerfile           # HF Spaces (atau app_file + README config)
  README.md            # sumber checkpoint, cara jalan
```

**`requirements.txt`:** `torch`, `transformers>=4.30`, `emoji`, `lime`, `scikit-learn`, `pandas`,
`numpy`, `fastapi`, `uvicorn[standard]`.

**Impor dari `src/`:** tambahkan repo-root ke `sys.path` di awal (mis.
`sys.path.insert(0, str(Path(__file__).resolve().parents[2]))`) lalu `from src.phase9_model_b_layer2
import ...`. Impor **hanya leaf yang ringan**: kelas model (butuh numpy/pandas/torch/transformers) &
`anchor_patterns` (hanya `re`). JANGAN impor `phase9_late_fusion` (arsip CLI) - salin rumusnya. Untuk
Space **self-contained**, boleh vendor (`anchor_patterns.py` + 2 file kelas model + `clean_text`) ke
`backend/`; bila vendor, catat asal dan jaga sinkron.

**Muat model SEKALI** saat startup (FastAPI startup event / import `pipeline`), simpan flag
`models_loaded`. Jangan muat per-request.

---

## 9. Deploy HF Spaces (CPU)

- **Sumber daya:** CPU basic; ~3 GB RAM saat kedua model dimuat (muat A dan B). Inference ~1-3 dtk/teks.
- **Checkpoint di luar Git** (`models/*.pt`, ~506 MB each). Untuk Space: unggah ke **HF model repo**
  privat lalu `huggingface_hub.hf_hub_download(...)` saat startup (Space git tetap ramping). IndoBERT
  base juga terunduh saat `from_pretrained` (butuh internet Space; menambah cold start).
- **Cold start:** muat model + unduh IndoBERT bisa ~30-60 dtk. Frontend SUDAH menangani (badge
  `BackendStatus` ping `/health` saat load + timeout classify 30s/explain 120s). Buat `/health` murah.
- **CORS (WAJIB):** izinkan origin frontend. `CORSMiddleware(allow_origins=[<domain-Vercel>,
  "http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])`. Tanpa ini, browser blokir.
- Endpoint & body **persis** §5. Bentuk mock referensi di `dashboard/frontend/src/lib/mock/{classify,explain}.ts`.

---

## 10. Sanity check WAJIB sebelum serve

Setelah muat checkpoint, evaluasi test split dan cocokkan dengan target. Bila meleset jauh: cek nama
atribut layer (`bert`/`bigru`/`bilstm`/`classifier`), urutan `LABEL2ID`, `max_len=128`. Jangan lanjut.

| Model | Split | Target |
|---|---|---|
| A (Layer 1) | `data/splits/layer1_test.csv` | macro-F1 ~ **0.968** (recall relevan ~0.967) |
| B (Layer 2) | `data/splits/layer2_test.csv` | macro-F1 ~ **0.977** |

Reuse `build_dataset()` + `evaluate()` yang sudah ada di kedua file model untuk sanity cepat. Nilai
terukur ini yang dipakai di `/health` (`model_a_f1`, `model_b_f1`).

---

## 11. Integritas & larangan (jangan dilanggar)

- Monitoring = **prediksi model**, bukan label Snorkel (§6). Jangan hardcode angka karangan.
- Metrik `/health` dari sanity check nyata (§10), bukan tebakan.
- 6 label saja; jangan label ke-7; jangan Speaker Role R1-R5.
- Fusion **0.75:0.25 a priori** - jangan tuning ke test set (lihat `docs/phase9_fusion_ablation.md`).
- Checkpoint tetap **di luar Git** (`models/` sudah di-gitignore). Dokumentasikan sumbernya di README.
- Bagian tesis 3.11 Deployment / 3.12 Pengembangan / 3.13 Evaluasi ditulis SETELAH backend live.

---

## 12. Definition of Done

1. `POST /classify` menjalankan pipeline A -> gate -> B -> fusion, mengembalikan bentuk §5 (termasuk
   kasus `relevant=false`), < 3 dtk.
2. `POST /explain` mengembalikan token LIME bertanda untuk teks relevan (num_samples clamp 100-150).
3. `GET /health` mengembalikan `models_loaded` + F1 sanity nyata.
4. Sanity F1 A~0.968 / B~0.977 lolos.
5. `scripts/build_monitoring.py` menghasilkan `monitoring.json` nyata (prediksi model) dan ditaruh di
   `dashboard/frontend/public/data/` tanpa `is_sample`.
6. Deploy ke HF Spaces; CORS mengizinkan origin Vercel + localhost; terhubung dari frontend dengan
   `NEXT_PUBLIC_API_BASE_URL=<url-space>` dan `NEXT_PUBLIC_USE_MOCK=false`.
