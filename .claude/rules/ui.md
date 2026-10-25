---
paths:
  - "index.html"
  - "css/**"
  - "lib/**"
---

# UI-Regeln (ausgelagert aus CLAUDE.md §7, §8, §21a-c)

Gilt für jede neue oder geänderte UI im Design „Performance Dark“. Vollständig: `docs/DESIGN.md`.

## Design (§7)

* Kein eigener Stil, keine fremden Paletten, keine externen Fonts. Nur System-Fonts:
  `var(--font-display)` für Headlines, `var(--font-body)` für Fließtext.
* Vorhandene CSS-Tokens verwenden (`--accent`, `--bg`, `--surface`, `--text`, `--border`,
  `--radius`, `--shadow`, `--fr`/`--mi`/`--ab` …), nichts hartkodieren, wofür es ein Token gibt.
* Light **und** Dark pflegen — `@media (prefers-color-scheme: dark)` und `:root[data-theme=…]`.
* Makros immer als `kcal → KH → P → F`, in einer der **drei** erlaubten Formen. Keine vierte.
  Nie `K` für Kohlenhydrate oder `Eiw.`/`Fett` in Wertzeilen.
* Abschnittsüberschriften bekommen `.sec-h`, keine eigenen Werte.
* Mehrstufige Abläufe: durchgängige Progress-Bar (`.wg-progress-bar`), **nicht anklickbar**.
  Zurück nur über einen eigenen `Zurück`-Button.
* Ansichtswechsel folgen dem Schiebe-Schema; `MOTION`-Tokens sind die einzige Quelle für Dauer
  und Kurve (Ausnahme nur `--dur-marke*`/`--ease-marke` für Startbildschirm und Marken-Lader);
  `reducedMotion()` immer berücksichtigen.
* **In einem Snap-Streifen niemals einen zweiten Scroll-Container anlegen.**

**Design-Skills** bei jeder Design-Änderung vorab, in dieser Reihenfolge:
1. `ui-ux-pro-max:ui-ux-pro-max` (UI-Zustände, UX, A11y, Farben) bzw. `ui-ux-pro-max:design`
   (Branding, Logo, Banner)
2. `apple-design` (fluide Interaktion, Motion, Materialien)
3. `emil-design-eng` (Detailpolitur, Press-States)

Empfehlungen **auf Performance Dark mappen**, nie Variablen, Farben oder Kurven der Skills
übernehmen. Animations-Skills (`find-animation-opportunities`, `improve-animations`) nur, wenn
Bewegung Teil der Änderung ist.

## Mobile (§8)

Mobile ist Bestandteil **jeder** UI-Änderung. Breakpoints `max-width: 720px` und
`max-width: 560px`. Eingaben bei 16 px lassen, sonst zoomt iOS. Prüfen mit echter
Geräte-Emulation, nie über die Fensterbreite:

```powershell
python tools/abnahme-mobil.py        # Alltag: iPhone SE, Hell + Dunkel (~2 min)
python tools/abnahme-mobil.py --voll # 3 Breiten x Light/Dark, 96 Stationen
```

⚠️ **Einen `@media`-Block nie mitten in einen bestehenden einfügen** (`docs/TROUBLESHOOTING.md` §97).

## Bevor etwas Neues entsteht — drei Stufen (§21a)

Gilt für **UI-Bausteine und Interaktionsmuster**, nicht für jede interne Hilfsfunktion.

| Stufe | Frage | Wenn ja |
|---|---|---|
| 1 | **Gibt es das in der App schon?** (`Grep` über `index.html`, `css/`, `lib/`) | Bestehenden Baustein verwenden, **nicht danebenbauen**. In `docs/BAUSTEINE.md` eintragen |
| 2 | **Gibt es das anderswo schon?** (Watermelon, Origin UI, Base UI, React Aria, MDN, WCAG) | **Nachbauen statt erfinden** — besonders bei Tastatur und ARIA. Quelle im Kommentar nennen **und dem Nutzer melden** |
| 3 | Nirgends vorhanden? | **Neu bauen** und festhalten, *warum* nichts passte |

**Wird ein Baustein angefasst, werden ALLE seine Fundstellen angefasst** — sonst entstehen aus
einem Muster zwei. **Die Herkunft wird dem Nutzer nach jeder Änderung genannt** — Vorbild mit
Link und was davon übernommen wurde, oder „eigene Lösung, weil …“.
Register: `docs/BAUSTEINE.md` · Prüfer: `python tools/bausteine.py`

## Vorführung vor dem Livegang (§21b)

**Jede sichtbare Änderung wird dem Nutzer zuerst als Ist/Soll gezeigt** — als fertiger Film mit
Bildpaaren, die er nur ansieht, nicht bedient. Erst nach seiner Zustimmung wird committet und
gepusht.

```powershell
python tools/schnappschuss.py <baustein>   # Ist-Stand einfrieren, VOR der Arbeit
python tools/vorher-nachher.py <baustein>  # Film + Bildpaare, Hell/Dunkel, oeffnet die Seite
python tools/vorfuehren.py <baustein>      # nur zum Selbst-Ausprobieren, EIGENES Profil
```

Dazwischen: Änderung bauen, in `tools/vergleich-bausteine.js` `film` mit `tippe` je Schritt.
⚠️ **Nie im Alltagsbrowser vorführen** — dort ist ein Cloud-Konto angemeldet; `__test` trennt nur
den lokalen Speicher. Was kein Bild zeigt (Tastaturwege, Bewegung, Zustände nach einem Klick),
wird **dazugesagt oder vorgeführt**. Unsichtbares (Werkzeuge, Prüfstände, Doku) ist ausgenommen.
→ `docs/TESTING.md` 2g-ter

## Änderungswünsche: erst das Vorgehen anbieten (§21c)

Gilt für alles, was der Nutzer **sieht oder bedient**, und für **neue Funktionen** — **nicht**
für Fehlerbehebungen, Tippfehler, Doku, Werkzeuge und Prüfstände.

**Zuerst per Auswahlbildschirm fragen, ob vorher recherchiert werden soll.** „Ohne Recherche“
ist eine gültige Antwort. Bei Ja:

1. **Recherche:** Konkurrenten (z. B. MyFitnessPal, Lifesum, Yazio, Mealime) und Üblichkeit
   (Apple HIG, Material, NN/g, Baymard, WCAG), mit **Quellen**, Lücken offen benannt.
2. **Vorschläge:** 2–3 Varianten mit Skizze, Empfehlung zuerst, Für und Wider gegen §4 und §7.
3. **Erst nach der Auswahl bauen.** Dann Vorher/Nachher (§21b), Prüfungen, Livegang.
4. **Größere Umbauten** (neuer Ablauf, mehrere Bildschirme): vor dem Livegang
   `tools/abnahme-mobil.py`, **direkt danach** den Nutzer bitten, es am eigenen Handy
   anzusehen (der Testserver ist nur am PC erreichbar). Fällt etwas auf: Rückweg über `/deploy`.

Vorbild: Umbau des Anmeldebereichs (`docs/PRODUCT.md`, „eine Entscheidung statt zwei“).
