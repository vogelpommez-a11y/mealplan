# -*- coding: utf-8 -*-
u"""
Barcode-Schnellzugriff: die Packung als eine Portion (Entscheidung 11.09.2026).

Gemessen wird die Zahl, um die es geht: Welche MENGE landet im Plan, wenn jemand ein
Produkt scannt - und steht sie so am Meal, dass man sie noch aendern kann?

Bis zum 11.09.2026 galt eine reine Packungsgroesse ausdruecklich NICHT als Portion
(`docs/TROUBLESHOOTING.md` 41): "500 g" Nudeln haetten still 1750 kcal in den Plan
geschrieben. Der Nutzer hat die Regel umgedreht - der Becher, die Tuete, der Riegel SIND
im Alltag eine Portion. Dieser Pruefstand haelt beide Seiten der neuen Regel fest: dass
die Menge uebernommen wird UND dass sie sichtbar und aenderbar bleibt.

Der Code ist ECHT ausgeschnitten (quickAddByBarcode aus index.html, offServingSize aus
lib/barcode.js, qtyLabel samt Helfern) - kein Nachbau. Gestubbt ist nur, was von aussen
kommt: der Scan, der OFF-Abruf, render/toast und der Zustand.

SECHS FAELLE:
  packung      "500 g" ohne Portionsangabe -> still angelegt, 500 g, Werte hochgerechnet
  liter        "1 l" -> 1000 ml, der Toast beschriftet sie als Liter, die Zutat als ml
  mehrfach     "6 x 65 g" -> EIN Riegel ist die Portion, nicht die Schachtel
  portion      "1 Stueck (65 g)" -> unveraendert 65 g
  unvollstaendig  fehlende Naehrwerte -> Formular statt Raten, kein Meal im Plan
  zweitscan    derselbe Barcode zweimal -> kein zweites Rezept (Dedupe ueber barcode)

Gegenproben - ohne sie zaehlt kein Ergebnis:
  python tools/pruefstand-scan-packung.py --rueckbau alteregel   # Packung wieder ablehnen
  python tools/pruefstand-scan-packung.py --rueckbau ohnezutat   # Menge nicht als Zutat

Aufruf:  python tools/pruefstand-scan-packung.py [--rueckbau <name>]
"""
import io, json, os, re, subprocess, sys, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
INDEX = os.path.join(BASIS, "index.html")
BARCODE = os.path.join(BASIS, "lib", "barcode.js")

RUECKBAUTEN = {
    "alteregel": ("const portion = ss && ss.grams > 0 ? ss.grams : null;",
                  "const portion = ss && ss.grams > 0 && (ss.count || ss.serving) ? ss.grams : null;"),
    "ohnezutat": ("ingredients: [Object.assign({ name: p.name, grams: portion },",
                  "ingredients: [].concat([]).length ? [] : [], _weg: ([Object.assign({ name: p.name, grams: portion },"),
}


def block(text, kopf):
    u"""Den Funktionsblock ab `kopf` bis zur schliessenden Klammer auf gleicher Einrueckung.

    Bewusst nicht ueber die naechste Zeile, die "  }" ENTHAELT: in verschachteltem Code ist
    das regelmaessig `    }));` mitten in der Funktion, und der Schnitt waere kaputt
    (docs/TESTING.md, Fallarchiv zum Schnitt-Endmarker).
    """
    i = text.index(kopf)
    einzug = ""
    zeilenanfang = text.rfind("\n", 0, i) + 1
    einzug = text[zeilenanfang:i]
    ende = "\n" + einzug + "}"
    j = text.index(ende, i)
    return text[zeilenanfang:j + len(ende)]


def baue_seite(rueckbau=None):
    seite = pm_quelle.lade_seite(INDEX)
    if rueckbau:
        alt, neu = RUECKBAUTEN[rueckbau]
        if seite.count(alt) != 1:
            raise SystemExit("Rueckbau '%s' fand seine Stelle nicht genau einmal (%d) - der "
                             "Pruefstand wuerde sonst still gegen unveraenderten Code messen."
                             % (rueckbau, seite.count(alt)))
        seite = seite.replace(alt, neu, 1)
        if rueckbau == "ohnezutat":
            # Die geoffnete Klammer des Rueckbaus wieder schliessen: aus der Zutatenliste
            # wird ein totes Feld, das Meal traegt danach keine Menge mehr.
            seite = seite.replace("{ kcal: p.kcal, carbs: p.carbs, protein: p.protein, fat: p.fat })],",
                                  "{ kcal: p.kcal, carbs: p.carbs, protein: p.protein, fat: p.fat })]),", 1)
    return seite


