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
--accent-solid
--accent-solid-strong

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

`--accent` · `--accent-strong` · `--accent-solid` · `--accent-solid-strong`

Rot ist der zentrale Akzent.

Light- und Dark-Werte immer berücksichtigen.

#### Die Regel für Rot hinter weißer Schrift

**Steht `--accent-contrast` (Weiß) auf einer roten Fläche, trägt die Fläche
`--accent-solid` bzw. das Verlaufspaar `--accent-solid` → `--accent-solid-strong`.
Niemals `--accent`/`--accent-strong`.**

Der Grund ist gemessen, nicht Geschmack. Im Dark-Theme ist das Akzentrot bewusst hell
(`#FF3040`), und Weiß darauf erreicht nur **3,65:1** — verlangt sind 4,5:1 für Text. Bei
`--accent-strong` (`#FF5A66`) sind es sogar nur 3,04:1. `--accent-solid` (`#E02234`)
erreicht 4,72:1.

Im **Light-Theme ändert die Regel nichts**: dort sind `--accent-solid` und `--accent`
derselbe Wert, `--accent-solid-strong` und `--accent-strong` ebenso. Die Umstellung ist
dort ein reiner Umbenennung ohne sichtbare Wirkung.

Im Dark-Theme sind beide Vollton-Token **derselbe Ton**. Das ist Absicht: Ein Verlauf
bräuchte zwei Enden über 4,5:1, und zwischen 4,72:1 und 4,52:1 liegt kein sichtbarer
Verlauf mehr. Lieber ehrlich Vollton als ein Verlaufsende, das durchfällt.

**Balken, Füllstände und Fortschrittsanzeigen behalten den hellen Verlauf** — sie tragen
keinen Text. Für grafische Elemente verlangt WCAG 3:1, und das erreicht auch das helle
Rot.

Am 10.09.2026 bei einer Geräteabnahme gefunden: Zehn Flächen trugen weiße Schrift auf dem
hellen Verlauf — Primärknopf, Profil-Avatar, aktiver Wochentag, aktive Umschalter, das
Kalender-Symbol und der Einkaufswagen. `--accent-solid` existierte zu diesem Zeitpunkt
bereits **mit genau dieser Begründung im Kommentar**, wurde aber an keiner einzigen Stelle
verwendet. Ein Token anzulegen genügt nicht.

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

`initCarousel()` ist die gemeinsame Quelle für die scroll-gekoppelte Pille (`.db-ind`, in `.daybar`; bis 05.09.2026 auch in `.wgbar` auf der Startseite). `slideIn(el, dir)` ist der gemeinsame Enter-Helfer für gerichtete Inhaltswechsel (Wochenwechsel, Tab-Wechsel). `.week-switch` braucht eine eigene WAAPI-Pille (`syncWeekSwitchPill()`), weil ihr Markup bei jedem `render()` per `view.innerHTML` neu gebaut wird — eine CSS-`transition` würde dort nie greifen, siehe `docs/TROUBLESHOOTING.md`.

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

## Der Startreiter passt auf einen Bildschirm (seit 05.09.2026)

> **Diese Zusage ist am 06.09.2026 verschärft worden: Der Reiter *füllt* den Bildschirm.**
> Der Abschnitt hier beschreibt den Weg dorthin und gilt weiter; was sich geändert hat,
> steht unten unter „Der Startreiter füllt den Bildschirm“.

**Home scrollt nicht.** Bei einem 1440 × 900 großen Fenster steht alles zwischen Kopf- und
Fußzeile: die Heute-Karte, die Wochenkarte und die Aktionszeile. Das ist eine Zusage an das
Layout, keine Beobachtung — wer dem Reiter etwas hinzufügt, nimmt dafür an anderer Stelle
etwas weg oder macht es kompakter.

Zwei Dinge haben den Platz geschaffen:

