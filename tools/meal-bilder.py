#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meal-Bilder fuer die kuratierte Bibliothek erzeugen (OpenAI Images API).

WARUM NICHT ADOBE FIREFLY, obwohl es als einziger Anbieter eine vertragliche Freistellung
bei Urheberrechtsanspruechen bietet: Die Firefly Services API ist am 15.08.2026 in der Adobe
Developer Console geprueft worden - JEDER Firefly-Eintrag ist dort gesperrt, mit der
Begruendung "License required. Your organization does not have a license to access this API".
Sie laeuft ausschliesslich ueber Unternehmenslizenzen mit Vertriebsvertrag. Fuer rund 115
Bilder im Jahr steht das in keinem Verhaeltnis.

Das Restrisiko ohne Freistellung ist hier gering: Es geht um "Teller mit Essen von oben" -
keine Marken, keine Personen, keine ikonischen Kompositionen, deren Nachbildung jemand
einklagen wuerde.

Rechtlich zu wissen:
  * KI-Bilder haben in der EU keinen Urheberrechtsschutz (kein menschlicher Schoepfer).
    Massgeblich sind allein die Nutzungsbedingungen des Anbieters - bei OpenAI ist die
    kommerzielle Nutzung erlaubt.
  * Eine Kennzeichnungspflicht besteht NICHT: Der EU AI Act (Art. 50 Abs. 4, in Kraft seit
    02.08.2026) verlangt Offenlegung nur bei Deep Fakes - also Inhalten, die realen Personen,
    Orten oder Ereignissen aehneln. Ein generiertes Steak ist keiner.
    Gekennzeichnet wird trotzdem, in PHOTO_CREDITS - es kostet eine Zeile.

Keine neuen Abhaengigkeiten (CLAUDE.md §12): nur die Standardbibliothek und Pillow, das
ohnehin installiert ist. Absichtlich kein `requests`.

Zugangsdaten in .env im Projektwurzelverzeichnis (dort bereits gitignored):
    OPENAI_API_KEY=sk-...

Aufrufe:
    python tools/meal-bilder.py --probe                      # ein einziges Bild, Kostentest
    python tools/meal-bilder.py --dry-run --meals "Linsencurry" "Tofu-Bowl"
    python tools/meal-bilder.py --meals "Linsencurry" --varianten 3
    python tools/meal-bilder.py --datei meals.txt --out img/library
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from io import BytesIO
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------------------
# EINGEFROREN. Aendern heisst: Die Sammlung zerfaellt in sichtbar verschiedene Generationen.
# Wer diesen Block anfasst, muss ALLE Bilder neu erzeugen - sonst stehen im Rezeptbuch zwei
# Bildsprachen nebeneinander, und das sieht man auf den ersten Blick.
# ------------------------------------------------------------------------------------------
# Der erste Teil ist keine Geschmacksfrage, sondern folgt aus einer Messung: Die App zeigt
# Meal-Bilder in einem sehr breiten Streifen (.rimg ist 116 px hoch, die Karte 330-485 px
# breit - also 2,85:1 bis 4,18:1). Das breiteste Format, das das Modell liefert, ist 3:2.
# Beim Zuschneiden faellt deshalb knapp die Haelfte der Hoehe weg. Wenn oben oder unten
# etwas Wichtiges liegt, ist es in der App nicht mehr da.
# Ausgewaehlt am 15.08.2026 aus sechs Varianten, die an ZWEI Motiven verglichen wurden:
# einem Steak (sieht in jedem dunklen Stil gut aus) und einem Porridge (der schwierige Fall -
# hell, breiig, ohne Struktur). Ein Stil, der nur am Steak gewaehlt wird, faellt bei der
# Haelfte einer Bibliothek durch, die zu grossen Teilen vegetarisch und vegan ist.
#
# Die drei Bestandteile und warum sie zusammen funktionieren:
#   * dunkles Nussbaumholz - traegt die "professionelle" Anmutung (reine Studio-Optik auf
#     Weiss wirkte wie ein Katalog);
#   * HELLES Steingut darauf - der Kontrast ist der Grund, warum auch ein Porridge nicht im
#     Dunkeln absaeuft. Dunkles Geschirr auf dunklem Grund war die verworfene Variante B;
#   * 45-Grad-Seitenansicht - gibt Volumen und Tiefe. Bewusst in Kauf genommen: Bei
#     geschichteten Bowls verdeckt der Schuesselrand mehr als eine Draufsicht. Die Zutaten
#     stehen als Liste darunter, die Anmutung entscheidet ueber den ersten Eindruck.
STIL = ("the plate is exactly centered in the frame with equal space on the left and right, "
        "the dish fills the middle of the frame, "
        "generous empty margin at top and bottom, nothing important near the upper or lower edge, "
        "moody food photography, 45 degree side angle view, "
        "matte light ceramic plate, dark walnut wood table, "
        "soft directional side light from the left, gentle shadows, shallow depth of field, "
        "warm and appetizing, no text, no logos, no hands, no cutlery in frame")

