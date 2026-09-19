# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: Konto loeschen hinterlaesst keinen Rest vom Zweitgeraet (19.09.2026).

Der Befund (docs/TROUBLESHOOTING.md §172): Ein zweites angemeldetes Geraet behaelt sein Token
bis zu einer Stunde nach deleteUser(). In dieser Zeit konnte es Meals und das Kontodokument neu
anlegen - Reste ohne Konto, die niemand mehr loeschen kann. Dazu kam die Falle aus §170/§171:
Geloescht wurde die LISTE des Aufrufers (lokaler Stand), nicht die Sammlung in der Cloud.

Der Fix: erst sperren (loeschsperren/{uid} mit Ablaufdatum), dann vom SERVER listen, dann
loeschen. Die Sperre setzen die Firestore-Regeln durch (nichtImLoeschen() in firestore.rules).
Die Attrappe unten bildet GENAU diese Regel nach: Anlegen und Aendern unter users/{uid},
shared/ und invites/ wird abgelehnt, solange eine gueltige Sperre steht. Das ist der einzige
nachgebaute Teil - deleteAccount() und kontoDatenLoeschen() sind echter, ausgeschnittener Code.

Was hier NICHT geprueft werden kann: die Regeln selbst (kein Emulator, CLAUDE.md Ziffer 12).
Hier steht nur, dass sie im Repo an den sechs Stellen stehen. Ob sie wirken, zeigt erst ein
Versuch am echten Konto, nachdem sie in der Konsole veroeffentlicht sind.

