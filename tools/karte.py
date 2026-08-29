# -*- coding: utf-8 -*-
u"""
Karte: erhebt den tatsaechlichen technischen Zustand des Repositories.

Was diese Datei ist
-------------------
Die Erhebung schreibt zwei Dateien aus EINEM Lauf:

  docs/module-index.json   maschinenlesbar - die Wahrheit, aus der spaeter ein Dashboard
                           entstehen kann, ohne dass irgendetwas neu erhoben werden muss
  docs/MODULE.md           dieselben Daten als lesbare Tabellen

Was diese Datei NICHT ist
-------------------------
Keine Roadmap, kein Backlog, keine Planung. Sie enthaelt ausschliesslich, was es
tatsaechlich gibt - keine Absichten, keine Prioritaeten, keine Termine, keine Bewertungen.

  "Bereich X hat keinen Pruefer"    ist eine Tatsache und steht drin.
  "Bereich X sollte einen bekommen" ist eine Absicht und steht nicht drin.

`ROADMAP.html` und `plans/` sind harte Ausschlussbereiche. Sie sind gitignored, und die
Erhebung geht ausschliesslich ueber `git ls-files` - schon dadurch koennen sie nicht
hineingeraten. Zusaetzlich prueft `_pruefe_sperrliste()` das Ergebnis noch einmal und
bricht ab, falls doch. Der Grund fuer den doppelten Boden: Sobald ein einziges geplantes
Feature in der Karte steht, ist ihre Kernaussage - "das ist der Ist-Zustand" - nicht mehr
belastbar, und genau das faellt niemandem auf.

Bewusst ohne Zeitstempel und ohne Commit-Hash: beides wuerde jeden Lauf zu einer
Aenderung machen und --pruefe wertlos.

Aufruf:
    python tools/karte.py                # erhebt neu und schreibt beide Dateien
    python tools/karte.py --pruefe       # schreibt nichts, Exit 1 bei Abweichung
    python tools/karte.py --neuerungen   # was hat sich gegenueber HEAD geaendert?
"""
import io
import json
import os
import re
import subprocess
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WURZEL, "tools"))

INDEX_JSON = os.path.join("docs", "module-index.json")
KARTE_MD = os.path.join("docs", "MODULE.md")

# Nichtoeffentliches. Taucht davon etwas in der Erhebung auf, ist die Erhebung falsch.
SPERRLISTE = ("ROADMAP.html", "plans/", "Fotos/", "Marketing/", "Instagram/",
              ".env", "docs/DATENSCHUTZ-INTERN.md", ".claude/settings.local.json")

BINAER = (".png", ".jpg", ".jpeg", ".webp", ".ico", ".gif", ".pdf", ".zip", ".woff",
          ".woff2", ".ttf")

# Abschnittsmarken, wie sie im Projekt seit jeher benutzt werden.
MARKE_JS = re.compile(r"^\s*//\s*[-=]{3,}\s*(.+?)\s*[-=]{3,}\s*$")
MARKE_CSS = re.compile(r"^\s*/\*\s*[-=]{3,}\s*(.+?)\s*[-=]{3,}\s*\*/\s*$")


def _lies(pfad):
    try:
        return io.open(os.path.join(WURZEL, pfad), encoding="utf-8", errors="replace").read()
    except Exception:
        return u""


def _git(*args):
    try:
        p = subprocess.run(["git"] + list(args), capture_output=True, text=True,
                           timeout=60, cwd=WURZEL, encoding="utf-8", errors="replace")
        return p.stdout or u""
    except Exception:
        return u""


def _gesperrt(pfad):
    p = pfad.replace("\\", "/")
    return any(p == s or p.startswith(s) for s in SPERRLISTE)


