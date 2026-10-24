# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: Google-Anmeldung in der Store-App (D7 Etappe 2, 24.10.2026).

In der Capacitor-Huelle verweigert Google OAuth-Popups (disallowed_useragent, docs/STORE.md
Abschnitt 4). Dort holt Androids Kontoauswahl ueber das Plugin SocialLogin ein Google-ID-Token,
Firebase meldet damit an (signInWithCredential) bzw. bestaetigt damit vor dem Konto-Loeschen
(reauthenticateWithCredential). Im Browser muss alles beim Popup bleiben.

Echt und ausgeschnitten: GOOGLE_WEB_CLIENT_ID, popupFallback(), der Block ab `const CAP`
(googleNativCredential), loginGoogle, logout und der Anfang von deleteAccount bis zur
Bestaetigung. Attrappen: die Firebase-Funktionen und das Plugin - sie protokollieren nur.

Gegenprobe: dieselben Stuecke aus ALT_COMMIT (vor Etappe 2) muessen in der App beim Popup
landen - genau der Weg, den Google dort blockiert.

Was hier NICHT geprueft wird: ob Google das Token wirklich ausstellt (Konsole, SHA-1) - das
zeigt nur der Lauf im Emulator mit echtem Konto.
"""
import io, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-google-nativ.html")
# Der Stand vor Etappe 2. Fest verdrahtet, damit die Gegenprobe nicht mitwandert.
ALT_COMMIT = "845a388"


def zeile(lines, anfang):
    for z in lines:
        if z.startswith(anfang):
            return z
    return None


def schnitt(lines, sig, ende, pflicht=True):
    """Ab der Signaturzeile bis zur ersten Zeile, die genau `ende` ist (inklusive).
    Endet die Signaturzeile selbst schon mit '},', ist sie das ganze Stueck."""
    for i, z in enumerate(lines):
        if z.startswith(sig):
            if z.rstrip().endswith("},") and ende.strip() == "},":
                return z
            for j in range(i + 1, len(lines)):
                if lines[j] == ende:
                    return "\n".join(lines[i:j + 1])
            raise SystemExit("KEIN ENDE: " + sig)
    if pflicht:
        raise SystemExit("NICHT GEFUNDEN: " + sig)
    return ""


def bis_zeile(lines, sig, bis):
    for i, z in enumerate(lines):
        if z.startswith(sig):
            for j in range(i + 1, len(lines)):
                if bis in lines[j]:
                    return "\n".join(lines[i:j + 1])
    raise SystemExit("NICHT GEFUNDEN: " + sig + " ... " + bis)


def stuecke(text, neu):
    lines = text.split("\n")
    s = {
        "ID": zeile(lines, "  const GOOGLE_WEB_CLIENT_ID") or "",
        "FALLBACK": schnitt(lines, "      function popupFallback(e, provider) {", "      }"),
        "NATIV": schnitt(lines, "      const CAP = window.Capacitor;", "      }", pflicht=neu),
        "LOGIN": schnitt(lines, "        loginGoogle: function () {", "        },"),
        "LOGOUT": schnitt(lines, "        logout: function () {", "        },"),
        "LOESCHEN": bis_zeile(lines, "        deleteAccount: async function (opts) {", "const uid = user.uid;"),
    }
    return s


neu = stuecke(pm_quelle.lade_seite(QUELLE), True)
# Sicherungen gegen einen stillen Fehlschnitt - auf Aufrufe pruefen, nicht auf Woerter.
if "sl.login(" not in neu["NATIV"] or "GoogleAuthProvider.credential(token)" not in neu["NATIV"]:
    raise SystemExit("googleNativCredential() nicht vollstaendig geschnitten")
if "signInWithCredential(auth, c)" not in neu["LOGIN"]:
    raise SystemExit("loginGoogle nimmt den nativen Weg nicht")
if "reauthenticateWithCredential(user, await googleNativCredential())" not in neu["LOESCHEN"]:
    raise SystemExit("deleteAccount bestaetigt nativ nicht mit Credential")
if ".apps.googleusercontent.com" not in neu["ID"]:
    raise SystemExit("GOOGLE_WEB_CLIENT_ID fehlt oder ist leer")

alt_text = subprocess.check_output(["git", "show", ALT_COMMIT + ":index.html"], cwd=BASIS).decode("utf-8")
alt = stuecke(alt_text, False)
if alt["NATIV"]:
    raise SystemExit("die Gegenprobe enthaelt schon den nativen Weg - ALT_COMMIT pruefen")

FABRIK = u"""function __NAME__(capacitor) {
  window.Capacitor = capacitor;
  var auth = { currentUser: NUTZER };
  var RESOLVER = "RESOLVER", REDIRECT_MERKER = "pm-test-redirect";
__ID__
__FALLBACK__
__NATIV__
  return {
__LOGIN__
__LOGOUT__
__LOESCHEN__
          return "bestaetigt";
        }
  };
}
"""


def fabrik(name, s):
    f = FABRIK.replace("__NAME__", name)
    for k in ("ID", "FALLBACK", "NATIV", "LOGIN", "LOGOUT", "LOESCHEN"):
        f = f.replace("__" + k + "__", s[k])
    return f


seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Google nativ</title>
<pre id="log"></pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) { document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")"; };
window.addEventListener("unhandledrejection", function (e) { LOG.push("UNBEHANDELT: " + (e.reason && (e.reason.code || e.reason.message))); });
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
  document.getElementById("log").textContent = LOG.join("\\n");
}

// ---- Attrappen: protokollieren nur ----
var RUF = [], NOTIZ = [];
var NUTZER = { uid: "ich", providerData: [{ providerId: "google.com" }] };
window.noteError = function (k) { NOTIZ.push(k); };
function GoogleAuthProvider() { this.setCustomParameters = function () {}; }
GoogleAuthProvider.credential = function (t) { RUF.push("credential:" + t); return { token: t }; };
function OAuthProvider() { this.addScope = function () {}; }
var EmailAuthProvider = { credential: function () { return {}; } };
function signInWithPopup() { RUF.push("popup"); return Promise.resolve("popup-nutzer"); }
function signInWithRedirect() { RUF.push("redirect"); return Promise.resolve(); }
function signInWithCredential(a, c) { RUF.push("signInWithCredential:" + c.token); return Promise.resolve("nutzer"); }
function reauthenticateWithPopup() { RUF.push("reauthPopup"); return Promise.resolve(); }
function reauthenticateWithCredential(u, c) { RUF.push("reauthCredential:" + c.token); return Promise.resolve(); }
function signOut() { RUF.push("signOut"); return Promise.resolve(); }

// Das Plugin. modus: ok | abbruch | ohneToken | fehler | initFehltEinmal
function plugin(modus) {
  var initVersuche = 0;
  return {
    initialize: function (o) {
      initVersuche++;
      RUF.push("sl.initialize:" + (o.google.webClientId.indexOf(".apps.googleusercontent.com") > 0 ? "web-id" : o.google.webClientId));
      if (modus === "initFehltEinmal" && initVersuche === 1) return Promise.reject({ message: "init kaputt" });
      return Promise.resolve();
    },
    login: function (o) {
      RUF.push("sl.login:" + o.provider);
      if (modus === "abbruch") return Promise.reject({ code: "USER_CANCELLED", message: "cancelled" });
      if (modus === "fehler") return Promise.reject({ message: "[28444] Developer console is not set up correctly" });
      if (modus === "ohneToken") return Promise.resolve({ provider: "google", result: {} });
      return Promise.resolve({ provider: "google", result: { idToken: "T1" } });
    },
    logout: function () { RUF.push("sl.logout"); return Promise.resolve(); }
  };
}
function app(modus) { return { isNativePlatform: function () { return true; }, Plugins: modus ? { SocialLogin: plugin(modus) } : {} }; }
async function ruf(fn) {
  RUF = []; NOTIZ = [];
  try { await fn(); return "ok"; } catch (e) { return "fehler:" + (e && e.code); }
}

__NEU__
__ALT__

(async function () {
  var a, erg;

  // ===== 1. Browser: alles bleibt beim Popup =====
  a = NEU(undefined);
  pruef("Web: Anmelden oeffnet das Popup", [await ruf(a.loginGoogle), RUF], ["ok", ["popup"]]);
  pruef("Web: Abmelden ruft nur signOut", [await ruf(a.logout), RUF], ["ok", ["signOut"]]);
  pruef("Web: Konto loeschen bestaetigt per Popup", [await ruf(function () { return a.deleteAccount({}); }), RUF], ["ok", ["reauthPopup"]]);
  a = NEU({ isNativePlatform: function () { return false; }, Plugins: { SocialLogin: plugin("ok") } });
  pruef("Capacitor-Objekt ohne native Plattform: weiter Popup", [await ruf(a.loginGoogle), RUF], ["ok", ["popup"]]);

  // ===== 2. Store-App: Androids Kontoauswahl =====
  a = NEU(app("ok"));
  pruef("App: Anmelden ueber Plugin, Token an Firebase",
    [await ruf(a.loginGoogle), RUF], ["ok", ["sl.initialize:web-id", "sl.login:google", "credential:T1", "signInWithCredential:T1"]]);
  pruef("App: zweites Anmelden initialisiert nicht erneut",
    [await ruf(a.loginGoogle), RUF], ["ok", ["sl.login:google", "credential:T1", "signInWithCredential:T1"]]);
  pruef("App: Konto loeschen bestaetigt mit Credential, kein Popup",
    [await ruf(function () { return a.deleteAccount({}); }), RUF], ["ok", ["sl.login:google", "credential:T1", "reauthCredential:T1"]]);
  pruef("App: Abmelden vergisst auch Androids Kontoauswahl", [await ruf(a.logout), RUF], ["ok", ["sl.logout", "signOut"]]);

  // ===== 3. Store-App: Abbruch und Fehler =====
  a = NEU(app("abbruch"));
  erg = await ruf(a.loginGoogle);
  pruef("App: Abbruch meldet 'Anmeldung abgebrochen', ohne Fehlernotiz", [erg, NOTIZ], ["fehler:auth/cancelled-popup-request", []]);
  pruef("App: nach Abbruch keine Anmeldung bei Firebase", RUF.indexOf("signInWithCredential:T1"), -1);
  a = NEU(app("fehler"));
  pruef("App: Plugin-Fehler -> eigene Meldung + Notiz fuer die Diagnose", [await ruf(a.loginGoogle), NOTIZ], ["fehler:auth/google-nativ", ["auth:googleNativ"]]);
  a = NEU(app("ohneToken"));
  pruef("App: kein Token -> eigene Meldung, keine Anmeldung", [await ruf(a.loginGoogle), RUF.indexOf("popup")], ["fehler:auth/google-nativ", -1]);
  a = NEU(app(null));
  pruef("App ohne Plugin: Meldung statt Popup (das Google dort blockt)", [await ruf(a.loginGoogle), RUF], ["fehler:auth/google-nativ", []]);
  a = NEU(app("initFehltEinmal"));
  erg = await ruf(a.loginGoogle);
  pruef("App: scheitert das Initialisieren ...", erg, "fehler:auth/google-nativ");
  pruef("... versucht der naechste Tipp es erneut", [await ruf(a.loginGoogle), RUF[0]], ["ok", "sl.initialize:web-id"]);

  // ===== 4. Gegenprobe: der Stand vor Etappe 2 =====
  a = ALT(app("ok"));
  pruef("GEGENPROBE: alter Stand oeffnet in der App das Popup (von Google blockiert)", [await ruf(a.loginGoogle), RUF], ["ok", ["popup"]]);
  pruef("GEGENPROBE: alter Stand bestaetigt das Loeschen per Popup", [await ruf(function () { return a.deleteAccount({}); }), RUF], ["ok", ["reauthPopup"]]);
  pruef("GEGENPROBE: alter Stand ruft das Plugin beim Abmelden nicht", [await ruf(a.logout), RUF], ["ok", ["signOut"]]);

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""

seite = seite.replace("__NEU__", fabrik("NEU", neu)).replace("__ALT__", fabrik("ALT", alt))
io.open(ZIEL, "w", encoding="utf-8").write(seite)
print("geschrieben: " + ZIEL)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(ZIEL))
