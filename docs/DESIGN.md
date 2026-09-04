# DESIGN.md

# „Performance Dark" — das Design-System

**Verbindlich für jede neue oder geänderte UI.** Kein eigener Stil, keine fremden
Farbpaletten, keine externen Fonts, keine Design-Neuerfindung. Neue Elemente fügen sich in
das bestehende System ein.

Dieses Dokument stand bis zum 26.08.2026 vollständig in `CLAUDE.md`. Es ist von dort
hierher gezogen, **wortgetreu und ohne Regeländerung** — die Begründungen gehören dorthin,
wo man sie sucht, wenn man sie braucht, und nicht in eine Datei, die bei jeder Sitzung
vollständig mitgeladen wird.

In `CLAUDE.md` steht weiterhin die kurze Fassung: die Regel und der Zeiger hierher.

**Register:**

| Abschnitt | Inhalt |
|---|---|
| Bestehende CSS-Tokens | die Variablen, die zu verwenden sind |
| Typografie · Farbe · Theme · Form | Grundlagen |
| Makros und Nährwerte | die drei erlaubten Formen, verbindlich |
| Abschnittsüberschriften `.sec-h` | genau eine Form, an einer Stelle |
| Markencharakter | Slogan, Logo |
| Design-Skills | Reihenfolge und Mapping-Regel |
| Mehrstufige Abläufe | Progress-Bar, `initCarousel()` |
| Schiebe-Schema | Ansichtswechsel, Bewegung, `MOTION`-Tokens |
| Die ersten Schritte bewegen sich wie der Rest | Wizard: `slideIn()`, Höhenübergang, `.onb-still` |
| Der Fortschritt-Kalender | zwei Gitter in einer Karte, `max-width: 420px`, Symbolsprache |

---


**Jede neue oder geänderte UI muss im bestehenden Design „Performance Dark“ umgesetzt werden.**

Kein eigener Stil.

Keine fremden Farbpaletten.

Keine externen Fonts.

Keine Design-Neuerfindung.

Neue Elemente müssen sich in das bestehende System einfügen.

### Bestehende CSS-Tokens verwenden

Für Farben, Flächen, Typografie und Form bevorzugt die bestehenden CSS-Variablen aus
`css/tokens.css` verwenden (dort stehen alle vier Theme-Blöcke; die Komponenten-Styles
liegen in `css/basis.css`, `css/komponenten.css` und `css/mobil.css` — Regeln dazu in
`css/CLAUDE.md`):

```text
--font-display
--font-body

--accent
--accent-strong

--bg
--surface
--surface-2

--text
--text-muted

--border
--border-strong

--radius
--radius-sm

--shadow
--maxw

--fr
--mi
--ab
```

Keine Werte unnötig hartkodieren, wenn ein vorhandener Token dafür existiert.

### Typografie

Headlines/Display:

`var(--font-display)`

Fließtext:

`var(--font-body)`

Nur System-Fonts.

Kein externes Font-CDN.

### Farbe

Akzent:

`--accent`

Rot ist der zentrale Akzent.

Light- und Dark-Werte immer berücksichtigen.

### Theme

Bestehende Light-/Dark-Mechanik erhalten.

Insbesondere:

* `@media (prefers-color-scheme: dark)`
* `:root[data-theme=…]`

Nicht nur einen Theme-Zustand pflegen.

### Form

Bestehende Werte für:

* Radius
* Shadow
* maximale Breite

verwenden.

### Makros und Nährwerte

**Kalorien und Makros werden in der ganzen App gleich benannt, gleich sortiert und in einer der drei festgelegten Formen dargestellt.**

Verbindlich:

* Kürzel: `KH`, `P`, `F`
* Reihenfolge: `kcal → KH → P → F`
* In der Kompaktform **kein** `g` — Makros sind immer Gramm, das Kürzel trägt die Bedeutung. Nur die ausführliche Kachelform zeigt die Einheit.
* Farben ausschließlich über die bestehenden Tokens `--prot`, `--carb`, `--fat` und die `t-*`-Klassen.

