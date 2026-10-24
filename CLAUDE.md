# CLAUDE.md

Anleitung für Claude Code in diesem Repository.

**Diese Datei enthält Regeln und Zeiger — keine Begründungen.** Sie wird bei jeder Sitzung
vollständig geladen; jedes Wort hier kostet Kontext in jeder Anfrage. Das *Warum* steht in
`docs/`. Neue Geschichten, Daten und Beispiele gehören dorthin, nicht hierher.

---

# 1. Das Leitziel

**Paddy's Mealplan erscheint im App Store und bei Google Play.** Das ist der Maßstab für
**alle** Entscheidungen — Architektur, Bezahlung, Fremdcode, Berechtigungen.

* **Kein Code wird zur Laufzeit nachgeladen** (Apple 2.5.2). Kein neuer
  `<script src="https://…">`, kein `import()` auf eine fremde URL.
* **Die App startet ohne Netz** und ist ohne Anmeldung sinnvoll nutzbar.
* **Digitale Funktionen in der App brauchen In-App-Purchase** (Apple 3.1.1). Vor allem an
  Pro/Bezahlung: `docs/STORE.md` Abschnitt 2 lesen.

→ Prüfliste und Stand: `docs/STORE.md` · Prüfer: Agent `store-check`

---

# 2. Projektgrundsätze

Kommunikation im gesamten Projekt auf **Deutsch** — Antworten, Code-Kommentare,
Dokumentation, Commit-Messages. Commit-Messages in ASCII: `geprueft`, `geaendert`.

**Paddy's Mealplan** ist ein deutschsprachiger Wochen-Essensplaner aus statischen Dateien
**ohne Build-Prozess**:

| Ort | Inhalt |
|---|---|
| `index.html` | Markup, Firebase-Brücke und der verwobene App-Kern (eine IIFE) |
| `css/` | Design-Tokens und Styles |
| `data/` | Rezeptkatalog, Zutaten, Bilder, Icons, **Rechtstexte** — nur Daten, keine Logik |
| `lib/` | gemeinsame Helfer (`window.PM`), PDF-Schreiber, Barcode-Infrastruktur |

**Klassische Skripte in Dokumentreihenfolge**, keine ES-Module — Module laufen nicht über
`file://`, darauf bauen Smoke-Test und Prüfstände. Wo was liegt: `docs/MODULE.md` (erzeugt,
`python tools/karte.py`).

Neben Abschnitt 3: `docs/BAUSTEINE.md` (UI-Bausteine), `docs/ABDECKUNG.md` (wer prüft was),
`docs/RUNBOOK.md` (Deploy, Rollback, Notfälle), `css/CLAUDE.md`, `data/CLAUDE.md`,
`docs/DATENSCHUTZ-INTERN.md` (gitignored), `FIREBASE-SETUP.md`.

**Code, Dokumentation und Projektstatus müssen nach einer Änderung konsistent sein.**

---

# 3. Dokumentation automatisch synchron halten

Betrifft eine Änderung eine dokumentierte Regel, Architektur, Testmethode oder Fehlerquelle,
wird die Doku **im selben Arbeitsschritt** aktualisiert — ohne dass der Nutzer darum bittet.

| Datei | Aktualisieren bei Änderungen an |
|---|---|
| `docs/PRODUCT.md` | Feature-Regeln, UX, Markenstimme, Premium, Meal-Datenbank, Produktentscheidungen |
| `docs/ARCHITECTURES.md` | Datenmodell, State, localStorage, Firebase, Auth, Sync, Gruppen, Firestore, Rollen, Datenflüssen |
| `docs/DESIGN.md` | Tokens, Typografie, Theme, Makro-Darstellung, Bewegung |
| `docs/TESTING.md` | Testverfahren, Prüfständen, Regressionen, Prüfregeln |
| `docs/TROUBLESHOOTING.md` | Fallen, Bugs, Workarounds, behobenen Fehlern |
| `docs/SECURITY.md` | Regeln, Bedrohungen, Geheimnissen, bewussten Kompromissen |
| `docs/STORE.md` | Bezahlung, Konto, Berechtigungen, Fremdcode, Store-Angaben |