# Zielverhaeltnis beim Zuschneiden. 2,4:1 ist der Mittelwert der gemessenen Darstellungen
# (Karte 2,85-4,18:1, Meal-Ansicht 2,10-4,91:1) - naeher an der App als das 1,5:1 des
# Modells, aber nicht so extrem, dass ein etwas anderes Layout das Bild sofort unbrauchbar
# macht. Zugeschnitten wird MITTIG; dafuer sorgt der Stil-Baustein oben fuer freie Raender.
ZUSCHNITT = 2.4

# Ebenfalls eingefroren: Ein anderes Modell erzeugt einen anderen Look. Nur bewusst wechseln
# - und dann alle Bilder neu.
MODELL = "gpt-image-2"
API_GENERATE = "https://api.openai.com/v1/images/generations"

# Querformat passt zu den Meal-Karten. Muss eine der vom Modell erlaubten Groessen sein.
GROESSE = "1536x1024"
# Auf diese Breite wird fuers Repo verkleinert. 1100 statt 800, weil die Meal-Ansicht auf
# dem Desktop bis zu 1080 CSS-Pixel breit wird - bei 800 waere sie sichtbar unscharf.
# Durch den Zuschnitt auf 2,4:1 bleibt die Dateigroesse trotzdem im selben Rahmen.
ZIEL_BREITE = 1100

# Kostenschutz: Ein Tippfehler darf nicht 500 Bilder erzeugen.
MAX_BILDER = 60

CREDIT_VORLAGE = {
    "urheber": "KI-generiert (OpenAI, %s)" % MODELL,
    "lizenz": "OpenAI Terms of Use (kommerzielle Nutzung erlaubt)",
    "lizenzUrl": "https://openai.com/policies/terms-of-use",
    "quelle": "generiert mit der OpenAI Images API"
}

# Herkunftsnachweis. Je Bild werden Prompt, Modell und Datum protokolliert - das ist der
# Beleg dafuer, WIE ein Bild entstanden ist. Er schuetzt vor keinem Anspruch, aber er
# belegt im Streitfall, dass nichts von fremden Seiten uebernommen wurde. Die Datei liegt
# neben den Bildern und wird mit eingecheckt (sie enthaelt keine Geheimnisse).
PROTOKOLL = "bilder-protokoll.json"


def lade_env():
    """Zugangsdaten aus .env oder aus der Umgebung. Nie ins Repo - .env ist gitignored."""
    pfad = WURZEL / ".env"
    if pfad.exists():
        for zeile in pfad.read_text(encoding="utf-8").splitlines():
            zeile = zeile.strip()
            if not zeile or zeile.startswith("#") or "=" not in zeile:
                continue
            k, v = zeile.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"\''))
    return os.environ.get("OPENAI_API_KEY")


# Geschirr nach Kategorie. Das Modell trifft es meistens von selbst, aber "meistens" ist bei
# 100 Bildern zu wenig - ein Porridge auf einem flachen Teller sieht falsch aus.
KAT_GESCHIRR = {
    "Frühstück": "in a bowl",
    "Hauptgericht": "on a plate",
    "Snack": "in a small bowl",
    "Dessert": "in a small bowl",
    "Beilage": "in a small bowl",
    "Getränk": "in a glass"
}

# Ausnahmen, die VOR der Kategorie greifen. Die Kategorie allein reicht nicht: "Rührei mit
# Avocado auf Vollkornbrot" ist Fruehstueck und bekaeme damit eine Schuessel - eine Scheibe
# Brot in einer Schuessel sieht falsch aus, und zwar sofort. Dasselbe bei Pancakes und
# Ofengemuese vom Blech. Bewusst nur wenige, sehr eindeutige Stichwoerter: Jede weitere
# Regel ist eine neue Gelegenheit fuer eine Teilwort-Kollision (CLAUDE.md §22).
NAME_GESCHIRR = [
    (("brot", "toast", "sandwich", "pancake", "pfannkuchen", "waffel", "steak", "blech"), "on a plate"),
    # Getrunken wird aus einem Glas, egal welche Kategorie das Rezept traegt. Aufgefallen am
    # Beispiel-Meal "Eiweissshake mit Whey und Milch": Es steht in der Kategorie SNACK und
    # bekam damit eine Schuessel - im Bild eine cremige Masse mit einem Haufen Pulver darauf.
    # Ein Shake, den man nicht trinken kann.
    (("shake", "smoothie", "saft", "limonade", "kaffee", "tee"), "in a glass"),
]

