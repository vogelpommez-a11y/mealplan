# -*- coding: utf-8 -*-
u"""
Prueft die Einkaufsliste ueber BEIDE Wochenreiter hinweg ("Aktuelle Woche" / "Naechste Woche").

Die Frage, die dieser Pruefstand stellt:

  Haengt der abgehakte Zustand an der Woche, fuer die man einkauft?

Bis zum 28.08.2026 nicht: SHOP_DONE_KEY war EIN flaches Set aus `norm`-Schluesseln
(Name + Einheit), geteilt von beiden Wochen. Wer in der aktuellen Woche "500 g Hackfleisch"
abhakte und dann auf "Naechste Woche" umschaltete, fand die Position dort schon abgehakt -
und kaufte zu wenig ein. Am Montag rueckte derselbe Zustand ausserdem stillschweigend in die
neue Woche nach: die frische Woche startete mit den Haken der vergangenen.

Zweiter Punkt: der Kopf des Modals beschriftete die naechste Woche als "diese Woche"
(`state.viewWeek !== "next" && todayIdx > 0 ? "ab heute" : "diese Woche"` faellt fuer "next"
in den zweiten Zweig). Das PDF machte es an derselben Stelle richtig ("Naechste Woche") -
womit belegt ist, dass es ein Versehen war und keine Absicht.

Getestet wird die ECHTE App headless: Plan seeden, Liste oeffnen, abhaken, Woche wechseln,
wieder oeffnen. Der Abhak-Zustand lebt in localStorage - nur der echte Lauf zeigt ihn.

Aufruf:  python tools/pruefstand-einkaufsliste.py [pfad-zu-index.html]
"""
import io, json, os, re, subprocess, sys, tempfile, shutil, datetime

# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ANKER = '<meta charset="utf-8">'   # index.html hat kein <head>-Tag, siehe TROUBLESHOOTING 109

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def wochen_key(dt):
    u"""ISO-Wochenschluessel wie isoWeekKey() in index.html: "2026-W35"."""
    jahr, woche, _ = dt.isocalendar()
    return u"%d-W%02d" % (jahr, woche)


HEUTE = datetime.date.today()
KEY_CUR = wochen_key(HEUTE)
KEY_NEXT = wochen_key(HEUTE + datetime.timedelta(days=7))

GOAL = {"kcal": 2200, "carbs": 220, "protein": 160, "fat": 65, "sex": "m", "age": 34,
        "height": 182, "weight": 88, "activity": "pal16", "mode": "lose", "pace": "moderate",
        "training": {}}

# Zwei Rezepte, die sich EINE Zutat teilen. Genau daran haengt der Befund: der
# Abhak-Schluessel `norm` ist "hackfleisch|g" - in beiden Wochen derselbe. Ohne die
# gemeinsame Zutat wuerde der Fehler gar nicht sichtbar.
REZEPTE = [
    {"id": "r-bolo", "name": "Bolognese", "category": "Mittagessen",
     "nutrition": {"kcal": 600, "carbs": 60, "protein": 40, "fat": 20},
     "ingredients": [
         {"name": "Hackfleisch", "grams": 150, "unit": "g"},
         {"name": "Nudeln", "grams": 100, "unit": "g"},
     ], "steps": "", "created": 1755000000000},
    {"id": "r-chili", "name": "Chili", "category": "Abendessen",
     "nutrition": {"kcal": 550, "carbs": 50, "protein": 38, "fat": 18},
     "ingredients": [
         {"name": "Hackfleisch", "grams": 120, "unit": "g"},
         {"name": "Kidneybohnen", "grams": 200, "unit": "g"},
     ], "steps": "", "created": 1755000000000},
]


def plan(rid_mi, rid_ab):
    u"""Alle sieben Tage belegen - in der aktuellen Woche zaehlen nur die Tage ab heute
    (planDaysAhead), sonst waere die Liste am Sonntagabend leer und der Lauf nichtssagend."""
    p = {}
    for d in DAYS:
        p[d] = {"fr": [], "mi": [rid_mi], "ab": [rid_ab], "sn": []}
    return p


STATE = {
    "recipes": REZEPTE,
    "plans": {KEY_CUR: plan("r-bolo", "r-chili"), KEY_NEXT: plan("r-bolo", "r-chili")},
    "goal": GOAL, "onboarded": True, "tab": "plan", "viewWeek": "cur",
    "favs": [], "planned": {}, "shopPersons": 1,
    "weights": [], "weightGoals": {}, "weekStats": {},
}
PROFILE = {"name": "Test"}

