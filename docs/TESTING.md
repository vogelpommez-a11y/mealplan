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

## 0. Syntax-Check (läuft zuerst, vor allem anderen)

```powershell
python syntax-check.py
```

Rund **1 Sekunde**. Prüft jeden `<script>`-Block in `index.html`, **ohne ihn auszuführen**.
Rückgabe `0` = sauber, `1` = Syntaxfehler, `2` = die Prüfung selbst ist fehlgeschlagen.

**Nach jeder Änderung an JavaScript ausführen, bevor der Smoke-Test überhaupt sinnvoll ist.**
Ein Syntaxfehler beendet das gesamte App-Script — der Smoke-Test zeigt dann ein leeres `#view`,
sagt aber nicht, wo der Fehler steckt. Genau diese Situation ist zweimal eingetreten
(`docs/TROUBLESHOOTING.md`, Punkte 5 und 6).

### Wie er arbeitet

* **Klassische Blöcke** gehen durch `new Function(code)`. Das parst vollständig, führt den Rumpf
  aber nie aus: kein DOM-Zugriff, kein `localStorage`, kein Firebase, keine Nebenwirkungen.
* **Der Modul-Block** (`type="module"`) kann so nicht geprüft werden — `import` wäre innerhalb
  einer Funktion selbst ein Syntaxfehler. Er läuft deshalb über eine Blob-URL mit dynamischem
  `import()`, wobei die Import-Quellen auf ein leeres `data:`-Modul umgebogen werden. Damit
  braucht die Prüfung kein Netz, und die Syntax bleibt echte Modulsyntax.
* Geprüft wird mit der **V8-Engine von Edge** — derselben, die die App später ausführt. Ein
  Python-JS-Parser wie `esprima` kennt neuere Syntax (`?.`, `??`, `#private`) oft nicht und
  meldet Fehler, die keine sind.
* **Nicht jeder `<script>`-Block ist Code.** Der JSON-LD-Block im Kopf
  (`type="application/ld+json"`, Aufgabe A5) ist ein Datenblock; als JavaScript geparst
  scheitert er zwangsläufig am ersten `:`. Das Skript entscheidet deshalb nach `type`: Alles
  außerhalb der JS-Typen geht **nicht** durch V8. JSON-LD wird stattdessen mit `json.loads`
  geprüft — ein Tippfehler dort bricht die Such­maschinen-Auswertung, sonst nichts, und fällt
  daher an keiner anderen Stelle auf. Andere Nicht-JS-Typen werden mit Hinweis übersprungen.

### Zwei Fallen, die beim Bau aufgetreten sind

**V8 meldet Modul-Linking-Fehler ebenfalls als `SyntaxError`.** Beim ersten Lauf schlug der
Modul-Block mit „does not provide an export named 'EmailAuthProvider'" fehl — ein Fehlalarm des
Prüfstands, kein Befund. Solche Fehler entstehen erst **nach** dem Parsen und sind damit der
Beweis für sauberen Code. Sie werden deshalb ausgefiltert.

**V8 nennt bei einem Parse-Fehler keine Position.** `e.stack` ist blank (`"SyntaxError:
Unexpected number"`) — sowohl bei `new Function` als auch bei dynamischem `import()`. Die
Zeilennummer wird deshalb **eingegrenzt statt ausgelesen**: Ein abgeschnittenes Stück Code meldet
„Unexpected end of input", solange der Schnitt vor dem Fehler liegt. Gesucht ist per binärer Suche
der erste Schnitt, der **dieselbe Meldung** liefert wie der vollständige Code (rund 14 Versuche
für 10.000 Zeilen).

Nur auf „irgendeinen harten Fehler" zu prüfen reicht **nicht**: Ein Schnitt mitten durch einen
String oder ein Template-Literal erzeugt ebenfalls einen harten Fehler und stoppt die Suche zu
früh — im Versuch 250 Zeilen vor der echten Stelle.

### Die Genauigkeitsangabe ernst nehmen

Das Skript unterscheidet zwei Fälle und sagt, welcher vorliegt:

```text
-> index.html:5000                                  bewiesen
-> etwa index.html:3960 (eingegrenzt, nicht bewiesen)   Näherung
```

„Bewiesen" heißt: Entfernt man genau diese eine Zeile, ist der Fehler weg. Bei „etwa" liegt die
Stelle in der Nähe — gemessen zwischen 0 und 40 Zeilen daneben. Beides zusammen mit der
Fehlermeldung reicht zum Auffinden.

### Gegenprobe (bei Änderungen am Skript zu wiederholen)

Ein Prüfstand, der nichts findet, beweist nichts. Der Check wurde gegen vier präparierte Kopien
von `index.html` gefahren — fehlender Wert, unterminierter String, fehlende Klammer, fehlendes
Komma, jeweils an bekannter Zeile:

| Fehler | eingebaut in | gemeldet |
|---|---|---|
| fehlender Wert (`const x = ;`) | 5000 | 5000, bewiesen |
| unterminierter String | 9000 | 9000 |
| fehlende Klammer | 6000 | 6000 |
| fehlendes Komma (`foo(1 2)`) | 4000 | etwa 3960 |
| kaputte Funktionssignatur | 7000 | etwa 7000 |
| fehlendes Komma im JSON-LD | 50 | 51, JSON-LD-Block |

## 1. Smoke-Test

Der Smoke-Test rendert `index.html` headless mit Microsoft Edge.

**Erst nach bestandenem Syntax-Check ausführen** (Abschnitt 0) — sonst prüft man neun Sekunden
lang, ob ein Fehler vorliegt, den eine Sekunde präzise benannt hätte.

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
* **Der Fehlermelder `window.noteError`** (A7). Er hat keine Abhängigkeiten und lässt sich
  deshalb direkt aus dem **ersten** `<script>`-Block schneiden — alles bis zum Kommentar
  `/* Erscheinungsbild vor dem ersten Paint`. Neun Prüfungen, alle grün:
  Existenz samt `dump()`; Drosselung auf 3 pro Kennung (und zwar die **ersten** drei, nicht die
  letzten); getrennte Zählung je Kennung; Ringpuffer bei 50 gedeckelt; wirft nie selbst —
  auch nicht bei `noteError()` ohne Argumente, mit `null`, mit einem zirkulären Objekt oder mit
  einer Kennung, deren `toString()` selbst wirft; `dump()` liefert eine Kopie statt eines
  lebenden Verweises; Einträge tragen Zeit, Kennung und Meldung.
  Die letzten drei Punkte sind der Kern: Ein Melder, der im Fehlerpfad selbst wirft, ist
  schlimmer als gar keiner (`docs/TROUBLESHOOTING.md` §71).
* **Meal-Merkmale (B6)**: `sanitizeRecipe()`/`sanitizeTags()` samt `mealFlagsHtml()` und
  `mealMetaEditHtml()` lassen sich mit echtem `esc()` und gestubbtem `sanitizeIng()` schneiden.
  19 Prüfungen, alle grün. Seit dem Ausbau des Felds `difficulty` (13.08.2026) prüfen drei davon
  die **Gegenrichtung**: Ein Alt-Wert muss aus dem Objekt **verschwinden**, nicht nur unbenutzt
  bleiben — `Object.assign()` in `sanitizeRecipe()` kopiert sonst jedes unbekannte Feld aus
  Altdaten und geteilten Meals ewig weiter. Dazu: kein `f-diff`-Umschalter mehr im
  Eingabe-Markup, keine Aufwand-Marke mehr in der Anzeige. Die drei, die wirklich zählen: **unbekannte Tag-Schlüssel und
  Duplikate fliegen raus**, die **Reihenfolge ist stabil** (eine umsortierte Liste wäre ein
  Dauer-Diff gegen `canonJSON()` und damit ein Endlos-Schreibzyklus in `syncRecipes()`), und ein
  **Bestands-Meal ohne Merkmale bekommt keine neuen Felder** — sonst schriebe allein das Laden
  jedes Rezept einmal in die Cloud.
  *Falle beim Prüfstand selbst:* Ein XSS-Testwert mit `</script>` im String beendet den
  `<script>`-Block der Testdatei. Das Ergebnis war ein leeres `<pre>`, das wie ein stiller
  Testfehler aussah. Solche Nutzlasten mit `<img src=x onerror=…>` bauen oder maskieren.
