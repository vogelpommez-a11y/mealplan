# -*- coding: utf-8 -*-
u"""
Punkt 1 der Alltagsbefunde: Bleiben die Naehrwerte im Wochenplan nach dem Bearbeiten stehen?

Gemessen wird NICHT, wie oft render() laeuft (die Funktion lebt im IIFE und ist von aussen
nicht patchbar), sondern die Zahl, um die es dem Nutzer geht: die Tageskalorien im Wochenplan.

Ablauf je Lauf - genau der Weg, den ein Mensch nimmt:
  Plan-Reiter -> Slot antippen -> "Bearbeiten" -> kcal aendern -> schliessen -> Zahl ablesen

Drei Faelle, und der zweite und dritte sind die Gegenproben:
  A  Wochenplan, kcal geaendert   -> die Zahl MUSS sich mitbewegen
  B  Wochenplan, nichts geaendert -> die Zahl darf sich NICHT bewegen (sonst zeichnet die
     App bei jedem Blick in ein Meal den ganzen Reiter neu)
  C  Meals-Reiter, kcal geaendert -> die Karte MUSS die neue Zahl zeigen (dort lief das
     Teil-Repaint schon immer; es darf durch die Aenderung nicht kaputtgehen)

Gegenprobe gegen den Stand davor:
  git show HEAD:index.html > alt.html
  python tools/pruefstand-sheet-repaint.py alt.html     # Fall A MUSS dort rot sein

Aufruf:  python tools/pruefstand-sheet-repaint.py [pfad-zu-index.html]
"""
import io, json, os, re, subprocess, sys, tempfile, shutil

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ANKER = '<meta charset="utf-8">'   # index.html hat kein <head>-Tag, siehe TROUBLESHOOTING 109

GOAL = {"kcal": 2200, "carbs": 220, "protein": 160, "fat": 65, "sex": "m", "age": 34,
        "height": 182, "weight": 88, "activity": "pal16", "mode": "lose", "pace": "moderate",
        "training": {}}
# Die Zutaten sind BEWUSST gemischt: ein Freitext-String, ein Objekt mit eigener Einheit und
# eines mit vollen Naehrwerten. Grund (Befund des kvp-Agenten): mutateLocal() schreibt bei
# JEDEM commitNow() `target.ingredients = collectIngs()` - also den vollen Umweg
# Datensatz -> DOM -> rowData() -> zurueck. Mit einer leeren Zutatenliste lief Fall B durch,
# ohne diesen Umweg auch nur einmal zu belasten. Waere er nicht verlustfrei, gaelte jedes
# blosse Hineinsehen in ein Meal mit Zutaten als Aenderung - genau die Regression, die
# Fall B ausschliessen soll.
MEAL = {"id": "r1", "name": "Testgericht", "category": "Hauptgericht", "tags": [],
        "nutrition": {"kcal": 500, "carbs": 50, "protein": 30, "fat": 15},
        "steps": "Alles zusammen in die Pfanne und braten.",
        "ingredients": [
            "Salz und Pfeffer",
            {"name": "Milch 1,5 %", "grams": 300, "unit": "ml", "kcal": 64,
             "carbs": 4.8, "protein": 3.4, "fat": 3.5},
            {"name": "Haehnchenbrust", "grams": 150, "kcal": 165,
             "carbs": 0, "protein": 31, "fat": 3.6},
            {"name": "Banane", "grams": 120}
        ]}


def zustand(woche):
    # Das Meal liegt am Montag im Mittagsslot. Ein einziges Meal im Plan: dann ist die
    # Tagessumme identisch mit seinen kcal, und die Messung braucht keine Rechnung.
    plan = {"mon": {"fr": [], "mi": ["r1"], "ab": [], "sn": []}}
    for tag in ["tue", "wed", "thu", "fri", "sat", "sun"]:
        plan[tag] = {"fr": [], "mi": [], "ab": [], "sn": []}
    return {"recipes": [dict(MEAL)], "plans": {woche: plan}, "goal": GOAL, "onboarded": True,
            "tab": "plan", "favs": [], "planned": {}, "shopPersons": 1, "viewWeek": "cur"}


