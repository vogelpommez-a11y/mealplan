# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Die Kommunikation im Projekt läuft auf Deutsch — auch Code-Kommentare und Commit-Messages.
Commit-Messages werden bewusst in ASCII geschrieben (`geprueft` statt `geprüft`).

## Design-Vorgabe: „Performance Dark" (verbindlich)

**Jede neue oder geänderte UI wird im bestehenden Design „Performance Dark" umgesetzt — egal
worum es geht.** Kein Neuentwurf eines eigenen Stils, keine fremden Farbpaletten/Schriften.
Neue Elemente fügen sich in das vorhandene System ein und nutzen dessen CSS-Variablen aus dem
`:root` von `index.html` (nicht hartkodieren):

- **Schrift:** Display/Headlines `var(--font-display)` (kondensiert, athletisch — Bahnschrift/
  Arial Narrow/…, nur System-Fonts, kein externes Font-CDN), Fließtext `var(--font-body)`.
- **Akzent:** Rot — `--accent` (`#DC2626` light / `#FF3040` dark), `--accent-strong`.
- **Flächen/Text:** `--bg`, `--surface`, `--surface-2`, `--text`, `--text-muted`, `--border`,
  `--border-strong`. Dark ist der Charakter des Themes; Light- und Dark-Werte immer beide pflegen
  (Blöcke `@media (prefers-color-scheme: dark)` und `:root[data-theme=…]`).
- **Form:** `--radius`/`--radius-sm`, `--shadow`, `--maxw`. Kategorie-Farben `--fr`/`--mi`/`--ab`.
- **Ton:** sportlich/„Performance", Slogan „Plan it. Cook it. Lift it.", rundes Logo auf rotem Kreis.

Wenn eine Design-Entscheidung nicht durch vorhandene Tokens abgedeckt ist, erst fragen bzw. einen
neuen Token im gleichen Stil anlegen — nicht danebendesignen.

## Schritt-für-Schritt-Abläufe: durchgängige Leiste (verbindlich)

**Jeder mehrstufige Ablauf (Assistent/Wizard, der Objekte/Werte schrittweise abfragt oder
einpflegt) zeigt seinen Fortschritt als durchgängige Leiste — dieselbe Klasse
`.wg-progress-bar`, nicht neu gebaut.** Ein rein visueller Balken, der sich anteilig füllt
(`(aktueller Schritt + 1) / Gesamtschritte`), plus ein kurzer Text darunter im Stil
„Schritt 3 von 4 · Training". Kein Rückgriff auf einzelne nummerierte Kacheln/Buttons je
Schritt (wie früher `.cb-b` im Kalorienrechner: vier 44 px hohe Zwei-Zeilen-Kästen mit
Nummer + Beschriftung) — das wirkt klobig neben der schlanken Optik der ersten Schritte
(Onboarding) und wurde deshalb im Kalorienrechner durch genau diese Leiste ersetzt.

Die Leiste ist **nicht antippbar** — kein Sprung auf einen beliebigen früheren Schritt per
Klick auf die Leiste. Zurück geht ausschließlich über einen eigenen „Zurück"-Knopf, wie im
Onboarding. Ein Zwischenstand mit vier antippbaren Segmenten (Sprung auf jeden erreichten
Schritt) wurde bewusst wieder verworfen, um exakt der Onboarding-Optik zu folgen.

Technischer Hinweis, falls der Ablauf auf `initCarousel()` aufsetzt (wie der Kalorienrechner):
Die Funktion braucht intern eine feste Anzahl Kind-Elemente als Gerüst, um den aktuellen
Schritt zu verfolgen — ohne sie bricht die Navigation. Diese Platzhalter bleiben unsichtbar
und aus Tastatur-/Screenreader-Fokus genommen (`aria-hidden="true"`, `tabindex="-1"` auf den
Elementen), sichtbar ist ausschließlich der durchgängige Balken darüber.

## Textmenge-Vorgabe: knapp statt erklärend (verbindlich)

**Die App bleibt übersichtlich. Jede UI zeigt so wenig Text wie möglich, nicht so viel wie
möglich erklärt.** Kein Zusatzsatz, der begründet, *warum* eine Frage gestellt wird oder was ein
Wert *bedeutet*, wenn die Frage/Beschriftung/das Beispiel für sich schon verständlich ist.

Negativbeispiel, das genau deshalb entfernt wurde: „Für den Grundumsatz – bei sonst gleichen
Werten macht das rund 160 kcal aus." unter der Frage „Was ist dein Geschlecht?" — die Frage
steht sichtbar im Kontext eines Kalorienrechners, die Begründung war überflüssige Fachsimpelei.

