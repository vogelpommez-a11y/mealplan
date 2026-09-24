# Technische Landkarte

**Erzeugt von `tools/karte.py`. Nicht von Hand aendern.**

Diese Datei beschreibt ausschliesslich den *tatsaechlichen* technischen
Zustand des Repositories. Sie ist keine Roadmap und kein Backlog: nichts
Geplantes, nichts Gewuenschtes, keine Prioritaeten, keine Termine. Die
Roadmap liegt getrennt und ist gitignored.

Neu erzeugen mit `python tools/karte.py`, pruefen mit
`python tools/karte.py --pruefe`.

## 1. Reiter der App

| Reiter |
|---|
| home |
| plan |
| progress |
| recipes |

## 2. Ladereihenfolge

Die Reihenfolge ist Architektur: klassische Skripte laufen synchron
nacheinander, bevor die App-IIFE geparst wird.

| # | Datei |
|---|---|
| 1 | css/tokens.css |
| 2 | css/basis.css |
| 3 | css/komponenten.css |
| 4 | css/mobil.css |
| 5 | lib/basis.js |
| 6 | data/ikonen.js |
| 7 | data/bilder.js |
| 8 | data/cookbook.js |
| 9 | data/foods.js |
| 10 | data/rechtstexte.js |
| 11 | lib/pdf.js |
| 12 | lib/barcode.js |

## 3. Bereiche

Erhoben aus den Abschnittsmarken im Code, nicht von Hand gepflegt.

