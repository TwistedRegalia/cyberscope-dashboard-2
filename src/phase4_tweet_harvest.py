#!/usr/bin/env python3
"""
Phase 4 — Tweet Harvest Query Executor
Runs targeted X/Twitter queries per vector and saves raw results.

This script executes queries from a query spec (JSON) via Tweet Harvest CLI.
Tweet Harvest tool: https://github.com/elyra-ai/tweet_harvest

Prerequisites:
- tweet_harvest installed: pip install tweet-harvest
- X/Twitter API credentials (Bearer token) or auth via Tweet Harvest
- query_spec.json in data/ with structure:
  {
    "vektor_name": {
      "queries": ["query1", "query2", ...],
      "limit": 500,
      "lang": "id"
    }
  }

Output: raw_additional_tweets/{vektor}/{query_idx}.jsonl (or .csv)
        with columns: tweet_id, author, text, created_at, likes, retweets, lang

Note: Tweet Harvest v2.7.1 outputs .jsonl by default; convert to CSV for phase5_consolidate.py
"""

import os
import sys
import json
import subprocess
import csv
from pathlib import Path
from datetime import datetime


def load_query_spec(spec_path):
    """Load query specification from JSON."""
    with open(spec_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_tweet_harvest(query, vektor, query_idx, output_file, lang="id", limit=500):
    """
    Execute a single Tweet Harvest query.
    Returns (success: bool, count: int, error: str or None)
    """
    cmd = [
        "tweet-harvest",
        "--query", query,
        "--output", str(output_file),
        "--limit", str(limit),
        "--lang", lang,
        "--format", "jsonl"  # Tweet Harvest default
    ]

    # Optional: add credentials if in environment
    if os.getenv("TWITTER_BEARER_TOKEN"):
        os.environ["BEARER_TOKEN"] = os.getenv("TWITTER_BEARER_TOKEN")

    print(f"[{vektor}:q{query_idx}] Running: {' '.join(cmd)}", file=sys.stderr)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            # Count lines in output file (each line = 1 tweet)
            count = 0
            if output_file.exists():
                with open(output_file, "r", encoding="utf-8") as f:
                    count = sum(1 for _ in f)
            print(f"  ✓ Scraped {count} tweets → {output_file}", file=sys.stderr)
            return (True, count, None)
        else:
            error = result.stderr or result.stdout
            print(f"  ✗ Error: {error[:200]}", file=sys.stderr)
            return (False, 0, error)
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout (>300s)", file=sys.stderr)
        return (False, 0, "Timeout")
    except FileNotFoundError:
        print(f"  ✗ tweet-harvest not found; install: pip install tweet-harvest", file=sys.stderr)
        return (False, 0, "tweet-harvest not installed")


def jsonl_to_csv(jsonl_path, csv_path):
    """
    Convert Tweet Harvest JSONL output to CSV for compatibility with phase5_consolidate.py.
    Expected JSONL columns: tweet_id, author, text, created_at, likes, retweets, lang
    """
    tweets = []
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    tweets.append(json.loads(line))
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSONL decode error in {jsonl_path}: {e}", file=sys.stderr)
        return 0

    if not tweets:
        print(f"  ⚠ No tweets in {jsonl_path}", file=sys.stderr)
        return 0

    # Standardize keys (Tweet Harvest might use different keys)
    fieldnames = ["tweet_id", "author", "text", "created_at", "likes", "retweets", "lang"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for tweet in tweets:
            writer.writerow(tweet)

    print(f"  → Converted to CSV: {csv_path} ({len(tweets)} rows)", file=sys.stderr)
    return len(tweets)


def main():
    # Load query spec
    spec_path = Path("data/query_spec.json")
    if not spec_path.exists():
        print(f"ERROR: {spec_path} not found", file=sys.stderr)
        print("Create query_spec.json with structure: { 'vektor': { 'queries': [...], 'limit': 500, 'lang': 'id' } }", file=sys.stderr)
        sys.exit(1)

    spec = load_query_spec(spec_path)
    print(f"[Phase 4] Loaded {len(spec)} vectors from {spec_path}", file=sys.stderr)

    # Create output dirs
    output_dir = Path("raw_additional_tweets")
    output_dir.mkdir(exist_ok=True)

    stats = {"total_vectors": 0, "total_queries": 0, "total_tweets": 0, "failed_queries": []}

    for vektor, config in spec.items():
        queries = config.get("queries", [])
        limit = config.get("limit", 500)
        lang = config.get("lang", "id")

        vektor_dir = output_dir / vektor
        vektor_dir.mkdir(exist_ok=True)

        print(f"\n[{vektor}] {len(queries)} queries, limit={limit}, lang={lang}", file=sys.stderr)
        stats["total_vectors"] += 1

        for query_idx, query in enumerate(queries, 1):
            # Short query preview for log
            query_preview = query[:60] + "..." if len(query) > 60 else query

            jsonl_output = vektor_dir / f"q{query_idx}.jsonl"
            csv_output = vektor_dir / f"q{query_idx}.csv"

            # Run query
            success, count, error = run_tweet_harvest(query, vektor, query_idx, jsonl_output, lang, limit)
            stats["total_queries"] += 1

            if success and count > 0:
                # Convert JSONL to CSV
                csv_count = jsonl_to_csv(jsonl_output, csv_output)
                stats["total_tweets"] += csv_count
            elif not success:
                stats["failed_queries"].append((vektor, query_idx, error))

            # Throttle between queries (rate-limiting)
            import time
            time.sleep(2)

    # Summary
    print(f"\n[Phase 4 Summary]", file=sys.stderr)
    print(f"  Vectors: {stats['total_vectors']}", file=sys.stderr)
    print(f"  Queries executed: {stats['total_queries']}", file=sys.stderr)
    print(f"  Total tweets: {stats['total_tweets']}", file=sys.stderr)
    print(f"  Failed queries: {len(stats['failed_queries'])}", file=sys.stderr)
    print(f"  Output: {output_dir}/", file=sys.stderr)

    if stats["failed_queries"]:
        print(f"\nFailed queries:", file=sys.stderr)
        for vektor, idx, err in stats["failed_queries"]:
            print(f"  - {vektor}:q{idx}: {err[:100]}", file=sys.stderr)

    # Write summary JSON for reproducibility
    summary_file = Path("raw_additional_tweets") / "_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "executed_at": datetime.utcnow().isoformat(),
            "spec_file": str(spec_path),
            **stats
        }, f, indent=2)
    print(f"  Summary: {summary_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
