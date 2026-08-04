# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 1. Projektgrundsätze

Die Kommunikation im gesamten Projekt läuft auf Deutsch.

Das gilt für:

* Antworten
* Code-Kommentare
* Dokumentation
* Commit-Messages

Commit-Messages werden bewusst in ASCII geschrieben:

* `geprueft` statt `geprüft`
* `geaendert` statt `geändert`
* `aktualisiert` statt Sonderzeichen

## Projekt

**Paddy's Mealplan** ist ein deutschsprachiger Wochen-Essensplaner.

Die App ist aktuell eine einzige:

`index.html`

Sie enthält:

* HTML
* CSS
* JavaScript
* Firebase-Anbindung
* Meal-Daten
* Fotos bzw. Foto-Metadaten
* Impressum
* Datenschutzerklärung

Die App wird ohne Build-Prozess direkt ausgeliefert.

Produktdefinition:
→ `docs/PRODUCT.md`

Technische Architektur:
→ `docs/ARCHITECTURES.md`

Test- und Verifikationsverfahren:
→ `docs/TESTING.md`

Bekannte Fehler, Fallen und Workarounds:
→ `docs/TROUBLESHOOTING.md`

Firebase-Einrichtung:
→ `FIREBASE-SETUP.md`

## Wichtige Arbeitsregel

**Code, Dokumentation und Projektstatus müssen nach einer Änderung konsistent sein.**

Dokumentation ist kein späterer Aufräumschritt, sondern Bestandteil der Änderung.

---

# 2. Dokumentation automatisch synchron halten

**Wenn eine Änderung eine dokumentierte Produktregel, Architektur, Testmethode oder bekannte Fehlerquelle betrifft, muss die entsprechende Dokumentation im selben Arbeitsschritt aktualisiert werden.**

Claude soll das selbstständig erkennen. Der Nutzer muss nicht extra sagen „aktualisiere die Dokumentation“.

## Zuordnung

### `docs/PRODUCT.md`

Aktualisieren bei Änderungen an:

* Produktphilosophie
* Produktidentität
* Feature-Regeln
* UX-Grundsätzen
* Markenstimme
* Premium-Philosophie
* langfristiger Produktvision
* Meal-Datenbank-Philosophie
* bewussten Produktentscheidungen

### `docs/ARCHITECTURES.md`

Aktualisieren bei Änderungen an:

* Architektur
* Datenmodell
* State
* localStorage
* Firebase
* Authentication
* Cloud Sync
* Gruppenmodus
* Firestore-Struktur
* Rollen
* Datenflüssen
* technischen Schnittstellen
* wichtigen technischen Abhängigkeiten
* dauerhaften Architekturentscheidungen

### `docs/TESTING.md`

Aktualisieren bei Änderungen an:

* Testverfahren
* Verifikationsverfahren
* neuen Testtechniken
* neuen Testanforderungen
* Browser-/API-Testmethoden
* neuen Regressionstests
* neuen Prüfregeln

### `docs/TROUBLESHOOTING.md`

Aktualisieren bei:

* neu entdeckten Fehlerquellen
* wichtigen Bugs
* Browser-Fallen
* Firebase-Fallen
* Sync-Fallen
* Workarounds
* Problemen, die bei zukünftigen Änderungen erneut auftreten könnten
* wichtigen historischen Fehlern, deren Ursache weiterhin relevant ist

Wenn eine Änderung mehrere Bereiche betrifft, dürfen und sollen mehrere Dokumentationsdateien aktualisiert werden.

## Dokumentations-Gate

**Vor Abschluss jeder Aufgabe prüfen:**

* Ist `docs/PRODUCT.md` noch korrekt?
* Ist `docs/ARCHITECTURES.md` noch korrekt?
* Ist `docs/TESTING.md` noch korrekt?
* Ist `docs/TROUBLESHOOTING.md` noch korrekt?
* Wurde durch die Änderung etwas veraltet oder widersprüchlich?

Wenn ja, Dokumentation vor Abschluss der Aufgabe aktualisieren.

**Code und Dokumentation müssen nach Abschluss derselben Änderung denselben Stand beschreiben.**

