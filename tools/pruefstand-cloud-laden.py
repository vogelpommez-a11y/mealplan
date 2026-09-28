# -*- coding: utf-8 -*-
u"""
Pruefstand Cloud-Laden: Was zeigt ein frisches Geraet, solange der erste Abgleich laeuft?

ANLASS (28.09.2026, docs/ABNAHME-MENSCH.md 1.9): Im Instagram-Browser brauchte der erste
Cloud-Abgleich 45 Sekunden. So lange zeigte jeder Reiter einen schwarzen, leeren Plan mit
"0 Meals" - fuer einen neuen Nutzer sieht das aus wie "alles weg". Seitdem zeichnet render()
eine Ladeanzeige, solange `authMode === "cloud" && !cloudBaselineOk && !state.goal`, und
startCloudSync() zeichnet danach neu.

WAS ER PRUEFT - an der ECHTEN, geladenen App:
  A  waehrend des Abgleichs steht die Ladeanzeige, auch nach einem Reiterwechsel
  B  Abgleich fertig, Konto mit Ziel und Meals: die Ladeanzeige ist weg, die App ist da
  C  Abgleich fertig, Konto ganz neu (kein Ziel): die ersten Schritte stehen da
  D  Abgleich scheitert (offline): ebenfalls die ersten Schritte, keine haengende Anzeige
  E  neues Konto kommt ueber einen Teilen-Link (?s=): die ersten Schritte starten dort
     bewusst NICHT (shareOnStart) - die Ladeanzeige darf trotzdem nicht stehen bleiben.
     Das ist der einzige Fall, in dem die Neuzeichnung am Ende von startCloudSync() traegt:
     sonst setzen mergeRemoteRecipes() bzw. der Gruppenzweig das Ziel vor ihrem render()
     (per Aufrufspur nachgewiesen, 28.09.2026).

WIE, OHNE ANS NETZ ZU GEHEN: Nach dem Start steht die App in der Cloud-Anmeldung (Profil
mit cloud:true, kein Firebase-Nutzer). Dann wird window.CloudSync durch eine Attrappe
ersetzt, deren load() erst auf Zuruf antwortet, und der echte handleCloudUser() ueber
window.__onCloudAuth aufgerufen. Alles danach - enterApp(), render(), startCloudSync() - ist
Produktionscode. Nichts erreicht Firestore: die Attrappe ersetzt den einzigen Weg dorthin,
der Pro-Listener (CloudEntitlement) wird abgeschaltet.

ZWEI GEGENPROBEN (--gegenprobe), beide muessen DURCHFALLEN:
  1  derselbe Lauf gegen tools/vorher/cloud-laden/ (eingefrorener Stand vor der Aenderung):
     A muss rot sein - dort gibt es keine Ladeanzeige
  2  der neue Stand ohne die Neuzeichnung im Erfolgszweig von startCloudSync():
     E muss rot sein - die Ladeanzeige bliebe hinter dem Teilen-Dialog stehen. Der erste
     Entwurf liess hier B durchfallen und blieb gruen: B braucht die Zeile gar nicht.

UMGEBUNG: Edge headless, eigenes frisches Profil, Browser-Klasse aus pruefstand-reiter.py.
NIE tools/cdp.py - dessen Profil ist mit dem echten Konto angemeldet.

    python tools/pruefstand-cloud-laden.py
    python tools/pruefstand-cloud-laden.py --gegenprobe
"""
import importlib.util
import io
import json
import os
import sys
import time

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_spec = importlib.util.spec_from_file_location(
    "reiter", os.path.join(WURZEL, "tools", "pruefstand-reiter.py"))
reiter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reiter)
_lauf_nr = 0

NEU = "http://localhost:8000/index.html"
VORHER = "http://localhost:8000/tools/vorher/cloud-laden/index.html"
LADETEXT = u"werden geladen"

# Frisches Geraet: kein Ziel, keine Meals.
ZUSTAND = {"tab": "home", "onboarded": False, "recipes": [], "plans": {},
           "weights": [], "weightGoals": {}, "weekStats": {}}
PROFIL = {"name": "Probe", "email": "", "uid": "probe", "cloud": True}

ZIEL = {"mode": "cut", "kcal": 1950, "protein": 150, "carbs": 180, "fat": 60,
        "activity": "pal14", "training": []}
MEAL = {"id": "rprobe1abc", "name": "Skyr-Bowl", "cat": "Fruehstueck",
        "nutrition": {"kcal": 310, "protein": 34, "carbs": 28, "fat": 6}}