Nie wieder einführen:

* `K` für Kohlenhydrate (verwechselbar mit kcal)
* `Eiw.` oder `Fett` ausgeschrieben in Wertzeilen
* eine eigene Reihenfolge „weil es hier besser passt"

#### Die drei erlaubten Formen

**1. Kompaktzeile** — überall dort, wo Werte nur abgelesen werden: Meal-Karte, Zutaten-Anzeigezeile, Makro-Ruhezustand der Meal-Ansicht, Tagesbilanz im Wochenplan. Läuft über den gemeinsamen Helfer, nicht über neu geschriebenes Markup.

**2. Kachelform** (`.nutfacts`) — wo Platz ist und die Zahl im Mittelpunkt steht, etwa im Nur-Lese-Modus der Meal-Ansicht. Mit Einheit.

**3. Balkenform** (`.wg-macros`) — ausschließlich für Fortschritt gegen ein Ziel, nicht für einen reinen Wert. Die **Reihenfolge** gilt auch hier. Die Beschriftung darf ausgeschrieben bleiben (`Kohlenhydrate`, `Protein`, `Fett`): Dort ist Platz, und die Spaltenbreite ist nachweislich auf das längste Wort ausgelegt (siehe Kommentar bei `.wg-macros .gm`). **Nicht auf Kürzel umstellen** — das bricht das Layout auf schmalen Tageskarten.

Langform und Kürzel derselben Begriffe sind kein Widerspruch. Verboten ist ein **drittes** Vokabular: `K`, `Eiw.` oder frei erfundene Abkürzungen.

Fließtext ist von alldem ausgenommen: In ganzen Sätzen (z. B. der Onboarding-Zusammenfassung) darf und soll ausgeschrieben werden.

Eine vierte Form wird nicht erfunden. Passt ein neuer Ort in keine der drei, ist zuerst zu prüfen, ob er wirklich etwas anderes zeigt.

#### Wann die Kompaktzeile ganz entfällt (29.08.2026)

**Bei einer Zutat, die in TL oder EL dosiert wird und unter 15 kcal beiträgt, steht keine
Nährwertzeile.** Ein halber Teelöffel Salz zeigte dort `0 kcal · 0 KH 0 P 0 F` — vier Zahlen,
die nichts aussagen, an genau der Stelle, an der der Blick die Menge sucht.

Die Entscheidung fällt in `ingShowsNut()`, **einmal** für beide Ansichten: die Leseansicht
(`roIngRowHtml`) und den Ruhezustand einer Zeile im Meal-Editor (`paintIngView`). Die beiden
zeigen dieselbe Zeile; eine Regel an zwei Stellen läuft auseinander, sobald sie sich ändert.

Die Grenze steht bewusst **neben** der Einheit statt allein auf den Kalorien: Nach reinen
Kalorien ließe sich nicht trennen, was zu trennen ist — 1 TL Vanilleextrakt und 100 g Gurke
liegen beide bei 12 kcal. Und ein **Ess**löffel Öl sind 90 kcal; die gehören sichtbar, auch
wenn die Einheit dieselbe ist. Erst beides zusammen trifft die Gewürze und nur sie.

Das ist keine vierte Form, sondern das Weglassen der ersten. Die Menge und der Name bleiben.

**Dieselbe Zutatengruppe hat eine zweite Folge — in der Einkaufsliste entfällt dort die
Menge.** Man kauft eine Packung Salz, nicht „1¼ TL": Die Löffelmenge ist beim Kochen die
Information, im Laden ist sie Rauschen. `buildShoppingList()` setzt für sie `qty = 0`,
wodurch sie in die vorhandene Darstellung für mengenlose Zutaten fallen — nur der Name,
dahinter `×N` für „in N Meals der Woche". Das gilt dadurch in einem Zug für Modal,
Text-Export und PDF.

