#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""Vergleicht die LIVE veroeffentlichten Firestore-Regeln mit der Vorlage firestore.rules.

Warum es dieses Skript gibt
---------------------------
Verbindlich ist der in der Firebase-Konsole veroeffentlichte Stand, nicht die Datei im Repo
(CLAUDE.md Abschnitt 12). Bis zum 19.09.2026 galt dieser Stand als "lokal nicht abrufbar" -
verglichen wurde per Augenschein im Regel-Editor, und am 18.09.2026 fiel dabei eine Abweichung
auf, deren Art (nur Kommentar oder echter Regeltext?) nur angenommen war.

Die Firebase-Rules-API liefert das aktive Regelwerk mit derselben gcloud-Anmeldung wie
tools/firestore-backup.py. Dieses Skript LIEST nur - es veroeffentlicht nie etwas. Das
Token wird nie ausgegeben.

Ausgabe
-------
    identisch            Datei und Live-Stand gleichen sich zeichengenau
    nur Kommentare       der Regeltext ist gleich, Kommentare weichen ab (Diff folgt)
    REGELN WEICHEN AB    der durchgesetzte Text ist ein anderer (Diff folgt) - Exit-Code 1

Jeder Lauf hinterlaesst seinen Ausgang in .claude/.letzter-regelvergleich. Daraus liest
tools/wartung-check.py, ob der Beleg noch frisch ist: Der Live-Stand kann sich jederzeit
aendern, ohne dass im Repo eine Zeile anders wird - ein Beleg dafuer altert also lautlos
(Phase E5, angebunden am 20.09.2026).

Aufruf:
    python tools/regeln-live.py              vergleichen
    python tools/regeln-live.py --speichern  zusaetzlich den Live-Text in den TEMP-Ordner
"""
import datetime, difflib, io, json, os, re, sys, tempfile, urllib.error, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from firestore_api import WURZEL, Zugang, ZugangFehler  # noqa: E402

API = "https://firebaserules.googleapis.com/v1/"


def holen(zugang, pfad):
    anfrage = urllib.request.Request(API + pfad)
    anfrage.add_header("Authorization", "Bearer " + zugang.token())
    # Ohne Kontingent-Projekt lehnt die Rules-API Nutzer-Anmeldungen teils ab.
    anfrage.add_header("x-goog-user-project", zugang.projekt)
    try:
        with urllib.request.urlopen(anfrage, timeout=60) as antwort:
            return json.loads(antwort.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
        raise ZugangFehler(u"Rules-API antwortete mit HTTP %d:\n%s" % (e.code, text[:600]))
    except urllib.error.URLError as e:
        raise ZugangFehler(u"Keine Verbindung zur Rules-API: %s" % e.reason)


def ohne_kommentare(text):
    u"""Nur der durchgesetzte Text: Zeilenkommentare und Leerzeilen raus.

    Die Regeln enthalten kein "//" innerhalb von Zeichenketten (Pfade beginnen mit EINEM
    Schraegstrich) - deshalb genuegt hier der einfache Schnitt.
    """
    zeilen = []
    for z in text.splitlines():
        z = re.sub(r"\s*//.*$", "", z).rstrip()
        if z.strip():
            zeilen.append(z)
    return zeilen


VERMERK = os.path.join(".claude", ".letzter-regelvergleich")


def vermerken(ausgang, regelwerk):
    u"""Haelt fest, wann zuletzt verglichen wurde und wie es ausging.

    tools/wartung-check.py liest das und mahnt, wenn der Beleg aelter als 30 Tage ist oder
    die letzte Prüfung eine Abweichung ergab. Ein fehlgeschlagener Lauf (kein Zugang, API
    nicht erreichbar) schreibt bewusst NICHTS - sonst sähe ein Abbruch wie eine Prüfung aus.
    """
    ziel = os.path.join(WURZEL, VERMERK)
    try:
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        with io.open(ziel, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"datum": datetime.date.today().isoformat(),
                       "ausgang": ausgang,
                       "regelwerk": regelwerk.rsplit("/", 1)[-1]}, f, ensure_ascii=False)
        print(u"\nVermerkt in %s (%s)." % (VERMERK, ausgang))
    except Exception as e:
        # Der Vergleich selbst ist das Ergebnis - am Vermerk soll er nicht scheitern.
        print(u"\nHinweis: Vermerk konnte nicht geschrieben werden (%s)." % e)


def main(argv):
    zugang = Zugang()
    release = holen(zugang, "projects/%s/releases/cloud.firestore" % zugang.projekt)
    regelwerk = release["rulesetName"]
    dateien = holen(zugang, regelwerk).get("source", {}).get("files", [])
    if len(dateien) != 1:
        raise ZugangFehler(u"Erwartet war genau eine Regeldatei, geliefert wurden %d." % len(dateien))
    live = dateien[0]["content"].replace("\r\n", "\n")
    with io.open(os.path.join(WURZEL, "firestore.rules"), encoding="utf-8") as f:
        repo = f.read().replace("\r\n", "\n")

    print(u"Aktives Regelwerk: %s" % regelwerk.rsplit("/", 1)[-1])
    print(u"Veroeffentlicht:   %s" % release.get("updateTime", "?"))
    print(u"Zeilen live/Repo:  %d / %d" % (live.count("\n") + 1, repo.count("\n") + 1))

    if "--speichern" in argv:
        ziel = os.path.join(tempfile.gettempdir(), "firestore-live.rules")
        with io.open(ziel, "w", encoding="utf-8", newline="\n") as f:
            f.write(live)
        print(u"Live-Text gespeichert: %s" % ziel)

    if live.rstrip() == repo.rstrip():
        print(u"\nidentisch")
        vermerken("identisch", regelwerk)
        return 0
    regel_gleich = ohne_kommentare(live) == ohne_kommentare(repo)
    print(u"\n" + (u"nur Kommentare weichen ab" if regel_gleich else u"REGELN WEICHEN AB"))
    for zeile in difflib.unified_diff(repo.splitlines(), live.splitlines(),
                                      "firestore.rules (Repo)", "live", lineterm="", n=1):
        print(zeile)
    vermerken("nur Kommentare" if regel_gleich else "ABWEICHUNG", regelwerk)
    return 0 if regel_gleich else 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except ZugangFehler as e:
        print(u"FEHLER: %s" % e)
        sys.exit(2)
