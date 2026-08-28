# -*- coding: utf-8 -*-
u"""
Kontowechsel auf demselben Geraet: den fremden Cache leeren, aber nur einmal.

docs/TROUBLESHOOTING.md 134: Der Firestore-Zwischenspeicher liegt pro URSPRUNG, nicht pro
Konto. Meldet sich auf demselben Geraet ein anderes Konto an, trifft es auf den Cache des
vorigen - und genau dort war der Zustand messbar, in dem JEDER Zugriff `permission-denied`
liefert, dauerhaft und ohne Erholung.

`kontoWechselAufraeumen(uid)` leert den Cache und laedt neu. Die Messgroesse ist NICHT
"wird gewischt", sondern:

    nach dem Neuladen wird NICHT ERNEUT gewischt

Denn die Reihenfolge entscheidet: merken, wischen, neu laden. Stuende das Merken hinter dem
Wischen, entstuende eine Neulade-Schleife - der teuerste denkbare Fehler an dieser Stelle,
weil die App danach ueberhaupt nicht mehr startet.

Dazu die drei Faelle, in denen NICHTS passieren darf: Erstanmeldung (kein fremder Cache),
dasselbe Konto (kein Wechsel), und ein Modul ohne wipeCache (aelterer Stand aus dem
Service-Worker-Cache).

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-kontowechsel.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile, shutil

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(zeilen, start, ende, anhang=u""):
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    if a is None:
        raise SystemExit(u"Marker nicht gefunden: " + start)
    b = next((i for i, l in enumerate(zeilen) if i > a and ende in l), None)
    if b is None:
        raise SystemExit(u"Endmarker nicht gefunden: " + ende)
    return u"\n".join(zeilen[a:b + 1]) + anhang


UMFELD = u"""
var protokoll = [], neugeladen = 0, gewischt = 0, gestartet = [], appOffen = 0;
var wipeScheitert = false;
function noteError(k){ protokoll.push(k); }
function localKey(k){ return k; }
function enterApp(){ appOffen++; }
function startCloudSync(uid){ gestartet.push(uid); }
// location ist im Browser global schreibgeschuetzt - der ganze Pruefstand laeuft deshalb in
// einem Funktionsbereich (siehe main()), in dem `let location` den Namen sauber verdeckt.
let location = { reload: function(){ neugeladen++; } };
window.CloudSync = {
  wipeCache: function(){ gewischt++; return wipeScheitert ? Promise.reject({code:"failed-precondition"}) : Promise.resolve(); }
};
function zuruecksetzen(){
  protokoll=[]; neugeladen=0; gewischt=0; gestartet=[]; appOffen=0; wipeScheitert=false;
  try { localStorage.removeItem("wochenkueche_lastuid_v1"); } catch(e){}
}
function gemerkteUid(){ return localStorage.getItem("wochenkueche_lastuid_v1"); }
function warten(){ return new Promise(function(r){ setTimeout(r, 30); }); }
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}

