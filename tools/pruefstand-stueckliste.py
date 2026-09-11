# -*- coding: utf-8 -*-
u"""
Die Schnellauswahl im Picker: stimmt sie, und was fehlt ihr noch?

Anlass (11.09.2026): Beim Erweitern der Stueckliste sind vier Eintraege uebersehen worden -
Kirsche, Erdbeere, Mango und die gruene Olive standen laengst in FOODS, nur ohne Gewicht je
Stueck. Niemand hat es gemerkt, weil die Luecke nirgends sichtbar war. Genau diese Luecke
macht dieses Skript sichtbar.

Was es HART prueft (rot, wenn es nicht stimmt):

  1. Jeder Name in PIECE_TOP loest in FOODS auf. Tut er das nicht, faellt der Vorschlag
     im Picker STILL weg - pieceTop() filtert ihn mit .filter(Boolean) heraus.
  2. Jeder PIECE_TOP-Eintrag ist auch wirklich stueckweise zaehlbar (Einheit "st" oder
     Gramm je Stueck). Sonst steht er in der Liste und traegt keine Menge.
  3. Jedes Gramm-je-Stueck-Feld ist eine plausible Zahl (groesser 0, hoechstens 1000 g)
     und sitzt an der richtigen Stelle (achtes Feld, Einheit davor gesetzt).
  4. Kein Name kommt doppelt vor - eine Dublette waere im Picker nicht unterscheidbar.
  5. FOOD_ICON (data/ikonen.js) zeigt nur auf Namen, die es in FOODS gibt, und nur auf
     Symbole, die es in ICONS gibt. Beides faellt sonst nicht auf: foodIcon() faellt still
     auf das Fruchtsymbol zurueck, so wie es vor dem 11.09.2026 ueberall aussah.

Was es BERICHTET, ohne rot zu werden: welche stueckweise zaehlbaren Eintraege noch kein
eigenes Symbol haben, und welche Eintraege aus Obst, Gemuese und Backwaren noch
kein Gewicht je Stueck haben. Das ist bewusst kein Fehler - Spinat und Rucola brauchen keins.
Es ist die Durchsehliste fuer den naechsten Ausbau.

Gegenprobe - ohne sie zaehlt kein Ergebnis:

  python tools/pruefstand-stueckliste.py --gegenprobe

Sie nimmt dem Apfel im Speicher das Stueckgewicht weg. Danach MUSS der Apfel in der
Lueckenliste stehen und die PIECE_TOP-Pruefung rot werden - sonst misst das Skript nichts.

Aufruf:  python tools/pruefstand-stueckliste.py [--gegenprobe]
"""
import io, os, re, sys

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOODS_DATEI = os.path.join(BASIS, "data", "foods.js")
INDEX = os.path.join(BASIS, "index.html")

# Die Kategorien, in denen ein Gewicht je Stueck ueberhaupt Sinn ergibt. Sie kommen aus den
# Abschnittskommentaren in foods.js - steht dort einmal ein anderer Text, faellt die
# Durchsehliste leer aus und das Skript sagt es (statt still nichts zu melden).
STUECK_KATEGORIEN = ["Obst", "Gemüse", "Brot und Backwaren"]


def lies_foods():
    u"""FOODS aus data/foods.js lesen - Name, Felder und Abschnitt."""
    s = io.open(FOODS_DATEI, encoding="utf-8").read()
    block = s[s.index("const FOODS = ["):]
    gruppe = "?"
    eintraege = []
    for zeile in block.split("\n"):
        k = zeile.strip()
        if k.startswith("//"):
            gruppe = k[2:].strip()
            continue
        for m in re.finditer(r'\["([^"]+)"([^\]]*)\]', zeile):
            felder = [t.strip() for t in m.group(2).split(",") if t.strip()]
            eintraege.append({"name": m.group(1), "felder": felder, "gruppe": gruppe})
    return eintraege


def stueckgewicht(e):
    u"""Gramm je Stueck, oder None. Einheit "st" heisst: schon je Stueck erfasst."""
    f = e["felder"]
    einheit = f[4].strip('"') if len(f) > 4 else "g"
    if einheit == "st":
        return "st"
    if len(f) >= 7 and re.match(r"^-?[\d.]+$", f[6]):
        return float(f[6])
    return None


def lies_food_icon():
    u"""FOOD_ICON aus data/ikonen.js - die Zuordnung Lebensmittel -> Symbol."""
    t = io.open(os.path.join(BASIS, "data", "ikonen.js"), encoding="utf-8").read()
    m = re.search(r"const FOOD_ICON = \{(.*?)\n  \};", t, re.S)
    if not m:
        raise SystemExit("FOOD_ICON nicht gefunden - der Pruefstand misst sonst gegen nichts.")
    return dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', m.group(1)))


def lies_icons():
    t = io.open(os.path.join(BASIS, "data", "ikonen.js"), encoding="utf-8").read()
    m = re.search(r"const ICONS = \{(.*?)\n  \};", t, re.S)
    if not m:
        raise SystemExit("ICONS nicht gefunden.")
    return set(re.findall(r"^\s*([a-zA-Z_][\w]*)\s*:", m.group(1), re.M))