# Diaet-Hinweise. OHNE diese Zeilen legt das Modell aus Gewohnheit Fleisch in ein Curry,
# weil Currys meistens so aussehen - ein veganes Rezept mit Haehnchen im Bild ist bei einer
# App, die Veganer gezielt anspricht, kein Schoenheitsfehler, sondern ein Vertrauensbruch.
TAG_HINWEIS = {
    "vegan": "strictly vegan, no meat, no fish, no eggs, no dairy, no cheese",
    "vegetarisch": "vegetarian, no meat, no fish",
    "glutenfrei": "gluten free, no bread, no wheat pasta",
    "laktosefrei": "no milk, no cheese, no cream"
}


def haupt_zutaten(rezept, anzahl=4):
    """Die mengenmaessig groessten Zutaten - die beschreiben das Gericht.

    Die ersten vier aus der Liste zu nehmen hiesse womoeglich "Salz, Pfeffer, Olivenoel,
    Petersilie". Freitext-Zutaten ohne Menge (Gewuerze) fliegen deshalb raus, der Rest wird
    nach Menge sortiert. Stueckzahlen ("1 Paprika") werden hochgewichtet, weil 1 Stueck
    mengenmaessig neben 200 g Reis sonst untergeht, obwohl es sichtbar auf dem Teller liegt.
    """
    mit_menge = []
    for z in (rezept.get("ingredients") or []):
        if not isinstance(z, dict):
            continue                      # Freitext wie "Salz, Pfeffer" - nicht abbildbar
        name = str(z.get("name") or "").strip()
        menge = z.get("grams")
        if not name or not isinstance(menge, (int, float)) or menge <= 0:
            continue
        gewicht = menge * 80 if z.get("unit") == "st" else menge
        mit_menge.append((gewicht, name))
    mit_menge.sort(reverse=True)
    return [n for _, n in mit_menge[:anzahl]]


def prompt_fuer(name, zutaten=None, stil=None, kategorie=None, tags=None):
    """Der Gerichtname traegt die Bildidee, die Hauptzutaten schaerfen sie.

    Ohne Zutaten raet das Modell - "Bowl" kann alles sein. Mit den mengenmaessig groessten
    Zutaten wird daraus ein bestimmtes Gericht, und das Bild passt zum Rezept daneben.
    Deshalb entstehen die Bilder NACH den Rezepten, nicht davor.

    `stil` ueberschreibt den eingefrorenen Baustein - AUSSCHLIESSLICH fuer den einmaligen
    Stilvergleich vor dem Festlegen (--stil). Im Normalbetrieb nie benutzen: Zwei Bilder mit
    verschiedenen Stilen in derselben Sammlung sieht man sofort.
    """
    teile = [name]
    if zutaten:
        teile.append("with " + ", ".join(zutaten))
    # Diaet zuerst nach dem Gericht: Die Verneinungen sollen moeglichst weit vorn stehen,
    # weit hinten im Prompt werden sie erfahrungsgemaess schwaecher gewichtet.
    for t in (tags or []):
        if t in TAG_HINWEIS:
            teile.append(TAG_HINWEIS[t])
    geschirr = None
    n = name.lower()
    for woerter, wahl in NAME_GESCHIRR:
        if any(w in n for w in woerter):
            geschirr = wahl
            break
    if not geschirr and kategorie:
        geschirr = KAT_GESCHIRR.get(kategorie)
    if geschirr:
        teile.append(geschirr)
    teile.append(stil or STIL)
    return ", ".join(teile)


def generiere(key, prompt, anzahl):
    """Liefert die Rohdaten der erzeugten Bilder.

    Die API antwortet je nach Modell mit b64_json ODER mit einer URL - beides wird
    behandelt, damit ein Modellwechsel das Skript nicht stillschweigend zerlegt.
    """
    koerper = json.dumps({
        "model": MODELL,
        "prompt": prompt,
        "n": anzahl,
        "size": GROESSE
    }).encode()
    req = urllib.request.Request(API_GENERATE, data=koerper, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + key)
    with urllib.request.urlopen(req, timeout=180) as a:
        antwort = json.loads(a.read())
    roh = []
    for eintrag in antwort.get("data", []):
        if eintrag.get("b64_json"):
            import base64
            roh.append(base64.b64decode(eintrag["b64_json"]))
        elif eintrag.get("url"):
            with urllib.request.urlopen(eintrag["url"], timeout=120) as b:
                roh.append(b.read())
    return roh


