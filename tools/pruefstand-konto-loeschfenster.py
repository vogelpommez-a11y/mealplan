# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: "Konto loeschen" - Fenster, Marken-Lader und Schreibsperre
(TROUBLESHOOTING 201).

Stufe 1 (25.10.2026): Das Fenster liess sich waehrend "Wird gelöscht …" schliessen, das Ergebnis
ging verloren oder traf ein fremdes Fenster. Fix: Ergebnis haengt an offen().

Stufe 2, Gesamtloesung (26.10.2026): Das Fenster bleibt nur bis zur bestaetigten Neuanmeldung
offen ("Wird bestätigt …"). Dann meldet CloudAuth.deleteAccount() sich ueber opts.bestaetigt:
Fenster zu, Marken-Lader "Dein Konto wird gelöscht …" sperrt die App, der Abgleich schreibt
nichts mehr (kontoLoeschen = "loescht"), die Bruecke lehnt jedes Schreiben ab (kontoLoescht).
Scheitert es, wird beides aufgehoben und nachgeholt. Ein zweiter Start zeigt einen Toast.
Schlussmeldungen treffen kein fremdes Fenster mehr (fensterZuNachLoeschen).

Echter Code:
  * App: der Zurueck-/Modal-Block, scheduleCloudPush() samt kontoLoeschen, der Marken-Lader
    (Frist ML_ECHT_MAX_MS gestaucht auf 800 ms), deleteAccountFlow(), fensterZuNachLoeschen(),
    fotosGebliebenMelden(), el()/esc() aus lib/basis.js.
  * Bruecke: CloudAuth.deleteAccount() mit kontoLoeschenNachBestaetigung() und die
    Sperr-Schleife ueber CloudSync/CloudShare/CloudGroup - in einer eigenen Funktion mit
    eigenem `window`, die Firebase-Aufrufe (setDoc, deleteUser ...) als Stubs.
Gestubbt: CloudAuth der App-Seite (ein Versprechen, das der Pruefstand von aussen in zwei
Schritten aufloest: Neuanmeldung, dann Loeschen), wipeLocalData & Co. als Zaehler.

