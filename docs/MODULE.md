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
| css/basis.css | Header | 20-229 | 210 |
| css/basis.css | Section head | 230-235 | 6 |
| css/basis.css | Buttons | 236-308 | 73 |
| css/basis.css | Week grid | 309-1379 | 1071 |
| css/komponenten.css | Recipe grid | 8-310 | 303 |
| css/komponenten.css | Meal-Ansicht (openMealSheet) | 311-507 | 197 |
| css/komponenten.css | Empty state | 508-513 | 6 |
| css/komponenten.css | Modal | 514-838 | 325 |
| css/komponenten.css | Profil (Login) & Teilen | 839-932 | 94 |
| css/komponenten.css | Profilbild-Zuschnitt (Kreis-Crop) | 933-1123 | 191 |
| css/komponenten.css | PDF / Druck | 1124-1157 | 34 |
| css/mobil.css | Mobile / Smartphone | 8-994 | 987 |
| css/mobil.css | Gemeinsam planen (Gruppe) | 995-1061 | 67 |
| data/bilder.js | Gerichtsfotos (nach Namen zugeordnet) | 11-142 | 132 |
| data/cookbook.js | Rezeptbuch | 11-569 | 559 |
| data/foods.js | Zutaten-Datenbank fuer die Suche | 11-244 | 234 |
| data/ikonen.js | Strich-Icons fuer die Kategorie-Ueberschriften | 11-89 | 79 |
| index.html | Cloud-Sync (Firestore): pro Nutzer ein Dokument users/{uid} | 433-466 | 34 |
| index.html | Fehlerbehandlung fuer onSnapshot | 467-494 | 28 |
| index.html | Pro-Berechtigung (D1): eigenes Dokument entitlements/{uid}, NUR lesbar | 495-544 | 50 |
| index.html | Rezepte: eigenes Dokument je Meal (users/{uid}/recipes/{id}) | 545-593 | 49 |
| index.html | Teilen per Cloud-Link: öffentlich lesbare Snapshots in shared/{id} | 594-602 | 9 |
| index.html | Gemeinsam planen: groups/{gid} mit Mitgliedern, Wochenplan und Meals | 603-655 | 53 |
| index.html | Mitglieder: ein Dokument je Person, damit Rollenrechte pro Dokument gelten | 656-685 | 30 |
| index.html | Mitgliederlimit: Beitritt und Austritt sind ATOMAR | 686-726 | 41 |
| index.html | Wochenplan | 727-753 | 27 |
| index.html | Einladungscodes | 754-786 | 33 |
| index.html | Testumgebung von den echten Daten trennen | 787-854 | 68 |
| index.html | Aktivitaet und Training (Stammdaten des Kalorienrechners) | 855-952 | 98 |
| index.html | Merkmale eines Meals (Tags, Meal-Prep) | 953-969 | 17 |
| index.html | Ernaehrungsprofil (state.goal.diet / state.goal.avoid) | 970-1036 | 67 |
| index.html | State | 1037-1085 | 49 |
| index.html | Wochen (aktuelle + naechste, an ISO-Kalenderwochen gebunden) | 1086-1488 | 403 |
| index.html | Gewichtsverlauf | 1489-1505 | 17 |
| index.html | B2: Der Verlauf rechnet in WOCHEN, nicht mehr in Monaten | 1506-1651 | 146 |
| index.html | Gedaechtnis des Auto-Planers (state.planned) | 1652-1699 | 48 |
| index.html | Grabsteine geloeschter Meals | 1700-1823 | 124 |
| index.html | Bilder in IndexedDB (Paket A3) | 1824-1913 | 90 |
| index.html | Cloud-Sync (Firestore) | 1914-1917 | 4 |
| index.html | Pro-Berechtigung (D1) | 1918-1966 | 49 |
| index.html | Gemeinsam planen: Gruppenmodus | 1967-2064 | 98 |
| index.html | Wochenplan flach <-> verschachtelt (fuer Gruppen-Dokumente) | 2065-2569 | 505 |
| index.html | Empfaenger fuer die Gruppe | 2570-3188 | 619 |
| index.html | Rezeptbuch: was zeigen, was ist schon uebernommen | 3189-3206 | 18 |
| index.html | Startmeals nach dem Onboarding | 3207-3267 | 61 |
| index.html | Einmalige Aufraeumung alter Dubletten (Teil 3 des Katalog-Umbaus, 17.08.2026) | 3268-3328 | 61 |
| index.html | Zahleneingabe: Rad am Handy, Tastatur am Rechner | 3329-3407 | 79 |
| index.html | Sicherheitsnetz fuer fremde Bilddaten | 3408-3508 | 101 |
| index.html | Bilder der kuratierten Bibliothek (img/library/) | 3509-3649 | 141 |
| index.html | Rendering | 3650-3754 | 105 |
| index.html | Nährwerte | 3755-3808 | 54 |
| index.html | Strukturierte Zutaten | 3809-3945 | 137 |
| index.html | Schnelleintrag: zaehlbare Lebensmittel | 3946-4035 | 90 |
| index.html | Kamerabild: Buehnenformat und Fokus | 4036-4244 | 209 |
| index.html | Trainingstage (Verbrauch je Einheit) | 4245-4835 | 591 |
| index.html | Merkmale: Anzeige (Nur-Lese-Zweig) und Eingabe (Bearbeiten-Zweig) | 4836-4870 | 35 |
| index.html | Handy-Karussell (Wochenplan, Wochenziele, Rechner) | 4871-5277 | 407 |
| index.html | „Ziele <Jahr>": Gewichtsverlauf als Jahresdiagramm | 5278-5653 | 376 |
| index.html | Fortschritt-Kalender (Paket 6, B7/B11) | 5654-6004 | 351 |
| index.html | Der eine Zeitraum fuer den ganzen Reiter (seit 03.09.2026) | 6005-6827 | 823 |
| index.html | Zurueck-Taste (D5) | 6828-6903 | 76 |
| index.html | Modal | 6904-6988 | 85 |
| index.html | Wiegen | 6989-7065 | 77 |
| index.html | Stepper (seit 03.09.2026) | 7066-7312 | 247 |
| index.html | Ziel von Hand justieren (B4) | 7313-7425 | 113 |
| index.html | Bewegung: FLIP am Rechner, Bottom-Sheet am Handy | 7426-7571 | 146 |
| index.html | Nur-Lese-Zweig: keine Eingabefelder, kein Autosave, kein Loeschen | 7572-7651 | 80 |
| index.html | Bearbeiten-Zweig | 7652-7730 | 79 |
| index.html | Autosave: input mutiert nur lokal, change/blur committen, 1500ms Leerlauf-Timer als Netz | 7731-7938 | 208 |
| index.html | Foto: waehlen/aendern/entfernen, aktualisiert nur die offene Ansicht (photoDoneCb) | 7939-7969 | 31 |
| index.html | Zutaten-Zeilen (Name, Menge, Naehrwerte pro 100 g, Barcode-Scan) | 7970-8179 | 210 |
| index.html | Zutaten-Suche (ARIA-Combobox auf dem Namensfeld) | 8180-8303 | 124 |
| index.html | Zutaten per Ziehen sortieren (Paket 3) | 8304-8743 | 440 |
| index.html | Picker | 8744-9098 | 355 |
| index.html | Shopping list | 9099-9310 | 212 |
| index.html | Vorkochen (C3) | 9311-9512 | 202 |
| index.html | Actions | 9513-9597 | 85 |
| index.html | Rechtstexte (Impressum / Datenschutz) | 9598-9619 | 22 |
| index.html | Auto-Wochenplaner (D2) | 9620-9726 | 107 |
| index.html | Wiederholung: was zuletzt dran war, rutscht nach hinten | 9727-9745 | 19 |
| index.html | Passt die Groesse zum Slot? | 9746-9752 | 7 |
| index.html | In der Gruppe: was zu MEHR Profilen passt, kommt weiter nach vorn | 9753-10130 | 378 |
| index.html | Toast | 10131-10140 | 10 |
| index.html | Toast mit Rueckgaengig (Paket B1) | 10141-10176 | 36 |
| index.html | Event delegation | 10177-10398 | 222 |
| index.html | Drag & drop between slots | 10399-10460 | 62 |
| index.html | Foto per Drag & Drop auf eine Meal-Karte (Desktop) | 10461-10492 | 32 |
| index.html | Foto per Strg+V auf eine Meal-Karte einfuegen | 10493-10524 | 32 |
| index.html | Profil (lokal) & Teilen | 10525-10571 | 47 |
| index.html | Kontowechsel auf demselben Geraet | 10572-11179 | 608 |
| index.html | Kalorienrechner (Baustein 1: Tages-/Wochenbedarf → state.goal) | 11180-11270 | 91 |
| index.html | Wiegen: speichern, loeschen, ans Ziel koppeln | 11271-11344 | 74 |
| index.html | Erste Schritte (Onboarding) | 11345-12197 | 853 |
| index.html | Erscheinungsbild | 12198-12224 | 27 |
| index.html | Einstellungen | 12225-12348 | 124 |
| index.html | Einstieg (D1b) | 12349-12424 | 76 |
| index.html | Cloud-Anmeldung (Firebase) | 12425-12984 | 560 |
| index.html | Gemeinsam planen (Gruppe) | 12985-13958 | 974 |
| index.html | Teilen ueber den nativen Dialog des Geraets (Web Share API) | 13959-13992 | 34 |
| index.html | Einkaufsliste als PDF (Paket B3) | 13993-14232 | 240 |
| index.html | Boot | 14233-14251 | 19 |
| lib/barcode.js | Barcode-Scan (Open Food Facts) | 14-157 | 144 |
| lib/pdf.js | PDF selbst erzeugen (kein window.print, sandbox-sicher) | 14-38 | 25 |
| lib/pdf.js | Marken-Kopf fuer die PDFs (Logo, "PADDY'S MEALPLAN", Slogan) | 39-106 | 68 |
| lib/pdf.js | Echtes Logo-PNG fuer die PDFs vorbereiten (einmalig, async, gecacht) | 107-241 | 135 |