| Datei | Bereich | Zeilen | Umfang |
|---|---|---|---|
| css/basis.css | Header | 20-273 | 254 |
| css/basis.css | Section head | 274-307 | 34 |
| css/basis.css | Buttons | 308-401 | 94 |
| css/basis.css | Week grid | 402-1552 | 1151 |
| css/komponenten.css | Recipe grid | 8-327 | 320 |
| css/komponenten.css | Meal-Ansicht (openMealSheet) | 328-551 | 224 |
| css/komponenten.css | Empty state | 552-563 | 12 |
| css/komponenten.css | Modal | 564-955 | 392 |
| css/komponenten.css | Profil (Login) & Teilen | 956-1058 | 103 |
| css/komponenten.css | Profilbild-Zuschnitt (Kreis-Crop) | 1059-1253 | 195 |
| css/komponenten.css | PDF / Druck | 1254-1347 | 94 |
| css/mobil.css | Mobile / Smartphone | 8-1006 | 999 |
| css/mobil.css | Gemeinsam planen (Gruppe) | 1007-1073 | 67 |
| data/bilder.js | Gerichtsfotos (nach Namen zugeordnet) | 11-142 | 132 |
| data/cookbook.js | Rezeptbuch | 11-569 | 559 |
| data/foods.js | Zutaten-Datenbank fuer die Suche | 11-244 | 234 |
| data/ikonen.js | Strich-Icons fuer die Kategorie-Ueberschriften | 11-30 | 20 |
| data/ikonen.js | Ein Symbol je Lebensmittel (12.09.2026) | 31-72 | 42 |
| data/ikonen.js | Symbole fuer die Schnellauswahl im Picker | 73-168 | 96 |
| index.html | Cloud-Sync (Firestore): pro Nutzer ein Dokument users/{uid} | 532-565 | 34 |
| index.html | Fehlerbehandlung fuer onSnapshot | 566-593 | 28 |
| index.html | Pro-Berechtigung (D1): eigenes Dokument entitlements/{uid}, NUR lesbar | 594-643 | 50 |
| index.html | Rezepte: eigenes Dokument je Meal (users/{uid}/recipes/{id}) | 644-692 | 49 |
| index.html | Teilen per Cloud-Link: öffentlich lesbare Snapshots in shared/{id} | 693-701 | 9 |
| index.html | Gemeinsam planen: groups/{gid} mit Mitgliedern, Wochenplan und Meals | 702-761 | 60 |
| index.html | Mitglieder: ein Dokument je Person, damit Rollenrechte pro Dokument gelten | 762-791 | 30 |
| index.html | Mitgliederlimit: Beitritt und Austritt sind ATOMAR | 792-857 | 66 |
| index.html | Wochenplan | 858-921 | 64 |
| index.html | Einladungscodes | 922-954 | 33 |
| index.html | Der Aufklapp-Pfeil | 955-969 | 15 |
| index.html | Leere Zustaende: EINE Form statt fuenf | 970-999 | 30 |
| index.html | Testumgebung von den echten Daten trennen | 1000-1067 | 68 |
| index.html | Aktivitaet und Training (Stammdaten des Kalorienrechners) | 1068-1165 | 98 |
| index.html | Merkmale eines Meals (Tags, Meal-Prep) | 1166-1182 | 17 |
| index.html | Ernaehrungsprofil (state.goal.diet / state.goal.avoid) | 1183-1249 | 67 |
| index.html | State | 1250-1298 | 49 |
| index.html | Wochen (aktuelle + naechste, an ISO-Kalenderwochen gebunden) | 1299-1701 | 403 |
| index.html | Gewichtsverlauf | 1702-1718 | 17 |
| index.html | B2: Der Verlauf rechnet in WOCHEN, nicht mehr in Monaten | 1719-1864 | 146 |
| index.html | Gedaechtnis des Auto-Planers (state.planned) | 1865-1912 | 48 |
| index.html | Grabsteine geloeschter Meals | 1913-2036 | 124 |
| index.html | Bilder in IndexedDB (Paket A3) | 2037-2126 | 90 |
| index.html | Cloud-Sync (Firestore) | 2127-2130 | 4 |
| index.html | Pro-Berechtigung (D1) | 2131-2179 | 49 |
| index.html | Gemeinsam planen: Gruppenmodus | 2180-2277 | 98 |
| index.html | Wochenplan flach <-> verschachtelt (fuer Gruppen-Dokumente) | 2278-2796 | 519 |
| index.html | Empfaenger fuer die Gruppe | 2797-3415 | 619 |
| index.html | Rezeptbuch: was zeigen, was ist schon uebernommen | 3416-3433 | 18 |
| index.html | Startmeals nach dem Onboarding | 3434-3494 | 61 |
| index.html | Einmalige Aufraeumung alter Dubletten (Teil 3 des Katalog-Umbaus, 17.08.2026) | 3495-3555 | 61 |
| index.html | Zahleneingabe: Rad am Handy, Tastatur am Rechner | 3556-3634 | 79 |
| index.html | Sicherheitsnetz fuer fremde Bilddaten | 3635-3735 | 101 |
| index.html | Bilder der kuratierten Bibliothek (img/library/) | 3736-3867 | 132 |
| index.html | Symbol statt Foto | 3868-3930 | 63 |
| index.html | Rendering | 3931-4051 | 121 |
| index.html | Nährwerte | 4052-4105 | 54 |
| index.html | Strukturierte Zutaten | 4106-4242 | 137 |
| index.html | Schnelleintrag: zaehlbare Lebensmittel | 4243-4337 | 95 |
| index.html | Kamerabild: Buehnenformat und Fokus | 4338-4549 | 212 |
| index.html | Trainingstage (Verbrauch je Einheit) | 4550-5144 | 595 |
| index.html | Merkmale: Anzeige (Nur-Lese-Zweig) und Eingabe (Bearbeiten-Zweig) | 5145-5179 | 35 |
| index.html | Handy-Karussell (Wochenplan, Wochenziele, Rechner) | 5180-5470 | 291 |
| index.html | Hinweis: title=, das auch auf Touch ankommt | 5471-5543 | 73 |
| index.html | Ladezustand der Meal-Bilder | 5544-5574 | 31 |
| index.html | Spotlight: ein Hinweis auf genau eine Funktion | 5575-5667 | 93 |
| index.html | Sortieren per Ziehen: die gemeinsame Geste | 5668-6125 | 458 |
| index.html | „Ziele <Jahr>": Gewichtsverlauf als Jahresdiagramm | 6126-6502 | 377 |
| index.html | Fortschritt-Kalender (Paket 6, B7/B11) | 6503-6853 | 351 |
| index.html | Der eine Zeitraum fuer den ganzen Reiter (seit 03.09.2026) | 6854-7683 | 830 |
| index.html | Zurueck-Taste (D5) | 7684-7759 | 76 |
| index.html | Modal | 7760-7844 | 85 |
| index.html | Wiegen | 7845-7921 | 77 |
| index.html | Stepper (seit 03.09.2026) | 7922-8168 | 247 |
| index.html | Ziel von Hand justieren (B4) | 8169-8281 | 113 |
| index.html | Bewegung: FLIP am Rechner, Bottom-Sheet am Handy | 8282-8427 | 146 |
| index.html | Nur-Lese-Zweig: keine Eingabefelder, kein Autosave, kein Loeschen | 8428-8507 | 80 |
| index.html | Bearbeiten-Zweig | 8508-8586 | 79 |
| index.html | Autosave: input mutiert nur lokal, change/blur committen, 1500ms Leerlauf-Timer als Netz | 8587-8794 | 208 |
| index.html | Foto: waehlen/aendern/entfernen, aktualisiert nur die offene Ansicht (photoDoneCb) | 8795-8824 | 30 |
| index.html | Zutaten-Zeilen (Name, Menge, Naehrwerte pro 100 g, Barcode-Scan) | 8825-9056 | 232 |
| index.html | Zutaten-Suche (ARIA-Combobox auf dem Namensfeld) | 9057-9193 | 137 |
| index.html | Zutaten per Ziehen sortieren (Paket 3) | 9194-9503 | 310 |
| index.html | Picker | 9504-9843 | 340 |
| index.html | Shopping list | 9844-10055 | 212 |
| index.html | Vorkochen (C3) | 10056-10263 | 208 |
| index.html | Actions | 10264-10349 | 86 |
| index.html | Rechtstexte (Impressum / Datenschutz) | 10350-10375 | 26 |
| index.html | Auto-Wochenplaner (D2) | 10376-10482 | 107 |
| index.html | Wiederholung: was zuletzt dran war, rutscht nach hinten | 10483-10501 | 19 |
| index.html | Passt die Groesse zum Slot? | 10502-10508 | 7 |
| index.html | In der Gruppe: was zu MEHR Profilen passt, kommt weiter nach vorn | 10509-10883 | 375 |
| index.html | Toast | 10884-10893 | 10 |
| index.html | Toast mit Rueckgaengig (Paket B1) | 10894-10929 | 36 |
| index.html | Event delegation | 10930-11157 | 228 |
| index.html | Meals im Plan per Ziehen sortieren | 11158-11261 | 104 |
| index.html | Foto per Drag & Drop auf eine Meal-Karte (Desktop) | 11262-11293 | 32 |
| index.html | Foto per Strg+V auf eine Meal-Karte einfuegen | 11294-11325 | 32 |
| index.html | Profil (lokal) & Teilen | 11326-11372 | 47 |
| index.html | Kontowechsel auf demselben Geraet | 11373-12120 | 748 |
| index.html | Kalorienrechner (Baustein 1: Tages-/Wochenbedarf → state.goal) | 12121-12211 | 91 |
| index.html | Wiegen: speichern, loeschen, ans Ziel koppeln | 12212-12285 | 74 |
| index.html | Erste Schritte (Onboarding) | 12286-13166 | 881 |
| index.html | Erscheinungsbild | 13167-13193 | 27 |
| index.html | Einstellungen | 13194-13317 | 124 |
| index.html | Einstieg (D1b) | 13318-13393 | 76 |
| index.html | Cloud-Anmeldung (Firebase) | 13394-13955 | 562 |
| index.html | Gemeinsam planen (Gruppe) | 13956-14981 | 1026 |
| index.html | Teilen ueber den nativen Dialog des Geraets (Web Share API) | 14982-15015 | 34 |
| index.html | Einkaufsliste als PDF (Paket B3) | 15016-15255 | 240 |
| index.html | Boot | 15256-15274 | 19 |
| lib/barcode.js | Barcode-Scan (Open Food Facts) | 14-163 | 150 |
| lib/pdf.js | PDF selbst erzeugen (kein window.print, sandbox-sicher) | 14-38 | 25 |
| lib/pdf.js | Marken-Kopf fuer die PDFs (Logo, "PADDY'S MEALPLAN", Slogan) | 39-106 | 68 |
| lib/pdf.js | Echtes Logo-PNG fuer die PDFs vorbereiten (einmalig, async, gecacht) | 107-241 | 135 |

