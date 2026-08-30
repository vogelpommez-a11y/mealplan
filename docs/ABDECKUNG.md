# ABDECKUNG.md

# Wer prüft was — und was gerade niemand prüft

**Register** — was hier steht:

| Abschnitt | Frage, die er beantwortet |
|---|---|
| 1. Wozu diese Datei | Warum Konsistenz nicht genügt |
| 2. Wie sie gelesen wird | Das Format, an das sich das Skript hält |
| 3. Pfade | Welcher Ordner hat welchen Prüfer? |
| 4. Reiter der App | Welcher Produktbereich hat welchen Prüfer? |
| 5. Externe Verbindungen | Wer prüft, was nach draußen geht? |
| 6. Bewusst ohne Prüfer | Was absichtlich keinen hat — und warum |
| 7. Wenn eine Lücke gemeldet wird | Was dann zu tun ist |

Geprüft von `tools/abdeckung.py`. Gemeldet beim Sitzungsstart, in
`tools/wartung-check.py` und in der monatlichen Cloud-Routine.

---

## 1. Wozu diese Datei

`tools/wartung-check.py` prüft **Konsistenz**: Stimmt das Modell eines Agenten mit dem, was
`CLAUDE.md` verspricht? Zeigt ein Verweis ins Leere? Hat ein Agent eine `tools:`-Zeile?

Das sind alles Fragen über Dinge, **die es gibt**. Keine davon findet, was **fehlt**.

Käme morgen ein Marketing-Bereich in die App — mit Werbetexten, einem Newsletter, vielleicht
Tracking —, dann gäbe es dafür keinen Prüfer, und das gesamte Setup meldete weiterhin
„keine Befunde". Es weiß nicht, dass es etwas nicht weiß.

Diese Datei ist die Antwort darauf: eine Liste dessen, was das Projekt an Bereichen **hat**,
und wer sie jeweils prüft. Findet `tools/abdeckung.py` im Repo etwas, das hier nicht steht,
meldet es das.

> **Ein Bereich ohne Prüfer ist kein Fehler.** Er ist eine Entscheidung, die jemand treffen
> muss — und genau deshalb muss sie sichtbar sein statt unbemerkt zu bleiben.

---

## 2. Wie sie gelesen wird

`tools/abdeckung.py` liest **ausschließlich die Tabellen** in den Abschnitten 3 bis 6 und
darin **nur die Spalte `Kennung`**. Alles andere ist Text für Menschen.

Eine Kennung hat die Form `art:wert` und entspricht genau dem, was die Erkennung im Repo
findet:

| Art | Woher sie kommt | Beispiel |
|---|---|---|
| `pfad` | erste Pfadkomponente aus `git ls-files` | `pfad:vendor/` |
| `doku` | Datei in `docs/` | `doku:docs/STORE.md` |
| `reiter` | `data-tab="…"` in `index.html` | `reiter:recipes` |
| `domain` | Hostname aus `http(s)://…` in `index.html`, `sw.js`, `worker/` | `domain:firestore.googleapis.com` |

**Neue Zeile anlegen heißt: eine bewusste Zuordnung treffen.** Wer eine Kennung nur einträgt,
damit die Meldung verschwindet, hat die Prüfung abgeschaltet, nicht bestanden.

### Was die Erkennung strukturell **nicht** sieht

Diese Grenzen sind bekannt und bewusst. Wer einen Bereich anlegt, der so aussieht, trägt ihn
**von Hand** ein — das Skript wird ihn nie melden:

| Fall | Warum | Was stattdessen greift |
|---|---|---|
| Ein Reiter, den JavaScript zur Laufzeit erzeugt | Gesucht wird `data-tab="…"` im **Quelltext**. Heute stehen alle vier Reiter im Template (`dataset.tab` wird nur gelesen, nie gesetzt) | von Hand eintragen |
| Ein gitignorter Ordner (`plans/`, `Fotos/`, `Marketing/`) | `git ls-files` kennt nur Versioniertes | er geht auch nicht live; der Commit-Wächter blockiert ihn zusätzlich |
| Ein leeres Verzeichnis | git kennt keine leeren Verzeichnisse | fällt auf, sobald die erste Datei darin liegt |
| Hostnamen ohne Punkt (`localhost`) | bewusst gefiltert, sonst landet jedes URL-Fragment im Register | keine echte Verbindung nach draußen |
| Eine Domain, die nur in `vendor/` steht | Fremdcode nennt Dutzende Hosts, die er nie kontaktiert — das Register wäre nach einem Update unlesbar | `pfad:vendor/` hat mit `lieferkette` seinen eigenen Prüfer |

**Die andere Richtung prüft das Skript ebenfalls:** Steht eine Kennung im Register, die im
Repo nirgends vorkommt, meldet es das als **Verrottung**. Ohne diese Prüfung könnte ein
gelöschter Bereich seine Zeile behalten, und die Zuordnung wäre Fiktion, ohne dass es jemand
merkt.

