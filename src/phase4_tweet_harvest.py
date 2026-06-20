#!/usr/bin/env python3
"""
Phase 4 — Tweet Harvest Query Runner (real CLI: `npx tweet-harvest@latest`)

Runs targeted X/Twitter queries per vector and saves raw results in the NATIVE
Tweet Harvest CSV schema (identik dengan file sesi*.csv lama), supaya bisa
dikonsumsi langsung oleh src/phase5_consolidate_additional.py.

PENTING — tool yang benar:
- Tweet Harvest adalah CLI berbasis Node.js + Chromium (Helmi Satria), BUKAN paket pip.
  Dijalankan via: `npx tweet-harvest@latest ...`
- Autentikasi memakai Twitter **auth_token cookie** (dari sesi browser yang sudah login),
  BUKAN developer bearer token.
- Flag CLI yang valid (v2.7.1):
    -s/--search-keyword, -t/--token, -l/--limit, -o/--output-filename,
    --tab {TOP,LATEST}, -e/--export-format {csv,xlsx}, -f/--from, --to, -d/--delay
- Output ditulis ke folder `tweets-data/<output-filename>` (relatif ke cwd),
  lalu script ini memindahkannya ke raw_additional_tweets/{vektor}/q{idx}.csv

Prerequisites:
- Node.js + npx (cek: `npx --version`)
- TWITTER_AUTH_TOKEN env var = nilai cookie `auth_token` dari akun X yang sudah login.
  Cara ambil: login x.com di browser → DevTools (F12) → Application → Cookies →
  https://x.com → salin value cookie bernama `auth_token`.
  GUNAKAN AKUN SEKUNDER (mitigasi risiko rate-limit / suspend).
- data/query_spec.json — query specification per vektor (sudah ada).

Snapshot caveat (Temuan #1): Tweet Harvest praktis mengembalikan snapshot tweet
terbaru (mengabaikan rentang tanggal historis). Karena itu --from/--to TIDAK dipakai
secara default. Posisikan data X sebagai cross-sectional OSINT snapshot, bukan rentang
multi-tahun.

Eksekusi:
    setx TWITTER_AUTH_TOKEN "xxxx"   # (sekali; buka shell baru) atau set di sesi:
    $env:TWITTER_AUTH_TOKEN="xxxx"   # PowerShell
    python src/phase4_tweet_harvest.py

Output:
    raw_additional_tweets/{vektor}/q{idx}.csv  (native Tweet Harvest schema)
    raw_additional_tweets/_summary.json
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime

# npx launcher: di Windows binary-nya npx.cmd (bukan 'npx' executable polos)
NPX = "npx.cmd" if os.name == "nt" else "npx"
TWEET_HARVEST_PKG = "tweet-harvest@latest"
# Tweet Harvest selalu menulis ke folder ini relatif terhadap cwd
HARVEST_OUTPUT_DIR = Path("tweets-data")


def load_query_spec(spec_path):
    """Load query specification from JSON."""
    with open(spec_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_tweet_harvest(query, vektor, query_idx, dest_csv, token,
                      limit=500, tab="LATEST", delay=3):
    """
    Execute a single Tweet Harvest query via the real Node CLI.
    Tweet Harvest writes tweets-data/<out_name>; we move it to dest_csv.
    Returns (success: bool, count: int, error: str or None)
    """
    out_name = f"{vektor}__q{query_idx}.csv"
    produced = HARVEST_OUTPUT_DIR / out_name

    # Bersihkan sisa file lama dengan nama sama (hindari hitung baris basi)
    if produced.exists():
        produced.unlink()

    cmd = [
        NPX, "--yes", TWEET_HARVEST_PKG,
        "--search-keyword", query,
        "--limit", str(limit),
        "--output-filename", out_name,
        "--tab", tab,
        "--export-format", "csv",
        "--delay", str(delay),
    ]
    if token:
        cmd += ["--token", token]

    query_preview = query[:70] + "..." if len(query) > 70 else query
    print(f"[{vektor}:q{query_idx}] tweet-harvest -s \"{query_preview}\" "
          f"-l {limit} --tab {tab}", file=sys.stderr)

    try:
        # timeout besar: run pertama mengunduh Chromium (Playwright) ~150MB
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout (>1200s)", file=sys.stderr)
        return (False, 0, "Timeout")
    except FileNotFoundError:
        print(f"  ✗ npx not found; install Node.js (https://nodejs.org)", file=sys.stderr)
        return (False, 0, "npx/node not installed")

    if produced.exists():
        dest_csv.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(produced), str(dest_csv))
        # hitung baris data (kurangi header)
        count = 0
        with open(dest_csv, "r", encoding="utf-8") as f:
            count = max(0, sum(1 for _ in f) - 1)
        print(f"  ✓ {count} tweets → {dest_csv}", file=sys.stderr)
        return (True, count, None)

    # Tidak ada file output
    err = (result.stderr or result.stdout or "").strip()
    if result.returncode == 0:
        print(f"  ⚠ 0 tweets (tidak ada hasil untuk query ini)", file=sys.stderr)
        return (True, 0, None)
    print(f"  ✗ Error (rc={result.returncode}): {err[:200]}", file=sys.stderr)
    return (False, 0, err or f"returncode={result.returncode}")


def parse_args():
    ap = argparse.ArgumentParser(
        description="Phase 4 Tweet Harvest runner — bisa per-vektor (monitor kesehatan akun)."
    )
    ap.add_argument("--vektor",
                    help="Jalankan HANYA 1 vektor (nama persis di query_spec.json). "
                         "Default: semua vektor.")
    ap.add_argument("-q", "--query", type=int, default=None,
                    help="Jalankan HANYA 1 query index (1-based) dalam vektor terpilih. "
                         "Berguna untuk uji 1 query dulu sebelum membakar kuota akun.")
    ap.add_argument("--limit", type=int, default=None,
                    help="Override limit per query (default: dari spec).")
    ap.add_argument("--tab", choices=["TOP", "LATEST"], default=None,
                    help="Override tab pencarian (default: dari spec / LATEST).")
    ap.add_argument("--list", action="store_true",
                    help="Tampilkan daftar vektor + jumlah query, lalu keluar (tak butuh token).")
    return ap.parse_args()


def main():
    args = parse_args()

    spec_path = Path("data/query_spec.json")
    if not spec_path.exists():
        print(f"ERROR: {spec_path} not found", file=sys.stderr)
        sys.exit(1)
    spec = load_query_spec(spec_path)

    # --list: cukup tampilkan vektor, tanpa perlu token / npx
    if args.list:
        print("Vektor tersedia di query_spec.json:", file=sys.stderr)
        for v, c in spec.items():
            print(f"  - {v}: {len(c.get('queries', []))} queries "
                  f"(limit={c.get('limit', 500)}, tab={c.get('tab', 'LATEST')})",
                  file=sys.stderr)
        print("\nContoh jalankan 1 vektor:\n  python src/phase4_tweet_harvest.py "
              "--vektor penipuan_ewallet_qris", file=sys.stderr)
        return

    # Token wajib via env (CLI akan prompt interaktif jika kosong → bisa hang)
    token = os.getenv("TWITTER_AUTH_TOKEN") or os.getenv("TWITTER_BEARER_TOKEN")
    if not token:
        print("ERROR: TWITTER_AUTH_TOKEN env var belum di-set.", file=sys.stderr)
        print("  Set value cookie `auth_token` dari sesi browser X yang sudah login.",
              file=sys.stderr)
        print("  PowerShell:  $env:TWITTER_AUTH_TOKEN=\"xxxx\"", file=sys.stderr)
        sys.exit(1)
    if os.getenv("TWITTER_BEARER_TOKEN") and not os.getenv("TWITTER_AUTH_TOKEN"):
        print("  ⚠ Memakai TWITTER_BEARER_TOKEN sebagai auth_token. Catatan: Tweet "
              "Harvest butuh cookie auth_token, BUKAN developer bearer token.",
              file=sys.stderr)

    # Cek npx tersedia
    if shutil.which(NPX) is None and shutil.which("npx") is None:
        print(f"ERROR: npx tidak ditemukan. Install Node.js dari https://nodejs.org",
              file=sys.stderr)
        sys.exit(1)

    # Filter ke 1 vektor jika diminta
    if args.vektor:
        if args.vektor not in spec:
            print(f"ERROR: vektor '{args.vektor}' tidak ada di spec. "
                  f"Pilihan: {', '.join(spec)}", file=sys.stderr)
            sys.exit(1)
        spec = {args.vektor: spec[args.vektor]}

    print(f"[Phase 4] Menjalankan {len(spec)} vektor: {', '.join(spec)}", file=sys.stderr)
    if args.query is not None:
        print(f"           (hanya query index {args.query})", file=sys.stderr)

    output_dir = Path("raw_additional_tweets")
    output_dir.mkdir(exist_ok=True)

    stats = {"total_vectors": 0, "total_queries": 0, "total_tweets": 0,
             "failed_queries": [], "empty_queries": []}

    for vektor, config in spec.items():
        queries = config.get("queries", [])
        limit = args.limit or config.get("limit", 500)
        tab = args.tab or config.get("tab", "LATEST")
        delay = config.get("delay", 3)

        vektor_dir = output_dir / vektor
        vektor_dir.mkdir(exist_ok=True)

        print(f"\n[{vektor}] {len(queries)} queries, limit={limit}, tab={tab}",
              file=sys.stderr)
        stats["total_vectors"] += 1

        for query_idx, query in enumerate(queries, 1):
            if args.query is not None and query_idx != args.query:
                continue

            csv_output = vektor_dir / f"q{query_idx}.csv"

            success, count, error = run_tweet_harvest(
                query, vektor, query_idx, csv_output, token, limit, tab, delay
            )
            stats["total_queries"] += 1

            if success and count > 0:
                stats["total_tweets"] += count
            elif success and count == 0:
                stats["empty_queries"].append((vektor, query_idx))
            else:
                stats["failed_queries"].append((vektor, query_idx, error))

            # Throttle antar-query (rate-limit mitigation)
            time.sleep(2)

    # Summary
    print(f"\n[Phase 4 Summary]", file=sys.stderr)
    print(f"  Vectors: {stats['total_vectors']}", file=sys.stderr)
    print(f"  Queries executed: {stats['total_queries']}", file=sys.stderr)
    print(f"  Total tweets: {stats['total_tweets']}", file=sys.stderr)
    print(f"  Empty queries: {len(stats['empty_queries'])}", file=sys.stderr)
    print(f"  Failed queries: {len(stats['failed_queries'])}", file=sys.stderr)
    print(f"  Output: {output_dir}/", file=sys.stderr)

    if stats["failed_queries"]:
        print(f"\nFailed queries:", file=sys.stderr)
        for vektor, idx, err in stats["failed_queries"]:
            print(f"  - {vektor}:q{idx}: {str(err)[:100]}", file=sys.stderr)

    # Summary per-vektor agar run terpisah tidak saling menimpa
    suffix = f"_{args.vektor}" if args.vektor else ""
    summary_file = output_dir / f"_summary{suffix}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "executed_at": datetime.utcnow().isoformat(),
            "tool": "npx tweet-harvest@latest (Node/Chromium)",
            "spec_file": str(spec_path),
            "vektor_filter": args.vektor,
            "query_filter": args.query,
            **stats
        }, f, indent=2, ensure_ascii=False)
    print(f"  Summary: {summary_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
