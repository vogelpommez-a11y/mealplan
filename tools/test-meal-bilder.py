# Pruefstand fuer tools/meal-bilder.py - ohne einen einzigen API-Aufruf.
# Getestet wird alles, was NACH der Antwort passiert: Verkleinern, WebP, Dateinamen,
# Prompt-Bau, Kostenschutz. Ein Fehler darin faellt sonst erst beim ersten kostenpflichtigen
# Lauf auf - und kostet dann Geld pro Fehlversuch.
import importlib.util, sys, io, json, tempfile
from pathlib import Path
from PIL import Image

PFAD = Path(r"C:\Users\Paddy\Documents\Paddys Mealplan\tools\meal-bilder.py")
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
        pruef("Seitenverhaeltnis bleibt", erg.height, round(1024 * mb.ZIEL_BREITE / 1536))
        pruef("Format ist WebP", erg.format, "WEBP")
    pruef("Groesse unter 150 KB", groesse < 150 * 1024, True)

    # Kleines Bild darf NICHT hochskaliert werden
    klein = Image.new("RGB", (400, 300), (10, 10, 10))
    pk = io.BytesIO(); klein.save(pk, "PNG")
    ziel2 = Path(tmp) / "klein.webp"
    mb.speichere_webp(pk.getvalue(), ziel2)
    with Image.open(ziel2) as k:
        pruef("kleines Bild bleibt klein", k.width, 400)

# --- Konstanten, die eingefroren sind ---
pruef("Modell ist gesetzt", mb.MODELL, "gpt-image-2")
pruef("Kostenschutz existiert", mb.MAX_BILDER > 0, True)
pruef("Credits nennen die KI-Herkunft", "KI-generiert" in mb.CREDIT_VORLAGE["urheber"], True)
pruef("Credits nennen das Modell", mb.MODELL in mb.CREDIT_VORLAGE["urheber"], True)

print()
print("FEHLGESCHLAGEN: %d von %d" % (bad, ok + bad) if bad else "ALLE %d PRUEFUNGEN GRUEN" % ok)
sys.exit(1 if bad else 0)
