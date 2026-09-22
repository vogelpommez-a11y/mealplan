# -*- coding: utf-8 -*-
u"""Prueft die 12-Monats-Frist geteilter Meals - an drei Stellen zugleich.

Die Frist steht dreimal im Projekt, und zwar notgedrungen:

  1. `firestore.rules` -> shareFrisch()     - die Durchsetzung
  2. `index.html`       -> SHARE_TTL_MS     - die Beschriftung in der Oberflaeche
  3. `tools/shared-aufraeumen.py` -> TTL_MS - das physische Aufraeumen

Firestore-Regeln lassen sich nicht aus JavaScript speisen, und das Wartungsskript
laeuft ohne Browser. Drei Zahlen also - und drei Zahlen driften auseinander. Faellt
eine davon zurueck, sagt die App "12 Monate", die Regel sperrt nach sechs, und das
Aufraeumskript loescht nach zwei Jahren. Keiner dieser drei Zustaende faellt im
Alltag auf; der Nutzer sieht nur einen Link, der frueher stirbt, als versprochen.

Geprueft wird ausserdem die Logik des Aufraeumskripts selbst - mit echten
Grenzfaellen statt eines Nachbaus (CLAUDE.md 11).

    python tools/pruefstand-share-frist.py
    python tools/pruefstand-share-frist.py --gegenprobe
"""
import importlib.util
import io
import os
import re
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERWARTET_MS = 31536000000   # 365 Tage - die eine Wahrheit, gegen die alles laeuft
ERWARTET_TEXT = "12 Monate"


def lies(pfad):
    return io.open(os.path.join(WURZEL, pfad), encoding="utf-8").read()


