# Pruefstand fuer tools/meal-bilder.py - ohne einen einzigen API-Aufruf.
# Getestet wird alles, was NACH der Antwort passiert: Verkleinern, WebP, Dateinamen,
# Prompt-Bau, Kostenschutz. Ein Fehler darin faellt sonst erst beim ersten kostenpflichtigen
# Lauf auf - und kostet dann Geld pro Fehlversuch.
import importlib.util, sys, io, json, tempfile
from pathlib import Path
from PIL import Image

# Nachbarskript im selben Ordner - kein fester Laufwerkspfad.
PFAD = Path(__file__).resolve().parent / "meal-bilder.py"
spec = importlib.util.spec_from_file_location("mb", PFAD)
mb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mb)

ok = bad = 0
def pruef(name, ist, soll):
    global ok, bad
    gut = ist == soll
    if gut: ok += 1
    else: bad += 1
    print(("OK   " if gut else "FEHL ") + name + ("" if gut else "  ist=%r soll=%r" % (ist, soll)))

# --- slug: Umlaute und Sonderzeichen muessen zu brauchbaren Dateinamen werden ---
pruef("Umlaute werden umschrieben", mb.slug("Hähnchen mit Püree"), "haehnchen-mit-pueree")
pruef("scharfes S", mb.slug("Weißbrot"), "weissbrot")
pruef("Klammern und Komma", mb.slug("Bowl (vegan), scharf"), "bowl-vegan-scharf")

# --- prompt_fuer: Stil haengt immer dran, Zutaten schaerfen ---
p1 = mb.prompt_fuer("Linsencurry")
pruef("Gerichtname steht vorn", p1.startswith("Linsencurry"), True)
pruef("Stil-Baustein haengt dran", mb.STIL in p1, True)
p2 = mb.prompt_fuer("Bowl", ["Tofu", "Reis", "Brokkoli"])
pruef("Zutaten kommen mit hinein", "with Tofu, Reis, Brokkoli" in p2, True)
p3 = mb.prompt_fuer("Bowl", ["a", "b", "c", "d", "e", "f"])
pruef("hoechstens vier Zutaten", "with a, b, c, d," in p3, True)

# --- haupt_zutaten: die groessten Mengen beschreiben das Gericht, nicht die ersten vier ---
rez = { "name": "Test", "ingredients": [
    "Salz, Pfeffer",                                    # Freitext, keine Menge
    { "name": "Petersilie", "grams": 5 },
    { "name": "Basmatireis", "grams": 200 },
    { "name": "Rote Linsen", "grams": 120 },
    { "name": "Olivenoel", "grams": 10 },
    { "name": "Paprika", "grams": 1, "unit": "st" } ] }
h = mb.haupt_zutaten(rez)
pruef("Freitext ohne Menge faellt raus", "Salz, Pfeffer" in h, False)
pruef("groesste Menge zuerst", h[0], "Basmatireis")
pruef("zweitgroesste danach", h[1], "Rote Linsen")
pruef("Stueckzahl wird hochgewichtet", "Paprika" in h, True)
pruef("Kleinkram faellt raus", "Petersilie" in h, False)
pruef("hoechstens vier", len(h) <= 4, True)
pruef("Rezept ohne Zutaten ist harmlos", mb.haupt_zutaten({"name": "x"}), [])

# --- Diaet-Hinweise: der Grund, warum kein Haehnchen im veganen Curry landet ---
pv = mb.prompt_fuer("Curry", ["Linsen"], None, "Hauptgericht", ["vegan"])
pruef("vegan wird ausdruecklich verneint", "no meat" in pv and "no dairy" in pv, True)
pruef("Kategorie bestimmt das Geschirr", "on a plate" in pv, True)
pf = mb.prompt_fuer("Porridge", None, None, "Frühstück", ["vegetarisch"])
pruef("Fruehstueck kommt in die Schuessel", "in a bowl" in pf, True)
pruef("vegetarisch verneint nur Fleisch und Fisch",
      "no meat, no fish" in pf and "no dairy" not in pf, True)
pruef("Diaet steht VOR dem Stil",
      pf.index("vegetarian") < pf.index("moody food photography"), True)
po = mb.prompt_fuer("Irgendwas", None, None, None, [])
pruef("ohne Tags kein Diaet-Zusatz", "no meat" in po, False)

