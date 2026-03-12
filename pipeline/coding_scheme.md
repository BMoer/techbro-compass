# Coding Scheme: Political Compass für DACH Tech-Podcasts

## Wissenschaftliche Grundlage

Dieses Coding Scheme operationalisiert die politische Verortung von Podcast-Episoden
auf zwei unabhängigen Achsen, basierend auf dem etablierten Zwei-Achsen-Modell
politischer Ideologie (Eysenck, 1954; Nolan, 1971; Political Compass, 2001).

### Theoretischer Rahmen

**Achse 1: Ökonomisch (Links–Rechts)**
- Misst Einstellungen zu Wirtschaftspolitik, Marktregulierung und Ressourcenverteilung
- Links: Staatliche Intervention, Umverteilung, Regulierung, Kollektivgüter
- Rechts: Freier Markt, Deregulierung, Privatisierung, Eigenverantwortung

**Achse 2: Gesellschaftlich (Libertär–Autoritär)**
- Misst Einstellungen zu persönlichen Freiheiten, Überwachung und staatlicher Kontrolle
- Libertär: Bürgerrechte, Datenschutz, individuelle Freiheit, Anti-Überwachung
- Autoritär: Überwachung, Kontrolle, Hierarchie, Sicherheit vor Freiheit

### Methodischer Ansatz

Wir verwenden die "Ask and Average"-Methode (Le Mens et al., 2025), bei der ein
LLM direkt nach der ideologischen Position einzelner Aussagen gefragt wird. Die
Durchschnittswerte über alle codierten Aussagen einer Episode ergeben die
Episoden-Position. Korrelationen mit menschlicher Codierung erreichen r > 0.90.

## Analyseeinheit

**Primäre Einheit:** Einzelne meinungstragende Aussagen innerhalb einer Episode.
Nicht jeder Satz ist relevant — nur Aussagen, die eine politische, ökonomische oder
gesellschaftliche Position erkennen lassen.

**Aggregation:** Episoden-Score = Durchschnitt aller codierten Aussagen der Episode.

## Skala

Beide Achsen: **-10 bis +10** (ganzzahlig)

### Ökonomische Achse

| Score | Label | Beschreibung |
|-------|-------|--------------|
| -10 bis -7 | Stark Links | Verstaatlichung, radikale Umverteilung, Anti-Kapitalismus |
| -6 bis -3 | Links | Regulierung, Sozialstaat, Arbeitnehmerrechte, Steuerprogression |
| -2 bis +2 | Zentrum | Pragmatisch, kontextabhängig, gemischte Positionen |
| +3 bis +6 | Rechts | Freier Markt, Steuersenkungen, Deregulierung, Unternehmertum |
| +7 bis +10 | Stark Rechts | Radikaler Libertarismus, Abschaffung von Sozialleistungen, Laissez-faire |

### Gesellschaftliche Achse

| Score | Label | Beschreibung |
|-------|-------|--------------|
| -10 bis -7 | Stark Autoritär | Totale Überwachung, Unterdrückung von Dissens, Polizeistaat |
| -6 bis -3 | Autoritär | Überwachung befürworten, Sicherheit > Freiheit, starke Hierarchien |
| -2 bis +2 | Zentrum | Abwägend, kontextabhängig, moderate Positionen |
| +3 bis +6 | Libertär | Datenschutz, Bürgerrechte, Pressefreiheit, Anti-Zensur |
| +7 bis +10 | Stark Libertär | Radikale Autonomie, Krypto-Anarchismus, Zero Staat |

## Ankerbeispiele (Few-Shot)

Die folgenden Beispiele dienen als Referenzpunkte für die LLM-Codierung.
Sie stammen aus typischen Aussagen im DACH Tech-Podcast-Kontext.

### Ökonomische Achse

**Econ -8:** "Big Tech muss zerschlagen werden. Diese Monopole schaden der Gesellschaft
und der Staat muss eingreifen, bevor es zu spät ist."

**Econ -4:** "Die EU-Regulierung von KI ist wichtig. Ohne Regeln werden nur die
großen Player profitieren und Startups haben keine Chance."

**Econ -1:** "Regulierung hat ihre Berechtigung, aber man muss aufpassen, dass man
Innovation nicht abwürgt. Es braucht eine Balance."

**Econ +3:** "Europa reguliert sich zu Tode. Kein Wunder, dass alle Gründer in die
USA gehen. Wir brauchen weniger Bürokratie, nicht mehr."

**Econ +6:** "Der Markt regelt das am besten. Wenn ein Produkt schlecht ist, kauft es
niemand. Regulierung verzerrt nur den Wettbewerb."

**Econ +9:** "Sozialleistungen machen Menschen abhängig. Jeder sollte selbst für sich
sorgen. Der Staat hat in der Wirtschaft nichts verloren."

### Gesellschaftliche Achse

**Soc -7:** "KI-Überwachung in Städten ist die Zukunft. Wer nichts zu verbergen hat,
hat nichts zu befürchten. Sicherheit geht vor."

