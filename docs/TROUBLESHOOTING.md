# TROUBLESHOOTING.md

# Troubleshooting & bekannte Fallen

Dieses Dokument enthält bekannte Fehlerquellen, historische Bugs und Probleme, die bei Änderungen an Paddy's Mealplan berücksichtigt werden müssen.

## 1. Firebase-Domain vergessen

Eine neue Domain oder Subdomain muss zusätzlich in Firebase Authentication unter den Authorized Domains eingetragen werden.

GitHub Pages allein reicht nicht.

Symptom:

* Seite lädt
* Firebase Login funktioniert nicht
* Cloud-Sync funktioniert nicht

Bei Domainänderungen immer prüfen:

`Firebase Console → Authentication → Settings → Authorized domains`

## 2. Firebase-Regeln im Repository sind nicht zwingend live

`firestore.rules` im Repository ist nur eine Vorlage.

Entscheidend ist der aktuell veröffentlichte Stand in der Firebase Console.

Der Live-Stand ist aus der lokalen Repository-Sicht nicht zuverlässig abrufbar.

Nach Änderungen:

1. Datei prüfen
2. Firebase Console öffnen
3. Rules veröffentlichen
4. anschließend Verhalten testen

## 3. `allow read` ist nicht dasselbe wie `allow get`

In Firestore umfasst:

`allow read`

sowohl:

* `get`
* `list`

Ein früheres Problem erlaubte dadurch das Auflisten geteilter Pläne.

Für Daten, die nur gezielt über eine ID abrufbar sein sollen, nicht versehentlich `allow read` verwenden.

## 4. Firebase-Web-Konfiguration ist kein Secret

`firebaseConfig` in `index.html` ist bei Firebase-Web-Apps grundsätzlich öffentlich.

Nicht als Geheimnis behandeln.

Die eigentliche Zugriffskontrolle erfolgt über:

* Authentication
* Authorized Domains
* Firestore Rules

## 5. `#view` leer trotz HTTP 200

Ein HTTP-200 beweist nicht, dass die App funktioniert.

Ein JavaScript-Syntaxfehler kann das gesamte App-Script stoppen.

Typisches Symptom:

* Header sichtbar
* Footer sichtbar
* `#view` leer

Lösung:

* `--dump-dom` verwenden
* `#view` prüfen
* JavaScript-Konsole/Fehlerursache untersuchen
* nicht nur HTTP-Status betrachten

## 6. Strict Mode und Oktal-Escapes

Unter `"use strict"` sind Oktal-Escapes wie:

```js
"\267"
```

Syntaxfehler.

Das kann das gesamte App-Script töten.

Für PDF-Bytes:

* echtes Zeichen verwenden und über `pdfEsc` wandeln
* oder Backslash korrekt escapen:

```js
"\\267"
```

Das PDF wird selbst erzeugt (`planPdfString` / `downloadPdf`) und verwendet Helvetica/WinAnsi.

`window.print()` nicht als Ersatz verwenden, wenn die Artifact-Sandbox Drucken blockiert.

## 7. Base64-Fotos

`index.html` enthält Base64-Fotos mit sehr langen Zeilen.

Niemals:

* komplette Datei blind lesen
* `cat` verwenden
* Base64 durch den Kontext kopieren

Stattdessen:

* `Grep`
* gezielte Ausschnitte
* Python-Skripte zum Injizieren/Verarbeiten

Beim Kopieren über Chat-/Kontextgrenzen können Base64-Daten beschädigt werden.

## 8. Namensdualität nicht „bereinigen"

Sichtbar:

`Paddy's Mealplan`

Intern:

`wochenkueche` / `recipe`

Diese Namen sind Teil bestehender Daten und Links.

Nicht einfach umbenennen.

Betroffen sind beispielsweise:

* `wochenkueche_v1`
* `wochenkueche_profile_v1`
* `app: "wochenkueche"`
* `state.recipes`
* `getRecipe`
* `data-tab="recipes"`

Eine scheinbar kosmetische Umbenennung kann gespeicherte Daten oder alte Sharing-Links brechen.

## 9. Gruppen-Sync: `plans` nicht doppelt speichern

Wenn `syncGid` aktiv ist, darf `dataJSON` nicht gleichzeitig die Gruppen-`plans` enthalten.

Sonst können:

* `state.plans`
* `data.plans`

gegeneinander laufen.

Mögliche Symptome:

* Snapshot wird ständig als Änderung erkannt
* Endlos-Toast
* Endlos-Push
* wiederholte Render-Zyklen

## 10. Gruppen-Sync: leere Slots

