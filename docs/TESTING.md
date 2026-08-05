# TESTING.md

# Testing & Verifikation

Paddy's Mealplan besitzt derzeit keinen klassischen Test-Stack.

Es gibt:

* kein Node
* kein npm
* kein Test-Framework
* keinen Linter
* keinen Bundler

Die primäre Verifikation erfolgt deshalb über den Browser und gezielte isolierte Tests.

## Testprinzip

**Nicht vermuten. Ausführen.**

Wenn eine Funktion eine externe API, Browser-API oder komplexe Zustandslogik verwendet, muss sie möglichst mit realem Verhalten getestet werden.

Besonders wichtig:

> Wenn ein Test hängt, kann das ein echter Fehler sein.

Nicht automatisch den Test als defekt betrachten.

## 1. Smoke-Test

Der Smoke-Test rendert `index.html` headless mit Microsoft Edge.

Beispiel:

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --virtual-time-budget=9000 `
  --user-data-dir="<scratchpad>\edge-profile" `
  --dump-dom "file:///C:/Users/Paddy/Documents/Paddys%20Mealplan/index.html" > dump.html
```

Danach `dump.html` prüfen.

Nicht nur den HTTP-Status betrachten.

### Wichtigstes Signal

Wenn JavaScript wegen eines Syntaxfehlers nicht startet:

* statischer Header bleibt sichtbar
* `#view` bleibt leer

Deshalb muss geprüft werden, ob `#view` tatsächlich App-Inhalt enthält.

Beispiele:

* `Willkommen`
* `Anmelden`

Ein HTTP-200 beweist hier nichts.

## 2. Ausschneide-Prüfstand

Der Ausschneide-Prüfstand ist die wichtigste Methode für Funktionen, die hinter Login, Modal oder komplexem Zustand liegen.

### Grundidee

Den relevanten Code direkt aus `index.html` ausschneiden.

Nicht:

* abtippen
* manuell kopieren
* eine vereinfachte Kopie schreiben

Sondern:

* Marker im Original finden
* per Python den Bereich ausschneiden
* in eine temporäre HTML-Datei schreiben
* fehlende Helfer gezielt stubben
* headless ausführen

So wird tatsächlich der aktuelle Produktionscode getestet.

### Gegenprobe gegen den alten Stand

Ein Prüfstand, der nur den neuen Code grün zeigt, beweist nichts — er könnte am eigentlichen
Verhalten vorbeimessen. Bei Fehlerbehebungen deshalb denselben Prüfstand ein zweites Mal gegen
die Fassung vor der Änderung fahren:

```powershell
git show HEAD:index.html > "<scratchpad>\index_alt.html"
```

Das Build-Skript nur auf die andere Quelldatei zeigen lassen. Der alte Stand **muss** durchfallen.
Tut er es nicht, prüft der Test nicht das, was er zu prüfen vorgibt.

### Zusicherungen im Build-Skript

Das Ausschneiden per Regex/Klammernzählung kann stillschweigend den falschen Bereich erwischen.
Deshalb im Build-Skript mit `assert` festhalten, was im ausgeschnittenen Text stehen muss.
Dabei auf **Aufrufe** prüfen, nicht auf bloße Wortvorkommen: `assert "removeMember" not in code`
schlägt auch bei einem Kommentar an, der das Wort erklärt — `assert "CloudGroup.removeMember"
not in code` trifft den Aufruf.

### `--virtual-time-budget` wartet nicht auf IndexedDB

Wird IndexedDB (oder etwas anderes außerhalb der JS-Ereignisschleife) geprüft, liefert der
sonst übliche Aufruf **stillschweigend nichts**: `--virtual-time-budget` lässt die virtuelle
Uhr ablaufen und `--dump-dom` feuert, während die IDB-Rückrufe noch in Echtzeit unterwegs sind.
Kein Fehler, kein Log, leeres `<pre>` — das sieht aus wie ein Absturz, ist aber nur das Timing.

Lösung: Die Testseite meldet ihr Ergebnis aktiv zurück, statt auf den DOM-Dump zu warten.

```javascript
navigator.sendBeacon("/result", out.join("\n"));
```