Beides hängt an **einem** Begriff, `ingIsSeasoning()`. Zwei getrennte Schwellen für dieselbe
Frage würden auseinanderlaufen, sobald eine davon angefasst wird.

#### Mengen: Brüche bei Löffelmengen

`qtyLabel()` schreibt Löffelmengen als Bruch — **½ TL**, nicht `0,5 TL`. So dosiert man in
der Küche; die Dezimalform liest sich wie ein Messprotokoll und stand außerdem im
Widerspruch zur Zubereitung, die „1/2 TL" sagt.

**Nur ¼ ½ ¾, und das ist keine Bequemlichkeit:** Diese drei stehen in WinAnsi und überleben
damit den PDF-Export der Einkaufsliste (`WINANSI` in `lib/pdf.js`). ⅓ und ⅔ tun das nicht —
`pdfEsc()` ersetzt sie stumm durch `?`. Wer ein weiteres Bruchzeichen ergänzt, trägt es
**dort ebenfalls** nach; `tools/pruefstand-mengenanzeige.py` fängt das Vergessen ab.

Eine krumme Menge (0,3 TL) bleibt dezimal — ein Bruch wäre dort schlicht falsch. Gramm,
Milliliter und Stück bleiben unverändert.

### Abschnittsüberschriften: `.sec-h`

**Es gibt genau eine Abschnittsform in der App.** Sie steht als Klasse `.sec-h` an einer Stelle:

```text
12.5px · 700 · letter-spacing .05em · uppercase · --text-muted
```

Ein neuer Abschnitt bekommt `.sec-h`, keine eigenen Werte. Ort-abhängig bleibt nur der Abstand
(`margin`), nie die Schrift.

Sie war vorher dreimal wortwörtlich kopiert (`.ms-ings h4`, `.nut-total > h4`,
`.detail .dsec h4`) — der Kommentar an einer der Stellen sagte sogar ausdrücklich, es solle
dieselbe Form sein. Genau so entstehen Abweichungen.

`font-weight` gehört in die Klasse, nicht in die Aufrufer: Die Altstellen sind `<h4>` und tragen
die 700 des Browsers, die Slot-Überschrift des Wochenplans ist ein `<div>` und läge sonst bei 400.

Bewusst **nicht** angeglichen und kein Versehen:

* `.shop-cat` (Einkaufsliste) — eigene Display-Schrift, `.06em`
* `.modal-head .kicker` — 11,5 px

Wer sie „aufräumt", verändert bestehende Ansichten sichtbar.

### Markencharakter

Die UI soll sportlich und leistungsorientiert wirken.

Slogan:

**Plan it. Cook it. Lift it.**

Logo:

* rund
* roter Kreis

Wenn eine Designentscheidung nicht durch bestehende Tokens abgedeckt ist:

1. vorhandene Tokens prüfen
2. wenn nötig neuen Token im bestehenden Stil anlegen
3. nicht daneben einen eigenen Stil bauen

---

## Design-Skills

**Bei jeder Design-Änderung müssen alle drei Design-Skills vorab berücksichtigt werden.**

Reihenfolge:

#### ui-ux-pro-max

Für:

* UI-Zustände
* UX
* A11y
* Farben
* Branding
* Logo
* Banner

Verwenden:

`ui-ux-pro-max:ui-ux-pro-max`

und bei Branding:

`ui-ux-pro-max:design`

#### apple-design

Für:

* fluide Interaktion
* Motion
* Springs
* Materialien
* Wayfinding
* Agency

#### emil-design-eng

Für:

* Detailpolitur
* Animationsentscheidungen
* frequenzbasierte Animationen
* Press-States

### Wichtig

Die Empfehlungen der Skills werden auf **Performance Dark** gemappt.

Nicht die Variablen, Farben, Kurven oder sonstigen Design-Systeme der Skills direkt übernehmen.

Bestehende Projekt-Tokens haben Vorrang.

Animations-Skills wie:

* `find-animation-opportunities`
* `improve-animations`