* **Einstiegspfad (D1b)**: Der Verzweigungsblock aus `handleCloudUser()` samt
  `enterLocalMode()` lässt sich schneiden; die fünf Bildschirme sind Attrappen, die nur ihren
  Namen notieren. 12 Prüfungen, alle grün. Wichtig sind die drei Lagen ohne angemeldeten
  Cloud-Nutzer: **kein Profil → die Wahl**, **lokales Profil → direkt in die App**,
  **Cloud-Profil → Anmeldemaske**. Dazu die Gegenprobe, dass ein zweiter `enterLocalMode()`
  wirkungslos bleibt (`cloudSignalled`) — sonst überschriebe ein spät eintreffendes
  Cloud-Signal den bereits gezeigten lokalen Weg.
* **Pro-Berechtigung (D1)**: `sanitizeEntitlement()`/`isPro()` lassen sich ohne jede Abhängigkeit
  schneiden. 16 Prüfungen, alle grün — und **eine echte Lücke gefunden**: `until: NaN` ergab
  unbefristetes Pro (§76). Pflichtfälle für diesen Prüfstand: nur ein echtes `true` zählt
  (kein `"true"`, keine `1`), Ablauf als Zahl **und** als Firestore-Timestamp (`toMillis()`),
  kaputtes Ablaufdatum → **kein** Pro, unbekannte `source` → `"manual"`, und der Ablauf muss
  **zur Laufzeit** greifen (Testfall: kurzer Ablauf, aktive Warteschleife, danach erneut
  `isPro()` — eine App, die über Mitternacht offen bleibt, darf Pro nicht behalten).
  Nicht automatisiert prüfbar ist die eigentliche Sicherheitsgrenze: dass `entitlements/{uid}`
  vom Client **nicht schreibbar** ist. Das hängt am veröffentlichten Regelstand in der
  Firebase-Konsole (`CLAUDE.md` §18) und ist nur dort nachweisbar.
