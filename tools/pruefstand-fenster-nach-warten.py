# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: Fenster, die nach einem `await` schliessen, treffen kein fremdes Fenster
mehr (26.10.2026, TROUBLESHOOTING 201 - dieselbe Grundluecke wie beim Konto-Loeschen).

  * Passwort zuruecksetzen (openForgotPassword) und Profil speichern (openProfileForm, Cloud):
    nach dem await nur noch `if (offen()) closeModal()`; ein Fehler bei geschlossenem Fenster
    kommt als Toast statt in ein Fehlerfeld, das niemand sieht.
  * Gruppe aufloesen/verlassen (#grp-leave): confirmModal() schliesst schon vor onConfirm - das
    zweite closeModal() nach `await dissolveGroup()/leaveGroup()` ist weg. Stattdessen begleitet
    der Marken-Lader das Warten ("Die Gruppe wird aufgelöst …" / "Du verlässt die Gruppe …").

Echter Code: Zurueck-/Modal-Block, confirmModal(), Marken-Lader, openForgotPassword(),
openProfileForm(), der #grp-leave-Block aus openGroupModal(). Gestubbt: CloudAuth,
dissolveGroup/leaveGroup als Versprechen, die der Pruefstand von aussen aufloest.

Gegenprobe: dieselben Stuecke aus GEGEN_COMMIT (vor dem Fix) - dort greift das spaete
closeModal() ins fremde Fenster (dessen Hook laeuft).
"""
import io, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-fenster-nach-warten.html")
GEGEN_COMMIT = "d316ca9"


def funktion(lines, sig, ende="  }"):
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


def stuecke(lines, endung):
    """Die drei Fenster; Funktionsnamen bekommen `endung`, damit alt und neu nebeneinander passen."""
    leave = funktion(lines, '      const leave = body.querySelector("#grp-leave");', "      });")
    teil = "\n".join([
        funktion(lines, "  function openForgotPassword(prefill) {"),
        funktion(lines, "  function openProfileForm(prefillName) {"),
        "  function gruppeVerlassenKnopf(body) {\n" + leave + "\n  }"])
    for name in ("openForgotPassword", "openProfileForm", "gruppeVerlassenKnopf"):
        teil = teil.replace("function " + name + "(", "function " + name + endung + "(")
    return teil


lines = pm_quelle.lade_seite(QUELLE).split("\n")
start = next((i for i, z in enumerate(lines) if "// ---------- Zurueck-Taste (D5) ----------" in z), None)
oeffnen = next((i for i, z in enumerate(lines) if start is not None and i > start and z.startswith("  function openModal(")), None)
ende = next((i for i, z in enumerate(lines) if oeffnen is not None and i > oeffnen and z == "  }"), None)
if start is None or ende is None:
    raise SystemExit("Schnitt Zurueck/Modal nicht gefunden")
KERN = "\n".join(lines[start:ende + 1]) + "\n" + funktion(lines, "  function confirmModal(o) {")
HILFEN = [z for z in lines if z.startswith("  function el(html)") or z.startswith("  function esc(s)")]
if len(HILFEN) != 2:
    raise SystemExit("el()/esc() nicht gefunden - liegen sie noch in lib/basis.js?")
ML = "\n".join([zeile(lines, "  const ML_SCHRITT_MS"), zeile(lines, "  const ML_ECHT_ZEIGEN_MS"), zeile(lines, "  const ML_LOGO"),
                funktion(lines, "  function markenKarteHtml("), funktion(lines, "  function markenLader(o) {"),
                zeile(lines, "  function validEmail(")])
NEU = stuecke(lines, "")
if "markenLader(" not in NEU or "if (offen()) closeModal();" not in NEU:
    raise SystemExit("Fix nicht im Schnitt - Code pruefen")
alt_lines = subprocess.check_output(["git", "show", GEGEN_COMMIT + ":index.html"], cwd=BASIS).decode("utf-8").split("\n")
ALT = stuecke(alt_lines, "ALT")

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Fenster nach Warten</title>
<div id="modal-root"></div>
<pre id="log">laeuft…</pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) {
  var el = document.getElementById("log");
  el.textContent = (el.textContent || "") + "\\nJS-FEHLER: " + m + " (Zeile " + z + ")";
};
window.addEventListener("unhandledrejection", function (e) {
  var el = document.getElementById("log");
  el.textContent = (el.textContent || "") + "\\nJS-FEHLER (async): " + (e.reason && (e.reason.stack || e.reason.message) || e.reason);
});
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
  document.getElementById("log").textContent = LOG.join("\\n");
}
function warte(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

var hoveredCardId = null, liveScanStop = null, groupModalRepaint = null, gemeldet = [];
var appEl = document.createElement("div"), onb = null;
document.body.appendChild(appEl);
function render() {}
function noteError(k, e) { gemeldet.push(k); }
var MOTION = { base: "200" };
var toasts = [];
function toast(t, ms) { toasts.push(t); }
function cloudErrMsg(e) { return "Fehler: " + e.message; }
// Profil
var state = { profileImage: null }, profile = { name: "Paddy", email: "p@x.de" }, authMode = "cloud";
var ACT_ICONS = { edit: "" }, avatarCropCb = null, avatarInput = { click: function () {} };
function initials(n) { return "P"; }
function saveProfile() {} function rememberLast() {} function renderProfileChip() {}
var namen = null;
function applyDisplayName() { return new Promise(function (ja, nein) { namen = { ja: ja, nein: nein }; }); }
// Passwort
var mail = null;
window.CloudAuth = { resetPassword: function () { return new Promise(function (ja, nein) { mail = { ja: ja, nein: nein }; }); } };
// Gruppe
var rolle = "owner", gruppe = null;
function groupRole() { return rolle; }
function dissolveGroup() { return new Promise(function (ja) { gruppe = { ja: ja, wer: "aufloesen" }; }); }
function leaveGroup() { return new Promise(function (ja) { gruppe = { ja: ja, wer: "verlassen" }; }); }

__HILFEN__
__KERN__
__ML__
__NEU__
__ALT__

function offenZahl() { return modalRoot.childElementCount; }
function q(s) { return modalRoot.querySelector(s); }
function lader() { return document.querySelector(".ml-overlay"); }
var fremdHook = 0;
function fremdesFenster() {
  openModal(el('<div class="modal" role="dialog" aria-label="Fremd"><h2>Fremd</h2></div>'));
  modalCloseHook = function () { fremdHook++; modalCloseHook = null; return false; };
}
function aufraeumen() { modalCloseHook = null; closeModal(); fremdHook = 0; toasts = []; }
function leaveBody(knopf) {
  var body = el('<div><button id="grp-leave">Gruppe</button></div>');
  knopf(body);
  return body;
}

async function passwort(oeffnen, alt) {
  var pre = alt ? "GEGENPROBE alt: " : "";
  oeffnen("a@b.de");
  q("[data-send]").click();
  q(".modal-head [data-close]").click();
  await warte(60);
  fremdesFenster();
  mail.ja();
  await warte(40);
  pruef(pre + "Passwort: spaeter Erfolg " + (alt ? "greift ins fremde Fenster" : "laesst das fremde Fenster in Ruhe"),
        fremdHook, alt ? 1 : 0);
  aufraeumen(); await warte(60);
}

async function profil(oeffnen, alt) {
  var pre = alt ? "GEGENPROBE alt: " : "";
  oeffnen();
  q("[data-save]").click();
  q(".modal-head [data-close]").click();
  await warte(60);
  fremdesFenster();
  namen.ja();
  await warte(40);
  pruef(pre + "Profil: spaeter Erfolg " + (alt ? "greift ins fremde Fenster" : "laesst das fremde Fenster in Ruhe"),
        fremdHook, alt ? 1 : 0);
  aufraeumen(); await warte(60);
}

async function gruppeWeg(knopf, alt, r) {
  var pre = alt ? "GEGENPROBE alt: " : "";
  rolle = r;
  leaveBody(knopf).querySelector("#grp-leave").click();
  q("[data-confirm]").click();
  await warte(250);
  if (!alt) pruef("Gruppe " + gruppe.wer + ": Lader begleitet das Warten",
                  [!!lader(), lader() && lader().textContent.trim()],
                  [true, r === "owner" ? "Die Gruppe wird aufgelöst …" : "Du verlässt die Gruppe …"]);
  else pruef(pre + "Gruppe " + gruppe.wer + ": kein Lader", !!lader(), false);
  // Ein fremdes Fenster geht auf, waehrend es noch laeuft (nach der Frist des Laders moeglich -
  // hier direkt, der Lader liegt nur darueber).
  fremdesFenster();
  gruppe.ja();
  await warte(700);
  pruef(pre + "Gruppe " + gruppe.wer + ": danach " + (alt ? "greift closeModal() ins fremde Fenster" : "bleibt das fremde Fenster unberuehrt"),
        [fremdHook, !!lader()], [alt ? 1 : 0, false]);
  aufraeumen(); await warte(60);
}

(async function () {
  history.pushState({ polster: 1 }, "");
  await warte(30);

  // Fehler bei geschlossenem Fenster: Toast statt unsichtbarem Fehlerfeld
  openForgotPassword("a@b.de");
  q("[data-send]").click();
  q(".modal-head [data-close]").click();
  await warte(60);
  mail.nein(new Error("Netz weg"));
  await warte(30);
  pruef("Passwort: Fehler bei geschlossenem Fenster kommt als Toast", toasts, ["Fehler: Netz weg"]);
  aufraeumen(); await warte(60);
  // ... und bei offenem Fenster wie bisher im Fenster
  openForgotPassword("a@b.de");
  q("[data-send]").click();
  mail.nein(new Error("Netz weg"));
  await warte(30);
  pruef("Passwort: Fehler bei offenem Fenster steht dort", [q("#fp-err").textContent, toasts.length], ["Fehler: Netz weg", 0]);
  aufraeumen(); await warte(60);

  await passwort(openForgotPassword, false);
  await profil(openProfileForm, false);
  await gruppeWeg(gruppeVerlassenKnopf, false, "owner");
  await gruppeWeg(gruppeVerlassenKnopf, false, "edit");
  pruef("kein Fehler protokolliert", gemeldet, []);

  await passwort(openForgotPasswordALT, true);
  await profil(openProfileFormALT, true);
  await gruppeWeg(gruppeVerlassenKnopfALT, true, "owner");

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""

seite = (seite.replace("__HILFEN__", "\n".join(HILFEN)).replace("__KERN__", KERN).replace("__ML__", ML)
         .replace("__NEU__", NEU).replace("__ALT__", ALT))
io.open(ZIEL, "w", encoding="utf-8").write(seite)
print("geschrieben: " + ZIEL)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(ZIEL, zeitbudget=30000))
