# -*- coding: utf-8 -*-
u"""Passt der Startreiter ohne Scrollen auf einen Bildschirm?

Seit dem 05.09.2026 ist das eine Zusage, keine Beobachtung (docs/DESIGN.md). Sie haelt
nur, solange niemand dem Reiter etwas hinzufuegt, ohne an anderer Stelle Platz zu machen -
und genau das faellt beim Bauen nicht auf: Am 27-Zoll-Monitor ist immer Platz.

Gemessen wird die ECHTE App in einem <iframe> fester Groesse. Das ist der Punkt: Die
Media Queries eines Rahmens richten sich nach SEINER Breite, nicht nach der des Fensters -
so laesst sich ein iPhone-Viewport auf einem Desktop-Browser wirklich herstellen. Der
Umweg ueber --window-size taugt dafuer nicht, headless liefert dabei eine andere
CSS-Breite als angefordert (gemessen: 390 angefordert, 489 bekommen).

Geprueft wird gegen die tatsaechlichen CSS-Viewports gaengiger Geraete - also die Hoehe
OHNE Browserleisten, nicht die Bildschirmdiagonale.

Aufruf:
    python tools/pruefstand-home-eine-seite.py [pfad-zu-index.html]
    python tools/pruefstand-home-eine-seite.py --gegenprobe   # gegen den Stand VOR dem Umbau

Die Gegenprobe faehrt denselben Messaufbau gegen HEAD~ (bzw. gegen den in
GEGENPROBE_COMMIT genannten Stand) und MUSS durchfallen. Tut sie das nicht, misst der
Pruefstand nicht das, was er zu messen vorgibt.
"""
import io, json, os, re, shutil, subprocess, sys, tempfile

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASIS, "tools"))
import quelle as pm_quelle

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ANKER = '<meta charset="utf-8">'
GEGENPROBE_COMMIT = "HEAD"   # der Stand VOR dem Umbau liegt im letzten Commit

# Name, Breite, Hoehe des CSS-Viewports, muss-passen
#
# ACHTUNG, hier lag der Fehler: Bis zum 06.09.2026 standen hier nur die Hoehen OHNE
# Browserleisten (lvh). Die sieht man auf dem Handy aber erst NACH dem Scrollen - beim
# Aufruf sind rund 100px weniger da. Der Pruefstand meldete deshalb gruen, waehrend der
# Reiter auf einem echten iPhone scrollte. Ein Pruefstand, der die falsche Zahl fuer die
# richtige haelt, ist schlimmer als keiner.
#
# Jetzt steht jedes Handy ZWEIMAL drin: einmal mit Adressleiste (svh, der Zustand beim
# Aufruf) und einmal ohne (lvh, nach dem Scrollen). Beide muessen passen.
GERAETE = [
    (u"iPhone SE",           375, 553, True),
    (u"iPhone 13/14/15 svh", 390, 556, True),
    (u"iPhone 13/14/15 lvh", 390, 664, True),
    (u"Pixel 7 svh",         412, 616, True),
    (u"Pixel 7 lvh",         412, 719, True),
    (u"ProMax svh",          430, 643, True),
    (u"ProMax lvh",          430, 745, True),
    (u"iPad hochkant",       768, 954, True),
    (u"Notebook 1440x900",  1440, 790, True),
    (u"Desktop 1920x1080",  1920, 969, True),
]