Keine Dokumentation künstlich verändern, wenn die Änderung dort keine Relevanz hat.

---

# 3. Produktphilosophie

Paddy's Mealplan ist **kein Kalorien-Tracker**.

Ein Tracker schaut zurück:

> Was habe ich gegessen?

Paddy's Mealplan schaut nach vorne:

> Was werde ich essen?

Die App soll Entscheidungen abnehmen und Planung vereinfachen.

Jedes Feature muss mindestens einen echten Produktnutzen erzeugen:

* Es spart Zeit.
* Es reduziert Entscheidungen.
* Es vereinfacht Ernährung.
* Es verbessert die Nutzererfahrung.

**Qualität vor Quantität. Einfachheit vor unnötigen Funktionen.**

Technische Machbarkeit allein ist kein Grund für ein Feature.

„Wäre auch ganz nett“ ist kein ausreichender Grund.

Die ausführliche Produktdefinition steht in:

→ `docs/PRODUCT.md`

---

# 4. Feature-Entscheidungsregel

Vor jeder neuen Funktion — auch vor einem bloßen Vorschlag — prüfen:

1. Spart sie Zeit?
2. Reduziert sie Entscheidungen des Nutzers?
3. Verbessert sie die Nutzererfahrung?
4. Passt sie zu Paddy's Mealplan, insbesondere Wochenplan-Konzept, Fitness/Abnehmen und `state.goal`?

Wenn keine dieser Fragen sinnvoll mit Ja beantwortet wird:

**Feature nicht umsetzen.**

Nicht als Kompromiss und nicht als abgespeckte Variante.

---

# 5. UX-Grundsätze

Jeder Screen soll möglichst genau ein Problem lösen.

Grundprinzipien:

* möglichst wenige Nutzerinteraktionen
* geringe kognitive Last
* klare nächste Aktion
* wenige statt viele Optionen
* keine unnötigen Erklärungen
* möglichst kurze Nutzerwege

Wenn zwei technisch gleichwertige Lösungen existieren, gewinnt diejenige mit weniger notwendigen Nutzerinteraktionen.

---

# 6. Markenstimme

Paddy's Mealplan soll sich wie ein erfahrener Trainingspartner anfühlen:

* motivierend
* freundlich
* modern
* vertrauenswürdig

Nicht wie:

* Behördensoftware
* Medizinsoftware
* komplizierte Ernährungs-Fachsoftware

**Die Marke hilft dem Nutzer. Sie bewertet ihn niemals.**

Das gilt besonders für:

* Gewicht
* Kalorien
* Ziele
* Fortschritt
* Fehler
* Fehlermeldungen
* leere Zustände

## UI-Texte

Alle Texte sind:

* kurz
* freundlich
* motivierend
* modern
* positiv
* leicht verständlich

Vermeiden:

* Behörden-Deutsch
* Roboter-Sprache
* unnötige Fachsprache
* lange Erklärungen
* wertende Formulierungen
* Slang wie „Bro“, „Digga“ usw.

Buttons aktiv formulieren.

Gut:

`Meal anlegen`

Nicht:

`Neues Meal wird angelegt`

Fehlermeldungen sind freundlich und nicht anklagend.

Erfolgsmeldungen dürfen motivierend sein.

---

# 7. Textmenge

**So wenig Text wie möglich.**

Keinen zusätzlichen Erklärungssatz schreiben, wenn die Information bereits aus Frage, Label, Option, Beispiel oder Platzhalter hervorgeht.

Vor jedem neuen Hilfetext prüfen:

* Ist die Information bereits offensichtlich? → Text weglassen.
* Entsteht ohne Text eine echte fachliche/technische Lücke? → kurz erklären.
* Rechtlich oder fachlich notwendiger Hinweis? → möglichst kompakt und, wenn passend, hinter `<details>`.

Keine UI mit Erklärtext überladen.

---

# 8. Verbindliche Design-Vorgabe: „Performance Dark“

**Jede neue oder geänderte UI muss im bestehenden Design „Performance Dark“ umgesetzt werden.**

