# -*- coding: utf-8 -*-
u"""Erzeugt dashboard.html aus plans/app-karte.json - die bildliche Uebersicht der App.

Warum es das gibt
-----------------
ROADMAP.html wurde von Hand gepflegt. Am 20.09.2026 stellte sich heraus, dass eine ihrer
Karten seit ueber einem MONAT falsch war ("Store-Plan Phasen B, C, D - 28 offen"), waehrend
in Wahrheit A/B/C fertig und D1-D6 live waren. Wer danach plante, plante gegen einen Stand,
den es nicht mehr gab.

Deshalb hier die Trennung:

    plans/app-karte.json   die Wahrheit, an EINER Stelle gepflegt
    tools/dashboard.py     macht daraus ein Bild
    dashboard.html         erzeugt, nie von Hand angefasst

Wer etwas aendert, aendert die JSON und faehrt dieses Skript. Wer die HTML bearbeitet,
verliert seine Aenderung beim naechsten Lauf - das ist Absicht.

    python tools/dashboard.py
    python tools/dashboard.py --pruefen   # nur melden, ob die Karte zum Code passt

Ganz oben steht der Netzplan aus "etappen": welche Etappe auf welche wartet. Den Zustand
"kann starten" rechnet das Skript aus; --pruefen meldet Pfeile ins Leere, Kreise und
Fertiges, das auf Offenes wartet.
"""
import io, json, os, re, sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KARTE = os.path.join(WURZEL, "plans", "app-karte.json")
ZIEL = os.path.join(WURZEL, "dashboard.html")

ZEICHEN = {"fertig": u"●", "arbeit": u"◐", "geplant": u"○", "idee": u"△"}
WORT = {"fertig": u"fertig", "arbeit": u"in Arbeit", "geplant": u"geplant", "idee": u"Idee"}


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def reiter_aus_code():
    u"""Welche Reiter kennt index.html wirklich? Die Karte darf nicht danebenliegen."""
    pfad = os.path.join(WURZEL, "index.html")
    if not os.path.exists(pfad):
        return set()
    text = io.open(pfad, encoding="utf-8", errors="replace").read()
    return set(re.findall(r'data-tab="([a-z]+)"', text))


def pruefen(daten):
    u"""Meldet, was zwischen Karte und Code auseinanderlaeuft.

    Die Struktur der Reiter ist die einzige Stelle, an der ein Skript die Karte gegen die
    Wirklichkeit halten kann. Den Status kann es nicht - der ist eine Bewertung.
    """
    befunde = []
    im_code = reiter_aus_code()
    in_karte = {b["id"] for b in daten["bereiche"] if b["art"] == "reiter"}
    for fehlt in sorted(im_code - in_karte):
        befunde.append(u"Reiter '%s' steht im Code, fehlt aber in der Karte." % fehlt)
    for zuviel in sorted(in_karte - im_code):
        befunde.append(u"Reiter '%s' steht in der Karte, aber nicht mehr im Code." % zuviel)
    for b in daten["bereiche"]:
        for f in b["funktionen"]:
            if f.get("status") not in ZEICHEN:
                befunde.append(u"%s / %s: unbekannter Status '%s'"
                               % (b["name"], f["name"], f.get("status")))
            if f.get("phase") not in (1, 2, 3):
                befunde.append(u"%s / %s: unbekannte Phase '%s'"
                               % (b["name"], f["name"], f.get("phase")))
    return befunde + etappen_pruefen(daten)


# ---------------------------------------------------------------------------------------
# Netzplan: die Etappen als Kaestchen mit Pfeilen, von links (frueh) nach rechts (spaet).
#
# Vorbild fuer die Zustaende: Lars Wirzenius, "roadmap visualisation" (2018) -
# https://blog.liw.fi/posts/2018/12/13/roadmap_visualisation/ - fertig / verfuegbar /
# blockiert, je mit eigener Farbe UND eigener Form. Uebernommen: die Idee, "kann starten"
# auszurechnen statt zu pflegen, und keine Termine fuer Offenes. Eigene Loesung statt
# Mermaid/Graphviz: beide waeren ein Fremdpaket bzw. Programm fuer rund 40 Kaestchen.
# ---------------------------------------------------------------------------------------

ETAPPEN_STATUS = ("fertig", "arbeit", "geplant")
ETAPPEN_ART = (None, "meilenstein", "extern")


