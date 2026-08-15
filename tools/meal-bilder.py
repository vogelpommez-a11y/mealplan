#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meal-Bilder ueber die Adobe Firefly Services API erzeugen.

Warum Firefly und nicht ein anderer Anbieter: Firefly ist auf ausschliesslich lizenziertem
Material trainiert und bietet als einziger eine vertragliche Freistellung bei
Urheberrechtsanspruechen. Bei einem Produkt mit Impressum und zwei Store-Einreichungen ist
das den Aufpreis wert (~0,02 $/Bild, Stand August 2026).

Rechtlich zu wissen:
  * KI-Bilder haben in der EU keinen Urheberrechtsschutz (kein menschlicher Schoepfer).
    Massgeblich sind allein die Nutzungsbedingungen des Anbieters.
  * Eine Kennzeichnungspflicht besteht NICHT: Der EU AI Act (Art. 50 Abs. 4, in Kraft seit
    02.08.2026) verlangt Offenlegung nur bei Deep Fakes - also Inhalten, die realen Personen,
    Orten oder Ereignissen aehneln. Ein generiertes Steak ist keiner.
    Gekennzeichnet wird trotzdem, in PHOTO_CREDITS - es kostet eine Zeile.

Keine neuen Abhaengigkeiten (CLAUDE.md §12): nur die Standardbibliothek und Pillow, das
ohnehin installiert ist. Absichtlich kein `requests`.

Zugangsdaten in .env im Projektwurzelverzeichnis (dort bereits gitignored):
    FIREFLY_CLIENT_ID=...
    FIREFLY_CLIENT_SECRET=...

Aufrufe:
    python tools/meal-bilder.py --probe                      # ein einziges Bild, Kostentest
    python tools/meal-bilder.py --dry-run --meals "Linsencurry" "Tofu-Bowl"
    python tools/meal-bilder.py --meals "Linsencurry" --varianten 3
    python tools/meal-bilder.py --datei meals.txt --out img/library
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
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
MODELL = "firefly_v3"
API_GENERATE = "https://firefly-api.adobe.io/v3/images/generate"
API_TOKEN = "https://ims-na1.adobelogin.com/ims/token/v3"
SCOPE = "openid,AdobeID,firefly_api,ff_apis"

# 1408x1024 ist das 4:3-nahe Format aus den erlaubten Groessen - passt zu den Meal-Karten.
BREITE, HOEHE = 1408, 1024
# Auf diese Breite wird fuers Repo verkleinert. 100 Bilder x ~70 KB bleiben so ertraeglich.
ZIEL_BREITE = 800

# Kostenschutz: Ein Tippfehler darf nicht 500 Bilder erzeugen.
MAX_BILDER = 60

CREDIT_VORLAGE = {
    "urheber": "KI-generiert (Adobe Firefly, %s)" % MODELL,
    "lizenz": "Adobe Firefly Nutzungsbedingungen (kommerzielle Nutzung erlaubt)",
    "lizenzUrl": "https://www.adobe.com/legal/licenses-terms/adobe-gen-ai-user-guidelines.html",
    "quelle": "generiert mit Adobe Firefly Services API"
}


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
    cid = os.environ.get("FIREFLY_CLIENT_ID")
    secret = os.environ.get("FIREFLY_CLIENT_SECRET")
    return cid, secret


def hole_token(cid, secret):
    """Zugriffstoken von Adobe IMS. 24 h gueltig - fuer einen Lauf genuegt eines."""
    daten = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": secret,
        "scope": SCOPE
    }).encode()
    req = urllib.request.Request(API_TOKEN, data=daten, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as a:
        return json.loads(a.read())["access_token"]


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


def generiere(token, cid, prompt, anzahl):
    """Liefert die URLs der erzeugten Bilder."""
    koerper = json.dumps({
        "prompt": prompt,
        "numVariations": anzahl,
        "size": {"width": BREITE, "height": HOEHE}
    }).encode()
    req = urllib.request.Request(API_GENERATE, data=koerper, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("x-api-key", cid)
    req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=120) as a:
        antwort = json.loads(a.read())
    return [o["image"]["url"] for o in antwort.get("outputs", [])]


def speichere_webp(url, ziel):
    """Herunterladen und als WebP verkleinern - Ladezeit ist in dieser App ein Produktwert."""
    from PIL import Image
    with urllib.request.urlopen(url, timeout=120) as a:
        roh = a.read()
    bild = Image.open(BytesIO(roh)).convert("RGB")
    if bild.width > ZIEL_BREITE:
        h = round(bild.height * ZIEL_BREITE / bild.width)
        bild = bild.resize((ZIEL_BREITE, h), Image.LANCZOS)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    bild.save(ziel, "WEBP", quality=82, method=6)
    return ziel.stat().st_size


def slug(name):
    tausch = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"}
    s = "".join(tausch.get(z, z) for z in name).lower()
    return "".join(z if z.isalnum() else "-" for z in s).strip("-").replace("--", "-")


def main():
    p = argparse.ArgumentParser(description="Meal-Bilder ueber Adobe Firefly erzeugen")
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

    cid, secret = lade_env()
    if not cid or not secret:
        print("Es fehlen die Zugangsdaten. Lege im Projektwurzelverzeichnis eine .env an")
        print("(die ist bereits gitignored) mit:")
        print("    FIREFLY_CLIENT_ID=...")
        print("    FIREFLY_CLIENT_SECRET=...")
        print("Beides steht in der Adobe Developer Console unter deinem Firefly-Projekt")
        print("(Berechtigungsart: OAuth Server-to-Server).")
        return 1

    print("Hole Zugriffstoken ...")
    try:
        token = hole_token(cid, secret)
    except urllib.error.HTTPError as e:
        print("Token abgelehnt (%s). Stimmen Client-ID und Secret?" % e.code)
        print(e.read().decode("utf-8", "replace")[:400])
        return 1

    ziel_ordner = WURZEL / args.out
    credits = {}
    for name in namen:
        key = slug(name)
        print("\n%s" % name)
        try:
            urls = generiere(token, cid, prompt_fuer(name), args.varianten)
        except urllib.error.HTTPError as e:
            print("  FEHLER %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
            continue
        for i, u in enumerate(urls, 1):
            ziel = ziel_ordner / ("%s%s.webp" % (key, "" if len(urls) == 1 else "-%d" % i))
            groesse = speichere_webp(u, ziel)
            print("  %s  (%.0f KB)" % (ziel.relative_to(WURZEL), groesse / 1024))
        credits[key] = dict(CREDIT_VORLAGE, titel=name)

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