Kein eigener Stil.

Keine fremden Farbpaletten.

Keine externen Fonts.

Keine Design-Neuerfindung.

Neue Elemente müssen sich in das bestehende System einfügen.

## Bestehende CSS-Tokens verwenden

Für Farben, Flächen, Typografie und Form bevorzugt die bestehenden CSS-Variablen aus `index.html` verwenden:

```text
--font-display
--font-body

--accent
--accent-strong

--bg
--surface
--surface-2

--text
--text-muted

--border
--border-strong

--radius
--radius-sm

--shadow
--maxw

--fr
--mi
--ab
```

Keine Werte unnötig hartkodieren, wenn ein vorhandener Token dafür existiert.

## Typografie

Headlines/Display:

`var(--font-display)`

Fließtext:

`var(--font-body)`

Nur System-Fonts.

Kein externes Font-CDN.

## Farbe

Akzent:

`--accent`

Rot ist der zentrale Akzent.

Light- und Dark-Werte immer berücksichtigen.

## Theme

Bestehende Light-/Dark-Mechanik erhalten.

Insbesondere:

* `@media (prefers-color-scheme: dark)`
* `:root[data-theme=…]`

Nicht nur einen Theme-Zustand pflegen.

## Form

Bestehende Werte für:

* Radius
* Shadow
* maximale Breite

verwenden.

## Markencharakter

Die UI soll sportlich und leistungsorientiert wirken.

Slogan:

**Plan it. Cook it. Lift it.**

Logo:

* rund
* roter Kreis

Wenn eine Designentscheidung nicht durch bestehende Tokens abgedeckt ist:

1. vorhandene Tokens prüfen
2. wenn nötig neuen Token im bestehenden Stil anlegen
3. nicht daneben einen eigenen Stil bauen

---

# 9. Design-Skills

**Bei jeder Design-Änderung müssen alle drei Design-Skills vorab berücksichtigt werden.**

Reihenfolge:

### 1. ui-ux-pro-max

Für:

* UI-Zustände
* UX
* A11y
* Farben
* Branding
* Logo
* Banner

Verwenden:

`ui-ux-pro-max:ui-ux-pro-max`

und bei Branding:

`ui-ux-pro-max:design`

### 2. apple-design

Für:

* fluide Interaktion
* Motion
* Springs
* Materialien
* Wayfinding
* Agency

### 3. emil-design-eng

Für:

* Detailpolitur
* Animationsentscheidungen
* frequenzbasierte Animationen
* Press-States

## Wichtig

Die Empfehlungen der Skills werden auf **Performance Dark** gemappt.

Nicht die Variablen, Farben, Kurven oder sonstigen Design-Systeme der Skills direkt übernehmen.

Bestehende Projekt-Tokens haben Vorrang.

Animations-Skills wie:

* `find-animation-opportunities`
* `improve-animations`

nur verwenden, wenn Bewegung tatsächlich Teil der Änderung ist.

---

# 10. Mehrstufige Abläufe

**Jeder mehrstufige Ablauf verwendet die bestehende durchgängige Progress-Bar.**

Standard:

`.wg-progress-bar`

Darstellung:

* visueller Balken
* anteilige Füllung
* kurzer Text darunter
* Beispiel: `Schritt 3 von 4 · Training`

Die Progress-Bar ist **nicht anklickbar**.

Kein Sprung zu früheren Schritten durch Anklicken des Balkens.

Zurück geht ausschließlich über einen separaten:

`Zurück`

-Button.

Keine nummerierten Schritt-Kacheln oder alten Schritt-Buttons wieder einführen.

## `initCarousel()`

Wenn ein Ablauf auf `initCarousel()` basiert, kann die Funktion weiterhin eine feste Anzahl Kind-Elemente als internes Gerüst benötigen.

Diese Platzhalter nicht entfernen, nur weil sie nicht sichtbar sind.

Sie müssen aus Tastatur-/Screenreader-Fokus genommen werden:

```html
aria-hidden="true"
tabindex="-1"
```

Sichtbar ist ausschließlich die durchgängige Progress-Bar.

