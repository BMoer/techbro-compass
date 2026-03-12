#!/usr/bin/env python3
"""
02_analyze_episodes.py — Political Compass Scoring via Claude API

Takes podcast transcripts and scores them on two axes:
  - Economic (Left -10 to Right +10)
  - Social (Authoritarian -10 to Libertarian +10)

Uses the "Ask and Average" method (Le Mens et al., 2025).
"""

import argparse
import json
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

# Try to import anthropic, give helpful error if missing
try:
    import anthropic
except ImportError:
    print("pip install anthropic python-dotenv")
    sys.exit(1)

CODING_PROMPT = """Du bist ein politikwissenschaftlicher Codierer. Deine Aufgabe ist es, 
meinungstragende Aussagen in einem Podcast-Transkript auf zwei Achsen zu verorten:

**Achse 1: Ökonomisch (Links–Rechts)**
- -10 = Stark Links (Verstaatlichung, radikale Umverteilung, Anti-Kapitalismus)
- -5 = Links (Regulierung, Sozialstaat, Arbeitnehmerrechte)
- 0 = Zentrum (pragmatisch, gemischt)
- +5 = Rechts (Freier Markt, Deregulierung, Unternehmertum)
- +10 = Stark Rechts (Radikaler Libertarismus, Abschaffung Sozialleistungen)

**Achse 2: Gesellschaftlich (Autoritär–Libertär)**
- -10 = Stark Autoritär (Totale Überwachung, Polizeistaat)
- -5 = Autoritär (Überwachung befürworten, Sicherheit > Freiheit)
- 0 = Zentrum (abwägend)
- +5 = Libertär (Datenschutz, Bürgerrechte, Anti-Zensur)
- +10 = Stark Libertär (Krypto-Anarchismus, Zero Staat)

**Ankerbeispiele:**
- "Big Tech muss zerschlagen werden" → Econ: -6, Soc: null
- "Europa reguliert sich zu Tode" → Econ: +5, Soc: null
- "KI-Überwachung ist effizient" → Econ: null, Soc: -5
- "Datenschutz ist ein Grundrecht" → Econ: null, Soc: +4
- "Sozialleistungen machen abhängig" → Econ: +8, Soc: null
- "Crypto = echte Freiheit" → Econ: +5, Soc: +7
- "Plattformen müssen Content moderieren" → Econ: null, Soc: -2
- "Wer nicht arbeitet, soll nicht essen" → Econ: +8, Soc: -3

**Codierregeln:**
1. Nur meinungstragende Aussagen codieren. Nachrichten/Fakten ignorieren.
2. Ironie und Sarkasmus erkennen! Tech-Podcasts sind oft ironisch.
3. null setzen wenn eine Achse nicht betroffen ist.
4. Mindestens 5 Aussagen codieren. Wenn weniger als 5 codierbar: "insufficient_data": true
5. Für das Quiz-Feature: Markiere besonders pointierte/extreme Aussagen mit "quiz_suitable": true

**WICHTIG:** Antworte NUR mit validem JSON. Kein Markdown, keine Erklärungen außerhalb des JSON.

Analysiere das folgende Transkript:

PODCAST: {podcast_name}
EPISODE: {episode_title}
HOSTS: {hosts}

---TRANSKRIPT---
{transcript}
---ENDE TRANSKRIPT---

Antworte mit diesem JSON-Format:
{{
  "economic_score": <float, Durchschnitt aller ökonomischen Scores>,
  "social_score": <float, Durchschnitt aller gesellschaftlichen Scores>,
  "n_coded": <int, Anzahl codierter Aussagen>,
  "insufficient_data": <bool>,
  "confidence": <float 0-1, wie sicher bist du dir>,
  "coded_statements": [
    {{
      "text": "<die Aussage, max 120 Zeichen>",
      "speaker": "host" | "guest",
      "economic": <int -10 to +10 oder null>,
      "social": <int -10 to +10 oder null>,
      "reasoning": "<kurze Begründung, max 60 Zeichen>"
    }}
  ],
  "notable_quotes": [
    {{
      "text": "<pointierte Aussage für das Quiz>",
      "context": "<Kontext in 1 Satz>",
      "quiz_suitable": true
    }}
  ]
}}"""


def analyze_episode(transcript_path: Path, client: anthropic.Anthropic) -> dict:
    """Analyze a single episode transcript."""
    with open(transcript_path, 'r', encoding='utf-8') as f:
        episode = json.load(f)
    
    # Truncate transcript if too long (Claude context limit)
    transcript = episode["transcript"]
    max_chars = 80000  # ~20k tokens, well within limits
    if len(transcript) > max_chars:
        # Take first and last portions to capture intro and conclusion
        half = max_chars // 2
        transcript = transcript[:half] + "\n\n[...MITTE GEKÜRZT...]\n\n" + transcript[-half:]
    
    prompt = CODING_PROMPT.format(
        podcast_name=episode["podcast_name"],
        episode_title=episode.get("title", transcript_path.stem),
        hosts=episode.get("hosts", "unbekannt"),
        transcript=transcript,
    )
    
    print(f"  Sending to Claude API ({len(transcript):,} chars)...")
    
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    
    response_text = message.content[0].text.strip()
    
    # Parse JSON response
    response_text = response_text.strip().lstrip("\ufeff")
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    if start >= 0 and end > start:
        response_text = response_text[start:end]

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parse error: {e}")
        print(f"  Response preview: {response_text[:200]}")
        result = {"error": str(e), "raw_response": response_text[:500]}
    
    # Enrich with episode metadata
    result["episode_id"] = f"{episode['podcast_id']}_{episode['video_id']}"
    result["podcast"] = episode["podcast_name"]
    result["podcast_id"] = episode["podcast_id"]
    result["title"] = episode.get("title", transcript_path.stem)
    result["date"] = episode.get("upload_date")
    result["country"] = episode.get("country")
    result["word_count"] = episode.get("word_count")
    
    return result