# Messung als Kette von Schritten - jeder Schritt wartet auf den vorigen, weil der
# Reiterwechsel ueber render() laeuft und die Modals ueber openModal/closeModal.
MESS = u"""<script>
(function () {
  var raus = { schritte: [] };
  function q(s) { return document.querySelector(s); }
  function modalInfo() {
    var m = q('.modal[aria-label^="Einkaufsliste"]');
    if (!m) return { da: false };
    var ch = Array.prototype.slice.call(m.querySelectorAll(".shop-check"));
    var k = m.querySelector(".kicker");
    return {
      da: true,
      positionen: ch.length,
      abgehakt: ch.filter(function (c) { return c.checked; }).length,
      kicker: k ? k.textContent.trim() : "(kein kicker)",
      ueberschrift: (m.querySelector(".modal-head h3") || {}).textContent || "",
      // Der Dialogname ist das, was ein Screenreader beim OEFFNEN ansagt - der Kicker wird
      // erst beim Weiterlesen erreicht. Seit die Ueberschrift gekuerzt ist ("Einkaufsliste"
      // statt "Einkaufsliste der Woche"), traegt sonst nichts im Namen die Woche.
      dialogname: m.getAttribute("aria-label") || "",
      fortschritt: (m.querySelector("#shop-count") || {}).textContent || "",
      erste: ch.length ? (ch[0].parentElement.querySelector(".lbl") || {}).textContent : ""
    };
  }
  function schliessen() {
    var b = document.querySelector('.modal[aria-label^="Einkaufsliste"] [data-close]');
    if (b) b.click();
  }
  function oeffnen() { var b = q('[data-action="shopping"]'); if (b) b.click(); return !!b; }
  function woche(w) {
    var b = q('[data-action="week"][data-week="' + w + '"]');
    if (b) b.click();
    return !!b;
  }
  function ende() {
    raus.fehler = (window.__fehler || []).join(" || ") || "keine";
    var p = document.createElement("pre");
    p.id = "messung"; p.textContent = JSON.stringify(raus);
    document.documentElement.appendChild(p);
  }
  var kette = [
    // 1) Plan-Reiter, aktuelle Woche
    function () { var t = q('[data-tab="plan"]'); raus.planReiter = !!t; if (t) t.click(); },
    // 2) Einkaufsliste der AKTUELLEN Woche oeffnen
    function () { raus.knopfDa = oeffnen(); },
    function () { raus.a_offen = modalInfo(); },
    // 3) die erste Position abhaken und schliessen
    function () {
      var c = q('.modal[aria-label^="Einkaufsliste"] .shop-check');
      if (c) { c.click(); raus.a_abgehakt = c.dataset.norm; }
      raus.a_nachKlick = modalInfo();
      schliessen();
    },
    // 4) auf "Naechste Woche" umschalten
    function () { raus.wochenknopf = woche("next"); },
    // 5) Einkaufsliste der NAECHSTEN Woche oeffnen - hier faellt der Befund
    function () { oeffnen(); },
    function () { raus.b_next = modalInfo(); schliessen(); },
    // 6) zurueck auf die aktuelle Woche - das Haekchen muss noch da sein
    function () { woche("cur"); },
    function () { oeffnen(); },
    function () { raus.c_zurueck = modalInfo(); schliessen(); },
    ende
  ];
  var i = 0;
  (function next() {
    if (i >= kette.length) return;
    var f = kette[i++];
    try { f(); } catch (e) { raus.messfehler = (raus.messfehler || "") + " | " + e.message; }
    setTimeout(next, 260);
  })();
})();
</script>"""


# --- Lauf B: Altbestand und Verfall -----------------------------------------------------
# Der zweite Lauf startet mit einem VORBELEGTEN Abhak-Speicher und beantwortet drei Fragen,
# die der erste nicht stellen kann, weil er bei null anfaengt:
#   1. Ueberlebt ein Haken den Neustart ueberhaupt? (er lebt in localStorage, nicht im State)
#   2. Was passiert mit dem Altbestand im flachen Format aus der Fassung vor dem 28.08.2026?
#      Wegwerfen waere die bequeme Loesung - und wuerde jedem Nutzer beim Update seinen halb
#      abgehakten Einkauf loeschen.
#   3. Fliegt eine laengst verfallene Woche wieder raus, oder waechst der Eintrag ewig weiter?
ALT_NORM = u"kidneybohnen|g"          # eine Position, die es in beiden Wochen wirklich gibt
KEY_ALT = wochen_key(HEUTE - datetime.timedelta(days=21))   # drei Wochen her: muss verfallen