def etappen_pruefen(daten):
    u"""Pfeile ins Leere, Kreise, und Fertiges, das auf Offenes wartet."""
    etappen = daten.get("etappen", [])
    befunde = []
    ids = [e["id"] for e in etappen]
    nach_id = {e["id"]: e for e in etappen}
    for doppelt in sorted({i for i in ids if ids.count(i) > 1}):
        befunde.append(u"Etappe '%s' gibt es mehrfach." % doppelt)
    funktionen = {f["name"] for b in daten["bereiche"] for f in b["funktionen"]}
    for e in etappen:
        wer = u"Etappe '%s'" % e["id"]
        if e.get("status") not in ETAPPEN_STATUS:
            befunde.append(u"%s: unbekannter Status '%s'" % (wer, e.get("status")))
        if e.get("art") not in ETAPPEN_ART:
            befunde.append(u"%s: unbekannte Art '%s'" % (wer, e.get("art")))
        if e.get("status") == "fertig" and not e.get("am"):
            befunde.append(u"%s ist fertig, aber ohne Datum (am)." % wer)
        if e.get("status") != "fertig" and e.get("am"):
            befunde.append(u"%s hat ein Datum, ist aber nicht fertig." % wer)
        for v in e.get("nach", []):
            if v not in nach_id:
                befunde.append(u"%s wartet auf '%s' - die gibt es nicht." % (wer, v))
            elif e.get("status") in ("fertig", "arbeit") and nach_id[v]["status"] != "fertig":
                befunde.append(u"%s ist '%s', aber '%s' davor ist noch nicht fertig."
                               % (wer, e["status"], v))
        for name in e.get("umfasst", []):
            if name not in funktionen:
                befunde.append(u"%s umfasst '%s' - keine solche Funktion in den Bereichen."
                               % (wer, name))
    if kreis_in(etappen):
        befunde.append(u"Die Etappen warten im Kreis aufeinander: %s"
                       % u" -> ".join(kreis_in(etappen)))
    return befunde


def kreis_in(etappen):
    u"""Gibt einen Kreis als Liste von ids zurueck, sonst eine leere Liste."""
    nach = {e["id"]: [v for v in e.get("nach", [])] for e in etappen}
    farbe = {}

    def tief(k, pfad):
        farbe[k] = 1
        for v in nach.get(k, []):
            if v not in nach:
                continue
            if farbe.get(v) == 1:
                return pfad[pfad.index(v):] + [v] if v in pfad else [k, v]
            if not farbe.get(v):
                r = tief(v, pfad + [v])
                if r:
                    return r
        farbe[k] = 2
        return []

    for k in nach:
        if not farbe.get(k):
            r = tief(k, [k])
            if r:
                return r
    return []


def zustand(e, nach_id):
    u"""fertig | arbeit | bereit (kann starten) | wartet - 'bereit' wird nie gepflegt."""
    if e["status"] in ("fertig", "arbeit"):
        return e["status"]
    if all(nach_id[v]["status"] == "fertig" for v in e.get("nach", []) if v in nach_id):
        return "bereit"
    return "wartet"


NZ_B, NZ_H = 186, 74          # Kaestchen
NZ_SX, NZ_SY = 232, 88        # Abstand von Spalte zu Spalte, von Zeile zu Zeile
NZ_RAND = 14
NZ_ZEICHEN = {"fertig": u"●", "arbeit": u"◐", "bereit": u"○", "wartet": u"○"}
NZ_WORT = {"arbeit": u"läuft", "bereit": u"kann starten", "wartet": u"wartet"}
STRANG_RANG = {None: 0, "store": 1, "markt": 2}


def datum_kurz(iso):
    return u"%s.%s." % (iso[8:10], iso[5:7])