**Der Intro-Hero ist entfallen.** Er trug eine Wochenzeile, die Überschrift „Dein Plan. Dein
Fortschritt." und einen Beschreibungssatz — zusammen rund 150 px über der Falz, die bei jedem
Aufruf dasselbe sagten. Eine Ansage, die man beim zweiten Besuch nicht mehr liest, aber jedes
Mal wegscrollen muss. Erhalten geblieben ist seine einzige veränderliche Information, die
Wochenangabe: Sie steht als `.wg-week` weiterhin da — erst in der Kopfzeile der damaligen
Wochenkarte, vom 05. bis zum 06.09.2026 im Kartenfuß der zusammengelegten Karte, seither in
deren Kopfzeile, an den Zahlen, die sie datiert.

**Der Rest kommt aus totem Raum, nicht aus weggelassenen Aussagen.** Jede Zahl, jeder Balken
und jeder Knopf steht unverändert da. Verkleinert wurden der 80-px-Fuß von `<main>`, der
Abstand unter dem letzten Element und die Innenabstände der damals **zwei** Zielkarten
(`css/basis.css`, Block hinter `.week-nut`). Seit dem Umbau am selben Tag ist es **eine** Karte —
siehe den Abschnitt „Der Startreiter ist eine Karte“ weiter unten.

Drei Regeln dazu, die zusammengehören:

* Die Kompaktierung hängt an **`.week-nut`** und gilt erst ab **681 px**. Dieselben Bauteile
  (`.wg-h`, `.gm`, `.wg-macros`) stehen im Wochenplan in den Tageskarten — dort ist die Seite
  ohnehin lang, dort ändert sich nichts. Und unterhalb von 681 px braucht die klebende
  Tagesbilanz den Fuß von `<main>` weiterhin.
* Der Fußabstand hängt an **`main:has(.week-nut)`**, nicht an einer Klasse aus dem JS. Fällt
  `:has()` aus, bleibt schlicht der alte Abstand stehen: Der Reiter scrollt dann wieder ein
  Stück, nichts bricht.
* **Auf dem Handy gilt dieselbe Zusage** (05.09.2026, zweiter Schritt). Damals lagen die beiden
  Zielkarten dort im Wisch-Streifen (`.wg-cols`) — eine Karte auf einmal, die Höhe kam von
  `initCarousel()`; **beides ist mit dem dritten Schritt desselben Tages entfallen.** Schmal
  stapeln sich Ring, Kennzahlen **und** die drei Makrobalken untereinander statt nebeneinander;
  damit fehlten nach dem Desktop-Schritt noch rund 100 px auf einem iPhone 14. Woher sie kamen,
  steht unten.

### Mobil: woher der Platz kam

**Der Fuß von `<main>` war doppelt vergeben.** `.app` hält bereits 77 px für die feste
Tab-Kapsel frei; die 64 px in `main` reservieren die klebende Tagesbilanz `#day-bal` — die es
**nur im Wochenplan gibt**. Auf Home standen dadurch 141 px Leere unter dem letzten Knopf.
Gekürzt wird deshalb nur dort (`main:has(.week-nut)`), im Plan bleibt alles unverändert.

**Der Makrobalken steht auf zwei Zeilen statt auf drei.** Die Restzeile („99 g übrig“) rückt
neben den Wert, statt eine eigene dritte Zeile zu belegen: 51 px je Balken werden 29. Das ist
**keine vierte Darstellungsform** — es bleibt die Balkenform, es bleiben die ausgeschriebenen
Namen (`Kohlenhydrate`, nicht `KH`), es bleibt die Reihenfolge, es bleibt jede Zahl. Technisch
löst `display: contents` auf `.gm-r` die Zwischenverpackung auf; die Rasterplätze stehen
**explizit** da, weil die Auto-Platzierung den Balken sonst in Zeile 1, Spalte 3 setzt.

**Ring und Kennzahlen tauschen die Führung.** Die drei Kennzahlen neben dem Ring waren mit
150 px höher als der Ring selbst (118) und bestimmten damit die Höhe der ganzen Zeile. Enger
gesetzt geben sie die Führung an den Ring zurück — ab da kostet jede weitere Kürzung dort
nichts mehr. **Wer eines von beiden ändert, muss das andere mitdenken.**

**Ein zweiter Block hängt an der Höhe, nicht an der Breite:**
`@media (max-width: 680px) and (max-height: 620px)`. Ein iPhone SE hat rund 553 px CSS-Höhe,
gut 110 weniger als ein iPhone 14 — und ein breites, aber flaches Fenster (Querformat,
geteilter Bildschirm) hat dasselbe Problem. Dort weicht zuerst der Slogan, wie schon im
400-px-Block; die Marke selbst bleibt vollständig.

