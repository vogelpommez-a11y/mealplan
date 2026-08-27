# CLAUDE.md

Anleitung für Claude Code in diesem Repository.

**Diese Datei enthält Regeln und Zeiger — keine Begründungen.** Sie wird bei jeder Sitzung
vollständig geladen; jedes Wort hier kostet Kontext in jeder einzelnen Anfrage. Das *Warum*
steht in `docs/`, dort wo man es sucht, wenn man es braucht.

---

# 1. Das Leitziel

**Paddy's Mealplan erscheint im App Store und bei Google Play.** Das ist der Maßstab für
**alle** Entscheidungen — Architektur, Bezahlung, Fremdcode, Berechtigungen.

Die drei Regeln, die daraus unmittelbar folgen:

* **Kein Code wird zur Laufzeit nachgeladen** (Apple 2.5.2). Deshalb liegt das
  Firebase-SDK in `vendor/`, nicht auf einem CDN. Kein neuer `<script src="https://…">`,
  kein `import()` auf eine fremde URL.
* **Die App startet ohne Netz** und ist ohne Anmeldung sinnvoll nutzbar.
* **Digitale Funktionen in der App brauchen In-App-Purchase** (Apple 3.1.1). Bevor etwas
  an Pro/Bezahlung gebaut wird: `docs/STORE.md` lesen, Abschnitt 2.

→ Prüfliste und Stand: `docs/STORE.md` · Prüfer: Agent `store-check`

---

# 2. Projektgrundsätze

Die Kommunikation im gesamten Projekt läuft auf **Deutsch** — Antworten,
Code-Kommentare, Dokumentation, Commit-Messages.

Commit-Messages bewusst in ASCII: `geprueft`, `geaendert`, `aktualisiert`.

**Paddy's Mealplan** ist ein deutschsprachiger Wochen-Essensplaner. Die App ist eine
einzige Datei — `index.html` — mit HTML, CSS, JavaScript, Firebase-Anbindung, Meal-Daten,
Fotos, Impressum und Datenschutzerklärung. Ausgeliefert ohne Build-Prozess.

| Thema | Datei |
|---|---|
| Produktdefinition | `docs/PRODUCT.md` |
| Technische Architektur | `docs/ARCHITECTURES.md` |
| Design-System „Performance Dark" | `docs/DESIGN.md` |
| Test- und Verifikationsverfahren | `docs/TESTING.md` |
| Bekannte Fehler, Fallen, Workarounds | `docs/TROUBLESHOOTING.md` |
| Sicherheitsmodell | `docs/SECURITY.md` |
| Store-Anforderungen | `docs/STORE.md` |
| Wer prüft was | `docs/ABDECKUNG.md` |
| Deploy, Rollback, Notfälle | `docs/RUNBOOK.md` |
| Datenschutz-Pflichten (gitignored) | `docs/DATENSCHUTZ-INTERN.md` |
| Firebase-Einrichtung | `FIREBASE-SETUP.md` |

## Wichtige Arbeitsregel

**Code, Dokumentation und Projektstatus müssen nach einer Änderung konsistent sein.**
Dokumentation ist kein späterer Aufräumschritt, sondern Bestandteil der Änderung.

---

# 3. Dokumentation automatisch synchron halten

Wenn eine Änderung eine dokumentierte Produktregel, Architektur, Testmethode oder
Fehlerquelle betrifft, wird die Dokumentation **im selben Arbeitsschritt** aktualisiert.
Claude erkennt das selbstständig; der Nutzer muss nicht darum bitten.

