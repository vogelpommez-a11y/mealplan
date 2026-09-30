# -*- coding: utf-8 -*-
u"""Spricht die App OHNE Konto mit fremden Servern? Gemessen, nicht gegrept.

    python tools/netz-ohne-konto.py                 # lokal (localhost:8000)
    python tools/netz-ohne-konto.py --live          # www.paddysmealplan.de
    python tools/netz-ohne-konto.py --gegenprobe    # alter Stand (live) MUSS durchfallen,
                                                    # neuer (lokal) MUSS bestehen - nur
                                                    # solange der Fix noch nicht gepusht ist

Wozu
----
Die Datenschutzerklaerung sagt in Ziffer 3 und 5 zu: Ohne Konto entsteht keine Verbindung zu
Google. CLAUDE.md §1 sagt: Kein Code wird zur Laufzeit nachgeladen (Apple 2.5.2). Beides ist
eine Aussage ueber das NETZ, und das Netz sieht man nur im Browser.

Warum vier Browserkennungen
---------------------------
Am 30.09.2026 war die App auf dem Desktop sauber - und lud auf iPhone, Android und Safari
trotzdem apis.google.com/js/api.js und ein iframe von firebaseapp.com (TROUBLESHOOTING §181).
Das Firebase-SDK entscheidet an der Browserkennung (_shouldInitProactively). Eine Messung nur
mit Desktop-Chrome hat den Fehler genau deshalb uebersehen. Eine Kennung allein reicht nie.

Was gemessen wird - und was nicht
---------------------------------
Je Kennung, frisches Profil, keine Anmeldung, vier Phasen: Erstaufruf, Impressum und
Datenschutz, Anmeldebildschirm (ohne Klick auf Google), lokales Profil mit allen Reitern.
Erfasst werden alle Anfragen der Seite (auch Dokumente von iframes), Cookies, Speicher.
NICHT erfasst: was ein fremdes iframe selbst nachlaedt - braucht es auch nicht, denn schon
das iframe-Dokument ist ein fremder Host und laesst den Lauf durchfallen.
Die Kamera (Barcode -> Open Food Facts) wird nicht ausgeloest; die ist nutzergetrieben und in
Ziffer 7a beschrieben.

Nur lesend: eigenes Wegwerf-Profil, nie ein Konto, nie ein Schreibzugriff auf die Cloud.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time, urllib.request
from urllib.parse import urlparse

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9334
LOKAL = "http://localhost:8000/index.html"
LIVE = "https://www.paddysmealplan.de/"

KENNUNGEN = [
    # (Name, User-Agent, Plattform, Breite, Hoehe, mobil)
    ("desktop-chrome",
     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
     "Win32", 1280, 900, False),
    ("iphone-safari",
     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
     "iPhone", 390, 844, True),
    ("android-chrome",
     "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
     "Linux armv8l", 412, 915, True),
    ("mac-safari",
     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
     "MacIntel", 1280, 900, False),
]


def server_laeuft():
    try:
        urllib.request.urlopen(LOKAL, timeout=2).read(1)
        return True
    except Exception:
        return False


def server_sicherstellen():
    if server_laeuft():
        return True
    print(u"Der lokale Server laeuft nicht - starte test-server.ps1 ...")
    subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Minimized",
                      "-File", os.path.join(WURZEL, "test-server.ps1")], cwd=WURZEL)
    for _ in range(30):
        time.sleep(0.5)
        if server_laeuft():
            return True
    return False


class Sitzung(object):
    def __init__(self, ws):
        self.ws, self.nid, self.phase = ws, 0, "?"
        self.anfragen = []

    def _ereignis(self, m):
        if m.get("method") == "Network.requestWillBeSent":
            u = m["params"]["request"]["url"]
            if u.startswith(("http://", "https://", "ws://", "wss://")):
                self.anfragen.append({"phase": self.phase, "host": urlparse(u).netloc,
                                      "typ": m["params"].get("type"), "url": u[:160]})

    def pumpen(self, sek):
        import websocket
        ende = time.time() + sek
        while time.time() < ende:
            try:
                self._ereignis(json.loads(self.ws.recv()))
            except websocket.WebSocketTimeoutException:
                pass

    def cmd(self, methode, params=None):
        import websocket
        self.nid += 1
        mid = self.nid
        self.ws.send(json.dumps({"id": mid, "method": methode, "params": params or {}}))
        ende = time.time() + 30
        while time.time() < ende:
            try:
                m = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                continue
            if m.get("id") == mid:
                return m.get("result", {})
            self._ereignis(m)
        return {}

    def js(self, ausdruck):
        r = self.cmd("Runtime.evaluate", {"expression": ausdruck, "awaitPromise": True,
                                          "returnByValue": True, "userGesture": True})
        return (r.get("result") or {}).get("value")


def klick_text(s, text):
    return s.js(u"""(()=>{const e=[...document.querySelectorAll('a,button')].find(x=>x.textContent.trim()===%s&&x.offsetParent!==null);
        if(!e) return false; e.click(); return true;})()""" % json.dumps(text))


def modal_zu(s):
    s.js("""(()=>{const b=[...document.querySelectorAll('button')].find(b=>/schlie/i.test((b.getAttribute('aria-label')||'')+b.textContent)&&b.offsetParent!==null); if(b) b.click();})()""")


def ein_lauf(url, kennung):
    import websocket
    name, ua, plattform, breite, hoehe, mobil = kennung
    profil = tempfile.mkdtemp(prefix="mp-netz-")
    proc = subprocess.Popen([CHROME, "--headless=new", "--remote-debugging-port=%d" % PORT,
                             "--remote-allow-origins=*", "--user-data-dir=" + profil,
                             "--no-first-run", "--no-default-browser-check", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        tab = None
        for _ in range(60):
            try:
                seiten = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json/list" % PORT, timeout=2).read())
                tab = [t for t in seiten if t["type"] == "page"][0]
                break
            except Exception:
                time.sleep(0.25)
        if not tab:
            raise SystemExit(u"Chrome kam nicht hoch.")
        ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=60)
        ws.settimeout(0.3)
        s = Sitzung(ws)
        s.cmd("Network.enable"); s.cmd("Page.enable"); s.cmd("Runtime.enable")
        # Kennung VOR dem ersten Aufruf setzen - das SDK liest sie beim Start.
        s.cmd("Network.setUserAgentOverride", {"userAgent": ua, "platform": plattform})
        s.cmd("Emulation.setDeviceMetricsOverride", {"width": breite, "height": hoehe,
                                                     "deviceScaleFactor": 3 if mobil else 1, "mobile": mobil})
        s.cmd("Emulation.setTouchEmulationEnabled", {"enabled": mobil})

        s.phase = "erstaufruf"
        s.cmd("Page.navigate", {"url": url}); s.pumpen(9)
        start_ok = bool(s.js("!!document.querySelector('#a-local')"))

        s.phase = "rechtstexte"
        for t in ("Impressum", "Datenschutz"):
            if klick_text(s, t):
                s.pumpen(1.5); modal_zu(s); s.pumpen(0.8)

        s.phase = "anmeldebildschirm"
        s.js("(()=>{const b=document.querySelector('#a-cloud'); if(b) b.click();})()"); s.pumpen(4)

        s.phase = "lokal"
        s.cmd("Page.reload"); s.pumpen(6)
        s.js("(()=>{const b=document.querySelector('#a-local'); if(b) b.click();})()"); s.pumpen(1)
        s.js("""(()=>{const n=document.querySelector('#a-name'); if(!n) return; n.value='Netzprobe';
               n.dispatchEvent(new Event('input',{bubbles:true})); document.querySelector('#a-go').click();})()""")
        s.pumpen(4)
        reiter = s.js("[...new Set([...document.querySelectorAll('[data-tab]')].map(e=>e.dataset.tab))]") or []
        for r in reiter:
            s.js("(()=>{const e=[...document.querySelectorAll('[data-tab=%s]')].find(e=>e.offsetParent!==null); if(e) e.click();})()"
                 % json.dumps(r))
            s.pumpen(2.5)

        speicher = {
            "cookies": [c["name"] + "@" + c["domain"] for c in s.cmd("Network.getAllCookies").get("cookies", [])],
            "indexedDB": s.js("indexedDB.databases ? indexedDB.databases().then(d=>d.map(x=>x.name).sort()) : []"),
        }
        ws.close()
        eigen = urlparse(url).netloc
        fremd = [a for a in s.anfragen if a["host"] != eigen]
        return {"kennung": name, "start_ok": start_ok, "reiter": reiter,
                "anzahl": len(s.anfragen), "fremd": fremd, "speicher": speicher}
    finally:
        proc.terminate()
        try:
            proc.wait(5)
        except Exception:
            proc.kill()
        shutil.rmtree(profil, ignore_errors=True)


def pruefen(url, still=False):
    ergebnisse = [ein_lauf(url, k) for k in KENNUNGEN]
    sauber = True
    for e in ergebnisse:
        ok = e["start_ok"] and not e["fremd"] and not e["speicher"]["cookies"]
        sauber = sauber and ok
        if still:
            continue
        print(u"  %-15s %s  %d Anfragen, %d fremd, Reiter: %s" % (
            e["kennung"], u"OK    " if ok else u"FEHLER", e["anzahl"], len(e["fremd"]), ",".join(e["reiter"])))
        if not e["start_ok"]:
            print(u"      Startbildschirm nicht erreicht - Messung nicht aussagekraeftig")
        hosts = {}
        for a in e["fremd"]:
            hosts.setdefault((a["host"], a["phase"]), []).append(a["url"])
        for (h, ph), urls in sorted(hosts.items()):
            print(u"      %-38s Phase %-18s %s" % (h, ph, urls[0][:70]))
        if e["speicher"]["cookies"]:
            print(u"      Cookies: %s" % ", ".join(e["speicher"]["cookies"]))
        print(u"      IndexedDB: %s" % ", ".join(e["speicher"]["indexedDB"] or []))
    return sauber, ergebnisse


def main():
    p = argparse.ArgumentParser(description=u"Netzverkehr ohne Konto messen")
    p.add_argument("--live", action="store_true", help=u"gegen www.paddysmealplan.de")
    p.add_argument("--gegenprobe", action="store_true",
                   help=u"live (alter Stand) muss durchfallen, lokal (neuer Stand) bestehen")
    a = p.parse_args()
    if not os.path.exists(CHROME):
        print(u"Chrome nicht gefunden: %s" % CHROME)
        return 2

    if a.gegenprobe:
        if not server_sicherstellen():
            return 2
        print(u"Alter Stand (live) - muss FEHLER zeigen:")
        alt_sauber, _ = pruefen(LIVE)
        print(u"Neuer Stand (lokal) - muss OK zeigen:")
        neu_sauber, _ = pruefen(LOKAL)
        if not alt_sauber and neu_sauber:
            print(u"\nGEGENPROBE BESTANDEN: Der Pruefer erkennt den alten Fehler, der neue Stand ist sauber.")
            return 0
        if alt_sauber:
            print(u"\nGEGENPROBE UNGUELTIG: Der alte Stand faellt nicht durch - misst der Pruefer ueberhaupt?"
                  u"\n(Oder ist der Fix schon live? Dann ist keine Gegenprobe gegen live mehr moeglich.)")
            return 1
        print(u"\nGEGENPROBE: Der neue Stand ist NICHT sauber.")
        return 1

    url = LIVE if a.live else LOKAL
    if not a.live and not server_sicherstellen():
        return 2
    print(u"Netz ohne Konto: %s" % url)
    sauber, _ = pruefen(url)
    print(u"\n%s" % (u"SAUBER: kein fremder Server, keine Cookies - bei allen vier Kennungen."
                      if sauber else u"BEFUND: Ohne Konto wird ein fremder Server angefragt (oder Start fehlgeschlagen)."))
    return 0 if sauber else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
