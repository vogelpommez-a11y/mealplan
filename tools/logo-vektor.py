# -*- coding: utf-8 -*-
u"""Zeichnet das App-Logo als Vektor nach: img/logo.svg aus img/icon-512.png.

    python tools/logo-vektor.py            # schreibt img/logo.svg UND das Inline-Logo des
                                           # Startbildschirms in index.html (LOGO-SVG-Marken)
    python tools/logo-vektor.py --pruefen  # zeigt nur, welche Teile gefunden wurden

Warum
-----
Das Logo lag nur als 220-px-PNG vor (img/logo.png). Auf einem iPhone braucht es bei 116 CSS-px
rund 350 Geraetepixel - es war hochgerechnet und damit weich. Eine groessere Vorlage gibt es
nicht; auch icon-512.png ist schon hochgerechnet.

Wie
---
Die weissen Flaechen werden aus icon-512.png abgenommen, NICHT von Hand nachgebaut: viermal
vergroessert, leicht weichgezeichnet, an der 50-%-Kante geschnitten (OpenCV findContours),
die Punkte geglaettet und als Catmull-Rom-Kurven geschrieben. Der Kreis ist ein echter
<circle> in der Originalfarbe.

Jedes Teil ist ein eigener Pfad: lg-kreis, lg-muetze-rand (weisser Umriss), lg-muetze
(Fuellung), lg-stange, lg-scheiben-l, lg-scheiben-r - in der Datei als id, im Startbildschirm
als Klasse, damit er sie einzeln bewegen kann (css/komponenten.css, Erst-Intro).
img/logo.png bleibt unveraendert liegen - der PDF-Export braucht ein Rasterbild (lib/pdf.js).
"""
import argparse, io, os, sys
import cv2
import numpy as np

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(WURZEL, "img", "icon-512.png")
ZIEL = os.path.join(WURZEL, "img", "logo.svg")
ROT = "#FD2A3B"     # haeufigste Farbe im Kreis von icon-512.png
FAKTOR = 4          # Arbeitsaufloesung 2048 px - die Kante liegt damit auf Viertelpixeln


def weiss_maske():
    bild = cv2.imread(QUELLE, cv2.IMREAD_UNCHANGED)
    if bild is None:
        raise SystemExit("Quelle fehlt: " + QUELLE)
    bgr = bild[:, :, :3].astype(np.float32)
    # Weiss ist dort, wo der GRUENanteil hoch ist: im Rot (#FD2A3B) liegt er bei 42,
    # in Weiss bei 255. Auf dem transparenten Rand ist er egal - dort liegt kein Weiss.
    g = bgr[:, :, 1]
    gross = cv2.resize(g, None, fx=FAKTOR, fy=FAKTOR, interpolation=cv2.INTER_CUBIC)
    gross = cv2.GaussianBlur(gross, (0, 0), FAKTOR * 0.9)
    return (gross > (42 + 255) / 2).astype(np.uint8) * 255