### Die eine dokumentierte Ausnahme — am 06.09.2026 entfallen

Hier stand, dass der Reiter auf einem iPhone SE rund 40 px über dem Bildschirm steht und das
als `OFFEN` geführt wird. **Das gilt nicht mehr: Gemessen sind es 0 px.**

Die Ausnahme war nie eine Eigenschaft des Geräts, sondern die Folge einer *festen* Höhe.
Seit der Reiter sich dem Fenster anpasst, statt eine Größe mitzubringen, passt er auch auf
553 px — ohne dass ein Tippziel unter 44 px gerutscht wäre. `SE_DECKEL` ist ersatzlos aus
dem Prüfstand entfernt; das Gerät steht dort jetzt auf `muss passen`.

### Die Zusage wird gemessen, nicht geglaubt

`tools/pruefstand-home-eine-seite.py` fährt die echte App in `<iframe>`s fester Größe — seit
dem 06.09.2026 **zehn** Geräte statt sechs — und prüft je Gerät: passt es ohne Scrollen,
scrollt nichts quer, ist `#view` gefüllt, stehen Ring, drei Makrobalken und Wochenangabe da,
ist kein Tippziel zu klein, **liegt die Knopfzeile frei vor der Kapsel, bleibt der Notausgang
offen und wird der Platz auch genutzt**. Mit `--gegenprobe`.

## Der Startreiter ist eine Karte (seit 05.09.2026)

**Ein Rahmen statt zweier.** Bilddeckel oben, darunter links die Kalorien und rechts die
Makros, darunter die Knopfzeile. Der Kartenfuß mit der Woche ist am 06.09.2026 wieder
entfallen (siehe unten). Vorher lagen hier zwei gleich große
Zielkarten in einem Wisch-Streifen (`.wgbar` + `.wg-cols`); beide sind entfallen, ebenso
`.wg-b`, `.wg-progress` und `.wg-open`. **`.wg-col` bleibt** — Gewichtskarte und Kalender im
Fortschritt-Reiter benutzen sie.

Die Zeile links/rechts baut unverändert `goalRingHtml()` aus `.wg-col-cal` und
`.wg-col-macros`. Deshalb ist der Umbau im Code klein geblieben.

### Der Bilddeckel

Die Abdunklung über dem Foto ist **bewusst nicht tokenisiert** und in beiden Themes gleich:
Sie stellt den Kontrast zum *Bild* her, nicht zum Hintergrund der Seite. Ein helles Token im
Light-Theme machte den weißen Text auf einem hellen Gericht unlesbar — dieselbe Überlegung wie
bei `.wg-c`, das seine Farbe auch nicht vom Ring bezieht.

`object-position: center 42%`: In den Meal-Fotos sitzt der Teller unterhalb der Bildmitte, bei
118 px Höhe zeigte `center` vor allem Tischplatte.

**Hover nur mit Zeigegerät** (`@media (hover: hover) and (pointer: fine)`) — auf Touch bleibt
der Zustand nach dem Tippen hängen, dieselbe Falle wie bei `.rcard`. Und der Deckel hat einen
**Press-State**: Er ist die größte antippbare Fläche des Reiters. Nicht stauchen wie einen Knopf
— ein Foto zu skalieren wirkt wackelig —, sondern kurz abdunkeln (`opacity: .86`).

Die Nährwerte im Deckel stehen in der **Kompaktform ohne „g“**, genau wie `macroLineHtml()` sie
überall schreibt. Auf dem Handy bleiben davon die Kalorien; KH/P/F weichen. **Sie ganz zu
streichen wäre falsch:** Die Balken darunter zeigen den *Tag*, der Deckel dieses *eine Gericht*.
Zwei verschiedene Zahlen — die eine ersetzt die andere nicht.

### Der Kartenfuß ist wieder entfallen (06.09.2026)