**Dokumentations-Gate:** Vor Abschluss jeder Aufgabe prüfen, ob eine dieser Dateien falsch
oder widersprüchlich geworden ist, und im selben Schritt korrigieren. Bei nicht-trivialen
Änderungen macht das der Agent **`doku-waechter`** über den `git diff`. Keine Doku künstlich
ändern, wo die Änderung keine Relevanz hat.

---

# 4. Produktphilosophie

Paddy's Mealplan ist **kein Kalorien-Tracker**. Ein Tracker schaut zurück — *was habe ich
gegessen?* Paddy's Mealplan schaut nach vorne — *was werde ich essen?*

**Qualität vor Quantität. Einfachheit vor unnötigen Funktionen.** Technische Machbarkeit
oder „wäre auch ganz nett" ist kein Grund für ein Feature.

**Feature-Entscheidungsregel** — vor jeder neuen Funktion, auch vor einem bloßen Vorschlag:

1. Spart sie Zeit?
2. Reduziert sie Entscheidungen des Nutzers?
3. Verbessert sie die Nutzererfahrung?
4. Passt sie zum Wochenplan-Konzept, zu Fitness/Abnehmen und zu `state.goal`?

Kein sinnvolles Ja: **nicht umsetzen** — auch nicht als abgespeckte Variante.
→ `docs/PRODUCT.md`

---

# 5. UX-Grundsätze

Jeder Screen löst möglichst genau ein Problem: wenige Interaktionen, geringe kognitive Last,
klare nächste Aktion, wenige Optionen, keine unnötigen Erklärungen, kurze Wege. Bei zwei
gleichwertigen Lösungen gewinnt die mit weniger Interaktionen.

---

# 6. Markenstimme und Textmenge

Wie ein erfahrener Trainingspartner: motivierend, freundlich, modern, vertrauenswürdig.
**Die Marke hilft dem Nutzer. Sie bewertet ihn niemals** — besonders bei Gewicht, Kalorien,
Zielen, Fortschritt, Fehlern und leeren Zuständen.

UI-Texte kurz, positiv, leicht verständlich. Kein Behörden-Deutsch, keine Roboter- oder
Fachsprache, nichts Wertendes, kein Slang („Bro", „Digga"). Buttons aktiv: `Meal anlegen`,
nicht `Neues Meal wird angelegt`. Fehlermeldungen nicht anklagend.

**So wenig Text wie möglich.** Kein Erklärungssatz, wenn Frage, Label, Option, Beispiel oder
Platzhalter es schon sagen. Notwendige Hinweise kompakt, wenn passend hinter `<details>`.

---

# 7. Design

**Jede neue oder geänderte UI im bestehenden Design „Performance Dark".** Kein eigener Stil,
keine fremden Paletten, keine externen Fonts.

* Vorhandene CSS-Tokens verwenden (`--accent`, `--bg`, `--surface`, `--text`, `--border`,
  `--radius`, `--shadow`, `--fr`/`--mi`/`--ab` …), nichts hartkodieren, wofür es ein Token gibt.
* Nur System-Fonts: `var(--font-display)` für Headlines, `var(--font-body)` für Fließtext.
* Light **und** Dark pflegen — `@media (prefers-color-scheme: dark)` und
  `:root[data-theme=…]`.
* Makros immer als `kcal → KH → P → F`, in einer der **drei** erlaubten Formen. Keine
  vierte. Nie `K` für Kohlenhydrate oder `Eiw.`/`Fett` in Wertzeilen.
* Abschnittsüberschriften bekommen `.sec-h`, keine eigenen Werte.
* Mehrstufige Abläufe: durchgängige Progress-Bar (`.wg-progress-bar`), **nicht anklickbar**.
  Zurück nur über einen eigenen `Zurück`-Button.
* Ansichtswechsel folgen dem Schiebe-Schema; `MOTION`-Tokens sind die einzige Quelle für
  Dauer und Kurve (Ausnahme nur `--dur-marke*`/`--ease-marke` für Startbildschirm und
  Marken-Lader); `reducedMotion()` immer berücksichtigen.
