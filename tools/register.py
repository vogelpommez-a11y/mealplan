# -*- coding: utf-8 -*-
u"""
Register: erzeugt die Inhaltsverzeichnisse am Kopf der grossen docs/*.md aus deren Ueberschriften.

Warum es das gibt
-----------------
Die Register in PRODUCT, ARCHITECTURES, TESTING und TROUBLESHOOTING tragen seit dem
26.08.2026 den Vermerk "erzeugt aus den Ueberschriften, nicht von Hand pflegen". Das
Skript dazu ist damals nie ins Repo gekommen. Am 24.09.2026 waren deshalb alle vier
veraltet: TROUBLESHOOTING endete bei 172 von 179, TESTING fuehrte 63 von 81 Abschnitten,
PRODUCT zeigte eine laengst umbenannte Ueberschrift. Niemand hatte gelogen - es hat nur
niemand nachgesehen. Genau dafuer steht dieser Lauf jetzt in tools/wartung-check.py.

Was erzeugt wird
----------------
Zwischen <!-- REGISTER-ANFANG ... --> und <!-- REGISTER-ENDE --> steht ein Einleitungstext
(Handarbeit, bleibt stehen - nur die Zahl hinter "**Register — " wird nachgezogen) und die
Tabelle (wird vollstaendig neu geschrieben):

  ## 110. Titel      ->  | 110 | Titel |
  ## Titel           ->  | · | Titel |
  # Teil B — Titel   ->  | | **— ab hier Teil B: Titel —** |   (nur NACH dem Register)

Ueberschriften in ```-Bloecken zaehlen nicht: TESTING zeigt dort "# dann: http://...".

Aufruf:
    python tools/register.py              # schreibt die Register neu
    python tools/register.py --pruefe     # schreibt nichts, Exit 1 bei Abweichung
    python tools/register.py --gegenprobe # wuerde --pruefe eine Luecke ueberhaupt bemerken?
"""
import io, os, re, sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATEIEN = ["docs/PRODUCT.md", "docs/ARCHITECTURES.md", "docs/TESTING.md", "docs/TROUBLESHOOTING.md"]
ANFANG = "<!-- REGISTER-ANFANG"
ENDE = "<!-- REGISTER-ENDE -->"
NUMMER = re.compile(r"^## ([0-9][0-9a-z-]*)\. (.+?)\s*$")


def lies(pfad):
    # newline="" - die Zeilenenden der Datei bleiben, wie sie sind (CRLF oder LF).
    with io.open(os.path.join(WURZEL, pfad), encoding="utf-8", newline="") as f:
        return f.read()


def zeilen_und_umbruch(text):
    u"""Zeilen und das ueberwiegende Zeilenende.

    An JEDEM Ende trennen, nicht nur am ueberwiegenden: Eine Datei kann gemischt sein - ein
    per Shell angehaengter Abschnitt endet auf LF, der Rest auf CRLF. Der erste Entwurf
    trennte nur an CRLF und las so den ganzen angehaengten Abschnitt als EINE Zeile; dessen
    Ueberschrift fehlte still im Register (TROUBLESHOOTING 179, am 24.09.2026). Geschrieben
    wird einheitlich im ueberwiegenden Ende - Git speichert ohnehin LF.
    """
    crlf = text.count("\r\n")
    umbruch = "\r\n" if crlf > text.count("\n") - crlf else "\n"
    return re.split(r"\r?\n", text), umbruch


def tabelle(zeilen, ab):
    u"""Tabellenzeilen aus allen Ueberschriften ab Zeile `ab` (hinter dem Register)."""
    aus = ["| # | Abschnitt |", "|---|---|"]
    im_block = False
    for z in zeilen[ab:]:
        if z.lstrip().startswith("```"):
            im_block = not im_block
            continue
        if im_block:
            continue
        if z.startswith("## "):
            m = NUMMER.match(z)
            nr, titel = (m.group(1), m.group(2)) if m else (u"·", z[3:].strip())
            aus.append(u"| %s | %s |" % (nr, titel.replace("|", "\\|")))
        elif z.startswith("# "):
            titel = z[2:].strip().replace(u" — ", ": ")
            aus.append(u"| | **— ab hier %s —** |" % titel)
    return aus


