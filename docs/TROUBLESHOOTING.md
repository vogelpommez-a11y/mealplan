# TROUBLESHOOTING.md

# Troubleshooting & bekannte Fallen

Dieses Dokument enthält bekannte Fehlerquellen, historische Bugs und Probleme, die bei Änderungen an Paddy's Mealplan berücksichtigt werden müssen.

<!-- REGISTER-ANFANG (erzeugt aus den Ueberschriften, nicht von Hand pflegen) -->

**Register — 137.** Chronologisch gewachsen: je hoeher die Nummer,
desto juenger der Fund. Wer eine Falle sucht, sucht hier zuerst; die Ueberschrift sagt
jeweils, worum es geht. **Nicht die ganze Datei lesen** — sie ist rund 286 KB gross.

| # | Abschnitt |
|---|---|
| 1 | Firebase-Domain vergessen |
| 2 | Firebase-Regeln im Repository sind nicht zwingend live |
| 3 | `allow read` ist nicht dasselbe wie `allow get` |
| 4 | Firebase-Web-Konfiguration ist kein Secret |
| 5 | `#view` leer trotz HTTP 200 |
| 6 | Strict Mode und Oktal-Escapes |
| 7 | Sehr lange Zeilen in `index.html` (früher: Base64-Fotos) |
| 8 | Namensdualität nicht „bereinigen" |
| 9 | Gruppen-Sync: `plans` nicht doppelt speichern |
| 10 | Gruppen-Sync: leere Slots |
| 11 | Gruppen-Sync: parallele Pushes |
| 12 | UI-Rolle ist keine Security Boundary |
| 13 | Meal `by` enthält nur UID |
| 14 | Foto-Credits |
| 15 | Teilwort-Matching |
| 16 | `initCarousel()` und Progress-Bar |
| 17 | Kamera-Test |
| 18 | Hängende Tests |
| 19 | Mobile Makro-Raster |
| 20 | Push hängt unter Windows |
| 21 | `ROADMAP.html` vergessen |
| 22 | Farbverläufe lassen sich nicht überblenden |
| 23 | `element.style.transition` ist eine Kurzform und löscht alles andere |
| 24 | Zwei Bedingungen für einen sichtbaren Zustand |
| 25 | `will-change: transform` und Paint-Eigenschaften vertragen sich nicht |
| 26 | `display: none` ist nicht übergangsfähig |
| 27 | Gruppen-Wartezustand: Zeitfenster zwischen Beitritt und Aktivierung |
| 28 | QR-Code im Dark Theme |
| 29 | `window.CloudGroup` hat kein `loadRecipes` |
| 30 | ZXing-SVG-QR-Code braucht ein eigenes `viewBox` |
| 31 | Zwei-Konten-Race im Gruppen-Wartezustand |
| 32 | Popover in `.day` wird von `overflow: hidden` abgeschnitten |
| 33 | `state.plan`-Einträge nie direkt an `getRecipe()` übergeben |
| 34 | Zusammengeführte Listen müssen sortiert sein, sonst schaukeln sich zwei Geräte auf |
| 35 | Ein gescheiterter Lesevorgang darf nie zu einem Schreibvorgang werden |
| 36 | Der lokale Teststand schreibt in die echte Cloud |
| 37 | Löschen muss beide Speicher treffen, nicht nur `localStorage` |
| 38 | hitSlop bei benachbarten Knöpfen: die Enge gilt nur in einer Achse |
| 39 | CSS-`transition` greift nicht an Elementen aus `view.innerHTML` |
| 40 | `navigator.share()` verliert die Nutzer-Aktivierung nach einem `await` |
| 41 | Open Food Facts liefert `serving_size` nicht zuverlässig |
| 42 | Wochenplan bleibt beim Zurückwischen zwischen zwei Tagen stehen |
| 43 | Grundregel bei Fehlern |
| 44 | Firestore sortiert Map-Schlüssel — Fortsetzung von Ziffer 34 |
| 45 | `fromCache` ist kein Beweis |
| 46 | Ein Reload vor dem erfolgreichen Push kann eine lokale Änderung innerhalb einer bereits |
| 47 | Zweiter Tab bekommt Änderungen des ersten nicht live mit (unbestätigt, nicht root-ursächlich geklärt) |
| 48 | `deleteAccountFlow()` kann durch einen einzigen fremden oder toten `shared/{id}`-Eintrag |
| 49 | `wipeCache()` stand am falschen Objekt und lief dadurch nie (gefunden und behoben) |
| 50 | Messenger-Crawler führen kein JavaScript aus — statische `og:`-Tags reichen für geteilte Links nicht |
| 51 | `onRecipesRemote()` ersetzt Rezept-Objekte statt sie zu mutieren — langlebige Ansichten müssen immer über `getRecipe(id)` zugreifen |
| 52 | Ein Element ausblenden, das gerade den Fokus hat, löst `focusout` aus — Aufklapp-Zeilen schlossen sich sofort wieder |
| 53 | FLIP wird unsichtbar, wenn Ursprung und Ziel gleich breit sind |
| 54 | Im Hintergrund-Tab misst kein Animationstest etwas Verlässliches |
| 55 | Ein Transform über die halbe Bildschirmhöhe ist auf dem Handy zu teuer |
| 56 | Grid-Auto-Platzierung rutscht hoch, wenn eine Reihe `display: none` ist |
| 57 | Höhe eines Sheets nie aus einzelnen Variablen summieren |
| 58 | `overflow-y: auto` macht die andere Achse mit zum Scroller — und blockiert die Wischgeste |
| 59 | Ein Aufklapper, der seinen eigenen Auslöser verschiebt, ist praktisch nicht schließbar |
| 60 | `flex-wrap: wrap` in der Kopfzeile — ein Umbruch, der die Leiste verdoppelt |
| 61 | Ein Farbstreifen im Fensterrand — warum das kein zweiter Scroller wird |
| 62 | `.btn.icon-gh` schlägt eine einzelne Klasse — der Knopf bleibt quadratisch |
| 63 | Kamera-Bühne ≠ Kamera-Bild: warum der Barcode-Scanner nur quer funktionierte |
| 64 | `focusMode` gibt es nur in Chromium — der Nahfokus ist kein Bug, der sich überall fixen lässt |
| 65 | Hochformat lässt sich im Web auf dem iPhone nicht erzwingen — das Querformat muss taugen |
| 66 | Ein offener Scanner + `--virtual-time-budget` = hängender Prüfstand |
| 67 | Das Logo im PDF hängt jetzt am Netzpfad, nicht mehr am CSS |
| 68 | Der Service Worker lud 1 MB vor, das kaum jemand brauchte |
| 69 | Ein JSON-LD-Block ist kein JavaScript — der Syntax-Check lief prompt darauf auf |
| 70 | Vorschaubilder werden bei WhatsApp, Facebook und Co. **serverseitig** zwischengespeichert |
| 71 | Leere `catch`-Blöcke sind jetzt gefüllt — und dabei zwei Fallen aufgetaucht |
| 72 | Der Rückblick zeigte Streuung und sah dabei wie Zielerreichung aus |
| 73 | Ein neues Feld im Slot-Eintrag wäre am Sync fast unbemerkt verschwunden |
| 74 | Von Hand gesetzte Kalorienziele wurden von der nächsten Wiegung überschrieben |
| 75 | Eine CSS-Regel, die nie griff — und die es auch nicht sollte |
| 76 | `if (wert)` statt `if ("feld" in objekt)` — die Lücke zeigte in die falsche Richtung |
| 77 | Der Baseline-Push lief los, bevor feststand, ob das Konto Pro hat |
| 78 | Eine Sperre nur beim Schreiben hätte bei jedem Start Daten gekostet |
| 79 | `leaveGroup()` hätte ein Gratis-Konto in der Gruppe festgehalten |
| 80 | Ein Einzeiler zerlegte den Prüfstand — und der Fehler war unsichtbar |
| 81 | Cloud-Sync war einen Tag lang Pro — die Rücknahme war die richtige Entscheidung |
| 82 | Ein Feld, das nur an einer von drei Stellen rechnete — und deshalb falsch einkaufte |
| 83 | Geschätzte Nährwerte in einem Rezept sehen aus wie gerechnete |
| 84 | Ein falsch zugeordnetes Lebensmittel ist schlimmer als ein fehlendes |
| 85 | Freitext-Zutaten fallen aus jeder Rechnung |
| 86 | Stichwort-Fotos greifen im Rezeptbuch daneben — an den Regeln zu drehen ist der falsche Hebel |
| 87 | „High Protein" als Tag und „Proteinreich" als Badge sind zwei Quellen für dieselbe Aussage |
| 88 | Das Geschirr aus der Kategorie allein legt Brot in eine Schüssel |
| 89 | Ein Dateiname darf nicht aus der Katalog-`id` abgeleitet werden |
| 90 | `z-index` ohne `position` ist wirkungslos — und ein Kommentar ist kein Code |
| 91 | Mitgelieferte Daten vor dem Onboarding einsetzen heißt, sie ohne Profilwissen zu wählen |
| 92 | `array.filter(fn)` übergibt den Index — und ein abgebrochener Repaint sieht aus wie ein Filter ohne Wirkung |
| 93 | Ein Rückgabewert, n-mal eingefügt: derselbe Eintrag steht dann n-mal im Plan — als ein Objekt |
| 94 | `.btn` in einer Reihe mit `.btn.icon-gh` sieht gleich groß aus — und ist kein Touch-Ziel |
| 95 | Der Automatismus braucht eine engere Kategorie-Bindung als der Picker |
| 96 | Vier Portionen desselben Snacks — dieselbe Formel, zwei Bedeutungen |
| 97 | Eine Klammer zu früh: der halbe 680px-Block landete in einer 360px-Abfrage |
| 98 | Zwei Slots, dieselbe Menge, dieselbe Bewertung, derselbe Index — dasselbe Ergebnis |
| 99 | Eine Datumsrechnung in der Vergleichsfunktion eines `sort()` |
| 100 | Ein `uids.push()` am fremden Eintrag hätte den Undo-Pfad ausgehebelt |
| 101 | Mitgliederlimit: drei Stellen, die den ganzen Umbau still gekippt hätten |
| 102 | 61 Rezepte, 51 Namen: zwei Zuflüsse, eine falsche Verdächtige |
| 103 | Zwei Planer gleichzeitig: die Funktion war unschuldig, der Zeitpunkt nicht |
| 104 | Einladungscodes überlebten jeden Gruppenwechsel |
| 105 | Einladungscode verbrauchen: warum das zwei Regel-Deploys braucht, nicht einen |
| 106 | Firebase lokal: der eine Pfad, der die App sonst zweimal startet |
| 107 | Zwei `history.back()` im selben Tick sind nur eines |
| 108 | Ein `undefined` im Ziel legte die ganze Cloud-Sicherung still |
| 109 | Zwei Prüfwerkzeuge, die seit ihrer Entstehung nichts geprüft haben |
| 110 | Das versprochene `render()`, das es nie gab |
| 111 | Eine Filterschwelle direkt neben der Zahl, die die App selbst erzeugt |
| 112 | `weekLabel()` war zweimal deklariert — und die falsche gewann |
| 113 | Ein neues Icon, das nur die halbe `viewBox` benutzt |
| 114 | Die eine ID-Ausgabe ohne `esc()` — gefunden beim Lesen der Nachbarzeilen |
| 115 | Ein neues Sync-Feld braucht ZWEI Merge-Stellen — der isolierte Prüfstand sieht nur eine |
| 116 | `innerHTML` wirft die Scrollposition NICHT weg — zwei Runden toter Code dafür |
| 117 | Die 16-px-Regel gegen den iOS-Zoom griff im Querformat nicht |
| 118 | Ein Guard, der nach innen wandert, erzeugt Datensätze ohne ein Feld, auf das anderswo still gebaut wird |
| 119 | Ein Wächter, der die eigenen Werkzeuge blockiert — und `core.ignorecase` als stiller Mitwisser |
| 120 | Eine Schutzregel, die von der Regel überholt wird, die sie schützen soll |
| 121 | Ein freundlicher Toast ist auch ein Schlucken |
| 122 | Ein Zähler, der beim Start wandert — und kein Fehler ist |
| 123 | Eine Ausnahme, die vor den Verboten steht, hebelt sie alle aus |
| 124 | Ein Zustand ohne Wochenbezug neben zwei Wochenreitern |
| 125 | Gruppe verlassen: der Altbestand kam als Dublette zurück |
| 126 | Ein leeres Leseergebnis, das eine Entscheidung trägt |
| 127 | Ein zugewiesenes Meal ließ sich nicht aus dem Plan löschen |
| 128 | Der Beitretende verlor seine Woche — und eine Migration räumte fremden Bestand auf |
| 129 | „Synchronisiert“, während nichts mehr ankam |
| 130 | Ein Gericht, das niemandem gehörte — und ein leeres Array, das `true` ist |
| 131 | Ein Prüfstand, der immer grün meldete, weil er nie lief |
| 132 | „Mengen × Mitglieder: Aus“ galt nur für die Hälfte der Rechnung |
| 133 | Wer aus einer Gruppe entfernt wird, bleibt für immer daran hängen |
| 134 | Der vergiftete Offline-Cache — Ursache der `permission-denied`-Phasen |
| 135 | Der Home-Screen-Verweis auf dem iPhone ist ein zweites Gerät |
| 136 | Ein `let` am Rand eines Schnitts: geteilter Zustand bricht die Aufteilung |
| 137 | Ein Cache in einer Fassade ist eine Kopie, kein Cache |

<!-- REGISTER-ENDE -->

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

* **zuerst `python syntax-check.py --alles`** — benennt Fehlermeldung und Zeile in rund einer Sekunde,
  statt sie im leeren `#view` zu suchen (siehe `docs/TESTING.md`, Abschnitt 0)
* `--dump-dom` verwenden
* `#view` prüfen
* JavaScript-Konsole/Fehlerursache untersuchen
* nicht nur HTTP-Status betrachten

**Seit dem 10.08.2026 ist dieser Fall vermeidbar.** Der Syntax-Check prüft jeden `<script>`-Block
mit derselben V8-Engine, die die App ausführt, ohne ihn auszuführen. Er läuft vor dem Smoke-Test
und vor jedem Push. Dieser Punkt und Punkt 6 wären damit beide sofort gefunden worden.

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

## 7. Sehr lange Zeilen in `index.html` (früher: Base64-Fotos)

`index.html` ist ~0,76 MB gross und rund 12.860 Zeilen lang; dazu kommen `css/`,
`data/` und `lib/` (siehe `docs/MODULE.md`).

Niemals:

* komplette Datei blind lesen
* `cat` verwenden

Stattdessen:

* `Grep`
* gezielte Ausschnitte mit Offset/Limit
* Python-Skripte zum Injizieren/Verarbeiten

**Nachtrag 27.08.2026 — die Begründung stimmte nicht mehr.** Dieser Abschnitt und
`CLAUDE.md` §10 sprachen weiter von „Base64-Fotos in der Datei". Nachgezählt: **null**. Die
Meal-Fotos liegen seit dem Bildumbau als 32 Dateien in `img/`; der einzige Treffer auf
`base64,` im Quelltext ist die Prüf-Regex in `safeImage()` (Zeile 6648). Was zur Laufzeit
noch als `data:image;base64` auftaucht, sind Bilder des Nutzers aus `localStorage` bzw.
Firestore — die Warnung fürs Kopieren über Kontextgrenzen gilt dort weiter, im Quelltext
gibt es nichts mehr zu beschädigen.

Die Warnung „nicht blind lesen" bleibt richtig — wegen der Dateigrösse, nicht wegen Base64.

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

## 27. Gruppen-Wartezustand: Zeitfenster zwischen Beitritt und Aktivierung

Zwischen `prepareGroup()` und der Aktivierung (`finalizeGroupActivation()`) ändert der Owner
weiter in seinem **eigenen** Konto, nicht in der Gruppe (`state.groupId` bleibt leer). Das kann
kurzzeitig verwirren, wenn man erwartet, dass ab „Person einladen" schon alles synchron läuft.

Beim Nachtragen des Wochenplans werden nur Slots geschrieben, die in der Gruppe noch **leer**
sind (`have[slot]` geprüft in `finalizeGroupActivation()`). Ein Slot, den die beigetretene Person
in der Zwischenzeit selbst gefüllt hat, wird nicht überschrieben. Wer das beim Testen prüft: die
beigetretene Person muss dafür planen, *bevor* die Aktivierung durchläuft (schmales Zeitfenster,
im Zwei-Konten-Test ggf. den Owner künstlich offline halten).

## 28. QR-Code im Dark Theme

`qrSvg()` liefert ein SVG ohne eigenen Hintergrund (nur schwarze Module). Ohne einen fest hellen
Träger ist der Code im Dark Theme auf dunklem Grund unlesbar für Scanner. Deshalb hat `.grp-qr`
einen fest weißen Hintergrund (`#fff`), unabhängig vom Theme — **nicht** `var(--surface)`
verwenden, das ist im Dark Theme dunkel.

## 29. `window.CloudGroup` hat kein `loadRecipes`

Historischer Fehler in `dissolveGroup()`: der Code rief `window.CloudGroup.loadRecipes(...)` auf
— diese Methode existiert nur auf `window.CloudSync`, nicht auf `CloudGroup` (siehe
`### window.CloudGroup` in `ARCHITECTURES.md`). Der Aufruf warf eine `TypeError`, die vom
umgebenden `try/catch` verschluckt wurde: „Gruppe auflösen" räumte dadurch nie wirklich die
Firestore-Daten auf, sondern lief still in den lokalen `leaveGroup()`-Fallback. Behoben beim
Herauslösen der gemeinsamen Aufräumlogik in `dissolveGroupFirestore()`. Bei ähnlichen
`CloudGroup`/`CloudSync`-Aufrufen immer gegen die tatsächliche Methodenliste des jeweiligen
Objekts prüfen, nicht nur gegen den Namen.

## 30. ZXing-SVG-QR-Code braucht ein eigenes `viewBox`

`BrowserQRCodeSvgWriter.write()` setzt am erzeugten `<svg>` nur `width`/`height` in absoluten
Nutzereinheiten, kein `viewBox`. Wird das SVG danach per CSS auf eine andere Größe skaliert
(`width: 100%; height: 100%` in einem kleineren Container), skaliert nur die Zeichenfläche — die
Modul-Koordinaten bleiben bei den ursprünglichen Werten stehen und werden **abgeschnitten**, nicht
verkleinert. Sichtbar wurde das erst im Ausschneide-Prüfstand (Modul-Kante bei x=172 von 200, aber
Container 150 px): ohne `viewBox` fehlten in einem schmaleren `.grp-qr`-Container echte
Modulspalten, der Code wäre für einen Scanner unlesbar geworden. Fix: nach `writer.write()` sofort
`svg.setAttribute("viewBox", "0 0 " + size + " " + size)`.

## 31. Zwei-Konten-Race im Gruppen-Wartezustand

Beim ersten Entwurf des Wartezustands (siehe „Wartezustand“ in `ARCHITECTURES.md`) fielen bei
einer zweiten, unabhängigen Prüfung (Opus-Review desselben Diffs) mehrere Randfälle auf, die beim
ersten Umsetzen übersehen wurden — alle rund um „zwei Gruppen-Zeiger gleichzeitig“ oder „ein
verwaister Zeiger nach einem Fehler mitten im Ablauf“:

* Konto löschen, während eine Einladung offen ist, aber noch niemand beigetreten (`syncGid` ist
  in diesem Zustand noch leer, die bestehende Owner-Sperre griff nicht).
* Einer fremden Gruppe beitreten, während die eigene Einladung noch offen ist (führte dazu, dass
  bei einem späteren Beitritt über die alte Einladung der inzwischen fremde Meal-Bestand in die
  falsche Gruppe kopiert worden wäre).
* `enterGroupSync()` scheitert direkt nach einer gerade erst geglückten Aktivierung — ohne
  Wiederherstellung des Wartezustands wären `groupId` und `pendingGroupId` beide leer gewesen,
  obwohl die Gruppe für den Beitretenden längst aktiv war.
* Ein fehlgeschlagener `fetchMembers()`-Aufruf oder eine fehlgeschlagene Aktivierung ließ den
  Live-Listener (`watchPendingGroup()`) unangehängt zurück — die Aktivierung war dann für den Rest
  der Sitzung tot, bis zum nächsten Neustart.

**Lehre für ähnliche zweistufige Abläufe:** Jeden Fehlerpfad einzeln durchspielen, nicht nur den
Erfolgspfad — insbesondere „was, wenn Schritt N gerade dann scheitert, wenn Schritt N-1 schon
committet war". Ein zweites, unabhängiges Review (anderes Modell, kein Kontext aus der
Umsetzung) hat hier mehr gefunden als der ursprüngliche Ausschneide-Prüfstand, weil dieser nur den
Erfolgspfad und offensichtliche Fehlerfälle testete, nicht die Kombination aus zwei parallel
laufenden Abläufen.

## 32. Popover in `.day` wird von `overflow: hidden` abgeschnitten

`.day` trägt `overflow: hidden` für die mobilen Karussell-Streifen (`initCarousel()`,
`scroll-snap-type`). Ein absolut positioniertes Popover, das an eine Karte **innerhalb** von
`.day` angehängt wird (z. B. an eine `.filled`-Meal-Karte im Wochenplan), wird dadurch am
Kartenrand abgeschnitten, sobald es über die Kartenhöhe hinausragt — bei der
Gerichte-Zuweisung fiel das erst bei einer zweiten, unabhängigen Prüfung auf (Opus-Review,
kein Kontext aus der Umsetzung), nicht beim ersten Ausschneide-Prüfstand, weil der nur die
Positions-*Berechnung* isoliert testete, nicht das tatsächliche Clipping durch einen Ahnen.

**Lösung:** Popover als Portal an `document.body` hängen (`position: fixed`, Koordinaten aus
`getBoundingClientRect()` des Auslösers berechnen), nicht an einen Nachfahren von `.day`. Siehe
`openAssignMenu()` (index.html) für das Muster inklusive Schliessen bei Scroll.

**Lehre:** Bei jedem neuen Popover/Menü prüfen, ob ein Ahnen-Element `overflow: hidden` oder
`overflow: auto` trägt — nicht nur, ob die Positionsrechnung selbst stimmt.

## 33. `state.plan`-Einträge nie direkt an `getRecipe()` übergeben

Seit der Gerichte-Zuweisung ist ein Slot-Eintrag in `state.plan[day][meal]` entweder ein
blanker String (Rezept-ID) oder ein Objekt `{id, uids}`. `getRecipe()` erwartet einen String —
ein direkt durchgereichtes Objekt liefert `null`, und die betroffene Karte fällt **kommentarlos**
aus jeder Berechnung heraus, statt einen Fehler zu werfen.

Bei der ersten Umsetzung wurden `normalizePlan()`, `unflattenWeek()`, `buildShoppingList()` und
`draggedCat()` korrekt umgestellt, aber `dayNutOf()` (Tages-/Wochen-Nährwertsumme gegen
`state.goal`) und `buildPrintable()` (Strg+P-Ausdruck) übersehen — beide fielen erst bei einer
zweiten, unabhängigen Prüfung auf (kvp-Agent). Symptom war nicht ein Absturz, sondern eine
**stillschweigend zu niedrige** Kalorien-/Makrosumme bzw. eine leere Zelle im Ausdruck, obwohl
ein Gericht sichtbar eingeplant war — genau die Art Fehler, die ein Ausschneide-Prüfstand ohne
gezielten Testfall mit einem `{id,uids}`-Eintrag nicht findet.

**Lehre:** Jede Stelle, die `state.plan[day][meal]` iteriert, muss `entryId(entry)` statt der
rohen ID an `getRecipe()` übergeben. Bei einer neuen Konsumstelle immer gezielt mit einem
`{id,uids}`-Testeintrag prüfen, nicht nur mit dem alten String-Format — sonst besteht der Test
grün, obwohl der neue Fall nie durchlaufen wurde. Zusätzlich unterscheiden, **wofür** die Stelle
zählt: `dayNutOf()` läuft gegen das persönliche Ziel und muss nach `syncUid` filtern (nur
zugewiesene/geteilte Gerichte zählen mit), während `buildPrintable()` eine personen-neutrale
Übersicht ist und nur `entryId()` braucht, keine Filterung.

## 34. Zusammengeführte Listen müssen sortiert sein, sonst schaukeln sich zwei Geräte auf

**Symptom:** Sobald zwei Geräte gleichzeitig angemeldet sind, „zuckt" der Bildschirm — auch
wenn auf beiden Geräten niemand etwas ändert. Am auffälligsten beim Zeigen auf eine
Wochentag-Karte, weil `render()` `<main>` komplett neu aufbaut und der `:hover`-Zustand samt
`transform: translateY(-3px)` dabei für einen Moment verlorengeht.

**Ursache:** `onRemote()` vergleicht lokalen und entfernten Stand als **Zeichenkette**
(`dataJSON()`). Anschließend werden Listen **zusammengeführt** statt ersetzt, damit nichts
verlorengeht, das nur auf einem Gerät bekannt ist. Wenn diese Zusammenführung die Reihenfolge
der Einfügung übernimmt, bildet jedes Gerät aus **derselben Menge eine andere Reihenfolge**:

```text
Gerät A: unionIds(["x"], ["y","x"]) -> ["x","y"]
Gerät B: unionIds(["y"], ["x"])     -> ["y","x"]
```

Beide halten den Stand des anderen für eine Änderung, schreiben zurück, rendern — und das
endlos, alle ~800 ms (Debounce von `scheduleCloudPush`). Der Fehler liegt nicht im Vergleich,
sondern darin, dass für dieselbe Menge zwei gültige Zeichenketten existieren.

**Betroffen waren** `unionIds()` (`state.shares`, `state.inviteCodes`) und
`sanitizeWeightGoals()` (per `Object.assign` gemergt, das die Schlüsselreihenfolge des ersten
Objekts übernimmt). `sanitizeTombstones()` und `sanitizeFavs()` sortierten bereits — der
Kommentar dort beschrieb die Falle sogar schon, sie war nur nicht überall geschlossen.

**Regel:** Alles, was per Merge in `dataJSON()` landet, muss **kanonisch** sein — Listen
sortiert, Objektschlüssel sortiert. Prüffrage bei jeder neuen Merge-Funktion: *Liefert
`merge(a, b)` dieselbe Zeichenkette wie `merge(b, a)`?* Wenn nein, entsteht genau dieser
Ping-Pong. Das gilt auch für `normalizePlans()` (Wochenschlüssel).

**Zusätzliches Sicherheitsnetz:** `onRemote()` rendert nur noch, wenn sich der Stand durch die
Zusammenführung tatsächlich geändert hat (`dataJSON(state) === before` → kein `render()`).
`save()` läuft trotzdem, denn der eigene Mehrstand muss weiterhin hoch. Der Vergleich vor der
Zusammenführung schlägt schon an, wenn das eingehende Dokument nur *anders* ist — daraus kann
trotzdem derselbe Stand entstehen.

**Nachweis im Prüfstand:** Die Kette lässt sich ohne Firebase nachstellen — zwei „Geräte",
die abwechselnd den empfangenen Stand vereinigen und zurückschreiben. Mit der unsortierten
Fassung kommt sie nach 40 Runden nicht zur Ruhe, mit der sortierten nach Runde 2. Siehe
`docs/TESTING.md`.

**Fortsetzung:** Diese Ziffer schloss nur die Merge-*Reihenfolge* (Einfüge-Reihenfolge beim
Zusammenführen von Listen/Objekten). Die zweite Hälfte derselben Fehlerklasse — Firestore gibt
Objektschlüssel bei jedem Snapshot **sortiert** zurück, unabhängig vom Merge — steht in Ziffer 44.

## 35. Ein gescheiterter Lesevorgang darf nie zu einem Schreibvorgang werden

**Symptom:** Gruppe gestern eingerichtet und die Einladung verschickt, heute ist sie spurlos
weg — auf allen Geräten, auch nach Neustart.

**Ursache (behoben):** `enterGroupSync()` lieferte nur `true`/`false`. Vier grundverschiedene
Lagen fielen auf dasselbe `false` zusammen: „Gruppe aufgelöst", „ich wurde entfernt",
„Firestore-Zugriff gerade gescheitert" und „`CloudGroup` nicht verfügbar". `startCloudSync()`
leerte daraufhin `state.groupId`, und `pushNow()` schrieb dieses leere Feld anschließend als
`groupId: ""` ins Kontodokument. Ein einziger misslungener Aufruf beim Start — Funkloch,
frisch veröffentlichte Regeln, Rate-Limit — löschte damit die Gruppenzugehörigkeit dauerhaft
und für alle Geräte des Kontos.

Zusätzlich rief der `!info`-Zweig `removeMember(gid, syncUid)` auf, um „aufzuräumen".
`CloudGroup.fetch()` liefert `null` aber für jedes Leseergebnis ohne Dokument, nicht nur für
eine wirklich gelöschte Gruppe. Das Gerät warf sich also bei einer nur kurz nicht lesbaren
Gruppe selbst aus der Mitgliederliste — in einer Zweiergruppe stand die andere Person danach
allein da.

**Regel für künftige Änderungen:**

* Ein Rückgabewert, der „weg" und „gerade nicht erreichbar" nicht unterscheidet, ist bei
  Sync-Code ein Fehler. Drei Zustände (`"ok"`/`"gone"`/`"error"`) statt eines Booleschen.
* Aus einem fehlgeschlagenen oder leeren **Lesevorgang** darf niemals eine **Löschung**
  folgen.
* Solange ein Client den Gruppenzustand nicht kennt, darf er die Gruppenfelder nicht in die
  Cloud schreiben (`groupSyncFailed`). Bei `merge: true` bleibt ein weggelassenes Feld stehen —
  das ist die sichere Variante, nicht ein Feld mit leerem Wert.

**Nachweis im Prüfstand:** `enterGroupSync()`, `pushNow()` und der Entscheidungsblock aus
`startCloudSync()` lassen sich mit gestubbtem `CloudGroup`/`CloudSync` ohne Firebase
ausschneiden und gegen vier Szenarien fahren. Gegen den alten Stand (`git show HEAD:index.html`)
gegengeprobt: dort leert Szenario „Firestore wirft" die `groupId` und pusht sie als `""`, und
Szenario „fetch → null" ruft `removeMember` genau einmal auf. Siehe `docs/TESTING.md`.

### Rückfall am 06.08.2026: derselbe Bug an vier weiteren Stellen

Dasselbe Symptom trat erneut auf — eine gemeinsam eingerichtete Gruppe war bei **beiden**
Konten weg. `groupSyncFailed` war nie das Problem, sondern seine Reichweite: das Flag wird
**mitten im `try`-Block** von `startCloudSync()` gesetzt. Alles, was daran vorbeiläuft, war
ungeschützt. Vier Pfade schrieben weiterhin `groupId: ""`:

1. **`startCloudSync()` bricht vor Zeile ~4000 ab** (meist `CloudSync.load()` beim Kaltstart
   ohne Netz). `syncUid` ist da schon gesetzt, `groupSyncFailed` noch `false` — der nächste
   beliebige `save()` löschte die Gruppe. Hauptursache.
2. **Debounce-Race während `activateGroup()`/`joinGroup()`.** Zwischen dem Cloud-Write
   (`{ groupId: gid }`) und `switchGroup()` ist `syncGid` noch `null`; ein in dieses Fenster
   fallender Push nahm den Beitritt sofort wieder zurück. Danach war die Gruppe für den Owner
   weder aktiv noch wartend — `pendingGroupId` ist zu dem Zeitpunkt bereits geleert.
3. **Leerer Mitglieder-Snapshot galt als Rauswurf.** `getDocs()` *wirft offline nicht*, sondern
   liefert das leere Cache-Ergebnis; `onSnapshot` ruft dabei auch nicht den Error-Callback auf.
   `onMembersRemote([])` löste „Du bist nicht mehr Teil der Gruppe" aus, `enterGroupSync()`
   lieferte `"gone"`.
4. **`joinGroup()`-`catch` setzte pauschal `state.groupId = ""`** — auch wenn der Cloud-Write
   längst durch war und erst ein späterer Schritt scheiterte.

**Behoben durch** zwei zusätzliche Sperren neben `groupSyncFailed`, die `pushNow()` über
`groupKnown` auswertet:

* `syncHandshakeOk` — erst `true`, wenn `startCloudSync()` den Gruppenzustand vollständig
  geklärt hat (unmittelbar vor dem Baseline-Push). Der `catch` setzt zusätzlich
  `groupSyncFailed = true` als doppelten Boden.
* `groupTransition` — für die Dauer von `activateGroup()`/`joinGroup()`, dazu ein
  `clearTimeout(pushTimer)` beim Eintritt, statt auf günstiges Timing zu hoffen.

Dazu: leere Mitgliederlisten werden in `onMembersRemote()` und `enterGroupSync()` als
*ungeklärt* behandelt (`return` bzw. `"error"`), `watchMembers()` meldet echte Lesefehler als
`null` statt als leere Liste, `onRemote()` deutet ein leeres `groupId`-Feld bei laufender
Gruppen-Session nicht mehr als Austritt, und `joinGroup()` stellt im `catch` den vorherigen
Zeiger wieder her.

**Selbstheilung:** `wantGid` in `startCloudSync()` fällt auf `state.groupId` zurück, wenn die
Cloud kein `groupId` hat. Hat ein alter Fehlerpfad den Cloud-Zeiger geleert, holt der nächste
Start die Gruppe zurück, solange `groups/{gid}` und die Mitgliedschaft existieren.
`enterGroupSync()` bleibt die Instanz, die `"gone"` von `"error"` unterscheidet — der reguläre
Austritt auf einem anderen Gerät räumt weiterhin korrekt.

**Regel, die daraus folgt:** Ein Schutzflag muss den **gesamten** Zeitraum abdecken, in dem der
geschützte Zustand ungeklärt ist — nicht nur den Abschnitt, in dem es gesetzt wird. Bei jedem
neuen `await` in `startCloudSync()`, `activateGroup()` oder `joinGroup()` prüfen: *Was schriebe
ein `pushNow()`, der genau hier hineinfeuert?*

**Nachweis:** acht Szenarien im Ausschneide-Prüfstand, gegen `git show HEAD:index.html`
gegengeprobt (alter Stand: 13 Fehler, neuer Stand: 0). Siehe `docs/TESTING.md`.

## 36. Der lokale Teststand schreibt in die echte Cloud

**Symptom:** In der Cloud tauchen immer wieder Meals auf, die längst — teils mehrfach —
gelöscht wurden.

**Ursache (behoben):** `localStorage` ist an die Origin gebunden, die Firebase-Anbindung nicht.
`http://localhost:8000` hat einen eigenen lokalen Speicher, meldet sich aber am **selben**
Firebase-Projekt mit derselben UID an. Der dortige, veraltete Bestand galt in
`mergeRemoteRecipes()` als „lokal vorhanden, remote nicht → also neu, noch nicht hochgeladen"
und wurde beim nächsten `save()` in die echte Cloud gepusht.

Die Grabsteine (`state.deleted`) fangen das nicht in jedem Fall ab:

* `markDeleted()` steigt im Gruppenmodus bewusst sofort aus (`if (syncGid) return;`) — dort
  ersetzt `enterGroupSync()` den Bestand ohnehin, ein persönlicher Grabstein würde nach einem
  Austritt nur das gleichnamige eigene Meal mitreißen.
* Grabsteine greifen über die **ID**. Ein Speicher, der einmal frisch mit `SEED` gestartet ist,
  hat neue `uid()`s; sobald ein solches Meal bearbeitet wurde, greift auch `isExample()` nicht
  mehr (das vergleicht Name **und** `steps`).

**Behoben** über einen eigenen Schlüsselraum für die Testumgebung (`localKey()`, Suffix
`__test`) — siehe `docs/ARCHITECTURES.md`.

**Falle bei der Erkennung:** Nicht am Hostnamen allein festmachen. Capacitor läuft selbst unter
`localhost` (Android `https://localhost`, iOS `capacitor://localhost`). Ein reiner
Hostname-Test hätte die App-Store-Fassung als Testumgebung eingestuft und jedem Nutzer beim
Update die Daten entzogen. Prüfstand deckt alle zehn Umgebungen ab, Capacitor in drei Varianten.

**Wenn der Fehler schon passiert ist:** Der alte Speicher unter dem unsuffixierten Schlüssel
bleibt auf `localhost` liegen und ist ab jetzt wirkungslos. Wer ihn loswerden will, öffnet auf
`localhost` die Entwicklerwerkzeuge und ruft `localStorage.clear()`.

## 37. Löschen muss beide Speicher treffen, nicht nur `localStorage`

**Symptom:** Nach „Konto löschen" bzw. „Alle Daten löschen" bleiben Meal-Fotos, das Profilbild
und die abgehakten Einkaufsposten auf dem Gerät liegen. Besonders auffällig: Registriert man
sich direkt danach neu, ist das **alte Profilbild wieder da** — und wandert erneut in die Cloud.

**Ursache (behoben):** `wipeLocalData()` entfernte nur `STORE_KEY`, `PROFILE_KEY` und
`LAST_KEY`. Seit Paket A3 liegen die Bilder aber in **IndexedDB**, nicht mehr im
localStorage-JSON. `hydrateImages()` zieht beim Start `map.__profile__` zurück in den State
(`if (!state.profileImage && map.__profile__)`) — das Bild überlebte die Löschung also nicht nur
passiv, es kam aktiv zurück.

**Regel:** Bei jeder Änderung daran, *wo* Daten liegen, gehört `wipeLocalData()` mitgeprüft.
Der Speicherort einer Information und ihre Löschung sind ein Paar. Ziffer 10 der
Datenschutzerklärung sagt wörtlich „sämtliche auf diesem Gerät gespeicherten Daten sofort
entfernen" — jeder neue Speicherort ist damit automatisch eine rechtliche Zusage.

**Falle beim Löschen der IndexedDB:** `store.clear()` verwenden, **nicht**
`indexedDB.deleteDatabase()`. Letzteres wartet auf das Schließen jeder offenen Verbindung —
`idbOpen()` hält eine — und bleibt sonst still in `onblocked` hängen, ohne Fehler.
`wipeLocalData()` ist deshalb `async`, und alle Aufrufer `await`en es, bevor sie den Reload
planen.

**Nachweis im Prüfstand:** Gegen eine echte IndexedDB, gegengeprobt gegen `git HEAD` — der alte
Stand lässt dort vier Überbleibsel zurück (Einkaufsliste, Meal-Foto, Profilbild, Baseline), der
neue keines.

**Dritter Speicherort seit dem Firestore-Offline-Cache:** Der Firestore-Cache (`persistentLocalCache`,
ebenfalls IndexedDB, aber eine eigene Datenbank neben der Bild-IndexedDB) spiegelt jetzt
Wochenplan, Meals und Gruppendaten — auch das ist ein Speicherort im Sinne dieser Regel.
`CloudSync.wipeCache()` räumt ihn über `terminate(db)` gefolgt von `clearIndexedDbPersistence(db)`
(Reihenfolge zwingend), aufgerufen von `wipeLocalData()` als **letzter** Schritt, nach
`localStorage` und der Bild-IndexedDB. Anders als die beiden anderen Speicher kann dieser Schritt
erstmals **fehlschlagen** (`clearIndexedDbPersistence()` scheitert planmäßig bei mehreren offenen
Tabs) — deshalb kein leeres `catch`, sondern eine ehrliche Meldung an den Aufrufern statt eines
stillen Rests. Siehe Ziffer 45 („`fromCache` ist kein Beweis") für den zweiten, subtileren Effekt
desselben Pakets.

## 38. hitSlop bei benachbarten Knöpfen: die Enge gilt nur in einer Achse

**Symptom:** Das ✕ und der Stift an einer eingeplanten Meal-Karte (`.slot .filled`) waren auf
dem Handy schwer zu treffen — besonders in der Gruppe, wo beide nebeneinander stehen.

**Ursache:** Sichtbar 22×22 px, hitSlop `inset: -4px` → nur **30×30 px** Trefferfläche. Apple
HIG und WCAG 2.5.5 verlangen 44 px. Der Slop war bewusst so klein, weil die beiden Knöpfe nur
8 px Abstand haben — im Prüfstand nachgemessen berührten sich ihre Flächen bei 0,0 px, mehr
wäre also tatsächlich Überlappung gewesen.

**Regel:** Erst rechnen, was die Fläche *braucht*, dann den Abstand danach richten — nicht
umgekehrt. 28 px sichtbar + 8 px Slop je Seite = 44 px, zwei benachbarte Knöpfe brauchen
also **16 px zwischen sich**. Die Karte gab nur 8 px her, deshalb bekommt der Stift den
Zuschlag:

> **Stand heute:** sichtbar sind 32 px (das Personen-Icon löste den Stift ab), die
> Trefferfläche ist dadurch 48×48 px. Der Zuschlag `margin-right: 8px` blieb dabei
> unverändert richtig: die 16 px ergeben sich aus **hitSlop × 2**, nicht aus der
> Knopfbreite — die Knopfgröße kürzt sich aus der Rechnung heraus.

```css
.slot .filled .x::after, .slot .filled .pencil::after { inset: -8px; }  /* beide 44x44 */
.slot .filled .pencil { margin-right: 8px; }                           /* 8 + 8 = 16px Luecke */
```

**Der naheliegende Irrweg:** den Slop einfach kleiner machen, bis er „gerade so passt"
(`inset: -8px -3px`). Das ergibt 39×44 px und 34×44 px — beide unter 44 px in der Breite,
also weiterhin zu klein, nur weniger auffällig. Die Enge ist ein Abstandsproblem, kein
Slop-Problem. Der Zuschlag kostet 8 px Textbreite, und das auch nur im Gruppenmodus: den
Stift gibt es nur bei `showPencil = drag && groupMembers.length >= 2`, ohne Gruppe steht
das ✕ ohnehin allein.

**0 px Abstand ist kein Fehler.** Zwei 44×44-Flächen, die exakt aneinandergrenzen, sind
korrekt — dasselbe Maß wie im Symbolblock der Meal-Karten (`.act-icons`, `gap: 10px` bei
`.fav-ic::after { inset: -5px }`). Erst ein *negativer* Abstand ist eine Überlappung. Wer
im Prüfstand auf `> 0` statt `>= 0` testet, meldet sich den Normalfall als Fehler.

**Zweite Falle in derselben Regelgruppe:** `:active` muss **nach** `:hover` stehen. Beide haben
dieselbe Spezifität, also gewinnt die spätere Regel — und ein Touchscreen lässt den
Hover-Zustand nach dem Tippen hängen. Steht `:active` davor, sieht man den Press-State nie.

**Nachweis im Prüfstand:** CSS und Karten-Markup aus `index.html` ausgeschnitten, Trefferfläche
über `getComputedStyle(el, "::after")` gemessen und die vier Ecken mit `elementFromPoint`
wirklich angetippt — Ergebnis 44×44 px für ✕ und Stift (heute 48×48 px, siehe oben), Abstand
0,000 px. Gegenprobe gegen die alten Werte liefert 30×30 px; ohne sie würde der Test nicht
beweisen, dass er überhaupt misst.

## 39. CSS-`transition` greift nicht an Elementen aus `view.innerHTML`

**Symptom:** Eine gleitende Pille sollte für `.week-switch` (Aktuelle/Nächste Woche) dieselbe
einfache CSS-`transition` wie `.tab-ind` bekommen — bewegte sich aber nie, sie stand immer
sofort am Ziel.

**Ursache:** `renderPlan()` baut `.week-switch` bei **jedem** `render()` über
`view.innerHTML = html` komplett neu auf. Die neu geschriebene Pille bekommt ihre
Zielposition direkt als Startzustand — es gibt keinen "vorher" für den Browser, von dem aus
eine `transition` interpolieren könnte. Eine CSS-`transition` kann nur Zustandswechsel an
**demselben, im DOM verbleibenden** Element animieren.

**Regel:** Vor einer Pillen-/Übergangs-Transition prüfen, ob das Element den Neuaufbau
überlebt:

* **Überlebt `innerHTML`-Austausch nicht** (`.week-switch`, `.week`, `.wg-cols`) → WAAPI
  (`element.animate(...)`) mit Werten aus `getBoundingClientRect()`, siehe
  `syncWeekSwitchPill()` und `slideIn()` in `docs/ARCHITECTURES.md`.
* **Steht außerhalb von `view.innerHTML` im statischen Markup** (`.tabs`) → eine echte
  CSS-`transition` funktioniert, siehe `.tab-ind`.
* **Pille ist 1:1 an `scrollLeft` gekoppelt** (`.daybar`/`.wgbar`, `.db-ind`) → braucht gar
  keine eigene Transition, der native Sanftlauf des Scrollens liefert die Kurve mit.

**Nachweis im Prüfstand:** `syncWeekSwitchPill()` isoliert ausgeschnitten und gegen zwei
unterschiedlich breite Schaltflächen ("Aktuelle Woche"/"Nächste Woche") getestet — beide
Läufe (unterschiedliche Schriftmetrik je nach Umgebung) bestätigten übereinstimmend, dass
die beiden Knöpfe **spürbar unterschiedlich breit** sind (Differenz jeweils mehrere Pixel),
ein 50 %-Ansatz hätte also erkennbar danebengelegen. Zweiter Fund im selben Prüfstand:
`ind.style.left` rechnet gegen die *Padding*-Box von `.week-switch` (Containing Block eines
absolut positionierten Kindes), `getBoundingClientRect()` aber gegen die *Border*-Box — ohne
Abzug von `container.clientLeft` stand die Pille um genau die Randbreite (1 px) zu weit
rechts, am rechten Rand sichtbar asymmetrisch neben der 3-px-Polsterung.

## 40. `navigator.share()` verliert die Nutzer-Aktivierung nach einem `await`

`navigator.share()` verlangt eine gültige Nutzer-Aktivierung (der Klick selbst). Wird vor dem Aufruf zuerst ein Netzwerk-Roundtrip abgewartet (z. B. `await CloudShare.publish(...)`), ist die Aktivierung auf iOS Safari verbraucht — `share()` wirft dann `NotAllowedError`, obwohl der Nutzer gerade erst getippt hat.

`shareRecipeNow()` (10854) umgeht das: `shareId()` ist synchron, die Link-URL steht also sofort fest. `CloudShare.publish()` wird ohne `await` gestartet, direkt danach folgt `shareLink()` — beide laufen parallel, kein `await` liegt zwischen Klick und `navigator.share()`.

**Der Preis dafür:** Der Link kann beim Empfänger ankommen, bevor (oder ohne dass) `publish()` gelingt — das Teilen-Sheet öffnet sich unabhängig vom Ausgang des Uploads. Ein Fehlschlag zeigt einen Toast, der aber erst nach/hinter dem bereits geöffneten Sheet erscheint und den bereits verschickten Link nicht mehr zurückholen kann. Deshalb wird `state.shares` erst **nach erfolgreichem** `publish()` ergänzt (nicht sofort beim Start) — sonst würden gescheiterte oder abgebrochene Uploads mitgezählt, obwohl nie ein `shared/{id}`-Dokument entstanden ist.

Zusätzlich prüft `shareRecipeNow()` `authMode === "cloud"`, nicht nur `CloudShare.enabled` — Letzteres sagt nur, dass Firebase konfiguriert ist, nicht, dass diese Person gerade per Cloud angemeldet ist (dieselbe Weiche wie bei `loadSharedById()`, 8082). Ohne diese Prüfung würde ein lokales Profil `publish()` starten, das an `allow create: if request.auth != null` scheitert, während der Link bereits verschickt wurde.

Gilt für jeden künftigen Share-Flow, der Cloud-Daten UND das native Share-Sheet in derselben Aktion braucht.

## 41. Open Food Facts liefert `serving_size` nicht zuverlässig

**Symptom:** `quickAddByBarcode()` (Barcode-Schnellzugriff aus dem Wochenplan) könnte bei
manchen Produkten falsche oder fehlende Nährwerte errechnen, wenn man `serving_size`/`quantity`
blind vertraut.

**Ursache:** OFF ist eine offene, von Nutzern gepflegte Datenbank. `serving_size` fehlt bei
vielen Produkten komplett, und wenn es gesetzt ist, sind die Formate uneinheitlich ("65 g",
"1 Stück (65 g)", "6 x 65 g", aber auch Tippfehler oder leere Strings).

**Lösung:** `offServingSize(p)` liefert `null`, sobald sich weder eine Stückzahl noch ein reines
Gewicht/Volumen aus dem Text lesen lässt. `quickAddByBarcode()` verlangt zusätzlich Name UND alle
vier Nährwerte — fehlt irgendetwas davon, wird **nicht geraten**: Statt eines stillen Fehlwerts
öffnet sich `openRecipeForm(null, prefill)` vorausgefüllt, der Nutzer bestätigt einmal kurz. Ein
zusätzlicher Klick ist hier bewusst der sicherere Weg (siehe `docs/PRODUCT.md`, „Bewusste
Produktentscheidung: Barcode-Schnellzugriff").

**Die eigentliche Falle dabei: `quantity` ist keine Portion.** `offServingSize()` fällt auf
`quantity` zurück, wenn `serving_size` fehlt — für `applyBarcode()` ist das harmlos (dort dient
der Wert nur der Stückerkennung), für das stille Anlegen wäre es falsch: „500 g" Nudeln oder
„1 l" Milch würden ein Meal mit 1750 bzw. 640 kcal erzeugen, ohne dass der Nutzer je eine Menge
bestätigt hat. Deshalb trägt das Ergebnis ein `serving`-Flag (Wert stammt aus `serving_size`)
und `quickAddByBarcode()` legt nur bei `count || serving` still an. Aus demselben Grund gilt bei
Mehrfachpackungen („6 x 65 g") **ein** Stück als Portion, nicht die ganze Schachtel.

**Und die Werte fallen dabei nicht unter den Tisch:** Der Formular-Fallback bekommt die
OFF-Nährwerte als vorbefüllte Zutaten-Zeile (je 100 g, ohne Menge) mit. Der Nutzer trägt nur die
Menge ein, `updateMacroSum()` rechnet den Rest — sonst würde der sichere Weg zur Strafarbeit.

**Verwandt:** Das `barcode`-Feld auf dem entstehenden Recipe ist auch der Schutz vor unnötigem
Wachstum von `state.recipes` (und damit der Firestore-Gruppendokumente) — ein zweiter Scan
desselben Produkts sucht zuerst per `state.recipes.find(r => r.barcode === code)` nach einem
bestehenden Eintrag und plant nur diesen ein, statt ein Duplikat anzulegen.

## 42. Wochenplan bleibt beim Zurückwischen zwischen zwei Tagen stehen

**Symptom:** Auf dem Handy wischt man vom Folgetag zurück auf heute — und der Streifen bleibt
halb auf beiden Tageskarten stehen, statt einzurasten. In der Gegenrichtung (heute → morgen)
fällt es nicht auf.

**Ursache:** `fitHeight()` in `initCarousel()` schreibt `scroller.style.height` **während** der
Wisch noch läuft. Beim Zurückwischen ist die hereinkommende Karte in aller Regel höher als die
verlassene (heute ist der vollere Tag), der Streifen wächst also schon beim ersten Millimeter der
Geste. Ein Größenwechsel des Snap-Behälters lässt den Browser sein Snap-Ziel neu bestimmen und
kann den laufenden Wisch dabei verlieren. Vorwärts passiert derselbe Schreibvorgang erst in den
letzten Pixeln, deshalb die Richtungs-Asymmetrie. Auf iOS kommt hinzu, dass `requestAnimationFrame`
im Momentum-Scroll gedrosselt wird — die Höhenänderung schlägt dort gebündelt genau beim
Einrasten auf.

**Lösung:** `settleNative()` in `initCarousel()` — dieselbe Nachkorrektur, die `go()` mit
`settle()` seit jeher für den programmatischen Sanftlauf hat, jetzt auch für den Finger-Wisch.
Ausgelöst über `scrollend`, mit einem 220-ms-Timeout als Rückfall für Browser ohne `scrollend`.
Solange ein Finger auf dem Streifen liegt (`e.touches.length`), wird **nicht** korrigiert — dort
ist „zwischen zwei Tagen" der gewollte Zustand. Zielpunkt ist `lefts[currentIndex()]`, also genau
der Tag, den die Tagesleiste ohnehin hervorhebt. Hart gesetzt statt sanft: ein zweiter Sanftlauf
könnte auf demselben Weg wieder zwischen zwei Punkten enden.

**Nachweis (Prüfstand):** Headless Edge mit `--remote-debugging-port`, echte Wischgeste per CDP
`Input.dispatchTouchEvent`. Der Snap-Verlust wird nachgestellt, indem `scroll-snap-type` für die
Dauer der Geste auf `none` gesetzt wird. Alter Stand blieb 145 px neben dem Snap-Punkt stehen,
neuer Stand korrigiert auf 0 px — Normalbetrieb (beide Richtungen, Mehrtages-Sprung über die
Tagesleiste) in beiden Fassungen unverändert korrekt. Siehe `docs/TESTING.md`.

**Lehre:** Die Größe eines `scroll-snap`-Behälters nie sorglos während einer laufenden Geste
ändern. Wo es sich nicht vermeiden lässt, gehört eine Nachkorrektur auf den nächsten Snap-Punkt
dazu — für **jeden** Auslöser, nicht nur für den programmatischen.

**Nachtrag 08.08.2026 — die Ursache ist weg, die Nachkorrektur bleibt.** Der Wochenplan ist mobil
ein Sheet fester Höhe (`.plan-sheet`); der Streifen bekommt seine Höhe vom Raster, nicht mehr von
der sichtbaren Karte. `initCarousel()` kennt dafür die Option `noFit`, und `fitHeight()` steigt
damit sofort aus. Gemessen beim Fahren durch die Zwischenpositionen zwischen zwei Tagen:

| | alter Stand | mit Sheet |
|---|---|---|
| Inline-Höhe unterwegs | in 11 von 11 Schritten gesetzt | keine |
| Streifenhöhe | springt 776 → 609 px | konstant 524 px |

`settleNative()` wurde **nicht** entfernt. Es fängt Snap-Verlust auch aus anderen Gründen ab, und
die oben genannte iOS-Drosselung von `requestAnimationFrame` gibt es weiterhin. Wer hier aufräumen
will, braucht erst einen Beleg, dass kein anderer Auslöser mehr existiert.

## 43. Grundregel bei Fehlern

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

## 44. Firestore sortiert Map-Schlüssel — Fortsetzung von Ziffer 34

**Symptom:** Wie in Ziffer 34 — Dauer-Zucken bei zwei gleichzeitig angemeldeten Geräten, auch
ohne dass jemand etwas ändert. Diesmal aber selbst dann noch, wenn alle Merge-Funktionen aus
Ziffer 34 bereits sortiert zurückgeben. Zusätzliches Symptom im Rezeptpfad: **Meal-Bilder
blitzen**, ohne dass ein Toast erscheint.

**Ursache:** Ziffer 34 schloss nur die Merge-*Reihenfolge*. Offen blieb die andere Quelle zweier
gültiger Zeichenketten für denselben Inhalt: **Firestore gibt Map-Schlüssel bei jedem Snapshot
sortiert zurück**, lokal gebaute Objekte tragen dagegen die Reihenfolge, in der der Code sie
zusammensetzt (`sanitizeConsent()` → `{given, at}`, Firestore → `{at, given}`). `JSON.stringify`
ist reihenfolgeabhängig — der ganze Sync verglich strukturell Äpfel mit Birnen, unabhängig davon,
ob die Merge-Funktionen selbst schon korrekt waren.

**Neue Prüffrage bei jeder Sync-Vergleichsstelle:** *Vergleiche ich zwei Objekte, von denen eines
schon einmal in Firestore war?* Wenn ja, reicht `JSON.stringify` nicht.

**Lösung:** `canonValue()`/`canonJSON()` — sortieren Objektschlüssel rekursiv, Arrays bleiben
unangetastet. Einzige Serialisierung für **alle** Sync-Vergleiche (`dataJSON()`, `syncRecipes()`,
`onRecipesRemote()`, `pushGroupPlan()`/`onGroupPlansRemote()`). Details und die vollständige
Liste der Vergleichsstellen: `docs/ARCHITECTURES.md`, Abschnitt „Cloud-Synchronisation".

**Zwei Teilbefunde, die für sich genommen schon reichten, den Sync dauerhaft zu stören:**

* **Berechnete Werte gehören nie in einen Push.** `shopPersons()` ist ein abgeleiteter
  Anzeigewert (hängt an `groupMembers.length`/`"shopForAll"`), keine Kontoeinstellung. `pushNow()`
  schrieb ihn trotzdem roh in die Cloud — dadurch überschrieb er in der Gruppe eine bewusst auf 1
  gesetzte Zahl dauerhaft, und weil er sich pro Gerät je nach Gruppenzustand unterschiedlich
  berechnet, war er selbst wieder eine Endlos-Schreib-Quelle, ganz ohne Reihenfolge-Problem.
* **„Kein Toast" beweist nicht „kein Render".** `onRecipesRemote()` ist der einzige
  Render-Auslöser im Sync **ohne** eigenen Toast (anders als `onRemote()`, das „Von anderem Gerät
  aktualisiert" meldet). `hydrateImages()` hängt `r.image` als **letzten** Schlüssel an — danach
  liegt jedes Foto-Meal dauerhaft quer zu seiner Cloud-Form, `onRecipesRemote()` hält es für
  geändert, rendert neu, ohne dass irgendein Toast das anzeigt. Wer bei Bilder-Zucken zuerst nach
  einer fehlenden Meldung sucht, findet nichts — die Abwesenheit des Tosts ist hier gerade das
  Symptom, nicht der Hinweis auf die Ursache.

**Nachweis im Prüfstand:** Zwei Ausschneide-Prüfstände (Hauptdokument + Rezeptpfad), Details in
`docs/TESTING.md`. Gegen den alten Stand (`git show HEAD:index.html`) gegengeprobt: dort
oszilliert das Hauptdokument alle 40 Runden mit konstant zwei Schreibvorgängen pro Runde (der
„Dauer-Schreibverkehr" aus der Reihenfolge-Lücke, unabhängig vom sichtbaren Rendern), und der
Rezeptpfad zeigt bei erneut angewendetem `hydrateImages()`-Effekt (simuliert einen wiederholten
`render()`-Zyklus) fortlaufend Puts und Renders. Mit `canonJSON` ist beides ab der jeweils
nächsten Runde still.

### Rückfall am 06.08.2026: das dazugehörige Sicherheitsnetz griff nie

Der Fix brachte ein zweites Sicherheitsnetz mit (`lastGroupAttempt`, verhindert, dass ein
gescheiterter Gruppen-Beitrittsversuch bei jedem weiteren Snapshot erneut `switchGroup()`
auslöst — siehe `docs/ARCHITECTURES.md`, Abschnitt „Sicherheitsnetz gegen wiederholtes
switchGroup()"). Die erste Fassung setzte das Flag in `onRemote()`, direkt bevor `switchGroup()`
aufgerufen wurde. Das sah beim Code-Lesen richtig aus und war es nicht: `switchGroup()` ruft als
Erstes `stopCloudSync()` auf, und `stopCloudSync()` setzt genau dieses Flag wieder zurück — noch
bevor der eigentliche Fehlschlag (im `catch`-Block von `startCloudSync()`/`activateGroup()`/
`joinGroup()`) überhaupt eintritt. Der in `onRemote()` gesetzte Wert war zum Zeitpunkt des
Scheiterns also längst wieder `null`, das Netz strukturell wirkungslos — ein Prüfstand, der nur
den Normalablauf fährt (immer erfolgreicher Handshake), deckt das nicht auf, weil er den
Fehlerpfad nie durchläuft.

**Lehre, die über diesen einen Fall hinausgeht:** Ein Flag, das ein Aufräumpfad zurücksetzt, darf
nicht **vor** diesem Aufräumpfad gesetzt werden. Bei jedem neuen Sicherheitsnetz prüfen, in
welcher Reihenfolge die beteiligten Funktionen tatsächlich laufen — nicht nur, ob das Flag
irgendwo gesetzt wird. Die korrigierte Fassung setzt `lastGroupAttempt` deshalb an den drei
Stellen, die `groupSyncFailed = true` setzen (den `catch`-Blöcken selbst), nicht am Aufrufer.

**Nachweis im Prüfstand:** Eigener dritter Prüfstand, der `onRemote()`/`switchGroup()`/
`stopCloudSync()` echt ausschneidet und nur `startCloudSync()` realistisch stubbt (Stub spiegelt
exakt den `catch`-Block: `syncUid` bleibt gesetzt, `groupSyncFailed = true`, `lastGroupAttempt`
zeigt auf die gescheiterte Gruppe). Mehrere Snapshots mit derselben `remoteGid` nach einem
gescheiterten Versuch lösen `switchGroup()` genau einmal aus, ein echter Gruppenwechsel (andere
`remoteGid`) erneut. Gegenprobe gegen den alten Stand: dort läuft `switchGroup()` bei jedem
Snapshot erneut an. Details in `docs/TESTING.md`.

## 45. `fromCache` ist kein Beweis

**Kontext:** Firestore läuft seit dem Offline-Cache-Paket mit `persistentLocalCache` statt dem
flüchtigen `getFirestore(app)` (`docs/ARCHITECTURES.md`, Abschnitt „Firestore-Offline-Cache").

**Symptom, das ohne die Vorkehrung hier entstünde:** Genau der Gruppenverlust aus Ziffer 35 — nur
über einen neuen Weg. `enterGroupSync()` schließt aus „Gruppendokument fehlt" bzw. „eigene UID
nicht in der Mitgliederliste" auf `"gone"` und räumt dann `state.groupId`.

**Ursache:** Mit dem flüchtigen Cache **warf** `getDoc`/`getDocs` offline zuverlässig — laut und
erkennbar als Fehler. Mit Persistenz liefern beide **still den letzten bekannten Stand** aus
IndexedDB zurück, kenntlich nur über `snap.metadata.fromCache`. Liefert der Cache eine
Mitgliederliste aus der Zeit **vor** dem eigenen Beitritt, ist sie nicht leer — der `!members.length`-Guard
aus Ziffer 35 greift also **nicht** — enthält aber die eigene UID nicht. Ohne Gegenmaßnahme:
`"gone"` → Zeiger weg → Gruppe wieder verschwunden, diesmal ohne dass überhaupt ein Fehler auftrat.

**Lösung:** `CloudGroup.fetch()`/`fetchMembers()` geben `fromCache` mit zurück (`{ data, fromCache }`
bzw. `{ members, fromCache }`), `watchMembers()` reicht es als zweiten Callback-Parameter durch.
`enterGroupSync()` leitet aus einem `fromCache`-Ergebnis **nie** `"gone"` ab, sondern `"error"` —
derselbe Zustand wie bei einer leeren Mitgliederliste, der Zeiger bleibt stehen, der nächste Start
entscheidet mit Serverdaten. `onMembersRemote()` überspringt den Rauswurf-Zweig (Toast +
`switchGroup(null)`) bei `fromCache`. Der Aktivierungspfad in `startCloudSync()` (Wartezustand)
löst bei `fromCache` ebenfalls keine Aktivierung aus, sondern hängt weiter einen Live-Listener an.

**Löschung, gleicher Anlass:** Der Cache ist ab jetzt ein Speicherort im Sinne von Ziffer 37 —
siehe dort und die `terminate()`-vor-`clearIndexedDbPersistence()`-Reihenfolge in
`CloudSync.wipeCache()`.

**Falle beim Umsetzen:** `initializeFirestore` mit `persistentLocalCache` sitzt im selben großen
`try`-Block wie der übrige Cloud-Aufbau, dessen `catch` `cloudauth:disabled` wirft und die
**gesamte** Cloud-Anmeldung deaktiviert. Ein eigenes, inneres `try/catch` mit Fallback auf
`getFirestore(app)` ist deshalb zwingend — sonst kostet ein reiner Persistenzfehler (Privatmodus
ohne IndexedDB, exotische WebView) die ganze Cloud-Anmeldung, nicht nur den Komfortgewinn.

**Nachweis im Prüfstand:** Zwei zusätzliche Szenarien neben den acht aus Ziffer 35 — `fetchMembers()`
mit `fromCache:true` und Liste ohne eigene UID (muss `"error"` liefern), jeweils mit Gegenprobe bei
`fromCache:false` (dort muss weiterhin `"gone"` herauskommen, sonst ist der echte Rauswurf kaputt).
Details in `docs/TESTING.md`.

## 46. Ein Reload vor dem erfolgreichen Push kann eine lokale Änderung innerhalb einer bereits
    bekannten Woche verlieren — vorbestehend, nicht durch den Offline-Cache verursacht

**Symptom:** Im Flugmodus-Test von Hand zu Ziffer 45 (siehe `docs/TESTING.md`, „Offline-Testverfahren"):
offline Meals zu einem Tag hinzugefügt, WLAN wieder an, App neu geladen — die Meals waren noch da.
Ein **zweiter** Reload kurz danach zeigte den Tag wieder leer. Per direktem Firestore-REST-Aufruf
verifiziert (nicht nur über die App-Anzeige): Der Server-Stand kannte die Meals nie, obwohl der Push
danach als `"synced"` markiert wurde.

**Ursache:** `startCloudSync()` (Zeile ~4057) führt bei einem Konto **ohne** aktive Gruppe den lokalen
und den geladenen Cloud-Plan pro **Woche**, nicht pro Tag/Slot, zusammen:

```js
const rp = pruneWeeks(normalizePlans(plansField(remote), state.recipes));
Object.keys(state.plans).forEach(k => { if (!rp[k]) rp[k] = state.plans[k]; }); // lokale Wochen behalten, die es remote nicht gibt
state.plans = pruneWeeks(rp);
```

Nur Wochen, die der Server **gar nicht** kennt, bleiben vom lokalen Stand erhalten. Für eine Woche,
die auf beiden Seiten existiert, gewinnt bedingungslos die Cloud-Version — auch wenn der lokale Stand
eine Änderung enthält, die noch nicht erfolgreich gepusht wurde. Trifft ein Reload also genau in dieses
Fenster (Änderung gemacht, aber `pushNow()` noch nicht durchgelaufen — z. B. weil der vorherige Push
offline hängen blieb), überschreibt der nächste `startCloudSync()`-Lauf die Änderung mit dem älteren
Server-Stand, und der anschließende Baseline-Push (`await pushNow()`, direkt nach `syncHandshakeOk = true`)
schreibt diesen bereinigten Stand zurück — die Änderung ist dann auch auf dem Server weg, nicht nur lokal.

**Wichtig, damit hier niemand denselben Verdacht zweimal prüft:** Das ist **kein** Rückfall durch
`persistentLocalCache` (Ziffer 45) — die Merge-Zeilen oben sind nicht Teil des Firestore-Cache-Commits
und verhalten sich unabhängig davon, ob `getDoc` aus dem Cache oder vom Server antwortet. Das Risiko
besteht grundsätzlich immer dann, wenn zwischen einer lokalen Änderung und ihrem erfolgreichen Push ein
Reload passiert — mit dem Offline-Cache ist das nur leichter zu erreichen (offline weiterplanen fühlt
sich jetzt normal an), nicht neu entstanden.

**Bewusst nicht mitgefixt:** Ein slot-genaues Merge (statt Wochen-Ersetzung) für den persönlichen
Plan wäre ein eigenes, größeres Paket — analog zur bereits vorhandenen slot-genauen Merge-Logik im
Gruppenmodus (`groups/{gid}/plans`, ein Dokument je Woche mit flachen Feldern, siehe
`docs/ARCHITECTURES.md`, Abschnitt „Gruppen-Wochenplan"). Nicht ungefragt im Rahmen des
Offline-Cache-Pakets umgesetzt (CLAUDE.md §31, Minimalprinzip).

## 47. Zweiter Tab bekommt Änderungen des ersten nicht live mit (unbestätigt, nicht root-ursächlich geklärt)

**Symptom im Multi-Tab-Test zu Ziffer 45** (`docs/TESTING.md`, „Offline-Testverfahren"): zwei Tabs
mit demselben Konto gleichzeitig offen, in Tab 1 ein Meal eingeplant. Der Server hatte die Änderung
sofort (per direktem Firestore-REST-Aufruf gegengeprüft), ein manueller `CloudSync.load()` in Tab 2
zeigte sie ebenfalls korrekt — aber die laufende Seite in Tab 2 aktualisierte sich auch nach rund
60 Sekunden nicht von selbst. Kein Rauswurf, keine Fehlermeldung, `firestore_clients_*` in
`localStorage` zeigte beide Tabs korrekt als zwei registrierte Clients — nur der Live-Listener
(`window.CloudSync.watch(uid, onRemote)`) schien in Tab 2 nicht auf die Änderung zu reagieren.

**Möglicher Zusammenhang mit `persistentMultipleTabManager`:** Vor dem Offline-Cache-Paket lief
jeder Tab mit `getFirestore(app)` unabhängig und direkt gegen den Server — Live-Updates kamen
unabhängig vom Zustand anderer Tabs an. Der Multi-Tab-Manager bündelt die tatsächliche
Serververbindung dagegen auf einen primären Tab; die übrigen sollen Änderungen über die gemeinsame
IndexedDB mitbekommen. Dieser Weg scheint hier nicht (rechtzeitig) zu greifen.

**Ausdrücklich unbestätigt:** Nicht bis zur Ursache instrumentiert. Könnte auch ein Artefakt der
ferngesteuerten Browser-Testumgebung sein (Chrome drosselt Timer in nicht fokussierten Tabs, was die
interne Cross-Tab-Benachrichtigung verzögern könnte) statt ein echter App-Fehler. Kein Datenverlust
in diesem Test — nur die Live-Anzeige blieb stehen, ein manueller Reload zeigte den korrekten Stand.

**Nächster Schritt bei erneutem Auftreten:** Mit zwei echten, sichtbaren Browser-Fenstern (nicht
ferngesteuert) nachstellen, um Tab-Drosselung als Ursache auszuschließen. Erst danach entscheiden,
ob ein Fix nötig ist.

## 48. `deleteAccountFlow()` kann durch einen einzigen fremden oder toten `shared/{id}`-Eintrag
    dauerhaft blockiert werden — DSGVO-relevant (gefunden und behoben)

**Symptom im Löschtest zu Ziffer 45** (`docs/TESTING.md`, „Offline-Testverfahren"): „Konto löschen"
brach mit `Es ist ein Fehler aufgetreten. (permission-denied)` ab, ohne dass ein erneuter Versuch
half — der Fehler ist strukturell, kein vorübergehendes Netzproblem.

**Ursache:** `deleteAccountFlow()` löscht `state.shares` (die Liste eigener Teilen-Link-Codes) in
einer Schleife (index.html, `CloudAuth.deleteAccount()`), **ohne** einzelne Fehler abzufangen —
bewusst so kommentiert, damit ein liegengebliebener Snapshot nicht stillschweigend übersehen wird.
Diese Annahme bricht, wenn `state.shares` einen Eintrag enthält, der **nicht mehr existiert** (404)
oder **einer fremden UID gehört** — die Firestore-Regel `allow delete: if resource.data.uid ==
request.auth.uid` (`firestore.rules`) blockt Letzteres zu Recht als Sicherheitsgrenze, nicht als Bug.
Auf dem betroffenen Testkonto trugen mehrere der 18 gespeicherten Share-IDs eine fremde UID sowie
zwei weitere gar keine existierende Cloud sein Dokument mehr — beides per direktem Firestore-REST-
Aufruf verifiziert, nicht nur vermutet.

**Warum das über einen kaputten Testdatensatz hinausgeht:** `state.shares` wird ausschließlich per
`unionIds()` zusammengeführt (`onRemote()`) — Einträge werden nie automatisch entfernt, auch nicht,
wenn der zugehörige `shared/{id}`-Zugriff schon lange fehlschlägt. Wie genau eine fremde UID in
dieses Konto gelangte, wurde nicht abschließend geklärt (denkbar: Kontowechsel im selben Browser
ohne vollständige lokale Bereinigung dazwischen). Unabhängig vom genauen Weg bleibt die Lücke: **ein
einziger nicht löschbarer Eintrag in `shares` blockiert die gesamte Kontolöschung ohne Weg zur
Selbsthilfe für den Nutzer** — das betrifft die Löschzusage aus Ziffer 10 der Datenschutzerklärung
und Art. 17 DSGVO.

**Für den ursprünglichen Löschtest umgangen, nicht behoben:** die betroffenen Share-IDs wurden
zunächst direkt in Firestore aus `state.shares` des Testkontos entfernt (Datenreparatur, kein
Code-Fix) — die Löschung lief danach durch.

**Fix (separater Schritt, auf Nutzerwunsch nachgezogen):** `deleteAccount()` prüft jetzt bei drei
betroffenen Löschvorgängen — `shared/{id}`, `groups/{gid}/members/{uid}`, `invites/{code}` — gezielt
den Fehlercode. `shared/{id}` (`firestore.rules:70f.`) und `invites/{code}` (`firestore.rules:171f.`)
referenzieren in ihrer `delete`-Regel tatsächlich `resource.data...`, nicht nur den Pfad — deshalb
liefert Firestore für ein **bereits nicht mehr existierendes** Dokument denselben
`"permission-denied"`-Fehler wie für ein fremdes (`resource` ist bei einem nicht existierenden
Dokument `null`, der Zugriff auf `.data` scheitert). Bei `groups/{gid}/members/{uid}`
(`firestore.rules:134f.`, `request.auth.uid == uid || isOwner(gid)`) greift dagegen beim
Selbstlöschen die linke Seite der Oder-Verknüpfung per Kurzschluss immer, unabhängig vom
Dokumentinhalt — `resource.data` wird praktisch nie ausgewertet; `deleteBestEffort()` dient hier vor
allem der Konsistenz mit den anderen beiden Stellen, nicht derselben Notwendigkeit (Fund von
`anwalt`, korrigiert gegenüber einer ersten, zu pauschalen Version dieses Absatzes).

Die neue Hilfsfunktion `deleteBestEffort(ref)` verzeiht **ausschließlich** `"permission-denied"` und
macht mit dem nächsten Eintrag weiter; jeder andere Fehlercode (Netz, noch nicht veröffentlichte
Regeln) bricht die Löschung weiterhin ab, damit der Nutzer es erneut versuchen kann — das war die
ursprüngliche Absicherung und bleibt erhalten. Die `recipeIds`-Schleife und der abschließende
`deleteDoc(doc(db,"users",uid))` bleiben unverändert bei striktem `deleteDoc()`: ihre Regeln sind
rein pfadbasiert (kein `resource.data`-Zugriff), das Problem existiert dort strukturell nicht.

**Rechtstext nachgezogen:** Ziffer 10 der Datenschutzerklärung versprach zuvor unbedingt „schlägt das
für einen einzelnen Link fehl, bricht die Löschung ab" — das traf nach dem Fix nicht mehr zu (Fund
von `anwalt`). Text ergänzt: ein Link, der sich beim Löschversuch als nicht (mehr) dem Konto
zugeordnet herausstellt, wird übersprungen; nur ein Fehlschlagen aus einem anderen Grund bricht
weiterhin ab.

**Bewusst nicht behoben:** *wie* die fremde UID überhaupt in `state.shares` gelangte (vermuteter,
nicht bestätigter Kontowechsel im selben Browser). `unionIds()` entfernt weiterhin nie einen Eintrag —
das ist beabsichtigt (kein Share-Link darf durch einen Merge verloren gehen), heißt aber, ein einmal
hineingeratener Fehleintrag bleibt bis zur Kontolöschung bestehen. Er blockiert die Löschung durch
diesen Fix nur nicht mehr.

**Nachweis im Prüfstand:** Ausschneide-Prüfstand für `deleteAccount()` (Fake-`deleteDoc()`, die je
nach Dokument-ID `permission-denied`, einen anderen Fehlercode oder Erfolg liefert), sechs Szenarien,
alle PASS: Normalfall; je ein verziehener `permission-denied` bei Share/Gruppenmitglied/
Einladungscode (inkl. Beleg, dass die Schleife beim Share-Fall tatsächlich mit dem nächsten Eintrag
weitermacht, nicht nur die Gesamtfunktion nicht wirft); ein echter anderer Fehlercode (`unavailable`)
bricht weiterhin ab; ein `permission-denied` bei einem Rezept bricht ebenfalls ab (Regressionstest,
nur die drei beabsichtigten Stellen sind tolerant). Gegenprobe gegen `git show HEAD:index.html`
(Stand vor diesem Fix): dort scheitern genau die drei Verzeihen-Szenarien wie erwartet — der Fix
verändert also nachweislich etwas.

**Von `anwalt` und `website-security` geprüft** (nach den beiden oben genannten Korrekturen erneut
freigegeben, siehe Rechtstext- und Kommentar-Anpassung): keine Angriffsfläche durch das gezielte
Verzeihen von `"permission-denied"`, kein zu weiter Catch-Alles, keine Datenreste, die die
Löschzusage verletzen — ein übersprungenes fremdes Dokument enthält keine personenbezogenen Daten
dieses Kontos.

## 49. `wipeCache()` stand am falschen Objekt und lief dadurch nie (gefunden und behoben)

**Symptom im Löschtest zu Ziffer 45:** Nach vollständig erfolgreicher Kontolöschung (Server-Löschung
bestätigt, Weiterleitung zur Registrierung) lagen weiterhin alle 26 Dokumente des gelöschten Kontos
im Firestore-Cache (`remoteDocumentsV14`, per direktem IndexedDB-Zugriff ausgelesen) — das komplette
`users/{uid}`-Kontodokument und alle Rezept-Unterdokumente. Kein Fehler-Toast, kein Hinweis.

**Ursache:** Beim Umsetzen von TEIL 3B ist `wipeCache` versehentlich in das Objektliteral von
`window.CloudGroup` gerutscht statt in `window.CloudSync` (beide Objekte enden im Quelltext mit einem
sehr ähnlichen `deleteInvite`-Eintrag, das war die Verwechslungsstelle). `wipeLocalData()` prüft
`if (window.CloudSync && window.CloudSync.wipeCache) await window.CloudSync.wipeCache();` —
`window.CloudSync.wipeCache` war dadurch immer `undefined`, der Guard griff also genauso wie beim
vorgesehenen Fall „Firebase nicht konfiguriert" und übersprang den Aufruf lautlos. Kein Fehler, keine
Meldung, einfach ein nie ausgeführter Schritt.

**Verifiziert vor UND nach dem Fix, direkt per IndexedDB-Inhalt (nicht nur Datenbank-Namen, die auch
nach einem Reload leer neu angelegt werden und nichts beweisen):**

* Vorher: `window.CloudSync.wipeCache` → `undefined`. Isolierter Aufruf war nicht möglich; die
  26 Alt-Dokumente blieben auch 8 Sekunden nach der Löschung unverändert liegen.
* Nachher: `window.CloudSync.wipeCache` → Funktion. Isoliert aufgerufen (bewusst ohne anschließenden
  Reload, um einen Reload-Race als Erklärung auszuschließen) → die gesamte `remoteDocumentsV14`-Store
  existierte danach nicht mehr (`no-store`, die komplette Datenbank wurde neu angelegt). Kein Race mit
  dem Reload, rein die falsche Objektzuordnung war die Ursache.

**Lehre:** Bei zwei strukturell ähnlichen Objektliteralen im selben Modul (hier `CloudSync`/
`CloudGroup`, beide mit `deleteInvite`) reicht „nach dem passenden Text suchen" nicht — die
schließende Klammer der jeweiligen Funktion muss mitgeprüft werden. Ein Test, der nur „wirft
`wipeCache()` einen Fehler" prüft, hätte diesen Bug nicht gefunden: der Aufruf wurde nie erreicht,
es gab nichts, das hätte werfen können. Erst die Kontrolle des tatsächlichen IndexedDB-**Inhalts**
nach der Löschung deckte es auf.

## 50. Messenger-Crawler führen kein JavaScript aus — statische `og:`-Tags reichen für geteilte Links nicht

**Symptom:** Ein per `shareRecipeNow()`/`openShareRecipe()` verschickter `?s=<id>`-Link zeigte in WhatsApp/Telegram immer dieselbe generische Karte („Paddy's Mealplan – Plan it. Cook it. Lift it.") statt Meal-Name und Meal-Foto, obwohl `index.html` den Link korrekt öffnet.

**Ursache:** `index.html` hat feste `og:`-Tags im `<head>` (Zeile 19–28). GitHub Pages liefert für jeden Pfad dieselbe Datei aus, unabhängig vom `?s=`-Parameter. Der Client könnte den Titel zwar per JS ändern, aber Messenger-Crawler (WhatsApp, Telegram, Facebook, …) führen kein JavaScript aus — sie lesen ausschließlich das erste ausgelieferte HTML.

**Lösung:** `worker/og.js`, eine Cloudflare-Worker-Schicht vor GitHub Pages (siehe `docs/ARCHITECTURES.md`, „Link-Vorschau in Messengern"). Der Worker reicht jede Anfrage unverändert an GitHub Pages weiter und ersetzt bei `?s=<id>` per `HTMLRewriter` nur die `og:`/`twitter:`-Werte im bereits ausgelieferten HTML — kein User-Agent-Sniffing, Crawler und Mensch bekommen dasselbe HTML, die App startet unverändert.

**Falle beim Testen:** Ein normaler `curl`/Browser-Aufruf ohne Crawler-User-Agent zeigt nichts über das Cloaking-Risiko — Facebook/WhatsApp cachen die erste abgerufene Vorschau zudem oft mehrere Stunden. Zum Prüfen den Facebook Sharing Debugger nutzen (erzwingt einen Re-Scrape) oder `curl -A "facebookexternalhit/1.1"`.

Gilt sinngemäß für jede künftige Funktion, die eine dynamische Linkvorschau braucht, solange die App ohne eigenen Server (GitHub Pages, kein SSR) ausgeliefert wird.

## 51. `onRecipesRemote()` ersetzt Rezept-Objekte statt sie zu mutieren — langlebige Ansichten müssen immer über `getRecipe(id)` zugreifen

**Symptom (Risiko, das der damalige Meal-Ansicht-Umbau bewusst verhindert):** Eine offene, langlebige Ansicht auf ein Meal hält eine JS-Referenz auf das Rezept-Objekt. Ein anderes Gerät ändert dasselbe Meal in der Cloud. Der lokale Sync-Listener zieht den neuen Stand — aber die offene Ansicht schreibt weiter in die alte, jetzt abgehängte Objekt-Referenz. Kein Absturz, keine Fehlermeldung, die Eingabe verschwindet einfach lautlos.

**Ursache:** `onRecipesRemote()` (`index.html`, Firestore-Listener auf die `recipes`-Subcollection) **ersetzt** ein geändertes Rezept-Objekt im „modified"-Zweig (`state.recipes[idx] = incoming;`), es mutiert das bestehende Objekt nicht. Jede Referenz, die vor diesem Zeitpunkt gezogen wurde, zeigt danach auf ein Objekt, das nicht mehr Teil von `state.recipes` ist.

**Regel:** Jede langlebige Ansicht (offenes Formular, offenes Detail) greift **ausschließlich** über `getRecipe(id)` zu, nie über eine gehaltene Variable. `openMealSheet()` (siehe `docs/ARCHITECTURES.md`) macht das über `const rec = () => (recId ? getRecipe(recId) : draft);` — jeder Lese-/Schreibzugriff holt frisch.

**Zusätzlich für Autosave-Ansichten:** Eine reine `getRecipe(id)`-Referenz reicht nicht, wenn die Ansicht selbst schreibt — ein `render()`-loser Remote-Merge während des Tippens würde trotzdem die eigene Eingabe überschreiben. `openMealSheet()` setzt deshalb zusätzlich `openSheetId`, das `onRecipesRemote()` veranlasst, Changes für genau dieses eine Meal zu überspringen, solange die Ansicht offen ist (Details in `docs/ARCHITECTURES.md`, „Meal-Ansicht"). Löscht ein anderes Gerät währenddessen genau dieses Meal, greift zusätzlich `openSheetRemovedCb`: die Ansicht schließt sich selbst mit einem Toast, statt lautlos an einem Meal weiterzuschreiben, das nicht mehr existiert.

**`closeModal()` / `modalCloseHook` — bisher nirgends dokumentiert.** `closeModal()` prüft zuerst die modulweite Variable `modalCloseHook`: ist sie gesetzt, ruft `closeModal()` sie auf (und leert sie sofort davor auf `null`) statt des Standard-Schließens (`modalRoot.innerHTML = ""` plus Fokus-Restore). Damit kann eine einzelne Ansicht Escape, Backdrop-Klick, das ✕ im Kopf und einen „Fertig"-Knopf im Fuß gleich behandeln, ohne dass jeder dieser vier Wege einzeln verdrahtet werden müsste — sie rufen alle `closeModal()`, der Hook entscheidet, was wirklich passiert (z. B. erst eine FLIP-Exit-Animation abspielen, oder das Schließen bei einem leeren Namensfeld abbrechen). `modalCloseHook` ist global und wird von jeder Ansicht, die ihn braucht, selbst gesetzt (`openMealSheet()`) und beim eigenen Schließen selbst wieder auf `null` geleert — ein Aufrufer, der ihn setzt, muss ihn auch selbst wieder leeren, `openModal()` tut das nicht automatisch.

## 52. Ein Element ausblenden, das gerade den Fokus hat, löst `focusout` aus — Aufklapp-Zeilen schlossen sich sofort wieder

**Symptom (echter Fehler, gefunden bei der Abnahme am 08.08.2026):** In der Zutatenliste der Meal-Ansicht ließ sich keine Zeile mehr bearbeiten. Ein Klick auf die Zeile tat scheinbar gar nichts — das Formular blitzte nicht einmal sichtbar auf.

**Ursache — eine Kette aus zwei für sich korrekten Mechanismen:**

1. Der Klick trifft `.ing-view-name`, einen echten `<button>`. Der Browser gibt ihm dabei den Fokus.
2. `openIngEdit(row)` setzt `.editing` auf der Zeile. Das CSS blendet daraufhin `.ing-view` aus (`.ing-row.editing .ing-view { display: none }`) — **also genau den Knopf, auf dem der Fokus gerade liegt**.
3. Ein Element, das `display: none` wird, verliert den Fokus. Der fällt auf `<body>` zurück und `focusout` steigt an der Zeile auf.
4. Der `focusout`-Handler der Zeile prüft `row.contains(document.activeElement)` — das ist jetzt `false` — und ruft `closeIngRow(row)`.

Öffnen und Schließen passieren im selben Tick. Im Code ist nichts davon zu sehen: Beide Handler sind einzeln richtig, der Fehler entsteht erst aus ihrem Zusammenspiel über den Umweg CSS.

**Lösung:** Die Zeile trägt `tabindex="-1"` und wird beim Aufklappen programmatisch fokussiert (`row.focus({ preventScroll: true })` direkt nach `openIngEdit()`). Damit bleibt der Fokus innerhalb der Zeile, `row.contains(document.activeElement)` bleibt `true`, der Wächter greift nicht. Bewusst die Zeile selbst und **nicht** `.ing-name`: ein fokussiertes Textfeld zieht auf dem Handy die Tastatur hoch und verdeckt die Nährwertfelder, obwohl der Nutzer vielleicht nur die Menge ändern will.

**Regel für künftige Aufklapp-/Umschalt-Muster:** Wer ein Element ausblendet, das den Fokus tragen könnte, muss den Fokus vorher oder unmittelbar danach aktiv an eine sinnvolle Stelle setzen. Das gilt für jedes Paar aus „Ruhezustand ↔ Bearbeiten-Zustand", das per CSS umschaltet — auch für `.ms-nut`, sollte es je wieder eine Umschaltmechanik bekommen.

**Testhinweis:** Der Fehler ist im Ausschneide-Prüfstand nur sichtbar, wenn man den Fokus vor dem Klick tatsächlich setzt (`btn.focus(); btn.click();`) **und** nach einem Tick misst — der `focusout`-Handler arbeitet mit `setTimeout(…, 0)`. Ein Test, der direkt nach dem Klick prüft, meldet fälschlich „alles gut". Für die Gegenprobe („Fokus nach draußen schließt weiterhin") taugt `document.body.focus()` nicht: `<body>` ist ohne `tabindex` nicht fokussierbar, der Fokus bewegt sich gar nicht und es feuert kein `focusout`. Es braucht ein echtes fokussierbares Element außerhalb der Zeile.

## 53. FLIP wird unsichtbar, wenn Ursprung und Ziel gleich breit sind

**Symptom (Abnahme am 08.08.2026):** Auf dem Handy schien die Meal-Ansicht ohne jede Animation aufzuspringen — im Wochenplan wie im Meals-Reiter. Am Rechner war dieselbe Bewegung deutlich sichtbar. Der naheliegende Verdacht (eine Media Query schaltet die Animation mobil ab) war falsch: der Code lief unverändert, und `reducedMotion()` war nicht im Spiel.

**Ursache:** `flipDelta()` leitet die Skalierung **allein aus der Breite** ab — `s = from.width / to.width`. Das ist Absicht: ein ungleiches `sx`/`sy` staucht den Text sichtbar. Am Rechner steht die Karte in einem Raster (`.recipes`, `minmax(260px, 1fr)`) und ist ~260 px breit, die Ansicht 540 px — `s ≈ 0,5`, ein deutliches Wachsen. Am Handy ist das Raster einspaltig: gemessen bei 360 px Viewport ist die Karte 317 px breit und das Modal 328 px, also `s ≈ 0,97`. Übrig bleibt eine reine Verschiebung um die Differenz der Mittelpunkte — je nach Scrollposition wenige Pixel. Die Animation lief die ganze Zeit, sie war nur nicht zu sehen.

**Lösung:** Unter `max-width: 560px` gar kein FLIP mehr, sondern ein Bottom-Sheet, das hoch- und wieder herunterfährt (siehe `docs/ARCHITECTURES.md`, „Meal-Ansicht"). Die Grenze liegt in `sheetLayout()` bewusst auf demselben Breakpoint wie das CSS und **nicht** auf `pointer: coarse`: über die Darstellung entscheidet die Breite, nicht das Eingabegerät.

**Regel für jede künftige FLIP-Bewegung:** Vorher prüfen, wie weit Ursprungs- und Zielbreite in **allen** Layouts auseinanderliegen. Liegt `from.width / to.width` nahe 1, trägt FLIP dort nicht und es braucht eine andere Bewegung. Das trifft besonders schmale Viewports, in denen ohnehin fast alles die volle Breite hat.

## 54. Im Hintergrund-Tab misst kein Animationstest etwas Verlässliches

**Symptom (beim Prüfen von Ziffer 53):** Im Browser-Prüfstand stand das Sheet nach 600 ms noch mitten in der Bewegung, ein anderes Mal war eine gerade erzeugte Animation schon nicht mehr in `getAnimations()`. Beim Schließen blieb die Ansicht nach 800 ms offen — was wie ein hängender `anim.finished`-Handler aussah, aber keiner war: sobald der Tab sichtbar wurde, lief alles zu Ende.

**Ursache:** Die Chrome-Erweiterung führt JavaScript aus, ohne den Tab zu aktivieren — `document.visibilityState` ist dabei `hidden`. Chrome drosselt in verborgenen Tabs `requestAnimationFrame` und die WAAPI-Zeitachse. Jede Messung, die „nach *n* ms sollte X gelten" prüft, misst dann Zufall: mal steht die Animation still, mal springt sie beim ersten Frame nach einer langen Pause direkt ans Ende.

**Vorgehen stattdessen — zustandsbasiert statt zeitbasiert messen:**

* Die Animation direkt nach dem Auslöser abgreifen (`el.getAnimations()`) und **Keyframes, Dauer und Easing** prüfen. Das belegt, dass die richtige Bewegung angelegt wird, ohne auf Zeit zu warten.
* Für die Geometrie die Animation anhalten und gezielt anspringen: `a.pause(); a.currentTime = dauer * anteil;` und danach messen. So lässt sich der Verlauf punktgenau belegen (Beispiel: bei `0` steht das Sheet vollständig unter dem Viewport, bei `1` bündig am unteren Rand).
* Eine `rAF`-Schleife im Prüfstand **immer** mit einem `setTimeout` absichern. Ohne Sicherheitsnetz löst die Promise im verborgenen Tab nie auf und der Werkzeugaufruf läuft in einen 45-Sekunden-CDP-Timeout, der wie ein abgestürzter Renderer aussieht.
* Bleibt eine Prüfung auf echte Zeit angewiesen, vorher mit einem Screenshot den Tab in den Vordergrund holen — und danach gegenprüfen, dass `visibilityState` noch `visible` ist.

**Verwandt:** Ziffer 47 und der Grundsatz aus Ziffer 43 — ein Hänger im Prüfstand ist erst dann ein Befund, wenn die Messmethode ausgeschlossen ist.

## 55. Ein Transform über die halbe Bildschirmhöhe ist auf dem Handy zu teuer

**Symptom (Rückmeldung nach ~30 Durchläufen am Gerät, 08.08.2026):** Das Bottom-Sheet der Meal-Ansicht fuhr beim Öffnen über die volle Bildschirmhöhe hoch (681 px, 420 ms). Dabei stand die „Schließen"-Zeile immer wieder für den Bruchteil einer Sekunde an falscher Stelle — nicht bei jedem Durchlauf, aber umso häufiger, je länger die Zutatenliste war.

**Erst ausschließen, was es *nicht* ist.** Der naheliegende Verdacht ist ein Layoutsprung (das Sheet wächst noch, während es fährt). Im Prüfstand widerlegt: Animation anhalten, an mehreren `currentTime`-Punkten Sheet-Höhe und Fußposition messen — beide waren über die gesamte Bewegung konstant (681 px bzw. 608 px unter der Oberkante). Wenn die Geometrie stabil ist und trotzdem etwas zuckt, ist es die **Darstellung**, nicht das Layout.

**Ursache:** Ein Transform verschiebt zwar nur eine Compositor-Schicht — aber nur, wenn das Element auch auf einer eigenen liegt und nicht pro Bild neu gerastert werden muss. Hier kam dreierlei zusammen:

1. **Kein `will-change`.** `flipIn()`/`flipOut()` setzen es, der Sheet-Zweig anfangs nicht. Ohne den Hinweis hebt der Browser das Element nicht vorab auf eine eigene Schicht.
2. **Ein aktiver Scroll-Container im bewegten Element.** `.modal-body` bleibt `overflow-y: auto` — ein zweiter Layer, der mitgerastert wird. Genau das erklärt die Abhängigkeit von der Länge der Zutatenliste: Ohne Überlänge ist der Container gar nicht scrollbar.
3. **Ein großes Foto** über die volle Sheet-Breite als Inhalt.

**Lösung — in dieser Reihenfolge:**

* **Den Weg kürzen.** Statt 681 px nur noch 48 px, begleitet von `opacity 0 → 1`. Ein Zehntel der Strecke heißt ein Zehntel der Gelegenheiten, ein Bild zu verlieren, und die Bewegung bleibt trotzdem spürbar. Das ist die eigentliche Abhilfe, die anderen beiden sind Absicherung.
* `will-change` vor dem Start setzen und im `finished`-Handler wieder leeren (Muster aus `flipIn()`). Nicht dauerhaft stehen lassen, siehe Ziffer 25.
* Innere Scroll-Container für die Dauer der Bewegung auf `overflow: hidden`.

**Die Falle bei der Lösung:** Beide Aufräumschritte müssen in **jedem** Ausgang laufen, auch wenn die Animation abgebrochen wird (`anim.finished` rejectet dann) — deshalb `then(clear, clear)`. Bleibt `overflow: hidden` inline stehen, ist die Zutatenliste danach dauerhaft nicht mehr scrollbar, und zwar lautlos. Der Prüfstand muss das eigens abfragen: nach dem Öffnen `getComputedStyle(body).overflowY === "auto"` und `el.getAttribute("style")` leer, zusätzlich einmal mit hart abgebrochener Animation (`anim.cancel()`).

**Regel:** Eine Enter-Bewegung verschiebt ein Element um einige Dutzend Pixel und blendet es dabei ein — sie schiebt es nicht über den halben Bildschirm. Große Flächen zu bewegen ist auf dem Handy nur dann unbedenklich, wenn nichts Teures darin liegt.

## 56. Grid-Auto-Platzierung rutscht hoch, wenn eine Reihe `display: none` ist

**Symptom (beim Sheet-Umbau des Wochenplans, 08.08.2026):** Die Tageskarte sollte
`Kopfzeile / Mahlzeiten (scrollend) / Tagesbilanz` werden — also `grid-template-rows: auto 1fr auto`.
Damit landete die Bilanz in der scrollenden Reihe und die Mahlzeiten in einer festen: genau
vertauscht.

**Ursache:** Ein Element mit `display: none` wird **nicht platziert**. `.day > .day-head` ist auf
dem Handy ausgeblendet, also gibt es nur zwei Kinder. Die Auto-Platzierung setzt `.slots` in
Reihe 1 (`auto`) und die Bilanz in Reihe 2 (`1fr`). Die dritte Reihe bleibt leer und ist
unsichtbar — der Fehler sieht deshalb nach einem CSS-Rechenfehler aus, nicht nach einem
Platzierungsproblem.

**Lösung:** Im Handy-Zweig `grid-template-rows: 1fr auto`, passend zu den tatsächlich platzierten
Kindern. Alternativ jedem Kind ein explizites `grid-row` geben — dann ist es egal, wer fehlt.

**Verwandt:** Optionale Kinder aus einem Template. `dayNutHtml()` gibt bei einem leeren Tag `""`
zurück, dann existiert die Bilanz gar nicht. Das ist unkritisch (die zweite Reihe fällt auf 0
zusammen), aber es heißt: die Anzahl der Kinder ist zur Laufzeit variabel, und eine feste
Reihenliste muss mit **jeder** Kombination aufgehen.

**Prüfregel:** Wo eine Reihenliste auf Kinder trifft, die per Media Query oder per Template
wegfallen können, `grid-template-rows` gegen die tatsächlich gerenderten Kinder prüfen — nicht
gegen das Markup im Editor.

*Das Raster in der Tageskarte gibt es nicht mehr (siehe Ziffer 58) — die Lehre gilt unverändert
für jedes Grid, dessen Kinder per Media Query verschwinden können.*

## 57. Höhe eines Sheets nie aus einzelnen Variablen summieren

> *Das Sheet selbst ist zurückgebaut (Ziffer 58), `--sheet-top` und `--foot-h` gibt es nicht
> mehr. Der Eintrag bleibt, weil der Fehler generisch ist: Er trifft jede Höhe, die aus
> Einzelmaßen zusammengerechnet wird.*

**Symptom:** Der Wochenplan sollte den Rest des Bildschirms füllen:
`100dvh - --head-h - --planhead-h - --tabbar-h`. Ergebnis: 170 px zu hoch, das Sheet schob sich
unter die Reiterleiste.

**Ursache:** Zwischen den Bausteinen liegen Abstände, die in keiner der Variablen stecken — hier
`main { padding-bottom }`, `.section-head { margin-bottom }` und das Innenabstands-Inset von
`.app`. Jede Summe dieser Art ist nur so lange richtig, bis jemand einen Abstand ändert.

**Lösung:** Die **Oberkante messen** statt sie zusammenzurechnen. `syncStickyOffsets()` setzt
`--sheet-top` aus `getBoundingClientRect().top + window.scrollY` — der Wert kennt alles, was
darüber liegt, von selbst. Nach unten ist die Rechnung dagegen zulässig, weil das Inset von `.app`
ausdrücklich als `--tabbar-h + 24px + safe-area` definiert ist; die Fußzeile kommt als gemessenes
`--foot-h` dazu.

**Dokumentposition, nicht Sichtfenster:** `getBoundingClientRect().top` allein wäre falsch, sobald
die Seite beim Messen gescrollt ist. Deshalb `+ window.scrollY`.

**Nebenbefund:** Die Fußzeile kostet 53 px, die aus dem Sheet abgezogen werden müssen. Sie
auszublenden wäre der bequeme Weg — das Impressum muss aber erreichbar bleiben (CLAUDE.md §23).
Die 64 px Bodenluft von `<main>` entfallen im Plan-Reiter dagegen zu Recht: Sie sind Abstand für
eine Seite, die gescrollt wird.

## 58. `overflow-y: auto` macht die andere Achse mit zum Scroller — und blockiert die Wischgeste

**Symptom (am Gerät gefunden, 08.08.2026):** Nach dem Sheet-Umbau ließ sich der Wochenplan auf
dem Handy **gar nicht mehr** zwischen den Tagen wischen. Kein Ruckeln, kein Hängen — die Geste
kam schlicht nicht an.

**Ursache, zwei Teile:**

1. `.slots` bekam `overflow-y: auto`, damit die Mahlzeiten in der Karte scrollen. Die
   Spezifikation rechnet die **andere** Achse dabei von `visible` auf `auto` um. Gemessen:
   `getComputedStyle(slots).overflowX === "auto"`, obwohl im Stylesheet nirgends `overflow-x`
   steht. Derselbe Mechanismus ist im Kommentar bei `.week` seit jeher beschrieben — nur
   andersherum, und an der neuen Stelle nicht mitgedacht.
2. Damit war `.slots` ein waagerechter Scroll-Container **im** waagerechten Snap-Streifen. Auf
   Touch gewinnt immer der innere (`CLAUDE.md` §11), der Wisch erreichte `.week` nie.

Dass `.slots` tatsächlich überlief, lag an einer **Trefferfläche**: Das ✕ am Zeilenende hat
`::after { inset: -8px }`, die Zeile hatte nur 2 px seitlichen Innenabstand — die unsichtbare
Fläche ragte 6 px hinaus (`scrollWidth 338` gegen `clientWidth 332`). Sechs Pixel unsichtbarer
Überlauf haben eine Kerngeste ausgeschaltet.

### Der erste Lösungsversuch war falsch — und hat den Ausfall verlängert

> **Diese beiden Zeilen nie wieder als Lösung eintragen:**
> ```css
> touch-action: pan-y;             /* verbietet die Achse, reicht sie NICHT weiter */
> overscroll-behavior-x: contain;  /* unterbindet das Chaining zum Elternteil */
> ```

Sie standen hier einen Commit lang als Empfehlung. Am Gerät blieb das Wischen tot, und zwar
schlimmer als vorher — es ging nur noch über der Kalorienzeile, die als eigene Rasterzeile
außerhalb von `.slots` liegt.

* **`touch-action` ist keine Weitergabe-Anweisung, sondern eine Erlaubnisliste.** Der Browser
  bildet die Schnittmenge über die gesamte Trefferkette. `pan-y` auf einem Kind schaltet
  waagerechtes Panning damit für **alle** Vorfahren ab — genau die Geste, die man retten wollte.
* **`overscroll-behavior: contain`** verhindert ausdrücklich Scroll-Chaining zum Nachbarbereich.
  Auch das ist das Gegenteil des Gewollten.

### Die tragfähige Lösung: gar keinen zweiten Scroller anlegen

Der innere Scroller ist ersatzlos entfallen — die **Seite** scrollt wieder. Damit gibt es nichts
mehr, was die Geste abfangen könnte. Vor dem Sheet-Umbau war es so, und dort funktionierte das
Wischen nachweislich.

Was dabei erhalten bleiben musste, ging auch ohne inneren Scroller:

* Der Höhensprung beim Wischen (Ziffer 42) wird von `fixedHeight` in `initCarousel()` abgefangen —
  die Höhe wird **einmal** auf das Maximum aller Karten gesetzt statt laufend nachgeführt.
* Der Kalorienstand bleibt über eine klebende Leiste (`#day-bal`) sichtbar. Die muss
  **außerhalb** von `.week` liegen: Der Streifen ist wegen `overflow-x` auch senkrecht ein
  Scroll-Kontext, ein `sticky` darin richtet sich an ihm aus statt am Bildschirm.

`overflow: hidden` ist übrigens unkritisch — `.day` trägt es seit jeher, und damals ging das
Wischen. Bei `hidden` kann der Nutzer nicht scrollen, der Browser reicht die Geste weiter. Nur
`auto` und `scroll` fangen sie ab.

**Prüfregel:** In einem Snap-Streifen keinen zweiten Scroll-Container anlegen. Lässt es sich nicht
vermeiden, ist die einzige belastbare Messung: `getComputedStyle(el).overflowX/Y` und
`scrollWidth === clientWidth` auf der Achse, die nicht scrollen soll. **Nicht** über `touch-action`
zu retten versuchen — das war der Umweg, der zwei Runden gekostet hat.

## 59. Ein Aufklapper, der seinen eigenen Auslöser verschiebt, ist praktisch nicht schließbar

**Symptom:** Der Makro-Bereich der Tagesbilanz ließ sich aufklappen, aber nicht wieder zu.

**Nicht die Ursache:** Die Toggle-Logik. `expandedDayGoals` setzt und löscht korrekt, und im
Prüfstand ging `aria-expanded` sauber von `false` auf `true` und zurück. Ein Test, der nur
programmatisch klickt, findet diesen Fehler **nie**.

**Die Ursache ist Geometrie.** Die Bilanz sitzt im Sheet fest am Kartenfuß. Klappt etwas darin
auf, wächst sie nach **oben** — und nimmt alles mit, was darüber liegt, einschließlich ihres
eigenen Auslösers. Gemessen: Der Knopf sprang von `y=487` auf `y=338`, also 149 px. Wer ein
zweites Mal an dieselbe Stelle tippt, trifft einen Makrobalken.

**Lösung:** Reihenfolge im Markup umdrehen. Der aufklappende Inhalt steht **vor** der Zeile mit
dem Auslöser; die bleibt damit unterste Zeile und bewegt sich keinen Pixel (nachgemessen: 0 px).

**Zweiter Fall derselben Klasse (08.08.2026): eine Umsortierung.** Die Gerichte eines Slots
wurden nach Zuweisung gruppiert (gemeinsam → eigene → fremde). Weist man eines jemandem zu,
wechselt es die Gruppe und rutscht im selben Moment an eine andere Stelle. Bei zwei
Gruppenmitgliedern schaltet das Personen-Icon ohne Zwischenmenü durch — der Sprung passiert
also direkt unter dem Finger, und beim zweiten Tippen trifft man ein anderes Gericht.

Auch hier war die Logik korrekt: Die Sortierung tat genau, was sie sollte. Der Fehler lag in der
Abwägung — sie löste einen seltenen Fall (ab drei fremden Gerichten in *einem* Slot bündeln, um
sie einklappen zu können) und kostete dafür bei **jeder** Zuweisung einen Sprung. Ersatzlos
entfernt; das Einklappen zählt jetzt in Plan-Reihenfolge und funktioniert unverändert.

**Die verallgemeinerte Regel:** Eine Liste, deren Reihenfolge von einer Eigenschaft abhängt, die
man per Antippen ändern kann, sortiert sich unter dem Finger um. Das ist fast immer ein
Bedienfehler, egal wie sinnvoll die Sortierung für sich ist. Entweder die Reihenfolge stabil
halten oder den Übergang sichtbar animieren — aber nie stumm umspringen lassen.

**Prüfregel:** Bei jedem Aufklapper die Bildschirmposition des Auslösers vor und nach dem Öffnen
vergleichen. Zusätzlich `elementFromPoint()` auf den alten Koordinaten abfragen — trifft man dort
noch den Auslöser? Bei einem Element, das an einer Kante verankert ist, ist das keine
Feinheit, sondern der Unterschied zwischen bedienbar und kaputt.

---

## 60. `flex-wrap: wrap` in der Kopfzeile — ein Umbruch, der die Leiste verdoppelt

Die Kopfzeile (`.head-inner`) trägt `flex-wrap: wrap`. Auf breiten Geräten fällt das nie auf. Bei
360 px reichte die Zeile nicht mehr für Marke und Profilknopf: Das Profil rutschte unter die Marke
und die Kopfzeile wuchs von 41 px auf **90 px** — 49 px, die dem Wochenplan fehlten.

Der Umbruch war kein Platzmangel, sondern eine fehlende Erlaubnis zu schrumpfen. **Ein Flex-Kind
schrumpft ohne `min-width: 0` nie unter die Breite seines Inhalts** — die Vorgabe ist `min-width:
auto`. Die Marke bestand also auf ihrer vollen Breite, und wenn der Container die nicht hergibt,
bleibt bei `wrap` nur der Umbruch.

**Behoben** in einem eigenen Block bei `max-width: 400px`:

* `flex-wrap: nowrap` — die Zeile bleibt eine Zeile.
* `.brand { min-width: 0 }` — die Marke darf schrumpfen.
* `.brand .slogan { display: none }` — der Slogan weicht zuerst, er ist Zierde.
* `.brand h1` mit `text-overflow: ellipsis` — greift erst unter ~340 px.

**Falle im Detail:** Der Slogan ist ein `<div class="slogan">`, kein `<p>`. Eine Regel
`.brand p { display: none }` greift ins Leere und die Höhe bleibt unverändert bei 56 px. Vor dem
Ausblenden im Markup nachsehen, nicht raten.

**Prüfregel:** Kopfzeilenhöhe bei 320, 360, 390 und 430 px messen. Sie muss überall gleich sein.
Ein einzelner Ausreißer nach oben ist immer ein Umbruch.

**Messfalle:** Der Prüfstand (`stand.py`) kopiert `index.html` **beim Start** in sein Wurzelver-
zeichnis, um den `apiKey` zu neutralisieren. Eine Änderung nach dem Start ist unsichtbar, und ein
zweites `python stand.py` scheitert still am belegten Port — es misst weiter der alte Server. Den
Prozess auf Port 8181 erst per `netstat -ano` suchen und beenden. Jede Messung mit einer Zusiche-
rung absichern, die belegt, dass der neue Stand tatsächlich geladen ist (etwa eine Suche nach dem
neuen Selektor im DOM).

## 61. Ein Farbstreifen im Fensterrand — warum das kein zweiter Scroller wird

**Stand 09.08.2026.** Der Farbstreifen der Mahlzeiten (`.slot::before`) war auf dem Handy
abgeschaltet und ist mit der Vereinheitlichung zurückgekehrt. Er sitzt dort **nicht** im Textfluss,
sondern per `left: -6px` im 8-px-Innenabstand von `.slots`.

Das sieht auf den ersten Blick nach genau dem Fehler aus, der in Punkt 58 beschrieben ist: Dort hat
die unsichtbar vergrößerte Trefferfläche eines Knopfes 6 px über den Rand geragt, `.slots` dadurch
waagerecht scrollbar gemacht (`scrollWidth 338` gegen `clientWidth 332`) und die Wischgeste zum
Nachbartag vollständig geschluckt.

**Warum es hier trotzdem trägt — zwei Gründe, die zusammen gelten müssen:**

1. Der Streifen bleibt innerhalb der **Padding-Box** von `.slots`. Der Innenabstand ist 8 px, der
   Streifen belegt davon 3 px ab Position −6. Er ragt also nicht über das Element hinaus.
2. Nach **links** gerichteter Überlauf erzeugt bei Leserichtung links-nach-rechts ohnehin keinen
   Scrollbereich — der Browser schneidet ihn ab, statt scrollbar zu werden. Nach rechts wäre
   dieselbe Konstruktion sehr wohl gefährlich.

**Gemessen** (Prüfstand, 390 px, voller Plan mit 23 Zeilen, beide Themes): `scrollWidth −
clientWidth = 0` auf allen sieben Tagen, `overflow` bleibt `visible/visible`. Der vollste Tag war
660 px hoch.

**Wer die Werte anfasst, misst nach.** Ein `left: -10px` läge außerhalb des Innenabstands, und ein
Streifen rechts statt links wäre selbst bei gleichem Abstand ein Scroller. Die Messung steht im
Prüfstand, sie kostet nichts:

```js
var s = document.querySelector('.week > .day > .slots');
console.log(s.scrollWidth - s.clientWidth, getComputedStyle(s).overflowX);
```

## 62. `.btn.icon-gh` schlägt eine einzelne Klasse — der Knopf bleibt quadratisch

**Stand 09.08.2026.** Der Einkaufsknopf sollte am Rechner Symbol **und** Text tragen und erst ab
680 px auf das reine Symbol schrumpfen. Die Regel dafür lautete zunächst:

```css
.shop-ic { width: auto; padding: 0 12px; }
```

Sie hat nicht gegriffen. `.btn.icon-gh { width: 34px }` steht mit **zwei** Klassen da (Spezifität
0-2-0), `.shop-ic` nur mit einer (0-1-0) — der Knopf blieb 34 px breit, der Text lief heraus.

**Richtig ist der Selektor mit denselben Klassen plus der eigenen:**

```css
.btn.icon-gh.shop-ic { width: auto; padding: 0 12px; gap: 8px; }
```

Das gilt für jeden Knopf, der `icon-gh` trägt und trotzdem Text bekommen soll. `icon-gh` einfach
wegzulassen wäre die falsche Abkürzung: An der Klasse hängt das hitSlop-Muster
(`::after { inset: -5px }`, siehe Punkt 38), das auf dem Handy aus 34 px die geforderten 44 px
Trefferfläche macht.

**Auffällig wurde es nur durch Messen**, nicht durch Hinsehen: Die Breite eines Knopfes im
Prüfstand ausgeben (`getBoundingClientRect().width`) und gegen die erwartete Form prüfen — bei
sichtbarem Text darf sie nicht der Icon-Breite entsprechen.

## 63. Kamera-Bühne ≠ Kamera-Bild: warum der Barcode-Scanner nur quer funktionierte

Der Scanner war hochkant praktisch unbenutzbar — man musste das Handy quer drehen, damit ein
Barcode überhaupt in den Rahmen passte. Der Grund steckte in zwei Zeilen, die einzeln beide
plausibel aussahen:

* `getUserMedia` forderte `1280×960` — ein **Querformat**.
* Das CSS nagelte die Bühne unter 560 px per Media Query auf `aspect-ratio: 3/4` — ein
  **Hochformat**.

Mit `object-fit: cover` füllt das Video die Bühne und schneidet den Rest weg. Bei 4:3-Bild in
3:4-Rahmen fällt links und rechts jeweils rund ein Drittel der Bildbreite weg — genau die Achse,
auf der ein Barcode lang ist.

**Die Regel: die Bühne richtet sich nach dem tatsächlichen Stream, nie nach der Bildschirmbreite.**
`track.getSettings()` liefert `width`/`height`; daraus wird eine CSS-Variable (`--scan-ar`,
Breite/Höhe als reine Zahl) gesetzt. Sind Bühne und Bild gleich, ist `cover` deckungsgleich mit
`contain` und schneidet nichts. Zusätzlich wird `aspectRatio` passend zur Haltung angefordert —
aber nur als `ideal`, siehe unten.

Drei Fallen dabei:

* **`aspect-ratio` plus `max-height` kippt das Verhältnis.** Steht daneben `width: 100%`, ist die
  Breite definit und gewinnt; die Höhe wird gekappt und das Seitenverhältnis ist wieder falsch —
  es schneidet erneut. Richtig ist die Höhenbremse über die **Breite**:
  `width: min(100%, calc(var(--scan-h) * var(--scan-ar)))`.
* **Und diese Höhe muss gemessen werden, nicht geschätzt.** Erst stand dort ein fester Wert
  (`62svh`), und der war an beiden Enden falsch: im Hochformat blieb die Bühne 64 px schmaler als
  möglich, obwohl Platz war, und im Querformat ragte der Kasten 1 px aus dem Bildschirm — der
  Foto-Knopf war abgeschnitten. Ein fester Anteil der Bildschirmhöhe kennt die Höhe von
  Kopfzeile, Hinweis und Fuß nicht, und der Hinweis wächst sogar zur Laufzeit (der Fokus-Zusatz
  kann umbrechen). `syncStage()` zieht deshalb die Höhe aller Geschwister plus Abstände von
  `.scanwrap.clientHeight` ab und schreibt das Ergebnis nach `--scan-h` — erneut bei jedem
  `resize` und nach jeder Textänderung.
* **`applyConstraints()` ohne Not lässt das Bild zucken**, weil der Track kurz neu ausgehandelt
  wird. Deshalb beim Drehen nur dann nachfordern, wenn Bild und Haltung wirklich quer zueinander
  liegen — die reine Bühnenkorrektur behebt den Beschnitt ohnehin schon.
* **Constraints hart zu fordern bricht die Kamera.** `aspectRatio: {exact: …}` oder eine feste
  Auflösung liefern auf Geräten, die das Format nicht können, einen `OverconstrainedError` — also
  gar kein Bild, obwohl ein anderes Format völlig ausgereicht hätte. Alles `ideal`.

## 64. `focusMode` gibt es nur in Chromium — der Nahfokus ist kein Bug, der sich überall fixen lässt

Der zweite Scanner-Befund: je näher man an den Barcode ging, desto unschärfer wurde er. Ursache
ist ein Fixfokus — es gab in der ganzen Datei kein `applyConstraints()`, also blieb die Kamera auf
dem, was der Browser vorgab.

Der Hebel ist `track.applyConstraints({ advanced: [{ focusMode: "continuous" }] })`, plus
`single-shot` beim Antippen des Bildes als Rettungsanker, wenn eine Kamera einmal falsch
scharfstellt und dort hängen bleibt.

**Aber: MediaStreamTrack `focusMode` ist derzeit Chromium-only (Android).** Safari/iOS kennt es
nicht. Daraus folgen drei Regeln:

* **Vorher `getCapabilities().focusMode` prüfen**, nicht blind anwenden. Ein `applyConstraints()`
  mit unbekanntem Feld ist nicht garantiert harmlos.
* **Nie `await`, immer `try/catch` samt `.catch()`.** Der Scanner darf an einer Kamera-Feinheit
  nicht hängen bleiben — dieselbe Lektion wie bei `video.play()` (Punkt 18).
* **Nichts versprechen, was das Gerät nicht kann.** Der Hinweis „Antippen stellt neu scharf"
  erscheint nur, wenn die Capability wirklich da ist. Auf iOS bleibt der Fokus Sache des Systems;
  dort hilft stattdessen die höhere angeforderte Auflösung (1920), weil der Code dann auch aus
  etwas mehr Abstand noch genug Pixel je Strich hat.

Automatisiert prüfbar ist das nur mit gemockter Kamera (siehe `docs/TESTING.md`): dass der
Constraint **mit** Capability angefordert wird und **ohne** sie nicht. Ob es am Gerät wirklich
scharf stellt, beweist nur das Gerät.

## 65. Hochformat lässt sich im Web auf dem iPhone nicht erzwingen — das Querformat muss taugen

Der Wunsch „beim Drehen soll sich das Scanner-Fenster nicht mitdrehen" ist im Safari nicht
erfüllbar, und zwar aus drei Gründen gleichzeitig:

* `screen.orientation.lock()` implementiert WebKit nicht. Auf iOS nutzen **alle** Browser WebKit,
  Chrome dort also auch.
* `"orientation": "portrait"` steht bereits in `manifest.webmanifest` — iOS setzt es nicht um,
  auch nicht als installierte Web-App.
* Die naheliegende Bastellösung, den ganzen Sucher per `transform: rotate(90deg)` gegenzudrehen,
  **kippt das Kamerabild**: iOS dreht den Stream schon selbst mit dem Gerät, das Bild steht also
  bereits richtig. Eine Gegenrotation macht aus einem korrekten Bild ein schiefes. UI am Gehäuse
  festnageln **und** Bild aufrecht halten geht nicht — genau deshalb zeigen native, auf Hochformat
  gesperrte Scanner ihr Vorschaubild quer, wenn man das Handy dreht.

**Die Konsequenz: das Querformat nicht bekämpfen, sondern brauchbar machen.** Übereinander
(Kopf → Bild → Hinweis → Fuß) bleiben auf einem 844×390-Bildschirm nur ~240 px Bildhöhe übrig.
Nebeneinander — Bild links, Bedienelemente rechts, per Grid in
`@media (orientation: landscape) and (max-height: 560px)` — sind es ~358 px, also rund die
doppelte Bildfläche für denselben Barcode. Reihenfolge und Elemente bleiben dieselben, nur die
Anordnung wechselt.

Eine echte Sperre gibt es nur in der geplanten Store-App über Capacitor
(`@capacitor/screen-orientation`). Das ist der richtige Ort dafür, nicht das Web.

## 66. Ein offener Scanner + `--virtual-time-budget` = hängender Prüfstand

Wer den Scanner im Prüfstand **offen lässt**, um ihn zu messen, bringt Edge headless zum Stehen:
Die Erkennung läuft als `setTimeout(tick, 160)`-Kette, und virtuelle Zeit springt von Timer zu
Timer. Die Schleife wird damit endlos schnell, das Zeitbudget läuft nie ab, es kommt kein
`--dump-dom`. Sichtbar war nur ein Prozess, der 120 s nichts tat, plus 16 zurückbleibende
`msedge.exe`.

Zwei Gegenmittel, je nach Zweck:

* **Messen mit offenem Scanner:** die native API vorher abschalten
  (`Object.defineProperty(window, "BarcodeDetector", { value: undefined })`) und `loadZXing()`
  hängen lassen. Dann tickt nichts, und die Geometrie steht trotzdem.
* **Ablauf prüfen:** den Scanner am Ende jedes Prüfschritts wirklich schließen (Escape), so wie
  es der Kamera-Prüfstand tut — dort trat das Problem deshalb nie auf.

Zusätzlich: den Browser im Prüfskript mit `WaitForExit(<ms>)` begrenzen und danach hart beenden.
Ohne Grenze schluckt ein einziger solcher Hänger das ganze Zeitfenster.

Und: **zwei `iframe`s gleichzeitig gegen `python -m http.server`** sind ebenfalls ein Hänger-Risiko —
der Server ist einfädig. Rahmen nacheinander messen, nicht parallel.

## 67. Das Logo im PDF hängt jetzt am Netzpfad, nicht mehr am CSS

Das App-Logo lag bis zum 10.08.2026 als 60-KB-Base64 in `--logoL` — mitten im render-blocking
`<style>`-Block. Jeder Seitenaufruf musste diese 60 KB parsen, bevor das erste Pixel erschien,
auch wer das Logo nie zu Gesicht bekam. Es liegt jetzt als `img/logo.png` (45 KB) daneben.

**Die Falle dabei:** `prepareLogoForPdf()` las die Bytes über
`getComputedStyle(document.documentElement).getPropertyValue("--logoL")` und dekodierte das
Base64 selbst. Ein reiner Austausch der CSS-Zeile hätte das Logo im Einkaufslisten-PDF still
durch die Vektor-Marke ersetzt — ohne Fehlermeldung, weil der Pfad bei Misserfolg bewusst
`logoPdfAsset = null` setzt und auf `pdfMarkOps` zurückfällt.

Die Funktion holt die Bytes deshalb jetzt per `fetch("img/logo.png", { cache: "force-cache" })`.

**Bekannte Einschränkung:** Unter `file://` ist `fetch` auf lokale Dateien blockiert. Ein
Prüfstand, der die PDF-Erzeugung über `file:///…` fährt, bekommt deshalb die Vektor-Marke statt
des Logos — das ist kein Fehler, sondern der dokumentierte Rückfall. **PDF-Tests müssen über
HTTP laufen** (`python -m http.server` oder `test-server.ps1`). Vorher funktionierte auch
`file://`, weil `getComputedStyle` keinen Netzzugriff braucht.

Produktion (HTTPS) und Capacitor (`https://localhost` bzw. `capacitor://localhost`) sind nicht
betroffen; dort greift zusätzlich der Service-Worker-Cache.

## 68. Der Service Worker lud 1 MB vor, das kaum jemand brauchte

`SHELL_ASSETS` enthielt bis zum 10.08.2026 alle 32 Meal-Fotos (~724 KB) **und**
`vendor/zxing.min.js` (~332 KB). Beides wurde bei der Installation geladen, bevor der Nutzer
irgendetwas davon anfasste.

ZXing war dabei doppelt teuer: Auf Android/Chrome läuft der Barcode-Scanner über das native
`BarcodeDetector`-API (`loadZXing()` in `index.html`), die Datei wird dort **nie** angefasst.
332 KB für einen iOS-Sonderfall vorab zu laden ist Verschwendung.

Beide gehen jetzt über den normalen Cache-First-Zweig des `fetch`-Handlers und liegen nach dem
ersten Gebrauch genauso dauerhaft im Cache — nur eben erst dann. Ersparnis bei der Installation:
**927 KB** (2203 → 1276 KB).

**Bewusst in Kauf genommen:** Wer die App zum allerersten Mal ohne Netz startet, bevor er je ein
Meal-Foto gesehen hat, bekommt die Rückfall-Kacheln. Wer sie einmal online geöffnet hat, hat
seine Fotos offline.

**Unverändert gilt:** Alles wird Cache-First ausgeliefert. Wird ein Foto **oder das Logo**
ausgetauscht, muss `VERSION` in `sw.js` hoch — sonst sieht ein wiederkehrender Nutzer weiter die
alte Datei. Steht jetzt auf `pm-v6`.

## 69. Ein JSON-LD-Block ist kein JavaScript — der Syntax-Check lief prompt darauf auf

Mit Aufgabe A5 kam ein `<script type="application/ld+json">` in den Kopf von `index.html`.
`python syntax-check.py` meldete sofort:

```text
FEHLER  Block 1 (classic, Zeile 43-57)
        Unexpected token ':'
```

Das war kein Befund, sondern die Bauart des Prüfstands: Er sammelte **jeden** `<script>`-Block
ein und schickte ihn durch `new Function()`. Ein JSON-Objekt scheitert dort zwangsläufig am
ersten `:` — für V8 ist `{ "@context": …}` ein Block mit einem String-Literal, dem ein
Doppelpunkt folgt.

Ein dauerhaft roter Prüfstand ist schlimmer als gar keiner: Man gewöhnt sich an den einen
bekannten Fehler und übersieht den nächsten. `extract_blocks()` entscheidet deshalb jetzt nach
dem `type`-Attribut. Nur die JS-Typen (`""`, `module`, `text/javascript`,
`application/javascript`, …) gehen durch V8. JSON-LD wird mit `json.loads` geprüft und mit
Zeilennummer gemeldet, alles andere übersprungen.

**Der JSON-Check ist kein Trostpreis, sondern der einzige Prüfer, den dieser Block hat.** Ein
Tippfehler im JSON-LD bricht weder Layout noch App — er fällt ausschließlich in der
Suchmaschinen-Auswertung auf, also nirgends, wo man hinsieht.

**Bei künftigen Nicht-JS-Blöcken** (`importmap`, `speculationrules`, Templates) greift dieselbe
Weiche automatisch: Sie werden mit Hinweis übersprungen, nicht fälschlich als Fehler gemeldet.

## 70. Vorschaubilder werden bei WhatsApp, Facebook und Co. **serverseitig** zwischengespeichert

Seit A4 ist `og:image` das eigens gestaltete `og-image.png` (1200×630), und `twitter:card` steht
auf `summary_large_image`.

Das Bild liegt im Repo, weil es unter der Domain abrufbar sein muss. **Seine Quelle liegt es
nicht:** `Marketing/og-image-source.html` ist gitignored wie alle Marketing-Assets. Wer das Bild
neu rendern will, braucht die lokale Datei; der Aufruf steht als Kommentar in ihr drin.

Der Service Worker hat damit nichts zu tun — Crawler haben keinen. Die Falle liegt woanders:
**Die Plattformen cachen die Vorschau auf ihren eigenen Servern**, teils wochenlang. Wer das
Bild austauscht und den Link erneut teilt, sieht mit hoher Wahrscheinlichkeit weiter das alte.

Erwartungsgemäß ist das **kein Bug**. Wenn die neue Vorschau tatsächlich sofort gebraucht wird:

* Facebook/WhatsApp: Sharing Debugger, „Scrape Again"
* LinkedIn: Post Inspector
* Notfalls unter neuem Dateinamen ausliefern (`og-image-2.png`) — das umgeht jeden Fremdcache.

Das Bild wird **absichtlich nicht** in `SHELL_ASSETS` aufgenommen: Die App fordert es nie an,
es wäre reiner Ballast im Precache (siehe Punkt 68).

## 71. Leere `catch`-Blöcke sind jetzt gefüllt — und dabei zwei Fallen aufgetaucht

Aufgabe A7 hat 34 leere `catch (e) {}` und 5 leere `.catch(() => {})` auf den zentralen Melder
`window.noteError(kennung, fehler)` umgestellt (siehe `docs/ARCHITECTURES.md`).

**Falle 1: Ein leerer `catch` ist unzerstörbar, ein gefüllter nicht.**
Steht im `catch` ein Aufruf, kann dieser Aufruf selbst scheitern. Wäre `noteError` aus
irgendeinem Grund nicht da, legte jede der 38 Stellen einen `ReferenceError` nach — die Änderung
hätte also exakt das Gegenteil ihres Zwecks bewirkt. Deshalb steht der Melder als **Erstes im
ersten Script-Block**, hat keine Abhängigkeiten und lädt nichts nach. Wer ihn verschiebt oder
hinter eine Bedingung setzt, baut diese Falle wieder ein.

**Falle 2: `reportError` ist ein belegter Name.**
Der Plan nannte den Hook `reportError()`. `window.reportError` ist aber eine echte Plattform-API,
die einen Fehler an die globalen Handler weiterreicht. Sie zu überschreiben wäre ein stiller
Nebeneffekt an genau der Stelle, an der es um das Gegenteil geht. Der Hook heißt `noteError`.

**Was der Melder ausdrücklich nicht tut:** verschicken oder persistieren. Beides würde die
Datenschutzerklärung berühren (`CLAUDE.md` §20/§23). Er hält 50 Fälle im Speicher und schreibt
gedrosselt nach `console.warn`. Der eigentliche Nutzen entsteht erst mit Store-Telemetrie in
Phase D — dann ist er die eine Stelle, an der sie andockt, statt 38 Stellen.

**Drosselung ist kein Komfort, sondern Voraussetzung:** Ohne sie hätte
`stream.getTracks().forEach(t => { try { t.stop(); } catch … })` bei jedem Scanner-Ende geloggt
und der Ringpuffer wäre nur noch mit Rauschen gefüllt. Pro Kennung ist bei 3 Meldungen Schluss.

---

## 72. Der Rückblick zeigte Streuung und sah dabei wie Zielerreichung aus

Die Balkenhöhe wurde gegen **Min/Max der letzten acht Wochen** gerechnet
(`h = 22 + (s.kcal - min) / span * 78`). Damit bekam eine 1900-kcal-Woche einen hohen Balken,
wenn alle anderen bei 1850 lagen — und einen niedrigen, sobald eine 2400er-Woche dabei war.
Dieselbe Woche, dieselbe Leistung, zwei völlig verschiedene Bilder. Die Grafik sah aus wie
Zielerreichung, zeigte aber reine Streuung.

**Die Falle ist die Bezugsgröße, nicht die Formel.** Eine relative Skala ist für einen Trend
richtig; für eine Aussage „habe ich mein Ziel getroffen?" braucht es das Ziel als Bezug.

Seit 13.08.2026 ist die Balkenhöhe das Verhältnis `kcal / Ziel der jeweiligen Woche`,
gezeichnet bis 140 %; das ±10-%-Zielband liegt als feste Fläche dahinter. Weil jede Woche
gegen **ihr eigenes** Ziel normiert wird, bleibt das Band trotz wechselnder Ziele eine
waagerechte Linie.

Drei Folgefehler steckten in derselben Sektion:

* **Der Streak ließ sich nicht verlieren.** `stats[wk].days > 0` — eine einzige geplante
  Mahlzeit machte eine Woche zur „geplanten Woche". Jetzt `>= STREAK_MIN_DAYS` (5 von 7).
* **Die Werte standen ausschließlich im `title`-Attribut**, und die Balken trugen
  `aria-hidden="true"`. Auf dem Handy gibt es kein Hover: dort war die Grafik damit vollständig
  unbeschriftet und für Screenreader gar nicht vorhanden. Jetzt sind die Balken Knöpfe mit
  `aria-label`, KW-Beschriftung darunter und einer Tippzeile (`aria-live="polite"`) — dasselbe
  Muster wie im Gewichtsdiagramm.
* **„Ziel getroffen" maß gegen das HEUTIGE Ziel.** Wer sein Defizit änderte, änderte damit
  rückwirkend die Bedeutung seiner gesamten Historie. `archiveWeek()` friert das damals gültige
  Tagesziel jetzt als `target` mit ein (B10).

Wochen, die vor dieser Änderung archiviert wurden, haben kein `target` und fallen auf das
heutige Ziel zurück. Das ist Absicht und kein Migrationsfall — der alte Zustand ist nicht
rekonstruierbar, und ein erfundener Wert wäre schlechter als ein bekannter Rückfall.

---

## 73. Ein neues Feld im Slot-Eintrag wäre am Sync fast unbemerkt verschwunden

`unflattenWeek()` filterte eingehende Slot-Einträge so:

```js
.filter(x => typeof x === "string" || (x && typeof x.id === "string" && Array.isArray(x.uids)))
```

Das war für zwei Formen richtig (`"rid"` und `{id, uids}`). Mit dem Portionsfaktor (B5) kam
eine dritte dazu: `{id, p}` — für alle, aber mit halber oder doppelter Portion. Sie hat kein
`uids`-Array. Ein solcher Eintrag von einem anderen Gerät wäre also **stillschweigend
weggefiltert** worden: Das Gericht verschwindet dort aus dem Plan, ohne Fehler, ohne Toast, und
beim nächsten Push schreibt dieses Gerät den Verlust zurück.

**Die Regel, die daraus folgt:** Wer eine Eintragsform ergänzt, muss immer beide Richtungen
anfassen — das Schreiben *und* den Eingangsfilter. Der Filter ist die Stelle, an der fremde
Daten ankommen, und er ist per Konstruktion schweigsam.

Zweiter Punkt an derselben Stelle: Ein Objekt ohne `uids` **und** ohne Faktor ist inhaltlich
die String-Form. Wird es nicht auf sie zurückgeführt, schreibt das Gerät den Eintrag anders
zurück, als er angekommen ist — ein Dauer-Diff im Gruppendokument, genau die Klasse Fehler, vor
der schon der `canonJSON()`-Kommentar in `syncRecipes()` warnt.

Aus demselben Grund waren die Portionsstufen eine **feste Leiter** (0,5 / 1 / 1,5 / 2) und kein
freier Zahlenwert: `0.1 + 0.2` ist in Gleitkomma `0.30000000000000004`, und dieser Wert würde
sich bei jedem Vergleich von seiner eigenen Cloud-Form unterscheiden.

**Nachtrag vom selben Tag: Der Portionsfaktor ist wieder ausgebaut** (Produktentscheidung, siehe
`docs/PRODUCT.md`). Die Lehre bleibt vollständig gültig — und sie gilt beim **Entfernen** genauso
wie beim Einbauen, nur ist die Falle dort noch leichter zu übersehen:

* Der Eingangsfilter darf **nicht** auf die alte, strengere Fassung zurückgesetzt werden. Auf
  einem anderen Gerät kann noch ein `{id, p}` liegen; ein Filter, der wieder ein `uids`-Array
  verlangt, löscht das Gericht dort aus dem Plan. `unflattenWeek()` lässt Objekte ohne `uids`
  deshalb weiterhin zu und führt sie auf die String-Form zurück — dabei fällt `p` weg, und der
  Zwischenstand räumt sich von selbst auf.
* Ein Prüfstand für ein Feld, das es nicht mehr gibt, ist trotzdem sinnvoll: Er prüft nicht das
  Feature, sondern dass **nichts verschwindet**.

## 74. Von Hand gesetzte Kalorienziele wurden von der nächsten Wiegung überschrieben

`syncGoalWeight()` rechnet das Ziel bei jeder neuen Wiegung mit `computeGoal()` neu — richtig,
solange das Ziel aus dem Rechner stammt. Mit der Direkt-Justierung (B4) hätte dieselbe Zeile
die Handanpassung beim nächsten Wiegen kommentarlos wieder eingesammelt.

Deshalb trägt ein von Hand gesetztes Ziel `manual: true`. Bei gesetzter Marke zieht nur noch
`weight` mit (daran hängt `dayTrainKcal()`), die Werte bleiben stehen. Ein Durchlauf des
Rechners hebt die Marke automatisch auf, weil `computeGoal()` ein frisches Objekt baut.

**Allgemein:** Jede Funktion, die abgeleitete Werte neu berechnet, braucht eine Antwort auf die
Frage „und wenn der Nutzer sie selbst gesetzt hat?". Ohne diese Antwort gewinnt immer die
Automatik — und zwar unsichtbar.

---

## 75. Eine CSS-Regel, die nie griff — und die es auch nicht sollte

Die Filter-Chips im Meals-Reiter (B7) bekamen zunächst eine eigene Klasse mit
`flex-wrap: nowrap; overflow-x: auto`, damit die Reihe waagerecht läuft statt umzubrechen.
Sie hat **nie gewirkt**: `.rfilters` steht im Stylesheet bei den Meals-Regeln, `.mtags` (mit
`flex-wrap: wrap`) rund 200 Zeilen weiter unten bei der Meal-Ansicht. **Gleiche Spezifität —
die spätere Regel gewinnt.** Im Browser sah alles richtig aus, weil das Ergebnis (Umbruch)
zufällig brauchbar war.

Aufgefallen ist es erst durch die Messung: `scrollWidth === clientWidth` bei sieben Chips auf
358 px — bei einem echten waagerechten Scroller hätte `scrollWidth` deutlich größer sein
müssen. **Ein Screenshot hätte den Fehler nicht gezeigt.**

Zwei Lehren, die beide zählen:

* **Eine Klasse, die eine andere überschreiben soll, muss dahinter stehen** — oder spezifischer
  sein. Bei zwei Klassen auf demselben Element (`class="mtags rfilters"`) entscheidet
  ausschließlich die Reihenfolge im Stylesheet, nicht die Reihenfolge im `class`-Attribut. Das
  ist ein häufiger Irrtum.
* **Die Regel war zusätzlich inhaltlich falsch.** Ein waagerechter Scroller über der Meal-Liste
  ist die Gestenfalle aus `CLAUDE.md` §11, und er versteckt Filter am rechten Rand. Der Umbruch
  ist die richtige Lösung; jetzt steht er ausdrücklich da, statt sich aus einer nicht greifenden
  Regel zu ergeben.

---

## 76. `if (wert)` statt `if ("feld" in objekt)` — die Lücke zeigte in die falsche Richtung

Die Prüfung der Pro-Berechtigung (D1) las das optionale Ablaufdatum so:

```js
let until = null;
if (d.until) { … if (!isFinite(ms)) return null; until = ms; }
```

Sieht richtig aus: „ist ein Ablaufdatum da, prüfe es". Tatsächlich sind `NaN`, `0` und `""`
**falsy** — bei einem kaputten `until` wurde der ganze Block übersprungen, `until` blieb `null`,
und `null` bedeutet in diesem Datenmodell **unbefristet gültig**. Ein beschädigter Wert hätte
also aus einem abgelaufenen Abo ein ewiges gemacht.

**Die Regel:** Bei optionalen Feldern entscheidet das **Vorhandensein**, nicht der Wahrheitswert
— `"until" in d && d.until !== null`. Und im Zweifel muss der Fehlerfall in die **restriktive**
Richtung fallen: kein Pro, nicht unbegrenztes Pro.

Gefunden hat das der Prüfstand, nicht das Lesen: Der Testfall `{ pro: true, until: NaN }` stand
in der Liste, weil „kaputte Werte" dort immer mit hineingehören. Beim Durchlesen wäre die Zeile
durchgegangen — sie liest sich vollkommen plausibel.

Verwandt, gleiche Denkfalle: `sanitizeRecipe()` prüft `"mealPrep" in r` statt `if (r.mealPrep)`,
weil sonst ein ausdrückliches `false` nicht von „gar nicht gesetzt" zu unterscheiden wäre.

---

## 77. Der Baseline-Push lief los, bevor feststand, ob das Konto Pro hat

> **Der auslösende Code ist seit dem 15.08.2026 wieder ausgebaut** — Cloud-Sync ist keine
> Pro-Funktion mehr, `entitlementGate()` gibt es nicht mehr. Die Denkfalle bleibt trotzdem
> stehen: Sie trifft jede Bedingung, die vor ihrer ersten Antwort einen Vorgabewert hat.

Beim Einbau der Pro-Sperren (D2b) fiel eine Reihenfolge auf, die vorher folgenlos war: Der
Berechtigungs-Listener startet in `startCloudSync()`, aber sein erster `onSnapshot` kommt
**nach** dem Baseline-Push am Ende derselben Funktion. Vorher war das egal, weil `isPro()`
nichts sperrte.

Mit den Sperren wäre daraus ein Fehler geworden, den ein zahlender Nutzer trägt: Beim Start
gilt `isPro() === false`, `pushNow()` bricht ab — und der nächste Push kommt erst bei der
nächsten Änderung. Schlimmer: `lastPushedJSON` und `lastPushedRecipes` stünden auf einem Stand,
den nie jemand geschrieben hat.

`entitlementGate()` löst das: `startCloudSync()` wartet auf den ersten Snapshot, gedeckelt auf
4 Sekunden. Zwei Eigenschaften sind dabei wichtig:

* **Die Zeitgrenze fällt in die sichere Richtung.** Bleibt die Antwort aus, gilt „kein Pro" —
  gesperrt wird nur das Schreiben, nichts geht verloren.
* **Mehrfaches Auflösen ist harmlos.** Der Listener feuert bei jedem Server-Echo erneut.

Und weil eine Zeitgrenze nie ein Ersatz für den echten Wert ist, holt der Listener den
übersprungenen Push nach, sobald die Berechtigung doch eintrifft.

**Die allgemeine Form:** Wer eine Bedingung einführt, die vorher immer `true` war, muss prüfen,
**wann** sie zum ersten Mal ihren richtigen Wert hat. Ein `false` vor der ersten Antwort ist
kein neutraler Startwert, sondern eine Aussage.

---

## 78. Eine Sperre nur beim Schreiben hätte bei jedem Start Daten gekostet

> **Gegenstandslos geworden am 15.08.2026** — Cloud-Sync ist keine Pro-Funktion mehr, es gibt
> keine einseitige Synchronisation. Der Merksatz am Ende gilt für jede künftige Situation, in
> der eine Datenrichtung wegfällt (abgelaufene Berechtigung, Nur-Lese-Rolle, Serverfehler).

Der naheliegende Zuschnitt für D2b war: ohne Pro nicht mehr in die Cloud schreiben, sonst alles
lassen. Das ist falsch, und zwar in eine Richtung, die man erst beim zweiten Start bemerkt.

Ohne Schreibrecht ist der Cloud-Stand **eingefroren**. Der Merge in `startCloudSync()` lässt
aber an mehreren Stellen ausdrücklich die Cloud gewinnen (`goal`, `favs`, `shopPersons`,
`profileImage`) — das ist richtig, solange beide Richtungen fließen. Ohne Rückweg heißt es:
Jeder Start überschreibt die lokale Arbeit mit einem Stand von vor der Umstellung, und die
Änderung ist weg, ohne dass irgendwo ein Fehler auftaucht.

Deshalb sperrt `personalCloud` in `startCloudSync()` und der Check in `onRemote()` auch das
**Hereinziehen**, nicht nur das Schreiben. Erreichbar bleibt der Cloud-Stand über „Cloud-Daten
laden" im Profilmenü — als Datei, nicht als Zusammenführung: Ohne Rückweg ließe sich nicht mehr
sagen, welcher der beiden Stände der gültige ist.

**Merksatz:** Eine einseitig gewordene Synchronisation ist keine halbe Synchronisation, sondern
ein Überschreiber.

---

## 79. `leaveGroup()` hätte ein Gratis-Konto in der Gruppe festgehalten

> **Die Feld-Allowlist ist seit dem 15.08.2026 wieder aus den Regeln raus**, `leaveGroup()`
> schreibt wieder unverändert `{ groupId: "", plans: … }`. Die Lehre am Ende bleibt für jede
> künftige Regel gültig, die Felder einzeln erlaubt.

`leaveGroup()` schreibt beim Austritt `{ groupId: "", plans: keepPlans }` — den geleerten
Zeiger **und** den Wochenplan, der aus der Gruppe wieder ins eigene Konto zurückwandert.

Die neue Firestore-Regel lässt ohne Pro genau vier Felder zu (`groupId`, `pendingGroupId`,
`pendingInviteUrl`, `updatedAt`). Ein Schreibvorgang mit `plans` scheitert damit **komplett** —
Firestore kennt kein „schreibt den erlaubten Teil". Der Fehler landete im `catch` und wäre
still geblieben; die Cloud-`groupId` wäre stehen geblieben, und der nächste Start hätte das
Konto in die Gruppe zurückgezogen, die es gerade verlassen hat.

Ohne Pro wird deshalb nur `{ groupId: "" }` geschrieben. Der Plan bleibt lokal — wie alles
andere auch.

**Die allgemeine Form:** Eine Feld-Allowlist in den Regeln muss gegen **jede** Aufrufstelle
geprüft werden, die das Dokument anfasst — nicht nur gegen den Hauptpfad. Die Zeiger-Felder
werden an vier Stellen einzeln geschrieben; `leaveGroup()` war die einzige, die noch etwas
anderes mitschickte.

---

## 80. Ein Einzeiler zerlegte den Prüfstand — und der Fehler war unsichtbar

Der Ausschneide-Prüfstand für D2b schneidet Funktionen „von der Signaturzeile bis zur ersten
Zeile, die genau `  }` ist". Bei `function canCloudWrite() { return isPro(); }` steht die
schließende Klammer in **derselben** Zeile — der Schnitt lief also weiter bis zur nächsten
Funktion und nahm deren Rumpf zur Hälfte mit.

Das Ergebnis war kein Testfehler, sondern eine **leere Seite**: Ein Syntaxfehler verhindert,
dass der `<script>`-Block überhaupt ausgeführt wird — und damit läuft auch der eigens
eingebaute `window.onerror`-Handler nicht, der den Fehler hätte anzeigen sollen. Genau
dieselbe Fehlerklasse wie §5/§6 in der App selbst, nur im Prüfstand.

**Die Regel:** Endet die Signaturzeile selbst auf `}`, ist sie die ganze Funktion. Und bei einem
leeren Prüfstand zuerst den ausgeschnittenen Code ansehen, nicht die Testfälle.

---

## 81. Cloud-Sync war einen Tag lang Pro — die Rücknahme war die richtige Entscheidung

D2b legte am 15.08.2026 Cloud-Sync und Gruppen hinter die Pro-Grenze. Die Umsetzung war
sauber, geprüft und dokumentiert. Sie war trotzdem falsch, und der Grund stand in keinem
Agentenbericht: **Wer sich anmeldet, erwartet seine Meals auf dem zweiten Gerät.**

Cloud-Sync ist für Nutzer keine Zusatzleistung, sondern das, wofür ein Konto überhaupt da ist.
Yazio und Lifesum synchronisieren gratis. Eine App, die dafür Geld verlangt, wirkt nicht
premium, sondern knausrig — und das Kostenargument trug sachlich nicht einmal: Firestore-Kosten
für ein paar Dutzend Konten sind nicht messbar.

Aufgefallen ist es bei einer einzigen Nutzerfrage nach dem Push: „Heißt das, die Daten liegen
jetzt nur noch lokal?" Vier Prüf-Agenten hatten die Änderung vorher abgenommen — keiner hat
diese Frage gestellt, weil alle vier prüften, **ob** die Sperre korrekt gebaut ist, nicht **ob
sie sein soll**. Der `kvp`-Agent hat als Einziger die Produktpassung im Auftrag und schrieb
„passt zu Paar oder WG" — er bewertete die Gruppenregel und übersah den Sync daneben.

**Zwei Lehren:**

1. **Prüf-Agenten validieren die Umsetzung, nicht die Prämisse.** Eine falsche
   Produktentscheidung kommt durch jeden Review, wenn sie sauber umgesetzt ist. Die Frage
   „will ein Nutzer das?" muss vor dem Bauen gestellt werden, nicht danach.
2. **Was Nutzer als Teil des Grundprodukts verstehen, lässt sich nicht nachträglich zum
   Verkaufsargument machen.** Der Preis dafür ist nicht Umsatz, sondern Vertrauen.

Technisch bemerkenswert: Der Rückbau ging in einer knappen Stunde, weil die Sperre an genau
fünf benannten Stellen saß und `canCloudWrite()` als **eine** Funktion existierte statt als
verstreute `isPro()`-Abfragen. Ein Torwächter mit eigenem Namen ist auch dann die richtige
Bauform, wenn man ihn später wieder entfernt.

---

## 82. Ein Feld, das nur an einer von drei Stellen rechnete — und deshalb falsch einkaufte

`portions` am Rezept sah nach einer harmlosen Angabe aus („ergibt 2 Portionen"). Tatsächlich
wurde es nur an **einer einzigen** Stelle ausgewertet: in der Einkaufsliste, und dort auch nur
bei individuell zugewiesenen Gerichten in einer Gruppe (`uids.length / (r.portions || 1)`).

Nicht ausgewertet wurde es:

* in der **Tagesbilanz** — `dayNutOf()` nimmt immer die vollen Nährwerte des Rezepts;
* in der Einkaufsliste bei **„für alle"** — dem Normalfall, dort war der Faktor fest `1`.

Ein Meal mit `portions: 2` zählte also mit den Nährwerten **einer** Portion und kaufte die
Zutaten für **zwei** ein. Wer nach dieser Liste einkaufte, kaufte doppelt.

**Aufgefallen ist es im eigenen Beispieldatensatz**, und zwar erst bei einer Frage des Nutzers
nach etwas ganz anderem (dem Auto-Planer). „Hähnchen mit Pute und Reis" trug `portions: 2`,
620 kcal und Zutaten, die zusammen weit über 1000 kcal ergeben. Beim Nachrechnen war klar:
Die Nährwerte galten für eine Portion, die Zutaten für zwei. Der Fehler stand seit Monaten in
den mitgelieferten Daten, hat jeden Prüfstand überlebt und wurde von keinem Prüf-Agenten
gemeldet — weil alle prüften, ob der Code **tut, was er soll**, nicht ob die **Bedeutung** der
Felder zueinander passt.

**Behoben durch Ausbau des Feldes** (ein Meal ist eine Portion) statt durch eine Korrektur der
drei Auswertungsstellen. Die Mengen werden in `sanitizeRecipe()` einmalig umgerechnet.

**Die allgemeine Form — und der eigentliche Wert dieses Eintrags:** Ein Feld, das in einer von
drei Auswertungen fehlt, ist gefährlicher als ein Feld, das überall fehlt. Fehlt es überall,
merkt man es sofort; fehlt es an zwei von drei Stellen, ergibt jede Ansicht für sich einen
plausiblen Wert — und nur die Kombination ist falsch.

**Prüffrage für jedes neue Feld am Datenmodell:** Welche Auswertungen gibt es, und rechnen
**alle** damit? Wenn nicht: Warum nicht, und ist das Ergebnis dann noch widerspruchsfrei?

---

## 83. Geschätzte Nährwerte in einem Rezept sehen aus wie gerechnete

Die ersten neun Rezepte des Rezeptbuchs bekamen ihre Nährwerte per Augenmaß. Sie sahen
plausibel aus — 540 kcal für eine Tofu-Pfanne, 420 für ein Curry. Tatsächlich lagen sie bis zu
**86 % daneben**; die Pfanne hatte 680 kcal, das Curry 713 (vor der Mengenkorrektur).

Aufgefallen ist es nur, weil der Nutzer beim Bearbeiten eines übernommenen Rezepts bemerkte,
dass die **Zutaten keine eigenen Nährwerte** trugen. Die daraus gebaute Gegenrechnung
(`tools/rezept-makros.py`) machte den Fehler in einem Lauf sichtbar.

**Warum das die gefährlichste Fehlerklasse in dieser App ist:** Bei einem Layoutfehler sieht
man, dass etwas nicht stimmt. Bei einer falschen Kalorienzahl sieht man gar nichts — sie wird
geglaubt, geplant und gegessen. In einer App, deren Kernversprechen „triff deine Makros" ist,
ist das der einzige Fehler, der das Produkt in seiner Substanz beschädigt.

**Regel:** Kein Rezept kommt in den Katalog, dessen Summe nicht gegen die Zutaten gerechnet
wurde. Und die Zutaten tragen ihre Werte mit, sonst kann die App beim Bearbeiten nichts
nachrechnen.

---

## 84. Ein falsch zugeordnetes Lebensmittel ist schlimmer als ein fehlendes

Beim Nachschlagen der Zutaten in `FOODS` matchte **„Zuckerschoten" auf „Zucker"** — 400 statt
42 kcal, fast reine Kohlenhydrate. Das Rezept kam damit auf 168 g KH statt 60. Die Ursache war
ein zu großzügiges Präfix-Matching (`"zuckerschoten".startswith("zucker")`).

**Der Unterschied zur fehlenden Zutat ist entscheidend:** Fehlt eine, meldet das Werkzeug eine
Lücke und niemand trägt etwas ein. Wird eine falsch zugeordnet, entsteht ein Wert, der
plausibel aussieht, durch jede Sichtprüfung geht und schlicht falsch ist.

Behoben durch Vergleich **nur an Wortgrenzen**: Ein Kandidat passt, wenn er ein vollständiges
Wortpräfix ist (`"zucker "` ist kein Präfix von `"zuckerschoten"`).

**Die allgemeine Form:** Bei jedem unscharfen Abgleich (Name → Datensatz) muss die Zuordnung
**sichtbar** sein, nicht nur das Ergebnis. Deshalb gibt das Werkzeug mit `--json` aus, welcher
Eintrag getroffen wurde. Wer nur die Summe prüft, prüft die Hälfte.

---

## 85. Freitext-Zutaten fallen aus jeder Rechnung

„1 EL Olivenöl, Oregano, Salz, Pfeffer" als Freitext-Zeile ist bequem zu schreiben und für die
Einkaufsliste ausreichend — aber ein Freitext hat keine Menge und keine Nährwerte. In den
ersten Katalog-Rezepten fehlte dadurch **das gesamte Bratfett**: Der Fettwert lag bis zu 69 %
zu niedrig, obwohl jedes Rezept einen Esslöffel Öl nannte.

Gewürze dürfen Freitext bleiben — sie tragen nichts bei. **Fett nie:** 10 g Öl sind 88 kcal,
das ist bei einem 500-kcal-Gericht ein Fünftel.

**Prüffrage bei jedem neuen Rezept:** Steht etwas im Freitext, das Kalorien hat?

---

## 86. Stichwort-Fotos greifen im Rezeptbuch daneben — an den Regeln zu drehen ist der falsche Hebel

Beim Ausbau des Katalogs auf 30 Rezepte (15.08.2026) bekam **„Grüner Smoothie mit Spinat und
Banane" das Salatfoto**, „Schoko-Protein-Quark" ein Porridge und „Dattel-Nuss-Bissen mit Kakao"
ein Getränk. Ursache ist keine Panne, sondern die Bauart von `PHOTO_RULES`: Die Regeln suchen
Stichwörter im **Namen**, und `salad` fängt unter anderem `spinat`, `brokkoli`, `zucchini` und
`gemüse`, `porridge` fängt `quark` und `hüttenkäse`, `drink` fängt `kakao`.

Für **selbst angelegte** Meals ist das richtig — dort heißt ein Gericht „Salat mit Hähnchen"
und nicht „Hähnchenbrust 180 g". Kuratierte Rezeptnamen nennen dagegen ihre Zutaten, und damit
springt fast immer eine Zutatenregel an, bevor die Gerichtsregel drankommt.

**Nicht die Regeln anfassen.** Sie wirken auf jedes Nutzer-Meal, und Teilwort-Kollisionen sind
dort die dokumentierte Falle (`CLAUDE.md` §22: `eis` steckt in `Rindfleisch`). Eine Regel zu
entschärfen, um elf Katalogbilder zu retten, verschlechtert die Zuordnung für alle anderen.

**Stattdessen entscheidet die Kuration**: `COOKBOOK[i].photo` trägt einen **Schlüssel aus
`PHOTOS`**, den `photoFor()` vor den Regeln prüft. Gesetzt nur dort, wo die Regel falsch liegt.

**Zwei Dinge, die dabei fast schiefgegangen wären:**

* **TDZ.** Die Gültigkeitsprüfung `PHOTOS[r.photo]` gehörte scheinbar in `sanitizeRecipe()` —
  das läuft aber schon in `let state = load()` (Zeile ~4264), und `PHOTOS` ist erst auf ~6165
  als `const` deklariert. Das hätte die App beim Start zerlegt. `typeof` hilft nicht: Auch das
  wirft in der TDZ. Geprüft wird dort deshalb nur die **Form**, die Gültigkeit in `photoFor()`.
* **Ein Tippfehler wäre unsichtbar gewesen.** Ein unbekannter Schlüssel fällt still auf die
  Regeln zurück — also genau auf das falsche Bild, das man vermeiden wollte. Dagegen gibt es
  jetzt eine Prüfung im Prüfstand.

---

## 87. „High Protein" als Tag und „Proteinreich" als Badge sind zwei Quellen für dieselbe Aussage

Auf jeder Meal-Karte stehen beide nebeneinander: der **gepflegte** Tag aus `RECIPE_TAGS`
(filterbar) und das **gerechnete** Badge aus `macroBadges()` (Protein ≥ 30 % der
Makro-Kalorien). Am 15.08.2026 trugen **vier der ersten neun Katalog-Rezepte** den Tag bei
17–25 % Proteinanteil — das Rote-Linsen-Dal mit 17 %. Wer im Rezeptbuch auf „High Protein"
filterte, bekam Karten, auf denen kein Badge stand.

Im **Katalog** ist das ein Kurationsfehler, und er ist jetzt geprüft. Bei **eigenen** Meals ist
es keiner: Dort taggt der Nutzer selbst, und ihm vorzuschreiben, was er proteinreich nennen
darf, wäre Bevormundung.

**Merken:** Wo eine gepflegte Angabe neben einer gerechneten steht, ist die gerechnete die
Wahrheit — und die Prüfung gehört an die Daten, nicht in den Kopf dessen, der sie einträgt.

---

## 88. Das Geschirr aus der Kategorie allein legt Brot in eine Schüssel

`tools/meal-bilder.py` wählte das Geschirr im Bildprompt nur nach `category`: Frühstück → Bowl,
Hauptgericht → Teller, Getränk → Glas. Beim Trockenlauf für die damals 30 Katalog-Rezepte fiel auf,
dass damit **„Rührei mit Avocado auf Vollkornbrot" eine Schüssel bekommen hätte** — genau wie
„Protein-Pancakes", „Hüttenkäse auf Vollkornbrot" und „Ofengemüse vom Blech". Eine Scheibe
Brot in einer Schüssel sieht auf den ersten Blick falsch aus, und es wäre erst nach dem
Bezahlen aufgefallen.

Behoben mit `NAME_GESCHIRR`: wenige, sehr eindeutige Stichwörter (`brot`, `toast`, `sandwich`,
`pancake`, `pfannkuchen`, `waffel`, `steak`, `blech`) greifen **vor** der Kategorie. Bewusst
knapp gehalten — jede weitere Regel ist eine neue Gelegenheit für eine Teilwort-Kollision
(`CLAUDE.md` §22).

**Derselbe Fehler in die andere Richtung, wenige Stunden später:** Das Beispiel-Meal
„**Eiweißshake** mit Whey und Milch" steht in der Kategorie **Snack** und bekam damit eine
Schüssel — im Bild eine cremige Masse mit einem Haufen Pulver darauf. Ein Shake, den man nicht
trinken kann. Ergänzt um eine zweite Regel (`shake`, `smoothie`, `saft`, `limonade`, `kaffee`,
`tee` → Glas). **Die Lehre daraus ist die interessantere:** Die Kategorie beschreibt, *wann* man
etwas isst, nicht *woraus*. Für die Bildwahl ist sie deshalb nur ein Näherungswert — und wer
sie als einzige Quelle nimmt, produziert genau an den Rändern Unsinn.

**Die allgemeine Form:** Der Trockenlauf (`--dry-run`) ist bei einem Werkzeug, das Geld kostet,
kein optionaler Zwischenschritt. Die 30 Prompts einmal zu lesen hat einen Fehler gefunden, der
sonst 30 Bilder lang mitgelaufen wäre. Den Shake hat er allerdings **nicht** gefunden — dort war
der Prompt unauffällig, aufgefallen ist erst das Bild. Beides braucht es also: Trockenlauf
**und** Sichtprüfung.

---

## 89. Ein Dateiname darf nicht aus der Katalog-`id` abgeleitet werden

Der Kommentar am `COOKBOOK` sagte ursprünglich, die `id` sei „zugleich der Dateiname des Bildes
in `img/library/`". Das stimmt so nicht: `rührei-avocadobrot` ist eine gültige `id`, aber ein
schlechter Dateiname — Umlaute in Pfaden und URLs sind eine Fehlerquelle. Das Python-Werkzeug
schreibt deshalb `ruehrei-avocadobrot.webp`.

Damit gäbe es zwei Möglichkeiten, und nur eine ist tragfähig:

* **Ableiten in JavaScript** — dann existiert die Slug-Regel zweimal, in Python und in JS. Zwei
  Fassungen derselben Regel laufen auseinander, sobald eine id einen Fall trifft, den nur eine
  der beiden kennt (`ß`, ein Punkt, zwei Sonderzeichen hintereinander).
* **Den Dateinamen am Eintrag hinterlegen** (`img: "…webp"`) — eine Quelle, vom Werkzeug
  erzeugt, im Prüfstand gegen das Dateisystem abgeglichen. So ist es umgesetzt.

**Die `id` bleibt trotzdem der Schlüssel.** Sie wird nicht „aufgeräumt", nur weil ein Umlaut
darin steht: Sie steckt als `lib` in übernommenen Kopien und damit in Nutzerdaten.

**Und die Kopie speichert den Pfad nicht mit.** `libPhoto()` löst über `lib` im Katalog auf.
Ein ersetztes oder zurückgezogenes Bild wirkt damit sofort überall, und in Cloud-Daten und
geteilten Meals liegt kein Pfad, der eines Tages ins Leere zeigt.

---

## 90. `z-index` ohne `position` ist wirkungslos — und ein Kommentar ist kein Code

Der „Übernehmen"-Knopf auf den Rezeptbuch-Karten war **wirkungslos**: Statt zu übernehmen,
öffnete er die große Meal-Ansicht. Ursache ist das Stretched-Link-Muster der Karte —
`.rcard-open::after` liegt mit `position: absolute; inset: 0; z-index: 1` über der **ganzen**
Karte, damit Bild und Titel gemeinsam anklickbar sind.

`.cb-foot` war dagegen nur `margin-top: 10px`, also **`position: static`**. Ein statisch
positioniertes Element bildet keinen Stapelkontext und **ignoriert `z-index` vollständig** — es
liegt damit zwangsläufig unter dem Link, egal welchen Wert man setzt. Behoben mit
`position: relative; z-index: 2`.

**Der eigentliche Lehrsatz steht im JS.** Dort stand seit dem Bau der Ansicht:

> „Der Uebernehmen-Knopf liegt per z-index darueber (.cb-foot), sonst faenge der Stretched Link
> ihn ab."

Der Kommentar beschrieb eine Absicht, die nie im CSS gelandet ist — und er hat verhindert, dass
jemand nachsieht: Wer ihn liest, hält das Problem für gelöst. **Ein Kommentar, der eine
Umsetzung behauptet, muss gegen die Umsetzung geprüft werden**, sonst ist er schlimmer als kein
Kommentar.

**So ist es nachweisbar** (im Browser, nicht headless — der Stapelkontext entsteht erst im
Layout): `document.elementFromPoint()` auf die Mitte des Knopfes. Vorher lieferte es
`button.rcard-open`, jetzt `button.btn primary sm`; ein Klick auf das Bild liefert weiterhin
`button.rcard-open`. Die Gegenprobe im selben Schritt: `.cb-foot` per Stil auf `static` zurück —
der Treffer fällt sofort wieder auf den Link. Kein Schreibvorgang nötig, also auch keine
Testdaten in der Cloud.

---

## 91. Mitgelieferte Daten vor dem Onboarding einsetzen heißt, sie ohne Profilwissen zu wählen

`load()` füllte den Bestand beim allerersten Start aus einem festen `SEED`-Array — vier Meals,
darunter ein Rindersteak und ein Molke-Shake. Das geschah, **bevor** das Onboarding lief, also
bevor `state.goal.diet` existierte: Ein Veganer bekam als Erstes zwei Gerichte, die er nie kocht,
und ausgerechnet als Begrüßung.

Der Fehler war nicht die Auswahl, sondern der **Zeitpunkt**. Behoben, indem der erste Bestand in
`finishOnboarding()` über `addStarterMeals()` entsteht — dort ist die Ernährungsform bekannt, und
die fünf Meals kommen aus dem Katalog, durch `fitsDiet()` gefiltert.

**Zwei Fallen dabei:**

* **Nur in einen leeren Bestand.** Wer sich auf einem zweiten Gerät anmeldet und dort das
  Onboarding durchläuft, hat seine Meals schon — ohne die Bedingung `state.recipes.length === 0`
  wären fünf Dubletten die Folge.
* **Die Liste muss selbst zur Form passen, nicht nur ihr Ergebnis.** `addStarterMeals()` filtert
  mit `fitsDiet()` und füllt still aus demselben Katalog auf. Ein Fleischgericht in der veganen
  Liste fällt dadurch **nicht auf** — es wird weggefiltert, ersetzt, und alle Prüfungen bleiben
  grün. Aufgefallen ist das erst in der Gegenprobe des Prüfstands. Es gibt jetzt eine eigene
  Prüfung, die `dietOk()` auf jede Liste anwendet.

**Verallgemeinert:** Wo eine Auswahl gefiltert *und* aufgefüllt wird, prüft das Ergebnis nur den
Filter — nie die Kuration.

---

## 92. `array.filter(fn)` übergibt den Index — und ein abgebrochener Repaint sieht aus wie ein Filter ohne Wirkung

**Fund des Nutzers am 15.08.2026:** Im Meals-Reiter zeigte der Filter „High Protein" (und jeder
andere) **alles** an. Im Rezeptbuch funktionierte er.

Die Ursache stand seit B7 (13.08.2026) in `paintRecipeGroups()`:

```js
pool = pool.filter(recipeMatchesFilters);          // falsch
pool = pool.filter(r => recipeMatchesFilters(r, recipeFilters));   // richtig
```

`Array.prototype.filter` ruft den Callback mit **drei** Argumenten auf: `(element, index, array)`.
Der Index landete damit im zweiten Parameter `aktive`, und `for (const k of (aktive || …))` bekam
eine Zahl:

* **Index 0** ist falsy → der Rückfall auf `recipeFilters` griff, das erste Element wurde noch
  korrekt geprüft.
* **Ab Index 1** warf `for (const k of 1)` einen `TypeError: 1 is not iterable`.

**Deshalb sah es nach „Filter ohne Wirkung" aus, nicht nach einem Fehler:** `paintRecipeGroups()`
brach mitten drin ab, *bevor* es `#r-groups` neu beschrieb. Stehen blieb das, was schon im DOM war
— die ungefilterte Liste. Der Chip wurde trotzdem gedrückt dargestellt, weil `aria-pressed` im
Klick-Handler *vor* dem Repaint gesetzt wird. Ein stiller Abbruch mit sichtbar plausibler Oberfläche.

**Das Rezeptbuch war nie betroffen**, weil `paintCookbook()` das Set ausdrücklich übergibt. Genau
diese Asymmetrie machte die Suche kurz: derselbe Matcher, zwei Aufrufer, ein Unterschied.

**Zwei Lehren:**

1. **Eine Funktion mit optionalem zweiten Parameter darf nie direkt als `filter`/`map`/`forEach`-
   Callback übergeben werden.** Der Fehler ist unsichtbar, weil der erste Durchlauf zufällig
   funktioniert. `recipeMatchesFilters()` prüft jetzt `aktive instanceof Set`, statt nur auf
   truthy — damit kann derselbe Fehler nicht ein zweites Mal entstehen.
2. **Ein „Feature ohne Wirkung" ist ein Kandidat für einen abgebrochenen Repaint.** Nicht zuerst
   die Logik lesen, sondern die Konsole — und prüfen, ob die Funktion, die das DOM schreibt,
   überhaupt bis zum Ende läuft.

## 93. Ein Rückgabewert, n-mal eingefügt: derselbe Eintrag steht dann n-mal im Plan — als ein Objekt

**Beim Bau des Auto-Wochenplaners (16.08.2026) vermieden, nicht erlitten** — aber die Stelle ist
so verführerisch, dass sie hier stehen muss.

Der Planer legt für ein Gericht mehrere Portionen in denselben Slot. Naheliegend wäre:

```js
const eintrag = makeEntry(r.id, uids);          // FALSCH
for (let i = 0; i < n; i++) state.plan[d][m].push(eintrag);
```

`makeEntry()` liefert **entweder einen String** (der Normalfall „für alle") **oder ein Objekt**
`{id, uids}`. Beim String ist das harmlos, beim Objekt liegen danach n Verweise auf **dasselbe**
Objekt im Plan. Alles funktioniert — bis jemand die Zuweisung genau einer dieser Portionen
ändert oder ein `uids`-Array in place mutiert: Dann ändern sich alle mit, und zwar in einem
Feature (Zuweisung), das mit dem Planer nichts zu tun hat.

Der Fehler wäre also erst Wochen später und an ganz anderer Stelle aufgefallen. Richtig ist,
`makeEntry()` **je Eintrag** zu rufen. Der Prüfstand hält das mit einem paarweisen
`===`-Vergleich über alle Einträge fest — eine Prüfung, die man nur schreibt, wenn man die
Falle kennt.

**Die allgemeine Form:** Ein Helfer, der *manchmal* ein Objekt und *manchmal* einen Primitiven
zurückgibt, verzeiht das Wiederverwenden in der Hälfte der Fälle. Das ist schlimmer, als wenn er
es nie verziehe.

## 94. `.btn` in einer Reihe mit `.btn.icon-gh` sieht gleich groß aus — und ist kein Touch-Ziel

Die Werkzeugleiste des Wochenplans arbeitet mit 34 px hohen Knöpfen. Die 44 px Trefferfläche
entstehen dort **nicht** aus der Höhe, sondern aus `.btn.icon-gh::after { inset: -5px }`
(siehe §38). Ein neuer Knopf, der nur `.btn` trägt, übernimmt die Optik der Reihe, aber nicht
den hitSlop — sichtbar identisch, auf dem Handy 34 px hoch antippbar.

Beim „Woche planen"-Knopf (D2) ist die Lösung nicht ein weiterer `::after`, sondern die Zeile:
Unter 720 px bekommt er `flex: 1 0 100%` und **echte** `height: 44px`. Auf der eigenen Zeile ist
der Platz da, und ein echtes Maß ist einem Trick vorzuziehen, wo beides möglich ist.

**Prüfregel:** Wer der Leiste einen Knopf hinzufügt, misst dessen `getBoundingClientRect()`
**und** `getComputedStyle(el, "::after")`. Eine der beiden Zahlen muss 44 ergeben.

## 95. Der Automatismus braucht eine engere Kategorie-Bindung als der Picker

**Fund des Nutzers am 16.08.2026, einen Tag nach dem Live-Gang von D2:** Der Auto-Wochenplaner
lieferte *sechsmal Joghurt als Mittagessen und vier Shakes als Snack*.

Zwei Ursachen, die sich gegenseitig verstärkten:

**1. `catFitsMeal()` ist absichtlich großzügig.**

```js
function catFitsMeal(cat, mealKey) {
  const bound = CAT_TO_MEAL[cat];
  return !bound || bound.indexOf(mealKey) !== -1;   // !bound = passt ueberall
}
```

`CAT_TO_MEAL` kennt nur Frühstück, Hauptgericht, Snack und Dessert. **Beilage, Getränk und jede
unbekannte Kategorie fallen in den `!bound`-Zweig und passen damit in jeden Slot.** Für den
Picker ist das richtig und war es immer: Wer einen Shake zum Mittag einplanen will, soll das
dürfen, und ein geteiltes Meal mit fremder Kategorie darf nicht unplanbar werden.

Ein Automatismus, der dieselbe Freiheit nutzt, trifft diese Entscheidung aber für den Nutzer —
und dann ist sie falsch. Der Planer fragt seit dem 16.08.2026 `catPlanFitsMeal()`, das nur
**exakte** Treffer zulässt.

**2. Der Planer hatte zu wenig Auswahl.** Er sah nur `state.recipes`. Nach dem Onboarding sind
das fünf Startmeals — bei drei Haupt-Slots muss die Rotation auf demselben Gericht landen.
Behoben durch das Rezeptbuch als zweite Kandidatenquelle.

**Die Lehre, die über diesen Fall hinausgeht:** Eine Regel, die für eine *Auswahl durch Menschen*
gebaut ist, taugt nicht unbesehen für eine *Auswahl durch die App*. Der Mensch sieht, was er
wählt, und korrigiert sofort; der Automatismus legt 28 Einträge an und niemand prüft jeden
einzeln. Wer eine bestehende Prüffunktion in einem neuen Automatismus wiederverwendet, muss
zuerst fragen, welche Freiheit sie absichtlich lässt.

**Falle beim Prüfen dieser Regel:** Der erste Prüfstand-Anlauf war grün und bewies nichts. Mit
einem normalen Bestand verdrängt schon die Bewertung (`planRang`) die losen Kandidaten aus den
Top drei — die Gegenprobe färbte nur eine einzige Zeile rot. Erst ein Testfall mit *wenigen*
exakt passenden Gerichten und einem losen Kandidaten mit Meal-Prep und hohem Proteinanteil
erzwingt den Fehler. Und die drei losen Fälle müssen **einzeln** laufen: In einem gemeinsamen
Testfall verdrängten sie sich gegenseitig, der kategorielose fiel um 0,5 Punkte heraus.

## 96. Vier Portionen desselben Snacks — dieselbe Formel, zwei Bedeutungen

Aus demselben Fund vom 16.08.2026. `anzahl = round(budget / kcal)` ist bei Frühstück, Mittag und
Abend genau richtig: Es ist der Kern des Gruppen-Konzepts (zweimal Porridge bei 3000 kcal,
einmal bei 1800).

Beim **Snack-Slot** bedeutet dieselbe Formel etwas anderes. Er bekommt nicht einen Anteil,
sondern den **Rest** des Tages — und der ist groß. Bei einem 150-kcal-Shake und 600 offenen kcal
ergibt das vier Stück desselben Getränks. Rechnerisch korrekt, als Mahlzeit unbrauchbar.

Der Snack-Slot füllt jetzt mit **verschiedenen** Snacks, jeder höchstens einmal pro Tag. Bleibt
danach etwas offen, wird es im Toast benannt statt mit Wiederholungen kaschiert.

**Prüffalle, die zwei Anläufe gekostet hat:** Ein Testfall mit normalem Bestand beweist hier
nichts — fr/mi/ab decken den Tag schon ab, der Snack bekommt höchstens einen Eintrag, und
„keine Dublette" ist dann auch mit der alten Formel erfüllt. Die Gegenprobe blieb komplett grün.
Der Testfall muss den großen Rest **erzwingen**: hohes Ziel, absichtlich kleine Gerichte, damit
der Deckel bei fr/mi/ab greift. Dann zeigt die Gegenprobe den Unterschied unmittelbar —
`["ks1","ks1","ks1","ks1"]` gegen `["ks1","ks2"]`.

## 97. Eine Klammer zu früh: der halbe 680px-Block landete in einer 360px-Abfrage

**Fund des Nutzers am 16.08.2026, direkt nach dem Push:** „Bei Home kann man nicht mehr nach
links und rechts wischen und bei den Wochentagen auch nicht, es ist alles untereinander."

Ursache war ein CSS-Eingriff von zwei Zeilen. Der neue 359px-Block wurde **mitten in den
680px-Block** geschrieben, und dessen öffnende Klammer damit vorzeitig geschlossen:

```css
@media (max-width: 680px) {
  …
  .pa-w { display: none; }
  }                          /* ← schliesst den 680px-Block hier */

@media (max-width: 359px) {
  .plan-tools .plan-auto { display: none; }
  /* ab hier stand der GESAMTE Rest des 680px-Blocks: */
  .week { overflow-x: auto; scroll-snap-type: x mandatory; … }
  .daybar { … }
  .wg-cols { … }
}                            /* die urspruengliche Klammer schliesst jetzt DIESEN Block */
```

**Die gesamte mobile Ansicht galt damit nur noch unter 360 px.** Auf jedem echten Handy
(360–430 px) fiel `.week` auf das Desktop-Raster zurück — die sieben Tage untereinander, kein
Snap-Streifen, keine Wischgeste. Dasselbe auf der Startseite bei den Wochenzielen.

**Warum es kein Prüfstand gemerkt hat:** Der Layout-Prüfstand maß das *neue Bauteil* — Knopfbreite,
Zeilenhöhe, Trefferfläche — und das war alles korrekt. Gemessen wurde die Umgebung nicht.

**Zwei Regeln, die daraus folgen:**

1. **Einen neuen `@media`-Block nie zwischen bestehende Regeln setzen**, sondern hinter das Ende
   des Blocks, in dem man gerade liest. Wo das Ende liegt, wird gezählt, nicht geschätzt —
   der 680px-Block ist 375 Zeilen lang, sein Ende steht nicht auf demselben Bildschirm wie
   seine Regeln zur Werkzeugleiste.
2. **Ein Prüfstand für ein Bauteil muss die Umgebung mitmessen.** Der Layout-Prüfstand prüft
   jetzt bei jeder Breite: `.daybar` sichtbar, `.week` mit `overflow-x: auto` und
   `scroll-snap-type: x`, `scrollWidth > clientWidth`, und dasselbe für `.wg-cols` auf der
   Startseite. Am Rechner die Gegenrichtung (`display: grid`, Tagesleiste aus).

**Schnellprüfung nach jeder CSS-Änderung** — sie hätte den Fehler in einer Sekunde gefunden:
Klammerbilanz des `<style>`-Blocks zählen und die Grenzen aller `@media`-Blöcke ausgeben. Ein
Block, der plötzlich viel kürzer ist als vorher, ist genau dieser Fehler.

## 98. Zwei Slots, dieselbe Menge, dieselbe Bewertung, derselbe Index — dasselbe Ergebnis

**Fund des Nutzers am 16.08.2026:** Der Auto-Planer setzte an fast jedem Tag *dasselbe Gericht
für Mittag und Abend*. Das war kein Zufall, sondern zwangsläufig:

```js
wahl[m.key] = planWochengerichte(kand, m.key);   // fuer "mi" und "ab" identisch
…
const r = liste[di % liste.length];              // fuer beide derselbe Index
```

Drei Zutaten, jede für sich harmlos:

1. **Dieselbe Kandidatenmenge** — `catPlanFitsMeal("Hauptgericht", …)` ist für `mi` und `ab` wahr.
2. **Dieselbe Bewertung** — `planRang()` kannte den Slot nur für die Kategorie-Frage, die hier für
   beide gleich ausgeht.
3. **Derselbe Rotationsindex.**

Der Shuffle vor dem `sort()` half nicht: `Array.sort` ist **stabil und deterministisch**, der
Zufall wirkt also nur bei exaktem Punktgleichstand. Zwei Aufrufe derselben Funktion mit denselben
Eingaben liefern dieselbe Liste — genau wie es sich gehört, nur eben nicht das, was hier gebraucht
wurde.

**Behoben** durch drei Maßnahmen, weil eine allein zu leicht wieder kippt: getrennte Mengen für
Mittag und Abend, ein Rotationsversatz, und eine harte Kollisionsregel am Ende der Kette.

**Die Lehre:** Wenn zwei Aufrufer einer Auswahlfunktion *unterschiedliche* Ergebnisse brauchen,
muss sich mindestens eine Eingabe unterscheiden — Menge, Bewertung oder Zugriff. Zufall im
Inneren garantiert das **nicht**, solange die Sortierung ihn wieder aufhebt.

**Falle beim Rückfall:** Der erste Fix prüfte `restFuerAbend.length`, um zu entscheiden, ob die
volle Menge nötig ist. Die Restmenge enthält aber weiterhin Frühstücke und Snacks und ist deshalb
nie leer — nur an *Hauptgerichten* fehlte es. Bei genau zwei Hauptgerichten im Bestand blieb der
Abend dadurch die ganze Woche leer. Gezählt werden muss, was am Ende **gezogen** wurde, nicht was
vorher im Topf lag. Gefunden hat das der Prüfstand, nicht das Lesen des Codes.

## 99. Eine Datumsrechnung in der Vergleichsfunktion eines `sort()`

Beim Einbau des Planer-Gedächtnisses rief `planRang()` dreimal `weekKeyBack()`, und jedes davon
baute ein `new Date()`. `planRang()` läuft aber in der **Vergleichsfunktion** eines `sort()` — bei
43 Kandidaten sind das rund 400 Aufrufe je Slot, mal vier Slots, mal jeder Prüflauf.

Der Prüfstand brauchte damit **über zwei Minuten** statt einer Sekunde. Auf einem Handy mit einer
Bibliothek von 150 Rezepten wäre derselbe Effekt beim Antippen spürbar gewesen.

**Behoben** durch einen Puffer, der den Tagesstempel mitträgt (`new Date().toDateString()`) — ohne
den wäre er falsch, sobald die App über Mitternacht offen bleibt.

**Zwei Lehren:**

1. **In einer Vergleichsfunktion nichts konstruieren.** Was sich während eines Sortiervorgangs
   nicht ändert, gehört davor berechnet.
2. **Ein langsamer Prüfstand ist ein Befund, kein Ärgernis.** Die zwei Minuten waren derselbe
   Code, den später ein Handy ausführt — nur mit weniger Geduld auf der anderen Seite.

---

## 100. Ein `uids.push()` am fremden Eintrag hätte den Undo-Pfad ausgehebelt

Seit dem 16.08.2026 tritt der Auto-Planer in einer Gruppe einem vorhandenen Eintrag **bei**,
statt einen zweiten daneben zu legen. Der naheliegende Weg wäre gewesen:

```js
entryUids(alt).push(syncUid);          // FALSCH
```

Er hätte funktioniert — bis jemand „Rückgängig" drückt. `autoPlanWeek()` legt vor dem Lauf einen
Schnappschuss an:

```js
before[d.key][m.key] = state.plan[d.key][m.key].slice();
```

`.slice()` kopiert das **Array**, nicht die Einträge darin. Der Schnappschuss und der Plan zeigen
also auf **dieselben Objekte**. Ein `push()` am fremden Eintrag hätte damit auch den
Schnappschuss verändert, und „Rückgängig" hätte den fremden Eintrag mit der eigenen UID darin
wiederhergestellt — eine fremde Planung, dauerhaft verändert durch einen Lauf, den man gerade
zurückgenommen hat. In der Gruppe wäre das Ergebnis anschließend synchronisiert worden.

**Richtig ist Ersetzen:**

```js
state.plan[d][m][idx] = makeEntry(entryId(alt), entryUids(alt).concat(syncUid));
```

`concat()` liefert ein neues Array, `makeEntry()` ein neues Objekt — der Schnappschuss behält das
alte. Als Nebenwirkung macht `makeEntry()` daraus von selbst ein „für alle", sobald damit alle
Mitglieder abgedeckt sind.

**Die Regel dahinter, und sie gilt für jeden Slot-Eintrag:** Einträge im Wochenplan werden
**ersetzt, nie mutiert.** Wer einen vorhandenen Eintrag ändern will, baut einen neuen und setzt
ihn an dieselbe Stelle. Das ist dieselbe Linie wie §93 (ein Rückgabewert, n-mal eingefügt) — dort
ging es um geteilte Referenzen im Plan, hier um geteilte Referenzen zwischen Plan und
Schnappschuss.

**Nachgewiesen ist es über eine Gegenprobe**, die genau in diese Falle tritt: Wird der Beitritt im
Prüfstand auf `altUids.push(syncUid)` umgestellt, werden „das fremde Objekt wurde ersetzt, nicht
mutiert" und „Rückgängig stellt den fremden Eintrag her" rot. Ohne diese dritte Gegenprobe wären
beide Prüfungen unbemerkt wertlos gewesen (siehe `docs/TESTING.md`).

**Bekannte Grenze, bewusst so gelassen:** Kommt im 9-Sekunden-Fenster des Undo-Toasts ein Sync der
anderen Person herein, setzt „Rückgängig" den Slot auf den Stand **vor meinem Lauf** zurück und
verwirft damit deren zwischenzeitliche Änderung. Das ist bestehendes Verhalten des
Schnappschuss-Pfades und kein Sonderfall des Beitritts — durch die Zusammenführung fällt es nur
eher auf.

---

## 101. Mitgliederlimit: drei Stellen, die den ganzen Umbau still gekippt hätten

Seit dem 16.08.2026 begrenzt `memberCount` im Gruppendokument die Gruppe auf vier Personen,
per `getAfter()` hart an die Mitgliedschaft gekoppelt. Beim Durchgehen des Lebenszyklus kamen
drei Stellen heraus, die eine naive Umsetzung kaputtgemacht hätten — keine davon fällt beim
Lesen der Regel selbst auf.

### 1. `dissolve()` löscht das Gruppendokument mit

`CloudGroup.dissolve()` räumt Mitglieder, Pläne, Meals **und** das Gruppendokument in einem
einzigen Batch weg. Eine Regel „wer ein Mitglied löscht, muss `memberCount` senken" greift dort
auf ein Dokument zu, das es nach dem Batch nicht mehr gibt — **eine Gruppe ließe sich nie wieder
auflösen.** Deshalb die Ausnahme:

```
allow delete: if … && ( !existsAfter(grpPath(gid))
                        || grpAfter(gid).memberCount == grpNow(gid).memberCount - 1 );
```

### 2. `deleteAccount()` verzeiht genau den Fehler, den es melden müsste

Der Konto-Löschpfad entfernt `groups/{gid}/members/{uid}` über `deleteBestEffort()`, und das
verzeiht `permission-denied` — mit gutem Grund, denn mehrere Löschregeln prüfen `resource.data`
und liefern bei fehlendem Dokument dasselbe Signal.

Genau das wird hier zur Falle: Eine Einzellöschung lehnt die neue Regel mit `permission-denied`
ab, `deleteBestEffort()` schluckt es, und **Name samt Profilbild blieben für immer in fremder
Gruppe stehen** — ohne Fehlermeldung, ohne Spur. Das ist ein Bruch von Ziffer 10 der
Datenschutzerklärung und Art. 17 DSGVO, ausgelöst durch eine Zeile, die aussieht, als hätte man
sie nicht angefasst.

Der Gruppenaustritt läuft dort jetzt als **eigener Batch** und bewusst **ohne**
`deleteBestEffort`: Entweder er ist erlaubt, oder es liegt ein echter Fehler vor, den der
Löschvorgang melden soll. Die eine Ausnahme ist eine bereits aufgelöste Gruppe — dann gibt es
nichts mehr zu löschen, geprüft per `getDoc()` vorab.

**Die allgemeine Lehre:** Ein `catch`, der einen Fehlercode absichtlich verzeiht, ist eine
stillschweigende Annahme darüber, was diesen Code auslösen kann. Ändert man die Regeln, ändert
man diese Annahme — und der `catch` schweigt weiter.

### 3. Ein Nichtmitglied darf die Gruppe nicht lesen

Der ursprüngliche Plan wollte vor dem Beitritt `memberCount` lesen und freundlich abweisen. Das
geht nicht: `allow get: if isMember(gid)`. Und diese Regel zu lockern, nur um eine hübschere
Meldung zu bekommen, wäre der falsche Handel — die Mitgliederzahl einer fremden Gruppe geht
Außenstehende nichts an.

Stattdessen entscheidet die Regel, und der `catch` in `joinGroup()` übersetzt
`permission-denied` in „Diese Gruppe ist schon voll." Das ist ohnehin die ehrlichere Reihenfolge:
eine einzige Quelle der Wahrheit, und kein Rennen zwischen Prüfung und Beitritt.

### Die Reihenfolge beim Deployment — und warum „nichts bricht" falsch war

**Erst der Client, dann die Regeln.** Umgekehrt verlangen die Regeln ein Feld, das noch niemand
geschrieben hat — die bestehende Gruppe wäre sofort unbenutzbar.

1. Client pushen (enthält `migrateMemberCount()`).
2. Als Inhaber die App öffnen, dann in der Firebase Console prüfen, dass
   `groups/{gid}.memberCount` steht und zur Mitgliederzahl passt.
3. **Sofort danach** die Regeln veröffentlichen.

**Zwischen Schritt 1 und 3 ist der Beitritt kaputt, und das ist keine Kleinigkeit.** Der
ursprüngliche Plan behauptete an dieser Stelle „Regeln noch alt → nichts bricht". Das war falsch
und hat am 16.08.2026 real Schaden angerichtet:

`joinAtomic()` schreibt **zwei** Dokumente in einem Batch — den Mitglieder-Eintrag *und*
`memberCount` im Gruppendokument. Die alten Regeln erlauben `groups/{gid}`-Updates aber nur dem
**Inhaber**. Für alle anderen fällt damit der ganze Batch durch, und der Beitritt ist unmöglich.

Verschärft wurde es durch die damalige Fehlermeldung, die jedes `permission-denied` als „Diese
Gruppe ist schon voll" ausgab — bei einer Gruppe mit **einer** Person. Die Fehlersuche lief
daraufhin eine Stunde in die falsche Richtung, am Ende wurde die Gruppe gelöscht, und dabei ging
der Wochenplan verloren (siehe nächster Abschnitt).

**Die Lehre ist allgemeiner als dieser Fall:** Ein Client, der neue Regeln *voraussetzt*, ist
nicht abwärtskompatibel, nur weil er „zusätzlich" etwas schreibt. Vor jedem Deploy in dieser
Reihenfolge gehört die Frage beantwortet: *Welche Schreibvorgänge des neuen Clients lehnen die
alten Regeln ab?* Sind es welche, muss das Zeitfenster so kurz wie möglich sein — oder der Client
braucht einen Rückfallpfad.

### Gruppe auflösen nimmt den Wochenplan mit — behoben am 17.08.2026

`dissolveGroup()` ruft erst `dissolveGroupFirestore()` (löscht alle Pläne, Meals, Mitglieder und
das Gruppendokument in einem Batch) und danach `leaveGroup()`, das Plan und Meals als **eigene
Kopie** sichern soll:

```js
const keepRecipes = state.recipes.slice();
const keepPlans = JSON.parse(JSON.stringify(state.plans || {}));
```

Am 16.08.2026 kam dabei ein **leerer** Plan heraus. Der Grund liegt in der Reihenfolge: Zwischen
dem Löschen in Firestore und dem Snapshot feuert der `watchPlans`-Listener und räumt die
gelöschten Wochen aus `state.plans`. Gesichert wird dann, was übrig ist — nichts. Anschließend
schreibt `leaveGroup()` diesen leeren Stand ins eigene Konto und überschreibt damit auch die
letzte Kopie.

**Behoben am 17.08.2026.** `snapshotOwnData()` bündelt die beiden Kopierzeilen, `dissolveGroup()`
zieht den Snapshot **vor** `dissolveGroupFirestore()`, und `leaveGroup(keep)` nimmt ihn entgegen.
Ohne Argument bildet `leaveGroup()` ihn weiter selbst — beim einfachen Verlassen löscht ja niemand
etwas, dort gibt es kein Zeitfenster.

Die Listener bleiben dabei bewusst angemeldet. Sie vorher abzumelden wäre die zweite mögliche
Lösung gewesen, hätte aber `leaveGroupState()` vorgezogen und damit `syncGid` genullt — das
`if (!syncGid) return` am Anfang von `leaveGroup()` hätte den ganzen Rücklauf verschluckt.
Ein vorgezogener Snapshot kommt ohne diese Umbauten aus.

**Der allgemeine Fall dahinter:** Wer lokalen Zustand sichern will, den ein Remote-Listener
mitpflegt, muss ihn sichern, **bevor** er das Remote-Ende anfasst. Zwischen `await` und `await`
liegt in dieser App immer ein Listener-Fenster.

Belegt durch `tools/pruefstand-gruppe-aufloesen.py` (11 Prüfungen, mit Gegenprobe gegen den
alten Stand) — siehe `docs/TESTING.md`.

**Rollback:** alte Regeln aus der Git-Historie erneut veröffentlichen. Der Client bleibt
lauffähig — `memberCount` ist dann ein Feld, das niemand liest.

### Bekannte Grenze, bewusst offen

Zweig 4 der `update`-Regel erlaubt dem **Inhaber**, den Zähler zu senken. Er muss Mitglieder
entfernen können (Ziffer 8a sagt es zu), und die Regel für das Gruppendokument sieht nicht,
*wen* er im selben Batch löscht.

Gegen Beitretende ist der Riegel damit dicht. Gegen einen Inhaber, der mit den
Entwicklerwerkzeugen bei jedem Beitritt den Zähler zurücksetzt, ist er eine Bremse und keine
Mauer. Vertretbar, weil der realistische Missbrauch der weitergereichte Link ist und nicht die
gezielte Firestore-Manipulation am eigenen Abo.

## 102. 61 Rezepte, 51 Namen: zwei Zuflüsse, eine falsche Verdächtige

Der Zwei-Personen-Gruppentest vom 16.08.2026 hinterließ zehn Namenspaare mit gleichem `lib`,
verschiedener `id` und unterschiedlichen Nährwerten. Der im Aufräum-Plan notierte Verdacht -
`isAdopted()` versage nach einem Gruppenwechsel - **traf nicht zu.** `isAdopted()` sieht nur
`state.recipes` des eigenen Kontos und konnte den eigentlichen Fall gar nicht bemerken. Die
Ursache lag eine Ebene höher und hatte zwei getrennte Zuflüsse:

1. **Der Planer kopierte.** `planAdopt()` legte für jedes eingeplante Katalog-Rezept eine
   Bestandskopie mit neuer `uid()` an - drei Planerläufe an einem Abend erzeugten drei neue
   Meals. Der Bestand wuchs still mit jeder Benutzung.
2. **Der Gruppenbeitritt glich nicht ab.** `copyOwnRecipesToGroup()` lud jedes eigene Meal
   hoch, ohne zu prüfen, was in der Gruppe schon lag. Da Startmeals je Ernährungsform fest
   verdrahtet sind (`STARTER`), erzeugten zwei Konten mit gleichem Profil **garantiert** fünf
   Paare, bevor irgendjemand etwas tat.

**Die Lehre: ein plausibler erster Verdacht ist kein Befund.** `isAdopted()` liest sich wie der
naheliegende Übeltäter, weil er genau dort steht, wo Dubletten sichtbar werden (das
Rezeptbuch). Der tatsächliche Fehler lag an zwei ganz anderen Stellen, die beide *Kopien*
erzeugen - `isAdopted()` filtert nur, kopiert aber nie. Wer die Symptomstelle mit der
Ursachenstelle verwechselt, repariert am Ende die falsche Funktion.

**Behoben am 17.08.2026** (`plans/Katalog_als_Nachschlagequelle.MD`): Zufluss 1 ist
trockengelegt, weil der Planer nicht mehr kopiert - `getRecipe()` und `normalizePlan()` kennen
den Katalog jetzt direkt (siehe `docs/ARCHITECTURES.md`, „Der Katalog wird nachschlagbar").
Zufluss 2 ist trockengelegt, weil `copyOwnRecipesToGroup()` vor dem Hochladen gegen den
vorhandenen Gruppenbestand abgleicht. Altlasten aus der Zeit davor räumt eine einmalige,
idempotente Migration (`dedupeAgainstCatalog()`, `state.dedupeV1`) auf.

**Reihenfolge nicht verhandelbar:** Ein Plan-Verweis muss IMMER erst auf die neue `id`
umgebogen werden, dann erst darf die alte Kopie verschwinden (Löschung, Migration oder
Gruppen-Dedup gleichermaßen) - `normalizePlan()` filtert jeden Eintrag gegen die vorhandenen
IDs und wirft einen verwaisten Verweis beim nächsten Laden lautlos weg, ohne Fehlermeldung.

**Falle für die Gruppe:** Die Migration darf erst laufen, wenn der Bestand vollständig steht -
sonst hält sie einen noch leeren oder unvollständigen Gruppenbestand für die Wahrheit und
löscht die eigenen Meals. Deshalb der Riegel `syncGid && !syncHandshakeOk` → sofortiger
Ausstieg, ohne `state.dedupeV1` zu setzen (der nächste Handshake versucht es erneut).

**Nachtrag aus der Gegenprüfung:** Der Abgleich in `copyOwnRecipesToGroup()` brachte einen
*neuen Lesevorgang* in den Beitrittspfad — und der liegt im `try` von `joinGroup()`. Ohne
eigenes `catch` hätte ein Netzfehler beim **Lesen** den gesamten Beitritt zurückgerollt, obwohl
`joinAtomic()` die Mitgliedschaft in Firestore längst geschrieben hatte. Das ist exakt die
Fehlerklasse, die am 16.08.2026 den Beitritt für alle außer dem Inhaber unmöglich machte.

Die Regel dahinter, allgemeiner als dieser Fall: **Wer einem bereits funktionierenden,
mehrstufigen Cloud-Ablauf einen Schritt hinzufügt, muss entscheiden, ob der neue Schritt Pflicht
oder Kür ist.** Hier ist er Kür — fällt der Abgleich aus, wird wie früher alles hochgeladen, und
die Migration räumt die Dubletten später weg. Ein paar Dubletten sind ärgerlich, ein
gescheiterter Beitritt ist schlimmer.

Punkt 101 (Gruppe auflösen löscht den Wochenplan) bleibt davon unberührt; er ist am 17.08.2026
getrennt behoben worden.

## 103. Zwei Planer gleichzeitig: die Funktion war unschuldig, der Zeitpunkt nicht

**Befund vom 16.08.2026:** Luisa bekam Snacks in Slots (`mon.sn`, `sun.sn`), die durch einen
„für alle"-Eintrag längst geschlossen waren. Der notierte Verdacht: `slotOpenForMe()` behandle
`uids === null` falsch.

**Gemessen am 17.08.2026 — der Verdacht trifft nicht zu.** Der Autoplaner-Prüfstand fährt jetzt
zwei zeitversetzte Läufe (`tools/pruefstand-autoplaner.py`, Abschnitt am Ende):

| geprüft | Ergebnis |
|---|---|
| B plant auf A's **aktuellem** Stand | fügt **nichts** hinzu, meldet „Deine Woche ist schon geplant" |
| auch die Snack-Zeile | unangetastet |
| ein fremdes „für alle" | schließt den Slot auch für den, der es nicht geschrieben hat |
| ein Eintrag nur für die andere Person | lässt den Slot offen (Absicht, kein Widerspruch) |
| B plant auf dem **veralteten** Stand | belegt dieselben Slots — der reale Fehlerfall |

Die Ursache ist also ein reiner Zeitversatz: Der zweite Client hatte den Push des ersten noch
nicht empfangen. Das Fenster ist der Debounce von **800 ms** in `scheduleCloudPush()` plus die
Zustellzeit — genau deshalb tritt es nur auf, wenn beide fast gleichzeitig auf „Woche planen"
drücken.

**Bewusst nicht gebaut.** Wasserdicht wäre nur eine Firestore-Transaktion je Slot: `savePlanWeek`
schreibt heute mit `merge: true` ganze Slot-Felder, ein Read-Modify-Write über zwei Geräte kann
das nicht auflösen. Ein Vorab-Refresh im Planer würde das Fenster verkleinern, aber nicht
schließen — er müsste `autoPlanWeek()` asynchron machen (drei Aufrufer plus Undo-Pfad) und
brächte ein neues Risiko mit, weil ein Reload lokale, noch nicht gepushte Slots überschreiben
kann. Für einen seltenen und **gutartigen** Effekt (eine Zusatzportion, per Klick entfernt) ist
das unverhältnismäßig.

**Wer es doch angeht**, muss beides zusammen lösen: erst den eigenen Stand herausschreiben, dann
laden, dann planen — sonst tauscht man einen doppelten Eintrag gegen einen verlorenen.

## 104. Einladungscodes überlebten jeden Gruppenwechsel

**Befund:** Paddys Konto trug am 16.08.2026 vier Codes, die alle auf gelöschte Gruppen zeigten.
Angeklickt ergaben sie nur „Die Einladung konnte nicht geladen werden"; in Firestore lagen sie
als Karteileichen mit `gid`-Verweis.

Die Ursache stand als Kommentar bereits im Code: `dissolveGroupFirestore()` löscht nur Codes,
für die `inv.gid === gid` gilt — also ausschließlich die der **gerade** aufgelösten Gruppe. Ein
Code aus einer früheren Gruppe fällt durch genau diese Prüfung und wird danach nie wieder
angefasst. Über mehrere Gruppenwechsel an einem Abend sammelten sich so vier an.

**Behoben am 17.08.2026** mit `dropAllInviteCodes()`, aufgerufen in `leaveGroup()` — also auf
**beiden** Wegen, Verlassen wie Auflösen. Die Begründung ist eine Zusage der Regeln: Erzeugen darf
einen Code nur der Inhaber einer Gruppe (`allow create: … isOwner(…)`), und in dieser Gruppe ist
man danach nicht mehr. Es gibt keinen Code, der ein Verlassen überdauern dürfte.

Zwei Feinheiten, die leicht falsch herum gebaut werden:

* **Die `delete`-Regel trägt auch bei längst gelöschter Gruppe.** Ihr erster Zweig prüft nur
  `resource.data.by == request.auth.uid` und braucht kein `get()` auf das Gruppendokument — der
  zweite (`isOwner`) würde bei fehlender Gruppe scheitern.
* **Nur erfolgreich gelöschte fliegen aus `state.inviteCodes`.** Eine lokal geleerte Liste wäre
  die sichere Art, ein offline nicht gelöschtes Dokument nie wieder löschen zu können — dieselbe
  Liste benutzt auch `deleteAccountFlow()`. Ein Code in der Liste kostet nichts, er taucht in
  keiner Ansicht auf.
* **Das Aufräumen steht NACH der Datensicherung**, und das ist kein Schönheitsfehler: Ein
  Firestore-Schreibvorgang resolvt erst mit der Server-Bestätigung, offline also gar nicht.
  Im ersten Anlauf stand `dropAllInviteCodes()` vor dem `CloudSync.save()` — damit hätte der
  Rückweg des Wochenplans ins eigene Konto an einer Aufräumarbeit gehangen. Datenintegrität vor
  Ordnung (CLAUDE.md, Ziffer 33). Der Prüfstand misst die **Reihenfolge** der beiden
  `save()`-Aufrufe deshalb ausdrücklich mit.

## 105. Einladungscode verbrauchen: warum das zwei Regel-Deploys braucht, nicht einen

**Befund:** Ein weitergereichter Einladungslink blieb dauerhaft eine offene Tür. Wer ihn je
gesehen hatte, kam herein, sobald ein Platz frei wurde — das Mitgliederlimit von vier war damit
eine Bremse, keine Mauer.

**Umgesetzt am 17.08.2026.** `joinAtomic()` schreibt ein drittes Dokument im selben Batch:
`invites/{code}.used = true`. Atomar ist hier keine Kür — ein Verbrauch ohne Beitritt (oder
umgekehrt) wäre schlimmer als der alte Zustand.

**Gespeichert wird `used: true`, keine UID des Beitretenden.** Wer dabei ist, sagt die
Mitgliederliste; ein zweites Mal bräuchte es dafür einen Personenbezug in einem Dokument, das
jeder Angemeldete lesen darf (CLAUDE.md, Ziffer 20).

### Die Deploy-Reihenfolge ist der eigentliche Inhalt dieses Punktes

Der erste Entwurf notierte „Regeln zuerst, dann Client — reine Erlaubnis-Erweiterung, bricht
nichts". **Das stimmt nur für die Hälfte der Änderung.**

* `allow update` für `invites` ist tatsächlich eine Erweiterung. Ein alter Client schreibt
  einfach kein `used`, ihn stört die neue Erlaubnis nicht.
* Die Verschärfung der `members`-create-Regel ist das Gegenteil. Sie **verlangt**, dass der
  Beitretende den Code im selben Batch als verbraucht markiert. Ein Client, der das noch nicht
  tut, kann dann überhaupt nicht mehr beitreten.

Zwischen einem Regel-Deploy und dem Ankommen des neuen Clients liegen bei GitHub Pages der
Service Worker und der Browser-Cache — alte Clients sind also **garantiert** eine Weile
unterwegs. Genau diese Fehlerklasse hat am 16.08.2026 den Beitritt für alle außer dem Inhaber
unmöglich gemacht (Punkt 101).

Deshalb drei Schritte statt zwei:

1. Regeln mit `allow update` veröffentlichen — bricht nichts.
2. Client ausrollen, der `used: true` mitschreibt — funktioniert mit Regelstand 1.
3. Erst danach den Stufe-2-Block in `firestore.rules` einkommentieren und erneut
   veröffentlichen.

Bis Schritt 3 prüft **nur der Client** auf `used`. Das ist eine Bequemlichkeit, keine Grenze
(CLAUDE.md, Ziffer 18) — Schritt 3 ist Pflicht, nicht Kür.

**Die allgemeine Regel:** Bei einer gestaffelten Auslieferung genügt es nicht zu fragen, ob die
neuen Regeln den alten Client brechen. Man muss jede einzelne Bedingung danach sortieren, ob sie
etwas **erlaubt** oder etwas **verlangt**. Nur das Erlaubende darf vorausfahren.

### Zwei Fallen im Regeltext selbst

* **`get("used", false)` statt `.used`.** Der Zugriff auf ein fehlendes Feld lässt die
  Regelauswertung scheitern — und bei jedem heute bestehenden Code fehlt das Feld. Mit `.used`
  wäre kein einziger Altcode mehr benutzbar gewesen.
* **`existsAfter()` allein ist kein Beitritts-Nachweis** — und das war im ersten Entwurf genau
  der Fehler. Die Begründung lautete: „damit kann niemand einen Code verbrennen, ohne selbst
  beizutreten". Falsch. `existsAfter()` beschreibt den Zustand **nach** dem Batch, und für ein
  **bereits bestehendes** Mitglied ist er ohne jede weitere Aktion erfüllt. Jedes Mitglied —
  auch eines mit „Nur ansehen" — hätte damit jeden offenen Code der eigenen Gruppe per
  einzelnem `update()` verbrennen können. Mit Stufe 2 wäre daraus ein gezielter Riegel gegen
  eine gerade weitergegebene fremde Einladung geworden: Die eingeladene Person käme nie mehr
  herein. Nebenbei unterläuft es die engere `delete`-Regel, die das Zurückziehen bewusst auf
  Ersteller und Inhaber beschränkt.

  Richtig ist der **Zwei-Zustands-Riegel** `!exists(memberPath(gid)) && existsAfter(…)` —
  vorher kein Mitglied, nachher Mitglied. Dasselbe Muster stand längst zwei Regeln weiter oben
  im `memberCount`-Zweig; es war nur nicht übertragen worden. **Merksatz:** Ein `existsAfter()`
  ohne sein `!exists()` beweist einen Zustand, keinen Übergang. Gefunden vom
  `website-security`-Agenten, nicht beim Lesen.
* **`hasOnly(["used"])`** gehört ebenso dazu, sonst ließe sich über den Update-Weg die Rolle
  hochschreiben.

### Und die Reihenfolge im Client

`joinGroup()` prüft `inv.used` **innerhalb** des Else-Zweigs, also erst nachdem `istMitglied()`
verneint hat. Die Prüfung nach oben zu den anderen Riegeln zu ziehen ist die erste Idee, die man
hat — und sie sperrt jedes bestehende Mitglied aus, das über denselben Link zurückkehrt. Der
Prüfstand `tools/pruefstand-einladung-verbrauch.py` fährt genau diese falsche Fassung als
Gegenprobe.

---

## 106. Firebase lokal: der eine Pfad, der die App sonst zweimal startet

**Datum:** 23.08.2026 · **Anlass:** D4 — das SDK aus dem Repo statt vom gstatic-CDN.

Die drei ES-Module liegen jetzt in `vendor/firebase/10.12.5/` und werden relativ importiert.
Die Umstellung sieht nach „drei URLs ersetzen" aus. Sie hat drei Fallen.

### 1. `firebase-auth.js` und `firebase-firestore.js` importieren gstatic weiter

Beide Bundles enthalten am Anfang

```js
import{…}from"https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js"
```

Wer nur die drei Importe in `index.html` umstellt, hat das Ziel **verfehlt** und es zusätzlich
kaputt gemacht: Die Seite lädt `firebase-app.js` dann **zweimal** — einmal lokal für
`initializeApp`, einmal von gstatic für Auth und Firestore. Zwei Modulinstanzen heißen zwei
getrennte Komponenten-Register; `getAuth(app)` sucht seine App im falschen. Beweisen lässt es
sich nur über die Ressourcenliste der Seite, nicht über das DOM:

```js
performance.getEntriesByType("resource").filter(e => e.name.indexOf(location.origin) !== 0)
```

Muss `[]` sein. `tools/firebase-vendor.py` schreibt diesen einen Import um und **bricht ab**,
wenn er ihn nicht findet — ein stilles Weiterlaufen wäre hier das Schlimmste.

### 2. Dieselbe URL steht in `firebase-app.js` — und darf nicht angefasst werden

```js
const name$p = "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js"
const logger = new Logger('https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js')
```

Das ist kein Ladepfad, sondern der **Komponentenname**, unter dem sich das Modul registriert
und loggt. Ein `sed` über alle Dateien benennt eine registrierte Komponente um. Deshalb ersetzt
das Skript ausdrücklich nur das Muster `from"<url>"` und nur in den beiden anderen Dateien.

### 3. Der `file://`-Smoke-Test zeigt ab jetzt den lokalen Modus

Ein relativer Modul-Import scheitert über `file://` an der Opaque Origin. Die App fängt das über
ihren 6-Sekunden-Timeout ab und startet lokal — `#view` ist gefüllt, aber es steht „Wie sollen
wir dich nennen?" statt „Willkommen bei Paddy's Mealplan". Vor D4 ging der `file://`-Lauf durch,
weil gstatic per `https` mit `Access-Control-Allow-Origin: *` antwortete.

**Das ist ab jetzt kein Befund, sondern der Normalfall.** Wer den Cloud-Pfad sehen will, lädt
über `test-server.ps1`. Nachgemessene Belege stehen in `docs/TESTING.md`, Abschnitt 1.

### Was lokal *nicht* geht

`signInWithPopup` öffnet ein iframe unter `https://<projekt>.firebaseapp.com/__/auth/…`. Das ist
Google-Infrastruktur und kein Bundle — es bleibt ein Fremdaufruf, bis der native Login aus D7 da
ist. Für Apple 2.5.2 ist das unkritisch (es lädt keinen Code in die App), für die
Datenschutzerklärung bleibt Google damit weiterhin Empfänger.

---

## 107. Zwei `history.back()` im selben Tick sind nur eines

**Datum:** 23.08.2026 · **Anlass:** D5 — die Zurück-Taste schließt Overlays.

Der Umbau legt je offenem Overlay einen History-Eintrag an. Ein auf normalem Weg geschlossenes
Overlay muss seinen Eintrag zurücknehmen, sonst bleibt er als toter Eintrag stehen und der
nächste Druck auf Zurück tut **sichtbar nichts** — genau der Kritikpunkt, den D5 abstellen soll.

Die erste Fassung rief dafür schlicht `history.back()` und zählte mit, wie viele `popstate`
selbst ausgelöst wurden. Sie bestand acht Prüfungen und fiel bei der neunten durch:

> `closeModal()` beendet zuerst einen laufenden Barcode-Sucher (`liveScanStop`) und schließt
> danach sich selbst.

Das sind **zwei** Rücknahmen im selben Tick. Gemessen: Der Stapel war korrekt leer, beide
Overlays zu — aber die History stand noch einen Eintrag zu hoch. Der Browser führt zwei
unmittelbar aufeinanderfolgende `back()` nicht als zwei Sprünge aus.

### Zwei Lehren, nicht eine

**1. Rücknahmen bündeln.** Ein `setTimeout(…, 0)` sammelt die Rücknahmen eines Ticks und löst
sie als ein `history.go(-n)` aus.

**2. Nicht eigene Ereignisse zählen — die Marke im Eintrag lesen.** Ob `history.go(-2)` ein
`popstate` auslöst oder zwei, ist Browsersache; ein Zähler steht danach falsch und schließt beim
nächsten echten Zurück ein unbeteiligtes Overlay. Der Eintrag trägt deshalb `{pmOverlay: tiefe}`,
und der Handler schließt alles, was über der Marke des angesteuerten Eintrags liegt. Nach einer
selbst ausgelösten Rücknahme ist der Stapel bereits kurz genug — die Schleife läuft dann gar
nicht erst an, ganz ohne Zähler.

### Der Folgefall, der dabei auffiel

Schließen und im **selben Tick** wieder öffnen kommt real vor: „Teilen" in der Meal-Ansicht ruft
`closeModal()` und direkt danach `shareRecipeNow()`. Wäre die Rücknahme da schon unterwegs, risse
sie das eben geöffnete Fenster gleich wieder mit. `overlayOpened()` prüft deshalb auf offene
Rücknahmen und erbt den vorhandenen Eintrag per `replaceState`.

### Der Nebenfund: der zweite Schließversuch war ungeprüft

`closeModal()` leert `modalCloseHook`, **bevor** es ihn aufruft. Verweigert `attemptClose()`
danach das Schließen (Meal-Formular ohne Namen), ist der Hook weg — der **zweite** Versuch ging
seither ungeprüft durch und verwarf den Entwurf still. Über Escape war das schon vorher so; die
Zurück-Taste nimmt denselben Weg und hat es sichtbar gemacht. `attemptClose()` trägt sich beim
Abbruch jetzt wieder ein.

Dazu kommt der Fall, den es vorher gar nicht gab: Kommt der Versuch aus `popstate`, ist der
History-Eintrag beim Aufruf **schon zurückgenommen**. Das Formular stünde dann ohne Eintrag da,
und der nächste Druck auf Zurück verließe die App. `closeModal()` meldet eine Verweigerung
deshalb mit `false`, und der Handler legt den Eintrag neu an. Am DOM ablesen ließe sich das
nicht — während der Exit-Animation steht das Overlay genauso noch da.

### Und eine Falle im Prüfstand selbst

Der erste Lauf zeigte nur `laeuft…` — kein Ergebnis, keine Fehlermeldung. Ursache war ein
Syntaxfehler in der erzeugten Seite (die Gegenprobe hatte den ganzen Ausschnitt ein zweites Mal
eingebunden und damit `overlayStack` doppelt deklariert). Der `window.onerror`-Melder stand im
**selben** Script-Block und wurde deshalb nie angemeldet.

**Für Prüfstände gilt derselbe Ablauf wie für die App:** `python syntax-check.py <datei>` zuerst.
Er nimmt einen Pfad als Argument und benennt Fehler und Zeile in einer Sekunde.

## 108. Ein `undefined` im Ziel legte die ganze Cloud-Sicherung still

**Gemeldet als:** „Ich habe beim Onboarding Vegetarisch gewählt, dann über *Ziele neu berechnen*
etwas anderes eingestellt — danach hat es nie wieder gespeichert." Der alte Stand kam nach jedem
Neustart zurück. Betroffen war nicht nur das Ernährungsprofil, sondern **jedes** Feld des
Kontodokuments: Ziel, Gewichte, Zielgewichte, Favoriten, Profilbild, Einladungscodes.

Drei Ursachen, die sich gegenseitig verdeckt haben.

### (a) `computeGoal()` reicht `undefined` durch — Firestore lehnt das Dokument ab

`onbGoalInput()` schreibt „keine Einschränkung" bewusst nicht als Wert:

```js
diet:  c.diet && c.diet !== "alles" ? c.diet : undefined,
avoid: c.avoid && c.avoid.length   ? c.avoid.slice() : undefined,
```

Das ist richtig — ein Feld, das bei fast allen denselben Wert trägt, ist Ballast im Datensatz.
`computeGoal()` gibt beide Felder unverändert weiter, und der Kommentar dort sagte schon immer:
„undefined bleibt undefined, `sanitizeGoal` räumt es danach weg". **Nur lief `sanitizeGoal()` an
den zwei Stellen nicht, die `computeGoal()` aufrufen** — im Wizard-Schritt `result` und in
`syncGoalWeight()`.

Lokal fiel das nie auf: `JSON.stringify` verschluckt `undefined` ersatzlos. Das Firestore-SDK
nicht — es wirft `Unsupported field value: undefined`, und zwar für das **ganze Dokument**.

`syncGoalWeight()` ist dabei der schlimmere der beiden Wege: Dort fehlt der Schlüssel `diet` im
gespeicherten Ziel meistens **ganz** (weil `sanitizeGoal()` ihn korrekt entfernt hat).
`Object.assign` kopiert ihn deshalb nicht, `computeGoal()` setzt ihn auf `undefined` — und damit
kippte **jede Wiegung** eines Kontos ohne Ernährungsprofil die Cloud-Sicherung.

### (b) Der Fehler meldete sich als „offline"

```js
} catch (e) { lastPushedJSON = null; setSyncStatus("offline"); }
```

Ein Netzfehler heilt von selbst, ein Datenfehler nie — beide sahen gleich aus. `lastPushedJSON =
null` sorgte zusätzlich dafür, dass **jeder** weitere `save()` denselben Wurf erneut erzeugte.
Deshalb blieb der Fehler wochenlang unbemerkt: Der Sync-Punkt stand auf „offline", was in einer
App, die offline funktionieren soll, wie ein vorübergehender Zustand aussieht.

`pushNow()` unterscheidet jetzt am Fehlercode (`unavailable`, `deadline-exceeded`, `cancelled`,
`resource-exhausted` = Netz) und meldet alles andere **einmalig** über `noteError()` plus Toast —
einmal, nicht alle 800 ms (dasselbe Muster wie `cloudTooBigWarned`/`recipesSyncFailed`).

**Die allgemeine Regel:** Ein `catch`, der zwei Fehlerklassen mit derselben Meldung abfrühstückt,
versteckt die schlimmere von beiden. Wenn eine davon nicht von selbst weggeht, muss sie sich
unterscheiden lassen.

### (c) `merge: true` kann ein Feld gar nicht löschen — das falsche Werkzeug von Anfang an

`CloudSync.save()` schrieb mit `setDoc(..., { merge: true })`. Das ist ein **tiefer** Merge über
Blattpfade: Eine Map, die ohne `diet` ankommt, löscht `goal.diet` in Firestore nicht.
**„Vegetarisch → Alles" war über diesen Weg grundsätzlich nicht wegzuschreiben**, auch nach dem
Fix von (a) nicht.

Der Kommentar an der Stelle beschrieb die Absicht völlig korrekt („schreibt nur die übergebenen
Felder und lässt alles andere stehen") — nur ist das die Semantik von **`mergeFields`**, nicht die
von `merge: true`. Ein Kommentar, der die Absicht beschreibt, ist kein Beleg dafür, dass der Code
sie umsetzt.

Zwei weitere, bereits dokumentierte Entscheidungen hingen still daran:

* **`manual: true`** (Ziffer 74) verschwand nach „Ziele neu berechnen" nur lokal. In der Cloud
  blieb es stehen und kam beim nächsten Start zurück — der Rechner hob die Handmarke also
  **nicht** dauerhaft auf, entgegen der dortigen Zusage.
* Ein entfernter Trainingstag in `goal.training` und ein gelöschtes Jahr in `weightGoals`
  überlebten in der Cloud.

Jetzt `{ mergeFields: Object.keys(data) }`: Was der Aufrufer schickt, wird **ganz** ersetzt; was
er weglässt, bleibt unangetastet. Die Teil-Schreibvorgänge (`{ pendingGroupId: … }`) verhalten
sich unverändert.

**Zwei Felder ändern dadurch ihre Semantik, beide gewollt:** `plans` (nur außerhalb einer Gruppe)
wird ersetzt statt gemischt — `state.plans` ist durch `pruneWeeks()` ohnehin beschnitten, und
beim Lesen läuft `pruneWeeks()` erneut. `weightGoals`, `deleted`, `weightConsent` und `planned`
werden ebenfalls ersetzt; alle vier werden in `onRemote()` **vor** dem Speichern lokal vereinigt,
der lokale Stand ist also bereits der vollständige.

### Was den Fehler unsichtbar hielt

Der Nutzer sah eine App, die lokal alles richtig anzeigte. Erst der Neustart holte den alten
Stand zurück — und da war die Verbindung zur eigenen Änderung längst verloren. Genau deshalb sind
(a) und (b) getrennt behoben worden: (a) macht den Datensatz sauber, (b) sorgt dafür, dass der
nächste Fehler dieser Art beim ersten Auftreten sichtbar ist.

`ignoreUndefinedProperties: true` liegt jetzt zusätzlich als Netz unter den Sanitizern (beide
Zweige von `initializeFirestore()`, auch der Fallback ohne persistenten Cache). Es ersetzt sie
nicht: Ein still fallengelassenes Feld ist eine Notbremse, kein sauberer Datensatz.

## 109. Zwei Prüfwerkzeuge, die seit ihrer Entstehung nichts geprüft haben

Beim Bau des Prüfstands für Ziffer 108 fiel auf, dass `tools/smoke-mit-daten.py` seinen Zweck nie
erfüllt hat. Zwei Gründe, beide auch für jeden künftigen Prüfstand relevant.

### `index.html` hat gar kein `<head>`-Tag

Die Datei beginnt mit `<!doctype html>`, `<html lang="de">` und dann direkt den Meta-Tags — der
Browser ergänzt `<head>` selbst. Der **einzige** Treffer für die Zeichenkette `<head>` in der
ganzen Datei steht in einem JS-Kommentar (bei `MOTION`, rund um Zeile 8200).

`seite.replace("<head>", "<head>" + seed, 1)` setzte das Seed-Script also **mitten in einen
Kommentar** — das zerschlägt die Kommentarzeile, beendet den `<script>`-Block und schaltet damit
das halbe App-Script ab. Der Test lief trotzdem durch und meldete „keine Fehler", weil seine
Auswertung an `</html>` hing und dort intakt ankam.

**Einhängepunkt ist jetzt `<meta charset="utf-8">`** — genau einmal in der Datei, und der Test
bricht ab, wenn das nicht mehr stimmt. **Dahinter, nicht davor:** Ein Script vor der
Zeichensatzangabe schiebt sie über die 1024-Byte-Grenze hinaus, ab der der Browser sie ignoriert.

### `localKey()` hängt unter `file://` und auf `localhost` ein `__test` an

`isTestOrigin()` ist ausdrücklich so gebaut, damit Testläufe die echten Daten nicht anfassen.
Die Schlüssel heißen dort also `wochenkueche_v1__test` und `wochenkueche_profile_v1__test`.
Wer nur `wochenkueche_v1` setzt, sät ins Leere: Die App liest nichts und zeigt den Login — der
Test misst dann den Anmeldebildschirm und hält ihn für einen gesunden Start.

Beide Prüfstände setzen jetzt **beide** Schreibweisen. Nach der Reparatur zeigt
`smoke-mit-daten.py` tatsächlich den Wochenplan.

**Die allgemeine Lehre, und sie ist die wichtigere:** Ein Prüfstand, der noch nie rot war, ist
kein Beweis, sondern ein Verdachtsfall. Die Gegenprobe gegen den Stand **vor** der Änderung ist
deshalb keine Kür — `tools/pruefstand-rezeptbuch-ansicht.py` nimmt dafür einen Dateipfad als
Argument, `tools/mobilprobe-rezeptbuch.html` einen `?alt=1`-Schalter.

## 110. Das versprochene `render()`, das es nie gab

**Gemeldet als:** „Die Nährwerte im Wochenplan bleiben nach dem Bearbeiten stehen." Der Zustand
war korrekt, nur die Anzeige alt — die kcal je Slot-Karte, die Tagesbilanz und die klebende
Leiste `#day-bal` standen auf dem alten Wert, bis irgendetwas anderes neu zeichnete
(Reiterwechsel, Drag&Drop, ein Cloud-Snapshot).

`commitNow()` endete mit:

```js
save();
if (view.querySelector("#r-groups")) paintRecipeGroups();
```

`#r-groups` gibt es nur im Meals-Reiter. Der Kommentar darüber versprach ausdrücklich, über dem
Wochenplan genüge ein `render()` **nach** dem Schließen, „siehe `attemptClose()`/`[data-close]`".
**Dieses `render()` existierte an keiner der drei genannten Stellen.** `attemptClose()` →
`finishClose()` machte nur `restoreFocusTarget()` + `closeModal()`; `closeModal()` leert
`modalRoot`; der `[data-close]`-Handler ist schlicht `closeModal`.

**Ein Kommentar, der eine Stelle nennt, ist kein Beleg dafür, dass es sie gibt.** Dieselbe
Fehlerklasse wie bei `merge: true` in Ziffer 108 — dort beschrieb der Kommentar korrekt eine
Absicht, die der Code nicht umsetzte.

### Die eigentliche Arbeit steckte nicht im `render()`, sondern in der Frage „hat sich was geändert?"

Ein `render()` bei **jedem** Schließen wäre falsch: `commitNow()` läuft auch beim bloßen
Hineinsehen — `attemptClose()` ruft es, und jedes `focusout` ebenfalls. Der Wochenplan würde
dann bei jedem Blick in ein Meal komplett neu gezeichnet.

Zwei Anläufe waren nötig, und beide Fehlschläge sind lehrreich:

**(a) Signatur vor/nach `mutateLocal()` innerhalb von `commitNow()` — maß nichts.**
`scheduleCommit()` ruft `mutateLocal()` bereits beim `input`-Ereignis. Das nachfolgende
`commitNow()` sah vorher wie nachher denselben, längst geänderten Wert. Die Marke blieb `false`,
**der Fehler sah behoben aus, ohne behoben zu sein** — der Prüfstand hat das gefangen, das
Codelesen nicht.

**(b) `canonJSON()` über das ganze Objekt, verglichen mit dem Stand beim Öffnen — schlug zu oft
an.** `mutateLocal()` normalisiert nebenbei: Ein Meal ohne `steps` bekommt `""`, ein leeres
`tags: []` wird gelöscht. Das ist keine Nutzeränderung, zählte aber als eine.

**Die Signatur beschreibt jetzt ausdrücklich nur die Felder, die dieses Formular schreibt** —
`name`, `category`, `ingredients`, `nutrition`, `steps`, `tags`, `mealPrep` — und zwar in
derselben normalisierten Form, in der `mutateLocal()` sie ablegt. `image` bleibt draußen (ein
eigenes Foto ist Base64; der Vergleich wäre ein megabytegroßer String bei jedem `focusout`), die
beiden Foto-Knöpfe melden sich stattdessen selbst.

**Allgemein:** Eine „hat sich etwas geändert?"-Prüfung muss gegen den Stand **beim Öffnen**
vergleichen, nicht gegen den Stand kurz vor dem Schreiben — und sie muss wissen, welche Felder
überhaupt zur Frage gehören.

### Und die Reihenfolge in `finishClose()` ist nicht beliebig

```js
function finishClose() {
  if (sheetDirty() && !view.querySelector("#r-groups")) render();
  restoreFocusTarget(recId);
  closeModal();
}
```

`render()` steht **vor** `restoreFocusTarget()`. Das merkt sich einen **Knoten** in `lastFocused`,
und `render()` ersetzt `view` komplett per `innerHTML`. Andersherum wäre der gemerkte Knopf danach
abgehängt, `closeModal()` prüft `document.contains()` — und der Fokus fiele ins Nichts. Die
Exit-Animation ist davon nicht betroffen: `finishClose` läuft ohnehin erst nach `closeWithMotion`.

### Der Prüfstand hat gleich den nächsten Fehler mitgebracht: `macroOverridden`

Der erste Entwurf des Prüfstands testete den Fall „nur hineingesehen, nichts geändert" mit einem
Meal **ohne Zutaten** — aufgefallen ist das dem `kvp`-Agenten, nicht mir. Mit gemischten Zutaten
(Freitext, Objekt mit Einheit, Objekt mit Nährwerten) fiel er sofort um, und zwar härter als
erwartet: **Beim bloßen Öffnen wurden aus 500 gespeicherten kcal 440.**

`macroOverridden` lebte **innerhalb** von `openMealSheet()` und startete bei jedem Öffnen auf
`false`. `updateMacroSum()` schrieb daraufhin die Zutatensumme in die Felder, und der erste
`commitNow()` — den schon das Schließen auslöst — machte sie dauerhaft. Wer seine Makros von
Hand gesetzt hatte, verlor sie beim nächsten **Öffnen** des Editors, ohne etwas zu tun.

**Die Übersteuerung ist eine Eigenschaft des Meals, kein Sitzungszustand.** Sie wird deshalb aus
den Daten abgeleitet: Weicht das gespeicherte `nutrition` von der Zutatensumme ab, war es von
Hand gesetzt. Kein neues Datenfeld nötig, rückwärtskompatibel.

**Zwei Details entscheiden, ob das funktioniert:**

* **Aus den DATEN rechnen, nicht aus dem DOM,** und die Marke **vor** dem Aufbau der
  Zutatenzeilen setzen. `addIngRow()`/`openIngEdit()` rufen `updateMacroSum()` bereits selbst —
  genau dieser Aufruf überschreibt die Felder, solange die Marke noch `false` ist. Eine
  Ableitung nach der Schleife kam nachweislich zu spät: Der Reset-Knopf erschien dann korrekt,
  im Feld stand aber längst die Summe. Das war erst an einer Messung von `#f-kcal` direkt nach
  dem Aufbau zu sehen, nicht am Ergebnis.
* **Auf dieselbe Genauigkeit runden, in der `updateMacroSum()` schreibt** (kcal ganzzahlig,
  Makros auf eine Nachkommastelle). Sonst gilt ein Rundungsrest als Übersteuerung, und
  „Automatisch übernehmen" stünde dauerhaft da.

**Allgemein, und das ist die Lehre aus Ziffer 74 in neuer Form:** Jede Funktion, die abgeleitete
Werte neu berechnet, braucht eine Antwort auf die Frage „und wenn der Nutzer sie selbst gesetzt
hat?". Steht die Antwort in einer Variablen, die bei jedem Öffnen neu entsteht, ist sie keine
Antwort.

### Was `sheetDirty()` ausdrücklich NICHT erkennt

Gleichzeitiges Bearbeiten desselben Meals auf zwei Geräten bleibt **last-write-wins**.
`mutateLocal()` schreibt beim Schließen alle Formularfelder zurück, unabhängig davon, ob
zwischenzeitlich ein Remote-Snapshot dieselben Felder geändert hat — nur die *Löschung* des Meals
wird über `openSheetRemovedCb` abgefangen, ein reines Update nicht. `sheetDirty()` vergleicht
dabei gegen den Stand beim Öffnen, sieht also „unverändert" und meldet keinen Konflikt.

Das ist **kein neues Verhalten** — `commitNow()` schrieb beim Schließen schon immer —, aber
`sheetDirty()` ist ab jetzt die Stelle, an der man es vermuten würde. Wer einem künftigen
Sync-Fehler nachgeht, sucht ihn dort vergeblich (Fund des `kvp`-Agenten).

## 111. Eine Filterschwelle direkt neben der Zahl, die die App selbst erzeugt

`recipeFilterHtml()` begann mit `if (liste.length < 6) { aktive.clear(); return ""; }`.
`addStarterMeals()` legt nach dem Onboarding genau `STARTER_ANZAHL = 5` Meals an.

**5 < 6 — jeder neue Nutzer sah seine Startmeals ohne eine einzige Filterzeile**, bis er das
sechste Meal anlegte. Die Schwelle war als Schutz gegen eine Chip-Reihe über zwei Karten gedacht;
sie stand aber genau eine Position neben der Zahl, die die App selbst erzeugt. Das ist kein
Grenzfall, das ist der Regelfall.

Schwelle jetzt `< 4`. Dazu die zweite Hälfte, ohne die die erste das Problem nur verlagert hätte:
**ein Merkmal wird nur zum Chip, wenn es auf mindestens einen und nicht auf alle Einträge
zutrifft.** Nachgerechnet ergäbe die gesenkte Schwelle allein über den fünf Startmeals eines
Veganers sechs Chips, davon zwei („Vegan", „Vegetarisch") auf *alle fünf* zutreffend. Ein Filter
ist ein Werkzeug zum Wegnehmen; trifft er auf alles zu, nimmt er nichts weg.

**Merkregel für Schwellenwerte:** Wenn die App selbst eine Anzahl erzeugt, muss jede Schwelle in
ihrer Nähe gegen genau diese Zahl geprüft werden — nicht gegen einen gefühlten Normalfall.

## 112. `weekLabel()` war zweimal deklariert — und die falsche gewann

Zwei Top-Level-Function-Declarations gleichen Namens im selben Script-Block:

* eine erwartete einen ISO-Wochenschlüssel (`"2026-W33"`) → `"KW 33 · 10.08."`
* eine erwartete eine Zahl (Wochen-Offset) → `"Woche 29 · 13.–19. Juli"`

Durch Hoisting gewinnt die **spätere** für alle Aufrufer. Die acht Aufrufstellen mit
Wochenschlüssel rechneten deshalb `getDate() + "2026-W33" * 7` → `NaN`. **Live gemessen:**

```
Woche NaN · NaN. undefined – NaN. undefined: 88,5 Kilogramm
```

Betroffen waren das Gewichtsdiagramm samt `aria-label` und `<title>` je Punkt, die Kennzahl unter
der Kurve, das Wochen-Dropdown, die Liste im Verwalten-Dialog samt Lösch-Beschriftung und der
Toast nach dem Wiegen. Der Fehler war **still**: keine Ausnahme, nur `NaN` im Text.

Die Wochenschlüssel-Variante heißt jetzt `weekKeyLabel()`, die acht Aufrufer sind mitgezogen.

**Verifikation vor dem Fix, nicht danach** — der Plan verlangte das ausdrücklich, und zu Recht:
Die Klammerbilanz ist als Beweis untauglich (Regex- und Template-Literale verfälschen sie), und
`weekLabel()` lebt im IIFE, ist also von außen nicht aufrufbar. Bewiesen wurde es über die
**Anzeige** (`tools/pruefstand-wochenbeschriftung.py`), mit der Hero-Zeile als Gegenprobe: Die
Zahl-Variante musste unverändert ihre eigene Form behalten.

**Allgemein:** Zwei gleichnamige Funktionsdeklarationen sind kein Syntaxfehler und keine Warnung.
Der Linter, der das fände, existiert in diesem Projekt nicht — die einzige Verteidigung ist, bei
`grep -n "function name"` auf die **Anzahl** der Treffer zu sehen.

---

## 113. Ein neues Icon, das nur die halbe `viewBox` benutzt

Mit dem Eiweißshake-Wechsel bekam die Kategorie „Getränk" ein eigenes Symbol — vorher fiel sie
über `CAT_ICON[cat] || "pot"` auf den Topf zurück. Die erste Fassung des Trinkglases war ein
sauberer Pfad und sah bei 64 px gut aus. In der Kopfzeile, wo das Icon **16 px** groß ist, las es
sich als Becher oder Batterie.

**Die Ursache war keine Detailfrage, sondern die Breite.** Das Glas lief von `x=6` bis `x=18` —
die Hälfte der 24er-`viewBox`. Alle Nachbarn nutzen sie ganz: der Topf `2–22`, das Besteck
`4–21`, das Brot `3,5–20,5`. Bei 16 px Renderbreite blieben davon also 8 px echte Zeichnung neben
16 px bei den anderen. In einer Reihe untereinander stehender Kategorien fällt genau das auf,
nicht die Form.

**Regel:** Ein neues `ICONS`-Symbol wird bei **16 px neben einem bestehenden Nachbarn** geprüft,
nicht allein und nicht groß. Der Vergleich kostet eine HTML-Datei im Scratchpad und einen
Edge-Screenshot; die Fassung mit `x=4,5` bis `19,5` stand danach in einer Minute.

Dieselbe Überlegung steht schon bei `ICON_DUMBBELL` im Code, dort aus dem umgekehrten Grund
(gefüllte Flächen statt Konturen, weil dünne Striche bei 13 px verschmelzen). Beide Fälle sagen
dasselbe: **Die Zielgröße ist Teil der Zeichnung, nicht eine Anzeigeeinstellung.**

---

## 114. Die eine ID-Ausgabe ohne `esc()` — gefunden beim Lesen der Nachbarzeilen

Beim Push-Check zum Schnell-Aufklapper fiel eine Stelle auf, die mit der Änderung nichts zu tun
hatte: Der Picker schrieb `data-assign="${r.id}"` **ohne** `esc()`. Die drei Geschwister tun es
seit jeher — `data-cbview="${esc(r.id)}"`, `data-adopt="${esc(r.id)}"`,
`data-cbcat="${esc(cat)}"`. Vier gleichartige Ausgaben, drei escaped, eine nicht.

**Warum das mehr als Kosmetik ist:** `sanitizeRecipe()` prüft die `id` nicht. Sie kommt über
`Object.assign({}, r)` ungeprüft durch — bewusst, denn die Funktion säubert Bild, Kategorie,
Zutaten und Merkmale, nicht Schlüssel. Und Rezepte entstehen nicht nur lokal: Sie kommen aus
**Sharing-Links und aus dem Gruppen-Sync**, also von fremd.

Die Gegenprobe mit dem echten `esc()` aus `index.html` (Prüfstand im Scratchpad):

| | Attribut `onmouseover` erzeugt? | `dataset.assign` |
|---|---|---|
| ohne `esc()` | **ja** — der Ausbruch gelingt | auf `r1` verstümmelt |
| mit `esc()` | nein, nur `class` und `data-assign` | vollständig und unverändert |

Die id kommt über `dataset` **dekodiert** wieder heraus — die Zuweisung ändert sich durch das
Escapen also nicht, gegengeprüft auch mit einer normalen id.

**Die Lehre ist nicht „immer escapen"** — das wusste das Projekt. Sie lautet: **Wo dieselbe Sache
an vier Stellen ausgegeben wird, ist die Abweichung der Fund.** Drei Stellen richtig zu haben
erzeugt genau das Vertrauen, das die vierte durchrutschen lässt. `grep` auf das Muster
(`data-[a-z]*="\${` ohne `esc`) kostet eine Sekunde und findet so etwas zuverlässiger als das
Lesen der geänderten Zeilen.

Nicht angefasst und bewusst offen: `sanitizeRecipe()` prüft die `id` weiterhin nicht. Escaping
bei der **Ausgabe** ist der richtige Ort dafür; eine Formatprüfung beim Einlesen träfe auch
Bestandsdaten und Katalogschlüssel und wäre ein eigener Umbau.

---

## 115. Ein neues Sync-Feld braucht ZWEI Merge-Stellen — der isolierte Prüfstand sieht nur eine

Beim Aufnehmen von `weekStats` in den Cloud-Sync war die Verschmelzungsfunktion
`mergeWeekStats()` fertig, mit 22 grünen Prüfungen samt Gegenprobe: Vereinigung, wertbasierter
Tiebreak, Konvergenz über zwei Runden, 26-Wochen-Grenze. Der Aufruf stand in `onRemote()`.

**Die Abnahme am echten Konto fiel trotzdem durch.** Ein Gerät, das eine Woche nicht kannte,
löschte sie in der Cloud — genau der Datenverlust, den die ganze Übung verhindern sollte.

**Der Grund:** Der Sync hat **zwei** Zusammenführungen, nicht eine.

| Stelle | Wann | Was passiert danach |
|---|---|---|
| `startCloudSync()`, Block `if (remote) { … }` | einmal beim Anmelden/Start | setzt `cloudBaselineOk = true` und ruft **sofort `pushNow()`** |
| `onRemote()` | bei jedem weiteren Snapshot | nur `save()`/`render()` |

`onRemote()` kam beim Start gar nicht zum Zug: Der Baseline-Push war schneller, hatte das
dünne lokale Archiv im Gepäck, und `mergeFields` ersetzte das Cloud-Feld ganz. Der eingehende
Snapshot war danach der **eigene** — `j === lastPushedJSON`, also `return`.

**Regel: Wer ein Feld in den Sync aufnimmt, sucht beide Stellen.** Der Baseline-Block ist an
seinen Nachbarn zu erkennen — `mergeWeights`, `mergeConsent`, `mergeTombstones`, `favs`,
`planned` stehen dort alle beieinander. Fehlt der neue Nachbar in dieser Reihe, ist er
vergessen worden. Umgekehrt gilt dasselbe: Nur im Baseline-Merge gepflegt, würde ein Gerät
Änderungen des anderen im laufenden Betrieb verwerfen.

**Die allgemeine Lehre ist die über Prüfstände:** Ein isolierter Prüfstand prüft die
**Funktion**, nicht ihre **Aufrufer**. Er kann per Konstruktion nicht bemerken, dass ein
zweiter Aufruf fehlt — er ruft ja selbst auf. 22 grüne Prüfungen waren hier kein Beleg für
Korrektheit, sondern nur dafür, dass die Funktion stimmt. **Bei Sync-Änderungen ist der Lauf
am echten Konto (`tools/cdp.py`) keine Kür, sondern der einzige Ort, an dem ein fehlender
Aufrufer auffällt.**

---

## 116. `innerHTML` wirft die Scrollposition NICHT weg — zwei Runden toter Code dafür

`kvp` meldete zum Picker: Der Knopf „Alle anzeigen" halte die Scrollposition nicht, während der
neue Schnell-Aufklapper daneben es richtig mache. Klang plausibel, die beiden standen
nebeneinander, und die Empfehlung war zwei Zeilen lang:

```js
const top = listEl.scrollTop;
paint(searchEl.value);
listEl.scrollTop = top;
```

**Gemessen war die Behauptung falsch — und zwar für beide Knöpfe.** Gegen eine Kopie *ohne*
diese Zeilen (Ganzdatei-Kopie, siehe `docs/TESTING.md`) im ferngesteuerten Chrome:

| | mit den Zeilen | ohne die Zeilen |
|---|---|---|
| „Alle anzeigen", `scrollTop` 200 | 200 | **200** |
| Schnell-Aufklapper, `scrollTop` 150 | 150 | **150** |

**Chrome hält `scrollTop` über einen `innerHTML`-Neuaufbau hinweg**, solange die neue Höhe es
zulässt. Auch `el.innerHTML = el.innerHTML` lässt die Position stehen. Und wird die Liste so
viel kürzer, dass der Browser klemmen muss, richtet die Rettung es ebenfalls nicht — der Inhalt
ist dann weg. Es gibt keinen Fall, in dem die zwei Zeilen etwas tun.

**Der Fokus dagegen geht wirklich verloren** und ist der einzige Grund, warum es den Helfer
`umschalten()` überhaupt gibt: Ohne ihn steht `document.activeElement` nach dem Neuzeichnen auf
`<body>` — gemessen, und das mitten in einem geöffneten Dialog.

**Zwei Lehren, und die zweite ist die unbequeme:**

1. **`innerHTML` und Scrollposition: nachmessen statt annehmen.** Die Annahme ist verbreitet
   genug, dass sie hier zweimal in den Code geraten wäre.
2. **Der falsche Kommentar stand zuerst von mir selbst da.** Der Schnell-Aufklapper (`56c4b41`)
   trug die Zeilen von Anfang an, mit der Begründung „sonst springt `.plist` beim Zuklappen
   nach oben" — ungeprüft. Der `kvp`-Fund hat sie nicht erfunden, sondern **zitiert**: Er sah
   zwei Knöpfe, von denen einer ein Muster hatte und der andere nicht, und schloss auf einen
   Mangel. **Ein ungeprüfter Kommentar wird zur Quelle des nächsten Fundes.** Genau deshalb
   steht in `CLAUDE.md`, dass ein Kommentar, der die Absicht beschreibt, kein Beleg dafür ist,
   dass der Code sie umsetzt (siehe auch Punkt 108, `merge: true`).

---

## 117. Die 16-px-Regel gegen den iOS-Zoom griff im Querformat nicht

`CLAUDE.md` §26 verlangt 16 px für Eingabefelder, damit Safari beim Fokussieren nicht
hineinzoomt. Die Regel gab es auch — aber im Block `@media (max-width: 560px)`.

**Gemessen am 25.08.2026:** Bei 720 px Viewport hatte das Suchfeld des Meal-Pickers **14 px**.
Und 560 px ist keine sinnvolle Grenze für „Handy":

| Gerät | CSS-Breite quer |
|---|---|
| iPhone SE | 667 px |
| iPhone 15 | 852 px |
| iPhone 15 Pro Max | 932 px |
| iPad mini (hoch!) | 768 px |

**Jedes iPhone im Querformat und jedes iPad in jeder Lage** fiel aus der Regel heraus. Wer dort
ins Suchfeld tippte, bekam genau den Zoom, den der Kommentar darüber verhindern wollte.

**Die Bedingung war von Anfang an die falsche.** Nicht die Breite entscheidet, ob ein Gerät
zoomt, sondern der Zeigertyp. Ergänzt wurde deshalb ein `@media (pointer: coarse)`-Block mit
derselben Regel — dasselbe Merkmal, an dem im Projekt schon der Zahlen-Picker hängt. Die
560er-Fassung bleibt unangetastet: Sie schadet nicht, und Bestand wird nicht ohne Not angefasst.

Belegkette über `tools/cdp.py messen`:

| | Suchfeld |
|---|---|
| 720 px **mit** Touch | **16 px** — neue Regel greift |
| 720 px **ohne** Touch | 14 px — am Rechner ändert sich nichts |
| 560 px ohne Touch | 16 px — alte Regel greift weiter |

Die mittlere Zeile ist die eigentliche Gegenprobe. Ohne sie wäre nicht belegt, dass die Regel
am Zeigertyp hängt und nicht einfach immer gilt.

**Der neue `@media`-Block steht bewusst direkt hinter der schliessenden Klammer des
560er-Blocks**, nicht irgendwo dazwischen — siehe die Falle beim 680er-Block, die einmal die
ganze mobile Ansicht lahmgelegt hat.

## 118. Ein Guard, der nach innen wandert, erzeugt Datensätze ohne ein Feld, auf das anderswo still gebaut wird

**Der Fall (26.08.2026, live gepusht und noch am selben Abend repariert):** Paket 6 verlegte
den Ziel-Guard in `archiveWeek()` nach innen — vorher stieg die Funktion bei `!state.goal`
sofort aus, jetzt archiviert sie auch ohne Ziel. Gewollt: Wer ohne Ziel plant, soll trotzdem
eine Vergangenheit bekommen.

**Die Folge, die niemand mitgedacht hat:** Ab da entstehen Archivwochen **ohne `target`**.
Und `rueckblickHtml()` hatte für diesen Fall längst eine Rückfalllösung:

```js
const fallback = avgDailyTargetToday();
const target = s.target || fallback;      // misst gegen das HEUTIGE Ziel
```

Diese Zeile war vorher praktisch tot — ohne Ziel wurde ja gar nicht archiviert. Nach dem
Umbau lief sie regelmäßig und maß fremde Wochen am heutigen Ziel: **genau der Fehler, gegen
den Ziffer 74 seinerzeit gebaut wurde.** Dazu behauptete die Tippzeile „0 von 5 Tagen im
Ziel" für eine Woche, in der es kein Ziel gab — eine **falsche** Aussage, keine fehlende.

**Warum es niemandem sofort auffiel:** Der Rückblick zeigt ohne Ziel gar nichts
(`if (!state.goal) return "";`). Der Fehler wird erst in dem Moment sichtbar, in dem jemand
sein **erstes** Ziel setzt — also genau auf dem normalen Onboarding-Weg: erst ein paar
Wochen planen, dann das Ziel.

**Der Fix:** Zwei abgeleitete Listen aus einem Archiv. Der **Streak** läuft über alle Wochen
(er fragt nur „wurde geplant?"), die **Grafik** nur über Wochen mit eigenem `target`. Beide
Stellen sind ausdrücklich kommentiert, sonst legt sie jemand wieder zusammen.

**Die Lehre, die über diesen Fall hinausgeht:** Wenn ein Guard wandert, ändert sich nicht
nur, *ob* etwas passiert, sondern **welche Form die entstehenden Daten haben**. Jede Stelle,
die ein optionales Feld mit `||` auffängt, ist ab dann ein Kandidat: Der Rückfall war für
einen seltenen Sonderfall gedacht und wird plötzlich zum Normalfall.

**Beim nächsten Guard-Umbau also fragen:** Welche Felder fehlen den neu entstehenden
Datensätzen — und wer fängt dieses Fehlen heute mit einem Standardwert auf, der dann falsch
ist?

Gefunden hat es die Sitzung, die den Umbau gebaut hatte, beim Aufschreiben ihres eigenen
Wissens — nicht der Code-Review. Prüfstand: `tools/pruefstand-rueckblick-ziel.py`.

## 119. Ein Wächter, der die eigenen Werkzeuge blockiert — und `core.ignorecase` als stiller Mitwisser

**Gefunden am 27.08.2026** bei der ersten Nachprüfung des Setups, das am Vortag entstanden war.

Der Commit-Wächter (`.claude/hooks/commit-waechter.py`) führte `.claude/Skills/` als
verboten, mit der Begründung „zugekaufte Skill-Texte — fremde Inhalte ohne belegte Lizenz".
Richtig gedacht, nur liegen im **selben Ordner** die vier selbst geschriebenen
Projekt-Skills, seit dem Vortag getrackt:

```
.claude/Skills/smoke/SKILL.md   .claude/Skills/abnahme/SKILL.md
.claude/Skills/deploy/SKILL.md  .claude/Skills/pruefstand/SKILL.md
```

Die nächste Änderung an `/smoke` oder `/deploy` wäre am eigenen Hook gescheitert — mit einer
Meldung, die einen falschen Grund nennt. Behoben über eine `ERLAUBT`-Liste, die vor den
Verbotslisten greift.

**Warum es niemand gemerkt hat**, obwohl `tools/wartung-check.py` die Deckung zwischen
`.gitignore` und Wächter prüft: Die Prüfung fragte nur eine Richtung — *blockiert der
Wächter genug?* Nie: *blockiert er zu viel?* Beide Richtungen sind jetzt drin, und die
Gegenrichtung fragt den Wächter über seine neue Funktion `bewerte()` selbst, statt seine
Listen ein zweites Mal nachzubauen — zwei Kopien derselben Regel driften auseinander.

**Der stille Mitwisser.** Beim selben Fund fiel auf, dass `.gitignore` die eigenen Skills
nur in Kleinschreibung wieder freigab (`!.claude/skills/smoke/`), der echte Ordner aber
`Skills` heisst. Auf diesem Rechner fällt das nicht auf:

```
git config core.ignorecase   →  true
```

Damit trifft ein Muster in Kleinschreibung auch `Skills/`, und `git check-ignore` meldet die
Datei brav als sichtbar — die Prüfung in `pruefe_skills()` schwieg deshalb zu Recht. Auf
einem **case-sensitiven** Dateisystem — Linux, der CI-Runner, ein Mac mit APFS-Case — trifft
es nicht mehr: dann greift `.claude/Skills/*`, die Ausnahme in Kleinschreibung aber nicht,
und ein **neu angelegter** eigener Skill wäre dort stillschweigend ignoriert. Die vier
bestehenden überlebten nur, weil `.gitignore` auf bereits getrackte Dateien nicht mehr wirkt.
Beide Schreibweisen stehen jetzt in beiden Dateien.

**Die Lehre:** Eine Prüfung, die eine Regel nur in einer Richtung testet, ist eine halbe
Prüfung — und eine lokale Git-Einstellung kann eine kaputte Regel monatelang richtig
aussehen lassen. Hängt ein Muster an Gross-/Kleinschreibung, gehören beide Schreibweisen
hin, auch wenn „es hier funktioniert".

## 120. Eine Schutzregel, die von der Regel überholt wird, die sie schützen soll

**Gefunden am 27.08.2026**, beim Durchsehen der App nach dem Setup-Umbau.

`.grp-m select` — die Rollenwahl je Mitglied in der Gruppenverwaltung — stand auf 13 px.
Safari zoomt beim Öffnen eines `<select>` unter 16 px in die Seite hinein. Den Schutz dagegen
gibt es seit Fall 117:

```css
@media (pointer: coarse) {
  input…, select, textarea { font-size: 16px; }   /* Zeile 2516 */
}
…
.grp-m select { … font-size: 13px; … }            /* Zeile 3207 */
```

**Der Schutz greift trotzdem nicht**, und zwar aus zwei voneinander unabhängigen Gründen:
`.grp-m select` hat die höhere Spezifität (0,1,1 gegen 0,0,1) **und** steht weiter unten.
Jeder für sich würde schon reichen.

Das ist die eigentliche Lehre: **Eine Schutzregel mit niedriger Spezifität schützt nur, bis
jemand weiter unten spezifischer wird.** Sie sieht danach unverändert richtig aus — man liest
den `@media (pointer: coarse)`-Block, findet `select` darin und hakt ab. Fall 117 hat die
Bedingung repariert (Breite → Zeigertyp) und dabei diese zweite Bruchstelle nicht gesehen.

Behoben durch dieselbe Regel noch einmal, direkt hinter der Regel, die sie korrigiert. Der
Block steht **hinter** `.grp-m select` auf oberster Ebene, nicht in einem fremden `@media`-Block
— siehe die Falle mit dem zerschnittenen 680er-Block.

Belegt über `tools/pruefstand-grpm-zoom.py` (echtes CSS aus `index.html`, Touch-Emulation
über CDP):

| | `<select>` |
|---|---|
| mit Touch, CSS wie es ist | **16 px** — der Block greift |
| mit Touch, neuer Block entfernt | 13 px — **Gegenprobe**, ohne ihn fällt es zurück |
| ohne Touch, CSS wie es ist | 13 px — am Rechner ändert sich nichts |

Die mittlere Zeile ist die eigentliche Gegenprobe. Ohne sie wäre nur belegt, dass irgendwo
16 px stehen — nicht, dass dieser Block sie bewirkt.

**Wer die 16-px-Regel prüft, prüft ab jetzt nicht den Schutzblock, sondern das Ergebnis am
Element.** Alles andere ist eine Behauptung über die Kaskade.

## 121. Ein freundlicher Toast ist auch ein Schlucken

**Gefunden am 27.08.2026.** Der Fehlermelder `noteError` (Fall 29, `docs/ARCHITECTURES.md`)
wurde eingeführt, um **leere** `catch`-Blöcke zu beseitigen. Er übersah eine zweite Sorte, die
genauso blind macht:

```js
} catch (e) {
  leaveGroupState();
  toast("Die Gruppe ist gerade nicht erreichbar – du planst vorerst für dich.");
}
```

Der Nutzer ist freundlich informiert. Der Fehler ist **weg** — kein Log, keine Konsole, kein
`dump()`. „Nicht erreichbar" kann heißen: offline, falsche `gid`, fehlende Firestore-Regel,
entfernte Mitgliedschaft. Vier verschiedene Ursachen, eine Meldung, keine Möglichkeit zu
unterscheiden.

Ergänzt wurden `group:switch`, `sync:recipes` und `save:localStorage`. **Der Nutzen war sofort
messbar:** Beim ersten Lauf über `localhost` stand im `dump()`

```
tag: "group:switch"   msg: "Missing or insufficient permissions."
```

— ein Firestore-Regelfall, kein Netzproblem. Diese Unterscheidung war vorher aus der App heraus
nicht zu treffen.

**Die Lehre:** Beim Aufräumen von `catch`-Blöcken nicht nach `{}` suchen, sondern danach, ob
der Block den Fehler *irgendwohin* rettet. Ein Toast ist eine Nachricht an den Nutzer, keine
Diagnose — die beiden ersetzen einander nicht.

Bewusst **nicht** angefasst: rund 28 weitere `catch`-Blöcke, die in einen Toast übersetzen
(Teilen, PDF, Zwischenablage, Einladung laden). Dort ergibt sich die Ursache meist aus der
Aktion selbst, und Bestand wird nicht ohne Not umgebaut.

## 122. Ein Zähler, der beim Start wandert — und kein Fehler ist

**Beobachtet am 27.08.2026, live:** Der Meals-Zähler im Reiter lief nach dem Laden ohne jede
Nutzeraktion von 33 über 34, 33, 31 auf **28** und blieb dort. Das sieht aus, als verlöre man
Meals.

Nachgerechnet:

```
im localStorage:        36 Rezepte, 36 eindeutige IDs
davon quick (Barcode):   8
libraryRecipes():       36 − 8 = 28      ← genau der Zähler
```

`libraryRecipes()` filtert `quick !== true` — Barcode-Produkte zählen bewusst nicht als Meals.
Der Endstand **28 ist korrekt**, und die 36 im Speicher sind vollständig. Die Zwischenwerte sind
Momentaufnahmen, während Gruppen-Handshake, Remote-Events und die einmalige `dedupeV1`-Migration
konvergieren. Beim zweiten Laden misst man 21 Sekunden lang unverändert 28.

**Warum das hier steht, obwohl nichts kaputt ist:** Der Verlauf sieht exakt wie Datenverlust aus
und hat bei der Durchsicht Zeit gekostet. Wer ihn das nächste Mal sieht, rechnet zuerst
`gesamt − quick` und lädt ein zweites Mal, bevor er eine Sync-Fehlersuche beginnt.

Verbleibt als **UX-Beobachtung**, nicht als Bug: Für den Nutzer zappelt eine Zahl etwa eine
halbe Minute lang. Nicht geändert — der Eingriff (Zähler bis zum Handshake zurückhalten) hätte
mehr Fläche als Nutzen.

## 123. Eine Ausnahme, die vor den Verboten steht, hebelt sie alle aus

**Gefunden am 27.08.2026** vom Agenten `website-security` im `/pushcheck` — und zwar an Code,
der am selben Tag entstanden war, um Fall 119 zu beheben. Die Reparatur hatte ein neues Loch
gerissen.

`bewerte()` im Commit-Wächter prüfte die neue `ERLAUBT`-Liste **zuerst**:

```python
if any(pfad.startswith(e) for e in ERLAUBT):
    return None          # <- vor allen Verbotslisten
```

`ERLAUBT` ist ein reiner Verzeichnis-Präfixtest auf vier Skill-Ordner. Damit entschied der
**Ordnername allein** — was für eine Datei darin lag, spielte keine Rolle mehr:

```
.claude/Skills/smoke/.env                  -> durchgelassen
.claude/Skills/smoke/serviceAccount.json   -> durchgelassen
.claude/Skills/deploy/geheim.pem           -> durchgelassen
```

**Beim Gegenprüfen fiel ein zweiter, älterer Fehler auf**, der nichts mit der Ausnahme zu tun
hatte: `.env` stand nur in `VERBOTEN`, und das ist ein **Präfix**test gegen den Repo-Pfad. Er
griff also ausschliesslich auf `.env` im Wurzelverzeichnis:

```
docs/.env                                  -> durchgelassen   (seit es den Wächter gibt)
```

Für das eine echte Geheimnis des Projekts fiel damit eine der vier Schutzschichten aus, sobald
die Datei in einem Unterordner lag und jemand `git add -f` benutzte.

**Behoben durch die Reihenfolge:** harte Verbote (Endungen, Namensmuster) zuerst — sie gelten
überall, auch in einem `ERLAUBT`-Ordner —, danach die Ausnahme, danach die Präfixe. Dazu `.env`
und `.env.*` als **Namensmuster** statt als Präfix, damit sie in jedem Verzeichnis greifen.
13 Fälle als Gegenprobe, beide Richtungen.

**Die Lehre, und sie ist unangenehm allgemein:** Eine Ausnahme gehört ans **Ende** einer
Prüfkette, nicht an den Anfang. Steht sie oben, ist sie kein Sonderfall mehr, sondern ein
Generalschlüssel. Und: Wer eine Sicherheitsregel repariert, prüft die Reparatur mit derselben
Härte wie das Original — die Lücke hier war jünger als einen Tag und stand in Code, dessen
ausdrücklicher Zweck das Verhindern genau solcher Lücken ist.

**Warum es auffiel:** Weil `/pushcheck` gelaufen ist, bevor gepusht wurde. Der Wächter hätte
sich selbst nie gemeldet — er prüft den Index, nicht sich.

## 124. Ein Zustand ohne Wochenbezug neben zwei Wochenreitern

**Datum:** 28.08.2026 · **Betrifft:** Einkaufsliste, `localStorage["wochenkueche_shop_v1"]`

### Der Fehler

Die Einkaufsliste kennt zwei Wochen — der Umschalter über dem Plan hat die Reiter
**Aktuelle Woche** und **Nächste Woche**, und `buildShoppingList()` folgt ihnen korrekt: Die
Positionen und ihre Mengen wechseln mit. Der **abgehakte Zustand** folgte ihnen nicht. Er lag
als ein einziges flaches Set aus `norm`-Schlüsseln (`"hackfleisch|g"`) im `localStorage`, ohne
jeden Bezug darauf, für welche Woche gehakt worden war.

Zwei Folgen, beide fallen erst im Supermarkt auf:

1. **Der Haken färbte auf die andere Woche ab.** Wer in der aktuellen Woche „500 g Hackfleisch"
   abhakte und auf *Nächste Woche* umschaltete, fand die Position dort erledigt — obwohl die
   nächste Woche eine andere Menge braucht (`ab heute` gegen die volle Woche). Man kauft zu
   wenig ein und merkt es beim Kochen.
2. **Am Montag rückte der Zustand still nach.** Die neue Woche startete mit den Haken der
   vergangenen, weil „aktuell" kein Schlüssel war, sondern nur eine Sicht.

Dazu ein zweiter, kleinerer Fund an derselben Stelle: Der Kopf des Modals beschriftete die
nächste Woche als **„diese Woche"**. Der Ausdruck

```js
state.viewWeek !== "next" && todayIdx > 0 ? "ab heute" : "diese Woche"
```

fällt für `viewWeek === "next"` in den zweiten Zweig — der `else`-Fall trug die Beschriftung
eines Falls, den er auch bedient. Dasselbe stand im Vorkoch-Modal, aus derselben kopierten
Zeile.

### Warum es so lange niemandem auffiel

**Weil die Liste selbst immer richtig war.** Positionen, Mengen, Warengruppen, PDF, Text und
Teilen folgten dem Reiter sauber — `shopPdfString()` schrieb sogar korrekt „Nächste Woche" in
den PDF-Kopf. Wer die Liste ansah, sah eine funktionierende Einkaufsliste. Falsch war nur die
eine Ebene darüber, die man beim Ansehen nicht sieht: welcher Woche ein Häkchen *gehört*.

Das PDF ist dabei der Beleg, dass die Kopfbeschriftung ein Versehen war und keine Absicht — an
zwei Stellen wurde dieselbe Frage beantwortet, einmal richtig und einmal falsch.

### Die Regel dahinter

> **Wenn eine Ansicht zwei Zeiträume hat, muss jeder Zustand, den der Nutzer darin erzeugt,
> sagen können, zu welchem er gehört.** Sonst gehört er stillschweigend beiden.

Das gilt nicht nur für Häkchen. Jeder künftige Zustand neben dem Wochenumschalter — eine
Sortierung, eine Filterung, ein „erledigt", ein Notizfeld — steht vor derselben Frage. Wird sie
nicht gestellt, lautet die Antwort per Vorgabe „beiden", und das fällt niemandem auf, solange
man nur eine Woche benutzt.

### Die Lösung

Der Speicher ist nach ISO-Wochenschlüssel gegliedert — **demselben**, unter dem schon
`state.plans` liegt:

```json
{ "2026-W35": ["hackfleisch|g"], "2026-W36": ["milch|ml"] }
```

Dass es derselbe Schlüssel ist und kein eigener („cur"/„next"), erledigt den zweiten Teil des
Fehlers von selbst: Die Haken der nächsten Woche **wandern beim Wochenwechsel mit**, weil ihr
Schlüssel sich nicht ändert — die Woche heißt am Montag nur nicht mehr „nächste". Ein eigenes
Schema hätte hier eine Rotationslogik gebraucht, also genau die Stelle, an der der Fehler
wieder entstünde.

`saveShopDone()` behält nur `cur` und `next` — dieselbe Regel wie `pruneWeeks()`. Ein flaches
Array aus der Fassung davor wird als Bestand der aktuellen Woche übernommen, nicht verworfen:
Wegwerfen wäre bequemer und hätte jedem Nutzer beim Update seinen halb abgehakten Einkauf
gelöscht.

Die Beschriftung liegt jetzt in `planScopeLabel(todayIdx)` — eine Quelle für Einkaufsliste
**und** Vorkochliste, als Gegenstück zu `planDaysAhead()`, das ihre Tage liefert. Zwei
Funktionen, die dieselbe Woche beschreiben, sollen sie auch gemeinsam benennen; als zwei Kopien
derselben Zeile war das Auseinanderlaufen nur eine Frage der Zeit — und war ja bereits
eingetreten.

### Der Nachzug am selben Tag: dieselbe Lüge stand noch im PDF

Der erste Fix ließ **`shopPdfString()` unberührt** — und die Dokumentation behauptete danach,
`planScopeLabel()` sei „eine Quelle für Einkaufsliste und Vorkochliste". Das PDF baute seinen
Zeitraum weiter selbst:

```js
const scope = state.viewWeek === "next" ? "Nächste Woche" : "Diese Woche";
```

Das nennt die richtige Woche und verschweigt das `ab heute`. Das PDF trug also „Diese Woche"
über einer Liste, die nur die restlichen Tage enthält — **derselbe Fehlertyp wie im
Modal-Kopf, nur andersherum**, und im Ausdruck sogar folgenreicher: Auf Papier gibt es keinen
Reiter, an dem man es merken könnte.

Gefunden hat das der Agent `kvp` bei der nachträglichen Prüfung. Die Lehre ist unbequem:
**Ich hatte die Einheitlichkeit dokumentiert, bevor ich sie hergestellt hatte.** Genau die
Behauptung im Fließtext war es, an der der Widerspruch auffiel — hätte die Doku
zurückhaltender formuliert, wäre das PDF stillschweigend falsch geblieben.

### Zwei bewusste Grenzen, damit sie nicht als Fehler gelesen werden

* **Der Haken kennt die Menge nicht.** `norm` ist Name + Einheit ohne Menge; ein Haken
  überlebt deshalb eine geänderte Personenzahl — aber auch ein *nachträglich eingeplantes*
  Gericht mit derselben Zutat. Kehrseite derselben Entscheidung, nicht ein Versehen.
  Begründung und der Weg, es doch zu lösen: `docs/ARCHITECTURES.md`.
* **Der Zustand geht nicht in die Cloud.** Ein geteilter Haken hieße in der Gruppe „jemand hat
  es geholt" — eine Aussage, die niemand getroffen hat.

### Prüfstand

`tools/pruefstand-einkaufsliste.py` — 49 Prüfungen in fünf Läufen. Gegen den Stand *vor* dem
ersten Fix **11 Fehler**, gegen den Stand *nach* dem ersten Fix (Commit `7f48cd7`) noch
**5** — die Dialognamen, das Komma und der PDF-Kopf. Details: `docs/TESTING.md`.

## 125. Gruppe verlassen: der Altbestand kam als Dublette zurück

**Datum:** 28.08.2026 · **Betrifft:** `leaveGroup()`, `startCloudSync()`, `users/{uid}/recipes`

### Der Befund

Am echten Konto gemessen, nicht vermutet: **43 Meals in der Gruppe, 81 im eigenen Konto,
14 doppelte `lib`** — einzelne bis zu **dreifach**. Die Gruppe selbst war sauber: keine
doppelte `lib`, nur zwei gleichnamige, inhaltlich verschiedene Meals von zwei Personen
(„Banane" als Barcode-Schnelleintrag neben einem echten Meal, „Steak mit Kartoffeln" einmal
als Hauptgericht und einmal als Frühstück). Der Abgleich in `copyOwnRecipesToGroup()` tut also
genau das, was Ziffer 102 zusagt.

Die Dubletten entstanden auf dem **Rückweg**.

### Die Ursachenkette

1. Beim Beitritt wandert der eigene Bestand in die Gruppe (`copyOwnRecipesToGroup()`) und wird
   **lokal ersetzt** (`enterGroupSync()`: „in einer Gruppe ist die Gruppe die Wahrheit").
   In `users/{uid}/recipes` bleibt er dabei unangetastet liegen — dorthin schreibt in einer
   Gruppe niemand mehr, `recipeBase()` zeigt auf `["groups", gid]`.
2. `leaveGroup()` setzte `lastPushedRecipes = new Map()`, mit der Begründung „damit der
   nächste Zyklus alle Meals als neu ins eigene Konto schreibt — dort liegen sie ja noch
   nicht". **Beide Hälften des Satzes waren falsch.** Sie liegen dort noch, und eine leere
   Baseline schreibt zwar alles, **löscht aber nichts**: `syncRecipes()` bildet `delIds` aus
   `prev ohne cur` — was nie in der Baseline stand, wird nie gelöscht.
3. `switchGroup(null)` → `startCloudSync()` liest im Zweig „keine Gruppe"
   `users/{uid}/recipes` und mischt den Altbestand über `mergeRemoteRecipes()` unter die
   mitgebrachten Gruppen-Meals. Beide Fassungen tragen dieselbe `lib`, aber eigene IDs —
   `mergeRemoteRecipes()` vereinigt über die **ID** und sieht deshalb keinen Konflikt.
4. Der folgende `pushNow()` schreibt die Vereinigung zurück. **Jeder weitere Beitritt und
   Austritt legt eine Lage obendrauf** — daher die Dreifachen.

Die Rechnung geht exakt auf: 43 mitgebrachte + 38 Karteileichen = 81.

### Die Behebung

`pruneOwnRecipes(behalten)` neben `copyOwnRecipesToGroup()` — das Gegenstück zum Beitritt:
Es liest `users/{uid}/recipes` und löscht, was der mitgebrachte Stand nicht mehr enthält.
`leaveGroup()` ruft es nach dem Zurückschreiben auf, `dissolveGroup()` über denselben Weg mit.

Vier Dinge daran sind keine Details:

* **Nur-Leser ausgenommen.** `joinGroup()` kopiert für `role === "view"` nichts in die Gruppe;
  dort ist das eigene Konto die **einzige** Kopie. `warNurLeser` wird **vor**
  `leaveGroupState()` gelesen — das räumt `myRole` weg.
* **Ein leerer Behalten-Stand räumt nichts.** Das ist kein Auftrag zum Leerräumen, sondern das
  Warnzeichen aus Ziffer 101: der Snapshot wurde zu spät gezogen.
* **Kür, nicht Pflicht.** Scheitert Lesen oder Löschen, bleibt es beim alten Verhalten
  (Dubletten). Dieselbe Abwägung wie beim Abgleich im Beitrittspfad (Ziffer 102): ein
  abgebrochener Austritt wäre schlimmer als ein doppelter Eintrag.
* **Ein Lesefehler löscht nie.** `loadRecipes()` liefert offline das leere Cache-Ergebnis,
  ohne zu werfen — deshalb kann ein Fehlschlag hier nur *zu wenig* löschen, nie zu viel.

### Nachtrag am selben Tag: die erste Fassung löschte zu viel

Der Push-Check hat einen Gegenfall gefunden, den die erste Fassung nicht überlebt hätte. Sie
löschte pauschal **alles**, was nicht im mitgebrachten Gruppenstand lag, gestützt auf die
Annahme: „Mein Bestand ist beim Beitritt vollständig in die Gruppe gewandert."

**Die Annahme ist falsch.** `joinGroup()` kopiert für `role === "view"` ausdrücklich nichts
(`if (role !== "view")`) — und der Inhaber kann ein Mitglied über `setRole()` jederzeit von
„Nur ansehen" auf „Mitplanen" heben. Beim Verlassen ist `warNurLeser` dann **false**, und die
pauschale Fassung hätte den **gesamten** eigenen Bestand gelöscht: Meals, die nie eine Kopie
in der Gruppe hatten.

**Die schärfere Regel:** Gelöscht wird nur, was nachweislich eine Dublette ist — ein Meal,
dessen `lib` im mitgebrachten Gruppenstand bereits vertreten ist. Das ist exakt dieselbe
Frage, die `copyOwnRecipesToGroup()` auf dem Hinweg stellt, nur in die andere Richtung:

> **Was der Beitritt wegen gleicher `lib` nicht hochgeladen hat, räumt der Austritt weg.
> Alles andere bleibt.**

Meals ohne `lib` (selbst angelegte) bleiben damit immer stehen — dieselbe Grenze wie beim
Beitritt, wo ein Namensabgleich fremde Meals verschlucken würde („Banane" darf es zweimal
geben, Ziffer 102). Die Rollen-Ausnahme `warNurLeser` bleibt zusätzlich bestehen; zwei
unabhängige Riegel sind hier billiger als ein verlorener Bestand.

Der Preis ist ehrlich zu benennen: Leftovers **ohne** `lib`-Gegenstück werden nicht mehr
aufgeräumt und wandern beim nächsten Start wieder in den Bestand. Sie sind aber auch keine
Dubletten — es sind Meals, die es nur einmal gibt. **Ein Meal ohne Gegenstück darf dieser
Weg unter keinen Umständen anfassen.**

### Zweiter Nachtrag: die verschärfte Regel löste das Problem nicht

Die Fassung aus dem ersten Nachtrag — „lösche nur, was eine `lib` trägt, die im Gruppenstand
vertreten ist" — ist **gegen die echten Daten gerechnet worden** und dabei durchgefallen.

Gemessen am Konto vom 28.08.2026 (81 eigene Meals, 44 in der Gruppe, rein lesend simuliert):

| Regel | löscht | Bestand danach | größte `lib`-Häufung |
|---|---|---|---|
| gar nicht aufräumen | 0 | 81 | **3** |
| pauschal (erste Fassung) | 37 | 44 | 1 — aber 1 Meal **ohne Gegenstück** dabei |
| `lib` in der Gruppe (zweite Fassung) | 9 | 72 | **2** — Dubletten bleiben |
| je `lib` einer (jetzige Fassung) | 17 | 64 | **1**, und 0 ohne Gegenstück |

**Warum die zweite Fassung nicht griff:** Von 37 Altbeständen lagen **11 als Paare
untereinander** — und **8 davon** trugen eine `lib`, die die Gruppe gar nicht kennt. Die
Frage „ist diese `lib` in der Gruppe?" ging an diesen Paaren vorbei. Die Regel war sicher,
aber sie löste das gemeldete Problem nicht.

**Die jetzige Regel zählt je `lib` mit:** Der erste bleibt, jeder weitere geht — der aus dem
mitgebrachten Gruppenstand hat Vorrang. Damit ist ein Meal, dessen `lib` nur **einmal**
vorkommt, strukturell unantastbar; die Ausnahme für Nur-Leser aus dem ersten Nachtrag bleibt
zusätzlich bestehen. Sortiert nach `id`, damit zwei Geräte unabhängig voneinander dieselbe
Kopie behalten (dieselbe Überlegung wie bei `memberColorSlot()`).

### Die Lehre, und sie ist die unangenehmste des Tages

> **Ein Prüfstand mit selbst erfundenen Daten prüft die Regel, die man im Kopf hatte — nicht
> die Wirklichkeit, für die sie gedacht war.**

Die synthetischen Testdaten bildeten den Fall ab, den ich mir vorgestellt hatte: eigene
Kopien, deren Gegenstück in der Gruppe liegt. Der häufigste Fall am echten Konto war ein
anderer: Paare, die *nur* im eigenen Bestand liegen, aus mehreren Beitritts-Zyklen. Beide
Fassungen waren grün — die zweite über zwei Commits hinweg, mit Gegenprobe.

Gefunden hat es erst die Rechnung gegen die 81 echten Dokumente. Der Prüfstand trägt den Fall
jetzt nach (Abschnitt 3c).

### Die Regel dahinter

> **Eine geleerte Baseline ist keine Aufräumung.** Sie sagt „ich weiß nichts über den
> Zielzustand", und ein Diff gegen Nichtwissen schreibt alles und löscht nichts. Wer wirklich
> aufräumen will, muss den Zielzustand **lesen** und die Differenz ausdrücklich löschen.

Und allgemeiner, als Gegenstück zu Ziffer 102: **Wer einen Bestand an einen anderen Ort
kopiert und lokal ersetzt, schuldet den Rückweg.** Der Hinweg war gebaut und geprüft, der
Rückweg nie — und er ist die Stelle, an der sich der Fehler mit jedem Durchlauf verstärkt.

### Prüfstand

`tools/pruefstand-gruppe-verlassen-dubletten.py` — 23 Prüfungen mit echtem, ausgeschnittenem
Code (`pruneOwnRecipes()`, `syncRecipes()`, `mergeRemoteRecipes()`) gegen ein falsches
Firestore mit zwei Sammlungen. Die **Gegenprobe** fährt denselben Ablauf ohne
`pruneOwnRecipes()` und muss rot werden: Sie liefert **12 statt 7 Meals**, `lib`-Zählung 2,
und wächst mit jedem weiteren Zyklus — dasselbe Muster wie am echten Konto.

Abschnitt 3b sichert den Nachtrag oben ab (Meal ohne `lib` und Meal mit unbekannter `lib`
überleben, die echten Dubletten verschwinden trotzdem), Abschnitt 7b ist seine Gegenprobe:
die pauschale Fassung löscht das Meal ohne Gegenstück. Ohne 7b misst 3b nichts.

## 126. Ein leeres Leseergebnis, das eine Entscheidung trägt

**Datum:** 28.08.2026 · **Betrifft:** `copyOwnRecipesToGroup()`, `CloudSync.loadRecipes()`

### Der Fehler

Der Dubletten-Abgleich beim Gruppenbeitritt (Ziffer 102) entscheidet anhand eines **leeren**
Leseergebnisses: „Die Gruppe kennt diese `lib` noch nicht, also lade ich meine Kopie hoch."

Gelesen wurde mit `getDocs()` — und seit dem `persistentLocalCache` **wirft das offline nicht
mehr**, sondern liefert stillschweigend das leere Cache-Ergebnis. Die Rezepte einer Gruppe,
der man **gerade erst** beigetreten ist, hat dieser Cache aber noch **nie** gesehen. „Die
Gruppe hat noch keine Meals" und „ich weiß es nicht" sahen damit identisch aus.

Fiel der Abgleich so aus, ging **jedes** eigene Meal hoch. Da `STARTER` je Ernährungsform
fest verdrahtet ist, sind das bei zwei Konten mit gleichem Profil garantiert **fünf Paare** —
exakt der Zustand, den Ziffer 102 beseitigt hatte. Die Reparatur von damals war also nicht
falsch, sie war nur an genau dem Punkt blind, an dem sie gebraucht wird.

Das ist dieselbe Fehlerklasse wie bei `CloudGroup.fetch()` („`fromCache` ist kein Beweis") —
hier aber **ohne den Ausweg über ein Flag: ein leeres Array trägt keine Herkunft.**

### Die Behebung

`CloudSync.loadRecipesFromServer()` über `getDocsFromServer()`. Diese Funktion **wirft**
offline, und das ist hier die gewünschte Eigenschaft: Der Aufrufer kann „leer" endlich von
„unbekannt" unterscheiden. `copyOwnRecipesToGroup()` liest darüber, fängt den Wurf ab und
fällt auf das bisherige Verhalten zurück (alles hochladen) — Kür, nicht Pflicht, unverändert
zu Ziffer 102: ein abgebrochener Beitritt wäre schlimmer als ein paar Dubletten.

Der Aufruf geht bewusst über `window.CloudSync.loadRecipesFromServer || …loadRecipes`. Der
Service Worker kann eine ältere Fassung des Moduls ausliefern; dann bleibt es beim alten Weg,
statt an einer fehlenden Funktion zu scheitern.

### Die Regel dahinter

> **Wo ein leeres Leseergebnis eine Entscheidung trägt, ist ein Cache-Lesevorgang das falsche
> Werkzeug.** Nicht weil er falsch antwortet, sondern weil er nicht sagen kann, ob er
> überhaupt geantwortet hat.

Der Prüfpunkt für jede künftige Stelle: *Was tue ich, wenn hier nichts zurückkommt?* Lautet
die Antwort „nichts" oder „weniger", ist der Cache in Ordnung — ein Fehlschlag kann dann nur
zu wenig bewirken (so bei `pruneOwnRecipes()`, Ziffer 125). Lautet sie „dann schreibe ich",
muss vom Server gelesen werden.

### Prüfstand

`tools/pruefstand-gruppe-beitritt-cache.py` — 18 Prüfungen mit ausgeschnittenem
`copyOwnRecipesToGroup()` gegen ein falsches Firestore, dessen Cache **genau so lügt wie in
echt**: Sammlungen, die er noch nie vom Server geladen hat, liefert er als leeres Array
zurück, ohne zu werfen.

Zwei Gegenproben statt einer, und die zweite ist die wichtigere: Abschnitt 7 zeigt, dass die
alte Fassung beim **kalten** Cache durchfällt (12 statt 7 Meals, `lib`-Zählung 2, nichts
umgebogen). Abschnitt 8 zeigt, dass dieselbe alte Fassung beim **warmen** Cache heil ist.
Ohne den zweiten Beleg misst Abschnitt 7 nur „die alte Fassung ist irgendwie kaputt" statt
der Cache-Ursache.

## 127. Ein zugewiesenes Meal ließ sich nicht aus dem Plan löschen

**Datum:** 28.08.2026 · **Betrifft:** `dropRecipeIds()`, Gerichte-Zuweisung, Gruppen-Sync

### Der Fehler

Seit „Gemeinsam planen" ist ein Slot-Eintrag **zweierlei**: ein blanker String (Rezept-ID,
„für alle") **oder** ein Objekt `{id, uids}`, wenn nur ein Teil der Gruppe das Gericht isst.
`dropRecipeIds()` filterte gegen den **rohen** Eintrag:

```js
p[d.key][m.key] = asIdList(p[d.key][m.key]).filter(x => !idSet.has(x));
```

`idSet` enthält ID-**Strings**. Für ein Objekt trifft `idSet.has(x)` deshalb **nie** zu. Ein
gelöschtes Meal verschwand sauber, solange es „für alle" geplant war — war es **jemandem
zugewiesen**, blieb es als Geisterverweis im Wochenplan stehen.

Drei Wege führen in diese Funktion, und alle drei sind in der Gruppe der Normalfall:

| Weg | Wann |
|---|---|
| `deleteRecipe()` | ich lösche selbst |
| `onRecipesRemote()`, `"removed"` | ein anderes Mitglied löscht |
| `startCloudSync()` | Grabsteine beim Anmelden |

Der zweite ist der unangenehmste: Löscht die andere Person ein Meal, das mir zugewiesen war,
bleibt es bei mir stehen — und `pushGroupPlan()` schreibt den Geisterverweis anschließend
zurück in das gemeinsame Wochendokument.

**Selbstheilend, aber nicht folgenlos.** `normalizePlan()` filtert über `entryId(e)` gegen die
bekannten IDs und wirft den Verweis beim nächsten *Laden* weg. Bis dahin steht er in der
Ansicht, in der Einkaufsliste und im gemeinsamen Plan.

### Was den Fund erst möglich machte

Der direkte Nachbar `rewritePlanIds()` macht es **seit jeher richtig** (`entryId(e)`) — und
sein Kommentar nennt `dropRecipeIds()` ausdrücklich sein „Vorbild, nur ersetzen statt
entfernen". Das Vorbild war die kaputte Fassung. Zwei Funktionen, die dieselbe Menge treffen
müssen, standen zwanzig Zeilen auseinander und taten es nicht.

`dropRecipeIds()` ist älter als das `{id, uids}`-Format. Beim Einbau der Zuweisung wurden
`normalizePlan()`, `flattenWeek()`, `buildShoppingList()` und `dayNutOf()` auf `entryId()`
umgestellt — diese eine Stelle nicht.

### Die Regel dahinter

> **Wenn ein Datenmodell eine zweite Form bekommt, ist die Liste der Stellen, die es lesen,
> nicht die Liste der Stellen, die es anfassen.** Gesucht werden muss nach jeder Stelle, die
> einen Eintrag *vergleicht* — auch dort, wo er nur wegsortiert wird.

Praktisch: Nach `asIdList(...)` darf kein `.filter`, `.indexOf`, `.includes` oder `.has` mehr
auf den rohen Eintrag zeigen. `state.favs` und `state.planned` in derselben Funktion sind
davon **nicht** betroffen — das sind reine ID-Sammlungen ohne Zuweisungsform.

### Prüfstand

`tools/pruefstand-zuweisung-loeschen.py` — 20 Prüfungen mit ausgeschnittenem
`dropRecipeIds()` **und** `rewritePlanIds()`. Die Testwoche enthält alle Formen: „für alle",
„nur ich", „nur die andere Person", beide-als-Objekt und einen gemischten Slot.

Abschnitt 6 prüft die beiden Funktionen **gegeneinander**: Was `rewritePlanIds()` umbiegt,
muss `dropRecipeIds()` auch löschen können. Genau diese Symmetrie war verletzt.

Die Gegenprobe (Abschnitt 8) fährt die alte Filterfassung: Sie lässt **4 von 5** Verweisen
stehen und entfernt nur die „für alle"-Form. Dazu die zweite Gegenprobe — ohne Zuweisungen
war die alte Fassung in Ordnung, die Ursache ist also die Eintragsform und nicht irgendein
anderer Defekt.

## 128. Der Beitretende verlor seine Woche — und eine Migration räumte fremden Bestand auf

**Datum:** 28.08.2026 · **Betrifft:** `joinGroup()`, `finalizeGroupActivation()`,
`dedupeAgainstCatalog()`

Zwei Funde aus derselben Durchsicht, beide vom Inhaber abgenommen.

### A. Die Woche des Beitretenden ging lautlos verloren

`enterGroupSync()` **ersetzt** `state.plans` durch den Gruppenplan — dieselbe Begründung wie
bei den Meals: In einer Gruppe ist die Gruppe die Wahrheit. Hochgeladen wurde der eigene Plan
aber **nur beim Owner** (`prepareGroup()`, `finalizeGroupActivation()`). Wer beitrat, verlor
seine geplante Woche ohne Meldung.

**Dass das nicht so gemeint war, stand im Code selbst.** `copyOwnRecipesToGroup()` biegt die
Planverweise des Beitretenden auf die Gruppen-IDs um und begründet das wörtlich mit „vor dem
Hochladen des Plans (siehe `prepareGroup()`/**den Beitrittspfad**)". Auf dem Beitrittspfad
wurde nie ein Plan hochgeladen — die Umschreibung lief dort ins Leere. Ein Kommentar, der
einen Schritt beschreibt, den es nicht gibt, ist der zuverlässigste Hinweis auf eine
vergessene Hälfte.

**Behoben** über `mergeOwnPlanIntoGroup(gid)` — **eine** Funktion für beide Aufrufer, statt
zweier Kopien, die auseinanderlaufen. Nachgetragen werden nur Slots, die in der Gruppe **noch
leer** sind; wer schon geplant hat, behält seinen Eintrag. Das ist exakt die Owner-Regel aus
`finalizeGroupActivation()`, jetzt für beide Seiten.

Die Reihenfolge ist zwingend: **erst** `copyOwnRecipesToGroup()` (biegt die Verweise um),
**dann** der Plan. Umgekehrt zeigten die nachgetragenen Slots auf IDs, die es in der Gruppe
nicht gibt, und `normalizePlan()` würfe sie beim nächsten Laden lautlos weg.

**Und derselbe Cache-Fallstrick wie in Ziffer 126:** Auch hier trägt ein leeres Leseergebnis
eine Entscheidung („der Slot ist frei, ich schreibe hinein"), und der Offline-Cache hat die
Pläne einer gerade erst beigetretenen Gruppe noch nie gesehen. Deshalb
`CloudGroup.loadPlansFromServer()`. Scheitert das Lesen, wird **nichts** geschrieben — ein
nicht nachgetragener Plan ist ein Ärgernis, ein überschriebener fremder ein Datenverlust.
Das ist bewusst **strenger** als beim Meal-Abgleich nebenan: Dort ist der Schaden eine
Dublette, hier wäre er die gelöschte Woche der anderen Person.

Diese Hälfte war auch in `finalizeGroupActivation()` schon latent falsch — der Owner konnte
beim Aktivieren mit kaltem Cache die Slots überschreiben, die der Beitretende gerade gefüllt
hatte. Der gemeinsame Helfer behebt beide Stellen auf einmal.

### B. `dedupeAgainstCatalog()` räumte den gemeinsamen Bestand auf

Die Migration lief bisher auch **in** einer Gruppe, sobald der Handshake stand
(`if (syncGid && !syncHandshakeOk) return;`). Zwei Gründe sprechen dagegen, und beide
entstehen erst durch das Steuerflag selbst:

1. **`state.dedupeV1` steht nur im `localStorage`**, nicht im Kontodokument (`dataJSON()`
   führt es nicht). Es ist damit ein **Geräte**-Flag, kein Konto-Flag. In der Gruppe räumt die
   Migration aber nicht den eigenen Bestand auf, sondern den **gemeinsamen** — und ein zweites
   Gerät, ein anderer Browser oder ein geleerter Speicher lässt sie erneut darauf los.
   „Einmalig" gilt pro Gerät, „gemeinsam" gilt für alle.
2. **Eine Löschreihenfolge, die andere Mitglieder trifft.** Die Migration löscht Meals *und*
   biegt Planverweise auf die Katalog-ID um. `pushNow()` schreibt die Löschung **vor** dem
   Plan (`syncRecipes()` vor `pushGroupPlan()`). Das andere Gerät sieht also zuerst das
   `"removed"` — `dropRecipeIds()` leert dort die Slots — und erst danach den umgebogenen
   Plan. Ein eigener `save()` dazwischen schreibt die geleerten Slots zurück: Gerichte fallen
   aus dem gemeinsamen Plan.

**Behoben:** `if (syncGid) return;` — ohne das Flag zu setzen. Nichts geht verloren: Wer die
Gruppe verlässt, läuft über `switchGroup(null)` → `startCloudSync()` sofort wieder hier durch,
dann auf dem eigenen Bestand, wo die Migration hingehört. Die Gruppe selbst ist beim Beitritt
ohnehin über `lib` abgeglichen (`copyOwnRecipesToGroup()`).

### Die Regel dahinter

> **Ein Aufräumschritt, dessen „erledigt"-Merker lokal liegt, darf nur lokale Daten
> anfassen.** Sobald er auf gemeinsame Daten zeigt, ist er nicht mehr einmalig — er ist
> einmalig *pro Gerät*, und das ist etwas völlig anderes.

### Prüfstand

`tools/pruefstand-gruppe-plan-mitbringen.py` — 23 Prüfungen über beide Änderungen, mit
ausgeschnittenem `mergeOwnPlanIntoGroup()` und `dedupeAgainstCatalog()`.

Zwei Gegenproben: **A** zeigt, dass der Cache-Weg beim kalten Cache den fremden Slot
überschreibt (und beim warmen heil ist — die Ursache ist also der Cache-Zustand). **B** baut
die alte Bedingung `syncGid && !syncHandshakeOk` nach und belegt, dass sie mitten im
Gruppenbestand gelöscht hätte. Ohne B misst Abschnitt 9 nichts.

## 129. „Synchronisiert", während nichts mehr ankam

**Datum:** 28.08.2026 · **Betrifft:** `CloudSync.watch`/`watchRecipes`, `CloudGroup.watch`/`watchPlans`/`watchMembers`, `setSyncStatus()`

### Der Befund

Am echten Konto gemessen, nicht vermutet: Der Sync-Punkt zeigte **„Cloud-Sync:
Synchronisiert"**, während dieselbe App-Instanz weder lesen noch schreiben konnte — jeder
Server-Zugriff endete in `permission-denied`, ein Schreibvorgang hing ohne Bestätigung. Eine
unabhängig erzeugte SDK-Instanz mit denselben Zugangsdaten las im selben Moment fehlerfrei.

Die Anzeige log also. Und zwar in genau der Richtung, die am teuersten ist: Sie versprach
Sicherheit.

**Die Ursache des `permission-denied` selbst ist inzwischen gefunden:** ein vergifteter
Offline-Cache, siehe Ziffer 134. Das entwertet diese Ziffer nicht — im Gegenteil: Ohne die
ehrliche Statusanzeige wäre der Zustand weiterhin unsichtbar geblieben.

### Die Ursache

Vier `onSnapshot`-Aufrufe trugen ein leeres `function () {}` als Fehlerbehandlung:

| Listener | was er trägt |
|---|---|
| `CloudSync.watch` | das Kontodokument |
| `CloudSync.watchRecipes` | alle Meals |
| `CloudGroup.watch` | das Gruppendokument |
| `CloudGroup.watchPlans` | den gemeinsamen Wochenplan |

Entscheidend ist eine Eigenschaft von Firestore, die man kennen muss: **Ein `onSnapshot`, der
mit einem Fehler endet, wird endgültig beendet.** Er versucht es nicht erneut. Der Listener ist
danach tot — und mit dem leeren Handler erfuhr das niemand.

`setSyncStatus("synced")` steht am Ende von `startCloudSync()`. Danach nahm es nichts mehr
zurück: Ein Lesefehler hatte keinen Weg zur Anzeige, und der Push-Pfad (`pushNow()`) meldet nur
seine *eigenen* Fehlschläge. Der Status blieb auf „synced", bis jemand die Seite neu lud.

`CloudGroup.watchMembers` war die einzige Ausnahme — sie meldete Lesefehler schon vorher als
`null` statt als leere Liste (Ziffer 105). Genau das hätten die anderen vier auch gebraucht.

### Die Behebung

Ein gemeinsamer Melder `watchFehler(kennung)` im Firebase-Modul, den alle fünf Listener tragen.
Er tut zwei Dinge und nichts weiter:

1. `noteError(kennung, e)` — gedrosselt auf drei je Kennung, also auch bei einem dauerhaft
   feuernden Fehler kein Fluten des Ringpuffers.
2. Durchreichen an `window.__onCloudWatchError`, dieselbe Brücken-Bauart wie
   `window.__onCloudAuth`. Die App setzt daraufhin `setSyncStatus("offline")` und meldet
   **einmal je Sitzung** freundlich, dass Änderungen auf diesem Gerät bleiben.

Drei Entscheidungen, die keine Details sind:

* **Kein automatisches Neuanhängen.** Ein Listener, der an einer Regel scheitert, scheitert
  beim nächsten Versuch genauso — eine Wiederanhänge-Schleife wäre Dauerfeuer gegen Firestore.
* **Ein Hinweis, nicht vier.** Greift eine Regel, scheitern alle Listener im selben Moment.
  `watchAbgerissen` sperrt nach dem ersten; `stopCloudSync()` setzt es zurück, damit die
  nächste Sitzung wieder melden darf. Das Flag steht bei den übrigen Sync-Flags und nicht
  neben seinem Verwender — `stopCloudSync()` räumt es mit auf und stünde sonst **vor** der
  `let`-Deklaration.
* **„offline", kein fünfter Status.** Für den Nutzer ist die Lage dieselbe: Die App läuft
  lokal weiter, der nächste Start verbindet neu. Ein eigener Zustand bräuchte ein eigenes
  Symbol und eine eigene Erklärung, ohne dass sich die Handlung ändert.

### Die Regel dahinter

> **Eine Statusanzeige, die nur den Erfolgsfall kennt, ist keine Anzeige, sondern eine
> Behauptung.** Wer einen Zustand setzt, muss sagen können, was ihn wieder aufhebt — sonst
> bleibt er stehen, gerade wenn er nicht mehr stimmt.

Das ist dieselbe Familie wie Ziffer 29 (leere `catch`-Blöcke) und Ziffer 121 (ein freundlicher
Toast ist auch ein Schlucken) — hier aber eine Stufe teurer: Dort ging eine *Ursache*
verloren, hier ging die Information verloren, dass überhaupt etwas nicht stimmt.

### Prüfstand

`tools/pruefstand-sync-abriss.py` — 22 Prüfungen mit ausgeschnittenem `watchFehler()`,
`setSyncStatus()` und `__onCloudWatchError`, gegen eine `onSnapshot`-Attrappe, die auf
Kommando den Fehlerpfad nimmt.

Die eigentliche Messgröße steht in Abschnitt 2: **vier gleichzeitige Abrisse, vier
Protokolleinträge, aber genau ein Hinweis.** Dazu Abschnitt 4 (nach `stopCloudSync()` darf die
nächste Sitzung wieder melden) und Abschnitt 5/6 (der Melder wirft nie — auch nicht, wenn die
App-Seite wirft oder ganz fehlt).

Zwei Gegenproben: Abschnitt 8 fährt die alte Fassung mit dem leeren `function () {}` und
verlangt, dass der Status auf „synced" **stehen bleibt**. Abschnitt 9 belegt, dass die
Attrappe im selben Modus wirklich einen Fehler liefert — sonst misst Abschnitt 8 nur, dass gar
nichts passiert ist.

## 130. Ein Gericht, das niemandem gehörte — und ein leeres Array, das `true` ist

**Datum:** 28.08.2026 · **Betrifft:** `unflattenWeek()`, Gerichte-Zuweisung, Auto-Planer

### Der Fehler

Der Zuweisungs-Dialog hält eine ausdrückliche Zusage: Würde eine Abwahl `uids.length === 0`
ergeben, wird der Eintrag **komplett entfernt** — „ein Gericht ohne zugewiesene Person darf nie
im Datenmodell existieren" (`docs/ARCHITECTURES.md`, Orphan-Schutz).

`unflattenWeek()` hielt sie nicht:

```js
return uids ? { id: x.id, uids: uids } : x.id;
```

**Ein leeres Array ist in JavaScript truthy.** `{ id, uids: [] }` überlebte also — und zwar
ausgerechnet auf dem Weg, auf dem Plandaten von einem **anderen Gerät** hereinkommen, dem
einzigen, der fremden Daten laut eigenem Kommentar ausdrücklich nicht vertraut.

### Warum so ein Eintrag besonders unangenehm ist

Er ist **sichtbar, aber für jede Auswertung unsichtbar**:

| Stelle | Verhalten bei `uids: []` |
|---|---|
| `dayNutOf()` | zählt ihn niemandem an (`uids.indexOf(syncUid) === -1`) |
| `slotOpenForMe()` | meldet den Slot als **frei** — der Auto-Planer plant darüber |
| `entryIsShared()` | „nicht gemeinsam" → `slotIsShared()` kippt für die ganze Zeile |
| `buildShoppingList()` | skaliert mit `uids.length` auf **null** — wird nie eingekauft |

Der Widerspruch, den der Prüfstand festhält: Der Slot meldet „frei", obwohl dort etwas
**steht**. Der Planer legt sein Gericht daneben, und in der Zeile stehen zwei Karten, von denen
eine niemandem gehört.

### Der Sanitizer erzeugte die Waise selbst

Das ist der Teil, der den Fund von einer Theorie zu einem Befund macht. Es braucht **kein**
manipuliertes Dokument:

```js
const uids = Array.isArray(x.uids) ? x.uids.filter(u => typeof u === "string").slice(0, 24) : null;
```

Enthält `uids` nur Nicht-Strings — `[null, 7]` —, bleibt nach dem `filter()` ein **leeres
Array** übrig. Die Schutzmaßnahme gegen fehlerhafte Fremddaten produzierte also genau den
Zustand, den die Zusage nebenan verbietet.

### Die Behebung

Drei Fälle statt zwei, ausdrücklich unterschieden:

```js
if (!uids) return x.id;           // Objekt ohne uids -> String-Form (Altbestand, §73)
if (!uids.length) return null;    // Waise -> fällt unten aus dem Array
return { id: x.id, uids: uids };
```

Verworfen wurde die Alternative, eine leere Liste als „für alle" zu lesen. Sie wäre die
schlechtere Wahl: Ein kaputter Eintrag würde damit **allen** angerechnet und für alle
eingekauft. Entfernen ist zugleich das, was der lokale Weg seit jeher tut — beide Wege sagen
jetzt dasselbe.

### Die Regel dahinter

> **`if (array)` prüft nicht, ob etwas drin ist.** Wo eine leere Liste eine andere Bedeutung
> hat als eine gefüllte, muss `.length` geprüft werden — und wo ein Sanitizer filtert, ist die
> leere Liste ein *Ergebnis*, mit dem zu rechnen ist.

Allgemeiner, und das ist der eigentliche Ertrag: **Eine Zusage, die nur der lokale Weg
einhält, ist keine Zusage.** Der Orphan-Schutz stand im Zuweisungs-Dialog, wurde dort geprüft
und galt als erledigt. Der Sync-Weg schrieb dieselbe Datenstruktur, ohne dieselbe Regel zu
kennen. Dieselbe Fehlerklasse wie Ziffer 127, nur andersherum: dort las eine Stelle die zweite
Eintragsform nicht, hier schrieb eine Stelle sie falsch.

### Prüfstand

`tools/pruefstand-waise-uids.py` — 23 Prüfungen mit ausgeschnittenem `unflattenWeek()` und
`slotOpenForMe()`.

Abschnitt 10 ist der wichtigste: Er stellt alte und neue Fassung nebeneinander und zeigt die
**Folgewirkung** statt nur die Datenform — alt meldet „Slot frei" bei einem Eintrag im Slot,
neu ist frei *und* leer.

Zwei Gegenproben: Abschnitt 11 belegt, dass die alte Fassung die Waise durchlässt **und sie
aus `[null, 7]` selbst erzeugt**. Abschnitt 12 belegt, dass beide Fassungen ohne Waisen
byte-gleiche Ergebnisse liefern — sonst misst Abschnitt 11 nur „irgendwie anders".

## 131. Ein Prüfstand, der immer grün meldete, weil er nie lief

**Datum:** 28.08.2026 · **Betrifft:** `tools/pruefstand-katalog-plan.py`, `tools/alle-pruefstaende.py`

### Der Fehler

`pruefstand-katalog-plan.py` endete mit:

```python
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))
print("geschrieben")
```

Es **erzeugte** eine HTML-Datei und war fertig. Rückgabewert: 0. Die 45 Zusagen darin liefen
nur, wenn ein Mensch die Datei im Browser öffnete.

`tools/alle-pruefstaende.py` bewertet ausschließlich den Rückgabewert. Der Reihenlauf meldete
diesen Prüfstand also bei **jedem** Durchgang grün — unabhängig davon, ob der geprüfte Code
noch stimmte.

### Warum es auffiel — und warum das der eigentliche Punkt ist

Nicht durch Lesen. Der Prüfstand enthielt die Erwartung „nach dem Handshake läuft dieselbe
Migration nach". Ziffer 128 hat genau das abgeschaltet — die Erwartung war ab da **falsch**.
Trotzdem blieb der Reihenlauf grün, und zwar in mehreren Durchgängen hintereinander.

Gefunden hat es der Agent `doku-waechter`, der die veraltete Beschreibung in `docs/TESTING.md`
bemerkte. Erst beim Nachsehen fiel auf, dass die zugehörige Prüfung gar nicht ausgeführt wird.

**Ein falscher Prüfstand ist harmlos, solange er läuft — dann wird er rot.** Gefährlich wird
er erst in Kombination: falsche Erwartung *und* kein Lauf. Dann meldet das System „sauber"
über eine Behauptung, die es nie geprüft hat. Genau der Zustand, vor dem `CLAUDE.md` 18a
warnt, nur eine Ebene tiefer: Dort geht es um Prüfer mit veralteten *Fakten*, hier um einen
Prüfer, der überhaupt nicht **stattfindet**.

### Die Behebung

Das Skript fährt die erzeugte Seite jetzt selbst headless (dasselbe Muster wie die sieben
Nachbarn), gibt jede Zeile aus und liefert einen echten Rückgabewert. `pruef()` schreibt
zusätzlich auf die Konsole, `window.onerror` meldet einen Absturz als `ERGEBNIS 0 grün, 1 rot`
statt still zu bleiben. Die HTML-Datei bleibt erhalten — `docs/ARCHITECTURES.md` verweist
darauf, und im Browser zeigt sie dasselbe Protokoll für Menschen.

**Dazu nimmt er den Pfad zu `index.html` jetzt als Argument** statt ihn fest verdrahtet zu
tragen. Das ist keine Kosmetik: Ohne Argument lässt sich der Prüfstand nicht gegen einen alten
Stand fahren — und ohne Gegenprobe zählt in diesem Projekt kein Ergebnis.

Beides sofort belegt: gegen `HEAD` **45 grün**, gegen den Stand vor Ziffer 128
(`git show 30f4015:index.html`) **43 grün, 2 rot**, Rückgabewert 1.

### Nachtrag am selben Abend: es war nicht einer, es waren acht

Beim Bau der Reihenlauf-Prüfung stellte sich heraus, dass `pruefstand-katalog-plan.py` kein
Einzelfall war. **Acht von 24 Prüfständen** — ein Drittel der Suite — schrieben nur eine
HTML-Datei und endeten mit 0:

| Prüfstand | Zusagen, die nie liefen |
|---|---|
| `pruefstand-autoplaner.py` | 158 |
| `pruefstand-rezeptbuch.py` | 113 |
| `pruefstand-zurueck-taste.py` | 48 |
| `pruefstand-rezeptbuch-filter.py` | 33 |
| `pruefstand-ziel-undefined.py` | 24 |
| `pruefstand-gruppenlimit.py` | 23 |
| `pruefstand-gruppe-aufloesen.py` | 19 |
| `pruefstand-einladung-verbrauch.py` | 18 |

Zusammen **436 Prüfungen**, die der Reihenlauf bei jedem Durchgang als grün meldete, ohne
dass eine einzige davon ausgeführt wurde. Darunter die drei Gruppen-Prüfstände — also genau
der Bereich, in dem die Ziffern 125 bis 132 entstanden sind.

**Und einer war rot.** `pruefstand-einladung-verbrauch.py` fiel beim allerersten echten Lauf
durch: `joinGroup()` ruft seit Ziffer 128 `mergeOwnPlanIntoGroup()`, die Funktion war aber
nicht mit ausgeschnitten — der Aufruf lief in einen `ReferenceError`, den das `catch` in
`joinGroup()` als `group:joinMergePlan` meldete. Die Zusage „ein Beitritt läuft ohne
Fehlermeldung durch" war damit verletzt.

Behoben, indem `mergeOwnPlanIntoGroup()` jetzt **echt** mitgeschnitten wird (nicht gestubbt —
sie ist Teil des Beitrittspfads) und die `CloudGroup`-Attrappe `loadPlansFromServer` und
`savePlanWeek` kennt. 18 grün.

**Das ist der Beleg dafür, dass es kein theoretisches Problem war.** Ein Prüfstand, der nicht
läuft, ist nicht nur nutzlos — er verdeckt aktiv einen Fehler, den er gefunden hätte.

### Wie es behoben ist

**Kein Umbau der acht.** Sie teilen dieselbe Bauart: ein `<div id="log">`, in das `pruef()`
Zeilen schreibt. `tools/pruefstand_lauf.py` hängt der **erzeugten** Seite einen Beobachter an
(an eine Kopie im Temp-Verzeichnis, nie an die Datei im Repo), wartet, bis das Protokoll
steht, schiebt es auf die Konsole und zählt `OK`/`FEHL` selbst nach. Jeder der acht bekam
lediglich vier Zeilen ans Ende:

```python
if __name__ == "__main__":
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pruefstand_lauf import fahren
    _sys.exit(fahren(OUT))
```

Acht Dateien umzubauen hieße acht Gelegenheiten, versehentlich eine Zusage zu verändern. Im
Browser geöffnet verhalten sie sich unverändert.

Der Beobachter hat **zwei** Abbruchbedingungen, und die zweite ist die wichtigere: eine
erkennbare Schlusszeile — oder das Protokoll hat sich 1,5 s nicht mehr verändert. Ohne die
zweite hinge ein Prüfstand mit abweichender Schlusszeile bis zur Zeitgrenze, und das sähe aus
wie ein Befund, obwohl nur das Muster nicht passt.

### Das Netz darunter: `alle-pruefstaende.py` verlangt einen Beleg

Damit dasselbe beim **nächsten** Prüfstand nicht wieder passiert, reicht Rückgabewert 0 nicht
mehr. Der Reihenlauf verlangt eine Zeile, die ein Ergebnis benennt (`BELEG_MUSTER`); fehlt
sie, meldet er `OHNE BELEG` und zählt den Prüfstand als **auffällig**, nicht als grün.

Bewusst eine **weiße** Liste und keine schwarze: Ein neuer Prüfstand, der nichts belegt, soll
auffallen — nicht durchrutschen, weil noch niemand sein Muster eingetragen hat.

Gegenprobe gefahren: Ein Skript, das nur `print("geschrieben: irgendwas.html")` tut, wird
sofort als `OHNE BELEG` gemeldet.

### Die Regel dahinter

> **Ein Prüfstand, dessen Rückgabewert nicht vom Prüfergebnis abhängt, ist kein Prüfstand.**
> Er ist eine Datei, die entsteht.

Der Prüfpunkt für jeden künftigen: *Kann dieses Skript überhaupt rot werden?* Lautet die
Antwort nein, misst der Reihenlauf an dieser Stelle nichts — und niemand sieht es, weil grün
wie grün aussieht.

Der Prüfpunkt für jeden künftigen: *Kann dieses Skript überhaupt rot werden?* Lautet die
Antwort nein, misst der Reihenlauf an dieser Stelle nichts — und niemand sieht es, weil grün
wie grün aussieht. Seit diesem Zug prüft `alle-pruefstaende.py` genau das (siehe Nachtrag).

## 132. „Mengen × Mitglieder: Aus" galt nur für die Hälfte der Rechnung

**Datum:** 28.08.2026 · **Betrifft:** `buildShoppingList()`, `buildBatchList()`, `shopCountsMembers()`

### Der Fehler

Die Einkaufsliste summiert pro Zutat:

```
Endsumme = sharedQty * per + assignedQty
```

Der linke Summand folgt der Gruppen-Einstellung **„Einkauf für alle rechnen"** über `per`
(`shopPersons()`). Der rechte trug seinen Faktor fest im Eintrag: `uids.length`, unabhängig
von der Einstellung.

Stand der Schalter auf **Aus**, bekam man deshalb:

| Eintrag | Menge |
|---|---|
| „für alle" | einfach ✓ |
| beiden zugewiesen | **weiterhin doppelt** ✗ |

Bei einem Schalter, der wörtlich **„Mengen × Mitglieder"** heißt. Wer ihn ausschaltete, um nur
für sich einzukaufen, stand mit der doppelten Menge da.

`buildBatchList()` hatte dieselbe Asymmetrie (`esser = uids ? uids.length : persons`) — und
weil beide Listen ausdrücklich dieselbe Woche beschreiben müssen, hätten sie sonst für
verschiedene Personenzahlen gekocht und eingekauft.

### Wie es gefunden wurde

Nicht durch einen Fehlschlag. `tools/pruefstand-einkauf-gruppe.py` hielt den Zustand zunächst
als **Messung** fest (`MESS`-Zeilen statt `pr()`), weil die Frage „was soll *Aus* bedeuten?"
eine Produktentscheidung ist und keine Fehlerbehebung: Falsche Einkaufsmengen heißen leerer
Kühlschrank, und das ist nicht die Entscheidung des Prüfstands. Der Inhaber hat sie
getroffen — beide Summanden folgen der Einstellung.

### Die Behebung

`shopCountsMembers()` neben `shopPersons()` — dieselbe Frage für die andere Hälfte der
Rechnung, mit derselben Antwort:

```js
function shopCountsMembers() {
  return !!(syncGid && groupSetting("shopForAll") && groupMembers.length > 1);
}
```

Beide Verwender hängen jetzt daran. **Die Zuweisung selbst bleibt unberührt** — sie sagt
weiterhin, *wer* isst; sie sagt nur nicht mehr allein, *wie viel* eingekauft wird.

Bewusst **nicht** an `per` gehängt: `per` kann auch aus einer von Hand gesetzten Personenzahl
stammen (`state.shopPersons`), und die ist ein Haushalts-Multiplikator, keine Aussage über
Gruppenmitglieder. Die Zuweisung folgt ausschließlich dem Schalter, der ihren Namen trägt.

### Die Regel dahinter

> **Wenn eine Einstellung eine Summe steuert, muss sie jeden Summanden steuern.** Sonst ist
> sie keine Einstellung, sondern ein Hinweis auf einen Teil des Ergebnisses.

### Prüfstand

`tools/pruefstand-einkauf-gruppe.py`, Abschnitte 7, 7b, 7c — 26 Prüfungen insgesamt.
Abschnitt 7 prüft beide Summanden bei **Aus** *und* bei **An** (sonst bestünde er auch, wenn
überall stumpf mit 1 gerechnet würde). 7b hält die Vorkochliste daneben. 7c baut die alte
Formel nach und verlangt, dass sie sich unterscheidet — der Prüfstand lässt sich nämlich
**nicht** gegen die alte `index.html` fahren: dort gibt es `shopCountsMembers()` nicht, der
Schnitt scheitert am fehlenden Marker. Eine Gegenprobe, die am Werkzeug scheitert, ist keine;
also wird die alte Rechnung im Lauf selbst nachgebildet.

## 133. Wer aus einer Gruppe entfernt wird, bleibt für immer daran hängen

**Datum:** 28.08.2026 · **Betrifft:** `enterGroupSync()`, `CloudGroup.fetch()`

### Der Befund

Am Testkonto beobachtet, nachdem der Inhaber es aus der Gruppe entfernt hatte: Das
Kontodokument trägt weiterhin `groupId`, und ein Lesen der Mitgliederliste antwortet
`permission-denied` — das Konto ist nachweislich **kein Mitglied mehr**, zeigt aber weiterhin
auf die Gruppe.

Der Weg dorthin:

1. `CloudGroup.fetch(gid)` ist ein schlichtes `getDoc`. Die Regel lautet
   `allow get: if isMember(gid)` — für ein Nicht-Mitglied **wirft** der Aufruf.
2. `enterGroupSync()` fängt das im äußeren `catch` und liefert **`"error"`**, nicht `"gone"`.
3. `"error"` heißt ausdrücklich „wir wissen es gerade nicht": Der Zeiger bleibt stehen,
   `groupSyncFailed = true` hält `pushNow()` davon ab, ihn zu räumen.
4. Beim nächsten Start dasselbe. **Es gibt keinen Weg heraus.**

Sichtbar wird das als „Die Gruppe ist gerade nicht erreichbar – du planst vorerst für dich."
— bei jedem einzelnen Start, dauerhaft. Der Nutzer plant für sich, glaubt an ein
Verbindungsproblem, und niemand sagt ihm, dass er schlicht nicht mehr dabei ist.

### Warum das nicht einfach zu beheben ist

Der naheliegende Schluss — „`permission-denied` heißt: kein Mitglied, also `gone`" — ist
technisch richtig und **trotzdem gefährlich**. Firestore liefert diesen Code nur, wenn der
Server die Regel ausgewertet hat; offline kommt `unavailable` oder ein Cache-Treffer.

Aber genau am 28.08.2026 war messbar, dass die App-Instanz **fälschlich**
`permission-denied` liefern kann, über längere Phasen, bei völlig intakten Regeln und
gültigem Konto (Ziffer 129 ist daraus entstanden). Würde dieser Code als „gone" gewertet,
verlöre ein rechtmäßiges Mitglied in so einer Phase seine Gruppe — und zwar für **alle**
seine Geräte, weil `pushNow()` das leere `groupId` hochschriebe.

Damit steht die Abwägung genau andersherum als die bisherige Regel vermuten lässt:

> **Ein Zustand, der sich nicht von selbst auflöst, ist ein Fehler. Ein Zustand, der Daten
> kostet, ist schlimmer.** Solange die Ursache der falschen `permission-denied` unbekannt
> ist, darf dieser Code keine Löschung auslösen.

### Was stattdessen zu entscheiden ist

Drei Wege, alle drei sind Produktentscheidungen und deshalb hier nur benannt:

1. **Ein Ausweg in der Oberfläche.** Bleibt `groupSyncFailed` über mehrere Starts bestehen,
   bietet der Gruppen-Dialog „Diese Gruppe ist nicht mehr erreichbar – Verbindung lösen" an.
   Der Nutzer entscheidet, nicht der Client. Sicher, aber er muss es finden.
2. **Zählen statt raten.** Erst nach *n* aufeinanderfolgenden `permission-denied` bei
   sonst funktionierender Verbindung (das Kontodokument liest sich ja) wird geräumt.
   Braucht einen Zähler, der Sitzungen überdauert.
3. **Die Ursache der falschen `permission-denied` finden.** Dann trägt Weg 1 oder 2 von
   selbst, und die einfache Auswertung wäre wieder vertretbar.

### Behoben über Weg 1 (29.08.2026)

Der Gruppen-Dialog zeigt in genau dieser Lage — Zeiger gesetzt, aber keine laufende
Gruppensitzung (`!syncGid && state.groupId`) — eine Zeile: **„Diese Gruppe ist nicht
erreichbar."** mit dem Knopf **„Verbindung lösen"**.

Bewusst Weg 1 und nicht Weg 2 oder 3: Der Nutzer entscheidet, nicht der Client. Er sieht ja,
dass es nicht mehr geht — und ein Fehlurteil des Clients könnte die Gruppe auf **allen**
Geräten kosten, weil `pushNow()` das leere `groupId` hochschriebe. Solange derselbe Fehlercode
auch fälschlich auftreten kann (Ziffer 134), darf keine Automatik daraus eine Löschung machen.

**Kein `leaveGroup()`.** Das schriebe Meals und Plan zurück und wollte eine Mitgliedschaft
beenden, die es nicht mehr gibt. Geräumt wird nur der Zeiger — lokal **und** in der Cloud,
denn `wantGid = remote.groupId || state.groupId` holte ihn sonst beim nächsten Start zurück
(„Selbstheilung des Zeigers“). Der eigene Bestand bleibt unangetastet.

### Wie man ein betroffenes Konto heute löst

Es gibt keinen Knopf. Der Zeiger muss im Kontodokument geleert werden
(`users/{uid}.groupId = ""`); danach startet die App normal und der Nutzer kann einer neuen
Gruppe beitreten oder selbst eine gründen.

## 134. Der vergiftete Offline-Cache — Ursache der `permission-denied`-Phasen

**Datum:** 28.08.2026 · **Betrifft:** `persistentLocalCache`, Kontowechsel auf demselben Ursprung

### Der Befund

Den ganzen 28.08.2026 über lieferte die App-Instanz phasenweise `permission-denied` auf
**jeden** Firestore-Zugriff — bei gültiger Anmeldung, intakten Regeln und einem Konto, das
über die REST-API und über frisch erzeugte SDK-Instanzen einwandfrei lesbar war. Ziffer 129
ist daraus entstanden (die Anzeige log dabei „Synchronisiert").

**Die Ursache ist der persistente Offline-Cache des jeweiligen Ursprungs.** Gemessen:

| Zustand | Ergebnis |
|---|---|
| App-Instanz, betroffener Ladevorgang | `permission-denied`, **25 Versuche über 13 s, nie erholt** |
| dieselbe Instanz nach `getIdToken(true)` | weiterhin `permission-denied` |
| dieselbe Instanz nach `disableNetwork`/`enableNetwork` | weiterhin `permission-denied` |
| frische SDK-Instanz, eigener `persistenceKey` | **immer in Ordnung** |
| App-Instanz nach `CloudSync.wipeCache()` + Neuladen | **erster Versuch in Ordnung, 0 Fehler** |

Der Zustand ist **pro Ladevorgang stabil**: Ein betroffener Tab erholt sich nicht, ein
gesunder bleibt gesund. Das erklärt, warum ein Reload manchmal half und manchmal nicht.

### Der Auslöser

Auf `http://localhost:8000` hatte ein **Kontowechsel** stattgefunden (Inhaber → Testkonto).
Der Firestore-Cache liegt pro **Ursprung**, nicht pro Konto; die Produktionsdomain, auf der
nie gewechselt wurde, blieb gesund. Das ist die naheliegende Erklärung und deckt die
Beobachtungen — als bewiesen gilt sie damit **nicht**: Warum ein Kontowechsel den Cache in
diesen Zustand bringt, ist offen.

### Was das praktisch anrichtet

Nicht nur die Anzeige. Am selben Tag reproduziert: **Der Einladungslink funktioniert in diesem
Zustand nicht.** `openInviteModal()` läuft beim App-Start, also genau im betroffenen Fenster;
`fetchInvite()` scheitert, und der Nutzer liest „Die Einladung konnte nicht geladen werden."
Zweimal hintereinander reproduziert, danach mit geleertem Cache auf Anhieb erfolgreich.

Wer in diesem Zustand einen Einladungslink bekommt, kann der Gruppe **nicht beitreten** — und
nichts an der Meldung deutet darauf hin, dass ein Cache das Problem ist.

### Der Ausweg, und warum er heute niemand findet

`CloudSync.wipeCache()` gibt es bereits — es wurde für die Löschzusage aus Ziffer 10 der
Datenschutzerklärung gebaut. Es behebt diesen Zustand **sofort und vollständig**, ist aber nur
über die Konto-Löschung erreichbar. Es gibt keinen Knopf „Cloud-Verbindung zurücksetzen".

Das war die eigentliche Lücke: **Für einen Zustand, der die App unbrauchbar macht und den ein
Neuladen nicht heilt, existierte die Reparatur bereits — nur ohne Weg dorthin.** Seit dem
29.08.2026 gibt es ihn (siehe unten).

### Was zu entscheiden ist

Nicht in diesem Zug gebaut, weil es eine Produktentscheidung ist:

1. **Ein Knopf in den Einstellungen** — „Cloud-Verbindung zurücksetzen" (`wipeCache()` +
   Neuladen). Wenige Zeilen, weil die Funktion steht. Sichtbar nur, wenn nötig?
2. **Automatisch beim Kontowechsel.** Erkennt `handleCloudUser()` eine andere UID als beim
   letzten Start, wird der Cache geleert. Behandelt die vermutete Ursache statt des Symptoms.
3. **Automatisch bei anhaltendem `permission-denied`** — riskanter, weil `wipeCache()`
   ungeschriebene Änderungen verwirft. Hängt an derselben Abwägung wie Ziffer 133.

Weg 2 ist der sauberste, wenn sich der Kontowechsel als Auslöser bestätigt. Solange das
offen ist, wäre Weg 1 der ehrliche Zwischenschritt.

### Der Ausweg ist gebaut (29.08.2026)

**Einstellungen → „Cloud-Verbindung zurücksetzen"** — eine Zeile in der bestehenden
`.setlist`, sichtbar nur mit Cloud-Konto und nur, wenn das Modul `wipeCache()` überhaupt
kennt (ein älterer Stand aus dem Service-Worker-Cache könnte es nicht).

Warum in den Einstellungen und nicht dort, wo der Fehler auftritt: Der Einstellungen-Dialog
rendert **rein lokal**. Er ist also auch dann erreichbar, wenn kein einziger Firestore-Zugriff
mehr durchgeht — genau der Zustand, für den der Knopf da ist. Ein Hinweis am Sync-Punkt wäre
näher am Problem, aber der Punkt ist klein und trägt schon eine Bedeutung.

Drei Eigenschaften, die keine Details sind:

* **Es wird vorher gefragt.** `wipeCache()` verwirft den lokalen Zwischenspeicher und damit
  auch Schreibvorgänge, die noch nicht beim Server sind. Der Text nennt beides — was bleibt
  („deine Meals und dein Wochenplan liegen in der Cloud") **und** was verloren geht. Nur die
  beruhigende Hälfte zu nennen wäre die bequemere Lüge.
* **Scheitert das Wischen, wird NICHT neu geladen.** Der häufigste Fehlschlag ist kein Fehler,
  sondern ein zweiter offener Tab: `clearIndexedDbPersistence()` verlangt, dass sonst keine
  Instanz läuft. Würde trotzdem neu geladen, sähe der Nutzer denselben kaputten Zustand wieder
  und hielte den Knopf für wirkungslos. Stattdessen ein Hinweis, der die Ursache nennt.
* **Kein Toast vor dem Neuladen.** Er wäre im selben Atemzug wieder weg.

**Live durchlaufen** am 29.08.2026 mit dem Testkonto: Zeile sichtbar, Rückfrage korrekt,
bestätigt → Cache geleert, Seite neu geladen, danach `permission-denied` weg, Kontodokument
lesbar, **null Fehler im Protokoll**.

Prüfstand: `tools/pruefstand-cache-reset.py`, 23 Prüfungen.

### Die Ursache ist jetzt behandelt, nicht nur das Symptom (29.08.2026)

`kontoWechselAufraeumen(uid)` in `handleCloudUser()`: Meldet sich auf demselben Gerät ein
**anderes** Konto an, wird der Firestore-Zwischenspeicher geleert und die Seite neu geladen —
**bevor** irgendetwas synchronisiert.

Die Reihenfolge ist der ganze Trick und nicht verhandelbar:

1. neue UID **merken** (`localStorage`, synchron)
2. Cache leeren
3. neu laden

Nach dem Neuladen stimmt die gemerkte UID mit der angemeldeten überein — es wird also **nicht
erneut** gewischt. Stünde das Merken hinter dem Wischen, entstünde eine Neulade-Schleife, und
die App startete überhaupt nicht mehr. Der Prüfstand baut genau diese falsche Reihenfolge als
Gegenprobe nach und verlangt, dass sie in die Schleife läuft.

Drei Fälle, in denen bewusst **nichts** passiert: Erstanmeldung auf dem Gerät (es gibt keinen
fremden Cache), dasselbe Konto (kein Wechsel), und ein Modul ohne `wipeCache()` (älterer Stand
aus dem Service-Worker-Cache). Scheitert das Wischen — meist ein zweiter offener Tab —, hält
es die Anmeldung nicht auf: Die App startet normal, der Fehler landet im Protokoll, und der
Knopf aus den Einstellungen bleibt als Ausweg.

**Bewiesen ist der Zusammenhang weiterhin nicht.** Der Kontowechsel deckte alle damaligen
Beobachtungen, mehr nicht.

**Und einen Tag später war klar, dass er nicht der einzige Auslöser sein kann:** Der Inhaber
nutzt die App auf dem iPhone über einen Home-Screen-Verweis, und der hat unter iOS einen
eigenen Speicherbereich — eigener `localStorage`, eigener Firestore-Cache (Ziffer 135). Dort
entsteht derselbe Zustand ganz ohne Kontowechsel. Diese Behandlung greift also nur für einen
von mehreren möglichen Wegen hinein; der Knopf aus den Einstellungen greift für alle.

Prüfstand: `tools/pruefstand-kontowechsel.py`, 22 Prüfungen.

### Eine Beobachtung, die kein Befund ist

Nach dem regulären „Gruppe verlassen" stand einmal der **lokale** Zeiger (`state.groupId` im
`localStorage`) noch auf der alten Gruppe, während der Cloud-Zeiger korrekt leer war. Weil
`startCloudSync()` mit `wantGid = remote.groupId || state.groupId` arbeitet, führte das beim
nächsten Start in genau die Sackgasse aus Ziffer 133 — erreicht über den **normalen** Weg.

**Nicht reproduzierbar.** Nach dem Leeren des lokalen Werts und einem Neustart blieb er leer,
das Protokoll sauber. Der Rest stammt vermutlich aus dem ungewöhnlichen Ablauf des Tests
(Verlassen, Messungen, `wipeCache` dazwischen) und nicht aus `leaveGroup()`.

Festgehalten wird es trotzdem, weil die Fehlerklasse teuer wäre — und nach der Regel aus
Ziffer 102: **ein plausibler erster Verdacht ist kein Befund.** Wer hier je wieder etwas
sieht, weiß, wo zu suchen ist: der lokale Zeiger nach `leaveGroup()`.

### Die Regel dahinter

> **Ein Cache, der eine Antwort des Servers ersetzt, muss verwerfbar sein — und zwar von der
> Person, die vor dem Gerät sitzt.** Solange die einzige Reparatur hinter „Konto löschen"
> liegt, ist sie keine.

## 135. Der Home-Screen-Verweis auf dem iPhone ist ein zweites Gerät

**Datum:** 29.08.2026 · **Betrifft:** iOS-Standalone-Betrieb, `state.dedupeV1`, Firestore-Cache
· **Hinweis des Inhabers, nicht selbst gemessen**

### Der Hinweis

Der Inhaber nutzt Paddy's Mealplan auf dem iPhone über einen **Home-Screen-Verweis aus
Safari**. `manifest.webmanifest` setzt `"display": "standalone"` — die App startet dort also
als eigenständiges Fenster, nicht als Safari-Tab.

**Das ist für die App ein zweites Gerät.** iOS führt für zum Home-Screen hinzugefügte
Web-Apps einen eigenen Speicherbereich — `localStorage`, IndexedDB und damit auch der
Firestore-Cache sind vom Safari-Browser desselben Geräts getrennt. Wer beides benutzt, hat
zwei vollständige, unabhängige Clients auf demselben Telefon.

### Warum das die gemessenen Befunde verstärkt

Drei Stellen hängen unmittelbar daran:

1. **`state.dedupeV1` ist ein Geräte-Flag** (nur `localStorage`, siehe Ziffer 128). Zwei
   Speicherbereiche heißen: Die Migration läuft **zweimal**, unabhängig voneinander.
2. **Der Rückweg aus der Gruppe** (Ziffer 125) läuft je Client. Zwei Clients, die je einen
   vollständigen `state` halten und unabhängig pushen, sind genau das Muster, aus dem
   `lib`-Häufungen von **zwei und drei** entstehen — gemessen wurden am 28.08.2026 beide.
3. **Der Firestore-Cache liegt je Speicherbereich** (Ziffer 134). Ein beschädigter Cache in
   *einem* der beiden erklärt, warum die App „mal geht und mal nicht", je nachdem, ob man sie
   über das Symbol oder über Safari öffnet.

### Was das für die Behebung von Ziffer 134 heißt — und das ist unbequem

Die dortige Behandlung leert den Cache **beim Kontowechsel**. Das war die Hypothese, die alle
damaligen Beobachtungen deckte. Ein Home-Screen-Verweis braucht dafür aber **gar keinen
Kontowechsel**: iOS räumt Speicher zum Teil selbsttätig weg, und ein nur teilweise
vorhandener Firestore-Cache kann denselben Zustand erzeugen.

> **Die Behandlung greift also nur für einen von mehreren möglichen Auslösern.** Der Knopf
> „Einstellungen → Cloud-Verbindung zurücksetzen" greift für alle — er verlangt nur, dass
> jemand ihn findet.

Damit ist die Ursachenfrage aus Ziffer 134 **nicht abgeschlossen**, sondern breiter geworden.

### Nicht selbst geprüft

Der gesamte Abschnitt beruht auf der Angabe des Inhabers und auf dem Verhalten von iOS, nicht
auf einer eigenen Messung — es stand kein iPhone zur Verfügung. Bevor darauf etwas gebaut
wird, gehört es nachgemessen: dieselbe Anmeldung einmal in Safari, einmal über das
Home-Screen-Symbol, und in beiden `localStorage.getItem("wochenkueche_v1")` vergleichen. Sind
die Stände unterschiedlich, ist die Trennung belegt.

### Der naheliegende nächste Schritt

Der Hinweis aus Ziffer 129 („Cloud-Verbindung unterbrochen – lade die Seite neu") **weist ins
Leere**, wenn die Ursache der beschädigte Cache ist: Neuladen hilft dort nachweislich nicht.
Er sollte stattdessen auf den Knopf zeigen, der wirklich hilft. Eine Textänderung, aber eine,
die den Unterschied zwischen „App kaputt" und „ein Klick" ausmacht.

## 136. Ein `let` am Rand eines Schnitts: geteilter Zustand bricht die Aufteilung

**Datum:** 29.08.2026, bei der Aufteilung des Codes in `css/`, `data/` und `lib/`.

**Symptom:** Nach dem Auslagern der Barcode-Infrastruktur nach `lib/barcode.js` fielen
`pruefstand-einkaufsliste` und `pruefstand-sheet-repaint` durch:

```
Uncaught ReferenceError: liveScanStop is not defined
```

**Ursache:** Vor dem Schnitt wurde gemessen, welche Namen der Kern aus dem Block
braucht. Die Messung zählte `function`-Deklarationen und GROSSGESCHRIEBENE Konstanten —
und übersah dabei `let liveScanStop = null;`, eine kleingeschriebene Variable am Ende
des Blocks. Sie wird von `scanBarcodeLive()` gesetzt (blieb im Kern) und von
`closeModal()` gelesen (ebenfalls Kern). Der Schnitt lag damit **eine Zeile zu spät**:
Er nahm den geteilten Zustand mit, ließ aber beide Nutzer zurück.

**Behebung:** `liveScanStop` samt zugehörigem Kommentarblock zurück in den Kern, direkt
vor `scanBarcodeLive()`. Die Fassade `PM.barcode` trägt nur noch Funktionen und
unveränderliche Konstanten.

**Die Lehre:** Beim Schneiden einer Datei ist nicht die Funktionsliste die kritische
Größe, sondern **geteilter veränderlicher Zustand**. Eine Namensanalyse, die nur nach
`function` und `CONST` sucht, findet ihn nicht — sie meldet einen sauberen Schnitt und
liegt falsch. Prüfe vor jedem Schnitt zusätzlich auf `let`/`var` auf oberster Ebene und
darauf, wer sie **schreibt**.

## 137. Ein Cache in einer Fassade ist eine Kopie, kein Cache

**Datum:** 29.08.2026, gleicher Umbau.

**Symptom:** Der Marken-Kopf der PDFs wäre ohne Logo geblieben — still, ohne Fehler.

**Ursache:** `logoPdfAsset` ist ein Cache: `prepareLogoForPdf()` füllt ihn einmal
asynchron, `buildPrintable()` liest ihn später. Beim Auslagern des PDF-Schreibers nach
`lib/pdf.js` wanderte die Variable mit, `buildPrintable()` blieb im Kern. Der
naheliegende Weg wäre gewesen, sie in die Fassade zu legen:

```javascript
PM.pdf = { logoPdfAsset: logoPdfAsset, ... };   // FALSCH
```

Das legt eine **Kopie zum Ladezeitpunkt** ab — also `null`, für immer. Der Kern hätte
nie das gefüllte Logo gesehen, und weil der Kopf ohne Logo trotzdem gezeichnet wird,
wäre nichts aufgefallen außer einem fehlenden Bild im PDF.

**Behebung:** Ein Zugriff statt eines Werts:

```javascript
function logoAsset() { return logoPdfAsset; }
PM.pdf = { logoAsset: logoAsset, ... };
// im Kern:  const logo = PM.pdf.logoAsset();
```

**Die Lehre:** In einer Fassade ist jeder **Wert** eine Momentaufnahme. Alles, was sich
nach dem Laden noch ändert, gehört als Funktion hinein — sonst friert die Grenze den
Zustand ein, und zwar lautlos. Das ist dieselbe Klasse von Fehler wie Ziffer 136, nur
von der anderen Seite: dort wurde geteilter Zustand mitgenommen, hier eingefroren.

**Wie beides gefunden wurde:** Nicht durch Lesen, sondern durch den Prüfstandslauf gegen
die vorher festgehaltene Grundlinie. Ohne diese Grundlinie wäre nicht unterscheidbar
gewesen, ob ein roter Prüfstand am Umbau liegt oder vorher schon rot war.

---

## 138. Ein neues Sync-Feld braucht drei Stellen — die dritte wirft es beim eigenen Push weg

**Datum:** 29.08.2026 · **Symptom:** Ein neues Feld am Wochenarchiv (`weekStats[wk].d`,
die Tagesmaske) wurde geschrieben, war aber nach dem nächsten Sync verschwunden — auch mit
nur **einem** Gerät. Kein Fehler, keine Meldung.

Ziffer 115 hält fest, dass ein neues Sync-Feld **zwei** Merge-Stellen braucht (`onRemote()`
und den Baseline-Merge in `startCloudSync()`). Das stimmt — ist hier aber nicht die Ursache
gewesen. Die dritte Stelle ist:

```javascript
function sanitizeWeekStats(o) {
  ...
  out[k] = { kcal: ..., days: ..., hit: ... };   // baut das Objekt NEU auf
  ...
}
```

**Eine Bereinigungsfunktion, die jedes Objekt neu aufbaut, verliert alles Unbekannte.** Und
`sanitizeWeekStats()` läuft in `dataJSON()` und in `pushNow()` — also auf dem **eigenen**
Weg in die Cloud. Das Feld war damit schon weg, bevor irgendein zweites Gerät es hätte
verlieren können. Wer nur die zwei Merge-Stellen prüft, sucht am falschen Ende.

**Die Lehre:** Bei einem neuen synchronisierten Feld nicht nur nach `merge` greppen, sondern
nach jeder Funktion, die ein **Objektliteral aus Einzelfeldern** zusammensetzt —
`sanitize*`, `canon*`, jede Normalisierung. Faustregel: Wo ein `{ a: ..., b: ... }` steht
statt eines `Object.assign`, fällt alles Neue lautlos heraus.

**Zwei Regeln, die dabei mit festgehalten gehören:**

* **Ein kaputter Wert kostet das Feld, nie den Datensatz.** `d: "abc"` darf nicht die ganze
  Woche löschen — sonst wird aus einem Übertragungsfehler ein Datenverlust.
* **Zwei Felder, die dieselbe Sache beschreiben, dürfen sich in der Bereinigung nicht
  gegenseitig korrigieren.** `days` gegen die Maske `d` zu ziehen wäre naheliegend und
  falsch: Die Funktion läuft auf Bestandsdaten, und jede vor der Maske archivierte Woche
  hätte ihre Tage verloren. Beide einzeln validieren, den Widerspruch stehen lassen.

**Belegt durch:** `tools/pruefstand-wochenmaske.py` (48 `OFFEN`-Zeilen grün, Gegenprobe
gegen `9ae227d` fällt mit sieben roten durch) und `tools/pruefstand-weekstats-sync.py`.

---

## 139. `const` auf Modulebene: die App startet nicht, der Syntax-Check sagt nichts

**Datum:** 29.08.2026 · **Symptom:** `Uncaught ReferenceError: Cannot access
'ARCHIV_JAHRE_BEHALTEN' before initialization`. `#view` bleibt leer, die Seite liefert
HTTP 200, und `python syntax-check.py --alles` meldet alles sauber — es ist kein
Syntaxfehler, sondern die **temporale Totzone** (Temporal Dead Zone).

`index.html` ruft `load()` sehr frueh auf Modulebene auf:

```javascript
let state = load();          // Zeile ~1053
```

Alles, was `load()` in seiner Kette braucht, muss zu diesem Zeitpunkt **schon existieren**.
Funktionsdeklarationen werden vollstaendig gehoistet und sind sicher. Ein `const` oder `let`
weiter unten im Script ist es **nicht** — es existiert dort zwar, ist aber noch nicht
initialisiert, und jeder Zugriff wirft. Das beendet das gesamte App-Script.

**Dieselbe Falle, drittes Mal:**

| Betroffen | Fix |
|---|---|
| `ING_UNITS` (Zutaten-Einheiten, über `sanitizeIng()`) | `const` ganz nach oben, vor `load()` |
| Einwilligungs-Vorgabe (über `sanitizeConsent()`) | Funktion `noConsent()` statt `const` |
| `ARCHIV_JAHRE_BEHALTEN` (über `sanitizeWeekStats()`) | Funktionen `archivJahreBehalten()` / `archivJahreZeigen()` |

**Die Lehre:** Jede neue Konstante, die von einer `sanitize*`-Funktion gebraucht wird, ist
verdächtig — diese Funktionen hängen alle an `load()`. Zwei sichere Wege: die Konstante ganz
an den Anfang der IIFE (vor `let state = load()`), oder als **Funktionsdeklaration**
schreiben. Die zweite Variante ist robuster, weil sie ueberlebt, wenn der Code später
verschoben wird.

**Und der Grund, warum es auffiel:** Nicht der Syntax-Check und nicht das Lesen des Diffs,
sondern `python tools/alle-pruefstaende.py` — `pruefstand-einkaufsliste.py` fährt die echte
App und meldete „kein JS-Fehler beim Start" als ersten von 34 Fehlschlägen. Ein Prüfstand,
der eine ganz andere Funktion misst, findet so etwas mit, ein gezielter nicht. Der
Smoke-Test hätte es ebenso gezeigt — er war zu diesem Zeitpunkt schlicht noch nicht
gelaufen. **Deshalb steht er in Abschnitt 21 von `CLAUDE.md` vor dem Commit, nicht danach.**
