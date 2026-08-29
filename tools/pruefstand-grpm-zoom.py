# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: die Rollenwahl der Gruppe zoomt auf iOS nicht mehr (27.08.2026).

Der Fall
--------
`.grp-m select` (die Rollenwahl je Mitglied in der Gruppenverwaltung) stand auf 13 px.
Safari zoomt beim Oeffnen eines <select> unter 16 px in die Seite hinein. Der Schutz dagegen
gibt es im Projekt seit Fall 117 als:

    @media (pointer: coarse) { input…, select, textarea { font-size: 16px; } }

Der Block greift hier trotzdem nicht: `.grp-m select` hat die hoehere Spezifitaet (0,1,1
gegen 0,0,1) UND steht weiter unten. Zwei Gruende, aus denen 13 px gewinnt - beide unsichtbar,
wenn man nur die Schutzregel liest und zufrieden ist.

Warum das einen Browser braucht
-------------------------------
Spezifitaet und Reihenfolge lassen sich am Quelltext behaupten, aber nicht beweisen. Erst
`getComputedStyle()` sagt, welche Regel wirklich gewonnen hat - und `pointer: coarse` gilt
nur unter Touch-Emulation, also nur ueber das DevTools-Protokoll.

Gemessen wird echtes, ausgeschnittenes CSS aus index.html - kein Nachbau. Der Prueftext
haengt an denselben Klassen, an denen die App haengt.

Drei Messungen, und die dritte ist die eigentliche Gegenprobe:

    mit Touch, CSS wie es ist          -> 16 px   der Fix greift
    mit Touch, neuer Block entfernt    -> 13 px   ohne ihn faellt es zurueck (GEGENPROBE)
    ohne Touch, CSS wie es ist         -> 13 px   am Rechner aendert sich nichts

Ohne die zweite Zeile misst der Pruefstand nur, dass 16 px dort steht - nicht, dass dieser
Block sie bewirkt.

Aufruf:  python tools/pruefstand-grpm-zoom.py
Rueckgabewert: 0 alle drei wie erwartet, 1 sonst.
"""
import io
import json
import os
import re
import subprocess
import sys
import time

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-grpm-zoom.html")
ZIEL_OHNE = os.path.join(BASIS, "tools", "pruefstand-grpm-zoom-ohne.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PORT = 9333
PROFIL = os.path.join(os.environ.get("TEMP", "."), "mp-edge-grpm")

sys.path.insert(0, os.path.join(BASIS, "tools"))
import quelle as pm_quelle

# Ueber pm_quelle.lade_seite() statt direkt: seit das CSS in css/*.css liegt, gibt es
# in index.html keinen <style>-Block mehr. quelle baut die eigenen Dateien an Ort
# und Stelle wieder ein - derselbe Text, nur wieder in einer Datei. Kein Nachbau.
text = pm_quelle.lade_seite(QUELLE)

# ---- Schnitt: das komplette CSS, echter Produktionscode ----
# Seit der Aufteilung sind es vier Dateien. pm_quelle.css_gesamt() liefert sie in
# Ladereihenfolge als einen Text - nur den ersten Block zu nehmen hiesse, gegen
# ein Viertel der Regeln zu messen und trotzdem ein Ergebnis zu melden.
CSS = pm_quelle.css_gesamt(QUELLE)

for muss in [".grp-m select", "@media (pointer: coarse)"]:
    if muss not in CSS:
        raise SystemExit("Ausschnitt unvollstaendig, fehlt: " + muss)

# ---- Die Fassung OHNE den neuen Block: Gegenprobe gegen den alten Stand ----
# Genau der Block, den der Fix hinzugefuegt hat - nicht die Schutzregel aus Fall 117, die
# bleibt stehen. Faellt die Messung damit auf 13 px zurueck, ist bewiesen, dass dieser eine
# Block den Unterschied macht und nicht irgendeine andere Regel.
OHNE = re.sub(r"\n  @media \(pointer: coarse\) \{\s*\n\s*\.grp-m select \{ font-size: 16px; \}\s*\n\s*\}",
              "", CSS, count=1)
if OHNE == CSS:
    raise SystemExit("Gegenprobe nicht bildbar - der Block sieht anders aus als erwartet")

SEITE = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand grp-m Zoom</title>
<style>
__CSS__
</style>
<!-- Derselbe Aufbau wie in memberRowHtml(): Avatar, Name, darunter die Rollenwahl. -->
<div class="grp-m">
  <span class="avatar" aria-hidden="true">PF</span>
  <span class="who"><b>Testperson</b><small>Mitglied</small></span>
  <select id="rolle">
    <option>darf planen</option>
    <option>darf zusehen</option>
  </select>
</div>
"""


