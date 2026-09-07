# Ausschneide-Pruefstand Bildstichworte: PHOTOS, PHOTO_RULES, CAT_PHOTO und photoFor.
#
# Warum es diesen Pruefstand gibt: Die Zuordnung Gerichtname -> Foto ist eine Liste von
# Teilwort-Treffern, bei der der ERSTE gewinnt. Ob sie richtig ist, sieht man dem Code nicht
# an - man sieht es erst, wenn man echte Gerichtnamen hindurchschickt. Am 07.09.2026 ergab
# genau das: "Schnitzel mit Pommes" landete auf einem Ribeye-Steak, "Currywurst" auf einem
# Burger, "Tofu-Gemuesepfanne" auf Blattsalat, "Edamame" auf gar nichts. Kein Test hat das
# je gemeldet, weil keiner die Zuordnung als Ganzes angesehen hat.
#
# Gegenprobe (CLAUDE.md 11) - MUSS durchfallen:
#   git show HEAD:data/bilder.js > alt-bilder.js
#   python tools/pruefstand-bildstichworte.py alt-bilder.js
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Die Regeln stehen in data/bilder.js, photoFor() in index.html. Ausgetauscht wird beim
# Gegenprobenlauf nur die erste - die Rangfolge selbst hat sich nicht geaendert.
BILDER = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(WURZEL, "data", "bilder.js")
SEITE = os.path.join(WURZEL, "index.html")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruefstand-bildstichworte.html")


def block(text, start_sig, end_sig):
    zeilen = text.split("\n")
    a = b = None
    for i, z in enumerate(zeilen):
        if a is None and z.startswith(start_sig):
            a = i
        elif a is not None and z.startswith(end_sig):
            b = i
            break
    if a is None or b is None:
        raise SystemExit("BLOCK NICHT GEFUNDEN: " + start_sig + "  in " + text[:0].join([]) or start_sig)
    return "\n".join(zeilen[a:b + 1])


def schnitt(text, sig):
    zeilen = text.split("\n")
    start = None
    for i, z in enumerate(zeilen):
        if z.startswith(sig):
            start = i
            break
    if start is None:
        raise SystemExit("NICHT GEFUNDEN: " + sig)
    if zeilen[start].rstrip().endswith("}"):
        return zeilen[start]
    for j in range(start + 1, len(zeilen)):
        if zeilen[j] == "  }":
            return "\n".join(zeilen[start:j + 1])
    raise SystemExit("KEIN ENDE: " + sig)


daten = io.open(BILDER, encoding="utf-8").read()
seite = pm_quelle.lade_seite(SEITE)

teile = [
    block(daten, "  const PHOTOS = {", "  };"),
    block(daten, "  const PHOTO_RULES = [", "  const CAT_PHOTO ="),
    # Der Katalog und die Bibliotheks-Zuordnung: photoFor() prueft sie VOR den Stichwoertern.
    # Ohne sie waere die Rangfolge nur behauptet, nicht gemessen (siehe die drei blinden
    # Flecken vom 07.09.2026 - zu grosszuegig gestubbt ist der haeufigste Fehler hier).
    block(pm_quelle.lade_seite(SEITE), "  const COOKBOOK = [", "  ];"),
    block(seite, "  const LIB_IMG = ", "  function libPhoto("),
    schnitt(seite, "  function photoFor("),
    schnitt(seite, "  function safeImage("),
    # Der Herkunftshinweis unter dem grossen Foto. Er ist eine Offenlegung nach dem
    # AI Act, keine Verzierung - und er darf bei eigenen Fotos des Nutzers NICHT
    # erscheinen, sonst behauptet die App etwas Falsches ueber dessen Bild.
    schnitt(seite, "  function istEigenesFoto("),
    schnitt(seite, "  function bildHinweisHtml("),
    schnitt(seite, "  function bildAlt("),
    schnitt(seite, "  function syncBildHinweis("),
]
code = "\n\n".join(teile)