* **In einem Snap-Streifen niemals einen zweiten Scroll-Container anlegen.**

**→ Vollständige Regeln: `docs/DESIGN.md` — bei jeder Design-Änderung zuerst dort.**

**Design-Skills** bei jeder Design-Änderung vorab, in dieser Reihenfolge:
1. `ui-ux-pro-max:ui-ux-pro-max` (UI-Zustände, UX, A11y, Farben) bzw.
   `ui-ux-pro-max:design` (Branding, Logo, Banner)
2. `apple-design` (fluide Interaktion, Motion, Materialien)
3. `emil-design-eng` (Detailpolitur, Press-States)

Empfehlungen **auf Performance Dark mappen**, nie Variablen, Farben oder Kurven der Skills
übernehmen. Animations-Skills (`find-animation-opportunities`, `improve-animations`) nur,
wenn Bewegung Teil der Änderung ist.

---

# 8. Mobile

Mobile ist Bestandteil **jeder** UI-Änderung. Breakpoints `max-width: 720px` und
`max-width: 560px`. Eingaben bei 16 px lassen, sonst zoomt iOS.

Prüfen mit echter Geräte-Emulation, nie über die Fensterbreite:

```powershell
python tools/abnahme-mobil.py        # 3 Breiten x Light/Dark, 96 Stationen
```

⚠️ **Einen `@media`-Block nie mitten in einen bestehenden einfügen** (`docs/TROUBLESHOOTING.md` §97).

---

# 9. Keine Toolchain erfinden

Es gibt **kein** Node, PHP, npm, `package.json`, Bundler, Build, Test-Framework, Linter.
**Keine npm-Befehle erfinden.** Eine Änderung an `index.html` ist unmittelbar die fertige
App. Python ist vorhanden für Hilfs- und Testskripte.

**Ausnahme nur außerhalb dieses Repos:** die Capacitor-Hülle im privaten Nachbar-Repo
`Paddys Mealplan App` (npm, Gradle, Xcode). Sie kopiert die Web-App, sie ändert sie nie
→ `docs/STORE.md` Abschnitt 1.

---

# 10. Lesen und Bearbeiten des Codes

`index.html` ist **rund 1 MB und weit über 13.000 Zeilen lang**. **Nie die komplette Datei
blind lesen** — kein `cat`, keine überlangen Zeilen ungefiltert. Mit `Grep` suchen, nur die
Stelle mit Offset/Limit lesen.

**Immer über alle Code-Dateien suchen, nicht nur `index.html`** — Tokens, Rezeptkatalog,
Rechtstexte, PDF und Barcode liegen woanders (`docs/MODULE.md`).

`data:image;base64` im Umlauf sind Nutzerbilder aus `localStorage`/Firestore — über Skripte
bearbeiten, nie durch den Kontext kopieren.

Zum Testen **nie abtippen oder nachbauen** — den echten Code aus `index.html` ausschneiden.

---

# 11. Testen und Verifikation

**Nach jeder Änderung an JavaScript zuerst** `python syntax-check.py --alles` (rund eine
Sekunde; ein Hook erledigt das automatisch, Abschnitt 18). Ein Syntaxfehler beendet das
ganze App-Script — HTTP 200, aber `#view` bleibt leer.

| Skill | Wofür |
|---|---|
| `/smoke` | Startet die App, ist `#view` gefüllt? |
| `/pruefstand` | Ausschneide-Prüfstand für Funktionen hinter Login, Modal oder komplexem State |
| `/abnahme` | Abnahme am echten Cloud-Konto über `tools/cdp.py` |
| `/deploy` | Push, Verifikation, Rollback |
| `/rezeptcharge` | Neue Rezepte für `COOKBOOK` — Recherche, Nährwerte, Anleitung, Bilder |

Gesamtlauf: `python tools/alle-pruefstaende.py`. Bei Prüfständen, die `OFFEN` von
`REGRESSION` trennen, heißt „grün" nur **keine Regression** — der Läufer weist das aus.

