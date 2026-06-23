#!/usr/bin/env python3
"""
Phase 4 — Single-vector wrapper (alias posisional untuk --vektor)

Wrapper TIPIS di atas src/phase4_tweet_harvest.py supaya bisa dijalankan per-vektor
dengan argumen posisional (sesuai docs/06_Phase3-4_Execution_Checkpoint.md):

    python src/phase4_tweet_harvest_single_vector.py <vektor> [query_idx]

Contoh:
    python src/phase4_tweet_harvest_single_vector.py penipuan_ewallet_qris
    python src/phase4_tweet_harvest_single_vector.py malware_apk 1   # hanya query #1

Ekuivalen dengan:
    python src/phase4_tweet_harvest.py --vektor <vektor> [--query <idx>]

TIDAK ada logika scraping di sini — semuanya didelegasikan ke
phase4_tweet_harvest.main() agar hanya ada SATU sumber kebenaran (no duplication).
Token & dependency sama: butuh TWITTER_AUTH_TOKEN + npx (lihat script utama).
"""

import sys

import phase4_tweet_harvest as p4


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: python src/phase4_tweet_harvest_single_vector.py <vektor> [query_idx]",
              file=sys.stderr)
        print("\nDaftar vektor tersedia:", file=sys.stderr)
        sys.argv = ["phase4_tweet_harvest.py", "--list"]
        p4.main()
        return

    forwarded = ["phase4_tweet_harvest.py", "--vektor", args[0]]
    if len(args) >= 2:
        forwarded += ["--query", args[1]]

    # Delegasikan ke entry point utama (parse_args membaca sys.argv ini)
    sys.argv = forwarded
    p4.main()


if __name__ == "__main__":
    main()
