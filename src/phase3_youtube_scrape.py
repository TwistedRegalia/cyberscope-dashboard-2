#!/usr/bin/env python3
"""
Phase 3 — YouTube Data API v3 Scraper
Pulls comments from video_candidates.csv and saves to raw_additional_youtube/

Prerequisites:
- YouTube Data API v3 key (set as env var YOUTUBE_API_KEY)
- video_candidates.csv in data/ with columns: vektor, video_id, video_title, channel_name, channel_type, publish_date, comment_count, verified_topic, notes
- google-api-python-client: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

Output: raw_additional_youtube/{vektor}/{video_id}.csv per video
        with columns: video_id, comment_id, author, text, likes, replies, published_at
"""

import os
import sys
import csv
from pathlib import Path
from datetime import datetime
import json

import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_youtube_service(api_key):
    """Initialize YouTube API v3 client."""
    return build("youtube", "v3", developerKey=api_key)


def scrape_comments(service, video_id, max_results=10000):
    """
    Scrape all comments (top-level + replies) from a video.
    Yields dicts with keys: comment_id, author, text, likes, replies, published_at
    """
    request = service.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        maxResults=100,  # API limit per page
        textFormat="plainText",
        pageToken=None
    )

    count = 0
    while request and count < max_results:
        response = request.execute()

        for item in response.get("items", []):
            # Top-level comment
            comment = item["snippet"]["topLevelComment"]["snippet"]
            yield {
                "comment_id": item["id"],
                "author": comment["authorDisplayName"],
                "text": comment["textDisplay"],
                "likes": comment["likeCount"],
                "replies": item["snippet"]["totalReplyCount"],
                "published_at": comment["publishedAt"],
                "is_reply": False
            }
            count += 1

            # Replies (if any)
            if item.get("replies"):
                for reply_item in item["replies"].get("comments", []):
                    reply = reply_item["snippet"]
                    yield {
                        "comment_id": reply_item["id"],
                        "author": reply["authorDisplayName"],
                        "text": reply["textDisplay"],
                        "likes": reply["likeCount"],
                        "replies": 0,
                        "published_at": reply["publishedAt"],
                        "is_reply": True
                    }
                    count += 1
                    if count >= max_results:
                        break

        # Next page
        pageToken = response.get("nextPageToken")
        if pageToken and count < max_results:
            request = service.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=100,
                textFormat="plainText",
                pageToken=pageToken
            )
        else:
            break

    print(f"  → Scraped {count} comments from {video_id}", file=sys.stderr)


def main():
    # Get API key
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    service = get_youtube_service(api_key)

    # Read video_candidates.csv
    candidates_path = Path("data/video_candidates.csv")
    if not candidates_path.exists():
        print(f"ERROR: {candidates_path} not found", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(candidates_path)
    print(f"[Phase 3] Scraping {len(df)} videos from {candidates_path}", file=sys.stderr)

    # Create output dirs
    output_dir = Path("raw_additional_youtube")
    output_dir.mkdir(exist_ok=True)

    total_comments = 0
    failed_videos = []

    for _, row in df.iterrows():
        vektor = row["vektor"]
        video_id = row["video_id"]
        video_title = row.get("video_title", "unknown")

        # Create vektor subdir
        vektor_dir = output_dir / vektor
        vektor_dir.mkdir(exist_ok=True)

        output_file = vektor_dir / f"{video_id}.csv"

        print(f"[{vektor}] Scraping {video_id} ({video_title})...", file=sys.stderr)

        try:
            comments = list(scrape_comments(service, video_id))

            if comments:
                # Save to CSV
                with open(output_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["comment_id", "author", "text", "likes", "replies", "published_at", "is_reply"])
                    writer.writeheader()
                    writer.writerows(comments)

                print(f"  ✓ Saved {len(comments)} comments to {output_file}", file=sys.stderr)
                total_comments += len(comments)
            else:
                print(f"  ⚠ No comments found (comments may be disabled)", file=sys.stderr)

        except HttpError as e:
            error_code = e.resp.status
            if error_code == 403:
                print(f"  ✗ Video {video_id} not found or comments disabled (403)", file=sys.stderr)
            elif error_code == 404:
                print(f"  ✗ Video {video_id} not found (404)", file=sys.stderr)
            elif error_code == 429:
                print(f"  ✗ API quota exceeded; stopping", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"  ✗ HTTP {error_code}: {e}", file=sys.stderr)
            failed_videos.append((video_id, str(e)))

    # Summary
    print(f"\n[Phase 3 Summary]", file=sys.stderr)
    print(f"  Total videos: {len(df)}", file=sys.stderr)
    print(f"  Successful: {len(df) - len(failed_videos)}", file=sys.stderr)
    print(f"  Failed: {len(failed_videos)}", file=sys.stderr)
    print(f"  Total comments scraped: {total_comments}", file=sys.stderr)
    print(f"  Output: {output_dir}/", file=sys.stderr)

    if failed_videos:
        print(f"\nFailed videos:", file=sys.stderr)
        for vid, err in failed_videos:
            print(f"  - {vid}: {err}", file=sys.stderr)


if __name__ == "__main__":
    main()