MESS_B = u"""<script>
(function () {
  var raus = {};
  function q(s) { return document.querySelector(s); }
  function speicher() {
    try { return JSON.parse(localStorage.getItem("wochenkueche_shop_v1__test") || "null"); }
    catch (e) { return "(unlesbar)"; }
  }
  function info() {
    var m = q('.modal[aria-label^="Einkaufsliste"]');
    if (!m) return { da: false };
    var ch = Array.prototype.slice.call(m.querySelectorAll(".shop-check"));
    return { da: true, positionen: ch.length,
             abgehakt: ch.filter(function (c) { return c.checked; }).length };
  }
  function schliessen() {
    var b = document.querySelector('.modal[aria-label^="Einkaufsliste"] [data-close]');
    if (b) b.click();
  }
  function ende() {
    raus.fehler = (window.__fehler || []).join(" || ") || "keine";
    var p = document.createElement("pre");
    p.id = "messung"; p.textContent = JSON.stringify(raus);
    document.documentElement.appendChild(p);
  }
  var kette = [
    function () { raus.speicherVorher = speicher(); var t = q('[data-tab="plan"]'); if (t) t.click(); },
    // Der Altbestand muss in der AKTUELLEN Woche ankommen - dort wurde er ja gesetzt.
    function () { var b = q('[data-action="shopping"]'); if (b) b.click(); },
    function () { raus.a_alt = info(); schliessen(); },
    // In der naechsten Woche darf er NICHT auftauchen.
    function () { var b = q('[data-action="week"][data-week="next"]'); if (b) b.click(); },
    function () { var b = q('[data-action="shopping"]'); if (b) b.click(); },
    function () {
      raus.b_next = info();
      // Dort etwas abhaken - das schreibt den Speicher neu und raeumt dabei auf.
      var c = q('.modal[aria-label^="Einkaufsliste"] .shop-check');
      if (c) c.click();
      raus.b_nachKlick = info();
      schliessen();
    },
    function () { raus.speicherNachher = speicher(); },
    ende
  ];
  var i = 0;
  (function next() {
    if (i >= kette.length) return;
    var f = kette[i++];
    try { f(); } catch (e) { raus.messfehler = (raus.messfehler || "") + " | " + e.message; }
    setTimeout(next, 260);
  })();
})();
</script>"""


# --- Lauf D: Personenzahl -----------------------------------------------------------
# Der Abhak-Schluessel `norm` ist Name + Einheit OHNE Menge - ausdruecklich, damit ein Haken
# eine geaenderte Personenzahl ueberlebt (siehe Kommentar an buildShoppingList). Der Umbau
# auf wochenweises Speichern fasst genau die Stelle an, die das leistet: persist() schreibt
# jetzt in einen Wochen-Eimer, save() laeuft dazwischen. Deshalb wird hier nachgemessen,
# dass beides weiter zusammenspielt - der Haken bleibt, die MENGE aendert sich.
MESS_D = u"""<script>
(function () {
  var raus = {};
  function q(s) { return document.querySelector(s); }
  function info() {
    var m = q('.modal[aria-label^="Einkaufsliste"]');
    if (!m) return { da: false };
    var ch = Array.prototype.slice.call(m.querySelectorAll(".shop-check"));
    return {
      da: true, positionen: ch.length,
      abgehakt: ch.filter(function (c) { return c.checked; }).length,
      personen: (m.querySelector("#shop-pers") || {}).textContent || "",
      erste: ch.length ? (ch[0].parentElement.querySelector(".lbl") || {}).textContent : ""
    };
  }
  function zu() { var b = q('.modal[aria-label^="Einkaufsliste"] [data-close]'); if (b) b.click(); }
  var kette = [
    function () { q('[data-tab="plan"]').click(); },
    function () { q('[data-action="shopping"]').click(); },
    function () {
      var c = q('.modal[aria-label^="Einkaufsliste"] .shop-check');
      if (c) c.click();
      raus.d_vor = info();
    },
    // Personenzahl hochstellen - das ruft buildShoppingList() neu und save()
    function () {
      var p = q('.modal[aria-label^="Einkaufsliste"] .pbtn[data-pers="1"]');
      if (p) p.click();
      raus.d_nach = info();
      zu();
    },
    // Neu oeffnen: kommt der Haken aus dem Speicher zurueck?
    function () { q('[data-action="shopping"]').click(); },
    function () { raus.d_neu = info(); zu(); },
    function () {
      raus.fehler = (window.__fehler || []).join(" || ") || "keine";
      var p = document.createElement("pre");
      p.id = "messung"; p.textContent = JSON.stringify(raus);
      document.documentElement.appendChild(p);
    }
  ];
  var i = 0;
  (function n() {
    if (i >= kette.length) return;
    try { kette[i++](); } catch (e) { raus.messfehler = (raus.messfehler || "") + " | " + e.message; }
    setTimeout(n, 260);
  })();
})();
</script>"""


