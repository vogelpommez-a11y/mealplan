---
description: Führt die Push-Checks aus — website-security und doku-waechter immer, alle anderen Agenten und /code-review nur nach Anlass im Diff
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

**Im Zweifel die höhere Stufe.** Die Stufe gilt für die Prüfstände davor
(`CLAUDE.md` Abschnitt 11): Ab B muss `alle-pruefstaende.py --betroffen` gelaufen sein, in C
zusätzlich `abnahme-mobil.py`. Ist das nicht passiert, sag es, statt den Pushcheck trotzdem grün
zu melden. **Die Agenten richten sich NICHT nach der Stufe, sondern nach dem Anlass** (unten).

**Warum nach Anlass:** Bis 18.10.2026 liefen alle Agenten bei jedem Push, danach je nach Stufe.
Auch so dauerte der Pushcheck oft 15–25 Minuten, länger als die Änderung selbst (Paddy, 25.10.2026). Was ein Agent ohne Anlass prüfen
würde, sieht er ohnehin in der monatlichen Wartung (`/rechtspruefung` über die ganze App).

## Immer

1. **`website-security`** · `model: sonnet` — Geheimnisse, personenbezogene Daten, Rules,
   Service Worker, Worker, Historie. Läuft bei **jedem** Push: Das Repo ist öffentlich, ein
   Leck in einem Doku- oder Werkzeugtext ist genauso wenig rückholbar wie eines im App-Code.
2. **`doku-waechter`** · `model: sonnet` — bei jeder nicht-trivialen Änderung.
3. Bei Änderungen unter `.claude/`: `python tools/wartung-check.py` — muss ohne Rot sein.

## Nur nach Anlass im Diff

| Agent | Läuft, wenn der Diff das berührt | Modell |
|---|---|---|
| `/code-review` (Skill, `medium`) | Sync, Speichern, Löschen, Gruppen, Teilen, Rechnen (Makros, Mengen), Login/Konto, `sw.js`, `worker/`, `firestore.rules`, `lib/*.js`. **Nicht** bei reinen Texten, Styles, Markup | — |
| `anwalt` | `data/rechtstexte.js`, neues Datenfeld, neuer Dienst/externer Verweis, Teilen, Gruppen, Löschlogik, Konto, Bezahlung, Werbeaussagen in UI-Texten | sonnet |
| `kvp` | neue Funktion oder umgebauter Ablauf (mehr als eine Stelle). **Nicht** bei Fehlerbehebung, Text, kleinen Styles | sonnet |
| `ux-reviewer` | neuer oder umgebauter Bildschirm/Dialog. **Nicht** bei Textkorrektur oder einzelnem Style | haiku |
| `store-check` | Pro/Bezahlung, Konto/Löschung, Login, Kamera, `vendor/`, `manifest.webmanifest` | sonnet |
| `lieferkette` | alles unter `vendor/`, `tools/firebase-vendor.py`, neue externe Verweise | sonnet |
| `datenschutz-technik` | neuer Dienst, neues Datenfeld, Sharing, Gruppen, Löschlogik | sonnet |

Die Anlass-Agenten **parallel** starten, nicht nacheinander.

## Zeiten festhalten

Nenne am Ende, was wie lange gedauert hat (Prüfstände, Handy-Prüfung, jeder Agent). Paddy
entscheidet damit, ob weiter gekürzt wird (25.10.2026).

Wenn ein Auslöser nicht zutrifft, sag in einer Zeile, dass der Agent bewusst nicht lief —
nicht einfach weglassen.

## Ausgabe

Gib die Ergebnisse gebündelt und klar getrennt aus. Markiere kritische Funde mit 🔴,
unkritische Hinweise mit 🟡. Findet ein Check nichts: „Keine kritischen Punkte gefunden."

**Nur echte Fehler:** 🟡 und Vorschläge sind optional; sie werden nur auf Paddys Wunsch umgesetzt und
**nicht automatisch zu neuen Regeln** in CLAUDE.md oder docs. Prüfer melden nur, was Korrektheit,
Sicherheit, Recht oder Store betrifft.

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
