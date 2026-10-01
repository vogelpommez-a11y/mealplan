---
description: Monatlicher Rechts-Durchgang über die ganze App — anwalt auf Opus mit Recherche-Auftrag, parallel die Netzmessung ohne Konto. Pflichtschritt der Wartung und vor jeder Store-Einreichung
---

Führe den großen Rechts-Durchgang aus. Er ergänzt `/pushcheck`, er ersetzt ihn nicht:
Der Pushcheck sieht nur den Diff, dieser Durchgang die **ganze App**. Am 30.09.2026 fand
genau dieser Durchgang weit mehr als der Pushcheck — darunter einen 🔴, den kein Diff je
gezeigt hätte (`docs/TESTING.md`, Abschnitt „Rechtsprüfung“).

**Dieser Befehl ändert nichts an der App.** Er meldet. Fixes erst nach Freigabe durch den
Nutzer.

## 1. Stand festhalten

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
git status --short
```

Weichen HEAD und Remote ab oder gibt es uncommittete Änderungen an `index.html`, `data/`,
`lib/` oder `sw.js`: Die Netzmessung läuft dann **zusätzlich lokal** (Schritt 2b).

Lies den jüngsten Vorbericht `plans/rechtspruefung-*.md`, falls vorhanden — er wird in
Schritt 4 verglichen.

## 2. Parallel starten

**a) `anwalt` auf Opus über die ganze App** — `subagent_type: anwalt`, `model: opus`.
Auftrag sinngemäß:

> Prüfe nicht den Diff, sondern die ganze App: alle Rechtstexte (`data/rechtstexte.js`,
> Impressum/Datenschutz in `index.html`) gegen den gesamten Code, `firestore.rules`,
> `worker/`, `sw.js`, `tools/firestore-backup.py` und `tools/firestore-restore.py`. Gehe
> **alle** Prüfpunkte 1–13 durch, besonders 12 (Art. 13 im Einzelnen) und 13
> (Betroffenenrechte technisch). Recherchiere den aktuellen Stand von Recht und
> Rechtsprechung zu jedem Punkt, an dem sich seit dem letzten Bericht etwas geändert
> haben kann; Quelle und Abrufdatum dahinter. Offene Fragen für den Anwalt stehen in
> `docs/DATENSCHUTZ-INTERN.md` — nenne nur neue, keine Wiederholungen.

Opus ist hier Absicht, nicht Versehen: Sonnet ist für den Diff gut genug, für die ganze
App nicht.

**b) Netzmessung ohne Konto** — im Hintergrund:

```bash
python tools/netz-ohne-konto.py --live
```

Vier Browserkennungen, frische Profile, keine Anmeldung. Vorher alle `chrome.exe`/
`msedge.exe` beenden (`docs/TROUBLESHOOTING.md` §177). Ist der Stand nicht gepusht
(Schritt 1), zusätzlich lokal: Server starten (`powershell -NoProfile -File
test-server.ps1`) und `python tools/netz-ohne-konto.py` ohne `--live`.

## 3. Gegenprüfen

**Jeden 🔴 am echten Code nachsehen, bevor er gemeldet wird.** Ein *abgeleiteter* 🔴 des
Agenten ist ein Verdacht — entweder bestätigen (Fundstelle) oder als 🟡 mit dem, was ihn
bestätigen würde, weitergeben. Ein falscher 🔴 kostet mehr als die Gegenprüfung.

Schlägt die Netzmessung fehl, ist das ein 🔴 gegen Ziffer 3/5 der Datenschutzerklärung und
gegen Apple 2.5.2 — es sei denn, die Messung selbst ist gescheitert (Browser, Netz). Dann
erst ohne Parallellast nachfahren, bevor die App verdächtigt wird.

## 4. Bericht

Im Chat **und** als Datei `plans/rechtspruefung-JJJJ-MM-TT.md` (heutiges Datum; `plans/` ist
gitignored, der Bericht wird nie committet). Die Datei ist zugleich der Nachweis, den
`python tools/wartung-check.py --setze` verlangt — **nur schreiben, wenn der Durchgang
wirklich gelaufen ist**, auch wenn er scheiterte (dann steht das drin).

Aufbau:

1. **Einzeiler:** Widerspruch zwischen Rechtstext und Code — ja oder nein. Netzmessung
   sauber — ja oder nein.
2. **Geprüfter Stand:** Commit, gepusht ja/nein, Datum.
3. **Befunde**, 🔴 vor 🟡, je mit Fundort, Widerspruch, Fix, Belegart.
4. **Vergleich mit dem Vorbericht:** neu · erledigt · weiter offen. Ohne Vorbericht: „erster
   Durchgang“.
5. **Netzmessung:** je Kennung OK/FEHLER, fremde Hosts falls vorhanden.
6. **Für den Anwalt** — nur neue Fragen.
7. **Nicht prüfbar** — wie im Agenten.
8. Schluss: keine Rechtsberatung.

Danach dem Nutzer vorschlagen, welche Befunde behoben werden sollen — nicht selbst beheben.
