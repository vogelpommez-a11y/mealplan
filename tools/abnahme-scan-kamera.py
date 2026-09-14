# -*- coding: utf-8 -*-
u"""
Der Live-Kamera-Weg des Barcode-Scanners, am Rechner gefahren.

Bis heute war dieser Weg NIE gesehen: Am PC gibt es keine Kamera, geprueft wurde deshalb
immer nur der Foto-Weg, und der Ausschneide-Pruefstand (tools/pruefstand-scan-zeile.py)
stubbt den Sucher komplett weg. Genau darin lag die Luecke - der Pruefstand war gruen,
waehrend der Weg am Geraet weiter tot war (Meldung Paddy, 14.09.2026: "Reiter Plan geht,
Meals -> Meal anlegen -> Zutat hinzufuegen nicht, es flimmert kurz und dann nichts").

Chrome kann eine Kamera aus einer Videodatei vortaeuschen. Damit laeuft hier der ECHTE
Weg: echter Sucher, echtes getUserMedia, echtes ZXing, echter Overlay-Stapel, echte
Fokusereignisse, echter Netzabruf bei Open Food Facts. Gestubbt ist nichts.

  python tools/abnahme-scan-kamera.py           # beide Wege messen
  python tools/abnahme-scan-kamera.py --zeigen  # Browser am Ende offen lassen

Braucht den lokalen Server: powershell -NoProfile -File test-server.ps1

Eigenes Profil auf Port 9224, bewusst NICHT angemeldet - siehe docs/TESTING.md
(Cloud-Falle: localhost trennt nur den lokalen Speicher, nicht die Cloud).
"""
import json, os, subprocess, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cdp

PORT = 9224
PROFIL = os.path.join(os.environ.get("TEMP", "."), "mp-chrome-scan")
VIDEO = os.path.join(os.environ.get("TEMP", "."), "mp-barcode-640x480.y4m")
URL = "http://localhost:8000/index.html"

# Nutella 400 g - in Open Food Facts sicher vorhanden, Pruefziffer gueltig.
EAN = "3017620422003"
# Gueltige Pruefziffer, aber kein Produkt dahinter: Open Food Facts antwortet mit HTTP 404.
# Das ist beim Scannen der HAEUFIGSTE Ausgang, nicht der Ausnahmefall - siehe
# docs/TROUBLESHOOTING.md 167. Vorher meldete die App dafuer "offline?".
UNBEKANNT = "4099999999996"

# ---------------------------------------------------------------- EAN-13 -----
L = ["0001101", "0011001", "0010011", "0111101", "0100011",
     "0110001", "0101111", "0111011", "0110111", "0001011"]
G = ["0100111", "0110011", "0011011", "0100001", "0011101",
     "0111001", "0000101", "0010001", "0001001", "0010111"]
R = ["1110010", "1100110", "1101100", "1000010", "1011100",
     "1001110", "1010000", "1000100", "1001000", "1110100"]
PARITAET = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
            "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]


def ean13_muster(code):
    u"""Die 95 Module eines EAN-13 als '0'/'1'-Kette ('1' = schwarzer Strich)."""
    if len(code) != 13 or not code.isdigit():
        raise SystemExit("EAN-13 erwartet 13 Ziffern: %r" % code)
    z = [int(c) for c in code]
    pruef = (10 - sum(z[i] * (3 if i % 2 else 1) for i in range(12)) % 10) % 10
    if pruef != z[12]:
        raise SystemExit("Pruefziffer stimmt nicht (erwartet %d)" % pruef)
    muster = "101"                                   # Start-Guard
    par = PARITAET[z[0]]
    for i in range(6):
        muster += (L if par[i] == "L" else G)[z[i + 1]]
    muster += "01010"                                # Mittel-Guard
    for i in range(7, 13):
        muster += R[z[i]]
    muster += "101"                                  # End-Guard
    return muster