`flattenWeek` gibt leere Slots nicht aus.

Deshalb leere Slots nicht als:

```text
"[]"
```

in der Baseline merken.

Sonst erscheint die Leerung bei jedem Push erneut als Änderung.

Beim Entfernen eines Slots den Slot aus der Baseline entfernen.

## 11. Gruppen-Sync: parallele Pushes

Nicht das gesamte `plans`-Objekt bei jedem Push schreiben.

Sonst kann ein zweiter Push innerhalb von ca. 1–2 Sekunden Änderungen des ersten überschreiben.

Stattdessen:

* ISO-Woche als Dokument
* flache Slot-Felder
* `setDoc(..., { merge: true })`
* Baseline-Diff über `lastPushedSlots`

## 12. UI-Rolle ist keine Security Boundary

`owner`, `edit` und `view` werden in der UI berücksichtigt.

Aber:
**DevTools kann UI-Sperren umgehen.**

Die tatsächliche Zugriffskontrolle muss immer über Firestore Security Rules erfolgen.

Wenn eine Sicherheitsanforderung nur durch `blockedByRole()` erfüllt wird, ist sie nicht sicher.

## 13. Meal `by` enthält nur UID

Meals dürfen bei `by` nur die UID speichern.

Nicht:

* Name
* E-Mail-Adresse
* sonstige unnötige personenbezogene Daten

Der Name wird zur Anzeigezeit über `groupMembers` aufgelöst.

Das verhindert redundante personenbezogene Daten und vereinfacht Löschvorgänge.

## 14. Foto-Credits

`PHOTOS` und `PHOTO_CREDITS` müssen deckungsgleich sein.

Ein Foto ohne passenden Lizenznachweis ist ein relevantes rechtliches Risiko.

Neue Fotos nur hinzufügen, wenn:

1. Lizenz geprüft wurde
2. Quelle dokumentiert wurde
3. `PHOTO_CREDITS` ergänzt wurde

## 15. Teilwort-Matching

Beim Stichwort-Matching können kurze Begriffe ungewollt in anderen Wörtern vorkommen.

Beispiele:

* `eis` steckt in `Rindfleisch`
* `reis` steckt in `Preiselbeere`

Bei Änderungen an `PHOTO_RULES` deshalb immer auf Teilwort-Kollisionen achten.

## 16. `initCarousel()` und Progress-Bar

Bei bestimmten Wizard-/Carousel-Implementierungen benötigt `initCarousel()` intern weiterhin eine feste Anzahl Kind-Elemente.

Diese dürfen nicht einfach entfernt werden, nur weil die sichtbare Progress-Bar keine einzelnen Schritte mehr darstellt.

Platzhalter müssen:

```html
aria-hidden="true"
tabindex="-1"
```

haben.

Sichtbar bleibt ausschließlich:

`.wg-progress-bar`

## 17. Kamera-Test

`navigator.mediaDevices` ist nicht beliebig überschreibbar.

Wenn ein Kamera-Test eine Attrappe benötigt:

* `Object.defineProperty` verwenden
* `new MediaStream()` als echte Basis verwenden
* `getTracks()` kontrollieren
* `stop()` zählen

`video.srcObject` erwartet einen echten `MediaStream`.

## 18. Hängende Tests

Wenn ein isolierter Test hängen bleibt, nicht sofort den Test als fehlerhaft ansehen.

Historisch hat ein hängender Test reale Probleme aufgedeckt.

Beispiel:
`await video.play()` konnte auf bestimmten Geräten dauerhaft hängen.

Ein `catch` hilft dann nicht, weil das Promise nie rejected wird.

Bei hängenden Tests prüfen:

* welches Promise wartet
* ob eine Browser-API nie auflöst
* ob ein Event nie feuert
* ob ein Timer fehlt
* ob ein Mock unrealistisch ist

## 19. Mobile Makro-Raster

Ein früherer Fehler ließ das Makro-Raster mobil mit vier statt zwei Spalten erscheinen.

Bei Änderungen an Makro-/Grid-Komponenten immer explizit mobile Breiten prüfen.

Relevante Breakpoints:

* `max-width: 720px`
* `max-width: 560px`

## 20. Push hängt unter Windows

`git push` kann am Windows Git Credential Manager hängen.

Wenn GitHub CLI bereits authentifiziert ist:

```powershell
gh auth setup-git --hostname github.com
```

`gh` liegt auf diesem Rechner unter:

```text
C:\Program Files\GitHub CLI
```

und ist möglicherweise nicht im PATH.