# Der Messcode. `fall` steuert, welcher der drei Wege gelaufen wird.
MESS = u'''<script>
function warte(bed, ms) {
  return new Promise(function (fertig, schief) {
    var bis = Date.now() + (ms || 6000);
    (function tick() {
      var w; try { w = bed(); } catch (e) { w = false; }
      if (w) return fertig(w);
      if (Date.now() > bis) return schief(new Error("Zeit abgelaufen: " + bed));
      setTimeout(tick, 50);
    })();
  });
}
// Die Tagesbilanz am Montag. Im Meals-Reiter stattdessen die Zahl auf der Meal-Karte.
//
// ".day-goals", NICHT ".day-nut": dayNutHtml() ersetzt die Textzeile durch die Balkenform,
// sobald ein Ziel gespeichert ist ("sonst staende alles doppelt") - und ein Ziel ist hier
// gesetzt, sonst gaebe es ueberhaupt keine Tagesbilanz. Mit .day-nut fand der erste Lauf
// nichts, und die Faelle A und B meldeten beide "(nicht gefunden)" - B waere damit still
// gruen durchgelaufen, obwohl gar nichts gemessen wurde.
function zahl(imBuch) {
  var el = imBuch ? document.querySelector("#r-groups .rcard .rstats")
                  : document.querySelector(".week .day .day-goals");
  return el ? el.textContent.replace(/\\s+/g, " ").trim() : "(nicht gefunden)";
}
setTimeout(async function () {
  var raus = { fall: "__FALL__" };
  try {
    var imMeals = raus.fall === "meals";
    document.querySelector('[data-tab="' + (imMeals ? "recipes" : "plan") + '"]').click();
    await warte(function () { return document.querySelector(imMeals ? "#r-groups .rcard" : ".week .day"); });
    raus.vorher = zahl(imMeals);

    // Das Meal oeffnen - im Wochenplan ueber die Slot-Karte, im Meals-Reiter ueber den Titel.
    var oeffner = document.querySelector(imMeals ? "#r-groups .rcard .rcard-open"
                                                : '.week [data-action="view"][data-id="r1"]');
    raus.oeffnerDa = !!oeffner;
    oeffner.click();
    await warte(function () { return document.querySelector(".mealsheet"); });

    // Jedes bestehende Meal oeffnet zuerst LESEND (Nachtrag Abnahme Phase 2) - erst der
    // Bearbeiten-Knopf baut das Formular auf.
    var edit = document.querySelector(".mealsheet [data-edit]");
    raus.editDa = !!edit;
    if (edit) edit.click();
    await warte(function () { return document.querySelector("#f-kcal"); });

    // Was steht direkt nach dem Aufbau im Feld? Trennt "updateMacroSum hat ueberschrieben"
    // von "irgendetwas anderes schreibt spaeter".
    raus.kcalFeldBeimOeffnen = document.querySelector("#f-kcal").value;
    raus.resetSichtbar = !document.querySelector("#f-nut-reset").hidden;
    if (raus.fall !== "nichts") {
      // Aendern wie ein Mensch: Wert setzen, dann die Ereignisse, an denen der Autosave haengt.
      var f = document.querySelector("#f-kcal");
      f.value = "900";
      f.dispatchEvent(new Event("input", { bubbles: true }));
      f.dispatchEvent(new Event("change", { bubbles: true }));
    }
    // render()-Detektor ohne Patchen: render() ersetzt view.innerHTML komplett. Eine Marke
    // an einem Knoten INNERHALB von view ueberlebt das nicht. Damit ist unterscheidbar, ob
    // gar nicht neu gezeichnet wurde oder ob neu gezeichnet und falsch gerechnet wurde.
    var marke = document.querySelector(imMeals ? "#r-groups" : ".week");
    if (marke) marke.setAttribute("data-marke", "1");
    // Schliessen ueber den echten Knopf, nicht ueber closeModal() - der Weg ist Teil der Sache.
    var zu = document.querySelector(".mealsheet [data-close]");
    raus.schliesserDa = !!zu;
    zu.click();
    await warte(function () { return !document.querySelector(".mealsheet"); }, 4000);
    // Die Exit-Bewegung laeuft noch, finishClose kommt erst danach.
    await new Promise(function (r) { setTimeout(r, 700); });
    raus.nachher = zahl(imMeals);
    var jetzt = document.querySelector(imMeals ? "#r-groups" : ".week");
    raus.neuGezeichnet = !!jetzt && jetzt.getAttribute("data-marke") !== "1";
    // Trennt "die Anzeige ist nur alt" von "die Zahl wird falsch gerechnet": Ein
    // Reiterwechsel zeichnet garantiert neu. Steht die Zahl DANACH richtig da, war es
    // wirklich das fehlende Neuzeichnen.
    try {
      document.querySelector('[data-tab="home"]').click();
      await new Promise(function (r) { setTimeout(r, 120); });
      document.querySelector('[data-tab="' + (imMeals ? "recipes" : "plan") + '"]').click();
      await new Promise(function (r) { setTimeout(r, 250); });
      raus.nachWechsel = zahl(imMeals);
    } catch (e) { raus.nachWechsel = "(Wechsel fehlgeschlagen: " + e.message + ")"; }
    // Was steht wirklich im Zustand? Trennt "Anzeige alt" von "gar nicht gespeichert".
    try {
      var roh = JSON.parse(localStorage.getItem("wochenkueche_v1__test") || "{}");
      var m = (roh.recipes || []).filter(function (r) { return r.id === "r1"; })[0];
      raus.gespeichert = m && m.nutrition ? m.nutrition.kcal : null;
    } catch (e) { raus.gespeichert = "(nicht lesbar)"; }
  } catch (e) { raus.messfehler = e.message; }
  raus.fehler = (window.__fehler || []).join(" || ") || "keine";
  var p = document.createElement("pre");
  p.id = "messung"; p.textContent = JSON.stringify(raus);
  document.documentElement.appendChild(p);
}, 400);
</script>'''