# --- speichere_webp: das eigentliche Risiko, weil hier Bytes und Pillow zusammenkommen ---
gross = Image.new("RGB", (1536, 1024), (200, 120, 60))
puffer = io.BytesIO(); gross.save(puffer, "PNG")
with tempfile.TemporaryDirectory() as tmp:
    ziel = Path(tmp) / "unterordner" / "test.webp"
    groesse = mb.speichere_webp(puffer.getvalue(), ziel)
    pruef("Datei entsteht", ziel.exists(), True)
    pruef("Ordner wird angelegt", ziel.parent.is_dir(), True)
    with Image.open(ziel) as erg:   # schliessen, sonst haelt Windows die Datei fest
        pruef("auf Zielbreite verkleinert", erg.width, mb.ZIEL_BREITE)
        # Zugeschnitten, NICHT proportional verkleinert: Die App zeigt einen sehr breiten
        # Streifen (.rimg 116 px hoch), ein 3:2-Bild verlaere dort knapp die Haelfte.
        pruef("auf das Zielverhaeltnis zugeschnitten",
              round(erg.width / erg.height, 2), mb.ZUSCHNITT)
        pruef("Format ist WebP", erg.format, "WEBP")
    pruef("Groesse unter 150 KB", groesse < 150 * 1024, True)

    # Wird MITTIG zugeschnitten? Ein Testbild mit roten Streifen oben und unten: die muessen
    # verschwinden, die Mitte muss bleiben. Ohne diese Pruefung koennte der Zuschnitt vom
    # oberen Rand her laufen und immer die Bildmitte anschneiden.
    m = Image.new("RGB", (1536, 1024), (0, 200, 0))
    for y in list(range(0, 100)) + list(range(924, 1024)):
        for x in range(1536):
            m.putpixel((x, y), (255, 0, 0))
    pm = io.BytesIO(); m.save(pm, "PNG")
    ziel3 = Path(tmp) / "mitte.webp"
    mb.speichere_webp(pm.getvalue(), ziel3)
    with Image.open(ziel3) as z3:
        oben = z3.getpixel((z3.width // 2, 3))
        mitte = z3.getpixel((z3.width // 2, z3.height // 2))
        pruef("roter Rand oben ist weggeschnitten", oben[0] < 200, True)
        pruef("gruene Mitte ist erhalten", mitte[1] > 150, True)

    # Kleines Bild darf NICHT hochskaliert werden
    klein = Image.new("RGB", (400, 300), (10, 10, 10))
    pk = io.BytesIO(); klein.save(pk, "PNG")
    ziel2 = Path(tmp) / "klein.webp"
    mb.speichere_webp(pk.getvalue(), ziel2)
    with Image.open(ziel2) as k:
        pruef("kleines Bild bleibt klein", k.width, 400)

# --- Dateiname: die id gewinnt, und sie wird ASCII-sicher gemacht ---
# Ohne diese Regel zeigte die App nach einer Namensaenderung auf eine Datei, die es nicht
# mehr gibt - und bei einer id mit Umlaut auf einen Pfad, den kein Server gern ausliefert.
pruef("id schlaegt den Namen",
      mb.dateiname({"name": "Ganz anders benanntes Gericht", "id": "linsen-dal"}), "linsen-dal")
pruef("Umlaut in der id wird umgeschrieben",
      mb.dateiname({"name": "X", "id": "rührei-avocadobrot"}), "ruehrei-avocadobrot")
pruef("ohne id zaehlt der Name",
      mb.dateiname({"name": "Tofu-Bowl (scharf)"}), "tofu-bowl-scharf")

# --- Geschirr: der Name darf die Kategorie ueberstimmen ---
# Ein Brot in einer Schuessel sieht sofort falsch aus (TROUBLESHOOTING 88).
def geschirr(name, kat):
    p = mb.prompt_fuer(name, None, None, kat, None)
    for w in ("in a small bowl", "in a bowl", "on a plate", "in a glass"):
        if w in p:
            return w
    return None
pruef("Brot liegt auf dem Teller, nicht in der Schuessel",
      geschirr("Rührei mit Avocado auf Vollkornbrot", "Frühstück"), "on a plate")
pruef("Pancakes ebenso", geschirr("Protein-Pancakes mit Skyr", "Frühstück"), "on a plate")
pruef("Ofengemuese vom Blech ebenso", geschirr("Ofengemüse vom Blech", "Beilage"), "on a plate")
pruef("ein normales Fruehstueck bleibt in der Schuessel",
      geschirr("Overnight Oats mit Beeren", "Frühstück"), "in a bowl")
pruef("Getraenke bleiben im Glas",
      geschirr("Grüner Smoothie mit Spinat", "Getränk"), "in a glass")

# --- Konstanten, die eingefroren sind ---
pruef("Modell ist gesetzt", mb.MODELL, "gpt-image-2")
pruef("Kostenschutz existiert", mb.MAX_BILDER > 0, True)
pruef("Credits nennen die KI-Herkunft", "KI-generiert" in mb.CREDIT_VORLAGE["urheber"], True)
pruef("Credits nennen das Modell", mb.MODELL in mb.CREDIT_VORLAGE["urheber"], True)

print()
print("FEHLGESCHLAGEN: %d von %d" % (bad, ok + bad) if bad else "ALLE %d PRUEFUNGEN GRUEN" % ok)
sys.exit(1 if bad else 0)