Dazu ein kleiner Python-Server, der Dateien ausliefert und `POST /result` in eine Datei
schreibt (`result_server.py` im Scratchpad-Muster). Edge dann **ohne**
`--virtual-time-budget` und ohne `--dump-dom` starten, danach beenden.

`file:///` scheidet für IndexedDB ohnehin aus — über HTTP laden.

### Ablauf-Trace statt Raten

Bricht ein Prüfstand mittendrin ab, ist meist ein Stub vergessen worden. Statt zu raten, jeden
Stub seinen Namen protokollieren lassen und den Trace mit ausgeben — der letzte Eintrag zeigt,
welche Zeile im Produktionscode als Nächstes drankam. Zusätzlich `window.onerror` und
`unhandledrejection` in die Seite hängen, sonst verschluckt ein `catch` im Produktionscode den
Fehler und der Prüfstand liefert wortlos nichts.

## 3. Ergebnisfortschritt

Tests sollen nach jedem relevanten Schritt ein Ergebnis ausgeben.

Beispiel:

```html
<pre id="out"></pre>
```

Nach jedem Schritt aktualisieren.

Dadurch lässt sich erkennen, wo ein Test hängen bleibt.

## 4. Was isoliert getestet werden kann

### Reine Logik

Beispiele:

* Suchranking
* Namensauflösung
* Tabellen
* Plausibilitätsprüfungen
* Datenumwandlungen
* `qrSvg()` gegen das echte `vendor/zxing.min.js` (Skript-Tag lädt es lokal nach): prüft, dass
  ein `SVGSVGElement` mit quadratischen Maßen und mehreren Modul-Elementen entsteht.
* Einladungscode-Extraktion (`/[?&]g=([A-Za-z0-9_-]+)/`) gegen eine gültige URL, eine URL mit
  weiteren Parametern, eine fremde URL ohne `g=` und Klartext.
* Gruppen-Plan-Merge beim Aktivieren (`finalizeGroupActivation()`): mit gestubbtem `CloudGroup`
  prüfen, dass ein in der Gruppe bereits belegter Slot **nicht** überschrieben wird, ein dort
  noch leerer Slot aber nachgetragen wird.
* Gerichte-Zuweisung (`entryId`/`entryUids`/`entryIsShared`/`makeEntry`/`slotIsShared`) sowie der
  Aggregations-Kern von `buildShoppingList()` (Trennung `sharedQty`/`assignedQty`) lassen sich mit
  Mock-`state.plan`/`groupMembers`/Rezepten (inkl. `portions`) isoliert ohne DOM durchrechnen.
  Wichtiger Regressionsfall: `makeEntry` muss **Mengenabdeckung** prüfen (`groupMembers.every(...)`),
  nicht nur `uids.length` — sonst kollabiert eine veraltete UID eines ausgeschiedenen Mitglieds
  einen Eintrag fälschlich zu „für alle". Ebenso `unflattenWeek()` gegen ein simuliertes
  Fremd-Dokument mit kaputten `{id,uids}`-Objekten (fehlendes `id`, `uids` kein Array,
  Nicht-String-Elemente, überlange Arrays) — muss sanitisieren, nicht crashen oder blind
  übernehmen.
* `dayNutOf()` gezielt mit einem gemischten Tag testen (ein geteiltes Gericht, ein mir
  zugewiesenes, ein nur der anderen Person zugewiesenes) — die Summe darf nur die ersten
  beiden enthalten. Ein Test, der nur das alte String-Format prüft, findet diese Klasse Fehler
  nicht (siehe `docs/TROUBLESHOOTING.md` Ziffer 33).
* **Konvergenz zweier Geräte** — der wichtigste Sync-Test, den man ohne Firebase führen kann.
  Die Kette `onRemote()` → Merge → `save()` → Push nachstellen: zwei „Geräte" mit
  unterschiedlichem Anfangsstand, die abwechselnd den empfangenen Stand zusammenführen und
  zurückschreiben. Kriterium ist nicht das Ergebnis, sondern ob die Kette **zur Ruhe kommt**:
  Läuft sie nach einer festen Rundenzahl (z. B. 40) noch, schaukeln sich die Geräte im
  Echtbetrieb endlos auf. Immer **beide** Fassungen laufen lassen — die alte muss oszillieren,
  die neue nach ein bis zwei Runden still sein. Ohne diese Gegenprobe beweist ein „konvergiert"
  nichts, weil auch ein kaputter Prüfstand still ist (siehe `docs/TROUBLESHOOTING.md` Ziffer 34).
