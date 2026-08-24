# -*- coding: utf-8 -*-
u"""
Ansichts-Pruefstand Rezeptbuch: die ECHTE App, lokal angemeldet, Reiter "Rezeptbuch".

Der Logik-Pruefstand daneben (pruefstand-rezeptbuch-filter.py) rechnet Mengen nach. Er kann
aber nicht sagen, ob die Chip-Reihe wirklich im DOM landet, ob die Kategorien bei aktivem
Chip noch einen Klappknopf tragen und ob der entfallene Hinweistext auch wirklich weg ist.
Genau das prueft diese Datei - an der ungekuerzten index.html, ohne Ausschnitt und ohne Stub.

Aufruf:  python tools/pruefstand-rezeptbuch-ansicht.py
"""
import io, json, os, re, subprocess, sys, tempfile, shutil

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Gegenprobe: Der Pruefstand nimmt wahlweise eine andere Datei entgegen, damit er gegen den
# Stand VOR der Aenderung laufen kann. Ohne diesen Lauf beweist er nichts - er muesste dort
# rot sein (kein Chip vorbelegt, Kopfzeilen bei aktivem Filter ohne Caret).
#   git show HEAD:index.html > alt.html && python tools/pruefstand-rezeptbuch-ansicht.py alt.html
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ANKER = '<meta charset="utf-8">'

# Ohne cloud-Flag im Profil geht die App in den lokalen Login und startet ohne Handshake
# durch (index.html, handleStart). Mit gesetztem goal bleibt das Onboarding aus.
PROFILE = {"name": "Test"}


