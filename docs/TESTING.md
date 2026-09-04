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

<!-- REGISTER-ANFANG (erzeugt aus den Ueberschriften, nicht von Hand pflegen) -->

**Register — 48.** Vorne (0 bis 9) die geltenden Verfahren: Syntax-Check,
Smoke-Test, Ausschneide-Pruefstand, Sync-Tests. Dahinter das datierte Fallarchiv —
einzelne Pruefstaende und was ihre Gegenprobe gezeigt hat.

Die Verfahren gibt es auch als Skill: `/smoke`, `/pruefstand`, `/abnahme`, `/deploy`.

| # | Abschnitt |
|---|---|
| · | Testprinzip |
| 0 | Syntax-Check (läuft zuerst, vor allem anderen) |
| 1 | Smoke-Test |
| 2 | Ausschneide-Prüfstand |
| 3 | Ergebnisfortschritt |
| 4 | Was isoliert getestet werden kann |
| 5 | UI-Testregeln |
| 6 | Mehrstufige Abläufe |
| 7 | Sync-Tests |
| 8 | Datenschutz-/Security-Regression |
| 8a | Cloudflare-Worker-Test (`worker/og.js`) |
| 9 | Testabschluss |
| · | Grundregel |
| | **— ab hier Teil B: Fallarchiv, datierte Einzelfälle —** |
| · | Sichtprüfung generierter Bilder: Kontaktabzug statt Einzelaufrufe (15.08.2026) |
| · | Auto-Wochenplaner: zwei Prüfstände, zwei Fragen (16.08.2026) |
| · | Mitgliederlimit: die eine Hälfte ist prüfbar, die andere nicht (16.08.2026) |
| · | Katalog als Nachschlagequelle: eine Erwartung dreht sich um (17.08.2026) |
| · | Stapelkontext und Trefferflächen: `elementFromPoint()` im echten Browser (15.08.2026) |
| · | Ein Listener als Prüfobjekt: die Attrappe muss den Nebeneffekt haben (17.08.2026) |
| · | Ein absichtlich zufälliger Planer braucht festgenagelten Zufall (17.08.2026) |
| · | Zwei Clients ohne Firestore: derselbe Ausgangsstand, zwei Läufe (17.08.2026) |
| · | Eine Reihenfolge prüfen, die beim Lesen richtig aussieht (17.08.2026) |
| · | `tools/pruefstand-zurueck-taste.py` — die Zurück-Taste schließt Overlays (D5) |
| · | Drei Prüfstände zum Ernährungsprofil und zum Rezeptbuch (24.08.2026) |
| · | Paket 1 der Alltagsbefunde: drei weitere Prüfstände (24.08.2026) |
| · | Abnahme am echten Cloud-Konto: `tools/cdp.py` (24.08.2026) |
| · | Ein Zweig, der nur bei leerem Bestand läuft: die Ganzdatei-Kopie (25.08.2026) |
| · | Ein Escape-Fix beweist sich nur mit dem Vorher (25.08.2026) |
| · | `tools/pruefstand-weekstats-sync.py` — und warum er den Fehler nicht fand (25.08.2026) |
| · | `tools/pruefstand-wochenmaske.py` — ein Prüfstand, der absichtlich rot war (26.–29.08.2026) |
| · | Eine Zeile prüfen, indem man sie WEGNIMMT (25.08.2026) |
| · | Mobile Abnahme fernsteuern: `cdp.py messen` (25.08.2026) |
| · | `tools/pruefstand-rueckblick-ziel.py` — der Beweis, dass eine Woche fehlt (26.08.2026) |
| · | `tools/alle-pruefstaende.py` — der Reihenlauf (26.08.2026) |
| · | `tools/pruefstand-grpm-zoom.py` — eine Behauptung über die CSS-Kaskade messen (27.08.2026) |
| · | `tools/pruefstand-einkaufsliste.py` — fünf Läufe über beide Wochenreiter (28.08.2026) |
| · | `tools/pruefstand-gruppe-verlassen-dubletten.py` — der Rückweg aus der Gruppe (28.08.2026) |
| · | `tools/pruefstand-gruppe-beitritt-cache.py` — ein Cache, der lügt (28.08.2026) |
| · | `tools/pruefstand-zuweisung-loeschen.py` — zwei Funktionen gegeneinander (28.08.2026) |
| · | `tools/pruefstand-gruppe-plan-mitbringen.py` — zwei Änderungen, zwei Gegenproben (28.08.2026) |
| · | `tools/pruefstand-sync-abriss.py` — eine Anzeige, die lügt (28.08.2026) |
| · | `tools/pruefstand-waise-uids.py` — die Folge messen, nicht die Datenform (28.08.2026) |
| · | `tools/pruefstand-einkauf-gruppe.py` — die Lücke im Nachbarprüfstand (28.08.2026) |
| · | Ein Prüfstand, der nie lief: `pruefstand-katalog-plan.py` (28.08.2026) |
| · | `tools/pruefstand-cache-reset.py` — was NICHT passieren darf (29.08.2026) |
| · | `tools/pruefstand-kontowechsel.py` — eine Gegenprobe, die in die Schleife läuft (29.08.2026) |
| · | Abnahme am echten Konto: Gruppen-Sync zu zweit (29.08.2026) |
| · | Aufteilung des Codes: was sich am Prüfverfahren ändert (29.08.2026) |
| · | `tools/pruefstand-jahresumschalter.py` — ein Jahrgang, der nicht auftauchen darf (30.08.2026) |
| · | `tools/pruefstand-kalender.py` — die laufende Woche, die im Archiv fehlt (30.08.2026) |
| · | `tools/pruefstand-kalender-layout.py` — ein Überlauf, den niemand sieht (30.08.2026) |
| · | `tools/probe-fortschritt.html` — die Abnahme in der echten App (30.08.2026) |
| · | `tools/probe-onboarding.html` — wie weit der Weiter-Knopf springt (30.08.2026) |
| · | `tools/probe-onboarding-fluss.html` — den Weg messen, nicht das Ziel (30.08.2026) |

<!-- REGISTER-ENDE -->

# Teil A — Die geltenden Verfahren

## Testprinzip

**Nicht vermuten. Ausführen.**

Wenn eine Funktion eine externe API, Browser-API oder komplexe Zustandslogik verwendet, muss sie möglichst mit realem Verhalten getestet werden.

Besonders wichtig:

> Wenn ein Test hängt, kann das ein echter Fehler sein.

Nicht automatisch den Test als defekt betrachten.

## 0. Syntax-Check (läuft zuerst, vor allem anderen)

```powershell
python syntax-check.py --alles
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

### Seit D4: `file://` prüft nur noch den Fallback

Das Firebase-SDK liegt seit dem 23.08.2026 in `vendor/firebase/` und wird **relativ**
importiert. Über `file://` blockiert der Browser genau diesen Import (Modul-Auflösung gegen
eine Opaque Origin) — die App fängt das nach 6 Sekunden über ihren Timeout ab und startet im
lokalen Modus. Nachgemessen am 23.08.2026, jeweils im ersten Bildschirm von `#view`:

| Ladeweg | Überschrift in `#view` |
|---|---|
| `file://`, Stand vor D4 (gstatic per https) | „Willkommen bei Paddy's Mealplan" — Cloud-Einstieg |
| `file://`, Stand nach D4 | „Wie sollen wir dich nennen?" — **lokaler Modus** |
| `http://127.0.0.1`, Stand nach D4 | Cloud-Einstieg, `window.CloudAuth.configured === true` |

Der `file://`-Lauf bleibt als schneller Startbeweis brauchbar — er zeigt aber ab jetzt **nie**
den Cloud-Pfad, und ein „Wie sollen wir dich nennen?" ist dort **kein Befund**. Wer die
Anmeldung, Firestore oder den Sync im Smoke-Test sehen will, muss über HTTP laden:

```powershell
powershell -NoProfile -File test-server.ps1   # http://localhost:8000/
```

Dass das SDK wirklich lokal geladen hat, zeigt am zuverlässigsten die Ressourcenliste der
Seite selbst — nicht das DOM:

```js
performance.getEntriesByType("resource")
  .filter(e => e.name.indexOf(location.origin) !== 0)   // muss [] sein
```

Gemessen wird das aus einer Prüfseite mit `<iframe src="./index.html">` im selben Origin
(dort ist `contentWindow` zugänglich) und das Ergebnis in ein `<pre>` geschrieben, damit
`--dump-dom` es einsammelt. Gegenprobe, ohne die kein Ergebnis zählt: `firebase-app.js`
kurz umbenennen — dann muss `window.CloudAuth` **fehlen** und `#view` trotzdem gefüllt sein.
Am 23.08.2026 genau so belegt.

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

## 2a-2. Ausschneide-Prüfstand für reine Helfer — `pruefstand-mengenanzeige.py`

Nicht jeder Ausschneide-Prüfstand muss die App starten. Geht es um **reine Funktionen**,
genügt es, sie im Wortlaut aus `index.html` und `lib/pdf.js` zu schneiden und in einer
leeren Seite aufzurufen — kein `state`, keine Stubs, kein Onboarding. `qtyLabel()`,
`ingShowsNut()` und `pdfEsc()` sind solche Funktionen.

Geschnitten wird über die **Klammerbilanz**, nicht über ein Regex bis zum Zeilenende. Und:
**Eine nicht gefundene Funktion ist ein Befund, keine Ausnahme.** Ein Prüfstand, der eine
fehlende Deklaration still überspringt, prüft danach nichts mehr und meldet trotzdem grün —
dieselbe Falle wie die Deckungsprobe in `pruefstand-rezepttexte.py`.

**Der eigentliche Grund für diesen Prüfstand ist der PDF-Export.** Die Brüche in der App
sieht man sofort; `pdfEsc()` dagegen ersetzt jedes Zeichen außerhalb von WinAnsi stumm durch
`?`, ohne Fehler und ohne Meldung. Die Einkaufslisten-PDF hätte „? TL Salz" gedruckt. Genau
das ist dort schon einmal passiert, damals mit dem `×`. Deshalb prüft er beides zusammen —
und mit einer Gegenprobe im Prüfstand selbst: `⅓` **muss** weiterhin als `?` durchfallen,
sonst misst die Prüfung nur, dass `pdfEsc()` überhaupt etwas zurückgibt.

### Gegenprobe (29.08.2026)

Zwei Läufe. Der erste gegen den Stand vor der Änderung meldete lediglich „4 Bausteine nicht
gefunden" — das beweist, dass die Funktionen neu sind, **nicht**, dass sie etwas tun. Der
zweite ist der eigentliche Beleg: eine Kopie des neuen Stands, in der gezielt die
Bruch-Zeile in `qtyLabel()` zurückgedreht und `½` aus `WINANSI` entfernt wurde. Ergebnis:
genau 8 von 26 Prüfungen rot — die sieben Bruchfälle und der PDF-Fall für `½`, sonst keine.

Eine Gegenprobe, die nur „Funktion fehlt" meldet, ist keine.

### Lauf F in `pruefstand-einkaufsliste.py`: Würze wird gezählt, nicht summiert

Zwei Rezepte mit **verschiedenen** Salzmengen sind der Kern des Falls — ohne die
Zusammenlegung stünden „½ TL Salz" und „¼ TL Salz" als zwei Zeilen da. Das Öl ist die
Gegenprobe im selben Lauf: Ein Esslöffel Öl ist keine Würze und muss seine Menge behalten.

**Der Zähler wird bewusst ohne feste Zahl geprüft.** Die aktuelle Woche zählt nur die Tage
ab heute (`planDaysAhead`), der Wert hängt also vom Wochentag des Laufs ab — am Montag steht
dort etwas anderes als am Freitag. Ein Prüfstand, der nur an manchen Tagen grün ist, wird
beim ersten roten Montag als kaputt abgetan. Geprüft wird deshalb, was die Aussage trägt:
Es ist **ein** Zähler, und er fasst mehr als ein Meal zusammen.

Gegenprobe am 29.08.2026: `ingIsSeasoning()` in `buildShoppingList()` auf `false` gesetzt →
„1½ TL Salz", drei Prüfungen rot, Rückgabewert 1.

## 2b. Datenprüfstand — `pruefstand-rezepttexte.py`

Nicht jeder Prüfstand schneidet Code aus. `tools/pruefstand-rezepttexte.py` liest
`data/cookbook.js` und rechnet — kein Browser, keine Stubs. Der `pruefstand-`-Präfix ist
trotzdem richtig: `tools/alle-pruefstaende.py` sammelt per `glob("tools/pruefstand-*.py")`
ein und bewertet den Rückgabewert, die Registrierung passiert dadurch von selbst.

Er prüft, ob **jede Zutat aus `ingredients` in `steps` vorkommt**, ob die Anleitung
nummeriert ist, ob `img` auf eine vorhandene Datei zeigt und ob `id` eindeutig ist.

Seit dem 29.08.2026 außerdem der **Herkunftsnachweis je Bild**. Das Impressum sagt zu, dass
zu jedem Rezeptbild festgehalten ist, mit welcher Beschreibung und wann es entstanden ist —
eingelöst von `img/library/bilder-protokoll.json`. Bis dahin prüfte das **niemand**:
`PHOTO_CREDITS` deckt die Katalogbilder bewusst nicht ab, und die Datei-Existenz allein sagt
nichts über den Nachweis. Aufgefallen ist die Lücke dem Agenten `anwalt` im Pushcheck — er
konnte es nur stichprobenartig prüfen und hat genau das gemeldet. **Ein Nachweis, den man
einzeln nachzählen muss, ist auf Dauer keiner.**

Fehlt die Protokolldatei ganz, bricht der Prüfstand ab, statt 36 fehlende Nachweise zu
melden — sonst stünde die wahre Ursache nirgends.

Seit dem 29.08.2026 außerdem die **Mengen**: Jede Zutat muss ein Objekt mit `grams` sein —
ein Freitext-String (`"Oregano, Salz, Pfeffer"`) ist ein Befund. Und jede Zutat in `tl`/`el`
muss ihre Menge auch in der Anleitung nennen, gesucht als `<Zahl> <Einheit> <Zutat>`
(„1 TL Backpulver", „1/2 TL Salz").

**Was diese Prüfung bewusst nicht deckt:** die Menge bei Zutaten in Gramm oder Millilitern.
Der Schreibstandard verlangt sie dort, wo man sie nicht sehen kann — Öl, Süße, Kakao —, aber
bei einer Gramm-Zutat ist sowohl „10 g Backkakao" richtig als auch „Kakao unterrühren", je
nach Rezept. Eine Prüfung, die beides nicht unterscheiden kann, meldet Rauschen. TL und EL
sind der harte Kern: Dort steht die Menge nirgends sonst.

Seit dem 29.08.2026 zusätzlich: **passen die Ernährungsform-Tags zu den Zutaten?**
`vegan`, `vegetarisch`, `glutenfrei` und `laktosefrei` waren bis dahin reine Behauptungen —
`macroBadges()` deckt nur `highprotein` und `lowcarb` ab. Aufgefallen im zweiten Testlauf von
`/rezeptcharge`: Ein frisch gebautes Rezept trug `laktosefrei` und enthielt Magerquark, und
alle Prüfungen blieben grün. Diese Prüfung braucht **keine Grundlinie** — der Bestand ist
sauber, jeder Treffer ist ein Befund.

### Die Grundlinie — wie ein Prüfstand eingeführt wird, der von Anfang an Befunde hat

**Sie ist seit dem 29.08.2026 leer.** Der Mechanismus bleibt trotzdem beschrieben: Er ist die
Antwort auf eine wiederkehrende Lage, und der nächste Prüfstand dieser Art wird sie wieder
brauchen.

Beim Bau meldete er 18 von 34 Rezepten. Ein Prüfstand, der ab Tag eins rot ist, blockiert
die Suite und wird abgeschaltet — der Befund wäre damit teurer als sein Nutzen. Die Lösung
ist eine **Grundlinie im Skript**, die den Bestand vom Einführungstag festhält:

| Stufe | Bedeutung | Rückgabewert |
|---|---|---|
| `OFFEN` | steht in der Grundlinie — Bestand, bekannt, noch nicht nachgearbeitet | 0 |
| `REGRESSION` | alles andere: neues Rezept mit fehlender Zutat, fehlende Nummerierung, **oder eine wachsende Fehlerliste an einem Bestandsrezept** | 1 |
| `BEHOBEN` | ein Fall aus der Grundlinie ist verschwunden — Zeile streichen | 0 |

`BEHOBEN` ist der Teil, den man leicht vergisst. Ohne ihn verrottet die Grundlinie: Sie
enthielte irgendwann Fälle, die es nicht mehr gibt, und schaltete die Prüfung für diese
Rezepte dauerhaft ab, ohne dass es je auffällt. Das ist derselbe Mechanismus wie eine
Kennung in `docs/ABDECKUNG.md`, die nur eingetragen wird, damit Ruhe ist.

„Grün" heißt hier **keine Regression**, nicht „fehlerfrei".

**Am selben Tag wurde der Bestand vollständig nachgearbeitet** — alle 35 Rezepte auf Zutaten
mit Menge und nummerierte Anleitungen umgestellt. Damit sind `GRUNDLINIE` und
`UNNUMMERIERT_ALT` leer, „grün" heißt bei diesem Prüfstand wieder „keine Befunde", und der
Eintrag in `TEILWEISE` von `tools/alle-pruefstaende.py` ist entfallen. Wer dort oder in einer
Grundlinie wieder etwas einträgt, schaltet die Prüfung für diesen Fall dauerhaft ab — das
gehört begründet und wieder entfernt, sobald der Umbau durch ist.

### Gegenprobe

```powershell
git show HEAD:data/cookbook.js > alt.js
python tools/pruefstand-rezepttexte.py alt.js
```

Zwei Läufe, sonst zählt das Ergebnis nicht — durchgeführt am 29.08.2026:

1. Testfassung mit einem **neuen** Rezept, dessen Zutat in der Anleitung fehlt und dessen
   Schritte nicht nummeriert sind → meldete beide Punkte als `REGRESSION`, Rückgabewert 1.
2. Testfassung, in der `protein-pancakes-skyr` korrigiert und nummeriert ist → meldete
   dreimal `BEHOBEN`, Rückgabewert 0.

Für die Mengenprüfung am selben Tag noch einmal, gegen den Stand vor der Umstellung:
`python tools/pruefstand-rezepttexte.py alt.js` meldete **162 Regressionen** (32 Rezepte mit
Freitext-Zutaten, dazu die fehlenden Nummerierungen), derselbe Lauf gegen den neuen Stand
**keine**. Ohne diesen Gegenlauf wäre nicht belegt, dass die Prüfung überhaupt greift.

### Was der Auflöser leisten muss — und wo seine Grenze liegt

Ein Wort-für-Wort-Vergleich meldet 31 von 34 Rezepten und ist damit wertlos: „Olivenöl"
gegen „mit Öl und Kräutern mischen" ist kein Befund, sondern normales Deutsch. Es braucht
drei Nachsichten — Wortstamm/Kompositum, Sammelwörter (`Beeren`, `Kräuter`, `Öl`) und
Gewürze, die von „würzen"/„abschmecken" gedeckt sind.

Fünf Fallen dabei, alle dokumentiert in `docs/TROUBLESHOOTING.md` §141 — **vier davon sind
falsche Negative**, also Fälle, in denen der Prüfstand grün blieb und trotzdem nichts maß:

* **Der Kompositum-Rückfall darf nicht zu kurz greifen.** Bis auf zwei Zeichen herunter galt
  „Erdnussbutter" als erwähnt, weil `er` in „Haferflocken" steckt. Grenze jetzt vier
  Zeichen; kurze Grundwörter wie „Öl" und „Ei" stehen namentlich in `SAMMEL`.
* **Jeder Textvergleich braucht eine Wortgrenze vorn.** Ohne sie belegte `Reis` sich in
  „**P**r**eis**elbeeren" und `Ei` in „**ei**ne" — die Kollision, die `CLAUDE.md` §15
  namentlich nennt. Hinten darf keine Grenze stehen, sonst findet „Zucchini" die
  „Zucchinischeiben" nicht mehr.
* **Ein leerer Kopf ist ein Freifahrtschein.** `frisch\w*` als Füllwort fraß das Grundwort
  von „Frischkäse, light" mit; übrig blieb der leere String, und der galt als „immer
  erwähnt". `kopf()` gibt jetzt nie leer zurück.
* **Ein formatabhängiges Regex verliert Deckung, ohne es zu sagen.** Ein Rezept mit einem
  Umbruch nach `{` fiel aus der Erkennung: 33 statt 34 geprüft, Ergebnis weiter grün. Das
  Skript gleicht die erkannte Anzahl jetzt gegen die Zahl der `id:`-Felder ab und **bricht
  ab**, statt leise weniger zu prüfen.
* **Die Reihenfolge der Zutatenliste ist nicht mechanisch prüfbar.** Der Versuch meldete
  24 von 34. Die Regel gilt trotzdem, sie steht aber im Schreibstandard
  (`data/CLAUDE.md`), nicht im Skript.

Dazu die Verwaisung in der Gegenrichtung: Wird ein Rezept umbenannt oder entfernt, bleibt
seine Zeile in `GRUNDLINIE` stehen und deckt für immer eine `id`, die es nicht mehr gibt.
Der Prüfstand meldet solche Zeilen jetzt als `BEHOBEN`.

**Wie die vier gefunden wurden:** nicht vom Prüfstand selbst, sondern durch eine
Gegenprüfung in einer zweiten Sitzung, die verstellte Kopien des Katalogs durch das Skript
schickte (erfundene Zutat, leere `steps`, fehlendes Bild, behobener Grundlinienfall). Das
ist der Weg, der bei einem neuen Prüfer verbindlich ist: **Ein Prüfer, den niemand geprüft
hat, meldet „sauber" — und man glaubt ihm** (`CLAUDE.md` §18b).

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
* **Rezept-Nährwerte gegenrechnen (`tools/rezept-makros.py`, 15.08.2026)**: Kein Prüfstand im
  üblichen Sinn, sondern ein **Datenprüfer** — er schlägt jede Zutat in `FOODS` nach und
  vergleicht die Summe mit den angegebenen Rezeptwerten. Pflicht bei jedem neuen Rezept im
  Katalog, weil ein Rezept die einzige Stelle ist, an der falsche Zahlen wie richtige aussehen.
  Beim ersten Lauf fand er, dass **alle neun Katalog-Rezepte geschätzte Werte hatten** (bis zu
  86 % daneben) — und beim zweiten einen Fehler in sich selbst: „Zuckerschoten" auf „Zucker"
  gematcht. **Deshalb gibt `--json` die Zuordnung aus**: Wer nur die Summe prüft, sieht nicht,
  ob sie aus den richtigen Lebensmitteln entstanden ist.
  Toleranz 12 % — enger prüfen meldet vor allem Garverluste und Rundungen.
