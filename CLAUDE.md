# CLAUDE.md — techbro-oder-faschist

## Projekt

Longitudinale politische Verortung von DACH Tech-Podcasts auf dem Political Compass (Economic Left–Right × Social Authoritarian–Libertarian). Automatisiert via LLM-Coding von Podcast-Transkripten, visualisiert als interaktive Website.

Fun Feature: "Tech Bro oder Faschist?" — Quiz mit echten Podcast-Zitaten.

Hobbyprojekt. Deadline: Montag.

## Repo-Struktur

```
techbro-oder-faschist/
├── CLAUDE.md              ← du bist hier
├── .gitignore
├── .env                   # ANTHROPIC_API_KEY (nicht committen)
├── data/
│   ├── podcasts.json      # Podcast-Registry
│   ├── transcripts/       # Rohe Transkripte (git-ignored)
│   └── scores/            # LLM-Analyseergebnisse (committed)
├── pipeline/
│   ├── 01_fetch_transcripts.py
│   ├── 02_analyze_episodes.py
│   ├── coding_scheme.md
│   └── requirements.txt
├── web/
│   └── index.html         # Single-file Website (GitHub Pages)
└── docs/
    └── methodik.md
```

## Status

- [x] Podcast-Liste definiert (10 Podcasts, DE/AT/CH)
- [x] Transkript-Pipeline gebaut (YouTube Auto-Captions via yt-dlp)
- [x] Pipeline getestet: 131.927 Wörter aus 13 Episoden / 5 Podcasts extrahiert
- [x] Coding Scheme erstellt (operationalisiert, mit Ankerbeispielen)
- [x] LLM-Analyse-Script geschrieben (02_analyze_episodes.py)
- [x] Website-Skeleton gebaut (index.html mit Demo-Daten)
- [ ] Transkripte für alle 10 Podcasts fetchen
- [ ] LLM-Analyse über alle Transkripte laufen lassen
- [ ] Website mit echten Daten füttern
- [ ] Quiz-Quotes kuratieren
- [ ] Deployment (GitHub Pages)

## Podcast-Liste

| # | Podcast | Land | YouTube Channel ID | Profil |
|---|---------|------|--------------------|--------|
| 1 | Future Weekly | AT | UCAJ6dUsMbF8-PeQSdTMbgvg | Startup/VC |
| 2 | Doppelgänger Tech Talk | DE | UCZsFRBZ-5wNeFEqLFqnemcw | Tech/Business |
| 3 | OMR Podcast | DE | UCSZ6CHjd2o7KdHzugfvSxXw | Marketing/Tech |
| 4 | Lobo – Der Debatten-Podcast | DE | UC_pP8R8ERPHnR8otzaBfIoA (SPIEGEL) | Gesellschaft/Tech |
| 5 | t3n Podcast | DE | UCSUisuyxfH1OoPCV_6qIuMw | Digitale Wirtschaft |
| 6 | Bits und so | DE | UC6ySWla_95opV6RuXOX3HMQ | Tech-Kultur |
| 7 | Tech Briefing | DE | — (kein YT) | Tech/Politik |
| 8 | c't uplink | DE | UCT2gF-XYP9zFVGr5qmR5EDg | Tech-Journalismus |
| 9 | Tech, KI & Schmetterlinge | DE | — (Podigee) | KI/Gesellschaft |
| 10 | Digitec Tech-Telmechtel | CH | — (prüfen) | Consumer Tech |

Podcasts ohne YouTube-Channel: Transkripte via Apple Podcasts oder Whisper als Fallback.

## Pipeline

### 01_fetch_transcripts.py

- Nutzt `yt-dlp --no-check-certificates` (SSL-Workaround nötig)
- Holt deutsche Auto-Captions (`--write-auto-sub --sub-lang de --sub-format srt`)
- Konvertiert SRT → Plaintext (Timestamps + Sequenznummern strippen)
- Output: `data/transcripts/{podcast_id}_{video_id}.json`
- Qualität: ~90-95% akkurat, "Antrophic" statt "Anthropic" etc. — für LLM-Analyse ausreichend

### 02_analyze_episodes.py

- Liest Transkript-JSONs aus `data/transcripts/`
- Sendet an Claude API (claude-sonnet-4-20250514) mit Coding-Scheme-Prompt
- Coding Scheme: Zwei Achsen, -10 bis +10, Few-Shot Ankerbeispiele
- Output pro Episode: `data/scores/{episode_id}_score.json`
- Aggregiert: `data/scores/master_results.json` (für Website)
- Sammelt: `data/scores/quiz_quotes.json` (für Quiz-Feature)
- Braucht `ANTHROPIC_API_KEY` in `.env`

### Wissenschaftliche Basis

Zwei-Achsen-Modell: Eysenck (1954), Nolan (1971)
LLM-Codierung: Le Mens et al. (2025) "Ask and Average" — r > 0.90 mit Experten
Best Practices: Ornstein et al. (2025) Few-Shot-Prompting; Farjam et al. (2025) Codebook-LLM
Validierung: Heseltine & Clemm von Hohenberg (2024) — GPT-4 bis 95% Accuracy

## Website

- Single HTML file: `web/index.html`
- Fonts: Instrument Serif (Display) + DM Mono (Body) via Google Fonts
- Hosting: GitHub Pages aus `/web` Folder
- Lädt `data/scores/master_results.json` und `data/scores/quiz_quotes.json`
- Fallback auf eingebaute Demo-Daten wenn JSONs nicht vorhanden
- Features:
  - Interaktiver Political Compass (SVG, Podcasts als Dots)
  - "Tech Bro oder Faschist?" Quiz
  - Methodik-Sektion mit Referenzen

## Konventionen

- Sprache im Code: Englisch (Variablen, Comments)
- Sprache im Content/UI: Deutsch
- Umlaute (ä, ö, ü, ß) direkt verwenden, nie ae/oe/ue
- User Stories horizontal schneiden (full value, minimal depth)
- Wenn was fehlt: mit Annahmen arbeiten, markieren, weitermachen

## Nächste Schritte

1. Transkripte für alle 10 Podcasts holen (mehr Episoden pro Podcast, z.B. 10-20)
2. LLM-Analyse durchlaufen lassen
3. Website mit echten Daten testen
4. Quiz-Quotes kuratieren und ergänzen
5. GitHub Pages deployen
6. README.md für das öffentliche Repo schreiben