## 4. Agenten

| Agent | Modell | Werkzeuge | Alle Werkzeuge? | Referenzierte Pfade |
|---|---|---|---|---|
| anwalt | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | bilder-protokoll.json, data/rechtstexte.js, docs/MODULE.md, docs/PRODUCT.md, docs/STORE.md, firestore.rules, img/bilder-protokoll.json, img/library/bilder-protokoll.json, index.html, tools/meal-bilder.py, worker/og.js |
| datenschutz-technik | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | worker/og.js |
| doku-waechter | sonnet | Read, Grep, Glob, Bash | nein | CLAUDE.md, dashboard.html, data/rechtstexte.js, docs/ARCHITECTURES.md, docs/PRODUCT.md, docs/TESTING.md, docs/TROUBLESHOOTING.md |
| kvp | haiku | Read, Grep, Glob, Bash | nein | css/mobil.css, css/tokens.css, index.html |
| lieferkette | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | ./firebase-app.js, firebase-app.js, index.html, lib/barcode.js, package.json, sw.js, tools/firebase-vendor.py, vendor/HERKUNFT.md, vendor/zxing.min.js |
| store-check | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | FIREBASE-SETUP.md, bilder-protokoll.json, docs/MODULE.md, docs/PRODUCT.md, docs/SECURITY.md, firestore.rules, index.html, manifest.webmanifest, sw.js |
| ux-reviewer | haiku | Read, Grep, Glob, Bash, Skill | nein | css/CLAUDE.md, css/basis.css, css/komponenten.css, css/mobil.css, css/tokens.css, docs/DESIGN.md |
| website-security | sonnet | Read, Grep, Glob, Bash | nein | FIREBASE-SETUP.md, dashboard.html, data/rechtstexte.js, docs/MODULE.md, docs/SECURITY.md, firestore.rules, index.html, lib/barcode.js, sw.js, tools/firebase-vendor.py, worker/og.js |