## 4. Agenten

| Agent | Modell | Werkzeuge | Alle Werkzeuge? | Referenzierte Pfade |
|---|---|---|---|---|
| anwalt | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | bilder-protokoll.json, data/rechtstexte.js, docs/MODULE.md, docs/PRODUCT.md, docs/STORE.md, firestore.rules, img/bilder-protokoll.json, img/library/bilder-protokoll.json, index.html, tools/meal-bilder.py, worker/og.js |
| datenschutz-technik | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | worker/og.js |
| doku-waechter | sonnet | Read, Grep, Glob, Bash | nein | CLAUDE.md, data/rechtstexte.js, docs/ARCHITECTURES.md, docs/PRODUCT.md, docs/TESTING.md, docs/TROUBLESHOOTING.md |
| kvp | haiku | Read, Grep, Glob, Bash | nein | css/mobil.css, css/tokens.css, index.html |
| lieferkette | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | ./firebase-app.js, firebase-app.js, index.html, lib/barcode.js, package.json, sw.js, tools/firebase-vendor.py, vendor/HERKUNFT.md, vendor/zxing.min.js |
| store-check | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | FIREBASE-SETUP.md, bilder-protokoll.json, docs/MODULE.md, docs/PRODUCT.md, docs/SECURITY.md, firestore.rules, index.html, manifest.webmanifest, sw.js |
| ux-reviewer | haiku | Read, Grep, Glob, Bash, Skill | nein | css/CLAUDE.md, css/basis.css, css/komponenten.css, css/mobil.css, css/tokens.css, docs/DESIGN.md |
| website-security | sonnet | Read, Grep, Glob, Bash | nein | FIREBASE-SETUP.md, data/rechtstexte.js, docs/MODULE.md, docs/SECURITY.md, firestore.rules, index.html, lib/barcode.js, sw.js, tools/firebase-vendor.py, worker/og.js |

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
| ICONS | data/ikonen.js |
| ICON_CHECK | data/ikonen.js |
| ICON_CHEV_L | data/ikonen.js |
| ICON_CHEV_R | data/ikonen.js |
| ICON_DUMBBELL | data/ikonen.js |
| ICON_FLAG | data/ikonen.js |
| ICON_FLAME | data/ikonen.js |
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
| onerror | tools/probe-fortschritt.html, tools/probe-onboarding-fluss.html, tools/probe-onboarding.html | — | nein |