# --- Lauf E: der PDF-Kopf --------------------------------------------------------------
# `shopPdfString()` baut den Zeitraum seit dem 28.08.2026 aus derselben Quelle wie die
# Modal-Koepfe. Vorher stand dort eine eigene Zeile, die zwar die richtige WOCHE nannte, aber
# das "ab heute" verschwieg: Das PDF trug "Diese Woche" ueber einer Liste, die nur die
# restlichen Tage enthaelt. Wer es ausdruckt, sieht dem Blatt nicht an, dass die vergangenen
# Tage fehlen - derselbe Fehler wie im Modal-Kopf, nur andersherum.
#
# Gemessen wird der erzeugte PDF-Bytestrom. Die Kopfzeile steht dort als PDF-Textoperator
# `(Diese Woche ab heute) Tj` - lesbar, weil pdfEsc() nur Klammern und Backslashes maskiert.
MESS_E = u"""<script>
(function () {
  var raus = {};
  function ende() {
    raus.fehler = (window.__fehler || []).join(" || ") || "keine";
    var p = document.createElement("pre");
    p.id = "messung"; p.textContent = JSON.stringify(raus);
    document.documentElement.appendChild(p);
  }
  // shopPdfString() lebt im IIFE und ist von aussen nicht erreichbar - erreichbar ist nur der
  // Weg ueber den Knopf. Das fertige PDF wird deshalb im Blob-Konstruktor abgefangen.
  //
  // saveBlob() uebergibt pdfBytes(...), also ein Uint8Array - String() daraus ergaebe
  // "37,80,68,70,..." und keine lesbare Kopfzeile. Das PDF ist byteweise Latin-1 kodiert
  // (pdfEsc maskiert nur Klammern und Backslashes), deshalb Zeichen fuer Zeichen dekodieren.
  var echtesBlob = window.Blob;
  var gefangen = [];
  function alsText(teil) {
    if (typeof teil === "string") return teil;
    var b = (teil && teil.buffer) ? new Uint8Array(teil.buffer) : new Uint8Array(teil || []);
    var s = "", schritt = 8192;
    for (var i = 0; i < b.length; i += schritt) {
      s += String.fromCharCode.apply(null, b.subarray(i, i + schritt));
    }
    return s;
  }
  window.Blob = function (teile, opts) {
    try { if (opts && opts.type === "application/pdf") gefangen.push(alsText(teile[0])); } catch (e) {}
    return new echtesBlob(teile, opts);
  };
  // saveBlob() haengt einen <a download> ins Dokument und klickt ihn. Headless Edge startet
  // daraufhin einen ECHTEN Download - und beendet sich dann nicht mehr, auch nicht ueber
  // --virtual-time-budget (das steuert die Uhr, nicht laufende I/O). Der Lauf lief in den
  // Timeout. Der Bytestrom ist oben bereits eingesammelt, das Speichern traegt hier nichts
  // bei: Anker-Klicks werden unterbunden. Buttons sind nicht betroffen.
  var echterKlick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    if (this.hasAttribute("download")) { raus.downloadUnterbunden = true; return; }
    return echterKlick.apply(this, arguments);
  };
  function kopf(txt) {
    // pdfBrandHeader() setzt die Unterzeile als scope + "   \\267   " + dateStr (\\267 ist der
    // Mittelpunkt in WinAnsi). Gesucht wird deshalb die STRUKTUR, nicht das Wort: Nach
    // "Naechste" zu suchen scheiterte am Umlaut - "Nächste" steht dort byteweise WinAnsi-
    // kodiert, nicht als UTF-8. Ueber das Trennzeichen ist die Kodierung des Wortes egal.
    var m = /\\(([^)]*?)\\s*\\\\267\\s*[^)]*\\)\\s*Tj/.exec(txt);
    return m ? m[1].replace(/\\s+$/, "") : "(keine Kopfzeile gefunden)";
  }
  function q(s) { return document.querySelector(s); }
  var kette = [
    function () {
      // Der Fuss des Modals zeigt ENTWEDER "Teilen" (wenn das Geraet die Web Share API hat)
      // ODER "Als PDF" + "Als Text kopieren" - siehe canShare() in index.html. Headless Edge
      // meldet navigator.share, also erschiene hier nie ein PDF-Knopf. Abschalten, damit der
      // Zweig geprueft wird, den ein Rechner tatsaechlich sieht.
      try { navigator.share = undefined; } catch (e) {}
      raus.shareAus = typeof navigator.share !== "function";
      q('[data-tab="plan"]').click();
    },
    function () { q('[data-action="shopping"]').click(); },
    function () {
      var b = q('.modal[aria-label^="Einkaufsliste"] [data-pdf]');
      raus.pdfKnopfDa = !!b;
      if (b) b.click();
    },
    function () {
      raus.a_pdf = gefangen.length ? kopf(gefangen[gefangen.length - 1]) : "(kein PDF erzeugt)";
      var c = q('.modal[aria-label^="Einkaufsliste"] [data-close]'); if (c) c.click();
    },
    function () { q('[data-action="week"][data-week="next"]').click(); },
    function () { q('[data-action="shopping"]').click(); },
    function () {
      var b = q('.modal[aria-label^="Einkaufsliste"] [data-pdf]');
      if (b) b.click();
    },
    function () {
      raus.b_pdf = gefangen.length ? kopf(gefangen[gefangen.length - 1]) : "(kein PDF erzeugt)";
    },
    ende
  ];
  var i = 0;
  (function n() {
    if (i >= kette.length) return;
    try { kette[i++](); } catch (e) { raus.messfehler = (raus.messfehler || "") + " | " + e.message; }
    setTimeout(n, 300);
  })();
})();
</script>"""