**Prüfaufwand:** Während der Arbeit nur `/smoke` und der **eine** betroffene Prüfstand.
**Vor dem Push** entscheidet die **Stufe** — einmal am Ende, nicht nach jeder Text-, Doku-
oder Pushcheck-Korrektur erneut:

| Stufe | Wenn sich das geändert hat | Was vor dem Push läuft |
|---|---|---|
| **A** | **Nichts an der App**: nur `docs/`, `plans/`, `.claude/`, `tools/`, README, CI | `/pushcheck` Stufe A (`website-security`, `doku-waechter`); bei `.claude/` zusätzlich `python tools/wartung-check.py` |
| **B** | App-Code, aber **nichts, was man sieht oder bedient** (Sync, Rechnen, Speichern, Regeln, `sw.js`, Worker) | `alle-pruefstaende.py` (~5 min) + `/pushcheck` Stufe B |
| **C** | Etwas, das man **sieht oder bedient** (Markup, `css/`, Texte, Bilder, Abläufe) | Vorführung vor der Arbeit (§21b) + `alle-pruefstaende.py` + `abnahme-mobil.py` (~5 min) + `/pushcheck` Stufe C |

Im Zweifel die höhere Stufe. Ein Werkzeug unter `tools/`, das Nutzerdaten anfasst
(`firestore-*.py`, `shared-aufraeumen.py`, `konten-inaktiv.py`), zählt als **B**. `/smoke`
entfällt vor dem Push, sobald `alle-pruefstaende.py` läuft.

Bricht ein langer Test ab: **nicht neu starten**, `docs/TROUBLESHOOTING.md` lesen, Nutzer
fragen (`WebSocketTimeoutException` ist ein bekannter Flake). Ein Hänger kann der Befund sein.

Nicht verhandelbar:
* **Getestet wird echter, ausgeschnittener Produktionscode** — kein Nachbau.
* **Ohne Gegenprobe zählt kein Ergebnis.** Derselbe Prüfstand muss gegen den alten Stand
  **durchfallen**.

→ `docs/TESTING.md` (Teil A: Verfahren, Teil B: Fallarchiv)

---

# 12. Firebase, Cloud-Sync und Security

Die App muss **auch ohne Firebase funktionieren** (Platzhalter-Config, blockiertes Netz,
fehlgeschlagene Initialisierung → lokaler Login). `authMode = "local"` und `"cloud"` bleiben
beide funktionsfähig.

> **Die Firestore Security Rules sind die einzige Sicherheitsgrenze. Alles andere ist
> Bequemlichkeit.**

UI-Sperren sind **keine** Sicherheitsgrenze; DevTools umgehen sie in Sekunden. Jede neue
Berechtigung **zuerst in den Regeln**, dann im Client.

* `allow read` ist **nicht** `allow get` — `read` umfasst `list`. Wo eine unerratbare ID
  schützt: `allow get`, `list` aus.
* `firestore.rules` im Repo ist nur **Vorlage**; verbindlich ist der Stand in der Konsole.
  Vergleich, nur lesend: `python tools/regeln-live.py` (braucht `gcloud auth login`). Ohne
  diesen Lauf bei jeder Aussage zum Live-Zustand sagen, dass er nicht geprüft ist.
* **Vor jedem Veröffentlichen** `python tools/regeln-pruefen.py` (es gibt keinen Emulator).
  **Veröffentlicht wird von Hand in der Konsole**, nie aus einem Skript.
* Die **Firebase-Web-Config in `index.html` ist kein Secret** — Web-Keys identifizieren das
  Projekt, sie autorisieren nichts. Nie als Leck behandeln.

→ `docs/SECURITY.md`

**Geheimnisse** gibt es genau zwei: `OPENAI_API_KEY` in `.env` und den GCP-Service-Account-
Schlüssel des Cloudflare Workers (nur in den Cloudflare-Secrets). **Nie ausgeben**, **nie in
einen Prüfstand oder ein Skript kopieren** (Skripte lesen aus der Umgebung). Stand ein
Schlüssel einmal irgendwo, hilft nur **Rotation**.

