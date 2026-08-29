# -*- coding: utf-8 -*-
u"""
Quelle: liefert Pruefstaenden die App als EINE Seite - egal, auf wie viele Dateien
der Produktionscode inzwischen verteilt ist.

Warum es das gibt
-----------------
Pruefstaende schreiben ihre praeparierte Seite nach `tools/` und starten sie ueber
`file:///`. Solange alles in `index.html` stand, war das folgenlos. Seit CSS, Daten und
zwei Bibliotheken in `css/`, `data/` und `lib/` liegen, wuerde ein relativer Verweis wie
`data/cookbook.js` aus `tools/` heraus auf `tools/data/cookbook.js` zeigen - also ins
Leere. Die Seite laedt, das Skript fehlt, und der Pruefstand misst nichts mehr.

Deshalb baut `lade_seite()` die externen Dateien an genau der Stelle wieder ein, an der
sie eingebunden sind. Das ist ausdruecklich KEIN Nachbau: es ist derselbe Text, nur
wieder in einer Datei. Die Regel aus CLAUDE.md Abschnitt 11 - getestet wird echter,
ausgeschnittener Produktionscode - bleibt damit unangetastet.

Bewusst NICHT eingebaut wird `vendor/`. Das Firebase-Modul scheitert aus `tools/` heraus
schon heute still, und die App faellt dann auf den lokalen Login zurueck. Genau diesen
Zustand wollen die Pruefstaende. Daran wird nichts geaendert.

Aufruf aus einem Pruefstand:

    import quelle
    seite = quelle.lade_seite(INDEX)          # statt io.open(INDEX).read()

Vor der Aufteilung war das ein No-Op - es gab keine externen Verweise. Der Aufruf ist
also in jedem Stand gueltig.
"""
import io
import os
import re

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL_ZEICHEN = chr(10)

# Nur diese Ordner werden eingebaut. vendor/ bleibt bewusst aussen vor (siehe Kopf).
EIGENE_ORDNER = ("css/", "data/", "lib/")

_LINK = re.compile(
    r"""<link\b[^>]*?\brel\s*=\s*["']stylesheet["'][^>]*?\bhref\s*=\s*["']([^"']+)["'][^>]*?>""",
    re.IGNORECASE)
_SCRIPT = re.compile(
    r"""<script\b([^>]*?)\bsrc\s*=\s*["']([^"']+)["']([^>]*)>\s*</script\s*>""",
    re.IGNORECASE)


def _ist_eigen(pfad):
    u"""Nur eigene, relative Verweise auf css/, data/, lib/ - nichts Fremdes, nichts Absolutes."""
    p = pfad.strip().lstrip("./")
    if "://" in pfad or pfad.startswith("//") or pfad.startswith("/"):
        return False
    return p.startswith(EIGENE_ORDNER)


def _lies(basis, pfad):
    voll = os.path.join(basis, pfad.strip().lstrip("./").replace("/", os.sep))
    if not os.path.isfile(voll):
        raise SystemExit(u"quelle.py: eingebundene Datei fehlt: " + voll)
    return io.open(voll, encoding="utf-8").read()


def _mit_umbruch(text):
    u"""Sorgt dafuer, dass der eingebaute Inhalt auf einer eigenen Zeile endet.

    WARUM DAS NOETIG IST (29.08.2026): Endet eine Datei ohne Zeilenumbruch, klebt das
    schliessende `</script>` an ihrer letzten Zeile - aus `  ];` wird `  ];</script>`.
    Die Ausschneide-Pruefstaende schneiden zeilenweise mit `startswith("  ];")`, ziehen das
    `</script>` dadurch in den ausgeschnittenen Code und beenden den Script-Block MITTEN in
    ihrer eigenen Seite. Ergebnis: "Uncaught SyntaxError", kein Protokoll, kein Ergebnis -
    und die Ursache steht in einer Datei, die selbst syntaktisch tadellos ist.

    Aufgefallen beim ersten Rezept, das ueber /rezeptcharge entstand: Ein fehlender Umbruch
    am Ende von data/cookbook.js legte zwei Pruefstaende lahm. Siehe
    docs/TROUBLESHOOTING.md 142.
    """
    return text if text.endswith("\n") else text + "\n"