* **Pro-Grenze (D2b)**: `sanitizeEntitlement()`, `isPro()`, `syncStatusInfo()`/`setSyncStatus()`,
  `syncRecipes()` und `pushNow()` werden geschnitten; die Cloud-Objekte sind Zähl-Attrappen.
  21 Prüfungen, alle grün.
  Der Prüfstand belegt seit dem 15.08.2026 vor allem eine **Nicht**-Eigenschaft: dass der Sync
  die Berechtigung an keiner Stelle abfragt. „Ohne Pro wird trotzdem geschrieben" ist ein
  vollwertiger Testfall — die Sperre war einen Tag lang da und ist bewusst wieder verschwunden;
  ein Prüfstand, der nur die Berechtigung selbst prüft, hätte ihre Rückkehr nicht bemerkt.
  Dazu die Fälle aus §76 (kaputtes `until`, `"true"` als Zeichenkette, Firestore-Timestamp).
  **Falle beim Bauen des Prüfstands:** Der Schnitt „von der Signatur bis zur ersten Zeile `  }`"
  verschluckt bei einer **Einzeiler-Funktion** (`canCloudWrite()`) den kompletten Folgecode bis
  zur nächsten schließenden Klammer. Das Ergebnis ist ein Parse-Fehler im einzigen `<script>` —
  und damit läuft **auch `window.onerror` nicht**, die Seite bleibt einfach leer. Endet die
  Signaturzeile selbst auf `}`, ist sie die ganze Funktion.
  Die **Gegenprobe** lief noch an der ursprünglichen Fassung: `canCloudWrite()` künstlich auf
  `true` gesetzt, vier Prüfungen wurden rot. Das ist der Beweis, dass der Prüfstand misst und
  nicht nur läuft (`docs/TESTING.md`, „Messfallen").
* **Rezeptbuch (15.08.2026)**: `COOKBOOK`, `cookbookVisible()`, `isAdopted()`,
  `adoptFromCookbook()` samt `sanitizeRecipe()` geschnitten. 28 Prüfungen, alle grün.
  Drei Gruppen, und die erste ist die, die bei wachsendem Katalog Bestand haben muss:
  **Struktur des Katalogs** — alle IDs eindeutig, alle mit Nährwerten, Kategorie und Zutaten,
  und **jedes vegane Meal trägt auch `vegetarisch`** (sonst findet es der Filter im
  Meals-Reiter nicht, auch wenn `dietOk()` es durchließe). Bei 30 oder 100 Einträgen fällt so
  ein Fehler sonst niemandem auf.
  **Profilfilter** — vegan zeigt nur veganes, vegetarisch schließt veganes ein, Form und
  Einschränkung wirken zusammen.
  **Übernahme** — eigene `id` statt der Katalog-`id` (sonst kollidieren zwei Konten in einer
  Gruppe), `lib` als Herkunft, Rückgängig, und die Gegenprobe, dass **Umbenennen der Kopie
  nicht auf den Katalog abfärbt** (Kopie, keine Referenz).
* **Bild-Werkzeug (`tools/test-meal-bilder.py`, 15.08.2026)**: Kein Ausschneide-Prüfstand,
  sondern ein eigener Test für `tools/meal-bilder.py` — er lädt das Skript als Modul und
  kommt **ohne einen einzigen API-Aufruf** aus. 33 Prüfungen, alle grün.
  Das ist hier keine Sparsamkeit: Jeder Fehlversuch am scharfen Werkzeug kostet Geld, und ein
  Fehler in der Bildverarbeitung fiele sonst erst beim hundertsten bezahlten Bild auf. Genau
  so wurde `slug("Bowl (vegan), scharf")` → `bowl-vegan--scharf` gefunden.
  Geprüft werden vier Gruppen: **Dateinamen** (Umlaute, Sonderzeichenketten), **Prompt-Bau**
  (größte Mengen zuerst, Freitext-Zutaten raus, Diät-Verneinungen vor dem Stil, Kategorie →
  Geschirr), **Bildverarbeitung** (Zuschnitt auf das Zielverhältnis, **mittig** — belegt mit
  einem Testbild, dessen Ränder rot markiert sind —, WebP, kein Hochskalieren) und die
  **eingefrorenen Konstanten**.
  Als der Zuschnitt eingeführt wurde, hat der alte Testfall „Seitenverhältnis bleibt" die
  Änderung korrekt gemeldet, statt sie durchgehen zu lassen.
* **Ernährungsprofil (15.08.2026)**: `DIETS`/`AVOIDS`, `dietOk()`, `avoidOk()`, `fitsDiet()`,
  `toggleAvoid()`, `sanitizeGoal()` und `computeGoal()` geschnitten. 33 Prüfungen, alle grün.
  Drei Fälle, die man leicht übersieht: **vegetarisch muss vegane Gerichte zulassen** (sonst
  fällt die Hälfte des Bestands weg), **`computeGoal()` muss die Felder durchreichen** (seine
  Rückgabe zählt einzeln auf — ohne das wäre das Profil nach der ersten Wiegung weg), und die
  **Reihenfolge in `avoid` muss unabhängig von der Tippreihenfolge sein**, sonst entsteht gegen
  `canonJSON()` ein Endlos-Schreibzyklus. Dazu die Sanitizer-Fälle: unbekannte Werte fliegen
  raus, ohne Angabe entsteht **kein** Feld.
* **Ausbau von `portions` (15.08.2026)**: `sanitizeRecipe()` samt `nutNum()` und `ingObj()`
  geschnitten, der Rest gestubbt. 18 Prüfungen, alle grün. Der Kern ist nicht die Umrechnung
  selbst (200 → 100), sondern zweierlei: **Idempotenz** — dreimal durchlaufen ergibt dasselbe
  wie einmal, sonst schrumpften die Mengen bei jedem Cloud-Eingang weiter — und die
  **Unsinnswerte**: `portions: 0`, negativ oder als Text dürfen nichts verändern (keine Division
  durch null, keine erfundenen Mengen). Dazu: Freitext-Zutaten bleiben unangetastet, Einheiten
  überleben, gerundet wird auf eine Nachkommastelle.
* **Vorkochen (C3)**: `buildBatchList()` braucht nur Stubs für `getRecipe`, `shopPersons` und
  `todayDayKey` — dazu `planDaysAhead()`, die gemeinsame Zeitraum-Quelle. 17 Prüfungen, alle grün — Bündelung, Sortierung, Portionsfaktor, aufgerundete
  Kochdurchgänge, Zuweisung statt Personenzahl, leerer Plan. Zwei Fälle, die man leicht
  vergisst: **ein Rezept ohne `portions`** darf keine erfundene Durchgangszahl bekommen, und
  der **Zeitraum muss dem der Einkaufsliste entsprechen** (aktuelle Woche ab heute) — sonst
  beschreiben zwei Ansichten dieselbe Woche verschieden. Nach dem Zusammenführen des Zeitraums
  in `planDaysAhead()` wurde **`buildShoppingList()` gegengeprüft** (8 Prüfungen: ab heute,
  nächste Woche ganz, Sonntag, Personenzahl, Portionsfaktor) — ein geteilter Helfer ist erst
  dann eine Verbesserung, wenn der ältere Aufrufer sich nachweislich nicht verändert hat.

### Kontrast messen, nicht schätzen — und `color-mix` über ein Canvas-Pixel auflösen

Farbwerte lassen sich im Prüfstand berechnen (WCAG-Formel auf der relativen Luminanz), aber
zwei Fallen machen die Zahlen sonst wertlos:

* **`data-theme` wirkt nur am Wurzelelement.** Die Theme-Blöcke sind `:root[data-theme="dark"]`
  — an einem `<div data-theme="dark">` passiert nichts. Der erste Anlauf maß Light und Dark
  in einem Dokument und lieferte zweimal exakt dieselben Zahlen. **Identische Werte für beide
  Themes sind das Warnsignal**, nicht das Ergebnis. Je Theme eine eigene Datei.
* **`getComputedStyle()` liefert für `color-mix()` ein `color(srgb 0.78 0.63 0.15)`** — Werte
  von 0 bis 1. Ein Regex, der Zahlen einsammelt, liest daraus 0–255 und macht aus Hellgold
  fast Schwarz (gemeldet wurden 20:1 zwischen zwei hellen Flächen). Zuverlässig ist der Umweg
  über ein 1×1-Canvas: `ctx.fillStyle = farbe; fillRect; getImageData` gibt echte RGBA-Bytes
  für **jede** CSS-Farbe. Halbdurchlässige Werte danach selbst auf den Hintergrund rechnen.

So gemessen für die Pro-Marke (D1): Schrift auf der Marke **5,17:1** in Light und **7,93:1** in
Dark. Der erste Entwurf lag bei 4,38:1 und damit unter AA — sichtbar war das nicht, nur messbar.

### `syntax-check.py` läuft auch auf Prüfständen

`python syntax-check.py <datei.html>` prüft jede HTML-Datei, nicht nur `index.html`. Das spart
beim Prüfstandsbau echte Zeit: Ein leeres `<pre>` sieht wie ein stiller Testfehler aus, hat aber
meist eine banale Ursache. Zwei davon sind hier aufgetreten:

* **`Identifier 'ingLabel' has already been declared`** — der Stub deklarierte etwas, das im
  ausgeschnittenen Code schon stand. Ein `SyntaxError` bricht den ganzen Block ab, ein
  `try/catch` fängt ihn **nicht** (er entsteht beim Parsen, nicht beim Laufen).
* **`qtyLabel is not defined`** — umgekehrter Fall: gebraucht, aber außerhalb des Ausschnitts.
  Den findet man nur mit `try/catch` um die IIFE.

Reihenfolge deshalb: erst `syntax-check.py` auf den Prüfstand, dann `try/catch` für
Laufzeitfehler, erst dann die eigentlichen Prüfungen lesen.
* **Gewichtsverlauf in Wochen (B2)**: `sanitizeWeights()`, `mergeWeights()` und
  `weightChartSvg()` mit einem winzigen Stub-State. 21 Prüfungen, alle grün. Neben den
  Schlüssel-Randfällen (KW 0/54, Fremdformate) sind die beiden wichtigen: **beide Altformate
  werden umgerechnet statt verworfen** (Tag → Woche, Monat → Woche des 15.), und **die
  Trendlinie reagiert gedämpfter als die Rohkurve** — gemessen am Sprung des letzten Punktes,
  nachdem eine Ausreißer-Wiegung eingesetzt wurde. Ohne diesen Vergleich prüft man nur, *dass*
  eine zweite Linie existiert, nicht dass sie glättet.
* **Rücknahme des Portionsfaktors (B5, ausgebaut am 13.08.2026)**: Beim Entfernen eines
  Datenfelds ist der Prüfstand wichtiger als beim Einbauen — das Feld kann auf **anderen
  Geräten noch liegen**. 10 Prüfungen auf `unflattenWeek()`/`dayNutOf()`/`makeEntry()`, alle
  grün. Der entscheidende Fall: Ein eingehendes `{id, p}` darf **nicht verschwinden**, sondern
  fällt auf die String-Form zurück (`p` wird verworfen) — ein Filter, der wieder ein
  `uids`-Array verlangt hätte, hätte das Gericht dort aus dem Plan gelöscht
  (`docs/TROUBLESHOOTING.md` §73). Zusätzlich geprüft: `{id, uids, p}` behält die Zuweisung,
  im Ergebnis steckt **nirgends** mehr ein `"p"`, und die Tagesbilanz zählt wieder volle
  Portionen.
* **Meal-Filter (B7)**: `recipeFilterHtml()` und `recipeMatchesFilters()` brauchen nur einen
  Stub für `libraryRecipes()`. 17 Prüfungen, alle grün. Wichtig sind die Randfälle, nicht das
  Filtern selbst: unter sechs Meals **und** bei einem Bestand ganz ohne Merkmale entsteht keine
  Reihe, und in beiden Fällen werden aktive Filter geleert — ein Filter, dessen Chip nicht mehr
  sichtbar ist, würde sonst unsichtbar weiterfiltern und die Liste grundlos halb leer zeigen.
* **Rückblick (B9/B10)**: `archiveWeek()`, `sanitizeWeekStats()` und `rueckblickHtml()` lassen
  sich mit einem winzigen Stub-State (DAYS, `dayNutOf`, `goalTargetsForDay`, `nfmt`) schneiden;
  geprüft wird am erzeugten Markup. 23 Prüfungen, alle grün. Der entscheidende Regressionstest
  ist **derselbe Balken in zwei Reihen**: Eine Woche mit 2000 kcal bei Ziel 2000 muss ihre Höhe
  behalten, egal ob die Nachbarwoche bei 2000 oder bei 2800 liegt. Genau das war vorher nicht so
  (`docs/TROUBLESHOOTING.md` §72). Dazu: Ziel = 71 % der Skala, 140 % läuft an die Decke,
  gleiche Zielerreichung bei verschiedenen Zielen ergibt gleiche Höhe, Rückfall aufs heutige
  Ziel bei Wochen ohne `target`, und der Streak bricht bei 4 von 7 Tagen.
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
  **Firestore-Roundtrip-Stub:** Ein einfaches `doc = Object.assign({}, doc, payload)` (bildet
  `merge: true` nach) reicht nicht aus, um die zweite Hälfte derselben Fehlerklasse zu treffen
  (Ziffer 44) — Firestore liefert Objektschlüssel bei jedem Snapshot **sortiert** zurück, lokal
  gebaute Objekte nicht. Die Auslieferung an den Prüfstand muss deshalb durch `sortKeysDeep(...)`
  laufen: Objektschlüssel rekursiv sortieren, Arrays unangetastet lassen. Ohne diesen Schritt
  bleibt der Prüfstand blind für jede Reihenfolge-Differenz, die erst durch einen echten
  Firestore-Umweg entsteht — ein Bug, der auf zwei echten Geräten sofort zuckt, im Prüfstand aber
  grün bleibt. **`makeDevice()`-Bauart:** den ausgeschnittenen Funktionsblock wörtlich in
  `function makeDevice() { … }` setzen und mehrfach instanziieren — jedes „Gerät" behält seine
  eigenen Modulvariablen (`syncGid`, `lastPushedJSON`, `groupSyncFailed`, …), ohne dass der
  Produktionscode angefasst wird. Konstanten (`DAYS`, `MEALS`, `ACTIVITY`, `KG_MIN`/`KG_MAX`, …)
  dürfen außerhalb geteilt werden, sie unterscheiden sich nie zwischen Geräten.
  **Regel „kein berechneter Wert im Push":** jede Zusicherung, die einen Push-Payload prüft, muss
  mindestens ein Szenario mit einem *berechneten* Feld (Beispiel: `shopPersons()` in der Gruppe)
  gegen den *rohen* State-Wert abgleichen — sonst deckt der Test genau die Asymmetrie nicht auf,
  die `dataJSON()`/`pushNow()` unbrauchbar macht, obwohl der reine Reihenfolge-Vergleich längst
  grün ist.
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

* **`offServingSize()`** (OFF-Packungsgröße) rein als Textparser ausgeschnitten und gegen eine
  Fallliste durchrechnen: reines Gewicht/Volumen ("65 g", "500 g", "1 L", "1 kg") liefert
  `{grams, count: null}`, erkannte Stückzahl ("1 Stück (65 g)", "6 x 65 g", "6x65g", "6 × 65 g",
  "2 Scheiben (30g)", "4 Riegel à 40 g") liefert `{grams, count}` mit `grams` = **ein** Stück,
  leerer/fehlender Text, fehlende Einheit ("1 Portion") und "0 g" liefern `null`. Wichtigster
  Regressionsfall: reines Gewicht darf **nie** `count` setzen, sonst schaltet `applyBarcode()`
  eine Mehltüte fälschlich auf „Stück" um. Zweiter Regressionsfall: `serving` muss `false` sein,
  wenn der Wert aus `quantity` kam — sonst legt `quickAddByBarcode()` eine ganze Packung als
  Portion an (siehe `docs/TROUBLESHOOTING.md` Ziffer 41). Kommas als Dezimaltrennzeichen
  ("32,5 g", "1,5 l (1,58 kg)" — mehr als eines im selben Text) gehören in die Fallliste.
* **`quickAddByBarcode()`** (Barcode-Schnellzugriff aus dem Wochenplan) mit gestubbtem
  `scanBarcodeLive()`/`fetchOffNutrition()`: vollständige OFF-Daten (Name, alle vier Nährwerte,
  auswertbare `serving_size`) → Meal wird still angelegt (`quick: true`) und direkt eingeplant ·
  nur `quantity` ohne Stückzahl ("500 g"), fehlende `serving_size` oder unvollständige Nährwerte →
  `openRecipeForm(null, prefill)` öffnet sich vorausgefüllt (inkl. Zutaten-Zeile mit den
  OFF-Nährwerten je 100 g, ohne Menge) statt zu raten · zweiter Scan desselben Barcodes → kein zweiter
  `state.recipes`-Eintrag, die bestehende ID wird eingeplant (Dedupe über `r.barcode === code`) ·
  OFF-Fetch wirft (offline) → Toast statt unbehandeltem Promise, kein Halbzustand im Plan.
* **`pieceFoods()` / `pieceSearch()` / `quickAddPiece()`** (Schnelleintrag für Stück-Artikel). Der
  `FOODS`-Block lässt sich sauber zwischen `/*FOODS_START*/` und `/*FOODS_END*/` ausschneiden. Zu
  prüfen: jeder zählbare Eintrag hat ein Stückgewicht > 0 (Ausnahme: die schon je Stück erfassten
  wie das Ei) · die Hochrechnung gegen eine **Handrechnung** (Apfel 52 kcal/100 g × 150 g = 78) ·
  `PIECE_TOP` löst vollständig auf, sonst fällt ein Tippfehler im Namen erst in der UI auf ·
  `pieceSearch("b")` liefert nichts (dieselbe 2-Zeichen-Grenze wie `foodSearch`) · zweimal
  `quickAddPiece` mit demselben Lebensmittel → **ein** `state.recipes`-Eintrag (Dedupe über `qf`),
  zwei Slot-Einträge, Tagesbilanz doppelt, Einkaufsliste **eine** Zeile „2× Banane" in der
  richtigen Warengruppe · nach dem Leeren des Slots räumt `pruneQuickRecipes()` es weg, ein noch
  eingeplantes bleibt stehen.

  Messfalle dabei: `buildShoppingList()` zählt in der aktuellen Woche nur **ab heute**
  (`DAYS.slice(todayIdx)`). Ein fester Wochentag im Test läuft je nach Kalendertag stillschweigend
  leer — den Tag über `todayDayKey()` wählen.

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

#### Kamera-Constraints und Fokus mitmessen

Der Attrappen-Track braucht `getSettings()`, `getCapabilities()` und ein `applyConstraints()`, das
jeden Aufruf mitschreibt. Damit ist prüfbar, was sonst nur am Gerät sichtbar wäre:

* die angeforderten Constraints (`aspectRatio` als `ideal`, nicht `exact` — siehe
  `docs/TROUBLESHOOTING.md` Punkt 63),
* `--scan-ar` auf `.scanvid` gegen `settings.width / settings.height`,
* `focusMode: "continuous"` wird angefordert, **wenn** die Capability da ist — und **nicht**, wenn
  sie fehlt (Punkt 64); dazu der Hinweistext, der nichts versprechen darf,
* `cleanup()`: alle Tracks gestoppt, `resize`-Listener abgemeldet (ein `resize` nach dem Schließen
  darf keinen Constraint mehr auslösen).

#### Scanner-Geometrie in beiden Geräte-Haltungen messen

Hoch- und Querformat je in einem `iframe` fester Größe (390×844 und 844×390), Kamera-Attrappe mit
passenden Stream-Maßen (iOS dreht den Stream mit, also im Querformat 1920×1080 und im Hochformat
1080×1920). Geprüft wird: `--scan-ar`, die Bühnengröße, **ob der Kasten in den Bildschirm passt**
(`box.bottom <= viewport.height`) und ob die Reihenfolge der Kinder gleich bleibt. Genau so kamen
die zwei Defekte der festen `62svh`-Grenze heraus (64 px verschenkte Breite im Hochformat,
abgeschnittener Foto-Knopf im Querformat) — durch Hinsehen wäre keiner aufgefallen.

Drei Fallen im Prüfstand selbst:

* **Ein offen gelassener Scanner hängt den Browser auf.** Die Decode-Schleife ist eine
  `setTimeout`-Kette, und `--virtual-time-budget` springt von Timer zu Timer — die Schleife läuft
  endlos schnell, das Budget läuft nie ab. Beim Messen deshalb `window.BarcodeDetector` auf
  `undefined` setzen und `loadZXing()` hängen lassen; beim Ablauf-Prüfen den Scanner jedes Mal
  schließen. Siehe `docs/TROUBLESHOOTING.md` Punkt 66. Den Browserstart zusätzlich mit
  `WaitForExit(<ms>)` begrenzen und danach hart beenden.
* **Zwei `iframe`s gleichzeitig** gegen `python -m http.server` (einfädig) sind ein Hänger-Risiko —
  nacheinander messen.

* **`loadZXing()` nicht ablehnen lassen, sondern hängen lassen** (`new Promise(function(){})`).
  Headless Edge hat keinen `BarcodeDetector`, ein abgelehntes `loadZXing()` überschreibt den
  Hinweistext mit einer Fehlermeldung — der Test misst dann den Fehlerzustand statt der
  Bereitschaft. Das war zuerst als echter Befund gemeldet und war keiner.
* Fokus-**Fähigkeit** und Fokus-**Anwendung** müssen getrennte Funktionen sein. Ein
  `if (applyFocus("single-shot") || …)` als Fähigkeitsprüfung stellt beim Prüfen schon scharf.

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

**Wichtige Einschränkung: `--window-size` wirkt nicht immer.** Mit `--headless=new` und
`--dump-dom` wurde die Flagge in einem Durchlauf komplett ignoriert — `clientWidth` blieb bei
477 px, egal ob 320, 360 oder 390 übergeben wurde. Die Regel „mitloggen" ist damit nicht
Kür, sondern das Einzige, was die Messung überhaupt einordnet: Ohne sie hätte der ganze
Durchlauf Desktop-Regeln geprüft und als mobile Ansicht protokolliert.

**Der verlässliche Weg für schmale Breiten ist der iframe** (weiter unten ausführlich). Er
funktioniert auch ohne laufenden Server über `file://`, dann braucht Edge zusätzlich
`--allow-file-access-from-files`, damit die Rahmenseite den DOM des Rahmens lesen darf:

```text
--headless=new --allow-file-access-from-files --dump-dom  file:///…/frame.html?w=390
```

Der Rahmen liefert dann exakt die gewünschte CSS-Breite. Trotzdem die tatsächliche Breite
zurückmelden lassen (`soll=390 ist=390`) — bei sichtbarer Scrollleiste fehlen sonst 15 px und
ein Test „bei 681 px" läuft in Wahrheit bei 666 px, also noch im mobilen Zweig.

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

### Echte Wischgesten messen (CDP-Prüfstand)

Wisch- und Snap-Verhalten lässt sich nicht mit `scrollTo()` prüfen — ein programmatischer Lauf
nimmt einen anderen Weg durch den Browser als ein Finger. Für den Wochenplan-Streifen gibt es
deshalb einen eigenen Prüfstand:

1. Edge headless mit `--remote-debugging-port` und `--user-data-dir` starten.
2. Über einen minimalen WebSocket-Client (Python-Standardbibliothek, kein npm) am
   DevTools-Protokoll anmelden.
3. `Emulation.setDeviceMetricsOverride` (390 × 844, `mobile: true`) und
   `Emulation.setTouchEmulationEnabled` setzen — sonst greift die Handy-Abfrage nicht.
4. Die Geste mit `Input.dispatchTouchEvent` fahren: ein `touchStart`, viele `touchMove`
   über ~300 ms, ein `touchEnd`.
5. Danach `scrollLeft` gegen die Snap-Punkte prüfen.

Fallen dabei:

* **`Input.synthesizeScrollGesture` mit `gestureSourceType: "touch"` bewegt headless nichts.**
  Es kommt kein einziges `scroll`-Ereignis an. `"mouse"` funktioniert, ist aber ein Rad-Scroll
  und damit fast augenblicklich — für Snap-Fragen zu grob. Nur `Input.dispatchTouchEvent`
  liefert eine brauchbare Geste.
* **`Page.screencastFrame` muss quittiert werden** (`Page.screencastFrameAck`), sonst liefert
  Chrome genau ein Bild und schweigt danach.
* **Ein bestehender Fund braucht immer die Gegenprobe am alten Stand.** `git show HEAD:index.html`
  als zweite Datei ausliefern und denselben Test dagegen fahren — sonst ist nicht belegt, dass
  die Änderung überhaupt etwas bewirkt hat.
* **Der Browser der Chrome-Erweiterung taugt dafür nicht**: sein Tab läuft verborgen
  (`document.hidden === true`), `requestAnimationFrame` tickt dort nicht, Sanftläufe und
  Screenshots laufen ins Leere.

**Nachtrag 08.08.2026 — im `iframe`-Aufbau ist gar keine Geste messbar.** Beim Sheet-Umbau des
Wochenplans liefen beide Wege ins Leere, und zwar *lautlos*:

* `Input.dispatchTouchEvent` erzeugte im Rahmen zwar DOM-Ereignisse (nachgezählt: ein
  `touchstart`, 17 `touchmove`, ein `touchend`), aber **kein Scrollen** — `scrollLeft` blieb 0.
* `Input.synthesizeScrollGesture` geht durch den Compositor und scrollt deshalb immer das
  **Top-Dokument**, nie einen Scroller innerhalb eines `iframe`.

Beides zusammen ergab einen Prüfstand, der fröhlich „alles sauber" meldete, ohne dass sich
irgendetwas bewegt hatte. **Deshalb gehört in jeden Gesten-Test eine Zusicherung, dass sich
überhaupt etwas verändert hat** — misst der Lauf keine einzige Positionsänderung, muss er
fehlschlagen, nicht bestehen.

Wo eine Geste nicht durchkommt, ist oft die **Ursache** direkt prüfbar und sogar aussagekräftiger.
Statt Ziffer 42 über eine Wischgeste nachzustellen, fährt der Test die Zwischenpositionen mit
`scrollLeft` ab und beobachtet, ob dabei eine Inline-Höhe entsteht — das ist genau der Mechanismus,
der den Snap zerstörte (alter Stand: 11 von 11 Schritten, neuer: keiner).

### Zwei Fallen, die eine Gegenprobe still entwerten

Beide traten beim selben Umbau auf und ließen alten und neuen Stand identisch aussehen:

* **Der Browser-Cache.** `python -m http.server` liefert `Last-Modified` nur sekundengenau. Wird
  der Prüfstand für die Gegenprobe zweimal innerhalb derselben Sekunde neu gebaut, antwortet der
  Server auf das `If-Modified-Since` mit **304** und der Browser zeigt weiter den alten Stand. Im
  Prüfskript deshalb `Network.enable` + `Network.setCacheDisabled: true` setzen. Zur Sicherheit
  einen Marker mitprüfen (`grep -c "plan-sheet" stand/index.html`), damit belegt ist, welcher
  Stand tatsächlich läuft.
* **`requestAnimationFrame` nicht abgewartet.** `fitHeight()` hängt im `scroll`-Handler in einem
  `rAF`. Wer `scrollLeft` setzt und sofort liest, misst den Zustand *davor* — der Test meldete
  für beide Stände „keine Inline-Höhe". Zwischen Setzen und Messen zwei Frames abwarten
  (`await new Promise(r => rAF(() => rAF(r)))`).

### Überlauf gegen `innerHeight` prüfen, nicht gegen `clientHeight`

Im `iframe`-Prüfstand nehmen die klassischen Scrollleisten je 15 px von `clientWidth`/
`clientHeight` weg (bei 390 × 844 bleiben 375 × 829). Ein Test auf
`scrollHeight <= clientHeight` schlägt dadurch **immer** an, auch wenn die Seite gar nicht
scrollen kann. Gegen `innerHeight` prüfen und im Zweifel `scrollHeight - innerHeight` als
`maxScrollY` mit ausgeben — auf dem Handy sind Scrollleisten überlagert und kosten keinen Platz.
* **Nie gegen den echten `localhost`-Port testen, an dem die App schon angemeldet ist.**
  Ein zweiter Port ist eine eigene Origin mit eigenem `localStorage` und ohne Firebase-Sitzung;
  zusätzlich in der Testkopie den `apiKey` auf `DEIN_…` setzen, dann fällt die App auf den
  lokalen Login zurück und schreibt garantiert nichts in die Cloud (siehe
  `docs/TROUBLESHOOTING.md`, Punkt 36).

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

### Echte Handybreite im Browser: iframe statt Fenstergröße

Ein Chrome-Fenster lässt sich unter Windows nicht schmaler als ~500 px ziehen — ein
`resize_window(400, 860)` liefert trotzdem `innerWidth: 851`, und jede Media Query unterhalb
von 560 px bleibt ungetestet. Statt an der Fenstergröße zu drehen, die App in einem `iframe`
fester Breite laden. Der Rahmen bildet einen echten CSS-Viewport, Media Queries greifen darin
ganz normal, und weil dieselbe Origin gilt (`localhost:8000`), ist der komplette DOM des
Rahmens zugänglich — Klicks laufen über die echte Delegation, es wird nichts nachgebaut:

```js
document.documentElement.innerHTML =
  '<body style="margin:0"><iframe id="probe" src="/index.html" ' +
  'style="width:360px;height:740px;border:0"></iframe></body>';
// danach: const w = document.getElementById("probe").contentWindow, d = w.document;
// w.matchMedia("(max-width: 560px)").matches === true
```

Vier Fallen dabei:

* **`about:blank` meldet sofort `readyState: "complete"`.** Vor dem Laden von `/index.html` steht im
  Rahmen ein leeres Dokument. Ein `await warte(() => w.document.readyState === "complete")` ist
  also nach null Millisekunden zufrieden, und ein dort gemerktes `const d = w.document` bleibt für
  immer leer, während die App daneben ganz normal läuft — der Test läuft dann in jeden Timeout,
  obwohl nichts kaputt ist. Auf ein **Merkmal der App** warten
  (`f.contentDocument.querySelector(".app")`) und das Dokument erst danach greifen; besser gleich
  jedes Mal über `f.contentDocument` gehen statt es zu merken.
* **Die Reiterleiste ist statisches Markup und schon vor dem Login anklickbar.** `enterApp()` setzt
  `state.tab` hart auf `"home"` — ein früherer Klick auf `[data-tab="plan"]` ist danach wirkungslos.
  Erst warten, bis `.app` die Klasse `authing` verloren hat, dann klicken. Ohne Cloud fällt `boot()
  ` außerdem erst nach 6 s auf den lokalen Modus zurück; das Wartefenster muss darüber liegen.
* **Klassische Scrollleisten verkleinern den `fixed`-Bezug.** Im Rahmen sind die Leisten
  nicht wie auf dem Handy überlagert, sondern nehmen Platz weg: `position: fixed; inset: 0`
  spannt dann nur 345×725 statt 360×740. Eine Unterkante bei 725 px ist deshalb kein Fehler.
  Nicht gegen `innerHeight` prüfen, sondern gegen `overlay.clientHeight` — bündig heißt
  `sheet.getBoundingClientRect().bottom === overlay.clientHeight`.
* **Eine `querySelectorAll`-Liste überlebt kein `innerHTML`.** Wer Knoten vor einer Aktion greift,
  die neu zeichnet (jeder `paint()`-Aufruf im Picker, jedes `render()`), misst danach abgehängte
  Elemente — die melden brav `height: 0`. Das sieht wie ein Layout-Befund aus und ist keiner. Vor
  jeder Messung frisch abfragen.
* **Der lokale Teststand ist am echten Cloud-Konto angemeldet** (`lastprofile.cloud === true`).
  Im Rahmen deshalb nur lesen und Ansichten öffnen; keine Meals anlegen oder ändern, sonst
  landet der Testbestand in der echten Cloud (TROUBLESHOOTING §36 schützt nur `localStorage`,
  nicht die Firebase-Anbindung).

**Headless-Variante derselben Falle** (Edge, `--headless=new`, 13.08.2026 gemessen):
`--window-size` wirkt auf den CSS-Viewport, aber **nur nach oben** — `--window-size=700,900`
ergibt `innerWidth: 700`, `--window-size=390,844` ebenso wie `360` ergibt immer `504`. Wer
darunter messen will, stellt das zu prüfende Bauteil in einen Container fester Breite
(`.frame { width: 360px }`) statt am Fenster zu drehen; Grid und Flex rechnen in der
Containerbreite, genau das soll gemessen werden. **Aber:** Media Queries hängen weiter am
Viewport. Bei 504 px greift `max-width: 680px` — die 560er- und 400er-Zustände nicht. Ohne
Gegenprobe misst man sonst die Desktop-Variante und hält sie für die mobile. Die Gegenprobe ist
billig: `matchMedia("(max-width:680px)").matches` und `getComputedStyle(el).display` mit
ausgeben. Genau daran ist der erste Anlauf der Tab-Kapsel-Messung aufgefallen — die Zahlen
sahen richtig aus, stammten aber aus dem Desktop-Zustand.

**Vier Reiter in der mobilen Kapsel** wurden so gemessen (echtes Markup + beide `<style>`-Blöcke
aus `index.html`, drei Rahmen zu 360/400/560 px, Light und Dark): vier gleich breite Spalten,
Pille deckt den vierten Reiter (Position und Breite auf ±8 px), kein Reiter läuft aus der
Leiste, die Beschriftung „Fortschritt" passt bei 360 px (49 px Text auf 80 px Spalte), Reiter
bleiben 46 px hoch. Der Screenshot gehört dazu — die Zahlen sagen nichts über Kontrast.

Zum Messen von Animationen in so einem Rahmen siehe TROUBLESHOOTING §54: im verborgenen Tab
zustandsbasiert messen (`getAnimations()`, `pause()` + `currentTime`), nie zeitbasiert.

### Angemeldeter Prüfstand ohne Cloud-Gefahr (Aufbau vom 08.08.2026)

Für alles hinter dem Login braucht es einen Stand mit Daten. Der sichere Aufbau, komplett im
Scratchpad, ohne eine Datei im Projektordner:

1. `index.html` in den Scratchpad kopieren und dabei den `apiKey` auf `DEIN_API_KEY` setzen. Der
   Platzhalter-Test der App (`apiKey.indexOf("DEIN_") !== 0`) lässt Firebase dann gar nicht erst
   starten — die Kopie **kann** nichts in die echte Cloud schreiben. Das Ersetzen mit `assert`
   absichern und abbrechen, wenn es nicht greift.
2. Eigener Port (`8181`, nicht der 8000 aus `test-server.ps1`): eigene Origin, eigener
   `localStorage`, keine bestehende Firebase-Sitzung.
3. Eine `seed.html` daneben, die `wochenkueche_v1__test` und `wochenkueche_profile_v1__test`
   schreibt und dann auf `/index.html` weiterleitet. Das `__test`-Suffix ist Pflicht, weil
   `isTestOrigin()` bei `localhost` greift.

Drei Stolpersteine beim Seed:

* **`plans` nicht mitschreiben.** `load()` prüft `data.plans && typeof === "object"` zuerst — ein
  leeres Objekt ist truthy, und der Migrationszweig für den Einzelplan (`data.plan`) käme nie
  dran. Ohne `plans` wandert `plan` in die aktuelle Woche.
* **Ein Ziel setzen.** Ohne `state.goal` zwingt `maybeStartOnboarding()` in die ersten Schritte,
  und der Plan-Reiter ist unerreichbar. Mit Ziel zeigt die Tagesbilanz außerdem die Balkenform
  statt der Textzeile — beide Fälle wollen geprüft werden, also abschaltbar halten.
* **Auf den Endzustand warten, nicht auf „`#view` hat Inhalt".** Der Cloud-Auth-Zwischenschritt
  („Verbindung wird hergestellt") füllt `#view` sofort; ein Test, der nur darauf wartet, misst
  den Ladebildschirm. Auf eine Zielmarke warten (`.week` vorhanden) und den Reiter notfalls über
  einen echten Klick auf `[data-tab="plan"]` öffnen, damit die normale Delegation läuft.

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

### Pflichtprüfung: Was schriebe ein Push, der genau hier hineinfeuert?

Der Gruppenzeiger `groupId` ist zweimal verloren gegangen (`docs/TROUBLESHOOTING.md` Ziffer 35),
beim zweiten Mal an vier Stellen gleichzeitig. Deshalb bei **jeder** Änderung an
`startCloudSync()`, `activateGroup()`, `joinGroup()` oder `pushNow()` diese Szenarien fahren —
nicht nur den Gutfall:

1. **`CloudSync.load()` wirft** (Kaltstart ohne Netz) → anschließender `pushNow()` darf **kein**
   `groupId`-Feld schreiben. Das ist der Fall, der die Gruppe zweimal gekostet hat.
2. **`fetchMembers()` liefert `[]`** → `enterGroupSync()` muss `"error"` liefern, nicht `"gone"`.
   `getDocs()` wirft offline nicht, sondern gibt das leere Cache-Ergebnis zurück.
3. **`onMembersRemote([])`** → kein Rauswurf. Gegenprobe mit einer Liste *ohne die eigene UID*:
   dort muss der Rauswurf weiterhin greifen, sonst prüft der Test nur das Aussteigen.
4. **Push mitten in `finalizeGroupActivation()`** (Stub, der nach dem Cloud-Write ein `pushNow()`
   einschiebt) → die Cloud muss `groupId: gid` behalten.
5. **Selbstheilung**: Cloud-`groupId` leer, `state.groupId` gesetzt, Gruppe im Stub vorhanden →
   Session steht wieder, Zeiger landet zurück in der Cloud.
6. **Regression regulärer Austritt**: Cloud leer, lokal gesetzt, eigene UID **nicht** in der
   Mitgliederliste → `"gone"`, Zeiger geräumt. Ohne diesen Fall macht Szenario 5 das Verlassen kaputt.
7. **Regression**: normaler Gruppen-Push schreibt `groupId` weiterhin.
8. **`onRemote` mit leerem Cloud-Feld** reißt eine laufende Gruppen-Session nicht ab.

Seit dem Firestore-Offline-Cache (`docs/TROUBLESHOOTING.md` Ziffer 45, „`fromCache` ist kein
Beweis") kommen zwei weitere Pflichtszenarien dazu, **jeweils mit Gegenprobe**:

9. **`fetchMembers()` liefert `{ members, fromCache: true }`** mit einer Liste **ohne** die eigene
   UID → `enterGroupSync()` muss `"error"` liefern, nicht `"gone"`. Gegenprobe mit derselben Liste
   und `fromCache: false`: dort muss weiterhin `"gone"` herauskommen — sonst ist der echte
   Rauswurf kaputt.
10. **`onMembersRemote()` mit einem `fromCache`-Snapshot ohne eigene UID** → kein
    `switchGroup(null)`, kein Rauswurf-Toast. Gegenprobe mit `fromCache: false`: Rauswurf muss
    weiterhin greifen.

Ein Prüfstand, der die Funktionen zeilengenau über ihre **Signatur** statt über Zeilennummern
ausschneidet, lässt sich unverändert gegen `git show HEAD:index.html` bauen — das ist hier die
einzige belastbare Gegenprobe. Beim Gruppenverlust-Fix: alter Stand 13 Fehler, neuer Stand 0.
Stubs für `onGroupRemote`/`onGroupPlansRemote`/`onRecipesRemote` nicht vergessen; fehlen sie,
wirft `enterGroupSync()` in seinen eigenen `catch` und liefert `"error"` — das sieht wie ein
echter Befund aus, ist aber ein Prüfstandsfehler. Im Zweifel gegenprüfen, ob die Funktion in
`index.html` existiert.

### Offline-Testverfahren (Firestore-Cache)

Zusätzlich zum Ausschneide-Prüfstand gehört bei jeder Änderung an der Cache-Initialisierung oder
an `enterGroupSync()`/`onMembersRemote()` ein manueller Test von Hand, da der Prüfstand `getDoc`/
`getDocs` nur stubbt, aber keine echte IndexedDB-Persistenz über einen Browser-Neustart hinweg
prüft:

1. App laden, anmelden, kurz warten bis der erste Sync durchgelaufen ist.
2. Flugmodus an, Seite **neu laden** (nicht nur navigieren — ein reiner In-Memory-Zustand würde
   den Cache-Pfad nicht durchlaufen).
3. Wochenplan, Meals und Einkaufsliste müssen vollständig da sein.
4. Bei einer Gruppe zusätzlich: die Gruppe darf **nicht** verschwunden sein (Ziffer 45).
5. Zum Vergleich vorher einmal denselben Ablauf auf dem alten Stand (`getFirestore(app)` ohne
   Persistenz) fahren — dort ist der Plan nach dem Reload leer, das ist die Nullmessung.

Zusätzlich: `initializeFirestore` künstlich werfen lassen (z. B. per DevTools-Override) →
die App muss weiterhin mit Cloud-Login starten, **nicht** auf den lokalen Login zurückfallen
(Fallback-Test, siehe `docs/ARCHITECTURES.md` „Firestore-Offline-Cache").

**Bekannte Einschränkung, beim Testen nicht mit einem neuen Bug verwechseln:** Wird offline etwas
am Wochenplan geändert und die App lädt neu, *bevor* der Push danach durchgelaufen ist, kann diese
Änderung verloren gehen — vorbestehendes Verhalten der Wochen-Merge-Logik in `startCloudSync()`,
nicht durch den Offline-Cache verursacht. Details in `docs/TROUBLESHOOTING.md` Ziffer 46.

**Alle vier manuellen Tests wurden für dieses Paket durchgeführt** (Offline-Reload, Multi-Tab,
Löschung, Fallback). Dabei drei eigenständige Funde jenseits der ursprünglichen `fromCache`-Logik:
Ziffer 46 (Wochen-Merge verliert unsynced Änderungen, vorbestehend), Ziffer 47 (Live-Update zwischen
zwei Tabs blieb im Test aus, nicht abschließend geklärt ob echter Bug oder Testumgebungs-Artefakt),
Ziffer 48 (`deleteAccountFlow()` kann durch einen fremden/toten `shared/{id}`-Eintrag blockiert
werden, DSGVO-relevant, nicht behoben) und Ziffer 49 (`wipeCache()` stand am falschen Objekt und lief
nie — **gefunden und noch im selben Arbeitsschritt behoben**, per direktem IndexedDB-Inhalt vor und
nach dem Fix verifiziert). Der Löschtest selbst (Kern des Fallback- und Löschverfahrens) bestand nach
dem Fix. Details zu allen vieren in `docs/TROUBLESHOOTING.md`.

### Testlücke: ein Prüfstand, der nur den Normalablauf fährt, beweist nichts über Fehlerpfade

Historischer Fall (`docs/TROUBLESHOOTING.md` Ziffer 44, Rückfall vom 06.08.2026): Ein
Sicherheitsnetz gegen wiederholtes `switchGroup()` sah beim Code-Lesen korrekt aus und wurde von
einem Prüfstand bestätigt, der nur die Konvergenz zweier gesund verbundener Geräte prüfte — der
Fehler steckte aber ausschließlich im **Fehlerpfad** (gescheiterter Gruppen-Handshake), den dieser
Prüfstand nie durchlief. Ein Flag, das ein Aufräumpfad (`stopCloudSync()`) zurücksetzt, wurde
*vor* diesem Aufräumpfad gesetzt (in `onRemote()`, direkt vor dem `switchGroup()`-Aufruf, der
`stopCloudSync()` als Erstes ausführt) — dadurch strukturell wirkungslos.

**Regel:** Für jedes Sicherheitsnetz, das einen Fehlerzustand betrifft (`groupSyncFailed`,
`recipesSyncFailed`, `lastGroupAttempt`, …), gehört ein eigenes Prüfstand-Szenario, das den
Fehlerzustand tatsächlich **herbeiführt** — nicht nur eines, das seine Auswirkung im Normalfall
prüft. Konkret beim Gruppen-Handshake: `switchGroup()`/`stopCloudSync()`/`leaveGroupState()`/
`unwatchPending()` echt ausschneiden (sie sind klein und ohne Firebase-Abhängigkeit), nur
`startCloudSync()` stubben — aber **realistisch**, d. h. der Stub muss denselben `catch`-Block
nachbilden, der in Produktion den Fehlerzustand setzt (`syncUid` bleibt gesetzt, `groupSyncFailed
= true`, `lastGroupAttempt` zeigt auf die gescheiterte Gruppe). Ein Stub, der `startCloudSync()`
einfach leer lässt oder immer erfolgreich simuliert, reproduziert exakt die Lücke, die den Fehler
durchgelassen hat. Pflicht-Zusicherungen für dieses Szenario:

1. Mehrere Snapshots mit **derselben** `remoteGid` nach einem gescheiterten Versuch → das
   überwachte Aufräumverhalten (hier: `switchGroup()`) läuft **genau einmal**, nicht pro Snapshot.
2. Gegenprobe gegen `git show HEAD:index.html`: dort **muss** das Verhalten bei jedem Snapshot
   erneut auslösen. Tut es das nicht, misst das Szenario am Fehler vorbei.
3. Gegenprobe „kein Dead-Lock": ein Snapshot mit einer **anderen** `remoteGid` (echter
   Gruppenwechsel) muss das Verhalten erneut auslösen — sonst wurde das Netz gegen einen
   legitimen Wechsel gebaut, nicht nur gegen die Wiederholung.

## 8. Datenschutz-/Security-Regression

Bei Änderungen an Cloud-Daten prüfen:

* keine unnötigen personenbezogenen Daten
* Meal `by` bleibt UID
* keine E-Mail im Gruppen-Mitgliederdokument
* Security Rules bleiben restriktiv
* `get` und `list` nicht versehentlich verwechseln
* UI-Sperren nicht als Security betrachten
* bei `worker/og.js`: nur Meal-Titel und -Foto verlassen `shared/{id}` ohne Anmeldung (über den Service-Account-Zugriff), nicht das komplette Dokument — Firestore-Regel `allow get: if request.auth != null` bleibt unverändert

## 8a. Cloudflare-Worker-Test (`worker/og.js`)

Reine Web-API-Hilfsfunktionen des Workers (Firestore-Wert-Umwandlung, Base64, JWT-Kodierung, `SHARE_ID_RE`) lassen sich unverändert im Ausschneide-Prüfstand testen — Cloudflare Workers nutzen dieselben Standard-APIs (`atob`/`btoa`, `TextEncoder`, `crypto.subtle`) wie der Browser, kein `wrangler` nötig für diesen Teil.

Für den Worker selbst (`HTMLRewriter`, Firestore-REST-Zugriff über den Service-Account):

1. `wrangler dev` gegen eine echte Test-Share-ID.
2. Crawler-Test per User-Agent: `curl -A "facebookexternalhit/1.1" "https://www.paddysmealplan.de/?s=<id>"` → `og:`-Tags im HTML prüfen (siehe `docs/TROUBLESHOOTING.md` Ziffer 50).
3. Facebook Sharing Debugger + ein echter Link in Telegram/WhatsApp.
4. Gegenprobe: Seite ohne `?s=` und ein `?g=`-Link müssen unverändert funktionieren.
5. Worker-Fehlerfall simulieren (falsches Secret) → App muss normal laden, kein Blockieren.

## 9. Testabschluss

Vor Commit:

0. `python syntax-check.py` (Abschnitt 0) — kostet eine Sekunde und ist die einzige Prüfung,
   die bei jeder JS-Änderung ohne Ausnahme läuft
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

### Ein Aufklapper wird programmatisch nie richtig geprüft

Ein Test, der `button.click()` aufruft und danach `aria-expanded` liest, bestätigt nur die
Zustandslogik. Er findet nicht, was am Gerät tatsächlich schiefgeht: dass der Auslöser beim
Öffnen weggewandert ist und der zweite Tipp ins Leere geht (`docs/TROUBLESHOOTING.md`,
Punkt 59). Deshalb gehören zwei weitere Messungen dazu:

* Bildschirmposition des Auslösers **vor und nach** dem Öffnen vergleichen — Versatz muss 0 sein,
  wenn er an einer Kante verankert ist.
* Auf den **alten** Koordinaten `elementFromPoint()` abfragen und prüfen, ob dort noch der
  Auslöser liegt. Erst dann ist belegt, dass ein zweiter Tipp an derselben Stelle wieder trifft.

### Nicht-scrollende Achse mitmessen

Bei jedem Scroll-Container innerhalb eines Snap-Streifens auch die Achse prüfen, die *nicht*
scrollen soll: `scrollWidth === clientWidth` (bzw. `scrollHeight === clientHeight`) und
`getComputedStyle(el).touchAction`. `overflow-y: auto` macht die Gegenachse automatisch mit zum
Scroller, und schon sechs Pixel Überlauf schalten die Wischgeste des Elternteils ab. Die Geste
selbst ist headless nicht auslösbar — diese beiden Werte sind der belastbare Ersatz.

### `env(safe-area-inset-*)` prüfen, ohne ein Gerät mit Notch zu haben

Edge headless simuliert keine Safe-Area — `env()` liefert dort immer den Fallback. Ein Test, der
nur die fertige Seite lädt, misst deshalb **nichts** von der Sache, um die es geht, und wäre auch
dann grün, wenn die `calc()`-Kette gar nicht rechnet.

Der Prüfstand für D6 löst das mit **zwei** Seiten aus demselben ausgeschnittenen `<style>`-Block:

1. **Normalfall** — unverändert. Erwartung: exakt die Werte von vorher (`.wrap` 20 px bzw. 14 px,
   `.tabs` 12 px bzw. 10 px, `.overlay` 16 px). Das ist die eigentliche Regressionsprüfung: Der
   Fallback `0px` darf für alle Geräte ohne Notch nichts verändern.
2. **Gegenprobe** — im CSS wird `env(safe-area-inset-left, 0px)` per Textersetzung durch `44px`
   getauscht. Erwartung: jeder Wert um genau 44 px größer (64/58, 54, 60). Erst das beweist, dass
   die Kette überhaupt greift.

Gemessen wird mit `getComputedStyle`, nicht am Markup. Der `<style>`-Block wird vom Skript
kopiert, nie gelesen — er ist über 200 KB groß (`CLAUDE.md` §13).

**Was damit weiterhin offen bleibt:** wie breit die Aussparung auf einem echten iPhone im
Querformat wirklich ist und ob das Ergebnis gut aussieht. Der Prüfstand belegt die Rechnung,
nicht die Optik.

### Erst prüfen, ob überhaupt Daten da sind — dann messen

Ein Prüfstand, der die echte App mit vorbefülltem `localStorage` startet, kann einen **leeren**
Zustand messen und trotzdem lauter gute Werte melden. Beim Umbau des Wochenplans (09.08.2026)
lief genau das: Die Tagesschlüssel im Testplan hießen `mo`/`di`/`mi`, in der App heißen sie
`mon`/`tue`/`wed` (`const DAYS`). `normalizePlan()` filtert unbekannte Schlüssel still weg — der
Plan war komplett leer, der Test meldete „kein waagerechter Überlauf" für sieben leere Tage und
sah bestanden aus. Aufgefallen ist es erst, als die Einkaufsliste „0 Positionen" zeigte.

**Deshalb: jeder Prüfstand beginnt mit einer Gegenprobe, die laut wird.**

```js
var filled = document.querySelectorAll('.week > .day .slot .filled');
out.push('FILLED n=' + filled.length + (filled.length ? '' : '  <-- PLAN LEER, Messung wertlos'));
```

Dasselbe gilt für die Einkaufsliste: Sie rechnet **ab heute**. Fällt der Testtag auf einen späten
Wochentag, ist die Liste leer, obwohl der Plan gefüllt ist — im Testplan deshalb auch die Tage bis
Sonntag belegen.

Weitere Stolpersteine beim Vorbefüllen (alle gemessen, nicht vermutet):

* `load()` setzt `state.tab` nur auf `home` oder `recipes`. Der Wochenplan ist ein **dritter** Tab
  und lässt sich nur über einen echten Klick auf `#tab-plan` betreten — was ohnehin besser ist, weil
  dann der reguläre Pfad `render() → renderPlan() → initCarousel()` läuft.
* Ohne `state.goal` zwingt `maybeStartOnboarding()` in die ersten Schritte, und der Plan wird nie
  gerendert. Das Ziel-Objekt muss mit (Felder wie die Rückgabe von `computeGoal()`).
* Das alte Einzelplan-Format `data.plan` ist praktisch: `load()` migriert es selbst in die
  aktuelle Woche, man muss den ISO-Wochenschlüssel also nicht nachbauen.

### Auf Bedingungen warten, nicht auf Zeit

`--virtual-time-budget` beschleunigt Timer. Ein `setTimeout(…, 1800)` im Prüfstand feuert dadurch
unter Umständen, **bevor** die App fertig gerendert hat — der Test misst einen halbfertigen DOM.
Das äußert sich als sporadischer Fehlschlag: derselbe Aufruf lieferte in einem Lauf 23 Zeilen, im
nächsten null.

Nicht mit längeren Wartezeiten reparieren, sondern auf die Bedingung pollen:

```js
function waitFor(cond, done, tries) {
  tries = tries || 0;
  if (cond() || tries > 300) { done(tries > 300); return; }
  setTimeout(function () { waitFor(cond, done, tries + 1); }, 50);
}
waitFor(function () {
  return document.querySelectorAll('.week > .day .slot .filled').length > 0;
}, messen);
```

Den Timeout-Fall dabei **ausgeben**, nicht verschlucken — sonst ist man wieder bei stillen
Fehlmessungen.

### Wischgesten sind in diesem Aufbau nicht messbar — drei Anläufe, alle gescheitert

Stand 08.08.2026. Damit niemand ein viertes Mal denselben Weg geht:

| Weg | Ergebnis |
|---|---|
| `Input.dispatchTouchEvent`, App im `iframe` | DOM-Ereignisse kommen an (nachgezählt: 1 × `touchstart`, 17 × `touchmove`, 1 × `touchend`), **kein Scrollen** |
| `Input.synthesizeScrollGesture` im `iframe` | scrollt immer das Top-Dokument, erreicht keinen Scroller im Rahmen |
| Ohne `iframe`, `setDeviceMetricsOverride`, mit **und** ohne `--disable-gpu` | `scrollLeft` bleibt 0 |

**Der A/B-Prüfstand ist das Werkzeug, das „Prüfstand blind" von „Code kaputt" trennt.** Dieselbe
Geste zweimal im selben Browser fahren — einmal gegen den ausgelieferten Zustand, einmal gegen
einen zur Laufzeit per `<style>` korrigierten. Vier mögliche Ausgänge, jeder mit klarer Aussage:

* keiner bewegt sich → Prüfstand blind, der Lauf beweist nichts
* beide bewegen sich → die vermutete Ursache war es nicht
* nur der korrigierte → Ursache und Fix belegt
* nur der ausgelieferte → Analyse verkehrt herum

Ohne diese Gegenüberstellung meldet ein Prüfstand, der gar nichts auslöst, fröhlich „alles
sauber" — genau so ist ein Fix zweimal ungeprüft ans Gerät gegangen.

**Was stattdessen messbar ist:** die Struktur. Für „kann hier gewischt werden" heißt das:
`getComputedStyle(el).overflowX/overflowY`, `touchAction` und `scrollWidth === clientWidth` auf
der Achse, die nicht scrollen soll. Nur `auto`/`scroll` fangen Gesten ab — `hidden` nicht.
Das ist ein Indiz, kein Beweis; die Abnahme am Gerät bleibt Pflicht.
