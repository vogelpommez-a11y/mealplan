---
name: rezeptcharge
description: Führt eine neue Charge Rezepte für das Rezeptbuch (COOKBOOK) von der Idee bis zur geprüften Datei. Verankert jedes Gericht in mehreren echten Quellen, statt ein plausibles zu erfinden — dazu Nährwerte gegenrechnen, Schritt-für-Schritt-Anleitung nach festem Standard, Tags, Bilder, Prüfstände. Verwenden, wenn Rezepte in data/cookbook.js angelegt oder überarbeitet werden.
---

# Rezeptcharge

Der Katalog ist das Erste, was ein neuer Nutzer sieht — vor dem ersten eigenen Meal, vor dem
ersten Wochenplan. Ein Rezept, das man nicht nachkochen kann, ist dort teurer als anderswo.

## Was schon einmal schiefging

Am 29.08.2026 wurden **Protein-Pancakes mit Skyr und Beeren** gekocht. Die Zutatenliste
führt `"Backpulver, Vanille, Prise Salz"` — die Zubereitung erwähnte nur das Backpulver.
Vanille und Salz blieben in der Schublade, weil die Anleitung sie nie erwähnt.

Eine Sondierung fand denselben Fehler in 18 von 34 Rezepten. Keine Prüfung hatte je danach
gesehen; es gab weder ein Verfahren noch einen Prüfer für den Katalog.

**Die Lehre:** Der Fehler entstand nicht beim Rechnen, sondern beim Schreiben. Deshalb liegt
ein Schwerpunkt dieses Skills auf Schritt 4 — und deshalb wird die Anleitung **Zutat für
Zutat gegen die Liste gelesen**, bevor irgendetwas anderes passiert.

## Und was beim ersten Rezept nach diesem Skill schiefging

Am selben Tag entstand die **Protein-Pizza mit Quarkboden** — formal tadellos: Nährwerte auf
die Kalorie gegengerechnet, jede Zutat in der Anleitung, Tag und Badge in Deckung, alle
Prüfstände grün.

Der Teig war trotzdem falsch. Zwei Quellen hatten Quark zu Mehl bei etwa **1 : 1,4** ergeben.
Im Rezept stand am Ende **200 g Quark zu 70 g Mehl** — also 2,9 : 1, fast doppelt so nass wie
die nasseste Quelle, dazu ohne Öl.

**Warum:** Um bei rund 640 kcal zu landen, wurde am Mehl gespart. Nicht in einem Schritt,
sondern beim Rechnen — und die vorher recherchierte Technik wurde dabei stillschweigend
verlassen.

Eine spätere Recherche über **sieben** Quellen zeigte das Ausmaß: Es gibt zwei getrennte
Familien — einen **Rollteig** (Quark:Mehl 0,36–1,4, ohne Ei, wird ausgerollt) und einen
**Gießteig** (4,5–7,7, mit Eiern, wird aufs Blech gestrichen). Der Wert 2,9 liegt in der
**Lücke dazwischen**: zu nass zum Ausrollen, zu wenig gebunden zum Gießen. Und Schritt 4 der
Anleitung sagte „ausrollen" — die Technik widersprach der eigenen Mengenangabe.

**Drei Lehren, die zu Schritt 2 wurden:**

* Zwei Quellen zeigen einen Mittelwert, sieben zeigen eine **Struktur**. Die Familien waren
  mit zwei Quellen nicht zu sehen.
* Ein Mittelwert über Familien hinweg ergibt ein Gericht, das es **nicht gibt**.
* **Kein einziger Prüfstand hat etwas gemerkt** — und keiner hätte es können. Formale
  Prüfung und kulinarische Richtigkeit sind zwei verschiedene Dinge.

Das Rezept wurde deshalb **wieder aus dem Katalog entfernt**, statt es zu flicken. An
seine Stelle trat die *Protein-Pizza mit Schinken*: dieselbe Idee, aber im Korridor der
Gießteig-Familie (Quark zu Mehl 4,55) und mit „verstreichen“ statt „ausrollen“.
**Ein Rezept, das in keiner belegten Familie steht, wird entfernt, nicht repariert** —
eine Reparatur am Einzelfall lässt die Regel weich aussehen.