# Die andere Haelfte der Zusage. Bei den Geraeten oben MUSS es passen; hier darf es das
# ausdruecklich nicht - und genau deshalb stehen sie da: Sie pruefen den NOTAUSGANG.
#
# Ohne sie war er nur strukturell abgesichert ("<main> hat overflow-y:auto"). Das ist eine
# Aussage ueber CSS, nicht ueber Erreichbarkeit: Bei zu kleinem Fenster lag die Knopfzeile
# trotz auto hinter der fixierten Tabbar, weil der freigehaltene Rand 4px zu schmal war.
# Eine Eigenschaft zu pruefen, statt der Wirkung, haette das nie gefunden.
#
# Gemessen wird deshalb die Wirkung: bis ans Ende scrollen, dann nachsehen, ob die
# Knopfzeile vollstaendig im Bild liegt UND frei vor der Kapsel.
#
# Querformat ist hier kein Kunstfall - ein gedrehtes Handy hat rund 390px Hoehe.
NOTFALL = [
    (u"iPhone quer",   844, 390),
    (u"Pixel quer",    915, 412),
    (u"sehr flach",    390, 450),
    (u"extrem flach",  390, 380),
    (u"schmal+flach",  320, 420),
]

# Wieviel Leerraum unter der Knopfzeile noch als Abstand durchgeht und ab wann er ein
# Loch ist. 60px ist grosszuegig: Der normale Abstand zum Fuss betraegt gemessen 24px,
# das Loch von vorher 114 bis 351. Dazwischen liegt kein Grenzfall, ueber den man streiten
# muesste - der Wert muss nur beide Seiten sicher trennen.
LEERE_MAX = 60

# Der SE-Deckel ist am 06.09.2026 ERSATZLOS entfallen, und zwar nach oben: Seit der
# Startreiter den Bildschirm fuellt statt ihn nur nicht zu ueberschreiten, passt er auch
# auf einem iPhone SE vollstaendig - gemessen 0px Ueberstand, vorher 83.
#
# Die Ausnahme war nie eine Eigenschaft des Geraets, sondern eine Folge der festen Hoehe.
# Sie als "bekannte Ausnahme" stehen zu lassen, waere ab jetzt eine Erlaubnis fuer eine
# Verschlechterung, die niemand mehr bemerkt.

# Zustand mit Ziel und teilweise geplanter Woche - der Normalfall, und der hoechste:
# Mit Ziel zeigt die Heute-Karte drei Makrobalken, ohne Ziel faellt der halbe Reiter weg.
GOAL = {"kcal": 2586, "carbs": 309, "protein": 176, "fat": 72, "sex": "m", "age": 34,
        "height": 182, "weight": 88, "activity": "pal16", "mode": "lose", "pace": "moderate",
        "training": {"mon": {"level": "normal", "min": 60}, "wed": {"level": "normal", "min": 60},
                     "fri": {"level": "normal", "min": 60}}}
R = {"id": "rmess1", "name": u"Messgericht", "category": u"Hauptgericht", "time": 20,
     "tags": [], "ingredients": [],
     "nutrition": {"kcal": 700, "carbs": 70, "protein": 55, "fat": 21}}


# Der Plan wird im Browser gebaut, nicht hier: Er muss den HEUTIGEN Tag treffen, und an
# welchem Wochentag jemand den Pruefstand faehrt, weiss dieses Skript nicht.
#
# Gemessen wird der HOECHSTE Zustand, nicht irgendeiner:
#   * heute IST geplant  -> die Heute-Karte zeigt drei Makrobalken statt eines Hinweissatzes
#   * ein anderer Tag ist offen -> die Wochenkarte zeigt zusaetzlich die Zeile
#     "Fuer die N offenen Tage bleiben ..."
# Beides zusammen ist der laengste Reiter, den es gibt. Ein leerer Plan waere die
# bequemste Messung und die nutzloseste.
PLAN_JS = ("""(function () {
  var voll = function () { return {fr: ["rmess1"], mi: ["rmess1"], ab: ["rmess1"], sn: []}; };
  var tage = ["mon","tue","wed","thu","fri","sat","sun"], p = {};
  tage.forEach(function (t) { p[t] = voll(); });
  var heute = tage[(new Date().getDay() || 7) - 1];
  var offen = heute === "sun" ? "sat" : "sun";
  p[offen] = {fr: [], mi: [], ab: [], sn: []};
  return p;
})()""")


