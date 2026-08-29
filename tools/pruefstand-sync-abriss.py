# -*- coding: utf-8 -*-
u"""
Ein abgerissener Listener darf nicht als „Synchronisiert" weiterlaufen.

BEFUND vom 28.08.2026, am echten Konto gemessen: Der Sync-Punkt zeigte
„Cloud-Sync: Synchronisiert", waehrend die App weder lesen noch schreiben konnte.

Die Ursache: Vier onSnapshot-Aufrufe trugen ein leeres `function () {}` als
Fehlerbehandlung. Ein onSnapshot, der mit einem Fehler endet, wird von Firestore
ENDGUELTIG beendet - er versucht es nicht erneut. Der Listener war also tot, und
setSyncStatus("synced") vom Ende des startCloudSync() stand fuer immer.

Gemessen wird deshalb NICHT „kommt ein Fehler an", sondern:

    nach einem Listener-Abriss zeigt der Status NICHT mehr "synced",
    und der Nutzer bekommt GENAU EINEN Hinweis - nicht einen je Listener

Die zweite Haelfte ist keine Kosmetik: Greift eine Firestore-Regel, scheitern alle
Listener gleichzeitig. Vier Toasts hintereinander waeren die Folge.

Gegenprobe: die alte Fassung (leeres `function () {}`) muss ROT werden - dort bleibt der
Status auf "synced".

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-sync-abriss.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile, shutil

# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

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
// --- Umfeld der App-Seite -----------------------------------------------------------
var syncStatus = "off", uiRufe = [], toasts = [], watchAbgerissen = false;
function updateSyncUI(){ uiRufe.push(syncStatus); }
function toast(t){ toasts.push(t); }
var protokoll = [];
window.noteError = function(tag){ protokoll.push(tag); };

// --- Attrappe fuer onSnapshot: liefert ein Ergebnis ODER einen Fehler ----------------
var fehlerModus = false;
function onSnapshot(ref, weiter, fehler){
  if (fehlerModus) { setTimeout(function(){ fehler({ code: "permission-denied" }); }, 0); }
  return function(){};   // unsubscribe
}
function doc(){ return {}; }
function collection(){ return {}; }
function groupDoc(){ return {}; }
function recipesCol(){ return {}; }
var db = {};

function zuruecksetzen(){ syncStatus="off"; uiRufe=[]; toasts=[]; watchAbgerissen=false; protokoll=[]; fehlerModus=false; }

// --- Die ALTE Fassung, fuer die Gegenprobe ------------------------------------------
function watchKontoAlt(uid, cb){
  return onSnapshot(doc(), function(){}, function () {});
}
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}
function warte(){ return new Promise(function(r){ setTimeout(r, 5); }); }

(async function () {

console.log("--- 1. Der Melder protokolliert UND reicht durch ---");
zuruecksetzen(); fehlerModus = true;
setSyncStatus("synced");
watchFehler("sync:watchKonto")({ code: "permission-denied" });
pr("noteError bekam die Kennung", protokoll.indexOf("sync:watchKonto") !== -1, JSON.stringify(protokoll));
pr("Status ist nicht mehr synced", syncStatus === "offline", syncStatus);
pr("genau ein Hinweis", toasts.length === 1, toasts.length + "");

console.log("--- 2. Vier Listener reissen gleichzeitig ab - EIN Hinweis ---");
// Der Regelfall: eine Firestore-Regel greift, alle Listener scheitern im selben Moment.
zuruecksetzen();
setSyncStatus("synced");
["sync:watchKonto","sync:watchRezepte","sync:watchGruppe","sync:watchPlaene"]
  .forEach(function(k){ watchFehler(k)({ code: "permission-denied" }); });
pr("alle vier protokolliert", protokoll.length === 4, JSON.stringify(protokoll));
pr("aber nur EIN Hinweis", toasts.length === 1, toasts.length + " Hinweise");
pr("Status offline", syncStatus === "offline", syncStatus);

console.log("--- 3. Der Hinweis ist kurz, konkret und verspricht nichts ---");
pr("kein Fehlercode im Text", toasts[0].indexOf("permission") === -1, toasts[0]);
pr("sagt, was zu tun ist", /neu/i.test(toasts[0]), toasts[0]);
// Der Toast steht 1,9 Sekunden. Die erste Fassung hatte 21 Woerter und war damit nicht
// lesbar; ausserdem wiederholte sie den Sync-Punkt daneben. Die Grenze ist bewusst hart.
pr("hoechstens 10 Woerter", toasts[0].split(/\\s+/).length <= 10,
   toasts[0].split(/\\s+/).length + " Woerter: " + toasts[0]);
pr("wiederholt den Sync-Punkt nicht", !/lokal gespeichert|diesem Gerät/.test(toasts[0]),
   toasts[0]);
// Keine Zusage, dass ein Neuladen die Synchronisierung wiederherstellt - bei einer
// dauerhaften Regel-Ablehnung tritt derselbe Fehler danach erneut auf.
pr("verspricht keinen Erfolg", !/um weiter zu synchronisieren|stellt.*wieder her/.test(toasts[0]),
   toasts[0]);

console.log("--- 4. Nach stopCloudSync() meldet die naechste Sitzung wieder ---");
zuruecksetzen();
setSyncStatus("synced");
watchFehler("sync:watchKonto")({ code: "unavailable" });
pr("Sitzung 1: ein Hinweis", toasts.length === 1);
watchAbgerissen = false;          // genau das tut stopCloudSync()
setSyncStatus("synced");
watchFehler("sync:watchKonto")({ code: "unavailable" });
pr("Sitzung 2: wieder ein Hinweis", toasts.length === 2, toasts.length + "");

console.log("--- 5. Der Melder wirft nie, auch wenn die App-Seite wirft ---");
zuruecksetzen();
var alteFassung = window.__onCloudWatchError;
window.__onCloudWatchError = function(){ throw new Error("kaputt"); };
var geworfen = false;
try { watchFehler("sync:watchKonto")({ code: "x" }); } catch (e) { geworfen = true; }
window.__onCloudWatchError = alteFassung;
pr("wirft nicht weiter", !geworfen);
pr("und meldet den Melder-Fehler selbst", protokoll.indexOf("sync:watchMelder") !== -1,
   JSON.stringify(protokoll));

console.log("--- 6. Fehlt die App-Seite ganz, protokolliert er trotzdem ---");
zuruecksetzen();
var merk = window.__onCloudWatchError;
delete window.__onCloudWatchError;
geworfen = false;
try { watchFehler("sync:watchGruppe")({ code: "x" }); } catch (e) { geworfen = true; }
window.__onCloudWatchError = merk;
pr("wirft nicht", !geworfen);
pr("protokolliert trotzdem", protokoll.indexOf("sync:watchGruppe") !== -1);

console.log("--- 7. Ein gesunder Listener aendert nichts ---");
zuruecksetzen(); fehlerModus = false;
setSyncStatus("synced");
window.CloudSyncWatch = onSnapshot(doc(), function(){}, watchFehler("sync:watchKonto"));
await warte();
pr("Status bleibt synced", syncStatus === "synced", syncStatus);
pr("kein Hinweis", toasts.length === 0);
pr("kein Protokolleintrag", protokoll.length === 0);

console.log("--- 8. GEGENPROBE: die alte Fassung bleibt auf 'synced' ---");
zuruecksetzen(); fehlerModus = true;
setSyncStatus("synced");
watchKontoAlt("u1", function(){});
await warte();
pr("alte Fassung: Status bleibt synced", syncStatus === "synced", syncStatus);
pr("alte Fassung: kein Hinweis", toasts.length === 0, toasts.length + "");
pr("alte Fassung: kein Protokolleintrag", protokoll.length === 0, JSON.stringify(protokoll));

console.log("--- 9. Gegenprobe zur Gegenprobe: die Attrappe feuert wirklich ---");
// Sonst misst Abschnitt 8 nur, dass gar kein Fehler ankam.
zuruecksetzen(); fehlerModus = true;
var kam = false;
onSnapshot(doc(), function(){}, function(){ kam = true; });
await warte();
pr("die Attrappe liefert den Fehler", kam);

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
})();
"""


def main():
    quelle = pm_quelle.lade_seite(INDEX).split(u"\n")

    melder = schneide(quelle, u"function watchFehler(kennung)",
                      u'catch (e2) { window.noteError("sync:watchMelder", e2); }',
                      u"\n          }\n        };\n      }")
    setzer = schneide(quelle, u"function setSyncStatus(s)", u"updateSyncUI();", u"\n  }")
    handler = schneide(quelle, u"window.__onCloudWatchError = function (kennung, e)",
                       u'toast("Cloud-Verbindung unterbrochen', u"\n  };")

    tmp = tempfile.mkdtemp(prefix="mp-abriss-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + UMFELD + u"\n" + setzer + u"\n" + melder + u"\n" + handler +
            u"\n" + TEST + u"\n</script>")
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