def neu_aufbauen(text):
    u"""Liefert (neuer Text, Anzahl Abschnitte). Wirft ValueError ohne Marken."""
    zeilen, umbruch = zeilen_und_umbruch(text)
    try:
        a = next(i for i, z in enumerate(zeilen) if z.startswith(ANFANG))
        e = next(i for i, z in enumerate(zeilen) if i > a and z.startswith(ENDE))
    except StopIteration:
        raise ValueError("Register-Marken fehlen")
    alt = zeilen[a + 1:e]
    # Einleitung = alles vor der ersten Tabellenzeile; Leerzeilen am Ende kommen neu.
    t0 = next((i for i, z in enumerate(alt) if z.startswith("|")), len(alt))
    einleitung = alt[:t0]
    while einleitung and not einleitung[-1].strip():
        einleitung.pop()
    tab = tabelle(zeilen, e + 1)
    anzahl = sum(1 for z in tab[2:] if not z.startswith("| | "))
    einleitung = [re.sub(u"(\\*\\*Register — )\\d+", u"\\g<1>%d" % anzahl, z, count=1)
                  for z in einleitung]
    block = einleitung + [""] + tab + [""]
    return umbruch.join(zeilen[:a + 1] + block + zeilen[e:]), anzahl


def main():
    pruefen = "--pruefe" in sys.argv
    if "--gegenprobe" in sys.argv:
        return gegenprobe()
    abweichend = 0
    for pfad in DATEIEN:
        text = lies(pfad)
        neu, anzahl = neu_aufbauen(text)
        if neu == text:
            print(u"  aktuell     %s (%d)" % (pfad, anzahl))
            continue
        abweichend += 1
        if pruefen:
            print(u"  VERALTET    %s - 'python tools/register.py' laufen lassen" % pfad)
        else:
            with io.open(os.path.join(WURZEL, pfad), "w", encoding="utf-8", newline="") as f:
                f.write(neu)
            print(u"  geschrieben %s (%d)" % (pfad, anzahl))
    return 1 if (pruefen and abweichend) else 0


def gegenprobe():
    u"""Eine Ueberschrift kuenstlich anhaengen: --pruefe muss das Register dann veraltet finden.

    Ohne diese Probe koennte neu_aufbauen() still immer denselben Text liefern (etwa weil
    die Tabelle gar nicht aus den Ueberschriften kommt) - und --pruefe meldete fuer immer
    "aktuell".
    """
    fehler = 0
    for pfad in DATEIEN:
        text = lies(pfad)
        aktuell, _ = neu_aufbauen(text)
        _, umbruch = zeilen_und_umbruch(aktuell)
        mit_neuer = aktuell + umbruch + u"## Gegenprobe-Abschnitt" + umbruch
        erkannt = neu_aufbauen(mit_neuer)[0] != mit_neuer
        # Und im Codeblock darf dieselbe Zeile NICHT zaehlen.
        im_block = aktuell + umbruch + u"```" + umbruch + u"## Gegenprobe-Abschnitt" + umbruch + u"```" + umbruch
        ignoriert = neu_aufbauen(im_block)[0] == im_block
        # Und mit dem ANDEREN Zeilenende angehaengt muss sie in der Tabelle landen.
        fremd = "\n" if umbruch == "\r\n" else "\r\n"
        gemischt = aktuell + fremd + u"## Gegenprobe-Abschnitt" + fremd
        gemischt_erkannt = u"| · | Gegenprobe-Abschnitt |" in neu_aufbauen(gemischt)[0]
        ok = erkannt and ignoriert and gemischt_erkannt
        fehler += not ok
        print(u"  %s  %s  (neu erkannt: %s, im Codeblock ignoriert: %s, gemischte Zeilenenden: %s)"
              % ("OK  " if ok else "FEHL", pfad, erkannt, ignoriert, gemischt_erkannt))
    print(u"GEGENPROBE GRUEN" if not fehler else u"GEGENPROBE ROT (%d)" % fehler)
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