def _ohne_gesperrte(pfade):
    u"""Nichtoeffentliche Pfade aus einer erhobenen Liste entfernen.

    Ein Agent DARF `ROADMAP.html` in seinem Text erwaehnen - das ist eine Erwaehnung,
    kein Roadmap-Inhalt. Fuer die technische Karte ist die Datei trotzdem irrelevant:
    sie gehoert nicht zum Repository. Deshalb wird sie hier stillschweigend entfernt,
    statt den Lauf abzubrechen.
    """
    return [x for x in pfade if not _gesperrt(x.split(":", 1)[-1] if ":" in x else x)]


# --------------------------------------------------------------------------- Dateien

def erhebe_dateien():
    u"""Alle Dateien des Repositories - versioniert ODER neu, aber nie ignorierte.

    `--cached --others --exclude-standard` ist hier genau richtig: `--others` nimmt neue,
    noch nicht eingecheckte Dateien mit (sonst faende die Karte einen frisch angelegten
    Ordner erst nach dem Commit - sie waere also genau dann blind, wenn sich etwas
    aendert), und `--exclude-standard` haelt alles draussen, was .gitignore ausschliesst,
    ROADMAP.html und plans/ eingeschlossen. Der Ausschluss haengt damit an einer Stelle,
    die ohnehin gepflegt wird, statt an einer zweiten Liste hier.
    """
    raus = []
    for zeile in _git("ls-files", "--cached", "--others",
                      "--exclude-standard").split("\n"):
        pfad = zeile.strip()
        if not pfad or _gesperrt(pfad):
            continue
        voll = os.path.join(WURZEL, pfad)
        if not os.path.isfile(voll):
            continue
        # Groesse und Zeilenzahl bewusst aus dem NORMALISIERTEN Text, nicht aus
        # os.path.getsize(): .gitattributes setzt "* text=auto", also hat dieselbe
        # Datei unter Windows CRLF und auf dem Linux-Runner LF. Ueber die Dateigroesse
        # gerechnet waere die Karte auf jedem zweiten Rechner "veraltet" - und eine
        # Pruefung, die immer anschlaegt, sieht sich niemand mehr an.
        if pfad.replace("\\", "/") in (INDEX_JSON.replace("\\", "/"),
                                       KARTE_MD.replace("\\", "/")):
            # Die beiden erzeugten Dateien werden aufgefuehrt, aber OHNE Groesse.
            # Sonst verzeichnet die Karte ihre eigene Groesse - und ist in dem
            # Moment veraltet, in dem sie geschrieben wird. --pruefe waere damit
            # dauerhaft rot, ohne dass sich irgendetwas geaendert haette.
            eintrag = {"pfad": pfad, "erzeugt": True}
        elif pfad.lower().endswith(BINAER):
            eintrag = {"pfad": pfad, "bytes": os.path.getsize(voll)}
        else:
            text = _lies(pfad)
            eintrag = {"pfad": pfad, "bytes": len(text.encode("utf-8")),
                       "zeilen": text.count("\n") + 1}
        raus.append(eintrag)
    return sorted(raus, key=lambda d: d["pfad"])


# --------------------------------------------------------------------------- Bereiche

def _marken(pfad):
    u"""Abschnittsmarken einer Datei als (zeile, titel), in Dateireihenfolge."""
    text = _lies(pfad)
    if not text:
        return []
    treffer = []
    for nr, zeile in enumerate(text.split("\n"), 1):
        m = MARKE_JS.match(zeile) or MARKE_CSS.match(zeile)
        if m:
            titel = m.group(1).strip()
            if titel and not set(titel) <= set("-=*/ "):
                treffer.append((nr, titel))
    return treffer