**Soc -4:** "Gesichtserkennung im öffentlichen Raum kann Verbrechen verhindern.
Natürlich muss es Regeln geben, aber die Technologie ist gut."

**Soc -1:** "Plattformen haben eine Verantwortung, Desinformation zu bekämpfen.
Manchmal muss Content moderiert werden."

**Soc +3:** "Datenschutz ist ein Grundrecht. DSGVO ist zwar nervig für Startups,
aber im Kern richtig."

**Soc +4:** "Ich bin gegen jede Form von staatlicher Überwachung. End-to-End-
Verschlüsselung muss Standard sein."

**Soc +8:** "Staaten haben kein Recht, das Internet zu regulieren. Dezentralisierung
und Krypto sind der einzige Weg zu echter Freiheit."

### Spezifische Tech-Podcast-Indikatoren

Diese Themen tauchen regelmäßig in DACH Tech-Podcasts auf und haben klare Zuordnungen:

| Thema | Ökonomisch | Gesellschaftlich |
|-------|-----------|-----------------|
| "EU reguliert zu viel" | Rechts (+) | — |
| "Grundeinkommen wäre gut" | Links (-) | — |
| "Gründer verdienen ihren Reichtum" | Rechts (+) | — |
| "Arbeitnehmer brauchen mehr Schutz" | Links (-) | — |
| "KI-Überwachung ist effizient" | — | Autoritär (-) |
| "Datenschutz bremst Innovation" | Rechts (+) | Autoritär (-) |
| "Crypto = Freiheit" | Rechts (+) | Libertär (+) |
| "Social Media braucht Zensur" | — | Autoritär (-) |
| "Whistleblower schützen" | — | Libertär (+) |
| "Plattform-Monopole zerschlagen" | Links (-) | — |
| "Immigration bringt Fachkräfte" | — | Libertär (+) |
| "KI ersetzt Jobs, Staat muss handeln" | Links (-) | — |
| "Wer nicht arbeitet, soll nicht essen" | Rechts (+) | Autoritär (-) |
| "Musk ist ein Visionär" | Rechts (+) | kontextabhängig |
| "Tech-Milliardäre haben zu viel Macht" | Links (-) | — |

## Codierregeln

1. **Nur meinungstragende Aussagen codieren.** Nachrichtenberichte, Fakten ohne
   Wertung, und rein technische Diskussionen werden ignoriert.

2. **Host-Meinungen von Gast-Meinungen unterscheiden.** Der Episoden-Score
   gewichtet Host-Aussagen stärker (Faktor 1.5), da sie die redaktionelle
   Linie des Podcasts repräsentieren.

3. **Ironie und Sarkasmus erkennen.** Tech-Podcasts sind oft ironisch.
   "Na klar, Regulierung hat ja noch nie geschadet" ist NICHT pro-Regulierung.

4. **Kontextabhängig codieren.** "Der Markt regelt das" als ernstgemeinte
   Überzeugung ≠ als ironische Kritik an Marktversagen.

5. **Keine Codierung bei Ambiguität.** Wenn eine Aussage nicht eindeutig
   zuordenbar ist, wird sie nicht codiert.

6. **Minimum 5 codierte Aussagen pro Episode.** Episoden mit weniger als 5
   codierbaren Aussagen werden als "nicht auswertbar" markiert.

## Output-Format

```json
{
  "episode_id": "doppelgaenger_abc123",
  "podcast": "Doppelgänger Tech Talk",
  "title": "Episode Title",
  "date": "2026-03-01",
  "scores": {
    "economic": 3.2,
    "social": 1.8
  },
  "n_coded_statements": 24,
  "confidence": 0.78,
  "coded_statements": [
    {
      "text": "Europa reguliert sich zu Tode...",
      "speaker": "host",
      "economic": 5,
      "social": null,
      "reasoning": "Klare Kritik an Regulierung, pro freier Markt"
    }
  ],
  "notable_quotes": [
    {
      "text": "Wer nicht arbeitet, soll auch nicht essen",
      "context": "Diskussion über Sozialleistungen",
      "quiz_suitable": true
    }
  ]
}
```

## Referenzen

- Eysenck, H. J. (1954). The Psychology of Politics. Routledge & Kegan Paul.
- Nolan, D. (1971). Classifying and Analyzing Politico-Economic Systems. The Individualist.
- Heseltine, M. & Clemm von Hohenberg, B. (2024). Large language models as a substitute for human experts in annotating political text. Research & Politics, 11(1).
- Le Mens, G. et al. (2025). Positioning Political Texts with Large Language Models by Asking and Averaging. Political Analysis.
- Ornstein, J., Blasingame, B. & Truscott, J. (2025). How to Train Your Stochastic Parrot: Large Language Models for Political Texts. Political Science Research and Methods.
- Farjam, M., Meyer, H. & Lohkamp, M. (2025). A Practical Guide on How to Instruct LLMs for Automated Coding During Content Analysis. Social Science Computer Review.
