# -*- coding: utf-8 -*-
u"""Die Foto-Tokens muessen exakt das tragen, was vorher hartkodiert dastand.

Etappe 2 der UI-Grundlagen (22.09.2026). Die Farbsichtung ergab nicht "208 Werte
gehoeren in Tokens", sondern etwas Genaueres: 17 Zeilen beschrieben Farben, die auf
einem **Foto** liegen - Meal-Bild, Kamerabild, Favoritenstern. Dort ist Weiss in
Light wie in Dark richtig, weil darunter kein `--surface` liegt, sondern ein Bild.
Es fehlten also keine Theme-Tokens, sondern Tokens fuer "liegt auf einem Bild":
`--on-photo`, `--on-photo-dim`, `--photo-scrim`, `--shadow-float`.

WARUM NICHT EINFACH SCREENSHOTS VERGLEICHEN
-------------------------------------------
Ein Pixelvergleich der vier Reiter lief nach dem Umbau gruen - und belegte nichts.
Die geaenderten Regeln liegen auf Overlays, die auf keinem dieser Reiter zu sehen
sind. Gruen hiess dort nur: Unveraendertes ist unveraendert. Dieselbe Falle wie im
Fallarchiv ("Pruefer und Prueflich, gleiche Quelle").

Deshalb wird hier der **berechnete Wert** gemessen, und zwar in beiden Themes: Die
vier Tokens duerfen sich nicht unterscheiden, denn ein Foto ist in beiden Themes
dasselbe Foto. Faende sich `--on-photo` eines Tages im Dark-Block wieder, faellt
dieser Lauf um.

    python tools/pruefstand-foto-tokens.py

Braucht Chrome und den lokalen Server (beides besorgt sich die Sitzung selbst).
"""
import importlib.util, os, sys, time
sys.stdout.reconfigure(encoding="utf-8")
W = r"C:\Users\Paddy\Documents\Paddys Mealplan"
spec = importlib.util.spec_from_file_location("am", os.path.join(W, "tools", "abnahme-mobil.py"))
AM = importlib.util.module_from_spec(spec); spec.loader.exec_module(AM)

# Erwartet wird der Wert, der VOR dem Umbau hartkodiert dastand.
ERWARTET = {
    "--on-photo":     "#fff",
    "--on-photo-dim": "rgba(255,255,255,.85)",
    "--photo-scrim":  "#0a0c07",
    "--shadow-float": "0 2px 8px rgba(0,0,0,.35)",
}
JS = """(function(){
  var cs = getComputedStyle(document.documentElement);
  var out = {};
  ["--on-photo","--on-photo-dim","--photo-scrim","--shadow-float"].forEach(function(k){
    out[k] = cs.getPropertyValue(k).trim();
  });
  // Und eine echte Fundstelle: der Scrim-Knopf auf dem Foto
  var d = document.createElement('button');
  d.className = 'fav-ic on-photo'; d.style.position='fixed'; d.style.left='-999px';
  document.body.appendChild(d);
  var f = getComputedStyle(d);
  out["_fav-ic.on-photo color"] = f.color;
  out["_fav-ic.on-photo background"] = f.backgroundColor;
  d.remove();
  return JSON.stringify(out);
})()"""

def norm(s):
    return s.replace(" ", "").lower()

s = AM.Sitzung(); s.start()
fehler = 0
gruen = 0
try:
    for theme in ["dark", "light"]:
        s.geraet(393, 852, theme); s.laden(); time.sleep(0.6)
        import json
        werte = json.loads(s.js(JS))
        print("--- %s ---" % theme)
        for k, soll in ERWARTET.items():
            ist = werte.get(k, "")
            ok = norm(ist) == norm(soll)
            print("  %s %-16s %s" % ("OK  " if ok else "FAIL", k, ist))
            if ok:
                gruen += 1
            else:
                fehler += 1
                print("       erwartet: %s" % soll)
        for k in werte:
            if k.startswith("_"):
                print("  ..   %-26s %s" % (k, werte[k]))
finally:
    s.stoppen()
# Schlusszeile im Format, das tools/alle-pruefstaende.py erwartet - sonst gilt dieser
# Lauf dort als "prueft der ueberhaupt etwas?" (docs/TROUBLESHOOTING.md 131).
print("\nERGEBNIS %d gruen, %d rot" % (gruen, fehler))
print("%s" % ("GRUEN - die Tokens tragen exakt die alten Werte, in beiden Themes."
              if not fehler else "ROT - %d Abweichung(en)" % fehler))
sys.exit(1 if fehler else 0)