def netzplan_lage(etappen):
    u"""Spalte = laengster Weg vom Start; Zeile = Mittel der Vorgaenger (weniger Kreuzungen)."""
    nach_id = {e["id"]: e for e in etappen}
    spalte = {}

    def stufe(k):
        if k not in spalte:
            vor = [v for v in nach_id[k].get("nach", []) if v in nach_id]
            spalte[k] = 1 + max(stufe(v) for v in vor) if vor else 0
        return spalte[k]

    for e in etappen:
        stufe(e["id"])
    spalten = {}
    for i, e in enumerate(etappen):
        spalten.setdefault(spalte[e["id"]], []).append((i, e))
    hoehe = max(len(v) for v in spalten.values())
    zeile = {}
    for s in sorted(spalten):
        def schluessel(paar):
            i, e = paar
            vor = [zeile[v] for v in e.get("nach", []) if v in zeile]
            mitte = sum(vor) / float(len(vor)) if vor else 0.0
            return (STRANG_RANG.get(e.get("strang"), 0), mitte, i)
        reihe = sorted(spalten[s], key=schluessel)
        versatz = (hoehe - len(reihe)) / 2.0
        for n, (_, e) in enumerate(reihe):
            zeile[e["id"]] = versatz + n
    lage = {k: (NZ_RAND + spalte[k] * NZ_SX, NZ_RAND + zeile[k] * NZ_SY) for k in spalte}
    breite = NZ_RAND * 2 + max(spalte.values()) * NZ_SX + NZ_B
    hoch = NZ_RAND * 2 + (hoehe - 1) * NZ_SY + NZ_H
    return lage, breite, hoch


def netzplan(daten):
    etappen = daten.get("etappen", [])
    if not etappen or kreis_in(etappen):
        return u""
    nach_id = {e["id"]: e for e in etappen}
    fn_nach_name = {f["name"]: f for b in daten["bereiche"] for f in b["funktionen"]}
    lage, breite, hoch = netzplan_lage(etappen)
    zu = {e["id"]: zustand(e, nach_id) for e in etappen}

    pfeile = []
    for e in etappen:
        x2, y2 = lage[e["id"]]
        for v in e.get("nach", []):
            if v not in lage:
                continue
            x1, y1 = lage[v]
            ax, ay = x1 + NZ_B, y1 + NZ_H / 2.0
            bx, by = x2 - 6, y2 + NZ_H / 2.0
            dx = (bx - ax) / 2.0
            art = "ok" if zu[v] == "fertig" else "offen"
            pfeile.append(u'<path class="nz-p %s" d="M%.0f %.0f C%.0f %.0f %.0f %.0f %.0f %.0f" '
                          u'marker-end="url(#nz-spitze-%s)"/>'
                          % (art, ax, ay, ax + dx, ay, bx - dx, by, bx, by, art))

    kaestchen, infos = [], []
    for e in etappen:
        k, z = e["id"], zu[e["id"]]
        x, y = lage[k]
        if z == "fertig":
            unten = datum_kurz(e["am"])
        elif e.get("art") == "extern":
            unten = NZ_WORT[z] + u" · deine Aufgabe"
        else:
            unten = NZ_WORT[z]
        klassen = u"nz-k %s%s" % (z, u" " + e["art"] if e.get("art") else u"")
        kaestchen.append(
            u'<button type="button" class="%s" style="left:%dpx;top:%dpx" data-id="%s" '
            u'aria-expanded="false" aria-controls="nz-i-%s">'
            u'<span class="nz-z" aria-hidden="true">%s</span>'
            u'<span class="nz-n">%s</span><span class="nz-u">%s</span></button>'
            % (klassen, x, y, esc(k), esc(k), NZ_ZEICHEN[z], esc(e["name"]), esc(unten)))

        vor = [nach_id[v] for v in e.get("nach", []) if v in nach_id]
        danach = [d for d in etappen if k in d.get("nach", [])]
        zeilen = []
        if e.get("note"):
            zeilen.append(u'<p class="nz-note">%s</p>' % esc(e["note"]))
        if vor:
            zeilen.append(u'<p><span class="nz-l">Wartet auf</span> %s</p>' % u", ".join(
                u'<span class="nz-ref %s">%s %s</span>'
                % (zu[w["id"]], NZ_ZEICHEN[zu[w["id"]]], esc(w["name"])) for w in vor))
        if danach:
            zeilen.append(u'<p><span class="nz-l">Danach möglich</span> %s</p>' % u", ".join(
                esc(d["name"]) for d in danach))
        fns = [fn_nach_name[n] for n in e.get("umfasst", []) if n in fn_nach_name]
        if fns:
            zeilen.append(u'<ul>%s</ul>' % u"".join(knoten(f) for f in fns))
        status_text = (u"fertig am " + datum_kurz(e["am"]) + e["am"][:4]) if z == "fertig" \
            else NZ_WORT[z]
        infos.append(
            u'<div class="nz-info" id="nz-i-%s" hidden>'
            u'<h3><span class="nz-ref %s">%s</span> %s <small>%s</small></h3>%s</div>'
            % (esc(k), z, NZ_ZEICHEN[z], esc(e["name"]), esc(status_text), u"".join(zeilen)))

    fertig = sum(1 for z in zu.values() if z == "fertig")
    laeuft = [e["name"] for e in etappen if zu[e["id"]] == "arbeit"]
    bereit = [e["name"] for e in etappen if zu[e["id"]] == "bereit"]
    bilanz = u"%d von %d Etappen geschafft" % (fertig, len(etappen))
    if laeuft:
        bilanz += u" · läuft: " + u", ".join(esc(n) for n in laeuft)
    legende = u" ".join(
        u'<span class="nz-ref %s">%s %s</span>' % (z, NZ_ZEICHEN[z], w)
        for z, w in (("fertig", u"fertig"), ("arbeit", u"läuft"),
                     ("bereit", u"kann starten"), ("wartet", u"wartet")))
    return NETZPLAN % {
        "bilanz": bilanz,
        "bereit": u", ".join(esc(n) for n in bereit) or u"—",
        "legende": legende,
        "breite": breite, "hoch": hoch,
        "pfeile": u"\n".join(pfeile),
        "kaestchen": u"\n".join(kaestchen),
        "infos": u"\n".join(infos),
    }


