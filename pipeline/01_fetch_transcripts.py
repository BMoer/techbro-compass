#!/usr/bin/env python3
"""
Podcast Political Compass Pipeline
Step 1: Fetch YouTube auto-captions for DACH tech podcasts
Step 2: Convert SRT → clean text
Step 3: Output structured JSON per episode
"""

import subprocess
import re
import json
import os
from datetime import datetime
from pathlib import Path

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
        "youtube_channel": None,  # May not have YouTube
    },
    "tech_ki_schmetterlinge": {
        "name": "Tech, KI & Schmetterlinge",
        "country": "DE",
        "hosts": "Sascha Lobo",
        "profile": "KI/Gesellschaft",
        "youtube_channel": None,  # Podigee-hosted
    },
    "digitec": {
        "name": "Digitec Tech-Telmechtel",
        "country": "CH",
        "hosts": "Philipp Rüegg, Simon Balissat, Luca Fontana",
        "profile": "Consumer Tech",
        "youtube_channel": None,  # Check separately
    },
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "transcripts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_channel_videos(channel_url, max_videos=10):
    """Get list of recent video IDs from a YouTube channel."""
    cmd = [
        "yt-dlp", "--no-check-certificates",
        "--flat-playlist",
        "--playlist-end", str(max_videos),
        "--print", "%(id)s\t%(title)s\t%(upload_date)s",
        f"{channel_url}/videos"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    videos = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            videos.append({
                "id": parts[0],
                "title": parts[1],
                "upload_date": parts[2] if parts[2] != 'NA' else None,
            })
    return videos


def download_captions(video_id, output_path):
    """Download German auto-captions for a video."""
    cmd = [
        "yt-dlp", "--no-check-certificates",
        "--write-auto-sub",
        "--sub-lang", "de",
        "--sub-format", "srt",
        "--skip-download",
        "-o", str(output_path),
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    srt_file = Path(f"{output_path}.de.srt")
    if srt_file.exists():
        return srt_file
    return None


def srt_to_text(srt_path):
    """Convert SRT file to clean text."""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    text_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r'^\d+$', line):
            continue
        if re.match(r'^\d{2}:\d{2}:\d{2}', line):
            continue
        text_lines.append(line)
    
    full_text = ' '.join(text_lines)
    full_text = re.sub(r'\s+', ' ', full_text)
    return full_text.strip()


def process_podcast(podcast_id, max_episodes=5):
    """Process a single podcast: fetch videos, download captions, extract text."""
    podcast = PODCASTS[podcast_id]
    print(f"\n{'='*60}")
    print(f"Processing: {podcast['name']} ({podcast['country']})")
    print(f"{'='*60}")
    
    if not podcast.get("youtube_channel"):
        print(f"  ⚠ No YouTube channel configured, skipping")
        return []
    
    # Get recent videos
    print(f"  Fetching video list from channel...")
    videos = get_channel_videos(podcast["youtube_channel"], max_videos=max_episodes)
    print(f"  Found {len(videos)} videos")
    
    episodes = []
    for i, video in enumerate(videos):
        print(f"  [{i+1}/{len(videos)}] {video['title'][:60]}...")
        
        output_base = OUTPUT_DIR / f"{podcast_id}_{video['id']}"
        srt_file = download_captions(video['id'], output_base)
        
        if srt_file:
            text = srt_to_text(srt_file)
            word_count = len(text.split())
            print(f"    ✓ {word_count} words extracted")
            
            episode = {
                "podcast_id": podcast_id,
                "podcast_name": podcast["name"],
                "country": podcast["country"],
                "hosts": podcast["hosts"],
                "profile": podcast["profile"],
                "video_id": video["id"],
                "title": video["title"],
                "upload_date": video["upload_date"],
                "word_count": word_count,
                "transcript": text,
            }
            episodes.append(episode)
            
            # Save individual episode JSON
            json_file = OUTPUT_DIR / f"{podcast_id}_{video['id']}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(episode, f, ensure_ascii=False, indent=2)
        else:
            print(f"    ✗ No German captions available")
    
    return episodes


def main():
    # Process podcasts that have YouTube channels
    all_episodes = []
    
    # Start with the most interesting ones for our analysis
    priority_podcasts = [
        "future_weekly",
        "doppelgaenger", 
        "ct_uplink",
    ]
    
    for pid in priority_podcasts:
        try:
            episodes = process_podcast(pid, max_episodes=3)
            all_episodes.extend(episodes)
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total episodes processed: {len(all_episodes)}")
    
    for ep in all_episodes:
        print(f"  {ep['podcast_name']}: {ep['title'][:50]}... ({ep['word_count']} words)")
    
    # Save master index
    index = {
        "generated_at": datetime.now().isoformat(),
        "podcasts": PODCASTS,
        "episodes": [{k: v for k, v in ep.items() if k != 'transcript'} for ep in all_episodes],
    }
    with open(OUTPUT_DIR / "index.json", 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"\nAll data saved to {OUTPUT_DIR}")
    return all_episodes


if __name__ == '__main__':
    main()
