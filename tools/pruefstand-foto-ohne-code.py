# -*- coding: utf-8 -*-
u"""
Foto ohne Barcode: "Kein Barcode erkannt" statt "Erkennung nicht moeglich (offline?)".

Gemessen wird, was `detectBarcode()` (lib/barcode.js) fuer drei Fotos zurueckgibt - denn
daran entscheiden beide Aufrufer (`scanBarcodeCode()` und die Zutatenzeile in index.html)
zwischen "kein Code" (null) und "Fehler" (throw):

  leer      einfarbiges Bild           -> null       (bis 24.10.2026: ZXing warf, "offline?")
  ean       EAN-13 4006381333931       -> der Code   (Lesen funktioniert weiter)
  kaputt    Datei ist kein Bild        -> sofort throw "BildUnlesbar"
                                          (bis 24.10.2026: ZXing antwortete NIE, "Lese Barcode ..." blieb stehen)

ECHTER Code, kein Nachbau: lib/barcode.js und vendor/zxing.min.js werden unveraendert
geladen. Abgeschaltet ist nur `BarcodeDetector` - so laeuft jeder Fall durch den
ZXing-Zweig, um den es geht (Edge unter Windows hat ohnehin keinen).

Gegenprobe - ohne sie zaehlt kein Ergebnis:
  python tools/pruefstand-foto-ohne-code.py --gegenprobe   # lib/barcode.js von davor: "leer" und "kaputt" rot

ECHTZEIT, nicht pruefstand_lauf.fahren(): Dessen --virtual-time-budget laesst die Uhr davonlaufen,
waehrend Bilder im Hintergrund dekodiert werden - img.decode() und createImageBitmap() "dauerten"
dort bis zu 20 s, im Android-WebView 22 ms. Der Lauf meldete die Korrektur faelschlich rot und
zaehlte Faelle, die nie fertig wurden, gar nicht mit ("1 gruen, 0 rot" bei einem von drei).
Deshalb ein eigener Edge mit DevTools-Port (9353, kein anderer Pruefstand nutzt ihn), und
gruen heisst: genau 4 OK, 0 FEHL. Jeder Fall hat eine Frist (25 s, laenger als die 20-s-Frist
in detectBarcode) - wer nie antwortet, wird als "haengt" rot, statt still aus dem Protokoll zu
fallen. Gefunden wird nur DIE Seite dieses Laufs (genaue URL), nie ein liegengebliebener Edge.

Vierte Pruefung (Python, Vertrag): Der Fehlername "BildUnlesbar" steht in lib/barcode.js als
Wurf UND in index.html (scanBarcodeCode) als Weiche. Ein Tippfehler auf einer Seite brachte
still den "offline?"-Text zurueck. Den angezeigten Text selbst prueft nur die Vorfuehrung.

Aufruf:  python tools/pruefstand-foto-ohne-code.py [--gegenprobe [<commit>]]
Hintergrund: docs/TROUBLESHOOTING.md 196.
"""
import io, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Letzter Stand VOR der Korrektur (lib/barcode.js und index.html unveraendert seit Monaten).
# Bewusst fest: Die Gegenprobe soll gegen genau diesen Fehlerstand laufen, nicht gegen HEAD~.
ALT_STANDARD = "ff7dae3"