## Und der dritte Fall: eine Zutat ohne Menge

Am 29.08.2026 fiel beim Durchsehen der **Protein-Pizza mit Schinken** auf, dass die
Zutatenliste `"Backpulver, Salz"` und `"Oregano"` führt — **ohne jede Menge**. Wer danach
kocht, rät. Ein Teelöffel Backpulver oder drei ist bei einem Quarkboden kein Detail.

Der Katalog trug diese Form 32-mal: Gewürze standen als Freitext-Sammelstring in der
Zutatenliste, ohne Menge, ohne Einheit, ohne Nährwert.

**Das hing an drei Stellen gleichzeitig schief:**

* **Die Anleitung war unvollständig.** Die Prüfung „jede Zutat kommt vor" war erfüllt; die
  Frage „wie viel davon" hat nie jemand gestellt.
* **Die Einkaufsliste war falsch.** `shoppingData()` schlüsselt mengenlose Zutaten über
  ihren ganzen Text — aus `"Kurkuma, Kreuzkümmel, Salz"` wurde **eine** Zeile mit genau
  diesem Wortlaut, und die ließ sich mit `"Kurkuma, Salz, Pfeffer, Schnittlauch"` aus einem
  anderen Rezept nicht zusammenlegen. Wer beides plante, kaufte Kurkuma zweimal.