def lauf(mess=None, shop_seed=None):
    u"""shop_seed: Vorbelegung fuer den Abhak-Speicher (Lauf B). None = leer starten."""
    seite = pm_quelle.lade_seite(INDEX)
    # "__test"-Suffix: localKey() haengt es unter file:// an jeden Schluessel (isTestOrigin).
    extra = u""
    if shop_seed is not None:
        extra = (u'["wochenkueche_shop_v1","wochenkueche_shop_v1__test"]'
                 u'.forEach(function(k){localStorage.setItem(k, %s);});'
                 % json.dumps(json.dumps(shop_seed)))
    seed = (u'<script>window.__fehler=[];'
            u'window.addEventListener("error",function(e){window.__fehler.push((e.message||"")+" @"+(e.lineno||"?"));});'
            u'try{["wochenkueche_v1","wochenkueche_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
            u'["wochenkueche_profile_v1","wochenkueche_profile_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
            u'%s'
            u'}catch(e){}</script>'
            % (json.dumps(json.dumps(STATE)), json.dumps(json.dumps(PROFILE)), extra))
    if seite.count(ANKER) != 1:
        raise SystemExit("charset-Meta nicht genau einmal gefunden.")
    seite = seite.replace(ANKER, ANKER + seed, 1)
    seite = seite.replace("</html>", (mess or MESS) + "</html>", 1)

    tmp = tempfile.mkdtemp(prefix="einkauf-")
    try:
        ziel = os.path.join(tmp, "index.html")
        io.open(ziel, "w", encoding="utf-8").write(seite)
        dump = os.path.join(tmp, "dump.html")
        with io.open(dump, "wb") as f:
            subprocess.call([
                EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=25000",
                "--user-data-dir=" + os.path.join(tmp, "profil"),
                "--dump-dom", "file:///" + ziel.replace("\\", "/")
            ], stdout=f, stderr=subprocess.PIPE)
        roh = io.open(dump, encoding="utf-8", errors="replace").read()
        m = re.search(r'<pre id="messung">(.*?)</pre>', roh, re.S)
        if not m:
            raise SystemExit("KEINE MESSUNG - der Pruefstand selbst ist kaputt.")
        text = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">"))
        return json.loads(text)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def pdf_text(s):
    u"""Oktal-Escapes eines PDF-Strings aufloesen: "N\\344chste Woche" -> "Nächste Woche".

    `pdfEsc()` schreibt Zeichen ausserhalb von ASCII als \\ooo (WinAnsi/Latin-1). Ohne diese
    Umkehrung suchte man im PDF vergeblich nach "Nächste" - der Umlaut steht dort nicht als
    Buchstabe. (Genau daran ist die erste Fassung dieser Pruefung gescheitert.)
    """
    return re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), s)


def planScope_modal(kicker):
    u"""Den Zeitraum aus einem Kicker herausloesen ("3 Positionen . diese Woche ab heute"
    -> "diese woche ab heute"), um ihn mit der PDF-Kopfzeile vergleichen zu koennen."""
    return kicker.split(u"·")[-1].strip().lower()


ok = bad = 0
def pruef(name, bed, zusatz=""):
    global ok, bad
    if bed: ok += 1; print(u"  OK      " + name)
    else:   bad += 1; print(u"  FEHLER  " + name + (u"  ->  " + zusatz if zusatz else ""))


print(u"Datei: " + INDEX)
print(u"Wochen: aktuell=%s  naechste=%s" % (KEY_CUR, KEY_NEXT))
r = lauf()
a = r.get("a_offen") or {}
ak = r.get("a_nachKlick") or {}
b = r.get("b_next") or {}
c = r.get("c_zurueck") or {}

print(u"")
print(u"Gemessen:")
print(u"  aktuelle Woche, geoeffnet   " + json.dumps(a, ensure_ascii=False))
print(u"  aktuelle Woche, 1x abgehakt " + json.dumps(ak, ensure_ascii=False))
print(u"  NAECHSTE Woche, geoeffnet   " + json.dumps(b, ensure_ascii=False))
print(u"  aktuelle Woche, zurueck     " + json.dumps(c, ensure_ascii=False))
print(u"")

