# techbro-oder-faschist

**Political Compass für DACH Tech-Podcasts**

Longitudinale politische Verortung von deutschsprachigen Tech-Podcasts auf dem Political Compass (Economic Left–Right × Social Authoritarian–Libertarian), automatisiert via LLM-Coding, visualisiert als interaktive Website.

Fun Feature: "Tech Bro oder Faschist?" — Rate die Aussage.

## Repo-Struktur

```
techbro-oder-faschist/
├── README.md
├── .gitignore
├── data/
│   ├── podcasts.json          # Podcast-Registry (Metadaten, Channel-URLs)
│   ├── transcripts/           # Rohe Transkripte (git-ignored, zu groß)
│   └── scores/                # LLM-Analyseergebnisse (JSON, committed)
├── pipeline/
│   ├── 01_fetch_transcripts.py   # YouTube Captions → SRT → Text
│   ├── 02_analyze_episodes.py    # Transkript → LLM → Political Compass Scores
│   ├── coding_scheme.md          # Das wissenschaftliche Coding Scheme
│   └── requirements.txt
├── web/                          # Static Site (GitHub Pages)
│   ├── index.html
│   ├── style.css
│   └── app.js
└── docs/
    ├── methodik.md               # Wissenschaftliche Begründung
    └── quellen.md
```

## Setup (5 Minuten)

```bash
# 1. Repo erstellen
mkdir techbro-oder-faschist && cd techbro-oder-faschist
git init

# 2. .gitignore
cat > .gitignore << 'EOF'
data/transcripts/
__pycache__/
*.pyc
.env
node_modules/
.DS_Store
EOF

# 3. Ordnerstruktur
mkdir -p data/transcripts data/scores pipeline web docs

# 4. Python deps
cat > pipeline/requirements.txt << 'EOF'
yt-dlp>=2024.0.0
anthropic>=0.40.0
python-dotenv>=1.0.0
EOF

# 5. .env für API Keys (NICHT committen)
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
EOF

# 6. Initial commit
git add .
git commit -m "init: repo structure"

# 7. GitHub repo erstellen + pushen
# gh repo create techbro-oder-faschist --public --source=. --push
# ODER: manuell auf github.com → New Repository → push
```

## Hosting

**GitHub Pages** für die statische Website:
- Settings → Pages → Source: `main` branch, `/web` folder
- URL: `https://<username>.github.io/techbro-oder-faschist/`
- Alternativ: Custom Domain (z.B. `techbro.moerzinger.eu`)

## Workflow

1. `pipeline/01_fetch_transcripts.py` → holt YouTube Auto-Captions
2. `pipeline/02_analyze_episodes.py` → schickt Transkripte durch Claude mit Coding Scheme
3. Ergebnisse landen in `data/scores/*.json`
4. `web/` liest die JSON-Dateien und rendert den Compass + Quiz
5. `git push` → GitHub Pages deployed automatisch

## Parallelisierung

| Task | Wer | Dauer |
|------|-----|-------|
| Repo aufsetzen | Ben | 5 min |
| Coding Scheme finalisieren | Claude | nächster Chat-Turn |
| Transcripts für alle 10 Podcasts fetchen | Ben (Script laufen lassen) | ~30 min |
| LLM-Analyse über Transkripte | Claude/Ben | ~1h |
| Website bauen | Claude | nächster Chat-Turn |
| "Tech Bro oder Faschist" Quotes sammeln | Claude (aus Transkripten) | parallel |
