#!/usr/bin/env python3
"""Holt die Firebase-ESM-Bundles von gstatic und legt sie unter vendor/ ab.

Warum lokal statt CDN:
  Apple lehnt Apps ab, die ausfuehrbaren Code zur Laufzeit nachladen (Richtlinie 2.5.2),
  und ein CDN-Abruf beim Kaltstart macht die App ohne Netz unbrauchbar. Mit den Dateien
  im Repo startet die Cloud-Anmeldung offline und ohne fremden Host.

Zwei Eingriffe, mehr nicht:
  1. In firebase-auth.js und firebase-firestore.js zeigt der Import auf die absolute
     gstatic-URL von firebase-app.js. Nur dieser eine Pfad wird auf "./firebase-app.js"
     umgeschrieben - sonst laedt der Browser das App-Modul doch wieder aus dem Netz,
     und zwar als ZWEITE Instanz neben der lokalen. Doppelte Instanz heisst: zwei
     getrennte Komponenten-Register, und getAuth(app) findet seine App nicht mehr.
  2. Die sourceMappingURL-Zeile faellt weg - die .map-Dateien liegen nicht bei, das
     gaebe nur 404 in den DevTools.

Bewusst NICHT angefasst: die Strings
    "https://www.gstatic.com/firebasejs/<version>/firebase-app.js"
in firebase-app.js selbst. Das sind keine Ladepfade, sondern der Komponentenname, unter
dem sich das Modul registriert und loggt. Wer sie "aufraeumt", benennt eine registrierte
Komponente um.

Aufruf:  python tools/firebase-vendor.py [version]
"""
import re
import sys
import pathlib
import urllib.request

VERSION = sys.argv[1] if len(sys.argv) > 1 else "10.12.5"
DATEIEN = ["firebase-app.js", "firebase-auth.js", "firebase-firestore.js"]

wurzel = pathlib.Path(__file__).resolve().parent.parent
ziel = wurzel / "vendor" / "firebase" / VERSION
ziel.mkdir(parents=True, exist_ok=True)

absolut = f"https://www.gstatic.com/firebasejs/{VERSION}/firebase-app.js"

for name in DATEIEN:
    url = f"https://www.gstatic.com/firebasejs/{VERSION}/{name}"
    with urllib.request.urlopen(url) as antwort:
        text = antwort.read().decode("utf-8")

    treffer = 0
    if name != "firebase-app.js":
        # Nur den Import umschreiben, nicht jedes Vorkommen: from"<url>"
        text, treffer = re.subn(
            r'from\s*"' + re.escape(absolut) + r'"',
            'from"./firebase-app.js"',
            text,
        )
        if treffer == 0:
            sys.exit(f"FEHLER: {name} enthaelt keinen Import auf {absolut} - "
                     "Bundle-Format geaendert, Skript pruefen.")

    text = re.sub(r"\n?//# sourceMappingURL=[^\n]*\n?", "\n", text)

    (ziel / name).write_text(text, encoding="utf-8")
    print(f"{name}: {len(text.encode('utf-8')):>7} Bytes, {treffer} Import umgeschrieben")

rest = []
for name in DATEIEN:
    inhalt = (ziel / name).read_text(encoding="utf-8")
    for m in re.finditer(r'from\s*["\'](https?://[^"\']+)["\']', inhalt):
        rest.append(f"{name} -> {m.group(1)}")

if rest:
    print("\nWARNUNG: es laedt weiterhin etwas aus dem Netz:")
    for z in rest:
        print("  " + z)
    sys.exit(1)

print(f"\nOK - vendor/firebase/{VERSION}/ laedt nichts mehr nach.")