def schneide(rueckbau=None):
    seite = baue_seite(rueckbau)
    teile = [
        block(seite, "function offServingSize(p) {"),
        block(seite, "function bruchLabel(n) {"),
        block(seite, "function qtyLabel(n, u) {"),
        block(seite, "function numLabel(n) {"),
        block(seite, "function unitShort(u) {"),
        block(seite, "async function quickAddByBarcode(day, meal) {"),
    ]
    return "\n".join(teile)


BUEHNE = u"""<!doctype html><meta charset="utf-8"><title>Scan-Pruefstand</title>
<pre id="messung">laeuft</pre>
<script>
window.__fehler = [];
window.addEventListener("error", e => window.__fehler.push((e.message || "") + " @" + (e.lineno || "?")));
</script>
<script>
// ---- Stubs: alles, was von aussen kommt. Der geprueft Code selbst ist echt. ----
let uidZaehler = 0;
function uid() { return "r" + (++uidZaehler); }
const state = { recipes: [], plan: { mon: { fr: [] } } };
let syncUid = "", syncGid = null;
function makeEntry(rid, uids) { return { id: rid, uids: uids.filter(Boolean) }; }
function slotIsShared() { return false; }
let renderZahl = 0;
function render() { renderZahl++; }
const toasts = [];
function toast(t) { toasts.push(String(t)); }
const sheetAufrufe = [];
function openMealSheet(id, prefill) { sheetAufrufe.push({ id, prefill }); }
// Der Scan selbst - eine Kamera hat der Pruefstand nicht.
let naechsterCode = "111";
async function scanBarcodeCode() { return naechsterCode; }
// Das Produkt, das OFF liefern wuerde. offServingSize() laeuft darauf ECHT.
let naechstesProdukt = null;
async function fetchOffNutrition() {
  const p = naechstesProdukt;
  if (!p) return null;
  return {
    name: p.name, kcal: p.kcal, carbs: p.carbs, protein: p.protein, fat: p.fat,
    servingSize: offServingSize({ serving_size: p.serving_size, quantity: p.quantity }),
  };
}
</script>
<script>
__CODE__
</script>
<script>
const VOLL = { name: "Testprodukt", kcal: 100, carbs: 10, protein: 5, fat: 2 };
function zuruecksetzen() {
  state.recipes.length = 0; state.plan.mon.fr.length = 0;
  toasts.length = 0; sheetAufrufe.length = 0; uidZaehler = 0;
}
async function fall(name, produkt, code) {
  zuruecksetzen();
  naechstesProdukt = Object.assign({}, VOLL, produkt);
  naechsterCode = code || "111";
  await quickAddByBarcode("mon", "fr");
  const r = state.recipes[0] || null;
  const z = r && r.ingredients && r.ingredients[0];
  return {
    fall: name,
    rezepte: state.recipes.length,
    geplant: state.plan.mon.fr.length,
    kcal: r ? r.nutrition.kcal : null,
    carbs: r ? r.nutrition.carbs : null,
    zutatGramm: z ? z.grams : null,
    zutatEinheit: z ? (z.unit || "g") : null,
    zutatKcal: z ? z.kcal : null,
    toast: toasts.join(" | "),
    formular: sheetAufrufe.length,
  };
}
(async function () {
  const raus = {};
  try {
    raus.packung = await fall("packung", { quantity: "500 g" });
    raus.liter = await fall("liter", { quantity: "1 l" });
    raus.mehrfach = await fall("mehrfach", { quantity: "6 x 65 g" });
    raus.portion = await fall("portion", { serving_size: "1 Stück (65 g)" });
    raus.unvollstaendig = await fall("unvollstaendig", { quantity: "500 g", protein: null });
    // Zweitscan: derselbe Barcode ein zweites Mal, ohne den Zustand zu leeren.
    zuruecksetzen();
    naechstesProdukt = Object.assign({}, VOLL, { quantity: "500 g" });
    naechsterCode = "222";
    await quickAddByBarcode("mon", "fr");
    await quickAddByBarcode("mon", "fr");
    raus.zweitscan = { rezepte: state.recipes.length, geplant: state.plan.mon.fr.length };
  } catch (e) {
    raus.messfehler = e.message;
  }
  raus.fehler = (window.__fehler || []).join(" || ") || "keine";
  document.getElementById("messung").textContent = JSON.stringify(raus);
})();
</script>
"""


