#!/usr/bin/env python3
"""
Podcast Political Compass Pipeline
Step 1: Fetch YouTube auto-captions for DACH tech podcasts
Step 2: Convert SRT → clean text
Step 3: Output structured JSON per episode

Parallelized: one thread per podcast, progress every 50 episodes.
"""

import subprocess
import re
import json
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import Lock

# === PODCAST REGISTRY ===
PODCASTS = {
    "future_weekly": {
        "name": "Future Weekly",
        "country": "AT",
        "hosts": "Daniel Cronin, Markus Raunig",
        "profile": "Startup/VC",
        "youtube_channel": "https://www.youtube.com/channel/UCAJ6dUsMbF8-PeQSdTMbgvg",
    },
    "doppelgaenger": {
        "name": "Doppelgänger Tech Talk",
        "country": "DE",
        "hosts": "Philipp Glöckler, Philipp Klöckner",
        "profile": "Tech/Business",
        "youtube_channel": "https://www.youtube.com/channel/UCZsFRBZ-5wNeFEqLFqnemcw",
        "alt_transcript": "https://doppelgaenger.ai/",
    },
    "omr": {
        "name": "OMR Podcast",
        "country": "DE",
        "hosts": "Philipp Westermeyer",
        "profile": "Marketing/Tech",
        "youtube_channel": "https://www.youtube.com/channel/UCSZ6CHjd2o7KdHzugfvSxXw",
    },
    "lobo": {
        "name": "Lobo – Der Debatten-Podcast",
        "country": "DE",
        "hosts": "Sascha Lobo",
        "profile": "Gesellschaft/Tech",
        "youtube_channel": "https://www.youtube.com/channel/UC_pP8R8ERPHnR8otzaBfIoA",
    },
    "t3n": {
        "name": "t3n Podcast",
        "country": "DE",
        "hosts": "t3n Redaktion",
        "profile": "Digitale Wirtschaft",
        "youtube_channel": "https://www.youtube.com/channel/UCSUisuyxfH1OoPCV_6qIuMw",
    },
    "bits_und_so": {
        "name": "Bits und so",
        "country": "DE",
        "hosts": "Timo Hetzel",
        "profile": "Tech-Kultur",
        "youtube_channel": "https://www.youtube.com/channel/UC6ySWla_95opV6RuXOX3HMQ",
    },
    "ct_uplink": {
        "name": "c't uplink",
        "country": "DE",
        "hosts": "c't Redaktion",
        "profile": "Tech-Journalismus",
        "youtube_channel": "https://www.youtube.com/channel/UCT2gF-XYP9zFVGr5qmR5EDg",
    },
    "tech_briefing": {
        "name": "Tech Briefing",
        "country": "DE",
        "hosts": "Christoph Keese, Lena Waltle",
        "profile": "Tech/Politik",
        "youtube_channel": None,
    },
    "tech_ki_schmetterlinge": {
        "name": "Tech, KI & Schmetterlinge",
        "country": "DE",
        "hosts": "Sascha Lobo",
        "profile": "KI/Gesellschaft",
        "youtube_channel": None,
    },
    "digitec": {
        "name": "Digitec Tech-Telmechtel",
        "country": "CH",
        "hosts": "Philipp Rüegg, Simon Balissat, Luca Fontana",
        "profile": "Consumer Tech",
        "youtube_channel": None,
    },
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "transcripts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROGRESS_INTERVAL = 50
print_lock = Lock()


def log(msg):
    with print_lock:
        print(msg, flush=True)


def get_channel_videos(channel_url):
    """Get ALL video IDs from a YouTube channel."""
    cmd = [
        "yt-dlp", "--no-check-certificates",
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s\t%(upload_date)s",
        f"{channel_url}/videos",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            videos.append({
                "id": parts[0],
                "title": parts[1],
                "upload_date": parts[2] if parts[2] != "NA" else None,
            })
    return videos


def download_and_extract(video_id, podcast_id, podcast_meta):
    """Download captions for one video, return episode dict or None."""
    json_file = OUTPUT_DIR / f"{podcast_id}_{video_id}.json"
    if json_file.exists():
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    with tempfile.TemporaryDirectory() as tmpdir:
        outpath = Path(tmpdir) / "sub"
        cmd = [
            "yt-dlp", "--no-check-certificates",
            "--write-auto-sub",
            "--sub-lang", "de",
            "--sub-format", "srt",
            "--skip-download",
            "-o", str(outpath),
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        srt_file = Path(f"{outpath}.de.srt")
        if not srt_file.exists():
            return None

        text = srt_to_text(srt_file)

    word_count = len(text.split())
    if word_count < 50:
        return None

    episode = {
        "podcast_id": podcast_id,
        "podcast_name": podcast_meta["name"],
        "country": podcast_meta["country"],
        "hosts": podcast_meta["hosts"],
        "profile": podcast_meta["profile"],
        "video_id": video_id,
        "word_count": word_count,
        "transcript": text,
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(episode, f, ensure_ascii=False, indent=2)

    return episode


def srt_to_text(srt_path):
    """Convert SRT file to clean text."""
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    text_lines = []
    for line in content.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if re.match(r"^\d+$", line):
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2}", line):
            continue
        text_lines.append(line)

    full_text = " ".join(text_lines)
    return re.sub(r"\s+", " ", full_text).strip()


def process_podcast(podcast_id):
    """Fetch all episodes for one podcast. Logs progress every PROGRESS_INTERVAL."""
    podcast = PODCASTS[podcast_id]
    name = podcast["name"]

    if not podcast.get("youtube_channel"):
        log(f"[{name}] No YouTube channel, skipping")
        return []

    log(f"[{name}] Fetching video list...")
    videos = get_channel_videos(podcast["youtube_channel"])
    total = len(videos)
    log(f"[{name}] {total} videos found, starting caption download...")

    episodes = []
    skipped = 0

    for i, video in enumerate(videos, 1):
        ep = download_and_extract(video["id"], podcast_id, podcast)

        if ep is not None:
            # Attach title and date from playlist metadata
            ep["title"] = video["title"]
            ep["upload_date"] = video["upload_date"]
            episodes.append(ep)
        else:
            skipped += 1

        if i % PROGRESS_INTERVAL == 0 or i == total:
            total_words = sum(e["word_count"] for e in episodes)
            log(
                f"[{name}] {i}/{total} done — "
                f"{len(episodes)} transcripts, {skipped} skipped, "
                f"{total_words:,} words total"
            )

    return episodes


def main():
    podcast_ids = sys.argv[1:] if len(sys.argv) > 1 else [
        "future_weekly",
        "doppelgaenger",
        "ct_uplink",
    ]

    # Validate IDs
    for pid in podcast_ids:
        if pid not in PODCASTS:
            log(f"ERROR: Unknown podcast '{pid}'. Available: {', '.join(PODCASTS)}")
            sys.exit(1)

    log(f"Starting parallel fetch for: {', '.join(podcast_ids)}")
    log(f"Output: {OUTPUT_DIR}\n")

    all_episodes = []

    with ThreadPoolExecutor(max_workers=len(podcast_ids)) as pool:
        futures = {pool.submit(process_podcast, pid): pid for pid in podcast_ids}
        for future in as_completed(futures):
            pid = futures[future]
            try:
                episodes = future.result()
                all_episodes.extend(episodes)
            except Exception as e:
                log(f"[{PODCASTS[pid]['name']}] FAILED: {e}")

    # Summary
    log(f"\n{'='*60}")
    log("FETCH COMPLETE")
    log(f"{'='*60}")

    by_podcast = {}
    for ep in all_episodes:
        by_podcast.setdefault(ep["podcast_id"], []).append(ep)

    for pid, eps in sorted(by_podcast.items()):
        words = sum(e["word_count"] for e in eps)
        log(f"  {PODCASTS[pid]['name']:35s} {len(eps):>4d} episodes, {words:>10,} words")

    total_words = sum(e["word_count"] for e in all_episodes)
    log(f"\n  TOTAL: {len(all_episodes)} episodes, {total_words:,} words")

    # Save index (without transcripts)
    index = {
        "generated_at": datetime.now().isoformat(),
        "episodes": [
            {k: v for k, v in ep.items() if k != "transcript"}
            for ep in all_episodes
        ],
    }
    with open(OUTPUT_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    log(f"\nIndex saved to {OUTPUT_DIR / 'index.json'}")


if __name__ == "__main__":
    main()
