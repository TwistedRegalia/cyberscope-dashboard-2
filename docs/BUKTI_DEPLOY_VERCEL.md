# Deployment Vercel

## Perintah deployment

```bash
cd dashboard/frontend
vercel whoami
vercel --prod --yes
```

| | |
|---|---|
| ID | `dpl_DKvqaEXoXe2jZHYn9EvEnipxYx3L` |
| Waktu | 31 Juli 2026, 20:06:46 WIB |
| Status | Ready, target production |
| Build | 23 detik, Node 24.x |
| Domain | `https://cyberscope-webapp.vercel.app` |
| Akun | `twistedregalia` (tim `ray-siraj`) |
| Vercel CLI | 56.2.0 |

## Untuk di-screenshot

Dari `dashboard/frontend`, semuanya read-only:

```bash
vercel ls                                     # riwayat deployment, status Ready
vercel inspect cyberscope-webapp.vercel.app   # ID, stempel waktu, alias
vercel env ls production                      # nama env var, nilai tampil "Encrypted"
vercel project ls
vercel whoami
```

`vercel ls` paling layak jadi gambar utama — memperlihatkan deployment 15 Juli dan 31 Juli sekaligus.

Jangan menjalankan ulang `vercel --prod` demi screenshot; itu membuat deployment baru, bukan menampilkan yang lama.

Caption: **Gambar 3.x** Riwayat Deployment Frontend pada Vercel · **Gambar 3.y** Rincian Deployment Produksi CyberScope

Kalimat sisipan untuk §3.11:

> Deployment frontend dilakukan menggunakan Vercel CLI dari direktori proyek frontend. Hasil dan riwayatnya dapat ditelusuri melalui perintah `vercel ls` dan `vercel inspect` sebagaimana ditunjukkan pada Gambar 3.x dan Gambar 3.y.

## Koreksi §3.11 — tier backend

§3.11 menyebut "tier gratis" dua kali. Untuk backend itu keliru:

```
hardware : cpu-upgrade      (berbayar)
sleep    : 1800 detik
```

Frontend Vercel memang gratis, backend tidak. Usulan:

> Backend di-deploy pada Hugging Face Spaces menggunakan SDK Gradio dengan hardware CPU Upgrade, sedangkan frontend di-deploy pada Vercel tier gratis. Sebagai kendali biaya, backend dikonfigurasi tidur otomatis setelah 30 menit tanpa aktivitas.

Klaim cold start 25–60 detik tetap sah, justru auto-sleep itulah penyebabnya.