def lauf(rueckbau=None):
    seite = BUEHNE.replace("__CODE__", schneide(rueckbau))
    tmp = tempfile.mkdtemp(prefix="scan-packung-")
    try:
        ziel = os.path.join(tmp, "buehne.html")
        io.open(ziel, "w", encoding="utf-8").write(seite)
        dump = os.path.join(tmp, "dump.html")
        with io.open(dump, "wb") as f:
            subprocess.call([EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=15000",
                             "--user-data-dir=" + os.path.join(tmp, "profil"),
                             "--dump-dom", "file:///" + ziel.replace("\\", "/")],
                            stdout=f, stderr=subprocess.PIPE)
        roh = io.open(dump, encoding="utf-8", errors="replace").read()
        m = re.search(r'<pre id="messung">(.*?)</pre>', roh, re.S)
        if not m:
            return {"messfehler": "KEINE MESSUNG - der Pruefstand selbst ist kaputt."}
        text = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">"))
        if text.strip() == "laeuft":
            return {"messfehler": "Die Messung lief nicht zu Ende."}
        return json.loads(text)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    args = sys.argv[1:]
    rueckbau = None
    if "--rueckbau" in args:
        i = args.index("--rueckbau")
        rueckbau = args[i + 1]
        if rueckbau not in RUECKBAUTEN:
            raise SystemExit("Unbekannter Rueckbau: %s (bekannt: %s)"
                             % (rueckbau, ", ".join(sorted(RUECKBAUTEN))))

    print("Pruefstand Barcode-Schnellzugriff: die Packung als Portion")
    print("Quelle: index.html + lib/barcode.js"
          + (("   [Rueckbau: " + rueckbau + "]") if rueckbau else ""))
    print("")

    e = lauf(rueckbau)
    if e.get("messfehler"):
        print("  MESSFEHLER: " + e["messfehler"])
        print("")
        print("ERGEBNIS 0 gruen, 1 rot  (1 Messgroessen)")
        return 1

    pruefungen = []

    def p(was, ist, soll):
        pruefungen.append((was, ist == soll, ist, soll))

    a = e["packung"]
    p("Packung: still angelegt, kein Formular", a["formular"], 0)
    p("Packung: genau ein Rezept", a["rezepte"], 1)
    p("Packung: im Plan gelandet", a["geplant"], 1)
    p("Packung: 500 g hochgerechnet (100 kcal/100 g)", a["kcal"], 500)
    p("Packung: Kohlenhydrate mitgerechnet", a["carbs"], 50)
    p("Packung: die Menge haengt als Zutat am Meal", a["zutatGramm"], 500)
    p("Packung: die Zutat traegt die Werte je 100 g", a["zutatKcal"], 100)
    p("Packung: der Toast nennt die Menge", "500 g" in a["toast"], True)

    b = e["liter"]
    p("Liter: als 1000 ml uebernommen", b["zutatGramm"], 1000)
    p("Liter: Zutat traegt die Einheit ml", b["zutatEinheit"], "ml")
    p("Liter: der Toast schreibt 1 L", "1 L" in b["toast"], True)

    c = e["mehrfach"]
    p("Mehrfachpackung: EIN Riegel ist die Portion", c["zutatGramm"], 65)
    p("Mehrfachpackung: Werte fuer ein Stueck", c["kcal"], 65)

    d = e["portion"]
    p("Echte Portionsangabe: unveraendert 65 g", d["zutatGramm"], 65)
    p("Echte Portionsangabe: still angelegt", d["formular"], 0)

    u = e["unvollstaendig"]
    p("Fehlende Naehrwerte: Formular statt Raten", u["formular"], 1)
    p("Fehlende Naehrwerte: kein Meal angelegt", u["rezepte"], 0)
    p("Fehlende Naehrwerte: nichts im Plan", u["geplant"], 0)

    z = e["zweitscan"]
    p("Zweiter Scan: kein zweites Rezept", z["rezepte"], 1)
    p("Zweiter Scan: aber zweimal eingeplant", z["geplant"], 2)

    breit = max(len(x[0]) for x in pruefungen)
    rot = 0
    for was, ok, ist, soll in pruefungen:
        if ok:
            print("  OK    " + was)
        else:
            rot += 1
            print("  ROT   " + was.ljust(breit) + "   ist=" + repr(ist) + "  soll=" + repr(soll))
    print("")
    if e.get("fehler") and e["fehler"] != "keine":
        print("  JS-FEHLER: " + e["fehler"])
        rot += 1
    print("ERGEBNIS %d gruen, %d rot  (%d Messgroessen)"
          % (len(pruefungen) - rot, rot, len(pruefungen)))
    return 1 if rot else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
