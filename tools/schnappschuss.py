# -*- coding: utf-8 -*-
u"""Friert den VORHER-Stand eines UI-Bausteins ein, damit man ihn neben den neuen stellen kann.

    python tools/schnappschuss.py dropdown            # aus HEAD
    python tools/schnappschuss.py dropdown 71a4650    # aus einem bestimmten Commit
    python tools/schnappschuss.py --liste             # was liegt schon da?

Was eingefroren wird und was nicht
----------------------------------
Eingefroren:  index.html + css/*.css  - genau das, was sich bei UI-Arbeit aendert.
Aus der Wurzel geliehen:  lib/, data/, img/, vendor/  - Inhalt, nicht Gestaltung.

Der Schnappschuss bekommt dafuer ein <base href="/">, das alle relativen Pfade auf die
Projektwurzel zieht, und seine vier <link>-Zeilen werden auf den eigenen Ordner umgebogen.
Ohne diesen Kniff muesste man 32 Meal-Fotos je Baustein mitkopieren - oder der Vergleich
zeigte links andere Rezepte als rechts.

Warum aus Git und nicht aus dem Arbeitsbaum
-------------------------------------------
Es ist derselbe Text, nur aus der Historie gelesen. Das ist **kein Nachbau** - die
Projektregel verlangt echten Produktionscode (CLAUDE.md Abschnitt 11), und ein von Hand
nachgestelltes "Vorher" waere genau das, was sie verbietet.

Einmal erzeugt, wird ein Schnappschuss **nicht mehr angefasst**. Er ist ein Zeugnis, kein
lebendes Dokument. Wer ihn nachzieht, vergleicht am Ende zwei Staende des Nachher.

Nicht wiederverwendbar: tools/quelle.py baut eine EINZELNE Datei mit eingebettetem CSS.
Hier braucht es echte css/*.css in echter <link>-Reihenfolge, sonst stimmt die Kaskade nicht.
"""
import argparse, io, os, re, subprocess, sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VORHER = os.path.join(WURZEL, "tools", "vorher")
CSS_DATEIEN = ["tokens.css", "basis.css", "komponenten.css", "mobil.css"]


def aus_git(ref, pfad):
    u"""Liest eine Datei aus einem Git-Stand, ohne den Arbeitsbaum anzufassen."""
    roh = subprocess.check_output(["git", "show", "%s:%s" % (ref, pfad)], cwd=WURZEL)
    return roh.decode("utf-8", "replace")


def umbiegen(html, kennung):
    u"""<base> auf die Wurzel, die vier Stylesheets auf den eigenen Ordner.

    Reihenfolge ist wichtig: Erst die <link>-Zeilen absolut machen, dann <base> einsetzen.
    Umgekehrt zoege das <base> die noch relativen Links auf die Wurzel - und der
    Schnappschuss zeigte das AKTUELLE CSS. Er saehe dann aus wie das Nachher, und der
    Vergleich waere still kaputt.
    """
    for name in CSS_DATEIEN:
        html = html.replace('href="css/%s"' % name,
                            'href="/tools/vorher/%s/css/%s"' % (kennung, name))
    marke = "<base href=\"/\"><!-- Schnappschuss: lib/, data/, img/ kommen aus der Wurzel -->"
    # Verankert an <meta charset>, NICHT am ersten <link>: index.html hat gar kein <head>,
    # und der erste "<link rel=\"stylesheet\"" im Text steht in einem JS-String tief im
    # Dokument. Der erste Entwurf setzte das <base> deshalb in Zeile 5045 mitten in den Code
    # (20.09.2026) - die Datei blieb syntaktisch heil und war trotzdem kaputt.
    anker = '<meta charset="utf-8">'
    if anker not in html:
        raise SystemExit(u"FEHLER: '%s' nicht gefunden - Einfuegestelle unklar, abgebrochen."
                         % anker)
    html = html.replace(anker, anker + "\n" + marke, 1)
    return html


