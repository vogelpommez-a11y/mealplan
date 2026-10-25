# CLAUDE.md

Nur Regeln und Zeiger; das *Warum* steht in `docs/`. Ortsgebundenes in `.claude/rules/`,
`css/CLAUDE.md`, `data/CLAUDE.md` (laden nur beim Anfassen passender Dateien).

# 1. Das Leitziel
**Paddy's Mealplan erscheint im App Store und bei Google Play.** Maßstab für alle
Entscheidungen — Architektur, Bezahlung, Fremdcode, Berechtigungen.

* **Kein Code wird zur Laufzeit nachgeladen** (Apple 2.5.2): kein neuer `<script src="https://…">`,
  kein `import()` auf eine fremde URL.
* **Die App startet ohne Netz** und ist ohne Anmeldung sinnvoll nutzbar.
* **Digitale Funktionen in der App brauchen In-App-Purchase** (Apple 3.1.1). Vor Arbeit an
  Pro/Bezahlung `docs/STORE.md` §2 lesen. → Prüfliste und Stand: `docs/STORE.md` · Prüfer: Agent `store-check`

# 2. Projektgrundsätze
Kommunikation im Projekt auf **Deutsch** — auch Code-Kommentare, Doku, Commit-Messages
(Commit-Messages in ASCII: `geprueft`, `geaendert`).
Deutschsprachiger Wochen-Essensplaner aus statischen Dateien **ohne Build-Prozess**:
`index.html` (Markup, Firebase-Brücke, App-Kern als eine IIFE), `css/`, `data/` (nur Daten,
keine Logik), `lib/` (`window.PM`, PDF, Barcode). **Klassische Skripte in Dokumentreihenfolge,
keine ES-Module** — Module laufen nicht über `file://`, darauf bauen Smoke-Test und Prüfstände.
Wo was liegt: `docs/MODULE.md` (erzeugt mit `python tools/karte.py`), Firebase: `FIREBASE-SETUP.md`.
**Code, Doku und Projektstatus müssen nach einer Änderung konsistent sein.**

# 3. Dokumentation automatisch synchron halten
Betrifft eine Änderung eine dokumentierte Regel, Architektur, Testmethode oder Fehlerquelle,
wird die Doku **im selben Arbeitsschritt** aktualisiert, ohne dass der Nutzer bittet — in
`docs/`: PRODUCT (Features, UX, Marke, Premium), ARCHITECTURES (Daten, State, Firebase, Sync,
Gruppen), DESIGN (Tokens, Theme, Bewegung), TESTING (Prüfverfahren), TROUBLESHOOTING (Fallen,
behobene Fehler), SECURITY (Regeln, Bedrohungen), STORE (Bezahlung, Konto, Fremdcode).
**Dokumentations-Gate:** Vor Abschluss prüfen, ob eine davon falsch oder widersprüchlich
geworden ist; bei nicht-trivialen Änderungen macht das Agent `doku-waechter` über den
`git diff`. Keine Doku künstlich ändern, wo die Änderung keine Relevanz hat.

# 4. Produktphilosophie
**Kein Kalorien-Tracker.** Ein Tracker schaut zurück (*was habe ich gegessen?*), Paddy's
Mealplan nach vorne (*was werde ich essen?*). Qualität vor Quantität, Einfachheit vor Funktionen.
**Vor jeder neuen Funktion, auch vor einem bloßen Vorschlag:** Spart sie Zeit? Reduziert sie
Entscheidungen? Verbessert sie die Nutzererfahrung? Passt sie zum Wochenplan, zu
Fitness/Abnehmen und `state.goal`? Kein sinnvolles Ja: **nicht umsetzen**, auch nicht abgespeckt (`docs/PRODUCT.md`).

# 5. UX-Grundsätze
Jeder Screen löst möglichst genau ein Problem: wenige Interaktionen, klare nächste Aktion,
kurze Wege. Bei zwei gleichwertigen Lösungen gewinnt die mit weniger Interaktionen.