def seite_bauen(quelltext):
    u"""Legt Zustand und Profil in localStorage und liefert die fertige Seite."""
    state = {"recipes": [R], "plans": {}, "goal": GOAL, "onboarded": True, "tab": "home",
             "favs": [], "planned": {}, "shopPersons": 1, "viewWeek": "cur",
             "weights": [], "weightGoals": {}, "weekStats": {}}
    seed = (u'<script>try{'
            u'var st=%s; var d=new Date();'
            u'var don=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()-((d.getDay()||7)-1)+3));'
            u'var ft=new Date(Date.UTC(don.getUTCFullYear(),0,4));'
            u'ft.setUTCDate(ft.getUTCDate()-((ft.getUTCDay()+6)%%7)+3);'
            u'var wk=don.getUTCFullYear()+"-W"+("0"+(1+Math.round((don-ft)/6048e5))).slice(-2);'
            u'st.plans[wk]=%s;'
            u'["wochenkueche_v1","wochenkueche_v1__test"].forEach(function(k){localStorage.setItem(k,JSON.stringify(st));});'
            u'["wochenkueche_profile_v1","wochenkueche_profile_v1__test"].forEach(function(k){'
            u'localStorage.setItem(k,JSON.stringify({name:"Mess"}));});'
            u'}catch(e){}</script>' % (json.dumps(state), PLAN_JS))
    if quelltext.count(ANKER) != 1:
        raise SystemExit("charset-Meta nicht genau einmal gefunden.")
    return quelltext.replace(ANKER, ANKER + seed, 1)