def gleichmaessig(pkte, abstand=1.0):
    u"""Verteilt die Punkte einer geschlossenen Kontur gleichmaessig ueber ihre Laenge.
    Ungleiche Abstaende sind das, was Kurven ueberschiessen und Zacken bilden laesst."""
    zu = np.vstack([pkte, pkte[:1]])
    seg = np.hypot(*np.diff(zu, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(8, int(s[-1] / abstand))
    t = np.linspace(0, s[-1], n, endpoint=False)
    return np.stack([np.interp(t, s, zu[:, 0]), np.interp(t, s, zu[:, 1])], axis=1)


def glaetten(pkte, sigma=3.0):
    u"""Gauss-Glaettung ueber eine geschlossene Kontur - nimmt Treppe und Wackeln heraus.
    sigma in Arbeitspixeln (bei FAKTOR 4 also 0,75 px im 512er Logo)."""
    k = int(sigma * 3)
    if len(pkte) < k * 2 + 1:
        return pkte
    x = np.arange(-k, k + 1)
    kern = np.exp(-x ** 2 / (2 * sigma ** 2)); kern /= kern.sum()
    erw = np.concatenate([pkte[-k:], pkte, pkte[:k]])
    return np.stack([np.convolve(erw[:, 0], kern, mode="valid"),
                     np.convolve(erw[:, 1], kern, mode="valid")], axis=1)


def pfad(kontur):
    u"""Geschlossene Kontur -> SVG-Pfad aus zentripetalen Catmull-Rom-Kurven (als Bezier).

    Zentripetal (alpha 0,5) statt uniform: Die uniforme Form schiesst bei ungleich langen
    Nachbarstrecken ueber und bildet genau die kleinen Hoerner, die an den Hantelscheiben
    im ersten Entwurf zu sehen waren (Yuksel u. a., "Parameterization and Applications of
    Catmull-Rom Curves", 2011)."""
    p = kontur.reshape(-1, 2).astype(np.float64)
    p = glaetten(gleichmaessig(p))
    # Ausduennen: approxPolyDP haelt die Form auf 0,8 Arbeitspixel (= 0,2 px bei 512).
    p = cv2.approxPolyDP(p.astype(np.float32).reshape(-1, 1, 2), 0.8, True).reshape(-1, 2)
    p = p.astype(np.float64) / FAKTOR
    n = len(p)
    teile = ["M%.2f %.2f" % tuple(p[0])]
    for i in range(n):
        p0, p1, p2, p3 = p[(i - 1) % n], p[i], p[(i + 1) % n], p[(i + 2) % n]
        d1 = max(np.hypot(*(p1 - p0)), 1e-6) ** 0.5
        d2 = max(np.hypot(*(p2 - p1)), 1e-6) ** 0.5
        d3 = max(np.hypot(*(p3 - p2)), 1e-6) ** 0.5
        c1 = (d1 ** 2 * p2 - d2 ** 2 * p0 + (2 * d1 ** 2 + 3 * d1 * d2 + d2 ** 2) * p1) / (3 * d1 * (d1 + d2))
        c2 = (d3 ** 2 * p1 - d2 ** 2 * p3 + (2 * d3 ** 2 + 3 * d3 * d2 + d2 ** 2) * p2) / (3 * d3 * (d3 + d2))
        teile.append("C%.2f %.2f %.2f %.2f %.2f %.2f" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    return "".join(teile) + "Z"


def konturen():
    maske = weiss_maske()
    ks, hier = cv2.findContours(maske, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    hier = hier[0]
    stuecke = []   # (aussen, [loecher], bbox in 512er Koordinaten)
    for i, k in enumerate(ks):
        if hier[i][3] != -1:
            continue                      # Loch - kommt mit seinem Aussenumriss
        if cv2.contourArea(k) < (FAKTOR * 6) ** 2:
            continue                      # Krümel
        loecher = []
        j = hier[i][2]
        while j != -1:
            if cv2.contourArea(ks[j]) > (FAKTOR * 3) ** 2:
                loecher.append(ks[j])
            j = hier[j][0]
        x, y, w, h = cv2.boundingRect(k)
        stuecke.append((k, loecher, (x / FAKTOR, y / FAKTOR, w / FAKTOR, h / FAKTOR)))
    return stuecke


def einordnen(stuecke):
    u"""Ordnet jedes weisse Stueck einem Logoteil zu - nach Lage, nicht nach Reihenfolge."""
    gruppen = {"muetze-rand": [], "muetze": [], "stange": [], "scheiben-l": [], "scheiben-r": []}
    for k, loecher, (x, y, w, h) in stuecke:
        mitte_x = x + w / 2
        if y < 200 and h > 150:
            # Der Umriss der Muetze ist ein Ring (hat ein Loch), die Fuellung nicht.
            gruppen["muetze-rand" if loecher else "muetze"].append((k, loecher))
        elif y < 200:
            gruppen["muetze"].append((k, loecher))
        elif w > 150:
            gruppen["stange"].append((k, loecher))
        elif mitte_x < 256:
            gruppen["scheiben-l"].append((k, loecher))
        else:
            gruppen["scheiben-r"].append((k, loecher))
    return gruppen


def svg_bauen(inline=False):
    u"""inline=False: die Datei img/logo.svg (Hintergrundbild fuer .mark).
    inline=True: dieselben Formen fuer den Startbildschirm in index.html - mit Klassen statt
    ids (keine Kollision mit dem Dokument) und einer Maske, die den Muetzenumriss im Erst-Intro
    "zeichnet": ein dicker Strich entlang des Aussenumrisses, dessen Strichlaenge (pathLength 1)
    per stroke-dashoffset von 1 auf 0 laeuft."""
    gruppen = einordnen(konturen())
    if inline:
        zeilen = ['<svg class="splash-logo" viewBox="0 0 512 512" aria-hidden="true" focusable="false">']
        rand_aussen = pfad(gruppen["muetze-rand"][0][0])
        zeilen.append('<mask id="splash-spur-maske" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512">'
                      '<path class="lg-spur" d="%s" fill="none" stroke="#fff" stroke-width="44" '
                      'stroke-linecap="butt" pathLength="1"/></mask>' % rand_aussen)
        zeilen.append('<circle class="lg-teil lg-kreis" cx="256" cy="256" r="256" fill="%s"/>' % ROT)
    else:
        zeilen = [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Paddy’s Mealplan">',
            '<!-- Erzeugt von tools/logo-vektor.py aus img/icon-512.png - nicht von Hand bearbeiten. -->',
            '<circle id="lg-kreis" cx="256" cy="256" r="256" fill="%s"/>' % ROT,
        ]
    for name, teile in gruppen.items():
        if not teile:
            raise SystemExit("Logoteil nicht gefunden: " + name)
        d = "".join(pfad(k) + "".join(pfad(l) for l in loecher) for k, loecher in teile)
        if inline:
            maske = ' mask="url(#splash-spur-maske)"' if name == "muetze-rand" else ""
            zeilen.append('<path class="lg-teil lg-%s" fill="#fff" fill-rule="evenodd"%s d="%s"/>' % (name, maske, d))
        else:
            zeilen.append('<path id="lg-%s" fill="#fff" fill-rule="evenodd" d="%s"/>' % (name, d))
    zeilen.append("</svg>")
    return "\n".join(zeilen) + "\n", {n: len(t) for n, t in gruppen.items()}


MARKE_AN = "<!-- LOGO-SVG:ANFANG - erzeugt von tools/logo-vektor.py, nicht von Hand bearbeiten -->"
MARKE_AUS = "<!-- LOGO-SVG:ENDE -->"


def inline_einsetzen(svg):
    u"""Ersetzt den Block zwischen den Marken in index.html. Bytegenau: Zeilenenden der Datei
    (CRLF) bleiben, nur der Block dazwischen wird neu geschrieben."""
    pfad_html = os.path.join(WURZEL, "index.html")
    with io.open(pfad_html, "r", encoding="utf-8", newline="") as f:
        html = f.read()
    a, b = html.find(MARKE_AN), html.find(MARKE_AUS)
    if a < 0 or b < a or html.count(MARKE_AN) != 1:
        raise SystemExit("Marken LOGO-SVG in index.html fehlen oder sind doppelt")
    nl = "\r\n" if "\r\n" in html else "\n"
    neu = html[:a + len(MARKE_AN)] + nl + svg.rstrip("\n").replace("\n", nl) + nl + "    " + html[b:]
    if neu != html:
        with io.open(pfad_html, "w", encoding="utf-8", newline="") as f:
            f.write(neu)
    return neu != html


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pruefen", action="store_true", help="nur die Zuordnung zeigen, nichts schreiben")
    a = ap.parse_args()
    svg, zahl = svg_bauen()
    for n, z in zahl.items():
        print("  %-12s %d Stueck(e)" % (n, z))
    if a.pruefen:
        return
    with io.open(ZIEL, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("geschrieben: img/logo.svg (%d Bytes)" % len(svg.encode("utf-8")))
    inline, _ = svg_bauen(inline=True)
    print("index.html: Startbildschirm-Logo %s" % ("neu eingesetzt" if inline_einsetzen(inline) else "unveraendert"))


if __name__ == "__main__":
    main()