* **Badge-Kürzel** (`memberIni`/`memberBadgeIni`/`memberBadgeHtml`) mit einem
  `groupMembers`-Stub: gleiche Anfangsbuchstaben mit und ohne Nachnamen, Kleinschreibung,
  einbuchstabige Namen, Emoji im Namen (darf nicht halbiert werden), unbekannte UID.
* **Farbvergabe** (`memberColorSlot`) statistisch statt an einem Beispiel prüfen: einige hundert
  simulierte Gruppen mit 2–6 Mitgliedern und realistischen 28-stelligen UIDs durchrechnen und
  zählen, in wie vielen mindestens zwei dieselbe Farbe bekommen. Ein Einzelbeispiel beweist hier
  nichts — die alte Fassung war in 65 % der Gruppen betroffen und sah an jedem einzelnen
  handverlesenen Beispiel trotzdem gut aus. Randfälle mitnehmen: leere Gruppe, fremde UID, und
  **sieben** Mitglieder (mehr Personen als Farben — die Schleife darf dort nicht hängen).

* **`shareRecipeNow()`** mit gestubbtem `navigator.share`, `CloudShare.publish` und `shareId`
  ausschneiden und über ein Aufruf-Log prüfen: `navigator.share()` wird aufgerufen, bevor das
  `publish()`-Promise resolved (Nachweis, dass `await` die Nutzer-Aktivierung nicht verbraucht,
  siehe `docs/TROUBLESHOOTING.md` Ziffer 40) · `state.shares` enthält die ID, wenn `publish()`
  gelingt — auch wenn der Nutzer das Share-Sheet danach abbricht (`AbortError`) · ein
  `publish`-Reject erzeugt einen Toast statt eines unbehandelten Promise und lässt `state.shares`
  frei von der ID (kein Firestore-Dokument entstanden) · ohne `canShare()`, ohne Cloud-Konto, bei
  `authMode !== "cloud"` (lokales Profil, `CloudShare.enabled` allein reicht nicht) oder bei
  Payload > 400 KB öffnet sich `openShareRecipe()`. Ein gestubbtes `navigator.share` belegt nur
  die Aufruf-Reihenfolge, nicht dass iOS Safari die Aktivierung tatsächlich akzeptiert — das
  bleibt ein offener Handy-Test (siehe `ROADMAP.html`).

### Layout messen statt schätzen

Wo eine Änderung die Breite eines Elements verändert (hier: zweistellige Badge-Kürzel), reicht
ein Screenshot nicht — man sieht einen Überstand von wenigen Pixeln leicht nicht. Stattdessen
im Prüfstand mit `getBoundingClientRect()` gegen den Rand des Elternelements messen und den Wert
ausgeben. Gegenprobe: Die Messung muss zwischen den Fällen **unterschiedliche** Werte liefern —
lauter identische Zahlen heißen, dass gar nicht gemessen wurde. So fiel auf, dass zwei breite
Badges plus „+N" 5 px links aus der Karte liefen.

### Externe APIs

APIs nach Möglichkeit wirklich aufrufen.

Nicht nur anhand einer vermuteten Response-Struktur testen.

### Browser-/Geräte-APIs

Browser-APIs mit kontrollierten Attrappen testen.

Beispiel Kamera:

* `navigator.mediaDevices` über `Object.defineProperty` ersetzen
* echten `MediaStream` verwenden
* `getTracks()` kontrollieren
* `stop()` zählen

Nicht versuchen, schreibgeschützte Browser-Objekte direkt zu überschreiben.

### Layout

Für Layout-Tests:

1. relevanten `<style>`-Block ausschneiden
2. relevantes Markup isolieren
3. feste Fenstergröße verwenden
4. Screenshot erstellen
5. Light und Dark prüfen
6. Mobile Breiten prüfen

Kleine isolierte Seiten bevorzugen.

