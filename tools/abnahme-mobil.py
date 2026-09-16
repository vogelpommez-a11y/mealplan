# -*- coding: utf-8 -*-
u"""
Geraeteabnahme der mobilen Ansicht - Onboarding und alle vier Reiter, echt emuliert.

Warum es dieses Werkzeug gibt: Eine Abnahme "im Browser" ueber die Fensterbreite misst den
falschen Viewport und liefert `pointer: fine` - sie meldet gruen, wo am Geraet ein Fehler
waere. Hier laeuft echte Geraete-Emulation ueber das DevTools-Protokoll:
setDeviceMetricsOverride + setTouchEmulationEnabled + setEmulatedMedia, und getippt wird
mit Input.dispatchTouchEvent. Drei Geraetebreiten, Light UND Dark, 22 Stationen je Lauf.

  python tools/abnahme-mobil.py                  # alle sechs Laeufe
  python tools/abnahme-mobil.py --geraet 360x800 --theme light
  python tools/abnahme-mobil.py --gegenprobe     # misst sich selbst (siehe unten)
  python tools/abnahme-mobil.py --zeigen         # Browser am Ende offen lassen

Braucht den lokalen Server: powershell -NoProfile -File test-server.ps1
Eigenes Profil auf Port 9225, bewusst NICHT angemeldet - die Cloud-Falle aus
docs/TESTING.md: localhost trennt nur den lokalen Speicher, nicht die Cloud.

Gemessen wird sechserlei: waagerechter Ueberlauf, Elemente ueber dem Rand, Trefferflaechen
unter 44px (Apple HIG), Knoepfe die einander den Tipp wegnehmen, abgeschnittener Text,
Eingaben unter 16px (iOS-Zoom) und Kontrast nach WCAG.

ACHTUNG, hier steckt die Erfahrung vom 16.09.2026 drin - die erste Fassung meldete 346
Kontrastbefunde, von denen 345 falsch waren:

  * Farben werden NICHT selbst geparst. Die App benutzt `color(srgb 0.94 0.93 0.93)`;
    ein Parser, der die Zahlen fuer 0-255 haelt, macht aus fast-Weiss fast-Schwarz.
    Der Browser rechnet sie ueber ein Canvas selbst aus - das kann jede CSS-Syntax.
  * Der Grund eines Textes ist das, was am Ort des Textes wirklich dahinterliegt. Aktive
    Zustaende malen ihn ueber einen gleitenden Indikator - ein absolut gesetztes
    GESCHWISTER mit `pointer-events: none`. Eine Elternkette sieht den nie.
  * Gemessen wird die TREFFERFLAECHE, nicht der sichtbare Kasten: Das Projekt vergroessert
    sie an vielen Stellen ueber ein ::after (hitSlop). Wer das uebersieht, laesst Code
    "reparieren", der stimmt.
  * Text ueber Bild oder Verlauf ist NICHT messbar und wird als solcher ausgewiesen,
    statt eine Zahl zu erfinden.
"""
import argparse, base64, json, os, shutil, subprocess, sys, time, urllib.request

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9225
PROFIL = os.path.join(os.environ.get("TEMP", "."), "mp-chrome-mobil")
URL = "http://localhost:8000/index.html"
SCHUESSE = os.path.join(os.environ.get("TEMP", "."), "mp-abnahme-mobil")

GERAETE = [
    (360, 800, "klein_android"),   # engster Fall, Breakpoint 360
    (375, 667, "iphone_se"),       # kurzer Schirm
    (393, 852, "iphone14"),        # der Alltagsfall
]

# Was das Onboarding an Pflichtangaben braucht. Steht hier sichtbar, damit niemand raten
# muss, mit welchen Werten die Abnahme gelaufen ist.
#
# WIRD VON HAND GEPFLEGT. Benennt das Onboarding ein Feld um oder kommt eines dazu, steht
# es hier nicht mehr - und ohne die Meldung unten faellt die Abnahme dann STUMM durch:
# Sie waehlt irgendeinen Mittelwert, misst einen Zustand, den so nie jemand erzeugt, und
# meldet trotzdem gruen. Deshalb ist ein unbekanntes Zahlenfeld ein ROTER Befund und kein
# Achselzucken (Hinweis von `kvp`, 16.09.2026).
WUNSCH = {"age": "30", "height": "180", "weight": "82", "weightGoal": "78"}
# "weightGoal" stand hier zuerst als "target", dazu ein "rate", das es gar nicht gibt.
# Beides fiel NIE auf: Das Skript nahm klaglos den mittleren Listenwert, und alle
# Laeufe meldeten gruen. Gefunden hat es erst die Meldung oben, am Tag ihres Einbaus.

# Zahlenfelder, die das Onboarding verlangt, die aber in WUNSCH fehlen. Modulweit, weil
# sie im Bericht landen muessen und nicht im Durchlauf untergehen duerfen.
UNBEKANNTE_FELDER = set()