| Datei | Aktualisieren bei Änderungen an |
|---|---|
| `docs/PRODUCT.md` | Produktphilosophie, Feature-Regeln, UX-Grundsätze, Markenstimme, Premium, Meal-Datenbank, bewussten Produktentscheidungen |
| `docs/ARCHITECTURES.md` | Architektur, Datenmodell, State, localStorage, Firebase, Auth, Cloud-Sync, Gruppenmodus, Firestore-Struktur, Rollen, Datenflüssen, Schnittstellen |
| `docs/DESIGN.md` | Tokens, Typografie, Theme, Makro-Darstellung, Abschnittsformen, Bewegungssprache |
| `docs/TESTING.md` | Testverfahren, neuen Prüfständen, Regressionen, Prüfregeln |
| `docs/TROUBLESHOOTING.md` | neuen Fallen, Bugs, Browser-/Firebase-/Sync-Fallen, Workarounds, behobenen historischen Fehlern |
| `docs/SECURITY.md` | Regeln, Bedrohungen, Geheimnissen, bewussten Kompromissen |
| `docs/STORE.md` | Bezahlung, Konto, Berechtigungen, Fremdcode, Store-Angaben |

Eine Änderung darf mehrere Dateien betreffen — das ist der Normalfall.

## Dokumentations-Gate

Vor Abschluss jeder Aufgabe prüfen, ob eine der obigen Dateien durch die Änderung falsch
oder widersprüchlich geworden ist. Wenn ja: im selben Arbeitsschritt korrigieren.

Bei nicht-trivialen Änderungen macht das der Agent **`doku-waechter`** — er nimmt den
`git diff` und nennt die betroffenen Stellen mit Zeilennummer.

Keine Dokumentation künstlich verändern, wenn die Änderung dort keine Relevanz hat.

---

# 4. Produktphilosophie

Paddy's Mealplan ist **kein Kalorien-Tracker**. Ein Tracker schaut zurück — *was habe ich
gegessen?* Paddy's Mealplan schaut nach vorne — *was werde ich essen?*

Jedes Feature muss mindestens einen echten Produktnutzen erzeugen: Zeit sparen,
Entscheidungen reduzieren, Ernährung vereinfachen, die Nutzererfahrung verbessern.

**Qualität vor Quantität. Einfachheit vor unnötigen Funktionen.** Technische Machbarkeit
allein ist kein Grund für ein Feature. „Wäre auch ganz nett" ist kein ausreichender Grund.

## Feature-Entscheidungsregel

Vor jeder neuen Funktion — auch vor einem bloßen Vorschlag — prüfen:

1. Spart sie Zeit?
2. Reduziert sie Entscheidungen des Nutzers?
3. Verbessert sie die Nutzererfahrung?
4. Passt sie zum Wochenplan-Konzept, zu Fitness/Abnehmen und zu `state.goal`?

Wird keine dieser Fragen sinnvoll mit Ja beantwortet: **Feature nicht umsetzen.** Nicht als
Kompromiss, nicht als abgespeckte Variante.

→ Ausführlich: `docs/PRODUCT.md`

---

# 5. UX-Grundsätze

Jeder Screen löst möglichst genau ein Problem.

* möglichst wenige Nutzerinteraktionen
* geringe kognitive Last
* klare nächste Aktion
* wenige statt viele Optionen
* keine unnötigen Erklärungen
* möglichst kurze Nutzerwege

Bei zwei technisch gleichwertigen Lösungen gewinnt die mit weniger Interaktionen.

---

# 6. Markenstimme und Textmenge

Paddy's Mealplan fühlt sich an wie ein erfahrener Trainingspartner: motivierend,
freundlich, modern, vertrauenswürdig. Nicht wie Behörden-, Medizin- oder komplizierte
Ernährungsfachsoftware.

**Die Marke hilft dem Nutzer. Sie bewertet ihn niemals.** Besonders bei Gewicht, Kalorien,
Zielen, Fortschritt, Fehlern und leeren Zuständen.

UI-Texte sind kurz, freundlich, motivierend, positiv, leicht verständlich. Zu vermeiden:
Behörden-Deutsch, Roboter-Sprache, unnötige Fachsprache, lange Erklärungen, wertende
Formulierungen, Slang („Bro", „Digga").

Buttons aktiv formulieren: `Meal anlegen`, nicht `Neues Meal wird angelegt`.
Fehlermeldungen sind freundlich und nicht anklagend. Erfolgsmeldungen dürfen motivieren.

**So wenig Text wie möglich.** Keinen Erklärungssatz schreiben, wenn die Information bereits
aus Frage, Label, Option, Beispiel oder Platzhalter hervorgeht. Rechtlich oder fachlich
notwendige Hinweise möglichst kompakt, wenn passend hinter `<details>`.