* **Rezeptbuch (15.08.2026)**: `COOKBOOK`, `cookbookVisible()`, `isAdopted()`,
  `adoptFromCookbook()` samt `sanitizeRecipe()` geschnitten — beim Ausbau auf 30 Rezepte
  zusätzlich `PHOTOS`, `PHOTO_RULES`, `LIB_IMG`/`libPhoto()`, `photoFor()`, `safeImage()`,
  `macroBadges()`, `recipeNut()`, `copyFromCookbook()`, `STARTER` und `addStarterMeals()`. **100 Prüfungen, alle grün.**
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
  **Zusagen des Katalogs (ergänzt beim Ausbau auf 30)** — alle **sechs** Kategorien besetzt
  (vorher nur die drei häufigen geprüft, Dessert/Beilage/Getränk waren leer und niemand hätte
  es gemerkt), mindestens 30 Rezepte, weil die Zahl in `PRODUCT.md` und im Pro-Versprechen
  steht.
  **Eigene Bilder (`img`/`libPhoto`)** — sechs Prüfungen: jedes Rezept hat ein Bild, jeder
  Dateiname **existiert wirklich**, kein Dateiname trägt einen Umlaut, `photoFor()` nimmt das
  Bibliotheksbild, die übernommene **Kopie zeigt dasselbe Bild** (Auflösung über `lib`, sie
  hat eine eigene `id`), das eigene Foto des Nutzers schlägt es, und ein ausgemustertes Bild
  fällt auf den kuratierten Schlüssel zurück.
  **Der Dateisystem-Abgleich ist der Kern davon.** Unter `file://` kann der Browser den Ordner
  nicht lesen, deshalb legt der Generator die Liste der vorhandenen `.webp`-Dateien als
  Konstante `DATEIEN` in die Seite. Ohne ihn prüft die Seite nur, dass *irgendein* Name
  dasteht — ein Tippfehler ergibt in der App eine leere Bildfläche und fällt beim Lesen des
  Codes nicht auf. **Gegenprobe gefahren**: `rotes-linsen-dal.webp` → `rotes-linsen-dahl.webp`
  im Prüfstand, und die Prüfung wird rot.
  **Eine Fehlprüfung war zuerst falsch gedacht:** „ohne Bild kein Pfad nach img/library" löschte
  `img` am übergebenen Objekt — `LIB_IMG` ist aber aus dem Katalog gebaut, die Map kennt die
  `id` weiter. Der Rückfall entsteht dadurch, dass `img` am **Katalogeintrag** fehlt.
  **Der Aufrufweg des Filters** — drei Prüfungen, entstanden aus einem Fund des Nutzers:
  `recipeMatchesFilters()` direkt als `filter`-Callback (dort kommt der **Index** als zweites
  Argument an), mit ausdrücklich übergebenem Set, und ohne zweites Argument. Die erste war vor
  der Härtung ein `TypeError` — gegengeprüft, indem `instanceof Set` im Prüfstand auf `||`
  zurückgedreht wird. Getestet wird hier bewusst nicht die Filterlogik, sondern die **Signatur**:
  Die Logik war korrekt, der Aufruf nicht.
  **Startmeals** — je Ernährungsform (`alles`, `vegetarisch`, `vegan`) durchgespielt: genau fünf
  Meals, jedes trägt `lib`, jedes besteht `fitsDiet()`, Frühstück/Hauptgericht/Snack sind
  vertreten, keines trägt einen Pfad in den Nutzerdaten, und jedes findet sein Bild trotzdem
  (über `lib`). Dazu der Fall `vegan` + `glutenfrei`: trotzdem fünf, alle glutenfrei, und
  mindestens drei Kategorien — sonst hätte das Auffüllen vier Hauptgerichte ergeben. Und die
  Bedingung, die Dubletten verhindert: bei **nicht** leerem Bestand kommt nichts dazu.
  **Eine Prüfung ist erst durch die Gegenprobe entstanden:** Ein Fleischgericht in der veganen
  Liste ließ alles grün, weil `fitsDiet()` es herausfilterte und `addStarterMeals()` still
  auffüllte. Das Ergebnis prüft also nur den Filter, nie die Kuration — seither prüft
  `dietOk()` jede Liste einzeln.
  **Bildschlüssel** — jeder gesetzte `photo` steckt in `PHOTOS`; ein Tippfehler wäre sonst
  unsichtbar **und wirksam**, weil `photoFor()` still auf die Stichwortregeln zurückfällt,
  also genau auf die Zuordnung, die im Katalog danebengreift. Dazu drei Prüfungen am neuen
  Feld: dass es die Übernahme überlebt, und dass Freitext (`"../../etc/passwd"`) und
  Nicht-Strings verworfen werden — es kommt bei geteilten Meals von außen herein.
  **Merkmal gegen Badge** — kein Katalog-Meal darf `highprotein`/`lowcarb` tragen, ohne die
  Schwelle aus `macroBadges()` zu erreichen. Sonst widerspricht die Karte ihrem eigenen Filter.
  **Gegenprobe gefahren** (Prüfstand-HTML verfälscht, nicht `index.html`): ein Bildschlüssel auf
  `"gibtsnicht"` und ein entfernter Tag lassen genau die beiden neuen Prüfungen rot werden.
  Ohne diesen Schritt wüsste niemand, ob sie überhaupt etwas messen.
* **Bild-Werkzeug (`tools/test-meal-bilder.py`, 15.08.2026)**: Kein Ausschneide-Prüfstand,
  sondern ein eigener Test für `tools/meal-bilder.py` — er lädt das Skript als Modul und
  kommt **ohne einen einzigen API-Aufruf** aus. **41 Prüfungen, alle grün** — dazugekommen sind `dateiname()` (die `id` schlägt den Namen, Umlaute werden umgeschrieben) und die Geschirrwahl (`NAME_GESCHIRR` überstimmt die Kategorie, ohne Getränke und normale Frühstücke zu verändern).
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
* **Ziel-Quote (B9/B10)**: `archiveWeek()`, `sanitizeWeekStats()` und `zielQuote()` lassen
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

# Teil B — Fallarchiv

Ab hier stehen **datierte Einzelfälle**: einzelne Prüfstände, was sie gemessen haben und was
ihre Gegenprobe gezeigt hat. Sie sind Belege und Erfahrungsberichte, keine Vorschriften.

**Wer wissen will, WIE geprüft wird, liest Teil A** (Abschnitte 0 bis 9 und die Grundregel).
Hier nachschlagen, wenn die Frage lautet: „Hatten wir diesen Fall schon einmal?"

Die Trennung ist bewusst: In einer Datei von 140 KB geht sonst das Geltende zwischen den
Belegen unter, und beim Suchen findet man den Einzelfall von 2026 statt der Regel.

## Sichtprüfung generierter Bilder: Kontaktabzug statt Einzelaufrufe (15.08.2026)

30 Bilder einzeln zu öffnen ist der sichere Weg, den Vergleich zu verlieren — Stilbrüche sieht
man nur **nebeneinander**. Bewährt hat sich ein Kontaktabzug aus dem Skript: alle Bilder auf
eine Kachelbreite skaliert, zwei Spalten, Nummer und Gerichtname eingezeichnet, als PNG in den
Scratchpad. Zwei Blätter für 30 Bilder sind noch lesbar genug, um Text im Bild zu erkennen.

Geprüft wird in dieser Reihenfolge, und die erste Frage ist die rechtlich wichtige:

1. **Text, Logos, Marken** im Bild — der realistische Fallstrick, nicht das Motiv selbst.
2. **Diät-Treue**: Zeigt ein veganes Gericht Fleisch, Ei oder Käse? Das ist bei einer App, die
   Veganer gezielt anspricht, kein Schönheitsfehler.
3. **Geschirr**: Liegt Brot auf einem Teller und nicht in einer Schüssel?
4. **Appetitlichkeit** — die weichste, aber nicht die unwichtigste Frage. Aus 30 Bildern fiel
   genau eines durch (Chia-Pudding: sachlich richtig grau, im Schaufenster unbrauchbar).

**Ausschuss wird nicht repariert, sondern neu gezogen** — zwei Varianten desselben,
unveränderten Prompts, dann die bessere behalten. Den Prompt für ein einzelnes Bild
nachzuschärfen wäre eine Sonderbehandlung, und der Stil ist ausdrücklich eingefroren.

**Danach muss das Protokoll stimmen.** Wird `…-1.webp` zur finalen Datei umbenannt, muss der
Eintrag in `bilder-protokoll.json` mitwandern und der Eintrag der verworfenen Variante
verschwinden — sonst belegt der Herkunftsnachweis eine Datei, die es nicht gibt. Der Abgleich
gehört ins Skript: **Datei ohne Protokolleintrag** und **Protokolleintrag ohne Datei** müssen
beide leer sein.

## Auto-Wochenplaner: zwei Prüfstände, zwei Fragen (16.08.2026)

Der Planer (D2) zerfällt sauber in **Logik** und **Oberfläche** — und beide brauchen einen
eigenen Aufbau, weil sie an verschiedenen Dingen scheitern.

### `tools/pruefstand-autoplaner.py` — die Auswahl- und Mengenlogik

Schneidet den Planer samt seiner ganzen Rechenkette aus `index.html` aus: `fitsDiet`,
`catFitsMeal`, `recipeNut`/`dayNutOf`, `makeEntry`, `goalTargetsForDay` **mitsamt den
Trainingstagen** (`TRAIN_LEVELS`, `trainKcal`, `trainFromRest`) und `activeWeekKey`. Gestubbt
sind nur die Randstücke: `save`, `render`, `toast`, `undoToast` und die Sync-Variablen.

Dass die Tagesziele mit ausgeschnitten werden statt gestubbt, ist der Punkt: Ein Stub
`goalTargetsForDay = () => 2000` hätte die Prüfung „Trainingstag bekommt mehr eingeplant"
grün und wertlos gemacht.

149 Prüfungen, gegliedert nach den fünf Regeln. Die wichtigen sind die **Ausschlüsse**:

* Meals ohne Nährwerte und Barcode-Schnellprodukte kommen nicht in die Auswahl.
* Ein veganes Profil bekommt **nie** ein Gericht ohne den Tag — auch nicht, wenn neun Meals
  dastehen und nur drei passen (dann wird gar nicht geplant).
* Ein belegter Slot bleibt unberührt; eine volle Woche bleibt **byteweise identisch**.
* In der Gruppe: fremder Eintrag unangetastet, mein Eintrag nur mir zugewiesen, dem vorhandenen
  Gericht **beigetreten** statt gedoppelt — und ein Gericht, das nicht zu meinem Profil passt,
  ausdrücklich **nicht** übernommen (siehe eigener Abschnitt unten).
* Kein Eintrag ist eine geteilte Objektreferenz (paarweiser `===`-Vergleich über alle Einträge).

Sechs Prüfungen kamen aus dem Pushcheck dazu (16.08.2026): Ein Bestand aus fettigen
Kohlenhydraten trifft die Kalorien punktgenau und verfehlt das Proteinziel — der Toast muss das
nennen. **Mit beiden Gegenproben**, ohne die die Meldung wertlos wäre: bei getroffenem Protein
darf sie nicht erscheinen, und ein Protein-*Überschuss* ist kein Befund.

### Die Gegenprobe hat hier zwei Hebel

Ein Prüfstand, der nur den Normalfall fährt, beweist über Ausschlussregeln nichts. Belegt wurde
das, indem in der **generierten** Prüfseite je eine Regel ausgehebelt wurde:

| Sabotage | erwartet | gemessen |
|---|---|---|
| `fitsDiet` → `return true` | die Profil-Prüfungen fallen | 7 von 57 rot |
| `slotOpenForMe` → `return true` | Regel 1 fällt | 6 von 57 rot |

(Zahlen aus dem Lauf mit 57 Prüfungen; die Sabotage wirkt unverändert.)

