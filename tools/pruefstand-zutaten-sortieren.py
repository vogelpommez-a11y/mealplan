# -*- coding: utf-8 -*-
u"""
Paket 3 der Alltagsbefunde: Zutaten per Ziehen sortieren.

Gemessen wird die Zahl, um die es geht - die REIHENFOLGE, die collectIngs() liefert und
mutateLocal() nach localStorage schreibt. Nicht ein Nachbau der Geste, sondern der echte
Weg durch die App: Meals-Reiter -> Karte -> Bearbeiten -> Zeile aufnehmen -> loslassen.

Die Geste selbst (echter Finger, echtes Scrollen) ist NICHT automatisiert pruefbar
(docs/TESTING.md) - hier laufen synthetische PointerEvents. Was dieser Pruefstand deshalb
NICHT beweist: dass sich das Ziehen gut anfuehlt, und NICHTS ueber das Mitscrollen des
Sheets - requestAnimationFrame feuert unter --headless=new genau einmal, der Autoscroll
kaeme hier also nie in Gang und jeder Fall dazu waere dauerhaft gruen, ohne etwas zu
messen. Dafuer gibt es tools/abnahme-zutaten-sortieren.py am echten Geraet.

ACHT FAELLE, davon vier Abwehr:
  griff      Anfasser antippen nimmt SOFORT auf, ziehen tauscht Zeile 1 und 2
  halten     ohne Anfasser erst nach 400 ms - vorher passiert nichts
  tastatur   Alt+Pfeil runter verschiebt und meldet die neue Position
  grenze     Alt+Pfeil hoch auf Position 1 tut nichts und speichert nichts
  wackeln    wer vor Ablauf der 400 ms wischt, scrollt - er sortiert NICHT
  loeschen   das Kreuz startet keine Geste (sonst waere Loeschen unerreichbar)
  einzeln    bei einer einzigen Zutat gibt es keine Reihenfolge und keine Aufnahme
  klick      der Klick nach dem Ziehen darf die Zeile nicht aufklappen

Dazu zaehlt jeder Fall die Schreibvorgaenge nach localStorage: eine Verschiebung schreibt
genau EINMAL, eine abgebrochene Geste GAR NICHT.

Gegenproben - ohne sie zaehlt kein Ergebnis:
  python tools/pruefstand-zutaten-sortieren.py alt/index.html    # alter Stand, MUSS durchfallen
  python tools/pruefstand-zutaten-sortieren.py --rueckbau wackel  # Wischabbruch ausgebaut
  python tools/pruefstand-zutaten-sortieren.py --rueckbau klick   # Klicksperre ausgebaut
  python tools/pruefstand-zutaten-sortieren.py --rueckbau griff   # Sofortaufnahme ausgebaut

Aufruf:  python tools/pruefstand-zutaten-sortieren.py [pfad-zu-index.html]
"""
import io, json, os, re, subprocess, sys, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ANKER = '<meta charset="utf-8">'   # index.html hat kein <head>-Tag, siehe TROUBLESHOOTING 109

RUECKBAU = None
args = [a for a in sys.argv[1:]]
if "--rueckbau" in args:
    i = args.index("--rueckbau")
    RUECKBAU = args[i + 1]
    del args[i:i + 2]
INDEX = os.path.abspath(args[0]) if args else os.path.join(BASIS, "index.html")

GOAL = {"kcal": 2200, "carbs": 220, "protein": 160, "fat": 65, "sex": "m", "age": 34,
        "height": 182, "weight": 88, "activity": "pal16", "mode": "lose", "pace": "moderate",
        "training": {}}
# Vier Zutaten, bewusst gemischt: ein reiner Freitext, eines mit eigener Einheit, zwei mit
# vollen Naehrwerten. mutateLocal() schreibt bei jedem commitNow() den vollen Umweg
# Datensatz -> DOM -> rowData() -> zurueck; eine gleichfoermige Liste wuerde verdecken,
# wenn dabei eine Bauform verloren geht.
ZUTATEN = [
    {"name": "Haehnchenbrust", "grams": 150, "kcal": 165, "carbs": 0, "protein": 31, "fat": 3.6},
    {"name": "Reis", "grams": 80, "kcal": 350, "carbs": 78, "protein": 7, "fat": 1},
    {"name": "Milch 1,5 %", "grams": 200, "unit": "ml", "kcal": 47, "carbs": 4.8, "protein": 3.4, "fat": 1.5},
    "Salz und Pfeffer",
]
MEAL = {"id": "r1", "name": "Testgericht", "category": "Hauptgericht", "tags": [],
        "nutrition": {"kcal": 500, "carbs": 50, "protein": 30, "fat": 15},
        "steps": "Alles zusammen in die Pfanne.", "ingredients": list(ZUTATEN)}
