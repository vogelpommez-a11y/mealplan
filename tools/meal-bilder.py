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
STIL = ("top-down flat lay food photography, natural daylight from the left, "
        "matte light ceramic plate, light wooden table, soft shadows, shallow depth of field, "
        "fresh and appetizing, no text, no logos, no hands, no cutlery in frame")

# Ebenfalls eingefroren: Ein anderes Modell erzeugt einen anderen Look. Nur bewusst wechseln
# - und dann alle Bilder neu.
MODELL = "gpt-image-2"
API_GENERATE = "https://api.openai.com/v1/images/generations"

# Querformat passt zu den Meal-Karten. Muss eine der vom Modell erlaubten Groessen sein.
GROESSE = "1536x1024"
# Auf diese Breite wird fuers Repo verkleinert. 100 Bilder x ~70 KB bleiben so ertraeglich.
ZIEL_BREITE = 800

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


def prompt_fuer(name, zutaten=None):
    """Der Gerichtname traegt die Bildidee, die Hauptzutaten schaerfen sie.

    Ohne Zutaten raet das Modell - "Bowl" kann alles sein. Mit zwei, drei Hauptzutaten wird
    daraus ein bestimmtes Gericht, und das Bild passt zum Rezept daneben.
    """
    teile = [name]
    if zutaten:
        teile.append("with " + ", ".join(zutaten[:4]))
    teile.append(STIL)
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
    """Als WebP verkleinern - Ladezeit ist in dieser App ein Produktwert."""
    from PIL import Image
    bild = Image.open(BytesIO(roh)).convert("RGB")
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


def main():
    p = argparse.ArgumentParser(description="Meal-Bilder ueber die OpenAI Images API erzeugen")
    p.add_argument("--meals", nargs="+", help="Gerichtnamen")
    p.add_argument("--datei", help="Textdatei, ein Gerichtname je Zeile")
    p.add_argument("--varianten", type=int, default=2,
                   help="Bilder je Gericht (Standard 2 - rechne mit 30-50 %% Ausschuss)")
    p.add_argument("--out", default="img/library", help="Zielordner (Standard img/library)")
    p.add_argument("--dry-run", action="store_true", help="Nur die Prompts zeigen, nichts aufrufen")
    p.add_argument("--probe", action="store_true", help="Ein einziges Testbild erzeugen")
    args = p.parse_args()

    namen = list(args.meals or [])
    if args.datei:
        namen += [z.strip() for z in Path(args.datei).read_text(encoding="utf-8").splitlines() if z.strip()]
    if args.probe:
        namen = ["Rindersteak mit Ofenkartoffeln"]
        args.varianten = 1
    if not namen:
        p.error("Keine Gerichte angegeben (--meals, --datei oder --probe)")

    gesamt = len(namen) * args.varianten
    if gesamt > MAX_BILDER:
        print("ABBRUCH: %d Bilder ueberschreiten die Grenze von %d." % (gesamt, MAX_BILDER))
        print("Das ist der Kostenschutz - teile den Lauf auf oder erhoehe MAX_BILDER bewusst.")
        return 1

    if args.dry_run:
        for n in namen:
            print("\n%s\n  %s" % (n, prompt_fuer(n)))
        print("\n%d Bilder waeren das (%d Gerichte x %d Varianten)." % (gesamt, len(namen), args.varianten))
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
    for name in namen:
        key = slug(name)
        prompt = prompt_fuer(name)
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