---

# 13. Daten und Datenschutz

Ein Meal speichert bei `by` **ausschließlich die UID** — nie Name, E-Mail oder andere
personenbezogene Daten; der Name kommt bei der Anzeige aus `groupMembers`. E-Mail-Adressen
gehören nicht in Gruppen-Mitgliederdokumente.

Bei Änderungen an Sharing, Sync, Gruppen, Datenfeldern, Löschlogik oder personenbezogenen
Daten: Rechtstexte gegen die Implementierung prüfen, Agenten `anwalt` und
`datenschutz-technik` einsetzen. Die Rechtstexte (`data/rechtstexte.js`) enthalten konkrete
technische Zusagen.

**Der Footer bleibt ohne Anmeldung sichtbar**, das Impressum nie hinter dem Auth-Gate.

→ `docs/DATENSCHUTZ-INTERN.md`

---

# 14. Namensdualität

Sichtbar: **Paddy's Mealplan** und **Meal**. Intern: `wochenkueche` und `recipe`:

```text
wochenkueche_v1 · wochenkueche_profile_v1 · app: "wochenkueche"
state.recipes · getRecipe · data-tab="recipes" · .rcard · .recipes
```

**Nicht „aufräumen".** Die Namen stecken in bestehenden Daten und verschickten Sharing-Links.

---

# 15. Bilder und Lizenzen

