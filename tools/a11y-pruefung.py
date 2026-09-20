# -*- coding: utf-8 -*-
u"""A11y-Pruefung fuer Paddy's Mealplan - die Haelfte, die `abnahme-mobil.py` NICHT misst.

`tools/abnahme-mobil.py` misst die *sichtbare* Seite: Ueberlauf, Trefferflaechen, Schriftgroesse,
Kontrast. Das deckt WCAG 1.4.3, 1.4.4 und 2.5.5/2.5.8 ab. Diese Pruefung deckt die andere
Haelfte ab, die man mit blossem Auge nicht sieht:

  1. Name fehlt          (WCAG 4.1.2) - ein Knopf, den ein Screenreader nur "Schaltflaeche" nennt
  2. Eingabe ohne Label  (WCAG 3.3.2) - Platzhaltertext ist KEIN Label
  3. Bild ohne alt       (WCAG 1.1.1)
  4. Nicht per Tab erreichbar (WCAG 2.1.1) - bedienbar nur mit Maus/Geste
  5. Fokus unsichtbar    (WCAG 2.4.7) - man sieht nicht, wo man ist
  6. Ueberschriftensprung (WCAG 1.3.1)
  7. aria-hidden-Falle   (WCAG 4.1.2) - fokussierbar, aber fuer den Screenreader nicht da
  8. Seitengeruest       (WCAG 2.4.2, 3.1.1) - Titel und lang-Attribut

Anlass: Phase E4 (BFSG). Das Barrierefreiheitsstaerkungsgesetz greift an dem Tag, an dem Geld
fliesst - Massstab ist EN 301 549, die auf WCAG 2.1 AA verweist.

    python tools/a11y-pruefung.py                 # voller Durchlauf
    python tools/a11y-pruefung.py --gegenprobe    # misst sich selbst
    python tools/a11y-pruefung.py --schnell       # nur eine Breite, nur Dark

Braucht `test-server.ps1` auf Port 8000. Eigenes Chrome-Profil, bewusst NICHT angemeldet.

Warum kein zweites Geruest: Sitzung, Onboarding-Automat und Stationsweg stecken bereits in
`abnahme-mobil.py` und haben dort ihre eigene Gegenprobe. Ein Nachbau waere genau der Fehler,
vor dem CLAUDE.md Abschnitt 11 warnt - er wuerde bald etwas anderes fahren als die Abnahme.
"""
import argparse, importlib.util, os, sys, time

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _abnahme_laden():
    u"""Laedt abnahme-mobil.py als Modul. Der Bindestrich verbietet ein normales import."""
    pfad = os.path.join(WURZEL, "tools", "abnahme-mobil.py")
    spec = importlib.util.spec_from_file_location("abnahme_mobil", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


AM = _abnahme_laden()

# --------------------------------------------------------------------- Messung ---
# Teil 1: alles, was ohne Tastendruck messbar ist. Laeuft im Browser.
MESSEN_STATISCH = r"""(() => {
  const sichtbar = e => {
    const st = getComputedStyle(e);
    if (st.display === 'none' || st.visibility === 'hidden' || +st.opacity === 0) return false;
    const r = e.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const pfad = e => {
    let p = [], n = e, tiefe = 0;
    while (n && n.nodeType === 1 && tiefe++ < 4) {
      let t = n.tagName.toLowerCase();
      if (n.id) { p.unshift(t + '#' + n.id); break; }
      const k = (typeof n.className === 'string' ? n.className : '').trim().split(/\s+/).filter(Boolean).slice(0,2).join('.');
      p.unshift(k ? t + '.' + k : t);
      n = n.parentElement;
    }
    return p.join(' > ');
  };
  const txt = e => (e.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40);

  // Der zugaengliche Name, so wie ihn ein Screenreader bildet - vereinfacht, aber in der
  // Reihenfolge, die die Accessible Name Computation vorgibt.
  const name = e => {
    const b = e.getAttribute('aria-labelledby');
    if (b) {
      const s = b.split(/\s+/).map(id => {
        const z = document.getElementById(id);
        return z ? (z.textContent || '').trim() : '';
      }).join(' ').trim();
      if (s) return s;
    }
    const l = (e.getAttribute('aria-label') || '').trim();
    if (l) return l;
    if (e.tagName === 'INPUT' || e.tagName === 'SELECT' || e.tagName === 'TEXTAREA') {
      if (e.id) {
        const lab = document.querySelector('label[for="' + CSS.escape(e.id) + '"]');
        if (lab && (lab.textContent || '').trim()) return (lab.textContent || '').trim();
      }
      const um = e.closest('label');
      if (um && (um.textContent || '').trim()) return (um.textContent || '').trim();
      // `value` traegt nur bei Knopf-artigen Eingaben einen Namen, nicht bei Textfeldern.
      if (['submit','button','reset'].includes(e.type) && (e.value || '').trim()) return e.value.trim();
    }
    const t = (e.textContent || '').trim();
    if (t) return t;
    // Ein Bild im Knopf darf den Namen stellen - ueber sein alt.
    const bild = e.querySelector('img[alt]:not([alt=""])');
    if (bild) return bild.getAttribute('alt').trim();
    const ti = (e.getAttribute('title') || '').trim();
    if (ti) return ti;
    return '';
  };

  const alle = [...document.querySelectorAll('body *')].filter(sichtbar);

  const istBedienbar = e => {
    const t = e.tagName.toLowerCase();
    if (['button','a','select','textarea','summary'].includes(t)) return true;
    if (t === 'input') return !['hidden'].includes(e.type);
    const r = e.getAttribute('role');
    if (['button','tab','link','checkbox','switch','menuitem'].includes(r)) return true;
    if (e.hasAttribute('data-action') || e.hasAttribute('data-tab')) return true;
    return false;
  };
  const bedienbar = alle.filter(istBedienbar).filter(e => !e.disabled);

  // 1. Name fehlt (4.1.2)
  const ohneNamen = bedienbar.filter(e => {
    if (e.getAttribute('aria-hidden') === 'true') return false;   // zaehlt unter 7.
    if (e.tagName === 'A' && !e.hasAttribute('href') && !e.hasAttribute('data-action')) return false;
    return name(e) === '';
  }).map(e => ({ pfad: pfad(e), tag: e.tagName.toLowerCase(),
                 rolle: e.getAttribute('role') || '', aktion: e.getAttribute('data-action') || '' })).slice(0, 15);

  // 2. Eingabe ohne Label (3.3.2). Ein Platzhalter ist KEIN Label: er verschwindet beim Tippen
  //    und wird von manchen Screenreadern gar nicht gelesen.
  const ohneLabel = alle.filter(e => ['INPUT','SELECT','TEXTAREA'].includes(e.tagName))
    .filter(e => !['hidden','submit','button','reset'].includes(e.type))
    // Ein Feld, das fuer die Hilfstechnik gar nicht da ist, braucht auch keinen Namen.
    // So sind photoInput/avatarInput gesetzt: ausgeloest nur ueber .click(), nie bedient.
    .filter(e => !e.closest('[aria-hidden="true"]'))
    .filter(e => name(e) === '')
    .map(e => ({ pfad: pfad(e), typ: e.type || e.tagName.toLowerCase(),
                 platzhalter: (e.getAttribute('placeholder') || '').slice(0, 30) })).slice(0, 15);

  // 3. Bild ohne alt (1.1.1). alt="" ist erlaubt und richtig fuer reine Deko - fehlt es ganz,
  //    liest der Screenreader den Dateinamen vor.
  const ohneAlt = alle.filter(e => e.tagName === 'IMG' && !e.hasAttribute('alt'))
    .map(e => ({ pfad: pfad(e), quelle: (e.getAttribute('src') || '').slice(-40) })).slice(0, 15);

  // 4. Nicht per Tab erreichbar (2.1.1). Ein div mit data-action ist fuer die Maus bedienbar
  //    und fuer die Tastatur unsichtbar, solange es kein tabindex traegt.
  const nativFokussierbar = e => ['button','a','input','select','textarea','summary'].includes(e.tagName.toLowerCase())
    && !(e.tagName === 'A' && !e.hasAttribute('href'));
  const nichtErreichbar = bedienbar.filter(e => {
    if (e.getAttribute('aria-hidden') === 'true') return false;
    const ti = e.getAttribute('tabindex');
    if (ti !== null) return parseInt(ti, 10) < 0;
    return !nativFokussierbar(e);
  }).map(e => ({ pfad: pfad(e), text: txt(e), tag: e.tagName.toLowerCase(),
                 aktion: e.getAttribute('data-action') || '' })).slice(0, 15);

  // 6. Ueberschriftensprung (1.3.1). h1 -> h3 laesst einen Screenreader-Nutzer raten, ob er
  //    eine Ebene verpasst hat.
  const ueber = alle.filter(e => /^H[1-6]$/.test(e.tagName));
  const spruenge = [];
  let vorher = 0;
  for (const h of ueber) {
    const n = +h.tagName[1];
    if (vorher && n > vorher + 1) spruenge.push({ pfad: pfad(h), von: 'h' + vorher, nach: 'h' + n, text: txt(h) });
    vorher = n;
  }

  // 7. aria-hidden-Falle: fokussierbar, aber fuer die Hilfstechnik nicht vorhanden. Der Fokus
  //    landet auf etwas, das der Screenreader nicht ansagen kann.
  const ariaFalle = alle.filter(e => {
    if (e.closest('[aria-hidden="true"]') === null) return false;
    const ti = e.getAttribute('tabindex');
    // tabindex="-1" ist die RICHTIGE Loesung neben aria-hidden, keine Falle: Das Element
    // ist dann weder im Tabweg noch in der Vorleseansage. Die Falle ist der umgekehrte
    // Fall - aria-hidden gesetzt, aber fokussierbar geblieben.
    if (ti !== null) return parseInt(ti, 10) >= 0;
    return nativFokussierbar(e) && !e.disabled;
  }).map(e => ({ pfad: pfad(e), text: txt(e) })).slice(0, 15);

  // 8. Seitengeruest (2.4.2, 3.1.1) - einmal pro Lauf, nicht pro Station, deshalb billig.
  const geruest = [];
  if (!(document.title || '').trim()) geruest.push({ pfad: 'title', was: 'Seitentitel fehlt' });
  const lang = (document.documentElement.getAttribute('lang') || '').trim();
  if (!lang) geruest.push({ pfad: 'html', was: 'lang-Attribut fehlt' });
  else if (!/^de/i.test(lang)) geruest.push({ pfad: 'html', was: 'lang ist "' + lang + '", die App ist deutsch' });

  return { ohneNamen, ohneLabel, ohneAlt, nichtErreichbar, spruenge, ariaFalle, geruest };
})()"""


# Teil 2: der Fokusring. Nur ueber echte Tab-Tastendruecke messbar - `:focus-visible` haengt
# an der Eingabemodalitaet, und die kennt der Browser nur, wenn wirklich getippt wurde.
MESSEN_FOKUS = r"""(() => {
  const e = document.activeElement;
  if (!e || e === document.body || e === document.documentElement) return null;
  // Der Rundlauf wird am ELEMENT erkannt, nicht am Pfad-Text. Zwei Knoepfe im selben
  // Container tragen denselben Pfad - wer darauf abbricht, haelt nach sechs Schritten an
  // und meldet den Rest der Seite als "ohne Befund" (gefunden in der Gegenprobe, 20.09.2026).
  const schon = e.hasAttribute('data-a11y-besucht');
  e.setAttribute('data-a11y-besucht', '1');
  const pfad = n => {
    let p = [], t = 0;
    while (n && n.nodeType === 1 && t++ < 4) {
      let g = n.tagName.toLowerCase();
      if (n.id) { p.unshift(g + '#' + n.id); break; }
      const k = (typeof n.className === 'string' ? n.className : '').trim().split(/\s+/).filter(Boolean).slice(0,2).join('.');
      p.unshift(k ? g + '.' + k : g);
      n = n.parentElement;
    }
    return p.join(' > ');
  };
  // Der Ring sitzt in diesem Projekt an DREI Orten, nicht nur am Element selbst:
  //   .rcard-open:focus-visible::after { outline: 2px solid var(--accent) }   -> Pseudoelement
  //   .wch-pt:focus-visible .wch-dot   { r: 6; stroke: ... }                  -> Kind
  //   input:focus                      { border-color; box-shadow }           -> Element
  // Wer nur das Element misst, meldet zwei gut geloeste Stellen als Fehler - und laesst
  // Code "reparieren", der stimmt (Fehlalarm-Runde am 20.09.2026, vor der ersten Behebung).
  const teil = (n, pseudo) => {
    const st = getComputedStyle(n, pseudo || null);
    return [st.outlineStyle, st.outlineWidth, st.outlineColor, st.boxShadow,
            st.borderColor, st.borderWidth, st.backgroundColor,
            st.stroke, st.fill, st.r, st.opacity].join('|');
  };
  const ring = n => {
    const stuecke = [teil(n, null), teil(n, '::after'), teil(n, '::before')];
    // Kinder bis zwei Ebenen tief, gedeckelt - ein SVG-Punkt liegt in `g > circle`.
    const kinder = [...n.querySelectorAll('*')].slice(0, 12);
    for (const k of kinder) stuecke.push(teil(k, null));
    const st = getComputedStyle(n);
    return { alles: stuecke.join('#'),
             umriss: st.outlineStyle + ' ' + st.outlineWidth + ' ' + st.outlineColor,
             schatten: st.boxShadow };
  };
  // Der Vergleich ist der Kern: Ein Element, das IMMER einen Schatten traegt, hat deshalb noch
  // lange keinen Fokusring. Gemessen wird der UNTERSCHIED zwischen fokussiert und nicht.
  // Uebergaenge fuer die Dauer der Messung stilllegen. `input` traegt
  // `transition: border-color, box-shadow` - gemessen wird sonst der Wert am ANFANG der
  // Animation, und der ist noch der ungefokussierte. Ein sauberer Fokusring galt damit als
  // fehlend (20.09.2026). Der Stil fliegt am Ende wieder raus, sichtbar aendert sich nichts.
  const _stil = document.createElement('style');
  _stil.textContent = '*, *::before, *::after { transition: none !important; animation: none !important; }';
  document.head.appendChild(_stil);
  const mit = ring(e);
  e.blur();
  const ohne = ring(e);
  e.focus({ preventScroll: true });
  _stil.remove();
  const anders = mit.alles !== ohne.alles;
  const r = e.getBoundingClientRect();
  return {
    pfad: pfad(e),
    schonBesucht: schon,
    text: (e.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40),
    sichtbar: r.width > 0 && r.height > 0,
    imBild: r.top >= -2 && r.bottom <= (document.documentElement.clientHeight + 2),
    ringSichtbar: anders,
    mit: mit, ohne: ohne
  };
})()"""

ARTEN = [
    ("ohneNamen",      u"Name fehlt (4.1.2)"),
    ("ohneLabel",      u"Eingabe ohne Label (3.3.2)"),
    ("ohneAlt",        u"Bild ohne alt (1.1.1)"),
    ("nichtErreichbar", u"nicht per Tab erreichbar (2.1.1)"),
    ("ohneRing",       u"Fokus unsichtbar (2.4.7)"),
    ("spruenge",       u"Ueberschriftensprung (1.3.1)"),
    ("ariaFalle",      u"aria-hidden-Falle (4.1.2)"),
    ("geruest",        u"Seitengeruest (2.4.2, 3.1.1)"),
]


def tab_weg(s, schritte=90):
    u"""Geht die Seite mit der Tab-Taste ab und meldet, wo der Fokus unsichtbar bleibt.

    Warum echte Tastendruecke und kein `el.focus()` in einer Schleife: `:focus-visible` greift
    nur, wenn der Browser die Eingabe fuer eine Tastatureingabe haelt. Wer programmatisch
    fokussiert, misst einen Ring, den ein echter Nutzer nie zu sehen bekommt - oder anders
    herum meldet er einen fehlenden, den es gibt.
    """
    ohne_ring, reihenfolge, leer = [], [], 0
    # Markierungen einer frueheren Station wegraeumen, sonst gilt der Weg sofort als gelaufen.
    s.js("document.querySelectorAll('[data-a11y-besucht]').forEach(e=>e.removeAttribute('data-a11y-besucht'));"
         "document.body.focus()")
    for _ in range(schritte):
        for art in ("keyDown", "keyUp"):
            s.senden("Input.dispatchKeyEvent", {"type": art, "key": "Tab", "code": "Tab",
                                                "windowsVirtualKeyCode": 9, "nativeVirtualKeyCode": 9})
        time.sleep(0.05)
        m = s.js(MESSEN_FOKUS)
        if not m:
            # Der Fokus kann kurz in die Browser-Oberflaeche wandern. Einmal ist normal,
            # dreimal hintereinander heisst, dass er nicht zurueckkommt.
            leer += 1
            if leer >= 3:
                break
            continue
        leer = 0
        if m["schonBesucht"]:         # der Ring ist wirklich rum
            break
        reihenfolge.append(m["pfad"])
        if not m["ringSichtbar"]:
            ohne_ring.append({"pfad": m["pfad"], "text": m["text"],
                              "umriss": m["mit"]["umriss"], "schatten": m["mit"]["schatten"][:40]})
    s.js("document.querySelectorAll('[data-a11y-besucht]').forEach(e=>e.removeAttribute('data-a11y-besucht'))")
    return ohne_ring[:15], reihenfolge


def messen(s):
    m = s.js(MESSEN_STATISCH)
    m["ohneRing"], m["tabWeg"] = tab_weg(s)
    return m


def zaehle(m):
    return sum(len(m.get(k, [])) for k, _ in ARTEN)


# ------------------------------------------------------------------- Bericht ---
def bericht(alle):
    print("\n" + "=" * 74)
    print("A11y-BEFUNDE  (WCAG 2.1 AA / EN 301 549 - Massstab des BFSG)")
    print("=" * 74)

    gesamt = 0
    for kennung, titel in ARTEN:
        # Nach Pfad buendeln: derselbe Knopf in sechs Laeufen ist EIN Befund, nicht sechs.
        treffer = {}
        for m in alle:
            for f in m.get(kennung, []):
                schluessel = f.get("pfad", "?")
                if schluessel not in treffer:
                    treffer[schluessel] = (f, set())
                treffer[schluessel][1].add(m["station"])
        if not treffer:
            print(u"\n  %-34s ohne Befund" % titel)
            continue
        gesamt += len(treffer)
        print(u"\n  %-34s %d Stelle(n)" % (titel, len(treffer)))
        for pfad, (f, stationen) in sorted(treffer.items())[:12]:
            zusatz = f.get("text") or f.get("was") or f.get("aktion") or f.get("typ") or f.get("quelle") or ""
            if f.get("von"):
                zusatz = u"%s → %s  %s" % (f["von"], f["nach"], f.get("text", ""))
            print(u"     %-46s %s" % (pfad[:46], zusatz[:34]))
            print(u"        in: %s" % ", ".join(sorted(stationen)[:3]))

    # Plausibilitaetsanker: "0 Befunde" bei 0 abgegangenen Elementen ist kein Ergebnis,
    # sondern eine Messung, die nicht stattgefunden hat.
    wege = [len(m.get("tabWeg", [])) for m in alle]
    print("\n" + "-" * 74)
    print(u"  %d Stelle(n) ueber %d Station(en)." % (gesamt, len(alle)))
    print(u"  Tab-Weg: %d Elemente abgegangen (kuerzeste Station %d, laengste %d)."
          % (sum(wege), min(wege or [0]), max(wege or [0])))
    if min(wege or [0]) == 0:
        print(u"  ACHTUNG: Auf mindestens einer Station war der Tab-Weg leer - dort wurde"
              u" der Fokus NICHT gemessen.")
    if gesamt == 0:
        print(u"  Achtung: 0 Befunde heisst nur dann etwas, wenn --gegenprobe zuletzt gruen war.")
    return gesamt


# ---------------------------------------------------------------- Gegenprobe ---
# Ein Pruefstand, den niemand geprueft hat, meldet "sauber" - und man glaubt ihm.
# Jede Messgroesse bekommt einen kuenstlichen Fehler und MUSS anschlagen.
KUENSTLICH = r"""(() => {
  const d = document.createElement('div');
  d.id = '__a11y_probe';
  d.innerHTML =
    '<button id="__p1"><span aria-hidden="true"></span></button>' +   // Name fehlt
    '<input id="__p2" type="text" placeholder="Nur ein Platzhalter">' + // Label fehlt
    '<img id="__p3" src="img/neutral.jpg" width="20" height="20">' +    // alt fehlt
    '<div id="__p4" data-action="probe" tabindex="-1">Nur mit Maus</div>' + // nicht erreichbar
    '<h1 id="__p5">Eins</h1><h3 id="__p6">Drei</h3>' +                  // Sprung
    '<div aria-hidden="true"><button id="__p7">Falle</button></div>' +   // aria-hidden-Falle
    // Drei Gegenstuecke: Der Ring sitzt im Pseudoelement, im Kind, und hinter einer
    // Transition. Alle drei MUESSEN als "hat einen Ring" durchgehen - schlaegt hier eine
    // Messgroesse an, meldet die Pruefung wieder Fehlalarme auf gut geloesten Stellen.
    '<button id="__p8"><span>Ring im ::after</span></button>' +
    '<button id="__p9"><span id="__p9k">Ring im Kind</span></button>' +
    '<button id="__p10">Ring hinter Transition</button>';
  d.setAttribute('style', 'position:fixed;left:2px;top:2px;z-index:99999;background:#333');
  // GANZ nach vorn: an body angehaengt landet die Probe am Ende des Tab-Wegs und wird bei
  // einer begrenzten Zahl Tastendruecke nie besucht - die Fokus-Messgroesse haette dann
  // stumm "kein Befund" gemeldet, obwohl sie gar nicht gefragt wurde (20.09.2026).
  document.body.insertBefore(d, document.body.firstChild);
  // Fokusring: ein Knopf, der im Fokus exakt so aussieht wie ohne.
  const st = document.createElement('style');
  st.id = '__a11y_probe_stil';
  st.textContent =
    '#__p1, #__p1:focus, #__p1:focus-visible { outline: none !important; box-shadow: none !important; }' +
    '#__p8 { position: relative; outline: none; } #__p8::after { content: ""; position: absolute; inset: 0; }' +
    '#__p8:focus-visible { outline: none; } #__p8:focus-visible::after { outline: 2px solid red; }' +
    '#__p9 { outline: none; } #__p9:focus-visible { outline: none; } #__p9:focus-visible #__p9k { background: lime; }' +
    '#__p10 { outline: none; transition: box-shadow 900ms; } #__p10:focus-visible { outline: none; box-shadow: 0 0 0 3px red; }';
  document.head.appendChild(st);
  return true;
})()"""

AUFRAEUMEN = r"""(() => {
  for (const id of ['__a11y_probe', '__a11y_probe_stil']) {
    const e = document.getElementById(id);
    if (e) e.remove();
  }
  return true;
})()"""


def gegenprobe(s):
    print("\n=== Gegenprobe: schlaegt jede Messgroesse an? ===\n")
    s.senden("Page.enable")
    s.geraet(390, 844, "dark")
    s.laden()
    AM.onboarding(s)
    AM.reiter(s, "home")
    time.sleep(0.5)

    vorher = messen(s)
    if zaehle(vorher) != 0:
        print(u"  Hinweis: Die Seite hat schon ohne Probe %d Befund(e)." % zaehle(vorher))

    s.js(KUENSTLICH)
    time.sleep(0.4)
    nachher = messen(s)
    s.js(AUFRAEUMEN)

    fehlt = []
    for kennung, titel in ARTEN:
        if kennung == "geruest":
            continue       # kein kuenstlicher Fehler moeglich, ohne die Seite zu zerlegen
        v, n = len(vorher.get(kennung, [])), len(nachher.get(kennung, []))
        ok = n > v
        print(u"  %-38s %s  (%d → %d)" % (titel, "OK  " if ok else "FEHLT", v, n))
        if not ok:
            fehlt.append(titel)

    # Zweite Haelfte der Gegenprobe: Schlaegt sie auch dort NICHT an, wo der Ring sauber
    # geloest ist? Ein Pruefstand, der zu viel meldet, ist genauso wertlos wie einer, der zu
    # wenig meldet - er laesst funktionierenden Code "reparieren".
    print()
    gemeldet = {f["pfad"] for f in nachher.get("ohneRing", [])}
    for kennung, was in (("__p8", u"Ring im ::after"), ("__p9", u"Ring im Kind"),
                         ("__p10", u"Ring hinter einer Transition")):
        falsch = any(kennung in p for p in gemeldet)
        print(u"  %-38s %s" % (u"kein Fehlalarm: " + was, u"FEHLALARM" if falsch else u"OK  "))
        if falsch:
            fehlt.append(u"Fehlalarm bei: " + was)

    print()
    if fehlt:
        print(u"  %d Messgroesse(n) schlagen NICHT an: %s" % (len(fehlt), ", ".join(fehlt)))
        print(u"  Ein gruener Bericht waere damit wertlos.")
        return 1
    print(u"  Alle Messgroessen schlagen an. Ein gruener Bericht bedeutet etwas.")
    return 0


# ---------------------------------------------------------------------- Lauf ---
def lauf(s, breite, hoehe, theme, name):
    lauf_name = "%s-%s" % (name, theme)
    print("\n=== %s  %dx%d  %s ===" % (name, breite, hoehe, theme))
    s.senden("Page.enable")
    s.geraet(breite, hoehe, theme)
    s.laden()
    ergebnisse = []

    def station(titel):
        s.bild_abwarten()
        time.sleep(0.3)
        m = messen(s)
        m["station"], m["lauf"] = titel, lauf_name
        ergebnisse.append(m)
        n = zaehle(m)
        print(u"   %-30s %s" % (titel[:30], (u"%d Befund(e)" % n) if n else u"ohne Befund"))

    station("00_auth-gate")
    AM.onboarding(s)
    for kennung, titel in (("home", "10_startreiter"), ("plan", "20_wochenplan"),
                           ("recipes", "30_rezeptbuch"), ("progress", "40_fortschritt")):
        if AM.reiter(s, kennung):
            station(titel)

    AM.reiter(s, "plan")
    if s.tippen_auf('[data-slot="mon:fr"]'):
        time.sleep(1.0)
        station("21_meal-picker")
        AM.modal_zu(s)
    if s.tippen_auf('[data-action="shopping"]'):
        time.sleep(1.0)
        station("22_einkaufsliste")
        AM.modal_zu(s)
    # Die Vorkochliste gehoert dazu: `abnahme-mobil.py` faehrt sie an, und ein Bereich, den
    # nur einer der beiden Pruefstaende kennt, faellt niemandem auf (Fund von `kvp`,
    # 20.09.2026). Solange der Stationsweg in beiden Dateien getrennt steht, ist genau das
    # das Risiko - siehe docs/TESTING.md 2g-bis.
    if s.tippen_auf('[data-action="plan-menu"]'):
        time.sleep(0.6)
        if s.tippen_auf('[data-mi="batch"]'):
            time.sleep(1.0)
            station("23_vorkochen")
        AM.modal_zu(s)
    return ergebnisse


def main():
    p = argparse.ArgumentParser(description=u"A11y-Pruefung (WCAG 2.1 AA), Phase E4 / BFSG")
    p.add_argument("--gegenprobe", action="store_true", help=u"misst sich selbst")
    p.add_argument("--schnell", action="store_true", help=u"nur 390x844 dark")
    p.add_argument("--zeigen", action="store_true", help=u"Browser offen lassen")
    a = p.parse_args()

    s = AM.Sitzung()
    s.start()
    try:
        if a.gegenprobe:
            return gegenprobe(s)
        laeufe = [(390, 844, "dark", "iPhone-13")] if a.schnell else [
            (390, 844, "dark", "iPhone-13"), (390, 844, "light", "iPhone-13"),
            (1280, 900, "dark", "Desktop"),
        ]
        alle = []
        for breite, hoehe, theme, name in laeufe:
            alle.extend(lauf(s, breite, hoehe, theme, name))
        n = bericht(alle)
        return 1 if n else 0
    finally:
        if not a.zeigen:
            s.stoppen()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