# Die Attrappe. Bekannte Methoden explizit, alles andere ueber einen Proxy: watch*() liefert
# eine Abmeldefunktion, jede andere Methode ein erfuelltes Promise. `then` bleibt undefiniert,
# sonst hielte ein await die Attrappe selbst fuer ein Promise.
ATTRAPPE = u"""(function(){
  window.__rezepte = [];
  var basis = {
    enabled: true,
    load: function () { return new Promise(function (ok, nein) { window.__loese = ok; window.__scheitere = nein; }); },
    loadRecipes: function () { return Promise.resolve(window.__rezepte); }
  };
  window.CloudEntitlement = null;
  // Fuer E: Der Teilen-Link wird nie beantwortet - es geht nur um shareOnStart.
  window.CloudShare = { enabled: true, fetch: function () { return new Promise(function () {}); } };
  window.CloudSync = new Proxy(basis, { get: function (t, k) {
    if (k in t) return t[k];
    if (k === 'then' || typeof k !== 'string') return undefined;
    if (k.indexOf('watch') === 0) return function () { return function () {}; };
    return function () { return Promise.resolve([]); };
  }});
  window.__onCloudAuth({ uid: 'probe', emailVerified: true, displayName: 'Probe', email: '' });
  return 'ok';
})()"""

VIEW_TEXT = u"(document.getElementById('view')||{}).textContent||''"


def starten(b, url, anhang=""):
    u"""Zustand schreiben, neu laden, auf die Anmeldemaske warten, Attrappe einsetzen."""
    # Erst auf eine neutrale Seite derselben Herkunft: Die offene App schreibt beim Verlassen
    # ihr Profil zurueck und ueberschrieb damit - je nach Takt - den Testzustand. Dann stand
    # die Willkommensmaske statt der Cloud-Anmeldung da (28.09.2026, beim ersten Gegenprobelauf).
    b.js("location.href = 'http://localhost:8000/robots.txt'")
    for _ in range(40):
        time.sleep(.15)
        if b.js("location.pathname") == "/robots.txt" and b.js("document.readyState") == "complete":
            break
    b.js("localStorage.clear();"
         "localStorage.setItem('wochenkueche_v1__test', %s);"
         "localStorage.setItem('wochenkueche_profile_v1__test', %s);"
         % (json.dumps(json.dumps(ZUSTAND)), json.dumps(json.dumps(PROFIL))))
    b.js("location.href = %s" % json.dumps(url + "?v=" + str(time.time()) + anhang))
    for _ in range(60):
        time.sleep(.25)
        if b.js("!!document.getElementById('c-google')") is True:
            break
    else:
        return u"Anmeldemaske kam nicht (Seite %r, #view: %r)" % (
            b.js("location.pathname"), text(b)[:80])
    r = b.js(ATTRAPPE)
    time.sleep(1.0)
    return None if r == "ok" else u"Attrappe: %r" % (r,)


def text(b):
    t = b.js(VIEW_TEXT)
    return t if isinstance(t, str) else u""


def lauf(url, sichtbar=False):
    u"""Liefert {Kennung: (gruen, Beschreibung)}."""
    # Je Lauf eigener Port und eigenes Profil: Die Gegenprobe startet zwei Browser direkt
    # hintereinander, und der erste ist nach kill() noch nicht ganz weg - der zweite hing
    # sonst am selben Port und fand die Anmeldemaske nie.
    global _lauf_nr
    _lauf_nr += 1
    reiter.PORT = 9334 + _lauf_nr
    reiter.PROFIL = os.path.join(os.environ.get("TEMP", "."), "mp-edge-cloud-laden-%d" % _lauf_nr)
    reiter.URL = url
    b = reiter.Browser(sichtbar)
    erg = {}
    try:
        # --- A: waehrend des Abgleichs ----------------------------------------
        f = starten(b, url)
        if f:
            return {"A": (False, f)}
        a1 = LADETEXT in text(b)
        status = b.js("!!document.querySelector('#view [role=status]')") is True
        b.js("document.querySelector('[data-action=\"tab\"][data-tab=\"plan\"]').click()")
        time.sleep(.8)
        a2 = LADETEXT in text(b)
        erg["A"] = (a1 and a2 and status,
                    u"Ladeanzeige: Start %s, als Statusmeldung %s, nach Reiterwechsel %s"
                    % (a1, status, a2))

        # --- B: Abgleich fertig, Konto mit Ziel und Meals ---------------------
        b.js("window.__rezepte = [%s]" % json.dumps(MEAL))
        b.js("window.__loese({ goal: %s, onboarded: true })" % json.dumps(ZIEL))
        time.sleep(1.5)
        t = text(b)
        b_ok = LADETEXT not in t and len(t.strip()) > 0
        erg["B"] = (b_ok, u"nach dem Abgleich: Ladeanzeige %s, #view %d Zeichen"
                    % (u"weg" if LADETEXT not in t else u"STEHT NOCH", len(t.strip())))

        # --- C: Abgleich fertig, Konto ganz neu -------------------------------
        f = starten(b, url)
        if f:
            erg["C"] = (False, f)
        else:
            b.js("window.__loese(null)")
            time.sleep(1.5)
            onb = b.js("document.querySelectorAll('.onb-opt, [class*=\"onb-\"]').length") or 0
            t = text(b)
            erg["C"] = (LADETEXT not in t and onb > 0,
                        u"neues Konto: Ladeanzeige %s, erste Schritte %s"
                        % (u"weg" if LADETEXT not in t else u"STEHT NOCH", u"da" if onb else u"FEHLEN"))

        # --- D: Abgleich scheitert --------------------------------------------
        f = starten(b, url)
        if f:
            erg["D"] = (False, f)
        else:
            b.js("window.__scheitere(new Error('offline'))")
            time.sleep(1.5)
            t = text(b)
            onb = b.js("document.querySelectorAll('[class*=\"onb-\"]').length") or 0
            erg["D"] = (LADETEXT not in t and onb > 0,
                        u"Abgleich gescheitert: Ladeanzeige %s, erste Schritte %s"
                        % (u"weg" if LADETEXT not in t else u"STEHT NOCH", u"da" if onb else u"FEHLEN"))

        # --- E: neues Konto ueber einen Teilen-Link ----------------------------
        f = starten(b, url, "&s=probelink123")
        if f:
            erg["E"] = (False, f)
        else:
            vorher = LADETEXT in text(b)
            b.js("window.__loese(null)")
            time.sleep(1.5)
            t = text(b)
            # NICHT auf gefuellten #view pruefen: Ohne Ziel ist der Startreiter leer, und
            # die ersten Schritte kommen bei einem Teilen-Link erst beim naechsten Start
            # (maybeStartOnboarding). Das war vorher genauso und ist nicht Gegenstand hier.
            erg["E"] = (vorher and LADETEXT not in t,
                        u"Teilen-Link: Ladeanzeige vorher %s, danach %s"
                        % (vorher, u"weg" if LADETEXT not in t else u"STEHT NOCH"))
    finally:
        b.zu()
    return erg