MESSEN = r"""(() => {
  // Fuer die Dauer der Messung Trefferpruefung fuer ALLE Elemente einschalten.
  // elementsFromPoint ueberspringt `pointer-events: none` - und genau so ist der
  // gleitende Indikator hinter den aktiven Knoepfen gesetzt. Ohne diesen Schalter bleibt
  // er unsichtbar und die Messung meldet weissen Text auf hellgrauem statt auf rotem
  // Grund. Sichtbar aendert sich dabei nichts; der Stil fliegt am Ende wieder raus.
  // Der Stil wird NUR um die Kontrastmessung gelegt, nicht um die ganze Messung: Ein Toast
  // traegt `pointer-events: none`, damit man durch ihn hindurchtippen kann. Global
  // aufgehoben, liegt er ploetzlich ueber den Reitern - und die Ueberlappungspruefung
  // meldet zwei unbedienbare Knoepfe, die es in Wahrheit nicht gibt (16.09.2026).
  const _hilfsstil = document.createElement('style');
  _hilfsstil.textContent = '*, *::before, *::after { pointer-events: auto !important; }';
  try {
  const W = document.documentElement.clientWidth;
  const H = document.documentElement.clientHeight;
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
  const txt = e => (e.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 50);

  const alle = [...document.querySelectorAll('body *')].filter(sichtbar);

  // 1. Waagerechter Ueberlauf der Seite
  const seiteUeberlauf = document.documentElement.scrollWidth - W;

  // 2. Elemente, die ueber den rechten Rand ragen (ohne bewusste Scroll-Streifen)
  const imStreifen = e => {
    let n = e.parentElement, t = 0;
    while (n && t++ < 6) {
      const st = getComputedStyle(n);
      if (/(auto|scroll)/.test(st.overflowX)) return true;
      n = n.parentElement;
    }
    return false;
  };
  const ragtRaus = alle.filter(e => {
    const r = e.getBoundingClientRect();
    return (r.right > W + 1 || r.left < -1) && !imStreifen(e);
  }).map(e => {
    const r = e.getBoundingClientRect();
    return { pfad: pfad(e), text: txt(e), links: Math.round(r.left), rechts: Math.round(r.right), ueber: Math.round(r.right - W) };
  }).slice(0, 12);

  // 3. Tippflaechen unter 44 px (Apple HIG) - nur wirklich bedienbare Elemente
  const bedienbar = alle.filter(e => {
    const t = e.tagName.toLowerCase();
    if (['button','a','input','select','textarea','summary'].includes(t)) return true;
    if (e.getAttribute('role') === 'button' || e.getAttribute('role') === 'tab') return true;
    if (e.hasAttribute('data-action') || e.hasAttribute('data-tab')) return true;
    return false;
  }).filter(e => {
    if (e.tagName === 'INPUT' && ['hidden','checkbox','radio'].includes(e.type)) return false;
    return !e.closest('.visually-hidden') && !e.disabled;
  });
  // Gemessen wird die TREFFERFLAECHE, nicht der sichtbare Kasten. Das Projekt vergroessert
  // sie an mehreren Stellen ueber ein ::after (z. B. `.foot-link::after{height:44px}`,
  // `.kal-nb::after{inset:-7px}`) - sichtbar bleibt der Knopf klein, tippbar ist er gross.
  // Wer nur getBoundingClientRect() misst, meldet genau diese bereits geloesten Faelle als
  // Fehler und laesst Code "reparieren", der stimmt.
  const trifft = (e, x, y) => {
    const t = document.elementFromPoint(x, y);
    // NUR das Element selbst oder eines seiner Kinder zaehlt. Ein Vorfahre darf NICHT
    // zaehlen: neben einem kleinen Knopf liefert elementFromPoint dessen Container, und
    // `t.contains(e)` wuerde damit jede beliebige Flaeche als Treffer ausweisen - die
    // Gegenprobe fiel genau darauf herein und hielt einen 30x20-Knopf fuer gross genug.
    return !!t && (t === e || e.contains(t));
  };
  // Nicht jede Distanz abschreiten - nur die Grenze pruefen, um die es geht: reicht die
  // Trefferflaeche bis 22 px beiderseits der Mitte, sind es 44 px. Alles andere kostet
  // hunderte elementFromPoint-Aufrufe je Seite und laeuft in den Zeitablauf.
  const reicht44 = (e, r, achse) => {
    const mx = r.left + r.width/2, my = r.top + r.height/2;
    const p1 = achse === 'x' ? [mx - 21.5, my] : [mx, my - 21.5];
    const p2 = achse === 'x' ? [mx + 21.5, my] : [mx, my + 21.5];
    for (const [x, y] of [p1, p2]) {
      if (x < 0 || y < 0 || x > W || y > H) return false;
      if (!trifft(e, x, y)) return false;
    }
    return true;
  };
  // Rueckfallweg, wenn der Messpunkt ausserhalb des Bildes liegt (ein Knopf am unteren
  // Rand - der Fuss ist genau so ein Fall): dann die Trefferflaeche aus der Geometrie des
  // Pseudoelements ableiten, statt sie faelschlich als zu klein zu melden.
  const pseudoBox = (e, r) => {
    let b = r.width, h = r.height;
    for (const wo of ['::before', '::after']) {
      const ps = getComputedStyle(e, wo);
      if (!ps || ps.content === 'none' || !/absolute|fixed/.test(ps.position)) continue;
      const zahlpx = v => { const n = parseFloat(v); return isFinite(n) ? n : null; };
      const ph = zahlpx(ps.height), pw = zahlpx(ps.width);
      const oben = zahlpx(ps.top), unten = zahlpx(ps.bottom);
      const links = zahlpx(ps.left), rechts = zahlpx(ps.right);
      if (ph !== null) h = Math.max(h, ph);
      else if (oben !== null && unten !== null) h = Math.max(h, r.height - oben - unten);
      if (pw !== null) b = Math.max(b, pw);
      else if (links !== null && rechts !== null) b = Math.max(b, r.width - links - rechts);
    }
    return { b: Math.round(b), h: Math.round(h) };
  };

  const zuKlein = bedienbar.map(e => {
    const r = e.getBoundingClientRect();
    const sichtbarB = Math.round(r.width), sichtbarH = Math.round(r.height);
    let b = sichtbarB, h = sichtbarH;
    if (sichtbarB < 44 || sichtbarH < 44) {          // nur dann lohnt die teure Messung
      const mx = r.left + r.width/2, my = r.top + r.height/2;
      const imBild = mx >= 0 && mx <= W && my >= 0 && my <= H;
      if (imBild && trifft(e, mx, my)) {
        if (sichtbarB < 44 && reicht44(e, r, 'x')) b = 44;
        if (sichtbarH < 44 && reicht44(e, r, 'y')) h = 44;
      }
      const pb = pseudoBox(e, r);     // greift auch, wo der Messpunkt aus dem Bild faellt
      b = Math.max(b, pb.b); h = Math.max(h, pb.h);
    }
    return { pfad: pfad(e), text: txt(e), b, h, sichtbarB, sichtbarH };
  }).map(o => {
    const kleinste = Math.min(o.b, o.h);
    return Object.assign(o, {
      kleinste,
      erweitert: (o.b > o.sichtbarB || o.h > o.sichtbarH),
      schwere: kleinste < 32 ? 'deutlich' : 'knapp'   // 44 px ist Apples Mass; unter 32 wird es heikel
    });
  }).filter(o => o.kleinste < 44).slice(0, 25);

  // 3b. Klaut eine vergroesserte Trefferflaeche dem Nachbarn den Tipp?
  // Ein hitSlop, der ueber den Nachbarknopf reicht, macht diesen unbedienbar - der Fehler
  // waere schlimmer als die zu kleine Flaeche, die er heilen soll. Geprueft wird am
  // Mittelpunkt: wer dort nicht sich selbst trifft, ist verdeckt.
  // Liegt ein Overlay/Modal ueber der Seite, sind die Knoepfe DAHINTER selbstverstaendlich
  // verdeckt - das ist der Zweck eines Modals, kein Fehler. Dann zaehlt nur, was im
  // obersten Overlay selbst liegt.
  const oberstesOverlay = [...document.querySelectorAll('.overlay, .modal, [role="dialog"]')]
    .filter(e => { const st = getComputedStyle(e);
      return st.display !== 'none' && st.visibility !== 'hidden' && +st.opacity > 0
             && e.getBoundingClientRect().width > 0; }).pop() || null;
  const verdeckteKnoepfe = bedienbar.filter(e => !oberstesOverlay || oberstesOverlay.contains(e)).map(e => {
    const r = e.getBoundingClientRect();
    const mx = r.left + r.width/2, my = r.top + r.height/2;
    if (mx < 0 || my < 0 || mx > W || my > H) return null;
    const t = document.elementFromPoint(mx, my);
    if (!t || t === e || e.contains(t) || t.contains(e)) return null;
    return { pfad: pfad(e), text: txt(e), stattdessen: pfad(t), fremderText: txt(t) };
  }).filter(Boolean).slice(0, 12);

  // 4. Abgeschnittener Text
  const abgeschnitten = alle.filter(e => {
    if (!e.childNodes.length) return false;
    // Screenreader-Texte sind absichtlich 1x1 px gross - dort ist das Wegschneiden der Zweck.
    if (e.closest('.visually-hidden') || e.classList.contains('sr-only')) return false;
    const nurText = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!nurText) return false;
    const st = getComputedStyle(e);
    const versteckt = st.overflow === 'hidden' || st.overflowY === 'hidden' || st.overflowX === 'hidden';
    if (!versteckt) return false;
    return e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2;
  }).map(e => ({
    pfad: pfad(e), text: txt(e),
    sichtbarH: e.clientHeight, inhaltH: e.scrollHeight,
    sichtbarB: e.clientWidth, inhaltB: e.scrollWidth,
    ellipsis: getComputedStyle(e).textOverflow === 'ellipsis',
    clamp: getComputedStyle(e).webkitLineClamp || 'none'
  })).filter(o => !(o.ellipsis && o.inhaltH <= o.sichtbarH + 2) && o.clamp === 'none').slice(0, 12);

  // 5. Eingabefelder unter 16 px - iOS zoomt dann automatisch
  const zuKleineSchrift = alle.filter(e => ['INPUT','SELECT','TEXTAREA'].includes(e.tagName))
    .filter(e => !e.closest('.visually-hidden') && e.type !== 'hidden')
    .map(e => ({ pfad: pfad(e), px: parseFloat(getComputedStyle(e).fontSize) }))
    .filter(o => o.px < 16).slice(0, 10);

  // 6. Kontrast nach WCAG gegen den tatsaechlich dahinterliegenden Grund.
  //
  // Zwei Fallen, an denen eine naive Messung Unsinn meldet:
  //  * Halbdurchsichtige Hintergruende muessen UEBEREINANDER gerechnet werden. Wer sie
  //    einfach ueberspringt, misst gegen die Seitenfarbe und erfindet Befunde.
  //  * Ueber einem Bild oder Verlauf ist der Grund gar keine Farbe. Dort ist das ehrliche
  //    Ergebnis "nicht messbar" - nicht "1.17:1". Genau solche Scheinbefunde hat die erste
  //    Fassung am 16.09.2026 fuer die Startkarte und die Rezept-Badges geliefert.
  // Farben NICHT selbst parsen. Die App benutzt moderne Syntax wie
  // `color(srgb 0.943 0.928 0.928)`; ein Parser, der die Zahlen fuer 0-255 haelt, macht
  // aus fast-Weiss fast-Schwarz und erfindet damit reihenweise Kontrastbefunde (genau so
  // am 16.09.2026 geschehen). Deshalb rechnet der Browser selbst: einmal auf schwarzen,
  // einmal auf weissen Grund malen - daraus folgen Farbe UND Deckkraft eindeutig.
  const _lw = document.createElement('canvas').getContext('2d', {willReadFrequently: true});
  const _cache = new Map();
  const zahl = f => {
    if (!f) return null;
    if (_cache.has(f)) return _cache.get(f);
    let erg = null;
    try {
      const mal = (grund) => {
        _lw.canvas.width = _lw.canvas.height = 1;
        _lw.clearRect(0,0,1,1);
        _lw.fillStyle = grund; _lw.fillRect(0,0,1,1);
        _lw.fillStyle = '#000';            // ungueltige Farbe faellt sonst auf den Altwert zurueck
        _lw.fillStyle = f;
        if (_lw.fillStyle === '#000' && !/^(#000|black|rgb\(0, 0, 0\))/.test(f.trim())) return null;
        _lw.fillRect(0,0,1,1);
        return _lw.getImageData(0,0,1,1).data;
      };
      const s0 = mal('#000'), s1 = mal('#fff');
      if (s0 && s1) {
        const a = 1 - (s1[0] - s0[0]) / 255;
        erg = a <= 0.004 ? [0,0,0,0]
            : [s0[0]/a, s0[1]/a, s0[2]/a, Math.round(a*1000)/1000];
      }
    } catch (e) { erg = null; }
    _cache.set(f, erg);
    return erg;
  };
  const ueber = (v, h) => {           // v ueber h legen, beide [r,g,b,a]
    const a = v[3] === undefined ? 1 : v[3];
    return [0,1,2].map(i => v[i]*a + h[i]*(1-a)).concat([1]);
  };
  // Der Grund ist das, was am Ort des Textes tatsaechlich DAHINTER liegt - nicht das,
  // was die Elternkette hergibt. Aktive Zustaende malen ihren Grund hier ueber einen
  // gleitenden Indikator (span.ws-ind), ein absolut gesetztes GESCHWISTER. Eine Kette aus
  // Vorfahren sieht den nie und meldet weissen Text auf hellgrauem Grund - 1.17:1 fuer
  // etwas, das in Wahrheit weiss auf Rot ist. elementsFromPoint liefert die echte
  // Stapelreihenfolge und beendet diese Klasse von Fehlalarmen.
  const grundKette = e => {
    const r = e.getBoundingClientRect();
    const px = Math.min(Math.max(r.left + Math.min(r.width/2, 14), 1), W - 1);
    const py = Math.min(Math.max(r.top + r.height/2, 1), H - 1);
    let stapel = document.elementsFromPoint(px, py);
    const ab = stapel.indexOf(e);
    stapel = ab >= 0 ? stapel.slice(ab) : [e].concat([...document.querySelectorAll('*')].length ? [] : []);
    if (ab < 0) {                      // Punkt ausserhalb (gescrollt): auf die Elternkette zurueck
      stapel = []; let n = e;
      while (n && n.nodeType === 1) { stapel.push(n); n = n.parentElement; }
    }
    let schichten = [], bild = false;
    for (const n of stapel) {
      const st = getComputedStyle(n);
      if (n !== e && st.backgroundImage && st.backgroundImage !== 'none') bild = true;
      for (const wo of ['::before', '::after']) {
        const ps = getComputedStyle(n, wo);
        if (!ps || ps.content === 'none') continue;
        const pc = zahl(ps.backgroundColor);
        if ((pc && pc[3] > 0.05) || (ps.backgroundImage && ps.backgroundImage !== 'none')) bild = true;
      }
      const c = zahl(st.backgroundColor);
      if (c) {
        const al = c[3] === undefined ? 1 : c[3];
        if (al > 0) { schichten.unshift(c); if (al >= 0.999) break; }
      }
    }
    let grund = [255,255,255,1];
    schichten.forEach(c => { grund = ueber(c, grund); });
    return { grund, bild };
  };
  const lum = c => { const f = c.slice(0,3).map(v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); }); return 0.2126*f[0] + 0.7152*f[1] + 0.0722*f[2]; };
  const verh = (a, b) => { const l1 = lum(a), l2 = lum(b); return (Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05); };
  document.head.appendChild(_hilfsstil);      // ab hier zaehlt die echte Stapelreihenfolge
  const kontrast = [], kontrastUnsicher = [];
  alle.filter(e => {
    const eig = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!eig) return false;
    const r = e.getBoundingClientRect();
    return r.top < H && r.bottom > 0;
  }).forEach(e => {
    const st = getComputedStyle(e);
    const v = zahl(st.color);
    if (!v || (v[3] !== undefined && v[3] < 0.1)) return;
    const px = parseFloat(st.fontSize), fett = (parseInt(st.fontWeight) || 400) >= 700;
    const gross = px >= 24 || (px >= 18.66 && fett);
    const g = grundKette(e);
    const vorn = ueber(v, g.grund);
    const k = verh(vorn, g.grund);
    if (k >= (gross ? 3 : 4.5)) return;
    const o = { pfad: pfad(e), text: txt(e), px: Math.round(px),
                verhaeltnis: Math.round(k*100)/100, noetig: gross ? 3 : 4.5,
                farbe: st.color, grund: 'rgb(' + g.grund.slice(0,3).map(Math.round).join(',') + ')' };
    (g.bild ? kontrastUnsicher : kontrast).push(o);
  });

  _hilfsstil.remove();
  return {
    viewport: { b: W, h: H },
    seiteUeberlauf, ragtRaus, zuKlein, verdeckteKnoepfe, abgeschnitten, zuKleineSchrift,
    kontrast: kontrast.slice(0,20), kontrastUnsicher: kontrastUnsicher.slice(0,20)
  };
  } finally { _hilfsstil.remove(); }
})()"""