NETZPLAN = u"""
  <section class="nz" aria-labelledby="nz-titel">
    <h2 class="abs" id="nz-titel">Der Weg in den Store<small>Was geschafft ist, was läuft, was als Nächstes geht</small></h2>
    <p class="nz-bilanz">%(bilanz)s</p>
    <p class="nz-bilanz"><strong>Kann jetzt starten:</strong> %(bereit)s</p>
    <div class="legende nz-legende">%(legende)s</div>
    <div class="nz-scroll" tabindex="0" aria-label="Netzplan, seitlich verschiebbar">
      <div class="nz-flaeche" style="width:%(breite)dpx;height:%(hoch)dpx">
        <svg class="nz-svg" width="%(breite)d" height="%(hoch)d" aria-hidden="true">
          <defs>
            <marker id="nz-spitze-ok" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L8 4 L0 8 z" style="fill:var(--ok)"/></marker>
            <marker id="nz-spitze-offen" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L8 4 L0 8 z" style="fill:var(--border-strong)"/></marker>
          </defs>
%(pfeile)s
        </svg>
%(kaestchen)s
      </div>
    </div>
    <div class="nz-infos" aria-live="polite">
      <p class="nz-tipp">Tippe auf ein Kästchen für die Einzelheiten.</p>
%(infos)s
    </div>
  </section>
"""