---

# 7. Design

**Jede neue oder geänderte UI wird im bestehenden Design „Performance Dark" umgesetzt.**
Kein eigener Stil, keine fremden Farbpaletten, keine externen Fonts, keine
Design-Neuerfindung.

Die Kurzfassung:

* Vorhandene CSS-Tokens verwenden (`--accent`, `--bg`, `--surface`, `--text`, `--border`,
  `--radius`, `--shadow`, `--fr`/`--mi`/`--ab` …), keine Werte hartkodieren, für die ein
  Token existiert.
* Nur System-Fonts: `var(--font-display)` für Headlines, `var(--font-body)` für Fließtext.
* Light **und** Dark pflegen — `@media (prefers-color-scheme: dark)` und
  `:root[data-theme=…]`.
* Makros immer als `kcal → KH → P → F`, in einer der **drei** erlaubten Formen. Keine
  vierte erfinden. Nie wieder `K` für Kohlenhydrate oder `Eiw.`/`Fett` in Wertzeilen.
* Abschnittsüberschriften bekommen `.sec-h`, keine eigenen Werte.
* Mehrstufige Abläufe verwenden die durchgängige Progress-Bar (`.wg-progress-bar`), die
  **nicht anklickbar** ist. Zurück nur über einen eigenen `Zurück`-Button.
* Ansichtswechsel folgen dem Schiebe-Schema; `MOTION`-Tokens sind die einzige Quelle für
  Dauer und Kurve; `reducedMotion()` immer berücksichtigen.
* **In einem Snap-Streifen niemals einen zweiten Scroll-Container anlegen.**

**→ Die vollständigen Regeln samt Begründungen: `docs/DESIGN.md`. Bei jeder Design-Änderung
zuerst dort nachsehen.**

## Design-Skills

Bei jeder Design-Änderung vorab berücksichtigen, in dieser Reihenfolge:

1. `ui-ux-pro-max:ui-ux-pro-max` (UI-Zustände, UX, A11y, Farben) bzw.
   `ui-ux-pro-max:design` (Branding, Logo, Banner)
2. `apple-design` (fluide Interaktion, Motion, Materialien)
3. `emil-design-eng` (Detailpolitur, Press-States)

**Empfehlungen auf Performance Dark mappen** — nie die Variablen, Farben oder Kurven der
Skills direkt übernehmen. Projekt-Tokens haben Vorrang.

Animations-Skills (`find-animation-opportunities`, `improve-animations`) nur, wenn Bewegung
tatsächlich Teil der Änderung ist.

---

# 8. Mobile

Mobile Darstellung ist Bestandteil **jeder** UI-Änderung, nicht ein späterer Schritt.

Breakpoints: `max-width: 720px` und `max-width: 560px`.
Bei Eingaben 16 px beibehalten, sonst zoomt iOS automatisch.

Relevante mobile Zustände tatsächlich prüfen, nicht nur Desktop.

⚠️ **Einen `@media`-Block nie mitten in einen bestehenden einfügen** — das hat am
16.08.2026 den 680-px-Block zerschnitten und die ganze mobile Ansicht lahmgelegt.

---

# 9. Keine Toolchain erfinden

Es gibt **kein** Node, PHP, npm, `package.json`, Bundler, Build, Test-Framework, Linter.
**Keine npm-Befehle erfinden.** Eine Änderung an `index.html` ist unmittelbar die fertige App.

Python ist vorhanden und wird für Hilfs- und Testskripte verwendet.

---

# 10. Lesen und Bearbeiten von `index.html`

Die Datei ist ~1,1 MB groß, 16.700 Zeilen, einzelne Zeilen über 12.000 Zeichen lang.

**Niemals die komplette Datei blind lesen.** Kein `cat`, keine überlangen Zeilen ungefiltert
in den Kontext.

Stattdessen: mit `Grep` die relevante Stelle suchen, nur diese mit Offset/Limit lesen.

