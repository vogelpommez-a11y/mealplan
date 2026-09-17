#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""Sichert alle Firestore-Daten von Paddy's Mealplan auf die lokale Platte.

Warum es dieses Skript gibt
---------------------------
Bis heute gab es von den Nutzerdaten keine einzige Kopie. Ueberschreibt ein Fehler in der
App die `weekStats` oder die Rezepte eines Kontos, gibt es keinen Weg zurueck. Art. 32 DSGVO
nennt die Wiederherstellbarkeit ausdruecklich - sie war der einzige offene Punkt aus
docs/SECURITY.md 9.2, der ohne Blaze loesbar ist.

Die verwalteten Firestore-Exporte von Google brauchen den Blaze-Tarif und haengen damit an
der Bezahl-Entscheidung. Dieses Skript liest ueber die normale REST-Schnittstelle und laeuft
deshalb auch auf Spark.

Wohin gesichert wird - und wohin ausdruecklich nicht
----------------------------------------------------
Das Ziel liegt NEBEN dem Projektordner, nie darin. In einer Sicherung stehen Namen, Ziele,
Gewichtsverlaeufe und Gruppen ECHTER Menschen; alles im Repo landet frueher oder spaeter
oeffentlich auf GitHub, und Geloeschtes bleibt dort in der Historie stehen. Das Skript
bricht deshalb ab, wenn das Ziel innerhalb des Repos liegt - lieber gar keine Sicherung als
eine, die die Daten veroeffentlicht.

Aus demselben Grund raeumt es alte Staende weg: Eine unbegrenzt wachsende Halde fremder
personenbezogener Daten auf einer Arbeitsplatte waere selbst ein Datenschutzproblem.
Aufbewahrung siehe docs/DATENSCHUTZ-INTERN.md.

Aufruf:
    python tools/firestore-backup.py                 # sichern
    python tools/firestore-backup.py --ziel D:\\Pfad  # anderes Ziel
    python tools/firestore-backup.py --behalten 30   # Aufbewahrung in Tagen