def _schuetze(js):
    u"""`</script` im Text wuerde den umgebenden Block beenden.

    Innerhalb eines JS-Strings ist `<\\/script` derselbe Wert - der Code aendert sich
    dadurch nicht. Betrifft in der Praxis nur die Rechtstexte, die HTML enthalten.
    """
    return re.sub(r"</(script)", r"<\\/\1", js, flags=re.IGNORECASE)


def lade_seite(index=None):
    u"""Liest index.html und baut die eigenen css/-, data/- und lib/-Dateien wieder ein.

    Reihenfolge und Position bleiben exakt erhalten: jedes Tag wird an Ort und Stelle
    durch seinen Inhalt ersetzt. Die Ladereihenfolge der App ist damit dieselbe wie im
    Browser gegen den echten Server.
    """
    index = index or os.path.join(BASIS, "index.html")
    basis = os.path.dirname(os.path.abspath(index))
    seite = io.open(index, encoding="utf-8").read()

    def link_ersetzen(m):
        href = m.group(1)
        if not _ist_eigen(href):
            return m.group(0)
        return u"<style>/* eingebaut aus %s */\n%s</style>" % (href, _mit_umbruch(_lies(basis, href)))

    def script_ersetzen(m):
        vorn, src, hinten = m.group(1), m.group(2), m.group(3)
        if not _ist_eigen(src):
            return m.group(0)
        attrs = (vorn + hinten).replace("\n", " ").strip()
        attrs = (" " + attrs) if attrs else ""
        return u"<script%s>/* eingebaut aus %s */\n%s</script>" % (
            attrs, src, _mit_umbruch(_schuetze(_lies(basis, src))))

    seite = _LINK.sub(link_ersetzen, seite)
    seite = _SCRIPT.sub(script_ersetzen, seite)
    return seite


def css_gesamt(index=None):
    u"""Das komplette CSS der App als ein Text - in Ladereihenfolge.

    Frueher war das schlicht der eine <style>-Block. Seit das CSS in vier Dateien liegt,
    braucht ein Pruefstand, der ueber die Kaskade misst, alle vier - und zwar in genau
    der Reihenfolge, in der der Browser sie sieht. Ein Pruefstand, der nur den ersten
    Block nimmt, misst gegen ein Viertel der Regeln und meldet trotzdem ein Ergebnis.
    """
    seite = lade_seite(index)
    bloecke = re.findall(r"<style[^>]*>(.*?)</style\s*>", seite, re.S | re.I)
    if not bloecke:
        raise SystemExit(u"quelle.py: kein CSS gefunden - ist css/ noch eingebunden?")
    return (NL_ZEICHEN * 2).join(bloecke)


def js_dateien(basis=None):
    u"""Alle JS-Dateien, die zur App gehoeren - fuer syntax-check.py und die CI.

    vendor/ ist Fremdcode und wird nicht geprueft; sw.js gehoert dazu, weil ein
    Syntaxfehler dort die Offline-Faehigkeit still zerstoert.
    """
    basis = basis or BASIS
    raus = []
    for ordner in ("data", "lib"):
        voll = os.path.join(basis, ordner)
        if not os.path.isdir(voll):
            continue
        for name in sorted(os.listdir(voll)):
            if name.endswith(".js"):
                raus.append(ordner + "/" + name)
    if os.path.isfile(os.path.join(basis, "sw.js")):
        raus.append("sw.js")
    return raus


def eingebunden(index=None):
    u"""Was index.html tatsaechlich einbindet, in Dokumentreihenfolge.

    Die Reihenfolge ist Architektur: die klassischen Skripte laufen synchron
    nacheinander, bevor die App-IIFE geparst wird. karte.py belegt sie damit.
    """
    index = index or os.path.join(BASIS, "index.html")
    seite = io.open(index, encoding="utf-8").read()
    treffer = []
    for m in re.finditer(r"""<(?:link|script)\b[^>]*?\b(?:href|src)\s*=\s*["']([^"']+)["']""",
                         seite, re.IGNORECASE):
        p = m.group(1)
        if _ist_eigen(p):
            treffer.append(p.strip().lstrip("./"))
    return treffer


if __name__ == "__main__":
    import sys
    if "--liste" in sys.argv:
        for p in eingebunden():
            print(p)
    else:
        sys.stdout.write(lade_seite())