# Die Bilddateien, die TATSAECHLICH in img/ liegen. Der Browser kann das unter file:// nicht
# nachsehen. Ohne diesen Abgleich prueft die Seite nur, dass ein Dateiname dasteht - nicht,
# dass es die Datei gibt. Ein Tippfehler ergibt in der App eine leere Bildflaeche.
BILD_ORDNER = os.path.join(WURZEL, "img")
vorhanden = sorted(f for f in os.listdir(BILD_ORDNER)
                   if os.path.isfile(os.path.join(BILD_ORDNER, f))) if os.path.isdir(BILD_ORDNER) else []
code += "\n\nvar DATEIEN = " + json.dumps(vorhanden) + ";"

# Jede Stelle, die ein grosses Foto rendert, muss den Hinweis tragen. Gezaehlt wird im
# Quelltext, nicht im Browser: Die zweite Ansicht steckt hinter "Neues Meal" und liesse
# sich nur ueber einen kompletten Formular-Ablauf erreichen.
grosse_ansichten = seite.count('<div class="ms-photo has-photo">')
hinweis_aufrufe = seite.count("${bildHinweisHtml(")
if grosse_ansichten != hinweis_aufrufe:
    print("FEHL  %d grosse Foto-Ansichten, aber %d Hinweis-Aufrufe in index.html"
          % (grosse_ansichten, hinweis_aufrufe))
    print("      Jede Ansicht mit `.ms-photo has-photo` braucht ${bildHinweisHtml(...)} im")
    print("      modal-body - sonst zeigt eine davon ein KI-Bild ohne Kennzeichnung.")
    raise SystemExit(1)
print("OK    alle %d grossen Foto-Ansichten tragen den KI-Hinweis" % grosse_ansichten)

HTML = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Bildstichworte</title>
<pre id="log"></pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) { document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")"; };
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
}
// safeImage wird ausgeschnitten, nicht gestubbt - es entscheidet mit ueber die Rangfolge.
function esc(s) { return String(s == null ? "" : s); }

__CODE__

// Der Schluessel zu einem Pfad zurueck: die Zusagen unten sprechen ueber Schluessel
// ("Schnitzel gehoert auf das Schnitzelbild"), photoFor liefert einen Pfad.
function schluesselVon(pfad) {
  for (var k in PHOTOS) { if (PHOTOS[k] === pfad) return k; }
  return "?? " + pfad;
}
function fuer(name, kategorie) {
  return schluesselVon(photoFor({ name: name, category: kategorie || "Hauptgericht" }));
}

