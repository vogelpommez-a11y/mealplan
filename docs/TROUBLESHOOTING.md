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