## 10. Pruefabdeckung

Gelesen aus `docs/ABDECKUNG.md` - dort wird sie gepflegt, hier nur
angezeigt.

Bereiche ohne Pruefer: **0**

_keine_

## 11. Dateien

| Pfad | Zeilen | Bytes |
|---|---|---|
| .claude/Skills/abnahme/SKILL.md | 80 | 3793 |
| .claude/Skills/deploy/SKILL.md | 101 | 3653 |
| .claude/Skills/pruefstand/SKILL.md | 126 | 5263 |
| .claude/Skills/rezeptcharge/SKILL.md | 482 | 26234 |
| .claude/Skills/smoke/SKILL.md | 82 | 3368 |
| .claude/agents/anwalt.md | 278 | 16133 |
| .claude/agents/datenschutz-technik.md | 174 | 9879 |
| .claude/agents/doku-waechter.md | 105 | 5302 |
| .claude/agents/kvp.md | 162 | 9060 |
| .claude/agents/lieferkette.md | 124 | 6016 |
| .claude/agents/store-check.md | 170 | 8958 |
| .claude/agents/ux-reviewer.md | 71 | 3776 |
| .claude/agents/website-security.md | 195 | 10650 |
| .claude/commands/pushcheck.md | 70 | 2657 |
| .claude/hooks/commit-waechter.py | 174 | 7835 |
| .claude/hooks/push-waechter.py | 95 | 3107 |
| .claude/hooks/secrets-filter.py | 93 | 3856 |
| .claude/hooks/syntax-nach-edit.py | 100 | 3777 |
| .claude/hooks/wartung-erinnerung.py | 145 | 6088 |
| .claude/settings.json | 56 | 1526 |
| .gitattributes | 21 | 594 |
| .github/workflows/pruefung.yml | 188 | 8066 |
| .gitignore | 115 | 4972 |
| CLAUDE.md | 688 | 28834 |
| CNAME | 1 | 21 |
| FIREBASE-SETUP.md | 197 | 9363 |
| LICENSE | 40 | 1907 |
| README.md | 46 | 1990 |
| SECURITY.md | 71 | 3006 |
| css/CLAUDE.md | 92 | 4167 |
| css/basis.css | 1379 | 98958 |
| css/komponenten.css | 1157 | 90097 |
| css/mobil.css | 1061 | 69933 |
| css/tokens.css | 239 | 12542 |
| data/CLAUDE.md | 161 | 7408 |
| data/bilder.js | 142 | 9143 |
| data/cookbook.js | 569 | 52083 |
| data/foods.js | 244 | 17334 |
| data/ikonen.js | 89 | 10187 |
| data/rechtstexte.js | 165 | 28069 |
| docs/ABDECKUNG.md | 187 | 11136 |
| docs/ARCHITECTURES.md | 3114 | 196475 |
| docs/DESIGN.md | 890 | 46697 |
| docs/MODULE.md | — | — (erzeugt) |
| docs/PRODUCT.md | 1667 | 94319 |
| docs/RUNBOOK.md | 167 | 5665 |
| docs/SECURITY.md | 454 | 26176 |
| docs/STORE.md | 381 | 19757 |
| docs/TESTING.md | 4403 | 262278 |
| docs/TROUBLESHOOTING.md | 6165 | 356228 |
| docs/module-index.json | — | — (erzeugt) |
| firestore.rules | 443 | 25570 |
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
| index.html | 14251 | 878836 |
| lib/barcode.js | 157 | 8756 |
| lib/basis.js | 21 | 836 |
| lib/pdf.js | 241 | 13120 |
| manifest.webmanifest | 22 | 798 |
| robots.txt | 5 | 75 |
| sitemap.xml | 7 | 173 |
| sw.js | 156 | 7192 |
| syntax-check.py | 382 | 16172 |
| test-server.ps1 | 66 | 2182 |
| tools/abdeckung.py | 324 | 13049 |
| tools/abnahme-zutaten-sortieren.py | 458 | 20164 |
| tools/alle-pruefstaende.py | 226 | 9699 |
| tools/bildsatz-stichworte.json | 1061 | 20704 |
| tools/cdp.py | 261 | 11294 |
| tools/firebase-vendor.py | 75 | 2957 |
| tools/karte.py | 605 | 24255 |
| tools/meal-bilder.py | 473 | 24139 |
| tools/mobilprobe-rezeptbuch.html | 146 | 8092 |
| tools/probe-fortschritt.html | 351 | 20064 |
| tools/probe-onboarding-fluss.html | 270 | 14119 |
| tools/probe-onboarding.html | 191 | 9537 |
| tools/pruefstand-als-naechstes.py | 303 | 15833 |
| tools/pruefstand-autoplaner.py | 1160 | 63981 |
| tools/pruefstand-bildstichworte.py | 344 | 17071 |
| tools/pruefstand-cache-reset.py | 202 | 8848 |
| tools/pruefstand-css-pfade.py | 95 | 3572 |
| tools/pruefstand-einkauf-gruppe.py | 305 | 15777 |
| tools/pruefstand-einkaufsliste.py | 800 | 38502 |
| tools/pruefstand-einladung-verbrauch.py | 232 | 11518 |
| tools/pruefstand-grpm-zoom.py | 220 | 8553 |
| tools/pruefstand-gruppe-aufloesen.py | 255 | 12273 |
| tools/pruefstand-gruppe-beitritt-cache.py | 253 | 11335 |
| tools/pruefstand-gruppe-plan-mitbringen.py | 318 | 14800 |
| tools/pruefstand-gruppe-verlassen-dubletten.py | 342 | 17391 |
| tools/pruefstand-gruppenlimit.py | 243 | 11367 |
| tools/pruefstand-home-eine-seite.py | 405 | 22404 |
| tools/pruefstand-jahresumschalter.py | 234 | 9867 |
| tools/pruefstand-kalender-layout.py | 365 | 18822 |
| tools/pruefstand-kalender.py | 741 | 41592 |
| tools/pruefstand-katalog-plan.py | 534 | 25271 |
| tools/pruefstand-kontowechsel.py | 215 | 9393 |
| tools/pruefstand-mengenanzeige.py | 262 | 12448 |
| tools/pruefstand-rezept-id-format.py | 295 | 13133 |
| tools/pruefstand-rezeptbuch-ansicht.py | 188 | 10795 |
| tools/pruefstand-rezeptbuch-filter.py | 222 | 10222 |
| tools/pruefstand-rezeptbuch.py | 428 | 24044 |
| tools/pruefstand-rezepttexte.py | 576 | 28247 |
| tools/pruefstand-rueckblick-ziel.py | 283 | 13690 |
| tools/pruefstand-scan-packung.py | 291 | 11979 |
| tools/pruefstand-sheet-repaint.py | 273 | 14644 |
| tools/pruefstand-stueckliste.py | 177 | 6652 |
| tools/pruefstand-sync-abriss.py | 226 | 10106 |
| tools/pruefstand-waise-uids.py | 226 | 10687 |
| tools/pruefstand-weekstats-sync.py | 224 | 11329 |
| tools/pruefstand-wochenbeschriftung.py | 147 | 7387 |
| tools/pruefstand-wochenmaske.py | 375 | 21030 |
| tools/pruefstand-ziel-undefined.py | 186 | 8873 |
| tools/pruefstand-zurueck-taste.py | 352 | 16043 |
| tools/pruefstand-zutaten-sortieren.py | 395 | 19317 |
| tools/pruefstand-zuweisung-loeschen.py | 232 | 10378 |
| tools/pruefstand_lauf.py | 113 | 4894 |
| tools/quelle.py | 180 | 7137 |
| tools/rezept-makros.py | 283 | 12324 |
| tools/smoke-mit-daten.py | 145 | 8236 |
| tools/test-meal-bilder.py | 156 | 8295 |
| tools/wartung-check.py | 493 | 22371 |
| vendor/HERKUNFT.md | 105 | 4621 |
| vendor/firebase/10.12.5/LICENSE | 203 | 11358 |
| vendor/firebase/10.12.5/README.md | 27 | 1063 |
| vendor/firebase/10.12.5/firebase-app.js | 5122 | 102248 |
| vendor/firebase/10.12.5/firebase-auth.js | 3 | 150915 |
| vendor/firebase/10.12.5/firebase-firestore.js | 3 | 437972 |
| vendor/zxing.min.js | 1 | 336008 |
| worker/og.js | 191 | 8916 |