nur verwenden, wenn Bewegung tatsächlich Teil der Änderung ist.

---

## Mehrstufige Abläufe

**Jeder mehrstufige Ablauf verwendet die bestehende durchgängige Progress-Bar.**

Standard:

`.wg-progress-bar`

Darstellung:

* visueller Balken
* anteilige Füllung
* kurzer Text darunter
* Beispiel: `Schritt 3 von 4 · Training`

Die Progress-Bar ist **nicht anklickbar**.

Kein Sprung zu früheren Schritten durch Anklicken des Balkens.

Zurück geht ausschließlich über einen separaten:

`Zurück`

-Button.

Keine nummerierten Schritt-Kacheln oder alten Schritt-Buttons wieder einführen.

### `initCarousel()`

Wenn ein Ablauf auf `initCarousel()` basiert, kann die Funktion weiterhin eine feste Anzahl Kind-Elemente als internes Gerüst benötigen.

Diese Platzhalter nicht entfernen, nur weil sie nicht sichtbar sind.

Sie müssen aus Tastatur-/Screenreader-Fokus genommen werden:

```html
aria-hidden="true"
tabindex="-1"
```

Sichtbar ist ausschließlich die durchgängige Progress-Bar.

---

## Schiebe-Schema für Ansichtswechsel

**Jeder Wechsel zwischen gleichrangigen Ansichten folgt dem Schema der mobilen Tagesleiste** (`.daybar`/`.db-ind`, `initCarousel()`):

* Segmented Control mit gleitender Pille statt harter Umschaltung.
* gerichtete Enter-Bewegung beim Inhaltswechsel.
* `MOTION`-Tokens (`--dur-fast`/`--dur-base`/`--dur-slow`/`--ease-out`) als einzige Quelle für Dauer und Kurve.
* **Kurze Wege.** Eine Enter-Bewegung verschiebt ein Element um einige Dutzend Pixel und blendet es dabei ein — sie schiebt es nicht über den halben Bildschirm. Lange Transform-Strecken zwingen den Browser, in jedem Bild die ganze Fläche neu zu rastern; auf dem Handy fallen dabei Bilder aus (siehe `docs/TROUBLESHOOTING.md`). Wer doch eine große Fläche bewegt, setzt `will-change` und stellt innere Scroll-Container für die Dauer der Bewegung ruhig.
* `reducedMotion()` immer berücksichtigt — Überblendung bleibt, Richtung entfällt.

Wischen (echtes `scroll-snap`) nur dort, wo es keinen verschachtelten horizontalen Scroller erzeugt. Bei Woche und Tabs bewusst kein Wischen: alle Ansichten gleichzeitig im DOM würde einen horizontalen Scroller im horizontalen Scroller ergeben, auf Touch gewinnt immer der innere, und `overscroll-behavior-x: contain` unterbindet die Weitergabe zusätzlich absichtlich. Bei den Tabs käme auf iOS die Zurück-Wischgeste am linken Rand dazu. Dort wird nur die Optik und Bewegungssprache angeglichen, nicht die Geste.

**Ein Scroller entsteht auch ungewollt.** `overflow-y: auto` allein macht ein Element **auf beiden Achsen** zum Scroll-Container — die Spezifikation rechnet die andere Achse von `visible` auf `auto` um. Genau so ist im Wochenplan-Sheet ein waagerechter Scroller in den Snap-Streifen geraten und hat das Wischen zwischen den Tagen vollständig ausgeschaltet; ausgelöst hat es die unsichtbar vergrößerte Trefferfläche eines Knopfes, die 6 px über den Rand ragte.

**Die Regel lautet deshalb: in einem Snap-Streifen keinen zweiten Scroll-Container anlegen.** Punkt. Der Wochenplan hat das zwei Runden lang mit `touch-action` und `overscroll-behavior` zu retten versucht — beides hat es **schlimmer** gemacht:

