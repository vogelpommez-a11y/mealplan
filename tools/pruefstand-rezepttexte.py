#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pruefstand Rezepttexte: Deckt die Zubereitung die Zutatenliste ab?

ANLASS (29.08.2026): Beim Kochen von "Protein-Pancakes mit Skyr und Beeren" fiel auf, dass
die Zutatenliste "Backpulver, Vanille, Prise Salz" fuehrt, die Zubereitung aber nur das
Backpulver erwaehnt. Wer nach der Anleitung kocht, laesst Vanille und Salz weg - und merkt
es nicht. Eine Sondierung ueber den Katalog zeigte: kein Einzelfall.

Das ist ein DATEN-Pruefstand, kein Ausschneide-Pruefstand: Er liest data/cookbook.js und
rechnet, er faehrt keinen Browser. Der "pruefstand-"-Praefix ist trotzdem richtig -
tools/alle-pruefstaende.py sammelt per glob("tools/pruefstand-*.py") ein und bewertet den
Rueckgabewert. Die Registrierung in der Suite passiert dadurch von selbst.

WAS ER PRUEFT
  * Jede Zutat traegt eine Menge (`grams`), kein Freitext       -> REGRESSION, ohne Grundlinie
  * Zutaten in TL/EL nennen ihre Menge auch in `steps`          -> REGRESSION, ohne Grundlinie
  * Jede Zutat aus `ingredients` kommt in `steps` vor           -> REGRESSION
  * `steps` ist nummeriert ("1. ", "2. " ...)                   -> REGRESSION, ohne Grundlinie
  * `steps` ist nicht leer                                      -> REGRESSION
  * `img` verweist auf eine Datei in img/library/               -> REGRESSION
  * zu jedem Bild steht ein Herkunftsnachweis im Protokoll      -> REGRESSION
  * `id` ist eindeutig                                          -> REGRESSION
  * Ernaehrungsform-Tags passen zu den Zutaten                  -> REGRESSION, ohne Grundlinie

DIE MENGENPRUEFUNG - was sie deckt und was nicht
Am 29.08.2026 fiel an der "Protein-Pizza mit Schinken" auf, dass Backpulver, Salz und
Oregano als Freitext-String ohne jede Menge in der Zutatenliste standen. Wer danach kocht,
raet. Der Katalog trug diese Form 32-mal. Seitdem gilt: keine Zutat ohne `grams`.

GEMESSEN wird davon zweierlei: dass ueberhaupt eine Menge dasteht, und dass Zutaten in
TL/EL ihre Menge auch im Schritt nennen ("1 TL Backpulver unterruehren"). Der Schreibstandard
verlangt darueber hinaus die Menge bei allem, was man nicht sehen kann - Oel, Suesse, Kakao.
Das steht hier bewusst NICHT drin: Bei einer Zutat in Gramm ist "10 g Backkakao" richtig und
"Kakao" je nach Rezept auch, und eine Pruefung, die beides nicht unterscheiden kann, meldet
Rauschen. TL und EL sind der harte Kern - dort ist die Menge nirgends sonst ablesbar.