Bei nicht-interaktiven Shells kann zusätzlich helfen:

```powershell
$env:GIT_TERMINAL_PROMPT=0
```

Nach jedem Push Erfolg überprüfen:

```powershell
git ls-remote origin refs/heads/main
git rev-parse HEAD
```

Die beiden Commit-Hashes müssen übereinstimmen.

## 21. `ROADMAP.html` vergessen

Nach:

* Feature
* relevanter Entscheidung
* Push

`ROADMAP.html` aktualisieren.

Dabei:

* Status verschieben
* Fortschritt aktualisieren
* Datum aktualisieren
* Commit-Hash aktualisieren
* neue Risiken ergänzen

Die Datei bleibt `.gitignore` und wird nicht committed.

## 22. Farbverläufe lassen sich nicht überblenden

`linear-gradient` ist ein `background-image`. Eine `transition` darauf tut nichts — die Farbe
springt hart um.

Wenn ein Verlauf weich wechseln soll: den zweiten Verlauf als eigene Schicht darüberlegen
(`::after` mit `inset: 0`) und dessen `opacity` überblenden. Das läuft zusätzlich auf dem
Compositor statt in der Farbberechnung.

Beispiel im Code: die Pille der Tagesleiste wechselt zwischen Akzent-Rot und Trainings-Blau
über `.db-ind::after`.

## 23. `element.style.transition` ist eine Kurzform und löscht alles andere

Ein inline gesetztes `el.style.transition = "transform 300ms ease"` überschreibt **jede** im CSS
für dieses Element notierte Transition — auch solche für ganz andere Eigenschaften.

Konkreter Fall: `go()` im Karussell setzt beim Mehrtages-Sprung genau das auf `.db-ind`. Eine
Farb-Transition, die auf `.db-ind` selbst stünde, wäre danach still weg — und zwar nur beim
Sprung über mehrere Tage, also im seltenen Fall, der beim Klicken nicht auffällt.

Regel: Sollen inline gesteuerte und CSS-Transitions nebeneinander leben, gehören sie auf
**verschiedene Elemente** (z. B. Element und Pseudo-Element).

## 24. Zwei Bedingungen für einen sichtbaren Zustand

Wenn Fläche und Schrift eines Elements über **unterschiedliche** Bedingungen gesteuert werden,
können sie auseinanderlaufen — und der Fehlerfall ist meist unlesbarer Text.

Konkreter Fall: Die Schriftfarbe des aktiven Tagesreiters hing an einer Klasse des **Knopfes**
(`.db-b.is-train.active`), die Pillenfarbe an einer Klasse der **Leiste** (`.daybar.is-train`,
von JavaScript gesetzt). Passte beides nicht zusammen, stand im Dark-Theme dunkler Text auf
roter Pille.

Regel: eine Quelle für einen Zustand. Wenn schon zwei, dann so, dass der Ausfall **harmlos**
endet — hier: fällt die Klasse aus, bleibt es weiß auf rot statt dunkel auf rot.

## 25. `will-change: transform` und Paint-Eigenschaften vertragen sich nicht

Ein Element mit `will-change: transform` liegt auf einer eigenen Compositor-Schicht. Eine
`transition` auf `box-shadow`, `filter` oder `background` invalidiert diese Schicht in **jedem**
Bild und rastert sie neu.

Auf dem Handy ist das genau die Arbeit, die Scrollen stocken lässt. Solche Zustandswechsel
lieber hart springen lassen — bei kleinen Alphawerten fällt der Sprung ohnehin nicht auf.

## 26. `display: none` ist nicht übergangsfähig

Ein Element, das per `display: none` versteckt ist, kann nicht eingeblendet werden — die
Animation startet nie, das Element poppt auf.

Wenn eine Einblendung gewünscht ist: `width: 0` (bzw. `height: 0`) plus `opacity: 0` und nur die
`opacity` transitionieren. Die Breite springt dabei weiterhin — sie zu animieren wäre ein Layout
pro Bild und damit teurer als der Effekt wert ist.

## 27. Grundregel bei Fehlern

Nicht einfach den sichtbaren Fehler flicken.

Zuerst prüfen:

1. Ist das Problem reproduzierbar?
2. Betrifft es lokale Daten oder Cloud-Daten?
3. Ist es ein State-/Sync-Problem?
4. Ist es ein Browser-API-Problem?
5. Ist es ein Security-Rules-Problem?
6. Gibt es einen bereits dokumentierten historischen Fehler?
7. Lässt sich der betroffene Teil isoliert testen?

Erst danach die eigentliche Ursache beheben.
