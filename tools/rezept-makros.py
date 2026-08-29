#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Naehrwerte je Zutat aus der FOODS-Tabelle nachschlagen und die Rezept-Summe gegenrechnen.

WARUM DAS NOETIG IST: Ein Rezept, dessen Zutaten keine eigenen Naehrwerte tragen, laesst sich
in der App nicht nachrechnen. Wer beim Bearbeiten 200 g Reis auf 150 g aendert, bekommt
weiterhin die alten Gesamtwerte angezeigt - sie stimmen dann nicht mehr. Bei 30 kuratierten
Rezepten faellt das niemandem auf, bis es jemandem auffaellt.

DIE RECHENREGEL DER APP (ingContrib in index.html):
  * Einheit g/ml   -> Naehrwert gilt je 100, Faktor = menge / 100
  * Einheit st/el/tl -> Naehrwert gilt je EINHEIT, Faktor = menge
FOODS speichert je 100 g. Fuer Stueck-Zutaten muss also auf ein Stueck umgerechnet werden -
dafuer traegt der FOODS-Eintrag als letztes Feld optional das Gewicht eines Stuecks.

Das Skript AENDERT NICHTS an index.html. Es liest, rechnet und meldet - eintragen bleibt eine
bewusste Entscheidung. Aufruf:

    python tools/rezept-makros.py            # alle COOKBOOK-Rezepte pruefen
    python tools/rezept-makros.py --json     # Zutaten mit Naehrwerten als JSON ausgeben
