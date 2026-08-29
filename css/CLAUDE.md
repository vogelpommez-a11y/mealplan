# Regeln für `css/`

Ergänzt die Wurzel-`CLAUDE.md`. Hier steht nur, was **speziell für diesen Ordner** gilt.
Die vollständigen Design-Regeln samt Begründungen stehen in `docs/DESIGN.md` — bei jeder
Design-Änderung zuerst dort nachsehen.

---

## Was wo liegt

| Datei | Inhalt |
|---|---|
| `tokens.css` | ausschließlich Design-Tokens und Themes |
| `basis.css` | Notch/safe-area, Header, Fußzeile, Buttons, Wochenraster, Trainingstag, Makrozeilen, `.sec-h` |
| `komponenten.css` | Rezeptraster, Zutatenzeilen, Meal-Ansicht, Bottom-Sheet, Modal, Picker, Listen, Vorkochen, Toast, Profil, Intro/Rechner, Druck |
| `mobil.css` | alles ab der Marke „Mobile / Smartphone" bis zum Ende — Breakpoints, Wisch-Karussell, Onboarding, sehr schmale Geräte, Gruppen-Dialog |

Die Dateien werden in genau dieser Reihenfolge eingebunden.

**`.app` liegt bewusst auf zwei Dateien verteilt:** Schrift, Farbe, Hintergrund und
`min-height` stehen in `tokens.css`, `display: flex` und die Spaltenrichtung in
`basis.css`. Das war schon vor der Aufteilung so - die beiden Regeln standen im
`<style>`-Block rund zwoelf Zeilen auseinander. Der Schnitt hat sie nur auf zwei Dateien
verteilt, ohne ihre Reihenfolge zu aendern. Wer `.app` sucht, muss in beiden nachsehen;
sie zusammenzuziehen waere eine Aenderung an der Kaskade und keine Aufraeumarbeit.

**Die Reihenfolge ist Verhalten, nicht Geschmack.** CSS kaskadiert: zwei Regeln gleicher
Spezifität entscheidet die spätere. Dateien umsortieren, eine Regel in eine andere Datei
verschieben oder einen Block ans Dateiende hängen kann die Darstellung ändern, ohne dass
eine einzige Deklaration angefasst wurde. Deshalb steht der Gruppen-Dialog in `mobil.css`,
obwohl er keine mobile Regel ist — dort stand er vorher, und dort bleibt er.

---

## Die vier Token-Blöcke

Tokens stehen in **vier** Blöcken in `tokens.css`:

```
:root                                    Grundwerte (Light)
@media (prefers-color-scheme: dark)      Systemeinstellung dunkel
:root[data-theme="light"]                ausdrücklich hell gewählt
:root[data-theme="dark"]                 ausdrücklich dunkel gewählt
```

**Wer einen Wert nur in einem Block ändert, bricht die anderen drei.** Ein Token, das nur
im Dark-Media-Block existiert, fehlt jedem, der das Theme ausdrücklich umgestellt hat.

Keine Werte hartkodieren, für die ein Token existiert. Kein `#DC2626`, wo `var(--accent)`
steht. **Gold ist für Pro reserviert** und hat in normaler UI nichts zu suchen.

Nur System-Fonts: `var(--font-display)` für Headlines, `var(--font-body)` für Fließtext.
Keine externen Fonts — ein Google-Fonts-CDN wäre in Deutschland ein Datenschutzrisiko und
verstieße gegen den Offline-Start.

---

## `@media`-Blöcke

⚠️ **Nie einen `@media`-Block mitten in einen bestehenden einfügen.** Das hat am
16.08.2026 den 680-px-Block zerschnitten und die gesamte mobile Ansicht lahmgelegt.

Vor jedem Einfügen prüfen, auf welcher Verschachtelungsebene die Zeile liegt. Ein neuer
Block gehört auf die oberste Ebene, zwischen zwei abgeschlossene Blöcke.

Breakpoints: `max-width: 720px` und `max-width: 560px`, dazu die bestehenden 680er, 400er
und 359er. Bei Eingabefeldern **16 px beibehalten**, sonst zoomt iOS beim Fokus.

---

## Makros

Makros immer als `kcal → KH → P → F`, in einer der **drei** in `docs/DESIGN.md` erlaubten
Formen. Keine vierte erfinden. Nie `K` für Kohlenhydrate, nie `Eiw.`/`Fett` in Wertzeilen.

Abschnittsüberschriften bekommen `.sec-h`, keine eigenen Werte.

---

## Prüfen

Mobile Darstellung ist Bestandteil **jeder** UI-Änderung, nicht ein späterer Schritt.
Nach einer Änderung tatsächlich ansehen: 720 / 560 / 400 px, Light **und** Dark, beide
`data-theme`-Richtungen, Wisch-Karussell, Onboarding, `prefers-reduced-motion`.

`tools/pruefstand-grpm-zoom.py` misst über die Kaskade und holt sich das CSS mit
`quelle.css_gesamt()` — also alle vier Dateien in Ladereihenfolge. Ein Prüfstand, der nur
eine Datei nimmt, misst gegen ein Viertel der Regeln und meldet trotzdem ein Ergebnis.

Zuständige Prüfer laut `docs/ABDECKUNG.md`: `ux-reviewer` (Tokens, Zustände) und `kvp`
(Mobile).