def lauf(goal, was):
    state = {
        "recipes": [], "plans": {}, "goal": goal, "onboarded": True,
        "tab": "recipes", "favs": [], "planned": {}, "shopPersons": 1, "viewWeek": "cur"
    }
    seite = io.open(INDEX, encoding="utf-8").read()
    seed = (u'<script>window.__fehler=[];'
            u'window.addEventListener("error",function(e){window.__fehler.push((e.message||"")+" @"+(e.lineno||"?"));});'
            # "__test"-Suffix: localKey() haengt es unter file:// an jeden Schluessel
            # (isTestOrigin). Ohne das liest die App nichts und zeigt den Login.
            u'try{["wochenkueche_v1","wochenkueche_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
            u'["wochenkueche_profile_v1","wochenkueche_profile_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});}catch(e){}</script>'
            % (json.dumps(json.dumps(state)), json.dumps(json.dumps(PROFILE))))

    # Nach dem Start in den Katalog wechseln und den Zustand ablegen. Bewusst ueber die
    # vorhandenen Knoepfe statt ueber interne Variablen: So laeuft genau der Weg, den ein
    # Mensch auch geht - einschliesslich renderRecipes() und paintCookbook().
    #
    # Kein setTimeout mit langer Wartezeit: --dump-dom wartet nicht beliebig. 300 ms reichen,
    # die App rendert synchron; virtual-time-budget deckt den Rest ab.
    mess = u'''<script>setTimeout(function () {
  var raus = {};
  try {
    // Ueber die Reiterleiste gehen statt state.tab zu setzen: So laeuft genau der Weg, den
    // ein Mensch auch nimmt - einschliesslich render() und renderRecipes().
    var reiter = document.querySelector('[data-tab="recipes"]');
    if (reiter) reiter.click();
    var buch = document.querySelector('[data-rtab="buch"]');
    raus.reiterDa = !!buch;
    if (buch) buch.click();
    // Erst NACH dem Klick auslesen: Ein Fehler in einem Event-Listener steigt nicht zum
    // Aufrufer auf, er landet nur bei window.onerror. Vorher gelesen haette die Messung
    // "keine" gemeldet und die Ursache verschluckt.
    // Beweis, dass ueberhaupt die Katalogansicht gemessen wird und nicht ein leeres #view:
    // Ohne diese Zeile waeren alle Zaehlungen unten trivial 0 und der Test durchweg gruen.
    raus.cookbookDa = !!document.querySelector(".cookbook");
    raus.hinweis   = !!document.querySelector(".cb-hint");
    raus.chips     = Array.prototype.map.call(
      document.querySelectorAll("#cb-filters button"),
      function (b) { return b.dataset.f + (b.getAttribute("aria-pressed") === "true" ? "*" : ""); }).join(" ");
    raus.karten    = document.querySelectorAll("#cb-groups .rcard").length;
    raus.koepfe    = document.querySelectorAll("#cb-groups .cathead").length;
    raus.klappbar  = document.querySelectorAll("#cb-groups button.cathead").length;
    raus.starr     = document.querySelectorAll("#cb-groups .cathead.static").length;
    raus.carets    = document.querySelectorAll("#cb-groups .caret").length;
    // Aufgeklappt zaehlen, nachdem eine Kategorie angetippt wurde - das ist die eigentliche
    // Frage von Paket 2.2: Bleibt das Klappen bei aktivem Chip bedienbar?
    var k1 = document.querySelector("#cb-groups button.cathead");
    if (k1) { k1.click(); raus.nachKlick = document.querySelectorAll("#cb-groups .rcard").length; }
    // Und derselbe Blick, nachdem ein Chip von HAND angetippt wurde. Das ist die Gegenprobe
    // fuer Paket 2.2: Im alten Stand schaltete jeder aktive Filter die Kopfzeilen auf
    // .static um (kein Caret, kein Knopf) - dort muss der Test rot sein.
    var chip = document.querySelector("#cb-filters button");
    if (chip) {
      chip.click();
      raus.chipAktiv   = chip.getAttribute("aria-pressed") === "true";
      raus.koepfeChip  = document.querySelectorAll("#cb-groups .cathead").length;
      raus.klappChip   = document.querySelectorAll("#cb-groups button.cathead").length;
      raus.starrChip   = document.querySelectorAll("#cb-groups .cathead.static").length;
    }
  } catch (e) { raus.messfehler = e.message; }
  raus.fehler = (window.__fehler || []).join(" || ") || "keine";
  var p = document.createElement("pre");
  p.id = "messung"; p.textContent = JSON.stringify(raus);
  document.documentElement.appendChild(p);
}, 300);</script>'''

    # NICHT "<head>": index.html hat gar kein head-Tag, und der einzige Treffer dafuer
    # steht in einem JS-Kommentar - dort eingesetzt zerschlaegt das Script den Block.
    # Nach dem charset-Meta und nicht davor (1024-Byte-Grenze der Zeichensatzangabe).
    if seite.count(ANKER) != 1: raise SystemExit("charset-Meta nicht genau einmal gefunden.")
    seite = seite.replace(ANKER, ANKER + seed, 1)
    seite = seite.replace("</html>", mess + "</html>", 1)

    tmp = tempfile.mkdtemp(prefix="cb-ansicht-")
    try:
        ziel = os.path.join(tmp, "index.html")
        io.open(ziel, "w", encoding="utf-8").write(seite)
        dump = os.path.join(tmp, "dump.html")
        with io.open(dump, "wb") as f:
            subprocess.call([
                EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=9000",
                "--user-data-dir=" + os.path.join(tmp, "profil"),
                "--dump-dom", "file:///" + ziel.replace("\\", "/")
            ], stdout=f, stderr=subprocess.PIPE)
        roh = io.open(dump, encoding="utf-8", errors="replace").read()
        m = re.search(r'<pre id="messung">(.*?)</pre>', roh, re.S)
        if not m:
            print(u"  %s: KEINE MESSUNG - der Pruefstand selbst ist kaputt." % was)
            return None
        # &quot; & Co. zuruecknehmen: textContent landet HTML-escaped im Abzug.
        text = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">"))
        return json.loads(text)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


ok = bad = 0
def pruef(name, bedingung, zusatz=""):
    global ok, bad
    if bedingung:
        ok += 1; print(u"  OK      " + name)
    else:
        bad += 1; print(u"  FEHLER  " + name + (u"  ->  " + zusatz if zusatz else ""))

