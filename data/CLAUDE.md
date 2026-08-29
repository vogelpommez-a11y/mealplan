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
