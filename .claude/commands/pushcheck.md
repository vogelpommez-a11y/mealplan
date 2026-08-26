---
description: Führt die Push-Checks aus — anwalt und website-security auf Sonnet, ux-reviewer und kvp auf Haiku, weitere Agenten je nach Änderung
---

Führe die Prüfungen vor dem Push aus.

## Zuerst: was hat sich geändert?

```bash
git diff --name-only @{u}..
```

Falls kein Upstream gesetzt ist, nimm die Commits seit dem letzten Push bzw. den
uncommitteten Stand. Nenne die geänderten Dateien kurz, bevor du startest — daran hängt,
welche Agenten laufen.

## Immer laufen (auf Sonnet)

Diese beiden prüfen das, was im Fehlerfall nicht rückholbar ist. Sie laufen bei **jedem**
Push und ausdrücklich **nicht** auf Haiku:

1. **`anwalt`** — Rechtstext gegen Code · `model: sonnet`
2. **`website-security`** — Geheimnisse, personenbezogene Daten, Rules, Service Worker,
   Worker, Historie · `model: sonnet`

## Laufen bei passender Änderung (auf Haiku)

3. **`ux-reviewer`** — nur wenn UI geändert wurde (HTML/CSS, Screens, Komponenten)
4. **`kvp`** — bei jeder inhaltlichen Änderung, nicht bei reinen Doku-Commits

## Laufen bei bestimmten Auslösern

Starte zusätzlich, wenn der Diff das berührt:

| Agent | Auslöser | Modell |
|---|---|---|
| `store-check` | Pro/Bezahlung, Konto/Löschung, Login, Kamera, `vendor/`, `manifest.webmanifest` | sonnet |
| `lieferkette` | alles unter `vendor/`, `tools/firebase-vendor.py`, neue externe Verweise | sonnet |
| `datenschutz-technik` | neuer Dienst, neues Datenfeld, Sharing, Gruppen, Löschlogik | sonnet |
| `doku-waechter` | jede nicht-triviale Änderung an `index.html` | sonnet |

Wenn ein Auslöser nicht zutrifft, sag in einer Zeile, dass der Agent bewusst nicht lief —
nicht einfach weglassen.

## Ausgabe

Gib die Ergebnisse gebündelt und klar getrennt aus. Markiere kritische Funde mit 🔴,
unkritische Hinweise mit 🟡. Findet ein Check nichts: „Keine kritischen Punkte gefunden."

**Prüfe jeden 🔴-Fund am echten Code gegen, bevor du ihn meldest.** Fehlalarme kommen vor,
und ein falscher 🔴 kostet mehr Zeit als die Gegenprüfung.

Fasse am Ende zusammen:
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
