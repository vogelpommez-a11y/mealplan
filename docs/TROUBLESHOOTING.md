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

* **zuerst `python syntax-check.py`** — benennt Fehlermeldung und Zeile in rund einer Sekunde,
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

**Symptom (Risiko, das der Umbau in `plans/MealAnsicht.MD` bewusst verhindert):** Eine offene, langlebige Ansicht auf ein Meal hält eine JS-Referenz auf das Rezept-Objekt. Ein anderes Gerät ändert dasselbe Meal in der Cloud. Der lokale Sync-Listener zieht den neuen Stand — aber die offene Ansicht schreibt weiter in die alte, jetzt abgehängte Objekt-Referenz. Kein Absturz, keine Fehlermeldung, die Eingabe verschwindet einfach lautlos.

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