Gegenprobe: dieselben Funktionen aus GEGEN_COMMIT (vor der Gesamtloesung) muessen durchfallen.
"""
import io, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-konto-loeschfenster.html")
# Der Stand vor der Gesamtloesung. Fest verdrahtet, damit die Gegenprobe nicht mitwandert.
GEGEN_COMMIT = "d316ca9"


def funktion(lines, sig, ende="  }"):
    """Ab der Signaturzeile bis zur ersten Zeile, die nur `ende` ist."""
    for i, z in enumerate(lines):
        if z.startswith(sig):
            for j in range(i + 1, len(lines)):
                if lines[j] == ende:
                    return "\n".join(lines[i:j + 1])
            raise SystemExit("KEIN ENDE: " + sig)
    raise SystemExit("NICHT GEFUNDEN: " + sig)


def zeile(lines, anfang):
    treffer = [z for z in lines if z.startswith(anfang)]
    if len(treffer) != 1:
        raise SystemExit("Zeile nicht eindeutig: " + anfang)
    return treffer[0]


def bruecke(lines):
    """deleteAccount bis vor kontoDatenLoeschen, dazu die Sperr-Schleife (fehlt im alten Stand)."""
    a = next((i for i, z in enumerate(lines) if z.startswith("        deleteAccount: async function (opts) {")), None)
    b = next((i for i, z in enumerate(lines) if a is not None and i > a and "// Loescht alles, was zum Konto gehoert" in z), None)
    if a is None or b is None:
        raise SystemExit("Schnitt deleteAccount nicht gefunden")
    teil = "      Object.assign(window.CloudAuth, {\n" + "\n".join(lines[a:b])
    s = next((i for i, z in enumerate(lines) if z.startswith("      [window.CloudSync, window.CloudShare, window.CloudGroup].forEach(")), None)
    if s is not None:
        e = next(i for i in range(s + 1, len(lines)) if lines[i] == "      });")
        teil += "\n" + "\n".join(lines[s:e + 1])
    return teil


lines = pm_quelle.lade_seite(QUELLE).split("\n")

# ---- Schnitt 1: Zurueck-Block bis Ende openModal (wie pruefstand-zurueck-taste.py) ----
start = next((i for i, z in enumerate(lines) if "// ---------- Zurueck-Taste (D5) ----------" in z), None)
oeffnen = next((i for i, z in enumerate(lines) if start is not None and i > start and z.startswith("  function openModal(")), None)
ende = next((i for i, z in enumerate(lines) if oeffnen is not None and i > oeffnen and z == "  }"), None)
if start is None or ende is None:
    raise SystemExit("Schnitt Zurueck/Modal nicht gefunden")
KERN = "\n".join(lines[start:ende + 1])
HILFEN = [z for z in lines if z.startswith("  function el(html)") or z.startswith("  function esc(s)")]
if len(HILFEN) != 2:
    raise SystemExit("el()/esc() nicht gefunden - liegen sie noch in lib/basis.js?")

# ---- Schnitt 2: Abgleich-Sperre und Marken-Lader ----
PUSH = zeile(lines, "  let kontoLoeschen = null;") + "\n" + funktion(lines, "  function scheduleCloudPush() {")
ML = "\n".join([zeile(lines, "  const ML_SCHRITT_MS"), zeile(lines, "  const ML_ECHT_ZEIGEN_MS"), zeile(lines, "  const ML_LOGO")])
if "ML_ECHT_MAX_MS = 12000" not in ML:
    raise SystemExit("ML_ECHT_MAX_MS hat sich geaendert - Stauchung im Pruefstand anpassen")
ML = ML.replace("ML_ECHT_MAX_MS = 12000", "ML_ECHT_MAX_MS = 800")
ML += "\n" + funktion(lines, "  function markenKarteHtml(") + "\n" + funktion(lines, "  function markenLader(o) {")

# ---- Schnitt 3: die Loesch-Funktionen, neu und alt ----
NEU = "\n".join([funktion(lines, "  function deleteAccountFlow() {"), funktion(lines, "  function fensterZuNachLoeschen() {"),
                 funktion(lines, "  function fotosGebliebenMelden(titel) {")])
for muss in ("const offen = () => document.contains(node);", "bestaetigt", "markenLader("):
    if muss not in NEU:
        raise SystemExit("deleteAccountFlow() ohne '" + muss + "' - Schnitt oder Code pruefen")
BR_NEU = bruecke(lines)
if "kontoLoescht" not in BR_NEU:
    raise SystemExit("Bruecke ohne kontoLoescht - Schnitt pruefen")

alt_lines = subprocess.check_output(["git", "show", GEGEN_COMMIT + ":index.html"], cwd=BASIS).decode("utf-8").split("\n")
ALT = funktion(alt_lines, "  function deleteAccountFlow() {") + "\n" + funktion(alt_lines, "  function fotosGebliebenMelden(titel) {")
ALT = ALT.replace("function deleteAccountFlow(", "function deleteAccountFlowALT(").replace(
    "function fotosGebliebenMelden(", "function fotosGebliebenMeldenALT(")
BR_ALT = bruecke(alt_lines)

# ---- Schnitt 4: syncRecipes() - ein Push, der beim Bestaetigen schon lief (Code-Review 26.10.) ----
SYNC_NEU = funktion(lines, "  async function syncRecipes() {")
if '"konto-loescht"' not in SYNC_NEU:
    raise SystemExit("syncRecipes() kennt die Schreibsperre nicht - Schnitt oder Code pruefen")
SYNC_ALT = funktion(alt_lines, "  async function syncRecipes() {").replace(
    "async function syncRecipes(", "async function syncRecipesALT(")

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Konto-Loeschfenster</title>
<div id="modal-root"></div>
<pre id="log">laeuft…</pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.addEventListener("unhandledrejection", function (e) {
  var el = document.getElementById("log");
  el.textContent = (el.textContent || "") + "\\nJS-FEHLER (async): " + (e.reason && (e.reason.stack || e.reason.message) || e.reason);
});
window.onerror = function (m, s, z) {
  var el = document.getElementById("log");
  el.textContent = (el.textContent || "") + "\\nJS-FEHLER: " + m + " (Zeile " + z + ")";
};
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
  document.getElementById("log").textContent = LOG.join("\\n");
}
function warte(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

// ---- Randstuecke fuer Modal-Block und Marken-Lader ----
var hoveredCardId = null, liveScanStop = null, groupModalRepaint = null, gemeldet = [];
var appEl = document.createElement("div"), onb = null, renderZahl = 0;
document.body.appendChild(appEl);
function render() { renderZahl++; }
function noteError(k, e) { gemeldet.push(k); }
var MOTION = { base: "200" };
var datenGeloescht = false;

// ---- Randstuecke fuer den Abgleich ----
var syncUid = "u1", pushTimer = null, pushes = 0;
function pushNow() { pushes++; }

// ---- Randstuecke fuer deleteAccountFlow ----
var state = { tab: "home", shares: [], recipes: [], inviteCodes: [] };
var syncGid = "", groupMembers = [];
function groupRole() { return null; }
function confirmModal() { throw new Error("confirmModal unerwartet"); }
function openGroupModal() {}
var gestoppt = 0, gewischt = 0, neuladen = [], toasts = [], fotosBleiben = false, wischFehler = false;
function stopCloudSync() { gestoppt++; }
function wipeLocalData() { gewischt++; return wischFehler ? Promise.reject(new Error("idb")) : Promise.resolve(fotosBleiben); }
function nachLoeschenNeuladen(t) { neuladen.push(t); }
function toast(t, ms) { toasts.push([t, ms || 0]); }
function cloudErrMsg(e) { return "Fehler: " + e.message; }
var FOTOS_GEBLIEBEN = "Fotos blieben.";
// Zwei Schritte von aussen: anmelden() = Neuanmeldung bestaetigt (ruft opts.bestaetigt, wenn es
// das gibt), dann ja()/nein() = Ergebnis des Loeschens. nein() ohne anmelden() = Neuanmeldung
// gescheitert (falsches Passwort).
var lauf = null;
window.CloudAuth = {
  current: function () { return { uid: "u1", providerData: [{ providerId: "password" }] }; },
  deleteAccount: function (opts) {
    return new Promise(function (ja, nein) {
      lauf = { ja: ja, nein: nein, anmelden: function () { if (opts.bestaetigt) opts.bestaetigt(); } };
    });
  },
  logout: function () {}
};

__HILFEN__
__KERN__
__PUSH__
__ML__
__NEU__
__ALT__

// ---- syncRecipes(): Randstuecke ----
var lastPushedRecipes = null, recipesSyncFailed = false, CLOUD_DOC_MAX = 1e6;
function canonJSON(v) { return JSON.stringify(v); }
function recipeBase() { return ["users", "u1"]; }
__SYNC_NEU__
__SYNC_ALT__

// ---- Die Bruecke, abgeschottet: eigenes window, Firebase als Stubs ----
function brueckeBauen(quelltext) {
  return new Function("aufruf", [
    "var window = { CloudAuth: {}, noteError: function () {},",
    "  CloudSync: { save: function () { aufruf.push('save'); return Promise.resolve(); },",
    "               loadRecipes: function () { aufruf.push('loadRecipes'); return Promise.resolve([]); },",
    "               wipeCache: function () { return Promise.resolve(); } },",
    "  CloudShare: { publish: function () { aufruf.push('publish'); return Promise.resolve(); } },",
    "  CloudGroup: { watch: function () { aufruf.push('watch'); return function () {}; },",
    "                putMember: function () { aufruf.push('putMember'); return Promise.resolve(); } } };",
    "var auth = { currentUser: { uid: 'u1', email: 'a@b.c', providerData: [{ providerId: 'password' }] } };",
    "var db = {}, NATIV = false, RESOLVER = null;",
    "function doc() { return {}; }",
    "function reauthenticateWithCredential() { aufruf.push('reauth'); return Promise.resolve(); }",
    "var EmailAuthProvider = { credential: function () { return {}; } };",
    "function setDoc() { aufruf.push('sperre'); return Promise.resolve(); }",
    "function deleteDoc() { aufruf.push('entsperren'); return Promise.resolve(); }",
    "var datenLoesen = null, userFehler = null;",
    "function kontoDatenLoeschen() { return new Promise(function (ja, nein) { datenLoesen = { ja: ja, nein: nein }; }); }",
    "function deleteUser() { return userFehler ? Promise.reject(userFehler) : Promise.resolve(); }",
    quelltext,
    "return { w: window, daten: function () { return datenLoesen; }, userFehler: function (e) { userFehler = e; } };"
  ].join("\\n"));
}
var BR_NEU = brueckeBauen(__BR_NEU__);
var BR_ALT = brueckeBauen(__BR_ALT__);
function versuch(p) { return p.then(function () { return "ok"; }, function (e) { return e.code || e.message; }); }

function offenZahl() { return modalRoot.childElementCount; }
function q(s) { return modalRoot.querySelector(s); }
function lader() { return document.querySelector(".ml-overlay"); }
function escape() { document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })); }
function starten(flow) {
  flow();
  q("#del-pw").value = "geheim";
  q("[data-confirm]").click();
}
// Ein fremdes Fenster mit eigenem Hook - so wie das Meal-Blatt (attemptClose).
var fremdHook = 0;
function fremdesFenster() {
  openModal(el('<div class="modal" role="dialog" aria-label="Fremd"><h2>Fremd</h2></div>'));
  modalCloseHook = function () { fremdHook++; modalCloseHook = null; return false; };
}
function aufraeumen() { modalCloseHook = null; closeModal(); }
function zuruecksetzen() { toasts = []; neuladen = []; gemeldet = []; fremdHook = 0; fotosBleiben = false; wischFehler = false; }

(async function () {
  history.pushState({ polster: 1 }, "");
  await warte(30);

  // ---- 1. Vor dem Loeschen: Abbrechen schliesst wie immer ----
  deleteAccountFlow();
  q(".modal-foot [data-close]").click();
  await warte(120);
  pruef("vor dem Loeschen: Abbrechen schliesst", offenZahl(), 0);

  // ---- 2. Neuanmeldung laeuft: Fenster offen, "Wird bestätigt …" ----
  starten(deleteAccountFlow);
  await warte(20);
  pruef("Knopf zeigt die Neuanmeldung", q("[data-confirm]").textContent, "Wird bestätigt …");
  pruef("Abbrechen aus, X bleibt bedienbar",
        [q(".modal-foot [data-close]").disabled, q(".modal-head [data-close]").disabled], [true, false]);
  pruef("Fokus faellt nicht auf <body>, sondern auf die Ueberschrift",
        document.activeElement && document.activeElement.tagName, "H2");
  pruef("noch kein Lader, Abgleich schreibt noch", [!!lader(), kontoLoeschen], [false, "bestaetigen"]);

  // ---- 3. Falsches Passwort bei offenem Fenster: Meldung im Fenster, Knoepfe frei ----
  lauf.nein(new Error("falsches Passwort"));
  await warte(30);
  pruef("Fehler im offenen Fenster: Meldung dort, kein Toast, kein Lader",
        [offenZahl(), q("#del-err").textContent, toasts.length, !!lader()], [1, "Fehler: falsches Passwort", 0, false]);
  pruef("Knoepfe wieder frei, Sperre aus", [q("[data-confirm]").disabled, q(".modal-foot [data-close]").disabled, kontoLoeschen], [false, false, null]);
  escape();
  await warte(120);

  // ---- 4. Doppelstart: Fenster waehrend der Neuanmeldung zu, Menue erneut ----
  starten(deleteAccountFlow);
  await warte(20);
  escape();
  await warte(120);
  deleteAccountFlow();
  pruef("zweiter Start: kein neues Fenster, ein Toast", [offenZahl(), toasts.map(function (t) { return t[0]; })], [0, ["Dein Konto wird gerade gelöscht …"]]);
  toasts = [];
  lauf.nein(new Error("Netz weg"));
  await warte(30);
  pruef("spaeter Fehler bei geschlossenem Fenster: langer Toast", toasts, [["Konto nicht gelöscht: Fehler: Netz weg", 6000]]);
  zuruecksetzen();

  // ---- 5. Neuanmeldung bestaetigt: Fenster zu, Lader, Sperre ----
  starten(deleteAccountFlow);
  await warte(20);
  lauf.anmelden();
  await warte(250);
  pruef("nach der Bestaetigung: Fenster zu, Lader steht, App gesperrt",
        [offenZahl(), !!lader(), appEl.inert, lader() && lader().textContent.trim()], [0, true, true, "Dein Konto wird gelöscht …"]);
  pruef("Abgleich-Sperre an", kontoLoeschen, "loescht");
  clearTimeout(pushTimer); pushTimer = null;   // von den Fehlschlaegen oben noch eingeplant
  scheduleCloudPush();
  pruef("scheduleCloudPush() plant waehrenddessen nichts", pushTimer, null);

  // ---- 6. ... dann Fehler: Sperre aus, nachholen, langer Toast, Lader weg ----
  lauf.nein(new Error("Netz weg"));
  await warte(700);
  pruef("Fehler nach der Bestaetigung: Lader weg, App frei", [!!lader(), appEl.inert], [false, false]);
  pruef("Sperre aus und Abgleich nachgeholt", [kontoLoeschen, pushTimer !== null], [null, true]);
  pruef("Meldung als langer Toast", toasts, [["Konto nicht gelöscht: Fehler: Netz weg", 6000]]);
  clearTimeout(pushTimer); pushTimer = null;
  zuruecksetzen();

  // ---- 7. Erfolg: gewischt, Neuladen angekuendigt, Lader geht ----
  starten(deleteAccountFlow);
  await warte(20);
  lauf.anmelden();
  await warte(250);
  var vorher = gewischt;
  lauf.ja();
  await warte(700);
  pruef("Erfolg: lokal geloescht, Neuladen angekuendigt, Lader weg",
        [gewischt - vorher, neuladen.length, !!lader()], [1, 1, false]);
  pruef("kein Fehler gemeldet", gemeldet, []);
  kontoLoeschen = null; zuruecksetzen();

  // ---- 8. Frist: Lader geht nach ML_ECHT_MAX_MS, App wieder bedienbar, Sperre bleibt ----
  starten(deleteAccountFlow);
  await warte(20);
  lauf.anmelden();
  await warte(250);
  // Zwischenpruefung auch, weil der Laeufer nach 1,5 s ohne neue Zeile "fertig" annimmt.
  pruef("Lader steht vor der Frist", !!lader(), true);
  await warte(1050);
  pruef("nach der Frist: Lader weg, Toast sagt es, Sperre bleibt",
        [!!lader(), appEl.inert, toasts.length > 0 && /Hintergrund/.test(toasts[0][0]), kontoLoeschen], [false, false, true, "loescht"]);
  // ... inzwischen ist ein fremdes Fenster offen; dann Erfolg mit gebliebenen Fotos
  fremdesFenster();
  fotosBleiben = true;
  lauf.ja();
  await warte(200);
  pruef("Fotos geblieben: fremdes Fenster sauber zu (Hook nicht gefragt, Zurueck-Eintrag weg), Fotohinweis offen",
        [fremdHook, offenZahl(), q(".modal h2") && q(".modal h2").textContent, overlayStack.length], [0, 1, "Konto gelöscht", 0]);
  pruef("Fotohinweis fokussiert Verstanden", document.activeElement && document.activeElement.textContent, "Verstanden");
  aufraeumen(); datenGeloescht = false; kontoLoeschen = null; zuruecksetzen();
  await warte(120);

  // ---- 9. Nur der Zugang blieb (dataAlreadyDeleted), fremdes Fenster offen ----
  starten(deleteAccountFlow);
  await warte(20);
  lauf.anmelden();
  await warte(250);
  // Zwischenpruefung auch, weil der Laeufer nach 1,5 s ohne neue Zeile "fertig" annimmt.
  pruef("Lader steht vor der Frist", !!lader(), true);
  await warte(1050);
  fremdesFenster();
  var zugang = new Error("requires-recent-login"); zugang.dataAlreadyDeleted = true;
  lauf.nein(zugang);
  await warte(200);
  pruef("dataAlreadyDeleted: fremdes Fenster zu, Neuladen mit Zugangs-Hinweis, Sperre bleibt",
        [offenZahl(), fremdHook, neuladen.length, /Zugang/.test(neuladen[0] || ""), kontoLoeschen], [0, 0, 1, true, "loescht"]);
  kontoLoeschen = null; zuruecksetzen();

  // ---- 10. Bruecke: Schreibsperre ab der Neuanmeldung ----
  var aufruf = [], br = BR_NEU(aufruf), bestaetigt = [];
  var p = br.w.CloudAuth.deleteAccount({ password: "x", bestaetigt: function () { bestaetigt.push(aufruf.slice()); } });
  p.catch(function () {});
  await warte(20);
  pruef("Bruecke: bestaetigt nach der Neuanmeldung, vor der Sperre", bestaetigt, [["reauth"]]);
  pruef("Bruecke: waehrend des Loeschens kein Schreiben",
        [await versuch(br.w.CloudSync.save("u1", { a: 1 })), await versuch(br.w.CloudShare.publish("s", {})),
         await versuch(br.w.CloudGroup.putMember("g", "u1", {}))], ["konto-loescht", "konto-loescht", "konto-loescht"]);
  pruef("Bruecke: Lesen und Zuhoeren gehen weiter",
        [await versuch(br.w.CloudSync.loadRecipes(["users", "u1"])), typeof br.w.CloudGroup.watch("g", function () {})], ["ok", "function"]);
  br.daten().nein(new Error("offline"));
  pruef("Bruecke: Loeschen gescheitert -> Fehler kommt an", await versuch(p), "offline");
  pruef("Bruecke: danach wieder schreiben", await versuch(br.w.CloudSync.save("u1", { a: 1 })), "ok");

  aufruf = []; br = BR_NEU(aufruf);
  br.userFehler(Object.assign(new Error("zugang"), { code: "auth/x" }));
  p = br.w.CloudAuth.deleteAccount({ password: "x" });
  await warte(20);
  br.daten().ja();
  var r = await p.then(function () { return "ok"; }, function (e) { return !!e.dataAlreadyDeleted; });
  pruef("Bruecke: nur der Zugang blieb -> Sperre bleibt", [r, await versuch(br.w.CloudSync.save("u1", {}))], [true, "konto-loescht"]);

  // ---- 11. Bruecke: wirft der Rueckruf selbst, faellt die Sperre wieder ----
  aufruf = []; br = BR_NEU(aufruf);
  p = br.w.CloudAuth.deleteAccount({ password: "x", bestaetigt: function () { throw new Error("Rueckruf kaputt"); } });
  pruef("Bruecke: Wurf im Rueckruf kommt als Fehler an", await versuch(p), "Rueckruf kaputt");
  pruef("Bruecke: danach wird wieder geschrieben", await versuch(br.w.CloudSync.save("u1", {})), "ok");

  // ---- 12. Ein Meal-Abgleich, der beim Bestaetigen schon lief: still, Baseline bleibt ----
  window.CloudSync = { saveRecipesBatch: function () { var e = new Error("Konto wird gelöscht"); e.code = "konto-loescht"; return Promise.reject(e); } };
  state.recipes = [{ id: "r1", name: "Bowl" }];
  lastPushedRecipes = new Map(); toasts = []; gemeldet = [];
  await syncRecipes();
  pruef("syncRecipes: Schreibsperre ohne Hinweis und ohne Fehlerprotokoll", [toasts.length, gemeldet, recipesSyncFailed], [0, [], false]);
  pruef("syncRecipes: Baseline bleibt fuers Nachholen", lastPushedRecipes.size, 0);

  // ---- GEGENPROBE: der Stand vor der Gesamtloesung ----
  starten(deleteAccountFlowALT);
  await warte(20);
  lauf.anmelden();
  await warte(250);
  pruef("GEGENPROBE alt: nach der Neuanmeldung bleibt das Fenster offen, kein Lader",
        [offenZahl(), !!lader()], [1, false]);
  q(".modal-head [data-close]").click();
  await warte(120);
  deleteAccountFlowALT();
  pruef("GEGENPROBE alt: zweiter Start oeffnet ein zweites Fenster", offenZahl(), 1);
  aufraeumen();
  await warte(120);
  fremdesFenster();
  fotosBleiben = true;
  lauf.ja();
  await warte(200);
  pruef("GEGENPROBE alt: Fotohinweis ersetzt das fremde Fenster, dessen Zurueck-Eintrag bleibt haengen",
        [q(".modal h2") && q(".modal h2").textContent, overlayStack.length], ["Konto gelöscht", 1]);
  aufraeumen(); datenGeloescht = false; zuruecksetzen();
  await warte(120);

  starten(deleteAccountFlowALT);
  await warte(20);
  escape();
  await warte(120);
  lauf.nein(new Error("Netz weg"));
  await warte(30);
  pruef("GEGENPROBE alt: Fehler-Toast ist kurz", toasts, [["Konto nicht gelöscht: Fehler: Netz weg", 0]]);
  zuruecksetzen();

  aufruf = []; br = BR_ALT(aufruf);
  p = br.w.CloudAuth.deleteAccount({ password: "x" });
  p.catch(function () {});
  await warte(20);
  pruef("GEGENPROBE alt: Bruecke schreibt waehrend des Loeschens", await versuch(br.w.CloudSync.save("u1", { a: 1 })), "ok");
  br.daten().ja();

  // Alter syncRecipes() mit derselben Ablehnung: meldet sie als Foto-Problem
  lastPushedRecipes = new Map(); toasts = []; gemeldet = []; recipesSyncFailed = false;
  await syncRecipesALT();
  pruef("GEGENPROBE alt: syncRecipes meldet die Sperre als Fehler (Toast + Protokoll)", [toasts.length, gemeldet], [1, ["sync:recipes"]]);
  window.CloudSync = undefined; state.recipes = [];

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""

import json
seite = (seite.replace("__HILFEN__", "\n".join(HILFEN)).replace("__KERN__", KERN)
         .replace("__PUSH__", PUSH).replace("__ML__", ML)
         .replace("__NEU__", NEU).replace("__ALT__", ALT)
         .replace("__SYNC_NEU__", SYNC_NEU).replace("__SYNC_ALT__", SYNC_ALT)
         .replace("__BR_NEU__", json.dumps(BR_NEU)).replace("__BR_ALT__", json.dumps(BR_ALT)))
io.open(ZIEL, "w", encoding="utf-8").write(seite)
print("geschrieben: " + ZIEL)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(ZIEL, zeitbudget=30000))