def lies_piece_top():
    s = io.open(INDEX, encoding="utf-8").read()
    m = re.search(r'const PIECE_TOP = \[(.*?)\];', s, re.S)
    if not m:
        raise SystemExit("PIECE_TOP nicht gefunden - der Pruefstand misst sonst gegen nichts.")
    return re.findall(r'"([^"]+)"', m.group(1))


def main():
    gegenprobe = "--gegenprobe" in sys.argv[1:]
    eintraege = lies_foods()
    if gegenprobe:
        # Dem Apfel das Stueckgewicht wegnehmen - im Speicher, die Datei bleibt unberuehrt.
        for e in eintraege:
            if e["name"] == "Apfel":
                e["felder"] = e["felder"][:5]

    print("Pruefstand Schnellauswahl (Stueckliste)")
    print("Quelle: data/foods.js + PIECE_TOP aus index.html"
          + ("   [GEGENPROBE: Apfel ohne Stueckgewicht]" if gegenprobe else ""))
    print("")

    pruefungen = []

    def p(was, ok, hinweis=""):
        pruefungen.append((was, ok, hinweis))

    nach_name = {}
    dubletten = []
    for e in eintraege:
        if e["name"] in nach_name:
            dubletten.append(e["name"])
        nach_name[e["name"]] = e

    p("Keine doppelten Namen in FOODS", not dubletten, ", ".join(dubletten))

    # --- PIECE_TOP ---
    top = lies_piece_top()
    p("PIECE_TOP ist nicht leer", len(top) > 0)
    for name in top:
        e = nach_name.get(name)
        p(u"PIECE_TOP loest auf: " + name, e is not None,
          "" if e else "steht nicht in FOODS - faellt im Picker still weg")
        if e:
            p(u"PIECE_TOP zaehlbar: " + name, stueckgewicht(e) is not None,
              "" if stueckgewicht(e) is not None else "kein Gewicht je Stueck")

    # --- Format und Plausibilitaet ---
    zaehlbar = []
    for e in eintraege:
        g = stueckgewicht(e)
        if g is None:
            continue
        zaehlbar.append(e["name"])
        if g == "st":
            continue
        p(u"Plausibles Stueckgewicht: " + e["name"], 0 < g <= 1000, "%g g" % g)
        f = e["felder"]
        einheit = f[4].strip('"') if len(f) > 4 else ""
        p(u"Einheit vor dem Gewicht gesetzt: " + e["name"], einheit in ("g", "ml"), einheit)

    # --- Symbole: FOOD_ICON ---
    # Bis zum 11.09.2026 trug jeder Eintrag dasselbe Fruchtsymbol. Seither gibt es eine
    # Zuordnung - und damit zwei neue Arten, sie kaputt zu machen: ein Name, den es nicht
    # (mehr) gibt, und ein Symbol, das nicht existiert. Beides faellt sonst nicht auf, weil
    # foodIcon() still auf "fruit" zurueckfaellt.
    icons = lies_icons()
    zuordnung = lies_food_icon()
    p("FOOD_ICON ist nicht leer", len(zuordnung) > 0)
    tote = [n for n in zuordnung if n not in nach_name]
    p("Keine tote Zuordnung in FOOD_ICON", not tote, ", ".join(tote))
    fremde = sorted(set(v for v in zuordnung.values() if v not in icons))
    p("Jedes zugeordnete Symbol gibt es in ICONS", not fremde, ", ".join(fremde))
    ohne_icon = [n for n in zaehlbar if n not in zuordnung]

    # --- Bericht: was in den Stueck-Kategorien noch fehlt ---
    luecken = []
    kategorien_gefunden = set()
    for e in eintraege:
        if e["gruppe"] in STUECK_KATEGORIEN:
            kategorien_gefunden.add(e["gruppe"])
            if stueckgewicht(e) is None:
                luecken.append((e["gruppe"], e["name"]))
    p("Die Stueck-Kategorien gibt es in foods.js",
      len(kategorien_gefunden) == len(STUECK_KATEGORIEN),
      "gefunden: " + ", ".join(sorted(kategorien_gefunden)))

    breit = max(len(x[0]) for x in pruefungen)
    rot = 0
    for was, ok, hinweis in pruefungen:
        if ok:
            print("  OK    " + was + (("   (" + hinweis + ")") if hinweis and False else ""))
        else:
            rot += 1
            print("  ROT   " + was.ljust(breit) + ("   " + hinweis if hinweis else ""))

    print("")
    print("Stueckweise zaehlbar: %d Eintraege" % len(zaehlbar))
    print("")
    if ohne_icon:
        print("Ohne eigenes Symbol (faellt auf das Fruchtsymbol zurueck):")
        for n in ohne_icon:
            print("      " + n)
    else:
        print("Jeder stueckweise zaehlbare Eintrag hat ein eigenes Symbol.")
    print("")
    print("Ohne Gewicht je Stueck - zum Durchsehen, KEIN Fehler:")
    letzte = None
    for gruppe, name in luecken:
        if gruppe != letzte:
            print("  " + gruppe)
            letzte = gruppe
        print("      " + name)
    print("")
    print("ERGEBNIS %d gruen, %d rot  (%d Messgroessen)"
          % (len(pruefungen) - rot, rot, len(pruefungen)))
    return 1 if rot else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
