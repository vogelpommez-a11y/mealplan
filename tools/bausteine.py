# -*- coding: utf-8 -*-
u"""Zaehlt die Fundstellen der UI-Bausteine und meldet, wenn eine dazukommt.

    python tools/bausteine.py                # Bericht
    python tools/bausteine.py --gegenprobe   # bemerkt es ueberhaupt etwas?

Wozu
----
`CLAUDE.md` Abschnitt 21a verlangt: Wird ein Baustein angefasst, werden ALLE seine
Fundstellen angefasst. Und bevor etwas Neues entsteht, wird geprueft, ob es das schon gibt.

Beides steht und faellt damit, dass jemand nachzaehlt. Genau das ist ueber Monate nicht
passiert - daher vier Dropdown-Funktionen, sieben Namen fuer "leerer Zustand" und drei
Bauarten fuer Reiter.

Dieses Skript zaehlt. Es urteilt nicht ueber Gestaltung, es meldet nur Abweichungen von dem,
was in `docs/BAUSTEINE.md` als Stand festgehalten ist:

    Mehr Fundstellen als erwartet  ->  jemand hat danebengebaut (ROT)
    Weniger als erwartet           ->  vereinheitlicht? Dann BAUSTEINE.md nachziehen (GELB)

Was es NICHT kann: beurteilen, ob zwei Stellen wirklich dasselbe Muster sind. Das bleibt
Handarbeit - das Skript ist das Netz darunter, nicht der Plan.
"""
import io, os, re, sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WURZEL)