# ----------------------------------------------------------------- Sitzung ---
# Bewusst NICHT tools/cdp.py: dort oeffnet und schliesst jeder Aufruf eine eigene
# Verbindung. setEmulatedMedia und setTouchEmulationEnabled gelten aber nur, SOLANGE die
# Verbindung offen ist. Ein Ablauf, der klickt und danach misst, braucht deshalb EINE
# durchgehende Verbindung - sonst ist beim Messen das Theme wieder das des Systems und
# der Zeiger wieder `fine`, und die Abnahme misst etwas anderes, als sie behauptet.
class Sitzung(object):
    def __init__(self):
        self.ws = None
        self.kennung = 0

    def _seiten(self):
        with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % PORT, timeout=5) as r:
            return [t for t in json.loads(r.read().decode("utf-8")) if t.get("type") == "page"]

    def start(self, frisch=True):
        try:
            if self._seiten():
                self.verbinden()
                return
        except Exception:
            pass
        if frisch and os.path.isdir(PROFIL):
            shutil.rmtree(PROFIL, ignore_errors=True)
        subprocess.Popen([
            CHROME, "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
            "--user-data-dir=" + PROFIL, "--no-first-run", "--no-default-browser-check", URL])
        for _ in range(60):
            time.sleep(0.5)
            try:
                if self._seiten():
                    break
            except Exception:
                continue
        else:
            raise SystemExit("Chrome kam nicht hoch. Laeuft test-server.ps1?")
        self.verbinden()

    def verbinden(self):
        import websocket
        seiten = [t for t in self._seiten() if "localhost" in (t.get("url") or "")] or self._seiten()
        self.ws = websocket.create_connection(
            seiten[0]["webSocketDebuggerUrl"], timeout=90,
            origin="http://127.0.0.1:%d" % PORT, suppress_origin=False)

    def stoppen(self):
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
        subprocess.call(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | "
            "Where-Object { $_.CommandLine -like '*mp-chrome-mobil*' } | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def senden(self, methode, params=None, timeout=90):
        self.kennung += 1
        k = self.kennung
        self.ws.settimeout(timeout)
        self.ws.send(json.dumps({"id": k, "method": methode, "params": params or {}}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == k:
                if "error" in m:
                    raise RuntimeError("%s: %s" % (methode, m["error"]))
                return m.get("result", {})

    def js(self, ausdruck, timeout=90):
        r = self.senden("Runtime.evaluate", {
            "expression": ausdruck, "awaitPromise": True,
            "returnByValue": True, "userGesture": True}, timeout=timeout)
        if "exceptionDetails" in r:
            e = r["exceptionDetails"]
            raise RuntimeError((e.get("exception") or {}).get("description") or e.get("text"))
        return (r.get("result") or {}).get("value")

    def geraet(self, breite, hoehe, theme):
        self.senden("Emulation.setDeviceMetricsOverride", {
            "width": int(breite), "height": int(hoehe), "deviceScaleFactor": 3, "mobile": True})
        self.senden("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})
        self.senden("Emulation.setEmulatedMedia", {
            "features": [{"name": "prefers-color-scheme", "value": theme}]})
        self.bild_abwarten()

    def bild_abwarten(self):
        self.js("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")

    def laden(self):
        self.js("try{localStorage.clear();sessionStorage.clear()}catch(e){}")
        self.senden("Page.navigate", {"url": URL})
        for _ in range(80):
            time.sleep(0.25)
            try:
                if self.js("document.readyState") == "complete":
                    break
            except Exception:
                continue
        time.sleep(0.6)
        self.bild_abwarten()

    def tippen(self, x, y):
        p = [{"x": float(x), "y": float(y), "radiusX": 12, "radiusY": 12, "force": 1}]
        self.senden("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": p})
        time.sleep(0.04)
        self.senden("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        time.sleep(0.25)

    def tippen_auf(self, selektor):
        k = self.js(
            "(()=>{const e=document.querySelector(%s);if(!e)return null;"
            "e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();"
            "return {x:r.left+r.width/2,y:r.top+r.height/2,ok:r.width>0&&r.height>0};})()"
            % json.dumps(selektor))
        if not k or not k.get("ok"):
            return False
        self.tippen(k["x"], k["y"])
        return True

    def eingeben(self, selektor, text):
        if not self.tippen_auf(selektor):
            return False
        self.senden("Input.insertText", {"text": text})
        self.js("(()=>{const e=document.querySelector(%s);if(e){"
                "e.dispatchEvent(new Event('input',{bubbles:true}));"
                "e.dispatchEvent(new Event('change',{bubbles:true}));}})()" % json.dumps(selektor))
        return True

    def schuss(self, pfad):
        r = self.senden("Page.captureScreenshot", {"format": "png"})
        os.makedirs(os.path.dirname(pfad), exist_ok=True)
        with open(pfad, "wb") as f:
            f.write(base64.b64decode(r["data"]))


# --------------------------------------------------------- Onboarding-Weg ----
def warte_auf_schritt(s, versuche=12):
    u"""Waehrend des Schiebe-Wechsels ist die Fortschrittsleiste kurz nicht im Baum. Wer
    genau dann fragt, haelt das Onboarding faelschlich fuer beendet."""
    info = {"schritt": None, "gesamt": None, "titel": ""}
    for _ in range(versuche):
        info = s.js(r"""(()=>{
          const p = document.querySelector('.wg-progress-bar span');
          const h = [...document.querySelectorAll('h2,h3')].filter(e=>e.offsetParent!==null)
                     .map(e=>(e.textContent||'').replace(/\s+/g,' ').trim());
          return {schritt: p?p.dataset.step:null, gesamt: p?p.dataset.total:null,
                  titel: h.slice(0,2).join(' | ')};})()""")
        if info["schritt"]:
            return info
        time.sleep(0.25)
    return info


def schritt_ausfuellen(s):
    u"""Fuellt, was auf dem aktuellen Schritt noch leer ist, und sagt, was es war."""
    getan = []
    gruppen = s.js("""(()=>{
      const sicht = e => e.offsetParent !== null;
      const g = {};
      [...document.querySelectorAll('[data-opt]')].filter(sicht).forEach(e => {
        (g[e.dataset.opt] = g[e.dataset.opt] || []).push({v: e.dataset.v,
          aktiv: e.classList.contains('is-on') || e.classList.contains('active')
                 || e.getAttribute('aria-pressed') === 'true' || e.classList.contains('sel')});
      });
      return g;})()""")
    for name, werte in (gruppen or {}).items():
        if not any(w["aktiv"] for w in werte):
            if s.tippen_auf('[data-opt="%s"][data-v="%s"]' % (name, werte[0]["v"])):
                getan.append("%s=%s" % (name, werte[0]["v"]))
                time.sleep(0.25)

    felder = s.js("""(()=>{
      const sicht = e => e.offsetParent !== null;
      return [...document.querySelectorAll('[data-num]')].filter(sicht).map(e => ({
        n: e.dataset.num, tag: e.tagName.toLowerCase(), wert: e.value,
        optionen: e.tagName === 'SELECT' ? [...e.options].map(o=>o.value).filter(Boolean) : null}));})()""")
    for f in felder or []:
        if f["wert"] and f["wert"] not in ("", "-", u"\u2013"):
            continue
        ziel = WUNSCH.get(f["n"])
        if ziel is None:
            UNBEKANNTE_FELDER.add(f["n"])     # laut, nicht still - siehe WUNSCH
        if f["tag"] == "select":
            opts = f["optionen"] or []
            if ziel not in opts:
                if ziel is not None:
                    UNBEKANNTE_FELDER.add("%s (Wunschwert %s nicht waehlbar)" % (f["n"], ziel))
                ziel = opts[len(opts)//2] if opts else None
            if ziel is None:
                continue
            s.js("""(()=>{const e=document.querySelector('[data-num="%s"]');
                   e.value=%s;e.dispatchEvent(new Event('change',{bubbles:true}));
                   e.dispatchEvent(new Event('input',{bubbles:true}));})()""" % (f["n"], json.dumps(ziel)))
        else:
            if ziel is None:
                continue
            s.eingeben('[data-num="%s"]' % f["n"], ziel)
        getan.append("%s=%s" % (f["n"], ziel))
        time.sleep(0.2)

    haken = s.js("""(()=>{const c=[...document.querySelectorAll('input[type=checkbox]')]
      .filter(e=>!e.checked && e.required); c.forEach(e=>e.click()); return c.length;})()""")
    if haken:
        getan.append("%d Pflichthaken" % haken)
    return getan


def weiter(s, geduld=6.0):
    u"""Weiter tippen und AKTIV abwarten, bis der Schritt wechselt. Eine feste Wartezeit
    taugt nicht: Der Schiebe-Wechsel dauert laenger als eine Sekunde, und wer zu frueh
    nachsieht, haelt einen gelungenen Wechsel fuer Stillstand."""
    vorher = warte_auf_schritt(s)["schritt"]
    if not s.tippen_auf(".onb-next"):
        return False
    ende = time.time() + geduld
    while time.time() < ende:
        time.sleep(0.2)
        jetzt = s.js("""(()=>{const p=document.querySelector('.wg-progress-bar span');
          const r=[...document.querySelectorAll('[data-tab]')].filter(e=>e.offsetParent!==null);
          return {schritt: p?p.dataset.step:null, reiter: r.length};})()""")
        if jetzt["reiter"] > 0:
            return True
        if jetzt["schritt"] and jetzt["schritt"] != vorher:
            s.bild_abwarten()
            return True
    return False


def onboarding(s, protokoll=None):
    u"""Vom Auth-Gate bis zum fertigen Plan. protokoll(info, gefuellt) sieht jeden Schritt."""
    s.tippen_auf("#a-local"); time.sleep(0.8)
    s.eingeben("#a-name", "Paddy"); time.sleep(0.3)
    s.tippen_auf("#a-go"); time.sleep(1.3)

    for _ in range(14):
        info = warte_auf_schritt(s)
        if not info["schritt"]:
            break
        # Mehrfach fuellen: manche Schritte blenden nach der ersten Wahl einen zweiten
        # Block ein ("Was ist dein Ziel?" -> "Wie schnell?"). Einmal reicht dort nicht.
        gefuellt = []
        for _ in range(4):
            neu = schritt_ausfuellen(s)
            if not neu:
                break
            gefuellt += neu
            time.sleep(0.45)
            if warte_auf_schritt(s)["schritt"] != info["schritt"]:
                break
        if protokoll:
            protokoll(info, gefuellt)
        # Auswahlknoepfe schalten VON SELBST weiter - ein Tipp statt zwei. Wer danach noch
        # "Weiter" tippt, tippt auf den naechsten, noch leeren Schritt und haelt dessen
        # gesperrten Knopf faelschlich fuer Stillstand.
        time.sleep(0.5)
        if warte_auf_schritt(s)["schritt"] != info["schritt"]:
            continue
        if s.js("[...document.querySelectorAll('[data-tab]')].filter(e=>e.offsetParent!==null).length"):
            break
        if not weiter(s):
            break
    time.sleep(1.2)
    s.bild_abwarten()


# ------------------------------------------------------------- Stationen -----
def zaehle(m):
    return (1 if m["seiteUeberlauf"] > 1 else 0) + sum(len(m.get(k, [])) for k in (
        "ragtRaus", "zuKlein", "verdeckteKnoepfe", "abgeschnitten", "zuKleineSchrift", "kontrast"))


def station(s, name, lauf_name, ergebnisse, still=False):
    s.bild_abwarten()
    time.sleep(0.35)
    m = s.js(MESSEN)
    m["station"], m["lauf"] = name, lauf_name
    ergebnisse.append(m)
    sauber = "".join(c if (c.isalnum() or c in "-_") else "_" for c in name)
    s.schuss(os.path.join(SCHUESSE, "%s-%s.png" % (lauf_name, sauber)))
    n = zaehle(m)
    if not still:
        print("   %-30s %s" % (name[:30], ("%d Befund(e)" % n) if n else "ohne Befund"))
    return m


def modal_zu(s):
    for art in ("keyDown", "keyUp"):
        s.senden("Input.dispatchKeyEvent", {"type": art, "key": "Escape",
                                            "code": "Escape", "windowsVirtualKeyCode": 27})
    time.sleep(0.6)
    if s.js("[...document.querySelectorAll('.modal,[role=dialog]')].filter(e=>e.offsetParent!==null).length"):
        s.js("(()=>{const z=[...document.querySelectorAll('.modal [data-close],.modal-close')]"
             ".filter(e=>e.offsetParent!==null); if(z[0]) z[0].click();})()")
        time.sleep(0.5)


def reiter(s, welcher):
    ok = s.tippen_auf('[data-action="tab"][data-tab="%s"]' % welcher)
    time.sleep(1.0)
    s.bild_abwarten()
    return ok


def lauf(s, breite, hoehe, theme, name, still=False):
    lauf_name = "%s-%s" % (name, theme)
    if not still:
        print("\n=== %s  %dx%d  %s ===" % (name, breite, hoehe, theme))
    s.senden("Page.enable")
    s.geraet(breite, hoehe, theme)
    s.laden()
    ergebnisse = []

    station(s, "00_auth-gate", lauf_name, ergebnisse, still)
    onboarding(s, lambda info, gefuellt: station(
        s, "onb-%02d_%s" % (int(info["schritt"]), info["titel"].split("|")[0].strip()[:18]),
        lauf_name, ergebnisse, still))

    for kennung, titel in (("home", "10_startreiter"), ("plan", "20_wochenplan"),
                           ("recipes", "30_rezeptbuch"), ("progress", "40_fortschritt")):
        if reiter(s, kennung):
            station(s, titel, lauf_name, ergebnisse, still)

    reiter(s, "plan")
    if s.tippen_auf('[data-slot="mon:fr"]'):
        time.sleep(1.0)
        station(s, "21_meal-picker", lauf_name, ergebnisse, still)
        modal_zu(s)
    if s.tippen_auf('[data-action="shopping"]'):
        time.sleep(1.0)
        station(s, "22_einkaufsliste", lauf_name, ergebnisse, still)
        modal_zu(s)
    if s.tippen_auf('[data-action="plan-menu"]'):
        time.sleep(0.6)
        if s.tippen_auf('[data-mi="batch"]'):
            time.sleep(1.0)
            station(s, "23_vorkochen", lauf_name, ergebnisse, still)
        modal_zu(s)
    return ergebnisse


# --------------------------------------------------------------- Bericht -----
ARTEN = [
    ("zuKlein",          u"Trefferflaeche unter 44 px"),
    ("verdeckteKnoepfe", u"Knopf nimmt dem Nachbarn den Tipp weg"),
    ("ragtRaus",         u"ragt ueber den Rand"),
    ("abgeschnitten",    u"Text abgeschnitten"),
    ("zuKleineSchrift",  u"Eingabe unter 16 px (iOS zoomt)"),
    ("kontrast",         u"Kontrast unter WCAG"),
]


def bericht(alle):
    u"""Fasst nach URSACHE zusammen, nicht nach Vorkommen: Der Fuss taucht auf jedem
    Onboarding-Schritt auf; elfmal derselbe Fund ist ein Fund, nicht elf."""
    gruppen = {}
    ueberlauf = []
    for m in alle:
        wo = "%s/%s" % (m["lauf"], m["station"])
        if m["seiteUeberlauf"] > 1:
            ueberlauf.append((wo, m["seiteUeberlauf"]))
        for schluessel, titel in ARTEN:
            for o in m.get(schluessel, []):
                k = (titel, o.get("pfad", ""), (o.get("text") or "")[:24])
                g = gruppen.setdefault(k, {"n": 0, "wo": set(), "bsp": o})
                g["n"] += 1
                g["wo"].add(wo)

    if ueberlauf:
        print("\n[!] Seite scrollt waagerecht auf %d Station(en): %s" % (
            len(ueberlauf), ", ".join("%s (+%dpx)" % u for u in ueberlauf[:5])))
    if not gruppen:
        return 0
    print("\n%d Ursache(n):" % len(gruppen))
    for (titel, pfad, text), d in sorted(gruppen.items(), key=lambda kv: -kv[1]["n"]):
        b = d["bsp"]
        print("\n* %s" % titel)
        print("  %s" % pfad)
        if text:
            print('  Text:   "%s"' % text)
        if titel.startswith("Trefferflaeche"):
            print("  %dx%d px (sichtbar %dx%d)" % (b["b"], b["h"], b["sichtbarB"], b["sichtbarH"]))
        elif titel.startswith("Knopf nimmt"):
            print('  getroffen wird stattdessen: %s "%s"' % (b["stattdessen"], b["fremderText"]))
        elif titel.startswith("ragt"):
            print("  %d px ueber den rechten Rand" % b["ueber"])
        elif titel.startswith("Kontrast"):
            print("  %.2f:1, noetig %.1f:1 (%s auf %s, %d px)" % (
                b["verhaeltnis"], b["noetig"], b["farbe"], b["grund"], b["px"]))
        elif titel.startswith("Eingabe"):
            print("  %.1f px" % b["px"])
        print("  %dx gesehen | %s" % (d["n"], ", ".join(sorted(d["wo"])[:4])))
    return len(gruppen)


# ------------------------------------------------------------ Gegenprobe -----
STOERUNG = (
    "(()=>{const st=document.createElement('style');st.id='gegenprobe';"
    "st.textContent='#a-go{width:30px !important;height:20px !important}"
    "#a-name{font-size:11px !important}"
    ".auth-card h2{position:relative;left:260px}"
    ".auth-card .lead{color:#f6f4f4 !important}';"
    "document.head.appendChild(st);})()"
)
STOERUNG2 = (
    "(()=>{const st=document.createElement('style');st.id='gegenprobe2';"
    "st.textContent='.rfilters button::after{inset:-3px -60px !important}';"
    "document.head.appendChild(st);})()"
)
WEG = "(()=>{const e=document.getElementById('%s'); if(e) e.remove();})()"


def gegenprobe(s):
    u"""Wuerde diese Messung einen Fehler ueberhaupt finden? Ohne diesen Nachweis ist ein
    gruener Bericht wertlos - er koennte auch gruen sein, weil nichts gemessen wird."""
    print("Gegenprobe: je ein kuenstlicher Fehler pro Messgroesse\n")
    s.senden("Page.enable")
    s.geraet(393, 852, "light")
    s.laden()
    s.tippen_auf("#a-local")
    time.sleep(0.8)
    vorher = s.js(MESSEN)
    s.js(STOERUNG)
    s.bild_abwarten()
    time.sleep(0.3)
    nachher = s.js(MESSEN)
    s.js(WEG % "gegenprobe")

    offen = []
    for k, titel in (("zuKlein", "Trefferflaeche"), ("zuKleineSchrift", "Eingabeschrift"),
                     ("ragtRaus", "Rand"), ("kontrast", "Kontrast")):
        erkannt = len(nachher[k]) > len(vorher[k])
        print("  %-18s %d -> %d  %s" % (k, len(vorher[k]), len(nachher[k]),
                                        "ERKANNT" if erkannt else "NICHT ERKANNT"))
        if not erkannt:
            offen.append(titel)
    print("  %-18s %d -> %d" % ("seiteUeberlauf", vorher["seiteUeberlauf"], nachher["seiteUeberlauf"]))

    # Die Ueberlappung braucht einen eigenen Aufbau - sie zeigt sich erst an einer Reihe
    # echter Knoepfe, nicht am Auth-Gate.
    s.laden()
    onboarding(s)
    reiter(s, "recipes")
    v2 = s.js(MESSEN)
    s.js(STOERUNG2)
    time.sleep(0.5)
    s.bild_abwarten()
    n2 = s.js(MESSEN)
    s.js(WEG % "gegenprobe2")
    erkannt = len(n2["verdeckteKnoepfe"]) > len(v2["verdeckteKnoepfe"])
    print("  %-18s %d -> %d  %s" % ("verdeckteKnoepfe", len(v2["verdeckteKnoepfe"]),
                                    len(n2["verdeckteKnoepfe"]), "ERKANNT" if erkannt else "NICHT ERKANNT"))
    if not erkannt:
        offen.append("Ueberlappung")

    print("")
    if offen:
        print("ROT - diese Messgroessen finden nichts: %s" % ", ".join(offen))
        return 1
    print("GRUEN - jeder eingebaute Fehler wurde gefunden, die Messung taugt.")
    return 0


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--geraet", help="z. B. 360x800; ohne Angabe alle drei")
    p.add_argument("--theme", choices=["light", "dark"], help="ohne Angabe beide")
    p.add_argument("--gegenprobe", action="store_true", help="misst sich selbst")
    p.add_argument("--zeigen", action="store_true", help="Browser am Ende offen lassen")
    a = p.parse_args()

    s = Sitzung()
    s.start()
    try:
        if a.gegenprobe:
            return gegenprobe(s)

        geraete = GERAETE
        if a.geraet:
            b, h = a.geraet.lower().split("x")
            geraete = [(int(b), int(h), a.geraet)]
        themes = [a.theme] if a.theme else ["dark", "light"]

        alle = []
        for b, h, name in geraete:
            for theme in themes:
                erg = lauf(s, b, h, theme, name)
                alle += erg
                print("--- %s-%s: %d Stationen, %d Befunde" % (
                    name, theme, len(erg), sum(zaehle(m) for m in erg)))

        print("\n" + "=" * 74)
        anzahl = bericht(alle)
        print("\nBilder: %s" % SCHUESSE)
        # Ein Lauf, der Pflichtangaben geraten hat, misst einen Zustand, den so nie
        # jemand erzeugt. Das ist KEIN gruener Lauf, auch wenn die Seiten sauber aussahen.
        if UNBEKANNTE_FELDER:
            print("\nROT - das Onboarding verlangt Felder, die dieses Werkzeug nicht kennt:")
            for feld in sorted(UNBEKANNTE_FELDER):
                print("  * %s" % feld)
            print("  Der Lauf hat dort geraten. WUNSCH in diesem Skript ergaenzen und")
            print("  erneut fahren - bis dahin sagt das Ergebnis nichts.")
            return 1
        if anzahl:
            print("\nROT - %d Ursache(n) in %d Stationen." % (anzahl, len(alle)))
            return 1
        print("\nGRUEN - %d Stationen ohne Befund." % len(alle))
        return 0
    finally:
        if not a.zeigen:
            s.stoppen()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