Nebenbefund aus der zweiten Sabotage: Die Ehrlichkeits-Meldung funktioniert auch nach oben
(„rund 14.060 kcal über dem Ziel"). Das wäre im Normalfall nie aufgetreten.

### Nachtrag 16.08.2026: 92 Prüfungen, drei Gegenproben — und zwei blinde Tests

Mit dem Rezeptbuch als zweiter Kandidatenquelle kamen Prüfungen dazu, die den **Kopierpfad**
absichern: Jedes eingeplante Katalog-Rezept muss als Kopie im Bestand liegen, mit eigener id,
`lib` als Herkunft und ohne Bildpfad — und `normalizePlan(state.plan, state.recipes)` darf
**keinen** Eintrag verlieren. Genau das ist die aussagekräftigste Zeile des ganzen Prüfstands:
Mit ausgehebeltem `planAdopt()` meldet sie `ist=0 soll=33`, also einen Plan, der beim nächsten
Laden vollständig verschwunden wäre.

Der Katalog läuft im Prüfstand **per Vorgabe aus** (`katalogAus()` in `frischerPlan()`) und wird
nur dort zugeschaltet, wo es um ihn geht. Sonst maßen die Prüfungen zur Auswahllogik plötzlich
gegen 34 zusätzliche Rezepte statt gegen den gebauten Testfall.

**Zwei Prüfungen waren zunächst blind — beide fielen erst in der Gegenprobe auf:**

| Prüfung | Warum sie nichts maß | Behoben durch |
|---|---|---|
| „Beilage/Getränk wird nie eingeplant" | `planRang()` verdrängte die losen Kandidaten ohnehin aus den Top drei | dünner Bestand, lose Kandidaten mit Meal-Prep und hohem Protein, **jeder Fall einzeln** |
| „kein Snack-Slot enthält dasselbe Gericht zweimal" | Ohne großen Tagesrest bekommt der Snack höchstens einen Eintrag | hohes Ziel + absichtlich kleine Gerichte, damit der Deckel greift und ~800 kcal beim Snack landen |

Siehe `docs/TROUBLESHOOTING.md` 95 und 96. **Die Lehre: Eine grüne Prüfung ohne Gegenprobe sagt
nichts darüber, ob der Testfall die Regel überhaupt herausfordert.**

**`window.onerror` darf das Log nicht überschreiben.** Der Handler des Prüfstands setzte
`textContent` auf die Fehlermeldung — und löschte damit genau die roten Zeilen, die vor dem
Absturz entstanden waren. Bei der Gegenprobe zum Kopierpfad (der Produktionscode stürzt dort
absichtlich ab) sah man deshalb nur „JS-FEHLER" und keinen einzigen Befund. Der Handler hängt
die Meldung jetzt an das bestehende Log an, und `pruef()` schreibt **fortlaufend** ins `<pre>`
statt erst am Ende (Ergebnisfortschritt, Abschnitt 3).

### Nachtrag 16.08.2026, zweiter Teil: 127 Prüfungen, vier Gegenproben

Mit Abwechslung, Würfeln und Gedächtnis kamen Prüfungen dazu, die anders gebaut sind als die
bisherigen — sie messen **Verteilungen**, nicht Einzelergebnisse:

* „An keinem Tag Mittag = Abend" prüft alle sieben Tage und meldet die betroffenen Tage als
  Liste, nicht als `true`/`false`. Ein Fehlschlag sagt damit sofort, *wo*.
* „Acht Läufe ergeben mehr als einen Plan" sammelt Plan-Signaturen in einem Set. Ein einzelner
  Vergleich könnte zufällig gleich ausfallen, ohne dass etwas kaputt ist.
* „Ein Getränk taucht in 20 Läufen nie auf" — bei einer Zufallsauswahl ist ein einzelner
  sauberer Lauf kein Beweis.
* Das Gedächtnis wird über die **Bewertung** geprüft (`planRang` mit und ohne Eintrag), nicht
  über einen Plan-Vergleich: Der wäre durch den Zufall verrauscht.

**Vier Gegenproben** (disjunkte Auswahl · Portionsdeckel · Wiederholungs-Malus · Pool-Ziehung),
jede einzeln gefahren. Jede muss genau ihre Prüfungen rot färben.

**Was der Prüfstand dabei selbst gefunden hat** — beides beim Lesen des Codes nicht aufgefallen:

1. **Der Abend blieb leer**, wenn nach Abzug der Mittagsgerichte keine Hauptgerichte mehr übrig
   waren. Der Rückfall prüfte die Größe der Restmenge, die aber noch Frühstücke und Snacks
   enthält und deshalb nie leer ist (TROUBLESHOOTING §98).
2. **Der Lauf dauerte über zwei Minuten** statt einer Sekunde — eine Datumsrechnung in der
   Vergleichsfunktion eines `sort()` (§99). Ein langsamer Prüfstand ist ein Befund: Es ist
   derselbe Code, den später ein Handy ausführt.

**Prüfungen mit an die neuen Regeln ziehen, nicht bloß reparieren.** Vier Bestandsprüfungen
wurden nach der Ein-Portionen-Regel rot — zu Recht, denn ihre Erwartung galt nicht mehr. Sie
messen jetzt die neue Zusage (etwa: „bei sehr hohem Ziel wird die Lücke benannt" statt „der
Korridor wird getroffen"). Eine Prüfung, die man nur so weit lockert, bis sie wieder grün ist,
misst am Ende nichts.

### Nachtrag 16.08.2026, dritter Teil: der Planer in der Gruppe (141 Prüfungen)

Mit „Beitreten statt doppeln" kam die erste Prüfgruppe dazu, die den **Zustand eines fremden
Eintrags vor und nach** dem Lauf vergleicht. Vierzehn neue Prüfungen, drei Gegenproben.

**Die wichtigste Prüfung hält eine Referenz fest**, nicht nur einen Wert:

```js
var fremd = { id: "ha3", uids: ["du"] };
state.plan.mon.mi.push(fremd);
autoPlanWeek();
pruef("das fremde Objekt wurde ersetzt, nicht mutiert",
  JSON.stringify(fremd), JSON.stringify({ id: "ha3", uids: ["du"] }));
```

Ein Vergleich gegen `state.plan.mon.mi[0]` hätte hier **nichts** bewiesen: Bei einer Mutation
zeigt der Slot ja auf dasselbe Objekt, das gerade verändert wurde. Nur die außen gehaltene
Referenz trennt „ersetzt" von „mutiert" — und genau daran hängt der Undo-Pfad.

**Vier Gegenproben, jede einzeln gefahren** — sie belegen zusammen, was eine allein nicht kann:

| Sabotage | erwartet | gemessen |
|---|---|---|
| Beitritt abgeschaltet (`if (false)`) → wieder zwei Einträge | die Beitritts-Prüfungen fallen | 5 von 141 rot |
| Verträglichkeits-Beitrag in `planRang()` abgeschaltet | die Bewertungs-Prüfungen fallen | 2 von 141 rot |
| Beitritt **mutierend** (`altUids.push(syncUid)`) | die Ersetzt-Prüfungen fallen | 5 von 141 rot |
| vegan auf `+= 50` — **mit** `Math.min(8, …)` | Deckel greift, Zeile bleibt grün | „mehr als 8 gibt es nicht" = 8 ✔ |
| dieselbe Übertreibung **ohne** `Math.min` | Deckel fehlt, Zeile fällt | 53 statt 8 |
| `slotGemeinsam` entfernt (wieder immer `meineUids()`) | die „für alle"-Prüfungen fallen | 3 von 149 rot |

Die dritte war nicht optional: Bei der ersten Gegenprobe blieben „das fremde Objekt wurde
ersetzt" und „Rückgängig stellt den fremden Eintrag her" **grün** — ohne Beitritt wird eben
nichts mutiert. Eine Prüfung gegen genau die Falle, vor der der Code warnt, braucht eine
Gegenprobe, die genau in diese Falle tritt.

Die letzten beiden sind ein Paar und zeigen einen Fall, der sonst durchrutscht: **Ein Deckel, den
der Normallauf nie erreicht, ist im Normallauf nicht prüfbar.** Mit den heutigen vier Tags ergibt
die Summe von selbst genau 8 — `Math.min(8, …)` ändert am Ergebnis nichts und wäre durch eine
gewöhnliche Sabotage („Deckel entfernen") nicht zu fassen. Beweisen lässt er sich nur, indem man
ihn **auslöst**: einen Beitrag künstlich über die Grenze treiben und sehen, ob die Zahl stehen
bleibt. Wer einen Grenzwert prüfen will, muss an die Grenze gehen, nicht daneben.

**Die Bewertung wird als Differenz zweier Gerichte gemessen**, einmal allein und einmal in der
Gruppe. Alle übrigen Beiträge (Kategorie, Protein, Größe) sind in beiden Läufen gleich und kürzen
sich heraus — übrig bleibt exakt der neue Beitrag (`5` bzw. gedeckelte `8`). Ein Vergleich am
Planergebnis wäre durch die gewichtete Ziehung verrauscht gewesen.

### Ein leeres Log ist kein grünes Log (16.08.2026)

Nach dem TDZ-Fix (`PLAN_GEDAECHTNIS_WOCHEN` wanderte vor `let state = load()`) blieb das `<pre>`
des Prüfstands **komplett leer** — keine Zeile, kein „JS-FEHLER". Ursache: Der Extraktor schnitt
`block("  const PLAN_GEDAECHTNIS_WOCHEN = ", "  }")` und zog nach dem Umzug den halben
State-Aufbau samt `let state = load()` mit herein. Das kollidierte mit dem Stub oben
(`Identifier 'state' has already been declared`), und ein **Parse**-Fehler verhindert, dass
`window.onerror` überhaupt registriert wird — der Fehlerhaken sitzt ja im selben Block.

Zwei Werkzeuge dafür, beide vorhanden:

* `python syntax-check.py tools/pruefstand-autoplaner.html` — das Skript **nimmt einen Pfad
  entgegen** und prüft jede erzeugte Seite genauso wie `index.html`.
* Im Zweifel das `<pre id="log">` **roh** ansehen statt gefiltert. Ein Filter auf `FEHL|ALLE`
  liefert bei leerem Log dasselbe Bild wie bei einem sauberen Lauf: nichts.

**Merksatz:** Ein Prüfstand, der nichts sagt, hat nicht bestanden — er hat nicht stattgefunden.
Deshalb gehört in jede Auswertung eine Zeile, die *positiv* bestätigt, dass gelaufen wurde
(hier: „ALLE n PRUEFUNGEN GRUEN"), und nicht bloß die Abwesenheit von Fehlern.

Dieselbe Sitzung lieferte den Gegenpol: eine Prüfung, die den Extraktor **nicht** mitzog. Wird im
Produktionscode eine neue Funktion benutzt (`slotIsShared` im Planer), muss sie in `teile`
aufgenommen werden — sonst endet der Lauf in `ReferenceError`, diesmal immerhin sichtbar.

### Eine Prüfung, die den Würfel misst, ist schlimmer als keine

Beim Fahren der Gegenproben fiel eine Zeile auf, die **rot war, obwohl die Sabotage sie gar nicht
berührte**:

```js
var mi = planWochengerichte(kand, "mi");
pruef("Meal-Prep steht vorn", mi[0].mealPrep, true);   // bis 16.08.2026
```

Nachgemessen: **in 20 Läufen zweimal rot**, ohne jede Codeänderung. Die Prüfung war richtig,
solange strikt die besten `PLAN_VARIANTEN` genommen wurden — seit der gewichteten Pool-Ziehung
kann auch Platz 4 auf Platz 1 landen. Sie maß den Würfel, nicht die Bewertung.

Sie steht jetzt an `planRang()`, wo die Aussage tatsächlich sitzt, und vergleicht zwei sonst
**identische** Meals, damit die Differenz genau der Meal-Prep-Beitrag ist (`10`). Danach: 20 von
20 Läufen grün.

**Merksatz:** Wird eine Auswahl auf Zufall umgestellt, muss jede Prüfung mitwandern, die bisher
am *Ergebnis* der Auswahl hing. Ein sporadisch roter Prüfstand ist kein kleineres Problem als ein
falscher — man gewöhnt sich an die rote Zeile und übersieht die echte daneben. Deshalb gehört zu
jeder Änderung an der Auswahl ein **Wiederholungslauf** (hier: 20×), nicht ein einzelner grüner.

## Mitgliederlimit: die eine Hälfte ist prüfbar, die andere nicht (16.08.2026)

`tools/pruefstand-gruppenlimit.py` — 19 Prüfungen, drei Gegenproben. Er schneidet
`CloudGroup.joinAtomic`/`leaveAtomic`/`setCount` und `migrateMemberCount()` im Original-Wortlaut
aus `index.html` und lässt sie gegen eine **aufzeichnende Firestore-Attrappe** laufen: `doc()`
liefert nur einen Pfad, `writeBatch()` sammelt Vorgänge, `commit()` legt sie als **ein** Bündel
ab. Einzelne `setDoc`/`deleteDoc` landen in einem getrennten Eimer.

Das ist der Kern: Die Regel lehnt jeden Einzelvorgang ab, also ist die **Bündelung** die
eigentliche Zusage — und genau die lässt sich ohne Firebase messen.

Geprüft wird außerdem der **Typ** des Zählerwerts, nicht bloß sein Vorzeichen: `increment()`
statt eines gelesenen Werts, sonst lägen zwei gleichzeitige Beitritte auf derselben veralteten
Basis und die Regel wiese den zweiten ab.

Die Migration bekommt alle Verzweigungen: Inhaber ohne Feld schreibt einmal, ein zweiter Lauf
nicht mehr (selbstheilend, nicht wiederholend), ein Mitglied versucht es gar nicht erst — und
eine **leere Mitgliederliste schreibt nichts**, denn sie ist ein ungeklärtes Leseergebnis und
kein Beweis; ein `memberCount: 0` hätte die Gruppe für immer verriegelt.

Drei Gegenproben, jede einzeln gefahren:

| Sabotage | gemessen |
|---|---|
| `joinAtomic` wieder als einzelnes `setDoc` (der Stand vor dem Limit) | 7 von 19 rot |
| Owner-Prüfung aus der Migration entfernt | 1 von 19 rot |
| `increment(1)` durch die feste Zahl 3 ersetzt | 2 von 19 rot |

### Was dieser Prüfstand ausdrücklich NICHT beweist

**Die Firestore-Regeln selbst.** Es gibt kein Node und keinen Emulator im Projekt (CLAUDE.md
Ziffer 12), und die Regeln sind die *verbindliche* Grenze — der Prüfstand sichert nur, dass der
Client sie überhaupt bedienen kann.

### Der Rules Playground hilft hier nur zur Hälfte — und täuscht in der anderen

**Der Playground simuliert immer genau EINE Operation, nie einen Batch.** Für Regeln, die mit
`getAfter()` zwei Dokumente koppeln, ist er damit nicht nur nutzlos, sondern **irreführend**:
Beim simulierten `create` auf `members/{uid}` bleibt das Gruppendokument unangetastet, also ist
`grpAfter(gid) == grpNow(gid)`, die Bedingung `== grpNow + 1` schlägt fehl — und ein völlig
korrekter Beitritt erscheint als **verweigert**. Wer das für einen Befund hält, sucht einen
Fehler, den es nicht gibt.

Im Playground sinnvoll prüfbar sind deshalb nur die Einzeloperationen auf `groups/{gid}`:

| # | Vorgang (als Update auf `groups/{gid}`) | erwartet |
|---|---|---|
| 1 | `memberCount` 4 → 3, als Mitglied, ohne Austritt | **verweigert** |
| 2 | Inhaber ändert nur den Gruppennamen | erlaubt |
| 3 | Inhaber ändert Name **und** `memberCount` zugleich | **verweigert** |
| 4 | Inhaber trägt `memberCount` erstmalig nach (Feld fehlt vorher) | erlaubt (Migration) |
| 5 | `invites`-create für eine Gruppe mit `memberCount: 4` | **verweigert** |

Alles mit Batch — Beitritt, Austritt, Entfernen, `dissolve` — **muss in der echten App
abgenommen werden**. Der `dissolve`-Fall ist dabei der wichtigste: Ohne die
`!existsAfter()`-Ausnahme ließe sich eine Gruppe nie wieder auflösen
(`docs/TROUBLESHOOTING.md`, Punkt 101), und das merkt man erst am Gerät.

**Merksatz:** Ein Werkzeug, das eine Frage nicht beantworten *kann*, antwortet trotzdem. Vor dem
Verlassen auf ein Prüfwerkzeug gehört die Frage, ob es den geprüften Mechanismus überhaupt
abbilden kann — sonst misst man seine Grenzen statt des Codes. Dieselbe Klasse Fehler wie die
Prüfung, die den Würfel statt der Bewertung maß (Abschnitt oben).

### Der Layout-Prüfstand liegt im Scratchpad, nicht im Projekt

Für den Knopf selbst braucht es die **echte App mit Anmeldung** — Aufbau wie oben unter
„Angemeldeter Prüfstand ohne Cloud-Gefahr": Kopie mit `apiKey: "DEIN_API_KEY"` (per `assert`
abgesichert), eigener Port 8181, `seed.html` mit `__test`-Suffix, Rahmen mit fester CSS-Breite.

Gemessen bei 390 px und 1200 px, jeweils hell und dunkel: eigene Zeile unter dem Einkaufsknopf,
44 px Trefferfläche, kein waagerechter Überlauf, Symbol trägt den Akzent, `aria-label`, und der
Klick über die **echte Delegation** (nicht der Funktionsaufruf).

Gemessen wird bei **320/360/390/430 und 1200 px**, hell und dunkel. Die entscheidende Zahl ist
die **Höhe von `.plan-head`**: Sie muss über alle Breiten gleich sein (Prüfregel aus
TROUBLESHOOTING §60). 86 px statt 42 px heißt Umbruch, und im Sheet fester Höhe fehlt diese Höhe
den Tageskarten.

Ergänzend die Platzrechnung, die den Umbruch *erklärt* statt ihn nur festzustellen: Summe der
Kinderbreiten + Gaps gegen die Breite von `.plan-tools`. Bei 320 px sind es 300 gegen 277 — bei
360 px 300 gegen 317.

Fünf Fallen, die dabei Zeit gekostet haben:

* **`state.tab: "plan"` im Seed reicht nicht.** Die App startet auf der Startseite. Der Reiter
  muss per echtem Klick auf `[data-tab="plan"]` geöffnet werden, und der Rahmen wartet auf
  `.week` — nicht darauf, dass `#view` Inhalt hat.
* **`--force-dark-mode` schaltet die App nicht um.** Beide Durchläufe lieferten exakt dieselbe
  Farbe (`rgb(166,155,157)`), der Test war blind. Erst `documentElement.setAttribute("data-theme",
  …)` im Rahmen trennt die Themes wirklich — sichtbar an zwei verschiedenen Akzenten
  (`rgb(220,38,38)` hell, `rgb(255,48,64)` dunkel). **Wer im Prüfstand ein Theme setzt, muss
  belegen, dass es angekommen ist** — sonst prüft man zweimal dasselbe.
* **`textContent` ignoriert `display: none`.** Die Prüfung „auf dem Handy bleibt nur das Symbol"
  las den Text des Knopfes und schlug fehl, obwohl das CSS längst griff. Gefragt ist die
  berechnete Darstellung: `getComputedStyle(span).display`.
* **Zeilen nicht über verschiedene `top`-Werte zählen.** `.plan-tools` zentriert vertikal, und
  der Wochenumschalter ist höher als die Knöpfe — jedes Kind hat damit sein eigenes `top`, und
  die Leiste sah selbst am 1200-px-Rechner „zweizeilig" aus. Richtig ist die Höhe der Leiste
  gegen die des höchsten Kindes.
* **Ein `"\n"` in der Python-Vorlage ist ein echter Zeilenumbruch.** In der JS-Zeichenkette
  landete er mitten im String-Literal und zerlegte damit das gesamte Rahmen-Skript — die Seite
  blieb wortlos bei „laeuft…" stehen, was wie ein Timeout aussieht. Im eingebetteten JS immer
  `\\n` schreiben (der bestehende Code tut das an jeder anderen Stelle).

**Der Prüfstand misst seit dem 16.08.2026 auch die Umgebung, nicht nur das neue Bauteil.** Ein
CSS-Eingriff in der Werkzeugleiste hatte den 680px-Block zerlegt und damit die komplette mobile
Ansicht abgeschaltet (TROUBLESHOOTING §97) — während jede Prüfung zum Knopf selbst grün blieb.
Neu je Breite: `.daybar` sichtbar, `.week` mit `overflow-x: auto` und `scroll-snap-type: x`,
`scrollWidth > clientWidth`, dasselbe für `.wg-cols` auf der Startseite, und am Rechner die
Gegenrichtung (`display: grid`, Tagesleiste aus).

Das Skript kennt dafür einen **Sabotage-Schalter** (`--sabotage`), der genau diesen Fehler in der
Prüfkopie nachbaut. Er gehört zur Prüfung dazu: Ohne ihn ist nicht belegt, dass die neue Gruppe
den Fehler überhaupt sieht. Mit ihm meldet sie bei 390 px `overflow-x=visible snap=none
display=grid` und fünf rote Zeilen.

**Vor jeder CSS-Änderung an einem Media-Block: Klammerbilanz und Blockgrenzen zählen.** Ein
Zehnzeiler in Python über den `<style>`-Inhalt gibt Start- und Endzeile jedes `@media`-Blocks aus.
Wird ein Block plötzlich kürzer, ist eine Klammer zu früh gesetzt — der Fehler ist in einer
Sekunde sichtbar und sonst erst am Gerät.

**Und die Falle aus §60 hat wieder zugeschlagen:** Nach einem Lauf, der ins Timeout gelaufen war,
blieb der Server auf Port 8181 stehen und lieferte weiter die **alte** Seite aus — drei Läufe
lang. Das Skript prüft den Port jetzt beim Start und bricht mit einer Anleitung ab, statt still
falsch zu messen.

## Katalog als Nachschlagequelle: eine Erwartung dreht sich um (17.08.2026)

`plans/Katalog_als_Nachschlagequelle.MD`: Der Planer kopiert keine Katalog-Rezepte mehr in den
Bestand (siehe `docs/TROUBLESHOOTING.md` 102), `getRecipe()` und `normalizePlan()` kennen den
Katalog stattdessen direkt. Das dreht die zentrale Zusage von `tools/pruefstand-autoplaner.py`
um: **„kein Plan-Eintrag zeigt auf eine Katalog-id"** (bis 16.08.2026) wird zu **„ein
eingeplantes Katalog-Rezept zeigt direkt auf die Katalog-id"**.

**Eine falsch gelockerte Prüfung wäre hier der teuerste Fehler gewesen.** Vor der Anpassung
warf ein Lauf gegen den geänderten Code nur **zwei** von 149 Prüfungen um:

```
FEHL kein Plan-Eintrag zeigt auf eine Katalog-id     ist=true  soll=false
FEHL es sind Kopien entstanden                        ist=false soll=true
```

Alle übrigen „Kopien"-Prüfungen (`jede Kopie trägt eine Herkunft…`, `keine Kopie trägt einen
Bildpfad…`, `keine doppelten Kopien…`) blieben **grün, obwohl sie nichts mehr maßen** — auf
einer leeren `kopien`-Liste ist `.every(...)` vakuos wahr und `.some(...)` vakuos falsch. Ein
grünes Ergebnis an dieser Stelle hätte nur bewiesen, dass niemand mehr kopiert, nicht dass die
Prüfung noch etwas aussagt. Sie wurden ersetzt durch direkte Aussagen über die neue Zusage
(„ein Planerlauf kopiert nichts mehr in den Bestand", `state.recipes.length` bleibt exakt
gleich) statt über eine jetzt immer leere Zwischenmenge.

Dieselbe Falle traf `verwaisteKopien()` bei „Nochmal": Die Prüfung „keine verwaiste Kopie bleibt
zurück" wäre nach dem Umbau ebenfalls dauerhaft (und wertlos) grün geblieben, weil es gar keine
Kopien mehr gibt, die verwaisen könnten. Ersetzt durch die direktere Aussage, die auch nach
dreimaligem Würfeln gilt: `state.recipes.length` rührt sich durch „Nochmal" überhaupt nicht.

**Der Extraktor selbst brach zuerst.** `schnitt("  function planAdopt(")` fand die entfernte
Funktion nicht mehr und stoppte den Lauf mit `NICHT GEFUNDEN` — sichtbar, kein leeres Log. Die
Zeile wurde aus `teile` entfernt (mit Kommentar, warum). Nach der Anpassung: **145 von 145
Prüfungen grün** (149 minus vier: `planAdopt` fällt weg, drei „Kopien"-Detailprüfungen weichen
zwei direkteren).

**Neuer Prüfstand `tools/pruefstand-katalog-plan.py` → `pruefstand-katalog-plan.html`** (33
Prüfungen), Vorbild `pruefstand-autoplaner.py`/`pruefstand-gruppenlimit.py` für die
Firestore-Attrappe. Deckt die vier neuen Zusagen aus dem Plan ab, plus eine sechste (Gruppen-
Merge):

1. Ein Plan mit Katalog-id übersteht `normalizePlan()`, eine erfundene id fällt weiter raus.
2. Ein Planerlauf mit dünnem Bestand lässt `state.recipes.length` unverändert, und mindestens
   ein Plan-Eintrag stammt nachweislich direkt aus dem Katalog (sonst bewiese die erste Zeile
   nur einen Zufallstreffer ohne Katalog-Beteiligung).
3. `adoptFromCookbook()` aus einem simulierten Slot heraus biegt den Plan-Eintrag auf die neue
   Kopie um — **in allen gespeicherten Wochen**, nicht nur der aktiven, und im Planer-Gedächtnis
   (`state.planned`) gleich mit. Rückgängig macht beides wieder rückgängig.
4. `dedupeAgainstCatalog()` löscht eine unveränderte Kopie, lässt eine inhaltlich abweichende
   und eine bloß favorisierte (aber sonst identische) Kopie stehen, verliert dabei keinen
   Plan-Eintrag aus keiner Woche und ist beim zweiten Lauf ein Nullvorgang. Eine eigene Gruppe
   prüft die Vorsichtsregel. **Seit dem 28.08.2026 schärfer** (`docs/TROUBLESHOOTING.md`
   128): In einer Gruppe läuft die Migration überhaupt nicht mehr — auch nicht nach dem
   Handshake — und `state.dedupeV1` bleibt unten, damit sie nach dem Verlassen nachholt.
   Die Gegenprobe im selben Abschnitt setzt `syncGid = null` und verlangt, dass sie dann
   sofort aufräumt und das Flag setzt.
5. (Teil des Punkts oben, siehe Migration.)
6. `copyOwnRecipesToGroup()` gegen eine aufzeichnende `window.CloudSync`-Attrappe (Vorbild:
   `pruefstand-gruppenlimit.html`): Zwei Bestände mit demselben `lib` ergeben in der Gruppe
   **ein** Rezept, meine überflüssige Kopie wird nicht hochgeladen, und beide Pläne (aktive und
   andere Woche) zeigen danach auf die schon vorhandene Gruppen-id. Die Gegenprobe mit zwei
   gleichnamigen, aber `lib`-losen „Bananen" belegt, dass ein Namensabgleich hier bewusst
   **nicht** stattfindet — beide bleiben stehen.

**Nachtrag aus der Gegenprüfung (17.08.2026), jetzt 42 Prüfungen:**

7. **Der reale Fall vom 16.08.2026: beide Hälften eines Paars im SELBEN Slot.** Montag Frühstück
   trug „Chia-Pudding" zweimal — zwei Rezepte mit demselben `lib`. Biegt die Migration beide um,
   steht danach zweimal *dieselbe* id im Slot. Das ist festgehaltenes Verhalten und kein
   Versehen: Es bleibt bei zwei Portionen wie zuvor, der Nutzer entfernt eine von Hand. Geprüft
   wird nur, dass die Migration hier **keinen Eintrag verliert** und keiner ins Leere zeigt.
   Genau dieses Muster steckt in den echten Daten und fehlte in der ersten Fassung.
8. **Die Handauswahl sieht dieselbe Menge wie der Planer** (`pickerQuellen()`): eigener Bestand
   plus sichtbares Rezeptbuch, ein übernommenes Rezept genau einmal (als eigene Kopie, nicht als
   Katalogeintrag) — und `COOKBOOK` trägt hinterher **kein** `__cb`, die Marke sitzt nur an der
   flachen Kopie.

Zu 8 gehört eine Lehre über Prüfbarkeit: `pickerQuellen()` stand zuerst *innerhalb* von
`openPicker()` und war damit für den Ausschneide-Prüfstand unerreichbar — der Extraktor schneidet
über `function name(` auf oberster Ebene. Eine Funktion, die man prüfen will, gehört nach außen.
Das ist kein Selbstzweck: Die Alternative wäre gewesen, die Auswahllogik im Prüfstand
nachzubauen, und damit hätte man geprüft, was man selbst geschrieben hat, statt was die App tut.

**Aufruf** (wie bei den anderen Prüfständen: erst schneiden, dann headless ausführen):

```powershell
python tools\pruefstand-katalog-plan.py          # schneidet aus index.html, schreibt die .html
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --virtual-time-budget=20000 `
  --user-data-dir="<scratchpad>\edge-profile" `
  --dump-dom "file:///C:/Users/Paddy/Documents/Paddys%20Mealplan/tools/pruefstand-katalog-plan.html"
```

Im `<pre id="log">` des Dumps steht die Bilanz (`ALLE 42 PRUEFUNGEN GRUEN`). **Nach jeder Änderung
an `getRecipe()`, `normalizePlan()`, `rewritePlanIds()`, `dedupeAgainstCatalog()`,
`pickerQuellen()` oder `copyOwnRecipesToGroup()` laufen lassen** — bricht der Extraktor mit
`NICHT GEFUNDEN` ab, wurde eine dieser Funktionen umbenannt oder anders eingerückt, und der
Prüfstand misst sonst nichts mehr (siehe die `planAdopt`-Erfahrung oben).

## Stapelkontext und Trefferflächen: `elementFromPoint()` im echten Browser (15.08.2026)

**Headless nicht messbar.** Ob ein Knopf einen Klick tatsächlich bekommt, entscheidet der
Stapelkontext — und der entsteht erst im Layout. Der Prüfstand kann es nicht sehen, ein
Screenshot zeigt es nicht (das Element ist ja sichtbar, nur überdeckt).

Der Nachweis läuft über `document.elementFromPoint()` auf die **Mitte** des Elements, im
laufenden Browser über den lokalen Server:

```js
const r = knopf.getBoundingClientRect();
document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
```

Beim Übernehmen-Knopf der Rezeptbuch-Karte lieferte das `button.rcard-open` — den Stretched Link,
nicht den Knopf (siehe `TROUBLESHOOTING.md` 90). Nach dem Fix `button.btn primary sm`, und ein
Punkt auf dem Bild weiterhin `button.rcard-open`.

**Die Gegenprobe gehört in denselben Aufruf:** den Stil per `el.style.position = "static"`
zurücksetzen, erneut messen, danach zurücksetzen. Fällt der Treffer dabei wieder auf das
überdeckende Element, ist die Ursache bewiesen und nicht nur das Symptom verschwunden.

**Kein Schreibvorgang nötig.** Genau das ist der Vorteil: Ein echter Klick auf „Übernehmen" hätte
ein Meal in das Cloud-Konto geschrieben. Gemessen wird die Trefferfläche, nicht die Wirkung.

**Und: lokale Testdaten vorher sichern.** Für einen frischen Zustand müssen die
`wochenkueche_*`-Schlüssel aus `localStorage` weichen. Sie gehören dem Nutzer — vorher nach
`sessionStorage` sichern (überlebt den Reload), danach zurückschreiben. Der `__test`-Suffix
trennt nur localStorage, **nicht** die Cloud: Ein angemeldetes Konto schreibt von localhost in
dieselbe Firestore-Datenbank.

## Ein Listener als Prüfobjekt: die Attrappe muss den Nebeneffekt haben (17.08.2026)

`tools/pruefstand-gruppe-aufloesen.py` — 11 Prüfungen für `TROUBLESHOOTING.md` 101 (Gruppe
auflösen nahm den Wochenplan mit). Er schneidet `snapshotOwnData()`, `dissolveGroup()` und
`leaveGroup()` im Original-Wortlaut aus `index.html`.

**Der Fehler lag nicht in einer Funktion, sondern zwischen zweien.** Prüfbar wird so etwas nur,
wenn die Attrappe den fremden Nebeneffekt nachstellt: `dissolveGroupFirestore()` leert hier
`state.plans` und `state.recipes` — genau das, was der echte `watchPlans`-Listener nach dem
Löschen tut. Eine Attrappe, die bloß `Promise.resolve()` liefert, hätte den Fehler nie gezeigt.

Im Prüfstand passiert es synchron im selben `await`, im Echtbetrieb Millisekunden später. Das
reicht als Beweis, weil der fehlerhafte Code in **jedem** Fall erst nach dem Löschen sicherte.

**Die Gegenprobe ist hier die wichtigste Zeile.** Sie fährt denselben ausgeschnittenen Code mit
einer einzigen zurückgedrehten Stelle (`const keep = snapshotOwnData();` → `undefined`) und
verlangt, dass der Plan dabei **verloren geht**. Bleibt sie grün, misst Durchgang 1 nichts.

Der Extraktor bricht ab, wenn `dissolveGroup()` den Snapshot nicht mehr zieht oder ihn nicht
weiterreicht, und ebenso, wenn sich die Gegenprobe nicht mehr bilden lässt. Das ist die Lehre
aus dem stillen Fehlschnitt vom 16.08.2026: Ein Prüfstand, der nichts sagt, hat nicht bestanden.

**Dritter Durchgang, leicht zu vergessen:** das einfache Verlassen ohne Auflösen. Dort bildet
`leaveGroup()` den Snapshot weiterhin selbst — der Fix darf den häufigen Fall nicht mit ändern.

## Ein absichtlich zufälliger Planer braucht festgenagelten Zufall (17.08.2026)

`planWochengerichte()` mischt und zieht gewichtet — jeder Lauf ergibt einen anderen Plan, und
das ist eine zugesagte Eigenschaft. Jede Prüfung, die **zwei Tage derselben Woche** gegeneinander
misst, würfelt damit mit.

Aufgefallen ist es am Vergleich „Trainingstag gegen Ruhetag": Er war in etwa jedem sechsten Lauf
rot, weil der Ruhetag zufällig die teureren Hauptgerichte erwischte. Fünf grüne Läufe danach
hätten die Sache erledigt aussehen lassen — **ein sporadisch roter Prüfstand ist aber kein
kleineres Problem, sondern das gefährlichere**: Man gewöhnt sich an die rote Zeile.

`mitFestemZufall(saat, fn)` ersetzt `Math.random` für die Dauer eines Aufrufs durch einen LCG.
Zwei Punkte, die dabei zählen:

* **Ein LCG, keine Konstante.** `Math.random = () => 0.5` hätte die gewichtete Ziehung immer auf
  denselben Index gelegt und damit das Ergebnis verzerrt statt nur festgehalten.
* **Nur lokal um einzelne Fälle gelegt, nie global.** Die Streuung selbst wird an anderer Stelle
  geprüft („jeder Lauf ergibt einen anderen Plan") — global festgenagelt wäre diese Prüfung
  vakuos grün.

**Und der Befund dahinter war am Ende kein Fehler.** Bei einer der zwanzig Saaten landeten
Trainings- und Ruhetag auf exakt denselben 2050 kcal, der Trainingstag mit drei Snacks gegen zwei.
Er gleicht die teureren Hauptgerichte des Ruhetags über die Snack-Zeile genau aus. Die belastbare
Zusage heißt deshalb „nie **weniger**" — „immer mehr" wäre eine, die der Planer gar nicht gibt.
Wer eine Prüfung rot findet, sollte sich erst die Zahlen ausgeben lassen, bevor er den Code ändert:
Hier stand die Wahrheit in einer einzigen Log-Zeile.

## Zwei Clients ohne Firestore: derselbe Ausgangsstand, zwei Läufe (17.08.2026)

Für den Gleichzeitigkeits-Befund (`TROUBLESHOOTING.md` 103) braucht es keine Attrappe und kein
Netz. Zwei Läufe auf **demselben** Ausgangsstand, dazwischen nur ein Wechsel von `syncUid`, sind
exakt das, was zwei Clients tun, die voneinander noch nichts wissen.

Entscheidend ist, beide Fälle zu fahren und nicht nur den kaputten:

1. B plant auf A's **aktuellem** Stand → darf nichts hinzufügen.
2. B plant auf dem **veralteten** Stand → belegt dieselben Slots.

Erst der Vergleich trennt die Funktion vom Zeitpunkt. Läuft nur Fall 2, sieht `slotOpenForMe()`
schuldig aus; läuft nur Fall 1, ist alles grün und der reale Fehler unsichtbar. Dazu gehören die
direkten Fragen an die Funktion selbst — ein fremdes „für alle" schließt, eine leere Zeile ist
offen, ein Eintrag nur für die andere Person lässt offen. Ohne die letzten beiden misst die erste
nur „irgendetwas ist belegt".

## Eine Reihenfolge prüfen, die beim Lesen richtig aussieht (17.08.2026)

`tools/pruefstand-einladung-verbrauch.py` — 17 Prüfungen für den Verbrauch des Einladungscodes
(`TROUBLESHOOTING.md` 105). Er schneidet `joinGroup()` im Original-Wortlaut aus und lässt es
gegen aufzeichnende Attrappen laufen: `joinAtomic` und `putMember` merken sich nur, **welcher
Weg** genommen wurde.

Der Fehler, um den es geht, ist keine falsche Bedingung, sondern eine falsche **Position**. Die
Prüfung auf `inv.used` gehört hinter `istMitglied()` — davor sperrt sie jedes bestehende
Mitglied aus, das über denselben Link zurückkehrt. Beide Fassungen lesen sich plausibel.

**Deshalb ist die Gegenprobe hier der Prüfstand.** Der Extraktor baut aus demselben
ausgeschnittenen Code eine zweite Fassung, in der die `used`-Zeile nach oben zu den anderen
Riegeln wandert, und verlangt, dass das Mitglied dabei **ausgesperrt** wird. Bleibt sie grün,
misst der Hauptfall nichts. Der Extraktor bricht ab, wenn sich diese Fassung nicht mehr bilden
lässt — eine verschobene Zeile darf nicht dazu führen, dass die Gegenprobe still verschwindet.

Vier Zustände werden gefahren, und erst ihre Kombination trennt die beiden Bedingungen:

| Code | schon Mitglied? | erwartet |
|---|---|---|
| offen | nein | Beitritt über `joinAtomic`, Code fährt als `via` mit |
| verbraucht | nein | abgewiesen, nichts kopiert, keine Gruppe gewechselt |
| **verbraucht** | **ja** | **Rückkehr über `putMember`** — der kritische Fall |
| offen | ja | ebenfalls Rückkehr |

Die letzte Zeile sieht überflüssig aus und ist es nicht: Ohne sie wäre die dritte auch dann
grün, wenn die Rückkehr generell an `istMitglied()` hinge und der Verbrauch gar nicht mehr
geprüft würde.

**Was hier nicht geprüft wird:** die Firestore-Regeln. Der Verbrauch ist erst mit Stufe 2 eine
harte Grenze; bis dahin ist die Client-Prüfung eine Bequemlichkeit. Der Batch selbst — drei
Dokumente, `used: true` ohne UID — wird in `pruefstand-gruppenlimit.py` gemessen.

---

## `tools/pruefstand-zurueck-taste.py` — die Zurück-Taste schließt Overlays (D5)

48 Prüfungen, zwei Gegenproben. Geprüft wird der Overlay-Stapel aus D5
(`docs/ARCHITECTURES.md`, „Zurück-Taste und Overlay-Stapel").

**Warum dieser Prüfstand einen echten Browser braucht.** `history.back()` ist asynchron, und der
gefährliche Fall ist nicht das Öffnen, sondern das Schließen auf normalem Weg: Dabei muss der
Eintrag zurückgenommen werden, ohne dass der eigene `popstate`-Handler daraufhin ein zweites Mal
schließt. Diese Schleife lässt sich nicht durch Lesen ausschließen, nur durch Laufenlassen. Die
Prüfungen warten deshalb zwischen den Schritten (`await warte(120)`), statt synchron zu messen.

**Das Polster.** Vor dem ersten Fall legt die Prüfseite einen eigenen History-Eintrag an. Ohne
ihn würde ein Zurück ohne offenes Overlay die Prüfseite verlassen — der Lauf wäre zu Ende, nicht
bestanden.

**Der Fall, der die erste Fassung widerlegt hat** (Nr. 5b): `closeModal()` beendet erst einen
laufenden Barcode-Sucher und dann sich selbst — zwei Rücknahmen im selben Tick. Acht Prüfungen
waren grün, diese neunte nicht. Details: `docs/TROUBLESHOOTING.md`, Punkt 107.

**Der Scanner wird nicht mitgeschnitten** (Kamera), sondern über denselben Vertrag simuliert, den
er benutzt: `overlayOpened(fn)` beim Anhängen, `overlayClosed(fn)` im `cleanup`. Dass
`scanBarcodeLive()` das wirklich so tut, prüft der Extraktor zusätzlich am Quelltext und schreibt
das Ergebnis unter das Protokoll.

**Die beiden Gegenproben** bauen aus demselben Ausschnitt die zwei naheliegenden Fehlfassungen:
`openModal()` ohne History-Eintrag (der Stand vor D5 — Zurück darf dann nichts schließen) und
`closeModal()` ohne Rücknahme (der tote Eintrag — das erste Zurück muss dann ins Leere laufen).
Der Extraktor bricht ab, wenn sich eine davon nicht mehr bilden lässt.

Beide Ladewege funktionieren, `file://` wie HTTP.

### Und die Falle, die den ersten Lauf gekostet hat

Der Lauf zeigte nur `laeuft…` — kein Ergebnis, keine Fehlermeldung. Der Grund: ein Syntaxfehler
in der erzeugten Seite, und der `window.onerror`-Melder stand im **selben** Script-Block, wurde
also nie angemeldet.

**Für Prüfstände gilt deshalb dieselbe Reihenfolge wie für die App:**

```powershell
python tools\pruefstand-zurueck-taste.py            # erzeugt die .html
python syntax-check.py tools\pruefstand-zurueck-taste.html   # ERST prüfen
```

Der Syntax-Check nimmt einen Pfad als Argument. Er hat den Fehler mitsamt Zeile in einer Sekunde
benannt, nachdem der Browserlauf zweimal schweigend nichts geliefert hatte.

### Zusätzlich: ein Durchlauf gegen die echte `index.html`

Der Ausschnitt beweist die Mechanik, nicht die Verdrahtung. Eine Prüfseite mit
`<iframe src="./index.html">` im selben Origin klickt deshalb den Impressum-Knopf im Fuß (ohne
Anmeldung erreichbar), liest `history.state` aus und ruft `contentWindow.history.back()`. Gemessen
am 23.08.2026: Öffnen setzt `{"pmOverlay":1}`, Zurück schließt und stellt `null` her, und nach
Öffnen/Schließen/Öffnen genügt weiterhin **ein** Zurück — also bleibt kein toter Eintrag liegen.

## Drei Prüfstände zum Ernährungsprofil und zum Rezeptbuch (24.08.2026)

Zum Speicherfehler von `docs/TROUBLESHOOTING.md` Ziffer 108 und zum Umbau des Rezeptbuchs.
Alle drei tragen ihre **Gegenprobe eingebaut** — das ist hier nicht Kür, sondern der Grund,
warum es sie gibt (siehe Ziffer 109: zwei Werkzeuge hatten jahrelang nichts geprüft).

### `tools/pruefstand-ziel-undefined.py` — kein Feld darf `undefined` tragen

Schneidet `computeGoal()`, `sanitizeGoal()` und `onbGoalInput()` samt ihrer Konstanten aus
`index.html`. Geprüft wird eine einzige Eigenschaft:

```js
Object.keys(g).some(k => g[k] === undefined)
```

**Die Gegenprobe steht als erster Abschnitt im Ergebnis** und ist ein *erwarteter Treffer*:
`computeGoal()` ohne Hülle **muss** `diet` und `avoid` auf `undefined` liefern. Fällt dieser
Block weg, prüft der Rest nichts mehr.

Der wichtigste Fall ist nicht der Wizard, sondern `syncGoalWeight()`: Dort fehlt `diet` im
gespeicherten Ziel meistens ganz, `Object.assign` kopiert es nicht, und `computeGoal()` erzeugt
es als `undefined`. Der Prüfstand baut diesen Zustand deshalb ausdrücklich aus einem vorher
sanitisierten Ziel auf, statt ihn von Hand hinzuschreiben.

Zusätzlich belegt: `sanitizeGoal()` ist **idempotent**. Ohne das wäre jeder Push ein Dauer-Diff
gegen `canonJSON()` — dieselbe Falle wie bei `sanitizeTags()`.

### `tools/pruefstand-rezeptbuch-filter.py` — die Chips treffen dieselbe Menge

Rechnet nach, dass der vorbelegte Chip **exakt dieselbe Rezeptmenge** liefert wie der frühere
harte Vorfilter `cookbookVisible()` — über sechs Profile, verglichen als sortierte ID-Liste.
Das ist die eigentliche Zusage des Umbaus: Wer nichts anfasst, sieht genau das, was er vorher
sah, nur jetzt sichtbar begründet.

Zwei Prüfungen, die man leicht vergisst und die beide einen echten Fehler abdecken würden:

* **Jeder vorbelegte Schlüssel überlebt `recipeFilterHtml()`** und steht dort als `data-f`. Die
  Funktion löscht aktive Filter, deren Chip es nicht gibt — ein Schlüssel, der im Katalog nicht
  vorkommt, verschwände lautlos, und die Ansicht zeigte mehr, als das Profil vorsieht.
* **Ein von Hand abgewählter Chip kommt ohne Profilwechsel nicht zurück.** Ohne diese Zeile
  liefe auch ein „belegt bei jedem Aufbau neu vor" durchweg grün.

### `tools/pruefstand-rezeptbuch-ansicht.py` — an der ungekürzten `index.html`

Der Logik-Prüfstand rechnet Mengen; er kann nicht sagen, ob die Chip-Reihe im DOM landet. Diese
Datei startet deshalb die **echte App** headless mit gesetztem Ziel, geht über die Reiterleiste
in den Katalog und misst dort.

**Gegenprobe über ein Argument:**

```powershell
git show HEAD:index.html > alt.html
python tools/pruefstand-rezeptbuch-ansicht.py alt.html   # MUSS rot sein
```

Gegen den Stand vom 23.08.2026 fällt er an genau vier Stellen um: beide Chips nicht vorbelegt,
`.cb-hint` noch da, und die Kopfzeilen verlieren bei einem von Hand gesetzten Chip ihren
Klappknopf. Genau das sind die vier Dinge, die geändert wurden.

Drei Fallen, die den Bau gekostet haben — alle drei gelten für jeden künftigen Prüfstand dieser
Bauart:

* **Ein Fehler in einem Event-Listener steigt nicht zum Aufrufer auf.** Er landet nur bei
  `window.onerror`. Die Fehlerliste muss deshalb **nach** dem Klick gelesen werden; vorher
  gelesen meldet sie „keine" und verschluckt die Ursache.
* **`paintCookbook()` baut `#cb-groups` per `innerHTML` neu auf.** Ein vor dem Klick gegriffener
  Knoten ist danach abgehängt und meldet Höhe 0 — das sah wie ein A11y-Befund aus und war eine
  Messfalle.
* **Nicht über `state.tab` in eine Ansicht springen, sondern die Reiter klicken.** So läuft
  derselbe Weg wie beim Menschen, einschließlich `render()`.

### `tools/mobilprobe-rezeptbuch.html` — echte Handybreiten

Handgeschrieben, kein Erzeugnis — deshalb heißt sie **nicht** `pruefstand-*.html` (das Muster
steht in `.gitignore`, sie wäre beim nächsten Checkout weg). Läuft im `iframe`-Rahmen gegen den
lokalen Server, misst 360/390/560/720 px und trägt die Gegenprobe als `?alt=1` (lädt
`alt-index.html`).

**Ihr eigentlicher Wert war die Gegenprobe.** Drei Layout-Befunde — 3 px waagerechter Überstand,
eine 18 px überstehende Karte, 35 px hohe Kategorie-Kopfzeilen statt der geforderten 44 — sind
im `?alt=1`-Lauf **Zeichen für Zeichen gleich**. Sie sind also älter als der Umbau und ihm nicht
anzulasten. Sie stehen als `ALT` im Ergebnis und werden nicht als Fehler gezählt; wer einen davon
behebt, streicht ihn aus `ALTBEFUND`, dann fällt er beim nächsten Auftreten wieder auf.

Zwei Messfallen, die den ersten Lauf komplett rot gefärbt haben:

* **Gegen `innerWidth` prüfen, nicht gegen `clientWidth`.** Im Rahmen sind die Scrollleisten
  klassisch und nehmen ~15 px von `clientWidth` — dagegen geprüft schlägt „scrollt waagerecht"
  immer an. (Steht weiter oben schon einmal; es ist trotzdem wieder passiert.)
* **Die tatsächliche Breite mitloggen** (`soll=390 ist=390`), sonst ordnet die Messung nichts ein.

## Paket 1 der Alltagsbefunde: drei weitere Prüfstände (24.08.2026)

### `tools/pruefstand-sheet-repaint.py` — bleibt die Zahl im Wochenplan stehen?

Gemessen wird **nicht**, wie oft `render()` läuft — die Funktion lebt im IIFE und ist von außen
nicht patchbar. Gemessen wird die Zahl, um die es dem Nutzer geht: die Tagesbilanz im
Wochenplan, gelesen nach genau dem Weg, den ein Mensch nimmt (Plan-Reiter → Slot antippen →
„Bearbeiten" → kcal ändern → schließen).

**Der `render()`-Detektor ohne Patchen** ist der brauchbarste Teil und für jeden künftigen
Prüfstand nachnutzbar: Vor der Aktion bekommt ein Knoten **innerhalb** von `view` eine Marke
(`data-marke`). `render()` ersetzt `view.innerHTML` komplett — überlebt die Marke, wurde nicht
neu gezeichnet. Damit ist „die Anzeige ist nur alt" von „es wurde neu gezeichnet und falsch
gerechnet" sauber unterscheidbar, ohne eine einzige Zeile Produktionscode anzufassen.

Drei Fälle, und zwei davon sind die Gegenproben:

| | | erwartet |
|---|---|---|
| A | Wochenplan, kcal geändert | Zahl zieht mit, `render()` **lief** |
| B | Wochenplan, nur hineingesehen | Zahl gleich, `render()` lief **nicht** |
| C | Meals-Reiter, kcal geändert | Karte zeigt die neue Zahl (Teil-Repaint, unverändert) |

Fall B prüft ausdrücklich **beides**: dieselbe Zahl allein wäre ein Zufallstreffer.

**Zwei Messfallen haben je einen Lauf gekostet, beide sind eigene Lehren:**

* **`.day-goals`, nicht `.day-nut`.** `dayNutHtml()` ersetzt die Textzeile durch die Balkenform,
  sobald ein Ziel gespeichert ist — und ohne Ziel gäbe es gar keine Tagesbilanz. Mit `.day-nut`
  fand der erste Lauf nichts, und **Fall B lief still grün durch**, obwohl gar nichts gemessen
  wurde. Ein `(nicht gefunden)` == `(nicht gefunden)` ist kein bestandener Test.
* **Der Prüfstand hat einen falschen Fix entlarvt, den das Codelesen durchgehen ließ.** Die erste
  Fassung der „hat sich etwas geändert?"-Prüfung maß nachweislich nichts (siehe
  `docs/TROUBLESHOOTING.md` 110) — sie sah beim Lesen völlig plausibel aus.

Gegenprobe über ein Argument: `python tools/pruefstand-sheet-repaint.py alt.html` — gegen den
Stand davor muss Fall A rot sein (Zahl bleibt stehen, `render()` lief nicht).

**Die Testdaten tragen bewusst gemischte Zutaten** — einen Freitext-String, ein Objekt mit
eigener Einheit, eines mit vollen Nährwerten und eines ganz ohne. Der erste Entwurf nahm
`ingredients: []`, und Fall B lief damit grün durch, **ohne den Umweg Datensatz → DOM →
`collectIngs()` → zurück auch nur einmal zu belasten**, den `mutateLocal()` bei jedem
`commitNow()` geht. Mit echten Zutaten fiel er sofort um und legte einen zweiten, größeren
Fehler frei: `macroOverridden` (siehe `docs/TROUBLESHOOTING.md` 110). Der Hinweis kam vom
`kvp`-Agenten — **ein leerer Sonderfall ist kein Testfall.**

### `tools/pruefstand-wochenbeschriftung.py` — Verifikation VOR dem Fix

Der Plan verlangte hier ausdrücklich, den Befund erst zu beweisen. Zu Recht: Die Klammerbilanz
ist als Scope-Beweis untauglich (Regex- und Template-Literale verfälschen sie), und
`weekLabel()` ist von außen nicht aufrufbar. Bewiesen wurde es über die **Anzeige** — mit einer
Wiegung im Zustand, abgelesen an `.wch-tip` und am `aria-label` des Diagrammpunkts.

Zwei Dinge daran sind Absicht:

* **Genau EINE Wiegung.** Bei mehreren lässt `weightHtml()` die `.wch-tip` bewusst leer
  (dort steht dann der Vergleich statt des Einzelwerts) — der Text, um den es geht, wäre gar
  nicht da, und die Prüfung liefe ins Leere. Der erste Lauf hatte genau diesen Fehler.
* **Die Hero-Zeile als Gegenprobe.** Die Zahl-Variante muss unverändert ihre eigene Form
  behalten (`"Woche 35 · 24.–30. August"`). Ohne sie beweist der Test nur, dass irgendetwas
  anders geworden ist.

### `tools/pruefstand-rezeptbuch.py` — erweitert und wieder scharf

**Der Prüfstand lief seit einer Weile gar nicht mehr:** `adoptFromCookbook()` ruft
`rewritePlanIds()`, ein Stub dafür fehlte, und die Seite brach mit
`rewritePlanIds is not defined` ab — mitten im Lauf, sichtbar nur als eine Fehlerzeile. Damit ist
es das **dritte** Werkzeug in zwei Tagen, das nichts geprüft hat (vgl. Ziffer 109). Stub ergänzt,
Gegenprobe-Argument nachgerüstet, jetzt 113 Prüfungen.

Neu darin: die Startmeals sehen ihre Filter. Für alle drei Profile wird geprüft, dass
`addStarterMeals()` fünf Meals anlegt, dass darüber eine Filterreihe erscheint **und** dass kein
Chip auf alle fünf zutrifft. Die letzte Prüfung braucht ihre eigene Gegenprobe („und es gibt
überhaupt Chips"), sonst wäre „keiner wirkungslos" trivial wahr, sobald die Reihe fehlt — genau
der Zustand vor der Änderung.

## Abnahme am echten Cloud-Konto: `tools/cdp.py` (24.08.2026)

**Die Lücke, die das schließt:** Alles, was ein echtes Firebase-Konto braucht — Anmeldung,
Firestore-Schreibvorgänge, Zwei-Geräte-Verhalten —, galt bisher als „nur am Gerät prüfbar" und
blieb damit beim Nutzer liegen. Headless geht es nicht (kein Login), im Ausschneide-Prüfstand
auch nicht (keine Cloud).

`tools/cdp.py` steuert einen **sichtbaren** Chrome über das DevTools-Protokoll:

```powershell
python tools/cdp.py start          # Chrome mit Fernbedienung, Profil im TEMP
python tools/cdp.py eval "<js>"    # JavaScript in der App-Seite auswerten
python tools/cdp.py stop
```

**Die Arbeitsteilung ist der Punkt:** Der Mensch meldet sich **einmal von Hand** an — Passwörter
laufen nie durch das Skript und stehen in keinem Protokoll. Danach liest und klickt das Skript.

Vier Dinge, die den Aufbau brauchbar machen:

* **`--remote-allow-origins=*` beim Start und `origin=` beim Verbinden.** Ohne beides lehnt
  Chrome die WebSocket-Verbindung zum Debug-Port mit `403 Rejected an incoming WebSocket
  connection` ab. Das war die erste Hürde und ist nicht selbsterklärend.
* **`awaitPromise: true` und `returnByValue: true`** bei `Runtime.evaluate` — sonst kommt bei
  `await CloudSync.load(uid)` nur eine Objekt-ID zurück statt des Dokuments.
* **Eigenes Profilverzeichnis.** Ein bereits laufender Alltags-Chrome verhindert das
  Debug-Port-Flag sonst stillschweigend, und der Alltagsbrowser bleibt unangetastet.
* **`window.CloudSync` ist global** — damit ersetzt `CloudSync.load(uid)` den Gang in die
  Firebase-Konsole vollständig und liest genau das, was die App sieht. Die `uid` steht in
  `localStorage` unter `wochenkueche_lastprofile_v1__test`.

**`Object.keys(goal)` statt `JSON.stringify(goal)`** beim Prüfen auf ein *fehlendes* Feld:
`JSON.stringify` lässt `undefined`-Werte weg, ein fehlendes Feld sieht dann aus wie ein
Skriptfehler statt wie das Ergebnis. Das hat einen Lauf gekostet.

### Der Ablauf, wenn echte Nutzerdaten im Spiel sind

`localhost` trennt nur den **lokalen** Speicher (`__test`-Suffix über `localKey()`), **nicht die
Cloud** — ein Test am echten Konto schreibt in echte Firestore-Daten. Deshalb:

1. **Zuerst sichern.** Das betroffene Feld über `CloudSync.load()` lesen und wegschreiben.
2. Test fahren.
3. **Zurückschreiben und gegenprüfen**, dass die Schlüsselmenge deckungsgleich ist — nicht nur
   ein einzelner Wert.
4. Beide Fenster neu laden, damit keines mit dem alten Zustand weiterpusht.
5. Chrome beenden. **Ein offener Debug-Port ist eine offene Fernbedienung** und darf nicht
   länger laufen als die Abnahme.

### Damit gefahren: die Abnahme zu `78f125d`

Ergebnis am echten Konto, alle fünf Punkte:

| | |
|---|---|
| Ausgangsstand | `goal.diet: "vegetarisch"` stand tatsächlich in der Cloud |
| nach „Ziele neu berechnen" → „Alles" | Sync-Punkt **„Synchronisiert"**, nicht „offline" |
| in der Cloud | `goal.diet` **weg** — und `goal.manual` ebenfalls (Ziffer 74 damit erstmals wirklich eingelöst) |
| nach dem Neuladen | bleibt „Alles", der alte Stand kommt nicht zurück |
| zwei Fenster, 50 s | `updatedAt` steht still — **nichts oszilliert** |

Der Zwei-Fenster-Test misst `updatedAt` **in der Cloud**, nicht die Anzeige: Steigt der
Zeitstempel weiter, obwohl niemand etwas tut, schreiben sich die Geräte gegenseitig hoch. Das ist
die Messgröße für TROUBLESHOOTING 34/44, und sie ist billiger als jede DOM-Beobachtung.

---

## Ein Zweig, der nur bei leerem Bestand läuft: die Ganzdatei-Kopie (25.08.2026)

Der Schnell-Bereich im Picker klappt in einem Fall zwingend auf: wenn es **kein einziges Meal**
gibt (`libEmpty`) — zugeklappt wäre der Slot dann eine Sackgasse. Dieser Zweig ist am echten
Konto nicht erreichbar: `pickerQuellen()` liefert eigene Meals **plus** die nicht übernommenen
Katalogrezepte, und der Katalog ist nie leer.

Ausschneiden ließ sich `paint()` schlecht — es hängt an elf Helfern, an `state` und am Modal.
Der billigere Weg war die **Umkehrung des Prinzips**: nicht den Code aus der Datei schneiden,
sondern die ganze Datei kopieren und darin **einen** Helfer stumpfsinnig machen.

```python
alt = "  function pickerQuellen() {
    const eigene = libraryRecipes();"
neu = "  function pickerQuellen() {
    return [];  // PRUEFSTAND libEmpty
" + alt.split("
")[1]
io.open("_pruefstand-libempty.html", "w", encoding="utf-8", newline="").write(s.replace(alt, neu))
```

Die Kopie liegt **im Projektordner**, damit `test-server.ps1` sie ausliefert, und wird per
`tools/cdp.py` im laufenden Chrome geladen — mit derselben Anmeldung, demselben CSS, demselben
`state`. Ergebnis in einem Aufruf: Leer-Hinweis oben, Kopfzeile statisch, alle sechs
Schnell-Zeilen offen.

**Drei Bedingungen, damit das sauber bleibt:**

* Der Stub steht als **erste Zeile** der Funktion (`return []`), der Originalcode bleibt darunter
  stehen. Wer ihn löscht, kann den Prüfstand nicht mehr gegen das Original diffen.
* Der Dateiname beginnt mit `_` und die Kopie wird **sofort nach dem Lauf gelöscht**. Sie liegt
  im Projektordner, also im Blickfeld von `git status` — das ist Absicht, nicht Nachlässigkeit.
* Nach dem Lauf zurück auf `index.html` navigieren. Bleibt die Kopie offen, misst der nächste
  Prüfschritt eine App mit einem absichtlich kaputten Helfer.

Grenze der Methode: Sie taugt für Zweige, die von **einer** Datenquelle abhängen. Sobald zwei
Helfer zusammenspielen müssen, ist der echte Ausschneide-Prüfstand wieder der ehrlichere Weg —
eine Kopie mit fünf Stubs ist keine Produktionsimplementierung mehr.

---

## Ein Escape-Fix beweist sich nur mit dem Vorher (25.08.2026)

Zum `esc()`-Nachtrag bei `data-assign` (TROUBLESHOOTING 114) gehört ein Prüfstand, der **beide**
Fassungen rendert — die alte und die neue — statt nur zu zeigen, dass die neue harmlos aussieht.
`esc()` wird dazu unverändert aus `index.html` geschnitten:

```python
esc = [l for l in s.split("
") if l.strip().startswith("function esc(s)")]
assert len(esc) == 1
```

Geprüft wird nicht der ausgegebene Text, sondern **was der Parser daraus gemacht hat**:

* `el.hasAttribute("onmouseover")` — ohne `esc()` **true**, das ist der Beleg, dass der Ausbruch
  ohne den Fix wirklich gelingt. Ein Prüfstand, der nur die neue Fassung zeigt, beweist nichts.
* `el.attributes.length` — mit `esc()` genau zwei (`class`, `data-assign`).
* `el.dataset.assign === id` — die Nutzlast kommt **dekodiert** zurück, die Zuweisung bricht also
  nicht. Zusätzlich mit einer normalen id gegengeprüft, damit der Regelfall belegt ist und nicht
  nur der Angriffsfall.

**`innerHTML` im Prüfstand ist hier kein Fehler, sondern der Messpunkt:** Genau diesen Weg geht
die App, und nur er zeigt, ob ein Attribut entsteht. Ein String-Vergleich hätte den Fund nicht
belegt.

---

## `tools/pruefstand-weekstats-sync.py` — und warum er den Fehler nicht fand (25.08.2026)

Zum Cloud-Sync des Wochenarchivs gehört ein dauerhafter Prüfstand. Er schneidet
`sanitizeWeekStats()`, `weekStatRang()`, `mergeWeekStats()` und `canonValue()/canonJSON()` aus
`index.html` und fährt 24 Prüfungen headless. Exit-Code 0 nur bei „0 rot".

**Die Messgrösse ist nicht „kommt eine Woche an", sondern die Einigkeit zweier Geräte:**

```
mergeWeekStats(A, B) === mergeWeekStats(B, A)
```

Ein Tiebreak „remote gewinnt" erfüllt das nicht — A nähme den Wert von B und B gleichzeitig
den von A. **Prüfung 9 baut genau diese naive Fassung nach und verlangt, dass sie durchfällt**
(3 von 3 Fällen uneinig, während die echte in allen einig ist). Ohne diese Gegenprobe bestünde
den Test auch die kaputte Variante.

### Der Teil, den er nicht leisten kann

Der Prüfstand war **grün, bevor der eigentliche Fehler gefunden war** — der Aufruf im
Baseline-Merge von `startCloudSync()` fehlte, und `onRemote()` allein kam beim Start nie zum
Zug (TROUBLESHOOTING 115). Ein isolierter Prüfstand prüft die **Funktion**, nicht ihre
**Aufrufer**; einen fehlenden Aufruf kann er per Konstruktion nicht sehen.

**Bei Sync-Änderungen gehört deshalb der Lauf am echten Konto dazu.** Er hat hier drei Schritte
und dauert zwei Minuten (`tools/cdp.py`, siehe unten):

1. **Sichern.** `CloudSync.load(uid)` lesen, **Schlüsselmenge** notieren — nicht nur einen Wert.
2. **Gerät 1 spielen:** `weekStats` im `localStorage` (`wochenkueche_v1__test`) auf eine Woche
   setzen, neu laden, in der Cloud nachsehen, ob sie ankommt.
3. **Gerät 2 spielen:** lokal eine **andere** Woche setzen — die erste also lokal entfernen —,
   neu laden. Danach müssen **beide** Wochen lokal und in der Cloud stehen. Genau hier fiel der
   Lauf durch, und nur hier.

Danach `updatedAt` über ~45 s beobachten (muss stillstehen) und die Testdaten wieder
ausräumen: **lokal zuerst leeren, dann `CloudSync.save(uid, { weekStats: {} })`** — in dieser
Reihenfolge, sonst schiebt der Baseline-Merge die Testwochen sofort wieder hoch. Zum Schluss
die Schlüsselmenge gegen die Sicherung aus Schritt 1 prüfen.

---

## `tools/pruefstand-wochenmaske.py` — ein Prüfstand, der absichtlich rot war (26.–29.08.2026)

Zu Paket 6 (Fortschritt-Kalender) gehört die Tagesmaske `weekStats[wk].d`. Der Prüfstand dazu
wurde **vor** dem Umbau angelegt und läuft gegen den Stand, den er noch gar nicht beschreibt.
Er schneidet `DAYS`, `hasNut()`, `pruneWeeks()`, `archiveWeek()`, `sanitizeWeekStats()`,
`mergeWeekStats()` und `canonValue()/canonJSON()` aus `index.html`; gestubbt sind nur `state`,
`dayNutOf()` und `goalTargetsForDay()`.

**Er zählt zwei Gruppen getrennt, und nur eine bestimmt den Exit-Code:**

| Gruppe | Bedeutung | Exit-Code |
|---|---|---|
| `OFFEN` | Sollzustand nach B2–B5. Rot ist hier der erwartete Stand. | zählt nicht |
| `REGRESSION` | was heute schon gilt und beim Umbau nicht brechen darf | 0 nur bei „0 rot" |

Ohne diese Trennung wäre der Prüfstand während des ganzen Umbaus rot und damit als Warnsignal
wertlos — eine kaputte Regression ginge in 24 erwarteten Fehlschlägen unter.

**Die Eingangsprobe war die Gegenprobe** — und sie hat ihren Zweck erfüllt. Abschnitt 1
verlangte, dass ohne `state.goal` archiviert wird; die Fassung von damals tat das nicht
(`if (!pl || !state.goal) return;`).

**Stand 29.08.2026: B1–B5 sind umgesetzt, der Prüfstand ist vollständig grün** —
53 `OFFEN`-Zeilen und 13 `REGRESSION`-Zeilen. Der Weg dorthin, weil die Zwischenstände die
eigentliche Aussage tragen:

| Stand | `OFFEN` | Was fehlte |
|---|---|---|
| 26.08., vor B1 | Abschnitt 1 rot | `archiveWeek()` stieg ohne Ziel aus |
| 26.08., nach B2 | 7 rot | `d` überlebte `sanitizeWeekStats()` nicht, Masken wurden nicht vereinigt, Fenster noch 26 Wochen |
| 29.08., nach B3/B5 | 0 rot | — |

**Die Gegenprobe gehört zum Ergebnis** — für B3/B5 fiel derselbe Prüfstand gegen `9ae227d`
mit **sieben roten `OFFEN`-Zeilen** durch. Ohne diesen Lauf wäre „grün" nur eine Behauptung.

⚠️ **Dieser Lauf ist seit `d4b01f6` nicht mehr wiederholbar** und darf nicht als Beleg
nachgefahren werden: `9ae227d` kennt `archivJahre()` noch nicht, der Schnitt endet mit
**„Endmarker nicht gefunden: function archivJahre("** — ein Abbruch, kein roter Test. Wer das
für ein Ergebnis hält, liest einen kaputten Lauf als Beweis. Die heute gültige Gegenprobe
steht unten (verstellte Kopie).

### Eine Gegenprobe, die kein alter Commit liefern kann

Für das Archivfenster (Abschnitt 6, seit 29.08.2026) taugt der Vorgänger-Commit **nicht** als
Gegenprobe: Dort gibt es `archivJahre()` gar nicht, der Schnitt bricht
also mit „Marker nicht gefunden" ab — ein Abbruch ist kein roter Test. Die Gegenprobe läuft
deshalb über eine **verstellte Kopie**:

```powershell
sed 's/archivJahreBehalten() { return archivJahre(3); }/archivJahreBehalten() { return archivJahre(2); }/' index.html > _ohne_puffer.html
python tools/pruefstand-wochenmaske.py _ohne_puffer.html
python tools/pruefstand-weekstats-sync.py _ohne_puffer.html
```

Ergebnis: vier rote Zeilen, darunter „nichts heute Sichtbares fällt am 1. Januar weg →
verloren: 2025". Genau die Aussage, um die es bei der Entscheidung ging — und sie ist damit
gemessen statt behauptet. Danach `_ohne_puffer.html` wieder löschen.

Die Zeile selbst kommt **ohne Zeitreise** aus: Sie vergleicht die heutigen Anzeige-Jahre mit
dem Behalten-Fenster von morgen, statt die Systemuhr zu stellen. Ein Test, der `Date`
ersetzt, prüft am Ende die Attrappe.

**Seit dem 29.08.2026 bestimmen wieder BEIDE Gruppen den Rückgabewert** (`GESAMT 0 rot`).
Während des Umbaus durfte das nur die `REGRESSION`-Gruppe — danach wäre es eine Bremse
gewesen, die nie mehr greift: Eine kaputte `OFFEN`-Zeile wäre ab sofort lautlos durchgelaufen.
Die Trennung bleibt in der **Ausgabe** stehen, weil sie zeigt, was Umbau war und was schon
vorher galt. Der Eintrag in `TEILWEISE` (siehe unten) ist damit entfallen.

Wer diesen Absatz liest, während Abschnitt 1 rot ist, hat einen echten Rückschritt vor
sich — dann lädt der Prüfstand nicht die echte `archiveWeek()`, und alles Folgende misst
nichts.

### Die Falle: grüne Zeilen aus dem falschen Grund

Während des Umbaus war ein Teil der `OFFEN`-Zeilen grün, und zwar aus dem falschen Grund:
Solange `sanitizeWeekStats()` das Feld `d` gar nicht kannte, warf es **jedes** `d` weg —
kaputtes wie gültiges. „Kaputtes d: Feld fällt weg" und der komplette Determinismus-Abschnitt
waren damit grün, ohne etwas zu beweisen; sie messen erst seit B3/B5.

Die jeweilige Gegenprobe stand daneben und war rot („gültiges d überlebt", „Masken vereinigt").
**Die Paare gehören zusammen gelesen** — wer nach B3 nur auf die Zähler schaut, verpasst es.
Nachträglich geprüft: Seit B3 sind beide Hälften grün, die Paare messen also jetzt beide echt.
Das ist dieselbe Klasse wie die naive Fassung in `pruefstand-weekstats-sync.py`, nur andersherum:
Dort beweist ein erzwungener Fehlschlag, dass der Test misst; hier verrät ein zu früh grüner
Treffer, dass er es noch nicht tut.

### Was er festschreibt, weil der Plan es offen ließ

Der Plan sagt an einer Stelle „`days` auf `Math.max` ziehen" und an anderer „`days` = Anzahl der
Einsen". Der Prüfstand legt die einzige Lesart fest, die beides erfüllt:

```
days = max(alter days, neuer days, Anzahl Einsen der vereinigten Maske)
```

`days` ist damit nie kleiner als die Maske hergibt und nie kleiner als ein früher gemessener
Wert; für Altwochen ohne `d` bleibt schlicht das Maximum wirksam. Ebenso festgelegt:
`kcal`/`hit`/`target` ersetzt der neue Lauf nur, wenn er **mindestens so viele Tage** gesehen
hat — derselbe wertbasierte Gedanke wie im Tiebreak von `mergeWeekStats()`.

**Auch dieser Prüfstand sieht keinen fehlenden Aufrufer** (TROUBLESHOOTING 115). Sobald `d` im
Sync mitläuft, gehört der Zwei-Geräte-Lauf am echten Konto dazu, wie oben beschrieben.

---

## Eine Zeile prüfen, indem man sie WEGNIMMT (25.08.2026)

Zum Fund in TROUBLESHOOTING 116 gehört die Methode, die ihn geliefert hat — sie ist billig und
hätte die falsche Behauptung schon eine Runde früher gefunden.

Die Frage war nicht „funktioniert der Code?", sondern **„täte sich ohne ihn etwas anderes?"**
Beides sieht in der Messung gleich aus, solange man nur die vorhandene Fassung testet: `200 → 200`
liest sich wie ein Erfolg. Erst der Vergleich zeigt, ob die Zeile das bewirkt hat oder der
Browser.

```python
# Ganzdatei-Kopie, in der GENAU die fragliche Zeile fehlt
neu = alt.replace("      listEl.scrollTop = top;", "")
io.open("_ohne-scrollrettung.html", "w", encoding="utf-8", newline="").write(neu)
```

Dann beide Fassungen über `test-server.ps1` im selben ferngesteuerten Chrome fahren und
dieselbe Messung machen. Kommt **derselbe** Wert heraus, tut die Zeile nichts.

**Wann sich das lohnt:** immer, wenn Code eine Browser-Eigenheit „repariert" — Scrollposition,
Fokus, Layout-Flush, Repaint-Erzwingung. Genau dort häuft sich Code, den niemand mehr anfasst,
weil alle annehmen, er tue etwas. Bei diesem Lauf war die Fokus-Rettung echt (ohne sie steht
`activeElement` auf `<body>`) und die Scroll-Rettung wirkungslos — **im selben Helfer, zwei
Zeilen auseinander.**

Die Kopien wandern danach sofort in den Müll, und der Chrome wird zurück auf `index.html`
navigiert (siehe die Bedingungen bei der Ganzdatei-Kopie weiter oben).

---

## Mobile Abnahme fernsteuern: `cdp.py messen` (25.08.2026)

`tools/cdp.py` kann jetzt Viewport und Farbschema setzen. Der Unterschied zwischen den beiden
Befehlen ist kein Komfort, sondern eine harte Eigenschaft des DevTools-Protokolls:

| | hält wie lange |
|---|---|
| `Emulation.setDeviceMetricsOverride` (Viewport) | **persistent** — überlebt Verbindungsende und `location.reload()` |
| `Emulation.setEmulatedMedia` (Farbschema) | **nur solange die Verbindung offen ist** |
| `Emulation.setTouchEmulationEnabled` (`pointer: coarse`) | **nur solange die Verbindung offen ist** |

`cdp.py` schliesst den Socket nach jedem Befehl. Ein `theme light` als eigener Aufruf war
deshalb **wirkungslos** — und das fällt nicht auf, wenn das System selbst auf Dark steht: Dann
scheint `theme dark` zu „funktionieren", obwohl nur das System durchschlägt. Genau so wäre hier
eine Light-Abnahme als erledigt durchgegangen, die nie stattgefunden hat.

**Deshalb `messen`, das beides in EINER Verbindung tut:**

```powershell
python tools/cdp.py viewport 560 900              # dauerhaft, fuer Breakpoints
python tools/cdp.py messen 720 900 dark "<js>"    # Viewport + Theme + Auswertung
python tools/cdp.py viewport aus
```

Aus Python heraus mit `mobil=False` für die Desktop-Gegenprobe:

```python
import sys; sys.path.insert(0, "tools"); import cdp
cdp.messen(720, 900, "dark", js, mobil=True)    # pointer: coarse
cdp.messen(720, 900, "dark", js, mobil=False)   # pointer: fine
```

**Drei Fallen, alle beim ersten Lauf hineingetreten:**

* **Nach einer CSS-Änderung neu laden.** `messen` lädt nicht von selbst; sonst misst man den
  alten Stylesheet und sucht den Fehler in der Regel.
* **`//`-Kommentare im übergebenen JavaScript**, wenn der Code per `tr '
' ' '` auf eine Zeile
  gefaltet wird — der Rest der Zeile ist dann auskommentiert (`SyntaxError: Unexpected end of
  input`). Block-Kommentare nehmen.
* **Die Windows-Konsole steht auf cp1252.** Ein Schliesskreuz im gemessenen Text reichte, um
  `print()` mit `UnicodeEncodeError` abbrechen zu lassen — die Messung war gelaufen und trotzdem
  verloren. `cdp.py` stellt stdout jetzt selbst auf UTF-8.

Was so **nicht** prüfbar bleibt: die Android-Zurück-Taste (echte Geste), Wischen (drei Anläufe,
siehe oben) und alles, was am Gerät „sich richtig anfühlen" muss.

## `tools/pruefstand-rueckblick-ziel.py` — der Beweis, dass eine Woche fehlt (26.08.2026)

**Was er prüft:** Eine Archivwoche ohne eigenes `target` darf in der Ziel-Quote nicht auftauchen.

**Warum es ihn gibt:** Seit `archiveWeek()` auch ohne Ziel archiviert (Paket 6, B2),
entstehen solche Wochen regelmäßig. Der Rückblick fiel dafür auf
`avgDailyTargetToday()` zurück — maß die Woche also am **heutigen** Ziel — und schrieb
„0 von 5 Tagen im Ziel" für eine Woche, in der es gar kein Ziel gab.

### ⚠️ Umgezogen am 03.09.2026: Er misst jetzt `zielQuote()`, nicht `rueckblickHtml()`

Mit Konzept G ist der Rückblick-Block aus dem Reiter genommen; die Kennzahl steht im
Kalenderfuß. **Die Zusicherung ist dieselbe geblieben — und genau deshalb wandert der
Prüfstand mit, statt zu verschwinden:** Eine Woche ohne eigenes `target` darf nicht
mitzählen, sonst wird sie am heutigen Ziel gemessen.

Ein Prüfstand, der weiter `rueckblickHtml()` gemessen hätte, prüfte eine Funktion **ohne
Aufrufer** — er wäre grün geblieben, während die angezeigte Zahl falsch sein könnte.
Das ist die Falle aus `docs/TROUBLESHOOTING.md` 144, zum vierten Mal.

**Nachtrag 04.09.2026:** Mit der Löschung des Rückblicks ist auch sein **Schnitt** ins
Leere gelaufen (`avgDailyTargetToday()` … `initRueckblick()` — beide Marker weg). Ein
Schnitt genügt seither, denn `zielQuote()` liegt im Kalenderblock; die Attrappen
`weekKwLabel()` und `avgDailyTargetToday()` sind entfallen, `dayStreak()` ist dafür neu
gestubbt — sie stand im gelöschten Bereich. `HEUTE_ZIEL` bleibt: Der Fehler, gegen den
dieser Prüfstand gebaut ist, war genau dieser Rückfall aufs heutige Ziel.

**Auch die Gegenprobe musste umziehen.** Sie lief gegen den Commit `76d1120` — dort gibt
es weder `zielQuote()` noch den Kalender, der Schnitt bricht mit „Startmarker nicht
gefunden“ ab. **Ein Abbruch ist kein roter Test.** Sie läuft jetzt über eine verstellte
Kopie (`NAIV_QUOTE`), der genau der `target`-Filter fehlt:

```powershell
python tools/pruefstand-rueckblick-ziel.py               # heute: 7 von 7 grün
python tools/pruefstand-rueckblick-ziel.py --gegenprobe  # ohne Filter: 3 ROT
```

Der alte Stand fällt nicht einfach durch — er sagt auch **warum**:

```
ROT  keine Bezugstage -> gezaehlt: 5
ROT  und der Fuss zeigt sie nicht
```

Eine Trefferquote über 23 Tage statt über die 12, für die es überhaupt ein Ziel gab — und
im leeren Fall eine Quote, die gar nicht dastehen dürfte. Ein Prüfstand, der beim
Durchfallen den Fehler *benennt*, ist mehr wert als einer, der nur rot wird.

### Drei `<script>`-Blöcke statt einem — und warum das kein Schönheitsdetail ist

Der erste Anlauf hatte Attrappen, ausgeschnittenen Code und Prüfungen in **einem** Block.
Ergebnis: **völlig leere Ausgabe.** Kein Fehler, kein Hinweis, nichts.

Der Grund: Der ausgeschnittene Bereich enthält `const STREAK_MIN_DAYS`, und daneben stand
eine gleichnamige Attrappe — `Identifier has already been declared`. Ein **Parse**-Fehler
tötet aber den ganzen Block, also auch `melde()` und `window.onerror`, die im selben Block
standen. Der Melder war tot, bevor er etwas melden konnte.

**Die Regel daraus:** Attrappen (samt Fehlermelder), Produktionscode und Prüfungen gehören
in **getrennte** `<script>`-Blöcke. Dann überlebt der Melder aus Block 1 einen Fehler in
Block 2 — und der dritte Block prüft zuerst `typeof zielQuote === "function"` (bis zum
04.09.2026: `rueckblickHtml`) und sagt im Zweifel „der Codeblock hat nicht geladen" statt
gar nichts.

Das ist die praktische Anwendung von „Ablauf-Trace statt Raten" (Abschnitt 2): Ein
Prüfstand muss auch dann sprechen, wenn er selbst kaputt ist.

**Und nicht stubben, was der Ausschnitt mitbringt.** `STREAK_MIN_DAYS` kommt jetzt aus dem
echten Code — das ist ohnehin näher an der Produktion als jeder selbst gesetzte Wert.

## `tools/alle-pruefstaende.py` — der Reihenlauf (26.08.2026)

```powershell
python tools/alle-pruefstaende.py            # alle
python tools/alle-pruefstaende.py rezept     # nur passende Namen
```

**Warum es ihn gibt:** Es gibt über zwanzig Prüfstände, und die CI kann keinen davon fahren
— sie brauchen Edge und Windows. Bis heute musste man jeden einzeln aufrufen **und wissen,
dass es ihn gibt.** Ein Prüfstand, den niemand mehr findet, ist so gut wie keiner.

**Kein Ersatz für den Einzelaufruf.** Wer an einer Sache arbeitet, fährt ihren Prüfstand
direkt — nur dort sieht man die vollständige Ausgabe. Der Reihenlauf ist für den Blick aufs
Ganze: vor einem größeren Commit, oder wenn man wissen will, ob irgendwo etwas
kaputtgegangen ist, woran man gar nicht gedacht hat.

### „Grün" heißt nicht überall dasselbe — und das hat sofort einen Fehlalarm erzeugt

Manche Prüfstände trennen `OFFEN` (Sollzustand, wird noch gebaut) von `REGRESSION`
(Bestehendes heil?) und lassen **nur die zweite Gruppe den Rückgabewert bestimmen** — sonst
wäre so ein Prüfstand während des ganzen Umbaus rot und als Warnsignal wertlos.

Der Reihenlauf sieht aber nur den Rückgabewert. Beim ersten Lauf meldete er
`pruefstand-wochenmaske.py` prompt als **„unerwartet grün"**, obwohl dessen Rückgabewert
absichtlich 0 ist. Deshalb gibt es jetzt die Liste `TEILWEISE`: Für die dort genannten
Prüfstände weist der Läufer ausdrücklich **„keine Regression"** aus statt „grün", mit einem
Satz dazu, was noch offen ist.

**Die Lehre:** Ein Läufer, der falschen Alarm schlägt, wird abgeschaltet — und dann läuft
gar nichts mehr. Lieber eine Zeile mehr Erklärung als ein Signal, dem niemand glaubt.

**Und die Gegenrichtung, seit 29.08.2026:** `TEILWEISE` ist eine **Ausnahme auf Zeit**. Ist
der Umbau fertig, gehören beide Gruppen wieder in den Rückgabewert und der Eintrag heraus —
sonst bleibt genau die Hälfte der Zeilen dauerhaft zahnlos, und niemand bemerkt es je wieder.
`pruefstand-wochenmaske.py` ist an dem Tag so zurückgestellt worden; die Liste ist seither
leer und wartet auf den nächsten Umbau.

## `tools/pruefstand-grpm-zoom.py` — eine Behauptung über die CSS-Kaskade messen (27.08.2026)

```powershell
python tools/pruefstand-grpm-zoom.py
```

**Die Frage:** Gilt für `.grp-m select` auf einem Touch-Gerät 16 px (kein iOS-Zoom) oder die
13 px aus der spezifischeren Regel weiter unten? Siehe `docs/TROUBLESHOOTING.md` §120.

**Warum das ein Browser beantworten muss.** Spezifität und Reihenfolge kann man am Quelltext
*behaupten* — welche Regel gewonnen hat, sagt nur `getComputedStyle()`. Und `pointer: coarse`
gilt ausschliesslich unter Touch-Emulation, also nur über das DevTools-Protokoll.

**Der Aufbau, drei Punkte, die andere Prüfstände übernehmen können:**

1. **Echtes CSS, ausgeschnitten.** Der komplette `<style>`-Inhalt aus `index.html` wandert
   unverändert in die Prüfseite. Ein nachgebauter Auszug hätte genau die Eigenschaft verloren,
   um die es geht — die Reihenfolge zweier weit auseinanderliegender Regeln.
2. **Der Prüftext hängt an denselben Klassen** wie `memberRowHtml()`: `.grp-m` mit Avatar,
   Name und `<select>`.
3. **Alles in EINER CDP-Verbindung.** `setTouchEmulationEnabled` gilt nur, solange sie offen
   ist — dieselbe Sitzungsbindung, die `tools/cdp.py` dokumentiert. Wer den Zeigertyp in einem
   eigenen Aufruf setzt, misst hinterher wieder `fine` und merkt es nicht.

**Die Gegenprobe steckt im Prüfstand selbst**, nicht in git: Er erzeugt eine zweite Seite, aus
der genau der neue `@media`-Block herausgeschnitten ist, und misst beide.

| | `<select>` |
|---|---|
| mit Touch, CSS wie es ist | **16 px** |
| mit Touch, neuer Block entfernt | 13 px — **die Gegenprobe** |
| ohne Touch, CSS wie es ist | 13 px — am Rechner unverändert |

Ohne die mittlere Zeile wäre nur belegt, dass irgendwo 16 px stehen — nicht, dass dieser Block
sie bewirkt. Ohne die dritte wäre nicht belegt, dass die Regel am Zeigertyp hängt statt einfach
immer zu gelten.

**Edge statt Chrome, eigener Port (9333).** `tools/cdp.py` fährt einen sichtbaren Chrome für
die Abnahme am echten Konto; läuft der Alltags-Chrome des Nutzers schon, lässt sich der
Debug-Port nicht mehr öffnen. Dieser Prüfstand braucht kein Konto und keine Sichtbarkeit,
deshalb Edge headless auf einem eigenen Port — er kollidiert mit nichts.

## `tools/pruefstand-einkaufsliste.py` — vier Läufe über beide Wochenreiter (28.08.2026)

Die Einkaufsliste hat zwei Zustände, die verschiedenen Dingen gehören: Die **Positionen**
kommen aus `state.plan` und wechseln mit dem Reiter von selbst mit. Der **abgehakte Zustand**
liegt in `localStorage` — und lag bis zum 28.08.2026 wochenblind darin
(`docs/TROUBLESHOOTING.md` §124).

Ein Fehler in localStorage lässt sich nicht durch Ausschneiden prüfen. Er entsteht erst aus dem
Zusammenspiel von Schreiben, Reiterwechsel und Neuöffnen — deshalb fährt dieser Prüfstand die
**ungekürzte `index.html`** headless und bedient sie wie ein Nutzer: Reiter anklicken,
Liste öffnen, Haken setzen, Woche wechseln, wieder öffnen.

### Warum vier Läufe und nicht einer

Jeder Lauf startet den Browser mit einem **anderen Ausgangszustand**. Das ist der Punkt: Drei
der vier Fragen lassen sich nur stellen, wenn schon etwas im Speicher liegt — und ein Lauf kann
nur mit einem Vorher anfangen.

| Lauf | Ausgangslage | Frage |
|---|---|---|
| A | leerer Speicher | Färbt ein Haken der aktuellen Woche auf die nächste ab? Nennt der Kopf — sichtbar *und* im Dialognamen — die richtige Woche? |
| B | **flaches Array** (Format vor dem Umbau) | Überlebt ein Haken den Neustart? Wo landet der Altbestand? |
| C | Objekt mit einer **drei Wochen alten** Woche darin | Verfällt sie, oder wächst der Eintrag ewig weiter? |
| D | leerer Speicher | Überlebt ein Haken die geänderte Personenzahl — und ändert sich die Menge trotzdem? |
| E | leerer Speicher, Web Share API abgeschaltet | Nennt der **PDF-Kopf** denselben Zeitraum wie das Modal? |

**Lauf C ist bewusst ein eigener Lauf.** In Lauf B liegt gar keine alte Woche im Speicher; die
Prüfung „nichts Fremdes bleibt stehen" wäre dort trivial erfüllt gewesen und hätte nichts
gemessen. Genau die Sorte grüner Zeile, die man später glaubt.

### Was die Läufe belegen, und was das kostet

Die Wochenschlüssel rechnet der Prüfstand in Python aus `datetime.isocalendar()` — dieselbe
ISO-Regel wie `isoWeekKey()`. Nachgebaut ist daran nichts: Der Schlüssel ist der *Eingabewert*
des Tests, nicht sein Prüfobjekt.

Die Rezepte teilen sich mit Absicht **eine** Zutat (`Hackfleisch`). Ohne sie hätten beide Wochen
verschiedene `norm`-Schlüssel, und der geteilte Speicher wäre nie aufgefallen — der Fehler
braucht eine Kollision, um sichtbar zu werden.

Geplant wird auf **alle sieben Tage**. In der aktuellen Woche zählt nur `ab heute`
(`planDaysAhead()`); wer nur Montag belegt, bekommt am Freitag eine leere Liste und einen Lauf,
der nichts aussagt.

### Gegenprobe

```powershell
git show HEAD:index.html > alt.html
python tools/pruefstand-einkaufsliste.py alt.html   # MUSS rot sein
python tools/pruefstand-einkaufsliste.py            # der neue Stand
```

| Stand | Ergebnis |
|---|---|
| vor dem Fix | **11 Fehler** — in allen vier Läufen |
| nach dem Fix | 37 grün |

Der Prüfstand nimmt einen Pfad als Argument, genau dafür. Dass die Fehler sich über alle vier
Läufe verteilen, ist selbst ein Befund: Der geteilte Speicher war nicht ein Fehler an einer
Stelle, sondern eine falsche Annahme, die an vier verschiedenen Stellen durchschlug.

### Lauf E (PDF): drei Fallen, die den Prüfstand selbst betrafen

Der PDF-Lauf war nicht schwer zu *denken*, aber dreimal falsch gebaut. Alle drei Fehler
gehören hierher, weil sie beim nächsten PDF-Prüfstand wieder auftreten.

**1. Der Knopf war gar nicht da.** Der Modal-Fuß zeigt *entweder* „Teilen" *oder* „Als PDF" +
„Als Text kopieren" — `canShare()` entscheidet. Headless Edge meldet `navigator.share`, also
rendert die App den Teilen-Zweig, und `[data-pdf]` existiert nicht. Der Lauf muss
`navigator.share` abschalten, sonst prüft er einen Zweig, den er nie sieht.

**2. `--virtual-time-budget` beendet Edge nicht, wenn ein Download läuft.** `saveBlob()` hängt
einen `<a download>` ins Dokument und klickt ihn; headless Edge startet daraufhin einen echten
Download und bleibt hängen — das Zeitbudget steuert die *Uhr*, nicht laufende I/O. Der Lauf
lief in den Timeout, neun Edge-Prozesse blieben stehen. Lösung: `HTMLAnchorElement.prototype.click`
für Elemente mit `download`-Attribut neutralisieren. Der Bytestrom wird ohnehin schon im
`Blob`-Konstruktor eingesammelt; das Speichern trägt zur Messung nichts bei.

> **Ein hängender Prüfstand ist erst einmal ein Befund, kein Defekt.** Hier war es am Ende der
> Prüfstand — aber das stand nicht vorher fest, und die Reihenfolge (erst messen, dann
> reparieren) ist nicht verhandelbar.

**3. Zweimal am Text vorbeigesucht.** `saveBlob()` bekommt `pdfBytes(...)`, also ein
`Uint8Array` — `String()` darauf ergibt `"37,80,68,70,…"`. Und im PDF steht der Umlaut nicht
als Buchstabe: `pdfEsc()` schreibt ihn als Oktal-Escape, „Nächste" wird zu `N\344chste`. Zwei
Umkehrungen sind nötig: Bytes latin-1 dekodieren, dann `\ooo` auflösen. Wer stattdessen nach
dem Wort sucht, sucht vergeblich — deshalb greift der Regex über die **Struktur** der
Kopfzeile (`scope` + `\267` + Datum), nicht über ihren Inhalt.

### Und ein Scheingrün, das der Riegel gefangen hat

Die erste Fassung prüfte „das PDF der nächsten Woche sagt NICHT ‚Diese Woche'" — und war
**grün gegen die Zeichenkette `"(keine Kopfzeile gefunden)"`**. Eine Nicht-Bedingung ist immer
erfüllt, wenn gar nichts da ist.

Deshalb steht vor den inhaltlichen Prüfungen ein Riegel, der erst feststellt, *dass* beide
PDFs entstanden sind und eine Kopfzeile tragen; die inhaltlichen Zeilen laufen nur dann. Beim
ersten Versuch prüfte dieser Riegel nur die eine Seite — und ließ die andere durchrutschen.

> **Jede Prüfung der Form „X kommt nicht vor" braucht eine zweite, die belegt, dass überhaupt
> etwas da ist.** Sonst misst sie das Nichts.

Dasselbe Muster ist der Grund, warum Lauf C ein eigener Lauf ist.


## `tools/pruefstand-gruppe-verlassen-dubletten.py` — der Rückweg aus der Gruppe (28.08.2026)

Gehört zu `docs/TROUBLESHOOTING.md` 125. Geprüft wird nicht „kommt etwas an“, sondern:

    nach Verlassen + Neustart trägt jede `lib` genau EINEN Eintrag

Der Prüfstand schneidet drei Funktionen aus `index.html` — `pruneOwnRecipes()`,
`syncRecipes()` und `mergeRemoteRecipes()` — und stellt ihnen ein **falsches Firestore mit
zwei Sammlungen** (`users/ich` und `groups/g1`) daneben, das die Batch-Semantik von
`saveRecipesBatch()` echt nachbildet. Die Testdaten sind die Konstellation, die den Fehler
garantiert erzeugt: fünf Startmeals je Konto mit **gleicher `lib` und eigener id** — `STARTER`
ist je Ernährungsform fest verdrahtet.

Nachgebildet ist nur die **Reihenfolge** aus `leaveGroup()`/`startCloudSync()`. Das ist die
Grenze dieses Prüfstands und sie gehört benannt: Er beweist, dass der Bestand nach dem
Aufräumen dublettenfrei ist — nicht, dass `leaveGroup()` `pruneOwnRecipes()` an der richtigen
Stelle aufruft. Das bleibt Sache der Abnahme am echten Konto.

Acht Abschnitte, 18 Prüfungen. Vier davon sichern die Grenzen der neuen Funktion ab, und alle
vier waren beim Entwurf die eigentliche Arbeit: **Nur-Leser** (ihr Bestand ist die einzige
Kopie und darf nicht geräumt werden), **leerer Behalten-Stand** (das Warnzeichen aus Ziffer
101, kein Auftrag zum Leerräumen), **Lesefehler** (darf nie zu einer Löschung führen) und
**Idempotenz**.

### Die Gegenprobe

Abschnitt 8 fährt denselben Ablauf ohne `pruneOwnRecipes()` — also die Fassung mit der bloss
geleerten Baseline — und verlangt, dass sie **rot** wird: **12 statt 7 Meals**, `lib`-Zählung
2, und wachsend mit jedem weiteren Zyklus. Das ist genau das Muster, das am 28.08.2026 am
echten Konto gemessen wurde (81 statt 43, `lib` bis dreifach). Ohne diesen Abschnitt bestünde
auch die kaputte Fassung den Prüfstand — die Aufräumung hätte nichts zu tun gehabt, weil im
Modell schon alles gestimmt hätte.


## `tools/pruefstand-gruppe-beitritt-cache.py` — ein Cache, der lügt (28.08.2026)

Gehört zu `docs/TROUBLESHOOTING.md` 126. Das Besondere ist nicht der ausgeschnittene Code,
sondern die **Attrappe**: Das falsche Firestore führt eine Liste `gesehen` mit den Sammlungen,
die der Cache schon einmal vom Server geladen hat. `loadRecipes()` liefert für alles andere
ein leeres Array zurück — **ohne zu werfen**, genau wie `getDocs()` mit
`persistentLocalCache`. `loadRecipesFromServer()` wirft stattdessen, wenn `serverOffline`
gesetzt ist.

Damit lässt sich der Unterschied überhaupt erst messen, um den es geht: *kalter Cache* (der
reale Zustand beim Beitritt) gegen *echtes Offline*. Im ersten Fall muss der Abgleich
funktionieren, im zweiten darf er ausfallen — aber der Beitritt darf nicht scheitern.

### Zwei Gegenproben, und die zweite ist die wichtigere

Abschnitt 7 fährt die alte Fassung (Cache-Weg) beim **kalten** Cache und verlangt Rot:
12 statt 7 Meals, `lib`-Zählung 2, nichts umgebogen.

Abschnitt 8 fährt **dieselbe alte Fassung** beim **warmen** Cache und verlangt Grün.

Ohne Abschnitt 8 bestünde der Prüfstand auch dann, wenn die alte Fassung aus irgendeinem
anderen Grund kaputt wäre. Erst das Paar belegt, dass die Ursache der Cache-Zustand ist —
und nur diese Aussage rechtfertigt den Umbau auf `getDocsFromServer()`.

> **Eine Gegenprobe zeigt, DASS die alte Fassung durchfällt. Erst eine zweite zeigt,
> WORAN.** Wer nur die erste baut, hat einen Beleg für das Symptom und keinen für die
> Ursache — und repariert beim nächsten Mal wieder die falsche Funktion (Ziffer 102).


## `tools/pruefstand-zuweisung-loeschen.py` — zwei Funktionen gegeneinander (28.08.2026)

Gehört zu `docs/TROUBLESHOOTING.md` 127. Der Prüfstand schneidet **zwei** Funktionen aus,
obwohl nur eine kaputt war: `dropRecipeIds()` und ihren Nachbarn `rewritePlanIds()`.

Das ist der Kern des Aufbaus. Beide müssen über dieselben Slot-Einträge dieselbe Menge
treffen — die eine biegt um, die andere entfernt. Abschnitt 6 prüft genau diese Symmetrie:
erst `rewritePlanIds("r1","rNEU")`, dann `dropRecipeIds({rNEU})`, und beides muss vollständig
durchgreifen. Ein Prüfstand nur für `dropRecipeIds()` hätte den Fehler zwar auch gefunden,
aber nicht gezeigt, **woran** man ihn hätte sehen können.

Die Testwoche enthält alle Formen, die das Datenmodell zulässt: „für alle“ (String),
„nur ich“, „nur die andere Person“, beide-als-Objekt und einen gemischten Slot aus Strings
und Objekten. Der gemischte Slot ist der wichtigste — er belegt, dass die übrigen Einträge
stehen bleiben, statt dass einfach der ganze Slot geleert wird.

### Wieder zwei Gegenproben

Abschnitt 8 fährt die alte Filterfassung und verlangt Rot: **4 von 5** Verweisen bleiben
stehen, entfernt wird nur die „für alle“-Form. Danach dieselbe alte Fassung an einer Woche
**ohne** Zuweisungen — dort muss sie Grün sein. Erst das Paar belegt, dass die Eintragsform
die Ursache ist.

### Was er NICHT misst

Dass die drei Aufrufer (`deleteRecipe()`, `onRecipesRemote()`, `startCloudSync()`) die
Funktion an der richtigen Stelle rufen. Der Prüfstand deckt den Helfer ab, nicht die
Verdrahtung — das bleibt Sache der Abnahme am echten Konto.


## `tools/pruefstand-gruppe-plan-mitbringen.py` — zwei Änderungen, zwei Gegenproben (28.08.2026)

Gehört zu `docs/TROUBLESHOOTING.md` 128. Deckt zwei Veränderungen ab, die nichts miteinander
zu tun haben außer dem Bereich: den nachgetragenen Wochenplan des Beitretenden und die
Migration, die in einer Gruppe nicht mehr läuft.

Der Attrappen-Cache ist derselbe wie in `pruefstand-gruppe-beitritt-cache.py` — `gesehen`
entscheidet, ob der Cache-Weg ein echtes oder ein leeres Ergebnis liefert, `serverOffline`
lässt den Server-Weg werfen. Damit lassen sich *kalter Cache* und *echtes Offline*
auseinanderhalten, und genau darauf beruht der Unterschied zwischen „nachtragen" und
„gar nichts tun".

`flattenWeek()` ist hier **bewusst gestubbt** statt ausgeschnitten: Gemessen wird
`mergeOwnPlanIntoGroup()`, nicht die Umwandlung einer Woche in flache Slot-Felder — die hat
ihre eigenen Prüfstände. Der Stub liefert die flache Form direkt.

### Die schwierigste Prüfung ist Abschnitt 9

`pr("das Flag bleibt UNGESETZT", state.dedupeV1 === false)` — dass in der Gruppe nichts
gelöscht wird, ist die halbe Aussage. Die andere Hälfte ist, dass die Migration danach noch
**stattfinden kann**. Würde `dedupeAgainstCatalog()` in der Gruppe das Flag setzen, wäre der
eigene Bestand nach dem Verlassen für immer unaufgeräumt — ein stiller Folgefehler, den ein
Test nur findet, wenn er ihn ausdrücklich fragt. Abschnitt 10 fährt deshalb direkt hinterher
und verlangt, dass sie nach `syncGid = null` sofort nachholt.

### Zwei Gegenproben

**A** (Abschnitt 8): der Cache-Weg überschreibt beim kalten Cache den fremden Slot — und ist
beim warmen Cache heil. **B** (Abschnitt 11): die alte Bedingung `syncGid && !syncHandshakeOk`
hätte mit erfolgtem Handshake mitten im Gruppenbestand gelöscht. Ohne B bestünde Abschnitt 9
auch dann, wenn die Testdaten gar nichts zu löschen hätten.


## `tools/pruefstand-sync-abriss.py` — eine Anzeige, die lügt (28.08.2026)

Gehört zu `docs/TROUBLESHOOTING.md` 129. Geprüft wird nicht „kommt ein Fehler an", sondern:

    nach einem Listener-Abriss zeigt der Status NICHT mehr "synced" —
    und der Nutzer bekommt GENAU EINEN Hinweis, nicht einen je Listener

Die zweite Hälfte ist der Grund, warum der Prüfstand mehr ist als eine Formalität. Greift eine
Firestore-Regel, scheitern alle vier Listener im selben Moment. Ohne Sperre wären das vier
Toasts hintereinander — eine Verbesserung, die sich sofort wieder als Ärgernis auszahlt.
Abschnitt 2 misst genau das: vier Protokolleinträge, ein Hinweis.

Die Attrappe ist winzig und trägt trotzdem den ganzen Test: ein `onSnapshot`, das je nach
`fehlerModus` entweder nichts tut oder asynchron den Fehlerpfad ruft. Mehr braucht es nicht,
weil die Messgröße nicht im SDK liegt, sondern in dem, was die App daraus macht.

### Was die Abschnitte 5 und 6 absichern

Der Melder läuft im Firebase-Modul, der Empfänger in der App — zwei Skriptblöcke, die
unabhängig scheitern können. Abschnitt 5 lässt `__onCloudWatchError` werfen, Abschnitt 6
entfernt es ganz. In beiden Fällen muss der Melder trotzdem protokollieren und darf nicht
weiterwerfen. Ein Fehlermelder, der selbst einen Fehler auslöst, ist die schlimmste Variante:
Er verwandelt eine gemeldete Störung in einen Absturz — dieselbe Falle, die bei `noteError()`
schon einmal beschrieben wurde (`docs/ARCHITECTURES.md`, „Warum die Position kritisch ist").

### Wieder zwei Gegenproben

Abschnitt 8 fährt die alte Fassung mit dem leeren `function () {}`: Der Status bleibt auf
„synced", kein Hinweis, kein Protokolleintrag — genau der gemessene Zustand vom 28.08.2026.
Abschnitt 9 belegt, dass die Attrappe im selben Modus wirklich feuert. Ohne ihn bestünde
Abschnitt 8 auch dann, wenn schlicht kein Fehler ausgelöst worden wäre.

### Was er NICHT misst

Dass Firestore einen fehlgeschlagenen `onSnapshot` wirklich endgültig beendet — das ist eine
Eigenschaft des SDK und hier als Annahme gesetzt. Wäre sie falsch, wäre die Behebung zu
streng (ein Hinweis, obwohl sich der Listener erholt), nicht zu lasch.


## `tools/pruefstand-waise-uids.py` — die Folge messen, nicht die Datenform (28.08.2026)

Gehört zu `docs/TROUBLESHOOTING.md` 130. Der naheliegende Prüfstand hätte nur gefragt:
„kommt `{ id, uids: [] }` durch?“ Das wäre richtig gewesen und hätte trotzdem das
Wichtigste nicht gezeigt.

Abschnitt 10 stellt deshalb alte und neue Fassung **nebeneinander** und misst die
Folgewirkung: `slotOpenForMe()` meldet bei der alten Fassung „Slot frei“, während im Slot ein
Eintrag steht — der Auto-Planer plant also darüber, und in der Zeile stehen danach zwei
Karten, von denen eine niemandem gehört. Neu ist der Slot frei **und** leer, der Widerspruch
ist weg.

> **Ein Prüfstand, der nur die Datenform prüft, belegt die Reparatur. Einer, der die
> Folgewirkung prüft, belegt den Schaden.** Nur der zweite sagt dem nächsten Leser, warum die
> Zeile so aussehen muss.

Abschnitt 2 ist der zweite Kern: Er füttert `uids: [null, 7, {}]` — also Daten, aus denen der
Sanitizer die Waise **selbst** erzeugt. Es braucht kein manipuliertes Dokument, ein
fehlerhaftes genügt, und genau das macht aus dem theoretischen Fall einen realen.

Dazu die übliche Absicherung der Nachbarschaft: Objekte ohne `uids` bleiben die String-Form
(§73), teilweise kaputte Listen behalten ihre Strings, die 24er-Deckelung hält, Müll fällt
weiterhin heraus. Und zwei Gegenproben — die alte Fassung lässt die Waise durch, liefert
aber **ohne** Waisen byte-gleiche Ergebnisse.


## `tools/pruefstand-einkauf-gruppe.py` — die Lücke im Nachbarprüfstand (28.08.2026)

`tools/pruefstand-einkaufsliste.py` deckt den Abhak-Zustand, die Wochenbindung, die
Personenzahl und den PDF-Kopf ab — und kennt **keine einzige Zuweisung**. Genau dort verläuft
in der Gruppe die interessante Grenze: Ein Slot-Eintrag ist entweder ein String („für alle")
oder `{id, uids}`.

Dieser Prüfstand hält den Vertrag fest, den `buildShoppingList()` und `buildBatchList()`
gemeinsam einhalten müssen:

    Endsumme = sharedQty * per + assignedQty

„Für alle" wird mit dem globalen Personenfaktor hochgerechnet; zugewiesene Gerichte sind
bereits pro Gericht auf `uids.length` skaliert und dürfen den globalen Faktor **nicht noch
einmal** abbekommen. Abschnitt 4 ist der schärfste Test: dieselbe Zutat (Tomaten) aus **beiden**
Arten im selben Lauf — 200 g „für alle" × 2 plus 50 g zugewiesen × 1 = 450 g. Ein Prüfstand mit
nur je einer Art bestünde auch dann, wenn beide Töpfe vertauscht wären.

Abschnitt 11 ist die Gegenprobe zum Aufbau: Mit zwei Mitgliedern muss 200 herauskommen, mit
drei 300. Ohne sie bestünden die Abschnitte 2–4 auch dann, wenn überall stumpf mit 1 gerechnet
würde.

Abschnitt 9 prüft die Zusage aus `planDaysAhead()`: Einkaufsliste und Vorkochliste müssen
**dieselbe** Woche beschreiben — sonst kauft man für einen Tag ein, den die Vorkochliste nicht
mehr kennt.

### Ein Abschnitt, der misst statt zu urteilen

Abschnitt 7 ist bewusst **kein** Fehlschlag, sondern eine Messung mit `MESS`-Zeilen. Er hält
fest, was „Einkauf für alle rechnen: **Aus**" tatsächlich tut: Der „für alle"-Anteil folgt der
Einstellung (einfache Menge), der **zugewiesene** Anteil nicht — dort steckt der
Mitglieder-Faktor im Eintrag selbst und bleibt erhalten.

Das ist heute so gewollt (jede zugewiesene Person braucht ein eigenes Meal) und steht trotzdem
quer zur Beschriftung „Mengen × Mitglieder". Die Entscheidung darüber gehört dem Inhaber, nicht
dem Prüfstand.

> **Ein Prüfstand darf eine offene Produktfrage festhalten, ohne sie zu beantworten.** Als
> `FAIL` getarnt wäre sie ein Dauerrot, das man wegklickt; als Messwert bleibt sie sichtbar und
> ändert sich mit, sobald jemand die Regel ändert.

### Zwei Schnittfehler, die der Prüfstand beim Bauen selbst produziert hat

Beide gehören ins Archiv, weil sie sich bei jedem Ausschneide-Prüfstand wiederholen können:

* `makeEmptyPlan()` endet mit `return p;`, nicht `return plan;`. Der Endmarker `return plan;`
  traf deshalb erst Hunderte Zeilen später — der Schnitt schluckte halb `index.html`, samt einer
  zweiten `syncUid`-Deklaration. Das Symptom war ein `SyntaxError`, nicht ein falsches Ergebnis.
* `shopPersons()` enthält `return own;` **zweimal** (Kurzausstieg und Schluss). Der Endmarker
  traf den ersten und lieferte eine Funktion, die bei einer Person `undefined` zurückgab —
  sieben Prüfungen wurden rot, obwohl der Produktionscode stimmte.

> **Ein Endmarker muss im Zielbereich EINDEUTIG sein.** Ein `return`, eine schließende Klammer
> oder ein `}` sind es fast nie. Wird ein Prüfstand ohne Codeänderung rot, ist der Schnitt der
> erste Verdächtige — nicht der Code.


## Ein Prüfstand, der nie lief: `pruefstand-katalog-plan.py` (28.08.2026)

Gehört zu `docs/TROUBLESHOOTING.md` 131. Das Skript **erzeugte** eine HTML-Datei, gab
`print("geschrieben")` aus und war fertig — Rückgabewert 0. Seine 45 Zusagen liefen nur, wenn
jemand die Datei im Browser öffnete. `tools/alle-pruefstaende.py` bewertet ausschliesslich den
Rückgabewert und meldete ihn deshalb bei jedem Durchgang grün.

Aufgefallen ist es nicht beim Lesen, sondern weil eine seiner Erwartungen durch Ziffer 128
falsch wurde — und der Reihenlauf trotzdem grün blieb.

Jetzt fährt er die Seite selbst headless, gibt jede Zeile aus und liefert einen echten
Rückgabewert; `window.onerror` meldet einen Absturz als `ERGEBNIS 0 grün, 1 rot` statt still
zu bleiben. Und er nimmt den Pfad zu `index.html` als **Argument** — ohne das lässt er sich
nicht gegen einen alten Stand fahren, und ohne Gegenprobe zählt hier kein Ergebnis. Belegt:
gegen `HEAD` 45 grün, gegen `30f4015` 43 grün / 2 rot.

> **Ein Prüfstand, dessen Rückgabewert nicht vom Prüfergebnis abhängt, ist kein Prüfstand.**
> Die Frage an jeden neuen lautet: *Kann dieses Skript überhaupt rot werden?*

**Es waren nicht einer, sondern acht.** Beim Bau der Reihenlauf-Prüfung kamen sieben weitere
Blindgänger heraus — zusammen **436 Zusagen**, die nie liefen, darunter alle drei
Gruppen-Prüfstände. Behoben über `tools/pruefstand_lauf.py`: Der gemeinsame Läufer hängt der
**erzeugten** Seite einen Beobachter an und liest ihr `#log` aus; die acht Prüfstände selbst
bleiben unangetastet (acht Umbauten wären acht Gelegenheiten, eine Zusage zu verändern).

**Einer war sofort rot.** `pruefstand-einladung-verbrauch.py` fiel beim ersten echten Lauf
durch — `mergeOwnPlanIntoGroup()` war nicht mitgeschnitten, der Aufruf lief in einen
`ReferenceError`. Ein Prüfstand, der nicht läuft, ist also nicht nur nutzlos: Er verdeckt
aktiv einen Fehler, den er gefunden hätte.

**Und das Netz darunter:** `alle-pruefstaende.py` verlangt jetzt eine Zeile, die ein Ergebnis
benennt (`BELEG_MUSTER`). Fehlt sie, meldet er `OHNE BELEG` und zählt den Prüfstand als
*auffällig* statt als grün — eine weiße Liste, damit ein neuer Prüfstand auffällt statt
durchzurutschen. Gegenprobe gefahren: Ein Skript, das nur `print("geschrieben: ...")` tut,
wird sofort gemeldet.


## `tools/pruefstand-cache-reset.py` — was NICHT passieren darf (29.08.2026)

Gehört zu `docs/TROUBLESHOOTING.md` 134. Der Knopf „Cloud-Verbindung zurücksetzen“ ruft eine
Funktion auf, die es längst gab. Zu prüfen ist deshalb nicht, **dass** gewischt wird, sondern
die drei Eigenschaften, an denen so ein Knopf scheitert:

1. **Er ist da, wenn er gebraucht wird — und nur dann.** Kein Cloud-Konto, kein `wipeCache()`
   im Modul (älterer Stand aus dem Service-Worker-Cache), gar kein `CloudSync`: keine Zeile,
   kein Absturz.
2. **Er fragt vorher**, und der Text nennt beides — was bleibt und was verloren geht.
3. **Scheitert das Wischen, wird NICHT neu geladen.** Abschnitt 5, und der eigentliche Grund
   für diesen Prüfstand: Der häufigste Fehlschlag ist kein Fehler, sondern ein zweiter offener
   Tab. Würde trotzdem neu geladen, sähe der Nutzer denselben kaputten Zustand wieder.

### Der Prüfstand hing zuerst — und der Grund gehört ins Archiv

Die Attrappe setzte `var location = { reload: ... }` auf oberster Ebene. **Im Browser ist
`location` global schreibgeschützt**: Die Zuweisung greift nicht, der ausgeschnittene Code rief
den ECHTEN `location.reload()` — und der Prüfstand lud sich selbst in einer Endlosschleife neu,
bis die Zeitgrenze zuschlug. Behoben, indem die ganze Seite in einen Funktionsbereich
gewickelt wird; dort verdeckt `let location` den globalen Namen sauber.

> **Ein hängender Prüfstand ist nicht automatisch ein Befund — aber auch nicht automatisch
> ein kaputter Prüfstand.** Hier war es weder: Es war eine Attrappe, die einen
> schreibgeschützten Namen überschreiben wollte.


## `tools/pruefstand-kontowechsel.py` — eine Gegenprobe, die in die Schleife läuft (29.08.2026)

Gehört zu `docs/TROUBLESHOOTING.md` 134. Geprüft wird **nicht**, dass beim Kontowechsel der
Cache geleert wird — das ist die leichte Hälfte. Die Messgröße steht in Abschnitt 4:

    nach dem Neuladen wird NICHT ERNEUT gewischt

Denn die Reihenfolge entscheidet über alles: merken, wischen, neu laden. Stünde das Merken
hinter dem Wischen, käme die Seite mit der alten gemerkten UID zurück, würde erneut wischen,
erneut neu laden — und die App startete nie wieder.

Abschnitt 8 baut genau diese falsche Reihenfolge nach und verlangt, dass sie **fünf Runden
lang** weiterläuft, während die richtige Fassung nach dem ersten Neuladen ruhig bleibt. Das
ist die seltene Gegenprobe, die einen Fehler nicht als falsches Ergebnis zeigt, sondern als
**Nichtterminierung** — und deshalb im Prüfstand nachgebildet statt live provoziert.

Dazu die Fälle, in denen nichts passieren darf (Erstanmeldung, dasselbe Konto, Modul ohne
`wipeCache`) und der Fehlschlag: Scheitert das Wischen, muss die Anmeldung trotzdem
durchlaufen — sonst sperrte ein zweiter offener Tab den Nutzer aus seiner eigenen App aus.


## Abnahme am echten Konto: Gruppen-Sync zu zweit (29.08.2026)

Kein Prüfstand, sondern ein Durchlauf am lebenden System — zwei angemeldete Konten auf zwei
Ursprüngen (Inhaber auf der Produktionsdomain, Testkonto auf `localhost`), damit beide
gleichzeitig eine eigene Sitzung haben.

| Geprüft | Ergebnis |
|---|---|
| Beitritt über den echten Einladungslink | `memberCount` 2→3 atomar, **keine Fehlermeldung** |
| Gruppenbestand danach | 44 → 44, keine doppelte `lib`, **keine Slot-Änderung** |
| Inhaber plant ein Meal | beim Testkonto **ohne Neuladen** da, als „für alle“ (leerer Slot) |
| Testkonto weist zu (3 Mitglieder → Chip-Popover) | korrektes `{id, uids}`, beim Inhaber sofort sichtbar |
| Badges | „PA“ + „L“ — die zweistellige Unterscheidung greift, weil *Paddy* und *Patrick* beide mit P beginnen |
| Änderungshinweis | „Patrick hat Sonntag geändert“ |
| Verlassen | Meals mitgekommen, **keine doppelte `lib`**, beide Zeiger geleert |
| Wiederherstellung | `memberCount`, Mitglieder, 44 Meal-IDs und alle Slots identisch |

### Zwei Fallen beim Vergleichen, beide hausgemacht

**Erstens:** Der erste Abgleich meldete neun Slot-Abweichungen. Acht davon waren **nur
Schlüssel-Reihenfolge** (`{"id":…,"uids":…}` gegen `{"uids":…,"id":…}`) — der Vergleich lief
über `JSON.stringify`, das reihenfolgeabhängig ist. Genau die Falle, gegen die `canonJSON()`
im Produktionscode gebaut wurde; ein Abnahmeskript darf sie ebenso wenig ignorieren.

**Zweitens:** Die neunte war `sun_sn: undefined → []`. Auch kein Unterschied: Ein geleerter
Slot wird von `pushGroupPlan()` ausdrücklich als leeres Array geschrieben, damit die Löschung
beim anderen Gerät ankommt. „Leer“ und „nicht vorhanden“ sind hier dasselbe.

> **Ein Abnahmeskript, das den Produktionscode prüft, muss dessen Vergleichsregeln kennen.**
> Sonst meldet es Unterschiede, die keine sind — und beim nächsten Mal glaubt ihm niemand.

### Was auch dieser Durchlauf NICHT gezeigt hat

Den ursprünglich gemeldeten Dublettenfall. Das Testkonto trug dieselben Dokument-IDs wie die
Gruppe (es hatte den Bestand bei einem früheren Austritt übernommen), der Abgleich in
`copyOwnRecipesToGroup()` hatte also nichts zu tun. Belegt ist der Fall weiterhin über
`tools/pruefstand-gruppe-verlassen-dubletten.py` und über die Rechnung gegen die 81 echten
Dokumente (`docs/TROUBLESHOOTING.md` 125, zweiter Nachtrag) — nicht durch einen beobachteten
Durchlauf. Dafür bräuchte es ein Testkonto mit **eigenen** Startmeals.

Der Auto-Planer in der Gruppe blieb ebenfalls aussen vor: Er füllt eine ganze Woche, und der
Rückbau wäre größer als der Erkenntnisgewinn. Er ist über `tools/pruefstand-autoplaner.py`
abgedeckt — 158 Prüfungen, die seit dem 28.08.2026 auch wirklich laufen (Ziffer 131).

## Aufteilung des Codes: was sich am Prüfverfahren ändert (29.08.2026)

Seit dem 29.08.2026 liegt ein Teil des Produktionscodes in `css/`, `data/` und `lib/`.
Am Verfahren ändert das drei Dinge — jedes davon ist eine Falle, die still zuschlägt.

**1. Der Syntax-Check braucht `--alles`.**

```powershell
python syntax-check.py --alles
```

Ohne das Argument prüft er nur `index.html` und meldet „sauber“, während ein
Syntaxfehler in `data/foods.js` die App genauso zerlegt. Die Dateiliste kommt aus
`tools/quelle.py`, damit sie nur an einer Stelle steht. `sw.js` wird seitdem mitgeprüft —
vorher gar nicht.

Der Hook `syntax-nach-edit.py` prüft die **geänderte** Datei gezielt und schweigt bei
allem, was kein App-JavaScript ist. Er prüft bewusst nicht ersatzweise `index.html`: eine
Prüfung, die etwas anderes ansieht als das Geänderte, meldet „sauber“ und beweist
nichts.

**2. Prüfstände laden die Seite über `tools/quelle.py`.**

```python
import quelle as pm_quelle
text = pm_quelle.lade_seite(INDEX)      # baut css/, data/ und lib/ wieder ein
CSS  = pm_quelle.css_gesamt(INDEX)      # alle vier Stylesheets in Ladereihenfolge
```

Ein Prüfstand schreibt seine Seite nach `tools/`. Ein relativer Verweis wie
`data/cookbook.js` zeigt von dort in ein tools/data/ — ein Verzeichnis, das es nicht
gibt. Die Seite lädt, das Skript fehlt, der Prüfstand misst nichts mehr. `quelle` setzt
denselben Text an dieselbe Stelle zurück; es bleibt echter Produktionscode.

Der Modulname ist `pm_quelle`, nicht `quelle`: mehrere Prüfstände benutzen `quelle`
bereits als **Variablennamen**. Beim ersten Umbau überschattete die lokale Variable das
Modul, und zwölf Prüfstände starben mit `UnboundLocalError`, bevor sie irgendetwas maßen.

**3. Was der Umbau tatsächlich gefunden hat.** Zwei Fälle, die eine Sichtprüfung nicht
gezeigt hätte — beide fielen erst im Prüfstandslauf auf:

* `liveScanStop` war als `let` am Ende des Barcode-Blocks deklariert, wurde aber vom Kern
  (`closeModal`) gesetzt und gelesen. Eine Analyse, die nur `function`-Deklarationen und
  GROSSGESCHRIEBENE Konstanten zählt, übersieht so etwas.
* `logoPdfAsset` ist ein Cache, den `prepareLogoForPdf()` füllt und `buildPrintable()`
  liest. Als Wert in einer Fassade wäre es eine Kopie vom Ladezeitpunkt — also immer
  `null`. Deshalb ein Zugriff (`PM.pdf.logoAsset()`) statt eines Werts.

Die Lehre: **geteilter veränderlicher Zustand ist die Stelle, an der ein Schnitt bricht**
— nicht die Funktionsliste.

**Gegenprobe des Umbaus.** Ein absichtlicher Syntaxfehler in `data/foods.js` muss den Hook
auslösen und die CI rot machen; ein absichtlich gebrochener Schnitt muss den betroffenen
Prüfstand durchfallen lassen; `python tools/karte.py --pruefe` muss nach einer
Strukturänderung ohne Neuerhebung mit Exit 1 abbrechen. Alle drei wurden gefahren und
anschließend vollständig zurückgesetzt.


## `tools/pruefstand-jahresumschalter.py` — ein Jahrgang, der nicht auftauchen darf (30.08.2026)

**Was er prüft:** `weightYears()` speist ab Paket 6/B6 den Jahr-Umschalter **beider** Karten
der Fortschritt-Seite — Gewicht und Kalender. Er muss deshalb die Jahre des Wochenarchivs
kennen, ohne dabei das Pufferjahr zu verraten.

```powershell
python tools/pruefstand-jahresumschalter.py            # heute: alles grün
python tools/pruefstand-jahresumschalter.py 91c202b    # davor:  fällt durch
```

**Der eigentliche Grund für diesen Prüfstand ist Abschnitt 2.** `sanitizeWeekStats()` behält
mit `archivJahreBehalten()` **drei** Jahrgänge, angeboten werden mit `archivJahreZeigen()`
nur **zwei** — die Differenz ist der Neujahrs-Puffer (`docs/ARCHITECTURES.md`,
„Archivfenster"). Eine naheliegende Fassung, die über `Object.keys(state.weekStats)` geht,
liefert dieselben Jahre wie die richtige, **solange keine Woche aus dem Pufferjahr existiert**
— und hebt den Puffer in dem Moment auf, in dem eine existiert. Genau diese Woche legt der
Prüfstand an.

### Die Falle beim Lesen der Gegenprobe

Beim alten Stand ist Abschnitt 2 **grün, aus dem falschen Grund**: Wo überhaupt kein
Archivjahr angeboten wird, kann auch kein Pufferjahr durchrutschen. Rot sind dort nur die Zeilen,
die ohne die Archivjahre gar nicht entstehen können.

Dasselbe Muster wie bei `pruefstand-wochenmaske.py` vor B3 — und dieselbe Lehre: **Zeilen
gehören paarweise gelesen.** Abschnitt 2 misst erst dann etwas, wenn Abschnitt 1 grün ist.
Wer nur auf den Zähler schaut, hält eine wirkungslose Zeile für einen bestandenen Test.

### Zwei Schnitte, weil die Funktionen weit auseinander liegen

`archivJahre()`/`archivJahreZeigen()` stehen bei `load()`, `weightYears()`/`activeYear()`
gut 3.800 Zeilen weiter bei der Gewichtskarte. Beide Bereiche werden **einzeln
ausgeschnitten** und in getrennte `<script>`-Blöcke gelegt (Attrappen, Code, Prüfungen —
siehe `pruefstand-rueckblick-ziel.py`). Der dritte Block bricht mit einer eigenen Meldung
ab, wenn eine der beiden Funktionen fehlt: sonst wäre ein misslungener Schnitt von einem
bestandenen Test nicht zu unterscheiden.

**Kein festes Jahr im Prüfstand.** Alle Jahre werden im Test aus `new Date().getFullYear()`
abgeleitet. Ein eingetragenes `"2026"` wäre am 1. Januar still falsch — und der Stichtag ist
hier ausgerechnet das, was geprüft wird.


## `tools/pruefstand-kalender.py` — die laufende Woche, die im Archiv fehlt (30.08.2026)

**Was er prüft:** `kalenderHtml()`, `kalJahrHtml()`, `kalMonatHtml()` und `dayStreak()`
(Paket 6, B7/B8) über `kalWoche()` und `kalTagStatus()`.

```powershell
python tools/pruefstand-kalender.py                      # heute: alles grün
python tools/pruefstand-kalender.py --gegenprobe         # naive kalWoche: fällt durch
python tools/pruefstand-kalender.py --gegenprobe-monat   # Monatstag statt Wochentag
```

**Zwei Gegenproben, weil zwei getrennte Aussagen zu sichern sind.** `--gegenprobe`
verstellt die gemeinsame Quelle und wirft Jahr **und** Monat um (12 rote Zeilen).
`--gegenprobe-monat` verstellt nur `kalTagStatus()` so, dass es das Bit über den
**Monatstag** statt den Wochentag greift — der naheliegende Off-by-one im Monatsgitter.
Dabei fallen **ausschließlich** die Monatszeilen (4 rote), die Zeilen 1–10 bleiben grün.
Genau das ist der Beweis, dass die Monatszeilen das Monatsgitter messen und nicht bloß
mitlaufen: Eine Gegenprobe, die *alles* rot färbt, zeigt nur, dass irgendetwas kaputt ist.

**Die Attrappen-Falle, die einen halben Prüflauf gekostet hat:** `SEITE` ist ein normaler
Python-String, kein Raw-String. Ein `\"` in einer Attrappen-Zeile löst Python zu `"` auf
und zerlegt damit den JS-Block — und weil `melde()` dann gar nicht erst existiert, gibt der
Prüfstand **überhaupt keine Zeilen mehr aus**, nur Kopf und Fuß. Das sieht nicht nach
einem Fehler aus, sondern nach einem leeren Lauf. In den Attrappen deshalb **einfache**
Anführungszeichen für JS-Strings mit HTML darin.

**Die Gegenprobe läuft nicht gegen einen Commit, sondern gegen eine verstellte Kopie.** Gegen
`91c202b` bräche der Schnitt mit „Endmarker nicht gefunden" ab, weil `kalenderHtml()` dort
noch gar nicht existiert — und **ein Abbruch ist kein roter Test**. Stattdessen ersetzt
`--gegenprobe` per Regex `kalWoche()` durch die naive Fassung, die nur ins Archiv schaut und
einen Datensatz ohne Maske als sieben Nullen liest. Genau die Zeilen, die B7/B8 ausmachen,
werden damit rot; alles Übrige bleibt grün.

**Zwei Fallen, die er selbst getreten hat:**

* Die erste Fassung zählte für „laufende Woche ist gefüllt" **alle** `on`-Zellen des Jahres —
  und war grün, während die laufende Woche leer war. Jetzt zählt sie die Spalte dieser Woche.
* Alle Daten entstehen relativ zu *heute*. Ein fest eingetragenes Datum wäre ab morgen eine
  andere Probe, und der Kalender ist die eine Ansicht, in der das Datum die Aussage ist.
* **Und genau daran ist der Tastatur-Abschnitt zuerst gescheitert:** Er startete die
  Pfeilprobe auf der *heutigen* Zelle. Am 30.08.2026 — einem Sonntag — ist das die letzte
  Zeile, `ArrowDown` geht dort zu Recht nicht, und der Test maß den Wochentag statt die
  Bedienung. Er startet jetzt auf einer festen, füllzellenfreien Zelle. **Relativ zu
  heute rechnen heißt nicht, von heute aus zu messen.**
* **Dieselbe Falle, zweite Auflage (30.08.2026):** Nach dem Umbau prüfte `ArrowUp` aus
  Zeile 1 heraus. Der 1. März 2026 ist ein Sonntag — Zeile 0 besteht dort fast nur aus
  Füllzellen, der Fokus bleibt völlig zu Recht stehen, und die Zeile war rot, ohne dass
  etwas kaputt war. Gemessen wird jetzt aus Zeile 2: Zeile 1 und 2 sind in **jedem** Monat
  voll.

Die Abschnitte 9 und 10 führen die Tastatur im echten DOM (`view` ist ein Knoten *im*
Dokument — ein losgelöstes Element nimmt keinen Fokus an).

⚠️ **Seit dem Wegfall des Bandes (30.08.2026) prüfen sie eine andere Zusicherung:** nicht
mehr *einen* Tabstopp im ganzen Jahr, sondern **einen je Monatsgitter, also zwölf**. Das ist
kein aufgeweichter Test — mit zwölf springt man gezielt in einen Monat, mit den 371 des
Bandes käme man aus der Karte nicht mehr heraus. Ebenso gedreht: Im Band war eine Spalte
eine *Woche*, im Monatsgitter ist sie ein *Tag* — `ArrowRight` geht einen Tag weiter,
`ArrowDown` eine Woche tiefer. Und `Home` springt auf Spalte **0**; im Band stand dort der
Zeilenkopf, weshalb die Grenze bei 1 lag.

Eine Zeile davon war kurz **grün aus dem falschen Grund**: Die Prüfung „der Tipp folgt dem
Fokus" lief nach einer Diagnosezeile, die per `mouseenter` denselben Tipp gesetzt hatte. Sie
leert ihn jetzt vor der Messung.

### Der flackernde Test — und warum er flackerte

Der Tastatur-Abschnitt meldete zunächst sporadisch `FEHLERZAHL=1`, während Einzelläufe
davor und danach grün waren. Notiert statt weggeklickt — und beim nächsten Reihenlauf war es
reproduzierbar: **„der Tipp folgt dem Fokus" schlug fehl, weil `focus()` kein Ereignis
auslöste.**

In einem headless-Fenster hat das Dokument nicht immer den Systemfokus. `element.focus()`
setzt dann zwar `activeElement` — die Prüfung darauf war ja grün —, feuert aber **kein**
`focus`-Ereignis. Der Handler lief nie, der Tipp blieb leer.

Der Test löst das Ereignis jetzt selbst aus, wenn der Tipp nach `focus()` leer geblieben ist.
Das ist keine Schönfärberei: Geprüft wird, dass der Handler am Element hängt und den Tipp
schreibt. Der Systemfokus ist eine Eigenschaft der Umgebung, nicht des Produkts.

**Die Lehre:** `activeElement` und ein gefeuertes `focus`-Ereignis sind zwei verschiedene
Dinge. Wer Fokus-Verhalten headless prüft, muss wissen, welches von beiden er misst.

## `tools/pruefstand-kalender-layout.py` — ein Überlauf, den niemand sieht (30.08.2026)

**Was er prüft:** dass **beide Ansichten** bei 360, 390, 768 und 1280 px in hell **und**
dunkel passen — ohne waagerechten Scroller, den sie bewusst nicht bekommen
(`docs/TROUBLESHOOTING.md` 58).

Gemessen im `srcdoc`-iframe mit echtem CSS (`quelle.css_gesamt()`) und echtem Markup. Ergebnis
der Messung, die die Papierrechnung ersetzt:

Gemessen **nach** dem Wegfall des Bandes (30.08.2026) — die Jahresspalte trägt jetzt
Mini-Monatsgitter, keine 5-px-Striche mehr:

| Breite | Zelle Jahr (B × H) | Zellbreite Monat | Monate nebeneinander |
|---|---|---|---|
| 360 px | 38,70 × 24,00 px | 40,84 px | 1 |
| 390 px | 43,00 × 24,00 px | 44,00 px | 1 |
| 768 px | 29,66 × 29,19 px | 53,14 px | 3 |
| 1280 px | 30,84 × 36,39 px | 53,14 px | 3 |

Stand 04.09.2026, nach der Anhebung auf `minmax(min(200px, 100%), 1fr)`. Davor: 21,25 px
bei 768 px und 22,14 px bei 1280 px, jeweils vier Monate nebeneinander.

⚠️ **Die Jahresspalte ist nicht monoton** — bei 360 px ist eine Zelle *breiter* als bei
768 px. Das ist kein Messfehler: Unter der 200-px-Grenze des `auto-fill`-Rasters passt nur
**ein** Monat nebeneinander, der dann die volle Breite bekommt. Ab zwei Spalten fällt die
Breite auf rund 30 px und bleibt dort, weil `max-width: 720px` verhindert, dass fünf Monate
nebeneinander rutschen. Wer hier eine monoton fallende Reihe erwartet, sucht einen Fehler,
den es nicht gibt.

**Zwei Untergrenzen und eine Obergrenze, weil zwei verschiedene Dinge unlesbar werden.**
In beiden Ansichten muss eine **Zahl** lesbar bleiben: 30 px im Monatsgitter (Zahl plus
Haken), früher 14 px im Mini-Gitter (Zahl auf der Fläche, kein Symbol). Bis zum Wegfall des
Bandes stand die zweite Grenze bei **2 px** — der Breite eines Strichs, der keine Zahl zu
tragen hatte.

**Seit dem 04.09.2026 steht sie bei 24 px, und gemessen werden beide Kanten.** Nicht wegen
der Lesbarkeit, sondern weil die Zelle ein **Tastziel** ist: Sie nimmt Klick, Hover und
Fokus an und schreibt ihren Wert in die Tipp-Zeile — WCAG 2.5.8 (AA) verlangt dafür
24 × 24 px. Gemessen waren es vorher 21,25 × 23 px bei 768 px. Die Breite hängt an der
Spaltenbreite des Grids, die Höhe an einem eigenen `clamp()`; eine Prüfung nur auf die
Breite hätte eine Zelle von 31 × 23 px durchgewinkt. Die Gegenprobe gegen den CSS-Stand
davor meldet **8 ROT** — vier davon die Höhe (alle Breiten), vier die Breite (ab 768 px).

**Nach oben ist nur der Monat gedeckelt (70 px)** — und diese Zeile hat sofort einen
echten Fehler gefangen: Die Höhe der Tageszelle ist bei 56 px gedeckelt, die Breite folgte
ohne `max-width` der Karte. Auf 1280 px standen die Tage dadurch als 168 × 56 px flache
Balken da — ein Balkendiagramm, kein Kalender. Die Antwort ist `max-width: 420px` auf
`.kal-grid.monat`, `.kal-nav` und `.kal-note.monat`.

### Seit 03.09.2026: auch die Wrapper werden gemessen

Der Prüfstand maß bis dahin **nur die Tabelle**. Mit Konzept G kamen zwei Elemente um sie
herum dazu — die Zeitraumwahl (`.zeitraum`) und der Kartenfuß (`.kal-foot`). Beide hätten
überlaufen können, ohne dass eine Zeile rot wird. Befund des `kvp`-Agenten im Pushcheck.

Zusätzlich gemessen wird jetzt das **Raster des Kartenfußes**: Drei Kennzahlen brauchen bei
den real verbleibenden 283 px Kartenbreite je rund 94 px, und „12/18 geplanten“ ist darin
nicht mehr lesbar. Unter 560 px müssen es deshalb **zwei Spalten** sein (bei drei Feldern
also 2 + 1), darüber alle nebeneinander.

⚠️ **Die Schwelle dieser Prüfung stand bis zum 04.09.2026 bei `fussFelder >= 4`** — der
Zahl der damaligen Kennzahlen. Mit dem Wegfall der „Geplant"-Kachel sind es höchstens drei:
Die Bedingung wäre nie wieder wahr geworden, und die Prüfung hätte sich **still selbst
abgeschaltet**, ohne dass eine Zeile rot wird. Sie steht jetzt bei `>= 2`, und daneben prüft
eine eigene Zeile, dass der Fuß überhaupt Kennzahlen trägt — ein leerer Fuß hätte die
Spaltenprüfung sonst einfach übersprungen und wäre grün geblieben.

⚠️ **Das ist ein gestaltetes 2×2-Raster, kein zugelassener `flex-wrap`-Umbruch.** Der
Unterschied ist sichtbar: Beim Umbruch stehen die Spalten der zweiten Zeile nicht unter
denen der ersten. Geprüft wird über die Zahl verschiedener `left`-Positionen.

⚠️ **Die Testdaten brauchen `target`.** Ohne es fällt die Ziel-Quote aus dem Fuß, es
bleiben drei Kennzahlen — und die Spaltenprüfung greift erst ab vier. Sie wäre stumm
grün geblieben.


### Die Lehre steckt in der Gegenprobe, nicht im Lauf

Die erste Fassung maß `scrollWidth - clientWidth` **am Dokument** — und blieb grün, obwohl die
Gegenprobe (`table-layout: auto`, 12 px Mindestbreite) das Gitter auf 407 px über die Karte
hinaus trieb. Der Grund: **`.wg-col` hat `overflow: hidden`.** Ein zu breites Gitter läuft gar
nicht über, es wird lautlos abgeschnitten — der Fehler, den der Prüfstand fangen sollte, war
für die Zahl, die er maß, unsichtbar.

**Und ein drittes Mal dieselbe Lehre, am 30.08.2026:** Nach dem Umbau suchte der Prüfstand
in der Jahresansicht weiter nach `td.kal-c`, der Zellklasse des Bandes. Der Selektor griff
ins Leere, meldete 0 px und wurde rot — die **vier Nachbarprüfungen daneben meldeten
weiterhin grün**, über ein Band, das es nicht mehr gab. Wäre die Zellbreitenprüfung nicht
dabei gewesen, hätte der Prüfstand den Umbau schweigend durchgewinkt. Genau der Fall aus
CLAUDE.md Abschnitt 18a: *Ein Prüfer mit veralteten Fakten prüft das Falsche und meldet
trotzdem „sauber".*

Die tragende Zeile heißt jetzt `tab.scrollWidth <= wrap.clientWidth`. **Ein Prüfstand, dessen
Gegenprobe grün bleibt, misst nicht das Falsche — er misst gar nichts.**

Zweite Falle desselben Laufs: Der Schalter für die kaputte Variante hing zuerst an
`location.search`. **Eine Query an einer `file://`-URL kam in Edge `--headless` nicht an**, die
Gegenprobe lief als Normallauf durch und war folgerichtig grün. Der Schalter steht seither in
der erzeugten Seite selbst.

## Konzept G: was die Prüfstände dabei gelernt haben (03.09.2026)

Der Umbau des Fortschritt-Reiters (ein Zeitraum, zwei Karten, Stepper beim Wiegen) hat
vier Prüfstände berührt. Zwei Muster daraus sind allgemein:

**Ein neuer Helfer im Ausschnitt braucht eine Attrappe — oder er reißt den Block ab.**
`kalenderHtml()` ruft jetzt `nfmt()`, `wochenSerie()` und `dayStreak()`. In
`pruefstand-kalender-layout.py` sind sie gestubbt (er misst **Breiten**, keine Zahlen —
eine echte Serie würde nichts anderes messen, aber den Ausschnitt vergrößern), in
`pruefstand-kalender.py` liegen sie im Schnitt. Fehlt einer, bricht der ganze
JS-Block mit `ReferenceError` ab, und die Seite meldet gar nichts.

**Was nicht mehr in der Karte steckt, muss die Hülle mitliefern.** Abschnitt 14 von
`pruefstand-kalender.py` prüfte die Ansichtswahl über `kalenderHtml()`. Die steht seit G
in `zeitraumHtml()`; der Prüfstand setzt beide zusammen (`zeitraumHtml() + kalenderHtml()`)
und prüft zusätzlich, dass es **genau eine** Zeitraumwahl gibt — die eigentliche Zusage
des Umbaus.

### Die Falle, die nur die echte App gefunden hat

Die **Tagesserie** („Am Stück · 9 Tage“) ist beim Umbau still verschwunden: Sie stand nur
in `rueckblickHtml()`, und mit dem Block war sie weg. Alle 31 Prüfstände blieben grün —
gefunden hat es `tools/probe-fortschritt.html`, weil die Seite die **vollständige App**
fährt und nach der Kennzahl sucht statt nach einer Funktion.

Sie ist eine eigene Produktentscheidung (`docs/PRODUCT.md`: andere Einheit, andere Regeln,
trägt die Flamme nicht) und steht jetzt im Kalenderfuß neben der Wochenserie.

⚠️ **Diese Probe läuft nicht in `alle-pruefstaende.py` mit** — sie ist eine Browser-Seite.
Wer nur den Gesamtlauf ansieht, übersieht genau die Fehler, die erst im Zusammenspiel
sichtbar werden. Nach jeder Änderung am Fortschritt-Reiter von Hand aufrufen.

### Zwei Fallen der Vorschau selbst

* **Der Testschlüssel.** Über `localhost` hängt die App an **jeden**
  `localStorage`-Schlüssel ein `__test` (`localKey`/`isTestOrigin`) — damit Prüfstände
  echte Daten nie anfassen. Wer in `wochenkueche_v1` schreibt statt in
  `wochenkueche_v1__test`, startet auf einem leeren Konto und sucht den Fehler im Code.
* **Der Browser-Cache.** Eine frisch geänderte `data/*.js` kommt im iframe aus dem Cache
  eines früheren Besuchs. Symptom: `ICON_FLAME is not defined`, obwohl `curl` die neue
  Datei liefert. Ein anderer Port erzeugt neue URLs und umgeht ihn zuverlässig; den
  Service Worker abzumelden allein genügt **nicht**.

## Abnahme des Fortschritt-Reiters im Browser (04.09.2026)

**Ausgangsstand:** `71787b1`. **Endstand:** unverändert — die Abnahme hat keinen
Produktionscode angefasst, nur Befunde erzeugt.

**Aufbau:** `python -m http.server 8000` statt `test-server.ps1` (die Execution Policy
sperrt PowerShell-Skripte auf diesem Rechner), dazu `tools/cdp.py start`. Im
Abnahme-Chrome war ein **echtes Cloud-Konto** angemeldet; erfundene Datenlagen hätten in
echte Firestore-Daten geschrieben. Deshalb: Profilordner `%TEMP%\mp-chrome-abnahme`
beiseitegelegt, mit frischem Profil ohne Konto im **lokalen Modus** geprüft, danach
zurückgespielt. `localhost` trennt nur den lokalen Speicher (`__test`), **nicht die Cloud** —
das Beiseitelegen des Profils ist die einzige verlässliche Trennung.

**Datenlage** (in `wochenkueche_v1__test` gesetzt, dann `location.reload()`): 14 Wochen mit
eigenem `target`, **3 Wochen ohne** `target`, eine Altwoche **ohne Maske** (`d` fehlt), eine
Woche im Vorjahr, 17 Gewichtseinträge.

### Drei Messfallen, die hier Zeit gekostet haben

**`.click()` ist am Stepper kein Test.** Die Wiegen-Knöpfe hängen an `pointerdown`; ein
synthetischer Klick lässt den Wert unverändert und sieht aus wie ein Fehler. Echte Ereignisse
über `Input.dispatchMouseEvent` (Press + Release auf die Mitte des Elements) — erst damit
zählt der Stepper. Dasselbe gilt für Menüs: Ein Klick auf Koordinaten **außerhalb des
Viewports** trifft nichts, ohne zu scheitern; vorher `scrollIntoView({block:'center'})`.

**Direkt nach `location.reload()` gemessene Breiten sind wertlos.** Eine Messung meldete
16 px waagerechten Überlauf bei 360 px; stabil gemessen sind es 0. Wer das ungeprüft meldet,
jagt ein Layoutproblem, das es nicht gibt.

**`Emulation.setEmulatedMedia` als Einzelaufruf ist wirkungslos** — es gilt nur, solange die
Verbindung offen ist (steht so im Abschnitt zu `cdp.py messen`, und ist mir trotzdem
passiert). Das Light-Theme wurde deshalb über `python tools/cdp.py messen 390 800 light "…"`
geprüft: Label `#6B5F62`, Wert `#1A1416`, Trennlinie `#E7E0E1` — greift.

### Was nachweislich funktioniert

| Geprüft | Ergebnis |
|---|---|
| Leerzustand | kein Fuß, Notiz „Noch kein geplanter Tag." |
| Ziel-Quote im Jahr | „Im Ziel 55/72 geplanten" — **gegengerechnet**, entspricht exakt den Testdaten |
| Zusicherung B10 | die 3 zielfreien Wochen (15 Tage) sind **nicht** im Nenner — in der echten App belegt, nicht nur im Prüfstand |
| Monatsblättern | September → August → Mai; Pfeile am Archivrand gesperrt |
| Jahreswechsel | 2025 zeigt „Im Ziel 5/6 geplanten", „Nächstes Jahr" am Rand gesperrt |
| Altwoche ohne Maske | 7 neutrale Zellen, `<span class="visually-hidden">Tage nicht aufgezeichnet</span>` |
| Tastatur im Gitter | ein Tabstopp (heute), Pfeile, Home/End = Wochenanfang/-ende, Rand blockiert, Tipp-Zeile folgt dem Fokus |
| Wiegen-Stepper | Maus **und** Tastatur (Enter/Space), Differenzzeile aktualisiert live |
| Speichern | Eintrag steht in `state.weights`, Kartenfuß rechnet mit, Ziel wird neu berechnet (2.451 → 2.545 kcal) mit sichtbarer Begründung |
| Jahresziel | derselbe Stepper, Startwert = letzter Stand, Einordnungszeile „10,1 kg unter deinem letzten Stand" |
| Escape / Zurück-Taste | schließen den Dialog, der Reiter bleibt stehen |
| Mobil 360 px | Zelle **38,19 × 24 px** (die 24-px-Untergrenze greift), kein Überlauf, Fuß als 2 + 1 |
| Light-Theme | greift, Kontraste stehen |

### Was dabei aufgefallen ist

Die Befunde stehen in `docs/TROUBLESHOOTING.md` — der wichtigste: **„Verlauf verwalten" ist
mit erteilter Einwilligung über die UI nicht erreichbar.**

## `tools/probe-fortschritt.html` — die Abnahme in der echten App (30.08.2026)

Prüfstände messen ausgeschnittene Funktionen. Diese Seite lädt die **vollständige** App in
einem iframe, legt vorher einen fertigen Zustand ins `localStorage` und klickt sich in den
Fortschritt-Reiter — Reihenfolge der Karten, gefüllte laufende Woche, Jahr-Umschalter über
beide Karten, Tipp, Tages-Serie.

```powershell
powershell -NoProfile -File test-server.ps1
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu `
  --virtual-time-budget=45000 --user-data-dir="<scratchpad>\edge" --dump-dom `
  http://localhost:8000/tools/probe-fortschritt.html > dump.html
```

Sie läuft **nicht** im Reihenlauf mit: Sie braucht einen Server. Das Zeitbudget muss über dem
6-Sekunden-Rückfall in den lokalen Modus liegen — bei 30000 brach sie sporadisch mit
„Zeit abgelaufen" ab, bei 45000 nicht mehr.

### Drei Befunde, und zwei davon waren die Testdaten

Genau dafür ist die Abnahme da — die drei roten Zeilen des ersten Laufs:

* **Der Plan ist nach Mahlzeiten gegliedert** (`plan[tag][fr|mi|ab|sn]`), nicht flach je Tag.
  Eine flache Liste lässt `dayNutOf()` ins Leere greifen: kein Fehler, keine Meldung — die
  Woche ist einfach still leer.
* **Nährwerte liegen unter `r.nutrition`**, nicht flach am Rezept. Flach daneben geschrieben
  existieren sie für `recipeNut()` nicht, und jeder Tag gilt als unbeplant.
* **Die 16 px, die keine waren.** Der Reiter meldete 16 px waagerechten Überlauf. Nachgemessen
  mit einem `git worktree` auf `91c202b` und einem zweiten Server: **derselbe Wert im alten
  Stand.** Es war die klassische Scrollleiste des iframe, die 15 px von `clientWidth` nimmt
  (Abschnitt „Überlauf gegen `innerHeight` prüfen"). Gegen `innerWidth` gemessen: 0.

Der Umweg über den Worktree hat sich gelohnt — ohne ihn hätte die Zahl wie ein Befund dieser
Änderung ausgesehen. **Wer einen Messwert nicht einordnen kann, misst denselben Wert am alten
Stand.**


## `tools/probe-onboarding.html` — wie weit der Weiter-Knopf springt (30.08.2026)

**Was sie misst:** Paket 5 des Alltags-Plans beginnt ausdrücklich mit *messen*, nicht mit
umbauen. Die Frage lautet: Wie weit wandert der Weiter-Knopf zwischen den Bildschirmen der
ersten Schritte — und muss überhaupt einer scrollen?

Gefahren wird die **echte App** im iframe. Der Wizard startet über „Neu berechnen"
(`data-action="recalc-goal"`): Dann sind alle Felder aus dem vorhandenen Ziel vorbelegt, und
man klickt durch, ohne Eingaben zu erfinden. Gemessen wird je Bildschirm die Höhe von
`.onb-stage`, die Absolutposition von `.onb-next` und `scrollHeight - innerHeight`.

```powershell
powershell -NoProfile -File test-server.ps1
# http://localhost:8000/tools/probe-onboarding.html            (Messung)
# http://localhost:8000/tools/probe-onboarding.html?kaputt=1   (Gegenprobe)
```

### Das Ergebnis, auf dem Schritt 2 aufsetzt

| Breite | größter Sprung des Weiter-Knopfes | Bildschirme, die scrollen |
|---|---|---|
| 390 px | **420 px** | 3 von 8 (bis 138 px) |
| 768 px | 402 px | 3 von 8 |
| 1280 px | 402 px | 3 von 8 |

Die Bühne schwankt zwischen **64 px** („Da fehlt noch etwas") und **538 px** („Wie viel
bewegst du dich?"). Der Knopf steht damit mal bei 251 px, mal bei 721 px — auf demselben
Bildschirm, im selben Ablauf, zwei Klicks auseinander.

**Zwei Dinge, die die Messung entscheidet:**

* Das Problem ist **nicht mobil-spezifisch**. 402 px bei 1280 px Breite sind fast dasselbe
  wie 420 px bei 390 px — eine reine Mobile-Korrektur würde daneben greifen.
* Es gibt **Bildschirme, die auch bei 390 px scrollen müssen** (bis 138 px). Ein pauschaler
  Deckel auf die Bühnenhöhe würde sie abschneiden; die Antwort ist der weiche Höhenübergang,
  nicht die feste Höhe.

### Die Gegenprobe misst die Lösung mit

`?kaputt=1` gleicht alle Bühnen per `min-height: 620px` an. Der größte Sprung fällt damit von
420 px auf **58 px** — die Messung trennt also nachweislich.

Ein Aufschlag auf *alle* Bühnen (`padding-bottom: 200px`, wie zuerst geplant) hätte dagegen
nichts bewiesen: Er verschiebt jeden Bildschirm gleich weit und lässt die Sprünge unverändert.
**Eine Gegenprobe muss die gemessene Größe verändern, nicht irgendeine.**

### Drei Fallen, die sie gekostet hat

* **„Neu berechnen" sitzt auf Home**, an der Wochenziele-Karte (`weekGoalHtml`), nicht im
  Plan-Reiter. Über den Plan gesucht, fand die erste Fassung den Knopf nur bei 1280 px — und
  übersprang stillschweigend genau die beiden Breiten, auf die es ankommt.
* **Der Zustand gehört vor jeden Rahmen gelegt, nicht einmal an den Anfang.** Der Wizard des
  vorigen Laufs schreibt in denselben `localStorage`-Schlüssel; beim zweiten Rahmen fehlte
  dadurch das Ziel, und ohne Ziel gibt es keine Zielkarte und keinen Einstieg.
* **Der Fokus wandert 30 ms nach dem Zeichnen in die Frage** (`renderOnboardStep`) und
  verschiebt dabei die Scrollposition. Vor jeder Messung abwarten, sonst misst man den
  Fokussprung statt das Layout.


## `tools/probe-onboarding-fluss.html` — den Weg messen, nicht das Ziel (30.08.2026)

**Warum es eine zweite Probe braucht.** `probe-onboarding.html` misst Endpositionen. Nach dem
Umbau von Paket 5 liefert sie **exakt dieselben Zahlen** wie davor — 420 px bei 390 px, 402 px
bei 1280 px. Das ist kein Fehlschlag, sondern richtig: Der Übergang ändert den *Weg* zur neuen
Position, nicht die Position. Wer nur diese Probe fährt, hält den Umbau für wirkungslos.

Die zweite Probe misst deshalb vier Dinge, die eine Endpositions-Messung nicht sehen kann:

1. **Überlebt das Gerüst?** Bühne, Fuß und Fortschritts-`<span>` müssen nach einem
   Bildschirmwechsel **dieselben Knoten** sein — sonst kann nichts weich übergehen.
2. **Wird die Höhe gehalten und wieder freigegeben?** Während des Übergangs muss
   `style.height` stehen, danach muss `getAttribute("style")` leer sein. Bliebe sie stehen,
   wäre die Bühne auf der Höhe von gestern eingefroren.
3. **Steht der Bildschirm still, wenn man nur eine Kachel antippt?** Geprüft über
   `getComputedStyle(kachel).animationName === "none"`.
4. **Ist ein Klick auf „Weiter" genau ein Schritt?** Die Fuß-Knöpfe überleben jetzt — würden
   ihre Handler weiter je Schritt gebunden, wäre ein Klick zwei Schritte.

### Abschnitt 5 fand einen Fehler, den der `kvp`-Agent zuerst nur vermutet hatte

**Ohne Ziel darf es keinen Ausgang geben** (`maybeStartOnboarding`). Seit der
Schließen-Knopf immer gebaut und nur per `hidden` gesteuert wird, hängt diese Regel an einer
CSS-Frage: `.btn` setzt `display: inline-flex`, und eine **Autorenregel schlägt das
`[hidden] { display: none }` des Browsers** — bei gleicher Spezifität gewinnt die
Autoren-Ebene, unabhängig von der Reihenfolge.

Gemessen: `display: flex`, `offsetParent` gesetzt. Der Ausgang wäre sichtbar und klickbar
gewesen, ohne dass ein Ziel existiert. Behoben mit `.onb-skip[hidden] { display: none; }` —
derselbe Fall wie `.ms-photobtn[hidden]` in `komponenten.css`, den es dort seit Längerem gibt.

**Ein übersprungener Abschnitt ist keine grüne Zeile.** Abschnitt 4 lief zunächst mal mit,
mal nicht — je nachdem, ob die Abschnitte davor auf einem Bildschirm mit Pflichtfeld
endeten. Er bekommt jetzt einen eigenen, frischen Rahmen.

### Gegenprobe

Gegen den Stand vor dem Umbau (`git worktree` auf `b7017f3`, zweiter Server auf eigenem
Port): **11 rote Zeilen**, gegen den neuen Stand **null**. Damit die Bilanz ehrlich bleibt, bricht die
Probe ohne Gerüst nicht ab, sondern zählt die nicht messbaren Abschnitte als rot — ein Abbruch
wäre kein roter Test.

### Zwei Fehler, die erst diese Probe gefunden hat

* **„Schritt −54 von 8".** `animateOnbProgress()` läuft 700 ms in `requestAnimationFrame`.
  Solange `#view` bei jedem Schritt ersetzt wurde, schrieb eine noch laufende Schleife in
  einen abgehängten Knoten — wirkungslos. Seit der Knoten überlebt, überholen sich mehrere
  Schleifen gegenseitig. Behoben mit einer **Laufmarke**: Nur der jüngste Lauf zeichnet.
* **„Schritt −66 von 8", und das war ein Bestandsfehler.** Beide rAF-Schleifen der App
  klemmten ihren Fortschritt nur nach **oben** (`Math.min(1, …)`). Ist `now` kleiner als `t0`
  — unter virtueller Zeit im Prüfstand regelmäßig, bei einer zurückgestellten Uhr auch auf
  echten Geräten —, wird `p` negativ, und die Kurve `1-(1-p)³` verstärkt das kräftig. Jetzt
  steht `Math.max(0, Math.min(1, …))` in beiden Schleifen.

### Die Lehre für den nächsten Prüfstand: nicht die animierte Zahl messen

Abschnitt 4 war zweimal rot, ohne dass etwas kaputt war: Er las den **sichtbaren** Zähler
(„Schritt 3 von 8"), und der läuft 700 ms lang animiert von der alten zur neuen Zahl. Gemessen
wird jetzt `aria-valuenow` an der Progress-Bar — der Wert steht sofort richtig, und er **muss**
es, sonst läge ein Screenreader 700 ms lang daneben.

**Eine animierte Anzeige ist kein Messpunkt.** Wo eine Animation den sichtbaren Wert langsam
nachzieht, gehört die Messung an die Stelle, die den Zustand sofort trägt.