* `touch-action: pan-y` reicht die Geste nicht weiter, es **verbietet** sie. Der Browser bildet die Schnittmenge über die ganze Trefferkette; waagerechtes Panning war damit für alle Vorfahren aus.
* `overscroll-behavior: contain` unterbindet ausdrücklich das Chaining zum Elternteil.

Lässt sich ein innerer Scroller nicht vermeiden, ist das Einzige, was zählt: `getComputedStyle(el).overflowX/overflowY` und `scrollWidth === clientWidth` auf der Achse, die nicht scrollen soll. Nur `auto`/`scroll` fangen Gesten ab, `hidden` nicht. Und: **Wischgesten sind in diesem Projekt nicht automatisiert prüfbar** (drei Anläufe, siehe `docs/TESTING.md`) — die Abnahme am Gerät ist der einzige Beweis.

Siehe `docs/TROUBLESHOOTING.md`, Punkt 58.

`initCarousel()` ist die gemeinsame Quelle für die scroll-gekoppelte Pille (`.db-ind`, in `.daybar` und `.wgbar`). `slideIn(el, dir)` ist der gemeinsame Enter-Helfer für gerichtete Inhaltswechsel (Wochenwechsel, Tab-Wechsel). `.week-switch` braucht eine eigene WAAPI-Pille (`syncWeekSwitchPill()`), weil ihr Markup bei jedem `render()` per `view.innerHTML` neu gebaut wird — eine CSS-`transition` würde dort nie greifen, siehe `docs/TROUBLESHOOTING.md`.

---

## Die ersten Schritte bewegen sich wie der Rest der App (seit 30.08.2026)

Der Wizard hatte seine eigene Bewegungssprache: eine hartkodierte Keyframe-Animation
(`onbin`, 260 ms, 10 px senkrecht), unabhängig von den `MOTION`-Tokens und ohne Richtung —
obwohl es „Zurück" gibt.

Seither gilt auch dort das Schiebe-Schema der App:

* **Wechsel**: `slideIn(el, dir)` — 16 px waagerecht, Richtung aus `onbGo(delta)`, Dauer und
  Kurve aus `MOTION`, unter `reducedMotion()` eine reine Überblendung.
* **Höhe**: eine CSS-Transition am `.onb-stage-wrap` (`var(--dur-base)`, `var(--ease-out)`),
  die unter „weniger Bewegung" von der globalen Regel abgeschaltet wird.
* **Was bleibt**: die gestaffelte Einblendung der Kacheln (`.onb-opt`, `.onb-bf-o`) und die
  rAF-Animation des Fortschrittsbalkens. Beide sind der Teil, der sich lebendig anfühlt.

**Die Regel, die dabei entstanden ist:** Eine Einblendung gehört zum *Wechsel*, nicht zu
jeder Änderung auf demselben Bildschirm. Wer eine Kachel antippt, hat den Bildschirm nicht
gewechselt — dort steht die Bühne still (`.onb-still`). Beim vierten Tipp auf denselben
Bildschirm ist dieselbe Animation, die beim ersten Mal lebendig wirkte, nur noch Unruhe.

## Der Fortschritt-Kalender: zwei Gitter, eine Karte (seit 30.08.2026)

Der Kalender hat zwei Ansichten in **einer** Karte — Monat (Standard) und Jahr. Warum
beide nebeneinander stehen und warum es weder rotes X noch Tages-Ampel gibt, steht in
`docs/PRODUCT.md`; hier stehen nur die Formregeln.

**Die Zeitraumwahl steht über den Karten, nicht in ihnen** (seit 03.09.2026). Ein Block
`.zeitraum` trägt den Umschalter `Monat | Jahr` und darunter **genau eine** Zeitraumzeile
`‹ September 2026 ›` bzw. `‹ 2026 ›`. Er regiert **beide** Karten darunter.