* **Die Nährwerte rechneten daran vorbei.** `rezept-makros.py` überspringt Nicht-Objekte
  kommentarlos („Freitext trägt nichts bei"). Bei Salz stimmt das, bei 10 g Backkakao oder
  einem Esslöffel Sojasoße nicht.

**Die Regel, die daraus folgt:**

> **Es gibt keine Zutat ohne Menge.** Jeder Eintrag in `ingredients` ist ein Objekt mit
> `name` und `grams`. Freitext-Strings sind im Katalog nicht mehr zulässig.

---

## 1. Entwurf

Rezepte nach `data/cookbook.js`. Die Struktur:

```js
{ id: "rotes-linsen-dal", name: "Rotes Linsen-Dal mit Reis",
  category: "Hauptgericht", time: 25,
  tags: ["vegan","vegetarisch","glutenfrei","laktosefrei"], mealPrep: true,
  img: "rotes-linsen-dal.webp",
  nutrition: { kcal: 636, carbs: 95, protein: 25, fat: 13 },
  ingredients: [
    { name: "Rote Linsen, roh", grams: 120, kcal: 340, carbs: 50, protein: 24, fat: 1.5 },
    { name: "Kurkuma, gemahlen", grams: 1, unit: "tl", kcal: 9, carbs: 2, protein: 0.3, fat: 0.1 }
  ],
  steps: "1. …\n2. …" },
```

### Jede Zutat trägt eine Menge

**Ein Eintrag in `ingredients` ist immer ein Objekt.** Kein Freitext-String, keine
Sammelzeile wie `"Kurkuma, Kreuzkümmel, Salz"` — auch nicht für Salz, auch nicht für eine
Prise. `sanitizeIng()` lässt Strings weiterhin durch, weil fremde Daten aus Sync und Import
sie tragen können; **im Katalog haben sie nichts zu suchen.**

Die Einheit ist die, in der man das Zeug in der Küche dosiert:

| Zutat | Einheit | Beispiel |
|---|---|---|
| Getrocknete Gewürze, Backpulver, Vanilleextrakt | `tl`, `el` | `grams: 1, unit: "tl"` |
| Öl, Sojasoße, Zitronensaft, Brühe | `ml` | `grams: 10, unit: "ml"` |
| Frische Kräuter, Knoblauch, Ingwer, Kakao, Sesam | `g` | `grams: 5` |
| Ganze Stücke (Ei) | `st` | `grams: 2, unit: "st"` |

Die getrockneten Gewürze stehen in `FOODS` **je Teelöffel**, nicht je 100 g — `ingContrib()`
nimmt bei `st`/`el`/`tl` den Nährwert direkt je Einheit. Ein Stückgewicht tragen sie
bewusst **nicht**: Das hübe sie in den Schnelleintrag des Wochenplans (`pieceFoods`), und
„1 Stück Salz" ist dort Unsinn.

**Sammelbegriffe werden aufgelöst.** `"Kräuter"` ist keine Zutat — Rosmarin ist eine.
`"Süße nach Geschmack"` auch nicht: Entweder das Rezept braucht Honig, dann steht dort Honig
mit einer Menge, oder es braucht ihn nicht.

Vier weitere Dinge, die hier leicht übersehen werden:

* **`id` ist unveränderlich.** Sie landet beim Übernehmen als `lib` an der Nutzerkopie und
  verbindet sie mit dem Original. Auch bei einer Namensänderung bleibt sie stehen.
* **Zutatennamen müssen `FOODS` in `data/foods.js` treffen**, sonst kann Schritt 3 nichts
  rechnen.
* **Öl gehört als Zutat**, nicht in den Freitext — als Freitext fällt es aus jeder Rechnung,
  und 10 g Öl sind 90 kcal.
* **Zutaten stehen in der Reihenfolge ihrer Verwendung.** Wer die Liste liest, liest die
  Anleitung in Kurzform. Das ist die eine unumstößliche Regel des professionellen
  Rezeptlektorats — der Prüfstand kann sie nicht messen, also gilt sie hier.

Kategorien: `Frühstück`, `Hauptgericht`, `Beilage`, `Snack`, `Getränk`, `Dessert`.
Ein Shake gehört zu `Getränk`, nicht zu `Snack` — `Snack` ist über `CAT_TO_MEAL` fest an den
Slot `sn` gebunden und wäre sonst nirgends sonst planbar.

⚠️ **`data/cookbook.js` muss mit einem Zeilenumbruch enden.** Wer die Datei per Skript
schreibt, verliert ihn leicht. Die Folge sieht dann nach einem kaputten Prüfstand aus, nicht
nach einem kaputten Datenstand: `tools/quelle.py` klebt beim Zusammenbau `</script>` an die
letzte Zeile, die Ausschneide-Prüfstände ziehen es in ihren Code und beenden damit ihren
eigenen Script-Block. Ergebnis: „Kein ERGEBNIS", während `syntax-check.py` die Datei zu Recht
für sauber erklärt. `quelle.py` fängt das seit dem 29.08.2026 selbst ab
(`docs/TROUBLESHOOTING.md` §142) — sich darauf zu verlassen ist trotzdem unnötig.

## 2. Verankerung — das Rezept muss es wirklich geben

> **Am Ende dieses Schritts steht kein plausibles Rezept, sondern ein Gericht, das so schon
> gekocht worden ist.** Der Unterschied ist der ganze Punkt dieses Schritts.

Ein Sprachmodell erzeugt mühelos etwas, das *aussieht* wie ein Rezept: Die Zutaten passen
zueinander, die Schritte klingen richtig, die Nährwerte stimmen sogar. Ob ein Teig daraus
wird, steht in keiner dieser Prüfungen. Deshalb wird nicht erfunden, sondern **verankert**.

### 2a. Wann verankert wird

Nicht bei jedem Rezept — beim Beeren-Shake gäbe es nichts zu verankern. Verankert wird,
sobald **ein** Auslöser zutrifft:

1. **Der Garpunkt entscheidet über Sicherheit** — Geflügel, Hackfleisch, Schwein, Fisch,
   Meeresfrüchte, weiches Ei.
2. **Roh problematisch oder braucht Vorbehandlung** — Hülsenfrüchte (getrocknete
   Kidneybohnen sind roh giftig), Quinoa (Saponine abspülen), Tofu (pressen), Auberginen.
3. **Die Technik kann scheitern** — Teig, Hefe, Emulsion, Wenden, Stocken, Bindung,
   Karamell. Alles, wo „es klappt nicht" ein häufiges Ergebnis ist.
4. **Das Gericht hat eine kulturelle Referenz** — Dal, Curry, Bolognese, Shakshuka.
5. **Noch nie selbst gekocht.**

Trifft keiner zu — alles, was ohne Hitze zusammengerührt wird: Overnight Oats, Quarkspeisen,
Shakes, Salate, Dips — genügt die eigene Idee plus die Prüfung aus Schritt 4.

### 2b. Wie verankert wird — sechs Punkte

1. **Fünf bis sieben Quellen** sammeln. Auf **Unabhängigkeit** achten: Rezeptseiten schreiben
   voneinander ab, fünf Treffer können eine einzige Quelle sein. Gleiche Grammzahlen in
   gleicher Reihenfolge sind das Erkennungszeichen.
2. Nur die **strukturbestimmenden** Größen herausziehen — die, an denen das Gericht
   scheitert: Teig- und Bindungsverhältnisse, Flüssigkeit zu Mehl, Ei als Bindung, Gar- und
   Backtemperatur, Zeiten, Ruhezeiten. Beläge, Gemüse und Gewürze gehören **nicht** dazu.
3. **Nach Technik-Familien gruppieren, niemals mitteln.** Das ist der Punkt, an dem eine
   Recherche kippt (siehe „Was schon einmal schiefging"). Zwei Rezepte mit demselben Namen
   können völlig verschiedene Teige sein; der Mittelwert aus beiden ist keines von beiden.
4. **Eine Familie wählen** — die, die zum Ziel passt — und ihren **Korridor** notieren:
   kleinstes und größtes belegtes Verhältnis.
5. **Innerhalb des Korridors bleiben.** Kalorien werden über **Beläge und Beilagen**
   justiert, **nie über die strukturbestimmenden Mengen**. Wer am Teig spart, um ein
   Kalorienziel zu treffen, verlässt die Verankerung und hat wieder ein erfundenes Rezept.
6. **Jede Abweichung wird benannt** — im Bericht an den Nutzer, und wenn sie bewusst bleibt,
   als Kommentar am Katalogeintrag. Stillschweigend abweichen ist der Fehler, nicht das
   Abweichen selbst.

### 2c. Die Abbruchbedingung

**Findet sich keine Familie, in die das Gericht passt, wird es nicht gebaut.**

Nicht als abgespeckte Variante, nicht „nah dran". Dann ist die Idee entweder ungewöhnlich
genug, dass sie erst am Herd geprüft gehört — oder sie taugt nicht. Beides sagt man dem
Nutzer, statt ein Rezept zu liefern, das nur formal in Ordnung ist.

Dasselbe gilt, wenn die Zielvorgabe (Kalorien, Makros, ein Tag wie `lowcarb`) den Korridor
sprengt: Dann wird **die Zielvorgabe** angepasst oder das Gericht verworfen — nicht der Teig.

### 2d. Zwei Grenzen

* **Recherchiert wird die Technik, nie der Text.** Mengenangaben und Arbeitsschritte sind
  Tatsachen und nicht geschützt; der ausformulierte Text ist es. Lesen, verstehen, **neu
  formulieren** — nie übernehmen, auch nicht umgestellt. Ein Konsens aus mehreren Quellen ist
  dabei sicherer als eine eng gefolgte Einzelquelle, weil man niemandes Formulierung
  übernimmt.
* **Mindestens zwei unabhängige Quellen**, sobald es um Zeit, Temperatur oder Sicherheit
  geht. Ein falscher Garpunkt bei Geflügel ist kein Schönheitsfehler.

### 2e. Was im Bericht steht

Am Ende der Charge gehört je verankertem Rezept eine Zeile in den Bericht:

```
Protein-Pizza · Familie „Gießteig" · Korridor Quark:Mehl 4,5–7,7 (2 Quellen)
             · gewählt 4,0 — knapp unter dem Korridor, weil …
```

Ohne diese Zeile ist die Verankerung nicht nachvollziehbar, und niemand kann später prüfen,
worauf sich das Rezept stützt. **Ein Prüfstand kann das nicht abfangen** — es gibt im Repo
keine Wahrheit, gegen die er messen könnte. Diese Regel trägt sich allein dadurch, dass sie
befolgt wird.

## 3. Nährwerte — nie schätzen

```powershell
python tools/rezept-makros.py            # rechnet jede Zutat aus FOODS gegen die Summe
python tools/rezept-makros.py --anwenden # traegt die FOODS-Werte je Zutat ein
```

**Die Reihenfolge ist verbindlich, sonst schleicht sich eine Schätzung ein:**

1. Zutaten mit Mengen eintragen, `nutrition` mit einem **groben Platzhalter** füllen.
2. `rezept-makros.py` laufen lassen.
3. **Die gerechneten Werte übernehmen** — nicht den Platzhalter stehen lassen, auch nicht,
   wenn er „ungefähr passt".
4. Erneut laufen lassen. Erst wenn dort `OK` steht, ist der Schritt fertig.

Der Platzhalter ist nie das Ergebnis. Beim Testlauf am 29.08.2026 stand er bei
Protein 51 g, gerechnet waren es 58 — **16 % daneben**, und das Werkzeug hat es gemeldet.
Ohne Punkt 4 wäre die Schätzung im Katalog gelandet.

Toleranz sind 12 % — Garverluste, Öl in der Pfanne und Rundungen bewegen sich in dieser
Größenordnung. `PRUEFEN` heißt: nachrechnen, nicht die Toleranz dehnen.

Die Rechenregel der App: Einheit `g`/`ml` → Nährwert gilt je 100, Faktor `menge / 100`.
Einheit `st`/`el`/`tl` → Nährwert gilt je **Einheit**, Faktor `menge`.

Fehlt eine Zutat in `FOODS`, wird sie dort ergänzt — nicht das Rezept umgeschrieben.

⚠️ **Hier ist die gefährlichste Stelle der ganzen Charge.** Wenn die Summe nicht zum
Kalorienziel passt, ist die Versuchung groß, an einer Menge zu drehen, bis es passt. Erlaubt
ist das **nur bei Belägen, Beilagen und Fetten obenauf** — nie bei den strukturbestimmenden
Mengen aus Schritt 2. Wer den Teig verkleinert, um 640 kcal zu treffen, hat die Verankerung
verloren und wieder ein erfundenes Rezept. Genau so ist die Protein-Pizza entstanden.

Passt das Ziel nicht in den Korridor, wird **das Ziel** angepasst: höhere Kalorien, kleinere
Beilage, oder das Gericht wird verworfen (Schritt 2c).

## 4. Die Anleitung schreiben

> **Eine Zubereitung ist eine Anleitung für jemanden, der nicht kochen kann.**
> Nicht die Erinnerungsstütze für jemanden, der das Gericht schon kennt.

`steps` bleibt ein String; Schritte werden mit `\n` getrennt und nummeriert. Die Darstellung
trägt das bereits (`.detail .steps { white-space: pre-wrap }`) — es braucht keine
Code-Änderung.

1. **Nummerierte Schritte**: `"1. …\n2. …"`.
2. **Ein Schritt, eine Handlung.** Nicht drei Verben in einem Satz. Beginnt mit dem Verb im
   Imperativ: *Mahlen, Verrühren, Anschwitzen, Backen.*
3. **Jede Zutat kommt vor** — auch Gewürze, auch die Prise Salz. Ein Sammelwort darf sie
   decken („mit Kräutern würzen"), wenn es sie eindeutig meint.
4. **Kleine Mengen tragen ihre Menge im Schritt.** Alles, was in `tl` oder `el` gemessen
   wird, dazu Öl, Süße und Kakao: „1 TL Backpulver unterrühren", nicht „Backpulver
   unterrühren". Bei den großen Zutaten wird die Menge **nicht** wiederholt — die
   Zutatenliste steht in der App unmittelbar über der Anleitung, und „200 g Magerquark mit
   2 Eiern verrühren" liest sich wie ein Formular.
   Die Grenze ist kein Geschmack: Bei 200 g Quark sieht man im Topf, ob es passt; bei einem
   halben Teelöffel Salz sieht man gar nichts — und ein ganzer ist das Doppelte.
   **Geschrieben wird der Bruch, nicht die Dezimalzahl** — `½ TL`, `¼ TL`, `¾ TL`. Genau so
   setzt `qtyLabel()` die Menge in der Zutatenliste; zwei Schreibweisen für denselben Wert
   waren der Anlass für die Umstellung. **Nur diese drei Zeichen**: ⅓ und ⅔ überleben den
   PDF-Export der Einkaufsliste nicht (`docs/DESIGN.md`).
5. **Die Zutatenliste steht in der Reihenfolge ihrer Verwendung** (siehe Schritt 1).
6. **Garpunkt sinnlich**, nie „bis fertig": *bis die Sauce bindet*, *bis die Ränder stocken*,
   *bis die Linsen weich sind*.
   **Ausnahme bei Auslöser 1 (Sicherheit):** Dort ist ein Sinneseindruck zu wenig. Geflügel,
   Hackfleisch, Schwein und Fisch bekommen den **sicheren Garpunkt als Zahl** — Geflügel
   75 °C Kerntemperatur — **und** ein Zeichen, das ohne Thermometer funktioniert („kein
   rosa Fleisch mehr, der Saft tritt klar aus"). Beides, nicht eines von beiden: Die Zahl
   ist die Grenze, das Zeichen ist das, was die meisten tatsächlich benutzen.
7. **Zeiten als Von-bis**: „10–15 Min.", nicht „12 Min." — Herde sind verschieden.
8. **Geräte und Vorbereitung zuerst.** Ofen vorheizen, Blech auslegen, Mixer bereitstellen:
   das ist Schritt 1.
9. **Kein Vorwissen voraussetzen.** „Quinoa vor dem Kochen heiß abspülen" gehört hin, auch
   wenn es für Geübte selbstverständlich ist.
10. **Markenstimme** (`CLAUDE.md` §6): freundlich, knapp, nicht belehrend.
11. **Rezepte sind für eine Person gerechnet.** Keine Portionsangabe im Text — `portions`
    wird von `sanitizeRecipe()` ohnehin entfernt, und eine Angabe könnte den Makros
    widersprechen.

### Die Geruchsprobe

Der Text muss sich lesen wie ein Kochbuch, nicht wie ein Sprachmodell. Von einem Menschen
für einen Menschen, knapp und unaufgeregt. KI-Text verrät sich an wiederkehrenden Mustern:

**Verboten:**

* **Gleichförmigkeit.** Fünf Schritte, alle gleich lang, alle im selben Satzbau. Echte
  Anleitungen sind ungleich: „Ofen auf 200 °C vorheizen." neben einem Schritt über drei
  Zeilen.
* **Füllwörter am Schrittanfang** — *Zunächst, Anschließend, Nun, Danach, Im nächsten
  Schritt, Abschließend.* Die Nummer sagt bereits, dass es weitergeht.
* **Ein Erklärnachsatz an jedem Schritt** („— so bleibt es saftig", „dies sorgt für eine
  gleichmäßige Bräunung"). **Höchstens einer pro Rezept**, und nur dort, wo ohne ihn etwas
  schiefgeht.
* **Dreierketten** — „schneiden, würzen und anbraten", „cremig, saftig und aromatisch".
* **Werbende Adjektive** — *perfekt, herrlich, wunderbar, im Handumdrehen, goldbraun und
  knusprig.* Ein Zustand wird beschrieben, nicht gelobt.
* **Schlussformeln** — „Guten Appetit!", „Genieße dein Meal!". Das letzte Wort ist das
  Anrichten.
* **Emojis, Ausrufezeichen, Zwischenüberschriften** innerhalb der Schritte.
* **Zutaten neu bewerben** — nicht „das eiweißreiche Skyr", sondern „Skyr".

**Erwünscht:** unterschiedliche Schrittlängen, auch mal ein Vier-Wort-Schritt · Fachbegriffe
unaufgeregt und ohne Erklärung, wo sie eindeutig sind (*anschwitzen, ablöschen, stocken,
quellen, abschmecken*) · konkrete Zahlen statt Stimmung.

**Die Probe:** Den Text neben ein Rezept aus einem echten Kochbuch legen. Fällt sofort auf,
welches der beiden aus einer Maschine kommt, ist er nicht fertig.

### Beispiel

```js
// zu wenig - Zutaten fehlen, keine Schritte
steps: "Haferflocken fein mahlen, mit Eiklar, Ei und Backpulver zu einem dickflüssigen Teig
verrühren und 5 Min. quellen lassen. Bei mittlerer Hitze kleine Pancakes backen. Mit Skyr
und Beeren servieren."

// nach dem Standard
steps: "1. Haferflocken fein mahlen.\n2. Eiklar, Ei, 1 TL Backpulver, 1 TL Vanilleextrakt
und ½ TL Salz zugeben und zu einem dickflüssigen Teig verrühren.\n3. Teig 5 Min. quellen lassen.\n4. Pfanne
bei mittlerer Hitze erhitzen und kleine Pancakes 2–3 Min. je Seite backen, bis die Ränder
stocken – zu heiß und sie werden außen dunkel, bevor die Mitte fest ist.\n5. Mit Skyr und
Heidelbeeren anrichten."
```

**Zum Schluss dieses Schritts: die Zutatenliste von oben nach unten durchgehen und jede
Zutat in der Anleitung zeigen.** Nicht überfliegen — zeigen. Genau hier ist der Fehler
entstanden. Bei allem in `tl`/`el` und bei Öl, Süße und Kakao muss dabei **die Menge**
dastehen, nicht nur der Name.

## 5. Tags gegen die Badge-Schwellen

Tag und Badge müssen sich decken, sonst zeigt der Filter Karten, auf denen kein Badge steht.
Dieselben Schwellen, die `macroBadges()` rechnet — und zwar gegen die **Makro-Kalorien**
`macroKcal = KH × 4 + P × 4 + F × 9`, **nicht** gegen das angegebene `kcal`:

* `highprotein` — `P × 4 / macroKcal ≥ 0,30`
* `lowcarb` — `KH × 4 / macroKcal ≤ 0,15` **und** `KH ≤ 20 g`

Unter 100 Makro-Kalorien vergibt `macroBadges()` gar kein Badge — dort wäre jeder Anteil
Rauschen. Ein Getränk mit wenig Substanz bekommt deshalb kein `highprotein`, auch wenn die
Rechnung aufgeht.

**Wenn ein Rezept „Fettreich" erbt (Fettanteil ≥ 45 %), gehört das in den Bericht.** Das ist
kein Fehler — Shakshuka ist nun einmal fettreich —, aber es ist eine **Produktentscheidung**:
Die Karte trägt das Badge sichtbar, und Paddy's Mealplan richtet sich an Leute mit
Fitness- und Abnehmzielen. Nicht stillschweigend aufnehmen, sondern vorlegen.

Ernährungsform-Tags (`vegan`, `vegetarisch`, `glutenfrei`, `laktosefrei`) sind Wahrheit über
die Zutaten, keine Rechnung — aber `vegan` impliziert immer auch `vegetarisch`.

**Jedes dieser vier Tags wird Zutat für Zutat belegt**, nicht aus dem Gesamteindruck
vergeben. Die häufigen Fallen:

* **`laktosefrei`** — Quark, Skyr, Joghurt, Käse, Butter und Molke/Whey schließen es aus.
  Pflanzliche Varianten (Sojajoghurt, Hafermilch) nicht.
* **`glutenfrei`** — Weizen, Dinkel, Roggen, Gerste, Nudeln, Brot, Couscous, Bulgur. **Hafer
  ebenfalls**, solange nicht ausdrücklich glutenfreier Hafer gemeint ist.
* **`vegan`** — zusätzlich zu Fleisch und Fisch auch Ei, Honig und alle Milchprodukte.

Ein falsches Tag ist kein Schönheitsfehler: Der Katalog wird nach `state.goal.diet`
**gefiltert**, das Gericht wird also jemandem ausdrücklich als geeignet vorgeschlagen.

`tools/pruefstand-rezepttexte.py` prüft das seit dem 29.08.2026 mechanisch und **ohne
Grundlinie** — jeder Treffer ist ein Befund. Anlass war der zweite Testlauf dieses Skills:
Ein frisch gebautes Rezept trug `laktosefrei` und enthielt Magerquark, und alle damaligen
Prüfungen blieben grün.

## 6. Bilder

**`--nur-ohne-bild` allein genügt nicht** — es ist ein Filter, keine Quelle. Der empfohlene
Weg ist `--rezepte` mit einer JSON-Datei, denn nur dort kommen Zutaten, Kategorie und
Diät-Tags in den Prompt; über `--meals` geht allein der Name hinein.

```json
[{ "id": "rotes-linsen-dal", "name": "Rotes Linsen-Dal mit Reis",
   "kategorie": "Hauptgericht", "tags": ["vegan"],
   "zutaten": ["Rote Linsen", "Basmatireis", "Passierte Tomaten"] }]
```

```powershell
python tools/meal-bilder.py --rezepte charge.json --nur-ohne-bild --dry-run   # Prompts zeigen
python tools/meal-bilder.py --rezepte charge.json --nur-ohne-bild --out img/library
```

**Das kostet Geld** (OpenAI, zwei Varianten je Gericht). Vor dem echten Lauf beim Nutzer
rückfragen.

Der Stilblock im Werkzeug ist **eingefroren**. Wer ihn ändert, muss alle Bilder neu erzeugen
— sonst stehen zwei Bildsprachen nebeneinander, und das sieht man auf den ersten Blick.

### Danach: Variante wählen und aufräumen

Das Werkzeug schreibt `<id>-1.webp` und `<id>-2.webp`. **Beide ansehen** — das Werkzeug
verlangt die Sichtprüfung ausdrücklich, und der realistischste rechtliche Fallstrick ist Text
oder ein Logo im Bild, nicht das Motiv.

Dann die gewählte Variante auf `<id>.webp` umbenennen, die andere löschen **und den
Schlüssel in `img/library/bilder-protokoll.json` mitziehen** — das Protokoll ist nach dem
endgültigen Dateinamen geschlüsselt, verworfene Varianten stehen nicht darin.

**Kein Eintrag in `PHOTO_CREDITS`.** Die Rezeptbuch-Bilder sind über einen Sammelhinweis im
Impressum abgedeckt (`data/rechtstexte.js`, `IMPRESSUM_HTML_2`); der Nachweis je Bild steht
im Protokoll. Das Werkzeug schlägt am Ende trotzdem eine `PHOTO_CREDITS`-Zeile vor — das ist
ein Überbleibsel aus der Zeit vor dem Sammelhinweis. Nicht übernehmen, sonst steht ein
einzelnes Bild in der Tabelle und 35 andere nicht.

`img` trägt den **Dateinamen**, nicht die `id`: Eine `id` darf einen Umlaut haben
(`rührei-avocadobrot`), ein Dateiname nicht.

## 7. Kategorie-Tiefe prüfen

Der Katalog wird nach `state.goal.diet` gefiltert. Wer vegan wählt, darf nicht vor einer
halb leeren Ansicht stehen — und zwar in **jeder** Kategorie, nicht nur in der Summe.

Nach der Charge zählen: Wie viele Rezepte bleiben je Kategorie übrig für `vegan`,
`vegetarisch`, `glutenfrei`, `laktosefrei`?

## 8. Prüfen

```powershell
python syntax-check.py --alles
python tools/pruefstand-rezepttexte.py
python tools/pruefstand-rezeptbuch.py
python tools/pruefstand-rezeptbuch-filter.py
```

`pruefstand-rezepttexte.py` meldet die neuen Rezepte als **REGRESSION**, wenn eine Zutat in
der Anleitung fehlt oder die Nummerierung nicht steht. Der Bestand meldet sich als
**OFFEN** — das ist die Grundlinie vom 29.08.2026 und kein Befund dieser Charge.

Wird ein Bestandsrezept nebenbei korrigiert, meldet der Prüfstand **BEHOBEN**: dann die
Zeile aus `GRUNDLINIE` bzw. `UNNUMMERIERT_ALT` streichen.

## 9. Abschluss

Der Bericht an den Nutzer enthält je Rezept **eine Verankerungszeile** (Schritt 2e) und die
Angabe, **wo das Rezept im Korridor sitzt**. Ohne sie ist nicht nachvollziehbar, worauf es
sich stützt.

Danach auflisten, **welche Rezepte der Charge noch niemand gekocht hat.**

Der Pancake-Fehler ist nicht durch ein Skript aufgefallen, sondern am Herd. Keine Recherche
und kein Prüfstand meldet, dass eine Anleitung *als Anleitung* nicht trägt — das zeigt sich
erst in der Pfanne. Die Liste ist keine Formalie, sie ist der ehrliche Rest.

Danach das Dokumentations-Gate (`CLAUDE.md` §3): Betrifft die Charge eine Produktregel oder
eine Zahl in `docs/PRODUCT.md` — etwa „34 Rezepte" oder die Vegan-Quote — wird sie im selben
Arbeitsschritt nachgezogen.