Faustregel vor jedem neuen Hilfetext (`.onb-why`, `.hint`, `.tdays-note`, Platzhaltertexte o. ä.):
- Erklärt der Satz etwas, das aus Frage + Optionen/Platzhalter/Beispiel schon hervorgeht? → weg.
- Bleibt beim Streichen eine echte Lücke (z. B. „dein Training zählt hier NICHT mit" — sonst
  läuft die Rechnung doppelt)? → ein kurzer Halbsatz reicht, kein ganzer Absatz.
- Rechtlich/fachlich nötige Hinweise (Disclaimer, Datenschutz) gehören hinter ein `<details>`,
  nicht offen im Fließtext — sie sind Pflicht, aber keine Zusatzinformation für den Regelfall.

Gilt für alle Screens, nicht nur den Rechner/das Onboarding.

**Bei jeder Design-Änderung zuerst den Skill `ui-ux-pro-max` aufrufen** — verbindlich, nicht
optional. `ui-ux-pro-max:ui-ux-pro-max` für UI-Zustände, Farben, UX- und A11y-Regeln,
`ui-ux-pro-max:design` für Branding/Logo/Banner. Dessen Empfehlungen dann auf die Projekt-Tokens
mappen, nie dessen eigene Variablen übernehmen.

## Was das ist

„Paddy's Mealplan" — ein deutschsprachiger Wochen-Essensplaner. Die gesamte App ist **eine
einzige Datei**: `index.html` (~716 KB, HTML + CSS + JS inline, keine Abhängigkeiten außer
Firebase vom CDN). Sie wird unverändert von GitHub Pages ausgeliefert:
<https://vogelpommez-a11y.github.io/mealplan/> (Repo `vogelpommez-a11y/mealplan`, Branch `main`).

Betreiber ist eine Privatperson; die Seite ist öffentlich und nicht kommerziell. Monetarisierung
ist geplant, aber noch nicht aktiv.

## Es gibt keine Toolchain

Kein Build, kein Bundler, kein Test-Framework, kein Linter, kein `package.json`. **Node und PHP sind
auf diesem Rechner nicht installiert.** Erfinde keine `npm`-Befehle — es gibt sie nicht.
Eine Änderung an `index.html` ist sofort die fertige App.

**Python ist vorhanden** (`C:\Users\Paddy\AppData\Local\Programs\Python\Python312\python.exe`) — es
gehört nicht zur App, wird aber von den Skill-Skripten gebraucht (z. B. `ui-ux-pro-max`).

Daraus folgt: JS-Syntax lässt sich nicht direkt prüfen. Verifiziert wird ausschließlich im Browser
(siehe unten). Das ist keine Bequemlichkeit, sondern die einzige Möglichkeit.

## Befehle

```powershell
# Lokaler Test-Server (PowerShell-HttpListener, liefert diesen Ordner auf Port 8000)
powershell -NoProfile -File test-server.ps1     # -> http://localhost:8000/

# Verifikation ohne JS-Runtime: Seite headless rendern und das DOM prüfen
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --virtual-time-budget=9000 `
  --user-data-dir="<scratchpad>\edge-profile" `
  --dump-dom "file:///C:/Users/Paddy/Documents/Paddys%20Mealplan/index.html" > dump.html

# Deployen = pushen. Pages baut automatisch (~1 Min).
git push origin main
```