Gegenprobe: deleteAccount() aus dem letzten Commit vor dem Fix (git) muss die Reste liegen lassen.
"""
import io, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
REGELN = os.path.join(BASIS, "firestore.rules")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-konto-loeschsperre.html")
# Der Stand vor dem Fix. Fest verdrahtet, damit die Gegenprobe nicht mitwandert.
ALT_COMMIT = "5b11b8c"


def schnitt(lines, sig, tiefe):
    """Ab der Signaturzeile bis zur schliessenden Klammer auf `tiefe` Spaces."""
    zu = " " * tiefe + "}"
    for i, z in enumerate(lines):
        if z.startswith(sig):
            for j in range(i + 1, len(lines)):
                if lines[j] == zu:
                    return "\n".join(lines[i:j + 1])
            raise SystemExit("KEIN ENDE: " + sig)
    raise SystemExit("NICHT GEFUNDEN: " + sig)


lines = pm_quelle.lade_seite(QUELLE).split("\n")
LOESCHEN = schnitt(lines, "        deleteAccount: async function (opts) {", 8)
DATEN = schnitt(lines, "      async function kontoDatenLoeschen(", 6)

# Sicherung gegen einen stillen Fehlschnitt.
SPERRE = 'const sperre = doc(db, "loeschsperren", uid);'
if SPERRE not in LOESCHEN:
    raise SystemExit("deleteAccount() sperrt nicht - Schnitt oder Code pruefen")
if LOESCHEN.index(SPERRE) > LOESCHEN.index("kontoDatenLoeschen(uid, opts)"):
    raise SystemExit("die Sperre steht NACH dem Aufraeumen - genau der Fehler")
if "getDocsFromServer(collection(db, \"users\", uid, \"recipes\"))" not in DATEN:
    raise SystemExit("kontoDatenLoeschen() listet die Meals nicht vom Server")

alt_text = subprocess.check_output(["git", "show", ALT_COMMIT + ":index.html"], cwd=BASIS).decode("utf-8")
LOESCHEN_ALT = schnitt(alt_text.split("\n"), "        deleteAccount: async function (opts) {", 8)
if "loeschsperren" in LOESCHEN_ALT:
    raise SystemExit("die Gegenprobe enthaelt schon die Sperre - ALT_COMMIT pruefen")

# Die Regeln: nur Textpruefung, siehe Kopf.
regeln = io.open(REGELN, encoding="utf-8").read()
regel_befund = []
if "function nichtImLoeschen(uid)" not in regeln or "match /loeschsperren/{uid}" not in regeln:
    regel_befund.append("nichtImLoeschen() oder loeschsperren fehlt in firestore.rules")
for block, soll in (("match /users/{uid} {", "nichtImLoeschen(uid)"),
                    ("match /users/{uid}/recipes/{recipeId}", "nichtImLoeschen(uid)"),
                    ("match /shared/{id}", "nichtImLoeschen(request.auth.uid)"),
                    ("match /groups/{gid} {", "nichtImLoeschen(request.auth.uid)"),
                    ("match /groups/{gid}/members/{uid}", "nichtImLoeschen(uid)"),
                    ("match /invites/{code}", "nichtImLoeschen(request.auth.uid)")):
    i = regeln.find(block)
    ende = regeln.find("\n    match ", i + 1)
    teil = regeln[i:ende if ende != -1 else len(regeln)]
    if i == -1 or soll not in teil:
        regel_befund.append("keine Sperre in " + block)
# Loeschen muss unter der Sperre erlaubt bleiben - sonst sperrte sich die Loeschung selbst aus.
for block in ("match /users/{uid} {", "match /users/{uid}/recipes/{recipeId}"):
    i = regeln.find(block)
    if "allow read, delete: if request.auth != null && request.auth.uid == uid;" not in regeln[i:i + 300]:
        regel_befund.append("Loeschen nicht frei in " + block)

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Loeschsperre</title>
<pre id="log"></pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) { document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")"; };
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
  var el = document.getElementById("log");
  if (el) el.textContent = LOG.join("\\n");
}
var REGEL_BEFUND = __REGEL_BEFUND__;

// ---- Der Server: Pfad -> Daten ----
var server, fehler, notizen, geloeschtUser;
var nutzer = { uid: "ich", providerData: [{ providerId: "google.com" }] };
function frisch() {
  server = {
    "users/ich": { shares: ["s1", "s2"], inviteCodes: [] },
    "users/ich/recipes/r1": {},
    "users/ich/recipes/r2": {},          // vom Zweitgeraet, lokal noch unbekannt
    "shared/s1": { uid: "ich" },
    "shared/s2": { uid: "ich" }          // ebenso
  };
  fehler = {}; notizen = []; geloeschtUser = false;
}
// Nachbau der Regel nichtImLoeschen(): Anlegen/Aendern unter users/ich, shared/, invites/ wird
// abgelehnt, solange eine GUELTIGE Sperre steht. Loeschen bleibt frei. Mehr ist nicht nachgebaut.
function gesperrt() {
  var s = server["loeschsperren/ich"];
  return !!(s && s.bis > new Date());
}
function geschuetzt(p) { return p.indexOf("users/ich") === 0 || p.indexOf("shared/") === 0 || p.indexOf("invites/") === 0; }
function verweigert() { return Promise.reject({ code: "permission-denied" }); }
// Das Zweitgeraet: schreibt mit noch gueltigem Token ein neues Meal, das Kontodokument und einen Link.
function zweitgeraetSchreibt() {
  ["users/ich/recipes/r9", "users/ich", "shared/s9"].forEach(function (p) {
    if (geschuetzt(p) && gesperrt()) return;
    server[p] = p === "shared/s9" ? { uid: "ich" } : { neu: true };
  });
}

// ---- Firebase-Attrappen (nur Transport) ----
var db = {};
function doc() { return Array.prototype.slice.call(arguments, 1).join("/"); }
function collection() { return Array.prototype.slice.call(arguments, 1).join("/"); }
function setDoc(p, data) {
  if (p.indexOf("loeschsperren/") === 0) {
    if (fehler.sperre) return Promise.reject(fehler.sperre);
    server[p] = data; return Promise.resolve();
  }
  if (geschuetzt(p) && gesperrt()) return verweigert();
  server[p] = data; return Promise.resolve();
}
function deleteDoc(p) { delete server[p]; return Promise.resolve(); }
function getDoc(p) { return Promise.resolve({ exists: function () { return p in server; }, data: function () { return server[p]; } }); }
function getDocFromServer(p) {
  if (fehler.server) return Promise.reject(fehler.server);
  return getDoc(p);
}
function getDocsFromServer(c) {
  if (fehler.server) return Promise.reject(fehler.server);
  var docs = Object.keys(server).filter(function (p) {
    return p.indexOf(c + "/") === 0 && p.slice(c.length + 1).indexOf("/") === -1;
  }).map(function (p) { return { id: p.slice(c.length + 1) }; });
  return Promise.resolve({ docs: docs });
}
function writeBatch() { return { delete: function () {}, update: function () {}, commit: function () { return Promise.resolve(); } }; }
function increment(n) { return n; }
function GoogleAuthProvider() {}
function OAuthProvider() {}
var EmailAuthProvider = { credential: function () { return {}; } };
function reauthenticateWithPopup() { return Promise.resolve(); }
function reauthenticateWithCredential() { return Promise.resolve(); }
function deleteUser(u) {
  geloeschtUser = true;
  // Das Token des Zweitgeraets lebt weiter - genau jetzt schreibt es.
  zweitgeraetSchreibt();
  return Promise.resolve();
}
var auth = { currentUser: nutzer };
window.noteError = function (k) { notizen.push(k); };

__DATEN__
var NEU = { __LOESCHEN__ };
var ALT = { __LOESCHEN_ALT__ };

// Der Aufrufer kennt nur, was LOKAL bekannt ist: r1 und s1.
var AUFRUF = { shareIds: ["s1"], recipeIds: ["r1"], groupId: "", inviteCodes: [] };
function reste() {
  return Object.keys(server).filter(function (p) { return p.indexOf("loeschsperren/") !== 0; }).sort();
}
function lauf(fn) { return fn(AUFRUF).then(function () { return "durch"; }, function (e) { return "abgebrochen:" + (e && e.code); }); }

(function () {
  pruef("die Regeln sperren users, recipes, shared, groups, members, invites (nur Text)", REGEL_BEFUND, []);

  // ================= 1. Der Fix =================
  frisch();
  lauf(NEU.deleteAccount).then(function (erg) {
    pruef("die Loeschung laeuft durch", erg, "durch");
    pruef("der Zugang ist geloescht", geloeschtUser, true);
    pruef("NICHTS bleibt zurueck - auch nicht, was nur die Cloud kannte oder das Zweitgeraet danach schrieb", reste(), []);
    var s = server["loeschsperren/ich"];
    pruef("die Sperre bleibt stehen und traegt nur ein Ablaufdatum", s ? Object.keys(s) : null, ["bis"]);
    var h = s ? (s.bis - new Date()) / 36e5 : 0;
    pruef("sie laeuft in rund zwei Stunden ab (die Regel erlaubt hoechstens drei)", h > 1.9 && h <= 2, true);

    // ================= 2. Gegenprobe =================
    frisch();
    return lauf(ALT.deleteAccount);
  }).then(function (erg) {
    pruef("GEGENPROBE: die alte Fassung laeuft ebenfalls durch", erg, "durch");
    pruef("GEGENPROBE: und laesst Cloud-Meal, Link und die Schreibvorgaenge des Zweitgeraets liegen",
      reste(), ["shared/s2", "shared/s9", "users/ich", "users/ich/recipes/r2", "users/ich/recipes/r9"]);

    // ================= 3. Regeln noch nicht veroeffentlicht =================
    frisch();
    fehler.sperre = { code: "permission-denied" };
    return lauf(NEU.deleteAccount);
  }).then(function (erg) {
    pruef("lehnen die Regeln die Sperre ab, wird trotzdem geloescht (Art. 17)", erg, "durch");
    pruef("und es wird notiert", notizen, ["konto:loeschsperre"]);
    pruef("vom Server gelistet ist trotzdem alles weg, was vor deleteUser bestand",
      reste(), ["shared/s9", "users/ich", "users/ich/recipes/r9"]);

    // ================= 4. Die Sperre scheitert am Netz =================
    frisch();
    fehler.sperre = { code: "unavailable" };
    return lauf(NEU.deleteAccount);
  }).then(function (erg) {
    pruef("scheitert die Sperre am Netz, bricht die Loeschung ab", erg, "abgebrochen:unavailable");
    pruef("und nichts ist geloescht", reste().length, 5);
    pruef("der Zugang besteht weiter", geloeschtUser, false);

    // ================= 5. Das Aufraeumen scheitert NACH der Sperre =================
    frisch();
    fehler.server = { code: "unavailable" };
    return lauf(NEU.deleteAccount);
  }).then(function (erg) {
    pruef("scheitert das Listen, bricht die Loeschung ab", erg, "abgebrochen:unavailable");
    pruef("die Sperre wird zurueckgenommen - das Konto laeuft nicht zwei Stunden ins Leere",
      "loeschsperren/ich" in server, false);
    pruef("der Zugang besteht weiter", geloeschtUser, false);

    LOG.push("");
    LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
    document.getElementById("log").textContent = LOG.join("\\n");
  });
})();
</script>
"""

seite = (seite.replace("__REGEL_BEFUND__", json.dumps(regel_befund))
              .replace("__LOESCHEN_ALT__", LOESCHEN_ALT)
              .replace("__LOESCHEN__", LOESCHEN)
              .replace("__DATEN__", DATEN))
io.open(ZIEL, "w", encoding="utf-8").write(seite)
print("geschrieben: " + ZIEL)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(ZIEL))