NETZPLAN_CSS = u"""
  /* ---- Netzplan ---- */
  .nz-bilanz { margin: -4px 0 4px; font-size: 13px; color: var(--text-muted); }
  .nz-bilanz strong { color: var(--text); font-weight: 600; }
  .nz-legende { margin: 8px 0 12px; }
  .nz-scroll { overflow-x: auto; border: 1px solid var(--border); border-radius: var(--radius);
               background: var(--surface-2); }
  .nz-scroll:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .nz-flaeche { position: relative; }
  .nz-svg { position: absolute; inset: 0; }
  .nz-p { fill: none; stroke-width: 1.6; }
  .nz-p.ok { stroke: var(--ok); opacity: .55; }
  .nz-p.offen { stroke: var(--border-strong); stroke-dasharray: 4 4; }

  .nz-k { position: absolute; width: 186px; height: 74px; padding: 7px 10px 7px 26px;
          text-align: left; font: inherit; color: var(--text); cursor: pointer;
          background: var(--surface); border: 1px solid var(--border);
          border-radius: var(--radius-sm); display: flex; flex-direction: column;
          justify-content: center; gap: 1px; transition: transform .12s ease; }
  .nz-k:active { transform: scale(.97); }
  .nz-k:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .nz-k[aria-expanded="true"] { box-shadow: 0 0 0 2px var(--text); }
  .nz-z { position: absolute; left: 9px; top: 8px; font-size: 11px; }
  .nz-n { font-size: 13px; line-height: 1.25; font-weight: 600; overflow: hidden;
          display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
          hyphens: auto; overflow-wrap: anywhere; }
  .nz-u { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums;
          white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  .nz-k.fertig { border-color: color-mix(in srgb, var(--ok) 55%, transparent);
                 background: color-mix(in srgb, var(--ok) 12%, var(--surface)); }
  .nz-k.fertig .nz-z { color: var(--ok); }
  .nz-k.arbeit { border: 2px solid var(--accent);
                 background: color-mix(in srgb, var(--accent) 12%, var(--surface)); }
  .nz-k.arbeit .nz-z, .nz-k.arbeit .nz-u { color: var(--accent-strong); font-weight: 600; }
  .nz-k.bereit { border: 2px solid var(--text-muted); }
  .nz-k.bereit .nz-u { color: var(--text); font-weight: 600; }
  .nz-k.wartet { border-style: dashed; background: var(--surface-2); }
  .nz-k.wartet .nz-n, .nz-k.wartet .nz-z { color: var(--text-muted); font-weight: 500; }
  .nz-k.meilenstein { border-radius: 99px; padding-left: 30px; }
  .nz-k.meilenstein .nz-z { left: 13px; }
  .nz-k.meilenstein .nz-n { font-family: var(--font-display); font-weight: 800; }
  .nz-k.extern .nz-u { font-style: italic; }

  .nz-ref.fertig { color: var(--ok); }
  .nz-ref.arbeit { color: var(--accent-strong); }
  .nz-ref.bereit { color: var(--text); }
  .nz-ref.wartet { color: var(--text-muted); }

  .nz-infos { margin: 12px 0 34px; }
  .nz-tipp { margin: 0; font-size: 12.5px; color: var(--text-muted); }
  .nz-info { background: var(--surface); border: 1px solid var(--border);
             border-radius: var(--radius); padding: 13px 15px; font-size: 13.5px; }
  .nz-info h3 { font-family: var(--font-display); font-size: 16px; margin: 0 0 6px; }
  .nz-info h3 small { font-family: var(--font-body); font-weight: 500; font-size: 12px;
                      color: var(--text-muted); margin-left: 6px; }
  .nz-info p { margin: 0 0 6px; }
  .nz-note { color: var(--text-muted); }
  .nz-l { display: inline-block; min-width: 118px; font-size: 12px; color: var(--text-muted); }
  .nz-info ul { list-style: none; margin: 8px 0 0; padding: 0; }
  @media (max-width: 560px) { .nz-l { display: block; } }
  @media (prefers-reduced-motion: reduce) { .nz-k { transition: none; } }
"""

NETZPLAN_JS = u"""
<script>
(function () {
  var flaeche = document.querySelector(".nz-flaeche");
  if (!flaeche) return;
  var tipp = document.querySelector(".nz-tipp");
  var offen = null;
  flaeche.addEventListener("click", function (ev) {
    var k = ev.target.closest(".nz-k");
    if (!k) return;
    var info = document.getElementById("nz-i-" + k.dataset.id);
    if (offen) { offen.k.setAttribute("aria-expanded", "false"); offen.info.hidden = true; }
    if (offen && offen.k === k) { offen = null; tipp.hidden = false; return; }
    k.setAttribute("aria-expanded", "true"); info.hidden = false; tipp.hidden = true;
    offen = { k: k, info: info };
  });
  // Beim Oeffnen dorthin schieben, wo es gerade weitergeht - der Anfang liegt links davon.
  var jetzt = flaeche.querySelector(".nz-k.arbeit") || flaeche.querySelector(".nz-k.bereit");
  if (jetzt) flaeche.parentNode.scrollLeft = Math.max(0, jetzt.offsetLeft - 2 * %(schritt)d);
})();
</script>
"""


def knoten(f):
    st = f.get("status", "geplant")
    note = f.get("note", "")
    seit = f.get("seit", "")
    titel = esc(note) if note else ""
    zusatz = u'<span class="seit">%s</span>' % esc(seit[-5:].replace("-", ".")) if seit else ""
    return (u'<li class="fn %s"%s><span class="pt">%s</span>'
            u'<span class="nm">%s</span>%s%s</li>'
            % (st,
               u' title="%s"' % titel if titel else "",
               ZEICHEN[st], esc(f["name"]), zusatz,
               u'<span class="note">%s</span>' % esc(note) if note else ""))


def spalte(b):
    return (u'<div class="sp %s" id="b-%s">\n'
            u'  <div class="kopf"><h3>%s</h3><p>%s</p></div>\n'
            u'  <ul>\n%s\n  </ul>\n</div>'
            % (b["art"], esc(b["id"]), esc(b["name"]), esc(b.get("beschreibung", "")),
               "\n".join("    " + knoten(f) for f in b["funktionen"])))


def balken(funktionen):
    ges = len(funktionen)
    fertig = sum(1 for f in funktionen if f["status"] == "fertig")
    proz = int(round(100.0 * fertig / ges)) if ges else 0
    return fertig, ges, proz