def css_pfade(text):
    u"""Biegt url(../img/...) auf die Wurzel um.

    `<base href="/">` gilt fuer das DOKUMENT, nicht fuer Stylesheets: CSS-URLs werden
    immer relativ zur CSS-DATEI aufgeloest. Im Original zeigt `url(../img/logo.png)` aus
    css/ auf /img/logo.png; aus tools/vorher/<id>/css/ zeigt dieselbe Zeile auf
    tools/vorher/<id>/img/logo.png - und dort liegt nichts.

    Ohne diese Zeile fehlt links das Logo, waehrend rechts eines steht. Man haelt es fuer
    eine Designaenderung und sucht sie im Diff (gefunden am 20.09.2026 im ersten Vergleich).
    """
    return text.replace("url(../img/", "url(/img/")


def bauen(kennung, ref):
    ziel = os.path.join(VORHER, kennung)
    if os.path.exists(ziel):
        print(u"Es gibt schon einen Schnappschuss '%s'." % kennung)
        print(u"Schnappschuesse werden bewusst NICHT nachgezogen - sie sind ein Zeugnis.")
        print(u"Wirklich neu bauen? Dann erst loeschen:  %s" % os.path.relpath(ziel, WURZEL))
        return 1

    try:
        html = aus_git(ref, "index.html")
        css = {n: aus_git(ref, "css/" + n) for n in CSS_DATEIEN}
    except subprocess.CalledProcessError:
        print(u"FEHLER: '%s' ist kein gueltiger Git-Stand, oder eine Datei fehlt dort." % ref)
        return 2

    os.makedirs(os.path.join(ziel, "css"))
    io.open(os.path.join(ziel, "index.html"), "w", encoding="utf-8", newline="\n").write(
        umbiegen(html, kennung))
    for name, text in css.items():
        io.open(os.path.join(ziel, "css", name), "w", encoding="utf-8",
                newline="\n").write(css_pfade(text))

    kurz = subprocess.check_output(["git", "rev-parse", "--short", ref],
                                   cwd=WURZEL).decode().strip()
    io.open(os.path.join(ziel, "HERKUNFT.txt"), "w", encoding="utf-8", newline="\n").write(
        u"Schnappschuss '%s'\nGit-Stand: %s (%s)\n\n"
        u"Eingefroren: index.html + css/*.css\n"
        u"Geliehen aus der Wurzel: lib/, data/, img/, vendor/ (ueber <base href=\"/\">)\n\n"
        u"NICHT nachziehen. Dieser Ordner zeigt, wie es VORHER war.\n" % (kennung, kurz, ref))

    print(u"Schnappschuss '%s' aus %s angelegt." % (kennung, kurz))
    print(u"  tools/vorher/%s/index.html  (+ 4 CSS-Dateien)" % kennung)
    print(u"  Ansehen: http://localhost:8000/tools/probe-vergleich.html?baustein=%s" % kennung)
    return 0


def liste():
    if not os.path.isdir(VORHER):
        print(u"Noch kein Schnappschuss angelegt.")
        return 0
    eintraege = sorted(d for d in os.listdir(VORHER)
                       if os.path.isdir(os.path.join(VORHER, d)))
    if not eintraege:
        print(u"Noch kein Schnappschuss angelegt.")
        return 0
    print(u"Vorhandene Schnappschuesse:\n")
    for d in eintraege:
        h = os.path.join(VORHER, d, "HERKUNFT.txt")
        stand = u"?"
        if os.path.exists(h):
            for z in io.open(h, encoding="utf-8"):
                if z.startswith("Git-Stand:"):
                    stand = z.split(":", 1)[1].strip()
        print(u"  %-22s %s" % (d, stand))
    return 0


def main():
    p = argparse.ArgumentParser(description=u"Friert den Vorher-Stand eines UI-Bausteins ein")
    p.add_argument("kennung", nargs="?", help=u"Name des Bausteins, z. B. dropdown")
    p.add_argument("ref", nargs="?", default="HEAD", help=u"Git-Stand (Standard: HEAD)")
    p.add_argument("--liste", action="store_true", help=u"vorhandene Schnappschuesse zeigen")
    a = p.parse_args()

    if a.liste or not a.kennung:
        return liste()
    if not re.match(r"^[a-z0-9-]+$", a.kennung):
        print(u"Die Kennung darf nur Kleinbuchstaben, Ziffern und Bindestriche enthalten.")
        return 2
    return bauen(a.kennung, a.ref)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