def ausgeben(titel, erg):
    print(titel)
    print(u"=" * 60)
    for k in sorted(erg):
        ok, besch = erg[k]
        print(u"  %-4s %s  %s" % (u"ok" if ok else u"ROT", k, besch))
    print()


# Die Neuzeichnung im Erfolgszweig - die erste der beiden gleichlautenden Zeilen, die zweite
# steht im catch. Fehlt sie, bleibt die Anzeige im Fall E stehen.
MUTATION = [
    u"      if (cloudLaedtAngezeigt) { cloudLaedtAngezeigt = false; render(); }\n",
]


def main():
    args = sys.argv[1:]
    sichtbar = "--sichtbar" in args
    os.chdir(WURZEL)
    if not reiter.server_laeuft() and not reiter.server_starten():
        print(u"FEHLGESCHLAGEN: Kein Server auf :8000.")
        return 2

    if "--gegenprobe" in args:
        gut = True
        if not os.path.isdir(os.path.join(WURZEL, "tools", "vorher", "cloud-laden")):
            print(u"Gegenprobe 1 nicht moeglich: python tools/schnappschuss.py cloud-laden ddd8146")
            return 2
        erg = lauf(VORHER, sichtbar)
        ausgeben(u"GEGENPROBE 1 - alter Stand (tools/vorher/cloud-laden):", erg)
        if erg.get("A", (True,))[0]:
            print(u"DURCHGEFALLEN: A ist gegen den alten Stand gruen - misst nichts.")
            gut = False

        pfad = os.path.join(WURZEL, "index.html")
        sicherung = io.open(pfad, encoding="utf-8", newline="").read()
        # Die Datei liegt mit CRLF auf der Platte - die Anker also in beiden Formen suchen.
        kaputt = sicherung
        for z in MUTATION:
            for form in (z.replace(u"\n", u"\r\n"), z):
                if form in kaputt:
                    kaputt = kaputt.replace(form, u"", 1)
                    break
            else:
                print(u"Gegenprobe 2 nicht moeglich: Anker fehlt:\n  " + z.strip())
                return 2
        io.open(pfad, "w", encoding="utf-8", newline="").write(kaputt)
        try:
            erg = lauf(NEU, sichtbar)
        finally:
            io.open(pfad, "w", encoding="utf-8", newline="").write(sicherung)
        ausgeben(u"GEGENPROBE 2 - neuer Stand OHNE Neuzeichnung nach dem Abgleich:", erg)
        if erg.get("E", (True,))[0]:
            print(u"DURCHGEFALLEN: E bleibt ohne die Neuzeichnung gruen - misst nichts.")
            gut = False

        print(u"BESTANDEN: beide Gegenproben schlagen an." if gut else u"GEGENPROBE FEHLGESCHLAGEN")
        return 0 if gut else 1

    erg = lauf(NEU, sichtbar)
    ausgeben(u"Cloud-Laden auf frischem Geraet", erg)
    rot = [k for k, (ok, _) in erg.items() if not ok]
    print(u"ERGEBNIS %d gruen, %d rot" % (len(erg) - len(rot), len(rot)))
    return 1 if rot else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