---

## 3. Pfade

| Bereich | Kennung | Prüfer | Auslöser |
|---|---|---|---|
| Die App selbst | `pfad:index.html` | alle, je nach Änderung | siehe `CLAUDE.md` §19 |
| Styles und Design-Tokens | `pfad:css/` | `ux-reviewer` (Tokens, Zustände), `kvp` (Mobile) | jede UI-Änderung |
| Daten und Rechtstexte | `pfad:data/` | `anwalt` (Rechtstexte, Bildlizenzen), `kvp` (Katalog, Nährwerte), `tools/pruefstand-rezepttexte.py` (Zubereitungen) | neues Meal, neues Bild, geänderter Rechtstext |
| Eigenständige Bibliotheken | `pfad:lib/` | `website-security` (Open Food Facts, Kamera), `lieferkette` (ZXing-Anbindung) | Änderung an Barcode, PDF oder den gemeinsamen Helfern |
| Prüfsystem (Agenten, Hooks, Skills) | `pfad:.claude/` | `tools/wartung-check.py` | jede Änderung am Setup |
| CI | `pfad:.github/` | `website-security` | Änderung am Workflow |
| Dokumentation | `pfad:docs/` | `doku-waechter` | jede nicht-triviale Änderung |
| Meal-Fotos und ihre Lizenzen | `pfad:img/` | `anwalt` (Bildrechte) | neues Bild, neue Quelle |
| Werkzeuge und Prüfstände | `pfad:tools/` | `kvp` | neuer Prüfstand, neues Werkzeug |
| Fremdcode | `pfad:vendor/` | `lieferkette` | jede Änderung, plus regelmäßig ohne Anlass |
| Cloudflare Worker | `pfad:worker/` | `website-security`, `datenschutz-technik` | Deploy, neue Verarbeitung |
| Firestore-Regeln | `pfad:firestore.rules` | `website-security` | jede Regeländerung |
| Service Worker | `pfad:sw.js` | `website-security` | Cache-Strategie, neue Assets |
| Store-Manifest | `pfad:manifest.webmanifest` | `store-check` | Name, Icons, Berechtigungen |
| Syntax-Prüfung | `pfad:syntax-check.py` | `tools/wartung-check.py` | Änderung am Prüfverfahren |
| Lokaler Server | `pfad:test-server.ps1` | — nur Werkzeug, nicht ausgeliefert — | — |
| Projektregeln | `pfad:CLAUDE.md` | `doku-waechter` | jede Regeländerung |
| Meldeweg für Lücken | `pfad:SECURITY.md` | `website-security` | Änderung am Meldeweg |
| Lizenzhinweise | `pfad:LICENSE` | `lieferkette` | neuer Fremdcode |
| Öffentliche Beschreibung | `pfad:README.md` | `doku-waechter` | Änderung am Projektbild |
| Firebase-Einrichtung | `pfad:FIREBASE-SETUP.md` | `doku-waechter` | Änderung an der Einrichtung |
| Domain | `pfad:CNAME` | `website-security` | Domainwechsel (auch Authorized Domains!) |
| Suchmaschinen | `pfad:robots.txt` | — statisch, keine Verarbeitung — | — |
| Suchmaschinen | `pfad:sitemap.xml` | — statisch, keine Verarbeitung — | — |
| Zeilenenden | `pfad:.gitattributes` | `tools/wartung-check.py` | — |
| Ausschlüsse | `pfad:.gitignore` | `website-security` | jede neue Ausnahme |
| App-Icons und Vorschaubild | `pfad:img/` | `store-check` (Icons), `anwalt` (Bildrechte) | Icon-Wechsel, Bildwechsel |

ℹ️ **Warum die Icons keine eigenen Zeilen mehr haben (30.08.2026):** Sie lagen bis dahin
in der Repo-Wurzel und waren dort je ein eigener Bereich. Seit dem Umzug nach `img/` sieht
die Erhebung nur noch **einen** Bereich `pfad:img/` — fünf Einzelzeilen zeigten danach ins
Leere, und die Prüfung meldete Verrottung.

Zusammengefasst heißt hier **nicht** „nur noch ein Prüfer": Die Zeile nennt weiterhin beide.
`store-check` für die Icons (Store-Anforderungen an Größen und Maskierbarkeit), `anwalt` für
die Bildrechte. Wer die Zeile später kürzt, nimmt einem der beiden die Zuständigkeit —
lautlos.

## 4. Reiter der App

Ein neuer Reiter ist fast immer ein neuer Produktbereich — und damit die wahrscheinlichste
Stelle, an der eine Prüflücke entsteht.

| Bereich | Kennung | Prüfer | Auslöser |
|---|---|---|---|
| Startseite, Tagesziele | `reiter:home` | `kvp`, `ux-reviewer` | jede UI-Änderung |
| Wochenplan | `reiter:plan` | `kvp`, `ux-reviewer` | jede UI-Änderung |
| Meals und Rezeptbuch | `reiter:recipes` | `kvp`, `ux-reviewer` | jede UI-Änderung |
| Fortschritt, Gewicht | `reiter:progress` | `kvp`, `ux-reviewer`, `datenschutz-technik` | Gesundheitsdaten — Art. 9 DSGVO ist offen |

