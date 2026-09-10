# -*- coding: utf-8 -*-
u"""Prueft, ob jede url(...) in css/ auf eine Datei zeigt, die es wirklich gibt.

Warum es diesen Pruefstand gibt: Am 10.09.2026 stand in css/tokens.css
`--logoL: url(img/logo.png)`. Relative URLs im CSS loesen gegen die CSS-DATEI auf, nicht
gegen das Dokument - der Pfad zeigte also auf css/img/logo.png, und die Datei liegt in
img/. Ergebnis: Das Markenlogo fehlte in der Kopfzeile, auf dem Willkommensschirm und im
Onboarding. Niemandem ist es aufgefallen, weil ein fehlendes Hintergrundbild keinen Fehler
wirft - die Flaeche bleibt einfach leer.

Die Falle ist heimtueckisch, weil derselbe Pfad in JavaScript RICHTIG ist: dort loest
fetch("img/logo.png") gegen index.html auf. In lib/pdf.js steht deshalb genau diese Zeile,
und sie funktioniert.

Aufruf:
    python tools/pruefstand-css-pfade.py
    python tools/pruefstand-css-pfade.py --gegenprobe
"""
import io
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_ORDNER = os.path.join(WURZEL, "css")
URL_MUSTER = re.compile(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""")


def verweise():
    u"""Alle url(...)-Verweise aus css/, als (Datei, Zeile, Rohpfad)."""
    raus = []
    for name in sorted(os.listdir(CSS_ORDNER)):
        if not name.endswith(".css"):
            continue
        pfad = os.path.join(CSS_ORDNER, name)
        with io.open(pfad, encoding="utf-8") as f:
            for nr, zeile in enumerate(f, 1):
                for _, roh in URL_MUSTER.findall(zeile):
                    raus.append((name, nr, roh.strip()))
    return raus


def pruefe(zusatz=None):
    u"""Liefert die Liste der Verweise, die ins Leere zeigen.

    zusatz: optionale Liste (Datei, Zeile, Rohpfad) fuer die Gegenprobe - so wird ein
    kuenstlicher Fehler geprueft, OHNE eine Datei im Repo anzufassen.
    """
    fehler = []
    for name, nr, roh in verweise() + (zusatz or []):
        if roh.startswith(("data:", "http://", "https://", "//", "#")):
            continue
        # Relativ zur CSS-Datei aufloesen - genau so macht es der Browser.
        ziel = os.path.normpath(os.path.join(CSS_ORDNER, roh.split("?")[0].split("#")[0]))
        if not os.path.isfile(ziel):
            fehler.append((name, nr, roh, os.path.relpath(ziel, WURZEL)))
    return fehler


def main():
    gegenprobe = "--gegenprobe" in sys.argv
    print(u"Pruefstand: Dateipfade in css/")
    print(u"=" * 62)

    fehler = pruefe()
    gesamt = len(verweise())
    print(u"%d url()-Verweise in css/ geprueft." % gesamt)
    for name, nr, roh, ziel in fehler:
        print(u"  ROT  css/%s:%d  url(%s)  ->  %s fehlt" % (name, nr, roh, ziel))
    if not fehler:
        print(u"  GRUEN  jeder Verweis zeigt auf eine vorhandene Datei.")
    print(u"")
    print(u"ERGEBNIS %d gruen, %d rot" % (gesamt - len(fehler), len(fehler)))

    if gegenprobe:
        print(u"")
        print(u"Gegenprobe: derselbe Pruefstand gegen einen bekannt falschen Pfad")
        print(u"-" * 62)
        # Genau der Fehler vom 10.09.2026, ohne eine Datei zu aendern.
        kuenstlich = pruefe([("tokens.css", 0, "img/logo.png")])
        neu = [f for f in kuenstlich if f not in fehler]
        if neu:
            print(u"  GRUEN  der Pruefstand faellt darueber:")
            for name, nr, roh, ziel in neu:
                print(u"         url(%s) -> %s fehlt" % (roh, ziel))
        else:
            print(u"  ROT    der Pruefstand hat den bekannten Fehler NICHT bemerkt.")
            return 2

    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