pruef(u"kein JS-Fehler beim Start", r.get("fehler") == "keine", str(r.get("fehler")))
if r.get("messfehler"): pruef(u"Messung lief durch", False, r["messfehler"])
pruef(u"der Plan-Reiter existiert", r.get("planReiter") is True)
pruef(u"der Einkaufsknopf existiert", r.get("knopfDa") is True)
pruef(u"der Wochenumschalter existiert", r.get("wochenknopf") is True)

# --- Grundfunktion: sammelt die Liste ueberhaupt Zutaten ein? ---
pruef(u"die Liste oeffnet sich (aktuelle Woche)", a.get("da") is True)
pruef(u"sie zeigt Positionen", (a.get("positionen") or 0) >= 3,
      u"positionen=%s" % a.get("positionen"))
pruef(u"sie startet unabgehakt", a.get("abgehakt") == 0, u"abgehakt=%s" % a.get("abgehakt"))
pruef(u"Abhaken wirkt sofort", ak.get("abgehakt") == 1, u"abgehakt=%s" % ak.get("abgehakt"))

# --- Der Kern: haengt der Abhak-Zustand an der Woche? ---
pruef(u"die Liste oeffnet sich (naechste Woche)", b.get("da") is True)
pruef(u"die naechste Woche zeigt dieselbe Positionszahl",
      b.get("positionen") == a.get("positionen"),
      u"cur=%s next=%s" % (a.get("positionen"), b.get("positionen")))
pruef(u"das Haekchen der AKTUELLEN Woche faerbt NICHT auf die naechste ab",
      b.get("abgehakt") == 0, u"in der naechsten Woche abgehakt: %s" % b.get("abgehakt"))
pruef(u"und das Haekchen ueberlebt die Rueckkehr in die aktuelle Woche",
      c.get("abgehakt") == 1, u"abgehakt=%s" % c.get("abgehakt"))

# --- Die Beschriftung: welche Woche steht im Kopf? ---
kb = (b.get("kicker") or u"").lower()
ka = (a.get("kicker") or u"").lower()
pruef(u"der Kopf der naechsten Woche sagt NICHT 'diese Woche'",
      u"diese woche" not in kb, b.get("kicker"))
pruef(u"der Kopf der naechsten Woche nennt die naechste Woche",
      u"nächste woche" in kb or u"naechste woche" in kb, b.get("kicker"))
pruef(u"der Kopf der aktuellen Woche nennt die naechste Woche NICHT",
      u"nächste" not in ka, a.get("kicker"))
# Die Woche steht genau EINMAL im Kopf. Vorher hiess die Ueberschrift "Einkaufsliste der
# Woche" - zusammen mit dem jetzt genauen Kicker waere das dieselbe Angabe zweimal,
# einmal unbestimmt und einmal genau (CLAUDE.md Abschnitt 6: so wenig Text wie moeglich).
pruef(u"die Ueberschrift wiederholt die Woche nicht",
      u"woche" not in (a.get("ueberschrift") or u"").lower(), a.get("ueberschrift"))
pruef(u"die Ueberschrift heisst weiterhin 'Einkaufsliste'",
      (a.get("ueberschrift") or u"").strip() == u"Einkaufsliste", a.get("ueberschrift"))

# Der Dialogname ist das, was beim OEFFNEN angesagt wird. Der sichtbare Kicker wird erst beim
# Weiterlesen erreicht - fuer einen Screenreader-Nutzer waere die Woche sonst eine Stufe
# tiefer versteckt als fuer alle anderen. Befund des ux-reviewer zu 7f48cd7.
da = a.get("dialogname") or u""
db = b.get("dialogname") or u""
pruef(u"der Dialogname der aktuellen Woche nennt den Zeitraum",
      u"woche" in da.lower(), da)
pruef(u"der Dialogname der naechsten Woche nennt SIE",
      u"nächste woche" in db.lower(), db)
pruef(u"und verwechselt sie nicht mit dieser",
      u"diese woche" not in db.lower(), db)

# Ohne Komma: "diese Woche ab heute" ist EINE Aussage. Mit Komma lasen sich zwei Angaben
# hintereinander, als kaeme noch etwas.
pruef(u"der Zeitraum kommt ohne Komma aus", u"," not in ka.split(u"·")[-1], a.get("kicker"))

# ========================================================================================
# Lauf B: Altbestand (flaches Array) und Verfall alter Wochen
# ========================================================================================
print(u"")
print(u"--- Lauf B: Altbestand im flachen Format + eine verfallene Woche (%s) ---" % KEY_ALT)
rb = lauf(MESS_B, [ALT_NORM])
ba = rb.get("a_alt") or {}
bn = rb.get("b_next") or {}
bk = rb.get("b_nachKlick") or {}
sv = rb.get("speicherVorher")
sn = rb.get("speicherNachher")