Die Meal-Fotos liegen als 32 Dateien in `img/`, **nicht** mehr als Base64 in der Datei. Was
noch als `data:image;base64` vorkommt, sind Bilder des Nutzers aus `localStorage`/Firestore —
zur Laufzeit, nicht im Quelltext. Trifft man sie doch einmal an: über Skripte arbeiten, nie
durch den Kontext kopieren.

Wenn Code getestet werden soll: **niemals abtippen oder manuell nachbauen** — den echten
Code aus `index.html` ausschneiden.

---

# 11. Testen und Verifikation

**Nach jeder Änderung an JavaScript zuerst:**

```powershell
python syntax-check.py
```

Rund eine Sekunde. Ein Syntaxfehler beendet das gesamte App-Script — die Seite liefert
weiter HTTP 200, aber `#view` bleibt leer. Deshalb läuft der Syntax-Check **vor** allem
anderen. (Ein Hook erledigt das inzwischen automatisch, siehe Abschnitt 15.)

Die Verfahren gibt es als Skill:

| Skill | Wofür |
|---|---|
| `/smoke` | Startet die App, ist `#view` gefüllt? |
| `/pruefstand` | Ausschneide-Prüfstand für Funktionen hinter Login, Modal oder komplexem State |
| `/abnahme` | Abnahme am echten Cloud-Konto über `tools/cdp.py` |
| `/deploy` | Push, Verifikation, Rollback |

Für den Blick aufs Ganze vor einem größeren Commit:

```powershell
python tools/alle-pruefstaende.py
```

Achtung: Bei Prüfständen, die `OFFEN` von `REGRESSION` trennen, heißt „grün" dort nur
**keine Regression** — offene Punkte kann es trotzdem geben. Der Läufer weist das aus.

Zwei Regeln, die dabei nicht verhandelbar sind:

* **Getestet wird echter, ausgeschnittener Produktionscode** — kein Nachbau.
* **Ohne Gegenprobe zählt kein Ergebnis.** Derselbe Prüfstand muss gegen den alten Stand
  **durchfallen**, sonst misst er nicht das, was er zu messen vorgibt.

Wenn ein Test hängt: nicht automatisch annehmen, der Prüfstand sei kaputt. Ein Hänger kann
der Befund sein.

→ Ausführlich: `docs/TESTING.md` (Teil A: Verfahren, Teil B: Fallarchiv)

---

# 12. Firebase, Cloud-Sync und Security

Die App muss **auch ohne Firebase funktionieren**. Wenn `firebaseConfig` Platzhalter
enthält, das CDN blockiert wird oder die Initialisierung fehlschlägt, fällt sie auf den
lokalen Login zurück. Beide Modi — `authMode = "local"` und `"cloud"` — bleiben
funktionsfähig.

## Security — die eine Regel

> **Die Firestore Security Rules sind die einzige Sicherheitsgrenze. Alles andere ist
> Bequemlichkeit.**

UI-Sperren sind **keine** Sicherheitsgrenze; DevTools umgehen sie in Sekunden. Jede neue
Berechtigung wird **zuerst in den Regeln** durchgesetzt, dann im Client abgebildet.

* `allow read` ist **nicht** `allow get` — `read` umfasst `list`. Wo eine unerratbare ID der
  Schutz ist, gehört `allow get` hin und `list` ausgeschaltet.
* `firestore.rules` im Repo ist nur eine **Vorlage**. Verbindlich ist der in der
  Firebase-Konsole veröffentlichte Stand — der ist lokal nicht abrufbar. Das bei jeder
  Aussage über den Live-Zustand dazusagen.
* Die **Firebase-Web-Config in `index.html` ist kein Secret.** Web-Keys identifizieren das
  Projekt, sie autorisieren nichts. Nie als Leck behandeln.

→ Bedrohungsmodell, bewusste Kompromisse, Notfälle: `docs/SECURITY.md`

## Geheimnisse

Es gibt genau zwei echte Geheimnisse: den `OPENAI_API_KEY` in `.env` und den
GCP-Service-Account-Schlüssel des Cloudflare Workers (nur in den Cloudflare-Secrets).