def lauf(fall, woche):
    seite = io.open(INDEX, encoding="utf-8").read()
    st = zustand(woche)
    seed = (u'<script>window.__fehler=[];'
            u'window.addEventListener("error",function(e){window.__fehler.push((e.message||"")+" @"+(e.lineno||"?"));});'
            u'try{["wochenkueche_v1","wochenkueche_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
            u'["wochenkueche_profile_v1","wochenkueche_profile_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
            u'}catch(e){}</script>' % (json.dumps(json.dumps(st)), json.dumps(json.dumps({"name": "Test"}))))
    if seite.count(ANKER) != 1:
        raise SystemExit("charset-Meta nicht genau einmal gefunden.")
    seite = seite.replace(ANKER, ANKER + seed, 1)
    seite = seite.replace("</html>", MESS.replace("__FALL__", fall) + "</html>", 1)

    tmp = tempfile.mkdtemp(prefix="sheet-repaint-")
    try:
        ziel = os.path.join(tmp, "index.html")
        io.open(ziel, "w", encoding="utf-8").write(seite)
        dump = os.path.join(tmp, "dump.html")
        with io.open(dump, "wb") as f:
            subprocess.call([
                EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=15000",
                "--user-data-dir=" + os.path.join(tmp, "profil"),
                "--dump-dom", "file:///" + ziel.replace("\\", "/")
            ], stdout=f, stderr=subprocess.PIPE)
        roh = io.open(dump, encoding="utf-8", errors="replace").read()
        m = re.search(r'<pre id="messung">(.*?)</pre>', roh, re.S)
        if not m:
            return {"messfehler": "KEINE MESSUNG - der Pruefstand selbst ist kaputt."}
        text = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">"))
        return json.loads(text)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# Der Wochenschluessel muss der sein, den die App gerade als "aktuelle Woche" ansieht -
# sonst steht der Plan in einer Woche, die niemand sieht, und alle Zahlen sind leer.
def isoweek_key():
    import datetime
    d = datetime.date.today()
    jahr, woche, _ = d.isocalendar()
    return "%04d-W%02d" % (jahr, woche)


ok = bad = 0
def pruef(name, bed, zusatz=""):
    global ok, bad
    if bed: ok += 1; print(u"  OK      " + name)
    else:   bad += 1; print(u"  FEHLER  " + name + (u"  ->  " + zusatz if zusatz else ""))

WOCHE = isoweek_key()
print(u"Datei:  " + INDEX)
print(u"Woche:  " + WOCHE)
print(u"")

