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
    python tools/cdp.py viewport 560 900          CSS-Viewport setzen (mit Touch)
    python tools/cdp.py viewport 1280 900 desktop dasselbe ohne Touch
    python tools/cdp.py viewport aus              Ueberschreibung aufheben
    python tools/cdp.py messen 560 900 dark "<js>"  Viewport+Theme setzen UND auswerten
                                                   (Theme gilt NUR so, siehe messen())
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


def befehl_senden(methode, params, tab=None, timeout=30):
    u"""Ein beliebiges CDP-Kommando schicken (nicht nur Runtime.evaluate)."""
    import websocket
    t = tab or app_seite()
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=timeout,
                                     origin="http://127.0.0.1:%d" % PORT,
                                     suppress_origin=False)
    try:
        ws.send(json.dumps({"id": 1, "method": methode, "params": params}))
        while True:
            nachricht = json.loads(ws.recv())
            if nachricht.get("id") == 1:
                break
    finally:
        ws.close()
    return nachricht


def viewport(breite, hoehe, mobil=True):
    u"""CSS-Viewport dauerhaft setzen - die Groesse, auf die die @media-Regeln reagieren.

    Bewusst Emulation.setDeviceMetricsOverride und NICHT --window-size beim Start: Das
    Fensterargument enthaelt die Browser-Leisten, der CSS-Viewport ist entsprechend
    kleiner und trifft die Breakpoints (720/560/360 px) nicht sauber.

    Dieser Override ist persistent - er ueberlebt das Schliessen der Verbindung und ein
    location.reload(). Farbschema und Zeigertyp NICHT: die gelten nur in der Verbindung,
    die sie gesetzt hat. Wer sie braucht, nimmt messen(). Der Rueckgabewert hier sagt
    deshalb ausdruecklich, was gerade gilt - sonst haelt jemand eine Desktop-Messung fuer
    eine Handy-Abnahme.
    """
    befehl_senden("Emulation.setDeviceMetricsOverride", {
        "width": int(breite), "height": int(hoehe),
        "deviceScaleFactor": 0, "mobile": bool(mobil)
    })
    r = auswerten("JSON.stringify({b:innerWidth,h:innerHeight,"
                  "c:matchMedia('(pointer: coarse)').matches})")
    try:
        g = json.loads(r.get("wert") or "{}")
    except Exception:
        g = {}
    return "gemessen: %sx%s px | pointer: %s | Farbschema: nur ueber messen()" % (
        g.get("b", "?"), g.get("h", "?"),
        "coarse" if g.get("c") else "fine (fuer coarse: messen() nehmen)")


def viewport_aus():
    befehl_senden("Emulation.clearDeviceMetricsOverride", {})
    return "Viewport zurueckgesetzt"


def messen(breite, hoehe, welches_theme, js, mobil=True):
    u"""Viewport + Farbschema setzen UND auswerten - alles in EINER CDP-Verbindung.

    Das ist keine Bequemlichkeit, sondern notwendig. Gemessen am 25.08.2026:

      * `Emulation.setDeviceMetricsOverride` ist ein persistenter Override. Er ueberlebt
        das Schliessen der Verbindung und sogar ein location.reload().
      * `Emulation.setEmulatedMedia` und `setTouchEmulationEnabled` gelten nur, SOLANGE die
        Verbindung offen ist. In derselben Verbindung liefert die Seite `dark: false` und
        `--text-muted: #6B5F62`; nach dem Schliessen sofort wieder `dark: true`.

    Ein `theme light` als eigener Aufruf war deshalb wirkungslos - und faellt gar nicht auf,
    wenn das System selbst auf Dark steht: Dann scheint `theme dark` zu "funktionieren",
    obwohl nur das System durchschlaegt. Genau so ist hier eine Light-Abnahme beinahe als
    erledigt durchgegangen, die nie stattgefunden hat.

    `pointer: coarse` gehoert zur zweiten Gruppe und ist damit HIER erzwingbar - ueber
    `mobil=True` (setDeviceMetricsOverride mit mobile:true + setTouchEmulationEnabled).
    Ausserhalb dieser Funktion bleibt es `fine`; das ist kein Widerspruch, sondern
    dieselbe Sitzungsbindung.
    """
    import websocket
    t = app_seite()
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30,
                                     origin="http://127.0.0.1:%d" % PORT,
                                     suppress_origin=False)

    def senden(kennung, methode, params):
        ws.send(json.dumps({"id": kennung, "method": methode, "params": params}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == kennung:
                return m

    try:
        senden(1, "Emulation.setDeviceMetricsOverride", {
            "width": int(breite), "height": int(hoehe),
            "deviceScaleFactor": 0, "mobile": bool(mobil)})
        senden(2, "Emulation.setTouchEmulationEnabled",
               {"enabled": bool(mobil), "maxTouchPoints": 5 if mobil else 0})
        if welches_theme in ("light", "dark"):
            senden(3, "Emulation.setEmulatedMedia", {
                "features": [{"name": "prefers-color-scheme", "value": welches_theme}]})
        else:
            senden(3, "Emulation.setEmulatedMedia", {"features": []})
        # Ein Bild abwarten, damit Layout und Farben zum gesetzten Zustand passen.
        senden(4, "Runtime.evaluate", {
            "expression": "new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))",
            "awaitPromise": True, "returnByValue": True})
        antwort = senden(5, "Runtime.evaluate", {
            "expression": js, "awaitPromise": True, "returnByValue": True, "userGesture": True})
    finally:
        ws.close()
    ergebnis = antwort.get("result", {})
    if "exceptionDetails" in ergebnis:
        e = ergebnis["exceptionDetails"]
        return {"fehler": (e.get("exception") or {}).get("description") or e.get("text")}
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
    # Die Windows-Konsole steht auf cp1252. Sobald eine gemessene Seite ein Sonderzeichen
    # enthaelt - das Schliesskreuz der Modals reicht schon -, bricht print() sonst mit
    # UnicodeEncodeError ab, und die Messung ist verloren, obwohl sie gelaufen ist.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    befehl = sys.argv[1] if len(sys.argv) > 1 else "tabs"
    if befehl == "start":
        starten()
    elif befehl == "stop":
        stoppen()
    elif befehl == "tabs":
        for t in seiten():
            print("- %s\n  %s" % (t.get("title"), t.get("url")))
    elif befehl == "viewport":
        if len(sys.argv) > 2 and sys.argv[2] == "aus":
            print(viewport_aus())
        else:
            mobil = not (len(sys.argv) > 4 and sys.argv[4] == "desktop")
            print(viewport(sys.argv[2], sys.argv[3], mobil))
    elif befehl == "messen":
        r = messen(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        if "fehler" in r:
            print("FEHLER: " + str(r["fehler"])); sys.exit(1)
        w = r["wert"]
        print(json.dumps(w, ensure_ascii=False, indent=2) if isinstance(w, (dict, list)) else w)
    elif befehl == "eval":
        r = auswerten(sys.argv[2])
        if "fehler" in r:
            print("FEHLER: " + str(r["fehler"])); sys.exit(1)
        w = r["wert"]
        print(json.dumps(w, ensure_ascii=False, indent=2) if isinstance(w, (dict, list)) else w)
    else:
        raise SystemExit(__doc__)