* **Nie ausgeben** — nicht mit `cat`, nicht in eine Fehlermeldung, nicht in ein Protokoll.
* **Nie in einen Prüfstand oder ein Skript kopieren.** Skripte lesen sie aus der Umgebung.
* Steht ein Schlüssel einmal irgendwo, hilft nur **Rotation**. Löschen reicht nicht.

---

# 13. Daten und Datenschutz

Ein Meal speichert bei `by` **ausschließlich die UID** — nie Name, E-Mail oder andere
personenbezogene Daten. Der Name wird bei der Anzeige aus `groupMembers` aufgelöst.
E-Mail-Adressen gehören nicht in Gruppen-Mitgliederdokumente.

Bei Änderungen an Sharing, Sync, Gruppen, Datenfeldern, Löschlogik oder personenbezogenen
Daten: Rechtstexte gegen die tatsächliche Implementierung prüfen und die Agenten `anwalt`
und `datenschutz-technik` einsetzen.

Impressum und Datenschutzerklärung stehen in `index.html`. **Der Footer muss auch ohne
Anmeldung sichtbar bleiben**, das Impressum darf nicht hinter das Auth-Gate.

Die Rechtstexte enthalten konkrete technische Zusagen — eine Änderung am Verhalten kann
sie inhaltlich falsch machen.

→ Auftragsverarbeiter, Art. 30, TOM, Meldeweg: `docs/DATENSCHUTZ-INTERN.md`

---

# 14. Namensdualität

Sichtbar heißt die App **Paddy's Mealplan**, die sichtbare Entität heißt **Meal**.
Intern bleibt es bei `wochenkueche` und `recipe`:

```text
wochenkueche_v1 · wochenkueche_profile_v1 · app: "wochenkueche"
state.recipes · getRecipe · data-tab="recipes" · .rcard · .recipes
```

**Nicht „aufräumen".** Die internen Namen stecken in bestehenden Daten und in bereits
verschickten Sharing-Links. Eine Umbenennung bricht beides.

---

# 15. Bilder und Lizenzen

`photoFor(r)` verwendet die Priorität: eigenes Bild → Stichwort/`PHOTO_RULES` →
Kategorie/`CAT_PHOTO` → `PHOTOS.neutral`. Keine alten Emoji-/Gradient-Fallbacks wieder
einführen.

`PHOTOS` und `PHOTO_CREDITS` müssen deckungsgleich bleiben. Neue Bilder nur mit belegter
freier Lizenz: Lizenz prüfen, Quelle dokumentieren, `PHOTO_CREDITS` aktualisieren.
Ein Bild ohne Lizenznachweis ist ein rechtliches Risiko.

Bei Stichwort-Matching auf Teilwort-Kollisionen achten: `eis` steckt in `Rindfleisch`,
`reis` in `Preiselbeere`.

**Nährwerte nie schätzen** — vor jedem neuen Rezept `tools/rezept-makros.py` gegenrechnen.

---

# 16. Fremdcode unter `vendor/`

Firebase-SDK und ZXing liegen **lokal**, nicht auf einem CDN. Grund: Apple 2.5.2 und
Offline-Start (Abschnitt 1). Diese Entscheidung wird nicht zurückgedreht — auch nicht mit
dem Argument, ein CDN sei einfacher zu aktualisieren.

* Aktualisiert wird über `tools/firebase-vendor.py`, nicht von Hand. Version, Quelle
  und SHA-256 je Datei stehen in **`vendor/HERKUNFT.md`** — nach jedem Update dort
  nachtragen, sonst ist die Unversehrtheit beim nächsten Mal wieder unbelegbar.
* Ein Update **nur mit Anlass** — Sicherheitslücke oder konkreter Fehler. Es gibt keine
  Testsuite, die ein Update auffängt; eine höhere Versionsnummer ist kein Grund.
* Es gibt kein npm und kein Dependabot: **niemand merkt von selbst, wenn eine Bibliothek
  altert.** Dafür gibt es den Agenten `lieferkette`.
* Apache-2.0-Lizenzhinweise müssen mitgeliefert bleiben (siehe `LICENSE`).

---

# 17. Git und Deployment