`photoFor(r)`: eigenes Bild → `img/library/` → `r.photo` → `PHOTO_RULES` → `CAT_PHOTO` →
`PHOTOS.neutral`. Keine Emoji-/Gradient-Fallbacks. Davor entscheidet `mealIcon(r)`:
Schnelleinträge und gescannte Produkte zeigen ein Symbol (`docs/ARCHITECTURES.md`, „Bilder").

* Neue Bilder **nur über `tools/meal-bilder.py`**, nie von Hand, nie aus fremden Quellen.
  Der Stil-Baustein ist **eingefroren**.
* Dateinamen in `PHOTOS` **nie ändern**, Endung inklusive (Sharing-Links, `img/neutral.jpg`
  in `worker/og.js`). Bild ausgetauscht → `VERSION` in `sw.js` hoch.
* Stichworte: Teilwort-Kollisionen beachten (`eis` in `Rindfleisch`, `reis` in
  `Preiselbeere`) — `tools/pruefstand-bildstichworte.py`.
* **Nährwerte nie schätzen** — `tools/rezept-makros.py` gegenrechnen.
* **Katalogrezepte nur über `/rezeptcharge`.** Nummerierte Anleitung, in der **jede Zutat
  vorkommt**, auch Gewürze (`data/CLAUDE.md`, `tools/pruefstand-rezepttexte.py`).

---

# 16. Fremdcode unter `vendor/`

Firebase-SDK und ZXing liegen **lokal**, nicht auf einem CDN (Abschnitt 1). Wird nicht
zurückgedreht, auch nicht „weil ein CDN einfacher zu aktualisieren ist".

* Aktualisieren nur über `tools/firebase-vendor.py`; danach Version, Quelle und SHA-256 in
  **`vendor/HERKUNFT.md`** nachtragen.
* Update **nur mit Anlass** (Sicherheitslücke, konkreter Fehler) — nie wegen einer höheren
  Versionsnummer.
* Niemand merkt von selbst, wenn eine Bibliothek altert: dafür Agent `lieferkette`.
* Apache-2.0-Lizenzhinweise bleiben mitgeliefert (`LICENSE`).

---

# 17. Git und Deployment

Deployment ist ein Push auf `main`; GitHub Pages baut automatisch.

```powershell
git push origin main
git ls-remote origin refs/heads/main   # muss mit...
git rev-parse HEAD                     # ...uebereinstimmen
```

**Nie `git add .`** Alles im Repo ist öffentlich, Gelöschtes bleibt in der Historie. Immer
einzelne Pfade stagen.

Gitignored, nie committen: `plans/`, `dashboard.html`, `Fotos/`, `Marketing/`, `Instagram/`,
`.env`, `docs/DATENSCHUTZ-INTERN.md`, die zugekauften Skills.

**Vor jedem Push `/pushcheck`** in der Stufe aus Abschnitt 11.
→ Rollback, Notfälle: `docs/RUNBOOK.md` und `/deploy`

Lokaler Server: `powershell -NoProfile -ExecutionPolicy Bypass -File test-server.ps1` → `http://localhost:8000/`

---

# 18. Hooks — was automatisch läuft

In `.claude/settings.json`, Skripte unter `.claude/hooks/`:

| Hook | Wirkung |
|---|---|
| `commit-waechter.py` | **Blockiert** `git commit`, wenn Nichtöffentliches im Index liegt |
| `secrets-filter.py` | **Blockiert** Befehle, die `.env` ausgeben würden; dazu sperrt `permissions.deny` jeden Werkzeugzugriff auf `.env` |
| `push-waechter.py` | **Fragt nach** bei `git push`, wenn `/pushcheck` für diesen Stand fehlt |
| `syntax-nach-edit.py` | `syntax-check.py` auf die geänderte Datei — `index.html`, `data/*.js`, `lib/*.js`, `sw.js` |
| `syntax-am-ende.py` | Dasselbe **am Ende jeder Antwort** für alles laut `git status` Geänderte. **Hält an**, wenn rot |
| `wartung-erinnerung.py` | Meldet beim Sitzungsstart, wenn die Wartung überfällig ist |

Dazu `.github/workflows/pruefung.yml` bei jedem Push: Syntax und Secret-Scan.

Wird ein Hook zum Hindernis: melden, nicht umgehen. **Hooks nie relativ adressieren** —
`python "$CLAUDE_PROJECT_DIR/.claude/hooks/…"`, im Skript die Wurzel aus `__file__`
(`docs/TROUBLESHOOTING.md` §140).

---

# 18a. Wartung — das Prüfsystem prüft sich selbst

**Ein Prüfer mit veralteten Fakten prüft das Falsche und meldet trotzdem „sauber".** Deshalb
alle 30 Tage:

1. `python tools/wartung-check.py` — mechanisch, Sekunden.
2. **`/rechtspruefung`**, `store-check` und `lieferkette` — was das Skript nicht sehen kann.
3. `python tools/wartung-check.py --setze` — verweigert ohne Sicherung der letzten 24 h
   (`tools/firestore-backup.py`) und ohne `plans/rechtspruefung-*.md` der letzten 30 Tage.

Monatlich läuft die Prüfung zusätzlich in der Cloud (Routine „Monatliche Wartungsprüfung") —
sie sieht nur, was gepusht ist. → Umfang und Begründung: `docs/TESTING.md` 2k

---

# 18b. Abdeckung — hat jeder Bereich einen Prüfer?

`wartung-check.py` prüft nur, was es gibt. Ob es für alles einen Prüfer gibt, prüft:

```powershell
python tools/abdeckung.py              # Bericht
python tools/abdeckung.py --gegenprobe # wuerde sie eine Luecke ueberhaupt bemerken?
```

Register: **`docs/ABDECKUNG.md`**. **Entsteht ein neuer Produktbereich, gehört die Frage nach
seinem Prüfer zur Änderung** — das Skript ist das Netz darunter, nicht der Plan.

Meldet es eine Lücke:
1. Gehört zu einem bestehenden Prüfer → Zeile in `docs/ABDECKUNG.md` Abschnitt 3–5.
2. Braucht einen neuen → **Agenten entwerfen und dem Nutzer zur Abnahme vorlegen.** Nie still
   anlegen; ein neuer Agent wird **abgenommen**, bevor er scharf geht.
3. Braucht bewusst keinen → Abschnitt 6, **mit Begründung**.

**Falsch ist, eine Kennung einzutragen, damit Ruhe ist.** Das schaltet die Prüfung dauerhaft ab.

---

# 19. Prüf-Agenten

Acht Agenten in `.claude/agents/`. Sie ändern **nie** etwas, sie melden.

**Über `/pushcheck`, je nach Stufe (Abschnitt 11):**

| Agent | Modell | Prüft |
|---|---|---|
| `website-security` | sonnet | **jede Stufe**: Geheimnisse, personenbezogene Daten, XSS, Rules, `sw.js`, Worker, `vendor/`, Historie |
| `anwalt` | sonnet | ab Stufe B: Rechtstext gegen Code |
| `ux-reviewer` | haiku | Stufe C: Übersichtlichkeit geänderter UI (ruft vorher `ui-ux-pro-max`) |
| `kvp` | sonnet | ab Stufe B: Fitness-/Wochenplan-Bezug, Design, Mobile, Bedienbarkeit, Wartbarkeit, Sync |

Ab Stufe B zusätzlich `/code-review`. Rote Funde werden **widerlegt, nicht bestätigt**:
Erreichbarkeit, Wirkung, Schutz, je mit Fundstelle (`/pushcheck`).

**Nach Auslöser, alle auf sonnet:**

| Agent | Auslöser |
|---|---|
| `store-check` | Pro/Bezahlung, Konto, Login, Kamera, `vendor/`, Manifest |
| `lieferkette` | alles unter `vendor/`, neue externe Verweise — und regelmäßig ohne Anlass |
| `datenschutz-technik` | neuer Dienst, neues Datenfeld, Sharing, Gruppen, Löschlogik |
| `doku-waechter` | jede nicht-triviale Änderung — in `/pushcheck` jeder Stufe fest eingeplant |

Nicht für jede Textkorrektur alle Agenten, bei Sicherheit, Daten, Sync, Sharing, Store oder
Recht aber sehr wohl. **🔴-Funde vor dem Melden am echten Code gegenprüfen.** Ein neuer Agent
fehlt in einer laufenden Sitzung eventuell als `subagent_type` — dann neu starten.

---

# 20. Arbeitsweise

**Modellwahl:** Größere Pläne von **Sonnet** umsetzen lassen, danach mit **Opus**
gegenprüfen. Bei komplexen Aufgaben von selbst ein Modell vorschlagen.

**Pläne:** Nach `ExitPlanMode` den Plan aus `.claude/plans` mit sprechendem Namen nach
`plans/` kopieren. Umgesetzte und dokumentierte Pläne ohne Rückfrage löschen.

**`dashboard.html` ist erzeugt, nicht gepflegt.** Nach jedem abgeschlossenen Feature
`plans/app-karte.json` nachziehen und `python tools/dashboard.py` fahren. Drei Phasen in
fester Reihenfolge: **1** App fertig machen, **2** Marktstart, **3** App Store, Pro und
Bezahlung — der Stand steht in der Karte. `--pruefen` prüft die **Struktur** gegen den Code,
der **Status** bleibt Handarbeit. Beides gitignored, **nie committen.**

---

# 21. Ablauf bei jeder Änderung

**Vorher:** Aufgabe verstehen, Code mit `Grep` suchen, `docs/*.md` über das Register am
Dateikopf lesen (bei UI `docs/DESIGN.md` + Design-Skills, bei Problemfeldern
`docs/TROUBLESHOOTING.md`).

**Währenddessen:** Architektur und Tokens respektieren. Keine unnötigen Abstraktionen, keine
Funktion entfernen, weil sie alt aussieht, keine Security nur über UI, keine Daten unnötig
duplizieren.

**Danach:**
1. `/smoke`; vor dem Push die Stufe aus Abschnitt 11.
2. Isolierter Prüfstand, wenn nötig — mit Gegenprobe.
3. Bei UI: mobile, Light und Dark, A11y.
4. Bei Cloud-/Sync-Änderungen: Sync-Szenarien, notfalls `/abnahme`.
5. Rechtstexte prüfen, wenn betroffen; passende Agenten einsetzen.
6. Doku aktualisieren, bei Bedarf `plans/app-karte.json` + `tools/dashboard.py`.
7. `git diff` auf Unbeabsichtigtes prüfen, dann committen. Nach dem Push Remote verifizieren.

---

# 21a. Bevor etwas Neues entsteht — drei Stufen

Gilt für **UI-Bausteine und Interaktionsmuster**, nicht für jede interne Hilfsfunktion.

| Stufe | Frage | Wenn ja |
|---|---|---|
| 1 | **Gibt es das in der App schon?** (`Grep` über `index.html`, `css/`, `lib/`) | Bestehenden Baustein verwenden, **nicht danebenbauen**. In `docs/BAUSTEINE.md` eintragen |
| 2 | **Gibt es das anderswo schon?** (Watermelon, Origin UI, Base UI, React Aria, MDN, WCAG) | **Nachbauen statt erfinden** — besonders bei Tastatur und ARIA. Quelle im Kommentar nennen **und dem Nutzer melden** |
| 3 | Nirgends vorhanden? | **Neu bauen** und festhalten, *warum* nichts passte |

**Wird ein Baustein angefasst, werden ALLE seine Fundstellen angefasst** — sonst entstehen aus
einem Muster zwei.

**Die Herkunft wird dem Nutzer nach jeder Änderung genannt** — Vorbild mit Link und was davon
übernommen wurde, oder „eigene Lösung, weil …“.

Register: **`docs/BAUSTEINE.md`** · Prüfer: `python tools/bausteine.py`

---

# 21b. Sichtbare Änderungen werden vorgeführt, bevor sie live gehen

**Jede sichtbare Änderung wird dem Nutzer zuerst im Browser als Vorher/Nachher gezeigt.**
Erst nach seiner Zustimmung wird committet und gepusht.

```powershell
python tools/schnappschuss.py <baustein>   # Vorher-Stand einfrieren, VOR der Arbeit
# ... Aenderung bauen ...
python tools/vorfuehren.py <baustein>      # oeffnet sichtbar, in EIGENEM Profil
```

⚠️ **Nie im Alltagsbrowser vorführen** — dort ist ein Cloud-Konto angemeldet; `__test`
trennt nur den lokalen Speicher. Was kein Bild zeigt (Tastaturwege, Bewegung, Zustände nach
einem Klick), wird **dazugesagt oder vorgeführt**. Unsichtbares (Werkzeuge, Prüfstände, Doku)
ist ausgenommen. → `docs/TESTING.md` 2g-ter

---

# 21c. Änderungswünsche: erst das Vorgehen anbieten

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

---

# 22. Minimalprinzip

**Ändere nur, was für die Aufgabe notwendig ist.** Keine ungefragten Refactorings,
Umbenennungen, Design-Neuentwürfe, Architekturumbauten, Dependency-Wechsel,
Toolchain-Einführungen oder „Aufräumarbeiten".

Problem außerhalb des Auftrags entdeckt: dokumentieren und kurz darauf hinweisen, nicht
umbauen. **Ausnahme:** Gefährdet es Sicherheit, Datenintegrität oder die aktuelle Aufgabe,
wird es vor Abschluss berücksichtigt.

---

# 23. Definition of Done

Funktion korrekt umgesetzt, nichts Bestehendes beschädigt, relevante Tests und UI-Zustände
geprüft, Design, Mobile und A11y berücksichtigt, Security und Rechtstexte bei Relevanz
geprüft, Doku aktualisiert, Dashboard stimmt, `git diff` gesichtet.
**Code, Dokumentation und Projektstatus beschreiben denselben Stand.**

---

# 24. Prioritäten bei Zielkonflikten

1. Sicherheit und Datenintegrität
2. bestehende funktionierende Architektur
3. Produktnutzen
4. UX und Accessibility
5. Design-System „Performance Dark"
6. Wartbarkeit
7. Performance
8. Code-/Dokumentationskomfort

Keine Regel rechtfertigt eine Sicherheitsverletzung oder Datenbeschädigung.

---

# 25. Wichtigste Grundregel

**Nicht nur Code schreiben. Das Projekt als Ganzes konsistent halten:**
Produkt → UX → Design → Architektur → Daten → Security → Store → Tests → Dokumentation →
Dashboard. Betrifft eine Änderung einen dieser Bereiche, wird er mit aktualisiert und geprüft.