def erhebe_bereiche(dateien):
    u"""Fachliche Abschnitte mit Zeilenbereich.

    Quelle sind die vorhandenen `// ---------- ... ----------`-Marken. Sie werden nicht
    fuer die Karte erfunden, sie stehen seit jeher im Code - die Karte liest sie nur aus.
    Der Bereich reicht jeweils bis zur naechsten Marke derselben Datei.
    """
    kandidaten = [d["pfad"] for d in dateien
                  if d["pfad"] == "index.html"
                  or d["pfad"].startswith(("css/", "data/", "lib/"))
                  or d["pfad"] == "sw.js"]
    raus = []
    for pfad in kandidaten:
        marken = _marken(pfad)
        if not marken:
            continue
        ende = next((d.get("zeilen", 0) for d in dateien if d["pfad"] == pfad), 0)
        for i, (nr, titel) in enumerate(marken):
            bis = marken[i + 1][0] - 1 if i + 1 < len(marken) else ende
            raus.append({"datei": pfad, "titel": titel, "von": nr, "bis": bis,
                         "zeilen": max(0, bis - nr + 1)})
    return raus


# --------------------------------------------------------------- Automatisierung

def _frontmatter(text):
    if not text.startswith("---"):
        return {}
    ende = text.find("\n---", 3)
    if ende < 0:
        return {}
    kopf = {}
    for zeile in text[3:ende].split("\n"):
        if ":" in zeile and not zeile.startswith(" "):
            k, _, v = zeile.partition(":")
            kopf[k.strip()] = v.strip().strip('"').strip("'")
    return kopf


PFAD_IM_TEXT = re.compile(
    r"`([A-Za-z0-9_./-]+\.(?:html|js|py|md|json|rules|css|yml|webmanifest))`")


def erhebe_agenten():
    ordner = os.path.join(WURZEL, ".claude", "agents")
    if not os.path.isdir(ordner):
        return []
    raus = []
    for name in sorted(os.listdir(ordner)):
        if not name.endswith(".md"):
            continue
        text = _lies(os.path.join(".claude", "agents", name))
        kopf = _frontmatter(text)
        werkzeuge = [t.strip() for t in kopf.get("tools", "").split(",") if t.strip()]
        raus.append({
            "name": kopf.get("name", name[:-3]),
            "datei": ".claude/agents/" + name,
            "modell": kopf.get("model", ""),
            # Ein Agent OHNE tools-Zeile hat alle Werkzeuge. Das ist eine Falle, die schon
            # zugeschlagen hat - deshalb wird sie hier ausdruecklich ausgewiesen.
            "werkzeuge": werkzeuge,
            "werkzeuge_offen": "tools" not in kopf,
            "pfade": _ohne_gesperrte(sorted(set(PFAD_IM_TEXT.findall(text)))),
        })
    return raus


def erhebe_skills():
    raus = []
    versioniert = set(z.strip() for z in _git("ls-files").split("\n") if z.strip())
    for ordnername in ("Skills", "skills"):
        ordner = os.path.join(WURZEL, ".claude", ordnername)
        if not os.path.isdir(ordner):
            continue
        for name in sorted(os.listdir(ordner)):
            rel = ".claude/%s/%s/SKILL.md" % (ordnername, name)
            if not os.path.isfile(os.path.join(WURZEL, rel)):
                continue
            text = _lies(rel)
            kopf = _frontmatter(text)
            # Zugekaufte Skills sind gitignored und liegen nur auf diesem Arbeitsplatz.
            # Sie gehoeren zum Ist-Zustand des Rechners, nicht zu dem des Repositories.
            # Wuerden sie mitgeschrieben, waere --pruefe in der CI - wo es sie nicht gibt -
            # dauerhaft rot, und eine Pruefung, die immer rot ist, prueft nichts mehr.
            if rel not in versioniert:
                continue
            raus.append({
                "name": kopf.get("name", name),
                "datei": rel,
                "zweck": kopf.get("description", "")[:200],
                "pfade": _ohne_gesperrte(sorted(set(PFAD_IM_TEXT.findall(text)))),
            })
    return sorted(raus, key=lambda d: d["name"])


def erhebe_hooks():
    try:
        roh = json.loads(_lies(os.path.join(".claude", "settings.json")) or "{}")
    except ValueError:
        return []
    raus = []
    for ereignis, eintraege in sorted((roh.get("hooks") or {}).items()):
        for eintrag in eintraege or []:
            for h in eintrag.get("hooks") or []:
                raus.append({
                    "ereignis": ereignis,
                    "matcher": eintrag.get("matcher", ""),
                    "kommando": h.get("command", ""),
                })
    return raus