(async function () {

console.log("--- 1. Erstanmeldung ist KEIN Wechsel ---");
zuruecksetzen();
var r = kontoWechselAufraeumen("alice");
pr("meldet 'kein Neuladen'", r === false);
pr("nichts gewischt", gewischt === 0);
pr("die UID ist trotzdem gemerkt", gemerkteUid() === "alice", String(gemerkteUid()));

console.log("--- 2. Dasselbe Konto noch einmal: nichts passiert ---");
r = kontoWechselAufraeumen("alice");
pr("kein Neuladen", r === false);
pr("nichts gewischt", gewischt === 0, gewischt + "");

console.log("--- 3. Anderes Konto: wischen und neu laden ---");
r = kontoWechselAufraeumen("bob");
pr("meldet 'Neuladen laeuft'", r === true);
pr("einmal gewischt", gewischt === 1, gewischt + "");
await warten();
pr("neu geladen", neugeladen === 1, neugeladen + "");
pr("die App wurde NICHT nebenbei gestartet", appOffen === 0 && gestartet.length === 0,
   "sonst liefe der Sync gegen den Cache, der gerade verschwindet");

console.log("--- 4. DIE MESSGROESSE: nach dem Neuladen wird nicht erneut gewischt ---");
// Das Neuladen bildet der Pruefstand nach, indem er dieselbe UID noch einmal anmeldet -
// genau das tut die Seite nach location.reload().
gewischt = 0; neugeladen = 0;
r = kontoWechselAufraeumen("bob");
pr("kein zweites Wischen", gewischt === 0, gewischt + "");
pr("kein zweites Neuladen", neugeladen === 0, neugeladen + "");
pr("die App startet jetzt normal", r === false);

console.log("--- 5. Hin und her: jeder Wechsel wischt genau einmal ---");
zuruecksetzen();
kontoWechselAufraeumen("alice");            // Erstanmeldung
kontoWechselAufraeumen("bob");   await warten();   // Wechsel 1
kontoWechselAufraeumen("bob");                     // Neuladen
kontoWechselAufraeumen("alice"); await warten();   // Wechsel 2
kontoWechselAufraeumen("alice");                   // Neuladen
pr("zwei Wechsel, zwei Wischvorgaenge", gewischt === 2, gewischt + "");
pr("zwei Neuladevorgaenge", neugeladen === 2, neugeladen + "");

console.log("--- 6. Scheitert das Wischen, haelt es die Anmeldung nicht auf ---");
// Haeufigster Grund: ein zweiter offener Tab. Die App muss trotzdem starten.
zuruecksetzen();
kontoWechselAufraeumen("alice");
wipeScheitert = true;
r = kontoWechselAufraeumen("bob");
await warten();
pr("kein Neuladen", neugeladen === 0, neugeladen + "");
pr("aber die App startet", appOffen === 1 && gestartet[0] === "bob",
   "appOffen=" + appOffen + " gestartet=" + JSON.stringify(gestartet));
pr("und der Fehler ist protokolliert", protokoll.indexOf("cloud:wipeOnSwitch") !== -1,
   JSON.stringify(protokoll));
pr("die neue UID bleibt gemerkt", gemerkteUid() === "bob",
   "sonst wischte der naechste Start erneut - und wieder vergeblich");

console.log("--- 7. Ohne wipeCache im Modul passiert nichts ---");
zuruecksetzen();
kontoWechselAufraeumen("alice");
var merk = window.CloudSync;
window.CloudSync = {};
r = kontoWechselAufraeumen("bob");
window.CloudSync = merk;
pr("kein Neuladen", r === false);
pr("die UID ist trotzdem gemerkt", gemerkteUid() === "bob",
   "sonst wischte ein spaeteres Update rueckwirkend fuer einen laengst erledigten Wechsel");

console.log("--- 8. GEGENPROBE: die falsche Reihenfolge erzeugt eine Endlosschleife ---");
// merken NACH dem wischen - genau der Fehler, den die Reihenfolge im Code vermeidet.
function kontoWechselFalschHerum(uid){
  var vorige = localStorage.getItem("wochenkueche_lastuid_v1");
  if (!vorige || vorige === uid) { localStorage.setItem("wochenkueche_lastuid_v1", uid); return false; }
  gewischt++; neugeladen++;
  localStorage.setItem("wochenkueche_lastuid_v1", uid);   // zu spaet: der Reload war schon
  return true;
}
zuruecksetzen();
kontoWechselFalschHerum("alice");
// Der Reload passiert VOR dem Merken - die Seite kommt also mit der ALTEN gemerkten UID zurueck.
localStorage.setItem("wochenkueche_lastuid_v1", "alice");
var runden = 0;
for (var i = 0; i < 5; i++) {
  if (!kontoWechselFalschHerum("bob")) break;
  runden++;
  localStorage.setItem("wochenkueche_lastuid_v1", "alice");   // der Reload verwirft das Merken
}
pr("falsche Reihenfolge laedt immer wieder neu", runden === 5, runden + " Runden");
pr("die richtige Fassung tut das nicht", (function(){
  zuruecksetzen();
  kontoWechselAufraeumen("alice");
  kontoWechselAufraeumen("bob");
  return kontoWechselAufraeumen("bob") === false;
})());

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
})();
"""


def main():
    quelle = io.open(INDEX, encoding="utf-8").read().split(u"\n")
    kern = schneide(quelle, u"const LETZTE_UID_KEY = localKey(",
                    u"    return true;", u"\n  }")
    tmp = tempfile.mkdtemp(prefix="mp-kontowechsel-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n(function () {\n" + UMFELD + u"\n" + kern +
            u"\n" + TEST + u"\n})();\n</script>")
        p = subprocess.run(
            [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=6000",
             "--user-data-dir=" + os.path.join(tmp, "profil"),
             "--enable-logging=stderr", "--v=0", "file:///" + seite.replace("\\", "/")],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        aus = (p.stdout or "") + (p.stderr or "")
        zeilen = []
        for z in aus.split("\n"):
            m = re.search(r'CONSOLE:\d+\] "(.*)", source', z)
            if m:
                zeilen.append(m.group(1))
        if not zeilen:
            print(u"Keine Konsolenausgabe - lief das Script? Rohausgabe:")
            print(aus[:2000])
            return 2
        for z in zeilen:
            print(z)
        letzte = [z for z in zeilen if z.startswith("ERGEBNIS")]
        return 0 if letzte and letzte[-1].endswith("0 rot") else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