def schreibe(pfad, css):
    io.open(pfad, "w", encoding="utf-8").write(SEITE.replace("__CSS__", css))


schreibe(ZIEL, CSS)
schreibe(ZIEL_OHNE, OHNE)


# --------------------------------------------------------------------------- Browser
def seiten():
    import urllib.request
    roh = urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT, timeout=5).read()
    return json.loads(roh.decode("utf-8"))


def starte_edge():
    try:
        seiten()
        return None   # laeuft schon
    except Exception:
        pass
    p = subprocess.Popen([
        EDGE, "--headless=new", "--disable-gpu",
        "--remote-debugging-port=%d" % PORT,
        "--remote-allow-origins=*",
        "--user-data-dir=" + PROFIL,
        "--no-first-run", "--no-default-browser-check",
        "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        time.sleep(0.5)
        try:
            seiten()
            return p
        except Exception:
            continue
    raise SystemExit("Edge kam nicht hoch (Port %d)" % PORT)


def miss(datei, touch):
    """Laedt die Datei und liefert die gerechnete font-size des <select>.

    Alles in EINER Verbindung: setTouchEmulationEnabled gilt nur, solange sie offen ist -
    dieselbe Sitzungsbindung, die in tools/cdp.py dokumentiert ist. Wer den Zeigertyp in
    einem eigenen Aufruf setzt, misst hinterher wieder `fine` und merkt es nicht.
    """
    import websocket
    ziel = [s for s in seiten() if s.get("type") == "page"][0]
    ws = websocket.create_connection(ziel["webSocketDebuggerUrl"], timeout=30,
                                     origin="http://127.0.0.1:%d" % PORT,
                                     suppress_origin=False)
    kennung = [0]

    def senden(methode, params):
        kennung[0] += 1
        eigene = kennung[0]
        ws.send(json.dumps({"id": eigene, "method": methode, "params": params}))
        while True:
            nachricht = json.loads(ws.recv())
            if nachricht.get("id") == eigene:
                return nachricht

    try:
        senden("Emulation.setDeviceMetricsOverride", {
            "width": 390, "height": 844, "deviceScaleFactor": 0, "mobile": bool(touch)})
        senden("Emulation.setTouchEmulationEnabled",
               {"enabled": bool(touch), "maxTouchPoints": 5 if touch else 0})
        senden("Page.enable", {})
        senden("Page.navigate", {"url": "file:///" + datei.replace("\\", "/")})
        time.sleep(1.2)
        antwort = senden("Runtime.evaluate", {
            "expression": "JSON.stringify({"
                          "px: getComputedStyle(document.getElementById('rolle')).fontSize,"
                          "coarse: matchMedia('(pointer: coarse)').matches})",
            "returnByValue": True})
    finally:
        ws.close()
    roh = ((antwort.get("result") or {}).get("result") or {}).get("value")
    return json.loads(roh) if roh else {}


def main():
    prozess = starte_edge()
    try:
        faelle = [
            ("mit Touch, CSS wie es ist       ", ZIEL,      True,  "16px", True),
            ("mit Touch, neuer Block entfernt ", ZIEL_OHNE, True,  "13px", True),
            ("ohne Touch, CSS wie es ist      ", ZIEL,      False, "13px", False),
        ]
        print("Pruefstand: Rollenwahl der Gruppe, iOS-Zoom")
        print("=" * 66)
        schlecht = 0
        for name, datei, touch, soll, soll_coarse in faelle:
            g = miss(datei, touch)
            ist = g.get("px", "?")
            gut = (ist == soll and g.get("coarse") is soll_coarse)
            if not gut:
                schlecht += 1
            print("  %s %s  %s  (pointer: %s)" % (
                "OK  " if gut else "FEHL", name, ist,
                "coarse" if g.get("coarse") else "fine"))
            if not gut:
                print("       erwartet: %s bei pointer %s" % (
                    soll, "coarse" if soll_coarse else "fine"))
        print("=" * 66)
        if schlecht:
            print("FEHLGESCHLAGEN: %d von %d" % (schlecht, len(faelle)))
            return 1
        print("ALLE 3 MESSUNGEN WIE ERWARTET.")
        print("Die mittlere Zeile ist die Gegenprobe: ohne den neuen Block faellt es")
        print("auf 13 px zurueck - der Block bewirkt den Unterschied, nicht der Zufall.")
        return 0
    finally:
        if prozess:
            prozess.terminate()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
