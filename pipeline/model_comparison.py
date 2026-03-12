#!/usr/bin/env python3
"""Quick comparison: same episode coded by Sonnet vs Haiku."""

import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

import anthropic

# Reuse the prompt from the main script
sys.path.insert(0, str(Path(__file__).parent))
from importlib.machinery import SourceFileLoader
_mod = SourceFileLoader("ep", str(Path(__file__).parent / "02_analyze_episodes.py")).load_module()
CODING_PROMPT = _mod.CODING_PROMPT

MODELS = {
    "sonnet": "claude-sonnet-4-20250514",
    "haiku": "claude-haiku-4-5-20251001",
}

TEST_FILES = [
    "data/transcripts/future_weekly_-7uOHXuZ4fE.json",
    "data/transcripts/doppelgaenger_-JwUcl1lZNk.json",
    "data/transcripts/ct_uplink_-4qnQpVEeHg.json",
]


def code_episode(client, model_id, episode):
    transcript = episode["transcript"]
    max_chars = 80000
    if len(transcript) > max_chars:
        half = max_chars // 2
        transcript = transcript[:half] + "\n\n[...MITTE GEKÜRZT...]\n\n" + transcript[-half:]

    prompt = CODING_PROMPT.format(
        podcast_name=episode["podcast_name"],
        episode_title=episode.get("title", "?"),
        hosts=episode.get("hosts", "unbekannt"),
        transcript=transcript,
    )

    message = client.messages.create(
        model=model_id,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]

    # Strip any leading/trailing whitespace and BOM
    text = text.strip().lstrip("\ufeff")
    # Try to find JSON object boundaries
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": text[:300]}


def main():
    client = anthropic.Anthropic()

    for filepath in TEST_FILES:
        with open(filepath, "r", encoding="utf-8") as f:
            episode = json.load(f)

        podcast = episode["podcast_name"]
        words = episode["word_count"]
        print(f"\n{'='*70}")
        print(f"{podcast} ({words} words)")
        print(f"{'='*70}")

        # Run both models in parallel
        results = {}
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {
                pool.submit(code_episode, client, mid, episode): name
                for name, mid in MODELS.items()
            }
            for future in futures:
                name = futures[future]
                results[name] = future.result()

        # Compare scores
        for model_name in ["sonnet", "haiku"]:
            r = results[model_name]
            if "error" in r:
                print(f"\n  [{model_name.upper()}] ERROR: {r['error']}")
                print(f"    {r.get('raw', '')[:200]}")
                continue
            econ = r.get("economic_score", 0)
            soc = r.get("social_score", 0)
            n = r.get("n_coded", "?")
            conf = r.get("confidence", "?")
            print(f"\n  [{model_name.upper()}] Econ: {float(econ):+.1f} | Soc: {float(soc):+.1f} | "
                  f"{n} statements | confidence: {conf}")

            for stmt in r.get("coded_statements", [])[:5]:
                e = stmt.get("economic", "—")
                s = stmt.get("social", "—")
                e_str = f"{e:+d}" if isinstance(e, int) else "  —"
                s_str = f"{s:+d}" if isinstance(s, int) else "  —"
                print(f"    E:{e_str} S:{s_str}  \"{stmt['text'][:70]}\"")

            quotes = r.get("notable_quotes", [])
            if quotes:
                print(f"    Quiz quotes: {len(quotes)}")
                for q in quotes[:2]:
                    print(f"      \"{q['text'][:80]}\"")

        # Delta
        s_econ = results["sonnet"].get("economic_score", 0)
        h_econ = results["haiku"].get("economic_score", 0)
        s_soc = results["sonnet"].get("social_score", 0)
        h_soc = results["haiku"].get("social_score", 0)
        print(f"\n  DELTA (Sonnet - Haiku): Econ {s_econ - h_econ:+.1f} | Soc {s_soc - h_soc:+.1f}")


if __name__ == "__main__":
    main()