**Der Render-Test ist der Smoke-Test.** Ein JS-Syntaxfehler killt das komplette Script: Der Header
(statisches HTML) bleibt sichtbar, aber `<main id="view">` bleibt **leer**. Prüfe im Dump also
nicht nur den HTTP-Status, sondern ob `#view` tatsächlich Inhalt hat (z. B. „Willkommen",
„Anmelden"). Ein 200er sagt hier gar nichts.

Screenshots der Gesamtseite laufen in Timeouts — nutze `--dump-dom` und suche im Text.

### Ausschneide-Prüfstand (die eigentliche Testmethode)

Der Render-Test sagt nur „kein Syntaxfehler". Er kann **nichts** prüfen, was hinter dem Login oder
in einem Modal liegt — und das ist fast jede Funktion. Dafür gibt es hier ein Verfahren, das ohne
Test-Framework auskommt und sich mehrfach bezahlt gemacht hat:

**Den zu prüfenden Teil per Python aus `index.html` herausschneiden** (zwischen zwei Markern im
Code, z. B. `src.index("// ---------- Barcode-Scan")` bis `src.index("// Ziel aus dem")`),
in eine kleine HTML-Datei im Scratchpad schreiben, fehlende Helfer (`el`, `esc`, …) stubben und
headless mit `--dump-dom` ausführen. Ergebnisse in ein `<pre>` schreiben und **nach jedem Schritt**
aktualisieren — sonst sieht man bei einem Hänger nicht, wie weit es kam.

Entscheidend: **nicht abtippen, sondern ausschneiden.** Getestet wird sonst eine Kopie, die von der
Wahrheit abweichen kann.

Damit prüfbar, was sonst nur im Handbetrieb auffiele:

- **Reine Logik** gegen echte Daten (Suchranking, Namensauflösung, Plausibilität ganzer Tabellen).
- **Fremde APIs** wirklich aufrufen statt zu vermuten, welche Felder sie liefern.
- **Zustandsverwaltung mit Attrappen** — z. B. `navigator.mediaDevices` per
  `Object.defineProperty` überschreiben (es ist schreibgeschützt) und jedes `stop()` mitzählen, um
  alle Ausstiegspfade der Kamera zu prüfen. `video.srcObject` akzeptiert dabei nur einen echten
  `MediaStream`, also `new MediaStream()` als Basis nehmen und `getTracks` überschreiben.
- **Layout**, indem der `<style>`-Block ausgeschnitten und ein Stück Markup isoliert bei fester
  Breite fotografiert wird (`--window-size` + `--screenshot`). Kleine Seiten laufen nicht in
  Timeouts, anders als die Gesamtseite. Beide Themes über `data-theme` prüfen.

Zwei echte Fehler kamen so ans Licht, die im Browser erst der Nutzer gefunden hätte: ein
`await video.play()`, das auf manchen Geräten nie auflöst (der Scanner wäre dauerhaft in „Kamera
wird gestartet" hängen geblieben, ohne dass ein `catch` greift), und ein Makro-Raster, das mobil
vier statt zwei Spalten ergab. Faustregel: Wenn eine Prüfung hängt statt fehlzuschlagen, ist das
meist ein Befund, kein kaputter Prüfstand.

### Push-Falle (teuer gelernt)

`git push` hängt am Windows Git Credential Manager (Timeout, kein Popup in nicht-interaktiven
Shells). Wenn `gh` eingeloggt ist, einmalig `gh auth setup-git --hostname github.com` setzen. Sonst
`$env:GIT_TERMINAL_PROMPT=0` und hoffen, dass die Credentials gecacht sind. Push-Erfolg immer
gegenprüfen: `git ls-remote origin refs/heads/main` gegen `git rev-parse HEAD`.

`gh` liegt unter `C:\Program Files\GitHub CLI` und ist nicht im PATH — in neuen Sessions ergänzen.

## Architektur von index.html

Grob nach Zeilen (verschiebt sich; mit `Grep` nachsehen, nicht auf Zahlen verlassen):

| Bereich | Inhalt |
|---|---|
| ~1–547 | `<head>`, CSS. Enthält `<meta charset>` + `viewport` — **nicht entfernen**, sonst ist die Seite auf dem Handy winzig |
| 548–596 | `<header>`, `<main id="view">`, `<footer class="site-foot">` |
| 597–698 | `<script type="module">` — Firebase |
| 700–2402 | `<script>` mit `(function () { "use strict"; …` — die eigentliche App |
| 937–984 | `PHOTO_CREDITS` und `PHOTOS` zwischen `/*CREDITS_START*/`…`/*PHOTOS_END*/` |

### Die zwei Scripts und ihre Brücke

Das **Modul-Script** (`type="module"`, läuft *vor* der App) importiert Firebase v10 vom
gstatic-CDN und legt drei Objekte auf `window`:

- `window.CloudAuth` — Registrieren/Login (E-Mail + Google), Bestätigungsmail, Passwort-Reset
- `window.CloudSync` — `load`/`save`/`watch` auf `users/{uid}`
- `window.CloudShare` — `publish`/`fetch` auf `shared/{id}`

Die Verbindung zur App läuft über **eine einzige Brücke**: Das Modul ruft aus
`onAuthStateChanged` heraus `window.__onCloudAuth(user)`; die App setzt dieses Feld auf ihre
Funktion `handleCloudUser`. Beide Scripts teilen sonst nichts. Wer die Auth anfasst, muss beide
Seiten dieser Brücke im Blick haben.

`handleCloudUser` verzweigt dreifach: verifiziert → `enterApp`, unverifiziert →
`renderVerifyPending`, kein User → `renderAuthCloud`.

### Graceful Fallback — die App darf nie brechen

Wenn die `firebaseConfig` Platzhalter enthält **oder** das CDN blockiert ist, feuert
`cloudauth:disabled` bzw. ein 6-Sekunden-Timeout in `boot()`, und die App fällt auf den alten
**lokalen Login** zurück (`renderAuthLocal`, Profil nur in localStorage). `authMode`
(`"local"` / `"cloud"`) steuert danach Logout und Profil-Formular. Dieser Pfad muss funktionsfähig
bleiben — er ist der Grund, warum die App auch ohne Firebase startet.

### Datenmodell

`state = { recipes, plan, tab }`, persistiert unter dem localStorage-Key `wochenkueche_v1`
(`load()`/`save()`). Im Cloud-Modus schiebt `save()` zusätzlich via `scheduleCloudPush()`
(800 ms Debounce) das **ganze** State-Dokument nach `users/{uid}`. Live-Pull über `onSnapshot`;
gegen Endlosschleifen prüft der Handler `hasPendingWrites` und vergleicht JSON — `tab` ist
ausgenommen, damit ein Tab-Wechsel keinen Write auslöst.

Beim Login merged `startCloudSync(uid)` die Rezepte per Union (nichts geht verloren) und filtert
dabei `!isExample(r)`, damit die Beispiel-Meals nicht in ein bestehendes Konto wandern.

## Fallen, die Geld oder Daten gekostet haben

**Die Datei ist zu groß zum Lesen.** Die Base64-Fotos sind einzelne Zeilen mit zehntausenden
Zeichen. Nie `Read` ohne `offset`/`limit`, nie `cat`. Immer `Grep` und nur die Trefferstellen
lesen.

**Oktal-Escapes im Strict Mode.** `"\267"` in einem String-Literal ist unter `"use strict"` ein
**Syntaxfehler, der das ganze Script tötet**. Für Bytes im PDF-Stream das echte Zeichen (`·`)
nehmen und `pdfEsc` wandeln lassen, oder `"\\267"` schreiben. Das PDF wird komplett selbst erzeugt
(`planPdfString`/`downloadPdf`, Helvetica + WinAnsi, alles ASCII), weil `window.print()` in der
Artifact-Sandbox blockiert ist.

**Base64 nie durch den Kontext kopieren** — die Zeichen verfälschen sich. Bilder immer per Skript
injizieren.

**`allow read` in Firestore umfasst `get` UND `list`.** Genau daran hing ein echtes Leck: Jede
angemeldete Person konnte alle geteilten Pläne auflisten. Deshalb steht dort jetzt `allow get`.

**`firestore.rules` im Repo ist nur eine Vorlage.** Wirksam ist ausschließlich, was in der
Firebase-Konsole **veröffentlicht** wurde. Der Live-Stand ist von hier aus nicht abrufbar — bei
jeder Aussage über die Regeln dazusagen. Nach Änderungen an der Datei muss der Nutzer sie manuell
in der Konsole veröffentlichen.

**Die `firebaseConfig` in `index.html` ist kein Geheimnis.** Firebase-Web-Keys sind öffentlich by
design; sie identifizieren das Projekt, sie autorisieren nichts. Der Schutz kommt aus Authorized
Domains + Security Rules. Nie als Leck melden.

## Namensdualität — nicht „aufräumen"

Sichtbar heißt die App **„Paddy's Mealplan"** und die Entität **„Meal"**. Intern heißt alles
weiter `wochenkueche` und `recipe`:

- localStorage-Keys (`wochenkueche_v1`, `wochenkueche_profile_v1`), `app: "wochenkueche"` im
  Teilen-Payload
- `state.recipes`, `getRecipe`, `data-tab="recipes"`, CSS `.rcard` / `.recipes`

**Das ist Absicht.** Umbenennen bricht gespeicherte Daten und alte Teilen-Links. Nur Anzeigetexte
wurden umgestellt. (Der Kategorie-Rückfall `r.category || "Gericht"` bleibt ebenfalls — Kategorie
ist keine Entität.)

## Bilder und Lizenzen

`photoFor(r)` liefert **immer** ein Foto: eigenes Bild > Stichwort (`PHOTO_RULES`) > Kategorie
(`CAT_PHOTO`) > `PHOTOS.neutral`. Der frühere Emoji-/Farbverlauf-Fallback ist entfernt —
`pickEmoji`, `gradientFor`, `EMOJI_RULES`, `visualFor` existieren nicht mehr.

Alle mitgelieferten Fotos sind **CC0 1.0 / Public Domain Mark 1.0** und in `PHOTO_CREDITS`
belegt, das `creditsHtml()` als Tabelle im Impressum ausgibt. **Die Schlüssel von `PHOTOS` und
`PHOTO_CREDITS` müssen deckungsgleich bleiben.** Ein angezeigtes Foto ohne Nachweis ist das
teuerste Risiko dieser Seite (Abmahnung). Neue Fotos nur aus Quellen mit belegter freier Lizenz und
nur mit Eintrag in `PHOTO_CREDITS`.

Beim Stichwort-Matching auf Teilwörter achten: „eis" steckt auch in „Rindfleisch", „reis" in
„Preiselbeere".

## Rechtstexte

Impressum und Datenschutzerklärung stehen im Code (`openImpressum()`, `openDatenschutz()`, gerendert
über `legalModal`). Der Footer ist **immer** sichtbar, auch auf dem Login-Screen — das Impressum
muss ohne Anmeldung erreichbar sein. Nicht hinter das Auth-Gate schieben.

Die Texte machen konkrete technische Zusagen (§8: Teilen-Links sind nicht auflistbar; §10:
geteilte Pläne sind löschbar, weil jeder Snapshot eine `uid` trägt). **Wer an Teilen, Sync oder
Datenfeldern arbeitet, ändert damit potenziell die Wahrheit dieser Zusagen.**

## Prüf-Agenten

Drei projektspezifische Agenten liegen unter `.claude/agents/`:

- **`website-security`** — Geheimnisse, personenbezogene Daten, XSS, Git-Historie
- **`anwalt`** — gleicht Rechtstext gegen Code ab (keine Rechtsberatung)
- **`kvp`** — sieht sich den `git diff` an und schlägt Verbesserungen vor. Fragt immer zuerst,
  ob die Änderung zum Thema Fitness/Abnehmen und zum Wochenplan-Konzept passt (`state.goal`,
  Makro-Logik, Wochenrhythmus), danach Design-Konformität, Mobile, Bedienbarkeit, Wartbarkeit
  und Sync. Ändert bewusst nichts, hat keine Schreibrechte.

`website-security` und `anwalt` vor einem Push einsetzen, wenn ein Dienst, ein Datenfeld oder
etwas an der Teilen-Funktion dazugekommen ist. `kvp` passt davor — wenn eine Änderung fertig ist
und vor dem Commit noch einmal jemand draufschauen soll.

Hinweis: Ein **neu angelegter** Agent ist in der laufenden Session noch nicht als `subagent_type`
wählbar — die Liste wird beim Start gelesen. Dann entweder die Session neu starten oder
`general-purpose` die `.md` lesen lassen.

## ROADMAP.html — verbindlich automatisch pflegen

Im Projektordner liegt `ROADMAP.html`: eine visuelle Übersicht im Design „Performance Dark"
(erledigte Bausteine, „Als Nächstes", „Später", Leitplanken-Fragen für jedes neue Feature). Der
Nutzer öffnet sie im Browser, um den Stand zu sehen — sie ist seine Hauptansicht auf das Projekt.

**Nach jedem abgeschlossenen Feature, jeder Entscheidung und jedem Push automatisch mitziehen —
ohne dass der Nutzer extra danach fragen muss:**

- Karte von „Als Nächstes"/„Später" nach „Erledigt und live" verschieben.
- Fortschrittszähler und Balkenbreite (`.bar > i { width }`) anpassen.
- Datum und Commit-Hash im `.stand`-Absatz aktualisieren.
- Neue offene Fragen/Risiken als `<p class="warn">`-Absatz ergänzen, nicht im Fließtext
  verstecken.

**Die Datei bleibt in `.gitignore` und wird nie committet.** Sie beschreibt offene Schwachstellen
(z. B. dass das Pro-Gating aktuell clientseitig und damit umgehbar ist) und Geschäftsplanung —
das gehört nicht öffentlich auf GitHub Pages.

## Weiteres

- `FIREBASE-SETUP.md` — Anleitung für den Nutzer (Projekt anlegen, Provider, Authorized Domains,
  Firestore, Regeln veröffentlichen).
- `.gitignore` hält `Fotos/`, `ROADMAP.html`, Exporte und `.claude/settings.local.json` draußen.
  Alles im Repo ist öffentlich — auch Dateien, die die Seite nie lädt, und auch Gelöschtes
  bleibt in der Historie.
- Mobile: Media-Queries bei `max-width:720px` und `560px`; Eingaben sind 16 px gegen den
  iOS-Auto-Zoom.