def y4m_schreiben(pfad, code, breite=640, hoehe=480, modul=4, bars=260, frames=30):
    u"""Standbild-Video mit dem Barcode - das Format, das Chrome als Kamera einliest."""
    muster = ean13_muster(code)
    strichbreite = len(muster) * modul
    links = (breite - strichbreite) // 2
    oben = (hoehe - bars) // 2
    WEISS, SCHWARZ = 235, 16

    zeile_bars = bytearray([WEISS] * breite)
    for i, m in enumerate(muster):
        if m == "1":
            for x in range(links + i * modul, links + (i + 1) * modul):
                zeile_bars[x] = SCHWARZ
    zeile_weiss = bytes([WEISS] * breite)
    zeile_bars = bytes(zeile_bars)

    y = bytearray()
    for zy in range(hoehe):
        y += zeile_bars if oben <= zy < oben + bars else zeile_weiss
    uv = bytes([128] * ((breite // 2) * (hoehe // 2)))

    with open(pfad, "wb") as f:
        f.write(("YUV4MPEG2 W%d H%d F15:1 Ip A1:1 C420mpeg2\n" % (breite, hoehe)).encode())
        for _ in range(frames):
            f.write(b"FRAME\n")
            f.write(y)
            f.write(uv)
            f.write(uv)
    return pfad


# ------------------------------------------------------------- Fernsteuern ---
def _json_holen(pfad):
    with urllib.request.urlopen("http://127.0.0.1:%d%s" % (PORT, pfad), timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))


def seiten():
    return _json_holen("/json/list")


def app_seite():
    for s in seiten():
        if s.get("type") == "page" and "index.html" in (s.get("url") or ""):
            return s
    raise SystemExit("Keine App-Seite gefunden - laeuft test-server.ps1?")


def js(code, timeout=40):
    u"""Wertet JavaScript in der App-Seite aus (eigener Port, deshalb nicht cdp.auswerten).

    cdp.auswerten() gibt den Wert in einer Huelle {"wert": ...} zurueck; hier wird er
    ausgepackt, damit jede Aufrufstelle mit dem blanken Ergebnis arbeitet.
    """
    alt_port, alt_seite = cdp.PORT, cdp.app_seite
    cdp.PORT = PORT
    cdp.app_seite = app_seite
    try:
        r = cdp.auswerten(code, timeout=timeout)
    finally:
        cdp.PORT, cdp.app_seite = alt_port, alt_seite
    return r["wert"] if isinstance(r, dict) and "wert" in r else r


def chrome_starten(ean=None):
    try:
        seiten()
        print("Chrome auf Port %d laeuft bereits." % PORT)
        return
    except Exception:
        pass
    ean = ean or EAN
    y4m_schreiben(VIDEO, ean)
    print("Barcode-Video: %s (EAN %s)" % (VIDEO, ean))
    subprocess.Popen([
        cdp.CHROME,
        "--remote-debugging-port=%d" % PORT,
        "--remote-allow-origins=*",
        "--user-data-dir=" + PROFIL,
        "--no-first-run", "--no-default-browser-check",
        # Die gefaelschte Kamera. --use-fake-ui beantwortet die Berechtigungsfrage selbst,
        # sonst haengt getUserMedia an einem Dialog, den niemand wegklickt.
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        "--use-file-for-fake-video-capture=" + VIDEO,
        URL,
    ])
    for _ in range(40):
        time.sleep(0.5)
        try:
            seiten()
            print("Chrome laeuft. Port %d" % PORT)
            return
        except Exception:
            continue
    raise SystemExit("Chrome kam nicht hoch.")


def chrome_stoppen():
    """NUR den eigenen Chrome beenden - erkannt am Debug-Port in der Kommandozeile.

    taskkill /IM chrome.exe wuerde auch den Alltags-Browser des Nutzers mitnehmen,
    samt offener Tabs. Der Port ist das einzige verlaessliche Unterscheidungsmerkmal.
    """
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | "
          "Where-Object { $_.CommandLine -like '*--remote-debugging-port=%d*' } | "
          "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" % PORT)
    subprocess.call(["powershell", "-NoProfile", "-Command", ps],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --------------------------------------------------------------- Bedienen ---
# Echte Maus-Ereignisse, kein el.click(): Ein Klick per JavaScript fokussiert den Knopf
# NICHT. Genau der Fokuswechsel ist hier aber der Kern der Sache - mit .click() misst man
# am Fehler vorbei (dieselbe Falle wie bei den Wischgesten, docs/TESTING.md 2e).
def tippen(selector, nr=0):
    kasten = js("""(() => {
      const n = document.querySelectorAll(%s)[%d];
      if (!n) return null;
      const r = n.getBoundingClientRect();
      return {x: r.left + r.width / 2, y: r.top + r.height / 2};
    })()""" % (json.dumps(selector), nr))
    if not kasten:
        raise SystemExit("Nicht gefunden: %s [%d]" % (selector, nr))
    cdp.PORT_ALT = cdp.PORT
    for typ in ("mousePressed", "mouseReleased"):
        _senden("Input.dispatchMouseEvent", {
            "type": typ, "x": kasten["x"], "y": kasten["y"],
            "button": "left", "clickCount": 1,
        })
        time.sleep(0.05)


def _senden(methode, params):
    alt_port, alt_seite = cdp.PORT, cdp.app_seite
    cdp.PORT = PORT
    cdp.app_seite = app_seite
    try:
        return cdp.befehl_senden(methode, params)
    finally:
        cdp.PORT, cdp.app_seite = alt_port, alt_seite


def warten(bedingung_js, sekunden=15, takt=0.3):
    ende = time.time() + sekunden
    while time.time() < ende:
        if js("!!(%s)" % bedingung_js):
            return True
        time.sleep(takt)
    return False


def mitschrift_an():
    js("""(() => {
      if (window.__pmLog) return true;
      window.__pmLog = [];
      window.addEventListener("error", e => window.__pmLog.push("error: " + e.message));
      window.addEventListener("unhandledrejection", e => window.__pmLog.push("reject: " + e.reason));
      const alt = console.error;
      console.error = function () { window.__pmLog.push("console: " + [].join.call(arguments, " ")); alt.apply(console, arguments); };
      // Jeder Toast mit Zeitstempel - "nichts passiert" heisst genau das: kein Toast.
      window.__pmToasts = [];
      const beob = new MutationObserver(() => {
        const t = document.getElementById("toast");
        if (t && t.classList.contains("show")) {
          const txt = t.textContent.trim();
          const letzte = window.__pmToasts[window.__pmToasts.length - 1];
          if (!letzte || letzte.text !== txt) window.__pmToasts.push({text: txt, t: Math.round(performance.now())});
        }
      });
      const t = document.getElementById("toast");
      if (t) beob.observe(t, {attributes: true, childList: true, subtree: true, characterData: true});
      return true;
    })()""")


def profil_setzen():
    u"""Das zehnstufige Onboarding ueberspringen, indem der Zustand direkt gesetzt wird.

    Durchklicken waere der laengere Weg zum selben Ausgangspunkt - und er misst nichts,
    was dieser Lauf messen will. Das "__test"-Suffix haengt localKey() auf localhost an
    jeden Schluessel (docs/TESTING.md, Cloud-Falle).
    """
    js("""(() => {
      localStorage.setItem("wochenkueche_profile_v1__test", JSON.stringify({name: "Pruefer", email: ""}));
      localStorage.setItem("wochenkueche_lastprofile_v1__test", JSON.stringify({name: "Pruefer", email: ""}));
      const roh = localStorage.getItem("wochenkueche_v1__test");
      const s = roh ? JSON.parse(roh) : {recipes: [], plans: {}};
      s.goal = {kcal: 2200, carbs: 230, protein: 160, fat: 70};
      s.onboarded = true;
      localStorage.setItem("wochenkueche_v1__test", JSON.stringify(s));
      return true;
    })()""")
    js("location.reload()")
    time.sleep(3)


def text_tippen(text, tag="button"):
    u"""Das erste sichtbare Element mit passendem Textanfang antippen."""
    treffer = js("""(() => {
      const n = [].find.call(document.querySelectorAll(%s),
        e => e.textContent.trim().startsWith(%s) && e.getBoundingClientRect().width > 0);
      if (!n) return null;
      const r = n.getBoundingClientRect();
      return {x: r.left + r.width / 2, y: r.top + r.height / 2};
    })()""" % (json.dumps(tag), json.dumps(text)))
    if not treffer:
        raise SystemExit("Kein %s mit Text %r sichtbar" % (tag, text))
    for typ in ("mousePressed", "mouseReleased"):
        _senden("Input.dispatchMouseEvent", {"type": typ, "x": treffer["x"], "y": treffer["y"],
                                             "button": "left", "clickCount": 1})
        time.sleep(0.06)


def scan_fahren(mobil=True):
    u"""Einmal den ganzen Weg: Meals -> Neues Meal -> Zutat -> Scannen. Liefert die Zeile."""
    if mobil:
        _senden("Emulation.setDeviceMetricsOverride",
                {"width": 390, "height": 844, "deviceScaleFactor": 3, "mobile": True})
        js("location.reload()")
        time.sleep(3)
    mitschrift_an()
    tippen('[data-tab="recipes"]')
    time.sleep(1)
    text_tippen("Neues Meal")
    time.sleep(1.2)
    tippen("#ms-ing-add")
    time.sleep(0.8)
    tippen(".ing-row .ing-barcode")
    # Kamera starten, ZXing laden, erkennen, Open Food Facts fragen - alles echt.
    time.sleep(7)
    return js("""({
      name: (document.querySelector(".ing-name") || {}).value,
      kcal: (document.querySelector(".ing-kcal") || {}).value,
      msg: (() => { const p = document.querySelector(".ing-msg"); return p && !p.hidden ? p.textContent : ""; })(),
      zeilen: document.querySelectorAll(".ing-row").length,
      toasts: (window.__pmToasts || []).map(t => t.text),
      log: window.__pmLog || []
    })""")


def lauf(ean, was):
    chrome_stoppen()
    time.sleep(2)
    chrome_starten(ean)
    time.sleep(2)
    profil_setzen()
    e = scan_fahren()
    print("")
    print("--- %s (EAN %s) ---" % (was, ean))
    print("  Zeile lebt        : %s" % ("ja" if e["zeilen"] else "NEIN"))
    print("  Name              : %r" % (e["name"] or ""))
    print("  kcal              : %r" % (e["kcal"] or ""))
    print("  Meldung der Zeile : %r" % (e["msg"] or ""))
    print("  Toasts            : %s" % " | ".join(e["toasts"]))
    if e["log"]:
        print("  FEHLER            : %s" % " || ".join(e["log"]))
    return e


def main():
    zeigen = "--zeigen" in sys.argv
    try:
        seiten()
    except Exception:
        pass
    fehler = []
    try:
        # 1) Ein Code, den Open Food Facts kennt: Name und Naehrwerte muessen ankommen.
        a = lauf(EAN, "bekannter Code")
        if not a["zeilen"]:
            fehler.append("Die Zutatenzeile hat den Sucher nicht ueberlebt.")
        if not a["name"]:
            fehler.append("Kein Produktname in der Zeile - der Treffer kam nicht an.")
        if not a["kcal"]:
            fehler.append("Keine Naehrwerte in der Zeile.")
        if a["log"]:
            fehler.append("JavaScript-Fehler: %s" % " || ".join(a["log"]))

        # 2) Ein gueltiger Code, den Open Food Facts NICHT kennt (HTTP 404). Bis zum
        #    14.09.2026 meldete die App hier "Suche nicht moeglich (offline?)".
        b = lauf(UNBEKANNT, "unbekannter Code")
        if not b["zeilen"]:
            fehler.append("Unbekannter Code: die Zeile ist verschwunden.")
        if "Kein Treffer" not in (b["msg"] or ""):
            fehler.append("Unbekannter Code: die Zeile sagt nicht, dass es keinen Treffer gab "
                          "(Meldung: %r)" % (b["msg"] or ""))
        if "offline" in " ".join(b["toasts"]).lower():
            fehler.append("Unbekannter Code wird immer noch als Verbindungsproblem gemeldet.")
    finally:
        if zeigen:
            print("\nBrowser bleibt offen (--zeigen). Danach beenden mit:")
            print("  python tools/abnahme-scan-kamera.py --stoppen")
        else:
            # Ein offener Debug-Port ist eine offene Fernbedienung - er darf einen
            # abgebrochenen Lauf nicht ueberleben (docs/TESTING.md, Abschnitt zur Abnahme).
            chrome_stoppen()

    print("")
    if fehler:
        print("ROT - %d Befund(e):" % len(fehler))
        for f in fehler:
            print("  * %s" % f)
        return 1
    print("GRUEN - beide Wege antworten sichtbar.")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if "--stoppen" in sys.argv:
        chrome_stoppen()
        print("Chrome auf Port %d beendet." % PORT)
        sys.exit(0)
    sys.exit(main())