# 6. Markenstimme und Textmenge
Wie ein erfahrener Trainingspartner: motivierend, freundlich, vertrauenswürdig. **Die Marke
hilft dem Nutzer, sie bewertet ihn niemals** — besonders bei Gewicht, Kalorien, Zielen,
Fortschritt, Fehlern, leeren Zuständen. Kurz, positiv, kein Behörden-Deutsch, kein Slang.
Buttons aktiv (`Meal anlegen`). **So wenig Text wie möglich:** kein Erklärsatz, wo Label oder
Platzhalter es schon sagen; Notwendiges kompakt, wenn passend hinter `<details>`.

# 7. Design
Jede neue oder geänderte UI im bestehenden Design **„Performance Dark“**: Tokens statt
Hartkodiertes, nur System-Fonts, Light **und** Dark, Makros als `kcal → KH → P → F`.
Einzelregeln und Design-Skill-Reihenfolge: `.claude/rules/ui.md` (lädt bei `index.html`,
`css/`, `lib/`) und `docs/DESIGN.md` — bei jeder Design-Änderung zuerst dort.

# 8. Mobile
Mobile ist Teil **jeder** UI-Änderung (Breakpoints 720/560 px, Eingaben 16 px). Prüfen mit
echter Geräte-Emulation, nie über die Fensterbreite: `python tools/abnahme-mobil.py`
(Alltag, ~2 min), `--voll` in der Wartung. Details: `.claude/rules/ui.md`.

# 9. Keine Toolchain erfinden
Es gibt **kein** Node, PHP, npm, `package.json`, Bundler, Build, Test-Framework, Linter.
**Keine npm-Befehle erfinden.** Eine Änderung an `index.html` ist unmittelbar die fertige App;
Python ist da für Hilfs- und Testskripte. **Ausnahme nur außerhalb dieses Repos:** die
Capacitor-Hülle im privaten Nachbar-Repo `Paddys Mealplan App` — sie kopiert die Web-App und
ändert sie nie (`docs/STORE.md` §1).

# 10. Lesen und Bearbeiten des Codes
`index.html` ist **rund 1 MB und weit über 13.000 Zeilen lang**. **Nie die komplette Datei
blind lesen** — kein `cat`; mit `Grep` suchen, nur die Stelle mit Offset/Limit lesen. **Über
alle Code-Dateien suchen**, nicht nur `index.html` (`docs/MODULE.md`). `data:image;base64`
sind Nutzerbilder — über Skripte bearbeiten, nie durch den Kontext kopieren. Zum Testen
**nie nachbauen**: den echten Code aus `index.html` ausschneiden.

# 11. Testen und Verifikation
**Nach jeder JavaScript-Änderung zuerst** `python syntax-check.py --alles` (~1 s, läuft auch
als Hook). Ein Syntaxfehler beendet das ganze App-Script: HTTP 200, aber `#view` bleibt leer.
Skills: `/smoke`, `/pruefstand`, `/abnahme`, `/deploy`, `/rezeptcharge`. Gesamtlauf:
`python tools/alle-pruefstaende.py` („grün“ heißt bei OFFEN/REGRESSION nur **keine Regression**).
Während der Arbeit `/smoke` und der **eine** betroffene Prüfstand; vor dem Push entscheidet die
**Stufe**, einmal am Ende (im Zweifel die höhere):
| Stufe | Änderung | Vor dem Push |
|---|---|---|
| **A** | nichts an der App (`docs/`, `plans/`, `.claude/`, `tools/`, CI) | `/pushcheck`; bei `.claude/` auch `python tools/wartung-check.py` |
| **B** | App-Code, nichts Sicht-/Bedienbares (Sync, Rechnen, `sw.js`, Worker); auch `tools/`, die Nutzerdaten anfassen (`firestore-*.py`, `shared-aufraeumen.py`, `konten-inaktiv.py`) | `alle-pruefstaende.py --betroffen` + `/pushcheck` |
| **C** | Sicht-/Bedienbares (Markup, `css/`, Texte, Bilder, Abläufe) | Vorführung (§21b) + `--betroffen` + `abnahme-mobil.py` + `/pushcheck` |
Die volle Runde (alle Prüfstände, `abnahme-mobil.py
--voll`, alle Agenten, `tempo-mobil.py`) läuft in der Wartung, vor Store-Abgaben und nach großen
Umbauten; `abnahme-app.py` nur vor Store-Abgaben (`docs/TESTING.md`). Bricht ein langer Test ab:
**nicht neu starten**, `docs/TROUBLESHOOTING.md` lesen, Nutzer fragen.
Nicht verhandelbar: **Getestet wird echter, ausgeschnittener Produktionscode.** **Ohne
Gegenprobe zählt kein Ergebnis** — derselbe Prüfstand muss gegen den alten Stand durchfallen.