SEITE = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Foto ohne Code</title>
<pre id="log"></pre>
<script>window.BarcodeDetector = undefined;</script>
<script src="%(zxing)s"></script>
<script src="%(barcode)s"></script>
<script>
(async function () {
  var log = document.getElementById("log"), rot = [];
  function pruef(ok, text) { log.textContent += (ok ? "OK   " : "FEHL ") + text + "\\n"; if (!ok) rot.push(text); }
  function bild(zeichnen) {
    var c = document.createElement("canvas"); c.width = 760; c.height = 300;
    var x = c.getContext("2d"); x.fillStyle = "#fff"; x.fillRect(0, 0, c.width, c.height);
    zeichnen(x);
    return new Promise(function (ok) { c.toBlob(function (b) { ok(new File([b], "foto.png", { type: "image/png" })); }, "image/png"); });
  }
  function ean13(x, code) {
    var L = ["0001101","0011001","0010011","0111101","0100011","0110001","0101111","0111011","0110111","0001011"];
    var inv = function (s) { return s.replace(/./g, function (b) { return b === "1" ? "0" : "1"; }); };
    var G = L.map(function (s) { return inv(s).split("").reverse().join(""); }), R = L.map(inv);
    var P = ["LLLLLL","LLGLGG","LLGGLG","LLGGGL","LGLLGG","LGGLLG","LGGGLL","LGLGLG","LGLGGL","LGGLGL"][+code[0]];
    var bits = "101", i;
    for (i = 1; i < 7; i++) bits += (P[i - 1] === "L" ? L : G)[+code[i]];
    bits += "01010";
    for (i = 7; i < 13; i++) bits += R[+code[i]];
    bits += "101";
    x.fillStyle = "#000";
    for (i = 0; i < bits.length; i++) if (bits[i] === "1") x.fillRect(40 + i * 6, 40, 6, 220);
  }
  async function lauf(name, file) {
    // Frist statt endlosem Warten: ein Fall, der nie antwortet, ist ein Befund ("haengt")
    // und darf nicht still aus dem Protokoll fallen.
    var frist = new Promise(function (ok) { setTimeout(function () { ok({ haengt: true }); }, 25000); });
    return Promise.race([frist, PM.barcode.detectBarcode(file).then(
      function (w) { return { wert: w }; }, function (e) { return { fehler: e }; })]);
  }
  try {
    var leer = await lauf("leer", await bild(function (x) { x.fillStyle = "#8c8"; x.fillRect(0, 0, 760, 300); }));
    pruef(!leer.fehler && leer.wert === null,
      "leer: Foto ohne Barcode liefert null (\\"Kein Barcode erkannt\\") - " +
      (leer.haengt ? "haengt" : leer.fehler ? "warf: " + leer.fehler.message : "Wert " + JSON.stringify(leer.wert)));

    var ean = await lauf("ean", await bild(function (x) { ean13(x, "4006381333931"); }));
    pruef(!ean.fehler && ean.wert === "4006381333931",
      "ean: EAN-13 wird weiter gelesen - " + (ean.haengt ? "haengt" : ean.fehler ? "warf: " + ean.fehler.message : JSON.stringify(ean.wert)));

    var kaputt = await lauf("kaputt", new File(["kein Bild"], "foto.png", { type: "image/png" }));
    pruef(!!kaputt.fehler && kaputt.fehler.name === "BildUnlesbar",
      "kaputt: eine Datei, die kein Bild ist, meldet sofort BildUnlesbar - " +
      (kaputt.haengt ? "haengt (keine Antwort in 25 s)" : kaputt.fehler ? "warf " + kaputt.fehler.name : "lieferte " + JSON.stringify(kaputt.wert)));
  } catch (e) { pruef(false, "Absturz: " + (e && e.message)); }
  log.textContent += rot.length ? "FEHLGESCHLAGEN: " + rot.length + "\\n" : "ALLE 3 PRUEFUNGEN GRUEN\\n";
})();
</script>
"""


PORT = 9353
EDGE_PFADE = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def url(pfad):
    return "file:///" + pfad.replace("\\", "/")


def protokoll(seite, tmp, sekunden=90):
    u"""Seite headless in ECHTZEIT fahren und #log lesen, bis die Schlusszeile steht."""
    try:
        import websocket
    except ImportError:
        print(u"Paket websocket-client fehlt (pip install websocket-client) - Lauf unklar, nicht rot.")
        return None
    exe = next((p for p in EDGE_PFADE if os.path.isfile(p)), None)
    if not exe:
        print(u"Edge nicht gefunden.")
        return None
    proc = subprocess.Popen([exe, "--headless=new", "--disable-gpu",
                             "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
                             "--user-data-dir=" + os.path.join(tmp, "profil"), url(seite)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws = None
    try:
        ziel = None
        for _ in range(50):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT, timeout=5) as r:
                    ziel = next((s for s in json.loads(r.read().decode("utf-8"))
                                 if s.get("type") == "page" and s.get("url") == url(seite)), None)
                if ziel:
                    break
            except Exception:
                pass
            time.sleep(.4)
        if not ziel:
            print(u"Edge kam nicht hoch (Port %d)." % PORT)
            return None
        ws = websocket.create_connection(ziel["webSocketDebuggerUrl"], timeout=25,
                                         origin="http://127.0.0.1:%d" % PORT, suppress_origin=False)
        ende, text, nr = time.time() + sekunden, "", 0
        while time.time() < ende:
            nr += 1
            ws.send(json.dumps({"id": nr, "method": "Runtime.evaluate", "params": {
                "expression": "document.getElementById('log').textContent", "returnByValue": True}}))
            m = json.loads(ws.recv())
            while m.get("id") != nr:
                m = json.loads(ws.recv())
            text = m.get("result", {}).get("result", {}).get("value") or ""
            if re.search(r"PRUEFUNGEN GRUEN|FEHLGESCHLAGEN", text):
                return text
            time.sleep(.3)
        print(u"Zeitgrenze: das Protokoll wurde nicht fertig.")
        print(text)
        return None
    finally:
        try:
            if ws:
                ws.close()
        except Exception:
            pass
        # Ganzer Prozessbaum: proc.kill() traf nur den Startprozess, Edge-Kinder hielten sonst
        # den Port und der naechste Lauf (z. B. --gegenprobe) laese deren altes Protokoll.
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    tmp = tempfile.mkdtemp(prefix="foto-ohne-code-")
    try:
        barcode = os.path.join(BASIS, "lib", "barcode.js")
        index = io.open(os.path.join(BASIS, "index.html"), encoding="utf-8").read()
        if "--gegenprobe" in sys.argv:
            i = sys.argv.index("--gegenprobe")
            ref = sys.argv[i + 1] if len(sys.argv) > i + 1 else ALT_STANDARD
            alt = subprocess.check_output(["git", "show", ref + ":lib/barcode.js"], cwd=BASIS)
            barcode = os.path.join(tmp, "barcode-alt.js")
            io.open(barcode, "wb").write(alt)
            index = subprocess.check_output(["git", "show", ref + ":index.html"], cwd=BASIS).decode("utf-8")
            print(u"GEGENPROBE gegen lib/barcode.js und index.html aus " + ref + u" - leer, kaputt, Vertrag rot.")
        seite = os.path.join(tmp, "pruefstand-foto-ohne-code.html")
        io.open(seite, "w", encoding="utf-8").write(SEITE % {
            "zxing": url(os.path.join(BASIS, "vendor", "zxing.min.js")),
            "barcode": url(barcode)})
        text = protokoll(seite, tmp)
        if text is None:
            return 2
        zeilen = [z for z in text.splitlines() if z.strip()]
        lib = io.open(barcode, encoding="utf-8").read()
        vertrag = 'name = "BildUnlesbar"' in lib and 'e.name === "BildUnlesbar"' in index
        zeilen.append(("OK   " if vertrag else "FEHL ") +
                      'vertrag: "BildUnlesbar" in lib/barcode.js geworfen und in index.html abgefragt')
        for z in zeilen:
            print(z)
        gruen = sum(1 for z in zeilen if z.startswith("OK "))
        rot = sum(1 for z in zeilen if z.startswith("FEHL "))
        print("ERGEBNIS %d gruen, %d rot" % (gruen, rot))
        return 0 if rot == 0 and gruen == 4 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
