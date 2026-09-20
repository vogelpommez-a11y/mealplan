# UI-Bausteine — wer lebt wo, und woher stammt er

Das Register zu `CLAUDE.md` Abschnitt 21a. Es beantwortet drei Fragen:

1. **Gibt es das schon?** — damit niemand einen fünften Dropdown danebenbaut.
2. **Wo überall wird es verwendet?** — damit eine Verbesserung *alle* Stellen erreicht.
3. **Woher stammt die Lösung?** — damit später niemand dieselbe Recherche zweimal macht.

`python tools/bausteine.py` liest die Spalte **Fundstellen** und meldet, wenn eine Stelle
nicht auf den gemeinsamen Helfer umgestellt ist.

> **Ein Baustein ohne Zeile hier ist kein Baustein, sondern ein Einzelstück.** Genau daraus
> sind die vier Dropdowns entstanden.

**Herkunft** ist eines von dreien: `eigen` · `nachgebaut nach <Quelle>` · `neu, weil <Grund>`.

---

## 1. Vereinheitlicht — ein Helfer, alle Stellen

| Baustein | Helfer | Fundstellen | Herkunft | Geprüft von |
|---|---|---|---|---|
| **Modal / Dialog** | `openModal(node, opts)` | 27 Aufrufe + Definition | eigen | `a11y-pruefung.py` |
| **Bestätigungsdialog** | `confirmModal(o)` | 13 Aufrufe | eigen — ersetzte ausdrücklich fünf fast gleiche Modal-Blöcke | `a11y-pruefung.py` |
| **Meal-Blatt / Sheet** | `openMealSheet(id, …)` | ~25 Stellen | eigen | `abnahme-mobil.py` |
| **Toast** | `toast(msg)` · `undoToast(msg, fn)` | ~130 Aufrufe, **ein** `#toast`-Element | eigen — die Undo-Variante teilt bewusst dieselbe Basis, sonst entwickeln sich zwei Toasts auseinander | — |

**Diese vier sind das Vorbild, nicht die Baustelle.** Wer hier etwas ändert, ändert es für
alle — genau so soll es sein.

---

## 2. In Arbeit — noch mehrfach getrennt gebaut

Stand der Erhebung: 20.09.2026. Reihenfolge und Begründungen in `plans/UI-Grundlagen.MD`.

| Baustein | Heute | Ziel | Herkunft geplant |
|---|---|---|---|
| **Dropdown / Überlaufmenü** | **4 Funktionen**: `togglePlanMenu` (`index.html:11405`), `toggleProfileMenu` (`:11428`), `toggleWeightMenu` (`:11462`), `openAssignMenu` (`:11497`). Geteilt sind nur `.menu` und `attachMenuDismiss()` (`:11370`) | ein `openMenu(items, trigger)` | nachgebaut nach WAI-ARIA Menu Pattern + Radix/Base UI (Tastaturverhalten) |
| **Leere Zustände** | **10 Stellen mit 5 Klassennamen** (`.empty` 1×, `.wch-empty` 1×, `.ms-empty-ings` 4×, `.wl-empty` 1×, `.pempty` 3×), dazu **2 klassenlose `<p>`** | ein `leerZustand({icon, titel, text, aktion})` | eigen — muss zur Markenstimme passen |
| **Akkordeon** | **2 Mechanismen**: 6× natives `<details>`, 6× `data-action="toggle-*"` | eine Bauart, begründet in `docs/DESIGN.md` | offen — Entscheidung steht aus |
| **Tabs / Segmente** | **3 Muster**: `.tabs` (Hauptreiter), `.daybar` (Tagesleiste), `.kal-seg` (Zeitraum) | gemeinsamer Bauplan | eigen — die gleitende Pille ist bereits etabliert |
| **Button-Varianten** | Solide Basis `.btn`, aber Kontext und Variante vermischt (`onb-skip`, `wg-recalc`, `ms-ing-add`, `shop-ic`, `plan-auto`) | Kontext von Variante trennen | eigen |

---

## 3. Fehlt ganz

| Baustein | Stand | Anmerkung |
|---|---|---|
| **Ladezustände / Skeleton** | existiert **nirgends** im Projekt | Inhalte erscheinen schlagartig; beim Cloud-Sync gibt es nur hinterher einen Toast |
| **Tooltip / Popover** | nur native `title=`-Attribute | Auf Touch-Geräten praktisch unsichtbar |

Beides ist **neues Verhalten**, kein Aufräumen — und sinnvoll erst, wenn Abschnitt 2
abgearbeitet ist.

---

## 4. Bewusst kein eigener Baustein

Damit niemand sie „nachrüstet":

| Sache | Warum nicht |
|---|---|
| **Gleitende Pille in der Haupt-Reiterleiste** | Ein Reiterwechsel passiert dutzendfach am Tag. Auch Instagram und iOS animieren dort nur den Zustand, nicht die Bewegung. Ausführlich in `docs/DESIGN.md` |
| **Eigenes `confirm()`** | `confirmModal()` deckt das ab, natives `confirm()` blockiert und lässt sich nicht gestalten |
| **CSS Anchor Positioning** für Menüs | Chrome/Edge produktiv, Safari erst teilweise, Firefox hinter Flag. Die App muss in einen iOS-WebView — Position wird in JavaScript berechnet |