---

# 11. Schiebe-Schema für Ansichtswechsel

**Jeder Wechsel zwischen gleichrangigen Ansichten folgt dem Schema der mobilen Tagesleiste** (`.daybar`/`.db-ind`, `initCarousel()`):

* Segmented Control mit gleitender Pille statt harter Umschaltung.
* gerichtete Enter-Bewegung beim Inhaltswechsel.
* `MOTION`-Tokens (`--dur-fast`/`--dur-base`/`--dur-slow`/`--ease-out`) als einzige Quelle für Dauer und Kurve.
* `reducedMotion()` immer berücksichtigt — Überblendung bleibt, Richtung entfällt.

Wischen (echtes `scroll-snap`) nur dort, wo es keinen verschachtelten horizontalen Scroller erzeugt. Bei Woche und Tabs bewusst kein Wischen: alle Ansichten gleichzeitig im DOM würde einen horizontalen Scroller im horizontalen Scroller ergeben, auf Touch gewinnt immer der innere, und `overscroll-behavior-x: contain` unterbindet die Weitergabe zusätzlich absichtlich. Bei den Tabs käme auf iOS die Zurück-Wischgeste am linken Rand dazu. Dort wird nur die Optik und Bewegungssprache angeglichen, nicht die Geste.

`initCarousel()` ist die gemeinsame Quelle für die scroll-gekoppelte Pille (`.db-ind`, in `.daybar` und `.wgbar`). `slideIn(el, dir)` ist der gemeinsame Enter-Helfer für gerichtete Inhaltswechsel (Wochenwechsel, Tab-Wechsel). `.week-switch` braucht eine eigene WAAPI-Pille (`syncWeekSwitchPill()`), weil ihr Markup bei jedem `render()` per `view.innerHTML` neu gebaut wird — eine CSS-`transition` würde dort nie greifen, siehe `docs/TROUBLESHOOTING.md`.

---

# 12. Keine Toolchain erfinden

Es gibt aktuell:

* kein Node
* kein PHP
* kein npm
* kein `package.json`
* keinen Bundler
* keinen Build-Prozess
* kein Test-Framework
* keinen Linter

**Keine npm-Befehle erfinden.**

Eine Änderung an `index.html` ist unmittelbar die fertige App.

Python ist vorhanden und wird ausschließlich für Hilfs-/Testskripte verwendet.

Die ausführliche technische Beschreibung steht in:

→ `docs/ARCHITECTURES.md`

---

# 13. Lesen und Bearbeiten von `index.html`

`index.html` ist sehr groß und enthält Base64-Fotos.

**Niemals die komplette Datei blind lesen.**

Nicht:

* `cat`
* komplette Datei in den Kontext laden
* riesige Base64-Zeilen unnötig lesen
* Base64 über Chat-/Kontextgrenzen kopieren

Stattdessen:

1. mit `Grep` nach dem relevanten Code suchen
2. nur die benötigten Stellen lesen
3. gezielt mit Offset/Limit arbeiten
4. bei Base64 möglichst über Skripte arbeiten

Wenn Code getestet werden soll:

**niemals abtippen oder manuell kopieren.**

Den tatsächlichen Code aus `index.html` ausschneiden.

---

# 14. Testen und Verifikation

Es gibt aktuell keine klassische JS-Testtoolchain.

Die Verifikation erfolgt über Browser und isolierte Tests.

Vollständige Teststrategie:

→ `docs/TESTING.md`

## Smoke-Test

Microsoft Edge headless verwenden.

Beispiel:

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --virtual-time-budget=9000 `
  --user-data-dir="<scratchpad>\edge-profile" `
  --dump-dom "file:///C:/Users/Paddy/Documents/Paddys%20Mealplan/index.html" > dump.html
```

Der Smoke-Test prüft insbesondere, ob das App-JavaScript überhaupt läuft.

Ein HTTP-200 reicht nicht.

Wenn ein JS-Syntaxfehler das Script beendet:

* statischer Header kann sichtbar bleiben
* `#view` bleibt leer

Deshalb `#view` auf tatsächlichen Inhalt prüfen.