## 5. Skills

Nur die versionierten Skills des Projekts. Zugekaufte Skills liegen
ausserhalb des Repositories und gehoeren nicht zu seinem Zustand.

| Skill | Referenzierte Pfade |
|---|---|
| abnahme | docs/TESTING.md |
| deploy | .claude/hooks/push-waechter.py, firestore.rules, sw.js |
| pruefstand | data/cookbook.js, docs/TESTING.md, index.html, tools/quelle.py |
| rezeptcharge | CLAUDE.md, data/cookbook.js, data/foods.js, data/rechtstexte.js, docs/DESIGN.md, docs/PRODUCT.md, docs/TROUBLESHOOTING.md, img/library/bilder-protokoll.json, pruefstand-rezepttexte.py, quelle.py, rezept-makros.py, syntax-check.py, tools/pruefstand-rezepttexte.py, tools/quelle.py |
| smoke | dump.html |

## 6. Hooks

| Ereignis | Matcher | Kommando |
|---|---|---|
| PostToolUse | Edit|Write | `python "$CLAUDE_PROJECT_DIR/.claude/hooks/syntax-nach-edit.py"` |
| PreToolUse | Bash|PowerShell | `python "$CLAUDE_PROJECT_DIR/.claude/hooks/commit-waechter.py"` |
| PreToolUse | Bash|PowerShell | `python "$CLAUDE_PROJECT_DIR/.claude/hooks/secrets-filter.py"` |
| PreToolUse | Bash|PowerShell | `python "$CLAUDE_PROJECT_DIR/.claude/hooks/push-waechter.py"` |
| SessionStart | — | `python "$CLAUDE_PROJECT_DIR/.claude/hooks/wartung-erinnerung.py"` |

## 7. Externe Dienste

| Host |
|---|
| docs.github.com |
| firestore.googleapis.com |
| oauth2.googleapis.com |
| openai.com |
| opendatacommons.org |
| policies.google.com |
| schema.org |
| world.openfoodfacts.org |
| www.googleapis.com |
| www.paddysmealplan.de |

## 8. Datenbereiche

### Konstanten in `data/`

| Konstante | Datei |
|---|---|
| ACT_ICONS | data/ikonen.js |
| CAT_ICON | data/ikonen.js |
| CAT_PHOTO | data/bilder.js |
| COOKBOOK | data/cookbook.js |
| DATENSCHUTZ_HTML | data/rechtstexte.js |
| FOODS | data/foods.js |
| FOOD_ICON | data/ikonen.js |
| ICONS | data/ikonen.js |
| ICON_CHECK | data/ikonen.js |
| ICON_CHEV_L | data/ikonen.js |
| ICON_CHEV_R | data/ikonen.js |
| ICON_DUMBBELL | data/ikonen.js |
| ICON_FLAG | data/ikonen.js |
| ICON_FLAME | data/ikonen.js |
| ICON_GRIP | data/ikonen.js |
| ICON_PEOPLE | data/ikonen.js |
| IMPRESSUM_HTML_1 | data/rechtstexte.js |
| IMPRESSUM_HTML_2 | data/rechtstexte.js |
| MEAL_ICON | data/ikonen.js |
| PHOTOS | data/bilder.js |
| PHOTO_RULES | data/bilder.js |
| TOOL_ICONS | data/ikonen.js |

