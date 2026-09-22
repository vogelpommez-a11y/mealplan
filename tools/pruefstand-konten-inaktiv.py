# -*- coding: utf-8 -*-
u"""Die 24-Monats-Frist fuer verwaiste Konten - erkennt sie ueberhaupt etwas?

`tools/konten-inaktiv.py` meldet gegen die echte Datenbank "nichts zu tun". Das ist
richtig - alle 15 Konten sind aktiv - und genau deshalb belegt es nichts: Ein Werkzeug,
dessen Einstufung gar nicht greift, meldet dasselbe. Es sagt "sauber" und man glaubt ihm.

Geprueft wird deshalb `einstufen()` mit erfundenen Konten an den Grenzen der Frist, und
zwar der echte, importierte Code - kein Nachbau.

    python tools/pruefstand-konten-inaktiv.py
    python tools/pruefstand-konten-inaktiv.py --gegenprobe
"""
import datetime
import importlib.util
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def werkzeug():
    pfad = os.path.join(WURZEL, "tools", "konten-inaktiv.py")
    spec = importlib.util.spec_from_file_location("kt_inaktiv", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def main(argv):
    K = werkzeug()
    gegenprobe = "--gegenprobe" in argv
    befunde = []
    heute = datetime.datetime(2026, 9, 22, tzinfo=datetime.timezone.utc)
    jetzt = int(heute.timestamp() * 1000)
    tag = 86400000

    def konto(uid, still_tage, feld="lastLoginAt"):
        return {"localId": uid, "email": uid + "@beispiel.de",
                feld: str(jetzt - still_tage * tag)}

    def vor(tage):
        return (heute - datetime.timedelta(days=tage)).strftime("%Y-%m-%d")

    gruen = [0]

    def pr(name, ist, soll):
        if ist == soll:
            gruen[0] += 1
            print(u"  OK   %s -> %s" % (name, ist))
        else:
            print(u"  FAIL %s -> %s, erwartet %s" % (name, ist, soll))
            befunde.append(name)

    print(u"1. Die Schwelle bei 24 Monaten (730 Tage)")
    pr(u"gestern angemeldet", K.einstufen(konto("a", 1), {}, jetzt, heute)[0], u"aktiv")
    pr(u"vor 729 Tagen - einen Tag zu frueh",
       K.einstufen(konto("b", 729), {}, jetzt, heute)[0], u"aktiv")
    pr(u"vor 730 Tagen - die Frist ist um",
       K.einstufen(konto("c", 730), {}, jetzt, heute)[0], u"warnen")
    pr(u"vor 5 Jahren", K.einstufen(konto("d", 1825), {}, jetzt, heute)[0], u"warnen")

    print(u"\n2. Nach der Vorwarnung: 30 Tage Gnadenfrist")
    stand = {"e": {"gewarnt": vor(0)}, "f": {"gewarnt": vor(29)},
             "g": {"gewarnt": vor(30)}, "h": {"gewarnt": vor(400)}}
    pr(u"heute gewarnt", K.einstufen(konto("e", 800), stand, jetzt, heute)[0], u"wartend")
    pr(u"vor 29 Tagen gewarnt", K.einstufen(konto("f", 800), stand, jetzt, heute)[0], u"wartend")
    pr(u"vor 30 Tagen gewarnt", K.einstufen(konto("g", 800), stand, jetzt, heute)[0], u"loeschen")
    pr(u"vor 400 Tagen gewarnt", K.einstufen(konto("h", 800), stand, jetzt, heute)[0], u"loeschen")

    print(u"\n3. Ein Konto, das noch aktiv ist, wird NIE geloescht")
    # Auch dann nicht, wenn ein alter Warnvermerk herumliegt: Wer sich wieder angemeldet
    # hat, hat die Frist neu gestartet. Ohne diese Reihenfolge loeschte das Werkzeug
    # ausgerechnet Rueckkehrer.
    pr(u"gewarnt, aber wieder angemeldet",
       K.einstufen(konto("g", 3), stand, jetzt, heute)[0], u"aktiv")

    print(u"\n4. Kaputte Daten fuehren nie zur Loeschung")
    pr(u"kaputter Warnvermerk -> neu warnen statt loeschen",
       K.einstufen(konto("x", 800), {"x": {"gewarnt": "unsinn"}}, jetzt, heute)[0], u"warnen")
    pr(u"Vermerk ohne Datum -> neu warnen",
       K.einstufen(konto("y", 800), {"y": {}}, jetzt, heute)[0], u"warnen")
    pr(u"Konto ganz ohne Zeitstempel -> unbekannt, nicht geloescht",
       K.einstufen({"localId": "z"}, {}, jetzt, heute)[0], u"unbekannt")

    print(u"\n5. Ein nie benutztes Konto faellt nicht durchs Raster")
    # Ohne lastLoginAt zaehlt die Anlage. Sonst waere ausgerechnet das leere Konto -
    # angelegt, nie geoeffnet - von der Frist ausgenommen.
    pr(u"nie angemeldet, vor 3 Jahren angelegt",
       K.einstufen(konto("n", 1100, "createdAt"), {}, jetzt, heute)[0], u"warnen")
    pr(u"nie angemeldet, letzte Woche angelegt",
       K.einstufen(konto("m", 7, "createdAt"), {}, jetzt, heute)[0], u"aktiv")

    print(u"\n6. Der Warnstand liegt NICHT im Repo")
    # Er traegt UIDs und E-Mail-Adressen. Alles im Repo landet oeffentlich (CLAUDE.md 13).
    drin = os.path.abspath(K.WARNSTAND).startswith(os.path.abspath(WURZEL) + os.sep)
    pr(u"Ablage ausserhalb des Projektordners", not drin, True)

    if gegenprobe:
        print(u"\n7. Gegenprobe - misst dieser Pruefstand etwas?")
        # Der Zustand VOR dieser Aenderung war: gar keine Frist. Ein Werkzeug ohne
        # einstufen() faellt hier sofort auf - und ein Werkzeug, das pauschal "aktiv"
        # liefert, ebenfalls. Das zweite ist der wahrscheinlichere Fehler.
        alle_gleich = len(set([
            K.einstufen(konto("p", 1), {}, jetzt, heute)[0],
            K.einstufen(konto("q", 730), {}, jetzt, heute)[0],
            K.einstufen(konto("r", 800), {"r": {"gewarnt": vor(60)}}, jetzt, heute)[0],
        ])) == 1
        pr(u"die drei Zustaende sind wirklich verschieden", not alle_gleich, True)
        fehlt = not hasattr(K, "einstufen")
        pr(u"ohne einstufen() waere dieser Lauf gar nicht moeglich", not fehlt, True)

    print(u"\n" + u"=" * 66)
    # Schlusszeile im Format, das tools/alle-pruefstaende.py erwartet - sonst gilt der
    # Lauf dort als "prueft der ueberhaupt etwas?" (docs/TROUBLESHOOTING.md 131).
    print(u"ERGEBNIS %d gruen, %d rot" % (gruen[0], len(befunde)))
    if befunde:
        print(u"ROT - %d Befund(e):" % len(befunde))
        for b in befunde:
            print(u"  * %s" % b)
        return 1
    print(u"GRUEN - die Frist greift an allen Grenzen, und kaputte Daten loeschen nie.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