RAHMEN = u"""<!doctype html><meta charset="utf-8"><title>Messung</title>
<style>html,body{margin:0;background:#000}iframe{border:0;display:block}</style>
<script>
var GERAETE = __GERAETE__.concat(__NOTFALL__);
var offen = GERAETE.length, raus = [];
// Erst wenn <body> existiert. Das Skript steht im Kopf; ein appendChild auf ein noch
// nicht geparstes document.body wirft, und dann misst gar nichts mehr - der Pruefstand
// waere stumm statt rot. Genau die Falle aus TROUBLESHOOTING 109/119.
addEventListener("DOMContentLoaded", function () {
GERAETE.forEach(function (g) {
  var f = document.createElement("iframe");
  f.width = g[1]; f.height = g[2]; f.src = "app.html";
  document.body.appendChild(f);
  f.addEventListener("load", function () {
    setTimeout(function () {
      var e = {name: g[0], w: g[1], h: g[2], muss: g[3], notfall: g[3] === null};
      try {
        var d = f.contentDocument, D = d.documentElement, W2 = f.contentWindow;
        e.doc = D.scrollHeight; e.ueber = D.scrollHeight - g[2];
        e.quer = D.scrollWidth - g[1];
        var v = d.getElementById("view");
        e.viewGefuellt = !!(v && v.textContent.trim().length > 40);
        e.hatRing = !!d.querySelector(".wg-ring");
        e.hatMakros = d.querySelectorAll(".wg-macros .gm").length;
        e.hatWoche = !!d.querySelector(".wg-week");
        // Tippziele. Die Grenze haengt am Breakpoint, nicht an der Meinung:
        // Unter 681 px faehrt die App ihr Touch-Layout und css/mobil.css sagt dort
        // min-height:44px ausdruecklich zu - das wird hier nachgehalten. Darueber liegt
        // das Zeigergeraet-Layout; dafuer gilt WCAG 2.2 (2.5.8) mit 24x24 CSS-Pixeln.
        // Eine einzige Zahl fuer beides waere entweder am Rechner unsinnig streng oder
        // auf dem Handy zu lasch.
        var grenze = g[1] <= 680 ? 43.5 : 23.5;
        e.grenze = g[1] <= 680 ? 44 : 24;
        var klein = [];
        d.querySelectorAll(".week-nut button").forEach(function (b) {
          var r = b.getBoundingClientRect();
          if (r.height > 0 && r.height < grenze) klein.push(b.textContent.trim().slice(0, 18) + "=" + Math.round(r.height));
        });
        e.kleineZiele = klein;
        // Die zweite Luecke dieses Pruefstands: "passt auf den Bildschirm" heisst nicht
        // "ist bedienbar". Die Kapsel klebt fix am unteren Rand; Inhalt, der in ihren
        // Bereich quillt, steht im Dokument und ist trotzdem weg. Genau so lag am
        // 06.09.2026 die komplette Knopfzeile unsichtbar darunter, waehrend die
        // Hoehenmessung +0 meldete.
        var kap = d.querySelector(".tabs"), akt = d.querySelector(".wg-actions");
        e.verdeckt = 0;
        if (kap && akt) {
          var kr = kap.getBoundingClientRect(), ar = akt.getBoundingClientRect();
          // Nur wenn die Kapsel unten klebt - am Rechner sitzt sie oben und deckt nichts zu.
          if (kr.top > g[2] / 2 && ar.bottom > kr.top) e.verdeckt = Math.round(ar.bottom - kr.top);
        }
        // Der Notausgang: Passt es doch einmal nicht, muss <main> scrollen koennen.
        var mn = d.querySelector("main");
        e.mainOverflow = mn ? W2.getComputedStyle(mn).overflowY : "?";
        // Notfall: bis ans Ende scrollen und DANN nachsehen. Vorher gemessen hiesse
        // pruefen, ob es zufaellig sichtbar ist - nicht, ob man hinkommt.
        if (e.notfall && mn && akt) {
          mn.scrollTop = mn.scrollHeight;
          var ar3 = akt.getBoundingClientRect();
          var kr3 = kap ? kap.getBoundingClientRect() : null;
          e.imBild = ar3.top >= -1 && ar3.bottom <= g[2] + 1;
          e.freiVonKapsel = (!kr3 || kr3.top < g[2] / 2) ? true : ar3.bottom <= kr3.top + 1;
          e.erreichbar = e.imBild && e.freiVonKapsel;
          e.scrollWeg = Math.round(mn.scrollHeight - mn.clientHeight);
        }
        // Und die andere Haelfte der Zusage: NICHT scrollen ist nur die eine Bedingung,
        // den Platz auch NUTZEN die andere. Bis zum 06.09.2026 hatte der Reiter eine feste
        // Hoehe und der Fuss wurde per margin:auto nach unten gedrueckt - dazwischen stand
        // Leere: gemessen 114px am Notebook und 351px auf 1920x1080. Die Hoehenmessung
        // fand das in Ordnung, weil nichts uebersteht. Ein halber Pruefer.
        // Der Footer ist auf dem Handy display:none, steht aber im DOM und liefert dann
        // ein Null-Rechteck bei top=0. Wer ihn ungeprueft nimmt, misst dort immer 0 Leere
        // und haelt jeden mobilen Abstand fuer richtig.
        var fu = d.querySelector("footer");
        var unten = (fu && fu.getBoundingClientRect().height > 0) ? fu : kap;
        e.leere = 0;
        if (akt && unten) {
          var ur = unten.getBoundingClientRect(), ar2 = akt.getBoundingClientRect();
          if (ur.top >= ar2.bottom) e.leere = Math.round(ur.top - ar2.bottom);
        }
      } catch (ex) { e.fehler = ex.message; }
      raus.push(e);
      if (--offen === 0) {
        var p = document.createElement("pre");
        p.id = "messung"; p.textContent = JSON.stringify(raus);
        document.documentElement.appendChild(p);
      }
    }, 8000);   // die App faellt erst nach ~6 s vom Cloud- in den lokalen Modus
  });
});
});
</script>"""