# ------------------------------------------------------------------ Daten & Dienste

def erhebe_dienste():
    u"""Externe Verbindungen - dieselbe Erhebung, die abdeckung.py schon macht.

    Bewusst importiert statt nachgebaut: zwei Listen von Hosts wuerden auseinanderlaufen,
    und dann glaubt man der falschen.
    """
    try:
        import abdeckung
    except Exception:
        return []
    hosts = sorted(k.split(":", 1)[1] for k in abdeckung.ist_zustand()
                   if k.startswith("domain:"))
    return hosts


def erhebe_daten(dateien):
    konstanten = []
    for d in dateien:
        if not d["pfad"].startswith("data/") or not d["pfad"].endswith(".js"):
            continue
        for m in re.finditer(r"^\s*(?:const|var|let)\s+([A-Z][A-Z0-9_]*)\s*=",
                             _lies(d["pfad"]), re.M):
            konstanten.append({"name": m.group(1), "datei": d["pfad"]})

    text = _lies("index.html")
    schluessel = sorted(set(re.findall(r'"(wochenkueche[a-z0-9_]*)"', text)))
    sammlungen = sorted(set(re.findall(r"match\s+/([a-zA-Z][a-zA-Z0-9_]*)/",
                                       _lies("firestore.rules"))))
    return {
        "konstanten": sorted(konstanten, key=lambda d: d["name"]),
        "localstorage": schluessel,
        "firestore": sammlungen,
    }


# ------------------------------------------------------------------ Abhaengigkeiten

def erhebe_abhaengigkeiten(dateien):
    u"""Die Fassaden, ueber die getrennte Dateien miteinander reden - und wer sie benutzt.

    Das ist die eigentliche Architekturaussage der Karte: Solange jede Abhaengigkeit
    ueber eine benannte Fassade laeuft, ist die Grenze zwischen den Dateien pruefbar.
    """
    quellen = [d["pfad"] for d in dateien
               if d["pfad"].endswith((".js", ".html")) and not d["pfad"].startswith("vendor/")]
    texte = {p: _lies(p) for p in quellen}

    fassaden = {}
    for pfad, text in texte.items():
        for m in re.finditer(r"window\.([A-Za-z_$][A-Za-z0-9_$]*)\s*=", text):
            fassaden.setdefault(m.group(1), set()).add(pfad)

    raus = []
    for name in sorted(fassaden):
        muster = re.compile(r"(?<![.\w])(?:window\.)?" + re.escape(name) + r"\s*[.\[(]")
        verbraucher = sorted(p for p, t in texte.items()
                             if p not in fassaden[name] and muster.search(t))
        raus.append({
            "name": name,
            "definiert_in": sorted(fassaden[name]),
            "verbraucher": verbraucher,
            # "shared" ist keine Meinung, sondern eine Zaehlung: mehr als ein Verbraucher.
            "shared": len(verbraucher) > 1,
        })
    return raus


# ---------------------------------------------------------------------- Abdeckung

def erhebe_abdeckung():
    u"""Zuordnung Bereich -> Pruefer, GELESEN aus docs/ABDECKUNG.md.

    Die Karte schreibt diese Zuordnung nie und erfindet sie nie. ABDECKUNG.md bleibt die
    einzige Quelle - dort ist sie eine Entscheidung, hier nur eine Anzeige.
    """
    try:
        import abdeckung
    except Exception:
        return {"registriert": [], "ohne_pruefer": [], "lesbar": False}
    bekannt = abdeckung.register_kennungen()
    if bekannt is None or bekannt == "kaputt":
        return {"registriert": [], "ohne_pruefer": [], "lesbar": False}
    ist = abdeckung.ist_zustand()
    return {
        "registriert": _ohne_gesperrte(sorted(bekannt)),
        "ohne_pruefer": _ohne_gesperrte(sorted(ist - bekannt)),
        "lesbar": True,
    }


