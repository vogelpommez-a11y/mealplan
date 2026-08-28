# -*- coding: utf-8 -*-
u"""
"Cloud-Verbindung zuruecksetzen": der Ausweg aus dem vergifteten Offline-Cache.

Hintergrund in docs/TROUBLESHOOTING.md 134: Die Firestore-Instanz kann in einen Zustand
geraten, in dem JEDER Zugriff `permission-denied` liefert - bei gueltiger Anmeldung und
intakten Regeln. Ein Neuladen heilt ihn nicht, ein Token-Neubezug nicht, disableNetwork/
enableNetwork nicht. `CloudSync.wipeCache()` heilt ihn sofort - die Funktion gab es laengst,
sie hing nur hinter "Konto loeschen".

Gemessen wird deshalb nicht "wird gewischt", sondern die drei Eigenschaften, an denen so ein
Knopf scheitert:

  1. Er ist da, wenn er gebraucht wird - und nur dann (kein Cloud-Konto: keine Zeile).
  2. Er fragt VORHER. wipeCache() verwirft ungeschriebene Aenderungen.
  3. Scheitert das Wischen, wird NICHT neu geladen - sonst sieht der Nutzer denselben
     kaputten Zustand wieder und haelt den Knopf fuer wirkungslos.

Punkt 3 ist der eigentliche Grund fuer diesen Pruefstand: Der haeufigste Fehlschlag ist kein
Fehler, sondern ein zweiter offener Tab - clearIndexedDbPersistence() verlangt, dass sonst
keine Instanz laeuft.

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-cache-reset.py [pfad-zu-index.html]
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
var authMode = "cloud";
var toasts = [], protokoll = [], neugeladen = 0, gewischt = 0;
var wipeScheitert = false;
function toast(t){ toasts.push(t); }
function noteError(k){ protokoll.push(k); }
// location.reload() laesst sich im Pruefstand nicht ausloesen - der Aufruf wird gezaehlt.
// location.reload() darf hier NICHT wirklich laufen. `location` ist im Browser global
// schreibgeschuetzt - ein `var location` auf oberster Ebene greift nicht, der echte
// reload() lief daraufhin in eine Endlosschleife und der Pruefstand hing bis zur
// Zeitgrenze. Deshalb steht alles in einem Funktionsbereich (siehe main()), in dem
// `let location` den globalen Namen sauber verdeckt.
let location = { reload: function(){ neugeladen++; } };
window.CloudSync = {
  wipeCache: function () {
    gewischt++;
    return wipeScheitert ? Promise.reject({ code: "failed-precondition" }) : Promise.resolve();
  }
};
// confirmModal-Attrappe: merkt sich die Rueckfrage, statt sie zu zeigen.
var gefragt = null;
function confirmModal(o){ gefragt = o; }
async function bestaetigen(){ if (!gefragt) throw new Error("es wurde gar nicht gefragt"); await gefragt.onConfirm(); }
function zuruecksetzen(){ toasts=[]; protokoll=[]; neugeladen=0; gewischt=0; gefragt=null; wipeScheitert=false; authMode="cloud"; }
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}

(async function () {

console.log("--- 1. Die Zeile erscheint nur, wo sie etwas nuetzt ---");
zuruecksetzen();
pr("mit Cloud-Konto: ja", cloudResetVerfuegbar() === true);
authMode = "local";
pr("im lokalen Modus: nein", cloudResetVerfuegbar() === false,
   "ohne Cloud gibt es keinen Cache, den man zuruecksetzen koennte");
authMode = "cloud";
var merk = window.CloudSync;
window.CloudSync = {};
pr("ohne wipeCache im Modul: nein", cloudResetVerfuegbar() === false,
   "aelterer Stand aus dem Service-Worker-Cache");
window.CloudSync = undefined;
pr("ohne CloudSync ueberhaupt: nein (kein Absturz)", cloudResetVerfuegbar() === false);
window.CloudSync = merk;

console.log("--- 2. Es wird VORHER gefragt ---");
zuruecksetzen();
resetCloudCache();
pr("eine Rueckfrage steht", !!gefragt);
pr("und es wurde noch NICHTS gewischt", gewischt === 0, gewischt + "");
pr("und nicht neu geladen", neugeladen === 0);
pr("der Knopf heisst nicht 'Loeschen'", gefragt.okLabel === "Zurücksetzen", gefragt.okLabel);

console.log("--- 3. Der Text sagt, was bleibt UND was verloren geht ---");
// Beides gehoert hin: "deine Meals bleiben" allein waere beruhigend und unvollstaendig.
pr("nennt, dass die Daten bleiben", /bleiben/.test(gefragt.bodyHtml), gefragt.bodyHtml);
pr("nennt den Verlust ungeschriebener Aenderungen", /verloren/.test(gefragt.bodyHtml));
pr("kuendigt das Neuladen an", /neu geladen/.test(gefragt.bodyHtml));

console.log("--- 4. Bestaetigt: wischen, dann neu laden ---");
zuruecksetzen();
resetCloudCache();
await bestaetigen();
pr("genau einmal gewischt", gewischt === 1, gewischt + "");
pr("danach neu geladen", neugeladen === 1, neugeladen + "");
pr("kein Toast davor", toasts.length === 0,
   "er waere im selben Atemzug wieder weg - siehe Kommentar im Code");

console.log("--- 5. Scheitert das Wischen, wird NICHT neu geladen ---");
// Der haeufigste Fall ist kein Fehler, sondern ein zweiter offener Tab.
zuruecksetzen();
wipeScheitert = true;
resetCloudCache();
await bestaetigen();
pr("kein Neuladen", neugeladen === 0, neugeladen + "");
pr("dafuer ein Hinweis", toasts.length === 1, JSON.stringify(toasts));
pr("der Hinweis nennt die Ursache", /Tab/.test(toasts[0] || ""), toasts[0]);
pr("und der Fehler ist protokolliert", protokoll.indexOf("cloud:wipeCache") !== -1,
   JSON.stringify(protokoll));

console.log("--- 6. Abgebrochen heisst abgebrochen ---");
zuruecksetzen();
resetCloudCache();
// onConfirm wird schlicht nicht gerufen
pr("nichts gewischt", gewischt === 0);
pr("nichts neu geladen", neugeladen === 0);
pr("kein Hinweis", toasts.length === 0);

console.log("--- 7. GEGENPROBE: die Attrappe kann ueberhaupt scheitern ---");
// Sonst bestuende Abschnitt 5 auch dann, wenn wipeCache() immer durchlaeuft.
zuruecksetzen();
wipeScheitert = true;
var geworfen = false;
try { await window.CloudSync.wipeCache(); } catch (e) { geworfen = true; }
pr("wipeCache lehnt im Fehlermodus wirklich ab", geworfen);
zuruecksetzen();
var geworfen2 = false;
try { await window.CloudSync.wipeCache(); } catch (e) { geworfen2 = true; }
pr("und laeuft sonst durch", !geworfen2);

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
})();
"""


def main():
    quelle = io.open(INDEX, encoding="utf-8").read().split(u"\n")
    verf = schneide(quelle, u"function cloudResetVerfuegbar()",
                    u'return authMode === "cloud" && !!(window.CloudSync && window.CloudSync.wipeCache);',
                    u"\n  }")
    reset = schneide(quelle, u"function resetCloudCache()",
                     u'schließ die anderen Tabs',
                     u"\n        }\n      }\n    });\n  }")

    tmp = tempfile.mkdtemp(prefix="mp-cachereset-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n(function () {\n" + UMFELD + u"\n" + verf +
            u"\n" + reset + u"\n" + TEST + u"\n})();\n</script>")
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