Der Umschalter ist ein eigenes Segment (`.kal-seg`, seit 03.09.2026), **nicht** die
`.week-switch`-Optik aus dem Wochenplan: Dort sitzen die Knöpfe an einer Karte und richten
sich nach ihrer Beschriftung, hier steht die Wahl frei über dem ganzen Reiter. Eine binäre
Wahl mit ungleich breiten Hälften ließe die längere wichtiger aussehen, als sie ist —
deshalb zwei **gleich breite** Hälften und eine gleitende Pille (`.kal-pill`) dazwischen.
Die Pille ist Dekoration: Sie liegt unter den Knöpfen, fängt keinen Klick ab, und bei
`prefers-reduced-motion` gleitet sie nicht. Der aktive Zustand hängt an `aria-selected`,
nicht an einer Klasse — dieselbe Quelle, die auch der Screenreader liest.

Vorher trug jede Karte ihre eigene Wahl — ein Umschalter im Kalenderkopf, eine
Jahresleiste in derselben Karte, eine zweite in der Gewichtskarte. Drei Bedienelemente
für eine Frage, und das mittlere wirkte auf beides, ohne dass man ihm das ansah.

`.zeitraum` teilt sich die **Maximalbreite 420 px** mit Gitter und Navigation darunter:
Steht die Wahl breiter als das, was sie bedient, liest sie sich als Seiten-Steuerung
statt als Karten-Steuerung. Wer eine der Breiten ändert, ändert alle.

**Der Zustand hängt nie an der Farbe allein.** Ein geplanter Tag trägt Fläche *und* Symbol
(Haken auf Akzentkreis), ein ungeplanter eine Kante (leerer Kreis), eine Woche ohne
aufgezeichnete Tage einen neutral gefüllten Kreis. Ein Tag ohne jede Aussage bleibt leer —
Zukunft und die Zeit vor der ersten Nutzung sehen absichtlich gleich aus.

**In der Jahresansicht trägt die Fläche allein.** Bei rund 24–31 px je Zelle passt kein
Symbol mehr neben die Zahl, deshalb steht der Zustand hinter ihr: gefüllt, umrandet oder
gar nichts. Die Füllung ist dort **kräftiger** als im großen Gitter (32 % statt 12 %) — ohne
den Haken daneben ist sie der einzige Träger, und 12 % auf einer 24-px-Zelle sind aus einem
halben Meter Abstand nicht mehr von „leer" zu unterscheiden.

**24 px sind die Untergrenze, und zwar an beiden Kanten** (seit 04.09.2026). Jede Zelle ist
ein Tastziel — sie nimmt Klick, Hover und Fokus an und schreibt ihren Wert in die
Tipp-Zeile —, und WCAG 2.5.8 verlangt dafür 24 × 24 px. Gemessen wurden vorher auf 768 px
Viewport 21,25 × 23 px. Die Breite hängt an der Spaltenbreite des Grids (`.kal-jahr`,
`minmax(min(200px, 100%), 1fr)`, vorher 155 px), die Höhe an einem eigenen `clamp(24px,
3vw, 30px)` — wer nur eine der beiden Stellen ändert, lässt die andere Kante still unter die
Grenze fallen. `tools/pruefstand-kalender-layout.py` misst deshalb beide.

Der Preis sind **drei** Monate je Reihe statt vier auf dem Rechner; der Deckel von 720 px
bleibt. Auf dem Handy ändert sich nichts — dort stand ohnehin ein Monat je Reihe (38,7 px
je Zelle bei 360 px), die Anhebung greift erst ab 768 px.

**Der Kartenfuß trägt die Kennzahlen des Zeitraums** (`.kal-foot`, seit 03.09.2026).
Drei Werte in einer Reihe, durch eine Trennlinie vom Gitter abgesetzt, in derselben
Maximalbreite: Im Ziel · Serie · Am Stück. Die Serie trägt die Flamme, die
Tagesserie ausdrücklich **nicht** — andere Einheit, andere Aussage (`docs/PRODUCT.md`).
Fehlt eine Zahl (keine Zieldaten, Serie unter zwei Tagen), entfällt die Spalte ganz
statt eine Null zu zeigen; fehlen alle, entfällt der Fuß.

