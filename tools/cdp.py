# -*- coding: utf-8 -*-
u"""
Kleiner Fernbedienungs-Helfer fuer einen sichtbaren Chrome ueber das DevTools-Protokoll.

Zweck: Abnahmen, die ein ECHTES Cloud-Konto brauchen und deshalb weder headless noch mit
einem Ausschneide-Pruefstand zu fahren sind (Anmeldung, Firestore, Zwei-Geraete-Verhalten).
Der Mensch meldet sich einmal von Hand an - Passwoerter laufen nie durch dieses Skript -,
danach liest und steuert es die laufende Seite.

Aufruf:
    python tools/cdp.py start          Chrome sichtbar mit Fernbedienung starten
    python tools/cdp.py tabs           offene Seiten auflisten
    python tools/cdp.py eval "<js>"    JavaScript in der App-Seite auswerten
    python tools/cdp.py stop           Chrome beenden

Bewusst ein eigenes Profilverzeichnis: Der laufende Alltags-Chrome des Nutzers wird nicht
angefasst, und eine bereits offene Chrome-Sitzung verhindert sonst das Debug-Port-Flag.
"""
import io, json, os, subprocess, sys, time, urllib.request

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9222
PROFIL = os.path.join(os.environ.get("TEMP", "."), "mp-chrome-abnahme")
START_URL = "http://localhost:8000/index.html"


def _json(pfad):
    with urllib.request.urlopen("http://127.0.0.1:%d%s" % (PORT, pfad), timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))


def seiten():
    return [t for t in _json("/json/list") if t.get("type") == "page"]


def app_seite():
    # Die App-Seite, nicht irgendein Tab: erst nach localhost suchen, sonst die erste Seite.
    s = seiten()
    fuer_app = [t for t in s if "localhost:8000" in (t.get("url") or "")]
    if fuer_app:
        return fuer_app[0]
    if s:
        return s[0]
    raise SystemExit("Keine offene Seite gefunden. Laeuft Chrome ueber 'start'?")


def auswerten(js, tab=None, timeout=30):
    import websocket
    t = tab or app_seite()
    # origin mitschicken: Chrome lehnt WebSocket-Verbindungen zum Debug-Port sonst mit
    # "403 Rejected an incoming WebSocket connection" ab, sobald ein Origin-Header fehlt
    # bzw. nicht freigegeben ist. Passt zu --remote-allow-origins beim Start.
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=timeout,
                                     origin="http://127.0.0.1:%d" % PORT,
                                     suppress_origin=False)
    try:
        # awaitPromise: damit `await`-Ausdruecke und Promises (CloudSync.load) durchlaufen.
        # returnByValue: sonst kommt nur eine Objekt-ID zurueck, kein lesbarer Wert.
        ws.send(json.dumps({
            "id": 1, "method": "Runtime.evaluate",
            "params": {"expression": js, "awaitPromise": True,
                       "returnByValue": True, "userGesture": True}
        }))
        while True:
            nachricht = json.loads(ws.recv())
            if nachricht.get("id") == 1:
                break
    finally:
        ws.close()
    ergebnis = nachricht.get("result", {})
    if "exceptionDetails" in ergebnis:
        e = ergebnis["exceptionDetails"]
        beschreibung = (e.get("exception") or {}).get("description") or e.get("text")
        return {"fehler": beschreibung}
    return {"wert": (ergebnis.get("result") or {}).get("value")}


def starten():
    try:
        seiten()
        print("Chrome mit Fernbedienung laeuft bereits auf Port %d." % PORT)
        return
    except Exception:
        pass
    subprocess.Popen([
        CHROME,
        "--remote-debugging-port=%d" % PORT,
        "--remote-allow-origins=*",
        "--user-data-dir=" + PROFIL,
        "--no-first-run", "--no-default-browser-check",
        START_URL
    ])
    for _ in range(40):
        time.sleep(0.5)
        try:
            seiten(); print("Chrome laeuft. Port %d, Profil %s" % (PORT, PROFIL)); return
        except Exception:
            continue
    raise SystemExit("Chrome kam nicht hoch.")


def stoppen():
    subprocess.call(["taskkill", "/F", "/IM", "chrome.exe", "/FI",
                     "WINDOWTITLE ne DUMMY"], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
    print("Chrome beendet.")


if __name__ == "__main__":
    befehl = sys.argv[1] if len(sys.argv) > 1 else "tabs"
    if befehl == "start":
        starten()
    elif befehl == "stop":
        stoppen()
    elif befehl == "tabs":
        for t in seiten():
            print("- %s\n  %s" % (t.get("title"), t.get("url")))
    elif befehl == "eval":
        r = auswerten(sys.argv[2])
        if "fehler" in r:
            print("FEHLER: " + str(r["fehler"])); sys.exit(1)
        w = r["wert"]
        print(json.dumps(w, ensure_ascii=False, indent=2) if isinstance(w, (dict, list)) else w)
    else:
        raise SystemExit(__doc__)
