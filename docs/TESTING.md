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