def sample_per_podcast(files, n_per_podcast):
    """Pick n random files per podcast for a representative sample."""
    by_podcast = defaultdict(list)
    for f in files:
        podcast_id = f.stem.rsplit("_", 1)[0]
        by_podcast[podcast_id].append(f)

    sampled = []
    for pid, pfiles in sorted(by_podcast.items()):
        pick = min(n_per_podcast, len(pfiles))
        sampled.extend(random.sample(pfiles, pick))
    return sorted(sampled)


def main():
    parser = argparse.ArgumentParser(description="Analyze podcast transcripts")
    parser.add_argument("--sample", type=int, default=0,
                        help="Analyze N random episodes per podcast (0 = all)")
    parser.add_argument("files", nargs="*", help="Specific transcript files to analyze")
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in .env or environment")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if args.files:
        transcript_files = [Path(f) for f in args.files]
    else:
        transcript_dir = Path("data/transcripts")
        if not transcript_dir.exists():
            print(f"ERROR: {transcript_dir} not found. Run 01_fetch_transcripts.py first.")
            sys.exit(1)

        transcript_files = sorted(transcript_dir.glob("*.json"))
        transcript_files = [f for f in transcript_files if f.name != "index.json"]

    if not transcript_files:
        print("No transcript files found.")
        sys.exit(1)

    if args.sample > 0:
        transcript_files = sample_per_podcast(transcript_files, args.sample)
        print(f"SAMPLE MODE: {len(transcript_files)} episodes ({args.sample} per podcast)")
    else:
        print(f"Found {len(transcript_files)} episodes to analyze")
    
    # Output directory
    scores_dir = Path("data/scores")
    scores_dir.mkdir(parents=True, exist_ok=True)
    
    all_results = []
    
    for i, tf in enumerate(transcript_files):
        print(f"\n[{i+1}/{len(transcript_files)}] {tf.stem}")
        
        # Skip if already analyzed
        score_file = scores_dir / f"{tf.stem}_score.json"
        if score_file.exists():
            print(f"  Already analyzed, skipping")
            with open(score_file) as f:
                all_results.append(json.load(f))
            continue
        
        try:
            result = analyze_episode(tf, client)
            
            # Save individual result
            with open(score_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            econ = result.get("economic_score")
            soc = result.get("social_score")
            n = result.get("n_coded", 0)
            econ_str = f"{econ:+.1f}" if isinstance(econ, (int, float)) else "?"
            soc_str = f"{soc:+.1f}" if isinstance(soc, (int, float)) else "?"
            print(f"  ✓ Econ: {econ_str} | Soc: {soc_str} | {n} statements coded")
            
            all_results.append(result)
            
            # Rate limiting — generous delay to avoid 429s
            time.sleep(5)
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Save master results file (for the website)
    master = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "method": "LLM-based coding (Le Mens et al. 2025 Ask-and-Average)",
        "model": "claude-haiku-4-5-20251001",
        "episodes": []
    }
    
    # Collect all quiz quotes
    all_quotes = []
    
    for r in all_results:
        episode_summary = {
            "episode_id": r.get("episode_id"),
            "podcast": r.get("podcast"),
            "podcast_id": r.get("podcast_id"),
            "title": r.get("title"),
            "date": r.get("date"),
            "country": r.get("country"),
            "economic_score": r.get("economic_score"),
            "social_score": r.get("social_score"),
            "n_coded": r.get("n_coded"),
            "confidence": r.get("confidence"),
        }
        master["episodes"].append(episode_summary)
        
        for q in r.get("notable_quotes", []):
            if q.get("quiz_suitable"):
                all_quotes.append({
                    "text": q["text"],
                    "context": q.get("context", ""),
                    "podcast": r.get("podcast"),
                    "episode": r.get("title"),
                })
    
    with open(scores_dir / "master_results.json", 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    
    with open(scores_dir / "quiz_quotes.json", 'w', encoding='utf-8') as f:
        json.dump(all_quotes, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Episodes analyzed: {len(all_results)}")
    print(f"\nResults by podcast:")
    
    by_podcast = defaultdict(list)
    for r in all_results:
        by_podcast[r.get("podcast", "?")].append(r)
    
    for podcast, episodes in sorted(by_podcast.items()):
        econ_vals = [e.get("economic_score") for e in episodes if isinstance(e.get("economic_score"), (int, float))]
        soc_vals = [e.get("social_score") for e in episodes if isinstance(e.get("social_score"), (int, float))]
        econ_avg = sum(econ_vals) / len(econ_vals) if econ_vals else 0
        soc_avg = sum(soc_vals) / len(soc_vals) if soc_vals else 0
        print(f"  {podcast:35s} Econ: {econ_avg:+.1f} | Soc: {soc_avg:+.1f} ({len(episodes)} eps, {len(econ_vals)} valid)")
    
    print(f"\nQuiz quotes collected: {len(all_quotes)}")
    print(f"Files saved to {scores_dir}/")


if __name__ == "__main__":
    main()