Deployment ist ein Push auf `main`; GitHub Pages baut automatisch. Es gibt keinen Schritt
dazwischen.

```powershell
git push origin main
git ls-remote origin refs/heads/main   # muss mit...
git rev-parse HEAD                     # ...uebereinstimmen
```

**Nie `git add .`** Alles im Repo landet öffentlich, und Gelöschtes bleibt in der Historie.
Immer gezielt einzelne Pfade stagen. Ein Hook prüft das zusätzlich (Abschnitt 18), aber die
Regel gilt unabhängig davon.

Nicht öffentlich, deshalb gitignored: `plans/`, `ROADMAP.html`, `Fotos/`, `Marketing/`,
`Instagram/`, `.env`, `docs/DATENSCHUTZ-INTERN.md`, die zugekauften Skills.

**Vor jedem Push `/pushcheck`.** Er fährt `anwalt` und `website-security` auf Sonnet, dazu
`ux-reviewer` und `kvp` auf Haiku.

→ Rollback, Notfälle, Credential-Manager-Workaround: `docs/RUNBOOK.md` und `/deploy`

Lokaler Server: `powershell -NoProfile -File test-server.ps1` → `http://localhost:8000/`

---

# 18. Hooks — was automatisch läuft

In `.claude/settings.json`, Skripte unter `.claude/hooks/`. Sie greifen ohne Zutun:

| Hook | Wirkung |
|---|---|
| `commit-waechter.py` | **Blockiert** `git commit`, wenn Nichtöffentliches im Index liegt |
| `secrets-filter.py` | **Blockiert** Befehle, die `.env` ausgeben würden |
| `push-waechter.py` | **Fragt nach** bei `git push`, wenn `/pushcheck` für diesen Stand fehlt |
| `syntax-nach-edit.py` | Fährt `syntax-check.py` nach jeder Änderung an `index.html` |
| `wartung-erinnerung.py` | Meldet beim Sitzungsstart, wenn die Wartung überfällig ist |

Zusätzlich läuft `.github/workflows/pruefung.yml` bei jedem Push: Syntax und Secret-Scan.
Das ist die einzige Prüfung, die auch dann greift, wenn sie jemand vergisst.

Wird ein Hook zum Hindernis, ist das ein Befund — melden, nicht umgehen.

---

# 18a. Wartung — das Prüfsystem prüft sich selbst

**Ein Prüfer mit veralteten Fakten prüft das Falsche und meldet trotzdem „sauber".** Das ist
gefährlicher als gar keine Prüfung. Deshalb wird das Setup selbst regelmäßig geprüft.

Anlass war der Aufbautag: Das System war nach einem halben Tag an fünf Stellen falsch —
eine Produktentscheidung, ein geklärter Vertrag, korrigierte Zahlen. Über Monate passiert
das garantiert.

**Alle 30 Tage, drei Ebenen:**

```powershell
python tools/wartung-check.py          # mechanisch, Sekunden
```

Prüft Zahlen gegen die Wirklichkeit, tote Verweise, das Modell jedes Agenten gegen das,
was diese Datei verspricht, den Commit-Wächter in **beiden** Richtungen (blockiert er zu
wenig — oder zu viel?) — und die Falle, die schon zugeschlagen hat: **ein Agent ohne
`tools:`-Zeile hat ALLE Werkzeuge**, auch wenn seine Beschreibung „ändert nichts"
verspricht.

Was das Skript **nicht** kann: sehen, ob sich Recht, Store-Richtlinien oder die
Sicherheitslage von Fremdcode geändert haben. Dafür `anwalt`, `store-check` und
`lieferkette` mit ihrem Rechercheauftrag laufen lassen.

Danach `python tools/wartung-check.py --setze` — das datiert den Stand neu und bringt den
Erinnerungs-Hook zum Schweigen.