**„Geplant" stand hier bis zum 04.09.2026 als vierte Kachel — und stand damit zweimal auf
dem Schirm.** Die Zeile über dem Gitter (`.kal-note`) sagt bereits „18 von 30 Tagen
geplant". Sie war zugleich der Grund, aus dem der Fuß missverständlich war: Neben ihr stand
„Im Ziel 12/18 Tage" mit einem **anderen** Bezug — zwei Brüche nebeneinander, beide auf
„Tage" endend, deren Nenner Verschiedenes zählen (die Tage des Zeitraums bzw. die geplanten
Tage in Wochen mit Ziel).

**Ein Bruch nennt seinen Bezug, wenn er nicht selbsterklärend ist.** „Im Ziel 12/18
geplanten" statt „12/18 Tage" — das Wort steht dort, wo der Leser die Frage stellt, und
nicht in einem Erklärsatz darunter (`CLAUDE.md` §6).

**Das Gewichtsdiagramm führt eine Linie, nicht drei.** Die diagonale Ziellinie
(`.wch-goal`) ist entfallen: Sie lief gestrichelt und gedämpft neben dem gleitenden
Vier-Wochen-Schnitt, der ebenfalls eine ruhige zweite Linie ist — auf 375 px nicht
auseinanderzuhalten. Das Ziel steht als Zahl im Fuß und als unterster Achsenwert. Die
Legende erscheint nur, wenn wirklich zwei Serien im Bild sind (ab vier Messungen).

**Der gewählte Monat wird hinterlegt, nicht herausgeschnitten** (`.wch-span`). Die Skala
bleibt das ganze Jahr — bei wöchentlichem Wiegen hat ein Monat vier Punkte, und eine auf
sie gezoomte Achse ließe jede Wasserschwankung wie einen Trend aussehen. Der Streifen ist
**neutral** eingefärbt (`--text` bei 7 %), nicht im Akzent: Er ist ein Hinweis auf den
Zeitraum, kein Wert, und im Akzent zöge er mehr Aufmerksamkeit als die Kurve davor.

**Wiegen ist ein Stepper** (`.wg-step`): zwei runde Knöpfe von 54 px um eine große,
antippbare Zahl. Die 46 px der Zahl liegen weit über den 16 px, unter denen iOS beim
Fokus zoomen würde. `touch-action: manipulation` verhindert den Doppeltipp-Zoom beim
schnellen Zählen. Darunter die Differenz zur letzten Messung, dann die Woche eingeklappt.

**Die Maßregel, an der das Layout hängt: `max-width: 420px`.** Die Höhe der Tageszelle ist
bei 56 px gedeckelt, die Breite folgt ohne Deckel der Karte — auf 1280 px standen die Tage
dadurch als 168 × 56 px flache Balken da, ein Balkendiagramm statt eines Kalenders. Gitter
(`.kal-grid.monat`), Navigation (`.kal-nav`) und Klartextzeile (`.kal-note.monat`) teilen
sich deshalb dieselbe Maximalbreite und dieselbe Zentrierung. **Wer eine davon ändert,
ändert alle drei** — sonst steht eine Zeile allein an der Kartenkante, während der Rest
mittig sitzt.

**Kein zweiter Scroll-Container**, auch hier nicht: sieben Spalten passen auf jeder Breite.
Gemessen, nicht gerechnet — `tools/pruefstand-kalender-layout.py` fährt beide Ansichten bei
360/390/768/1280 px in hell und dunkel.

**Der Text bleibt kurz.** Die sichtbare Zeile unter der Navigation sagt „18 von 31 Tagen
geplant" — den Monat nennt die Zeile darüber schon. Die `<caption>` für den Screenreader
trägt ihn trotzdem („August 2026: 18 von 31 Tagen geplant"): Sie steht allein, ohne die
Zeile darüber.