def bauen(daten):
    bereiche = daten["bereiche"]
    hole = lambda art: [b for b in bereiche if b["art"] == art]
    alle_fn = [f for b in bereiche for f in b["funktionen"]]

    teile = []
    for art, ueberschrift, hinweis, fluss in (
            ("reiter", u"Die vier Reiter", u"Was der Nutzer sieht und antippt", True),
            ("quer", u"Quer durch alles", u"Gehört zu keinem einzelnen Reiter", False)):
        teile.append(u'<h2 class="abs">%s<small>%s</small></h2>' % (ueberschrift, hinweis))
        if fluss:
            # Der Stamm gehoert unmittelbar ueber die Reiter, sonst zeigt die Linie ins Leere.
            teile.append(u'<div class="stamm">Paddy&rsquo;s Mealplan'
                         u'<small>Wochen-Essensplaner · kein Kalorien-Tracker</small></div>')
        teile.append(u'<div class="reihe%s">%s</div>'
                     % (" fluss" if fluss else "", "\n".join(spalte(b) for b in hole(art))))

    phasen_html = []
    for nr in ("2", "3"):
        p = daten["phasen"][nr]
        art = "phase" + nr
        spalten = hole(art)
        if not spalten:
            continue
        fn = [f for b in spalten for f in b["funktionen"]]
        fertig, ges, proz = balken(fn)
        phasen_html.append(
            u'<section class="phase p%s">\n'
            u'  <h2 class="abs">Phase %s · %s'
            u'<small>%s</small></h2>\n'
            u'  <p class="bilanz">%d von %d erledigt</p>\n'
            u'  <div class="reihe">%s</div>\n</section>'
            % (nr, nr, esc(p["name"]), esc(p["leitsatz"]), fertig, ges,
               "\n".join(spalte(b) for b in spalten)))

    p1 = [f for f in alle_fn if f["phase"] == 1]
    f1, g1, proz1 = balken(p1)
    offen1 = [f for f in p1 if f["status"] != "fertig"]

    legende = " ".join(
        u'<span class="lg %s">%s %s</span>' % (k, ZEICHEN[k], WORT[k])
        for k in ("fertig", "arbeit", "geplant", "idee"))

    offen_liste = "\n".join(
        u'      <li><span class="pt %s">%s</span> %s</li>'
        % (f["status"], ZEICHEN[f["status"]], esc(f["name"]))
        for f in offen1)

    return VORLAGE % {
        "netzplan": netzplan(daten),
        "netzplan_css": NETZPLAN_CSS,
        "netzplan_js": NETZPLAN_JS % {"schritt": NZ_SX} if daten.get("etappen") else u"",
        "legende": legende,
        "proz1": proz1, "f1": f1, "g1": g1,
        "leitsatz1": esc(daten["phasen"]["1"]["leitsatz"]),
        "offen_anzahl": len(offen1),
        "offen_liste": offen_liste,
        "inhalt": "\n".join(teile),
        "phasen": "\n".join(phasen_html),
        "gesamt": len(alle_fn),
    }