Gesamte Seite kann bei Screenshots in Timeouts laufen.

### Fenstergröße und CSS-Viewport

`--window-size` **setzt** den CSS-Viewport — abzüglich Scrollbar und abhängig von der
Geräte-Pixeldichte. Gemessen: `--window-size=420` ergab `window.innerWidth === 504`,
`--window-size=1170` ergab `1140`.

Deshalb bei jedem Layout-/Media-Query-Test die tatsächliche Breite **mitloggen**:

```js
log(window.innerWidth + "px, Media-Query greift: "
    + window.matchMedia("(max-width: 680px)").matches);
```

Ohne diese Zeile testet man unter Umständen die Desktop-Regeln und hält das Ergebnis für die
mobile Ansicht.

`--force-device-scale-factor=3` ändert den CSS-Viewport **nicht**, liefert aber einen
dreifach aufgelösten Screenshot — nützlich, um kleine Icons zu beurteilen.

### Media-Queries nicht „flachklopfen"

Der Reflex, für einen Test die Hülle `@media (max-width: 680px) { … }` per Python zu entfernen,
ist gefährlich: **die Datei enthält mehrere Blöcke mit demselben Breakpoint.** `str.index()`
findet den ersten (Navigation), nicht den gesuchten (Tagesleiste) — die zu prüfenden Regeln
bleiben dann wirkungslos, und der Test meldet lauter Standardwerte statt eines Fehlers.

Besser: das CSS unverändert lassen und stattdessen ein schmales Fenster verwenden.

### Fallen im Prüfstand selbst

* **Keine `\n`-Escapes in erzeugten JS-Strings.** Sie sind in dieser Umgebung schon als echte
  Zeilenumbrüche in der Datei gelandet — das ergibt einen Syntaxfehler im Prüfstand, und die
  Seite bleibt einfach leer. `String.fromCharCode(10)` verwenden.
* **`window.onerror` als allererste Zeile registrieren.** Sonst ist ein Fehler von einer nicht
  gelaufenen Prüfung nicht zu unterscheiden.
* **`color-mix()` serialisiert Chrome als `color(srgb …)`, nicht als `rgb(…)`.** String-Vergleiche
  gegen `"96, 165, 250"` schlagen fehl, obwohl das CSS stimmt. Lieber zwei berechnete Werte
  gegeneinander vergleichen als gegen eine erwartete Schreibweise.
* **Schreibzugriffe auf `style.<prop>` zählen:** `CSSStyleDeclaration.prototype` hat keinen
  eigenen Descriptor für `height`. Stattdessen `element.style` per
  `Object.defineProperty(el, "style", …)` durch einen `Proxy` ersetzen, der Sets mitzählt und
  sonst durchreicht.

### Performance messbar machen

„Fühlt sich flüssiger an" ist kein Ergebnis. Messbar sind zum Beispiel:

* Wie oft wird `style.height` über einen Scrollverlauf geschrieben? (Ziel: 0, wenn sich nichts
  ändert)
* Wie oft läuft ein Zustandswechsel über alle Knöpfe? (Ziel: nur bei echtem Wechsel)

Beide Zahlen lassen sich mit dem Proxy-Trick und einem Aufrufzähler direkt belegen.

## 5. UI-Testregeln

Bei UI-Änderungen mindestens prüfen:

* Desktop
* mobile Breite
* `max-width: 720px`
* `max-width: 560px`
* Light Theme
* Dark Theme
* Tastaturbedienung
* sichtbare Fokuszustände
* relevante ARIA-Zustände

Inputs müssen auf mobilen Geräten 16 px behalten, damit iOS nicht automatisch zoomt.

### Messfalle: Zeilenumbruch nicht über `top` zählen

Ob eine Flex-Zeile umbricht, lässt sich **nicht** dadurch feststellen, dass man die
verschiedenen `getBoundingClientRect().top` der Kinder zählt. Bei `align-items: center`
— dem Normalfall in diesem Projekt — haben unterschiedlich hohe Kinder in *derselben*
Zeile verschiedene `top`-Werte. Der Test meldet dann überall Umbruch, auch auf 1920 px,
und der Fehler fällt nicht auf, weil das Ergebnis plausibel aussieht.

