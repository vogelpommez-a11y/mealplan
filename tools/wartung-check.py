#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wartungspruefung fuer das Projekt-Setup: bleibt das Pruefsystem selbst noch wahr?

Warum es dieses Skript gibt
---------------------------
Am 26.08.2026 wurde das Setup (Agenten, Hooks, Skills, Dokumentation) an einem Tag
aufgebaut - und war noch am selben Abend an fuenf Stellen falsch. Nicht aus Schlamperei,
sondern weil sich die Wirklichkeit darunter bewegt hatte: eine Produktentscheidung hier,
ein geklaerter Vertrag dort, eine korrigierte Zahl an dritter Stelle.

Der gefaehrlichste Zustand ist nicht "keine Pruefung", sondern eine Pruefung, der man
glaubt, obwohl sie veraltet ist. Ein Agent, der eine falsche Domain kennt, prueft die
falsche Seite - und meldet "sauber".

Dieses Skript findet genau die Fehlerarten, die damals Handarbeit waren. Es braucht kein
Modell, laeuft in Sekunden und wird nie muede.

Was es NICHT kann
-----------------
Es prueft Konsistenz, nicht Inhalt. Ob eine Rechtslage sich geaendert hat oder eine
Store-Richtlinie neu gefasst wurde, sieht es nicht - dafuer sind die Agenten mit
Recherche-Auftrag da (`anwalt`, `store-check`, `lieferkette`).

Aufruf:
    python tools/wartung-check.py            # Bericht
    python tools/wartung-check.py --setze    # zusaetzlich Wartungsdatum auf heute setzen
