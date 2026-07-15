---
title: CyberScope Backend
emoji: 🛡️
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.20.0
app_file: space_app.py
---

# CyberScope Backend

Backend FastAPI untuk dashboard CyberScope (skripsi S1, Ray) - klasifikasi otomatis diskursus vektor
ancaman siber di media sosial Indonesia. Detail spek lengkap: `CLAUDE.md` di direktori ini.

## Endpoint

- `POST /classify` - `{text}` -> pipeline Model A (relevansi) -> Model B (6 vektor) -> fusion 0,75
  neural : 0,25 rule-based -> label + confidence + probabilitas 6 kelas.
- `POST /explain` - `{text, num_samples}` -> LIME atas komponen neural murni Model B (num_samples
  clamp 100-150), ~10-60 detik.
- `GET /health` - status + `models_loaded` + F1 sanity nyata (`model_a_f1=0.9686`,
  `model_b_f1=0.9747`, hasil `scripts/sanity_check.py`, M0 - bukan tebakan).

## Sumber checkpoint

`models/model_a_layer1_best.pt` dan `models/model_b_layer2_best.pt` (~484MB masing-masing, dihasilkan
training Kaggle T4, Phase 9) **tidak ada di Git** (`.gitignore`). Untuk deploy HF Spaces, checkpoint
diunggah ke HF model repo privat terpisah dan diunduh saat startup lewat `hf_hub_download` (lihat
`app/pipeline.py:_resolve_checkpoint`). Untuk dev lokal, taruh kedua file itu langsung di `models/`
relatif ke root repo (`PI2/models/`) - tak perlu env var apa pun, dipakai duluan sebelum fallback HF.

## Setup lokal

```
pip install -r requirements.txt
python scripts/sanity_check.py          # wajib lolos dulu (target macro-F1 A~0.968, B~0.977)
uvicorn app.main:app --host 0.0.0.0 --port 8000   # dari direktori dashboard/backend/
```

## Deploy ke HF Spaces (checklist lengkap)

SDK **Gradio** (gratis) dipakai, bukan Docker - Docker SDK kini butuh HF Spaces Pro ($9/bulan) dan
tak bisa dipakai gratis lagi (berubah awal Juli 2026). `space_app.py` menjalankan FastAPI asli
(`app/main.py`, tak diubah - endpoint/CORS/lifespan identik dev lokal) langsung lewat `uvicorn` di
port 7860, dengan UI Gradio minimal ter-mount di `/ui` (cuma jaring pengaman kompatibilitas SDK, bukan
antarmuka fungsional - rute API asli tetap di path aslinya).

Repo Space **terpisah** dari monorepo `PI2/` - hanya berisi subset file yang benar-benar dipakai saat
runtime (bukan seluruh `src/`, bukan `data/`, bukan `models/`).

1. **Login CLI** (sekali, interaktif): `hf auth login`.
2. **Buat model repo privat** untuk checkpoint: `hf repo create <nama-model-repo> --type model
   --private`.
3. **Upload checkpoint** (dari root `PI2/`):
   ```
   hf upload <nama-model-repo> models/model_a_layer1_best.pt model_a_layer1_best.pt
   hf upload <nama-model-repo> models/model_b_layer2_best.pt model_b_layer2_best.pt
   ```
4. **Buat Space** (SDK Gradio): via web `huggingface.co/new-space`, atau
   `hf repo create <nama-space> --type space --space_sdk gradio`.
5. **Susun folder terpisah** untuk push ke Space (struktur relatif HARUS persis ini, supaya
   `Path(__file__).resolve().parents[3]` di `pipeline.py` tetap menunjuk ke root yang benar):
   ```
   <folder-space>/
     requirements.txt                    <- WAJIB di ROOT (bukan nested) - HF Spaces cuma
                                             auto-install requirements.txt yang ada di root repo,
                                             disalin dari dashboard/backend/requirements.txt.
                                             Nested-only pernah bikin Space RUNTIME_ERROR (ModuleNotFoundError)
                                             karena torch/transformers/emoji/dll tak ke-install sama sekali.
     space_app.py                        <- salin dari dashboard/backend/space_app.py
     README.md                           <- salin file ini (sudah ada YAML frontmatter)
     src/
       phase9_model_a_layer1.py          <- salin dari PI2/src/
       phase9_model_b_layer2.py          <- salin dari PI2/src/
       phase6_preprocess.py              <- salin dari PI2/src/
       anchor_patterns.py                <- salin dari PI2/src/
     dashboard/
       backend/
         requirements.txt                <- salin juga di sini (opsional, konsisten dgn lokal;
                                             yang di root di atas yang benar-benar dipakai HF Spaces)
         app/
           main.py                       <- salin dari dashboard/backend/app/
           pipeline.py                   <- salin dari dashboard/backend/app/
           schemas.py                    <- salin dari dashboard/backend/app/
   ```
   Ini "vendoring" yang disengaja (CLAUDE.md Sec 8) - Space jadi self-contained, tak butuh akses ke
   `src/` versi lengkap monorepo (yang punya banyak script training/labeling tak relevan utk
   inference).
6. **Push ke Space.** `hf auth login --token <token>` (tanpa `--add-to-git-credential`) TIDAK
   memberi `git` sendiri kredensial - `git push` polos akan gagal "Authentication failed". Dua opsi:
   - **Opsi A (dipakai, tak sentuh git credential store):** `huggingface_hub.HfApi().upload_folder(
     folder_path="<folder-space>", repo_id="<username>/<nama-space>", repo_type="space")` - pakai
     token yang sama dari `hf auth login`, tanpa git sama sekali.
   - **Opsi B (git manual):** `git init && git remote add space https://<token>@huggingface.co/spaces/
     <username>/<nama-space> && git add . && git commit -m "Deploy" && git push space main` - token
     ada di URL remote, cuma di repo folder deploy lokal (bukan git credential store global).
7. **Set Variable + Secret** (Settings -> Variables and secrets di web UI, atau via
   `HfApi().add_space_variable(repo_id, "HF_MODEL_REPO", "<nama-model-repo>")` +
   `HfApi().add_space_secret(repo_id, "HF_TOKEN", "<token>")`):
   - Variable `HF_MODEL_REPO` = `<nama-model-repo>` dari langkah 2.
   - Secret `HF_TOKEN` = token HF (perlu akses baca ke model repo privat).
8. **Verifikasi**: `curl https://<username>-<nama-space>.hf.space/health` harus mengembalikan
   `models_loaded: true` setelah cold start (~30-60 detik, unduh checkpoint + IndoBERT base).

## CORS + connect frontend (langkah terakhir, terpisah dari deploy Space)

`app/main.py` saat ini mengizinkan `http://localhost:3000` + placeholder TODO. Begitu frontend live di
Vercel (di luar lingkup backend ini) dan ada domain asli:
1. Update `allow_origins` di `app/main.py` (ganti baris placeholder TODO dengan domain Vercel asli).
2. Di Vercel, set env var `NEXT_PUBLIC_API_BASE_URL=https://<username>-<nama-space>.hf.space` dan
   `NEXT_PUBLIC_USE_MOCK=false`.