## 5. Externe Verbindungen

Alles, was nach draußen geht, ist entweder eine **Verarbeitung** (Datenschutz) oder ein
**Verweis im Rechtstext** (Belegpflicht). Beides braucht einen Prüfer.

| Bereich | Kennung | Prüfer | Auslöser |
|---|---|---|---|
| Firestore | `domain:firestore.googleapis.com` | `datenschutz-technik`, `website-security` | neues Datenfeld, neue Sammlung |
| Google-Login | `domain:oauth2.googleapis.com` | `datenschutz-technik`, `store-check` | Login-Änderung (Apple 4.8) |
| Google-APIs | `domain:www.googleapis.com` | `datenschutz-technik` | neuer Dienst |
| Eigene Domain | `domain:www.paddysmealplan.de` | `website-security` | Domainwechsel |
| Strukturierte Daten | `domain:schema.org` | — Namensraum, keine Verbindung — | — |
| OpenAI-Nutzungsbedingungen | `domain:openai.com` | `anwalt` | Rechtstext-Verweis |
| GitHub-Datenschutz | `domain:docs.github.com` | `anwalt` | Rechtstext-Verweis |
| Google-Datenschutz | `domain:policies.google.com` | `anwalt` | Rechtstext-Verweis |
| Open Food Facts | `domain:world.openfoodfacts.org` | `anwalt` | Lizenzverweis |
| ODbL-Lizenz | `domain:opendatacommons.org` | `anwalt` | Lizenzverweis |
| Creative Commons | `domain:creativecommons.org` | `anwalt` | Bildlizenz |
| Wikimedia Commons | `domain:commons.wikimedia.org` | `anwalt` | Bildquelle |
| Flickr | `domain:www.flickr.com` | `anwalt` | Bildquelle |
| Rawpixel | `domain:www.rawpixel.com` | `anwalt` | Bildquelle |
| StockSnap | `domain:stocksnap.io` | `anwalt` | Bildquelle |

## 6. Bewusst ohne Prüfer

Hier stehen Bereiche, für die es **absichtlich** keinen gibt. Ein Eintrag hier ist eine
Entscheidung mit Begründung, kein Versäumnis — und `tools/abdeckung.py` schweigt dazu.

| Bereich | Kennung | Warum ohne Prüfer |
|---|---|---|
| Doku: Produkt | `doku:docs/PRODUCT.md` | `doku-waechter` deckt `docs/` als Ganzes ab |
| Doku: Architektur | `doku:docs/ARCHITECTURES.md` | dito |
| Doku: Design | `doku:docs/DESIGN.md` | dito |
| Doku: Tests | `doku:docs/TESTING.md` | dito |
| Doku: Fallarchiv | `doku:docs/TROUBLESHOOTING.md` | dito |
| Doku: Runbook | `doku:docs/RUNBOOK.md` | dito |
| Doku: Sicherheit | `doku:docs/SECURITY.md` | `website-security` liest sie ohnehin |
| Doku: Store | `doku:docs/STORE.md` | `store-check` liest sie ohnehin |
| Doku: Datenschutz intern | `doku:docs/DATENSCHUTZ-INTERN.md` | `datenschutz-technik` liest sie ohnehin; gitignored |
| Doku: Abdeckung | `doku:docs/ABDECKUNG.md` | diese Datei selbst |
| Doku: Technische Landkarte | `doku:docs/MODULE.md` | erzeugt von `tools/karte.py`; `--pruefe` läuft in `wartung-check.py` und in der CI und schlägt an, sobald sie vom Ist-Zustand abweicht |

---

## 7. Wenn eine Lücke gemeldet wird

Die Meldung sagt: *Etwas ist im Repo, das in keiner Tabelle steht.* Sie sagt **nicht**, dass
ein neuer Agent gebaut werden muss. Drei Wege sind richtig, einer ist falsch:

1. **Der Bereich gehört zu einem bestehenden Prüfer.** Zeile in Abschnitt 3–5 anlegen, fertig.
2. **Der Bereich braucht wirklich einen neuen Prüfer.** Dann wird ein Agent **entworfen und
   zur Abnahme vorgelegt** — nie still angelegt. Ein Prüfer, den niemand geprüft hat, meldet
   „sauber" und man glaubt ihm; das ist am 26. und 27.08.2026 je einmal passiert
   (`docs/TROUBLESHOOTING.md` §119 und §123).
3. **Der Bereich braucht bewusst keinen.** Zeile in Abschnitt 6, **mit Begründung**.

**Falsch ist:** eine Kennung eintragen, damit Ruhe ist. Das schaltet die Prüfung für genau
diesen Bereich dauerhaft ab, und niemand sieht es je wieder.
