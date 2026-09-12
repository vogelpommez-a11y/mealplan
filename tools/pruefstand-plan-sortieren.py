# -*- coding: utf-8 -*-
u"""Meals im Wochenplan per Ziehen sortieren.

Gemessen wird die Zahl, um die es geht - die REIHENFOLGE in state.plan, so wie sie nach
save() in localStorage steht. Nicht ein Nachbau der Geste, sondern der echte Weg durch die
App: Plan-Reiter -> Karte aufnehmen -> ziehen -> loslassen.

Die Geste selbst (echter Finger, echtes Scrollen) ist NICHT automatisiert pruefbar
(docs/TESTING.md) - hier laufen synthetische PointerEvents. Was dieser Pruefstand deshalb
NICHT beweist: dass sich das Ziehen gut anfuehlt, und NICHTS ueber das Mitscrollen der
Seite - requestAnimationFrame feuert unter --headless=new genau einmal, der Autoscroll
kaeme hier also nie in Gang und jeder Fall dazu waere dauerhaft gruen, ohne etwas zu
messen. Dafuer gibt es tools/abnahme-plan-sortieren.py am echten Geraet.

NEUN FAELLE, davon vier Abwehr:
  umsortieren  innerhalb eines Slots getauscht - und genau EINMAL gespeichert
  kategorie    von "ab" nach "fr" desselben Tages, der Eintrag wandert unveraendert
  frei         ein Fruehstuecks-Meal darf ins Abendessen (die Kategoriesperre ist weg)
  versteckt    ab dem vierten fremden Gericht blendet der Slot aus - der Zielindex
               darf sich davon nicht taeuschen lassen
  zurueck      Rueckgaengig stellt Slot UND Position exakt wieder her
  tippen       der Klick nach dem Ziehen oeffnet das Meal-Blatt NICHT
  wackeln      wer vor Ablauf der 400 ms wischt, sortiert NICHT
  ansehen      ohne Schreibrecht (Rolle "view") nimmt gar nichts auf
  ueberlauf    die Tageskarte laeuft waagerecht nicht ueber - sonst stirbt das Wischen
               zum Nachbartag (docs/TROUBLESHOOTING.md 58 und 61)

Dazu zaehlt jeder Fall die Schreibvorgaenge: eine Verschiebung schreibt genau EINMAL, eine
abgebrochene Geste GAR NICHT.

Gegenproben - ohne sie zaehlt kein Ergebnis:
  python tools/pruefstand-plan-sortieren.py --rueckbau versteckt  # Zielindex aus der DOM-Position
  python tools/pruefstand-plan-sortieren.py --rueckbau klick      # Klicksperre ausgebaut
  python tools/pruefstand-plan-sortieren.py --rueckbau wackel     # Wischabbruch ausgebaut
  python tools/pruefstand-plan-sortieren.py --rueckbau ansehen    # Schreibrecht-Pruefung ausgebaut

Aufruf:  python tools/pruefstand-plan-sortieren.py [pfad-zu-index.html] [--rueckbau <name>]
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

# Vier Meals, damit ein Slot mehr als eine Karte traegt und das Umsortieren ueberhaupt eine
# Frage ist. Die Kategorien sind bewusst gemischt: "Fruehstueck" darf nach der alten Regel
# NUR in den fr-Slot - genau daran wird gemessen, dass die Sperre beim Ziehen gefallen ist.
MEALS = [
    {"id": "m1", "name": "Haehnchen mit Reis", "category": "Hauptgericht"},
    {"id": "m2", "name": "Lachs mit Brokkoli", "category": "Hauptgericht"},
    {"id": "m3", "name": "Chili sin Carne", "category": "Hauptgericht"},
    {"id": "m4", "name": "Porridge mit Beeren", "category": "Fruehstueck"},
]


def meal(m):
    return {"id": m["id"], "name": m["name"], "category": m["category"], "tags": [],
            "nutrition": {"kcal": 500, "carbs": 50, "protein": 30, "fat": 15},
            "steps": "Alles zusammen in die Pfanne.", "ingredients": ["Zutat"]}


def leerer_plan():
    plan = {}
    for tag in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        plan[tag] = {"fr": [], "mi": [], "ab": [], "sn": []}
    return plan


def zustand(fall):
    plan = leerer_plan()
    if fall == "versteckt":
        # Fuenf Eintraege im ab-Slot, die mittleren drei gehoeren jemand anderem. Ab dem
        # vierten FREMDEN blendet der Slot aus - hier sind es drei, also ist noch nichts
        # versteckt. Deshalb sechs: vier fremde, und der vierte verschwindet hinter
        # "+1 weitere". Genau dann weicht die Anzeigeposition vom echten Index ab.
        plan["mon"]["ab"] = [
            {"id": "m1", "uids": ["ich"]},
            {"id": "m2", "uids": ["fremd"]},
            {"id": "m3", "uids": ["fremd"]},
            {"id": "m4", "uids": ["fremd"]},
            {"id": "m1", "uids": ["fremd"]},
            {"id": "m2", "uids": ["ich"]},
        ]
    else:
        plan["mon"]["ab"] = ["m1", "m2", "m3"]
        plan["mon"]["fr"] = ["m4"] if fall in ("kategorie", "frei") else []
    st = {"recipes": [meal(m) for m in MEALS], "plans": {"__WOCHE__": plan}, "goal": GOAL,
          "onboarded": True, "tab": "plan", "favs": [], "planned": {},
          "shopPersons": 1, "viewWeek": "cur"}
    return st


# Die Rolle "view" entsteht aus syncGid und myRole - beides setzt erst eine echte
# Gruppenanmeldung, und die gibt es headless nicht. Der Fall baut sie deshalb an der einen
# Stelle nach, an der sie gelesen wird. Das ist AUFBAU, kein Rueckbau: geprueft wird, was
# der echte Code aus "nicht bearbeiten duerfen" macht - und genau das wird hier hergestellt.
AUFBAU_ANSEHEN = ('function canEdit() { return groupRole() !== "view"; }',
                  'function canEdit() { return false; }')

# ---- Gezielte Rueckbauten des ECHTEN Codes. Jeder darf genau einen Fall rot machen. ----
RUECKBAUTEN = {
    # Der Zielindex wieder aus der Position im Dokument statt aus data-slot-src - der
    # naheliegende Fehler, den die versteckten Karten aufdecken. Zurueckgebaut wird die
    # GANZE Regel, nicht nur die Schleife: wer ans Ende zieht, laeuft ueber den zweiten
    # Rueckgabeweg, und ein Rueckbau nur der Schleife waere dort wirkungslos geblieben.
    "versteckt": ('    for (let n = karte.nextElementSibling; n; n = n.nextElementSibling) {\n'
                  '      if (!n.classList.contains("filled") || !n.dataset.slotSrc) continue;\n'
                  '      return Number(n.dataset.slotSrc.split(":")[2]);\n'
                  '    }\n'
                  '    return laenge;',
                  '    return Array.prototype.indexOf.call(slot.querySelectorAll(".filled"), karte);'),
    "klick": ('if (!dgKlickSperre) return;\n      dgKlickSperre = false;\n      e.stopPropagation(); e.preventDefault();',
              'return;'),
    "wackel": ('if (Math.hypot(e.clientX - dg.startX, e.clientY - dg.startY) > WACKEL) dgAbbrechen();',
               '/* rueckgebaut */'),
    "ansehen": ('darfGreifen: () => canEdit(),', 'darfGreifen: () => true,'),
}

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
function tagEl() { return document.querySelector('.week > .day'); }
function slotEl(k) { return document.querySelector('.slot[data-slot="mon:' + k + '"]'); }
function karten(k) { return Array.prototype.slice.call(slotEl(k).querySelectorAll(".filled")); }
// Die Namen in der Reihenfolge, in der sie im Slot STEHEN - die Anzeige.
function folge(k) {
  return karten(k).map(function (c) { return c.querySelector(".r-name").textContent; }).join("|");
}
// Was wirklich gespeichert wurde. Trennt "Anzeige verschoben" von "Daten verschoben".
function gespeichert(k) {
  try {
    var roh = JSON.parse(localStorage.getItem("wochenkueche_v1__test") || "{}");
    var w = roh.plans || {};
    var erste = Object.keys(w)[0];
    if (!erste) return "(keine Woche)";
    var liste = (w[erste].mon || {})[k] || [];
    return liste.map(function (e) { return typeof e === "string" ? e : e.id; }).join("|");
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
    document.querySelector('[data-tab="plan"]').click();
    await warte(function () { return document.querySelector('.slot[data-slot="mon:ab"] .filled'); });
    await schlaf(200);

    raus.vorherAb = folge("ab");
    raus.vorherFr = folge("fr");
    raus.griffDa = !!document.querySelector('.slot[data-slot="mon:ab"] .pm-grip');
    // Waagerechter Ueberlauf der Tageskarte: sechs unsichtbare Pixel haben hier schon
    // einmal die Wischgeste zum Nachbartag ausgeschaltet.
    var tg = tagEl();
    raus.quer = tg ? (tg.scrollWidth - tg.clientWidth) : -1;
    var wk = document.querySelector(".week");
    raus.querWeek = wk ? (wk.scrollWidth - wk.clientWidth) : -1;

    // Ab hier zaehlen, wie oft der Zustand geschrieben wird.
    // Gezaehlt wird NUR der eigene Speichervorgang des Ablegens. Zwei Dinge schreiben
    // denselben Schluessel sonst mit: hydrateImages(), sobald ein Bild nachgeladen ist -
    // eine Messgroesse, die von einem Bild abhaengt, misst nicht die Reihenfolge - und
    // render() selbst, das seit jeher mit save() endet. Letzteres ist kein Fehler, sondern
    // der normale Weg jeder Plan-Aenderung; gemessen werden soll hier aber, dass das
    // Ablegen EINMAL schreibt und eine abgebrochene Geste GAR NICHT.
    window.__schreib = 0;
    var echt = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function (k, v) {
      if (k === "wochenkueche_v1__test") {
        var spur = String((new Error()).stack || "").replace(/\\s+/g, " ");
        if (spur.indexOf("abgelegt") >= 0 && spur.indexOf("at render") < 0) window.__schreib++;
      }
      return echt(k, v);
    };

    var f = raus.fall;
    var ab = karten("ab");

    if (f === "ueberlauf") {
      await schlaf(300);
    } else if (f === "wackeln") {
      // Aufsetzen und sofort wischen: das gehoert dem Blaettern, nicht dem Sortieren.
      var p = mitte(ab[0]);
      zeiger("pointerdown", ab[0], p.x, p.y);
      await schlaf(60);
      zeiger("pointermove", ab[0], p.x + 40, p.y + 3);
      await schlaf(500);
      raus.sortierzustand = document.body.querySelector("#view").classList.contains("plan-sorting");
      zeiger("pointerup", ab[0], p.x + 40, p.y + 3);
      await schlaf(200);
    } else if (f === "ansehen") {
      // Halten, wie es sonst aufnehmen wuerde - ohne Schreibrecht darf nichts passieren.
      var p = mitte(ab[0]);
      zeiger("pointerdown", ab[0], p.x, p.y);
      await schlaf(600);
      raus.sortierzustand = document.querySelector("#view").classList.contains("plan-sorting");
      zeiger("pointerup", ab[0], p.x, p.y);
      await schlaf(200);
    } else if (f === "tippen") {
      // Ziehen, loslassen - und der Ersatzklick darf das Meal-Blatt nicht oeffnen.
      //
      // Der Klick geht bewusst an das Element UNTER dem Finger, nicht an die alte
      // Kartenreferenz: Das Ablegen zeichnet den Reiter sofort neu, die aufgenommene Karte
      // ist danach nicht mehr im Dokument, und ein Klick auf einen losgeloesten Knoten
      // erreicht die Sperre gar nicht. Er waere immer folgenlos - der Fall waere dauerhaft
      // gruen, ohne etwas zu messen. Genau das hat die Gegenprobe am 12.09.2026 gezeigt.
      var a = mitte(ab[0]), b = mitte(ab[1]);
      zeiger("pointerdown", ab[0], a.x, a.y);
      await schlaf(520);
      zeiger("pointermove", ab[0], a.x, b.y + 4);
      await schlaf(80);
      zeiger("pointerup", ab[0], a.x, b.y + 4);
      var unterFinger = document.elementFromPoint(a.x, b.y + 4);
      raus.trefferDa = !!(unterFinger && unterFinger.closest(".filled"));
      if (unterFinger) unterFinger.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
      await schlaf(400);
      raus.blattOffen = !!document.querySelector(".mealsheet");
      // Und der ZWEITE, gewollte Tipp oeffnet wieder.
      var jetzt = karten("ab");
      jetzt[0].dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
      await schlaf(400);
      raus.blattOffenDanach = !!document.querySelector(".mealsheet");
    } else if (f === "kategorie" || f === "frei") {
      // Von "ab" nach "fr" desselben Tages ziehen. Bei "frei" ist es ein Fruehstueck, das
      // den umgekehrten Weg nimmt - nach der alten Regel war das gesperrt.
      var quelle = (f === "frei") ? karten("fr")[0] : ab[0];
      var zielSlot = slotEl(f === "frei" ? "ab" : "fr");
      var a = mitte(quelle), z = mitte(zielSlot);
      zeiger("pointerdown", quelle, a.x, a.y);
      await schlaf(520);
      raus.aufgenommen = quelle.classList.contains("dragging");
      zeiger("pointermove", quelle, z.x, z.y);
      await schlaf(120);
      raus.zielMarkiert = zielSlot.classList.contains("dragover");
      zeiger("pointerup", quelle, z.x, z.y);
      await schlaf(400);
    } else if (f === "zurueck") {
      var a = mitte(ab[0]), b = mitte(ab[1]);
      zeiger("pointerdown", ab[0], a.x, a.y);
      await schlaf(520);
      zeiger("pointermove", ab[0], a.x, b.y + 4);
      await schlaf(80);
      zeiger("pointerup", ab[0], a.x, b.y + 4);
      await schlaf(350);
      raus.nachZug = gespeichert("ab");
      var knopf = document.querySelector("#toast .toast-undo");
      raus.knopfDa = !!knopf;
      if (knopf) knopf.click();
      await schlaf(350);
    } else if (f === "versteckt") {
      // Die erste Karte ans Ende der SICHTBAREN Liste ziehen. Genau hier laufen Anzeige
      // und Wirklichkeit auseinander: hinter der letzten sichtbaren stehen noch drei
      // versteckte. Wer die Anzeigeposition nimmt, setzt die Karte auf Index 3 und
      // ueberholt damit die Versteckten; richtig ist das Ende des Arrays.
      // Ein Zug auf Platz zwei wuerde das NICHT zeigen - dort ist die Anzeigeposition
      // zufaellig gleich dem echten Index, und die Gegenprobe bliebe gruen.
      var a = mitte(ab[0]), b = mitte(ab[ab.length - 1]);
      zeiger("pointerdown", ab[0], a.x, a.y);
      await schlaf(520);
      raus.aufgenommen = ab[0].classList.contains("dragging");
      zeiger("pointermove", ab[0], a.x, b.y + 6);
      await schlaf(120);
      zeiger("pointerup", ab[0], a.x, b.y + 6);
      await schlaf(400);
    } else {
      // "umsortieren": die erste Karte unter die zweite ziehen.
      var a = mitte(ab[0]), b = mitte(ab[1]);
      zeiger("pointerdown", ab[0], a.x, a.y);
      await schlaf(520);
      raus.aufgenommen = ab[0].classList.contains("dragging");
      raus.sortierzustand = document.querySelector("#view").classList.contains("plan-sorting");
      zeiger("pointermove", ab[0], a.x, b.y + 4);
      await schlaf(120);
      zeiger("pointerup", ab[0], a.x, b.y + 4);
      await schlaf(400);
    }

    raus.schreibDurchAktion = window.__schreib;
    raus.nachherAb = folge("ab");
    raus.nachherFr = folge("fr");
    raus.gespeichertAb = gespeichert("ab");
    raus.gespeichertFr = gespeichert("fr");
    raus.live = (document.getElementById("plan-sort-live") || {}).textContent || "";
  } catch (e) {
    raus.messfehler = String(e && e.message || e);
  }
  var pre = document.createElement("pre");
  pre.id = "messung";
  pre.textContent = JSON.stringify(raus);
  document.body.appendChild(pre);
}, 1200);
</script>'''


def lauf(fall):
    seite = pm_quelle.lade_seite(INDEX)
    if fall == "ansehen":
        alt, neu = AUFBAU_ANSEHEN
        if seite.count(alt) != 1:
            raise SystemExit("Der Aufbau fuer 'ansehen' fand canEdit() nicht genau einmal (%d)."
                             % seite.count(alt))
        seite = seite.replace(alt, neu, 1)
    if RUECKBAU:
        if RUECKBAU not in RUECKBAUTEN:
            raise SystemExit("Unbekannter Rueckbau: " + RUECKBAU)
        alt, neu = RUECKBAUTEN[RUECKBAU]
        if seite.count(alt) != 1:
            raise SystemExit("Rueckbau '%s' fand seine Stelle nicht genau einmal (%d) - "
                             "der Pruefstand wuerde sonst still gegen unveraenderten Code messen."
                             % (RUECKBAU, seite.count(alt)))
        seite = seite.replace(alt, neu, 1)

    st = zustand(fall)
    # Der Wochenschluessel muss der sein, den die App fuer "diese Woche" bildet - sonst
    # legt sie einen leeren Plan an und der Pruefstand misst eine leere Seite.
    # Bewusst Ersetzung statt %-Formatierung: der ISO-Wochenschluessel rechnet mit Modulo,
    # und ein % im Vorlagentext waere dort als Formatzeichen gelesen worden.
    seed = (u'<script>(function(){'
            u'function iso(d){var t=new Date(d.getFullYear(),d.getMonth(),d.getDate());'
            u't.setDate(t.getDate()+3-((t.getDay()+6)%7));var e=new Date(t.getFullYear(),0,4);'
            u'var w=1+Math.round(((t-e)/86400000-3+((e.getDay()+6)%7))/7);'
            u'return t.getFullYear()+"-W"+(w<10?"0":"")+w;}'
            u'var st=__ZUSTAND__; var p=st.plans["__WOCHE__"]; delete st.plans["__WOCHE__"];'
            u'st.plans[iso(new Date())]=p;'
            u'try{["wochenkueche_v1","wochenkueche_v1__test"].forEach(function(k){localStorage.setItem(k, JSON.stringify(st));});'
            u'["wochenkueche_profile_v1","wochenkueche_profile_v1__test"].forEach(function(k){'
            u'localStorage.setItem(k, JSON.stringify({name:"Test"}));});}catch(e){}'
            u'})();</script>').replace("__ZUSTAND__", json.dumps(st))
    if seite.count(ANKER) != 1:
        raise SystemExit("charset-Meta nicht genau einmal gefunden.")
    seite = seite.replace(ANKER, ANKER + seed, 1)
    seite = seite.replace("</html>", MESS.replace("__FALL__", fall) + "</html>", 1)

    tmp = tempfile.mkdtemp(prefix="plan-sort-")
    try:
        ziel = os.path.join(tmp, "index.html")
        io.open(ziel, "w", encoding="utf-8").write(seite)
        dump = os.path.join(tmp, "dump.html")
        with io.open(dump, "wb") as f:
            subprocess.call([
                EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=20000",
                "--window-size=1280,900",
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


AB_VOR = "Haehnchen mit Reis|Lachs mit Brokkoli|Chili sin Carne"
AB_GETAUSCHT = "m2|m1|m3"


def main():
    print("Pruefstand: Meals im Wochenplan sortieren")
    print("Quelle: " + os.path.relpath(INDEX, BASIS).replace("\\", "/")
          + (("  [Rueckbau: " + RUECKBAU + "]") if RUECKBAU else ""))
    print("")

    faelle = ["umsortieren", "kategorie", "frei", "versteckt", "zurueck",
              "tippen", "wackeln", "ansehen", "ueberlauf"]
    erg = {}
    for f in faelle:
        erg[f] = lauf(f)

    pruefungen = []

    def p(was, ist, soll):
        pruefungen.append((was, ist == soll, ist, soll))

    # --- Aufbau: ohne diese Groessen misst alles Weitere nichts ---
    u = erg["umsortieren"]
    p("Der Anfasser steckt in der Karte", u.get("griffDa"), True)
    p("Drei Meals im Abendessen", u.get("vorherAb"), AB_VOR)

    # --- Fall 1: innerhalb eines Slots umsortieren ---
    p("Umsortieren: Karte aufgenommen", u.get("aufgenommen"), True)
    p("Umsortieren: Sortierzustand gesetzt", u.get("sortierzustand"), True)
    p("Umsortieren: Reihenfolge getauscht", u.get("gespeichertAb"), AB_GETAUSCHT)
    p("Umsortieren: genau EIN Schreibvorgang", u.get("schreibDurchAktion"), 1)
    p("Umsortieren: Position angesagt", ("Position 2 von 3" in (u.get("live") or "")), True)

    # --- Fall 2: die Kategorie wechseln ---
    k = erg["kategorie"]
    p("Kategorie: Karte aufgenommen", k.get("aufgenommen"), True)
    p("Kategorie: Zielfach markiert", k.get("zielMarkiert"), True)
    p("Kategorie: Meal ist im Fruehstueck", k.get("gespeichertFr"), "m4|m1")
    p("Kategorie: und aus dem Abendessen raus", k.get("gespeichertAb"), "m2|m3")
    p("Kategorie: genau EIN Schreibvorgang", k.get("schreibDurchAktion"), 1)

    # --- Fall 3: die Kategoriesperre ist beim Ziehen gefallen ---
    fr = erg["frei"]
    p("Frei: das Fruehstueck ging ins Abendessen", fr.get("gespeichertAb"), "m1|m2|m3|m4")
    p("Frei: und ist aus dem Fruehstueck raus", fr.get("gespeichertFr"), "")
    p("Frei: genau EIN Schreibvorgang", fr.get("schreibDurchAktion"), 1)

    # --- Fall 4: ausgeblendete fremde Karten ---
    # Sechs Eintraege, vier davon fremd - der vierte fremde steckt hinter "+1 weitere".
    # Wird die erste Karte unter die zweite gezogen, muss GENAU das passieren und nichts
    # an der versteckten Karte.
    # Ohne Anmeldung gibt es keine eigene UID, also gilt JEDER zugewiesene Eintrag als
    # fremd: von sechs bleiben drei sichtbar, die restlichen stecken hinter "+3 weitere".
    # Das ist der schaerfere Fall als der urspruenglich gedachte - die Anzeige zeigt die
    # Haelfte, und der Zielindex muss trotzdem stimmen.
    v = erg["versteckt"]
    p("Versteckt: nur die halbe Liste ist sichtbar", len((v.get("vorherAb") or "").split("|")), 3)
    p("Versteckt: Karte aufgenommen", v.get("aufgenommen"), True)
    # m1 wandert ans ECHTE Ende, hinter die drei versteckten - nicht auf Platz drei, wo die
    # Anzeige aufhoert.
    p("Versteckt: die Karte ueberholt die versteckten NICHT",
      v.get("gespeichertAb"), "m2|m3|m4|m1|m2|m1")
    p("Versteckt: genau EIN Schreibvorgang", v.get("schreibDurchAktion"), 1)

    # --- Fall 5: Rueckgaengig ---
    z = erg["zurueck"]
    p("Zurueck: der Zug hat gewirkt", z.get("nachZug"), AB_GETAUSCHT)
    p("Zurueck: der Knopf ist da", z.get("knopfDa"), True)
    p("Zurueck: Reihenfolge exakt wiederhergestellt", z.get("gespeichertAb"), "m1|m2|m3")

    # --- Fall 6: der Klick nach dem Ziehen ---
    t = erg["tippen"]
    p("Klick nach dem Ziehen oeffnet NICHT", t.get("blattOffen"), False)
    p("Der zweite, gewollte Tipp oeffnet wieder", t.get("blattOffenDanach"), True)
    p("Klick-Fall: Reihenfolge trotzdem getauscht", t.get("gespeichertAb"), AB_GETAUSCHT)

    # --- Fall 7: wischen statt sortieren ---
    w = erg["wackeln"]
    p("Wischen vor Ablauf der Haltezeit: keine Aufnahme", w.get("sortierzustand"), False)
    p("Wischen vor Ablauf der Haltezeit: Reihenfolge unveraendert", w.get("gespeichertAb"), "m1|m2|m3")
    p("Wischen vor Ablauf der Haltezeit: KEIN Schreibvorgang", w.get("schreibDurchAktion"), 0)

    # --- Fall 8: Nur-Ansehen ---
    a = erg["ansehen"]
    p("Nur-Ansehen: kein Anfasser in der Karte", a.get("griffDa"), False)
    p("Nur-Ansehen: keine Aufnahme", a.get("sortierzustand"), False)
    p("Nur-Ansehen: Reihenfolge unveraendert", a.get("gespeichertAb"), "m1|m2|m3")
    p("Nur-Ansehen: KEIN Schreibvorgang", a.get("schreibDurchAktion"), 0)

    # --- Fall 9: kein waagerechter Ueberlauf ---
    o = erg["ueberlauf"]
    p("Die Tageskarte laeuft waagerecht nicht ueber", o.get("quer"), 0)

    rot = 0
    for was, ok, ist, soll in pruefungen:
        if ok:
            print(u"  OK    %s" % was)
        else:
            rot += 1
            print(u"  ROT   %s   ist=%r  soll=%r" % (was, ist, soll))

    for f in faelle:
        if erg[f].get("messfehler"):
            rot += 1
            print(u"  ROT   Fall %s: %s" % (f, erg[f]["messfehler"]))

    print("")
    print(u"ERGEBNIS %d gruen, %d rot  (%d Messgroessen)"
          % (len(pruefungen) - rot, rot, len(pruefungen)))
    return 1 if rot else 0


if __name__ == "__main__":
    sys.exit(main())
