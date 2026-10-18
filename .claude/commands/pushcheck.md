---
description: Führt die Push-Checks in drei Stufen aus — website-security immer, anwalt, kvp und /code-review ab Stufe B, ux-reviewer in Stufe C, weitere Agenten nach Auslöser
---

Führe die Prüfungen vor dem Push aus — **so viel wie nötig, nicht mehr.**

## Zuerst: was hat sich geändert, und welche Stufe ist das?

```bash
git diff --name-only @{u}..
```

Falls kein Upstream gesetzt ist, nimm die Commits seit dem letzten Push bzw. den
uncommitteten Stand. Nenne die geänderten Dateien kurz und **die Stufe**, bevor du startest:

| Stufe | Geändert | Beispiele |
|---|---|---|
| **A** | **nichts an der App** | `docs/`, `plans/`, `.claude/`, `tools/`, `README.md`, `.github/` |
| **B** | App-Code, aber nichts, was man **sieht oder bedient** | Sync, Rechnen, Speichern, `firestore.rules`, `sw.js`, `worker/`, Werkzeuge, die Nutzerdaten anfassen (`tools/firestore-*.py`, `shared-aufraeumen.py`, `konten-inaktiv.py`) |
| **C** | etwas, das man **sieht oder bedient** | Markup, `css/`, UI-Texte, Rechtstexte, Bilder, Abläufe |

**Im Zweifel die höhere Stufe.** Die Stufe gilt auch für die Prüfstände davor
(`CLAUDE.md` Abschnitt 11): Ab B muss `alle-pruefstaende.py` gelaufen sein, in C zusätzlich
`abnahme-mobil.py`. Ist das nicht passiert, sag es, statt den Pushcheck trotzdem grün zu melden.

Warum Stufen (18.10.2026): Bis dahin liefen `anwalt`, `kvp` und die übrigen bei **jedem** Push,
auch wenn sich nur Doku oder Prüfer geändert hatten. `anwalt` prüft Rechtstext gegen App-Code —
ohne geänderten App-Code gibt es dort nichts Neues zu finden. Die ganze App sieht er ohnehin
monatlich in `/rechtspruefung`.

## Stufe A — immer

1. **`website-security`** · `model: sonnet` — Geheimnisse, personenbezogene Daten, Rules,
   Service Worker, Worker, Historie. Läuft in **jeder** Stufe: Das Repo ist öffentlich, ein
   Leck in einem Doku- oder Werkzeugtext ist genauso wenig rückholbar wie eines im App-Code.
2. **`doku-waechter`** · `model: sonnet` — bei jeder nicht-trivialen Änderung, in jeder Stufe.
3. Bei Änderungen unter `.claude/`: `python tools/wartung-check.py` — muss ohne Rot sein.

## Stufe B — zusätzlich

4. **`anwalt`** · `model: sonnet` — Rechtstext gegen Code.
5. **`kvp`** · `model: sonnet` — bei jeder inhaltlichen Änderung
   (seit 18.10.2026 auf Sonnet: Er soll Nährwerte und Mengen nachrechnen, dafür ist Haiku zu knapp).
6. **`/code-review`** (eingebauter Skill, Stufe `medium`) — wenn `index.html`, `data/*.js`,
   `lib/*.js`, `sw.js` oder `worker/` geändert wurden. Ziel sind die Änderungen seit dem letzten
   Push. Er ist die **Fehlersuche**: `kvp` verweist Korrektheitsfehler ausdrücklich hierher, und
   bis zum 18.10.2026 rief ihn kein Ablauf auf. Nebenbei prüft er, ob die Änderung die Regeln
   aus `CLAUDE.md` einhält. Seine Funde laufen durch dieselbe Gegenprüfung wie alle anderen.

## Stufe C — zusätzlich

7. **`ux-reviewer`** · `model: haiku` — Übersichtlichkeit der geänderten UI.

## Laufen bei bestimmten Auslösern

Starte zusätzlich, **unabhängig von der Stufe**, wenn der Diff das berührt:

| Agent | Auslöser | Modell |
|---|---|---|
| `store-check` | Pro/Bezahlung, Konto/Löschung, Login, Kamera, `vendor/`, `manifest.webmanifest` | sonnet |
| `lieferkette` | alles unter `vendor/`, `tools/firebase-vendor.py`, neue externe Verweise | sonnet |
| `datenschutz-technik` | neuer Dienst, neues Datenfeld, Sharing, Gruppen, Löschlogik | sonnet |

Wenn ein Auslöser nicht zutrifft, sag in einer Zeile, dass der Agent bewusst nicht lief —
nicht einfach weglassen.

## Ausgabe

Gib die Ergebnisse gebündelt und klar getrennt aus. Markiere kritische Funde mit 🔴,
unkritische Hinweise mit 🟡. Findet ein Check nichts: „Keine kritischen Punkte gefunden."

**Prüfe jeden 🔴-Fund am echten Code gegen, bevor du ihn meldest.** Fehlalarme kommen vor,
und ein falscher 🔴 kostet mehr Zeit als die Gegenprüfung.

**So wird gegengeprüft: widerlegen, nicht bestätigen.** Versuche, den Fund zu Fall zu bringen,
aus drei Blickwinkeln (übernommen aus dem Anthropic-Plugin `claude-security`, Agent
`scan-verifier`):

| Blickwinkel | Frage |
|---|---|
| **Erreichbarkeit** | Kommt ein Nutzer, ein fremdes Gruppenmitglied oder ein geteilter Link überhaupt an diese Stelle? Gibt es den Weg in der ausgelieferten App, nicht nur im Prüfstand? |
| **Wirkung** | Was passiert dann wirklich: Datenverlust, Leck, falscher Rechtstext, falsche Zahl? Oder nur „sieht unschön aus“? |
| **Schutz** | Hält schon etwas anderes dagegen: eine Firestore-Regel, `esc()`, ein Fallback, eine Prüfung eine Ebene höher? **Nur gelesenen Schutz zählen**, keinen vermuteten |

Ein 🔴 bleibt nur stehen, wenn für alle drei eine Fundstelle (`datei:zeile`) genannt werden kann.
Fehlt eine, wird er 🟡 mit dem Satz, was ihn bestätigen würde. Umgekehrt: Einen Fund nie mit
einem **erfundenen** Schutz wegerklären, das ist derselbe Fehler in die andere Richtung.
Rechtliche Funde (`anwalt`) lassen sich nicht immer so zerlegen. Dort gilt die Belegart des
Agenten (*beobachtet* oder *abgeleitet*).

Fasse am Ende zusammen:
- Welche Stufe, und an welcher Datei sie sich entschieden hat?
- Liegt mindestens ein 🔴 vor?
- Welche Agenten liefen, welche bewusst nicht?
- Was ist von hier aus grundsätzlich nicht prüfbar (Firebase-Konsole, Cloudflare-Secrets,
  Store-Konten)?

## Zum Schluss: den Stand festhalten

Wenn kein 🔴 offen ist, halte fest, welcher Commit geprüft wurde:

```bash
git rev-parse HEAD > .claude/.letzter-pushcheck
```

Der Push-Wächter (`.claude/hooks/push-waechter.py`) liest diese Datei und fragt vor
`git push` nach, wenn seitdem weitergearbeitet wurde. **Bei offenem 🔴 nicht schreiben** —
dann soll die Rückfrage beim Push ausdrücklich kommen.
