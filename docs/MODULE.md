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
| css/basis.css | Header | 20-224 | 205 |
| css/basis.css | Section head | 225-230 | 6 |
| css/basis.css | Buttons | 231-298 | 68 |
| css/basis.css | Week grid | 299-1007 | 709 |
| css/komponenten.css | Recipe grid | 8-261 | 254 |
| css/komponenten.css | Meal-Ansicht (openMealSheet) | 262-451 | 190 |
| css/komponenten.css | Empty state | 452-457 | 6 |
| css/komponenten.css | Modal | 458-782 | 325 |
| css/komponenten.css | Profil (Login) & Teilen | 783-876 | 94 |
| css/komponenten.css | Profilbild-Zuschnitt (Kreis-Crop) | 877-1073 | 197 |
| css/komponenten.css | PDF / Druck | 1074-1107 | 34 |
| css/mobil.css | Mobile / Smartphone | 8-796 | 789 |
| css/mobil.css | Gemeinsam planen (Gruppe) | 797-863 | 67 |
| data/bilder.js | Gerichtsfotos (eingebettet, nach Namen zugeordnet) | 11-134 | 124 |
| data/cookbook.js | Rezeptbuch | 11-569 | 559 |
| data/foods.js | Zutaten-Datenbank fuer die Suche | 11-236 | 226 |
| data/ikonen.js | Strich-Icons fuer die Kategorie-Ueberschriften | 11-76 | 66 |
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
| index.html | Wochen (aktuelle + naechste, an ISO-Kalenderwochen gebunden) | 1086-1462 | 377 |
| index.html | Gewichtsverlauf | 1463-1479 | 17 |
| index.html | B2: Der Verlauf rechnet in WOCHEN, nicht mehr in Monaten | 1480-1625 | 146 |
| index.html | Gedaechtnis des Auto-Planers (state.planned) | 1626-1673 | 48 |
| index.html | Grabsteine geloeschter Meals | 1674-1789 | 116 |
| index.html | Bilder in IndexedDB (Paket A3) | 1790-1879 | 90 |
| index.html | Cloud-Sync (Firestore) | 1880-1883 | 4 |
| index.html | Pro-Berechtigung (D1) | 1884-1932 | 49 |
| index.html | Gemeinsam planen: Gruppenmodus | 1933-2030 | 98 |
| index.html | Wochenplan flach <-> verschachtelt (fuer Gruppen-Dokumente) | 2031-2518 | 488 |
| index.html | Empfaenger fuer die Gruppe | 2519-3111 | 593 |
| index.html | Rezeptbuch: was zeigen, was ist schon uebernommen | 3112-3129 | 18 |
| index.html | Startmeals nach dem Onboarding | 3130-3190 | 61 |
| index.html | Einmalige Aufraeumung alter Dubletten (Teil 3 des Katalog-Umbaus, 17.08.2026) | 3191-3251 | 61 |
| index.html | Zahleneingabe: Rad am Handy, Tastatur am Rechner | 3252-3330 | 79 |
| index.html | Sicherheitsnetz fuer fremde Bilddaten | 3331-3431 | 101 |
| index.html | Bilder der kuratierten Bibliothek (img/library/) | 3432-3540 | 109 |
| index.html | Rendering | 3541-3645 | 105 |
| index.html | Nährwerte | 3646-3699 | 54 |
| index.html | Strukturierte Zutaten | 3700-3836 | 137 |
| index.html | Schnelleintrag: zaehlbare Lebensmittel | 3837-3926 | 90 |
| index.html | Kamerabild: Buehnenformat und Fokus | 3927-4135 | 209 |
| index.html | Trainingstage (Verbrauch je Einheit) | 4136-4617 | 482 |
| index.html | Merkmale: Anzeige (Nur-Lese-Zweig) und Eingabe (Bearbeiten-Zweig) | 4618-4652 | 35 |
| index.html | Handy-Karussell (Wochenplan, Wochenziele, Rechner) | 4653-5059 | 407 |
| index.html | „Ziele <Jahr>": Gewichtsverlauf als Jahresdiagramm | 5060-5517 | 458 |
| index.html | Fortschritt-Kalender (Paket 6, B7) | 5518-6417 | 900 |
| index.html | Zurueck-Taste (D5) | 6418-6493 | 76 |
| index.html | Modal | 6494-6578 | 85 |
| index.html | Wiegen | 6579-6757 | 179 |
| index.html | Ziel von Hand justieren (B4) | 6758-6870 | 113 |
| index.html | Bewegung: FLIP am Rechner, Bottom-Sheet am Handy | 6871-7016 | 146 |
| index.html | Nur-Lese-Zweig: keine Eingabefelder, kein Autosave, kein Loeschen | 7017-7095 | 79 |
| index.html | Bearbeiten-Zweig | 7096-7169 | 74 |
| index.html | Autosave: input mutiert nur lokal, change/blur committen, 1500ms Leerlauf-Timer als Netz | 7170-7377 | 208 |
| index.html | Foto: waehlen/aendern/entfernen, aktualisiert nur die offene Ansicht (photoDoneCb) | 7378-7406 | 29 |
| index.html | Zutaten-Zeilen (Name, Menge, Naehrwerte pro 100 g, Barcode-Scan) | 7407-7612 | 206 |
| index.html | Zutaten-Suche (ARIA-Combobox auf dem Namensfeld) | 7613-7942 | 330 |
| index.html | Picker | 7943-8282 | 340 |
| index.html | Shopping list | 8283-8494 | 212 |
| index.html | Vorkochen (C3) | 8495-8696 | 202 |
| index.html | Actions | 8697-8781 | 85 |
| index.html | Rechtstexte (Impressum / Datenschutz) | 8782-8814 | 33 |
| index.html | Auto-Wochenplaner (D2) | 8815-8921 | 107 |
| index.html | Wiederholung: was zuletzt dran war, rutscht nach hinten | 8922-8940 | 19 |
| index.html | Passt die Groesse zum Slot? | 8941-8947 | 7 |
| index.html | In der Gruppe: was zu MEHR Profilen passt, kommt weiter nach vorn | 8948-9325 | 378 |
| index.html | Toast | 9326-9335 | 10 |
| index.html | Toast mit Rueckgaengig (Paket B1) | 9336-9371 | 36 |
| index.html | Event delegation | 9372-9571 | 200 |
| index.html | Drag & drop between slots | 9572-9633 | 62 |
| index.html | Foto per Drag & Drop auf eine Meal-Karte (Desktop) | 9634-9665 | 32 |
| index.html | Foto per Strg+V auf eine Meal-Karte einfuegen | 9666-9697 | 32 |
| index.html | Profil (lokal) & Teilen | 9698-9744 | 47 |
| index.html | Kontowechsel auf demselben Geraet | 9745-10339 | 595 |
| index.html | Kalorienrechner (Baustein 1: Tages-/Wochenbedarf → state.goal) | 10340-10430 | 91 |
| index.html | Wiegen: speichern, loeschen, ans Ziel koppeln | 10431-10504 | 74 |
| index.html | Erste Schritte (Onboarding) | 10505-11216 | 712 |
| index.html | Erscheinungsbild | 11217-11243 | 27 |
| index.html | Einstellungen | 11244-11369 | 126 |
| index.html | Einstieg (D1b) | 11370-11445 | 76 |
| index.html | Cloud-Anmeldung (Firebase) | 11446-12005 | 560 |
| index.html | Gemeinsam planen (Gruppe) | 12006-12979 | 974 |
| index.html | Teilen ueber den nativen Dialog des Geraets (Web Share API) | 12980-13013 | 34 |
| index.html | Einkaufsliste als PDF (Paket B3) | 13014-13253 | 240 |
| index.html | Boot | 13254-13272 | 19 |
| lib/barcode.js | Barcode-Scan (Open Food Facts) | 14-153 | 140 |
| lib/pdf.js | PDF selbst erzeugen (kein window.print, sandbox-sicher) | 14-38 | 25 |
| lib/pdf.js | Marken-Kopf fuer die PDFs (Logo, "PADDY'S MEALPLAN", Slogan) | 39-106 | 68 |
| lib/pdf.js | Echtes Logo-PNG fuer die PDFs vorbereiten (einmalig, async, gecacht) | 107-241 | 135 |