# ----------------------------------------------------------------------- Erhebung

def erhebe():
    dateien = erhebe_dateien()
    try:
        import quelle
        ladereihenfolge = quelle.eingebunden(os.path.join(WURZEL, "index.html"))
    except Exception:
        ladereihenfolge = []

    karte = {
        "schema": 1,
        "hinweis": ("Erzeugt von tools/karte.py. Nicht von Hand aendern. "
                    "Enthaelt ausschliesslich den technischen Ist-Zustand - "
                    "keine Roadmap, kein Backlog, keine Planung."),
        "dateien": dateien,
        "reiter": sorted(set(re.findall(r'data-tab="([a-z0-9-]+)"', _lies("index.html")))),
        "ladereihenfolge": ladereihenfolge,
        "bereiche": erhebe_bereiche(dateien),
        "agenten": erhebe_agenten(),
        "skills": erhebe_skills(),
        "hooks": erhebe_hooks(),
        "dienste": erhebe_dienste(),
        "daten": erhebe_daten(dateien),
        "abhaengigkeiten": erhebe_abhaengigkeiten(dateien),
        "abdeckung": erhebe_abdeckung(),
    }
    _pruefe_sperrliste(karte)
    return karte


def _pruefe_sperrliste(karte):
    u"""Doppelter Boden gegen Roadmap/Backlog in der technischen Karte."""
    roh = json.dumps(karte, ensure_ascii=False)
    for s in SPERRLISTE:
        if s in roh:
            raise SystemExit(
                u"karte.py: '%s' ist in der Erhebung gelandet. Die Karte bildet nur den "
                u"technischen Ist-Zustand ab - Roadmap und Planung bleiben draussen. "
                u"Abgebrochen, nichts geschrieben." % s)


# ------------------------------------------------------------------------ Ausgabe