Rueckgabewert: 0 sauber, 1 mindestens ein Befund.
"""
import datetime
import io
import os
import py_compile
import re
import subprocess
import sys
import tempfile

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WURZEL)

MARKER = os.path.join(".claude", ".letzte-wartung")
ABSTAND_TAGE = 30

befunde = []   # (schwere, bereich, text)   schwere: "rot" | "gelb"


def rot(bereich, text):  befunde.append(("rot", bereich, text))
def gelb(bereich, text): befunde.append(("gelb", bereich, text))


def lies(pfad):
    try:
        return io.open(pfad, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def dateien(ordner, endung=".md"):
    treffer = []
    for wurzel, _, namen in os.walk(ordner):
        for n in namen:
            if n.endswith(endung):
                treffer.append(os.path.join(wurzel, n).replace("\\", "/"))
    return sorted(treffer)


# --------------------------------------------------------------------------- 1
def pruefe_fakten():
    """Zahlen und Namen, die in Anleitungen stehen und still veralten.

    Der Klassiker: website-security kannte am 26.08.2026 noch "~780 KB" und die alte
    github.io-Adresse. Ein Pruefer mit falscher Domain prueft die falsche Seite.
    """
    bereich = "Fakten"

    # Groesse von index.html gegen die Angaben in den Agenten.
    #
    # Nur Groessenangaben, die TATSAECHLICH index.html meinen: Der erste Entwurf dieser
    # Pruefung nahm jede "~NNN KB"-Angabe und meldete prompt die 336 KB von zxing.min.js
    # als falsche index.html-Groesse. Deshalb muss "index.html" im selben Satz stehen.
    if os.path.exists("index.html"):
        mb = os.path.getsize("index.html") / (1024 * 1024)
        for p in dateien(".claude") + dateien("docs"):
            for m in re.finditer(r"~\s*([\d,\.]+)\s*(MB|KB)", lies(p)):
                umfeld = lies(p)[max(0, m.start() - 120): m.end() + 120]
                if "index.html" not in umfeld:
                    continue
                wert = float(m.group(1).replace(",", "."))
                genannt_mb = wert if m.group(2) == "MB" else wert / 1024
                if abs(genannt_mb - mb) > 0.25:
                    gelb(bereich, "%s nennt ~%s %s fuer index.html, tatsaechlich %.2f MB"
                         % (p, m.group(1), m.group(2), mb))

    # Domain: die alte Adresse darf vorkommen, aber nicht als einzige
    for p in dateien(".claude"):
        t = lies(p)
        if "github.io" in t and "paddysmealplan.de" not in t:
            rot(bereich, "%s kennt nur die alte github.io-Adresse, nicht die Live-Domain" % p)

    # Vendor-Version: Ordnername gegen das, was die Doku behauptet
    vd = "vendor/firebase"
    if os.path.isdir(vd):
        versionen = [d for d in os.listdir(vd) if re.match(r"^\d+\.\d+", d)]
        for v in versionen:
            for p in dateien(".claude") + dateien("docs"):
                t = lies(p)
                for m in re.finditer(r"vendor/firebase[/ ](\d+\.\d+\.\d+)", t):
                    if m.group(1) not in versionen:
                        gelb(bereich, "%s nennt Firebase-SDK %s, im Ordner liegt %s"
                             % (p, m.group(1), ", ".join(versionen)))

    # Anzahl der Katalog-Rezepte gegen die Angaben in der Doku
    ih = lies("index.html")
    if "const COOKBOOK = [" in ih:
        i = ih.index("const COOKBOOK = [")
        tiefe, ende = 0, None
        for k in range(i + len("const COOKBOOK = "), len(ih)):
            if ih[k] == "[":
                tiefe += 1
            elif ih[k] == "]":
                tiefe -= 1
                if tiefe == 0:
                    ende = k
                    break
        if ende:
            anzahl = len(re.findall(r'\bid:\s*"', ih[i:ende]))
            # "damals 30 Rezepte" ist ein Bericht ueber die Vergangenheit und kein Fehler.
            # Eine Doku, die ihre Geschichte erzaehlt, darf alte Zahlen nennen - sie muss
            # nur kenntlich machen, dass sie alt sind.
            HISTORISCH = ("damals", "seinerzeit", "früher", "zunaechst", "zunächst",
                          "ursprünglich", "urspruenglich")
            for p in dateien("docs") + dateien(".claude"):
                t = lies(p)
                for m in re.finditer(r"(\d+)\s+(?:Katalog-Rezepte|Rezepte im Katalog)", t):
                    if int(m.group(1)) == anzahl:
                        continue
                    davor = t[max(0, m.start() - 60): m.start()].lower()
                    if any(w in davor for w in HISTORISCH):
                        continue
                    gelb(bereich, "%s nennt %s Katalog-Rezepte, tatsaechlich sind es %d"
                         % (p, m.group(1), anzahl))


# --------------------------------------------------------------------------- 2
def pruefe_verweise():
    """Zeigt eine Anleitung auf eine Datei, die es nicht (mehr) gibt?"""
    bereich = "Verweise"

    # Pfade, die absichtlich (noch) nicht existieren: Vorschlaege in Anleitungen und
    # Verzeichnisse, die ein Werkzeug erst bei Bedarf anlegt. Ohne diese Liste meldet die
    # Pruefung Absichten als Fehler - und wer Fehlalarme bekommt, schaltet sie ab.
    GEPLANT = {
        "vendor/HERKUNFT.md",     # Vorschlag im Agenten `lieferkette`, noch nicht angelegt
        ".claude/plans",          # legt Claude Code selbst an, sobald ein Plan entsteht
        ".claude/.letzte-wartung",
        ".claude/.letzter-pushcheck",
    }

    muster = re.compile(r"`((?:docs|tools|\.claude|worker|vendor)/[A-Za-z0-9_./-]+"
                        r"|[A-Z][A-Z-]+\.md|firestore\.rules|sw\.js|index\.html)`")
    for p in dateien(".claude") + dateien("docs") + ["CLAUDE.md"]:
        if not os.path.exists(p):
            continue
        ordner = os.path.dirname(p)
        for ziel in set(muster.findall(lies(p))):
            if "*" in ziel or ziel.endswith("/") or ziel in GEPLANT:
                continue
            # Ein Verweis darf relativ zum eigenen Ordner gemeint sein: In docs/TESTING.md
            # bedeutet `PRODUCT.md` die Datei docs/PRODUCT.md, nicht die im Wurzelordner.
            kandidaten = [ziel,
                          os.path.join(ordner, ziel),
                          ziel.replace("/skills/", "/Skills/")]
            if any(os.path.exists(k) for k in kandidaten):
                continue
            rot(bereich, "%s verweist auf %s - existiert nicht" % (p, ziel))


# --------------------------------------------------------------------------- 3
def erwartete_modelle(text):
    """Welches Modell verspricht ein Anleitungstext je Agent?

    Zwei Schreibweisen kommen im Projekt vor, beide werden gelesen:
      * eine Tabellenzeile mit eigener Modellspalte:  | `kvp` | haiku | ... |
      * ein Sammelsatz ueber einer Tabelle:           **Nach Ausloeser, alle auf sonnet:**
        Er gilt fuer jede Agentenzeile bis zur naechsten Ueberschrift oder zum naechsten
        Sammelsatz.
    """
    MODELLE = ("sonnet", "haiku", "opus", "fable")
    gefunden = {}
    sammel = None
    for zeile in text.splitlines():
        if zeile.startswith("#"):
            sammel = None
        s = re.search(r"alle auf (%s)" % "|".join(MODELLE), zeile)
        if s:
            sammel = s.group(1)
            continue
        agent = re.search(r"`([a-z][a-z-]+)`", zeile)
        if not agent or not (zeile.lstrip().startswith("|")
                             or "model:" in zeile):
            continue
        agent = agent.group(1)
        # Modell in einer eigenen Tabellenspalte (`| haiku |`) oder als `model: haiku`
        eigene = re.search(r"(?:\|\s*|model:\s*)(%s)\s*(?:\||`|$)" % "|".join(MODELLE),
                           zeile)
        if eigene:
            gefunden[agent] = eigene.group(1)
        elif sammel and zeile.lstrip().startswith("|"):
            gefunden[agent] = sammel
    return gefunden


def pruefe_agenten():
    """Formales und die eine Falle, die schon zugeschlagen hat.

    Ein Agent ohne `tools:`-Zeile bekommt ALLE Werkzeuge - auch Write und Edit. Wenn seine
    Beschreibung "aendert nichts" verspricht, ist das eine falsche Zusage. Genau das war am
    26.08.2026 beim ux-reviewer der Fall.
    """
    bereich = "Agenten"
    for p in dateien(".claude/agents"):
        t = lies(p)
        kopf = t.split("---")[1] if t.startswith("---") and t.count("---") >= 2 else ""
        for feld in ("name:", "description:", "model:"):
            if feld not in kopf:
                gelb(bereich, "%s: Feld %s fehlt im Kopf" % (p, feld.strip(":")))

        hat_tools = "tools:" in kopf
        verspricht_lesend = re.search(r"(aender[nt] nichts|keine Schreibrechte|schlägst vor)",
                                      t, re.I)
        if verspricht_lesend:
            if not hat_tools:
                rot(bereich, "%s verspricht, nichts zu aendern, hat aber keine tools-Zeile "
                             "- damit ALLE Werkzeuge inkl. Write/Edit" % p)
            else:
                zeile = re.search(r"tools:(.*)", kopf).group(1)
                for gefaehrlich in ("Write", "Edit", "NotebookEdit"):
                    if gefaehrlich in zeile:
                        rot(bereich, "%s verspricht, nichts zu aendern, hat aber %s"
                            % (p, gefaehrlich))

    # Jeder Agent sollte in CLAUDE.md vorkommen und umgekehrt
    cm = lies("CLAUDE.md")
    namen = [os.path.basename(p)[:-3] for p in dateien(".claude/agents")]
    for n in namen:
        if n not in cm:
            gelb(bereich, "Agent '%s' wird in CLAUDE.md nicht erwaehnt" % n)
    for m in re.finditer(r"`(anwalt|kvp|ux-reviewer|website-security|store-check|"
                         r"lieferkette|datenschutz-technik|doku-waechter)`", cm):
        if m.group(1) not in namen:
            rot(bereich, "CLAUDE.md nennt Agent '%s', die Datei fehlt" % m.group(1))

    # Modellabgleich: steht in der Agentendatei dasselbe Modell wie in der Anleitung?
    #
    # Warum das hier steht: Am 27.08.2026 lief `kvp` laut seiner eigenen Datei auf Sonnet,
    # waehrend CLAUDE.md und pushcheck.md an drei Stellen Haiku versprachen. Kein Fehlalarm
    # und kein Schoenheitsfehler - wer die Kosten eines /pushcheck abschaetzt, rechnet mit
    # dem, was in der Anleitung steht. Diese Pruefung hat es damals nicht gesehen.
    for datei, quelle in ((cm, "CLAUDE.md"), (lies(".claude/commands/pushcheck.md"),
                                              "pushcheck.md")):
        for agent, modell in erwartete_modelle(datei).items():
            if agent not in namen:
                continue
            kopf = lies(".claude/agents/%s.md" % agent).split("---")
            kopf = kopf[1] if len(kopf) >= 3 else ""
            m = re.search(r"model:\s*(\S+)", kopf)
            ist = m.group(1) if m else "(fehlt)"
            if ist != modell:
                rot(bereich, "%s verspricht fuer '%s' das Modell %s, die Agentendatei "
                             "sagt %s" % (quelle, agent, modell, ist))


# --------------------------------------------------------------------------- 4
def pruefe_hooks():
    """Laufen die Hooks ueberhaupt - und kennt der Commit-Waechter alles Heikle?"""
    bereich = "Hooks"
    s = lies(".claude/settings.json")
    for m in re.finditer(r"\.claude/hooks/([a-z-]+\.py)", s):
        pfad = ".claude/hooks/" + m.group(1)
        if not os.path.exists(pfad):
            rot(bereich, "settings.json ruft %s auf - Datei fehlt" % pfad)
            continue
        try:
            py_compile.compile(pfad, cfile=tempfile.mktemp(), doraise=True)
        except Exception as e:
            rot(bereich, "%s ist syntaktisch kaputt: %s" % (pfad, e))

    # Deckung: Was die .gitignore als heikel behandelt, muss der Waechter kennen.
    wc = lies(".claude/hooks/commit-waechter.py")
    HEIKEL = ["plans/", "Fotos/", "Marketing/", "Instagram/", "ROADMAP.html", ".env",
              "wochenplan-backup/", ".claude/settings.local.json",
              "docs/DATENSCHUTZ-INTERN.md", ".claude/Skills/", "index.backup",
              "serviceAccount", ".key", ".pem"]
    gi = lies(".gitignore")
    for eintrag in HEIKEL:
        if eintrag in gi and eintrag not in wc:
            rot(bereich, "'%s' ist gitignored, aber der Commit-Waechter kennt es nicht "
                         "- ein 'git add -f' kaeme durch" % eintrag)

    # Dieselbe Deckung in der ANDEREN Richtung: blockiert der Waechter etwas, das laengst
    # im Repo liegt?
    #
    # Warum das noetig ist: Am 27.08.2026 fuehrte der Waechter ".claude/Skills/" als
    # verboten - dort liegen aber auch die vier selbst geschriebenen Projekt-Skills, seit
    # dem Vortag getrackt. Jede Aenderung an /smoke oder /deploy waere am eigenen Hook
    # gescheitert, mit der Begruendung "fremde Inhalte ohne belegte Lizenz". Die Pruefung
    # oben konnte das nicht sehen: sie schaut nur, ob der Waechter genug blockiert, nie ob
    # er zu viel blockiert.
    #
    # Gefragt wird der Waechter selbst (bewerte()), nicht eine Kopie seiner Listen - sonst
    # driften Pruefung und Regel auseinander.
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("cw", ".claude/hooks/commit-waechter.py")
        cw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cw)
        getrackt = subprocess.run(["git", "ls-files"], capture_output=True,
                                  text=True, timeout=30).stdout.split()
        for pfad in getrackt:
            grund = cw.bewerte(pfad)
            if grund:
                rot(bereich, "Der Commit-Waechter blockiert '%s' (%s) - die Datei liegt "
                             "aber getrackt im Repo. Jede Aenderung daran waere nicht "
                             "committebar." % (pfad, grund))
    except Exception as e:
        gelb(bereich, "Gegenrichtung des Commit-Waechters nicht pruefbar: %s" % e)


# --------------------------------------------------------------------------- 5
def pruefe_skills():
    bereich = "Skills"
    basis = ".claude/Skills" if os.path.isdir(".claude/Skills") else ".claude/skills"
    EIGENE = ("smoke", "pruefstand", "abnahme", "deploy")
    for name in EIGENE:
        p = os.path.join(basis, name, "SKILL.md").replace("\\", "/")
        if not os.path.exists(p):
            rot(bereich, "Eigener Skill '%s' fehlt (%s)" % (name, p))
            continue
        t = lies(p)
        if "name:" not in t or "description:" not in t:
            gelb(bereich, "%s: name oder description fehlt im Kopf" % p)
        # Gitignore-Falle: eigene Skills muessen sichtbar bleiben
        try:
            r = subprocess.run(["git", "check-ignore", "-q", p], capture_output=True)
            if r.returncode == 0:
                rot(bereich, "%s ist gitignored - beim naechsten frischen Checkout weg" % p)
        except Exception:
            pass


# --------------------------------------------------------------------------- 6
def pruefe_alter():
    """Wie lange ist die letzte inhaltliche Wartung her?"""
    bereich = "Alter"
    heute = datetime.date.today()
    if os.path.exists(MARKER):
        try:
            stand = datetime.date.fromisoformat(lies(MARKER).strip()[:10])
            tage = (heute - stand).days
            if tage > ABSTAND_TAGE:
                gelb(bereich, "Letzte Wartung war vor %d Tagen (%s). Faellig alle %d Tage."
                     % (tage, stand.isoformat(), ABSTAND_TAGE))
        except Exception:
            gelb(bereich, "%s ist unlesbar - Datum im Format JJJJ-MM-TT erwartet" % MARKER)
    else:
        gelb(bereich, "Noch nie eine Wartung vermerkt (%s fehlt)." % MARKER)

    # Datierte Aussagen in der Doku, die alt werden
    for p in ["docs/SECURITY.md", "docs/STORE.md", "docs/DATENSCHUTZ-INTERN.md"]:
        if not os.path.exists(p):
            continue
        datumsangaben = re.findall(r"(\d{2})\.(\d{2})\.(\d{4})", lies(p))
        if not datumsangaben:
            continue
        juengstes = max(datetime.date(int(j), int(m), int(t)) for t, m, j in datumsangaben)
        tage = (heute - juengstes).days
        if tage > 180:
            gelb(bereich, "%s: juengste datierte Aussage ist %d Tage alt (%s)"
                 % (p, tage, juengstes.isoformat()))


# --------------------------------------------------------------------------- Lauf
def pruefe_abdeckung():
    """Gibt es einen Bereich im Projekt, den niemand prueft?

    Andere Frage als der Rest dieses Skripts: Hier geht es nicht um Konsistenz zwischen
    vorhandenen Dingen, sondern um FEHLENDES. Die Logik steht in tools/abdeckung.py, damit
    der Sitzungsstart-Hook dieselbe Antwort bekommt, ohne sie nachzubauen.
    """
    bereich = "Abdeckung"
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("abdeckung", "tools/abdeckung.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    except Exception as e:
        gelb(bereich, "tools/abdeckung.py nicht ladbar: %s" % e)
        return

    luecken, bekannt, _ = m.pruefe()
    if bekannt is None:
        rot(bereich, "docs/ABDECKUNG.md fehlt - ohne Register ist kein Bereich zugeordnet")
        return
    for k in luecken:
        gelb(bereich, "'%s' ist keinem Pruefer zugeordnet - Entscheidung noetig "
                      "(docs/ABDECKUNG.md, Abschnitt 7)" % k)

    # Und die Probe aufs Exempel: Wuerde die Pruefung eine Luecke ueberhaupt bemerken?
    # Eine Erhebung, die nichts mehr findet, meldet ewig "alles zugeordnet".
    try:
        echt = m.ist_zustand()
        if len(echt) < 20:
            rot(bereich, "Die Abdeckungserhebung liefert nur %d Bereiche - sie ist "
                         "vermutlich kaputt und meldet deshalb faelschlich 'sauber'"
                % len(echt))
    except Exception as e:
        gelb(bereich, "Abdeckungserhebung nicht pruefbar: %s" % e)


def main():
    print("Wartungspruefung - Paddy's Mealplan Setup")
    print("=" * 62)

    # Das Datum VOR den Pruefungen setzen, sonst meldet derselbe Lauf noch den alten Stand.
    if "--setze" in sys.argv:
        io.open(MARKER, "w", encoding="utf-8").write(datetime.date.today().isoformat() + "\n")
        print("Wartungsdatum auf %s gesetzt.\n" % datetime.date.today().isoformat())

    for fn in (pruefe_fakten, pruefe_verweise, pruefe_agenten,
               pruefe_hooks, pruefe_skills, pruefe_abdeckung, pruefe_alter):
        try:
            fn()
        except Exception as e:
            gelb("Skript", "Pruefung %s ist gescheitert: %s" % (fn.__name__, e))

    if not befunde:
        print("\nKeine Befunde. Das Setup beschreibt sich selbst korrekt.")
        print("\nWas dieses Skript NICHT prueft: ob sich Recht, Store-Richtlinien oder")
        print("Bibliotheken geaendert haben. Dafuer die Agenten mit Recherche-Auftrag:")
        print("  anwalt, store-check, lieferkette")
        return 0

    for schwere in ("rot", "gelb"):
        teil = [b for b in befunde if b[0] == schwere]
        if not teil:
            continue
        print("\n%s  (%d)" % ("ROT - jetzt beheben" if schwere == "rot"
                              else "GELB - ansehen", len(teil)))
        print("-" * 62)
        for _, bereich, text in teil:
            print("  [%s] %s" % (bereich, text))

    print("\n%d Befund(e). Danach erneut laufen lassen." % len(befunde))
    return 1 if any(b[0] == "rot" for b in befunde) else 0


if __name__ == "__main__":
    sys.exit(main())