### localStorage

| Schluessel |
|---|
| wochenkueche |
| wochenkueche_lastprofile_v1 |
| wochenkueche_lastuid_v1 |
| wochenkueche_profile_v1 |
| wochenkueche_shop_v1 |
| wochenkueche_theme_v1 |
| wochenkueche_v1 |

### Firestore-Sammlungen

| Sammlung |
|---|
| databases |
| entitlements |
| groups |
| invites |
| loeschsperren |
| shared |
| users |

## 9. Abhaengigkeiten ueber Fassaden

`shared` ist hier keine Meinung, sondern eine Zaehlung: mehr als ein
Verbraucher.

| Fassade | Definiert in | Verbraucher | Shared |
|---|---|---|---|
| CloudAuth | index.html | — | nein |
| CloudEntitlement | index.html | — | nein |
| CloudGroup | index.html | — | nein |
| CloudShare | index.html | — | nein |
| CloudSync | index.html | — | nein |
| __onCloudAuth | index.html | — | nein |
| __onCloudWatchError | index.html | — | nein |
| noteError | index.html | — | nein |
| onerror | tools/probe-fortschritt.html, tools/probe-onboarding-fluss.html, tools/probe-onboarding.html, tools/probe-vergleich.html | — | nein |

## 10. Pruefabdeckung

Gelesen aus `docs/ABDECKUNG.md` - dort wird sie gepflegt, hier nur
angezeigt.

Bereiche ohne Pruefer: **0**

_keine_

## 11. Dateien