# 12. Firebase, Cloud-Sync und Security
> **Die Firestore Security Rules sind die einzige Sicherheitsgrenze. Alles andere ist
> Bequemlichkeit.**
UI-Sperren sind keine Grenze; jede neue Berechtigung **zuerst in den Regeln**, dann im Client.
Die App muss auch ohne Firebase laufen (`authMode` `"local"` und `"cloud"`). Veröffentlicht
wird von Hand in der Konsole, nie aus einem Skript; vorher `python tools/regeln-pruefen.py`.
Die Web-Config in `index.html` ist kein Secret. **Geheimnisse** (`OPENAI_API_KEY` in `.env`,
Service-Account-Schlüssel des Workers): **nie ausgeben**, nie in Prüfstand oder Skript
kopieren; stand einer irgendwo, hilft nur Rotation. Einzelheiten: `.claude/rules/firebase.md`
(lädt bei Rules, `tools/firestore*`, `worker/`) und `docs/SECURITY.md`.

# 13. Daten und Datenschutz
Ein Meal speichert bei `by` **ausschließlich die UID** — nie Name, E-Mail oder andere
personenbezogene Daten; der Name kommt bei der Anzeige aus `groupMembers`. E-Mail-Adressen
gehören nicht in Gruppen-Mitgliederdokumente. Bei Änderungen an Sharing, Sync, Gruppen,
Datenfeldern, Löschlogik oder personenbezogenen Daten: Rechtstexte (`data/rechtstexte.js`, enthalten konkrete technische Zusagen) gegen die
Implementierung prüfen, Agenten `anwalt` und `datenschutz-technik` einsetzen.
**Der Footer bleibt ohne Anmeldung sichtbar**, das Impressum nie hinter dem Auth-Gate (`docs/DATENSCHUTZ-INTERN.md`).

# 14. Namensdualität
Sichtbar: **Paddy's Mealplan** und **Meal**. Intern: `wochenkueche` und `recipe`
(`wochenkueche_v1`, `state.recipes`, `getRecipe`, `data-tab="recipes"`, `.rcard`).
**Nicht „aufräumen“** — die Namen stecken in bestehenden Daten und verschickten Sharing-Links.

# 15. Bilder und Lizenzen
Neue Bilder **nur über `tools/meal-bilder.py`**, nie von Hand, nie aus fremden Quellen.
Dateinamen in `PHOTOS` **nie ändern**, Endung inklusive; Bild ausgetauscht → `VERSION` in
`sw.js` hoch. **Nährwerte nie schätzen** (`tools/rezept-makros.py`). **Katalogrezepte nur
über `/rezeptcharge`.** Stichworte: Teilwort-Kollisionen (`eis` in `Rindfleisch`, `reis` in
`Preiselbeere`; `tools/pruefstand-bildstichworte.py`). Zuordnungskette, Anleitung: `data/CLAUDE.md`.