Rueckgabewert: 0 gesichert, 1 Abbruch mit Meldung.
"""
import datetime
import io
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import firestore_api as fs

WURZEL = fs.WURZEL
STANDARD_ZIEL = os.path.join(os.path.dirname(WURZEL), "Mealplan-Backups")

# Aufbewahrung: alles aelter als BEHALTEN_TAGE faellt weg. Punkt.
#
# Die EINZIGE Ausnahme ist der juengste Stand - er bleibt, auch wenn er die Frist reisst.
# Sonst stuende man nach einer laengeren Pause ganz ohne Kopie da, und der Zweck des
# Verfahrens waere weg.
#
# Der erste Anlauf behielt die juengsten ZEHN unabhaengig vom Alter. Das klang harmlos und
# war es nicht: Bei seltenem Lauf sind zehn Staende schnell aelter als 90 Tage, und die
# Zusage in docs/DATENSCHUTZ-INTERN.md 3a ("nach spaetestens 90 Tagen ist die Person auch
# aus den Sicherungen verschwunden") waere damit schlicht falsch gewesen - eine Zusage, die
# bei einem Loeschverlangen nach Art. 17 zaehlt. Gefunden vom Agenten `datenschutz-technik`
# am 17.09.2026: Eine Untergrenze in Staenden sticht eine Frist in Tagen.
BEHALTEN_TAGE = 90
MINDESTENS_STAENDE = 1

ORDNER_MUSTER = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(\d{4})(?:-(\d+))?$")


def ziel_pruefen(ziel):
    u"""Bricht ab, wenn das Ziel im Repo liegt. Fremde Daten gehoeren nie ins Repo.

    `realpath` statt `abspath`, und `normcase` dazu - beides ist unter Windows noetig und
    beides fehlte im ersten Anlauf:

    * **Gross-/Kleinschreibung:** NTFS ist unempfindlich, ein Stringvergleich nicht.
      `...\\PADDYS MEALPLAN\\backups` zeigt in denselben Ordner, sah fuer die Pruefung aber
      aus wie ein fremder Pfad.
    * **Junctions und Symlinks:** Ein Ziel kann lexikalisch ausserhalb liegen und physisch
      in den Repo-Baum zeigen. `abspath` loest das nicht auf, `realpath` schon.

    Beides hiesse: Die Daten aller Nutzer landen unbemerkt im Repo - und damit auf GitHub.
    """
    echt = os.path.realpath(ziel)
    z = os.path.normcase(echt)
    r = os.path.normcase(os.path.realpath(WURZEL))
    if z == r or z.startswith(r + os.sep):
        raise fs.ZugangFehler(
            u"Das Ziel liegt im Projektordner:\n    %s\n"
            u"(aufgeloest aus: %s)\n"
            u"Dort stehen personenbezogene Daten anderer Menschen nicht richtig - alles im\n"
            u"Repo landet auf GitHub. Waehle einen Ordner ausserhalb, z.B.:\n    %s"
            % (echt, ziel, STANDARD_ZIEL))
    return echt


def ordnername(jetzt=None, vorhanden=None):
    u"""JJJJ-MM-TT-hhmm, bei Kollision mit einem Zaehler dahinter."""
    jetzt = jetzt or datetime.datetime.now()
    basis = jetzt.strftime("%Y-%m-%d-%H%M")
    vorhanden = set(vorhanden or [])
    if basis not in vorhanden:
        return basis
    for n in range(2, 100):
        if "%s-%d" % (basis, n) not in vorhanden:
            return "%s-%d" % (basis, n)
    raise fs.ZugangFehler(
        u"In dieser Minute liegen bereits 99 Sicherungen. Das ist kein normaler Betrieb -\n"
        u"laeuft das Skript versehentlich in einer Schleife?")


def aufteilen(alles):
    u"""{pfad: felder} -> {wurzelsammlung: {pfad: felder}}.

    Eine Datei je Wurzelsammlung, Unterkollektionen kommen in die Datei ihrer Wurzel. Der
    Schluessel bleibt immer der volle Pfad, damit die Rueckspielung nichts zusammensetzen
    muss - ein zusammengesetzter Pfad waere eine Fehlerquelle an der gefaehrlichsten Stelle.
    """
    raus = {}
    for pfad in sorted(alles):
        raus.setdefault(pfad.split("/")[0], {})[pfad] = alles[pfad]
    return raus


def staende(basis):
    u"""Die vorhandenen Sicherungsordner, aelteste zuerst."""
    if not os.path.isdir(basis):
        return []
    return sorted(n for n in os.listdir(basis)
                  if ORDNER_MUSTER.match(n) and os.path.isdir(os.path.join(basis, n)))


def _datum_aus(name):
    t = ORDNER_MUSTER.match(name)
    return datetime.datetime(int(t.group(1)), int(t.group(2)), int(t.group(3)),
                             int(t.group(4)[:2]), int(t.group(4)[2:]))


def alte_raeumen(basis, behalten_tage=BEHALTEN_TAGE, mindestens=MINDESTENS_STAENDE,
                 jetzt=None, loeschen=None):
    u"""Loescht jeden Stand, der aelter ist als die Frist - ausser dem juengsten.

    `mindestens` ist die Zahl der juengsten Staende, die unabhaengig vom Alter bleiben. Sie
    steht auf 1 und sollte dort bleiben: Jede groessere Zahl hebelt die Frist aus (siehe
    Kommentar bei BEHALTEN_TAGE). Der Parameter existiert, damit der Pruefstand beide
    Richtungen messen kann.

    `loeschen` ist einsetzbar, damit der Pruefstand die Auswahlregel pruefen kann, ohne
    Ordner anzulegen und wieder wegzuwerfen.
    """
    jetzt = jetzt or datetime.datetime.now()
    loeschen = loeschen or (lambda p: shutil.rmtree(p))
    vorhanden = staende(basis)
    zuviel = vorhanden[:-mindestens] if mindestens else vorhanden
    weg = []
    for name in zuviel:
        if (jetzt - _datum_aus(name)).days > behalten_tage:
            loeschen(os.path.join(basis, name))
            weg.append(name)
    return weg


def sichere(zugang, ziel, jetzt=None, melder=None):
    u"""Holt alles und schreibt es. Liefert das Manifest."""
    melder = melder or (lambda t: None)
    basis = ziel_pruefen(ziel)
    begonnen = jetzt or datetime.datetime.now()

    # Erst holen, dann anlegen: Scheitert der Zugang, soll kein leerer Ordner
    # zurueckbleiben, den beim naechsten Mal jemand fuer eine Sicherung haelt.
    melder(u"Sammlungen werden erhoben ...")
    alles = zugang.alles(melder=lambda s: melder(u"  lese %s" % s))
    if not alles:
        raise fs.ZugangFehler(
            u"Firestore lieferte KEIN einziges Dokument.\n"
            u"Das ist eher ein Zugriffs- als ein Datenbefund - eine leere Sicherung wird\n"
            u"deshalb gar nicht erst angelegt. Stimmt das Projekt, und hat das angemeldete\n"
            u"Konto Leserechte?")

    teile = aufteilen(alles)
    if not os.path.isdir(basis):
        os.makedirs(basis)
    ordner = os.path.join(basis, ordnername(begonnen, staende(basis)))
    os.makedirs(ordner)
    for sammlung in sorted(teile):
        with io.open(os.path.join(ordner, sammlung + ".json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(teile[sammlung], ensure_ascii=False,
                               indent=1, sort_keys=True))

    manifest = {
        "projekt": zugang.projekt,
        "erstellt": begonnen.strftime("%Y-%m-%d %H:%M:%S"),
        "dokumente": len(alles),
        "sammlungen": {s: len(teile[s]) for s in sorted(teile)},
        "werkzeug": "tools/firestore-backup.py",
        "format": "Firestore-Rohformat (fields), verlustfrei zurueckschreibbar",
    }
    with io.open(os.path.join(ordner, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True))
    manifest["ordner"] = ordner
    return manifest


def main():
    print(u"Firestore-Sicherung - Paddy's Mealplan")
    print(u"=" * 62)
    try:
        ziel = fs.arg(sys.argv, "--ziel", STANDARD_ZIEL)
        behalten = fs.arg(sys.argv, "--behalten", BEHALTEN_TAGE, zahl=True)
        zugang = fs.Zugang()
        print(u"Projekt: %s" % zugang.projekt)
        manifest = sichere(zugang, ziel, melder=lambda t: print(u"  " + t))
    except fs.ZugangFehler as e:
        print(u"")
        print(u"ABBRUCH: %s" % e)
        return 1

    print(u"")
    print(u"Gesichert: %d Dokumente" % manifest["dokumente"])
    for s in sorted(manifest["sammlungen"]):
        print(u"  %-16s %4d" % (s, manifest["sammlungen"][s]))
    print(u"Ordner:    %s" % manifest["ordner"])

    weg = alte_raeumen(ziel_pruefen(ziel), behalten_tage=behalten)
    if weg:
        print(u"")
        print(u"Aufgeraeumt (aelter als %d Tage; der juengste Stand bleibt immer):" % behalten)
        for n in weg:
            print(u"  weg: %s" % n)

    print(u"")
    print(u"Zurueckspielen im Notfall:  python tools/firestore-restore.py --stand %s"
          % os.path.basename(manifest["ordner"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