def als_json(karte):
    return json.dumps(karte, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _zelle(x):
    if isinstance(x, bool):
        return u"ja" if x else u"nein"
    if isinstance(x, (list, tuple)):
        return u", ".join(str(i) for i in x) if x else u"—"
    return str(x)


def _tab(kopf, zeilen):
    if not zeilen:
        return u"_keine_\n\n"
    aus = u"| " + u" | ".join(kopf) + u" |\n"
    aus += u"|" + u"|".join(["---"] * len(kopf)) + u"|\n"
    for z in zeilen:
        aus += u"| " + u" | ".join(_zelle(x) for x in z) + u" |\n"
    return aus + u"\n"


def als_markdown(karte):
    a = []
    a.append(u"# Technische Landkarte\n\n")
    a.append(u"**Erzeugt von `tools/karte.py`. Nicht von Hand aendern.**\n\n")
    a.append(u"Diese Datei beschreibt ausschliesslich den *tatsaechlichen* technischen\n"
             u"Zustand des Repositories. Sie ist keine Roadmap und kein Backlog: nichts\n"
             u"Geplantes, nichts Gewuenschtes, keine Prioritaeten, keine Termine. Die\n"
             u"Roadmap liegt getrennt und ist gitignored.\n\n")
    a.append(u"Neu erzeugen mit `python tools/karte.py`, pruefen mit\n"
             u"`python tools/karte.py --pruefe`.\n\n")

    a.append(u"## 1. Reiter der App\n\n")
    a.append(_tab([u"Reiter"], [[r] for r in karte["reiter"]]))

    a.append(u"## 2. Ladereihenfolge\n\n")
    a.append(u"Die Reihenfolge ist Architektur: klassische Skripte laufen synchron\n"
             u"nacheinander, bevor die App-IIFE geparst wird.\n\n")
    a.append(_tab([u"#", u"Datei"],
                  [[i + 1, p] for i, p in enumerate(karte["ladereihenfolge"])]))

    a.append(u"## 3. Bereiche\n\n")
    a.append(u"Erhoben aus den Abschnittsmarken im Code, nicht von Hand gepflegt.\n\n")
    a.append(_tab([u"Datei", u"Bereich", u"Zeilen", u"Umfang"],
                  [[b["datei"], b["titel"], u"%d-%d" % (b["von"], b["bis"]), b["zeilen"]]
                   for b in karte["bereiche"]]))

    a.append(u"## 4. Agenten\n\n")
    a.append(_tab([u"Agent", u"Modell", u"Werkzeuge", u"Alle Werkzeuge?", u"Referenzierte Pfade"],
                  [[g["name"], g["modell"] or u"—", g["werkzeuge"],
                    u"JA - pruefen!" if g["werkzeuge_offen"] else u"nein", g["pfade"]]
                   for g in karte["agenten"]]))

    a.append(u"## 5. Skills\n\n")
    a.append(u"Nur die versionierten Skills des Projekts. Zugekaufte Skills liegen\n"
             u"ausserhalb des Repositories und gehoeren nicht zu seinem Zustand.\n\n")
    a.append(_tab([u"Skill", u"Referenzierte Pfade"],
                  [[s["name"], s["pfade"]] for s in karte["skills"]]))

    a.append(u"## 6. Hooks\n\n")
    a.append(_tab([u"Ereignis", u"Matcher", u"Kommando"],
                  [[h["ereignis"], h["matcher"] or u"—", u"`%s`" % h["kommando"]]
                   for h in karte["hooks"]]))

    a.append(u"## 7. Externe Dienste\n\n")
    a.append(_tab([u"Host"], [[d] for d in karte["dienste"]]))

    d = karte["daten"]
    a.append(u"## 8. Datenbereiche\n\n")
    a.append(u"### Konstanten in `data/`\n\n")
    a.append(_tab([u"Konstante", u"Datei"], [[k["name"], k["datei"]] for k in d["konstanten"]]))
    a.append(u"### localStorage\n\n")
    a.append(_tab([u"Schluessel"], [[k] for k in d["localstorage"]]))
    a.append(u"### Firestore-Sammlungen\n\n")
    a.append(_tab([u"Sammlung"], [[k] for k in d["firestore"]]))

    a.append(u"## 9. Abhaengigkeiten ueber Fassaden\n\n")
    a.append(u"`shared` ist hier keine Meinung, sondern eine Zaehlung: mehr als ein\n"
             u"Verbraucher.\n\n")
    a.append(_tab([u"Fassade", u"Definiert in", u"Verbraucher", u"Shared"],
                  [[x["name"], x["definiert_in"], x["verbraucher"], x["shared"]]
                   for x in karte["abhaengigkeiten"]]))

    ab = karte["abdeckung"]
    a.append(u"## 10. Pruefabdeckung\n\n")
    a.append(u"Gelesen aus `docs/ABDECKUNG.md` - dort wird sie gepflegt, hier nur\n"
             u"angezeigt.\n\n")
    if not ab["lesbar"]:
        a.append(u"_Register nicht lesbar._\n\n")
    else:
        a.append(u"Bereiche ohne Pruefer: **%d**\n\n" % len(ab["ohne_pruefer"]))
        a.append(_tab([u"Ohne Pruefer"], [[k] for k in ab["ohne_pruefer"]]))

    a.append(u"## 11. Dateien\n\n")
    a.append(_tab([u"Pfad", u"Zeilen", u"Bytes"],
                  [[f["pfad"], f.get("zeilen", u"—"), f.get("bytes", u"— (erzeugt)")]
                   for f in karte["dateien"]]))
    return u"".join(a)


# ------------------------------------------------------------------------ Betrieb

def schreibe(karte):
    io.open(os.path.join(WURZEL, INDEX_JSON), "w", encoding="utf-8",
            newline="\n").write(als_json(karte))
    io.open(os.path.join(WURZEL, KARTE_MD), "w", encoding="utf-8",
            newline="\n").write(als_markdown(karte))
    print(u"geschrieben: %s, %s" % (INDEX_JSON, KARTE_MD))
    print(u"  %d Dateien, %d Bereiche, %d Agenten, %d Skills, %d Hooks, %d Fassaden"
          % (len(karte["dateien"]), len(karte["bereiche"]), len(karte["agenten"]),
             len(karte["skills"]), len(karte["hooks"]), len(karte["abhaengigkeiten"])))


def _zeige_abweichung(alt, neu):
    import difflib
    zeilen = list(difflib.unified_diff(alt.split("\n"), neu.split("\n"),
                                       "gespeichert", "ist-zustand", lineterm="", n=0))
    for z in zeilen[:40]:
        print(u"        " + z, file=sys.stderr)
    if len(zeilen) > 40:
        print(u"        ... (%d weitere Zeilen)" % (len(zeilen) - 40), file=sys.stderr)


def pruefe(karte):
    alt_json = _lies(INDEX_JSON)
    alt_md = _lies(KARTE_MD)
    if not alt_json:
        print(u"FEHLER: %s fehlt. Einmal 'python tools/karte.py' laufen lassen." % INDEX_JSON,
              file=sys.stderr)
        return 1
    fehler = []
    if alt_json != als_json(karte):
        fehler.append(INDEX_JSON)
    if alt_md != als_markdown(karte):
        fehler.append(KARTE_MD)
    if fehler:
        print(u"FEHLER: Die Landkarte ist veraltet: " + ", ".join(fehler), file=sys.stderr)
        print(u"        Der Ist-Zustand des Repositories weicht von der gespeicherten "
              u"Erhebung ab.", file=sys.stderr)
        print(u"        Neu erzeugen: python tools/karte.py", file=sys.stderr)
        _zeige_abweichung(alt_json, als_json(karte))
        return 1
    print(u"Landkarte ist aktuell.")
    return 0


def neuerungen(karte):
    u"""Was ist technisch dazugekommen oder weggefallen - gegenueber dem letzten Commit.

    Bewusst als Kommando statt als Feld in der Karte: ein Feld waere nach jedem Commit
    falsch und wuerde die Karte selbst zum Rauschen machen.
    """
    roh = _git("show", "HEAD:" + INDEX_JSON.replace("\\", "/"))
    if not roh.strip():
        print(u"Noch keine committete Landkarte - alles ist neu.")
        return 0
    try:
        alt = json.loads(roh)
    except ValueError:
        print(u"Committete Landkarte ist nicht lesbar.", file=sys.stderr)
        return 2

    def pfade(k):
        return set(d["pfad"] for d in k.get("dateien", []))

    def namen(k, feld):
        return set(d["name"] for d in k.get(feld, []))

    def zeig(titel, dazu, weg):
        print(u"")
        print(titel)
        for p in sorted(dazu):
            print(u"  + " + p)
        for p in sorted(weg):
            print(u"  - " + p)
        if not dazu and not weg:
            print(u"  (unveraendert)")

    zeig(u"Dateien", pfade(karte) - pfade(alt), pfade(alt) - pfade(karte))
    zeig(u"Agenten", namen(karte, "agenten") - namen(alt, "agenten"),
         namen(alt, "agenten") - namen(karte, "agenten"))
    zeig(u"Skills", namen(karte, "skills") - namen(alt, "skills"),
         namen(alt, "skills") - namen(karte, "skills"))
    zeig(u"Fassaden", namen(karte, "abhaengigkeiten") - namen(alt, "abhaengigkeiten"),
         namen(alt, "abhaengigkeiten") - namen(karte, "abhaengigkeiten"))
    zeig(u"Externe Dienste", set(karte["dienste"]) - set(alt.get("dienste", [])),
         set(alt.get("dienste", [])) - set(karte["dienste"]))
    return 0


def main():
    karte = erhebe()
    if "--pruefe" in sys.argv:
        return pruefe(karte)
    if "--neuerungen" in sys.argv:
        return neuerungen(karte)
    schreibe(karte)
    return 0


if __name__ == "__main__":
    sys.exit(main())