---

# 15. Ausschneide-Prüfstand

Der Ausschneide-Prüfstand ist die zentrale Methode für Funktionen hinter Login, Modals oder komplexem State.

Vorgehen:

1. relevanten Code mit Markern in `index.html` finden
2. direkt aus der Originaldatei ausschneiden
3. isolierte HTML-Datei im Scratchpad erzeugen
4. fehlende Helfer gezielt stubben
5. headless ausführen
6. Ergebnis nach jedem Prüfschritt ausgeben

**Nicht abtippen. Nicht manuell nachbauen.**

Getestet werden soll möglichst exakt die Produktionsimplementierung.

Prüfbar sind beispielsweise:

* reine Logik
* Suchranking
* Namensauflösung
* Tabellen
* externe APIs
* Browser-APIs
* State-Management
* Kamera
* Layout
* responsive Darstellung
* Light/Dark Theme

Wenn ein Test hängt:

**Nicht automatisch annehmen, dass der Prüfstand kaputt ist.**

Ein Hänger kann ein echter Befund sein.

Details:

→ `docs/TESTING.md`

---

# 16. Dokumentationspflicht nach Änderungen

Nach einer Änderung nicht nur den Code betrachten.

Prüfen:

### Produkt

Hat sich eine Produktentscheidung verändert?

→ `docs/PRODUCT.md`

### Architektur

Hat sich technische Struktur, Datenfluss, State, Firebase, Sync oder Datenmodell verändert?

→ `docs/ARCHITECTURES.md`

### Tests

Ist eine neue Testmethode oder Regression relevant?

→ `docs/TESTING.md`

### Troubleshooting

Wurde eine neue Falle entdeckt oder ein historischer Fehler behoben?

→ `docs/TROUBLESHOOTING.md`

Wenn ja:

**Dokumentation im selben Arbeitsschritt aktualisieren.**

---

# 17. Firebase und Cloud-Sync

Die App muss auch ohne Firebase funktionieren.

Wenn:

* `firebaseConfig` Platzhalter enthält
* Firebase-CDN blockiert wird
* Cloud-Initialisierung fehlschlägt bzw. timeoutet

muss die App auf den lokalen Login zurückfallen.

Die beiden Modi:

```text
authMode = "local"
authMode = "cloud"
```

müssen funktionsfähig bleiben.

Technische Details:

→ `docs/ARCHITECTURES.md`

Bekannte Fallen:

→ `docs/TROUBLESHOOTING.md`

---

# 18. Security-Regeln

UI-Sperren sind **keine Sicherheitsgrenze**.

DevTools können UI-Sperren umgehen.

Die tatsächliche Zugriffskontrolle erfolgt durch Firestore Security Rules.

Besonders wichtig:

* Rollen nicht nur clientseitig absichern
* Firestore Rules als tatsächliche Security Boundary betrachten
* `allow read` nicht unbewusst verwenden, wenn nur `get` erlaubt sein soll
* personenbezogene Daten minimieren

`firestore.rules` im Repository ist nur eine Vorlage.

Verbindlich ist der veröffentlichte Stand in der Firebase Console.

Bei Aussagen über den Live-Regelstand immer berücksichtigen, dass dieser lokal nicht zuverlässig abrufbar ist.

---

# 19. Firebase-Konfiguration

Die Firebase-Web-Konfiguration in `index.html` ist kein Secret.

Firebase-Web-Keys identifizieren das Projekt.

Sie autorisieren nicht automatisch Zugriff.

Sicherheit entsteht durch:

* Authentication
* Authorized Domains
* Firestore Security Rules

**Die `firebaseConfig` nicht als geleaktes Geheimnis behandeln.**

---

# 20. Daten und Datenschutz

Ein Meal speichert bei `by` ausschließlich die UID.

Nicht speichern:

* Name
* E-Mail-Adresse
* unnötige personenbezogene Daten

Der Name wird bei der Anzeige aus `groupMembers` aufgelöst.

E-Mail-Adressen gehören nicht in Gruppen-Mitgliederdokumente.

Grund:

* weniger personenbezogene Daten
* einfachere Löschung
* keine redundante Speicherung
* keine Nachpflege in vielen Meal-Dokumenten

Änderungen an Datenfeldern können Auswirkungen auf die Datenschutzerklärung haben.

Bei Änderungen an:

* Sharing
* Sync
* Gruppen
* Datenfeldern
* Löschlogik
* personenbezogenen Daten

Rechtstexte gegen tatsächliche Implementierung prüfen.

---

# 21. Namensdualität

Sichtbar heißt die App:

**Paddy's Mealplan**

Die sichtbare Entität heißt:

**Meal**

Intern bleibt es bei:

* `wochenkueche`
* `recipe`

Beispiele:

```text
wochenkueche_v1
wochenkueche_profile_v1
app: "wochenkueche"
state.recipes
getRecipe
data-tab="recipes"
.rcard
.recipes
```

**Nicht „aufräumen“.**

Die internen Namen sind Teil bestehender Daten und bestehender Sharing-Links.

Eine Umbenennung kann gespeicherte Daten und alte Links brechen.

---

# 22. Bilder und Lizenzen

`photoFor(r)` verwendet die bestehende Priorität:

1. eigenes Bild
2. Stichwort / `PHOTO_RULES`
3. Kategorie / `CAT_PHOTO`
4. `PHOTOS.neutral`

Keine alten Emoji-/Gradient-Fallbacks wieder einführen.

`PHOTOS` und `PHOTO_CREDITS` müssen deckungsgleich bleiben.

Neue Bilder nur mit belegter freier Lizenz.

Bei jedem neuen Bild:

1. Lizenz prüfen
2. Quelle dokumentieren
3. `PHOTO_CREDITS` aktualisieren
4. sicherstellen, dass `PHOTOS` und `PHOTO_CREDITS` denselben Schlüssel besitzen

Ein Bild ohne korrekten Lizenznachweis ist ein relevantes rechtliches Risiko.

Bei Stichwort-Matching auf Teilwort-Kollisionen achten.

Beispielsweise:

* `eis` steckt in `Rindfleisch`
* `reis` steckt in `Preiselbeere`

---

# 23. Rechtstexte

Impressum und Datenschutzerklärung befinden sich in `index.html`.

Der Footer muss auch ohne Anmeldung sichtbar bleiben.

Das Impressum darf nicht hinter das Auth-Gate verschoben werden.

Die Rechtstexte enthalten konkrete technische Zusagen.

Deshalb gilt:

**Änderungen an Sharing, Sync, Gruppen, Datenfeldern oder Löschlogik können die Rechtstexte inhaltlich verändern.**

Bei solchen Änderungen:

* tatsächliche Implementierung prüfen
* Rechtstexte prüfen
* gegebenenfalls `website-security` und `anwalt` einsetzen

Der Agent `anwalt` ersetzt keine Rechtsberatung.

---

# 24. Prüf-Agenten

Unter:

`.claude/agents/`

existieren projektspezifische Agenten.

## `website-security`

Prüft insbesondere:

* Secrets
* personenbezogene Daten
* XSS
* Sicherheitsprobleme
* Git-Historie

Einsetzen, wenn ein Dienst, Datenfeld, Auth-, Sharing- oder Cloud-Verhalten verändert wurde.

## `anwalt`

Prüft:

* Rechtstexte
* technische Zusagen
* Übereinstimmung zwischen Code und Datenschutzerklärung/Impressum

Einsetzen bei relevanten Änderungen an:

* Daten
* Sharing
* Sync
* Gruppen
* Löschung
* Auth
* personenbezogenen Informationen

Keine Rechtsberatung.

## `kvp`

Prüft den `git diff`.

Reihenfolge der Prüfung:

1. Passt die Änderung zum Fitness-/Abnehmen-Kontext?
2. Passt sie zum Wochenplan-Konzept?
3. Passt sie zu `state.goal` und Makro-Logik?
4. Design-Konformität
5. Mobile
6. Bedienbarkeit
7. Wartbarkeit
8. Sync
9. allgemeine Verbesserung

