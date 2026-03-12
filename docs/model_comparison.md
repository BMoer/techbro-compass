# Modellvergleich: Sonnet 4.6 vs Haiku 4.5

**Datum:** 2026-03-12
**Methode:** Gleiche Aussagen aus 3 Podcast-Episoden, codiert durch beide Modelle
**Podcasts:** Future Weekly, Doppelgänger Tech Talk, c't uplink

## Gesamtscores pro Episode

| Podcast | Modell | Econ | Soc | Statements | Confidence |
|---------|--------|------|-----|------------|------------|
| Future Weekly | Sonnet | -1.7 | +1.2 | 6 | 0.75 |
| | Haiku | +1.8 | +2.1 | 12 | 0.65 |
| Doppelgänger | Sonnet | -1.3 | +3.8 | 9 | 0.80 |
| | Haiku | -1.4 | +1.4 | 7 | 0.72 |
| c't uplink | Sonnet | -2.4 | +2.8 | 10 | 0.80 |
| | Haiku | -1.4 | +3.6 | 10 | 0.72 |

## Kontrollierte Aussagen-Codierung (gleiche Statements, beide Modelle)

### Future Weekly

| Aussage | Sonnet | Haiku | Delta |
|---------|--------|-------|-------|
| Plattform-Tracking und ertappte Pricing | E:— S:-3 | E:-7 S:-5 | dS:+2 |
| Chinesische Behörden zwingen Firmen, Algorithmen offenzulegen | E:-2 S:-5 | E:-6 S:-8 | **dE:+4 dS:+3** |
| Das ist genau das was immer alle kritisieren | E:— S:— | E:-3 S:+2 | — |

### Doppelgänger Tech Talk

| Aussage | Sonnet | Haiku | Delta |
|---------|--------|-------|-------|
| Trump macht wie Lichtschalter die Zölle an/aus | E:+6 S:— | E:-7 S:-8 | **dE:+13** |
| Ausnahmen helfen Leuten die sich gute Steuerberater leisten | E:-3 S:— | E:-6 S:-5 | **dE:+3** |
| Effektivstes Mittel wäre Big Tech mit allen Hebeln regulieren | E:-5 S:— | E:-8 S:-6 | **dE:+3** |
| Je mehr Ausnahmen desto komplexer das System | E:+3 S:— | E:+5 S:— | dE:-2 |
| Einzelner Mensch stellt sich über gesammeltes Wissen | E:— S:-4 | E:— S:-7 | **dS:+3** |

### c't uplink

| Aussage | Sonnet | Haiku | Delta |
|---------|--------|-------|-------|
| EU mit 500 Mio Usern sollte selbstbewusst vorgehen | E:-3 S:-2 | E:— S:-6 | **dS:+4** |
| Gute Argumente gegen große Social-Media-Konzerne | E:-4 S:— | E:-4 S:— | 0 |
| CDU prescht mit law-and-order Vorratsdatenspeicherung | E:— S:-7 | E:— S:-7 | 0 |
| Treibende Kräfte sind Versicherungen und Lobbyisten | E:-3 S:— | E:-6 S:— | **dE:+3** |

## Beobachtungen

### 1. Sprechakt-Verständnis
Größter Einzelfehler bei Sonnet: "Trump macht Zölle an/aus" wird als E:+6 codiert (pro Freihandel), weil Sonnet die **Kritik** des Sprechers an Trumps Protektionismus erkennt und die Position des Sprechers codiert. Haiku codiert E:-7 — die **beschriebene Politik** statt die Haltung des Sprechers.

**Bewertung durch menschlichen Codierer:** Beide Interpretationen sind vertretbar. Der Sprecher kritisiert Trump (= anti-protektionistisch), aber die Aussage selbst beschreibt auch Willkür. Für unser Projekt relevanter: Die **Position des Podcasts**, nicht die beschriebene Politik. Sonnet liegt hier näher, aber der Wert +6 übertreibt.

### 2. Extremitäts-Bias
Haiku codiert systematisch extremer (höhere Absolutwerte). Beispiele:
- "Chinesische Behörden zwingen Firmen": Sonnet S:-5 vs Haiku S:-8
- "Einzelner Mensch über gesammeltes Wissen": Sonnet S:-4 vs Haiku S:-7
- "Big Tech regulieren": Sonnet E:-5 vs Haiku E:-8

### 3. Übereinstimmung
Bei klar codierbaren Aussagen stimmen beide Modelle in der **Richtung** überein:
- CDU Vorratsdatenspeicherung: beide S:-7 (exakt gleich)
- Argumente gegen Social-Media-Konzerne: beide E:-4 (exakt gleich)
- Steuerausnahmen für Reiche: beide negativ economic

## Entscheidung

**Gewählt: Haiku 4.5** (`claude-haiku-4-5-20251001`)

Gründe:
- Zuverlässigeres JSON-Output (Sonnet hatte 2/3 Parse-Errors bei vollständiger Episoden-Codierung)
- Mehr Statements pro Episode codiert (10-12 vs 6-9) → robusterer Durchschnitt
- Extremitäts-Bias ist konsistent → verschiebt nur Absolutwerte, nicht relative Positionen
- 3x günstiger → ermöglicht vollständige Analyse aller 1.226 Episoden
- Sprechakt-Problem (Trump-Beispiel) betrifft beide Modelle, nur anders

Für die Website wird auf den Extremitäts-Bias hingewiesen.