def speichere_webp(roh, ziel):
    """Mittig auf das Zielverhaeltnis beschneiden, dann als WebP verkleinern.

    Der Zuschnitt passiert HIER und nicht in der App: object-fit: cover wuerde denselben
    Bereich wegschneiden, aber das Bild vorher vollstaendig laden - also mehrere hundert
    Kilobyte fuer Pixel, die niemand sieht. Ladezeit ist in dieser App ein Produktwert.
    """
    from PIL import Image
    bild = Image.open(BytesIO(roh)).convert("RGB")
    ziel_hoehe = round(bild.width / ZUSCHNITT)
    if ziel_hoehe < bild.height:
        oben = (bild.height - ziel_hoehe) // 2
        bild = bild.crop((0, oben, bild.width, oben + ziel_hoehe))
    if bild.width > ZIEL_BREITE:
        h = round(bild.height * ZIEL_BREITE / bild.width)
        bild = bild.resize((ZIEL_BREITE, h), Image.LANCZOS)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    bild.save(ziel, "WEBP", quality=82, method=6)
    return ziel.stat().st_size


def slug(name):
    """Dateiname aus dem Gerichtnamen.

    Mehrere Sonderzeichen hintereinander ergeben EINEN Bindestrich - "Bowl (vegan), scharf"
    wurde sonst zu "bowl-vegan--scharf". Aufgefallen im Pruefstand, nicht beim Lesen.
    """
    tausch = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"}
    s = "".join(tausch.get(z, z) for z in name).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def dateiname(auftrag):
    """Der Dateiname ohne Endung.

    Wenn das Rezept eine `id` mitbringt (COOKBOOK), gewinnt SIE - nicht der Gerichtname.
    Die id ist der dauerhafte Schluessel und aendert sich nie; ein Name darf sich aendern,
    und dann zeigte die App auf eine Datei, die es nicht mehr gibt. Durch slug() laeuft sie
    trotzdem, weil eine id einen Umlaut enthalten kann ("rührei-avocadobrot") und Umlaute
    in Dateinamen und URLs nur Aerger machen.
    """
    return slug(auftrag.get("id") or auftrag["name"])