# 16. Fremdcode unter `vendor/`
Firebase-SDK und ZXing liegen **lokal**, nie auf einem CDN; Update nur mit Anlass und über
`tools/firebase-vendor.py`. Regeln: `.claude/rules/vendor.md` · Prüfer: Agent `lieferkette`.

# 17. Git und Deployment
Deployment ist ein Push auf `main`; GitHub Pages baut automatisch. Danach muss
`git ls-remote origin refs/heads/main` mit `git rev-parse HEAD` übereinstimmen.
**Nie `git add .`** — alles im Repo ist öffentlich, Gelöschtes bleibt in der Historie; immer
einzelne Pfade stagen. Gitignored, nie committen: `plans/`, `dashboard.html`, `Fotos/`,
`Marketing/`, `Instagram/`, `.env`, `docs/DATENSCHUTZ-INTERN.md`, die zugekauften Skills.
**Vor jedem Push `/pushcheck`** in der Stufe aus §11. Rollback, Notfälle: `docs/RUNBOOK.md`
und `/deploy`. Lokaler Server: `powershell -NoProfile -ExecutionPolicy Bypass -File
test-server.ps1` → `http://localhost:8000/`

# 18. Hooks — was automatisch läuft
Hooks stehen in `.claude/settings.json`, Skripte unter `.claude/hooks/`. `commit-waechter.py`
**blockiert** `git commit` bei Nichtöffentlichem im Index, `secrets-filter.py` **blockiert**
Befehle, die `.env` ausgeben; dazu Syntax-Prüfung, Push- und Wartungs-Erinnerung. Wird ein Hook
zum Hindernis: melden, nicht umgehen. **Hooks nie relativ adressieren** —
`python "$CLAUDE_PROJECT_DIR/.claude/hooks/…"` (`docs/TROUBLESHOOTING.md` §140).

# 18a. Wartung — das Prüfsystem prüft sich selbst
Alle 30 Tage: `python tools/wartung-check.py`, `/rechtspruefung`, `store-check`, `lieferkette`,
volle Runde, zuletzt `wartung-check.py --setze` (verweigert ohne Sicherung und Rechtsbericht).
Umfang: `docs/TESTING.md` 2k.

# 18b. Abdeckung — hat jeder Bereich einen Prüfer?
`python tools/abdeckung.py` (`--gegenprobe`) gegen das Register `docs/ABDECKUNG.md`. **Entsteht
ein neuer Produktbereich, gehört die Frage nach seinem Prüfer zur Änderung.** Bei einer Lücke:
Zeile im Register, einen neuen Agenten **dem Nutzer zur Abnahme vorlegen** (nie still anlegen)
oder bewusst ohne Prüfer mit Begründung — **nie eine Kennung eintragen, nur damit Ruhe ist.**

# 19. Prüf-Agenten
Acht Agenten in `.claude/agents/`; sie ändern **nie** etwas, sie melden. Über `/pushcheck`:
`website-security` bei jedem Push, `doku-waechter` bei nicht-trivialen Änderungen, die übrigen
nur nach Anlass im Diff — `anwalt` (Recht, Datenfelder), `ux-reviewer` (neuer Bildschirm), `kvp`
(neue Funktion), `store-check` (Pro, Konto, Kamera, Manifest), `lieferkette` (`vendor/`),
`datenschutz-technik` (Dienst, Datenfeld, Sharing); `/code-review` bei Sync, Speichern, Löschen,
Rechnen, Login, Rules. Auslöser und Modelle: `.claude/commands/pushcheck.md`. Rote Funde werden
**widerlegt, nicht bestätigt**. 🟡 und Vorschläge sind optional, nur auf Paddys Wunsch
umzusetzen und nie automatisch neue Regeln; gemeldet wird nur, was Korrektheit, Sicherheit,
Recht oder Store betrifft.