`kvp` ändert bewusst nichts.

## Agenten nicht unnötig einsetzen

Nicht für jede triviale Textkorrektur alle Agents starten.

Bei sicherheits-, daten-, sync-, sharing- oder rechtlich relevanten Änderungen sind die entsprechenden Agents jedoch einzusetzen.

Ein neu angelegter Agent kann in einer bereits laufenden Session eventuell noch nicht als `subagent_type` verfügbar sein.

Dann:

* Session neu starten
* oder einen geeigneten Agenten die entsprechende `.md` lesen lassen

---

# 25. ROADMAP.html

Im Projektordner liegt:

`ROADMAP.html`

Sie ist die private visuelle Projektübersicht.

Sie enthält unter anderem:

* erledigte Features
* nächste Features
* spätere Features
* offene Leitplanken
* Risiken
* Fortschritt

## Automatische Pflege

**Nach jedem abgeschlossenen Feature, jeder relevanten Entscheidung und jedem Push muss die ROADMAP geprüft und bei Bedarf aktualisiert werden.**

Wenn relevant:

* Karte nach „Erledigt und live“ verschieben
* Fortschrittszähler aktualisieren
* Balkenbreite aktualisieren
* Datum aktualisieren
* Commit-Hash aktualisieren
* neue offene Risiken als `<p class="warn">` ergänzen

Die ROADMAP ist keine öffentliche Produktdatei.

Sie bleibt in `.gitignore`.

**Nie committen.**

---

# 26. Mobile

Mobile Darstellung ist Bestandteil jeder UI-Änderung.

Relevante Breakpoints:

```text
max-width: 720px
max-width: 560px
```

Bei Eingaben 16 px beibehalten, um iOS-Auto-Zoom zu vermeiden.

Bei UI-Änderungen relevante mobile Zustände tatsächlich prüfen.

Nicht nur Desktop testen.

---

# 27. Lokaler Server

Für lokale Tests steht zur Verfügung:

```powershell
powershell -NoProfile -File test-server.ps1
```

Erreichbar unter:

```text
http://localhost:8000/
```

---

# 28. Deployment

Deployment erfolgt durch Push auf `main`.

```powershell
git push origin main
```

GitHub Pages baut automatisch.

Nach Push den Erfolg überprüfen:

```powershell
git ls-remote origin refs/heads/main
git rev-parse HEAD
```

Remote-Commit und lokaler `HEAD` müssen übereinstimmen.

## Windows Git Credential Manager

Falls `git push` in einer nicht-interaktiven Shell hängt und GitHub CLI bereits authentifiziert ist:

```powershell
gh auth setup-git --hostname github.com
```

`gh` kann unter folgendem Pfad liegen:

```text
C:\Program Files\GitHub CLI
```

und nicht im PATH sein.

Bei Bedarf:

```powershell
$env:GIT_TERMINAL_PROMPT=0
```

---

# 29. Bekannte technische Fallen

Die vollständige Liste steht in:

→ `docs/TROUBLESHOOTING.md`

Dort insbesondere nachsehen bei Änderungen an:

* Firebase
* Authentication
* Firestore
* Gruppen-Sync
* Sharing
* Kamera
* PDF
* Fotos
* Base64
* Carousel/Wizards
* Mobile Layout
* Push/Deployment

**Wenn ein Problem bereits dokumentiert ist, nicht denselben Fehler erneut auf dieselbe Weise lösen.**

---

# 30. Arbeitsablauf bei jeder Änderung

## Vor der Änderung

1. Aufgabe vollständig verstehen.
2. Relevanten Code mit `Grep` suchen.
3. Nur benötigte Ausschnitte lesen.
4. Relevante `docs/*.md` lesen.
5. Bei UI-Änderungen Design-Regeln beachten.
6. Bei Design-Änderungen die drei Design-Skills berücksichtigen.
7. Bei Architekturänderungen bestehende Architektur prüfen.
8. Bei bekannten Problemfeldern `TROUBLESHOOTING.md` prüfen.
9. Keine unnötigen Änderungen an angrenzendem Code durchführen.

