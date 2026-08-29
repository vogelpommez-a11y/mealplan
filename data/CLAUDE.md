# Regeln für `data/`

Ergänzt die Wurzel-`CLAUDE.md`. Hier steht nur, was **speziell für diesen Ordner** gilt.

---

## Die eine Regel, an der alles hängt

> **Hier stehen Daten. Keine Logik.**

Diese Dateien wurden ausgelagert, weil sie *nichts* aufrufen — kein `state`, kein
`render()`, kein `save()`, kein `toast()`. Genau das macht sie ohne Risiko verschiebbar
und für einen Menschen wie für Claude Code auffindbar. Sobald hier eine Funktion steht,
die in den App-Kern greift, ist der Schnitt hinfällig und der Ordner wieder ein Stück
`index.html` mit anderem Namen.

Sie werden als **klassische Skripte vor der App-IIFE** geladen; die Konstanten stehen
dadurch global und werden vom Kern gelesen. Deshalb gilt auch: **hier nichts umbenennen.**
Der Kern greift auf die Namen zu, ohne dass ein Import das sichtbar machen würde.

| Datei | Inhalt |
|---|---|
| `cookbook.js` | `COOKBOOK` — der Rezeptkatalog |
| `foods.js` | `FOODS` — Zutaten- und Nährwerttabelle |
| `bilder.js` | `PHOTO_CREDITS`, `PHOTOS`, `PHOTO_RULES`, `CAT_PHOTO` |
| `ikonen.js` | `ICONS`, `CAT_ICON`, `MEAL_ICON`, `ACT_ICONS`, Einzel-Icons |
| `rechtstexte.js` | Impressum und Datenschutzerklärung als Markup |

**Die Namen sind global und damit reserviert.** Es gibt keinen Namensraum, der eine
Kollision abfangen wuerde: Eine zweite Deklaration desselben Namens ist ein `SyntaxError`
und beendet das gesamte App-Script - die Seite liefert weiter HTTP 200 und `#view` bleibt
leer. Vergeben sind heute:

```
COOKBOOK  FOODS  PHOTOS  PHOTO_CREDITS  PHOTO_RULES  CAT_PHOTO
ICONS  CAT_ICON  MEAL_ICON  ACT_ICONS  TOOL_ICONS
ICON_DUMBBELL  ICON_FLAG  ICON_PEOPLE
IMPRESSUM_HTML_1  IMPRESSUM_HTML_2  DATENSCHUTZ_HTML
```

Ein neuer Datensatz braucht einen neuen, eindeutigen Namen - die jeweils aktuelle Liste
steht erzeugt in `docs/MODULE.md` unter „Datenbereiche“.

---

## Marken nicht entfernen

```
/*FOODS_START*/  /*FOODS_END*/     tools/rezept-makros.py schneidet dazwischen
/*PHOTOS_END*/                     Ende der Foto-Zuordnung
/*CREDITS_START*/                  Beginn der Bildnachweise
```

Werkzeuge suchen danach. Verschwindet eine Marke, findet das Werkzeug nichts mehr — und
meldet in aller Regel nicht „kaputt", sondern „nichts gefunden".

---

## Zubereitung

> **Eine Zubereitung ist eine Anleitung für jemanden, der nicht kochen kann.**
> Nicht die Erinnerungsstütze für jemanden, der das Gericht schon kennt.