# 20. Arbeitsweise
**Modellwahl:** Größere Pläne von **Sonnet** umsetzen lassen, danach mit **Opus**
gegenprüfen; bei komplexen Aufgaben von selbst ein Modell vorschlagen. **Eine Sitzung pro
Thema;** nach zwei Korrekturen am selben Fehler neu starten mit besserer Beschreibung.
**Pläne** nach `ExitPlanMode` mit sprechendem Namen nach `plans/` kopieren; umgesetzte Pläne
ohne Rückfrage löschen. **`dashboard.html` ist erzeugt:** nach jedem Feature `plans/app-karte.json`
(auch `etappen`) nachziehen, dann `python tools/dashboard.py`; beides gitignored, **nie committen.**

# 21. Ablauf bei jeder Änderung
Vorher `Grep` und `docs/*.md` über das Register lesen. Danach `/smoke`, Stufe aus §11, bei UI
mobil/Hell/Dunkel/A11y, bei Cloud/Sync die Sync-Szenarien (notfalls `/abnahme`), Doku und
Dashboard nachziehen, `git diff` sichten, committen. **Beim Zusammenfassen eines langen
Gesprächs immer erhalten:** geänderte Dateien, Prüfergebnisse, offene Freigaben von Paddy,
was noch nicht committet oder gepusht ist.

# 21a. Bevor etwas Neues entsteht — drei Stufen
Bei UI-Bausteinen erst in der App suchen und den bestehenden verwenden, dann Vorbilder (MDN,
WCAG, Base UI) nachbauen statt erfinden, nur sonst neu bauen; die Herkunft dem Nutzer nennen.
Tabelle: `.claude/rules/ui.md`, Register `docs/BAUSTEINE.md`.

# 21b. Sichtbare Änderungen werden vorgeführt, bevor sie live gehen
Jede sichtbare Änderung zuerst als Ist/Soll-Film zeigen (`tools/vorher-nachher.py`), erst
nach Zustimmung committen und pushen. **Nie im Alltagsbrowser vorführen** (Cloud-Konto
angemeldet). Ablauf: `.claude/rules/ui.md`.

# 21c. Änderungswünsche: erst das Vorgehen anbieten
Bei allem Sicht- oder Bedienbaren und bei neuen Funktionen (nicht Fehler, Tippfehler, Doku,
Werkzeuge) zuerst per Auswahlbildschirm fragen, ob vorher recherchiert werden soll; „ohne
Recherche“ ist gültig. Ablauf: `.claude/rules/ui.md`.

# 22. Minimalprinzip
**Ändere nur, was für die Aufgabe notwendig ist** — keine ungefragten Refactorings,
Umbenennungen, Neuentwürfe, Dependency-Wechsel oder „Aufräumarbeiten“; keine Funktion
entfernen, weil sie alt aussieht; keine Daten unnötig duplizieren. Problem außerhalb des
Auftrags: darauf hinweisen. **Ausnahme:** Es gefährdet Sicherheit, Datenintegrität oder die Aufgabe.

# 23. Definition of Done
Funktion korrekt, nichts Bestehendes beschädigt, Tests, UI-Zustände, Mobile/A11y, bei
Relevanz Security und Rechtstexte geprüft, Doku und Dashboard stimmen, `git diff` gesichtet.

# 24. Prioritäten bei Zielkonflikten
1. Sicherheit und Datenintegrität, 2. bestehende Architektur, 3. Produktnutzen, 4. UX und A11y,
5. „Performance Dark“, 6. Wartbarkeit, 7. Performance, 8. Code-/Dokukomfort. Keine Regel
rechtfertigt eine Sicherheitsverletzung oder Datenbeschädigung.

# 25. Wichtigste Grundregel
Das Projekt als Ganzes konsistent halten (Produkt, UX, Design, Architektur, Daten, Security,
Store, Tests, Doku, Dashboard): Betrifft eine Änderung einen Bereich, wird er mit aktualisiert.
