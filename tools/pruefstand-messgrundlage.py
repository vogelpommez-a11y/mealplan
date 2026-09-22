# -*- coding: utf-8 -*-
u"""Misst der Pruefstand ueberhaupt die App - oder Chromes Fehlerseite?

TROUBLESHOOTING 174. Am 20.09.2026 meldete `tools/abnahme-mobil.py` eine zu kleine
Trefferflaeche an `div#suggestions-list`. Dieses Element gibt es in der App nicht: Es
gehoert zu Chromes eigener Fehlerseite, deren Links 20 px hoch sind. `test-server.ps1`
war zwischendurch weggefallen, und gemessen wurde nicht die App, sondern die
Entschuldigung dafuer, dass es sie gerade nicht gab.

  > Ein Pruefstand, der seine Messgrundlage nicht prueft, misst irgendwas - und meldet
  > es mit derselben Bestimmtheit wie einen echten Befund.

Seitdem prueft `Sitzung.start()` den Server (und startet ihn notfalls) und `laden()`
sieht nach jedem Laden nach, ob `.app` und `#view` ueberhaupt da sind. `a11y-pruefung.py`
importiert dieselbe Sitzung und erbt beides mit.

Dieses Skript ist die Gegenprobe dazu - ohne sie waere nicht belegt, dass die neue
Pruefung ueberhaupt anschlaegt:

  A) ohne Server bricht der Lauf mit klarer Ansage ab, statt zu messen
  B) mit Server, aber auf einer fremden Seite, schlaegt die Geruestpruefung an -
     und die echte App wird trotzdem nicht faelschlich abgelehnt

    python tools/pruefstand-messgrundlage.py

Braucht Chrome. Teil B wird uebersprungen, wenn sich kein lokaler Server starten laesst.
"""
import importlib.util, io, os, sys, time
sys.stdout.reconfigure(encoding="utf-8")
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("am", os.path.join(WURZEL, "tools", "abnahme-mobil.py"))
AM = importlib.util.module_from_spec(spec); spec.loader.exec_module(AM)

fehler = 0
gruen = 0

# --- A: toter Port -------------------------------------------------------
AM.URL = "http://localhost:8099/index.html"
AM.server_sicherstellen = lambda: AM.server_laeuft()   # nicht 15 s auf ps1 warten
s = AM.Sitzung()
try:
    s.start()
    print("A ROT   - start() lief durch, obwohl kein Server da ist")
    fehler += 1
except SystemExit as e:
    if "TROUBLESHOOTING 174" in str(e):
        gruen += 1
        print("A GRUEN - ohne Server bricht start() mit klarer Ansage ab")
    else:
        print("A ROT   - Abbruch, aber ohne Hinweis auf die Ursache: %s" % e)
        fehler += 1

# --- B: Server da, aber fremde Seite ------------------------------------
import importlib
spec2 = importlib.util.spec_from_file_location("am2", os.path.join(WURZEL, "tools", "abnahme-mobil.py"))
AM2 = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(AM2)
if not AM2.server_sicherstellen():
    print("B GRAU  - kein lokaler Server, Teil B nicht gefahren")
else:
    s2 = AM2.Sitzung()
    s2.start()
    try:
        s2.senden("Page.navigate", {"url": "data:text/html,<h1>keine App</h1>"})
        time.sleep(1.2)
        try:
            s2.messgrundlage_pruefen()
            print("B ROT   - fremde Seite wurde als App durchgewunken")
            fehler += 1
        except SystemExit as e:
            gruen += 1
            print("B GRUEN - fremde Seite erkannt: %s" % str(e).splitlines()[0])
        # Und die Probe aufs Exempel: die echte App muss durchgehen
        s2.laden()
        gruen += 1
        print("B GRUEN - die echte App wird nicht faelschlich abgelehnt")
    finally:
        s2.stoppen()

# Schlusszeile im Format, das tools/alle-pruefstaende.py erwartet - sonst gilt dieser
# Lauf dort als "prueft der ueberhaupt etwas?" (docs/TROUBLESHOOTING.md 131).
print("\nERGEBNIS %d gruen, %d rot" % (gruen, fehler))
print("%s" % ("GEGENPROBE GRUEN" if not fehler else "GEGENPROBE ROT (%d)" % fehler))
sys.exit(1 if fehler else 0)
