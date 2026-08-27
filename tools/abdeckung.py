#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Abdeckungspruefung: Gibt es einen Bereich im Projekt, den niemand prueft?

Warum es dieses Skript gibt
---------------------------
`tools/wartung-check.py` prueft KONSISTENZ - Fragen ueber Dinge, die es gibt: Stimmt das
Modell eines Agenten mit CLAUDE.md? Zeigt ein Verweis ins Leere? Keine dieser Fragen findet,
was FEHLT.

Am 27.08.2026 hat der Nutzer das Ziel so formuliert: Das Setup soll von sich aus melden,
wenn ein neuer Bereich entsteht, fuer den es keinen Pruefer gibt - sein Beispiel war ein
kuenftiger Marketing-Bereich. Ohne diese Pruefung meldet das ganze System weiter
"keine Befunde", weil es nicht weiss, dass es etwas nicht weiss.

Wie es arbeitet
---------------
Es erhebt aus dem Repo vier Arten von Bereichen und vergleicht sie mit dem Register in
`docs/ABDECKUNG.md`:

    pfad:   erste Pfadkomponente aus `git ls-files`
    doku:   Datei in docs/
    reiter: data-tab="..." in index.html   <- ein neuer Reiter ist fast immer ein neuer Bereich
    domain: Hostname aus http(s)://... in index.html, sw.js, worker/

Was im Register steht, schweigt. Was fehlt, wird gemeldet.

Was es BEWUSST NICHT tut
------------------------
Es baut nichts und schlaegt keinen konkreten Agenten vor. Es hat kein Modell und kann nicht
beurteilen, welche Art Pruefer ein Bereich braucht - es kann nur sagen, DASS eine
Entscheidung aussteht. Den Entwurf macht ein Mensch oder ein Modell, und er wird abgenommen,
bevor er scharf geht. Ein Pruefer, den niemand geprueft hat, meldet "sauber" und man glaubt
ihm - siehe docs/TROUBLESHOOTING.md 119 und 123.

Aufruf:
    python tools/abdeckung.py           # Bericht
    python tools/abdeckung.py --kurz    # eine Zeile, fuer den Sitzungsstart-Hook