## 4. Agenten

| Agent | Modell | Werkzeuge | Alle Werkzeuge? | Referenzierte Pfade |
|---|---|---|---|---|
| anwalt | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | data/bilder.js, data/rechtstexte.js, docs/MODULE.md, docs/PRODUCT.md, docs/STORE.md, firestore.rules, index.html, tools/meal-bilder.py, worker/og.js |
| datenschutz-technik | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | worker/og.js |
| doku-waechter | sonnet | Read, Grep, Glob, Bash | nein | CLAUDE.md, data/rechtstexte.js, docs/ARCHITECTURES.md, docs/PRODUCT.md, docs/TESTING.md, docs/TROUBLESHOOTING.md |
| kvp | haiku | Read, Grep, Glob, Bash | nein | css/mobil.css, css/tokens.css, index.html |
| lieferkette | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | ./firebase-app.js, firebase-app.js, index.html, lib/barcode.js, package.json, sw.js, tools/firebase-vendor.py, vendor/HERKUNFT.md, vendor/zxing.min.js |
| store-check | sonnet | Read, Grep, Glob, Bash, WebSearch, WebFetch | nein | FIREBASE-SETUP.md, docs/MODULE.md, docs/PRODUCT.md, docs/SECURITY.md, firestore.rules, index.html, manifest.webmanifest, sw.js |
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
| commons.wikimedia.org |
| creativecommons.org |
| docs.github.com |
| firestore.googleapis.com |
| oauth2.googleapis.com |
| openai.com |
| opendatacommons.org |
| policies.google.com |
| schema.org |
| stocksnap.io |
| world.openfoodfacts.org |
| www.flickr.com |
| www.googleapis.com |
| www.paddysmealplan.de |
| www.rawpixel.com |

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
| ICON_DUMBBELL | data/ikonen.js |
| ICON_FLAG | data/ikonen.js |
| ICON_PEOPLE | data/ikonen.js |
| IMPRESSUM_HTML_1 | data/rechtstexte.js |
| IMPRESSUM_HTML_2 | data/rechtstexte.js |
| MEAL_ICON | data/ikonen.js |
| PHOTOS | data/bilder.js |
| PHOTO_CREDITS | data/bilder.js |
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
| onerror | tools/probe-fortschritt.html, tools/sicht-dunkel.html, tools/sicht-hell.html | — | nein |

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
| .claude/Skills/rezeptcharge/SKILL.md | 482 | 26244 |
| .claude/Skills/smoke/SKILL.md | 82 | 3368 |
| .claude/agents/anwalt.md | 273 | 15770 |
| .claude/agents/datenschutz-technik.md | 174 | 9879 |
| .claude/agents/doku-waechter.md | 105 | 5302 |
| .claude/agents/kvp.md | 162 | 9060 |
| .claude/agents/lieferkette.md | 124 | 6016 |
| .claude/agents/store-check.md | 170 | 8925 |
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
| .gitignore | 114 | 4956 |
| CLAUDE.md | 678 | 28029 |
| CNAME | 1 | 21 |
| FIREBASE-SETUP.md | 197 | 9363 |
| LICENSE | 30 | 1364 |
| README.md | 46 | 1990 |
| SECURITY.md | 71 | 3006 |
| css/CLAUDE.md | 92 | 4167 |
| css/basis.css | 1007 | 73558 |
| css/komponenten.css | 1107 | 87302 |
| css/mobil.css | 863 | 56353 |
| css/tokens.css | 221 | 11084 |
| data/CLAUDE.md | 148 | 6658 |
| data/bilder.js | 134 | 14471 |
| data/cookbook.js | 569 | 52083 |
| data/foods.js | 236 | 16584 |
| data/ikonen.js | 76 | 8630 |
| data/rechtstexte.js | 163 | 27890 |
| docs/ABDECKUNG.md | 186 | 11050 |
| docs/ARCHITECTURES.md | 2775 | 174377 |
| docs/DESIGN.md | 377 | 13550 |
| docs/MODULE.md | — | — (erzeugt) |
| docs/PRODUCT.md | 1458 | 79147 |
| docs/RUNBOOK.md | 167 | 5665 |
| docs/SECURITY.md | 356 | 19197 |
| docs/STORE.md | 246 | 11876 |
| docs/TESTING.md | 3519 | 208012 |
| docs/TROUBLESHOOTING.md | 5496 | 315335 |
| docs/module-index.json | — | — (erzeugt) |
| firestore.rules | 416 | 23714 |
| img/apple-touch-icon.png | — | 35163 |
| img/beef.webp | — | 18750 |
| img/burger.webp | — | 17180 |
| img/cake.webp | — | 12206 |
| img/casserole.webp | — | 15062 |
| img/cheese.webp | — | 30690 |
| img/chicken.webp | — | 19368 |
| img/coffee.webp | — | 16304 |
| img/curry.webp | — | 19488 |
| img/drink.webp | — | 7948 |
| img/egg.webp | — | 16352 |
| img/fish.webp | — | 18264 |
| img/fruit.webp | — | 12870 |
| img/icecream.webp | — | 4984 |
| img/icon-192.png | — | 45024 |
| img/icon-512.png | — | 184703 |
| img/icon-maskable-512.png | — | 135906 |
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
| img/neutral.jpg | — | 26267 |
| img/noodle.webp | — | 17116 |
| img/og-image.png | — | 299103 |
| img/pancake.webp | — | 9678 |
| img/pasta.webp | — | 15086 |
| img/pizza.jpg | — | 25652 |
| img/porridge.jpg | — | 26250 |
| img/potato.webp | — | 26194 |
| img/rice.webp | — | 20660 |
| img/salad.jpg | — | 30336 |
| img/sandwich.jpg | — | 24921 |
| img/seafood.webp | — | 31854 |
| img/soup.webp | — | 20452 |
| img/steak.webp | — | 29984 |
| img/stew.webp | — | 17392 |
| img/sushi.webp | — | 24348 |
| img/taco.webp | — | 24782 |
| img/toast.webp | — | 15252 |
| img/waffle.webp | — | 33496 |
| img/wrap.webp | — | 29160 |
| index.html | 13272 | 820907 |
| lib/barcode.js | 153 | 8354 |
| lib/basis.js | 21 | 836 |
| lib/pdf.js | 241 | 13120 |
| manifest.webmanifest | 22 | 786 |
| robots.txt | 5 | 75 |
| sitemap.xml | 7 | 173 |
| sw.js | 141 | 6210 |
| syntax-check.py | 382 | 16172 |
| test-server.ps1 | 66 | 2182 |
| tools/abdeckung.py | 324 | 13049 |
| tools/alle-pruefstaende.py | 220 | 9230 |
| tools/cdp.py | 261 | 11294 |
| tools/firebase-vendor.py | 75 | 2957 |
| tools/karte.py | 605 | 24255 |
| tools/meal-bilder.py | 417 | 20204 |
| tools/mobilprobe-rezeptbuch.html | 146 | 8092 |
| tools/probe-fortschritt.html | 210 | 10834 |
| tools/pruefstand-autoplaner.py | 1160 | 63981 |
| tools/pruefstand-cache-reset.py | 202 | 8848 |
| tools/pruefstand-einkauf-gruppe.py | 305 | 15777 |
| tools/pruefstand-einkaufsliste.py | 800 | 38502 |
| tools/pruefstand-einladung-verbrauch.py | 232 | 11518 |
| tools/pruefstand-grpm-zoom.py | 220 | 8553 |
| tools/pruefstand-gruppe-aufloesen.py | 255 | 12273 |
| tools/pruefstand-gruppe-beitritt-cache.py | 253 | 11335 |
| tools/pruefstand-gruppe-plan-mitbringen.py | 318 | 14800 |
| tools/pruefstand-gruppe-verlassen-dubletten.py | 342 | 17391 |
| tools/pruefstand-gruppenlimit.py | 243 | 11367 |
| tools/pruefstand-jahresumschalter.py | 234 | 9867 |
| tools/pruefstand-kalender-layout.py | 252 | 11044 |
| tools/pruefstand-kalender.py | 370 | 17605 |
| tools/pruefstand-katalog-plan.py | 534 | 25271 |
| tools/pruefstand-kontowechsel.py | 215 | 9393 |
| tools/pruefstand-mengenanzeige.py | 262 | 12448 |
| tools/pruefstand-rezeptbuch-ansicht.py | 188 | 10795 |
| tools/pruefstand-rezeptbuch-filter.py | 222 | 10222 |
| tools/pruefstand-rezeptbuch.py | 428 | 24044 |
| tools/pruefstand-rezepttexte.py | 576 | 28247 |
| tools/pruefstand-rueckblick-ziel.py | 227 | 10088 |
| tools/pruefstand-sheet-repaint.py | 273 | 14644 |
| tools/pruefstand-sync-abriss.py | 226 | 10106 |
| tools/pruefstand-waise-uids.py | 226 | 10687 |
| tools/pruefstand-weekstats-sync.py | 208 | 10031 |
| tools/pruefstand-wochenbeschriftung.py | 145 | 7218 |
| tools/pruefstand-wochenmaske.py | 371 | 20614 |
| tools/pruefstand-ziel-undefined.py | 186 | 8873 |
| tools/pruefstand-zurueck-taste.py | 352 | 16043 |
| tools/pruefstand-zuweisung-loeschen.py | 232 | 10378 |
| tools/pruefstand_lauf.py | 113 | 4894 |
| tools/quelle.py | 180 | 7137 |
| tools/rezept-makros.py | 283 | 12324 |
| tools/sicht-dunkel.html | 212 | 10951 |
| tools/sicht-hell.html | 212 | 10950 |
| tools/smoke-mit-daten.py | 145 | 8236 |
| tools/test-meal-bilder.py | 144 | 7529 |
| tools/wartung-check.py | 493 | 22371 |
| vendor/HERKUNFT.md | 105 | 4621 |
| vendor/firebase/10.12.5/LICENSE | 203 | 11358 |
| vendor/firebase/10.12.5/README.md | 27 | 1063 |
| vendor/firebase/10.12.5/firebase-app.js | 5122 | 102248 |
| vendor/firebase/10.12.5/firebase-auth.js | 3 | 150915 |
| vendor/firebase/10.12.5/firebase-firestore.js | 3 | 437972 |
| vendor/zxing.min.js | 1 | 336008 |
| worker/og.js | 191 | 8916 |