# Je Baustein: (Anzeigename, Datei, Suchmuster, erwartete Zahl, Bemerkung)
#
# Die erwarteten Zahlen sind der Stand vom 20.09.2026, erhoben fuer plans/UI-Grundlagen.MD.
# Wer einen Baustein vereinheitlicht, setzt die Zahl hier UND in docs/BAUSTEINE.md neu -
# an zwei Stellen bewusst, damit die Aenderung auffaellt.
BAUSTEINE = [
    (u"Dropdown: gemeinsamer Helfer", "index.html",
     r"function openMenu\s*\(", 1,
     u"faellt er weg, ist jemand zurueckgefallen"),

    (u"Dropdown: Menue-Baufunktionen", "index.html",
     r"function (?:toggle\w*Menu|openAssignMenu)\s*\(", 4,
     u"3 nutzen jetzt openMenu, nur das Chip-Menue baut selbst"),

    (u"Dropdown: Markup-Stellen", "index.html",
     r'<div class="menu[ $"]', 2,
     u"openMenu() + das Chip-Menue. Am 20.09.2026 von 4 auf 2"),

    (u"Leere Zustaende: Helfer", "index.html",
     r"function leerZustand\s*\(", 1,
     u"faellt er weg, ist jemand zurueckgefallen"),

    (u"Leere Zustaende: Aufrufe", "index.html",
     r"\bleerZustand\(", 12,
     u"11 Aufrufe + Definition. Am 20.09.2026 aus 6 Klassennamen zusammengefuehrt"),

    (u"Leere Zustaende: alte Klassen", "index.html",
     r'class="(?:wch-empty|ms-empty-ings|wl-empty|pempty|shop-empty)\b', 0,
     u"muss 0 bleiben - jede davon waere ein Rueckfall"),

    (u"Akkordeon: natives <details>", "index.html",
     r"<details\b", 6,
     u"zweiter Mechanismus neben data-action=toggle-*"),

    # Nur MARKUP zaehlen, nicht die JS-Zeilen, die dasselbe Element suchen. Und
    # `toggle-fav` gehoert nicht dazu: ein Favoritenschalter klappt nichts auf.
    (u"Akkordeon: JS-Aufklapper", "index.html",
     r'<button[^>]*(?:data-action="toggle-(?:day-goals|others|cat)"|data-pq-toggle)', 5,
     u"4 Wege + pq-toggle; <details> ist der fuenfte Mechanismus"),

    (u"Tabs: Segment-Muster", "index.html",
     r'class="(?:tabs|daybar|kal-seg)\b', 3,
     u"drei Leisten - bleiben drei, vereinheitlicht ist ihre MARKIERUNG"),

    # Die gleitende Markierung (21.09.2026). Faellt die Zahl, hat jemand einen Indikator
    # aus dem gemeinsamen Fundament geloest und baut wieder eigene Flaechen.
    (u"Markierung: gemeinsames Fundament", "css/basis.css",
     r"\.tab-ind, \.kal-pill, \.db-ind, \.ws-ind \{", 1,
     u"eine Zeile fuer Position und z-index aller vier"),

    (u"Markierung: Akzent-Familie", "css/basis.css",
     r"\n  \.kal-pill, \.db-ind, \.ws-ind \{", 1,
     u"drei im Akzentverlauf; .tab-ind bleibt BEWUSST neutral (docs/DESIGN.md)"),

    # Beide standen bis zum 21.09. als Rohwert im CSS, obwohl es --shadow gibt.
    # Nur ausserhalb von Kommentaren zaehlen - die Begruendung darf sie nennen.
    (u"Markierung: harte Schatten", "css/basis.css",
     r"box-shadow: 0 1px [34]px rgba\(0, ?0, ?0, ?\.\d+\)", 0,
     u"muss 0 bleiben - dafuer gibt es --shadow (css/CLAUDE.md)"),

    (u"Modal: zentraler Helfer", "index.html",
     r"\bopenModal\s*\(", 28,
     u"VORBILD - 27 Aufrufe + Definition. Faellt die Zahl, ist er umgangen worden"),

    (u"Bestaetigung: zentraler Helfer", "index.html",
     r"\bconfirmModal\s*\(", 12,
     u"11 Aufrufe + Definition. Am 21.09. fielen zwei weg, die neben einem Undo standen"),

    # Loeschen mit Netz statt mit Rueckfrage (21.09.2026).
    #
    # Ein blosser undoToast-Zaehler taugt hier NICHT: Die Zahl war vor der Aenderung
    # dieselbe (9), die Gegenprobe merkte nichts. Gezaehlt wird deshalb das, was neu ist -
    # das verlaengerte Netz - und das, was verschwinden musste.
    (u"Loeschen: verlaengertes Netz", "index.html",
     r"\{\s*ms:\s*10000\s*\}", 1,
     u"deleteRecipe: 10 s statt 5 - ein Meal ist Name, Naehrwerte und oft ein Foto"),

    (u"Loeschen: keine doppelte Sicherung", "index.html",
     r'title:\s*"(?:Meal l\u00f6schen\?|Woche leeren\?)"', 0,
     u"muss 0 bleiben - beide standen vor einem undoToast, das denselben Fehler abfing"),

    # Der Trefferflaechen-Mechanismus (21.09.2026). Faellt die Zahl, hat jemand einen
    # Selektor aus der gemeinsamen Regel geloest - und der Knopf ist wieder unter 44 px,
    # ohne dass es irgendwo auffaellt.
    (u"Trefferflaeche: gemeinsame Regel", "css/basis.css",
     r"\.(?:hit|btn\.icon-gh|btn\.fav-ic|foot-link|ing-ic|ing-view-del|ing-barcode|wch-add|wch-more|avatar-edit-btn)::after", 13,
     u"9 in der ::after-Liste + 4 in der Rund-Zeile"),

    # Der rahmenlose Textknopf. 0 heisst: keiner hat sich wieder danebengebaut.
    (u"Textknopf: Eigenbauten", "css/komponenten.css",
     r"\.(?:auth-forgot|toggle-all)\s*\{[^}]*background:\s*(?:0|none)", 0,
     u"muss 0 bleiben - das Aussehen gehoert .btn.link"),

    (u"Textknopf: Variante genutzt", "index.html",
     r'class="btn link\b', 6,
     u"3 Orte + 2 inline + 1 leise"),

    # .btn.del-ic war am 21.09.2026 tot (nur CSS, kein Markup) und wurde entfernt.
    (u"Button: tote Variante del-ic", "css/basis.css",
     r"\.btn\.del-ic", 0,
     u"muss 0 bleiben - war eine Karteileiche"),
]