BASIS_GOAL = {"kcal": 2200, "carbs": 220, "protein": 160, "fat": 65,
              "sex": "m", "age": 34, "height": 182, "weight": 88,
              "activity": "pal16", "mode": "lose", "pace": "moderate", "training": {}}

print(u"--- Ohne Ernaehrungsprofil ---")
a = lauf(dict(BASIS_GOAL), u"alles")
if a:
    pruef(u"kein JS-Fehler beim Start", a["fehler"] == "keine", a["fehler"])
    pruef(u"der Reiter Rezeptbuch existiert", a["reiterDa"])
    pruef(u"die Katalogansicht steht tatsaechlich im DOM", a["cookbookDa"])
    pruef(u"der alte Hinweistext .cb-hint ist weg", not a["hinweis"])
    pruef(u"kein Chip ist vorbelegt", "*" not in a["chips"], a["chips"])
    pruef(u"es gibt ueberhaupt Chips zum Antippen", len(a["chips"]) > 0, a["chips"])
    pruef(u"alle Kategorien starten eingeklappt (0 Karten)", a["karten"] == 0, str(a["karten"]))
    pruef(u"jede Kopfzeile ist ein Knopf", a["klappbar"] == a["koepfe"],
          u"%s von %s" % (a["klappbar"], a["koepfe"]))
    pruef(u"ein Klick klappt auf", a.get("nachKlick", 0) > 0, str(a.get("nachKlick")))
    pruef(u"ein von Hand gesetzter Chip greift", a.get("chipAktiv") is True)
    pruef(u"und laesst die Kopfzeilen Knoepfe bleiben",
          a.get("klappChip") == a.get("koepfeChip") and a.get("starrChip") == 0,
          u"Knoepfe %s von %s, starr %s" % (a.get("klappChip"), a.get("koepfeChip"), a.get("starrChip")))

print(u"")
print(u"--- Mit Profil vegetarisch + glutenfrei ---")
g = dict(BASIS_GOAL); g["diet"] = "vegetarisch"; g["avoid"] = ["glutenfrei"]
b = lauf(g, u"vegetarisch")
if b:
    pruef(u"kein JS-Fehler beim Start", b["fehler"] == "keine", b["fehler"])
    # Genau hier stand der alte Hinweis "Passend zu deiner Auswahl ..." - dieser Lauf ist
    # der einzige, in dem seine Abwesenheit ueberhaupt etwas beweist.
    pruef(u"auch mit Profil kein .cb-hint", not b["hinweis"])
    pruef(u"der Chip vegetarisch ist gedrueckt", "tag:vegetarisch*" in b["chips"], b["chips"])
    pruef(u"der Chip glutenfrei ist gedrueckt", "tag:glutenfrei*" in b["chips"], b["chips"])
    # Der Kern von Paket 2.2: Ein aktiver Chip darf die Klappmechanik nicht abschalten.
    pruef(u"trotz aktivem Chip ist jede Kopfzeile ein Knopf", b["klappbar"] == b["koepfe"],
          u"%s von %s" % (b["klappbar"], b["koepfe"]))
    pruef(u"keine starre Kopfzeile", b["starr"] == 0, str(b["starr"]))
    pruef(u"jede Kopfzeile traegt ein Caret", b["carets"] == b["koepfe"],
          u"%s von %s" % (b["carets"], b["koepfe"]))
    pruef(u"ein Klick klappt auch gefiltert auf", b.get("nachKlick", 0) > 0, str(b.get("nachKlick")))
    if a:
        pruef(u"gefiltert stehen weniger Kategorien da als ungefiltert",
              b["koepfe"] <= a["koepfe"], u"%s vs. %s" % (b["koepfe"], a["koepfe"]))

print(u"")
print(u"FEHLGESCHLAGEN: %d von %d" % (bad, ok + bad) if bad else u"Alle %d Pruefungen gruen." % ok)
sys.exit(1 if bad else 0)