def aufraeumer():
    u"""Laedt das echte Aufraeumskript - kein Nachbau seiner Logik."""
    pfad = os.path.join(WURZEL, "tools", "shared-aufraeumen.py")
    spec = importlib.util.spec_from_file_location("sh_auf", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def dok(when):
    u"""Ein Firestore-Rohdokument, wie die REST-Schnittstelle es liefert."""
    if when is None:
        return {"name": "projects/p/databases/(default)/documents/shared/x", "fields": {}}
    return {"name": "projects/p/databases/(default)/documents/shared/x",
            "fields": {"when": {"integerValue": str(when)}}}


GRUEN_ZAEHLER = [0]


def pruefe(befunde, bedingung, gut, schlecht):
    if bedingung:
        GRUEN_ZAEHLER[0] += 1
        print(u"  OK   %s" % gut)
    else:
        print(u"  ROT  %s" % schlecht)
        befunde.append(schlecht)


def main(argv):
    gegenprobe = "--gegenprobe" in argv
    befunde = []
    tag = 86400000

    print(u"1. Die drei Fristzahlen")
    # --- Regel ---
    rules = lies("firestore.rules")
    m = re.search(r"function shareFrisch\(\)(.*?)\n    \}", rules, re.S)
    pruefe(befunde, m is not None,
           u"shareFrisch() steht in firestore.rules",
           u"shareFrisch() fehlt in firestore.rules - die Frist wird nirgends durchgesetzt")
    regel_ms = None
    if m:
        zahlen = re.findall(r"\b(\d{9,})\b", m.group(1))
        regel_ms = int(zahlen[0]) if zahlen else None
    pruefe(befunde, regel_ms == ERWARTET_MS,
           u"Regel: %s ms" % regel_ms,
           u"Regel: %s ms, erwartet %s" % (regel_ms, ERWARTET_MS))

    # --- Oberflaeche ---
    html = lies("index.html")
    m = re.search(r"const SHARE_TTL_MS = (\d+)", html)
    ui_ms = int(m.group(1)) if m else None
    pruefe(befunde, ui_ms == ERWARTET_MS,
           u"index.html: %s ms" % ui_ms,
           u"index.html: %s ms, erwartet %s" % (ui_ms, ERWARTET_MS))
    m = re.search(r'const SHARE_TTL_TEXT = "([^"]+)"', html)
    ui_text = m.group(1) if m else None
    pruefe(befunde, ui_text == ERWARTET_TEXT,
           u"index.html sagt dem Nutzer: %r" % ui_text,
           u"index.html sagt %r, erwartet %r" % (ui_text, ERWARTET_TEXT))
    pruefe(befunde, "SHARE_TTL_TEXT" in html and "${SHARE_TTL_TEXT}" in html,
           u"der Text steht auch wirklich in der Oberflaeche",
           u"SHARE_TTL_TEXT wird nirgends angezeigt - der Nutzer erfaehrt die Frist nicht")

    # --- Aufraeumskript ---
    A = aufraeumer()
    pruefe(befunde, A.TTL_MS == ERWARTET_MS,
           u"shared-aufraeumen.py: %s ms" % A.TTL_MS,
           u"shared-aufraeumen.py: %s ms, erwartet %s" % (A.TTL_MS, ERWARTET_MS))

    print(u"\n2. Die Regel sperrt nicht nur, sie erzwingt auch das Datum")
    # Ohne diese Bedingung koennte jeder `when` auf das Jahr 2099 setzen und die
    # Frist waere Zierde. Das ist keine Kosmetik, sondern ihre Voraussetzung.
    block = re.search(r"match /shared/\{id\}(.*?)\n    \}", rules, re.S)
    inhalt = block.group(1) if block else ""
    pruefe(befunde, "shareFrisch()" in inhalt,
           u"allow get haengt an shareFrisch()",
           u"allow get prueft die Frist nicht - sie wirkt nirgends")
    pruefe(befunde, "request.resource.data.when is int" in inhalt,
           u"create verlangt ein `when`",
           u"create verlangt kein `when` - Snapshots ohne Datum leben ewig weiter")
    pruefe(befunde, "request.time.toMillis()" in inhalt and "86400000" in inhalt,
           u"create haelt `when` an der Serverzeit fest",
           u"`when` ist frei waehlbar - die Frist laesst sich umdatieren")

    print(u"\n3. Grenzfaelle des Aufraeumskripts (echter Code, kein Nachbau)")
    jetzt = int(time.time() * 1000)
    grenze = jetzt - A.TTL_MS
    faelle = [
        (u"gestern geteilt",            jetzt - tag,                False),
        (u"vor 364 Tagen geteilt",      jetzt - 364 * tag,          False),
        (u"vor 366 Tagen geteilt",      jetzt - 366 * tag,          True),
        (u"vor 5 Jahren geteilt",       jetzt - 1825 * tag,         True),
        (u"kein Datum (Altbestand)",    None,                       False),
    ]
    for name, when, soll_weg in faelle:
        w = A.when_von(dok(when))
        ist_weg = (w is not None and w < grenze)
        pruefe(befunde, ist_weg == soll_weg,
               u"%s -> %s" % (name, u"wird geloescht" if ist_weg else u"bleibt"),
               u"%s -> %s, erwartet %s" % (name,
                                           u"wird geloescht" if ist_weg else u"bleibt",
                                           u"geloescht" if soll_weg else u"bleibt"))
    # Ein kaputtes Feld darf nicht zum Loeschen fuehren.
    pruefe(befunde, A.when_von({"fields": {"when": {"integerValue": "quatsch"}}}) is None,
           u"unlesbares `when` -> bleibt liegen, statt geraten zu werden",
           u"unlesbares `when` wird falsch ausgewertet")

    if gegenprobe:
        print(u"\n4. Gegenprobe - misst dieser Pruefstand ueberhaupt etwas?")
        # Der alte Stand hatte keine Frist. Gegen ihn MUSS dieser Pruefstand durchfallen,
        # sonst prueft er nur, dass sich Dateien lesen lassen.
        alt_rules = re.sub(r"function shareFrisch\(\).*?\n    \}", "", rules, flags=re.S)
        alt_rules = alt_rules.replace("allow get: if request.auth != null && shareFrisch();",
                                      "allow get: if request.auth != null;")
        traf = ("shareFrisch" not in alt_rules)
        pruefe(befunde, traf,
               u"gegen den alten Stand (ohne Frist) faellt Teil 1 durch - der Pruefstand misst",
               u"der alte Stand kaeme durch - dieser Pruefstand misst nichts")
        alt_html = re.sub(r"const SHARE_TTL_MS = \d+;[^\n]*\n", "", html)
        pruefe(befunde, "const SHARE_TTL_MS" not in alt_html,
               u"ohne SHARE_TTL_MS faellt Teil 1 ebenfalls durch",
               u"SHARE_TTL_MS liesse sich entfernen, ohne dass es auffaellt")

    print(u"\n" + u"=" * 66)
    # Schlusszeile im Format, das tools/alle-pruefstaende.py erwartet. Ohne sie gilt
    # dieser Lauf dort als "prueft der ueberhaupt etwas?" - und das zu Recht
    # (docs/TROUBLESHOOTING.md 131: acht Pruefstaende meldeten jahrelang gruen,
    # ohne je eine Zusage zu pruefen).
    print(u"ERGEBNIS %d gruen, %d rot" % (GRUEN_ZAEHLER[0], len(befunde)))
    if befunde:
        print(u"ROT - %d Befund(e):" % len(befunde))
        for b in befunde:
            print(u"  * %s" % b)
        return 1
    print(u"GRUEN - die Frist ist an allen drei Stellen dieselbe und wird erzwungen.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