NICHT GEPRUEFT WIRD DIE ZUTATENREIHENFOLGE, obwohl sie die eine unumstoessliche Regel des
professionellen Rezeptlektorats ist ("all ingredients must be listed, always, in the order
that they are used"). Der Versuch stand hier und wurde am 29.08.2026 wieder entfernt: Er
meldete 24 der 34 Rezepte. Der Grund liegt im Aufloeser - ein Sammelwort ("wuerzen" fuer
Salz, "Oel" fuer Rapsoel) trifft frueher, als die Zutat gebraucht wird, und verschiebt damit
jede Reihenfolge. Eine Pruefung, die bei 71 Prozent anschlaegt, wird ueberlesen, und eine
ueberlesene Pruefung ist schlechter als keine. Die Regel steht deshalb im Schreibstandard
(data/CLAUDE.md) und wird beim Schreiben durchgesetzt, nicht hier.

DIE GRUNDLINIE - warum sie leer ist
Ein Pruefstand, der ab Tag eins rot ist, blockiert die Suite und wird abgeschaltet. Deshalb
stand der Altbestand vom 29.08.2026 zunaechst als GRUNDLINIE unten und meldete sich als
OFFEN. Am selben Tag wurde er vollstaendig nachgezogen, die Liste ist seitdem LEER und
bleibt es: Jeder Treffer ist ein Befund. Die Mechanik dahinter bleibt erhalten (BEHOBEN
erinnert daran, eine erledigte Zeile zu streichen), damit eine kuenftige, bewusst
befristete Grundlinie nicht still verrottet.

Aufrufe:
    python tools/pruefstand-rezepttexte.py
    python tools/pruefstand-rezepttexte.py alt.js      # Gegenprobe gegen einen alten Stand
    python tools/pruefstand-rezepttexte.py --grundlinie  # Grundlinie neu ausgeben
"""

import json
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------------------------------
# GRUNDLINIE - leer, und das ist Absicht.
#
# Bis zum 29.08.2026 standen hier 18 Rezepte mit Zutaten, die in ihrer Anleitung nicht
# vorkamen - der Bestand, BEVOR der Zubereitungs-Standard galt. Am selben Tag wurde der
# ganze Katalog nachgezogen: jede Zutat als Objekt mit Menge, jede Anleitung nummeriert,
# jede Zutat in den Schritten. Seitdem ist jeder Treffer ein Befund.
#
# LEER LASSEN. Wer hier eine Zeile eintraegt, schaltet die Pruefung fuer dieses Rezept
# dauerhaft ab, und niemand sieht es je wieder (CLAUDE.md 18b: "Falsch ist, eine Kennung
# einzutragen, damit Ruhe ist"). Ein Rezept, das die Pruefung nicht besteht, wird
# korrigiert - nicht eingetragen.
# ------------------------------------------------------------------------------------------
GRUNDLINIE = {}

# Rezepte, deren Anleitung noch Fliesstext war. Ebenfalls leer seit dem 29.08.2026 - alle
# 35 Anleitungen sind nummeriert. Auch diese Liste bleibt leer, aus demselben Grund.
UNNUMMERIERT_ALT = set()

# ------------------------------------------------------------------------------------------
# Aufloeser: Wann gilt eine Zutat als erwaehnt?
#
# Ohne Nachsicht meldet der Pruefstand 31 von 34 Rezepten und ist damit wertlos - "Olivenoel"
# gegen "mit Oel und Kraeutern mischen" ist kein Befund, sondern normales Deutsch. Drei
# Nachsichten reichen aus; jede weitere waere schon Auslegung und gehoert zum Urteil, nicht
# zur Vorauswahl.
# ------------------------------------------------------------------------------------------

# Qualifizierer nach dem Komma - sie beschreiben den Zustand, nicht die Zutat.
QUALIFIZIERER = re.compile(
    r',\s*(roh|natur|Dose|mager|ungesüßt|ungesuesst|mittelalt|gemahlen\w*|'
    r'frisch\w*|tiefgekühlt|Größe \w+|\d+[,.]?\d*\s*%).*$', re.I)

# Die Mehltype haengt OHNE Komma am Namen ("Weizenmehl Type 405"), der Qualifizierer oben
# greift also nicht - und die Kompositum-Suche von hinten findet dann "405" statt "mehl".
# Aufgefallen am 29.08.2026 am ersten Rezept, das nach dem neuen Standard entstand: Die
# Anleitung sagte "Mehl", der Pruefstand meldete die Zutat trotzdem als fehlend. Betrifft
# alle drei Mehl-Eintraege in FOODS (Type 405, 630, 1150).
TYPENZAHL = re.compile(r'\s+Type\s+\d+\s*$', re.I)

# Fuellwoerter, die vor der Zutat stehen koennen.
#
# AUSGESCHRIEBENE FORMEN, KEIN \w*: "frisch\w*" fraß das Grundwort von "Frischkaese, light"
# mit. Uebrig blieb ", light", nach dem Komma-Schnitt der leere String - und eine Zutat mit
# leerem Kopf galt in position() als IMMER erwaehnt. Der Pruefstand haette dieses Rezept
# stillschweigend nicht mehr geprueft (Review 29.08.2026).
FUELLWORT = re.compile(
    r'\b(Prise|Etwas|nach Geschmack|frische[rns]?|frisch|gemahlene[rns]?|gemahlen)\b', re.I)

# Sammelwoerter: Ein Oberbegriff in der Anleitung deckt die konkrete Zutat ab.
#   Muster fuer die ZUTAT -> Muster, das in den SCHRITTEN stehen muss.
#
# Hier stehen ausdruecklich auch die Faelle, die der Kompositum-Rueckfall unten NICHT
# abdecken darf, weil ihr Grundwort zu kurz ist: "Oel" hat zwei Zeichen. Explizit
# aufgeschrieben ist das lesbar und pruefbar - eine allgemeine Regel, die bis auf zwei
# Zeichen heruntergeht, faengt dagegen "er" in "Haferflocken" (siehe unten).
SAMMEL = [
    (re.compile(r'(heidel|him|brom|erd|johannis)?beeren?$', re.I),
     re.compile(r'beeren?', re.I)),
    (re.compile(r'(rosmarin|thymian|oregano|petersilie|basilikum|dill|schnittlauch|koriander)$', re.I),
     re.compile(r'kräuter|kraeuter', re.I)),
    (re.compile(r'(oliven|raps|sesam|kokos|lein|sonnenblumen|erdnuss)?öl$', re.I),
     re.compile(r'öl\b', re.I)),
    # "Ei" ist zu kurz fuer die allgemeine Suche: Eine Wortgrenze vorn genuegt bei zwei
    # Zeichen nicht, "\bei" trifft "eine". Deshalb ausgeschrieben, mit den Formen, die in
    # einer Anleitung wirklich stehen.
    # Die gebeugten Formen muessen mit: "mit den Eiern vermengen" ist normales Deutsch,
    # der erste Entwurf kannte aber nur Ei/Eier/Eiklar und meldete die Zutat als fehlend
    # (Testlauf 5 am 29.08.2026). Laengere Alternativen zuerst, sonst gewinnt "er" vor "ern".
    (re.compile(r'^ei$', re.I),
     re.compile(r'\bei(ern|ers|er|klar|gelb|weiß|weiss)?\b', re.I)),
    # Die Sorte steht in der Zutat ("Erbsenprotein-Pulver"), die Anleitung sagt
    # "Proteinpulver". Das Grundwort steckt hier MITTEN im Wort der Anleitung, wo keine
    # Wortgrenze hilft - also namentlich.
    (re.compile(r'(erbsen|whey|soja|reis|hanf)?protein[- ]?pulver$', re.I),
     re.compile(r'protein[- ]?pulver', re.I)),
]

# Gewuerze gelten als abgedeckt, wenn die Anleitung ueberhaupt wuerzt. "Mit Salz und Pfeffer
# abschmecken" steht in echten Rezepten oft als "abschmecken" - das ist keine Luecke.
GEWUERZE = {
    "salz", "pfeffer", "muskat", "kurkuma", "kreuzkümmel", "kreuzkuemmel", "paprikapulver",
    "chili", "chiliflocken", "oregano", "rosmarin", "thymian", "zimt", "curry", "currypulver",
    "kräuter", "kraeuter", "vanille", "backkakao", "ingwer", "süße nach geschmack",
    "süßstoff", "kardamom", "koriander", "lorbeer", "senf",
}
WUERZT = re.compile(r'würz|wuerz|abschmeck|salz|pfeffer|gewürz|gewuerz', re.I)


def entpacke(js_string):
    """Aus dem Quelltext gelesene JS-Strings tragen \\n als zwei Zeichen. Fuer die
    Nummerierungspruefung muss daraus ein echter Umbruch werden."""
    return js_string.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")


def array_lesen(text, marker):
    """Inhalt eines JS-Arrays ab einem Marker holen - ohne die Datei zu interpretieren.
    Gleiche Bauart wie in tools/rezept-makros.py; bewusst nicht importiert, damit dieser
    Pruefstand allein von data/cookbook.js abhaengt."""
    i = text.index(marker)
    start = text.index("[", i)
    tiefe, j, in_str, esc, quote = 0, start, False, False, ""
    while j < len(text):
        c = text[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
        elif c in "\"'":
            in_str, quote = True, c
        elif c == "[":
            tiefe += 1
        elif c == "]":
            tiefe -= 1
            if tiefe == 0:
                return text[start:j + 1]
        j += 1
    raise SystemExit("Array nicht geschlossen: " + marker)


def rezepte_lesen(pfad):
    """Liefert je Rezept: id, Zutatennamen in Listenreihenfolge, steps, img."""
    with open(pfad, encoding="utf-8") as f:
        text = f.read()
    arr = array_lesen(text, "const COOKBOOK")

    grenzen = [(m.start(), m.group(1)) for m in
               re.finditer(r'\{\s*id:\s*"([^"]+)"\s*,\s*name:\s*"([^"]+)"', arr)]

    # DECKUNGSPROBE. Das Regex oben liest den Quelltext, nicht JavaScript - es haengt damit
    # an der Formatierung. Ein Rezept mit einem Umbruch an der falschen Stelle fiel im Test
    # heraus, ohne dass irgendwer etwas merkte: 33 statt 34 geprueft, Ergebnis weiter gruen
    # (Review 29.08.2026). Ein Pruefstand, der leise weniger prueft, ist schlimmer als einer,
    # der laut abbricht - deshalb hier der Abgleich gegen die Zahl der id-Vorkommen.
    erwartet = len(re.findall(r'\bid:\s*"', arr))
    if len(grenzen) != erwartet:
        gefunden = set(g[1] for g in grenzen)
        alle = set(re.findall(r'\bid:\s*"([^"]+)"', arr))
        raise SystemExit(
            "ABBRUCH: %d Rezepte erkannt, aber %d id-Felder im Katalog.\n"
            "Nicht erkannt: %s\n"
            "Vermutlich eine ungewohnte Formatierung in data/cookbook.js - erst das Regex "
            "in rezepte_lesen() anpassen, sonst prueft dieses Skript stillschweigend weniger."
            % (len(grenzen), erwartet, ", ".join(sorted(alle - gefunden)) or "(unbekannt)"))

    grenzen.append((len(arr), None))

    out = []
    for k in range(len(grenzen) - 1):
        rid = grenzen[k][1]
        block = arr[grenzen[k][0]:grenzen[k + 1][0]]

        # Zutaten als Saetze: name, menge, einheit. Freitext-Strings behalten ihre
        # aufgeteilten Namen - sie sind seit dem 29.08.2026 ein Befund, muessen aber
        # weiterhin gelesen werden koennen, um genau das melden zu koennen.
        zutaten = []
        ing = re.search(r'ingredients:\s*\[(.*?)\n\s*\],', block, re.S)
        if ing:
            body = ing.group(1)
            for m in re.finditer(r'\{([^{}]*)\}|^\s*"([^"]+)"\s*,?\s*$', body, re.M):
                if m.group(1) is not None:
                    feld = m.group(1)
                    nm = re.search(r'name:\s*"([^"]+)"', feld)
                    gr = re.search(r'grams:\s*([\d.]+)', feld)
                    un = re.search(r'unit:\s*"([a-z]+)"', feld)
                    if nm:
                        zutaten.append({"name": nm.group(1),
                                        "menge": float(gr.group(1)) if gr else None,
                                        "einheit": un.group(1) if un else "g",
                                        "freitext": False})
                else:
                    for teil in m.group(2).split(","):
                        if teil.strip():
                            zutaten.append({"name": teil.strip(), "menge": None,
                                            "einheit": None, "freitext": True})
        namen = [z["name"] for z in zutaten]

        st = re.search(r'steps:\s*"((?:[^"\\]|\\.)*)"', block, re.S)
        steps = entpacke(st.group(1)) if st else ""
        im = re.search(r'img:\s*"([^"]+)"', block)
        tg = re.search(r'tags:\s*\[([^\]]*)\]', block)
        tags = re.findall(r'"([^"]+)"', tg.group(1)) if tg else []
        out.append({"id": rid, "zutaten": namen, "eintraege": zutaten, "steps": steps,
                    "tags": tags, "img": im.group(1) if im else None})
    return out


def nummer(n):
    """1.0 -> "1", 0.5 -> "0,5" - so, wie es in einer Meldung lesbar ist."""
    return (str(int(n)) if float(n) == int(n) else str(n).replace(".", ",")) if n else "?"


def kopf(zutat):
    """Der Teil der Zutat, der in der Anleitung stehen muesste.

    Gibt NIE einen leeren String zurueck: Bleibt nach dem Kuerzen nichts uebrig, gilt die
    Zutat unveraendert. Ein leerer Kopf hiesse in position() "immer erwaehnt" - eine Zutat
    waere damit stillschweigend von der Pruefung ausgenommen."""
    n = TYPENZAHL.sub("", QUALIFIZIERER.sub("", zutat)).strip()
    gekuerzt = FUELLWORT.sub("", n).strip().split(",")[0].strip()
    if gekuerzt:
        return gekuerzt
    ohne_fuellwort = n.split(",")[0].strip()
    return ohne_fuellwort or zutat.strip()


# ------------------------------------------------------------------------------------------
# ERNAEHRUNGSFORM-TAGS GEGEN DIE ZUTATEN
#
# `highprotein` und `lowcarb` sind gerechnet, die kann der Rezeptbuch-Pruefstand gegen
# macroBadges() halten. `vegan`, `vegetarisch`, `glutenfrei` und `laktosefrei` waren dagegen
# reine BEHAUPTUNGEN - niemand hat je nachgesehen, ob die Zutaten dazu passen.
#
# Aufgefallen am 29.08.2026 im zweiten Testlauf von /rezeptcharge: Ein frisch gebautes Rezept
# trug `laktosefrei` und enthielt Magerquark. Alle Pruefungen gruen. Ein falsches Tag ist
# hier kein Schoenheitsfehler - der Katalog wird nach state.goal.diet gefiltert, und wer
# laktosefrei waehlt, bekommt das Gericht ausdruecklich als geeignet vorgeschlagen.
#
# KEINE GRUNDLINIE: Der Bestand vom 29.08.2026 ist sauber. Jeder Treffer ist ein Befund.
#
# Die Wortlisten sind bewusst grob und die AUSNAHMEN namentlich - "Erdnussbutter" enthaelt
# "butter", ist aber kein Milchprodukt (Teilwort-Kollision wie in CLAUDE.md 15).
# ------------------------------------------------------------------------------------------
MILCH = r"quark|skyr|joghurt|milch|käse|kaese|feta|mozzarella|gouda|parmesan|butter|sahne|whey|molke|schmand"
FLEISCH = r"hähnchen|haehnchen|pute|rind|schwein|hack|salami|schinken|speck|bacon|wurst|lamm|steak"
FISCH = r"lachs|thunfisch|garnele|forelle|kabeljau|pangasius|hering|makrele|meeresfrüchte"
EI = r"\bei\b|\beier\b|eiklar|eigelb"
GLUTEN = r"weizen|dinkel|roggen|gerste|nudel|brot|mehl|couscous|bulgur|grieß|griess|hafer|seitan|panko"

# Was trotz Treffer KEIN Widerspruch ist. Wird im Umfeld des Treffers gesucht.
KEIN_MILCH = r"soja|hafermilch|mandelmilch|kokosmilch|reismilch|erdnuss|nussmus|kakaobutter|erbsenprotein"
KEIN_GLUTEN = r"reisnudel|glasnudel|reismehl|maismehl|buchweizen|kichererbsenmehl"

# Welches Tag vertraegt sich mit welchen Zutaten nicht?
TAG_REGELN = [
    ("laktosefrei",  [(MILCH, KEIN_MILCH, "Milchprodukt")]),
    ("vegetarisch",  [(FLEISCH, None, "Fleisch"), (FISCH, None, "Fisch")]),
    ("vegan",        [(MILCH, KEIN_MILCH, "Milchprodukt"), (FLEISCH, None, "Fleisch"),
                      (FISCH, None, "Fisch"), (EI, None, "Ei")]),
    ("glutenfrei",   [(GLUTEN, KEIN_GLUTEN, "Getreide mit Gluten")]),
]


def tag_widersprueche(tags, zutaten):
    u"""Meldet jedes Tag, dem eine Zutat widerspricht."""
    text = " | ".join(zutaten)
    raus = []
    for tag, pruefungen in TAG_REGELN:
        if tag not in tags:
            continue
        for muster, ausnahme, was in pruefungen:
            for m in re.finditer(muster, text, re.I):
                umfeld = text[max(0, m.start() - 25):m.end() + 25]
                if ausnahme and re.search(ausnahme, umfeld, re.I):
                    continue
                raus.append('Tag "%s", aber Zutat "%s" ist %s'
                            % (tag, m.group(0), was))
                break
    return raus


# Kuerzeste Zeichenkette, die als Beleg zaehlt.
#
# WARUM 4 UND NICHT WENIGER: Der erste Entwurf ging bis auf zwei Zeichen herunter, damit
# "Olivenoel" von "Oel" gedeckt ist. Damit galt "Erdnussbutter" als erwaehnt, weil "er" in
# "Haferflocken" steckt - ein FALSCHES NEGATIV, also genau der Fehler, den dieser Pruefstand
# finden soll. Dieselbe Teilwort-Kollision, vor der CLAUDE.md 15 warnt ("eis" in
# "Rindfleisch", "reis" in "Preiselbeere"). Kurze Grundwoerter stehen jetzt namentlich in
# SAMMEL statt in einer allgemeinen Regel.
MIN_BELEG = 4


def position(zutat, steps):
    """Zeichenposition der ersten Erwaehnung, oder None."""
    h = kopf(zutat).lower()
    s = steps.lower()
    if not h:
        return 0

    treffer = []
    # JEDER Textvergleich verlangt eine Wortgrenze VOR dem Treffer. Ohne sie fand
    # position("Reis", "Preiselbeeren untermischen") einen Beleg - genau die Kollision, die
    # CLAUDE.md 15 namentlich nennt - und position("Ei", "...in eine Schuessel...") ebenso.
    # Beides sind falsche Negative: Die Zutat gilt als erwaehnt, obwohl sie fehlt (Review
    # 29.08.2026). Hinten braucht es KEINE Grenze, sonst faende "Zucchini" nicht mehr die
    # "Zucchinischeiben" in den Schritten.
    def wortstart(stueck):
        m = re.search(r'\b' + re.escape(stueck), s)
        return m.start() if m else None

    # Koepfe unter MIN_BELEG werden NICHT allgemein gesucht - sie brauchen einen
    # namentlichen Eintrag in SAMMEL oder GEWUERZE (siehe "Öl" und "Ei"). Ohne diese Sperre
    # belegt jedes kurze Wort sich selbst irgendwo im Text. Fehlt der Eintrag, meldet der
    # Pruefstand die Zutat als fehlend - ein Fehlalarm, den man sieht, statt eines stillen
    # Durchwinkens.
    if len(h) >= MIN_BELEG:
        p = wortstart(h)
        if p is not None:
            treffer.append(p)
    # Kompositum von hinten: Basmatireis -> reis, Hafermilch -> milch.
    for laenge in range(len(h) - 1, MIN_BELEG - 1, -1):
        p = wortstart(h[-laenge:])
        if p is not None:
            treffer.append(p)
            break
    # Wortstamm von vorne: Zucchini -> zucch, Erdnussbutter -> erdnu (deckt "Erdnussmus")
    if len(h) >= 5:
        p = wortstart(h[:5])
        if p is not None:
            treffer.append(p)
    for muster, deckung in SAMMEL:
        if muster.search(h):
            d = deckung.search(s)
            if d:
                treffer.append(d.start())
    if h in GEWUERZE:
        w = WUERZT.search(s)
        if w:
            treffer.append(w.start())

    return min(treffer) if treffer else None


# ------------------------------------------------------------------------------------------
# MENGE IM SCHRITT
#
# Fuer Zutaten in TL/EL muss die Menge dort stehen, wo sie gebraucht wird. Gesucht wird die
# Form "<Zahl> <Einheit> <Zutat>" - also "1 TL Backpulver", "1/2 TL Salz", "2 EL Sojasosse".
# Zwischen Menge und Zutat duerfen ein paar Woerter stehen ("1 TL gemahlener Kreuzkuemmel"),
# aber kein Satzende: Sonst deckte eine Menge am Anfang des Rezepts jede spaetere Zutat.
BRUCH = r"(?:\d+[.,]?\d*|1/2|1/4|3/4|1/3|2/3|½|¼|¾|⅓|⅔)"
EINHEIT_IM_TEXT = {"tl": r"TL|Teel[öo]ffel", "el": r"EL|Essl[öo]ffel"}


def menge_im_schritt(zutat, steps):
    """Steht die Menge dieser Zutat im Schritt? Nur fuer TL/EL - siehe Kopf."""
    einheit = EINHEIT_IM_TEXT.get(zutat["einheit"])
    if not einheit:
        return True
    h = kopf(zutat["name"])
    # Der Kompositum-Rueckfall aus position() reicht hier nicht: Gesucht wird die Zutat
    # unmittelbar hinter ihrer Menge, und dort steht sie ausgeschrieben. Ein kurzer Stamm
    # genuegt trotzdem ("Kreuzkuemmel, gemahlen" -> "Kreuzkuemmel").
    stamm = re.escape(h[:8] if len(h) > 8 else h)
    muster = BRUCH + r"\s*(?:" + einheit + r")\b[^.\n]{0,30}?" + stamm
    return re.search(muster, steps, re.I) is not None


def protokoll_lesen():
    """Der Herkunftsnachweis je Bild. Fehlt die Datei, ist das ein ABBRUCH und kein leeres
    dict: Sonst meldete der Pruefstand 36 fehlende Nachweise, und die wahre Ursache - eine
    verschwundene Datei - stuende nirgends."""
    p = os.path.join(WURZEL, "img", "library", "bilder-protokoll.json")
    if not os.path.isfile(p):
        raise SystemExit("ABBRUCH: img/library/bilder-protokoll.json fehlt. Ohne sie laesst "
                         "sich die Zusage im Impressum nicht pruefen.")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def pruefen(pfad):
    rezepte = rezepte_lesen(pfad)
    protokoll = protokoll_lesen()
    regression, offen, behoben = [], [], []

    gesehen = {}
    for r in rezepte:
        rid = r["id"]
        if rid in gesehen:
            regression.append(f'{rid}: id kommt zweimal vor')
        gesehen[rid] = True

        if not r["steps"].strip():
            regression.append(f'{rid}: keine Zubereitung')
            continue

        # --- Jede Zutat traegt eine Menge ---
        # Ohne Grundlinie: Der Bestand wurde am 29.08.2026 vollstaendig nachgezogen.
        for z in r["eintraege"]:
            if z["freitext"]:
                regression.append(
                    '%s: Zutat "%s" steht als Freitext ohne Menge - als Objekt mit '
                    'grams/unit eintragen' % (rid, z["name"]))
            elif not z["menge"]:
                regression.append(
                    '%s: Zutat "%s" hat keine Menge (grams)' % (rid, z["name"]))
            elif not menge_im_schritt(z, r["steps"]):
                regression.append(
                    '%s: Menge von "%s" fehlt in der Anleitung - erwartet "%s %s ..."'
                    % (rid, z["name"], nummer(z["menge"]), z["einheit"].upper()))

        # --- Zutaten gegen die Anleitung ---
        grund = set(GRUNDLINIE.get(rid, []))
        fehlt = [z for z in r["zutaten"] if position(z, r["steps"]) is None]

        for z in fehlt:
            if z in grund:
                offen.append(f'{rid}: "{z}"')
            else:
                regression.append(
                    f'{rid}: Zutat "{z}" kommt in der Anleitung nicht vor')
        for z in sorted(grund - set(fehlt)):
            behoben.append(f'{rid}: "{z}" - Zeile aus der GRUNDLINIE streichen')

        # --- Nummerierung ---
        nummeriert = bool(re.match(r'\s*1\.\s', r["steps"])) and "\n2. " in r["steps"]
        if not nummeriert:
            if rid in UNNUMMERIERT_ALT:
                offen.append(f'{rid}: Anleitung noch nicht nummeriert')
            else:
                regression.append(
                    f'{rid}: Anleitung ist nicht nummeriert ("1. ...\\n2. ...")')
        elif rid in UNNUMMERIERT_ALT:
            behoben.append(f'{rid}: nummeriert - Zeile aus UNNUMMERIERT_ALT streichen')

        # --- Ernaehrungsform-Tags gegen die Zutaten ---
        for w in tag_widersprueche(r["tags"], r["zutaten"]):
            regression.append("%s: %s" % (rid, w))

        # --- Bild und sein Herkunftsnachweis ---
        #
        # Der zweite Teil ist eine RECHTLICHE Zusage, keine Ordnungsliebe: Das Impressum
        # (data/rechtstexte.js) sagt zu, dass zu jedem Bild festgehalten ist, mit welcher
        # Beschreibung und wann es entstanden ist. Eingeloest wird das von
        # img/library/bilder-protokoll.json - und bis zum 29.08.2026 hat niemand geprueft,
        # ob dort wirklich jedes Bild steht. Aufgefallen ist die Luecke dem Agenten `anwalt`
        # im Pushcheck: Er konnte es nur stichprobenartig pruefen und hat genau das gemeldet.
        # Ein Nachweis, den man einzeln nachzaehlen muss, ist auf Dauer keiner.
        if not r["img"]:
            regression.append(f'{rid}: kein Bild (img-Feld fehlt)')
        else:
            if not os.path.isfile(os.path.join(WURZEL, "img", "library", r["img"])):
                regression.append(f'{rid}: Bild fehlt - img/library/{r["img"]}')
            eintrag = protokoll.get(r["img"])
            if eintrag is None:
                regression.append(
                    f'{rid}: kein Herkunftsnachweis fuer {r["img"]} in '
                    f'img/library/bilder-protokoll.json - das Impressum sagt einen zu')
            else:
                luecken = [f for f in ("prompt", "modell", "erzeugt") if not eintrag.get(f)]
                if luecken:
                    regression.append(
                        f'{rid}: Herkunftsnachweis unvollstaendig ({", ".join(luecken)}) - '
                        f'{r["img"]}')

    # Verwaiste Eintraege: Wird ein Rezept umbenannt oder entfernt, bleibt seine Zeile in
    # GRUNDLINIE bzw. UNNUMMERIERT_ALT stehen und deckt fuer immer eine id, die es nicht
    # mehr gibt. Das faellt von allein nie auf - die Listen werden nur laenger.
    vorhanden = set(gesehen)
    for verwaist in sorted((set(GRUNDLINIE) | UNNUMMERIERT_ALT) - vorhanden):
        behoben.append(f'{verwaist}: Rezept existiert nicht mehr - Zeile aus GRUNDLINIE '
                       f'bzw. UNNUMMERIERT_ALT streichen')

    return rezepte, regression, offen, behoben


def grundlinie_ausgeben(pfad):
    """Die aktuelle Fehlerlage als Python-Literal - fuer die Bestands-Nacharbeit."""
    rezepte = rezepte_lesen(pfad)
    print("GRUNDLINIE = {")
    for r in rezepte:
        fehlt = [z for z in r["zutaten"] if position(z, r["steps"]) is None]
        if fehlt:
            werte = ", ".join('"%s"' % z for z in fehlt)
            print('    "%s": [%s],' % (r["id"], werte))
    print("}")


def main():
    args = [a for a in sys.argv[1:] if a != "--grundlinie"]
    pfad = os.path.abspath(args[0]) if args else os.path.join(WURZEL, "data", "cookbook.js")

    if "--grundlinie" in sys.argv:
        grundlinie_ausgeben(pfad)
        return 0

    rezepte, regression, offen, behoben = pruefen(pfad)

    print("Pruefstand Rezepttexte")
    print("Quelle: " + os.path.relpath(pfad, WURZEL).replace("\\", "/"))
    print("%d Rezepte geprueft" % len(rezepte))
    print("")

    for titel, eintraege in (("REGRESSION", regression), ("BEHOBEN", behoben),
                             ("OFFEN (Bestand)", offen)):
        if eintraege:
            print("%s (%d)" % (titel, len(eintraege)))
            for e in eintraege:
                print("  " + e)
            print("")

    if regression:
        print("FEHLGESCHLAGEN: %d Regression(en)" % len(regression))
        return 1
    # "ERGEBNIS" am Zeilenanfang ist das Belegmuster, an dem tools/alle-pruefstaende.py
    # erkennt, dass dieser Lauf ueberhaupt etwas gemessen hat (BELEG_MUSTER dort).
    # Ohne diese Zeile meldet der Reihenlauf "OHNE BELEG" statt gruen - genau die Falle
    # aus docs/TROUBLESHOOTING.md 131.
    print("ERGEBNIS keine Befunde (%d offen aus einer Grundlinie)" % len(offen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