**Er trug drei Aussagen gleichzeitig** — Zeitraum, welche Tage offen sind, Wochenbilanz in
Kalorien — und war damit der überladenste Teil eines Reiters, der zeigen und nicht reden soll.
Entfallen sind `weekFootHtml()`, die Tagesreihe (`.hm-days`, `.hm-day`) und die Zeile
„X von 7 Tagen · 12.600 / 19.158 kcal“ (`.hm-zahl`), dazu `.hm-foot` und `.hm-foot-h`.

**Die Wochen-Kalorienbilanz fällt aus demselben Grund wie zuvor der zweite Kalorienring:**
Entschieden wird auf Tagesebene. „12.600 von 19.158 kcal diese Woche“ ist keine Zahl, nach
der jemand handelt.

**„Welcher Tag ist noch offen?“ beantwortet der Fortschritt-Reiter besser.** Sein Monatsgitter
„Geplante Tage“ zeigt geplant/offen über Monate statt über sieben Punkte, und geplant wird
ohnehin im Wochenplan. Die Tagesreihe war der Versuch, dieselbe Frage ein zweites Mal zu
beantworten — nur kleiner.

**Die Wochenangabe ist nicht mit entfallen.** Sie steht jetzt rechts in der Kopfzeile der
Karte (`.wg-lbl`), links davon die Tagesangabe: zwei Zeitangaben in einer Zeile, getrennt
durch **Abstand** (`margin-left: auto`) — nicht durch ein Zeichen und nicht durch Farbe. Auf
schmalen Geräten bricht sie in eine eigene Zeile um und steht dort linksbündig.

⚠️ **Sie trägt `--text-muted`, nicht `--accent-strong`.** Bis zum 06.09.2026 stand sie in der
Akzentfarbe; der `ux-reviewer` hat das als überladen gemeldet, und der Vergleich im Browser
gab ihm recht: Zwei Zeitangaben, von denen eine in der Warn- und Akzentfarbe der App steht,
konkurrieren um die Aufmerksamkeit — und die wichtigere von beiden ist die linke.

**Verworfen wurde dabei die naheliegende Gegenmaßnahme**, sie in eine eigene kleinere Zeile
mit Trennlinie zu setzen (der Gegenvorschlag des Prüfers). Am Handy war das die ruhigste
Fassung, am Rechner läuft die Linie quer über die ganze Karte und liest sich wie ein
Abschnittstrenner, obwohl sie nur ein Datum abtrennt — und sie kostet rund 30 px, die dem
Bilddeckel abgehen. Drei Entwürfe standen dafür unter `plans/kopf-varianten/` zum Durchschalten
im Browser nebeneinander.

⚠️ **Keine `opacity` auf dieser Zeile.** Im Entwurf stand `.75`, und das war messbar falsch:
Der Kontrast fällt damit auf **3,18:1** im Light-Theme (Dark 4,25) — unter die 4,5:1, die
WCAG AA für Text unter 18,66 px fett verlangt. Ohne sie sind es 5,21:1 und 6,58:1. Eine
Deckkraft ist kein Gestaltungsmittel für Text, der schon in einer gedämpften Farbe steht. **Sie muss bleiben**, und zwar aus drei Gründen: Der Reiter zeigt je nach
`state.viewWeek` die laufende *oder* die nächste Woche; sie ist der einzige Aufrufer der
Zahl-Variante von `weekLabel()`, an dem `tools/pruefstand-wochenbeschriftung.py` seine
Gegenprobe abliest; und `tools/pruefstand-home-eine-seite.py` prüft `.wg-week` ausdrücklich.

⚠️ **Das Leerzeichen vor `<span class="wg-week">` ist Absicht.** Ohne es stoßen die beiden
Angaben im Textinhalt direkt aneinander, und eine Vorlesesoftware liest „SonntagWoche 37“.
Reiner Leerraum zwischen Flex-Elementen wird nicht gerendert — am Layout ändert er nichts.

**Auf flachen Geräten steht die Kopfzeile wieder da.** Sie war dort ausgeblendet, begründet
damit, dass der Wochentag „5 Zeilen tiefer im Kartenfuß“ hell umrandet stehe. Mit dem Fuß ist
diese Begründung entfallen — ohne die Zeile nennt der Reiter dort weder Tag noch Woche. Der
Platz kommt aus derselben Änderung: Der Fuß gab auf 390×556 gemessene 47 px frei, die Zeile
kostet 17.