| Pfad | Zeilen | Bytes |
|---|---|---|
| .claude/Skills/abnahme/SKILL.md | 80 | 3793 |
| .claude/Skills/deploy/SKILL.md | 102 | 3702 |
| .claude/Skills/pruefstand/SKILL.md | 126 | 5263 |
| .claude/Skills/rezeptcharge/SKILL.md | 482 | 26234 |
| .claude/Skills/smoke/SKILL.md | 82 | 3368 |
| .claude/agents/anwalt.md | 283 | 16548 |
| .claude/agents/datenschutz-technik.md | 174 | 9879 |
| .claude/agents/doku-waechter.md | 106 | 5377 |
| .claude/agents/kvp.md | 162 | 9060 |
| .claude/agents/lieferkette.md | 124 | 6016 |
| .claude/agents/store-check.md | 176 | 9368 |
| .claude/agents/ux-reviewer.md | 71 | 3776 |
| .claude/agents/website-security.md | 195 | 10652 |
| .claude/commands/pushcheck.md | 70 | 2657 |
| .claude/hooks/commit-waechter.py | 178 | 8147 |
| .claude/hooks/push-waechter.py | 95 | 3107 |
| .claude/hooks/secrets-filter.py | 93 | 3856 |
| .claude/hooks/syntax-nach-edit.py | 100 | 3777 |
| .claude/hooks/wartung-erinnerung.py | 148 | 6318 |
| .claude/settings.json | 56 | 1526 |
| .gitattributes | 21 | 594 |
| .github/workflows/pruefung.yml | 188 | 8066 |
| .gitignore | 134 | 6081 |
| CLAUDE.md | 778 | 33879 |
| CNAME | 1 | 21 |
| FIREBASE-SETUP.md | 197 | 9363 |
| LICENSE | 40 | 1907 |
| README.md | 46 | 1990 |
| SECURITY.md | 71 | 3006 |
| css/CLAUDE.md | 92 | 4167 |
| css/basis.css | 1552 | 110429 |
| css/komponenten.css | 1347 | 102321 |
| css/mobil.css | 1073 | 70753 |
| css/tokens.css | 278 | 15313 |
| data/CLAUDE.md | 161 | 7419 |
| data/bilder.js | 142 | 9143 |
| data/cookbook.js | 569 | 52083 |
| data/foods.js | 244 | 17334 |
| data/ikonen.js | 168 | 19442 |
| data/rechtstexte.js | 184 | 30224 |
| docs/ABDECKUNG.md | 191 | 13235 |
| docs/ABNAHME-MENSCH.md | 139 | 7222 |
| docs/ARCHITECTURES.md | 3287 | 207605 |
| docs/BAUSTEINE.md | 103 | 10474 |
| docs/DESIGN.md | 1315 | 70119 |
| docs/MODULE.md | — | — (erzeugt) |
| docs/PRODUCT.md | 1746 | 99669 |
| docs/RUNBOOK.md | 249 | 10092 |
| docs/SECURITY.md | 580 | 34704 |
| docs/STORE.md | 509 | 29863 |
| docs/TESTING.md | 5315 | 314544 |
| docs/TROUBLESHOOTING.md | 6875 | 398812 |
| docs/module-index.json | — | — (erzeugt) |
| firestore.rules | 536 | 31035 |
| img/apple-touch-icon.png | — | 35163 |
| img/beef.webp | — | 56568 |
| img/bilder-protokoll.json | 310 | 34158 |
| img/bowl.webp | — | 66100 |
| img/braten.webp | — | 52854 |
| img/burger.webp | — | 36164 |
| img/cake.webp | — | 52430 |
| img/casserole.webp | — | 53922 |
| img/cheese.webp | — | 47208 |
| img/chicken.webp | — | 57634 |
| img/coffee.webp | — | 28810 |
| img/curry.webp | — | 55460 |
| img/drink.webp | — | 28074 |
| img/egg.webp | — | 51838 |
| img/fish.webp | — | 71190 |
| img/fruit.webp | — | 39242 |
| img/grain.webp | — | 68068 |
| img/hack.webp | — | 63916 |
| img/icecream.webp | — | 35520 |
| img/icon-192.png | — | 45024 |
| img/icon-512.png | — | 184703 |
| img/icon-maskable-512.png | — | 135906 |
| img/legumes.webp | — | 44934 |
| img/library/beeren-protein-shake-hafer.webp | — | 35192 |
| img/library/bilder-protokoll.json | 255 | 30987 |
| img/library/blumenkohl-curry-tofu.webp | — | 57510 |
| img/library/chia-pudding-soja-beeren.webp | — | 65746 |
| img/library/chili-rinderhack-bohnen.webp | — | 55492 |
| img/library/dattel-nuss-bissen.webp | — | 56126 |
| img/library/edamame-sesam-snack.webp | — | 37614 |
| img/library/eiweissshake-mit-whey-und-milch.webp | — | 23720 |
| img/library/garnelen-zucchini-tomaten.webp | — | 54210 |
| img/library/gruener-smoothie-spinat.webp | — | 33438 |
| img/library/haehnchen-bowl-brokkoli.webp | — | 45294 |
| img/library/haehnchen-brokkoli-auflauf.webp | — | 56092 |
| img/library/haehnchen-mit-pute-und-reis.webp | — | 52044 |
| img/library/haehnchen-zucchini-feta.webp | — | 73242 |
| img/library/huettenkaese-vollkornbrot.webp | — | 52688 |
| img/library/kichererbsen-curry-spinat.webp | — | 47438 |
| img/library/linsen-bolognese-vollkorn.webp | — | 50094 |
| img/library/ofen-feta-kichererbsen.webp | — | 66632 |
| img/library/ofengemuese-blech.webp | — | 68612 |
| img/library/ofenlachs-suesskartoffel.webp | — | 59954 |
| img/library/overnight-oats-soja-beeren.webp | — | 38496 |
| img/library/protein-pancakes-skyr.webp | — | 35382 |
| img/library/protein-pizza-schinken.webp | — | 64864 |
| img/library/protein-porridge-mit-beeren.webp | — | 56480 |
| img/library/putenpfanne-vollkornnudeln.webp | — | 70642 |
| img/library/quark-haferflocken-banane.webp | — | 40140 |
| img/library/quinoa-bowl-edamame.webp | — | 54642 |
| img/library/quinoa-salat-kichererbsen.webp | — | 36304 |
| img/library/rindersteak-mit-ofenkartoffeln.webp | — | 55732 |
| img/library/risotto-spargel.webp | — | 57342 |
| img/library/rotes-linsen-dal.webp | — | 52576 |
| img/library/ruehrei-avocadobrot.webp | — | 43314 |
| img/library/schoko-protein-quark.webp | — | 41272 |
| img/library/skyr-beeren-nuesse.webp | — | 36140 |
| img/library/thunfisch-quark-dip.webp | — | 34532 |
| img/library/tofu-gemuesepfanne.webp | — | 64756 |
| img/library/tofu-ruehrei-vollkornbrot.webp | — | 51236 |
| img/logo.png | — | 45014 |
| img/neutral.jpg | — | 55105 |
| img/noodle.webp | — | 50242 |
| img/nuts.webp | — | 58372 |
| img/og-image.png | — | 299103 |
| img/pancake.webp | — | 48268 |
| img/pasta.webp | — | 72582 |
| img/pizza.jpg | — | 78035 |
| img/porridge.jpg | — | 67793 |
| img/potato.webp | — | 62152 |
| img/rice.webp | — | 62776 |
| img/salad.jpg | — | 75064 |
| img/sandwich.jpg | — | 84388 |
| img/schnitzel.webp | — | 66698 |
| img/seafood.webp | — | 64814 |
| img/shake.webp | — | 30506 |
| img/skyr.webp | — | 32044 |
| img/soup.webp | — | 45500 |
| img/steak.webp | — | 50920 |
| img/stew.webp | — | 47176 |
| img/sushi.webp | — | 38390 |
| img/taco.webp | — | 60014 |
| img/toast.webp | — | 54984 |
| img/tofu.webp | — | 58128 |
| img/veggiepan.webp | — | 66886 |
| img/waffle.webp | — | 52546 |
| img/wrap.webp | — | 43594 |
| img/wurst.webp | — | 54064 |
| index.html | 15274 | 936854 |
| lib/barcode.js | 163 | 9247 |
| lib/basis.js | 21 | 836 |
| lib/pdf.js | 241 | 13120 |
| manifest.webmanifest | 22 | 798 |
| robots.txt | 5 | 75 |
| sitemap.xml | 7 | 173 |
| sw.js | 156 | 7192 |
| syntax-check.py | 382 | 16172 |
| test-server.ps1 | 66 | 2182 |
| tools/a11y-pruefung.py | 529 | 24702 |
| tools/abdeckung.py | 324 | 13049 |
| tools/abnahme-mobil.py | 949 | 43888 |
| tools/abnahme-plan-sortieren.py | 480 | 21478 |
| tools/abnahme-scan-kamera.py | 388 | 15468 |
| tools/abnahme-zutaten-sortieren.py | 458 | 20164 |
| tools/alle-pruefstaende.py | 226 | 9699 |
| tools/bausteine.py | 254 | 10401 |
| tools/bildsatz-stichworte.json | 1061 | 20704 |
| tools/cdp.py | 261 | 11294 |
| tools/dashboard.py | 392 | 15577 |
| tools/firebase-vendor.py | 75 | 2957 |
| tools/firestore-backup.py | 304 | 12982 |
| tools/firestore-restore.py | 270 | 10811 |
| tools/firestore_api.py | 325 | 14695 |
| tools/karte.py | 605 | 24255 |
| tools/konten-inaktiv.py | 233 | 9220 |
| tools/meal-bilder.py | 473 | 24139 |
| tools/mobilprobe-rezeptbuch.html | 146 | 8092 |
| tools/probe-farbstimmungen.html | 167 | 8797 |
| tools/probe-fortschritt.html | 351 | 20064 |
| tools/probe-onboarding-fluss.html | 270 | 14119 |
| tools/probe-onboarding.html | 191 | 9537 |
| tools/probe-symbole.html | 40 | 2266 |
| tools/probe-vergleich.html | 333 | 15049 |
| tools/pruefstand-als-naechstes.py | 303 | 15833 |
| tools/pruefstand-autoplaner.py | 1160 | 63981 |
| tools/pruefstand-bildstichworte.py | 357 | 17954 |
| tools/pruefstand-cache-reset.py | 202 | 8848 |
| tools/pruefstand-css-pfade.py | 95 | 3572 |
| tools/pruefstand-einkauf-gruppe.py | 305 | 15777 |
| tools/pruefstand-einkaufsliste.py | 803 | 38728 |
| tools/pruefstand-einladung-verbrauch.py | 232 | 11518 |
| tools/pruefstand-firestore-backup.py | 731 | 33982 |
| tools/pruefstand-foto-tokens.py | 89 | 3706 |
| tools/pruefstand-grpm-zoom.py | 220 | 8553 |
| tools/pruefstand-gruppe-anonymisieren.py | 446 | 19816 |
| tools/pruefstand-gruppe-aufloesen.py | 255 | 12273 |
| tools/pruefstand-gruppe-beitritt-cache.py | 253 | 11335 |
| tools/pruefstand-gruppe-plan-mitbringen.py | 318 | 14800 |
| tools/pruefstand-gruppe-sperre.py | 268 | 12117 |
| tools/pruefstand-gruppe-verlassen-dubletten.py | 342 | 17391 |
| tools/pruefstand-gruppenlimit.py | 243 | 11367 |
| tools/pruefstand-home-eine-seite.py | 405 | 22404 |
| tools/pruefstand-jahresumschalter.py | 234 | 9867 |
| tools/pruefstand-kalender-layout.py | 365 | 18822 |
| tools/pruefstand-kalender.py | 751 | 42159 |
| tools/pruefstand-katalog-plan.py | 539 | 25588 |
| tools/pruefstand-konten-inaktiv.py | 133 | 5890 |
| tools/pruefstand-konto-loeschsperre.py | 251 | 12278 |
| tools/pruefstand-kontowechsel.py | 215 | 9393 |
| tools/pruefstand-makro-abweichung.py | 125 | 6483 |
| tools/pruefstand-meal-symbol.py | 252 | 10879 |
| tools/pruefstand-mengenanzeige.py | 262 | 12448 |
| tools/pruefstand-messgrundlage.py | 84 | 3633 |
| tools/pruefstand-picker-quellen.py | 198 | 7217 |
| tools/pruefstand-plan-sortieren.py | 501 | 24539 |
| tools/pruefstand-reiter.py | 306 | 13267 |
| tools/pruefstand-rezept-id-format.py | 295 | 13133 |
| tools/pruefstand-rezeptbuch-ansicht.py | 188 | 10795 |
| tools/pruefstand-rezeptbuch-filter.py | 222 | 10222 |
| tools/pruefstand-rezeptbuch.py | 428 | 24044 |
| tools/pruefstand-rezepttexte.py | 576 | 28247 |
| tools/pruefstand-rueckblick-ziel.py | 283 | 13690 |
| tools/pruefstand-scan-packung.py | 291 | 11979 |
| tools/pruefstand-scan-zeile.py | 665 | 31959 |
| tools/pruefstand-share-frist.py | 185 | 8088 |
| tools/pruefstand-sheet-repaint.py | 273 | 14644 |
| tools/pruefstand-stueckliste.py | 219 | 8782 |
| tools/pruefstand-sync-abriss.py | 226 | 10106 |
| tools/pruefstand-waise-uids.py | 226 | 10687 |
| tools/pruefstand-weekstats-sync.py | 224 | 11329 |
| tools/pruefstand-wochenbeschriftung.py | 147 | 7387 |
| tools/pruefstand-wochenmaske.py | 375 | 21030 |
| tools/pruefstand-ziel-undefined.py | 186 | 8873 |
| tools/pruefstand-zurueck-taste.py | 352 | 16043 |
| tools/pruefstand-zutaten-sortieren.py | 400 | 19768 |
| tools/pruefstand-zuweisung-loeschen.py | 232 | 10378 |
| tools/pruefstand_lauf.py | 113 | 4894 |
| tools/quelle.py | 180 | 7137 |
| tools/regeln-live.py | 131 | 5770 |
| tools/regeln-pruefen.py | 61 | 2926 |
| tools/register.py | 155 | 6748 |
| tools/rezept-makros.py | 283 | 12324 |
| tools/schnappschuss.py | 159 | 7209 |
| tools/shared-aufraeumen.py | 115 | 3755 |
| tools/smoke-mit-daten.py | 145 | 8236 |
| tools/test-meal-bilder.py | 156 | 8295 |
| tools/vergleich-bausteine.js | 172 | 7429 |
| tools/vorfuehren.py | 120 | 4637 |
| tools/wartung-check.py | 631 | 29107 |
| vendor/HERKUNFT.md | 105 | 4816 |
| vendor/firebase/10.12.5/LICENSE | 203 | 11358 |
| vendor/firebase/10.12.5/README.md | 27 | 1063 |
| vendor/firebase/10.12.5/firebase-app.js | 5122 | 102248 |
| vendor/firebase/10.12.5/firebase-auth.js | 3 | 150915 |
| vendor/firebase/10.12.5/firebase-firestore.js | 3 | 437972 |
| vendor/zxing.min.js | 1 | 336008 |
| worker/og.js | 191 | 8916 |