**Monatlich läuft dieselbe Prüfung zusätzlich in der Cloud** (Routine „Monatliche
Wartungsprüfung", 1. des Monats), damit sie auch dann stattfindet, wenn wochenlang niemand
das Projekt öffnet. Sie ändert nichts und berichtet nur — und sie sieht **nur, was gepusht
ist**.

---

# 18b. Abdeckung — hat jeder Bereich einen Prüfer?

Abschnitt 18a fragt: *Sind die Fakten der Prüfer noch aktuell?* Hier ist die andere Frage:
**Gibt es für alles überhaupt einen Prüfer?**

Das ist keine Wortklauberei. `wartung-check.py` prüft Konsistenz zwischen Dingen, **die es
gibt**. Ein Bereich **ohne** Prüfer fällt ihm nie auf — er kennt nur die Agenten, die
existieren. Käme ein Marketing-Bereich in die App, meldete das ganze System weiter „keine
Befunde": Es weiß nicht, dass es etwas nicht weiß.

```powershell
python tools/abdeckung.py              # Bericht
python tools/abdeckung.py --gegenprobe # wuerde sie eine Luecke ueberhaupt bemerken?
```

Das Register steht in **`docs/ABDECKUNG.md`**. Erkannt werden vier Arten von Bereichen:
Pfade (`git ls-files`), Dateien in `docs/`, **Reiter der App** (`data-tab="…"`) und externe
Verbindungen. Läuft mit in `wartung-check.py`, im Sitzungsstart-Hook und in der
Monatsroutine.

## Die Regel, die nicht vom Skript abhängt

**Entsteht ein neuer Produktbereich, gehört die Frage nach seinem Prüfer zur Änderung —
nicht in einen späteren Aufräumschritt.** Das Skript ist das Netz darunter, nicht der Plan.

Meldet es eine Lücke, sind drei Wege richtig — und einer ist falsch:

1. Gehört zu einem bestehenden Prüfer → Zeile in `docs/ABDECKUNG.md` Abschnitt 3–5.
2. Braucht wirklich einen neuen → **Agenten entwerfen und dem Nutzer zur Abnahme vorlegen.**
   Nie still anlegen.
3. Braucht bewusst keinen → Zeile in Abschnitt 6, **mit Begründung**.

**Falsch ist, eine Kennung einzutragen, damit Ruhe ist.** Das schaltet die Prüfung für
diesen Bereich dauerhaft ab, und niemand sieht es je wieder.

> **Ein Prüfer, den niemand geprüft hat, meldet „sauber" — und man glaubt ihm.** Genau das
> ist am 26.08. und am 27.08.2026 je einmal passiert (`docs/TROUBLESHOOTING.md` §119, §123).
> Deshalb wird ein neuer Agent **abgenommen**, bevor er scharf geht.

---

# 19. Prüf-Agenten

Acht Agenten in `.claude/agents/`. Sie ändern **nie** etwas, sie melden.

**Vor jedem Push, über `/pushcheck`:**

| Agent | Modell | Prüft |
|---|---|---|
| `website-security` | sonnet | Geheimnisse, personenbezogene Daten, XSS, Rules, `sw.js`, Worker, `vendor/`, Historie |
| `anwalt` | sonnet | Rechtstext gegen Code |
| `ux-reviewer` | haiku | Übersichtlichkeit geänderter UI (ruft vorher `ui-ux-pro-max`) |
| `kvp` | haiku | Fitness-/Wochenplan-Bezug, Design, Mobile, Bedienbarkeit, Wartbarkeit, Sync |

Die beiden ersten laufen **nicht** auf Haiku.

**Nach Auslöser, alle auf sonnet:**

| Agent | Auslöser |
|---|---|
| `store-check` | Pro/Bezahlung, Konto, Login, Kamera, `vendor/`, Manifest |
| `lieferkette` | alles unter `vendor/`, neue externe Verweise — und regelmäßig ohne Anlass |
| `datenschutz-technik` | neuer Dienst, neues Datenfeld, Sharing, Gruppen, Löschlogik |
| `doku-waechter` | jede nicht-triviale Änderung an `index.html` |

Nicht für jede triviale Textkorrektur alle Agenten starten. Bei sicherheits-, daten-,
sync-, sharing-, store- oder rechtlich relevanten Änderungen aber sehr wohl.

**🔴-Funde vor dem Melden am echten Code gegenprüfen** — Fehlalarme kommen vor.

Ein neu angelegter Agent ist in einer bereits laufenden Sitzung eventuell noch nicht als
`subagent_type` verfügbar. Dann Sitzung neu starten.

---

# 20. Arbeitsweise

## Modellwahl

Größere Pläne von **Sonnet** umsetzen lassen, danach mit **Opus** gegenprüfen. Bei
komplexen Aufgaben von selbst vorschlagen, welches Modell sinnvoll ist.

## Pläne

Nach `ExitPlanMode` den Plan aus `.claude/plans` nach `plans/` kopieren, mit sprechendem
Namen. Umgesetzte und dokumentierte Pläne direkt löschen — ohne Rückfrage.

## `ROADMAP.html`

Die private visuelle Projektübersicht. Nach jedem abgeschlossenen Feature und jedem Push
prüfen und bei Bedarf aktualisieren: Karte verschieben, Fortschritt, Balken, Datum,
Commit-Hash, neue Risiken als `<p class="warn">`.

Bleibt in `.gitignore`. **Nie committen.**

---

# 21. Ablauf bei jeder Änderung

## Vorher

1. Aufgabe vollständig verstehen.
2. Relevanten Code mit `Grep` suchen, nur benötigte Ausschnitte lesen.
3. Relevante `docs/*.md` lesen — über das Register am Dateikopf, nicht am Stück.
4. Bei UI: `docs/DESIGN.md` und die drei Design-Skills.
5. Bei bekannten Problemfeldern: `docs/TROUBLESHOOTING.md`.

## Währenddessen

* Bestehende Architektur respektieren, bestehende Tokens verwenden.
* Keine unnötigen neuen Abstraktionen.
* Keine Funktion entfernen, nur weil sie alt aussieht.
* Keine internen Namen ohne Migrationsgrund umbenennen.
* Keine Security nur über UI lösen, keine Daten unnötig duplizieren.

## Danach

1. `python syntax-check.py`, dann `/smoke`.
2. Isolierter Prüfstand, wenn die Funktion es erfordert — mit Gegenprobe.
3. Bei UI: mobile, Light und Dark, A11y.
4. Bei Cloud-/Sync-Änderungen: Sync-Szenarien, notfalls `/abnahme`.
5. Rechtstexte prüfen, wenn betroffen.
6. Passende Agenten einsetzen.
7. Dokumentation aktualisieren, `ROADMAP.html` bei Bedarf.
8. `git diff` auf unbeabsichtigte Änderungen prüfen.
9. Erst danach committen. Nach dem Push Remote-Commit verifizieren.

---

# 22. Minimalprinzip

**Ändere nur, was für die Aufgabe notwendig ist.**

Keine ungefragten Refactorings, Umbenennungen, Design-Neuentwürfe, Architekturumbauten,
Dependency-Wechsel, Toolchain-Einführungen oder „Aufräumarbeiten".

Wird ein Problem außerhalb des Auftrags entdeckt: nicht ungefragt umbauen, sondern
dokumentieren und den Nutzer kurz darauf hinweisen.

**Ausnahme:** Gefährdet das Problem Sicherheit, Datenintegrität oder die korrekte Umsetzung
der aktuellen Aufgabe, muss es vor Abschluss berücksichtigt werden.

---

# 23. Definition of Done

Eine Aufgabe ist abgeschlossen, wenn die Funktion korrekt umgesetzt ist, nichts
Bestehendes beschädigt wurde, die relevanten Tests und UI-Zustände geprüft sind, Design,
Mobile und A11y berücksichtigt wurden, Security und Rechtstexte bei Relevanz geprüft sind,
die betroffene Dokumentation aktualisiert ist, `ROADMAP.html` stimmt und der `git diff`
gesichtet wurde.

**Code, Dokumentation und Projektstatus beschreiben danach denselben Stand.**

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

**Nicht nur Code schreiben. Das Projekt als Ganzes konsistent halten.**

> Produkt → UX → Design → Architektur → Daten → Security → Store → Tests → Dokumentation → ROADMAP

Betrifft eine Änderung einen dieser Bereiche tatsächlich, wird er ebenfalls aktualisiert
und geprüft.