Rueckgabewert: 0 alles zugeordnet, 1 mindestens eine Luecke.
"""
import io
import os
import re
import subprocess
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = os.path.join("docs", "ABDECKUNG.md")

# Dateien, die nach draussen zeigen koennen und deshalb auf Domains durchsucht werden.
# vendor/ steht BEWUSST nicht dabei: Fremdcode nennt Dutzende Hosts, die er nie kontaktiert,
# und das Register waere binnen eines Updates unlesbar. Fuer vendor/ ist `lieferkette`
# zustaendig - der Bereich steht als `pfad:vendor/` im Register und hat damit seinen Pruefer.
QUELLEN_FUER_DOMAINS = ["index.html", "sw.js", os.path.join("worker", "og.js")]

# Unterhalb dieser Zahl gilt das Register als kaputt statt als leer. Grosszuegig gewaehlt:
# Es geht um "Format gebrochen", nicht um "eine Zeile geloescht".
MINDESTENS_IM_REGISTER = 20


def lies(pfad):
    try:
        return io.open(os.path.join(WURZEL, pfad), encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def register_kennungen():
    """Alle Kennungen aus docs/ABDECKUNG.md - nur die Spalte `Kennung` zaehlt.

    Bewusst eine einzige Regex ueber die ganze Datei statt eines Tabellenparsers: Das
    Register ist fuer Menschen geschrieben und darf umgebaut werden, ohne dass diese
    Pruefung bricht. Was zaehlt, ist `art:wert` in Backticks - sonst nichts.
    """
    text = lies(REGISTER)
    if not text:
        return None   # Register fehlt - das ist selbst ein Befund, siehe main()
    gefunden = set(re.findall(r"`((?:pfad|doku|reiter|domain):[^`]+)`", text))
    # Sanity: Ein Register, dessen Format bricht, liefert plotzlich wenige oder gar keine
    # Kennungen - dann waere auf einen Schlag "alles ohne Pruefer", und der Bericht ginge in
    # 57 Meldungen unter statt den EINEN Fehler zu nennen. Lieber hier hart abbrechen.
    if len(gefunden) < MINDESTENS_IM_REGISTER:
        return "kaputt"
    return gefunden


def ist_zustand():
    """Was das Repo tatsaechlich enthaelt, als Menge von Kennungen."""
    gefunden = set()

    # --- Pfade: erste Komponente. Verzeichnisse mit Schraegstrich, Dateien ohne. ---
    try:
        roh = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                             timeout=60, cwd=WURZEL).stdout.split("\n")
    except Exception:
        roh = []
    for zeile in roh:
        zeile = zeile.strip()
        if not zeile:
            continue
        kopf = zeile.split("/")[0]
        gefunden.add("pfad:" + (kopf + "/" if "/" in zeile else kopf))

    # --- Doku ---
    docs = os.path.join(WURZEL, "docs")
    if os.path.isdir(docs):
        for name in sorted(os.listdir(docs)):
            if name.endswith(".md"):
                gefunden.add("doku:docs/" + name)

    # --- Reiter der App ---
    for m in re.finditer(r'data-tab="([a-z0-9-]+)"', lies("index.html")):
        gefunden.add("reiter:" + m.group(1))

    # --- Externe Verbindungen ---
    for quelle in QUELLEN_FUER_DOMAINS:
        for m in re.finditer(r"https?://([a-zA-Z0-9.-]+)", lies(quelle)):
            host = m.group(1).strip(".-")
            # Ein abschliessender Bindestrich oder Punkt entsteht durch Textumbruch im
            # Rechtstext ("https://...-Adresse"); solche Fragmente sind keine Hosts.
            if "." in host:
                gefunden.add("domain:" + host)

    return gefunden


def pruefe():
    """Liefert (luecken, bekannt, gefunden). luecken ist leer, wenn alles zugeordnet ist."""
    bekannt = register_kennungen()
    if bekannt is None or bekannt == "kaputt":
        return None, bekannt, None
    gefunden = ist_zustand()
    return sorted(gefunden - bekannt), bekannt, gefunden


def tote_zeilen():
    """Kennungen, die im Register stehen, aber im Repo nicht (mehr) vorkommen.

    Kein Fehler, aber Verrottung: Wird ein Verzeichnis geloescht, bleibt seine Zeile stehen
    und niemand merkt, dass die Zuordnung Fiktion geworden ist. Genau die stille Drift,
    gegen die dieses ganze Setup gebaut ist - hier in der Pruefung selbst.

    Gefunden am 27.08.2026 beim Gegenpruefen eines Fehlalarms: `domain:localhost` stand im
    Register und wurde nie erhoben, weil Hostnamen ohne Punkt bewusst durchfallen.
    """
    bekannt = register_kennungen()
    if bekannt is None or bekannt == "kaputt":
        return []
    return sorted(bekannt - ist_zustand())


def kurzmeldung():
    """Eine Zeile fuer den Sitzungsstart - oder None, wenn alles zugeordnet ist."""
    luecken, bekannt, _ = pruefe()
    if bekannt is None:
        return "Abdeckungspruefung: %s fehlt - kein Bereich ist mehr zugeordnet." % REGISTER
    if bekannt == "kaputt":
        return ("Abdeckungspruefung: %s liest kaum Kennungen - das Format ist vermutlich "
                "gebrochen." % REGISTER)
    if not luecken:
        return None
    beispiele = ", ".join(luecken[:3])
    if len(luecken) > 3:
        beispiele += " und %d weitere" % (len(luecken) - 3)
    return ("Abdeckung: %d Bereich(e) ohne Pruefer - %s. "
            "Details: python tools/abdeckung.py" % (len(luecken), beispiele))


def gegenprobe():
    """Wuerde die Pruefung einen neuen Bereich ueberhaupt bemerken?

    Ohne diese Probe misst `abdeckung.py` nur, dass es nichts findet - und das taete es
    auch, wenn die Erhebung kaputt waere und eine leere Menge zurueckgaebe. Ein gruener
    Melder, der nichts mehr erheben kann, ist genau die Sorte Pruefung, gegen die dieses
    Projekt CLAUDE.md 11 geschrieben hat: "Ohne Gegenprobe zaehlt kein Ergebnis."

    Eingespeist wird der Fall, den der Nutzer am 27.08.2026 selbst genannt hat: ein
    Marketing-Bereich, der eines Tages dazukommt - als Verzeichnis, als Reiter, als eigene
    Doku und als neue Verbindung nach draussen.
    """
    ERFUNDEN = {
        "pfad:marketing/",
        "reiter:marketing",
        "doku:docs/MARKETING.md",
        "domain:newsletter.example.com",
    }
    bekannt = register_kennungen()
    if bekannt is None or bekannt == "kaputt":
        print("GEGENPROBE nicht moeglich: %s fehlt oder ist unlesbar." % REGISTER)
        return 1

    echt = ist_zustand()
    print("Gegenprobe der Abdeckungspruefung")
    print("=" * 66)

    schlecht = 0

    # 1. Der Normalfall: ohne die erfundenen Bereiche muss es still sein.
    still = sorted(echt - bekannt)
    if still:
        print("  FEHL  ohne Zutun werden %d Bereich(e) gemeldet: %s" % (len(still), still))
        schlecht += 1
    else:
        print("  OK    ohne Zutun still")

    # 2. Der Ernstfall: mit ihnen muessen genau sie gemeldet werden.
    gemeldet = set(sorted((echt | ERFUNDEN) - bekannt))
    fehlend = ERFUNDEN - gemeldet
    if fehlend:
        print("  FEHL  diese erfundenen Bereiche wurden NICHT gemeldet: %s" % sorted(fehlend))
        schlecht += 1
    else:
        print("  OK    alle vier erfundenen Bereiche gemeldet")

    # 3. Die Erhebung darf nicht leer sein - sonst waere 1. trivial erfuellt.
    if len(echt) < 20:
        print("  FEHL  die Erhebung liefert nur %d Bereiche - das ist zu wenig, "
              "sie ist vermutlich kaputt" % len(echt))
        schlecht += 1
    else:
        print("  OK    die Erhebung liefert %d Bereiche" % len(echt))

    print("=" * 66)
    if schlecht:
        print("GEGENPROBE FEHLGESCHLAGEN: %d von 3" % schlecht)
        return 1
    print("GEGENPROBE BESTANDEN. Die Pruefung wuerde einen neuen Bereich bemerken.")
    return 0


def main():
    if "--gegenprobe" in sys.argv:
        return gegenprobe()
    if "--kurz" in sys.argv:
        meldung = kurzmeldung()
        if meldung:
            print(meldung)
            return 1
        return 0

    luecken, bekannt, gefunden = pruefe()
    print("Abdeckungspruefung - wer prueft was?")
    print("=" * 66)

    if bekannt is None:
        print("\n%s fehlt. Ohne Register ist keine Zuordnung pruefbar." % REGISTER)
        return 1

    if bekannt == "kaputt":
        print("\n%s liefert weniger als %d Kennungen - das Format ist vermutlich gebrochen."
              % (REGISTER, MINDESTENS_IM_REGISTER))
        print("Ohne lesbares Register waere jeder Bereich 'ohne Pruefer', und der eine")
        print("echte Fehler ginge in Dutzenden Meldungen unter. Erst das Register richten.")
        return 1

    tot = tote_zeilen()

    if not luecken:
        print("\n%d Bereiche erhoben, alle im Register zugeordnet." % len(gefunden))
        if tot:
            print("\nAber %d Registerzeile(n) ohne Entsprechung im Repo:" % len(tot))
            for k in tot:
                print("  * %s" % k)
            print("\nKein Fehler, aber Verrottung: Die Zuordnung beschreibt etwas, das es")
            print("nicht mehr gibt. Zeile streichen - oder pruefen, ob der Bereich in")
            print("Wahrheit noch da ist und die Erhebung ihn nur nicht sieht.")
        print("\nDas heisst NICHT, dass jeder Pruefer gut ist - nur, dass keiner fehlt.")
        print("Ob die Zuordnung noch stimmt, sagt kein Skript. Das Register lesen:")
        print("  %s" % REGISTER)
        return 1 if tot else 0

    print("\n%d Bereich(e) ohne Zuordnung:\n" % len(luecken))
    for k in luecken:
        print("  * %s" % k)
    if tot:
        print("\nAusserdem %d Registerzeile(n) ohne Entsprechung im Repo (Verrottung):"
              % len(tot))
        for k in tot:
            print("  * %s" % k)

    print("""
Das ist kein Fehler - es ist eine Entscheidung, die aussteht. Drei Wege sind richtig:

  1. Gehoert zu einem bestehenden Pruefer -> Zeile in ABDECKUNG.md Abschnitt 3-5.
  2. Braucht wirklich einen neuen Pruefer  -> Agenten ENTWERFEN und abnehmen lassen,
     nie still anlegen.
  3. Braucht bewusst keinen                -> Zeile in Abschnitt 6, MIT Begruendung.

Falsch ist, eine Kennung nur einzutragen, damit Ruhe ist. Das schaltet die Pruefung
fuer diesen Bereich dauerhaft ab, und niemand sieht es je wieder.""")
    return 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