Stattdessen die Höhe der Zeile gegen das höchste Kind prüfen:

```js
var rowH = row.getBoundingClientRect().height;
var zeilen = rowH > hoechstes + 1 ? Math.round(rowH / hoechstes) : 1;
```

Das ist derselbe Fehlertyp wie `focus()` vor einer Scroll-Messung: Der Prüfstand läuft
durch und liefert Zahlen, misst aber etwas anderes als gemeint. **Deshalb gehört zu jeder
Layout-Messung eine Gegenprobe gegen den alten Stand** — liefern alt und neu identische
Werte, misst der Test nicht das, was die Änderung betrifft.

### Trefferflächen mitmessen, wenn Abstände sich ändern

Wird an `gap` oder Knopfgrößen einer Reihe geschraubt, im selben Durchlauf die
Trefferflächen prüfen (`getComputedStyle(el, "::after")` für den hitSlop, Abstand
benachbarter Flächen ≥ 0). Beispiel: Der `gap: 10px` in `.rcard .actions` sieht nach
Spielraum aus, ist aber die Untergrenze — `.fav-ic` hat `::after { inset: -5px }`, die
Flächen liegen bereits exakt bei 0,0 px aneinander. Siehe TROUBLESHOOTING §38.

## 6. Mehrstufige Abläufe

Bei Wizard-/Carousel-Änderungen prüfen:

* Fortschrittsbalken
* korrekte Schrittzahl
* korrekter Füllstand
* Zurück-Navigation
* kein Klick-Sprung über die Progress-Bar
* Tastatur-/Screenreader-Verhalten
* unsichtbare `initCarousel()`-Platzhalter
* `aria-hidden="true"`
* `tabindex="-1"`

## 7. Sync-Tests

Bei Cloud-/Gruppenänderungen testen:

* lokaler Modus
* Cloud-Modus
* Login
* Logout
* Snapshot
* parallele Änderungen
* Gruppenrollen
* `owner`
* `edit`
* `view`
* leeren Slot
* geänderten Slot
* mehrere Tabs, wenn relevant

Besonders auf Endlosschleifen achten:

`render → push → snapshot → render → push`

**Zwei Geräte im Leerlauf sind der schärfste Test dafür.** Beide angemeldet, beide auf dem
Wochenplan, und dann bewusst **nichts** tun. Es darf weder wiederholt neu gezeichnet werden noch
im Minutentakt „Von anderem Gerät aktualisiert" erscheinen. Diese Schleife entsteht nicht durch
falsche Daten, sondern durch **zwei gültige Zeichenketten für dieselbe Menge** — jede neue
Merge-Funktion deshalb gegen die Frage prüfen: liefert `merge(a, b)` dieselbe Zeichenkette wie
`merge(b, a)`? Ohne echte zweite Anmeldung lässt sich das im Prüfstand nachstellen (siehe
Abschnitt 4, „Konvergenz zweier Geräte"). Historischer Fall: `docs/TROUBLESHOOTING.md` Ziffer 34.

## 8. Datenschutz-/Security-Regression

Bei Änderungen an Cloud-Daten prüfen:

* keine unnötigen personenbezogenen Daten
* Meal `by` bleibt UID
* keine E-Mail im Gruppen-Mitgliederdokument
* Security Rules bleiben restriktiv
* `get` und `list` nicht versehentlich verwechseln
* UI-Sperren nicht als Security betrachten

## 9. Testabschluss

Vor Commit:

1. relevante Funktion isoliert testen
2. Smoke-Test ausführen
3. UI bei relevanten Änderungen prüfen
4. Light/Dark prüfen
5. Mobile prüfen
6. bei Cloud-Änderungen Sync prüfen
7. passende Prüf-Agenten einsetzen
8. `git diff` kontrollieren

Nach Push:

```powershell
git ls-remote origin refs/heads/main
git rev-parse HEAD
```

Remote-Commit und lokaler HEAD müssen übereinstimmen.

## Grundregel

**Der Test soll möglichst nahe an der tatsächlichen Produktionsimplementierung bleiben.**

Je weniger manuell kopierter Testcode existiert, desto geringer das Risiko, eine Kopie statt der echten App zu testen.