### Mobil: eine Kante statt drei (06.09.2026)

**Beobachtung am Gerät:** Ring, Kennzahlen und beide Kopfzeilen klebten alle an der linken
Kante, rechts daneben stand ein leeres Drittel. Die Kennzahlenspalte war zwar breit
(`flex: 1`), ihr *Inhalt* aber kurz und linksbündig — „Grundbedarf" mit der Zahl darunter.

**Zentrieren wäre die naheliegende Antwort gewesen und die schlechtere.** Die Makrobalken
darunter laufen über die volle Breite; ein zentrierter Block darüber hätte zwei verschiedene
Kanten erzeugt — im Vergleich nebeneinander sofort sichtbar. Genauso eine zentrierte
Kopfzeile über linksbündigem Körper.

**Stattdessen sprechen die Kennzahlen jetzt dieselbe Sprache wie die Balken:** Name links,
Wert rechts, über die volle Breite (`.wg-stat` mit `justify-content: space-between`, der
Textblock von Spalte auf Zeile). Die rechte Kante läuft dadurch durch die ganze Karte —
`2.586` steht genau über `99 g übrig`. Nebenwirkung, die keine ist: einzeilig statt
zweizeilig spart zusätzlich Höhe.

**Nur mobil.** Am Rechner steht die Kennzahlenspalte *neben* dem Ring in einer Zeile, die
sie sich mit den Makros teilt — dort wäre dieselbe Regel eine zweite Kante mitten im
Kartenkörper.

**Die Wochenangabe steht mobil links**, nicht rechts. Sie bricht dort ohnehin in eine eigene
Zeile um, und `margin-left: auto` hätte sie als einziges Element dieser Zeile nach rechts
gezogen — eine dritte Kante, direkt unter einer linksbündigen.

### Der Ringinhalt muss in den Ring passen

Bei 80 px Ring bleiben innen 59 px nutzbar, bei 72 px noch 54 (`r=32` in einer viewBox von
78, abzüglich der Strichbreite). „Verbleibend" war mit 9,5 px und `.04em` Sperrung **58 px**
breit — auf 80er-Ringen bündig ohne Reserve, auf 72er 4 px zu breit, links wie rechts über
den Bogen hinaus.

⚠️ **Gemeldet wurde das als „der Text wandert bei vierstelligen Zahlen in den Ring“ — die
Zahl war es nicht.** `2.586` misst dort 40 px und hat 14 px Reserve. Es war immer das Wort,
auch bei dreistelligen Zahlen; der vierstellige Fall hat es nur auffällig gemacht, weil dann
oben und unten gleichzeitig eng aussieht. **Wer den gemeldeten Verdacht ungeprüft übernimmt,
vergrößert hier den Ring und behebt nichts.**

Jetzt 9 px ohne Sperrung: 51 px, also 8 px Reserve auf 80er- und 3 px auf 72er-Ringen.
Kleiner geht nicht — der Zustand *muss* als Wort dastehen, der Bogen sagt ihn nur zusätzlich
in Farbe. `tools/pruefstand-home-eine-seite.py` hält das seitdem nach.

### Trainingstag an der Karte

**Zwei Kennzeichen (Stand 06.09.2026).** Geblieben sind: der blaue Faden an der
Kartenkante (`.hm-card.is-train`, wie `.wg-col-training` im Wochenplan) und der Zuschlag in
der Kennzahlenliste. Das Badge `.wg-train` ist am selben Tag entfallen (unten), die
Wochentage im Kartenfuß (`.hm-day.is-train`) mit dem Fuß selbst.