def lies(pfad):
    try:
        return io.open(pfad, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def zaehlen(text_je_datei=None):
    u"""Liefert [(name, ist, soll, bemerkung), ...]."""
    ergebnis = []
    for name, datei, muster, soll, bem in BAUSTEINE:
        text = (text_je_datei or {}).get(datei)
        if text is None:
            text = lies(datei)
        ist = len(re.findall(muster, text))
        ergebnis.append((name, ist, soll, bem))
    return ergebnis


def bericht(zahlen, still=False):
    rot, gelb = [], []
    if not still:
        print(u"UI-Bausteine - Fundstellen gegen docs/BAUSTEINE.md")
        print(u"=" * 66)
    for name, ist, soll, bem in zahlen:
        if ist > soll:
            zeichen, wohin = u"ROT ", rot
        elif ist < soll:
            zeichen, wohin = u"GELB", gelb
        else:
            zeichen, wohin = u"ok  ", None
        if not still:
            print(u"  %s %-34s %2d von %2d   %s" % (zeichen, name[:34], ist, soll, bem[:30]))
        if wohin is not None:
            wohin.append((name, ist, soll))

    if still:
        return rot, gelb

    print()
    if rot:
        print(u"ROT - eine Stelle ist dazugekommen (%d):" % len(rot))
        for name, ist, soll in rot:
            print(u"  %s: %d statt %d" % (name, ist, soll))
        print()
        print(u"  Gibt es den Baustein schon? Dann den bestehenden verwenden, nicht")
        print(u"  danebenbauen (CLAUDE.md Abschnitt 21a, Stufe 1).")
    if gelb:
        print(u"GELB - weniger Stellen als erwartet (%d):" % len(gelb))
        for name, ist, soll in gelb:
            print(u"  %s: %d statt %d" % (name, ist, soll))
        print()
        print(u"  Vereinheitlicht? Dann die Zahl in docs/BAUSTEINE.md UND in diesem")
        print(u"  Skript nachziehen - sonst meldet es beim naechsten Mal das Falsche.")
    if not rot and not gelb:
        print(u"Keine Abweichung. Der Stand entspricht docs/BAUSTEINE.md.")
        print()
        print(u"Das heisst NICHT, dass die Bausteine gut sind - nur, dass keine Stelle")
        print(u"unbemerkt dazugekommen ist.")
    return rot, gelb


def gegenprobe():
    u"""Baut kuenstlich eine fuenfte Dropdown-Stelle ein. Wird sie gemeldet?

    Ohne diesen Lauf ist ein gruener Bericht wertlos: Er waere auch gruen, wenn das
    Suchmuster ins Leere liefe - etwa weil jemand `function toggleXMenu(` zu
    `const toggleXMenu = (` umgeschrieben hat.
    """
    print(u"Gegenprobe: bemerkt das Skript eine zusaetzliche Stelle?\n")
    echt = lies("index.html")

    fehlt = []
    for name, datei, muster, soll, bem in BAUSTEINE:
        ist = len(re.findall(muster, lies(datei)))
        if ist == 0:
            fehlt.append(name)
    if fehlt:
        print(u"  WARNUNG: %d Muster finden GAR NICHTS - sie messen nichts mehr:" % len(fehlt))
        for n in fehlt:
            print(u"    %s" % n)
        print()

    # Eine funktion danebenbauen, wie es im Alltag passieren wuerde.
    kuenstlich = echt + u"\n  function toggleProbeMenu() { /* Gegenprobe */ }\n"
    zahlen = zaehlen({"index.html": kuenstlich})
    rot, _ = bericht(zahlen, still=True)

    getroffen = any(u"Baufunktionen" in n for n, _, _ in rot)
    print(u"  %-44s %s" % (u"zusaetzliche Dropdown-Funktion gemeldet", u"OK" if getroffen else u"FEHLT"))

    # Und die Gegenrichtung: ohne Probe muss es still sein.
    rot2, gelb2 = bericht(zaehlen(), still=True)
    still = not rot2 and not gelb2
    print(u"  %-44s %s" % (u"ohne Probe still", u"OK" if still else u"MELDET ETWAS"))

    print()
    if getroffen and still and not fehlt:
        print(u"GEGENPROBE BESTANDEN. Ein gruener Bericht bedeutet etwas.")
        return 0
    print(u"GEGENPROBE NICHT BESTANDEN - ein gruener Bericht waere wertlos.")
    if not still:
        print(u"(Der zweite Punkt schlaegt fehl, solange ein echter Befund offen ist -")
        print(u" dann zuerst den beheben und erneut laufen lassen.)")
    return 1


def main():
    if "--gegenprobe" in sys.argv:
        return gegenprobe()
    rot, gelb = bericht(zaehlen())
    return 1 if rot else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