# ---- Fall A: Wochenplan, kcal geaendert ----
a = lauf("plan", WOCHE)
print(u"A  Wochenplan, kcal 500 -> 900")
print(u"   vorher %r" % (a.get("vorher"),))
print(u"   nachher %r" % (a.get("nachher"),))
print(u"   nach Reiterwechsel %r   gespeichert %r" % (a.get("nachWechsel"), a.get("gespeichert")))
print(u"   render() lief: %r   kcal-Feld beim Oeffnen: %r   Reset sichtbar: %r"
      % (a.get("neuGezeichnet"), a.get("kcalFeldBeimOeffnen"), a.get("resetSichtbar")))
if a.get("messfehler"): pruef(u"A: Messung lief durch", False, a["messfehler"])
pruef(u"A: kein JS-Fehler", a.get("fehler") == "keine", str(a.get("fehler")))
pruef(u"A: das Meal war ueber den Slot zu oeffnen", a.get("oeffnerDa") is True)
pruef(u"A: der Bearbeiten-Knopf war da", a.get("editDa") is True)
pruef(u"A: die Vorbedingung stimmt (500 kcal sichtbar)", "500" in (a.get("vorher") or ""), str(a.get("vorher")))
# Das ist der gemeldete Fehler.
pruef(u"A: der Zustand hat die Aenderung", a.get("gespeichert") == 900, str(a.get("gespeichert")))
pruef(u"A: und die ANZEIGE zieht mit", "900" in (a.get("nachher") or ""), str(a.get("nachher")))
pruef(u"A: es wurde tatsaechlich neu gezeichnet", a.get("neuGezeichnet") is True,
      str(a.get("neuGezeichnet")))
# Beweist, dass die Rechnung selbst stimmt - der Fehler war die Anzeige, nicht die Zahl.
pruef(u"A: ein Reiterwechsel liefert dasselbe", "900" in (a.get("nachWechsel") or ""),
      str(a.get("nachWechsel")))

# ---- Fall B: Wochenplan, nichts geaendert ----
print(u"")
b = lauf("nichts", WOCHE)
print(u"B  Wochenplan, nur geoeffnet und geschlossen")
print(u"   vorher %r   nachher %r   gespeichert %r" % (b.get("vorher"), b.get("nachher"), b.get("gespeichert")))
pruef(u"B: kein JS-Fehler", b.get("fehler") == "keine", str(b.get("fehler")))
pruef(u"B: die Zahl bleibt unveraendert", b.get("vorher") == b.get("nachher"),
      u"%r -> %r" % (b.get("vorher"), b.get("nachher")))
# Die eigentliche Gegenprobe: Es darf nicht nur dieselbe Zahl herauskommen, es darf gar
# nicht erst neu gezeichnet worden sein. Sonst waere "gleiche Zahl" ein Zufallstreffer.
pruef(u"B: und es wurde gar nicht erst neu gezeichnet", b.get("neuGezeichnet") is False,
      str(b.get("neuGezeichnet")))
pruef(u"B: und der Wert im Zustand auch", b.get("gespeichert") == 500, str(b.get("gespeichert")))

# ---- Fall C: Meals-Reiter, kcal geaendert ----
print(u"")
c = lauf("meals", WOCHE)
print(u"C  Meals-Reiter, kcal 500 -> 900")
print(u"   vorher %r   nachher %r   gespeichert %r" % (c.get("vorher"), c.get("nachher"), c.get("gespeichert")))
pruef(u"C: kein JS-Fehler", c.get("fehler") == "keine", str(c.get("fehler")))
pruef(u"C: die Vorbedingung stimmt (500 kcal auf der Karte)", "500" in (c.get("vorher") or ""), str(c.get("vorher")))
pruef(u"C: der Zustand hat die Aenderung", c.get("gespeichert") == 900, str(c.get("gespeichert")))
pruef(u"C: die Karte zeigt die neue Zahl", "900" in (c.get("nachher") or ""), str(c.get("nachher")))

print(u"")
print((u"FEHLGESCHLAGEN: %d von %d" % (bad, ok + bad)) if bad else (u"Alle %d Pruefungen gruen." % ok))
sys.exit(1 if bad else 0)
