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
| **Bestätigungsdialog** | `confirmModal(o)` | **11 Aufrufe** (21.09.2026: von 13) | eigen — ersetzte ausdrücklich fünf fast gleiche Modal-Blöcke | `a11y-pruefung.py`, `bausteine.py` |
| **Löschen mit Netz** | `undoToast(msg, fn, {ms})` | 8 Aufrufe | **eigen — und ausdrücklich die bessere Hälfte.** `deleteRecipe` und `clearWeek` fragten bis zum 21.09.2026 erst per Dialog **und** boten danach „Rückgängig“ an: zwei Sicherungen für denselben Fehler, von denen die erste jeden Nutzer jedes Mal einen Schritt kostete. Die Frage ist weg, das Netz blieb — bei `deleteRecipe` auf 10 s verlängert. Gegenmodell zu [Watermelons Inline-Bestätigung](https://ui.watermelon.sh/animated-components/inline-disclosure-menu), die dafür **zwei** Schritte braucht | `bausteine.py` |
| **Dropdown / Überlaufmenü** | `openMenu(wrap, trigger, eintraege)` | 3 Menüs (Plan, Profil, Gewicht). Das Chip-Menü `openAssignMenu` baut bewusst selbst — Mehrfachauswahl, Portal an `<body>`, eigene Positionsrechnung | nachgebaut nach WAI-ARIA Menu Pattern (Tastatur); Kollisionsvermeidung und Scroll-Schließen **aus dem eigenen Chip-Menü übernommen** | `bausteine.py`, `a11y-pruefung.py` |
| **Leere Zustände** | `leerZustand({icon, titel, text, aktion, klein})` | 11 Aufrufe. Zwei Größen: ganze Ansicht (`.empty`, im Dialog `.empty.im-dialog`) und eine Zeile im Inhalt (`.leer`) | **eigen — die Form stand schon im Rezeptbuch** (`.empty`), sie wurde nur auf die anderen zehn Stellen übertragen. Bestätigt durch [NN/g zu Empty States](https://www.nngroup.com/articles/empty-state-interface-design/): ohne nächste Aktion ist ein leerer Zustand eine Sackgasse | `bausteine.py`, `abnahme-mobil.py` |
| **Aufklapper** | `caretSvg()` für den Pfeil; **zwei** Mechanismen bleiben bewusst | 5× natives `<details>`, 5× `<button aria-expanded>` | **eigen.** Die Regel, wann welcher, steht in `docs/DESIGN.md` — sie zu vereinheitlichen wäre falsch: Der Picker baut bei jedem Tastendruck neu, ein `<details>`-Zustand ginge dabei verloren | `bausteine.py` |
| **Meal-Blatt / Sheet** | `openMealSheet(id, …)` | ~25 Stellen | eigen | `abnahme-mobil.py` |
| **Button-Varianten** | `.btn` + Varianten `primary` · `ghost` · `sm` · `danger` · `icon-gh` · `fav-ic` · **`link`** (neu) | 117 Markup-Stellen | **eigen.** Kontext und Variante sind jetzt getrennt: `onb-skip`, `onb-back`, `ing-done` tragen gar kein CSS (reine JS-Handles), `ms-ing-add`, `wg-recalc`, `shop-ic`, `plan-auto`, `auth-forgot`, `foot-link`, `toggle-all` setzen nur noch Ort und Breite. `.btn.del-ic` war tot und ist entfernt | `bausteine.py` |
| **Trefferflaeche (hitSlop)** | `.hit` / `.hit.rund`, zentrale Regel in `css/basis.css` | 9 Selektoren: `.btn.icon-gh`, `.btn.fav-ic`, `.foot-link`, `.ing-ic`, `.ing-view-del`, `.ing-barcode`, `.wch-add`, `.wch-more`, `.avatar-edit-btn` | **eigen.** Vorher stand an jeder Stelle ein von Hand ausgerechnetes `inset`: dreimal ergab es 44 px, zweimal 46, dreimal fehlte es ganz. `width/height: max(100%, 44px)` rechnet selbst und zaehlt ueber die Border-Box, also unabhaengig vom Rand. Mindestmass nach [WCAG 2.2 SC 2.5.5](https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html) | `bausteine.py`, `abnahme-mobil.py` |
| **Gleitende Markierung** | gemeinsames Fundament in `css/basis.css` („Gleitende Markierung“) | 4 Leisten: `.tab-ind`, `.kal-pill`, `.db-ind`, `.ws-ind` | **eigen.** Bis 21.09.2026 drei Einzuege (3/4/5 px) und zwei hartkodierte Schatten — gewachsen, nicht entschieden. **Zwei Familien bleiben bewusst**: akzent für kontextuelle Auswahl, neutral für die dauerhaft sichtbare Hauptnavigation (Rot ist die Aktionsfarbe, und die Leiste liegt auf Glas über wechselnden Fotos). Regel und Kontrastnachweis: `docs/DESIGN.md`. Auch **zwei Mechaniken** bleiben: drei schieben mit `translateX(n×100%)`, `.ws-ind` misst — Messen an der Tagesleiste wäre eine Performance-Regression | `bausteine.py`, `pruefstand-reiter.py` |
| **Toast** | `toast(msg)` · `undoToast(msg, fn)` | ~130 Aufrufe, **ein** `#toast`-Element | eigen — die Undo-Variante teilt bewusst dieselbe Basis, sonst entwickeln sich zwei Toasts auseinander | — |

**Diese zehn sind das Vorbild, nicht die Baustelle.** Wer hier etwas ändert, ändert es für
alle — genau so soll es sein.

---

## 2. In Arbeit — noch mehrfach getrennt gebaut

**Zurzeit leer — Etappe 1 ist durch** (21.09.2026). Alle fünf Bausteine aus
`plans/UI-Grundlagen.MD` stehen in Abschnitt 1: Dropdown, Leere Zustände, Aufklapper,
Buttons, Tabs.

Wer hier etwas einträgt, sagt damit: Dieser Baustein ist **heute** mehrfach getrennt
gebaut und wird zusammengeführt. Ein Eintrag ohne Termin und ohne Plan gehört nicht
hierher, sondern nach Abschnitt 3 oder 6.

| Baustein | Heute | Ziel | Herkunft geplant |
|---|---|---|---|

---

### Bekannter Rest: 15 Trefferflaechen sind noch handgerechnet

Der Mechanismus oben deckt die quadratischen Icon-Knoepfe und den Fuss ab. Fuenfzehn
weitere Stellen rechnen ihr `inset` weiter selbst — die meisten **asymmetrisch**
(`inset: -6px 0`), weil dort nur die Hoehe wachsen muss und die Breite ohnehin reicht:

`.section-head .btn.primary` · `.ws-btn` · `.kal-seg button` · `.zeitraum .kal-nb` ·
`.slot .filled .x` / `.pencil` · `.pm-grip` · `.cathead` · `.rfilters button` ·
`.ing-grip` · `.modal-head .btn.ghost` · `.pmore .btn` · `button.pq-h` · `.toast-undo` ·
`.profile-btn` · `.auth-card .btn`

`max(100%, 44px)` traegt diese Faelle mit — bei einem breiten Element bleibt die Breite
stehen und nur die Hoehe waechst. Sie wurden am 21.09.2026 bewusst **nicht** mitgezogen:
Der Auftrag war der Icon-Knopf, und `.ing-grip` (`-7px -12px`) sowie `.toast-antworten`
sind Ziehgriffe mit absichtlich anderer Form. Wer sie angeht, geht sie alle an.

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
| **Eine einzige Aufklapp-Bauart** | Der Meal-Picker baut seine Liste bei jedem Tastendruck über `innerHTML` neu. Ein `<details>`-Zustand ginge dabei jedes Mal verloren — deshalb liegt er dort in einer Variablen |
| **Ein dritter Leerzustand** | Zwei Größen reichen: ganze Ansicht und Zeile im Inhalt. Die alten fünf Namen unterschieden sich um 2 px Abstand und 0,5 px Schrift — genau solche Zufallsunterschiede sollten verschwinden |
| **CSS Anchor Positioning** für Menüs | Chrome/Edge produktiv, Safari erst teilweise, Firefox hinter Flag. Die App muss in einen iOS-WebView — Position wird in JavaScript berechnet |