print(u"")
print(u"Gemessen:")
print(u"  Speicher vorher             " + json.dumps(sv, ensure_ascii=False))
print(u"  aktuelle Woche (Altbestand) " + json.dumps(ba, ensure_ascii=False))
print(u"  naechste Woche              " + json.dumps(bn, ensure_ascii=False))
print(u"  Speicher nachher            " + json.dumps(sn, ensure_ascii=False))
print(u"")

pruef(u"kein JS-Fehler beim Start (Lauf B)", rb.get("fehler") == "keine", str(rb.get("fehler")))
if rb.get("messfehler"): pruef(u"Messung B lief durch", False, rb["messfehler"])
pruef(u"der Speicher lag wirklich im alten flachen Format vor", isinstance(sv, list), repr(sv))

# 1) Der Altbestand geht nicht verloren - er gehoert der aktuellen Woche.
pruef(u"ein Haken ueberlebt den Neustart", (ba.get("abgehakt") or 0) == 1,
      u"abgehakt=%s" % ba.get("abgehakt"))
# 2) Und er faerbt trotzdem nicht auf die naechste Woche ab.
pruef(u"der Altbestand landet NICHT in der naechsten Woche", bn.get("abgehakt") == 0,
      u"abgehakt=%s" % bn.get("abgehakt"))
pruef(u"Abhaken in der naechsten Woche wirkt", bk.get("abgehakt") == 1,
      u"abgehakt=%s" % bk.get("abgehakt"))

# 3) Nach dem Schreiben ist der Speicher ein nach Wochen geschluesseltes Objekt.
pruef(u"der Speicher liegt danach nach Wochen geschluesselt vor",
      isinstance(sn, dict), repr(sn))
if isinstance(sn, dict):
    pruef(u"beide Wochen stehen getrennt darin",
          KEY_CUR in sn and KEY_NEXT in sn, repr(sorted(sn.keys())))
    pruef(u"die aktuelle Woche hat ihren Altbestand behalten",
          ALT_NORM in (sn.get(KEY_CUR) or []), repr(sn.get(KEY_CUR)))
    pruef(u"die naechste Woche fuehrt ihren eigenen Haken",
          len(sn.get(KEY_NEXT) or []) == 1, repr(sn.get(KEY_NEXT)))

# ========================================================================================
# Lauf C: Verfall. Bewusst ein EIGENER Lauf - in Lauf B lag gar keine alte Woche im
# Speicher, dort waere "nichts Altes uebrig" trivial erfuellt gewesen und haette nichts
# gemessen. Hier liegt eine drei Wochen alte drin, und sie muss verschwinden.
# ========================================================================================
print(u"")
print(u"--- Lauf C: Verfall einer alten Woche (%s liegt im Speicher) ---" % KEY_ALT)
rc = lauf(MESS_B, {KEY_ALT: [ALT_NORM, u"nudeln|g"], KEY_CUR: [ALT_NORM]})
cv = rc.get("speicherVorher")
cn = rc.get("speicherNachher")
ca = rc.get("a_alt") or {}

print(u"")
print(u"Gemessen:")
print(u"  Speicher vorher   " + json.dumps(cv, ensure_ascii=False))
print(u"  Speicher nachher  " + json.dumps(cn, ensure_ascii=False))
print(u"")

pruef(u"kein JS-Fehler beim Start (Lauf C)", rc.get("fehler") == "keine", str(rc.get("fehler")))
if rc.get("messfehler"): pruef(u"Messung C lief durch", False, rc["messfehler"])
pruef(u"die alte Woche lag wirklich im Speicher",
      isinstance(cv, dict) and KEY_ALT in cv, repr(cv))
pruef(u"die aktuelle Woche wird aus dem Objektformat gelesen",
      (ca.get("abgehakt") or 0) == 1, u"abgehakt=%s" % ca.get("abgehakt"))
pruef(u"die alte Woche ist nach dem naechsten Schreiben verfallen",
      isinstance(cn, dict) and KEY_ALT not in cn, repr(cn))
pruef(u"und nur die zwei bekannten Wochen bleiben stehen",
      isinstance(cn, dict) and set(cn.keys()) <= {KEY_CUR, KEY_NEXT},
      repr(sorted(cn.keys())) if isinstance(cn, dict) else repr(cn))

# ========================================================================================
# Lauf D: Personenzahl - der Haken darf sie ueberleben, die Menge nicht
# ========================================================================================
print(u"")
print(u"--- Lauf D: Personenzahl aendern ---")
rd = lauf(MESS_D)
dv = rd.get("d_vor") or {}
dn = rd.get("d_nach") or {}
dneu = rd.get("d_neu") or {}

print(u"")
print(u"Gemessen:")
print(u"  vorher (1 Person)  " + json.dumps(dv, ensure_ascii=False))
print(u"  nachher (2 Pers.)  " + json.dumps(dn, ensure_ascii=False))
print(u"  neu geoeffnet      " + json.dumps(dneu, ensure_ascii=False))
print(u"")