"""

import argparse
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

import os
# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "index.html"

# Wie weit darf die Summe der Zutaten vom angegebenen Rezeptwert abweichen, bevor es gemeldet
# wird? 12 % ist bewusst grosszuegig: Garverluste, Oel in der Pfanne und Rundungen bewegen
# sich in dieser Groessenordnung. Wer enger prueft, meldet vor allem Rauschen.
TOLERANZ = 0.12


def js_array_lesen(text, marker):
    """Den Inhalt eines JS-Arrays ab einem Marker holen - ohne die Datei zu interpretieren."""
    i = text.index(marker)
    start = text.index("[", i)
    tiefe, j, in_str, esc, quote = 0, start, False, False, ""
    while j < len(text):
        c = text[j]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == quote: in_str = False
        elif c in "\"'":
            in_str, quote = True, c
        elif c == "[": tiefe += 1
        elif c == "]":
            tiefe -= 1
            if tiefe == 0: return text[start:j + 1]
        j += 1
    raise SystemExit("Array nicht geschlossen: " + marker)


def norm(s):
    """Vergleichsform: klein, ohne Akzente, ohne Klammerzusaetze und Mengenangaben.

    Vertraegt null: In FOODS steht an der Synonym-Stelle teilweise ein Platzhalter, wenn nur
    das Stueckgewicht dahinter gesetzt werden sollte.
    """
    if not s:
        return ""
    s = s.lower().split("(")[0]
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = s.replace("ß", "ss")
    return re.sub(r"[^a-z ]", " ", s).strip()


def foods_laden():
    text = pm_quelle.lade_seite(QUELLE)
    roh = js_array_lesen(text, "/*FOODS_START*/")
    # Die Tabelle ist reines JSON, sobald die Kommentarzeilen weg sind.
    ohne_kommentar = re.sub(r"//[^\n]*", "", roh)
    ohne_kommentar = re.sub(r",(\s*[\]}])", r"\1", ohne_kommentar)
    eintraege = json.loads(ohne_kommentar)
    tabelle = []
    for e in eintraege:
        name = e[0]
        tabelle.append({
            "name": name, "norm": norm(name),
            "kcal": e[1], "carbs": e[2], "protein": e[3], "fat": e[4],
            "unit": e[5] if len(e) > 5 else "g",
            "syn": norm(e[6]) if len(e) > 6 else "",
            "je_stueck": e[7] if len(e) > 7 else None
        })
    return tabelle


def cookbook_laden():
    text = pm_quelle.lade_seite(QUELLE)
    roh = js_array_lesen(text, "const COOKBOOK = ")
    ohne_kommentar = re.sub(r"^\s*//[^\n]*$", "", roh, flags=re.M)
    ohne_kommentar = re.sub(r",(\s*[\]}])", r"\1", ohne_kommentar)
    # JS erlaubt unquotierte Schluessel, JSON nicht.
    ohne_kommentar = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', ohne_kommentar)
    return json.loads(ohne_kommentar)


def treffer(zutat_name, tabelle):
    """Passenden FOODS-Eintrag finden. Zuerst exakt, dann als Wortanfang, dann ueber Synonyme.

    Bewusst KEIN unscharfes Raten: Ein falsch zugeordnetes Lebensmittel erzeugt Naehrwerte,
    die plausibel aussehen und falsch sind - schlimmer als gar keine.
    """
    z = norm(zutat_name)
    if not z:
        return None
    for e in tabelle:
        if e["norm"] == z:
            return e

    # Praefix NUR an der Wortgrenze. Ohne diese Bedingung matchte "Zuckerschoten" auf
    # "Zucker" - 400 kcal statt 42, und das Rezept kam auf 168 g Kohlenhydrate. Der Wert
    # sah plausibel aus und war grob falsch; aufgefallen ist es nur, weil die Summe nicht
    # zum Rezept passte. Genau dagegen ist dieses Skript da.
    def wortgrenze(kurz, lang):
        return lang.startswith(kurz + " ")
    kandidaten = [e for e in tabelle
                  if wortgrenze(z, e["norm"]) or wortgrenze(e["norm"], z)]
    if len(kandidaten) == 1:
        return kandidaten[0]
    if kandidaten:
        return sorted(kandidaten, key=lambda e: len(e["norm"]))[0]
    wort = z.split()[0]
    for e in tabelle:
        if wort and (wort in e["syn"].split() or e["norm"].split()[0] == wort):
            return e
    return None


def werte_fuer(zutat, eintrag):
    """Die Werte, die AN DIE ZUTAT geschrieben werden - in der Bezugsgroesse der App."""
    einheit = zutat.get("unit", "g")
    if einheit in ("st", "el", "tl"):
        # Naehrwert je Einheit. FOODS rechnet je 100 g, also ueber das Stueckgewicht.
        g = eintrag.get("je_stueck")
        if einheit == "st" and eintrag["unit"] == "st":
            f = 1.0                     # Eintrag ist bereits je Stueck (z. B. "Ei, Größe M")
        elif g:
            f = g / 100.0
        else:
            return None                 # Stueckgewicht unbekannt - lieber nichts als geraten
        return {k: round(eintrag[k] * f, 1) for k in ("kcal", "carbs", "protein", "fat")}
    # g/ml: die Werte gelten je 100 und werden unveraendert uebernommen
    return {k: eintrag[k] for k in ("kcal", "carbs", "protein", "fat")}


def zahl(n):
    """Wie JS es schreiben wuerde: 70 statt 70.0, aber 0.5 bleibt 0.5."""
    if n is None:
        return "0"
    return str(int(n)) if float(n) == int(n) else str(round(float(n), 1))


def beitrag(zutat, werte):
    """Was diese Zutat zum Rezept beitraegt - dieselbe Rechnung wie ingContrib in der App."""
    menge = zutat.get("grams") or 0
    einheit = zutat.get("unit", "g")
    f = menge if einheit in ("st", "el", "tl") else menge / 100.0
    return {k: werte[k] * f for k in ("kcal", "carbs", "protein", "fat")}


def main():
    p = argparse.ArgumentParser(description="Zutaten-Naehrwerte nachschlagen und Rezepte gegenrechnen")
    p.add_argument("--json", action="store_true", help="Zutaten mit Naehrwerten als JSON ausgeben")
    p.add_argument("--anwenden", action="store_true",
                   help="Die Naehrwerte in die COOKBOOK-Zutaten in index.html SCHREIBEN. "
                        "Nur ausfuehren, wenn der Bericht vorher sauber war.")
    args = p.parse_args()

    tabelle = foods_laden()
    rezepte = cookbook_laden()
    print("FOODS: %d Lebensmittel | COOKBOOK: %d Rezepte\n" % (len(tabelle), len(rezepte)))

    offen, schief = 0, 0
    ausgabe = {}
    for r in rezepte:
        zeilen, summe = [], {"kcal": 0, "carbs": 0, "protein": 0, "fat": 0}
        fehlend = []
        for z in r.get("ingredients", []):
            if not isinstance(z, dict):
                continue                      # Freitext ("Salz, Pfeffer") traegt nichts bei
            e = treffer(z["name"], tabelle)
            w = werte_fuer(z, e) if e else None
            if not w:
                fehlend.append(z["name"])
                zeilen.append((z["name"], None, e["name"] if e else None))
                continue
            b = beitrag(z, w)
            for k in summe: summe[k] += b[k]
            zeilen.append((z["name"], w, e["name"]))
        soll = r.get("nutrition") or {}
        abw = {}
        for k in ("kcal", "carbs", "protein", "fat"):
            s = soll.get(k)
            if not s:
                continue
            # Unter 5 g ist die PROZENTUALE Abweichung Rauschen: 1,5 g gerechnetes Fett
            # gegen 2 g angegebenes sind -20 %, obwohl beide Werte dasselbe aussagen und
            # die Rundung auf ganze Gramm richtig ist. Ein Werkzeug, das dauerhaft einen
            # unbehebbaren Treffer meldet, wird ueberlesen - und mit ihm der echte.
            if k != "kcal" and s < 5:
                continue
            abw[k] = (summe[k] - s) / s
        schlimmste = max((abs(v) for v in abw.values()), default=0)
        marke = "OK  " if schlimmste <= TOLERANZ and not fehlend else ("LUECKE" if fehlend else "PRUEFEN")
        if fehlend: offen += 1
        elif schlimmste > TOLERANZ: schief += 1
        print("%s  %s" % (marke, r["name"]))
        print("     angegeben: %4d kcal | %3d KH | %3d P | %3d F"
              % (soll.get("kcal", 0), soll.get("carbs", 0), soll.get("protein", 0), soll.get("fat", 0)))
        print("     gerechnet: %4d kcal | %3d KH | %3d P | %3d F  (%s)"
              % (summe["kcal"], summe["carbs"], summe["protein"], summe["fat"],
                 ", ".join("%s %+.0f%%" % (k, v * 100) for k, v in abw.items())))
        if fehlend:
            print("     ohne Naehrwert: " + ", ".join(fehlend))
        ausgabe[r["id"]] = [{"name": n, "werte": w, "quelle": q} for n, w, q in zeilen]
        print()

    print("%d Rezepte mit Luecken, %d ausserhalb der %d-%%-Toleranz."
          % (offen, schief, int(TOLERANZ * 100)))

    if args.anwenden:
        if offen:
            print("\nABBRUCH: Es gibt noch Zutaten ohne Naehrwert. Erst die Luecken schliessen -")
            print("halbe Daten sind schlimmer als keine, weil die Summe dann still falsch ist.")
            return 1
        text = pm_quelle.lade_seite(QUELLE)
        block = js_array_lesen(text, "const COOKBOOK = ")
        neu, ersetzt = block, 0
        # Nur im COOKBOOK-Block ersetzen - SEED und die Zutatenliste des Nutzers bleiben
        # unberuehrt. Die Werte kommen ans ENDE des Zutaten-Objekts, damit die Reihenfolge
        # name/grams/unit erhalten bleibt (sie ist beim Lesen der Datei die verstaendlichere).
        for r in rezepte:
            for z in r.get("ingredients", []):
                if not isinstance(z, dict) or "kcal" in z:
                    continue
                e = treffer(z["name"], tabelle)
                w = werte_fuer(z, e) if e else None
                if not w:
                    continue
                alt = '{ name: "%s", grams: %s%s }' % (
                    z["name"], zahl(z.get("grams")),
                    ', unit: "%s"' % z["unit"] if z.get("unit") else "")
                if alt not in neu:
                    print("  uebersprungen (nicht wortgleich gefunden): " + alt)
                    continue
                werte = ", ".join("%s: %s" % (k, zahl(w[k])) for k in ("kcal", "carbs", "protein", "fat"))
                neu = neu.replace(alt, alt[:-2] + ", " + werte + " }", 1)
                ersetzt += 1
        io.open(QUELLE, "w", encoding="utf-8").write(text.replace(block, neu, 1))
        print("\n%d Zutaten mit Naehrwerten versehen." % ersetzt)
        print("Danach zwingend: python syntax-check.py")

    if args.json:
        io.open(WURZEL / "tools" / "zutaten-makros.json", "w", encoding="utf-8").write(
            json.dumps(ausgabe, ensure_ascii=False, indent=2))
        print("Geschrieben: tools/zutaten-makros.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