**Das Badge `.wg-train` in der Kopfzeile ist entfallen** — mit seinem einzigen Aufrufer und
seinen CSS-Regeln. Es war der einzige der vier Kanäle, der **nichts Eigenes** beitrug: Die
Kennzahl sagt dasselbe und nennt zusätzlich den Wert. Dazu saß es am Ende einer reinen
Zeitangabe („Deine Ziele für Heute · Sonntag") und hatte dort keinen inhaltlichen Nachbarn —
ein blaues Wort allein am Zeilenende, während die Zahl, um die es geht, 170 px weiter unten
stand. Ursache und Wirkung waren getrennt.

**Die Kennzahl trägt die Aussage jetzt selbst:** An Trainingstagen färbt sich ihr Label
(`.wg-stat.train.is-on`) und die Zahl bekommt ein Vorzeichen — `+440` statt `440`. Das Plus
ist dabei kein Schmuck, sondern der zweite Kanal neben der Farbe (WCAG 1.4.1) **und** die
Antwort auf eine Frage, die vorher nirgends beantwortet war: was der Wert überhaupt tut. Er
erhöht das Budget; die Rechnung lautet Grundbedarf + Training − Ernährung = Ring.

An Ruhetagen bleibt die Zeile grau bei `0`. **Eine Null, die sich blau färbt, wäre eine
Auszeichnung für nichts.**

**Die Trainingsstufe lebt im `aria-label` weiter.** Das Badge trug sie im `title`
(„Trainingstag: moderat"); sichtbar steht jetzt nur die Zahl. Sie ersatzlos fallen zu lassen
hätte Screenreader-Nutzern etwas genommen, das Sehende dem gefärbten Label entnehmen — also
wandert sie als siebter Parameter von `goalRingHtml()` ins Label: „Trainingstag (moderat),
Zuschlag 440 kcal", an Ruhetagen „Kein Training heute". Dass die Variable `trLbl` nach dem
Entfernen des Badges verwaist dastand, war der Hinweis darauf — gefunden im `/pushcheck`.

Gemessen nach der Änderung: Auf **320 px Breite** steht `+440` vollständig und ohne Umbruch;
der Tint am Icon (`--train` zu 22 % in `--surface-2`) trägt in Light **und** Dark. 16 % waren
zu defensiv, um die Zeile auf hellem Grund erkennbar zu machen.

### Die Knopfzeile steht links

`.wg-actions` war jahrelang `justify-content: flex-end`, **ohne dass dafür ein Grund notiert
war**. Sie ist am 05.09.2026 nach links gerückt. Drei Gründe:

* Sie war das einzige Element des Reiters, das aus der linken Kante ausbrach — Ring,
  Überschriften und Wochenzeile stehen alle links. Der Blick liest die Karte von links nach
  unten und musste am Ende nach rechts springen.
* Rechtsbündig ist in diesem Projekt **Dialog-Grammatik** (`.modal-foot`, `.ing-done-row`):
  ein Knopf am Ende eines abgeschlossenen Vorgangs. Der Startreiter ist kein Dialog.
* Die nächstverwandte Leiste — die Werkzeugleiste des Wochenplans — steht ebenfalls links.

Auf dem Handy spielt es keine Rolle: Dort füllen die beiden Knöpfe die volle Breite
(`css/mobil.css`, `.wg-actions .wg-recalc`), je 44 px hoch.

### Die Zusage gilt weiter

Zum Stand 05.09.2026 maß der Prüfstand 0 px Überstand auf 390×664, 412×719, 430×745, 768×954
und 1440×790, auf dem iPhone SE dagegen 83 px (`SE_DECKEL = 90`). **Beides ist seit dem
06.09.2026 überholt** — der Deckel ist weg, der SE steht auf 0. Siehe unten.

## Der Startreiter füllt den Bildschirm (seit 06.09.2026)

**„Scrollt nicht“ und „passt“ sind nicht dasselbe.** Der Reiter hatte eine feste Höhe von
636 px. War das Fenster größer, blieb darunter Leere stehen — gemessen 114 px am Notebook,
351 px auf 1920×1080 —, weil `.site-foot` per `margin-top: auto` an den unteren Rand gedrückt
wurde. War es kleiner, stand er über. Zwei Symptome, eine Ursache: eine Höhe, die nicht zuhört.

### Warum es auf dem Handy trotz grünem Prüfstand scrollte

`100vh` ist auf iOS die Höhe **ohne** Browserleisten — die sieht man erst nach dem Scrollen.
Beim Aufruf sind rund 100 px weniger da. Der Prüfstand rechnete mit derselben falschen Zahl
und meldete deshalb grün, während das Gerät in der Hand scrollte. Beides steht jetzt auf
`100dvh`, und der Prüfstand führt jedes Handy **zweimal**: mit Adressleiste (svh) und ohne (lvh).

### Wie das Füllen gebaut ist

Die Kette `.app → main → .wrap → .week-nut → .hm-card` trägt durchgehend `flex: 1` und
`min-height: 0`; die Karte gibt den Rest an den Bilddeckel weiter. Vier Punkte, die dabei
nicht verhandelbar sind, jeder von ihnen mit einem Messwert bezahlt:

* **`.app` bekommt `height`, nicht `min-height`** — und nur auf diesem Reiter
  (`:has(.week-nut .hm-card)`). `flex: 1` verteilt nur *überschüssigen* Platz; ohne feste
  Höhe wächst der Container einfach mit und niemand wird zum Schrumpfen gezwungen. Ohne diese
  Zeile wurde die Karte sogar **höher** als vorher.
* **Der Deckel startet klein und wächst über `grow`**, `flex: 1 1 84px`. Eine mitwachsende
  `flex-basis` (`clamp(96px, 20dvh, 300px)`) stand hier zuerst und war ein Denkfehler: Die
  Basis geht in die `min-content`-Höhe der Karte ein, und unter die darf die Karte nicht.
  Auf 390×556 blieb der Deckel dadurch auf 111 px stehen, obwohl 72 gereicht hätten.
* **`.hm-body` ist `flex: none`.** Als schrumpfbares Item wurde es von `overflow: hidden`
  der Karte lautlos abgeschnitten — auf 390×556 fehlten der Fett-Balken und der Kartenfuß
  (den es inzwischen nicht mehr gibt). Nur der Deckel gibt nach.
* **`.wrap` braucht `width: 100%`** — der fünfte Punkt, nachgetragen am 06.09.2026. `.wrap`
  trägt `margin-inline: auto`, und ein Flex-Item mit einer Auto-Margin in der **Quer**achse
  wird nicht gestreckt: Die Margin frisst den freien Platz zuerst. Seit `main` `display: flex`
  trägt, war `#view` damit `fit-content` statt `max-width: 1120px`. Die Breite der Karte kam
  also vom längsten unumbrechbaren Text darin, und das war ausgerechnet die Zahlenzeile des
  Kartenfußes (`.hm-zahl`, `white-space: nowrap`) — gemessen **753 px statt 1080**. Beim
  Wegfall des Fußes wären daraus 541 px geworden, mit den Makros unter statt neben den
  Kalorien. **Eine Kartenbreite darf nicht am Wortlaut einer Fußzeile hängen.**
* **Der Notausgang ist `overflow-y: auto` auf `<main>`** — und er gehört genau dorthin.
  Zuerst stand ein `min-height: min-content` auf `.app` dafür da; es tat nichts, weil ein
  Glied mit `min-height: 0` **null** zum `min-content` seines Elternteils beiträgt. Die Zeile,
  die das Schrumpfen erlaubt, macht `min-content` damit wertlos.

### Der Abstand der Kapsel ist eine Untergrenze

`.app` hält unten Platz für die Tabbar frei. Die Kapsel schwebt gemessen **10 px** über dem
Rand — ein Freiraum von nur 6 px lässt die Knopfzeile also zwangsläufig darunter verschwinden,
und zwar auch dann noch, wenn man bis ans Ende gescrollt hat. Auf flachen Geräten stehen
deshalb `--tabbar-h + 12px`. **Dieser Wert ist kein Sparposten.**

### Was auf flachen Geräten weicht

Unter 620 px Höhe (`@media (max-width: 680px) and (max-height: 620px)`) fehlten 47 px. Sie
kommen aus Abständen, Ringgröße und Deckelhöhe — **ohne dass eine Aussage weicht**. Die 44 px
der Knopfzeile waren nie Teil der Rechnung.

**Die Kopfzeile war hier einmal ausgeblendet und ist am 06.09.2026 zurückgekehrt.** Begründet
war ihr Wegfall damit, dass der Wochentag „fünf Zeilen tiefer im Kartenfuß“ hell umrandet
stehe. Mit dem Kartenfuß ist diese Begründung entfallen: Ohne die Zeile nennt der Reiter auf
flachen Geräten weder den Tag noch die Woche. Der Platz kommt aus derselben Änderung — der
Fuß gab dort gemessene 47 px frei, die Zeile kostet 17. **Wer hier wieder kürzen muss, nimmt
es nicht von dieser Zeile:** Sie ist die einzige Zeitangabe des Reiters.

## Der Anfasser, der keinen Platz belegt (seit 11.09.2026)

Zutaten lassen sich sortieren. Der Anfasser dafür (`.ing-grip`, sechs Punkte) kostet im
Ruhezustand **keine Spalte**: Er liegt absolut im linken Rand, und die Zeile rückt nur dort ein,
wo dafür Platz ist.

| Umgebung | Was zu sehen ist |
|---|---|
| Rechner (`hover: hover`) | dauerhaft 22 px Einzug, der Anfasser erscheint beim Überfahren |
| Handy, Ruhezustand | kein Einzug, kein Anfasser — `opacity: 0`, `pointer-events: none` |
| Handy, während des Sortierens (`.ings-sorting`) | 22 px Einzug und Anfasser, mit Übergang |

**Der Grund ist die Zeile selbst.** Bei 360 px stehen Menge, Name, kcal und Makros schon gedrängt;
eine fünfte Spalte gibt es dort nicht. Deshalb sechs Punkte statt Striche (Striche lesen sich als
Menü), deshalb 44 px Tastfläche nur in der **senkrechten** Achse — waagerecht ist der Anfasser
nicht das einzige Ziel, auf dem Handy nimmt das Halten die ganze Zeile auf.

**Der Kontrast ist gemessen, nicht geschätzt** (11.09.2026, nach dem Befund vom 10.09.): Bei
`opacity: .8` auf `--surface` stehen die Punkte im Dark-Theme bei 4,88:1, im Light-Theme bei
3,88:1. Maßstab ist WCAG 1.4.11 für grafische Objekte, also 3:1 — beide bestehen. Wer die
Deckkraft oder `--text-muted` ändert, misst neu.

Die aufgenommene Zeile hebt sich über Fläche, Schatten und Rundung ab und verliert ihre
Trennlinie: Eine schwebende Karte hat keinen Nachbarn, von dem sie trennt. Sie folgt dem Finger
1:1 und bekommt deshalb **keine** Transition — die tragen nur die ausweichenden Nachbarn
(`.ing-row.shift`). `prefers-reduced-motion` schaltet beide ab; das Zurückfedern beim Loslassen
läuft über `MOTION`.

## Die Schnellauswahl bekommt Symbole (seit 11.09.2026)

Bis dahin trug jeder Eintrag im Schnellbereich des Pickers **dasselbe** Fruchtsymbol — auch das
Brötchen und das Ei. Jetzt gibt es vier Gruppen, alle aus dem vorhandenen Strich-Icon-Satz:

| Gruppe | Symbol |
|---|---|
| Obst aus der Hand | `fruit` |
| rohes Gemüse | `salad` |
| Backware vom Bäcker | `bread` |
| Süßgebäck (Berliner, Donut, Muffin) | `cake` |
| Ei | `egg`, **neu** |

**Das Ei-Symbol ist der einzige Neuzugang** — acht Strich-Icons gab es, keines passte. Es wurde
zweimal gezeichnet: Die erste Fassung war ein gleichmäßiges Oval und las sich bei 19 px wie der
Buchstabe O. Die zweite hat unten einen echten Kreisbogen und oben eine schlanke Spitze; erst
dadurch ist sie neben dem Brot eindeutig. Geprüft wurde am Gerät in der echten Liste, nicht in
einer Icon-Galerie — dieselbe Regel, die schon am Trinkglas steht: **wer einen Pfad ändert, sieht
ihn sich in seiner echten Größe neben einem Nachbarsymbol an, nicht bei 64 px.**

Die Zuordnung steht als Liste von Namen in `FOOD_ICON` (`data/ikonen.js`), nicht als
Stichwortregel. Bei 36 Einträgen ist die Liste überschaubar, und eine Stichwortregel liefe
genau in die Teilwort-Falle, die dieses Projekt schon kennt. Ein Eintrag ohne Zuordnung fällt auf
`fruit` zurück — also auf den Zustand von vorher — und `tools/pruefstand-stueckliste.py` sagt,
welcher das ist.