pruef(u"kein JS-Fehler beim Start (Lauf D)", rd.get("fehler") == "keine", str(rd.get("fehler")))
if rd.get("messfehler"): pruef(u"Messung D lief durch", False, rd["messfehler"])
pruef(u"die Personenzahl laesst sich hochstellen",
      u"2 Personen" in (dn.get("personen") or u""), dn.get("personen"))
pruef(u"der Haken ueberlebt die geaenderte Personenzahl",
      dn.get("abgehakt") == 1, u"abgehakt=%s" % dn.get("abgehakt"))
pruef(u"die MENGE aendert sich dabei sehr wohl",
      dv.get("erste") and dn.get("erste") and dv.get("erste") != dn.get("erste"),
      u"vorher=%r nachher=%r" % (dv.get("erste"), dn.get("erste")))
pruef(u"und der Haken kommt beim Neuoeffnen aus dem Speicher zurueck",
      dneu.get("abgehakt") == 1, u"abgehakt=%s" % dneu.get("abgehakt"))
pruef(u"die Personenzahl ebenfalls",
      u"2 Personen" in (dneu.get("personen") or u""), dneu.get("personen"))

# ========================================================================================
# Lauf E: der PDF-Kopf nennt denselben Zeitraum wie das Modal
# ========================================================================================
print(u"")
print(u"--- Lauf E: PDF-Kopfzeile ---")
re_ = lauf(MESS_E)
ea = pdf_text(re_.get("a_pdf") or u"")
eb = pdf_text(re_.get("b_pdf") or u"")

print(u"")
print(u"Gemessen:")
print(u"  PDF, aktuelle Woche  " + repr(ea))
print(u"  PDF, naechste Woche  " + repr(eb))
print(u"")

pruef(u"kein JS-Fehler beim Start (Lauf E)", re_.get("fehler") == "keine", str(re_.get("fehler")))
if re_.get("messfehler"): pruef(u"Messung E lief durch", False, re_["messfehler"])
pruef(u"die Web Share API ist fuer diesen Lauf abgeschaltet", re_.get("shareAus") is True)
pruef(u"der PDF-Knopf existiert", re_.get("pdfKnopfDa") is True)

# ZUERST: ist ueberhaupt ein PDF entstanden? Ohne diesen Riegel waeren die Zeilen darunter
# auf "(kein PDF erzeugt)" froehlich gruen - eine Zeichenkette, die kein "Diese Woche"
# enthaelt, erfuellt die Nicht-Bedingung ja. Genau die Sorte gruener Zeile, die man glaubt.
def pdf_lesbar(s):
    return bool(s) and u"kein PDF" not in s and u"keine Kopfzeile" not in s

# Der Riegel prueft BEIDE Seiten. Beim ersten Versuch stand hier nur `ea` - dadurch lief
# "das PDF der naechsten Woche sagt NICHT 'Diese Woche'" gruen gegen die Zeichenkette
# "(keine Kopfzeile gefunden)", die das Wort erwartungsgemaess nicht enthaelt. Dieselbe
# Falle, gegen die Lauf C ein eigener Lauf ist.
pdf_da = pdf_lesbar(ea) and pdf_lesbar(eb)
pruef(u"beide PDFs wurden erzeugt und tragen eine Kopfzeile", pdf_da,
      u"a=%r b=%r" % (ea, eb))

if pdf_da:
    pruef(u"das PDF der naechsten Woche nennt SIE",
          u"nächste woche" in eb.lower() or u"naechste woche" in eb.lower(), eb)
    pruef(u"das PDF der naechsten Woche sagt NICHT 'Diese Woche'",
          u"diese woche" not in eb.lower(), eb)
    # Der eigentliche Fund von kvp: In der aktuellen Woche stand "Diese Woche" ueber einer
    # Liste, die nur ab heute rechnet. Der Zeitraum muss dieselbe Einschraenkung tragen wie
    # das Modal - sonst sieht man dem ausgedruckten Blatt nicht an, dass Tage fehlen.
    pruef(u"das PDF der aktuellen Woche verschweigt 'ab heute' nicht",
          (u"ab heute" in ea.lower()) == (u"ab heute" in ka.lower()),
          u"pdf=%r  modal=%r" % (ea, a.get("kicker")))
    pruef(u"PDF und Modal beschreiben denselben Zeitraum",
          ea.lower().strip() == planScope_modal(ka),
          u"pdf=%r  modal=%r" % (ea, a.get("kicker")))

print(u"")
print((u"FEHLGESCHLAGEN: %d von %d" % (bad, ok + bad)) if bad else (u"Alle %d Pruefungen gruen." % ok))
sys.exit(1 if bad else 0)