def main():
    p = argparse.ArgumentParser(description="Meal-Bilder ueber die OpenAI Images API erzeugen")
    p.add_argument("--meals", nargs="+", help="Gerichtnamen")
    p.add_argument("--datei", help="Textdatei, ein Gerichtname je Zeile")
    p.add_argument("--rezepte", help="JSON-Datei mit fertigen Rezepten (Liste oder {recipes:[...]}). "
                                     "DER EMPFOHLENE WEG: Name, Hauptzutaten, Kategorie und Diaet-Tags "
                                     "gehen in den Prompt - das Bild passt dann zum Rezept.")
    p.add_argument("--nur-ohne-bild", action="store_true",
                   help="Aus --rezepte nur die ueberspringen, fuer die schon eine Datei existiert")
    p.add_argument("--varianten", type=int, default=2,
                   help="Bilder je Gericht (Standard 2 - rechne mit 30-50 %% Ausschuss)")
    p.add_argument("--out", default="img/library", help="Zielordner (Standard img/library)")
    p.add_argument("--dry-run", action="store_true", help="Nur die Prompts zeigen, nichts aufrufen")
    p.add_argument("--probe", action="store_true", help="Ein einziges Testbild erzeugen")
    p.add_argument("--stil", help="NUR fuer den einmaligen Stilvergleich: ueberschreibt den "
                                  "eingefrorenen Stil-Baustein. Im Normalbetrieb weglassen.")
    args = p.parse_args()

    # Ein Auftrag ist { name, zutaten, kategorie, tags } - aus --rezepte kommt alles davon,
    # aus --meals/--datei nur der Name.
    auftraege = [{"name": n} for n in (args.meals or [])]
    if args.datei:
        auftraege += [{"name": z.strip()} for z in
                      Path(args.datei).read_text(encoding="utf-8").splitlines() if z.strip()]
    if args.rezepte:
        roh = json.loads(Path(args.rezepte).read_text(encoding="utf-8"))
        liste = roh.get("recipes", roh) if isinstance(roh, dict) else roh
        for r in liste:
            if not isinstance(r, dict) or not r.get("name"):
                continue
            auftraege.append({
                "name": r["name"],
                "id": r.get("id"),
                "zutaten": haupt_zutaten(r),
                "kategorie": r.get("category"),
                "tags": r.get("tags") or []
            })
    if args.probe:
        auftraege = [{"name": "Rindersteak mit Ofenkartoffeln"}]
        args.varianten = 1
    if not auftraege:
        p.error("Keine Gerichte angegeben (--meals, --datei, --rezepte oder --probe)")

    if args.nur_ohne_bild:
        vorher = len(auftraege)
        auftraege = [a for a in auftraege
                     if not (WURZEL / args.out / (dateiname(a) + ".webp")).exists()]
        if vorher != len(auftraege):
            print("%d von %d haben schon ein Bild und werden uebersprungen.\n"
                  % (vorher - len(auftraege), vorher))

    gesamt = len(auftraege) * args.varianten
    if gesamt > MAX_BILDER:
        print("ABBRUCH: %d Bilder ueberschreiten die Grenze von %d." % (gesamt, MAX_BILDER))
        print("Das ist der Kostenschutz - teile den Lauf auf oder erhoehe MAX_BILDER bewusst.")
        return 1

    def prompt_von(a):
        return prompt_fuer(a["name"], a.get("zutaten"), args.stil, a.get("kategorie"), a.get("tags"))

    if args.dry_run:
        for a in auftraege:
            print("\n%s\n  %s" % (a["name"], prompt_von(a)))
        print("\n%d Bilder waeren das (%d Gerichte x %d Varianten)."
              % (gesamt, len(auftraege), args.varianten))
        return 0

    api_key = lade_env()
    if not api_key:
        print("Es fehlt der Zugangsschluessel. Lege im Projektwurzelverzeichnis eine .env an")
        print("(die ist bereits gitignored) mit:")
        print("    OPENAI_API_KEY=sk-...")
        print("Den Schluessel gibt es unter https://platform.openai.com/api-keys;")
        print("dort muss ausserdem Guthaben aufgeladen sein.")
        return 1

    from datetime import datetime, timezone
    ziel_ordner = WURZEL / args.out
    protokoll_pfad = ziel_ordner / PROTOKOLL
    protokoll = {}
    if protokoll_pfad.exists():
        protokoll = json.loads(protokoll_pfad.read_text(encoding="utf-8"))
    credits = {}
    for a in auftraege:
        name = a["name"]
        key = dateiname(a)
        prompt = prompt_von(a)
        print("\n%s" % name)
        try:
            bilder = generiere(api_key, prompt, args.varianten)
        except urllib.error.HTTPError as e:
            print("  FEHLER %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
            continue
        for i, roh in enumerate(bilder, 1):
            datei = "%s%s.webp" % (key, "" if len(bilder) == 1 else "-%d" % i)
            ziel = ziel_ordner / datei
            groesse = speichere_webp(roh, ziel)
            print("  %s  (%.0f KB)" % (ziel.relative_to(WURZEL), groesse / 1024))
            # Herkunftsnachweis: WAS wurde WOMIT und WANN erzeugt.
            protokoll[datei] = {
                "gericht": name, "prompt": prompt, "modell": MODELL,
                "groesse": GROESSE, "erzeugt": datetime.now(timezone.utc).isoformat(timespec="seconds")
            }
        credits[key] = dict(CREDIT_VORLAGE, titel=name)

    if protokoll:
        protokoll_pfad.parent.mkdir(parents=True, exist_ok=True)
        protokoll_pfad.write_text(json.dumps(protokoll, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\nHerkunftsnachweis: %s (%d Eintraege)" % (protokoll_pfad.relative_to(WURZEL), len(protokoll)))
        print("SICHTPRUEFUNG NICHT VERGESSEN: Bilder mit Text, Logos oder Marken aussortieren -")
        print("das ist der realistischste rechtliche Fallstrick, nicht das Motiv selbst.")

    if credits:
        print("\n--- Fuer PHOTO_CREDITS in index.html (PHOTOS muss dieselben Schluessel haben) ---")
        for k, v in credits.items():
            print('    %s: { titel: "%s", urheber: "%s", lizenz: "%s", lizenzUrl: "%s", quelle: "%s" },'
                  % (k, v["titel"], v["urheber"], v["lizenz"], v["lizenzUrl"], v["quelle"]))
        print("\nDie Bilder gehoeren NICHT in SHELL_ASSETS des Service Workers - sie kommen")
        print("cache-first bei Bedarf (sonst waechst das Precache um mehrere MB).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