**Keine Zutat ohne Menge.** Jeder Eintrag in `ingredients` ist ein Objekt mit `name` und
`grams` — auch Salz, auch Backpulver, auch eine Prise. Freitext-Strings (`"Oregano, Salz,
Pfeffer"`) sind im Katalog nicht mehr zulässig: Sie tragen keine Menge, fallen aus
`rezept-makros.py` heraus („Freitext trägt nichts bei") und erzeugen in der Einkaufsliste
eine Zeile, die sich mit keiner anderen zusammenlegen lässt. Getrocknete Gewürze stehen in
`FOODS` je Teelöffel (`grams: 1, unit: "tl"`), frische Kräuter je 100 g. Sammelbegriffe
werden aufgelöst — „Kräuter" ist keine Zutat, Rosmarin ist eine.

`steps` ist ein String; Schritte werden mit `\n` getrennt und nummeriert. Die Darstellung
trägt das bereits (`.detail .steps { white-space: pre-wrap }`) — es braucht keine
Code-Änderung.

1. **Nummerierte Schritte**: `"1. …\n2. …"`.
2. **Ein Schritt, eine Handlung.** Beginnt mit dem Verb im Imperativ.
3. **Jede Zutat kommt vor** — auch Gewürze, auch „Prise Salz". Ein Sammelwort darf sie
   decken („mit Kräutern würzen"), wenn es sie eindeutig meint.
4. **Kleine Mengen tragen ihre Menge im Schritt** — alles in `tl`/`el`, dazu Öl, Süße und
   Kakao: „1 TL Backpulver unterrühren". Bei großen Zutaten wird die Menge nicht wiederholt.
   Als **Bruch**, wie `qtyLabel()` ihn setzt: `½ TL`, `¼ TL`, `¾ TL` — keine anderen Zeichen,
   ⅓ und ⅔ überstehen den PDF-Export nicht.
5. **Die Zutatenliste steht in der Reihenfolge ihrer Verwendung.**
6. **Garpunkt sinnlich**, nie „bis fertig": *bis die Sauce bindet*, *bis die Ränder stocken*.
7. **Zeiten als Von-bis**: „10–15 Min." — Herde sind verschieden.
8. **Geräte und Vorbereitung zuerst.** Ofen vorheizen ist Schritt 1.
9. **Kein Vorwissen voraussetzen.**
10. **Markenstimme** (`CLAUDE.md` §6): freundlich, knapp, nicht belehrend.
11. **Rezepte sind für eine Person gerechnet.** Keine Portionsangabe im Text.
12. **Es klingt wie ein Kochbuch, nicht wie ein Sprachmodell.** Keine gleichlangen Schritte,
    keine Füllwörter am Schrittanfang (*Zunächst, Anschließend, Nun*), höchstens **ein**
    Erklärnachsatz pro Rezept, keine Dreierketten, keine werbenden Adjektive, keine
    Schlussformel. Der Text endet beim Anrichten.

Der Ablauf einer Charge steht im Skill **`/rezeptcharge`**, geprüft wird mit
`python tools/pruefstand-rezepttexte.py`. Regel 4 kann der Prüfstand **nicht** messen — sie
gilt trotzdem, siehe den Kopf des Skripts.

Anlass war ein Rezept, dessen Zutatenliste „Vanille, Prise Salz" führte, während die
Anleitung beides nie erwähnte: `docs/TROUBLESHOOTING.md` §141.

---

## Nährwerte

**Nie schätzen.** Vor jedem neuen Rezept gegenrechnen:

```powershell
python tools/rezept-makros.py
```

Das Werkzeug rechnet jede Zutat aus `FOODS` gegen die angegebene Summe und meldet alles
außerhalb der 12-%-Toleranz.

Bei Stichwort-Regeln in `bilder.js` auf **Teilwort-Kollisionen** achten: `eis` steckt in
`Rindfleisch`, `reis` in `Preiselbeere`.

---

## Bilder und Lizenzen

`PHOTOS` und `PHOTO_CREDITS` müssen **deckungsgleich** bleiben.

Neue Bilder nur mit belegter freier Lizenz: Lizenz prüfen, Quelle dokumentieren,
`PHOTO_CREDITS` mit Titel, Urheber, Lizenz und Fundstelle ergänzen. Ein Bild ohne
Lizenznachweis ist ein rechtliches Risiko — und die Nachweise werden im Impressum
tatsächlich angezeigt (`creditsHtml()` erzeugt sie aus `PHOTO_CREDITS`).

---

## Rechtstexte

`rechtstexte.js` ist kein gewöhnlicher UI-Text. Die Texte enthalten **konkrete technische
Zusagen** — eine Änderung am Verhalten der App kann sie inhaltlich falsch machen, ohne
dass jemand den Text angefasst hat.

* Jede Änderung hier braucht den Agenten `anwalt`; bei neuen Datenfeldern, Diensten,
  Sharing- oder Löschwegen zusätzlich `datenschutz-technik`.
* Der Text ist zweigeteilt, weil im Impressum der Bildnachweis eingesetzt wird:
  `IMPRESSUM_HTML_1 + creditsHtml() + IMPRESSUM_HTML_2`. Wer die Teile zusammenzieht,
  verliert die Nachweise.
* Der Footer muss **auch ohne Anmeldung** erreichbar bleiben — das Impressum darf nicht
  hinter das Auth-Gate.

Zuständige Prüfer laut `docs/ABDECKUNG.md`: `anwalt` (Rechtstexte, Bildlizenzen) und
`kvp` (Katalog, Nährwerte).