MEAL_EINZEL = dict(MEAL, ingredients=[dict(ZUTATEN[0])])


def zustand(einzeln):
    plan = {}
    for tag in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        plan[tag] = {"fr": [], "mi": [], "ab": [], "sn": []}
    meal = dict(MEAL_EINZEL if einzeln else MEAL)
    return {"recipes": [meal], "plans": {}, "goal": GOAL, "onboarded": True,
            "tab": "recipes", "favs": [], "planned": {}, "shopPersons": 1, "viewWeek": "cur"}


MESS = u'''<script>
function warte(bed, ms) {
  return new Promise(function (fertig, schief) {
    var bis = Date.now() + (ms || 6000);
    (function tick() {
      var w; try { w = bed(); } catch (e) { w = false; }
      if (w) return fertig(w);
      if (Date.now() > bis) return schief(new Error("Zeit abgelaufen"));
      setTimeout(tick, 40);
    })();
  });
}
function schlaf(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
// Die Reihenfolge, wie sie im DOM steht - genau das, was collectIngs() liest.
function folge() {
  return Array.prototype.map.call(document.querySelectorAll("#f-ings .ing-row"), function (r) {
    return r.querySelector(".ing-name").value;
  }).join("|");
}
// Was wirklich gespeichert wurde. Trennt "Anzeige verschoben" von "Daten verschoben".
function gespeichert() {
  try {
    var roh = JSON.parse(localStorage.getItem("wochenkueche_v1__test") || "{}");
    var m = (roh.recipes || []).filter(function (r) { return r.id === "r1"; })[0];
    if (!m || !m.ingredients) return "(nichts)";
    return m.ingredients.map(function (i) { return typeof i === "string" ? i : i.name; }).join("|");
  } catch (e) { return "(nicht lesbar)"; }
}
function zeiger(art, el, x, y) {
  el.dispatchEvent(new PointerEvent(art, { bubbles: true, cancelable: true, composed: true,
    pointerId: 1, pointerType: "touch", isPrimary: true, button: 0, buttons: art === "pointerup" ? 0 : 1,
    clientX: x, clientY: y }));
}
function mitte(el) { var b = el.getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + b.height / 2 }; }

setTimeout(async function () {
  var raus = { fall: "__FALL__" };
  try {
    document.querySelector('[data-tab="recipes"]').click();
    await warte(function () { return document.querySelector("#r-groups .rcard"); });
    document.querySelector("#r-groups .rcard .rcard-open").click();
    await warte(function () { return document.querySelector(".mealsheet"); });
    // Jedes bestehende Meal oeffnet zuerst LESEND - erst der Knopf baut das Formular auf.
    document.querySelector(".mealsheet [data-edit]").click();
    await warte(function () { return document.querySelector("#f-ings .ing-row .ing-name"); });
    await schlaf(150);

    var rows = document.querySelectorAll("#f-ings .ing-row");
    raus.zeilen = rows.length;
    raus.griffDa = !!document.querySelector("#f-ings .ing-grip");
    raus.vorher = folge();

    // Ab hier zaehlen, wie oft der Zustand geschrieben wird. Eine Verschiebung schreibt
    // genau einmal, eine abgebrochene Geste gar nicht.
    // Gezaehlt wird NUR, was aus commitNow() kommt. hydrateImages() schreibt denselben
    // Schluessel asynchron, sobald ein Bild nachgeladen ist - ohne diesen Filter zaehlte der
    // Pruefstand mal einen Schreibvorgang mehr, mal keinen, je nachdem wann das Bild fertig
    // war. Eine Messgroesse, die von einem Bild abhaengt, misst nicht die Reihenfolge.
    window.__schreib = 0; window.__spuren = [];
    var echt = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function (k, v) {
      if (k === "wochenkueche_v1__test") {
        var spur = String((new Error()).stack || "").replace(/\\s+/g, " ");
        if (spur.indexOf("commitNow") >= 0) { window.__schreib++; window.__spuren.push(spur.slice(0, 400)); }
      }
      return echt(k, v);
    };

    var eins = rows[0], zwei = rows[1];
    var f = raus.fall;

    if (f === "nichts") {
      await schlaf(900);
    } else if (f === "tastatur" || f === "grenze") {
      var btn = rows[0].querySelector(".ing-view-name");
      btn.focus();
      await schlaf(80);
      window.__schreib = 0;   // erst ab hier zaehlt die Taste, nicht der Fokuswechsel
      btn.dispatchEvent(new KeyboardEvent("keydown", { bubbles: true, cancelable: true,
        key: f === "grenze" ? "ArrowUp" : "ArrowDown", altKey: true }));
      await schlaf(200);
      raus.schreibDurchAktion = window.__schreib;
      raus.live = (document.querySelector("#ms-ing-live") || {}).textContent || "";
      raus.fokusBleibt = document.activeElement === btn;
    } else if (f === "einzeln") {
      var p = mitte(eins.querySelector(".ing-view"));
      window.__schreib = 0;
      zeiger("pointerdown", eins, p.x, p.y);
      await schlaf(600);
      raus.sortierzustand = document.querySelector("#f-ings").classList.contains("ings-sorting");
      zeiger("pointerup", eins, p.x, p.y);
      await schlaf(150);
      raus.schreibDurchAktion = window.__schreib;
    } else if (f === "loeschen") {
      var del = eins.querySelector(".ing-view-del");
      var d = mitte(del);
      window.__schreib = 0;
      zeiger("pointerdown", del, d.x, d.y);
      await schlaf(600);
      raus.sortierzustand = document.querySelector("#f-ings").classList.contains("ings-sorting");
      zeiger("pointerup", del, d.x, d.y);
      await schlaf(150);
      raus.schreibDurchAktion = window.__schreib;
    } else {
      // Ziehen: Zeile 1 an Position 2. Der Weg ist der Abstand der beiden Zeilenmitten.
      var start = mitte(eins.querySelector(".ing-view"));
      var weg = mitte(zwei.querySelector(".ing-view")).y - start.y + 2;
      var ziel = f === "griff" ? eins.querySelector(".ing-grip") : eins.querySelector(".ing-view");
      window.__schreib = 0;
      zeiger("pointerdown", ziel, start.x, start.y);
      if (f === "griff") {
        // Der Anfasser nimmt SOFORT auf - ohne Warten.
        raus.sofortAufgenommen = eins.classList.contains("dragging");
      } else if (f === "wackeln") {
        // Vor Ablauf der Haltezeit wischen: das ist Scrollen, kein Sortieren.
        zeiger("pointermove", eins, start.x, start.y + 30);
        await schlaf(600);
        raus.sortierzustand = document.querySelector("#f-ings").classList.contains("ings-sorting");
      } else {
        raus.vorAblauf = eins.classList.contains("dragging");
        await schlaf(500);
        raus.nachAblauf = eins.classList.contains("dragging");
      }
      if (f !== "wackeln") {
        zeiger("pointermove", eins, start.x, start.y + weg / 2);
        await schlaf(60);
        zeiger("pointermove", eins, start.x, start.y + weg);
        await schlaf(60);
        raus.nachbarWeicht = (zwei.style.transform || "").indexOf("translateY(-") === 0;
        raus.sortierzustand = document.querySelector("#f-ings").classList.contains("ings-sorting");
      }
      zeiger("pointerup", eins, start.x, start.y + (f === "wackeln" ? 30 : weg));
      await schlaf(200);
      raus.schreibDurchAktion = window.__schreib;
      // Der Klick, den ein echtes Geraet nach dem Loslassen nachschiebt, darf die Zeile
      // nicht aufklappen.
      eins.querySelector(".ing-view-name").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
      await schlaf(120);
      raus.zeileOffen = eins.classList.contains("editing");
      // Gegenstueck: der NAECHSTE Tipp ist ein gewollter und muss ankommen. Eine Sperre, die
      // mehr als den Ersatzklick schluckt, machte die Zeile nach jedem Sortieren unbedienbar.
      eins.querySelector(".ing-view-name").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
      await schlaf(120);
      raus.zweiterKlickOeffnet = eins.classList.contains("editing");
      raus.transformWeg = !eins.style.transform && !zwei.style.transform;
      raus.klasseWeg = !eins.classList.contains("dragging")
        && !document.querySelector("#f-ings").classList.contains("ings-sorting");
    }

    await schlaf(150);
    raus.nachher = folge();
    raus.schreib = window.__schreib;
    raus.spuren = window.__spuren;
    raus.gespeichert = gespeichert();
  } catch (e) { raus.messfehler = e.message; }
  raus.fehler = (window.__fehler || []).join(" || ") || "keine";
  var p = document.createElement("pre");
  p.id = "messung"; p.textContent = JSON.stringify(raus);
  document.documentElement.appendChild(p);
}, 400);
</script>'''