VORLAGE = u"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Paddy's Mealplan — Dashboard</title>
<style>
  :root {
    --bg: #14100F; --surface: #1D1817; --surface-2: #241E1D;
    --text: #F4EFEE; --text-muted: #A99C99;
    --border: #2E2726; --border-strong: #3A2F30;
    --accent: #FF3040; --accent-strong: #FF5A66;
    --ok: #4ADE80; --radius: 14px; --radius-sm: 9px;
    --font-display: ui-rounded, "SF Pro Rounded", system-ui, sans-serif;
    --font-body: system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  @media (prefers-color-scheme: light) {
    :root:not([data-theme="dark"]) {
      --bg: #FAF7F7; --surface: #FFFFFF; --surface-2: #F3EFEF;
      --text: #1A1416; --text-muted: #6B5F5D;
      --border: #E4DDDC; --border-strong: #CFC5C4; --ok: #16A34A;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 30px 22px 70px; background: var(--bg); color: var(--text);
    font-family: var(--font-body); font-size: 15px; line-height: 1.55;
  }
  .wrap { max-width: 1180px; margin: 0 auto; }

  header { display: flex; align-items: center; gap: 15px; margin-bottom: 6px; }
  .mark {
    flex: none; width: 46px; height: 46px; border-radius: 50%%;
    background: linear-gradient(135deg, var(--accent), var(--accent-strong));
    color: #fff; display: grid; place-items: center;
    font-family: var(--font-display); font-weight: 800; letter-spacing: .5px;
  }
  h1 { font-family: var(--font-display); font-size: 27px; margin: 0; letter-spacing: -.4px; }
  .slogan { color: var(--text-muted); font-size: 13px; }

  .erzeugt {
    margin: 14px 0 26px; padding: 10px 13px; border-radius: var(--radius-sm);
    background: var(--surface); border: 1px solid var(--border);
    color: var(--text-muted); font-size: 12.5px;
  }
  .erzeugt code { color: var(--text); }

  /* ---- Der Stamm oben: die App selbst ---- */
  .stamm {
    text-align: center; margin: 0 auto 4px; padding: 15px 20px; max-width: 420px;
    background: linear-gradient(135deg, var(--accent), var(--accent-strong));
    color: #fff; border-radius: var(--radius); font-family: var(--font-display);
    font-size: 19px; font-weight: 700;
  }
  .stamm small { display: block; font-size: 12px; font-weight: 500; opacity: .9;
                 font-family: var(--font-body); }
  .stamm + .reihe.fluss { padding-top: 30px; }
  .stamm + .reihe.fluss::before { top: 15px; }
  .stamm + .reihe.fluss .sp::before { top: -16px; height: 16px; }

  .fortschritt { margin: 0 0 30px; }
  .bar { height: 9px; border-radius: 99px; background: var(--surface-2);
         border: 1px solid var(--border); overflow: hidden; }
  .bar > i { display: block; height: 100%%;
             background: linear-gradient(90deg, var(--ok), var(--accent-strong)); }
  .bar-txt { display: flex; justify-content: space-between; font-size: 12.5px;
             color: var(--text-muted); margin-bottom: 6px; }

  h2.abs {
    font-family: var(--font-display); font-size: 13px; text-transform: uppercase;
    letter-spacing: .09em; color: var(--text-muted); font-weight: 700;
    margin: 34px 0 13px; padding-bottom: 7px; border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: baseline; gap: 12px;
  }
  h2.abs small { text-transform: none; letter-spacing: 0; font-weight: 500; font-size: 12px; }

  .reihe { display: grid; gap: 13px; grid-template-columns: repeat(auto-fit, minmax(235px, 1fr)); }

  /* Der Fluss vom Stamm zu den vier Reitern. Die Querlinie endet in der MITTE der
     aeusseren Spalten, nicht am Rand - sonst laeuft sie ins Leere. Bei vier Spalten
     liegt diese Mitte bei 1/8 und 7/8 der Breite. */
  .reihe.fluss { position: relative; padding-top: 25px; }
  .reihe.fluss::before {
    content: ""; position: absolute; top: 12px; left: 12.5%%; right: 12.5%%;
    height: 2px; background: var(--border-strong);
  }
  .reihe.fluss .sp { position: relative; }
  .reihe.fluss .sp::before {
    content: ""; position: absolute; top: -13px; left: 50%%; width: 2px; height: 13px;
    background: var(--border-strong);
  }
  /* Sobald die Spalten umbrechen, stimmt die Rechnung nicht mehr - dann lieber keine
     Linie als eine falsche. */
  @media (max-width: 1010px) {
    .reihe.fluss { padding-top: 0; }
    .reihe.fluss::before, .reihe.fluss .sp::before { display: none; }
  }

  .sp { background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 14px 15px; }
  .sp.reiter { border-top: 3px solid var(--accent); }
  .sp.quer   { border-top: 3px solid var(--border-strong); }
  .kopf h3 { font-family: var(--font-display); font-size: 16.5px; margin: 0 0 2px; }
  .kopf p { margin: 0 0 11px; font-size: 12.5px; color: var(--text-muted); line-height: 1.4; }

  .sp ul { list-style: none; margin: 0; padding: 0; }
  .fn { display: grid; grid-template-columns: 17px 1fr auto; gap: 2px 7px;
        align-items: baseline; padding: 4px 0; font-size: 13.5px;
        border-top: 1px solid var(--border); }
  .fn:first-child { border-top: 0; }
  .pt { font-size: 11px; line-height: 1.5; }
  .nm { min-width: 0; }
  .seit { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
  .note { grid-column: 2 / -1; font-size: 11.5px; color: var(--text-muted);
          line-height: 1.4; padding-bottom: 2px; }

  .fn.fertig .pt  { color: var(--ok); }
  .fn.arbeit .pt  { color: var(--accent-strong); }
  .fn.geplant .pt { color: var(--text-muted); }
  .fn.idee .pt    { color: var(--text-muted); opacity: .75; }
  .fn.geplant .nm, .fn.idee .nm { color: var(--text-muted); }
  .fn.idee .nm { font-style: italic; }

  .legende { display: flex; flex-wrap: wrap; gap: 14px; font-size: 12.5px;
             color: var(--text-muted); margin: 10px 0 0; }
  .lg.fertig  { color: var(--ok); }
  .lg.arbeit  { color: var(--accent-strong); }

  .jetzt { background: var(--surface-2); border: 1px solid var(--border-strong);
           border-radius: var(--radius); padding: 15px 17px; margin: 26px 0 0; }
  .jetzt h3 { font-family: var(--font-display); margin: 0 0 3px; font-size: 17px; }
  .jetzt > p { margin: 0 0 11px; color: var(--text-muted); font-size: 13px; }
  .jetzt ul { list-style: none; margin: 0; padding: 0;
              columns: 2; column-gap: 24px; font-size: 13.5px; }
  .jetzt li { break-inside: avoid; padding: 3px 0; }

  .phase { margin-top: 42px; }
  .phase.p2 { opacity: .62; }
  .phase.p3 { opacity: .78; }
  .phase .sp { border-top-color: var(--border-strong); }
  .bilanz { margin: -6px 0 13px; font-size: 12.5px; color: var(--text-muted); }

  footer { margin-top: 44px; padding-top: 15px; border-top: 1px solid var(--border);
           color: var(--text-muted); font-size: 12px; }

  @media (max-width: 560px) {
    body { padding: 20px 13px 48px; }
    h1 { font-size: 23px; }
    .jetzt ul { columns: 1; }
    /* Nebeneinander bricht die Bilanz mitten im Satz um - untereinander liest sie sich. */
    .bar-txt { flex-direction: column; gap: 2px; }
    h2.abs { flex-direction: column; gap: 1px; }
  }
%(netzplan_css)s
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div class="mark">PM</div>
    <div>
      <h1>Dashboard</h1>
      <div class="slogan">Plan it. Cook it. Lift it.</div>
    </div>
  </header>

  <p class="erzeugt">
    <strong>Erzeugt, nicht gepflegt.</strong> Diese Seite entsteht aus
    <code>plans/app-karte.json</code> über <code>python tools/dashboard.py</code>.
    Wer hier hineinschreibt, verliert es beim nächsten Lauf — Änderungen gehören in die
    JSON. %(gesamt)s Funktionen erfasst.
  </p>
%(netzplan)s

  <div class="fortschritt">
    <div class="bar-txt">
      <span><strong>Phase 1 — die App fertig machen</strong> · %(leitsatz1)s</span>
      <span>%(f1)d / %(g1)d</span>
    </div>
    <div class="bar" role="img" aria-label="%(f1)d von %(g1)d erledigt"><i style="width:%(proz1)d%%"></i></div>
    <div class="legende">%(legende)s</div>
  </div>

%(inhalt)s

  <div class="jetzt">
    <h3>Was in Phase 1 noch offen ist</h3>
    <p>%(offen_anzahl)d Punkte. Alles andere wartet — bewusst.</p>
    <ul>
%(offen_liste)s
    </ul>
  </div>

%(phasen)s

  <footer>
    Paddy&rsquo;s Mealplan — privates Dashboard. Nicht im Repo, nicht auf Pages.
  </footer>

</div>
%(netzplan_js)s
</body>
</html>
"""


def main():
    if not os.path.exists(KARTE):
        print(u"plans/app-karte.json fehlt.")
        return 2
    daten = json.load(io.open(KARTE, encoding="utf-8"))

    befunde = pruefen(daten)
    for b in befunde:
        print(u"  BEFUND: %s" % b)

    if "--pruefen" in sys.argv:
        if not befunde:
            print(u"Karte und Code passen zusammen.")
        return 1 if befunde else 0

    io.open(ZIEL, "w", encoding="utf-8", newline="\n").write(bauen(daten))
    anzahl = sum(len(b["funktionen"]) for b in daten["bereiche"])
    print(u"dashboard.html erzeugt - %d Bereiche, %d Funktionen."
          % (len(daten["bereiche"]), anzahl))
    return 1 if befunde else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