## Während der Änderung

* Bestehende Architektur respektieren.
* Bestehende Tokens verwenden.
* Keine unnötigen neuen Abstraktionen erzeugen.
* Keine bestehende Funktion entfernen, nur weil sie auf den ersten Blick alt aussieht.
* Keine internen Namen ohne Migrationsgrund umbenennen.
* Keine Security nur über UI lösen.
* Keine Daten unnötig duplizieren.
* Keine Base64-Daten durch den Kontext kopieren.

## Nach der Änderung

1. Funktion testen.
2. Smoke-Test ausführen, wenn JavaScript geändert wurde.
3. Isolierten Ausschneide-Test durchführen, wenn die Funktion dies erfordert.
4. Bei UI-Änderungen mobile prüfen.
5. Bei UI-Änderungen Light und Dark prüfen.
6. Bei relevanten Interaktionen A11y prüfen.
7. Bei Cloud-/Sync-Änderungen entsprechende Sync-Szenarien testen.
8. Prüfen, ob Rechtstexte betroffen sind.
9. Passende Prüf-Agenten einsetzen.
10. Alle vier Dokumentationen auf Konsistenz prüfen.
11. Betroffene Dokumentation im selben Arbeitsschritt aktualisieren.
12. `ROADMAP.html` aktualisieren, wenn erforderlich.
13. `git diff` auf unbeabsichtigte Änderungen prüfen.
14. Erst danach committen.
15. Nach Push Remote-Commit überprüfen.

---

# 31. Minimalprinzip

**Ändere nur, was für die Aufgabe notwendig ist.**

Keine ungefragten:

* Refactorings
* Umbenennungen
* Design-Neuentwürfe
* Architekturumbauten
* Dependency-Wechsel
* Toolchain-Einführungen
* „Aufräumarbeiten“

Wenn ein Problem außerhalb des Auftrags entdeckt wird:

* nicht ungefragt umbauen
* wenn relevant dokumentieren
* dem Nutzer kurz darauf hinweisen

Ausnahme:
Wenn das Problem die Sicherheit, Datenintegrität oder korrekte Umsetzung der aktuellen Aufgabe gefährdet, muss es vor Abschluss der Aufgabe berücksichtigt werden.

---

# 32. Definition of Done

Eine Aufgabe ist erst abgeschlossen, wenn:

* die gewünschte Funktion korrekt umgesetzt ist
* bestehende Funktionen nicht unbeabsichtigt beschädigt wurden
* relevante Tests durchgeführt wurden
* relevante UI-Zustände geprüft wurden
* Design-Regeln eingehalten wurden
* Mobile berücksichtigt wurde
* relevante A11y-Aspekte berücksichtigt wurden
* Security bei relevanten Änderungen geprüft wurde
* Rechtstexte bei relevanten Änderungen geprüft wurden
* betroffene Dokumentation aktualisiert wurde
* `ROADMAP.html` bei Bedarf aktualisiert wurde
* `git diff` geprüft wurde

**Code, Dokumentation und Projektstatus müssen danach denselben tatsächlichen Stand beschreiben.**

---

# 33. Prioritäten bei Zielkonflikten

Wenn mehrere Regeln miteinander kollidieren, gilt grundsätzlich diese Reihenfolge:

1. Sicherheit und Datenintegrität
2. bestehende funktionierende Architektur
3. Produktnutzen
4. UX und Accessibility
5. Design-System „Performance Dark“
6. Wartbarkeit
7. Performance
8. Code-/Dokumentationskomfort

Keine Regel darf als Begründung für eine Sicherheitsverletzung oder Datenbeschädigung verwendet werden.

---

# 34. Wichtigste Grundregel

**Nicht nur Code schreiben. Das Projekt als Ganzes konsistent halten.**

Bei jeder relevanten Änderung mitdenken:

> Produkt → UX → Design → Architektur → Daten → Security → Tests → Dokumentation → ROADMAP

Wenn eine Änderung einen dieser Bereiche tatsächlich betrifft, muss der entsprechende Bereich ebenfalls aktualisiert und geprüft werden.