(function () {
  // ---- 1. Kein Schluessel zeigt ins Leere ----
  var fehlend = [];
  PHOTO_RULES.forEach(function (r) { if (!PHOTOS[r[1]]) fehlend.push(r[1]); });
  pruef("jeder Schluessel aus PHOTO_RULES steht in PHOTOS", fehlend, []);
  var fehlendKat = [];
  for (var c in CAT_PHOTO) { if (!PHOTOS[CAT_PHOTO[c]]) fehlendKat.push(CAT_PHOTO[c]); }
  pruef("jeder Schluessel aus CAT_PHOTO steht in PHOTOS", fehlendKat, []);
  pruef("das neutrale Bild existiert", !!PHOTOS.neutral, true);

  // ---- 2. Jede Datei liegt wirklich im Ordner ----
  // Das ist die Pruefung, die ein Tippfehler im Dateinamen NICHT ueberlebt. Sie greift
  // auch, wenn jemand eine Endung aendert: img/salad.jpg heisst .jpg, weil dieser Pfad in
  // bereits verschickten Sharing-Links und in worker/og.js steht.
  var ohneDatei = [];
  for (var k in PHOTOS) {
    var name = PHOTOS[k].replace(/^img\\//, "");
    if (DATEIEN.indexOf(name) < 0) ohneDatei.push(PHOTOS[k]);
  }
  pruef("jede Datei aus PHOTOS liegt in img/", ohneDatei, []);
  pruef("die fuenf .jpg-Pfade sind unveraendert",
    [PHOTOS.salad, PHOTOS.porridge, PHOTOS.pizza, PHOTOS.sandwich, PHOTOS.neutral],
    ["img/salad.jpg", "img/porridge.jpg", "img/pizza.jpg", "img/sandwich.jpg", "img/neutral.jpg"]);

  // ---- 3. Keine Regel wird von einer frueheren verdeckt ----
  // includes() kennt keine Wortgrenzen. Steht "curry" VOR "currywurst", gewinnt bei
  // "Currywurst" das Curry - und das Stichwort "currywurst" waere unerreichbar, ohne dass
  // das je auffiele. Genau so lag es bis zum 07.09.2026 bei "wiener" und "wiener schnitzel".
  var verdeckt = [];
  for (var i = 0; i < PHOTO_RULES.length; i++) {
    for (var w = 0; w < PHOTO_RULES[i][0].length; w++) {
      var wort = PHOTO_RULES[i][0][w];
      for (var j = 0; j < i; j++) {
        if (PHOTO_RULES[j][1] === PHOTO_RULES[i][1]) continue;   // gleiches Ziel, egal
        for (var v = 0; v < PHOTO_RULES[j][0].length; v++) {
          if (wort.indexOf(PHOTO_RULES[j][0][v]) >= 0) {
            verdeckt.push(wort + " verdeckt von " + PHOTO_RULES[j][0][v] + " (" + PHOTO_RULES[j][1] + ")");
          }
        }
      }
    }
  }
  pruef("kein Stichwort wird von einer frueheren Regel verdeckt", verdeckt, []);

  // ---- 4. Echte Gerichtnamen ----
  // Die Zusage, um die es eigentlich geht. Jede Zeile ist ein Name, den ein Nutzer
  // tatsaechlich eintippt.
  var FAELLE = [
    // die Fehlgriffe, wegen derer der Bildsatz getauscht wurde
    ["Schnitzel mit Pommes", "schnitzel"],
    ["Wiener Schnitzel", "schnitzel"],
    ["Cordon bleu", "schnitzel"],
    ["Currywurst mit Fritten", "wurst"],
    ["Bratwurst", "wurst"],
    ["Leberkaese", "wurst"],
    ["Frikadellen mit Kartoffelsalat", "hack"],
    ["Hackbaellchen in Tomatensauce", "hack"],
    ["Tofu-Gemuesepfanne", "tofu"],
    ["Tempeh-Pfanne", "tofu"],
    ["Seitan-Geschnetzeltes", "tofu"],
    ["Edamame", "legumes"],
    ["Kichererbsen mit Spinat", "legumes"],
    ["Hummus mit Gemuese", "legumes"],
    ["Skyr mit Beeren", "skyr"],
    ["Magerquark mit Honig", "skyr"],
    ["Huettenkaese mit Tomate", "skyr"],
    ["Protein-Bowl mit Huhn", "bowl"],
    ["Quinoa-Bowl", "bowl"],
    ["Ofengemuese vom Blech", "veggiepan"],
    ["Gemuesepfanne", "veggiepan"],
    ["Zoodles mit Pesto", "pasta"],
    ["Pilzpfanne", "veggiepan"],
    ["Proteinriegel", "nuts"],
    ["Energy Balls mit Datteln", "nuts"],
    ["Mandeln", "nuts"],
    ["Proteinshake mit Whey", "shake"],
    ["Eiweissshake", "shake"],
    ["Couscous mit Kraeutern", "grain"],
    ["Bulgur mit Tomaten", "grain"],
    ["Schweinebraten mit Knoedeln", "braten"],
    ["Pulled Pork", "braten"],
    ["Griessbrei", "porridge"],
    ["Milchreis", "porridge"],
    // Faelle, in denen die REIHENFOLGE die Aussage traegt
    ["Nudeln mit Hackfleisch", "pasta"],
    ["Gebratener Reis mit Ei", "rice"],
    ["Gemuesesalat", "salad"],
    ["Erdnussbutter-Brot", "sandwich"],
    ["Protein-Pancakes mit Skyr", "pancake"],
    ["Bohnen-Chili", "stew"],
    ["Linsen-Bolognese", "pasta"],
    ["Rote-Linsen-Dal", "curry"],
    ["Linsensuppe", "soup"],
    ["Linsensalat", "salad"],
    ["Thunfischsalat", "salad"],
    ["Spargel-Risotto", "rice"],
    ["Brokkoli-Auflauf", "casserole"],
    ["Kakao-Kuchen", "cake"],
    ["Quark mit Haferflocken", "porridge"],
    ["Kaesespaetzle", "pasta"],
    // Ein bewusst festgehaltener Grenzfall, kein Versehen: "schwein" steht in der
    // braten-Regel (Pos. 26) und damit VOR rice (Pos. 28). Ein Gericht, das beides
    // nennt, bekommt deshalb das Bratenbild. Umdrehen loest es nicht, es verschiebt
    // es nur - dann verloere "Schweinebraten mit Reis" sein richtiges Bild. Die Zeile
    // steht hier, damit die Entscheidung sichtbar bleibt und eine kuenftige
    // Umsortierung auffaellt, statt still das Verhalten zu drehen.
    ["Schweinegeschnetzeltes mit Reis", "braten"],
    ["Schweinebraten mit Reis", "braten"],
    ["Schweinefilet mit Reis", "steak"],
    // und die Faelle, die schon immer stimmten - sie duerfen nicht kippen
    ["Spaghetti Bolognese", "pasta"],
    ["Pizza Margherita", "pizza"],
    ["Haehnchenbrust mit Reis", "chicken"],
    ["Rinderfilet", "steak"],
    ["Lachsfilet mit Zitrone", "fish"],
    ["Kuerbissuppe", "soup"],
    ["Doener", "wrap"],
    ["Ofenkartoffeln", "potato"],
    ["Cappuccino", "coffee"],
    ["Erdbeer-Smoothie", "drink"],
    ["Ramen", "noodle"],
    ["Sushi-Platte", "sushi"],
    ["Garnelen in Knoblauch", "seafood"],
    ["Ruehrei", "egg"],
    ["Gulasch", "stew"],
    ["Nudelauflauf", "casserole"]
  ];
  var falsch = [];
  FAELLE.forEach(function (f) {
    var ist = fuer(f[0]);
    if (ist !== f[1]) falsch.push(f[0] + ": " + ist + " statt " + f[1]);
  });
  pruef("alle " + FAELLE.length + " Gerichtnamen treffen ihr Bild", falsch, []);

  // ---- 5. Die Rangfolge von photoFor ----
  pruef("ohne jeden Treffer greift die Kategorie",
    schluesselVon(photoFor({ name: "Irgendwas Unbekanntes", category: "Snack" })), "fruit");
  pruef("Hauptgericht ohne Treffer bleibt neutral",
    schluesselVon(photoFor({ name: "Irgendwas Unbekanntes", category: "Hauptgericht" })), "neutral");
  pruef("ein kuratierter Schluessel schlaegt das Stichwort",
    schluesselVon(photoFor({ name: "Schnitzel mit Pommes", category: "Hauptgericht", photo: "salad" })), "salad");
  pruef("ein unbekannter Schluessel faellt still auf das Stichwort zurueck",
    schluesselVon(photoFor({ name: "Schnitzel mit Pommes", category: "Hauptgericht", photo: "gibtsnicht" })), "schnitzel");
  pruef("ein Bibliotheksbild schlaegt den kuratierten Schluessel",
    photoFor({ name: "Schnitzel", category: "Hauptgericht", photo: "salad", lib: COOKBOOK[0].id }),
    "img/library/" + COOKBOOK[0].img);
  pruef("das eigene Bild des Nutzers schlaegt alles",
    photoFor({ name: "Schnitzel", photo: "salad", lib: COOKBOOK[0].id,
               image: "data:image/webp;base64,AAAA" }), "data:image/webp;base64,AAAA");
  // Der Schutz davor, dass ein Pfad aus fremden Daten ungeprueft in ein src="" wandert.
  pruef("ein manipuliertes eigenes Bild wird verworfen",
    schluesselVon(photoFor({ name: "Schnitzel", image: "javascript:alert(1)" })), "schnitzel");

  // ---- 6. Jedes Katalogrezept hat weiterhin ein Bild ----
  var ohneBild = COOKBOOK.filter(function (r) { return !photoFor(r); }).map(function (r) { return r.id; });
  pruef("jedes Katalogrezept bekommt ein Bild", ohneBild, []);
  var kuratiert = COOKBOOK.filter(function (r) { return r.photo && !PHOTOS[r.photo]; }).map(function (r) { return r.photo; });
  pruef("jeder kuratierte photo-Schluessel im Katalog existiert noch", kuratiert, []);

  // ---- 7. Der KI-Hinweis unter dem grossen Foto ----
  // Warum das unter Zusage steht: Der Hinweis ist die Offenlegung, dass ein Bild
  // KI-generiert und ein Symbolbild ist. Faellt er still weg - etwa weil jemand die
  // Bedingung umdreht - merkt das niemand beim Draufsehen, denn das Bild bleibt ja da.
  var EIGENES = "data:image/webp;base64,AAAA";
  pruef("mitgeliefertes Bild traegt den Hinweis",
    bildHinweisHtml({ name: "Schnitzel mit Pommes", category: "Hauptgericht" }).indexOf("KI-generiert") >= 0, true);
  pruef("und nennt es ein Symbolbild",
    bildHinweisHtml({ name: "Schnitzel mit Pommes", category: "Hauptgericht" }).indexOf("Symbolbild") >= 0, true);
  pruef("ein Bibliotheksbild traegt ihn ebenfalls",
    bildHinweisHtml({ name: "X", lib: COOKBOOK[0].id }).indexOf("KI-generiert") >= 0, true);
  // Der Absatz steht jetzt IMMER im Markup und wird nur versteckt - sonst muesste ihn der
  // Fotowechsel im Bearbeiten-Zweig nachtraeglich erzeugen und wieder entfernen.
  pruef("beim EIGENEN Foto des Nutzers ist er versteckt",
    bildHinweisHtml({ name: "Mein Abendessen", image: EIGENES }).indexOf("hidden") >= 0, true);
  pruef("beim mitgelieferten Bild ist er sichtbar",
    bildHinweisHtml({ name: "Schnitzel" }).indexOf("hidden") >= 0, false);
  // Und der Fotowechsel im Bearbeiten-Zweig schaltet ihn mit. Ohne das stuende
  // "KI-generiert" unter dem gerade hochgeladenen Foto des Nutzers.
  var attrappe = document.createElement("div");
  attrappe.innerHTML = bildHinweisHtml({ name: "Schnitzel" });
  syncBildHinweis(attrappe, { name: "Schnitzel", image: EIGENES });
  pruef("Fotowechsel zu eigenem Bild versteckt den Hinweis",
    attrappe.querySelector(".ms-bildhinweis").hidden, true);
  syncBildHinweis(attrappe, { name: "Schnitzel" });
  pruef("Foto entfernen holt ihn zurueck",
    attrappe.querySelector(".ms-bildhinweis").hidden, false);

  // Der Alt-Text traegt dieselbe Auskunft - sonst erfaehrt sie nur, wer sehen kann.
  pruef("Alt-Text eines mitgelieferten Bildes nennt Symbolbild und KI",
    bildAlt({ name: "Schnitzel mit Pommes" }), "Schnitzel mit Pommes (Symbolbild, KI-generiert)");
  pruef("Alt-Text beim eigenen Foto bleibt der blosse Name",
    bildAlt({ name: "Mein Abendessen", image: EIGENES }), "Mein Abendessen");
  pruef("ohne Namen bleibt der Alt-Text trotzdem aussagekraeftig",
    bildAlt({}), "Symbolbild, KI-generiert");
  // Ein Bild, das safeImage verwirft, ist kein gueltiges eigenes Foto - dann zeigt die
  // Ansicht wieder eines von uns, und der Hinweis muss zurueckkommen.
  pruef("ein verworfenes eigenes Bild bekommt den Hinweis zurueck",
    bildHinweisHtml({ name: "X", image: "javascript:alert(1)" }).indexOf("KI-generiert") >= 0, true);
  // Und die Bedingung muss dieselbe sein, die photoFor benutzt - sonst laufen sie
  // auseinander und der Hinweis steht unter einem fremden Foto.
  pruef("Hinweis und Bildwahl folgen derselben Bedingung",
    [istEigenesFoto({ image: EIGENES }), photoFor({ name: "X", image: EIGENES }) === EIGENES], [true, true]);

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""

io.open(OUT, "w", encoding="utf-8").write(HTML.replace("__CODE__", code))
print("geschrieben")

if __name__ == "__main__":
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pruefstand_lauf import fahren
    _sys.exit(fahren(OUT))