# ---- Gezielte Rueckbauten des ECHTEN Codes. Jeder darf genau einen Fall rot machen. ----
RUECKBAUTEN = {
    "wackel": ('if (Math.hypot(e.clientX - dg.startX, e.clientY - dg.startY) > WACKEL) dgAbbrechen();',
               '/* rueckgebaut */'),
    "klick": ('if (!dgKlickSperre) return;\n      dgKlickSperre = false;\n      e.stopPropagation(); e.preventDefault();',
              'return;'),
    "griff": ('if (e.target.closest(".ing-grip")) dgAufnehmen();\n      else dg.timer = setTimeout(dgAufnehmen, HALTEN_MS);',
              'dg.timer = setTimeout(dgAufnehmen, HALTEN_MS);'),
}


def lauf(fall, einzeln=False):
    seite = pm_quelle.lade_seite(INDEX)
    if RUECKBAU:
        if RUECKBAU not in RUECKBAUTEN:
            raise SystemExit("Unbekannter Rueckbau: " + RUECKBAU)
        alt, neu = RUECKBAUTEN[RUECKBAU]
        if seite.count(alt) != 1:
            raise SystemExit("Rueckbau '%s' fand seine Stelle nicht genau einmal (%d) - "
                             "der Pruefstand wuerde sonst still gegen unveraenderten Code messen."
                             % (RUECKBAU, seite.count(alt)))
        seite = seite.replace(alt, neu, 1)
    st = zustand(einzeln)
    seed = (u'<script>window.__fehler=[];'
            u'window.addEventListener("error",function(e){window.__fehler.push((e.message||"")+" @"+(e.lineno||"?"));});'
            u'try{["wochenkueche_v1","wochenkueche_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
            u'["wochenkueche_profile_v1","wochenkueche_profile_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
            u'}catch(e){}</script>' % (json.dumps(json.dumps(st)), json.dumps(json.dumps({"name": "Test"}))))
    if seite.count(ANKER) != 1:
        raise SystemExit("charset-Meta nicht genau einmal gefunden.")
    seite = seite.replace(ANKER, ANKER + seed, 1)
    seite = seite.replace("</html>", MESS.replace("__FALL__", fall) + "</html>", 1)

    tmp = tempfile.mkdtemp(prefix="ing-sort-")
    try:
        ziel = os.path.join(tmp, "index.html")
        io.open(ziel, "w", encoding="utf-8").write(seite)
        dump = os.path.join(tmp, "dump.html")
        with io.open(dump, "wb") as f:
            subprocess.call([
                EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=20000",
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


AUSGANG = "Haehnchenbrust|Reis|Milch 1,5 %|Salz und Pfeffer"
GETAUSCHT = "Reis|Haehnchenbrust|Milch 1,5 %|Salz und Pfeffer"


def main():
    print("Pruefstand Zutaten sortieren (Paket 3)")
    print("Quelle: " + os.path.relpath(INDEX, BASIS).replace("\\", "/")
          + (("  [Rueckbau: " + RUECKBAU + "]") if RUECKBAU else ""))
    print("")

    faelle = ["nichts", "griff", "halten", "tastatur", "grenze", "wackeln", "loeschen", "einzeln", "klick"]
    ergebnisse = {}
    for f in faelle:
        ergebnisse[f] = lauf(f, einzeln=(f == "einzeln"))

    pruefungen = []

    def p(was, ist, soll):
        pruefungen.append((was, ist == soll, ist, soll))

    # --- Aufbau: ohne den Anfasser misst alles Weitere nichts ---
    g = ergebnisse["griff"]
    p("Der Anfasser steckt in der Zeile", g.get("griffDa"), True)
    p("Vier Zutaten im Formular", g.get("zeilen"), 4)
    p("Ausgangsreihenfolge stimmt", g.get("vorher"), AUSGANG)

    # --- griff: der Anfasser nimmt sofort auf ---
    p("Anfasser nimmt SOFORT auf", g.get("sofortAufgenommen"), True)
    p("Der Nachbar weicht nach oben", g.get("nachbarWeicht"), True)
    p("Griff: Reihenfolge getauscht", g.get("nachher"), GETAUSCHT)
    p("Griff: auch gespeichert", g.get("gespeichert"), GETAUSCHT)
    p("Griff: genau EIN Schreibvorgang", g.get("schreibDurchAktion"), 1)
    p("Griff: Schwebezustand aufgeraeumt", g.get("klasseWeg"), True)
    p("Griff: keine Transformation zurueckgeblieben", g.get("transformWeg"), True)

    # --- halten: ohne Anfasser erst nach 400 ms ---
    h = ergebnisse["halten"]
    p("Halten: vor Ablauf NICHT aufgenommen", h.get("vorAblauf"), False)
    p("Halten: nach Ablauf aufgenommen", h.get("nachAblauf"), True)
    p("Halten: Reihenfolge getauscht", h.get("nachher"), GETAUSCHT)
    p("Halten: auch gespeichert", h.get("gespeichert"), GETAUSCHT)
    p("Halten: genau EIN Schreibvorgang", h.get("schreibDurchAktion"), 1)

    # --- klick: der Klick nach dem Ziehen oeffnet die Zeile nicht ---
    k = ergebnisse["klick"]
    p("Klick nach dem Ziehen oeffnet NICHT", k.get("zeileOffen"), False)
    p("Der zweite, gewollte Tipp oeffnet wieder", k.get("zweiterKlickOeffnet"), True)
    p("Klick-Fall: Reihenfolge trotzdem getauscht", k.get("nachher"), GETAUSCHT)

    # --- tastatur ---
    t = ergebnisse["tastatur"]
    p("Alt+Pfeil runter verschiebt", t.get("nachher"), GETAUSCHT)
    p("Tastatur: auch gespeichert", t.get("gespeichert"), GETAUSCHT)
    p("Tastatur: genau EIN Schreibvorgang", t.get("schreibDurchAktion"), 1)
    p("Tastatur: Position wird angesagt", t.get("live"), "Haehnchenbrust: Position 2 von 4")
    p("Tastatur: Fokus bleibt auf der Zeile", t.get("fokusBleibt"), True)

    # --- Abwehr: die vier Faelle, in denen NICHTS passieren darf ---
    for name, titel in (("grenze", "Alt+Pfeil hoch an Position 1"),
                        ("wackeln", "Wischen vor Ablauf der Haltezeit"),
                        ("loeschen", "Druck auf das Loeschkreuz"),
                        ("einzeln", "Geste bei einer einzigen Zutat")):
        r = ergebnisse[name]
        p(titel + ": Reihenfolge unveraendert", r.get("nachher"),
          ZUTATEN[0]["name"] if name == "einzeln" else AUSGANG)
        p(titel + ": KEIN Schreibvorgang", r.get("schreibDurchAktion"), 0)
        if "sortierzustand" in r:
            p(titel + ": keine Aufnahme", r.get("sortierzustand"), False)

    # --- Ausgabe ---
    breit = max(len(x[0]) for x in pruefungen)
    rot = 0
    for was, ok, ist, soll in pruefungen:
        if ok:
            print("  OK    " + was)
        else:
            rot += 1
            print("  ROT   " + was.ljust(breit) + "   ist=" + repr(ist) + "  soll=" + repr(soll))
    print("")
    for f in faelle:
        r = ergebnisse[f]
        if r.get("messfehler"):
            print("  MESSFEHLER (%s): %s" % (f, r["messfehler"]))
            rot += 1
        if r.get("fehler") and r["fehler"] != "keine":
            print("  JS-FEHLER (%s): %s" % (f, r["fehler"]))
            rot += 1
    print("")
    print("ERGEBNIS %d gruen, %d rot  (%d Messgroessen)"
          % (len(pruefungen) - rot, rot, len(pruefungen)))
    return 1 if rot else 0


if __name__ == "__main__":
    sys.exit(main())
