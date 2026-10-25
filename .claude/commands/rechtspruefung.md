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
> **alle** Prüfpunkte 1–16 durch, besonders 12 (Art. 13 im Einzelnen), 13
> (Betroffenenrechte technisch), 6 (Impressum samt Erreichbarkeit vor der Anmeldung) und
> 15 (Meldeweg gegen den Ablauf in `docs/RUNBOOK.md`). Punkt 7 (Verkauf) und 16 (Marketing)
> sind Vorbereitungslisten, solange es keinen Kaufweg bzw. keine Werbung gibt. Recherchiere den aktuellen Stand von Recht und
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
(Schritt 1), zusätzlich lokal: Server starten (`powershell -NoProfile -ExecutionPolicy
Bypass -File test-server.ps1`) und `python tools/netz-ohne-konto.py` ohne `--live`.

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
2. **Ampel in Alltagssprache** — eine Zeile je Prüfpunkt 1–16: 🔴 fehlt oder falsch
   (Abmahnung/Bußgeld möglich) · 🟡 Risiko oder unklar · 🟢 in Ordnung · ⚪ trifft (noch)
   nicht zu, mit einem Satz warum. Spalten: *was gefunden* · *was schlimmstenfalls passiert*
   (ein Satz, ohne Juristendeutsch) · *wie man es behebt*. Das ist der Teil für den Nutzer —
   verständlich ohne Jura- und IT-Wissen (Vorbild: Rechts-Check vom 18.10.2026).
3. **Geprüfter Stand:** Commit, gepusht ja/nein, Datum.
4. **Befunde**, 🔴 vor 🟡, je mit Fundort, Widerspruch, Fix, Belegart.
5. **Vergleich mit dem Vorbericht:** neu · erledigt · weiter offen. Ohne Vorbericht: „erster
   Durchgang“.
6. **Netzmessung:** je Kennung OK/FEHLER, fremde Hosts falls vorhanden.
7. **Für den Anwalt** — nur neue Fragen.
8. **Nicht prüfbar** — wie im Agenten.
9. **To-do für den Betreiber** — höchstens fünf Punkte, nach Wichtigkeit: was sich **nicht**
   im Code lösen lässt (Angaben, Verträge, Einstellungen bei Anbietern, Anwaltsfragen,
   offene Meldungen nach dem Ablauf in `docs/RUNBOOK.md`).
10. Schluss: keine Rechtsberatung — und ein Satz, wann zusätzlich ein Anwalt gefragt werden
    sollte.

Danach dem Nutzer vorschlagen, welche Befunde behoben werden sollen — nicht selbst beheben.

**Nur echte Fehler:** 🟡 und Vorschläge sind optional; sie werden nur auf Paddys Wunsch umgesetzt und
**nicht automatisch zu neuen Regeln** in CLAUDE.md oder docs. Gemeldet wird nur, was Korrektheit,
Sicherheit, Recht oder Store betrifft.
