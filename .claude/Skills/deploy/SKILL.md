---
name: deploy
description: Bringt Paddy's Mealplan live — Push auf main, Verifikation, dass Remote und lokaler HEAD übereinstimmen, und die Prüfung, dass GitHub Pages die neue Fassung tatsächlich ausliefert. Enthält auch den Rückweg, wenn live etwas kaputt ist.
---

# Deploy

Ein Push auf `main` **ist** das Deployment. GitHub Pages baut automatisch, es gibt keinen
Zwischenschritt und keine Freigabe. Entsprechend sorgfältig.

## Vorher

1. `python syntax-check.py --alles` — grün.
2. `/smoke` — `#view` gefüllt.
3. `/pushcheck` — kein offenes 🔴.
4. `git diff` gelesen, keine unbeabsichtigten Änderungen.
5. Betroffene Doku aktualisiert (`/doku-waechter` oder selbst geprüft).

Der Push-Wächter (`.claude/hooks/push-waechter.py`) fragt nach, wenn Schritt 3 für diesen
Stand nicht dokumentiert ist. Das ist eine Rückfrage, kein Verbot — aber sie ernst nehmen.

## Push

```powershell
git push origin main
```

**Wenn der Push in einer nicht-interaktiven Shell hängt** und GitHub CLI bereits
angemeldet ist:

```powershell
gh auth setup-git --hostname github.com
```

`gh` liegt unter `C:\Program Files\GitHub CLI` und ist möglicherweise nicht im PATH.
Bei Bedarf zusätzlich `$env:GIT_TERMINAL_PROMPT=0`.

## Verifizieren — beide Stufen

**Stufe 1: Kam der Commit an?**

```powershell
git ls-remote origin refs/heads/main
git rev-parse HEAD
```

Beide Hashes müssen übereinstimmen. Tun sie es nicht, ist der Push nicht durch — dann
hier aufhören und die Ursache suchen.

**Stufe 2: Liefert Pages die neue Fassung aus?**

Der Bau dauert. Die Seite mit einem Cache-Buster abrufen und auf eine Zeichenfolge prüfen,
die es **nur** im neuen Stand gibt — nicht auf die Dateigröße, nicht auf HTTP 200.

```powershell
$url = "https://www.paddysmealplan.de/?cb=$(Get-Random)"
(Invoke-WebRequest -Uri $url -UseBasicParsing).Content.Contains("<neue Zeichenfolge>")
```

Bei Bedarf in einer kleinen Schleife mit Pause wiederholen. Erst wenn das `true` ist, ist
der Deploy fertig.

**Bei einer Änderung an `sw.js`:** Wurde `VERSION` erhöht? Ohne das räumt `activate` den
alten Cache nicht weg, und Nutzer bleiben auf dem alten Stand hängen.

## Danach

- `ROADMAP.html` aktualisieren: Karte verschieben, Fortschritt, Datum, Commit-Hash.
- Wenn `/pushcheck` sauber war, hat es den Marker geschrieben — sonst nachtragen.

## Wenn live etwas kaputt ist

Ruhe. Es gibt keinen Build, deshalb ist der Rückweg kurz.

**Zuerst feststellen, was gilt.** Ist die Seite leer (`#view` leer bei HTTP 200)? Dann ist
es fast immer ein Syntaxfehler — `python syntax-check.py --alles` sagt in einer Sekunde,
welche Datei und welche Zeile. Ohne `--alles` bliebe ein Fehler in `data/` oder `lib/`
unentdeckt.

**Zurück auf den letzten heilen Stand:**

```powershell
git revert <kaputter-commit>
git push origin main
```

`git revert` statt `reset --hard`: Es erzeugt einen neuen Commit, der die Änderung
rückgängig macht, ohne die Historie umzuschreiben. Ein erzwungener Push auf `main` würde
den Stand zerstören, auf den sich alles andere bezieht.

Danach **Stufe 2 der Verifikation erneut** — der Revert ist erst live, wenn Pages ihn
ausliefert.

**Der Service Worker kann einen kaputten Stand festhalten.** Navigationen sind
network-first, deshalb greift ein Deploy normalerweise sofort. Hängt trotzdem jemand fest,
hilft ein erhöhtes `VERSION` in `sw.js` mit anschließendem Deploy.

**Firebase-Regeln sind nicht Teil des Deploys.** `firestore.rules` im Repo ist nur die
Vorlage. Eine Regeländerung wird erst wirksam, wenn sie in der Firebase-Konsole
veröffentlicht wurde — ein Push allein ändert dort gar nichts.