def lauf(index_pfad):
    quelle_txt = pm_quelle.lade_seite(index_pfad)
    tmp = tempfile.mkdtemp(prefix="home-eine-seite-")
    try:
        io.open(os.path.join(tmp, "app.html"), "w", encoding="utf-8").write(seite_bauen(quelle_txt))
        # Notfall-Geraete tragen None als "muss" - daran erkennt sie das Messskript.
        rahmen = RAHMEN.replace("__GERAETE__", json.dumps([list(g) for g in GERAETE]))
        rahmen = rahmen.replace("__NOTFALL__", json.dumps([[n, w, h, None] for n, w, h in NOTFALL]))
        io.open(os.path.join(tmp, "mess.html"), "w", encoding="utf-8").write(rahmen)
        dump = os.path.join(tmp, "dump.html")
        with io.open(dump, "wb") as f:
            subprocess.call([
                EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=60000",
                # Ohne diese Flagge behandelt Chromium jeden file://-Rahmen als fremde
                # Herkunft: contentDocument ist dann null und es gibt nichts zu messen.
                "--allow-file-access-from-files",
                "--user-data-dir=" + os.path.join(tmp, "profil"),
                "--dump-dom", "file:///" + os.path.join(tmp, "mess.html").replace("\\", "/")
            ], stdout=f, stderr=subprocess.PIPE)
        roh = io.open(dump, encoding="utf-8", errors="replace").read()
        m = re.search(r'<pre id="messung">(.*?)</pre>', roh, re.S)
        if not m:
            raise SystemExit("KEINE MESSUNG - der Pruefstand selbst ist kaputt.")
        t = m.group(1)
        for a, b in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&amp;", "&")):
            t = t.replace(a, b)
        return json.loads(t)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def bewerte(messungen, titel, alt=False):
    u"""alt=True fuer die Gegenprobe.

    Der Stand VOR dem Umbau kennt `.wg-week` noch nicht - die Wochenangabe stand dort im
    Intro-Hero. Verlangte die Gegenprobe sie trotzdem, fiele der alte Stand an DIESER
    Bedingung durch und nicht an der Hoehe. Sie waere gruen, ohne je etwas ueber das
    Scrollen gesagt zu haben: genau die Sorte Pruefung, vor der TROUBLESHOOTING 119 und 123
    stehen. Deshalb faellt sie in der Gegenprobe weg - alles andere bleibt scharf.
    """
    ok = bad = offen = 0
    print(u"")
    print(titel)
    print(u"-" * 70)
    for e in sorted(messungen, key=lambda x: (x.get("notfall", False), x["w"])):
        marke = "%-20s %4dx%-4d" % (e["name"], e["w"], e["h"])
        if e.get("notfall"):
            if e.get("fehler"):
                print(u"  FEHLER  " + marke + u"  Messfehler: " + e["fehler"]); bad += 1; continue
            if e.get("erreichbar"):
                print(u"  OK      " + marke + u"  passt nicht (soll es nicht) - aber nach"
                      u" %dpx Scrollen voll erreichbar" % e.get("scrollWeg", 0)); ok += 1
            else:
                print(u"  FEHLER  " + marke + u"  NOTAUSGANG DEFEKT: Knopfzeile auch nach dem"
                      u" Scrollen nicht erreichbar (im Bild=%s, frei von Kapsel=%s)"
                      % (e.get("imBild"), e.get("freiVonKapsel"))); bad += 1
            continue
        if e.get("fehler"):
            print(u"  FEHLER  " + marke + u"  Messfehler: " + e["fehler"]); bad += 1; continue
        u_ = e["ueber"]
        zusatz = u"doc=%d  ueber=%+d  quer=%+d  leer=%d" % (e["doc"], u_, e["quer"], e.get("leere", 0))
        if not e["viewGefuellt"]:
            print(u"  FEHLER  " + marke + u"  #view ist leer - die App startet gar nicht"); bad += 1; continue
        if not (e["hatRing"] and e["hatMakros"] == 3 and (alt or e["hatWoche"])):
            print(u"  FEHLER  " + marke + u"  Inhalt fehlt: Ring=%s Makrobalken=%d Wochenangabe=%s"
                  % (e["hatRing"], e["hatMakros"], e["hatWoche"])); bad += 1; continue
        if e["kleineZiele"]:
            print(u"  FEHLER  " + marke + u"  Tippziel unter %dpx: %s"
                  % (e.get("grenze", 44), ", ".join(e["kleineZiele"]))); bad += 1; continue
        if e["quer"] > 0:
            print(u"  FEHLER  " + marke + u"  scrollt QUER  " + zusatz); bad += 1; continue
        if e.get("verdeckt"):
            print(u"  FEHLER  " + marke + u"  Knopfzeile liegt %dpx hinter der Kapsel  %s"
                  % (e["verdeckt"], zusatz)); bad += 1; continue
        if e["w"] <= 680 and e.get("mainOverflow") != "auto":
            print(u"  FEHLER  " + marke + u"  <main> ohne overflow-y:auto (%s) - ohne den"
                  u" Notausgang waere zu viel Inhalt unerreichbar" % e.get("mainOverflow"))
            bad += 1; continue
        if e.get("leere", 0) > LEERE_MAX:
            print(u"  FEHLER  " + marke + u"  %dpx ungenutzte Leere unter der Knopfzeile"
                  u" (erlaubt %d)  %s" % (e["leere"], LEERE_MAX, zusatz)); bad += 1; continue
        if u_ <= 0: print(u"  OK      " + marke + u"  " + zusatz); ok += 1
        else:       print(u"  FEHLER  " + marke + u"  scrollt  " + zusatz); bad += 1
    return ok, bad, offen


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    gegen = "--gegenprobe" in args
    args = [a for a in args if not a.startswith("--")]
    index = os.path.abspath(args[0]) if args else os.path.join(BASIS, "index.html")

    if not gegen:
        print(u"Datei: " + index)
        ok, bad, offen = bewerte(lauf(index),
                                 u"Fuellt Home den Bildschirm - und bleibt sonst alles erreichbar?")
        print(u"")
        print(u"ERGEBNIS %d gruen, %d rot" % (ok, bad))
        print(u"Gegenprobe mit --gegenprobe: der Stand davor MUSS durchfallen.")
        sys.exit(1 if bad else 0)

    # Gegenprobe: derselbe Aufbau gegen den Stand vor dem Umbau.
    print(u"GEGENPROBE gegen " + GEGENPROBE_COMMIT + u" - dieser Stand MUSS durchfallen.")
    tmp = tempfile.mkdtemp(prefix="home-alt-")
    try:
        for pfad in ("index.html", "css/tokens.css", "css/basis.css", "css/komponenten.css",
                     "css/mobil.css", "lib/basis.js", "lib/pdf.js", "lib/barcode.js",
                     "data/ikonen.js", "data/bilder.js", "data/cookbook.js", "data/foods.js",
                     "data/rechtstexte.js"):
            ziel = os.path.join(tmp, pfad.replace("/", os.sep))
            if not os.path.isdir(os.path.dirname(ziel)):
                os.makedirs(os.path.dirname(ziel))
            inhalt = subprocess.check_output(["git", "-C", BASIS, "show",
                                              "%s:%s" % (GEGENPROBE_COMMIT, pfad)])
            io.open(ziel, "wb").write(inhalt)
        ok, bad, offen = bewerte(lauf(os.path.join(tmp, "index.html")),
                                 u"Der Stand VOR dem Umbau", alt=True)
        print(u"")
        if bad:
            print(u"ERGEBNIS Gegenprobe bestanden - der alte Stand faellt durch (%d rot)" % bad)
            sys.exit(0)
        print(u"ERGEBNIS Gegenprobe FEHLGESCHLAGEN - der alte Stand kommt durch")
        print(u"Dann misst der Pruefstand nicht das, was er zu messen vorgibt.")
        sys.exit(1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
